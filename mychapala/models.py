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
        help_text="Ej: TAMBOR 55 GLS, SACOS 55 LBS, TOTEMS 1000 LT. Se conserva como texto libre "
                   "para no romper la búsqueda y las planillas existentes; el dato estructurado "
                   "vive ahora en cantidad_unitaria/unidad_medida/tipo_empaque."
    )
    libraje = models.CharField(
        max_length=100,
        blank=True,
        default="N/A",
        verbose_name="Libraje (texto, legado)",
        help_text="Libraje o peso neto en texto libre (ej. 55 LBS, 100 LBS). Se conserva por "
                   "compatibilidad; para calcular usar el método libraje_final()."
    )
    gravedad_especifica = models.CharField(
        max_length=50,
        blank=True,
        default="N/A",
        verbose_name="Gravedad Específica",
        help_text="Gravedad específica o densidad técnica"
    )

    class UnidadMedida(models.TextChoices):
        LB = "LB", "Libras (LB)"
        KG = "KG", "Kilogramos (KG)"
        GA = "GA", "Galones (GA)"
        LT = "LT", "Litros (LT)"
        BBL = "BBL", "Barriles (BBL)"
        EA = "EA", "Unidad (EA) — sin conversión de peso"

    class TipoEmpaque(models.TextChoices):
        BG = "BG", "Saco / Bolsa (BG)"
        CN = "CN", "Lata / Cuñete (CN)"
        DM = "DM", "Tambor (DM)"
        TOTE = "TOTE", "Tote"
        BLS = "BLS", "Barril (BLS)"
        EA = "EA", "Unidad (EA) — sin empaque físico, ej. servicios"

    cantidad_unitaria = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Cantidad unitaria",
        help_text="Cantidad por unidad de empaque (ej. 100, 50, 25, 5, 1000). "
                   "Dato estructurado equivalente al primer número del antiguo 'Unit Size'.",
    )
    unidad_medida = models.CharField(
        max_length=3, choices=UnidadMedida.choices, blank=True,
        verbose_name="Unidad de medida",
        help_text="Unidad de esa cantidad (LB, KG, GA, LT, BBL, EA).",
    )
    tipo_empaque = models.CharField(
        max_length=4, choices=TipoEmpaque.choices, blank=True,
        verbose_name="Tipo de empaque",
        help_text="Empaque en que viene esa cantidad (BG, CN, DM, TOTE, BLS, EA).",
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

    def libraje_de(self, cantidad_empaques):
        """Libraje = cantidad_unitaria × cantidad_empaques (fórmula 7.1 del contexto del
        proyecto). Devuelve None si el producto todavía no tiene cantidad_unitaria cargada
        (productos migrados desde el texto libre que no se pudieron parsear con certeza)."""
        if self.cantidad_unitaria is None:
            return None
        return self.cantidad_unitaria * Decimal(str(cantidad_empaques))

    @property
    def libraje_stock(self):
        """Libraje del stock actual (self.cantidad empaques)."""
        return self.libraje_de(self.cantidad)

    def to_dict(self):
        """Serializa el objeto a diccionario para respuestas API JSON."""
        return {
            "id": self.id,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "unidad": self.unidad,
            "libraje": self.libraje,
            "gravedad_especifica": self.gravedad_especifica,
            "cantidad_unitaria": float(self.cantidad_unitaria) if self.cantidad_unitaria is not None else None,
            "unidad_medida": self.unidad_medida,
            "tipo_empaque": self.tipo_empaque,
            "libraje_stock": float(self.libraje_stock) if self.libraje_stock is not None else None,
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
            "codigo_reporte": self.codigo_reporte or f"REP-{self.id:04d}",
            "fecha": self.fecha.strftime("%Y-%m-%d"),
            "fecha_formato": self.fecha.strftime("%d/%m/%Y"),
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
            "total_items_usados": self.usos.count(),
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

    @property
    def libraje_usado(self):
        """Libraje de esta salida = cantidad_unitaria del producto × cantidad usada
        (sección 7.1 del contexto). None si el producto no tiene cantidad_unitaria cargada."""
        return self.producto.libraje_de(self.cantidad)

    def to_dict(self):
        """Serializa el registro de uso para la API JSON."""
        libraje_usado = self.libraje_usado
        return {
            "id": self.id,
            "reporte_id": self.reporte_id,
            "producto_id": self.producto_id,
            "producto_codigo": self.producto.codigo,
            "producto_descripcion": self.producto.descripcion,
            "producto_unidad": self.producto.unidad,
            "cantidad": self.cantidad,
            "libraje_usado": float(libraje_usado) if libraje_usado is not None else None,
            "precio_unitario": float(self.precio_unitario),
            "costo_total": float(self.costo_total),
            "observacion": self.observacion,
            "fecha_hora": self.fecha_hora.strftime("%d/%m/%Y %H:%M"),
        }
