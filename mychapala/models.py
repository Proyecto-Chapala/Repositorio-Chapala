"""
================================================================================
MÓDULO DE MODELOS - PROYECTO CHAPALA (SISTEMA DE INVENTARIO Y REPORTES DIARIOS)
================================================================================
Define la estructura de datos para:
1. Producto: Catálogo y especificaciones técnicas de productos químicos.
2. ReporteDiario: Metadatos, firmas y costo acumulativo diario.
3. RegistroUso: Detalle de salidas de insumos con precio variable y subtotal.
================================================================================
"""

import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone


class Producto(models.Model):
    """
    Modelo representativo de un Producto Químico / Insumo en el almacén.
    Almacena las especificaciones del diagrama:
    - Código (SKU)
    - Descripción (Nombre químico / comercial)
    - Unidad del producto (Presentación)
    - Libraje
    - Gravedad Específica
    - Cantidad (Stock físico actual)
    """
    codigo = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código / SKU",
        help_text="Identificador único del producto (ej. AOS-1001)"
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name="Descripción",
        help_text="Nombre descriptivo del producto químico"
    )
    unidad = models.CharField(
        max_length=100,
        verbose_name="Unidad / Presentación",
        help_text="Ej: TAMBOR 55 GLS, SACOS 55 LBS, TOTEMS 1000 LT"
    )
    libraje = models.CharField(
        max_length=100,
        blank=True,
        default="N/A",
        verbose_name="Libraje",
        help_text="Libraje o peso neto (ej. 55 LBS, 100 LBS)"
    )
    gravedad_especifica = models.CharField(
        max_length=50,
        blank=True,
        default="N/A",
        verbose_name="Gravedad Específica",
        help_text="Gravedad específica o densidad técnica"
    )
    cantidad = models.IntegerField(
        default=0,
        verbose_name="Cantidad / Stock Actual",
        help_text="Existencia física actual en inventario"
    )
    stock_inicial = models.IntegerField(
        default=0,
        verbose_name="Stock Inicial",
        help_text="Existencia al inicio del período o creación"
    )
    CATEGORIA_CHOICES = [
        ('quimico', 'Producto Químico'),
        ('liquido', 'Producto Líquido'),
        ('wellsite', 'Wellsite Chemical Inventory'),
    ]

    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIA_CHOICES,
        default='quimico',
        db_index=True,
        verbose_name="Categoría",
        help_text="Clasificación del producto (Químico, Líquido o Wellsite)"
    )
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Precio / Costo Unitario ($)",
        help_text="Costo o precio base unitario del producto"
    )
    cum_used = models.IntegerField(
        default=0,
        verbose_name="Acumulado Usado (Cum Used)",
        help_text="Cantidad acumulada utilizada (Wellsite)"
    )
    daily_received = models.IntegerField(
        default=0,
        verbose_name="Recibido Diario (Daily Rec'd)",
        help_text="Cantidad recibida en el día"
    )
    cum_received = models.IntegerField(
        default=0,
        verbose_name="Acumulado Recibido (Cum Rec'd)",
        help_text="Total acumulado recibido"
    )
    daily_return = models.IntegerField(
        default=0,
        verbose_name="Devuelto Diario (Daily Return)",
        help_text="Cantidad devuelta en el día"
    )
    cum_return = models.IntegerField(
        default=0,
        verbose_name="Acumulado Devuelto (Cum Return)",
        help_text="Total acumulado devuelto"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el producto está disponible en el inventario"
    )
    cantidad_unitaria = models.DecimalField(
        blank=True,
        decimal_places=2,
        max_digits=10,
        null=True,
        verbose_name="Cantidad unitaria",
        help_text="Cantidad por unidad de empaque (ej. 100, 50, 25, 5, 1000). Dato estructurado equivalente al primer número del antiguo 'Unit Size'."
    )
    unidad_medida = models.CharField(
        blank=True,
        max_length=3,
        choices=[
            ("LB", "Libras (LB)"),
            ("KG", "Kilogramos (KG)"),
            ("GA", "Galones (GA)"),
            ("LT", "Litros (LT)"),
            ("BBL", "Barriles (BBL)"),
            ("EA", "Unidad (EA) — sin conversión de peso"),
        ],
        verbose_name="Unidad de medida",
        help_text="Unidad de esa cantidad (LB, KG, GA, LT, BBL, EA)."
    )
    tipo_empaque = models.CharField(
        blank=True,
        max_length=4,
        choices=[
            ("BG", "Saco / Bolsa (BG)"),
            ("CN", "Lata / Cuñete (CN)"),
            ("DM", "Tambor (DM)"),
            ("TOTE", "Tote"),
            ("BLS", "Barril (BLS)"),
            ("EA", "Unidad (EA) — sin empaque físico, ej. servicios"),
        ],
        verbose_name="Tipo de empaque",
        help_text="Empaque en que viene esa cantidad (BG, CN, DM, TOTE, BLS, EA)."
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Modificación"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["id"]

    def __str__(self):
        return f"{self.codigo} - {self.descripcion} ({self.cantidad} {self.unidad})"

    @property
    def estado_stock(self):
        """Calcula el estado visual del inventario."""
        if self.cantidad <= 0:
            return {"label": "Sin Stock", "badge_class": "status-out", "tipo": "danger"}
        elif self.cantidad <= 15:
            return {"label": "Bajo Stock", "badge_class": "status-low", "tipo": "warning"}
        elif self.cantidad <= 100:
            return {"label": "Stock Medio", "badge_class": "status-medium", "tipo": "info"}
        else:
            return {"label": "Stock Alto", "badge_class": "status-high", "tipo": "success"}

    def to_dict(self):
        """Serializa el objeto a diccionario para respuestas API JSON."""
        return {
            "id": self.id,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "unidad": self.unidad,
            "libraje": self.libraje,
            "gravedad_especifica": self.gravedad_especifica,
            "cantidad": self.cantidad,
            "stock_inicial": self.stock_inicial,
            "categoria": self.categoria,
            "precio_unitario": float(self.precio_unitario),
            "cum_used": self.cum_used,
            "daily_received": self.daily_received,
            "cum_received": self.cum_received,
            "daily_return": self.daily_return,
            "cum_return": self.cum_return,
            "estado": self.estado_stock,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion.strftime("%d/%m/%Y %H:%M") if self.fecha_creacion else "",
            "fecha_modificacion": self.fecha_modificacion.strftime("%d/%m/%Y %H:%M") if self.fecha_modificacion else "",
        }


class ReporteDiario(models.Model):
    """
    Modelo para el Reporte Diario Acumulativo de Almacén.
    Almacena los metadatos de la sección General:
    - Departamento
    - Encargado
    - Fecha
    - Comentarios / Observaciones Generales
    - Firmas de Elaboración y Revisión
    - Costo Final Acumulado de los productos usados
    """
    fecha = models.DateField(
        default=timezone.now,
        unique=True,
        db_index=True,
        verbose_name="Fecha del Reporte"
    )
    departamento = models.CharField(
        max_length=150,
        default="ALMACÉN",
        verbose_name="Departamento"
    )
    encargado = models.CharField(
        max_length=150,
        default="LUIS BRICEÑO",
        verbose_name="Encargado"
    )
    elaborado_por_nombre = models.CharField(
        max_length=150,
        default="Lusneila Franceschi",
        verbose_name="Elaborado Por (Nombre)"
    )
    elaborado_por_cargo = models.CharField(
        max_length=150,
        default="Administración",
        verbose_name="Elaborado Por (Cargo)"
    )
    revisado_por_nombre = models.CharField(
        max_length=150,
        default="Luis Briceño",
        verbose_name="Revisado Por (Nombre)"
    )
    revisado_por_cargo = models.CharField(
        max_length=150,
        default="Encargado de Almacen",
        verbose_name="Revisado Por (Cargo)"
    )
    codigo_reporte = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        db_index=True,
        verbose_name="Número / Identificación del Reporte",
        help_text="Ej: REP-2026-0001 o AOS-REP-0001"
    )
    observaciones = models.TextField(
        blank=True,
        default="",
        verbose_name="Observaciones / Comentarios Generales",
        help_text="Notas o comentarios generales del reporte del día"
    )
    operador = models.CharField(
        max_length=150,
        default="Cardon IV",
        blank=True,
        verbose_name="Operador (Wellsite)"
    )
    pozo = models.CharField(
        max_length=150,
        default="Perla-1X",
        blank=True,
        verbose_name="Pozo / Well Name"
    )
    locacion = models.CharField(
        max_length=150,
        default="Offshore",
        blank=True,
        verbose_name="Locación"
    )
    reporte_no_wellsite = models.CharField(
        max_length=50,
        default="16",
        blank=True,
        verbose_name="Report No (Wellsite)"
    )
    # -------------------------------------------------------------------------
    # ESPECIFICACIÓN: 04A_Starting_New_Day_General_Time_Distribution.md
    # -------------------------------------------------------------------------
    total_depth = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Total Depth (MD) (ft)", help_text="Profundidad total medida del pozo"
    )
    tvd = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="True Vertical Depth (ft)", help_text="Profundidad vertical verdadera"
    )
    midnight_depth = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Midnight Depth (ft)", help_text="Profundidad a las 00:00 hrs"
    )
    rotating_hours = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, default=Decimal("0.00"),
        verbose_name="Horas Rotando", help_text="Horas de rotación en 24h"
    )
    circulating_hours = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, default=Decimal("0.00"),
        verbose_name="Horas Circulando", help_text="Horas de circulación en 24h"
    )

    # -------------------------------------------------------------------------
    # ESPECIFICACIÓN: 05_Geometry_Volume_Accounting.md
    # -------------------------------------------------------------------------
    # 1. Geometría de Hoyo, Sarta y Parámetros Offshore/Riser (Geometry Tab)
    bit_depth = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Bit Depth (ft)", help_text="Profundidad actual de la mecha"
    )
    bit_size = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="Bit Size (in)", help_text="Diámetro de la mecha"
    )
    porcentaje_washout = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"),
        verbose_name="% Washout", help_text="Porcentaje de ensanchamiento del hoyo"
    )
    tipo_seccion_hoyo = models.CharField(
        max_length=20,
        choices=[
            ('casing', 'Casing'),
            ('liner', 'Liner'),
            ('open_hole', 'Open Hole'),
        ],
        default='open_hole',
        blank=True,
        verbose_name="Tipo de Sección del Hoyo"
    )
    water_depth = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Water Depth (ft)", help_text="Profundidad de agua (Offshore)"
    )
    air_gap = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Air Gap (ft)", help_text="Distancia vertical nivel del mar a mesa rotaria"
    )
    riserless_drilling = models.BooleanField(
        default=True, verbose_name="¿Riserless Drilling?",
        help_text="Activo si no se utiliza riser en perforación marina"
    )
    riser_od = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="Riser OD (in)"
    )
    riser_id = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="Riser ID (in)"
    )
    riser_length = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Riser Length (ft)", help_text="Longitud efectiva (Water Depth - Air Gap)"
    )

    # 2. Contabilidad Volumétrica (Volume Accounting Tab)
    volumen_anular = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Volumen Anular (Annulus, bbl)"
    )
    volumen_sarta = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Volumen Sarta (Total DS, bbl)"
    )
    volumen_debajo_mecha = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Volumen Debajo de Mecha (Below Bit, bbl)"
    )
    volumen_no_fluido = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Volumen No Fluido (Volume Not Fluids, bbl)"
    )
    volumen_teorico_fosas = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Volumen Teórico Fosas (Calc End Volume, bbl)"
    )
    volumen_medido_fosas = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Volumen Medido Fosas (Actual End Volume, bbl)"
    )
    total_perdidas_superficie = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Pérdidas de Superficie (bbl)"
    )
    total_perdidas_subsuelo = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Pérdidas de Subsuelo (bbl)"
    )
    total_perdidas_mecanicas = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Pérdidas Mecánicas (bbl)"
    )

    costo_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Costo Final Acumulado",
        help_text="Sumatoria automática del costo de los productos usados en el día"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )

    class Meta:
        verbose_name = "Reporte Diario"
        verbose_name_plural = "Reportes Diarios"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.codigo_reporte or f'REP-{self.id}'} ({self.fecha.strftime('%d/%m/%Y')}) - {self.departamento} (Total: ${self.costo_total})"

    def save(self, *args, **kwargs):
        if not self.codigo_reporte:
            count = ReporteDiario.objects.count() + 1
            self.codigo_reporte = f"REP-{self.fecha.strftime('%Y')}-{count:04d}"
        super().save(*args, **kwargs)

    @property
    def progreso_diario(self):
        """Progreso perforado en las últimas 24 hrs: Total Depth - Midnight Depth."""
        if self.total_depth is not None and self.midnight_depth is not None:
            return (self.total_depth - self.midnight_depth).quantize(Decimal("0.01"))
        return None

    @property
    def hole_size(self):
        """Hole Size = Bit Size * (1 + % Washout / 100). Si Washout es 0, hoyo en calibre (gauge hole)."""
        if self.bit_size is not None:
            factor = Decimal("1.0") + (self.porcentaje_washout / Decimal("100.0"))
            return (self.bit_size * factor).quantize(Decimal("0.001"))
        return None

    @property
    def total_hole_volume(self):
        """Total Hole Volume = Annulus + Total DS + Below Bit."""
        return self.volumen_anular + self.volumen_sarta + self.volumen_debajo_mecha

    @property
    def fluid_volume(self):
        """Fluid Volume = Total Hole Volume - Volume Not Fluids."""
        return self.total_hole_volume - self.volumen_no_fluido

    @property
    def not_accounted(self):
        """Not Accounted = Volumen Teórico Fosas - Volumen Medido Fosas."""
        return (self.volumen_teorico_fosas - self.volumen_medido_fosas).quantize(Decimal("0.01"))

    @property
    def balance_cuadrado(self):
        return abs(self.not_accounted) < Decimal("0.01")

    def recalcular_costo_total(self):
        """Calcula y actualiza la sumatoria de costos de todos los registros de uso asociados."""
        total = self.usos.aggregate(total_sum=models.Sum("costo_total"))["total_sum"] or Decimal("0.00")
        self.costo_total = total
        self.save(update_fields=["costo_total", "fecha_actualizacion"])
        return total

    def to_dict(self):
        """Serializa el reporte para la API JSON."""
        return {
            "id": self.id,
            "codigo_reporte": self.codigo_reporte or (f"REP-{self.id:04d}" if self.id else "REP-0000"),
            "fecha": self.fecha.strftime("%Y-%m-%d") if self.fecha else "",
            "fecha_formato": self.fecha.strftime("%d/%m/%Y") if self.fecha else "",
            "departamento": self.departamento,
            "encargado": self.encargado,
            "elaborado_por_nombre": self.elaborado_por_nombre,
            "elaborado_por_cargo": self.elaborado_por_cargo,
            "revisado_por_nombre": self.revisado_por_nombre,
            "revisado_por_cargo": self.revisado_por_cargo,
            "observaciones": self.observaciones,
            "operador": self.operador,
            "pozo": self.pozo,
            "locacion": self.locacion,
            "reporte_no_wellsite": self.reporte_no_wellsite,
            "costo_total": float(self.costo_total),
            "total_items_usados": self.usos.count() if self.id else 0,
            # Especificación 04A_Starting_New_Day_General_Time_Distribution
            "total_depth": float(self.total_depth) if self.total_depth is not None else None,
            "tvd": float(self.tvd) if self.tvd is not None else None,
            "midnight_depth": float(self.midnight_depth) if self.midnight_depth is not None else None,
            "progreso_diario": float(self.progreso_diario) if self.progreso_diario is not None else None,
            "rotating_hours": float(self.rotating_hours) if self.rotating_hours is not None else 0.0,
            "circulating_hours": float(self.circulating_hours) if self.circulating_hours is not None else 0.0,
            # Especificación 05_Geometry_Volume_Accounting
            "bit_depth": float(self.bit_depth) if self.bit_depth is not None else None,
            "bit_size": float(self.bit_size) if self.bit_size is not None else None,
            "porcentaje_washout": float(self.porcentaje_washout),
            "hole_size": float(self.hole_size) if self.hole_size is not None else None,
            "tipo_seccion_hoyo": self.tipo_seccion_hoyo,
            "water_depth": float(self.water_depth) if self.water_depth is not None else None,
            "air_gap": float(self.air_gap) if self.air_gap is not None else None,
            "riserless_drilling": self.riserless_drilling,
            "riser_od": float(self.riser_od) if self.riser_od is not None else None,
            "riser_id": float(self.riser_id) if self.riser_id is not None else None,
            "riser_length": float(self.riser_length) if self.riser_length is not None else None,
            "volumen_anular": float(self.volumen_anular),
            "volumen_sarta": float(self.volumen_sarta),
            "volumen_debajo_mecha": float(self.volumen_debajo_mecha),
            "total_hole_volume": float(self.total_hole_volume),
            "volumen_no_fluido": float(self.volumen_no_fluido),
            "fluid_volume": float(self.fluid_volume),
            "volumen_teorico_fosas": float(self.volumen_teorico_fosas),
            "volumen_medido_fosas": float(self.volumen_medido_fosas),
            "total_perdidas_superficie": float(self.total_perdidas_superficie),
            "total_perdidas_subsuelo": float(self.total_perdidas_subsuelo),
            "total_perdidas_mecanicas": float(self.total_perdidas_mecanicas),
            "not_accounted": float(self.not_accounted),
            "balance_cuadrado": self.balance_cuadrado,
        }


class RegistroUso(models.Model):
    """
    Modelo para el registro de salidas / consumos de productos químicos (Pestaña Uso).
    Características:
    - Vinculado al Reporte Diario.
    - Vinculado al Producto retirado.
    - Ingreso de Cantidad utilizada.
    - Ingreso de Precio Unitario (Variable, solicitado en cada operación).
    - Multiplicación automática: Subtotal / Costo Total = Cantidad * Precio Unitario.
    - Campo de Observación / Comentario opcional por cada salida.
    """
    reporte = models.ForeignKey(
        ReporteDiario,
        on_delete=models.CASCADE,
        related_name="usos",
        verbose_name="Reporte Diario Asociado"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="usos",
        verbose_name="Producto Utilizado"
    )
    cantidad = models.IntegerField(
        default=1,
        verbose_name="Cantidad Utilizada",
        help_text="Número de unidades/bultos retirados del inventario"
    )
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Precio Unitario",
        help_text="Precio variable fijado al momento de la salida"
    )
    costo_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Costo Subtotal (Cantidad × Precio)"
    )
    observacion = models.TextField(
        blank=True,
        default="",
        verbose_name="Observación de la Salida",
        help_text="Comentario o justificación del uso de este producto"
    )
    fecha_hora = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha y Hora del Registro"
    )

    class Meta:
        verbose_name = "Registro de Uso"
        verbose_name_plural = "Registros de Uso"
        ordering = ["-fecha_hora"]

    def __str__(self):
        return f"{self.producto.codigo} - {self.cantidad} {self.producto.unidad} @ ${self.precio_unitario} = ${self.costo_total}"

    def save(self, *args, **kwargs):
        """Calcula el costo total automáticamente antes de persistir."""
        self.costo_total = Decimal(str(self.cantidad)) * Decimal(str(self.precio_unitario))
        super().save(*args, **kwargs)
        # Recalcula el costo acumulado en el reporte
        self.reporte.recalcular_costo_total()

    def delete(self, *args, **kwargs):
        """Restituye el stock y actualiza el reporte al eliminar."""
        reporte_ref = self.reporte
        super().delete(*args, **kwargs)
        reporte_ref.recalcular_costo_total()

    def to_dict(self):
        """Serializa el registro de uso para la API JSON."""
        return {
            "id": self.id,
            "reporte_id": self.reporte_id,
            "producto_id": self.producto_id,
            "producto_codigo": self.producto.codigo,
            "producto_descripcion": self.producto.descripcion,
            "producto_unidad": self.producto.unidad,
            "cantidad": self.cantidad,
            "precio_unitario": float(self.precio_unitario),
            "costo_total": float(self.costo_total),
            "observacion": self.observacion,
            "fecha_hora": self.fecha_hora.strftime("%d/%m/%Y %H:%M"),
        }


# ==============================================================================
# MODELOS DE SOPORTE: ESPECIFICACIÓN 05_Geometry_Volume_Accounting.md
# ==============================================================================

class GeometriaHoyo(models.Model):
    """
    Wellbore Geometry (Geometría del Hoyo). Sección 1.
    Clasifica secciones en Casing, Liner u Open Hole con cálculo de Hole Size y capacidades.
    """
    class TipoSeccion(models.TextChoices):
        CASING = "casing", "Casing"
        LINER = "liner", "Liner"
        OPEN_HOLE = "open_hole", "Open Hole"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(
        ReporteDiario, on_delete=models.CASCADE, related_name="geometrias_hoyo",
        verbose_name="Reporte Diario"
    )
    tipo = models.CharField(
        max_length=20, choices=TipoSeccion.choices, default=TipoSeccion.OPEN_HOLE,
        verbose_name="Tipo de Sección"
    )
    diametro = models.DecimalField(
        max_digits=6, decimal_places=3,
        verbose_name="Diámetro / Hole Size (in)"
    )
    profundidad_tope = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Profundidad Tope (ft)"
    )
    profundidad_base = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Profundidad Base (ft)"
    )
    capacidad = models.DecimalField(
        max_digits=10, decimal_places=4, default=Decimal("0.00"),
        verbose_name="Capacidad (bbl/ft)"
    )
    volumen = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Volumen Sección (bbl)"
    )

    class Meta:
        verbose_name = "Geometría del Hoyo"
        verbose_name_plural = "Geometrías del Hoyo (Wellbore Geometry)"
        ordering = ["profundidad_tope"]

    def __str__(self):
        return f"{self.get_tipo_display()} ({self.diametro}\") {self.profundidad_tope}'-{self.profundidad_base}'"

    def to_dict(self):
        return {
            "id": str(self.id),
            "reporte_id": self.reporte_id,
            "tipo": self.tipo,
            "tipo_display": self.get_tipo_display(),
            "diametro": float(self.diametro),
            "profundidad_tope": float(self.profundidad_tope),
            "profundidad_base": float(self.profundidad_base),
            "capacidad": float(self.capacidad),
            "volumen": float(self.volumen),
        }


class TramoSarta(models.Model):
    """
    Sarta de perforación (Drill String Geometry). Sección 1.
    Componentes individuales con cálculo inverso de longitud para el tramo principal.
    """
    class TipoComponente(models.TextChoices):
        DRILL_PIPE = "drill_pipe", "Drill Pipe"
        HEAVY_WEIGHT = "heavy_weight", "Heavy Weight Drill Pipe"
        DRILL_COLLAR = "drill_collar", "Drill Collar"
        SUB = "sub", "Sub / Herramienta BHA"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(
        ReporteDiario, on_delete=models.CASCADE, related_name="tramos_sarta",
        verbose_name="Reporte Diario Asociado"
    )
    tipo = models.CharField(max_length=30, choices=TipoComponente.choices, default=TipoComponente.DRILL_PIPE)
    diametro_externo = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal("0.000"), verbose_name="OD (in)")
    diametro_interno = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal("0.000"), verbose_name="ID (in)")
    longitud = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Longitud (ft)",
        help_text="Si es el componente superior (Drill Pipe), se autocalcula como Bit Depth - sum(BHA)"
    )
    es_principal = models.BooleanField(
        default=False,
        verbose_name="¿Es tramo principal?",
        help_text="El primer tramo cuya longitud absorbe la profundidad de la mecha"
    )

    class Meta:
        verbose_name = "Tramo de Sarta"
        verbose_name_plural = "Tramos de Sarta (Drill String)"

    def __str__(self):
        return f"{self.get_tipo_display()} OD {self.diametro_externo}\" x ID {self.diametro_interno}\""

    def to_dict(self):
        return {
            "id": str(self.id),
            "reporte_id": self.reporte_id,
            "tipo": self.tipo,
            "tipo_display": self.get_tipo_display(),
            "diametro_externo": float(self.diametro_externo),
            "diametro_interno": float(self.diametro_interno),
            "longitud": float(self.longitud) if self.longitud is not None else None,
            "es_principal": self.es_principal,
        }


class Fosa(models.Model):
    """
    Inventario y estado de fosas/tanques del taladro (Pit Section & Non-Transactional Pits). Sección 2.
    """
    class TipoFosa(models.TextChoices):
        ACTIVE = "active", "Active"
        RESERVE = "reserve", "Reserve"
        PREMIX = "premix", "Premix"
        SPACER = "spacer", "Spacer"
        STORAGE = "storage", "Storage (Non-Transactional)"
        DEAD_VOLUME = "dead_volume", "Dead Volume"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(
        ReporteDiario, on_delete=models.CASCADE, related_name="fosas",
        null=True, blank=True, verbose_name="Reporte Diario"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre / Descripción de la Fosa")
    tipo = models.CharField(max_length=20, choices=TipoFosa.choices, default=TipoFosa.ACTIVE)
    capacidad = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name="Capacidad Máxima (bbl)")
    volumen_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name="Start Volume (bbl)")
    volumen_final_teorico = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name="Calc End Volume (bbl)")
    volumen_final_medido = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name="Actual End Volume (bbl)")
    peso_lodo = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Fluid Weight (ppg)")
    es_transaccional = models.BooleanField(
        default=True, verbose_name="¿Es transaccional?",
        help_text="Si es False, es almacenamiento pasivo (Non-Transactional Pits) que no entra en el balance activo"
    )

    class Meta:
        verbose_name = "Fosa / Tanque"
        verbose_name_plural = "Fosas y Tanques (Pit Section)"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

    def to_dict(self):
        return {
            "id": str(self.id),
            "nombre": self.nombre,
            "tipo": self.tipo,
            "tipo_display": self.get_tipo_display(),
            "capacidad": float(self.capacidad),
            "volumen_inicial": float(self.volumen_inicial),
            "volumen_final_teorico": float(self.volumen_final_teorico),
            "volumen_final_medido": float(self.volumen_final_medido),
            "peso_lodo": float(self.peso_lodo) if self.peso_lodo is not None else None,
            "es_transaccional": self.es_transaccional,
        }


class TransaccionVolumetrica(models.Model):
    """
    Transacciones volumétricas del libro mayor (Transaction Buttons). Sección 3.
    Add Chemicals, Add Whole Mud, Transfer, Return (Back Load) y Equipment Loss.
    """
    class TipoTransaccion(models.TextChoices):
        ADD_CHEMICALS = "add_chemicals", "Add Chemicals"
        ADD_WHOLE_MUD = "add_whole_mud", "Add Whole Mud"
        TRANSFER = "transfer", "Transfer"
        RETURN_BACK_LOAD = "return_back_load", "Return (Back Load)"
        EQUIPMENT_LOSS = "equipment_loss", "Create Equipment Loss Transaction"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(
        ReporteDiario, on_delete=models.CASCADE, related_name="transacciones_volumetricas",
        verbose_name="Reporte Diario"
    )
    tipo = models.CharField(max_length=30, choices=TipoTransaccion.choices)
    fosa_origen = models.ForeignKey(
        Fosa, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="transacciones_salida", verbose_name="Fosa Origen"
    )
    fosa_destino = models.ForeignKey(
        Fosa, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="transacciones_entrada", verbose_name="Fosa Destino"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="transacciones_volumen", verbose_name="Producto Asociado"
    )
    volumen = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), verbose_name="Volumen (bbl)")
    is_dilution = models.BooleanField(
        default=False, verbose_name="¿Es Dilución (Is Dilution)?",
        help_text="Etiqueta el movimiento como táctica de reducción de sólidos de baja gravedad (LGS)"
    )
    add_without_charge = models.BooleanField(
        default=False, verbose_name="¿Agregar Sin Cargo (Add Without Charge)?",
        help_text="Saltea la facturación si el lodo a granel pertenece a la operadora"
    )
    all_volume = models.BooleanField(
        default=False, verbose_name="¿Todo el Volumen (All Volume)?",
        help_text="Vacía a cero la fosa origen previniendo residuos decimales"
    )
    comentario = models.TextField(blank=True, default="", verbose_name="Comentario de la Transacción")
    fecha_hora = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora")

    class Meta:
        verbose_name = "Transacción Volumétrica"
        verbose_name_plural = "Transacciones Volumétricas (Transaction Buttons)"
        ordering = ["-fecha_hora"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.volumen} bbl"

    def to_dict(self):
        return {
            "id": str(self.id),
            "reporte_id": self.reporte_id,
            "tipo": self.tipo,
            "tipo_display": self.get_tipo_display(),
            "fosa_origen": self.fosa_origen.nombre if self.fosa_origen else None,
            "fosa_destino": self.fosa_destino.nombre if self.fosa_destino else None,
            "producto": self.producto.descripcion if self.producto else None,
            "volumen": float(self.volumen),
            "is_dilution": self.is_dilution,
            "add_without_charge": self.add_without_charge,
            "all_volume": self.all_volume,
            "comentario": self.comentario,
            "fecha_hora": self.fecha_hora.strftime("%d/%m/%Y %H:%M"),
        }


class Desplazamiento(models.Model):
    """
    Gestión de Desplazamientos (Displacements Tab). Sección 4.
    Tren de baches, píldoras viscosas y disposición de fluidos retornados (Reclaimed).
    """
    class TipoComponente(models.TextChoices):
        SPACER = "spacer", "Espaciador"
        VISCOUS_PILL = "viscous_pill", "Píldora Viscosa"
        BRINE = "brine", "Salmuera"
        MUD = "mud", "Lodo"
        WATER = "water", "Agua de Lavado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(
        ReporteDiario, on_delete=models.CASCADE, related_name="desplazamientos",
        verbose_name="Reporte Diario"
    )
    tipo_componente = models.CharField(
        max_length=30, choices=TipoComponente.choices, default=TipoComponente.SPACER,
        verbose_name="Tipo de Componente (Tren de Baches)"
    )
    descripcion = models.CharField(
        max_length=150, blank=True, default="",
        verbose_name="Descripción / Nombre del Bache"
    )
    fosa_origen = models.ForeignKey(
        Fosa, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="desplazamientos_origen",
        verbose_name="Fosa de Mezcla Previa (Precondición de Volume Accounting)"
    )
    volumen = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Volumen del Componente (bbl)"
    )
    reclaimed = models.BooleanField(
        default=False, verbose_name="¿Recuperado en Superficie (Reclaimed)?",
        help_text="Controla si el fluido retornado a superficie se recupera en tanques"
    )
    fosa_retorno = models.ForeignKey(
        Fosa, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="desplazamientos_retorno",
        verbose_name="Tanque de Retorno (Reclaimed to Pit)"
    )
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden en el Tren de Baches")
    observaciones = models.TextField(blank=True, default="", verbose_name="Observaciones de la Maniobra")

    class Meta:
        verbose_name = "Desplazamiento / Bache"
        verbose_name_plural = "Desplazamientos (Displacements Tab)"
        ordering = ["reporte", "orden"]

    def __str__(self):
        return f"Bache #{self.orden}: {self.get_tipo_componente_display()} ({self.volumen} bbl)"

    def to_dict(self):
        return {
            "id": str(self.id),
            "reporte_id": self.reporte_id,
            "tipo_componente": self.tipo_componente,
            "tipo_componente_display": self.get_tipo_componente_display(),
            "descripcion": self.descripcion,
            "fosa_origen": self.fosa_origen.nombre if self.fosa_origen else None,
            "volumen": float(self.volumen),
            "reclaimed": self.reclaimed,
            "fosa_retorno": self.fosa_retorno.nombre if self.fosa_retorno else None,
            "orden": self.orden,
            "observaciones": self.observaciones,
        }

