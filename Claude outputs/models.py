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
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Max


class Pozo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=120)
    operador = models.CharField(max_length=120)
    ubicacion = models.CharField(max_length=120)
    campo_area = models.CharField(max_length=120, blank=True)
    fecha_spud = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


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


class Intervalo(models.Model):
    class Estado(models.TextChoices):
        ABIERTO = "abierto", "Abierto"
        CERRADO = "cerrado", "Cerrado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pozo = models.ForeignKey(Pozo, on_delete=models.PROTECT, related_name="intervalos")
    numero = models.PositiveIntegerField()
    sistema_fluido = models.ForeignKey(
        SistemaFluido, on_delete=models.PROTECT, related_name="intervalos",
        help_text="Sistema de fluido asignado a este intervalo. Fijo mientras el intervalo está abierto.",
    )
    profundidad_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    profundidad_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    diametro = models.DecimalField(
        max_digits=6, decimal_places=3, help_text="Diámetro de hoyo o revestidor, en pulgadas."
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


class TuberiaInstalada(models.Model):
    """Lo que se metió de hierro en un intervalo (revestidor, liner, etc.).

    Uno a muchos con Intervalo: un mismo intervalo puede tener varios tramos.
    """

    class Tipo(models.TextChoices):
        REVESTIDOR = "revestidor", "Revestidor"
        LINER = "liner", "Liner"
        OTRO = "otro", "Otro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervalo = models.ForeignKey(Intervalo, on_delete=models.CASCADE, related_name="tuberias")
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.REVESTIDOR)
    longitud = models.DecimalField(max_digits=10, decimal_places=2, help_text="Longitud en pies.")
    diametro_externo = models.DecimalField(max_digits=6, decimal_places=3, help_text="OD en pulgadas.")
    diametro_interno = models.DecimalField(max_digits=6, decimal_places=3, help_text="ID en pulgadas.")

    class Meta:
        ordering = ["intervalo", "id"]

    def __str__(self):
        return f"{self.get_tipo_display()} {self.diametro_externo}\" - {self.intervalo}"

    def clean(self):
        if self.diametro_interno >= self.diametro_externo:
            raise ValidationError("El diámetro interno debe ser menor que el diámetro externo.")


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


class ReporteDiario(models.Model):
    """El encabezado del reporte del día. Cuelga de Intervalo, no de Pozo
    directamente, para heredar su contexto (incluyendo sistema_fluido) y
    respetar el bloqueo de cierre.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervalo = models.ForeignKey(Intervalo, on_delete=models.PROTECT, related_name="reportes")
    fecha = models.DateField()
    numero_reporte = models.PositiveIntegerField(
        editable=False, help_text="Correlativo por pozo, asignado automáticamente."
    )
    actividad = models.CharField(max_length=150, blank=True)
    peso_lodo = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

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
