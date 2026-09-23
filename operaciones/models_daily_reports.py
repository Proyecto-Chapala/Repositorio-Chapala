from django.db import models
from .models import Pozo, IntervaloRevestimiento, ComponenteSarta


class ReporteDiario(models.Model):
    TIPO_LODO_CHOICES = [
        ('WBM', 'Water Base'),
        ('WBM_CACL2', 'Water Base (CaCl2)'),
        ('OBM', 'Oil Base'),
        ('SBM', 'Synthetic Base'),
    ]
    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='reportes_diarios')
    fecha = models.DateField(verbose_name="Fecha del Reporte")
    tipo_lodo = models.CharField(max_length=20, choices=TIPO_LODO_CHOICES, default='WBM', verbose_name="Tipo de Lodo (Mud Check Type)")
    
    # --- Tab 1: General (Bloque Superior) ---
    profundidad_actual = models.FloatField(default=0.0, verbose_name="Profundidad (Depth)")
    profundidad_tvd = models.FloatField(default=0.0, verbose_name="Profundidad TVD")
    bit_depth = models.FloatField(default=0.0, verbose_name="Profundidad de Mecha (Bit Depth)", help_text="Disparador principal de la geometría.")
    actividad_actual = models.CharField(max_length=255, blank=True, verbose_name="Actividad (Present Activity)")
    tipo_fluido_display = models.CharField(max_length=150, blank=True, verbose_name="Nombre Comercial del Fluido (Fluid Type)")
    litologia = models.CharField(max_length=150, blank=True, verbose_name="Litología")

    # --- Tab 1: General (Contactos y Representantes) ---
    operador_representante = models.CharField(max_length=150, blank=True, verbose_name="Representante del Operador")
    contratista_representante = models.CharField(max_length=150, blank=True, verbose_name="Representante del Contratista")
    mi_representante_1 = models.CharField(max_length=150, blank=True, verbose_name="Ingeniero M-I SWACO 1")
    mi_representante_2 = models.CharField(max_length=150, blank=True, verbose_name="Ingeniero M-I SWACO 2")
    telefono_taladro = models.CharField(max_length=100, blank=True, verbose_name="Teléfono del Taladro")
    telefono_almacen = models.CharField(max_length=100, blank=True, verbose_name="Teléfono del Almacén")
    telefonos = models.CharField(max_length=255, blank=True, verbose_name="Otros Teléfonos")
    fax_numbers = models.CharField(max_length=255, blank=True, verbose_name="Pagers/FAX")

    # --- Tab 4: Well Geometry ---
    intervalo_costo = models.ForeignKey(
        IntervaloRevestimiento, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reportes_asignados', verbose_name="Intervalo de Costo (Interval Number)",
        help_text="Intervalo del pozo al que se imputan los costos del día."
    )
    orden_impresion_intervalo = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Orden de Impresión (Print Order)"
    )
    pilot_hole_size_in = models.FloatField(
        default=0.0, verbose_name="Diámetro del Hoyo Piloto (in)"
    )
    pilot_hole_depth_ft = models.FloatField(
        default=0.0, verbose_name="Profundidad del Hoyo Piloto (ft)"
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reporte Diario"
        verbose_name_plural = "Reportes Diarios"
        unique_together = ('pozo', 'fecha')
        ordering = ['-fecha']

    def __str__(self):
        return f"Reporte {self.fecha} - {self.pozo.nombre}"

    @property
    def numero_reporte(self):
        """Calcula el número correlativo de reporte para este pozo."""
        return ReporteDiario.objects.filter(pozo=self.pozo, fecha__lte=self.fecha).count()


class PropiedadExtraFluido(models.Model):
    TIPO_FLUIDO_CHOICES = [
        ('WBM', 'Water-Based Mud'),
        ('OBM', 'Oil-Based/Synthetic-Based Mud'),
    ]
    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='propiedades_extra')
    tipo_fluido = models.CharField(max_length=5, choices=TIPO_FLUIDO_CHOICES)
    numero = models.PositiveIntegerField(help_text="Numero de propiedad del 1 al 60")
    etiqueta = models.CharField(max_length=100, blank=True, verbose_name="Etiqueta (Label)")
    unidad = models.CharField(max_length=50, blank=True, verbose_name="Unidad (Unit)")
    orden_impresion = models.PositiveIntegerField(
        default=0,
        verbose_name="Print Order",
        help_text="Orden de impresion en reportes. 0 = oculto."
    )

    class Meta:
        verbose_name = "Propiedad Extra de Fluido"
        verbose_name_plural = "Propiedades Extra de Fluidos"
        unique_together = ('pozo', 'tipo_fluido', 'numero')
        ordering = ['tipo_fluido', 'numero']

    def __str__(self):
        return f"[{self.tipo_fluido}-{self.numero}] {self.etiqueta}"


class PlantillaExtraLabels(models.Model):
    """Plantilla predefinida de Extra Report Labels (ej. Statoil, Custom)."""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Plantilla")
    descripcion = models.CharField(max_length=255, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Plantilla de Extra Labels"
        verbose_name_plural = "Plantillas de Extra Labels"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class PlantillaExtraLabelItem(models.Model):
    """Cada etiqueta individual dentro de una plantilla predefinida."""
    TIPO_FLUIDO_CHOICES = [
        ('WBM', 'Water-Based Mud'),
        ('OBM', 'Oil-Based/Synthetic-Based Mud'),
    ]
    plantilla = models.ForeignKey(PlantillaExtraLabels, on_delete=models.CASCADE, related_name='items')
    tipo_fluido = models.CharField(max_length=5, choices=TIPO_FLUIDO_CHOICES)
    numero = models.PositiveIntegerField()
    etiqueta = models.CharField(max_length=100)
    unidad = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Item de Plantilla Extra Labels"
        unique_together = ('plantilla', 'tipo_fluido', 'numero')
        ordering = ['tipo_fluido', 'numero']

    def __str__(self):
        return f"{self.plantilla.nombre} [{self.tipo_fluido}-{self.numero}] {self.etiqueta}"


class WellSurveyStation(models.Model):
    """
    Estaciones de trayectoria direccional del pozo (Well Survey).
    Registra MD, Inclinación, Azimut y calcula automáticamente TVD, DLS y Sección Vertical.
    """
    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='survey_stations')
    estacion = models.PositiveIntegerField(default=1, verbose_name="N° de Estación")
    md_ft = models.FloatField(default=0.0, verbose_name="Profundidad Medida - MD (ft)")
    inclinacion_deg = models.FloatField(default=0.0, verbose_name="Inclinación (°)")
    azimut_deg = models.FloatField(default=0.0, verbose_name="Azimut (°)")
    tvd_ft = models.FloatField(default=0.0, verbose_name="Profundidad Vertical Verdadera - TVD (ft)")
    dls_deg_100ft = models.FloatField(default=0.0, verbose_name="Dogleg Severity (°/100ft)")
    seccion_vertical_ft = models.FloatField(default=0.0, verbose_name="Sección Vertical (ft)")
    comentarios = models.CharField(max_length=150, blank=True, verbose_name="Comentarios")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Estación de Well Survey"
        verbose_name_plural = "Estaciones de Well Survey"
        ordering = ['md_ft', 'estacion']

    def __str__(self):
        return f"{self.pozo.nombre} - Estación #{self.estacion} (MD: {self.md_ft} ft)"


class WellFormationTop(models.Model):
    """
    Topes de formación y litología por pozo (Lithology Setup).
    Columnas exactas de ONE-TRAX: Depth (ft), Formation Top, Lithology, % Sand.
    """
    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='formation_tops')
    depth_ft = models.FloatField(default=0.0, verbose_name="Depth (ft)")
    formation_top = models.CharField(max_length=150, verbose_name="Formation Top")
    lithology = models.CharField(max_length=150, blank=True, verbose_name="Lithology")
    porcentaje_arena = models.FloatField(default=0.0, verbose_name="% Sand")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tope de Formación y Litología"
        verbose_name_plural = "Topes de Formación y Litología"
        ordering = ['depth_ft', 'id']

    def __str__(self):
        return f"{self.pozo.nombre} - {self.formation_top} ({self.depth_ft} ft)"


class ReporteDiarioBomba(models.Model):
    """
    Bombas de lodo del taladro registradas en el reporte diario (Tab #2 - Pumps / Bits).
    """
    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='bombas')
    numero_bomba = models.PositiveIntegerField(default=1, verbose_name="N° Bomba")
    make_model = models.CharField(max_length=100, blank=True, verbose_name="Make and Model")
    liner_diameter = models.FloatField(default=6.5, verbose_name="Liner Diameter (in)")
    stroke_length = models.FloatField(default=12.0, verbose_name="Stroke Length (in)")
    rod_diam_duplex = models.FloatField(default=0.0, blank=True, null=True, verbose_name="Rod Diam Duplex Only (in)")
    eficiencia_pct = models.FloatField(default=97.0, verbose_name="Eff %")
    pump_rate_spm = models.FloatField(default=0.0, verbose_name="Pump Rate (spm)")
    pump_on_report = models.BooleanField(default=True, verbose_name="Pump On Report")
    riser_pump = models.BooleanField(default=False, verbose_name="Riser Pump")

    class Meta:
        verbose_name = "Bomba de Reporte Diario"
        verbose_name_plural = "Bombas de Reporte Diario"
        ordering = ['numero_bomba']
        unique_together = ('reporte', 'numero_bomba')

    def __str__(self):
        return f"Bomba #{self.numero_bomba} - {self.make_model or 'Sin Modelo'} ({self.reporte})"

    @property
    def desplazamiento_bbl_stk(self):
        """Desplazamiento volumétrico por embolada para bomba Tríplex en bbl/stk."""
        eff = (self.eficiencia_pct or 0.0) / 100.0
        return 0.000243 * (self.liner_diameter ** 2) * self.stroke_length * eff

    @property
    def desplazamiento_gal_stk(self):
        """Desplazamiento volumétrico por embolada en gal/stk."""
        return self.desplazamiento_bbl_stk * 42.0

    @property
    def caudal_gpm(self):
        """Caudal generado por la bomba en gal/min (GPM)."""
        if not self.pump_on_report:
            return 0.0
        return self.desplazamiento_gal_stk * (self.pump_rate_spm or 0.0)


class ReporteDiarioBitData(models.Model):
    """
    Datos de barrena, parámetros de perforación, presiones hidráulicas y datos de ECD
    (Tab #2 - Pumps / Bits).
    """
    reporte = models.OneToOneField(ReporteDiario, on_delete=models.CASCADE, related_name='bit_data')

    # Bit Identification
    bit_description = models.CharField(max_length=150, blank=True, default="Hycalog X-175", verbose_name="Bit Description")
    bit_number = models.CharField(max_length=50, blank=True, default="1", verbose_name="Bit Number")
    washout_pct = models.FloatField(default=0.0, verbose_name="% Washout")
    bit_size = models.FloatField(default=12.25, verbose_name="Bit Size / Hole Diameter (in)")
    washout_hole_size = models.FloatField(default=12.25, verbose_name="Washout Hole Size (in)")

    # Bit Detailed Information (Modal)
    bit_serial_no = models.CharField(max_length=100, blank=True, verbose_name="Serial Number")
    bit_iadc_code = models.CharField(max_length=50, blank=True, verbose_name="IADC Code")
    bit_manufacturer = models.CharField(max_length=100, blank=True, verbose_name="Manufacturer")

    # Drilling Parameters
    rotary_rpm = models.FloatField(default=0.0, verbose_name="Rotary RPM")
    rotating_hours = models.FloatField(default=0.0, verbose_name="Rotating Hours")
    weight_on_bit = models.FloatField(default=0.0, verbose_name="Weight on Bit (lbs)")
    rop = models.FloatField(default=0.0, verbose_name="ROP (ft/hr)")
    riser_pump_flow_rate = models.FloatField(default=0.0, verbose_name="Riser Pump Flow Rate (gpm)")

    # Pressures & Hydraulics
    pump_flow_rate = models.FloatField(default=0.0, verbose_name="Pump Flow Rate (gpm)")
    pump_pressure = models.FloatField(default=0.0, verbose_name="Pump Pressure (psi)")
    dp_mwd = models.FloatField(default=0.0, verbose_name="dP MWD (psi)")
    dp_motor = models.FloatField(default=0.0, verbose_name="dP Motor (psi)")
    motor_rpm = models.FloatField(default=0.0, verbose_name="Motor RPM")

    # Extra ECD Input
    surface_code = models.CharField(max_length=20, blank=True, default="1", verbose_name="Surface Code (1-5)")
    surface_pressure = models.FloatField(default=0.0, verbose_name="Surface Pressure (psi)")
    ref_flow_rate = models.FloatField(default=0.0, verbose_name="Ref. Flow Rate (gal/min)")
    on_off_bottom_pressure = models.FloatField(default=0.0, verbose_name="On/Off Bottom (psi)")

    class Meta:
        verbose_name = "Datos de Barrena y Perforación"
        verbose_name_plural = "Datos de Barrena y Perforación"

    def __str__(self):
        return f"Bit #{self.bit_number} - {self.bit_description} ({self.reporte})"


class ReporteDiarioBoquilla(models.Model):
    """
    Boquillas (jets/nozzles) instaladas en la barrena para el cálculo de TFA.
    """
    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='boquillas')
    size_32nds = models.PositiveIntegerField(default=14, verbose_name="Size (32nds of inch)")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Quantity")

    class Meta:
        verbose_name = "Boquilla de Barrena"
        verbose_name_plural = "Boquillas de Barrena"
        ordering = ['-size_32nds', 'id']

    def __str__(self):
        return f"{self.cantidad} x {self.size_32nds}/32\" ({self.reporte})"

    @property
    def area_sq_in(self):
        """Área de flujo de estas boquillas en pulgadas cuadradas."""
        import math
        diam_in = self.size_32nds / 32.0
        return self.cantidad * (math.pi / 4.0) * (diam_in ** 2)


class ReporteDiarioMudConfig(models.Model):
    """
    Configuración global de propiedades de lodo y análisis de sólidos para el reporte diario (Tab #3).
    """
    EQUATION_CHOICES = [
        ('M-I', 'M-I SWACO'),
        ('API', 'API Standard'),
    ]
    reporte = models.OneToOneField(ReporteDiario, on_delete=models.CASCADE, related_name='mud_config')
    solids_equation = models.CharField(max_length=20, default='M-I', choices=EQUATION_CHOICES, verbose_name="Current Solids Analysis Equations")
    is_weighted = models.BooleanField(default=True, verbose_name="Weighted Mud")
    
    # Specific Gravities (s.g.) required for mass/volume balance equations
    sg_base_oil = models.FloatField(default=0.84, verbose_name="Base Oil S.G.")
    sg_weight_material = models.FloatField(default=4.20, verbose_name="Weight Material S.G.")
    sg_drill_solids = models.FloatField(default=2.60, verbose_name="Drill Solids S.G.")
    obm_salt_type = models.CharField(max_length=10, default='CaCl2', choices=[('CaCl2', 'CaCl2'), ('NaCl', 'NaCl')], verbose_name="Internal Phase Salt")
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración de Lodo y Sólidos"
        verbose_name_plural = "Configuraciones de Lodo y Sólidos"

    def __str__(self):
        return f"Mud Config - {self.reporte} ({'Weighted' if self.is_weighted else 'Unweighted'}, Eq: {self.solids_equation})"


class ReporteDiarioMudCheck(models.Model):
    """
    Chequeos diarios de lodo (Tab #3 - Mud Properties).
    Permite hasta 4 chequeos diarios (#1 Primary, #2, #3, #4) en orden cronológico inverso.
    """
    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='mud_checks')
    check_number = models.PositiveIntegerField(default=1, verbose_name="N° Chequeo (1-4)")
    is_primary = models.BooleanField(default=False, verbose_name="Primary Check")

    # Identificación y Condiciones de Muestra
    sample_from = models.CharField(max_length=50, blank=True, default="In", verbose_name="Sample From")
    time_taken = models.CharField(max_length=20, blank=True, default="09:00", verbose_name="Time Taken")
    flowline_temp = models.FloatField(null=True, blank=True, verbose_name="Flow Line Temp (°F)")
    depth = models.FloatField(null=True, blank=True, verbose_name="Depth (ft)")
    tvd = models.FloatField(null=True, blank=True, verbose_name="TVD (ft)")

    # Densidad y Viscosidad
    mud_weight = models.FloatField(null=True, blank=True, verbose_name="Mud Weight (lb/gal)")
    mw_temp = models.FloatField(null=True, blank=True, verbose_name="MW Temp (°F)")
    funnel_viscosity = models.FloatField(null=True, blank=True, verbose_name="Funnel Viscosity (s/qt)")

    # Reología (Fann 35 / VG Meter)
    rheology_temp = models.FloatField(null=True, blank=True, default=120.0, verbose_name="Rheology Temp (°F)")
    r600 = models.FloatField(null=True, blank=True, verbose_name="R600")
    r300 = models.FloatField(null=True, blank=True, verbose_name="R300")
    r200 = models.FloatField(null=True, blank=True, verbose_name="R200")
    r100 = models.FloatField(null=True, blank=True, verbose_name="R100")
    r6 = models.FloatField(null=True, blank=True, verbose_name="R6")
    r3 = models.FloatField(null=True, blank=True, verbose_name="R3")
    pv = models.FloatField(null=True, blank=True, verbose_name="PV (cP)")
    yp = models.FloatField(null=True, blank=True, verbose_name="YP (lb/100ft²)")
    gel_10s = models.FloatField(null=True, blank=True, verbose_name="10s Gel (lb/100ft²)")
    gel_10m = models.FloatField(null=True, blank=True, verbose_name="10m Gel (lb/100ft²)")
    gel_30m = models.FloatField(null=True, blank=True, verbose_name="30m Gel (lb/100ft²)")

    # Filtrado y Revoque
    api_fluid_loss = models.FloatField(null=True, blank=True, verbose_name="API Fluid Loss (cc/30min)")
    hthp_fluid_loss = models.FloatField(null=True, blank=True, verbose_name="HPHT Fluid Loss (cc/30min)")
    cake_api = models.FloatField(null=True, blank=True, verbose_name="Cake API (1/32 in)")
    cake_hthp = models.FloatField(null=True, blank=True, verbose_name="Cake HPHT (1/32 in)")

    # Retorta y Sólidos
    solids_pct = models.FloatField(null=True, blank=True, verbose_name="Solids (%Vol)")
    oil_pct = models.FloatField(null=True, blank=True, verbose_name="Oil (%Vol)")
    water_pct = models.FloatField(null=True, blank=True, verbose_name="Water (%Vol)")
    sand_pct = models.FloatField(null=True, blank=True, verbose_name="Sand (%Vol)")

    # Solids Analysis on WATER BASED MUD (Inputs & Retort Parameters)
    retort_mud_weight = models.FloatField(null=True, blank=True, verbose_name="Retort Mud Wt (lb/gal)")
    retort_mud_temp = models.FloatField(null=True, blank=True, default=75.0, verbose_name="Retort Mud Temp (°F)")
    k_from_kcl = models.FloatField(null=True, blank=True, default=0.0, verbose_name="K+ From KCl (mg/l)")
    wt_additive_sg = models.FloatField(null=True, blank=True, default=4.20, verbose_name="Wt Additive SG")
    oil_sg = models.FloatField(null=True, blank=True, default=0.70, verbose_name="Oil SG")
    frac_bent = models.FloatField(null=True, blank=True, default=0.1111, verbose_name="Frac Bent (Activity Ratio)")
    chem_conc = models.FloatField(null=True, blank=True, default=0.0, verbose_name="Chem Conc (lb/bbl)")
    drill_solids_sg = models.FloatField(null=True, blank=True, default=2.60, verbose_name="Drill Solids SG")

    # Solids Analysis Results (Calculated in Yellow Section - WBM)
    nacl_pct = models.FloatField(null=True, blank=True, verbose_name="NaCl (%Vol)")
    nacl_ppb = models.FloatField(null=True, blank=True, verbose_name="NaCl (lb/bbl)")
    kcl_pct = models.FloatField(null=True, blank=True, verbose_name="KCl (%Vol)")
    kcl_ppb = models.FloatField(null=True, blank=True, verbose_name="KCl (lb/bbl)")
    lgs_pct = models.FloatField(null=True, blank=True, verbose_name="LGS (%Vol)")
    lgs_ppb = models.FloatField(null=True, blank=True, verbose_name="LGS (lb/bbl)")
    bentonite_pct = models.FloatField(null=True, blank=True, verbose_name="Bentonite (%Vol)")
    bentonite_ppb = models.FloatField(null=True, blank=True, verbose_name="Bentonite (lb/bbl)")
    drill_solids_pct = models.FloatField(null=True, blank=True, verbose_name="Drill Solids (%Vol)")
    drill_solids_ppb = models.FloatField(null=True, blank=True, verbose_name="Drill Solids (lb/bbl)")
    hgs_pct = models.FloatField(null=True, blank=True, verbose_name="HGS (%Vol)")
    hgs_ppb = models.FloatField(null=True, blank=True, verbose_name="HGS (lb/bbl)")

    # Solids Analysis Results (Calculated in Yellow Section - OBM/SBF)
    salt_pct_wt = models.FloatField(null=True, blank=True, verbose_name="Salt (%wt)")
    salt_ppb = models.FloatField(null=True, blank=True, verbose_name="Salt (lb/bbl)")
    adjusted_solids_pct = models.FloatField(null=True, blank=True, verbose_name="Adjusted Solids (%Vol)")
    oil_water_ratio = models.CharField(max_length=20, blank=True, default="", verbose_name="Oil/Water Ratio")
    avg_sg_solids = models.FloatField(null=True, blank=True, verbose_name="Avg SG Solids")

    # Química del Lodo y Filtrado
    ph = models.FloatField(null=True, blank=True, verbose_name="pH")
    ph_temp = models.FloatField(null=True, blank=True, verbose_name="pH Temp (°F)")
    pm = models.FloatField(null=True, blank=True, verbose_name="Pm")
    pf = models.FloatField(null=True, blank=True, verbose_name="Pf")
    mf = models.FloatField(null=True, blank=True, verbose_name="Mf")
    chlorides = models.FloatField(null=True, blank=True, verbose_name="Chlorides (mg/L)")
    calcium_hardness = models.FloatField(null=True, blank=True, verbose_name="Hardness Ca++ (mg/L)")
    mbt = models.FloatField(null=True, blank=True, verbose_name="MBT (lb/bbl)")
    electrical_stability = models.FloatField(null=True, blank=True, verbose_name="Electrical Stability (V)")
    excess_lime = models.FloatField(null=True, blank=True, verbose_name="Excess Lime (lb/bbl)")

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chequeo de Lodo (Mud Check)"
        verbose_name_plural = "Chequeos de Lodo (Mud Checks)"
        unique_together = ('reporte', 'check_number')
        ordering = ['check_number']

    def __str__(self):
        primary_badge = " (Primary)" if self.is_primary else ""
        return f"Check #{self.check_number}{primary_badge} - {self.reporte}"

    def calcular_reologia_automatica(self):
        """Calcula PV e YP según el modelo plástico de Bingham."""
        if self.r600 is not None and self.r300 is not None:
            self.pv = max(0.0, round(self.r600 - self.r300, 2))
            self.yp = max(0.0, round(self.r300 - self.pv, 2))

    def calcular_solids_analysis_wbm(self):
        """Calcula balance de sólidos para Water Based Mud (WBM) según especificación M-I SWACO ONE-TRAX."""
        mw = self.retort_mud_weight if self.retort_mud_weight is not None else (self.mud_weight or 10.0)
        vw = self.water_pct or 0.0
        vo = self.oil_pct or 0.0
        vs = self.solids_pct or (max(0.0, 100.0 - vw - vo) if vw > 0 else 0.0)

        # 1. KCl
        k_plus = self.k_from_kcl or 0.0
        if k_plus > 0 and vw > 0:
            kcl_mg_l = k_plus * 1.9066
            self.kcl_ppb = round(kcl_mg_l * 0.0003505 * (vw / 100.0), 1)
            self.kcl_pct = round(self.kcl_ppb / (3.5 * 1.984), 1)
        else:
            self.kcl_ppb = 0.0
            self.kcl_pct = 0.0

        # 2. NaCl
        cl_total = self.chlorides or 0.0
        cl_kcl = (self.kcl_ppb / (0.0003505 * (vw / 100.0))) * (35.45 / 74.55) if (self.kcl_ppb and vw > 0) else 0.0
        cl_nacl = max(0.0, cl_total - cl_kcl)
        if cl_nacl > 0 and vw > 0:
            self.nacl_ppb = round(cl_nacl * 1.6485 * 0.0003505 * (vw / 100.0), 1)
            self.nacl_pct = round(self.nacl_ppb / (3.5 * 2.165), 1)
        else:
            self.nacl_ppb = 0.0
            self.nacl_pct = 0.0

        # 3. Sólidos suspendidos y separación LGS/HGS
        v_ss = max(0.0, vs - (self.nacl_pct or 0.0) - (self.kcl_pct or 0.0))
        sg_hgs = self.wt_additive_sg or 4.20
        sg_lgs = self.drill_solids_sg or 2.60
        sg_oil = self.oil_sg or 0.70
        sg_water = 1.0 + ((self.nacl_ppb or 0.0) + (self.kcl_ppb or 0.0)) / 350.0

        m_total = (mw / 8.33) * 100.0
        m_liquid = (vw * sg_water) + (vo * sg_oil)
        m_ss = m_total - m_liquid

        if (sg_hgs - sg_lgs) > 0 and v_ss > 0:
            v_lgs = (sg_hgs * v_ss - m_ss) / (sg_hgs - sg_lgs)
            v_hgs = v_ss - v_lgs
        else:
            v_lgs = v_ss
            v_hgs = 0.0

        self.lgs_pct = max(0.0, round(v_lgs, 1))
        self.hgs_pct = max(0.0, round(v_hgs, 1))
        self.lgs_ppb = round(self.lgs_pct * 3.5 * sg_lgs, 1)

        # 4. Bentonita y Drill Solids
        frac_bent = self.frac_bent if self.frac_bent is not None else 0.1111
        chem_conc = self.chem_conc or 0.0
        mbt_val = self.mbt or 0.0
        # Bentonita comercial (M-I GEL) estimada a partir de MBT
        if mbt_val > 0:
            self.bentonite_ppb = round(max(0.0, mbt_val * 5.0 * (1.0 - frac_bent)), 1)
            self.bentonite_pct = round(self.bentonite_ppb / (3.5 * sg_lgs), 1)
        else:
            self.bentonite_ppb = 0.0
            self.bentonite_pct = 0.0

        self.drill_solids_ppb = max(0.0, round(self.lgs_ppb - self.bentonite_ppb - chem_conc, 1))
        self.drill_solids_pct = max(0.0, round(self.lgs_pct - self.bentonite_pct, 1))

    def calcular_solids_analysis_obm(self, salt_type=None):
        """
        Calcula balance de sólidos para Oil / Synthetic Based Mud (OBM/SBF)
        según especificación oficial M-I SWACO ONE-TRAX (media_1790024142384.png).
        Permite valores negativos cuando los datos de retorta tienen inconsistencias físicas.
        """
        mw = self.retort_mud_weight if self.retort_mud_weight is not None else (self.mud_weight or 12.0)
        vw = self.water_pct or 0.0
        vo = self.oil_pct or 0.0
        vs = self.solids_pct or (max(0.0, 100.0 - vw - vo) if (vw > 0 or vo > 0) else 0.0)

        # 1. Oil / Water Ratio (OWR)
        v_liq = vo + vw
        if v_liq > 0:
            oil_ratio = round((vo / v_liq) * 100.0)
            water_ratio = round((vw / v_liq) * 100.0)
            self.oil_water_ratio = f"{oil_ratio}/{water_ratio}"
        else:
            self.oil_water_ratio = ""

        # 2. Salinidad de fase interna
        if not salt_type:
            try:
                salt_type = self.reporte.mud_config.obm_salt_type
            except Exception:
                salt_type = 'CaCl2'

        cl_total = self.chlorides or 0.0
        if self.salt_pct_wt is not None and self.salt_pct_wt > 0:
            salt_wt = self.salt_pct_wt
        elif cl_total > 0 and vw > 0:
            cl_factor = 1.565 if salt_type == 'CaCl2' else 1.6485
            cl_brine = cl_total / (vw / 100.0)
            salt_wt = round((cl_brine * cl_factor) / 10000.0, 2)
        else:
            salt_wt = self.salt_pct_wt or 0.0

        self.salt_pct_wt = salt_wt

        # Salt lb/bbl
        if salt_wt > 0 and salt_wt < 100 and vw > 0:
            self.salt_ppb = round((salt_wt / (100.0 - salt_wt)) * vw * 3.50, 2)
        elif self.salt_ppb is not None and self.salt_ppb > 0:
            pass
        else:
            self.salt_ppb = 0.0

        # Volumen de sal seca
        sg_salt = 2.15 if salt_type == 'CaCl2' else 2.165
        v_salt = (self.salt_ppb / (3.5 * sg_salt)) if (self.salt_ppb and sg_salt > 0) else 0.0

        # 3. Adjusted Solids (%Vol)
        v_ss = round(vs - v_salt, 2)
        self.adjusted_solids_pct = v_ss

        # 4. Gravedades específicas y masas
        sg_hgs = self.wt_additive_sg or 4.20
        sg_lgs = self.drill_solids_sg or 2.60
        sg_oil = self.oil_sg or 0.80

        m_total = (mw / 8.33) * 100.0
        m_oil = vo * sg_oil
        m_brine = (vw * 1.0) + (self.salt_ppb / 3.5 if self.salt_ppb else 0.0)
        m_liquid = m_oil + m_brine
        m_ss = m_total - m_liquid

        # 5. Avg SG Solids
        if v_ss != 0:
            self.avg_sg_solids = round(m_ss / v_ss, 1)
        else:
            self.avg_sg_solids = 0.0

        # 6. Desacople LGS y HGS (permite valores negativos para detección de error de laboratorio)
        if (sg_hgs - sg_lgs) > 0 and v_ss != 0:
            v_lgs = (sg_hgs * v_ss - m_ss) / (sg_hgs - sg_lgs)
            v_hgs = v_ss - v_lgs
        else:
            v_lgs = v_ss
            v_hgs = 0.0

        self.lgs_pct = round(v_lgs, 1)
        self.hgs_pct = round(v_hgs, 1)
        self.lgs_ppb = round(self.lgs_pct * 3.5 * sg_lgs, 2)
        self.hgs_ppb = round(self.hgs_pct * 3.5 * sg_hgs, 2)

    def calcular_solids_analysis_automatica(self):
        """Despacha cálculo de sólidos a OBM o WBM según el tipo de lodo del reporte."""
        tipo = getattr(self.reporte, 'tipo_lodo', 'WBM')
        if tipo in ['OBM', 'SBM']:
            self.calcular_solids_analysis_obm()
        else:
            self.calcular_solids_analysis_wbm()


class TramoSarta(models.Model):
    """
    Un componente de la sarta de perforación instalado en el hoyo en la fecha del reporte
    (Tab #4 - Well Geometry, tabla 'Drill String').

    Las filas se ordenan DESDE LA MECHA HACIA ARRIBA (orden=1 es la mecha), que es como
    el ingeniero arma físicamente el ensamblaje. Cada tramo aporta un volumen interno
    (su propio ID) y un volumen anular (su OD contra el diámetro que lo confina, que lo
    da el perfil de revestidores del pozo y puede cambiar a lo largo de un mismo tramo).
    """

    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='tramos_sarta')
    orden = models.PositiveSmallIntegerField(
        default=1, verbose_name="Orden (1 = mecha)",
        help_text="Posición desde la mecha hacia superficie."
    )
    componente = models.ForeignKey(
        ComponenteSarta, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tramos_usados', verbose_name="Componente del Catálogo",
        help_text="Opcional: al elegirlo se autocompletan los diámetros, que siguen siendo editables."
    )
    descripcion = models.CharField(max_length=150, blank=True, verbose_name="Descripción / Tipo")

    longitud_ft = models.FloatField(default=0.0, verbose_name="Longitud (ft)")
    od_in = models.FloatField(default=0.0, verbose_name="Diámetro Externo — OD (in)")
    id_in = models.FloatField(default=0.0, verbose_name="Diámetro Interno — ID (in)")

    tool_joint_od_in = models.FloatField(default=0.0, verbose_name="OD de Junta (in)")
    tool_joint_id_in = models.FloatField(default=0.0, verbose_name="ID de Junta (in)")
    tool_joint_length_in = models.FloatField(default=0.0, verbose_name="Largo de Junta (in)")
    largo_tramo_ft = models.FloatField(default=31.0, verbose_name="Largo de Tramo (ft)")

    class Meta:
        verbose_name = "Tramo de Sarta de Perforación"
        verbose_name_plural = "Tramos de Sarta de Perforación"
        ordering = ['orden', 'id']
        unique_together = ('reporte', 'orden')

    def __str__(self):
        return f"#{self.orden} {self.descripcion or 'Tramo'} ({self.longitud_ft} ft) - {self.reporte}"

    @property
    def fraccion_junta(self):
        """
        Fracción de la longitud del tramo ocupada por juntas (tool joints).

        ONE-TRAX pondera la capacidad del tramo entre el cuerpo del tubo y la junta:
        con 21 in de junta por tramo de 31 ft la fracción es 21 / (31 * 12) = 0.05645.
        """
        largo_tramo_in = (self.largo_tramo_ft or 0.0) * 12.0
        if largo_tramo_in <= 0 or (self.tool_joint_length_in or 0.0) <= 0:
            return 0.0
        return min(1.0, self.tool_joint_length_in / largo_tramo_in)

    def to_dict(self):
        return {
            'id': self.id,
            'orden': self.orden,
            'componente_id': self.componente_id,
            'descripcion': self.descripcion,
            'longitud_ft': self.longitud_ft,
            'od_in': self.od_in,
            'id_in': self.id_in,
            'tool_joint_od_in': self.tool_joint_od_in,
            'tool_joint_id_in': self.tool_joint_id_in,
            'tool_joint_length_in': self.tool_joint_length_in,
            'largo_tramo_ft': self.largo_tramo_ft,
        }


class ReporteDiarioComentarios(models.Model):
    """
    Comentarios del día (Tab #5 - Comments).

    Tres bloques de texto con destinos distintos, más la especificación de propiedades
    del lodo (el rango objetivo acordado con el operador, no el valor medido del día:
    eso vive en los Mud Checks de la pestaña 3).
    """

    reporte = models.OneToOneField(
        ReporteDiario, on_delete=models.CASCADE, related_name='comentarios'
    )

    # --- Mud Property Specification (rangos objetivo, texto libre tipo "11.5-12.0") ---
    spec_mud_weight = models.CharField(
        max_length=50, blank=True, verbose_name="Peso del Lodo — Especificación",
        help_text="Rango objetivo acordado, por ejemplo 11.5-12.0"
    )
    spec_viscosidad = models.CharField(
        max_length=50, blank=True, verbose_name="Viscosidad — Especificación"
    )
    spec_filtrado = models.CharField(
        max_length=50, blank=True, verbose_name="Filtrado — Especificación",
        help_text="Rango objetivo acordado, por ejemplo 3.0-5.0"
    )

    # --- Bloques de comentarios ---
    mud_recap_remarks = models.TextField(
        blank=True, verbose_name="Resumen del Día (Mud Recap Remarks)",
        help_text="Una sola línea: es lo que se imprime en el Well Recap del pozo."
    )
    remarks_and_treatment = models.TextField(
        blank=True, verbose_name="Observaciones y Tratamiento",
        help_text="Actividad y servicio de fluidos prestado durante el día."
    )
    remarks = models.TextField(
        blank=True, verbose_name="Observaciones de Operaciones",
        help_text="Operaciones generales del taladro; normalmente se toma de la hoja IADC."
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comentarios del Reporte Diario"
        verbose_name_plural = "Comentarios de Reportes Diarios"

    def __str__(self):
        return f"Comentarios - {self.reporte}"

    @property
    def tiene_contenido(self):
        """True si el ingeniero ya escribió algo en cualquiera de los bloques."""
        return any([
            self.mud_recap_remarks.strip(),
            self.remarks_and_treatment.strip(),
            self.remarks.strip(),
        ])

    def to_dict(self):
        return {
            'spec_mud_weight': self.spec_mud_weight,
            'spec_viscosidad': self.spec_viscosidad,
            'spec_filtrado': self.spec_filtrado,
            'mud_recap_remarks': self.mud_recap_remarks,
            'remarks_and_treatment': self.remarks_and_treatment,
            'remarks': self.remarks,
            'tiene_contenido': self.tiene_contenido,
        }


class ReporteDiarioMudExtraValue(models.Model):
    """
    Valor de una propiedad extra (definida en PropiedadExtraFluido del pozo) para un chequeo específico.
    """
    mud_check = models.ForeignKey(ReporteDiarioMudCheck, on_delete=models.CASCADE, related_name='extra_values')
    propiedad_extra = models.ForeignKey(PropiedadExtraFluido, on_delete=models.CASCADE, related_name='check_values')
    valor = models.CharField(max_length=100, blank=True, default="", verbose_name="Valor")

    class Meta:
        verbose_name = "Valor de Propiedad Extra de Lodo"
        verbose_name_plural = "Valores de Propiedades Extra de Lodo"
        unique_together = ('mud_check', 'propiedad_extra')

    def __str__(self):
        return f"{self.mud_check} - {self.propiedad_extra.etiqueta}: {self.valor}"




class ReporteDiarioTiempo(models.Model):
    """
    Distribución de Tiempo del día (Tab #7 - Time Distribution).

    Guarda cuántas horas cubre el período del reporte. Casi siempre son 24, pero hay días
    que no: el primer día del pozo (se empezó a perforar a mitad del período), el último
    (se liberó el taladro) o cuando la operadora cambia la hora de corte. Por eso el total
    de horas se compara contra este valor y no contra 24 fijo; si no coincide, la pantalla
    avisa en rojo pero deja guardar (decisión del usuario: en campo siempre pasa algo distinto).
    """

    HORAS_PERIODO_ESTANDAR = 24

    reporte = models.OneToOneField(
        ReporteDiario, on_delete=models.CASCADE, related_name='distribucion_tiempo'
    )
    horas_periodo = models.DecimalField(
        max_digits=5, decimal_places=2, default=HORAS_PERIODO_ESTANDAR,
        verbose_name="Horas del Período",
        help_text="24 por defecto. Se cambia solo en días especiales (inicio, fin o cambio de hora de corte)."
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Distribución de Tiempo del Reporte"
        verbose_name_plural = "Distribuciones de Tiempo de Reportes"

    def __str__(self):
        return f"Distribución de tiempo - {self.reporte}"

    @property
    def total_horas(self):
        return sum((a.horas for a in self.reporte.actividades_tiempo.all()), 0)

    @property
    def cuadra(self):
        """True si el total de horas coincide con las horas del período (tolerancia de 0.01 h)."""
        return abs(float(self.total_horas) - float(self.horas_periodo)) < 0.01

    def to_dict(self):
        return {
            'horas_periodo': float(self.horas_periodo),
            'total_horas': float(self.total_horas),
            'cuadra': self.cuadra,
        }


class ReporteDiarioActividadTiempo(models.Model):
    """
    Horas dedicadas a una actividad del taladro durante el período del reporte.

    La actividad sale del catálogo 'Time Distribution Setup' del pozo (TipoDistribucionTiempo),
    pero se guarda por NÚMERO y con una copia de la descripción, no con una llave foránea:
    ese catálogo se guarda reemplazando todas sus filas, así que una llave foránea se perdería
    (o borraría el histórico) cada vez que alguien edita la configuración del pozo.
    """

    # Actividades que ONE-TRAX muestra siempre, en este orden, antes de las opcionales.
    NUMEROS_FIJOS = (1, 2, 3, 4)

    reporte = models.ForeignKey(
        ReporteDiario, on_delete=models.CASCADE, related_name='actividades_tiempo'
    )
    orden = models.PositiveSmallIntegerField(default=0, verbose_name="Orden")
    tipo_numero = models.PositiveIntegerField(verbose_name="Número de Actividad (catálogo del pozo)")
    descripcion = models.CharField(max_length=120, verbose_name="Actividad")
    horas = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Horas")

    class Meta:
        verbose_name = "Actividad de Distribución de Tiempo"
        verbose_name_plural = "Actividades de Distribución de Tiempo"
        ordering = ['orden', 'id']
        unique_together = ('reporte', 'tipo_numero')

    def __str__(self):
        return f"{self.reporte} - {self.descripcion}: {self.horas} h"

    @property
    def es_fija(self):
        return self.tipo_numero in self.NUMEROS_FIJOS

    def to_dict(self):
        return {
            'tipo_numero': self.tipo_numero,
            'descripcion': self.descripcion,
            'horas': float(self.horas),
            'es_fija': self.es_fija,
        }
