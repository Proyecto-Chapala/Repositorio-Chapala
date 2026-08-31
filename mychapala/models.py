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
