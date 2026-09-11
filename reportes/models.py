"""
Núcleo del sistema de reportes de fluidos de perforación.

Jerarquía: Pozo -> Intervalo -> ReporteDiario -> (InventarioItem, UsoMaterial)
Un Intervalo puede tener varios tramos de TuberiaInstalada (revestidor + liner, etc.)
y, cuando se cierra, exactamente un CierreVolumetrico.

Cada Intervalo tiene un SistemaFluido asignado (catálogo editable: "gama de
fluidos"). El sistema de fluido puede cambiar de un intervalo a otro del mismo
pozo (ej. intervalo 1 base agua, intervalo 2 polimérico, intervalo 3 base
aceite, según el diseño de fluidos del pozo), pero queda fijo para ese
intervalo desde que se abre hasta que se cierra. Es la base de la matriz de
propiedades selectivas (Misión 4): cada propiedad del catálogo maestro se
marcará como aplicable o no a cada SistemaFluido.

Reglas de negocio implementadas aquí:
  1. No se puede crear ni modificar un ReporteDiario si su Intervalo está cerrado.
  2. numero_reporte es correlativo por Pozo (no se reinicia entre intervalos).
  3. Al crear un CierreVolumetrico, el Intervalo pasa automáticamente a estado 'cerrado'.
  4. Cada Intervalo tiene un SistemaFluido (catálogo editable), fijo mientras
     el intervalo está abierto.

Los métodos `to_dict()` de cada modelo son la capa de serialización que usa
`views.py` para la interfaz web (Misión "Interfaz módulo Reportes"): mantienen
el JSON de la API desacoplado de los nombres internos de los campos.
"""

import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Max


class Pozo(models.Model):
    """Configuración inicial del pozo (manual resumido, Paso 1: Project -> General).

    Un grupo de campos queda congelado permanentemente en cuanto el pozo tiene
    su primer ReporteDiario (`tiene_reportes`): `unit_set`, `es_offshore` y
    `usa_riser`. El resto (incluidos los numéricos offshore) se puede seguir
    actualizando durante todo el proyecto — así lo indica el manual ("Estos
    campos numéricos sí pueden actualizarse durante el proyecto").
    """

    class UnitSet(models.TextChoices):
        OILFIELD = "oilfield", "Standard Oilfield (ft, in, bbl, lb/gal)"
        METRIC = "metric", "Metric"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # --- 1.1 Entradas de identificación ---
    numero_logit = models.CharField(
        max_length=60, unique=True, null=True, blank=True,
        help_text="Log-It Number: identificador único de seguimiento corporativo.",
    )
    nombre = models.CharField(max_length=120)
    operador = models.CharField(max_length=120)
    ubicacion = models.CharField(max_length=120)
    campo_area = models.CharField(max_length=120, blank=True, help_text="Field Name/Block.")
    nombre_taladro = models.CharField(max_length=120, blank=True, help_text="Rig Name.")
    contratista = models.CharField(max_length=120, blank=True, help_text="Contractor.")
    fecha_spud = models.DateField(null=True, blank=True)

    # Parámetros térmicos (API 5th Edition)
    surface_temp = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, help_text="Surface Temp, en °F.",
    )
    temp_gradient = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, help_text="Temp Gradient, en °F/100ft.",
    )

    # --- 1.2 Regla de congelamiento base ---
    unit_set = models.CharField(
        max_length=10, choices=UnitSet.choices, default=UnitSet.OILFIELD,
        help_text="Se bloquea permanentemente al crear el primer reporte diario.",
    )
    es_offshore = models.BooleanField(
        default=False, verbose_name="¿Es offshore?",
        help_text="Se bloquea permanentemente al crear el primer reporte diario.",
    )
    usa_riser = models.BooleanField(
        default=False, verbose_name="Usa riser",
        help_text="Se bloquea permanentemente al crear el primer reporte diario.",
    )

    # Configuración marina (numéricos — sí editables durante el proyecto)
    air_gap = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Air Gap, en ft.")
    water_depth = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, help_text="Water Depth, en ft.",
    )
    sea_floor_temp = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, help_text="Sea Floor Temp, en °F.",
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    @property
    def tiene_reportes(self):
        """True en cuanto el pozo tiene al menos un ReporteDiario (en cualquiera
        de sus intervalos) — dispara el bloqueo permanente de la sección 1.2."""
        return ReporteDiario.objects.filter(intervalo__pozo_id=self.id).exists()

    def clean(self):
        if self.pk and self.tiene_reportes:
            anterior = Pozo.objects.filter(pk=self.pk).values(
                "unit_set", "es_offshore", "usa_riser"
            ).first()
            if anterior:
                bloqueados = []
                if anterior["unit_set"] != self.unit_set:
                    bloqueados.append("Unit Set")
                if anterior["es_offshore"] != self.es_offshore:
                    bloqueados.append("Is Offshore?")
                if anterior["usa_riser"] != self.usa_riser:
                    bloqueados.append("Uses Riser")
                if bloqueados:
                    raise ValidationError(
                        "No se puede modificar "
                        + ", ".join(bloqueados)
                        + ": quedan bloqueados permanentemente desde el primer reporte diario del pozo."
                    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "numero_logit": self.numero_logit,
            "nombre": self.nombre,
            "operador": self.operador,
            "ubicacion": self.ubicacion,
            "campo_area": self.campo_area,
            "nombre_taladro": self.nombre_taladro,
            "contratista": self.contratista,
            "fecha_spud": self.fecha_spud.isoformat() if self.fecha_spud else None,
            "surface_temp": str(self.surface_temp) if self.surface_temp is not None else None,
            "temp_gradient": str(self.temp_gradient) if self.temp_gradient is not None else None,
            "unit_set": self.unit_set,
            "unit_set_display": self.get_unit_set_display(),
            "es_offshore": self.es_offshore,
            "usa_riser": self.usa_riser,
            "air_gap": str(self.air_gap) if self.air_gap is not None else None,
            "water_depth": str(self.water_depth) if self.water_depth is not None else None,
            "sea_floor_temp": str(self.sea_floor_temp) if self.sea_floor_temp is not None else None,
            "tiene_reportes": self.tiene_reportes,
            "total_intervalos": self.intervalos.count(),
        }


class SistemaFluido(models.Model):
    """Catálogo maestro de sistemas de fluido ("gama de fluidos") que puede
    asignarse a un Intervalo. Ej.: "Base Agua", "Lodo Polimérico KCl",
    "Base Aceite", "Sintético SBM". Editable desde el admin: no requiere
    migración de código para agregar un sistema nuevo.

    `categoria` es la clasificación base (agua / polimérico / aceite /
    sintético) que en la Misión 4 determinará qué propiedades del catálogo
    maestro de propiedades aplican a este sistema.
    """

    class Categoria(models.TextChoices):
        AGUA = "agua", "Base Agua"
        POLIMERICO = "polimerico", "Polimérico"
        ACEITE = "aceite", "Base Aceite"
        SINTETICO = "sintetico", "Sintético (SBM)"
        OTRO = "otro", "Otro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(
        max_length=120, unique=True,
        help_text='Nombre específico del sistema, ej. "Lodo Polimérico KCl".',
    )
    categoria = models.CharField(
        max_length=20, choices=Categoria.choices,
        help_text="Categoría base: determina qué propiedades del catálogo maestro aplican.",
    )
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def to_dict(self):
        return {
            "id": str(self.id),
            "nombre": self.nombre,
            "categoria": self.categoria,
            "categoria_display": self.get_categoria_display(),
            "descripcion": self.descripcion,
        }


class Intervalo(models.Model):
    """Manual resumido, Paso 2: Project -> Intervals.

    `tipo` clasifica la sección (Casing / Liner / Open Hole). `profundidad_
    tope_liner_sidetrack` (Top Of Liner / Sidetrack) es obligatorio solo si
    `tipo == LINER` o si `es_sidetrack` está marcado. Cuando `es_sidetrack`
    está marcado, se activa "Reset Start Depth for Sidetrack": la
    profundidad inicial del intervalo se fija automáticamente en esa cota
    (el tope del tapón de cemento), no la ingresa el usuario a mano.
    """

    class Estado(models.TextChoices):
        ABIERTO = "abierto", "Abierto"
        CERRADO = "cerrado", "Cerrado"

    class ModoOperativo(models.TextChoices):
        DRILLING = "drilling", "Drilling"
        COMPLETION = "completion", "Completion"

    class Tipo(models.TextChoices):
        CASING = "casing", "Casing"
        LINER = "liner", "Liner"
        OPEN_HOLE = "open_hole", "Open Hole"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pozo = models.ForeignKey(Pozo, on_delete=models.PROTECT, related_name="intervalos")
    numero = models.PositiveIntegerField()
    modo_operativo = models.CharField(
        max_length=12, choices=ModoOperativo.choices, default=ModoOperativo.DRILLING,
        help_text="Operational Mode: Drilling o Completion.",
    )
    tipo = models.CharField(
        max_length=10, choices=Tipo.choices, default=Tipo.OPEN_HOLE,
        help_text="Type: Casing, Liner u Open Hole.",
    )
    sistema_fluido = models.ForeignKey(
        SistemaFluido, on_delete=models.PROTECT, related_name="intervalos",
        help_text="Sistema de fluido asignado a este intervalo. Fijo mientras el intervalo está abierto.",
    )
    profundidad_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    profundidad_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    diametro = models.DecimalField(
        max_digits=6, decimal_places=3, help_text="Diámetro de hoyo o revestidor, en pulgadas."
    )
    es_sidetrack = models.BooleanField(
        default=False,
        help_text="Si este intervalo se abre por un desvío (side track) del hoyo.",
    )
    profundidad_tope_liner_sidetrack = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Top Of Liner / Sidetrack (ft). Obligatorio si tipo=Liner o es_sidetrack=True.",
    )
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ABIERTO)
    fecha_apertura = models.DateField(auto_now_add=True)
    fecha_cierre = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["pozo", "numero"]
        constraints = [
            models.UniqueConstraint(fields=["pozo", "numero"], name="unico_numero_intervalo_por_pozo"),
        ]

    def __str__(self):
        return f"{self.pozo} - Intervalo {self.numero}"

    @property
    def esta_cerrado(self):
        return self.estado == self.Estado.CERRADO

    def clean(self):
        if self.profundidad_final is not None and self.profundidad_final < self.profundidad_inicial:
            raise ValidationError("La profundidad final no puede ser menor que la profundidad inicial.")

        requiere_tope = self.tipo == self.Tipo.LINER or self.es_sidetrack
        if requiere_tope and self.profundidad_tope_liner_sidetrack is None:
            raise ValidationError(
                "Top Of Liner / Sidetrack (ft) es obligatorio cuando el tipo es Liner o el "
                "intervalo es un side track."
            )

    def save(self, *args, **kwargs):
        # Regla de Sidetrack: "Reset Start Depth for Sidetrack" — la profundidad
        # de arranque se fija en el tope del tapón de cemento, no la decide el
        # usuario a mano.
        if self.es_sidetrack and self.profundidad_tope_liner_sidetrack is not None:
            self.profundidad_inicial = self.profundidad_tope_liner_sidetrack
        super().save(*args, **kwargs)

    def to_dict(self):
        try:
            cierre = self.cierre
            cierre_dict = cierre.to_dict()
        except CierreVolumetrico.DoesNotExist:
            cierre_dict = None

        return {
            "id": str(self.id),
            "pozo_id": str(self.pozo_id),
            "pozo_nombre": self.pozo.nombre,
            "numero": self.numero,
            "modo_operativo": self.modo_operativo,
            "modo_operativo_display": self.get_modo_operativo_display(),
            "tipo": self.tipo,
            "tipo_display": self.get_tipo_display(),
            "sistema_fluido_id": str(self.sistema_fluido_id),
            "sistema_fluido_nombre": self.sistema_fluido.nombre,
            "categoria_sistema": self.sistema_fluido.categoria,
            "categoria_sistema_display": self.sistema_fluido.get_categoria_display(),
            "profundidad_inicial": str(self.profundidad_inicial),
            "profundidad_final": str(self.profundidad_final) if self.profundidad_final is not None else None,
            "diametro": str(self.diametro),
            "es_sidetrack": self.es_sidetrack,
            "profundidad_tope_liner_sidetrack": (
                str(self.profundidad_tope_liner_sidetrack)
                if self.profundidad_tope_liner_sidetrack is not None else None
            ),
            "estado": self.estado,
            "estado_display": self.get_estado_display(),
            "esta_cerrado": self.esta_cerrado,
            "fecha_apertura": self.fecha_apertura.isoformat() if self.fecha_apertura else None,
            "fecha_cierre": self.fecha_cierre.isoformat() if self.fecha_cierre else None,
            "total_tuberias": self.tuberias.count(),
            "cierre": cierre_dict,
        }


class TuberiaInstalada(models.Model):
    """Lo que se metió de hierro en un intervalo (revestidor, liner, etc.).

    Uno a muchos con Intervalo: un mismo intervalo puede tener varios tramos.
    Corresponde a una fila de la tabla "Wellbore Geometry" del manual resumido
    (Paso 5.1: Type, Casing OD, Casing ID, Depth, TVD) — `longitud` es la
    columna "Depth" (profundidad medida/MD de la zapata) y
    `profundidad_tvd` es "TVD" (profundidad vertical verdadera del mismo punto).
    """

    class Tipo(models.TextChoices):
        REVESTIDOR = "revestidor", "Revestidor"
        LINER = "liner", "Liner"
        OTRO = "otro", "Otro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervalo = models.ForeignKey(Intervalo, on_delete=models.CASCADE, related_name="tuberias")
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.REVESTIDOR)
    longitud = models.DecimalField(max_digits=10, decimal_places=2, help_text="Longitud/Depth (MD) en pies.")
    diametro_externo = models.DecimalField(max_digits=6, decimal_places=3, help_text="Casing OD, en pulgadas.")
    diametro_interno = models.DecimalField(max_digits=6, decimal_places=3, help_text="Casing ID, en pulgadas.")
    profundidad_tvd = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="TVD (profundidad vertical verdadera) de la zapata, en pies. Opcional en pozos verticales.",
    )

    class Meta:
        ordering = ["intervalo", "id"]

    def __str__(self):
        return f"{self.get_tipo_display()} {self.diametro_externo}\" - {self.intervalo}"

    def clean(self):
        if self.diametro_interno >= self.diametro_externo:
            raise ValidationError("El diámetro interno debe ser menor que el diámetro externo.")

    def to_dict(self):
        return {
            "id": str(self.id),
            "intervalo_id": str(self.intervalo_id),
            "tipo": self.tipo,
            "tipo_display": self.get_tipo_display(),
            "longitud": str(self.longitud),
            "diametro_externo": str(self.diametro_externo),
            "diametro_interno": str(self.diametro_interno),
            "profundidad_tvd": str(self.profundidad_tvd) if self.profundidad_tvd is not None else None,
        }


class CierreVolumetrico(models.Model):
    """Cierre volumétrico de un intervalo. Uno a uno: solo existe cuando el
    intervalo ya se cerró. Al crearse, marca el Intervalo como cerrado.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervalo = models.OneToOneField(Intervalo, on_delete=models.PROTECT, related_name="cierre")
    volumen_final = models.DecimalField(max_digits=10, decimal_places=2, help_text="Volumen final, en bbl.")
    volumen_no_fluido = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Volumen que queda atrapado bajo la profundidad de cierre (Volume Not Fluids), en bbl.",
    )
    perdida_left_in_hole = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Pérdida registrada para que el balance del intervalo cuadre en cero, en bbl.",
    )
    usuario = models.CharField(max_length=120)
    fecha_cierre = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_cierre"]

    def __str__(self):
        return f"Cierre de {self.intervalo}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            Intervalo.objects.filter(pk=self.intervalo_id).update(
                estado=Intervalo.Estado.CERRADO,
                fecha_cierre=self.fecha_cierre.date() if self.fecha_cierre else None,
            )

    def to_dict(self):
        return {
            "id": str(self.id),
            "intervalo_id": str(self.intervalo_id),
            "volumen_final": str(self.volumen_final),
            "volumen_no_fluido": str(self.volumen_no_fluido),
            "perdida_left_in_hole": str(self.perdida_left_in_hole),
            "usuario": self.usuario,
            "fecha_cierre": self.fecha_cierre.isoformat() if self.fecha_cierre else None,
        }


# ==============================================================================
# MANUAL RESUMIDO, PASO 3 — CATÁLOGOS MAESTROS DE FOSAS Y PÉRDIDAS
# ==============================================================================
#
# Catálogos de proyecto (por Pozo, igual que Well Survey / Lithology / Fluid
# Systems en "Setup del Proyecto.md" — Módulo 3: View Project Information).
# Todavía NO se conectan a la contabilidad volumétrica diaria (eso es el
# Paso 6: Volume Accounting, pendiente): por ahora son catálogos maestros que
# el usuario configura una vez por pozo, listos para que Volume Accounting los
# consuma más adelante. Esto resuelve el pendiente de "Próximos pasos a
# seguir.md" #3: formalizar el catálogo de categorías de pérdida (hoy
# `CierreVolumetrico.perdida_left_in_hole` sigue siendo un monto libre, no una
# categoría del catálogo — se conectará cuando se implemente Volume
# Accounting completo).


class Pit(models.Model):
    """Fosa o tanque del taladro (Pit Setup Tab). Manual resumido 3.1.

    `tipo` usa las categorías operativas fijas del manual (Active, Reserve,
    Premix, Spacer, Storage, Dead Volume) — el manual real distingue además
    valores "predefinidos" (fondo gris, inmutables) de "definidos por el
    usuario" (fondo blanco, editables) dentro de ese catálogo; esa capa
    adicional de catálogo-de-tipos no se implementa todavía, se deja como
    choices fijos por simplicidad.

    `es_transaccional=False` marca una fosa no transaccional (ej. "Base Oil
    Storage"): almacenamiento aislado que no participa del balance diario de
    lodo activo ni acepta Transfer/Dump/Add Chemical transaccional.
    """

    class TipoFosa(models.TextChoices):
        ACTIVE = "active", "Active"
        RESERVE = "reserve", "Reserve"
        PREMIX = "premix", "Premix"
        SPACER = "spacer", "Spacer"
        STORAGE = "storage", "Storage"
        DEAD_VOLUME = "dead_volume", "Dead Volume"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pozo = models.ForeignKey(Pozo, on_delete=models.PROTECT, related_name="pits")
    descripcion = models.CharField(
        max_length=80, help_text='Nombre único de la fosa, ej. "Active 1", "Reserve 1", "Premix 1".',
    )
    capacidad = models.DecimalField(max_digits=10, decimal_places=2, help_text="Capacidad volumétrica máxima, en bbl.")
    tipo = models.CharField(max_length=20, choices=TipoFosa.choices, default=TipoFosa.ACTIVE)
    es_transaccional = models.BooleanField(
        default=True,
        help_text=(
            "Si es False, es una fosa/tanque no transaccional (almacenamiento aislado, "
            "ej. Base Oil Storage): no participa del balance diario de lodo activo."
        ),
    )

    class Meta:
        ordering = ["pozo", "descripcion"]
        constraints = [
            models.UniqueConstraint(fields=["pozo", "descripcion"], name="unica_descripcion_fosa_por_pozo"),
        ]
        verbose_name = "Fosa / Tanque"
        verbose_name_plural = "Fosas / Tanques"

    def __str__(self):
        return f"{self.descripcion} ({self.pozo})"

    def clean(self):
        if self.pozo_id and self.descripcion:
            duplicado = Pit.objects.filter(pozo_id=self.pozo_id, descripcion__iexact=self.descripcion.strip())
            if self.pk:
                duplicado = duplicado.exclude(pk=self.pk)
            if duplicado.exists():
                raise ValidationError(f'Ya existe una fosa llamada "{self.descripcion}" en este pozo.')

    def to_dict(self):
        return {
            "id": str(self.id),
            "pozo_id": str(self.pozo_id),
            "descripcion": self.descripcion,
            "capacidad": str(self.capacidad),
            "tipo": self.tipo,
            "tipo_display": self.get_tipo_display(),
            "es_transaccional": self.es_transaccional,
        }


class CategoriaPerdida(models.Model):
    """Catálogo cerrado de motivos de pérdida (Loss Setup Tab). Manual
    resumido 3.2.

    Aislamiento de dominios: las categorías NO se comparten entre modos
    operativos — se configuran por separado para Drilling y Completion
    (`modo_operativo` es parte de la restricción de unicidad, no un simple
    filtro). `dominio` distingue las pérdidas superficiales (Shakers,
    Centrifuges, Surface/Dumped, Evaporation) de las subsuperficiales
    (Losses to Formation, Left in Hole), tal como las agrupa el manual.
    """

    class ModoOperativo(models.TextChoices):
        DRILLING = "drilling", "Drilling"
        COMPLETION = "completion", "Completion"

    class Dominio(models.TextChoices):
        SUPERFICIAL = "superficial", "Superficial"
        SUBSUPERFICIAL = "subsuperficial", "Subsuperficial"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pozo = models.ForeignKey(Pozo, on_delete=models.PROTECT, related_name="categorias_perdida")
    modo_operativo = models.CharField(max_length=12, choices=ModoOperativo.choices)
    nombre = models.CharField(max_length=80, help_text='Ej. "Shakers", "Evaporation", "Left in Hole".')
    dominio = models.CharField(max_length=20, choices=Dominio.choices)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["pozo", "modo_operativo", "dominio", "nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["pozo", "modo_operativo", "nombre"], name="unica_categoria_perdida_por_pozo_y_modo"
            ),
        ]
        verbose_name = "Categoría de pérdida"
        verbose_name_plural = "Categorías de pérdida (Loss Setup)"

    def __str__(self):
        return f"{self.nombre} ({self.get_modo_operativo_display()}) - {self.pozo}"

    def to_dict(self):
        return {
            "id": str(self.id),
            "pozo_id": str(self.pozo_id),
            "modo_operativo": self.modo_operativo,
            "modo_operativo_display": self.get_modo_operativo_display(),
            "nombre": self.nombre,
            "dominio": self.dominio,
            "dominio_display": self.get_dominio_display(),
            "descripcion": self.descripcion,
        }


class Producto(models.Model):
    """Catálogo de productos/materiales. El antiguo campo libre `presentacion`
    (ej. "100. LB BG", "5. GA CN") se separó en sus 3 componentes reales,
    confirmados contra la columna "Unit Size" de `Chem. Inv (DF)` en el mud
    report de referencia: cantidad unitaria, unidad de medida y tipo de
    empaque. Esta separación es la que permite calcular el libraje final
    (sección 7.1 del contexto del proyecto) en vez de tenerlo como texto.
    """

    class UnidadMedida(models.TextChoices):
        LB = "LB", "Libras (LB)"
        KG = "KG", "Kilogramos (KG)"
        GA = "GA", "Galones (GA)"
        EA = "EA", "Unidad (EA) — sin conversión de peso"

    class TipoEmpaque(models.TextChoices):
        BG = "BG", "Saco / Bolsa (BG)"
        CN = "CN", "Lata / Cuñete (CN)"
        DM = "DM", "Tambor (DM)"
        TOTE = "TOTE", "Tote"
        BLS = "BLS", "Barril (BLS)"
        EA = "EA", "Unidad (EA) — sin empaque físico, ej. servicios"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50, unique=True)

    cantidad_unitaria = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Cantidad por unidad de empaque (ej. 100, 50, 25, 5). Primer dato del antiguo Unit Size.",
    )
    unidad_medida = models.CharField(
        max_length=2, choices=UnidadMedida.choices,
        help_text="Unidad de esa cantidad (LB, KG, GA...). Segundo dato del antiguo Unit Size.",
    )
    tipo_empaque = models.CharField(
        max_length=4, choices=TipoEmpaque.choices,
        help_text="Empaque en que viene esa cantidad (BG, CN, DM...). Tercer dato del antiguo Unit Size.",
    )

    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Precio por unidad de empaque (por saco/tambor/lata/etc.), no por libra. Puede cambiar entre reportes.",
    )
    gravedad_especifica = models.DecimalField(max_digits=5, decimal_places=3)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    @property
    def presentacion(self):
        """Reconstruye el texto tipo "100. LB BG" para mostrarlo en reportes/planillas.
        Caso especial "1.  EA" (servicios sin empaque físico): no repite EA dos veces.
        """
        cantidad = self.cantidad_unitaria
        cantidad_str = f"{cantidad:g}" if cantidad == cantidad.to_integral_value() else str(cantidad)
        if self.unidad_medida == self.UnidadMedida.EA:
            return f"{cantidad_str}.  {self.tipo_empaque}"
        return f"{cantidad_str}. {self.unidad_medida} {self.tipo_empaque}"

    def libraje(self, cantidad_empaques):
        """Libraje final = libraje unitario × cantidad de empaques (sección 7.1).

        `cantidad_empaques` es el número de sacos/tambores/latas/etc., no el
        peso. Ej.: Producto(cantidad_unitaria=100, unidad_medida=LB) con
        cantidad_empaques=5 → libraje = 500 LB.
        """
        return self.cantidad_unitaria * cantidad_empaques

    def to_dict(self):
        return {
            "id": str(self.id),
            "nombre": self.nombre,
            "codigo": self.codigo,
            "cantidad_unitaria": str(self.cantidad_unitaria),
            "unidad_medida": self.unidad_medida,
            "tipo_empaque": self.tipo_empaque,
            "presentacion": self.presentacion,
            "precio_unitario": str(self.precio_unitario),
            "gravedad_especifica": str(self.gravedad_especifica),
        }


class ReporteDiario(models.Model):
    """El encabezado del reporte del día. Cuelga de Intervalo, no de Pozo
    directamente, para heredar su contexto (incluyendo sistema_fluido) y
    respetar el bloqueo de cierre.

    Los 3 campos de geometría (`bit_depth`, `bit_size`, `porcentaje_washout`)
    corresponden al manual resumido, Paso 5 ("Daily -> Geometry"): son
    valores del día (la broca avanza y el % de ensanchamiento se reevalúa
    reporte a reporte), a diferencia de la tubería instalada (revestidor/
    liner), que es del Intervalo porque no cambia día a día.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervalo = models.ForeignKey(Intervalo, on_delete=models.PROTECT, related_name="reportes")
    fecha = models.DateField()
    numero_reporte = models.PositiveIntegerField(
        editable=False, help_text="Correlativo por pozo, asignado automáticamente."
    )
    actividad = models.CharField(max_length=150, blank=True)
    peso_lodo = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # --- Paso 5.1: Wellbore Geometry (Hole Size) ---
    bit_depth = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Bit Depth: profundidad actual de la mecha, en ft.",
    )
    bit_size = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        help_text="Bit Size: diámetro nominal de la mecha, en pulgadas.",
    )
    porcentaje_washout = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, default=0,
        help_text="% Washout (ensanchamiento del hoyo). 0 = hoyo en calibre (gauge hole).",
    )

    class Meta:
        ordering = ["intervalo__pozo", "numero_reporte"]
        constraints = [
            models.UniqueConstraint(
                fields=["intervalo", "fecha"], name="unico_reporte_por_intervalo_y_fecha"
            ),
        ]

    def __str__(self):
        return f"Reporte {self.numero_reporte} - {self.intervalo.pozo}"

    def clean(self):
        if self.intervalo_id and self.intervalo.esta_cerrado:
            raise ValidationError(
                "No se puede crear ni editar un reporte de un intervalo cerrado."
            )

    def save(self, *args, **kwargs):
        self.full_clean(exclude=["numero_reporte"])
        if self._state.adding and not self.numero_reporte:
            with transaction.atomic():
                ultimo = (
                    ReporteDiario.objects.select_for_update()
                    .filter(intervalo__pozo_id=self.intervalo.pozo_id)
                    .aggregate(Max("numero_reporte"))["numero_reporte__max"]
                )
                self.numero_reporte = (ultimo or 0) + 1
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    @property
    def hole_size(self):
        """Hole Size (paso 5.1): diámetro real del hoyo ajustado por el
        ensanchamiento. Si %Washout es 0 (o no se ha registrado), el hoyo
        está "en calibre" y Hole Size = Bit Size."""
        if self.bit_size is None:
            return None
        washout = self.porcentaje_washout or Decimal("0")
        return (self.bit_size * (Decimal("1") + washout / Decimal("100"))).quantize(Decimal("0.001"))

    @property
    def diametro_confinamiento(self):
        """El "ID_hoyo_o_revestidor" que usan las fórmulas de volumen de la
        sarta (paso 5.2): si el intervalo ya tiene tubería instalada (Casing/
        Liner), usa el ID de la más reciente; si no, usa el Hole Size del
        día (hoyo abierto); si tampoco hay Bit Size cargado, cae al
        `Intervalo.diametro` genérico como último recurso."""
        ultima_tuberia = self.intervalo.tuberias.order_by("-id").first()
        if self.intervalo.tipo != Intervalo.Tipo.OPEN_HOLE and ultima_tuberia:
            return ultima_tuberia.diametro_interno
        if self.hole_size is not None:
            return self.hole_size
        return self.intervalo.diametro

    def to_dict(self):
        return {
            "id": str(self.id),
            "intervalo_id": str(self.intervalo_id),
            "pozo_nombre": self.intervalo.pozo.nombre,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "numero_reporte": self.numero_reporte,
            "actividad": self.actividad,
            "peso_lodo": str(self.peso_lodo) if self.peso_lodo is not None else None,
            "bit_depth": str(self.bit_depth) if self.bit_depth is not None else None,
            "bit_size": str(self.bit_size) if self.bit_size is not None else None,
            "porcentaje_washout": str(self.porcentaje_washout) if self.porcentaje_washout is not None else None,
            "hole_size": str(self.hole_size) if self.hole_size is not None else None,
            "diametro_confinamiento": str(self.diametro_confinamiento),
            "total_muestras": self.muestras.count(),
            "total_tramos_sarta": self.tramos_sarta.count(),
        }


class TramoSarta(models.Model):
    """Fila de la tabla "Drill String Geometry" del manual resumido (Paso
    5.2): modela tubular por tubular lo que cuelga dentro del pozo ese día
    (Drill Pipe, Heavy Weight, Drill Collar, Sub).

    Regla de la "celda amarilla" (fórmula de longitud automática): el tramo
    marcado `es_principal` (el Drill Pipe superior) NO recibe su longitud
    por input — se calcula siempre como
    `Bit Depth − Σ longitud de los demás tramos` (el resto de la sarta,
    BHA) y se recalcula en cada `save()`. Solo puede haber un tramo
    `es_principal=True` por reporte.
    """

    class Tipo(models.TextChoices):
        DRILL_PIPE = "drill_pipe", "Drill Pipe"
        HEAVY_WEIGHT = "heavy_weight", "Heavy Weight"
        DRILL_COLLAR = "drill_collar", "Drill Collar"
        SUB = "sub", "Sub"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name="tramos_sarta")
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.DRILL_PIPE)
    es_principal = models.BooleanField(
        default=False,
        help_text="Tramo con longitud autocalculada (Bit Depth − resto de la sarta). Como máximo uno por reporte.",
    )
    longitud = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Longitud (ft). Si es_principal=True se recalcula siempre al guardar; el valor enviado se ignora.",
    )
    diametro_externo = models.DecimalField(max_digits=6, decimal_places=3, help_text="Pipe OD, en pulgadas.")
    diametro_interno = models.DecimalField(max_digits=6, decimal_places=3, help_text="Pipe ID, en pulgadas.")
    tool_joint_od = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True, help_text="Tool Jt OD, en pulgadas.",
    )
    tool_joint_id = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True, help_text="Tool Jt ID, en pulgadas.",
    )
    longitud_tool_joint = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, help_text="TJ Length, en pulgadas.",
    )
    orden = models.PositiveIntegerField(default=0, help_text="Orden de la tabla, de arriba (superficie) hacia abajo.")

    class Meta:
        ordering = ["reporte", "orden"]
        verbose_name = "Tramo de sarta"
        verbose_name_plural = "Tramos de sarta (Drill String Geometry)"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.reporte}"

    def clean(self):
        if self.diametro_interno >= self.diametro_externo:
            raise ValidationError("Pipe ID debe ser menor que Pipe OD.")
        if self.reporte_id and self.reporte.intervalo.esta_cerrado:
            raise ValidationError("No se puede registrar geometría de sarta en un intervalo cerrado.")
        if self.es_principal:
            ya_existe = TramoSarta.objects.filter(reporte_id=self.reporte_id, es_principal=True)
            if self.pk:
                ya_existe = ya_existe.exclude(pk=self.pk)
            if ya_existe.exists():
                raise ValidationError("Ya existe un tramo principal (Drill Pipe autocalculado) en este reporte.")
        elif self.longitud is None:
            raise ValidationError("La longitud es obligatoria para un tramo que no es el principal (BHA).")

    def _longitud_calculada(self):
        """Bit Depth − Σ longitud de los demás tramos del mismo reporte (BHA)."""
        if self.reporte.bit_depth is None:
            return None
        suma_bha = (
            TramoSarta.objects.filter(reporte_id=self.reporte_id)
            .exclude(pk=self.pk)
            .exclude(es_principal=True)
            .aggregate(total=models.Sum("longitud"))["total"]
            or Decimal("0")
        )
        return self.reporte.bit_depth - suma_bha

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.es_principal:
            self.longitud = self._longitud_calculada()
        super().save(*args, **kwargs)

    @property
    def capacidad_interna_bbl(self):
        """Capacidad interior de sarta: (Pipe ID² / 1029.4) × Length."""
        if self.longitud is None:
            return None
        return ((self.diametro_interno ** 2) / Decimal("1029.4") * self.longitud).quantize(Decimal("0.0001"))

    @property
    def volumen_anular_bbl(self):
        """Capacidad anular: ((ID_hoyo_o_revestidor² − Pipe OD²) / 1029.4) × Length.

        Usa `ReporteDiario.diametro_confinamiento` como el ID de hoyo o
        revestidor vigente para este reporte (ver esa propiedad para el
        criterio de selección)."""
        if self.longitud is None:
            return None
        id_confinamiento = self.reporte.diametro_confinamiento
        if id_confinamiento is None:
            return None
        diferencia = (id_confinamiento ** 2) - (self.diametro_externo ** 2)
        if diferencia <= 0:
            return None
        return (diferencia / Decimal("1029.4") * self.longitud).quantize(Decimal("0.0001"))

    def to_dict(self):
        return {
            "id": str(self.id),
            "reporte_id": str(self.reporte_id),
            "tipo": self.tipo,
            "tipo_display": self.get_tipo_display(),
            "es_principal": self.es_principal,
            "longitud": str(self.longitud) if self.longitud is not None else None,
            "diametro_externo": str(self.diametro_externo),
            "diametro_interno": str(self.diametro_interno),
            "tool_joint_od": str(self.tool_joint_od) if self.tool_joint_od is not None else None,
            "tool_joint_id": str(self.tool_joint_id) if self.tool_joint_id is not None else None,
            "longitud_tool_joint": str(self.longitud_tool_joint) if self.longitud_tool_joint is not None else None,
            "orden": self.orden,
            "capacidad_interna_bbl": str(self.capacidad_interna_bbl) if self.capacidad_interna_bbl is not None else None,
            "volumen_anular_bbl": str(self.volumen_anular_bbl) if self.volumen_anular_bbl is not None else None,
        }


class MovimientoProducto(models.Model):
    """Clase base abstracta: InventarioItem y UsoMaterial comparten reporte,
    producto y la validación de intervalo cerrado.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name="%(class)ss")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    class Meta:
        abstract = True

    def clean(self):
        if self.reporte_id and self.reporte.intervalo.esta_cerrado:
            raise ValidationError("No se puede registrar movimientos en un intervalo cerrado.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class InventarioItem(MovimientoProducto):
    """Existencia inicial y recepción de un producto en el reporte del día."""

    cantidad_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_entrada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_final = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta(MovimientoProducto.Meta):
        constraints = [
            models.UniqueConstraint(fields=["reporte", "producto"], name="unico_inventario_por_reporte_y_producto"),
        ]

    def __str__(self):
        return f"{self.producto} - {self.reporte}"

    def save(self, *args, **kwargs):
        total_usado = self.reporte.usomaterials.filter(producto=self.producto).aggregate(
            total=models.Sum("cantidad_usada")
        )["total"] or 0
        self.cantidad_final = self.cantidad_inicial + self.cantidad_entrada - total_usado
        super().save(*args, **kwargs)

    @property
    def libraje_final(self):
        """Libraje del stock final, en la unidad_medida del producto (ej. LB, KG)."""
        return self.producto.libraje(self.cantidad_final)

    def to_dict(self):
        return {
            "id": str(self.id),
            "reporte_id": str(self.reporte_id),
            "producto_id": str(self.producto_id),
            "producto_nombre": self.producto.nombre,
            "cantidad_inicial": str(self.cantidad_inicial),
            "cantidad_entrada": str(self.cantidad_entrada),
            "cantidad_final": str(self.cantidad_final),
            "libraje_final": str(self.libraje_final),
        }


class UsoMaterial(MovimientoProducto):
    """Cada transacción individual de consumo. El reporte va acumulando
    estas transacciones a lo largo del día (mañana, tarde, etc.)."""

    cantidad_usada = models.DecimalField(max_digits=10, decimal_places=2)
    hora_registro = models.TimeField(auto_now_add=True)

    class Meta(MovimientoProducto.Meta):
        ordering = ["reporte", "hora_registro"]

    def __str__(self):
        return f"{self.producto} x{self.cantidad_usada} - {self.reporte}"

    @property
    def libraje_usado(self):
        """Libraje = libraje unitario del producto × cantidad de empaques usados (sección 7.1)."""
        return self.producto.libraje(self.cantidad_usada)

    @property
    def subtotal_costo(self):
        """Costo = cantidad usada × precio unitario (sección 5). Nunca se guarda
        manual: sale siempre del precio_unitario vigente del producto."""
        return self.cantidad_usada * self.producto.precio_unitario

    def to_dict(self):
        return {
            "id": str(self.id),
            "reporte_id": str(self.reporte_id),
            "producto_id": str(self.producto_id),
            "producto_nombre": self.producto.nombre,
            "cantidad_usada": str(self.cantidad_usada),
            "hora_registro": self.hora_registro.isoformat() if self.hora_registro else None,
            "libraje_usado": str(self.libraje_usado),
            "subtotal_costo": str(self.subtotal_costo),
        }


# ==============================================================================
# MISIÓN 4 — MATRIZ DE PROPIEDADES SELECTIVAS
# ==============================================================================
#
# Catálogo maestro de propiedades (PropiedadCatalogo), qué propiedades aplican
# a cada categoría de SistemaFluido (PropiedadSistema = "la matriz"), y los
# valores cargados por muestra en cada reporte (MuestraFluido + PropiedadValor).
#
# Decisión confirmada: un reporte no tiene un solo valor por propiedad — tiene
# varias muestras en el día (ej. "TK 2 20:00", "TK 2 12:00"), cada una con su
# propio valor de cada propiedad activa. Las propiedades que en el mud report
# real vienen como par (R600/R300, R200/R100, R6/R3, Pf/Mf) se separaron en
# campos numéricos independientes en el catálogo, en vez de un solo texto libre.
# La categoría "polimerico" reutiliza el mismo catálogo que "agua" (confirmado
# por el usuario: no hay una hoja de referencia separada para polímeros en el
# mud report base).


class PropiedadCatalogo(models.Model):
    """Catálogo maestro de propiedades posibles (peso del lodo, PV, YP, etc.).
    Extraído de las hojas MUD PROPERTIES del Mud Report 16 PERLA-1X (WBM/CALDRIL/
    OBM/SBM Check). No toda propiedad aplica a todo sistema — eso lo define
    PropiedadSistema."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.SlugField(max_length=50, unique=True, help_text='Ej. "mud_weight", "pv", "r600".')
    nombre = models.CharField(max_length=120, help_text='Ej. "Peso del Lodo", "Viscosidad Plástica (PV)".')
    unidad = models.CharField(
        max_length=30, blank=True,
        help_text='Ej. "lb/gal", "cP", "lb/100ft²". Vacío para adimensionales (ej. lecturas R600/R300).',
    )
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición en el reporte.")

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Propiedad (catálogo)"
        verbose_name_plural = "Propiedades (catálogo)"

    def __str__(self):
        return f"{self.nombre} ({self.unidad})" if self.unidad else self.nombre

    def to_dict(self):
        return {
            "id": str(self.id),
            "codigo": self.codigo,
            "nombre": self.nombre,
            "unidad": self.unidad,
            "orden": self.orden,
        }


class PropiedadSistema(models.Model):
    """La 'matriz': qué propiedad del catálogo maestro aplica a cada categoría
    de SistemaFluido. Se filtra por categoria_sistema (no por instancia de
    SistemaFluido), porque contexto.md sección 4 define la selectividad a
    nivel de tipo de sistema (agua/polimérico/aceite/sintético)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    propiedad = models.ForeignKey(PropiedadCatalogo, on_delete=models.CASCADE, related_name="sistemas")
    categoria_sistema = models.CharField(max_length=20, choices=SistemaFluido.Categoria.choices)
    obligatoria = models.BooleanField(
        default=True,
        help_text="Si debe estar cargada para poder cerrar el reporte del día (cierre a las 12:00 a.m., sección 4).",
    )

    class Meta:
        ordering = ["categoria_sistema", "propiedad__orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["propiedad", "categoria_sistema"], name="unica_propiedad_por_categoria_sistema"
            ),
        ]
        verbose_name = "Propiedad × Sistema (matriz)"
        verbose_name_plural = "Propiedades × Sistema (matriz)"

    def __str__(self):
        return f"{self.propiedad} — {self.get_categoria_sistema_display()}"

    def to_dict(self):
        return {
            "id": str(self.id),
            "propiedad_id": str(self.propiedad_id),
            "categoria_sistema": self.categoria_sistema,
            "obligatoria": self.obligatoria,
        }


class MuestraFluido(models.Model):
    """Una muestra tomada durante el día de un ReporteDiario (ej. 'TK 2 20:00').
    Cada reporte puede tener varias muestras (mañana/tarde, distintos tanques),
    tal como aparece en la fila 'Sample From' del mud report real."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name="muestras")
    identificador = models.CharField(max_length=60, help_text='Ej. "TK 2 20:00", "TK 1 12:00".')
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["reporte", "orden"]
        verbose_name = "Muestra de fluido"
        verbose_name_plural = "Muestras de fluido"

    def __str__(self):
        return f"{self.identificador} — {self.reporte}"

    def clean(self):
        if self.reporte_id and self.reporte.intervalo.esta_cerrado:
            raise ValidationError("No se pueden registrar muestras en un intervalo cerrado.")

    def to_dict(self):
        return {
            "id": str(self.id),
            "reporte_id": str(self.reporte_id),
            "identificador": self.identificador,
            "orden": self.orden,
            "valores": [v.to_dict() for v in self.valores.select_related("propiedad").all()],
        }


class PropiedadValor(models.Model):
    """El valor de una propiedad en una muestra concreta. Se guarda como
    Decimal — todas las propiedades del catálogo son numéricas porque los
    pares del mud report (R600/R300, Pf/Mf, etc.) ya se separaron en campos
    independientes en PropiedadCatalogo (ej. r600 y r300 por separado)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    muestra = models.ForeignKey(MuestraFluido, on_delete=models.CASCADE, related_name="valores")
    propiedad = models.ForeignKey(PropiedadCatalogo, on_delete=models.PROTECT, related_name="valores")
    valor = models.DecimalField(max_digits=12, decimal_places=4)

    class Meta:
        ordering = ["muestra", "propiedad__orden"]
        constraints = [
            models.UniqueConstraint(fields=["muestra", "propiedad"], name="unico_valor_por_muestra_y_propiedad"),
        ]
        verbose_name = "Valor de propiedad"
        verbose_name_plural = "Valores de propiedad"

    def __str__(self):
        return f"{self.propiedad.nombre} = {self.valor} ({self.muestra})"

    def clean(self):
        if self.muestra_id and self.muestra.reporte.intervalo.esta_cerrado:
            raise ValidationError("No se pueden registrar valores de propiedad en un intervalo cerrado.")

        if self.muestra_id and self.propiedad_id:
            categoria = self.muestra.reporte.intervalo.sistema_fluido.categoria
            aplica = PropiedadSistema.objects.filter(
                propiedad=self.propiedad, categoria_sistema=categoria
            ).exists()
            if not aplica:
                raise ValidationError(
                    f"La propiedad '{self.propiedad.nombre}' no está habilitada para el "
                    f"sistema de fluido de categoría '{categoria}' de este intervalo."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": str(self.id),
            "muestra_id": str(self.muestra_id),
            "propiedad_id": str(self.propiedad_id),
            "propiedad_codigo": self.propiedad.codigo,
            "propiedad_nombre": self.propiedad.nombre,
            "propiedad_unidad": self.propiedad.unidad,
            "valor": str(self.valor),
        }


# ==============================================================================
# EQUIPOS Y COMENTARIOS (sección 3, puntos 7 y 8 del contexto del proyecto)
# ==============================================================================
#
# Mismo patrón que Producto/UsoMaterial: Equipo es el catálogo (código, nombre,
# costo diario vigente — puede cambiar entre reportes, igual que el precio de
# un producto), y UsoEquipo es el movimiento real dentro de un ReporteDiario
# (horas usadas ese día). El costo se calcula siempre a partir de la tarifa
# diaria prorrateada por las horas usadas — nunca se guarda a mano.
#
# Comentario es un log simple de observaciones por reporte, sin más lógica que
# el bloqueo estándar de intervalo cerrado.


class Equipo(models.Model):
    """Catálogo de equipos (bombas, zarandas, centrífugas, etc.)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50, unique=True)
    costo_diario = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Tarifa diaria vigente. Puede cambiar entre reportes, igual que el precio de un producto.",
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    def to_dict(self):
        return {
            "id": str(self.id),
            "nombre": self.nombre,
            "codigo": self.codigo,
            "costo_diario": str(self.costo_diario),
        }


class UsoEquipo(models.Model):
    """Uso de un equipo dentro de un ReporteDiario: cuántas horas se usó ese
    día. El costo se prorratea de la tarifa diaria del equipo según las horas
    usadas sobre 24 (sección 5 del contexto: el costo siempre sale de una
    fórmula, nunca se ingresa a mano)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name="usos_equipo")
    equipo = models.ForeignKey(Equipo, on_delete=models.PROTECT, related_name="usos")
    horas_usadas = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["reporte", "id"]

    def __str__(self):
        return f"{self.equipo} x{self.horas_usadas}h - {self.reporte}"

    @property
    def subtotal_costo(self):
        """Costo = tarifa diaria del equipo × (horas usadas / 24)."""
        return (self.equipo.costo_diario * self.horas_usadas / Decimal("24")).quantize(Decimal("0.01"))

    def clean(self):
        if self.reporte_id and self.reporte.intervalo.esta_cerrado:
            raise ValidationError("No se puede registrar uso de equipo en un intervalo cerrado.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": str(self.id),
            "reporte_id": str(self.reporte_id),
            "equipo_id": str(self.equipo_id),
            "equipo_nombre": self.equipo.nombre,
            "equipo_codigo": self.equipo.codigo,
            "horas_usadas": str(self.horas_usadas),
            "costo_diario": str(self.equipo.costo_diario),
            "subtotal_costo": str(self.subtotal_costo),
        }


class Comentario(models.Model):
    """Observaciones/comentarios generales de un ReporteDiario."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name="comentarios")
    texto = models.TextField()
    autor = models.CharField(max_length=120, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["reporte", "fecha_hora"]

    def __str__(self):
        return f"Comentario de {self.reporte} ({self.fecha_hora:%Y-%m-%d %H:%M})"

    def clean(self):
        if self.reporte_id and self.reporte.intervalo.esta_cerrado:
            raise ValidationError("No se pueden agregar comentarios a un intervalo cerrado.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": str(self.id),
            "reporte_id": str(self.reporte_id),
            "texto": self.texto,
            "autor": self.autor,
            "fecha_hora": self.fecha_hora.isoformat() if self.fecha_hora else None,
        }
