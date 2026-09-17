# ============================================================
# AGREGAR a operaciones/models.py (debajo de la clase Producto)
# ============================================================
from django.conf import settings


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
        if not self.pozo_plantilla:
            return
        for item in self.pozo_plantilla.categorias_perdida.all():
            CategoriaPerdidaItem.objects.create(
                pozo=self,
                codigo=item.codigo,
                descripcion=item.descripcion,
                tipo=item.tipo,
            )

    def clonar_unidades_personalizadas(self):
        if not self.pozo_plantilla or self.sistema_unidades != 'CUSTOM':
            return
        for item in self.pozo_plantilla.unidades_personalizadas.all():
            PropiedadUnidadPozo.objects.update_or_create(
                pozo=self,
                propiedad=item.propiedad,
                defaults={'unidad': item.unidad},
            )

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
