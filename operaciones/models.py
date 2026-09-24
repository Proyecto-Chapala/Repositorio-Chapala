from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Producto(models.Model):
    CATEGORIA_CHOICES = [
        ('SOLIDO', 'Sólido'),
        ('LIQUIDO', 'Líquido'),
    ]

    ESTADO_CHOICES = [
        ('ALTO', 'Stock Alto'),
        ('MEDIO', 'Stock Medio'),
        ('BAJO', 'Stock Bajo'),
    ]

    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código del Producto",
        help_text="Código único identificador del producto (SKU)"
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name="Descripción"
    )
    unidad = models.CharField(
        max_length=50,
        verbose_name="Unidad / Presentación",
        help_text="Ej: SACOS 55 LBS, TAMBOR 55 GLS, TOTE"
    )
    libraje = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.0,
        verbose_name="Libraje (LBS)",
        help_text="Peso o libraje unitario en libras"
    )
    gravedad = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=1.0,
        verbose_name="Gravedad Específica"
    )
    costo = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0.0,
        verbose_name="Costo Unitario ($)"
    )
    cantidad = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0.0,
        verbose_name="Cantidad (Stock)"
    )
    categoria = models.CharField(
        max_length=10,
        choices=CATEGORIA_CHOICES,
        default='SOLIDO',
        verbose_name="Categoría"
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='ALTO',
        verbose_name="Estado de Stock"
    )
    observacion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observación"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto de Inventario"
        verbose_name_plural = "Productos de Inventario"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

    def clean(self):
        # Normalizar código
        if self.codigo:
            self.codigo = self.codigo.strip()
            # Validar unicidad insensible a mayúsculas
            qs = Producto.objects.filter(codigo__iexact=self.codigo)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({"codigo": f"Ya existe un producto registrado con el código '{self.codigo}'."})

        if self.cantidad is not None and self.cantidad < 0:
            raise ValidationError({"cantidad": "La cantidad no puede ser negativa."})

        # Cálculo automático del estado
        self.estado = self.calcular_estado_automatico()

    def save(self, *args, **kwargs):
        self.estado = self.calcular_estado_automatico()
        super().save(*args, **kwargs)

    def calcular_estado_automatico(self):
        """
        Regla de negocio:
        0 a 20: Stock Bajo
        21 a 50: Stock Medio
        > 50: Stock Alto
        """
        cant = float(self.cantidad or 0)
        if cant <= 20:
            return 'BAJO'
        elif cant <= 50:
            return 'MEDIO'
        return 'ALTO'

    def to_dict(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "unidad": self.unidad,
            "libraje": float(self.libraje),
            "gravedad": float(self.gravedad),
            "costo": float(self.costo),
            "cantidad": float(self.cantidad),
            "categoria": self.categoria,
            "categoria_display": self.get_categoria_display(),
            "estado": self.estado,
            "estado_display": self.get_estado_display(),
            "observacion": self.observacion or "",
            "puede_eliminar": self.cantidad == 0,
        }


class Pozo(models.Model):
    """
    Representa un Pozo (Well), equivalente al archivo .MDB de ONE-TRAX.
    Se crea a través del wizard de 4 pasos. Mientras el wizard está en
    curso, el registro vive en estado BORRADOR (permite autoguardado
    paso a paso); al confirmar el paso 4 pasa a ACTIVO y las unidades
    quedan bloqueadas.
    """

    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador (en creación)'),
        ('ACTIVO', 'Activo'),
        ('CERRADO', 'Cerrado'),
    ]

    SISTEMA_UNIDADES_CHOICES = [
        ('STANDARD_OILFIELD', 'Standard Oilfield'),
        ('STANDARD_1', 'Standard 1 (lb/ft³)'),
        ('STANDARD_2', 'Standard 2 (m)'),
        ('STANDARD_3', 'Standard 3 (m, m/min)'),
        ('SI_METRIC', 'SI Métrico'),
        ('METRIC_1', 'Métrico 1'),
        ('METRIC_2', 'Métrico 2'),
        ('METRIC_3', 'Métrico 3'),
        ('METRIC_4', 'Métrico 4'),
        ('METRIC_5', 'Métrico 5'),
        ('CUSTOM', 'Personalizado'),
    ]

    ECUACION_SOLIDOS_CHOICES = [
        ('MI', 'M-I'),
        ('API', 'API'),
    ]

    CATEGORIA_PERDIDA_CHOICES = [
        ('MI', 'M-I'),
        ('UK', 'UK'),
        ('HYDRO', 'Hydro'),
        ('STATOIL', 'Statoil'),
        ('IFE', 'IFE'),
        ('COMPLETION_FLUIDS', 'Completion Fluids'),
        ('CUSTOM', 'Personalizado'),
    ]

    TIPO_FLUIDO_INICIAL_CHOICES = [
        ('WATER_BASE', 'Base Agua'),
        ('WATER_BASE_CACL2', 'Base Agua (CaCl2)'),
        ('OIL_BASE', 'Base Aceite'),
        ('SYNTHETIC_BASE', 'Base Sintética'),
        ('COMPLETION_FLUIDS', 'Fluidos de Completación'),
    ]

    # --- Paso 1: Datos básicos ---
    nombre = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nombre del Pozo"
    )
    pozo_plantilla = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='pozos_clonados',
        verbose_name="Pozo usado como plantilla"
    )

    # --- Paso 2: Sistema de unidades (INMUTABLE tras activar) ---
    sistema_unidades = models.CharField(
        max_length=20,
        choices=SISTEMA_UNIDADES_CHOICES,
        default='STANDARD_OILFIELD',
        verbose_name="Sistema de Unidades"
    )
    # Nota: cuando sistema_unidades = CUSTOM, el detalle unidad-por-propiedad
    # vive en la tabla relacional PropiedadUnidadPozo (abajo), no en un JSON,
    # para que cada valor quede como fila auditable.
    unidades_bloqueadas = models.BooleanField(
        default=False,
        verbose_name="Unidades Bloqueadas",
        help_text="Se activa automáticamente al confirmar el paso 4 del wizard."
    )

    # --- Paso 4: Financiero (moneda BLOQUEADA tras activar, tax rate editable) ---
    moneda_simbolo = models.CharField(max_length=6, default='USD', verbose_name="Símbolo de Moneda")
    moneda_decimales = models.PositiveSmallIntegerField(default=2, verbose_name="Decimales de Moneda")
    tasa_impuesto = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Tasa de Impuesto (%)"
    )
    ecuacion_solidos_base_agua = models.CharField(
        max_length=5, choices=ECUACION_SOLIDOS_CHOICES, default='MI',
        verbose_name="Ecuación de Sólidos — Base Agua"
    )
    ecuacion_solidos_base_aceite = models.CharField(
        max_length=5, choices=ECUACION_SOLIDOS_CHOICES, default='MI',
        verbose_name="Ecuación de Sólidos — Base Aceite/Sintética"
    )
    usar_api_5ta_edicion_hidraulica = models.BooleanField(
        default=False,
        verbose_name="Usar API 5ta Edición para Cálculo Hidráulico"
    )
    categoria_perdida_tipo = models.CharField(
        max_length=20, choices=CATEGORIA_PERDIDA_CHOICES, default='MI',
        verbose_name="Categorías de Pérdida"
    )

    # --- Pantalla única "Spud Date" (se muestra la 1ra vez que se abre el pozo) ---
    fecha_primera_captura = models.DateField(
        null=True, blank=True,
        verbose_name="Primera Fecha de Datos",
        help_text="Inmutable una vez confirmada. Puede ser anterior a la fecha de spud."
    )
    tipo_fluido_inicial = models.CharField(
        max_length=20, choices=TIPO_FLUIDO_INICIAL_CHOICES,
        null=True, blank=True,
        verbose_name="Tipo de Fluido — Primer Chequeo"
    )
    con_tratamiento_disposicion = models.BooleanField(
        default=False,
        verbose_name="Con Tratamiento y Disposición de Desechos"
    )
    numero_control_logit = models.CharField(
        max_length=50, blank=True,
        verbose_name="Número de Control de Proyecto Log-It"
    )
    spud_date_completado = models.BooleanField(
        default=False,
        verbose_name="Pantalla Spud Date completada"
    )

    # --- Control interno del wizard / estado ---
    estado = models.CharField(
        max_length=10, choices=ESTADO_CHOICES, default='BORRADOR',
        verbose_name="Estado"
    )
    paso_wizard_actual = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Último paso guardado del wizard"
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Creado por"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pozo"
        verbose_name_plural = "Pozos"
        ordering = ['-created_at']

    def __str__(self):
        return self.nombre

    def clonar_configuracion_desde_plantilla(self):
        """
        Copia campos de configuración (NO datos operativos) desde
        self.pozo_plantilla. Se llama en el paso 1 del wizard cuando
        el usuario activa 'usar pozo anterior como plantilla'.
        """
        if not self.pozo_plantilla:
            return
        origen = self.pozo_plantilla
        self.sistema_unidades = origen.sistema_unidades
        self.unidades_personalizadas = origen.unidades_personalizadas
        self.moneda_simbolo = origen.moneda_simbolo
        self.moneda_decimales = origen.moneda_decimales
        self.tasa_impuesto = origen.tasa_impuesto
        self.ecuacion_solidos_base_agua = origen.ecuacion_solidos_base_agua
        self.ecuacion_solidos_base_aceite = origen.ecuacion_solidos_base_aceite
        self.categoria_perdida_tipo = origen.categoria_perdida_tipo
        # Nota: las categorías de pérdida CUSTOM (tabla CategoriaPerdidaItem)
        # y las unidades CUSTOM (tabla PropiedadUnidadPozo) se clonan aparte.

    def clonar_categorias_perdida(self):
        """
        Copia las categorías de pérdida (Loss Setup) desde la plantilla.
        Si la plantilla no tiene, o no hay plantilla, se siembran las
        categorías estándar de ONE-TRAX.
        """
        if self.pozo_plantilla:
            for item in self.pozo_plantilla.categorias_perdida.all():
                CategoriaPerdidaItem.objects.get_or_create(
                    pozo=self, codigo=item.codigo,
                    defaults={'descripcion': item.descripcion, 'tipo': item.tipo},
                )
        if not self.categorias_perdida.exists():
            CategoriaPerdidaItem.sembrar_estandar(self)

    def clonar_unidades_personalizadas(self):
        if not self.pozo_plantilla or self.sistema_unidades != 'CUSTOM':
            return
        for item in self.pozo_plantilla.unidades_personalizadas.all():
            PropiedadUnidadPozo.objects.update_or_create(
                pozo=self,
                propiedad=item.propiedad,
                defaults={'unidad': item.unidad},
            )

    def clonar_fosas_y_tipos(self):
        """
        Copia las Fosas y los TipoFosa (Pit Information) desde la
        plantilla. Si la plantilla no tiene tipos de fosa personalizados
        (o no hay plantilla), se siembran los 7 tipos estándar de ONE-TRAX.
        """
        if self.pozo_plantilla:
            for tf in self.pozo_plantilla.tipos_fosa.all():
                TipoFosa.objects.get_or_create(
                    pozo=self, codigo=tf.codigo, defaults={'descripcion': tf.descripcion}
                )
            for fosa in self.pozo_plantilla.fosas.all():
                Fosa.objects.get_or_create(
                    pozo=self, numero=fosa.numero,
                    defaults={'descripcion': fosa.descripcion, 'capacidad': fosa.capacidad},
                )
        if not self.tipos_fosa.exists():
            TipoFosa.sembrar_estandar(self)

    def activar(self):
        """Confirma el paso 4: bloquea unidades y pasa el pozo a ACTIVO."""
        self.unidades_bloqueadas = True
        self.estado = 'ACTIVO'
        self.save()


class PropiedadUnidadPozo(models.Model):
    """
    Una fila por cada propiedad de ingeniería del pozo cuando
    sistema_unidades = 'CUSTOM' (pantalla 'Unit Selection for New Well').
    Tabla relacional (no JSON) para que cada unidad elegida quede
    como registro auditable e individualmente consultable.
    """

    PROPIEDAD_CHOICES = [
        ('PROFUNDIDAD', 'Profundidad (Depth)'),
        ('HOYO_TUBERIA', 'Hoyo/Tubería (Hole/Pipe Size)'),
        ('VOLUMEN', 'Volumen'),
        ('CAUDAL', 'Caudal (Flow Rate)'),
        ('BOQUILLA_BROCA', 'Tamaño de Boquilla (Bit-Nozzle Size)'),
        ('VELOCIDAD', 'Velocidad'),
        ('PRESION', 'Presión'),
        ('FACTOR_K', 'Factor K'),
        ('PESO_FLUIDO', 'Peso de Fluido'),
        ('VISCOSIDAD_PLASTICA', 'Viscosidad Plástica'),
        ('PUNTO_CEDENCIA_GELES', 'Punto de Cedencia y Geles'),
        ('VELOCIDAD_CHORRO', 'Velocidad de Chorro (Jet Velocity)'),
        ('CONCENTRACION_PRODUCTO', 'Concentración de Producto'),
        ('FUERZA', 'Fuerza'),
        ('TEMPERATURA', 'Temperatura'),
        ('ESPESOR_TORTA', 'Espesor de Revoque (Filter-Cake Thickness)'),
    ]

    # Opciones válidas de unidad por propiedad — se usa para poblar el
    # <select> del paso 2 del wizard y para validar en el backend.
    OPCIONES_UNIDAD = {
        'PROFUNDIDAD': ['ft', 'm'],
        'HOYO_TUBERIA': ['in', 'mm'],
        'VOLUMEN': ['bbl', 'm3', 'L'],
        'CAUDAL': ['gal/min', 'bbl/min', 'L/min', 'm3/min'],
        'BOQUILLA_BROCA': ['1/32"', 'mm'],
        'VELOCIDAD': ['ft/min', 'm/min', 'm/s'],
        'PRESION': ['psi', 'kPa', 'bar'],
        'FACTOR_K': ['lb-s^n/100ft2', 'Pa-s^n'],
        'PESO_FLUIDO': ['lb/gal', 'kg/m3', 'sg'],
        'VISCOSIDAD_PLASTICA': ['cP', 'mPa-s'],
        'PUNTO_CEDENCIA_GELES': ['lb/100ft2', 'Pa'],
        'VELOCIDAD_CHORRO': ['ft/s', 'm/s'],
        'CONCENTRACION_PRODUCTO': ['lb/bbl', 'kg/m3'],
        'FUERZA': ['lbf', 'N'],
        'TEMPERATURA': ['F', 'C'],
        'ESPESOR_TORTA': ['1/32"', 'mm'],
    }

    pozo = models.ForeignKey(
        Pozo, on_delete=models.CASCADE, related_name='unidades_personalizadas'
    )
    propiedad = models.CharField(max_length=30, choices=PROPIEDAD_CHOICES)
    unidad = models.CharField(max_length=20, verbose_name="Unidad Elegida")

    class Meta:
        verbose_name = "Unidad Personalizada del Pozo"
        verbose_name_plural = "Unidades Personalizadas del Pozo"
        unique_together = ('pozo', 'propiedad')
        ordering = ['propiedad']

    def clean(self):
        opciones = self.OPCIONES_UNIDAD.get(self.propiedad, [])
        if opciones and self.unidad not in opciones:
            raise ValidationError({
                'unidad': f"'{self.unidad}' no es una unidad válida para "
                          f"{self.get_propiedad_display()}. Opciones: {', '.join(opciones)}."
            })

    def __str__(self):
        return f"{self.pozo.nombre} — {self.get_propiedad_display()}: {self.unidad}"


class CategoriaPerdidaItem(models.Model):
    """
    Fila editable de 'Loss Data Categories' cuando el pozo usa
    categoria_perdida_tipo = 'CUSTOM'. Ej: Shakers, Evaporation,
    Centrifuge, Formation, Left in Hole, Other.
    """
    TIPO_CHOICES = [
        ('SUPERFICIE', 'Superficie'),
        ('SUBSUELO', 'Subsuelo'),
    ]

    pozo = models.ForeignKey(
        Pozo, on_delete=models.CASCADE, related_name='categorias_perdida'
    )
    codigo = models.PositiveSmallIntegerField(verbose_name="Código")
    descripcion = models.CharField(max_length=100, verbose_name="Descripción")
    tipo = models.CharField(
        max_length=12, choices=TIPO_CHOICES, default='SUPERFICIE',
        verbose_name="Superficie / Subsuelo"
    )

    class Meta:
        verbose_name = "Categoría de Pérdida"
        verbose_name_plural = "Categorías de Pérdida"
        ordering = ['codigo']
        unique_together = ('pozo', 'codigo')

    def __str__(self):
        return f"{self.codigo} - {self.descripcion} ({self.pozo.nombre})"

    CATEGORIAS_ESTANDAR = [
        (1, 'Zarandas', 'SUPERFICIE'),
        (2, 'Otros Sólidos', 'SUPERFICIE'),
        (3, 'Centrífuga', 'SUPERFICIE'),
        (4, 'Viajes (Tripping)', 'SUPERFICIE'),
        (5, 'Evaporación', 'SUPERFICIE'),
        (6, 'Retornado', 'SUPERFICIE'),
        (7, 'Detrás del Revestimiento / En el Hoyo', 'SUBSUELO'),
        (8, 'Perdido en Formación', 'SUBSUELO'),
        (9, 'Cajas de Recortes', 'SUPERFICIE'),
        (10, 'Barridos (Piso Marino)', 'SUBSUELO'),
        (11, 'Descargado', 'SUPERFICIE'),
        (12, 'Limpiador de Lodo', 'SUPERFICIE'),
        (13, 'Líneas de Superficie', 'SUPERFICIE'),
        (14, 'Interfase', 'SUPERFICIE'),
        (15, 'Unidad de Filtración', 'SUPERFICIE'),
    ]

    @classmethod
    def sembrar_estandar(cls, pozo):
        """Crea las categorías de pérdida estándar de ONE-TRAX para un pozo nuevo (si no existen)."""
        for codigo, descripcion, tipo in cls.CATEGORIAS_ESTANDAR:
            cls.objects.get_or_create(
                pozo=pozo, codigo=codigo, defaults={'descripcion': descripcion, 'tipo': tipo}
            )


# ============================================================
# Project Main Screen — sub-pantallas de "Well Information"
# ============================================================

class WellHeaderInfo(models.Model):
    """
    'Well Header Information' — pantalla de 2 pestañas (Well Information +
    Marketing Codes) dentro del Project Main Screen. Un registro por pozo.
    """

    pozo = models.OneToOneField(
        Pozo, on_delete=models.CASCADE, related_name='well_header_info'
    )

    # --- Offshore (obligatorio si es_offshore=True; afecta volumetría) ---
    es_offshore = models.BooleanField(default=False, verbose_name="Proyecto Offshore")
    usa_riser = models.BooleanField(
        default=False, verbose_name="El pozo usa Riser",
        help_text="Si está activo, el riser se incluye como primer tramo del perfil de confinamiento del pozo."
    )
    riser_id_in = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True, verbose_name="Diámetro Interno del Riser (in)"
    )
    riser_length_ft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Longitud del Riser (ft)",
        help_text="Si se deja vacío se asume Air Gap + Water Depth."
    )
    air_gap_ft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Altura Libre — Air Gap (ft)"
    )
    water_depth_ft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Profundidad de Agua (ft)"
    )
    sea_floor_temp_f = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Temperatura del Lecho Marino (°F)"
    )

    # --- Datos del pozo ---
    operador = models.CharField(max_length=150, blank=True, verbose_name="Operador")
    field_area = models.CharField(max_length=150, blank=True, verbose_name="Campo/Área")
    descripcion = models.CharField(max_length=255, blank=True, verbose_name="Descripción")
    ubicacion = models.CharField(max_length=150, blank=True, verbose_name="Ubicación")
    almacen = models.CharField(max_length=150, blank=True, verbose_name="Almacén")
    contratista = models.CharField(max_length=150, blank=True, verbose_name="Contratista")
    nombre_taladro = models.CharField(max_length=150, blank=True, verbose_name="Nombre del Taladro")
    ingeniero_proyecto = models.CharField(max_length=150, blank=True, verbose_name="Ingeniero de Proyecto")
    ingeniero_miswaco_1 = models.CharField(max_length=150, blank=True, verbose_name="Ingeniero M-I SWACO 1")
    ingeniero_miswaco_2 = models.CharField(max_length=150, blank=True, verbose_name="Ingeniero M-I SWACO 2")

    spud_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Spud")
    td_date = models.DateField(null=True, blank=True, verbose_name="Fecha de TD")
    td_days = models.PositiveIntegerField(null=True, blank=True, verbose_name="Días de TD")
    re_entry_depth_ft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Profundidad de Reentrada (ft)"
    )
    latitud_ns_indicador = models.CharField(max_length=20, blank=True, verbose_name="Indicador de Latitud N/S")
    longitud_ew_indicador = models.CharField(max_length=20, blank=True, verbose_name="Indicador de Longitud E/O")

    # --- API 5ta edición (opcional, mejora precisión de hidráulica) ---
    surface_temp_f = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Temperatura Superficial (°F)"
    )
    temp_gradient_f_100ft = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Gradiente de Temperatura (°F/100ft)"
    )

    # --- Fin del pozo (se completa al finalizar el pozo) ---
    total_depth_ft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Profundidad Total (ft)"
    )
    total_days = models.PositiveIntegerField(null=True, blank=True, verbose_name="Días Totales")
    maximum_temperature_f = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Temperatura Máxima (°F)"
    )
    tvd_ft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="TVD (ft)"
    )
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Fin")
    total_cost = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Costo Total ($)",
        help_text="Calculado; se deja manual hasta integrar el módulo de costos."
    )
    horiz_displacement_ft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Desplazamiento Horizontal (ft)",
        help_text="Se usa para identificar pozos de Alcance Extendido (Extended Reach)."
    )

    comentarios = models.TextField(blank=True, verbose_name="Comentarios")
    numero_control_logit = models.CharField(
        max_length=50, blank=True, verbose_name="Número de Control de Proyecto Log-It"
    )

    # --- Pestaña 2: Códigos de Mercadeo (código + descripción; catálogo pendiente) ---
    primary_mud_type_codigo = models.CharField(max_length=20, blank=True, verbose_name="Tipo de Lodo Principal — Código")
    primary_mud_type_descripcion = models.CharField(max_length=150, blank=True, verbose_name="Tipo de Lodo Principal")
    well_type_codigo = models.CharField(max_length=20, blank=True, verbose_name="Tipo de Pozo — Código")
    well_type_descripcion = models.CharField(max_length=150, blank=True, verbose_name="Tipo de Pozo")
    contract_type_codigo = models.CharField(max_length=20, blank=True, verbose_name="Tipo de Contrato — Código")
    contract_type_descripcion = models.CharField(max_length=150, blank=True, verbose_name="Tipo de Contrato")
    completion_fluid_type_codigo = models.CharField(max_length=20, blank=True, verbose_name="Tipo de Fluido de Completación — Código")
    completion_fluid_type_descripcion = models.CharField(max_length=150, blank=True, verbose_name="Tipo de Fluido de Completación")

    completado = models.BooleanField(default=False, verbose_name="Información del Pozo guardada al menos una vez")
    marketing_codes_completado = models.BooleanField(default=False, verbose_name="Códigos de Mercadeo guardados al menos una vez")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Información General del Pozo"
        verbose_name_plural = "Información General del Pozo"

    def __str__(self):
        return f"Información General — {self.pozo.nombre}"

    def clean(self):
        if self.es_offshore:
            faltantes = []
            if self.air_gap_ft is None:
                faltantes.append("Air Gap")
            if self.water_depth_ft is None:
                faltantes.append("Water Depth")
            if self.sea_floor_temp_f is None:
                faltantes.append("Sea Floor Temp")
            if faltantes:
                raise ValidationError(
                    "Los proyectos Offshore deben completar: " + ", ".join(faltantes) + "."
                )


class IntervaloRevestimiento(models.Model):
    """'Well Casing Intervals (Cost)' — una fila por intervalo de revestimiento."""

    TIPO_CHOICES = [
        ('CONDUCTOR', 'Conductor'),
        ('SUPERFICIE', 'Superficie'),
        ('INTERMEDIO', 'Intermedio'),
        ('PRODUCCION', 'Producción'),
        ('LINER', 'Liner'),
        ('CASING', 'Revestimiento'),
        ('HOYO_ABIERTO', 'Hoyo Abierto'),
    ]

    pozo = models.ForeignKey(
        Pozo, on_delete=models.CASCADE, related_name='intervalos_revestimiento'
    )
    numero_intervalo = models.PositiveSmallIntegerField(verbose_name="Número de Intervalo")
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, blank=True, verbose_name="Tipo")

    casing_od_in = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name="OD Revestimiento (in)")
    casing_id_in = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name="ID Revestimiento (in)")
    hole_size_in = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name="Diámetro de Hoyo (in)")
    profundidad_ft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Profundidad (ft)")
    tvd_ft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="TVD (ft)")
    top_of_liner_ft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Tope de Liner (ft)")

    maximum_density_lb_gal = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Densidad Máxima (lb/gal)")
    max_bht_f = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Temperatura Máx. de Fondo — BHT (°F)")
    maximum_angle = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Ángulo Máximo")

    interval_days = models.PositiveIntegerField(null=True, blank=True, verbose_name="Días del Intervalo")
    planned_days = models.PositiveIntegerField(null=True, blank=True, verbose_name="Días Planeados")
    planned_length_ft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Longitud Planeada (ft)")

    interval_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Costo del Intervalo ($)")
    planned_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Costo Planeado ($)")
    frac_grad_lb_gal = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Gradiente de Fractura (lb/gal)")

    fluid_type_code_1 = models.CharField(max_length=50, blank=True, verbose_name="Código de Tipo de Fluido 1")
    fluid_type_code_2 = models.CharField(max_length=50, blank=True, verbose_name="Código de Tipo de Fluido 2")

    observaciones_recomendaciones = models.TextField(blank=True, verbose_name="Observaciones y Recomendaciones")
    comentarios_recap = models.TextField(
        blank=True, verbose_name="Comentarios del Intervalo para Recap",
        help_text="Hasta 10,000 caracteres."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Intervalo de Revestimiento (Casing)"
        verbose_name_plural = "Intervalos de Revestimiento (Casing)"
        unique_together = ('pozo', 'numero_intervalo')
        ordering = ['numero_intervalo']

    def clean(self):
        if self.comentarios_recap and len(self.comentarios_recap) > 10000:
            raise ValidationError({'comentarios_recap': "Máximo 10,000 caracteres."})

    def __str__(self):
        return f"{self.pozo.nombre} — Intervalo {self.numero_intervalo}"


class TipoFosa(models.Model):
    """
    'Pit Type Setup' — catálogo de tipos de fosa por pozo (clonable desde
    plantilla). Por defecto se siembran los 7 tipos estándar de ONE-TRAX;
    se pueden agregar tipos adicionales (ej: Base Oil, Brine).
    """

    TIPOS_ESTANDAR = [
        (0, 'Vacía'),
        (1, 'Activa'),
        (2, 'Reserva'),
        (3, 'Premix'),
        (4, 'Espaciador'),
        (5, 'Píldora'),
        (6, 'Rompedor'),
    ]

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='tipos_fosa')
    codigo = models.PositiveSmallIntegerField(verbose_name="#")
    descripcion = models.CharField(max_length=100, verbose_name="Descripción")

    class Meta:
        verbose_name = "Tipo de Fosa"
        verbose_name_plural = "Tipos de Fosa"
        unique_together = ('pozo', 'codigo')
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

    @classmethod
    def sembrar_estandar(cls, pozo):
        """Crea los 7 tipos de fosa estándar para un pozo nuevo (si no existen)."""
        for codigo, descripcion in cls.TIPOS_ESTANDAR:
            cls.objects.get_or_create(pozo=pozo, codigo=codigo, defaults={'descripcion': descripcion})


class Fosa(models.Model):
    """
    'Pits and Tanks Information' — fosas/tanques físicos del sistema de
    lodo del pozo. El nombre es solo descriptivo; el uso real diario lo
    determina el TipoFosa elegido en Volume Accounting (módulo aún no
    construido).
    """

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='fosas')
    numero = models.PositiveSmallIntegerField(verbose_name="N° de Fosa")
    descripcion = models.CharField(max_length=100, verbose_name="Descripción")
    capacidad = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Capacidad")

    class Meta:
        verbose_name = "Fosa / Tanque"
        verbose_name_plural = "Fosas y Tanques"
        unique_together = ('pozo', 'numero')
        ordering = ['numero']

    def __str__(self):
        return f"{self.pozo.nombre} — Pit #{self.numero} ({self.descripcion})"


# ============================================================
# General Setup — Warehouse Code Setup + Time Distribution Setup
# ============================================================

class AlmacenCodigo(models.Model):
    """
    'Warehouse Code Setup' — catálogo de almacenes/bodegas usados en el
    proyecto (pozo). Se pueden agregar en cualquier momento; no trae
    datos precargados, el usuario los define.
    """

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='almacenes')
    codigo = models.CharField(max_length=15, verbose_name="Código")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Almacén")

    class Meta:
        verbose_name = "Código de Almacén"
        verbose_name_plural = "Códigos de Almacén"
        unique_together = ('pozo', 'codigo')
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class TipoDistribucionTiempo(models.Model):
    """
    'Time Distribution Setup' — catálogo de categorías que describen la
    actividad del taladro durante un período de 24h. Se siembra con el
    catálogo estándar de ONE-TRAX al crear el pozo; se puede editar y
    ampliar libremente después desde Configuración General.
    """

    TIPO_CHOICES = [
        ('DF', 'DF'),
        ('CF', 'CF'),
        ('DF/CF', 'DF/CF'),
    ]

    TIPOS_ESTANDAR = [
        (1, 'Alistamiento / Servicio del Taladro', 'DF/CF'),
        (2, 'Perforación', 'DF/CF'),
        (3, 'Maniobras (Viajes)', 'DF/CF'),
        (4, 'Tiempo No Productivo', 'DF/CF'),
        (5, 'Instalación de BOP', 'DF'),
        (6, 'Prueba de BOP', 'DF'),
        (7, 'Cementación', 'DF'),
        (8, 'Acondicionamiento de Hoyo', 'DF'),
        (9, 'Acondicionamiento de Lodo', 'DF'),
        (10, 'Toma de Núcleos', 'DF'),
        (11, 'Registro Direccional', 'DF'),
        (12, 'Trabajo Direccional', 'DF'),
        (13, 'Pesca', 'DF'),
        (14, 'Pérdida de Circulación', 'DF'),
        (15, 'Rimado', 'DF'),
        (16, 'Reparación del Taladro', 'DF'),
        (17, 'Bajada de Revestimiento', 'DF'),
        (18, 'Pruebas', 'DF'),
        (19, 'Espera de Fraguado de Cemento', 'DF'),
        (20, 'Espera por Clima', 'DF'),
    ]

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='tipos_distribucion_tiempo')
    numero = models.PositiveIntegerField(verbose_name="Número")
    descripcion = models.CharField(max_length=120, verbose_name="Descripción")
    tipo = models.CharField(max_length=5, choices=TIPO_CHOICES, default='DF', verbose_name="Tipo")

    class Meta:
        verbose_name = "Tipo de Distribución de Tiempo"
        verbose_name_plural = "Tipos de Distribución de Tiempo"
        unique_together = ('pozo', 'numero')
        ordering = ['numero']

    def __str__(self):
        return f"{self.numero:05d} - {self.descripcion}"

    @classmethod
    def sembrar_estandar(cls, pozo):
        """Crea el catálogo estándar de distribución de tiempo para un pozo nuevo (si no existe)."""
        for numero, descripcion, tipo in cls.TIPOS_ESTANDAR:
            cls.objects.get_or_create(
                pozo=pozo, numero=numero, defaults={'descripcion': descripcion, 'tipo': tipo}
            )


# ============================================================
# Productos / Equipos / Mallas Activos
# (Active Products/Equipment/Screens)
# ============================================================
# Master Product List = catálogo global "Producto" (módulo Inventario),
# ya existente — se reutiliza tal cual, sin duplicarlo.
# Equipo y MallaZaranda son catálogos maestros globales nuevos,
# equivalentes a "Master Equipment List" y "Master Screen List".

class Equipo(models.Model):
    """Catálogo maestro global de equipos ('Master Equipment List')."""

    TIPO_EQUIPO_CHOICES = [
        ('CENTRIFUGA', 'Centrífuga'),
        ('LIMPIADOR_LODO', 'Limpiador de Lodo (Mud Cleaner)'),
        ('ZARANDA', 'Zaranda (Shale Shaker)'),
        ('SECADOR_RECORTES', 'Secador de Recortes (Cuttings Dryer)'),
        ('SISTEMA_VACIO', 'Sistema de Vacío'),
        ('CONTENEDOR_RECORTES', 'Contenedor de Recortes'),
        ('OTROS', 'Otros'),
    ]

    codigo = models.CharField(max_length=30, unique=True, verbose_name="Código de Equipo")
    nombre = models.CharField(
        max_length=150, verbose_name="Nombre Oficial",
        help_text="Nombre oficial del equipo (equivalente a 'Equip. Detail' de ONE-TRAX); no debería modificarse al usarlo en un pozo."
    )
    tipo_equipo = models.CharField(
        max_length=25, choices=TIPO_EQUIPO_CHOICES, default='OTROS', verbose_name="Tipo de Equipo",
        help_text="Agrupa el equipo para 'Equipment Properties Setup' (Centrífuga, Mud Cleaner, Shale Shaker, etc.)."
    )
    posiciones_malla = models.PositiveSmallIntegerField(
        default=0, verbose_name="Posiciones de Malla",
        help_text="Cuántas mallas lleva el equipo (0 = no usa mallas; máximo 12). "
                  "Ej.: zaranda BEM 3 = 3, BEM 600 = 5. La posición 1 es la más cercana a la línea de flujo."
    )

    POSICIONES_MALLA_MAX = 12

    class Meta:
        verbose_name = "Equipo (Catálogo Maestro)"
        verbose_name_plural = "Equipos (Catálogo Maestro)"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def to_dict(self):
        return {
            "id": self.id, "codigo": self.codigo, "nombre": self.nombre,
            "tipo_equipo": self.tipo_equipo,
            "tipo_equipo_display": self.get_tipo_equipo_display(),
            "posiciones_malla": self.posiciones_malla,
        }


class MallaZaranda(models.Model):
    """Catálogo maestro global de mallas de zaranda ('Master Screen List')."""

    codigo = models.CharField(max_length=30, unique=True, verbose_name="Código de Malla")
    descripcion = models.CharField(max_length=150, verbose_name="Descripción")
    mesh_size = models.PositiveSmallIntegerField(verbose_name="Tamaño de Malla (Mesh)")

    class Meta:
        verbose_name = "Malla de Zaranda (Catálogo Maestro)"
        verbose_name_plural = "Mallas de Zaranda (Catálogo Maestro)"
        ordering = ['mesh_size', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

    def to_dict(self):
        return {
            "id": self.id, "codigo": self.codigo,
            "descripcion": self.descripcion, "mesh_size": self.mesh_size,
        }


class ComponenteSarta(models.Model):
    """
    Catálogo maestro global de componentes de sarta ('Master Drill String Component List').

    Cada fila es un componente físico con sus diámetros característicos: una mecha de
    12¼", un drill collar 8½" x 3", una tubería de perforación 5" x 4.276" con junta
    6.375" x 3.75". Al elegirlo en la tabla de Sarta del reporte diario, los diámetros
    se autocompletan pero quedan editables (requerimiento explícito del ingeniero de
    fluidos: "esos números podrían ser modificables").
    """

    TIPO_CHOICES = [
        ('MECHA', 'Mecha (Bit)'),
        ('MOTOR', 'Motor de Fondo / MWD'),
        ('DRILL_COLLAR', 'Portamecha (Drill Collar)'),
        ('HEAVY_WEIGHT', 'Tubería Pesada (Heavy Weight)'),
        ('DRILL_PIPE', 'Tubería de Perforación (Drill Pipe)'),
        ('ESTABILIZADOR', 'Estabilizador'),
        ('CROSSOVER', 'Crossover / Nipple'),
        ('REVESTIDOR', 'Revestidor (bajando casing)'),
        ('OTROS', 'Otros'),
    ]

    # Tipos cuya geometría incluye juntas (tool joints) que afectan el cálculo volumétrico.
    TIPOS_CON_JUNTA = ('DRILL_PIPE', 'HEAVY_WEIGHT')

    codigo = models.CharField(max_length=30, unique=True, verbose_name="Código del Componente")
    descripcion = models.CharField(max_length=150, verbose_name="Descripción")
    tipo = models.CharField(
        max_length=20, choices=TIPO_CHOICES, default='DRILL_PIPE', verbose_name="Tipo de Componente"
    )

    od_in = models.DecimalField(
        max_digits=8, decimal_places=4, verbose_name="Diámetro Externo — OD (in)"
    )
    id_in = models.DecimalField(
        max_digits=8, decimal_places=4, default=0, verbose_name="Diámetro Interno — ID (in)",
        help_text="0 para componentes macizos o para la mecha."
    )

    tool_joint_od_in = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="OD de Junta (in)"
    )
    tool_joint_id_in = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="ID de Junta (in)"
    )
    tool_joint_length_in = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Largo de Junta (in)",
        help_text="Largo de la junta por tramo, en pulgadas (ONE-TRAX usa 21 in por tramo de 31 ft)."
    )
    largo_tramo_ft = models.DecimalField(
        max_digits=8, decimal_places=2, default=31.0, verbose_name="Largo de Tramo (ft)",
        help_text="Largo nominal de un tramo (joint). Se usa para ponderar el efecto de la junta."
    )

    class Meta:
        verbose_name = "Componente de Sarta (Catálogo Maestro)"
        verbose_name_plural = "Componentes de Sarta (Catálogo Maestro)"
        ordering = ['tipo', '-od_in', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

    def to_dict(self):
        def _f(valor):
            return float(valor) if valor is not None else None

        return {
            "id": self.id,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "tipo": self.tipo,
            "tipo_display": self.get_tipo_display(),
            "od_in": _f(self.od_in),
            "id_in": _f(self.id_in),
            "tool_joint_od_in": _f(self.tool_joint_od_in),
            "tool_joint_id_in": _f(self.tool_joint_id_in),
            "tool_joint_length_in": _f(self.tool_joint_length_in),
            "largo_tramo_ft": _f(self.largo_tramo_ft),
        }


class ProductoActivoPozo(models.Model):
    """
    'Active Product List' — productos del catálogo maestro seleccionados
    para este pozo, con sus datos propios del proyecto (precio, código de
    costo diario, etc.). Se permite más de una fila para el mismo producto
    maestro (ej. mismo código con dos abreviaciones distintas), igual que
    en ONE-TRAX 1.5.
    """

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='productos_activos')
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name='activos_en_pozos',
        verbose_name="Producto (Catálogo Maestro)"
    )
    abreviatura = models.CharField(max_length=30, blank=True, verbose_name="Abreviación")
    unit_size = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Tamaño de Unidad")
    unidad = models.CharField(max_length=30, blank=True, verbose_name="Unidad")
    empaque = models.CharField(max_length=30, blank=True, verbose_name="Empaque")
    precio = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Precio")
    gravedad_especifica = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Gravedad Específica")
    calcular_concentracion = models.BooleanField(default=True, verbose_name="¿Calcular Concentración?")
    es_producto_mi = models.BooleanField(default=True, verbose_name="¿Producto M-I?")
    grupo_producto = models.PositiveSmallIntegerField(default=1, verbose_name="Grupo de Producto")
    codigo_costo_diario = models.PositiveSmallIntegerField(default=1, verbose_name="Código de Costo Diario")
    calcular_wmgt_conc = models.BooleanField(default=True, verbose_name="¿Calcular Conc. WMgt?")
    categoria_costo_wmgt = models.PositiveSmallIntegerField(default=1, verbose_name="Categoría de Costo WMgt")
    categoria_costo_cf = models.PositiveSmallIntegerField(default=1, verbose_name="Categoría de Costo CF")

    class Meta:
        verbose_name = "Producto Activo del Pozo"
        verbose_name_plural = "Productos Activos del Pozo"
        ordering = ['producto__codigo']

    def __str__(self):
        return f"{self.pozo.nombre} — {self.producto.codigo}"

    def to_dict(self):
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "producto_codigo": self.producto.codigo,
            "producto_nombre": self.producto.descripcion,
            "abreviatura": self.abreviatura,
            "unit_size": float(self.unit_size) if self.unit_size is not None else None,
            "unidad": self.unidad,
            "empaque": self.empaque,
            "precio": float(self.precio) if self.precio is not None else None,
            "gravedad_especifica": float(self.gravedad_especifica) if self.gravedad_especifica is not None else None,
            "calcular_concentracion": self.calcular_concentracion,
            "es_producto_mi": self.es_producto_mi,
            "grupo_producto": self.grupo_producto,
            "codigo_costo_diario": self.codigo_costo_diario,
            "calcular_wmgt_conc": self.calcular_wmgt_conc,
            "categoria_costo_wmgt": self.categoria_costo_wmgt,
            "categoria_costo_cf": self.categoria_costo_cf,
        }


class EquipoActivoPozo(models.Model):
    """'Active Equipment List' — equipos seleccionados para este pozo."""

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='equipos_activos')
    equipo = models.ForeignKey(
        Equipo, on_delete=models.PROTECT, related_name='activos_en_pozos',
        verbose_name="Equipo (Catálogo Maestro)"
    )
    numero_serie = models.CharField(max_length=30, verbose_name="N° de Serie")
    descripcion = models.CharField(
        max_length=150, blank=True, verbose_name="Descripción",
        help_text="Editable para necesidades de reporte; el nombre oficial vive en el Equipo maestro."
    )
    precio_renta = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Precio de Renta")
    precio_standby = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Precio Stand-By")

    class Meta:
        verbose_name = "Equipo Activo del Pozo"
        verbose_name_plural = "Equipos Activos del Pozo"
        unique_together = ('pozo', 'numero_serie')
        ordering = ['equipo__codigo', 'numero_serie']

    def __str__(self):
        return f"{self.pozo.nombre} — {self.numero_serie}"

    def to_dict(self):
        return {
            "id": self.id,
            "equipo_id": self.equipo_id,
            "equipo_codigo": self.equipo.codigo,
            "equipo_nombre": self.equipo.nombre,
            "numero_serie": self.numero_serie,
            "descripcion": self.descripcion,
            "precio_renta": float(self.precio_renta),
            "precio_standby": float(self.precio_standby),
        }


class MallaActivaPozo(models.Model):
    """'Active Screen List' — mallas de zaranda seleccionadas para este pozo."""

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='mallas_activas')
    malla = models.ForeignKey(
        MallaZaranda, on_delete=models.PROTECT, related_name='activas_en_pozos',
        verbose_name="Malla (Catálogo Maestro)"
    )
    precio = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Precio")
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Descuento (%)")

    class Meta:
        verbose_name = "Malla Activa del Pozo"
        verbose_name_plural = "Mallas Activas del Pozo"
        unique_together = ('pozo', 'malla')
        ordering = ['malla__mesh_size']

    def __str__(self):
        return f"{self.pozo.nombre} — {self.malla.codigo}"

    def to_dict(self):
        return {
            "id": self.id,
            "malla_id": self.malla_id,
            "malla_codigo": self.malla.codigo,
            "malla_descripcion": self.malla.descripcion,
            "mesh_size": self.malla.mesh_size,
            "precio": float(self.precio),
            "descuento_porcentaje": float(self.descuento_porcentaje),
        }


# ============================================================
# Equipment Properties Setup
# ============================================================

class PropiedadEquipoTipo(models.Model):
    """
    Catálogo maestro global (editable) de propiedades disponibles por
    Tipo de Equipo (ej: para Centrífuga: Flow Rate, WT In, Bowl Speed...).
    Es la lista que aparece pre-cargada en ONE-TRAX; aquí el ingeniero
    puede agregar, modificar o eliminar propiedades libremente.
    """

    tipo_equipo = models.CharField(
        max_length=25, choices=Equipo.TIPO_EQUIPO_CHOICES, verbose_name="Tipo de Equipo"
    )
    descripcion = models.CharField(max_length=100, verbose_name="Descripción de la Propiedad")
    unidad = models.CharField(max_length=30, blank=True, verbose_name="Unidad")
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden")

    class Meta:
        verbose_name = "Propiedad de Equipo (Catálogo Maestro)"
        verbose_name_plural = "Propiedades de Equipo (Catálogo Maestro)"
        unique_together = ('tipo_equipo', 'descripcion')
        ordering = ['tipo_equipo', 'orden', 'descripcion']

    def __str__(self):
        return f"{self.get_tipo_equipo_display()} — {self.descripcion}"

    def to_dict(self):
        return {
            "id": self.id, "tipo_equipo": self.tipo_equipo,
            "tipo_equipo_display": self.get_tipo_equipo_display(),
            "descripcion": self.descripcion, "unidad": self.unidad, "orden": self.orden,
        }


class EquipoPropiedadSeleccionada(models.Model):
    """Propiedades estándar seleccionadas (checkbox) para un pozo, por tipo de equipo."""

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='propiedades_equipo_seleccionadas')
    tipo_equipo = models.CharField(max_length=25, choices=Equipo.TIPO_EQUIPO_CHOICES, verbose_name="Tipo de Equipo")
    propiedad = models.ForeignKey(
        PropiedadEquipoTipo, on_delete=models.PROTECT, related_name='seleccionadas_en_pozos',
        verbose_name="Propiedad"
    )

    class Meta:
        verbose_name = "Propiedad de Equipo Seleccionada"
        verbose_name_plural = "Propiedades de Equipo Seleccionadas"
        unique_together = ('pozo', 'propiedad')
        ordering = ['tipo_equipo', 'propiedad__orden']

    def __str__(self):
        return f"{self.pozo.nombre} — {self.propiedad.descripcion}"


class EquipoPropiedadExtra(models.Model):
    """Propiedades adicionales de texto libre capturadas para un pozo, por tipo de equipo."""

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='propiedades_equipo_extra')
    tipo_equipo = models.CharField(max_length=25, choices=Equipo.TIPO_EQUIPO_CHOICES, verbose_name="Tipo de Equipo")
    descripcion = models.CharField(max_length=100, verbose_name="Descripción")
    unidad = models.CharField(max_length=30, blank=True, verbose_name="Unidad")

    class Meta:
        verbose_name = "Propiedad de Equipo Extra"
        verbose_name_plural = "Propiedades de Equipo Extra"
        ordering = ['tipo_equipo', 'descripcion']

    def __str__(self):
        return f"{self.pozo.nombre} — {self.descripcion} (extra)"

    def to_dict(self):
        return {"id": self.id, "tipo_equipo": self.tipo_equipo, "descripcion": self.descripcion, "unidad": self.unidad}


class CentrifugaUnidadConfig(models.Model):
    """'Centrifuge Flexible Units Selection' — configuración de unidades, una por pozo."""

    UNIDAD_FLOW_RATE_CHOICES = [
        ('gal/min', 'gal/min'),
        ('bbl/min', 'bbl/min'),
        ('bbl/hr', 'bbl/hr'),
        ('L/min', 'L/min'),
        ('m3/hr', 'm3/hr'),
    ]
    UNIDAD_MASS_CHOICES = [
        ('Ton', 'Ton'),
        ('lb', 'lb'),
        ('kg', 'kg'),
        ('bbl', 'bbl'),
    ]

    pozo = models.OneToOneField(Pozo, on_delete=models.CASCADE, related_name='centrifuga_unidad_config')
    unidad_flow_rate = models.CharField(max_length=15, choices=UNIDAD_FLOW_RATE_CHOICES, default='gal/min', verbose_name="Unidad de Flow Rate")
    unidad_mass = models.CharField(max_length=10, choices=UNIDAD_MASS_CHOICES, default='Ton', verbose_name="Unidad de Mass")

    class Meta:
        verbose_name = "Configuración de Unidades de Centrífuga"
        verbose_name_plural = "Configuraciones de Unidades de Centrífuga"

    def __str__(self):
        return f"{self.pozo.nombre} — Unidades de Centrífuga"

    def to_dict(self):
        return {"unidad_flow_rate": self.unidad_flow_rate, "unidad_mass": self.unidad_mass}


# ============================================================
# Benchmark Setup
# ============================================================

class ParametroBenchmark(models.Model):
    """
    Catálogo maestro global (editable) de parámetros disponibles para
    Benchmark Setup (ej: Mud Weight(WBM), PV(WBM), YP(OBM)...).
    """

    TIPO_FLUIDO_CHOICES = [
        ('WBM', 'WBM (Base Agua)'),
        ('OBM', 'OBM (Base Aceite)'),
        ('AMBOS', 'Ambos'),
        ('NA', 'No Aplica'),
    ]
    TIPO_DATO_CHOICES = [
        ('NUMERICO', 'Numérico (valor único)'),
        ('MIN_MAX', 'Mínimo / Máximo'),
        ('TEXTO', 'Texto'),
    ]

    grupo = models.CharField(
        max_length=60, verbose_name="Grupo",
        help_text="Categoría para agrupar en la lista de selección (ej: 'Mud Properties')."
    )
    descripcion = models.CharField(max_length=100, verbose_name="Descripción")
    unidad = models.CharField(max_length=30, blank=True, verbose_name="Unidad")
    tipo_fluido = models.CharField(max_length=5, choices=TIPO_FLUIDO_CHOICES, default='NA', verbose_name="Tipo de Fluido")
    tipo_dato = models.CharField(max_length=10, choices=TIPO_DATO_CHOICES, default='MIN_MAX', verbose_name="Tipo de Dato")

    class Meta:
        verbose_name = "Parámetro de Benchmark (Catálogo Maestro)"
        verbose_name_plural = "Parámetros de Benchmark (Catálogo Maestro)"
        unique_together = ('grupo', 'descripcion', 'tipo_fluido')
        ordering = ['grupo', 'descripcion']

    def __str__(self):
        return f"{self.grupo} — {self.descripcion}"

    def to_dict(self):
        return {
            "id": self.id, "grupo": self.grupo, "descripcion": self.descripcion,
            "unidad": self.unidad, "tipo_fluido": self.tipo_fluido,
            "tipo_fluido_display": self.get_tipo_fluido_display(),
            "tipo_dato": self.tipo_dato,
            "tipo_dato_display": self.get_tipo_dato_display(),
        }


class BenchmarkSeleccionado(models.Model):
    """'Benchmark Definitions' — parámetros elegidos para monitorear en este pozo."""

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='benchmarks_seleccionados')
    parametro = models.ForeignKey(
        ParametroBenchmark, on_delete=models.PROTECT, related_name='seleccionados_en_pozos',
        verbose_name="Parámetro"
    )

    class Meta:
        verbose_name = "Benchmark Seleccionado"
        verbose_name_plural = "Benchmarks Seleccionados"
        unique_together = ('pozo', 'parametro')
        ordering = ['parametro__grupo', 'parametro__descripcion']

    def __str__(self):
        return f"{self.pozo.nombre} — {self.parametro.descripcion}"


class BenchmarkTarget(models.Model):
    """'Target Entry' — valores objetivo por parámetro, por sección (Whole Well o Intervalo)."""

    MIN_MAX_CHOICES = [
        ('VALOR', 'Valor'),
        ('MIN', 'Mínimo'),
        ('MAX', 'Máximo'),
    ]

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='benchmark_targets')
    parametro = models.ForeignKey(
        ParametroBenchmark, on_delete=models.PROTECT, related_name='targets_en_pozos',
        verbose_name="Parámetro"
    )
    intervalo = models.ForeignKey(
        IntervaloRevestimiento, on_delete=models.CASCADE, null=True, blank=True,
        related_name='benchmark_targets', verbose_name="Intervalo",
        help_text="Vacío = 'Whole Well' (todo el pozo)."
    )
    min_max = models.CharField(max_length=5, choices=MIN_MAX_CHOICES, default='VALOR', verbose_name="Min/Max")
    valor = models.CharField(max_length=50, blank=True, verbose_name="Valor")

    class Meta:
        verbose_name = "Objetivo de Benchmark"
        verbose_name_plural = "Objetivos de Benchmark"
        unique_together = ('pozo', 'parametro', 'intervalo', 'min_max')
        ordering = ['parametro__grupo', 'parametro__descripcion', 'min_max']

    def __str__(self):
        columna = self.intervalo.numero_intervalo if self.intervalo_id else 'Whole Well'
        return f"{self.pozo.nombre} — {self.parametro.descripcion} ({columna})"


# === Nuevos modulos (Avances 19 Sep) ===


from .models_daily_reports import *
from .models_control_solidos import *
