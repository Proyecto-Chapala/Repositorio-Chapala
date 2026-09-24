"""
Pestaña 8 del reporte diario — Inventario, Hidráulica y Concentraciones
(ONE-TRAX: Inv/Hyd/Conc).

- "Pérdidas del reporte" (Daily Loss Print Selection).
- Volumetría e inventario de productos (Volume Accounting and Product Inventory).

Como en las pestañas 6 y 7, las fosas, los productos y las categorías de pérdida se
referencian por NÚMERO / CÓDIGO / catálogo maestro con copia del texto, no por llave
foránea a las listas del pozo: esas listas se guardan borrando y recreando sus filas.
Los volúmenes calculados, el balance, el inventario y las concentraciones NO se guardan:
se derivan repitiendo los movimientos del pozo (volumetria.py).
"""

from django.db import models

from .models import Pozo, Producto
from .models_daily_reports import ReporteDiario
from .models_control_solidos import TipoTicketMalla


class PerdidaReportePozo(models.Model):
    """
    Categorías de pérdida que se muestran en el reporte diario (máximo 10), en orden.

    El pozo puede tener hasta 20 categorías (Configuración de Pérdidas), pero el reporte
    diario solo imprime 10. La selección es POR POZO (decisión del usuario) y se guarda
    por CÓDIGO de categoría: la Configuración de Pérdidas se guarda recreando sus filas.
    Si el pozo no tiene selección guardada, se usan las 10 primeras por código.
    """

    MAXIMO_EN_REPORTE = 10

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='perdidas_reporte')
    codigo = models.PositiveSmallIntegerField(verbose_name="Código de la categoría de pérdida")
    orden = models.PositiveSmallIntegerField(default=0, verbose_name="Orden en el reporte")

    class Meta:
        verbose_name = "Pérdida Mostrada en el Reporte"
        verbose_name_plural = "Pérdidas Mostradas en el Reporte"
        unique_together = ('pozo', 'codigo')
        ordering = ['orden', 'codigo']

    def __str__(self):
        return f"{self.pozo.nombre} — pérdida {self.codigo}"


# =====================================================================
# Volumetría (Volume Accounting)
# =====================================================================

class VolumenFosaDia(models.Model):
    """
    Datos del día de una fosa: el tipo con que se usó (activa, reserva, premezcla...) y lo
    que el ingeniero MIDIÓ al cierre. El volumen calculado no se guarda: sale de los
    movimientos. El manual insiste: el volumen real no se cambia para cuadrar el balance.
    """

    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='volumenes_fosa')
    fosa_numero = models.PositiveSmallIntegerField(verbose_name="N° de Fosa")
    fosa_descripcion = models.CharField(max_length=100, blank=True, verbose_name="Fosa")
    capacidad = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Capacidad (bbl)")
    tipo_codigo = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Tipo de fosa (código)")
    tipo_descripcion = models.CharField(max_length=100, blank=True, verbose_name="Tipo de fosa")
    volumen_final = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Volumen final real (bbl)"
    )
    peso_fluido = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Peso del fluido (lb/gal)")
    temperatura = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name="Temperatura (°F)")

    class Meta:
        verbose_name = "Volumen Diario de Fosa"
        verbose_name_plural = "Volúmenes Diarios de Fosas"
        unique_together = ('reporte', 'fosa_numero')
        ordering = ['fosa_numero']


class VolumenHoyoDia(models.Model):
    """Volumen del hoyo que NO ocupa el fluido del sistema activo (Volume Not Fluids)."""

    reporte = models.OneToOneField(ReporteDiario, on_delete=models.CASCADE, related_name='volumen_hoyo')
    no_fluido_anular = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="No fluido — anular (bbl)")
    no_fluido_sarta = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="No fluido — sarta (bbl)")
    no_fluido_bajo_mecha = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="No fluido — bajo la mecha (bbl)")

    class Meta:
        verbose_name = "Volumen del Hoyo del Día"
        verbose_name_plural = "Volúmenes del Hoyo por Día"


class TransaccionVolumen(models.Model):
    """
    Movimiento de fluido o de productos (Add Chemicals, Add Whole Mud, Transfer/Loss).
    'secuencia' crece por pozo: solo la última se puede deshacer (Undo Last Transaction).
    """

    QUIMICOS = 'QUIMICOS'
    LODO_ENTERO = 'LODO_ENTERO'
    TRANSFERENCIA = 'TRANSFERENCIA'
    DEVOLUCION = 'DEVOLUCION'
    PERDIDA = 'PERDIDA'
    TIPO_CHOICES = [
        (QUIMICOS, 'Agregar químicos'),
        (LODO_ENTERO, 'Agregar lodo entero'),
        (TRANSFERENCIA, 'Transferencia entre fosas'),
        (DEVOLUCION, 'Devolución'),
        (PERDIDA, 'Pérdida y descarte'),
    ]

    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='transacciones_volumen')
    secuencia = models.PositiveIntegerField(verbose_name="N° de Movimiento")
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, verbose_name="Tipo")

    fosa_numero = models.PositiveSmallIntegerField(verbose_name="Fosa")
    fosa_descripcion = models.CharField(max_length=100, blank=True)
    destino_numero = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Fosa destino")
    destino_descripcion = models.CharField(max_length=100, blank=True)

    volumen_bbl = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Volumen (bbl)")
    aceite_bbl = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Fluido base agregado (bbl)")
    agua_bbl = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Agua agregada (bbl)")
    peso_lodo = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Peso del lodo (lb/gal)")

    # Lodo entero: producto del inventario que se consume (ej. VERSACLEAN MUD 11.5 ppg).
    lodo_producto = models.ForeignKey(Producto, on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    lodo_producto_texto = models.CharField(max_length=255, blank=True)
    lodo_cantidad = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name="Cantidad consumida")
    lodo_precio = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    lodo_categoria = models.PositiveSmallIntegerField(default=1)

    origen_destino = models.CharField(max_length=120, blank=True, verbose_name="Recibido de / Devuelto a")
    perdida_codigo = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Tipo de pérdida (código)")
    perdida_descripcion = models.CharField(max_length=100, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimiento de Volumetría"
        verbose_name_plural = "Movimientos de Volumetría"
        ordering = ['secuencia']


class TransaccionVolumenProducto(models.Model):
    """
    Producto de un movimiento. En 'Agregar químicos' es la CANTIDAD agregada (en la unidad
    del producto); en 'Agregar lodo entero' es la CONCENTRACIÓN del lodo (lb/bbl), que solo
    sirve para el cálculo de concentraciones. Guarda copia de los datos del producto.
    """

    transaccion = models.ForeignKey(TransaccionVolumen, on_delete=models.CASCADE, related_name='productos')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='+')
    descripcion = models.CharField(max_length=255, blank=True)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    es_concentracion = models.BooleanField(default=False)
    unidad = models.CharField(max_length=30, blank=True)
    tamano = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    gravedad = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    precio = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    categoria_costo = models.PositiveSmallIntegerField(default=1)
    calcula_concentracion = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Producto de Movimiento de Volumetría"
        verbose_name_plural = "Productos de Movimientos de Volumetría"
        ordering = ['id']


class InventarioProductoDia(models.Model):
    """
    Columnas del inventario que el ingeniero llena a mano: uso en otro módulo (personal de
    servicio, por ejemplo días de ingeniero), ajuste, cantidad pedida y "no imprimir".
    """

    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='inventario_productos')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='+')
    usado_otro = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name="Usado en otro módulo")
    ajuste = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name="Ajuste (+ suma / − resta)")
    en_pedido = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name="En pedido")
    no_imprimir = models.BooleanField(default=False, verbose_name="No imprimir")
    precio = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="Precio aplicado")
    categoria_costo = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = "Inventario Diario de Producto"
        verbose_name_plural = "Inventario Diario de Productos"
        unique_together = ('reporte', 'producto')


class TicketProducto(models.Model):
    """Ticket de entrega o devolución de productos. Usa los mismos tipos de ticket que las mallas."""

    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='tickets_producto')
    tipo = models.ForeignKey(TipoTicketMalla, on_delete=models.RESTRICT, related_name='tickets_producto')
    numero = models.CharField(max_length=40, blank=True)
    pedido_por = models.CharField(max_length=100, blank=True)
    recibido_por = models.CharField(max_length=100, blank=True)
    almacen_codigo = models.CharField(max_length=15, blank=True)
    almacen_nombre = models.CharField(max_length=100, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ticket de Productos"
        verbose_name_plural = "Tickets de Productos"
        ordering = ['id']


class TicketProductoDetalle(models.Model):
    ticket = models.ForeignKey(TicketProducto, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='+')
    cantidad_ticket = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name="Según ticket")
    cantidad_real = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name="Real")

    class Meta:
        verbose_name = "Detalle de Ticket de Productos"
        verbose_name_plural = "Detalles de Tickets de Productos"
        unique_together = ('ticket', 'producto')
