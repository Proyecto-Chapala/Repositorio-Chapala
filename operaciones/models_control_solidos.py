"""
Pestaña 6 del reporte diario — Control de Sólidos (ONE-TRAX: Solids Equipment).

Fase 1: inventario de mallas de zaranda, tickets de entrega/devolución y transacciones
de mallas en los equipos (instalar, pasar al almacén, desechar).

Decisiones de diseño:
- El inventario diario NO se guarda: se DERIVA repitiendo, en orden, los tickets y las
  transacciones del pozo (el final de ayer es el inicial de hoy). Así nunca hay que
  "recalcular" y un error de un día no se arrastra en silencio. Ver control_solidos.py.
- Las mallas se referencian por el catálogo maestro (MallaZaranda) y los equipos por el
  catálogo maestro (Equipo) + su número de serie en el pozo, NO por las listas activas
  del pozo (MallaActivaPozo / EquipoActivoPozo): esas listas se guardan borrando y
  recreando sus filas, así que una llave foránea a ellas se perdería en cada edición.
- El precio de la malla se copia en la transacción al instalarla nueva: el costo de un día
  pasado no cambia si después se actualiza el precio del pozo.
"""

from django.db import models

from .models import Pozo, Equipo, MallaZaranda
from .models_daily_reports import ReporteDiario


class TipoTicketMalla(models.Model):
    """
    Tipos de ticket de mallas del pozo (catálogo editable).

    El usuario todavía no sabe qué tipos maneja AOS, así que se siembran ejemplos y se
    pueden renombrar, agregar o quitar desde la pantalla de tickets. Lo único que importa
    para el cálculo es el sentido: si el ticket ENTRA mallas al pozo o las SACA.
    """

    SENTIDO_CHOICES = [
        ('ENTRADA', 'Entrada al pozo'),
        ('SALIDA', 'Salida del pozo'),
    ]

    TIPOS_EJEMPLO = [
        ('Recepción desde almacén', 'ENTRADA'),
        ('Devolución a almacén', 'SALIDA'),
        ('Recepción desde otro pozo', 'ENTRADA'),
        ('Envío a otro pozo', 'SALIDA'),
    ]

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='tipos_ticket_malla')
    nombre = models.CharField(max_length=80, verbose_name="Tipo de Ticket")
    sentido = models.CharField(max_length=8, choices=SENTIDO_CHOICES, default='ENTRADA', verbose_name="Sentido")

    class Meta:
        verbose_name = "Tipo de Ticket de Mallas"
        verbose_name_plural = "Tipos de Ticket de Mallas"
        unique_together = ('pozo', 'nombre')
        ordering = ['sentido', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_sentido_display()})"

    @classmethod
    def sembrar_ejemplos(cls, pozo):
        for nombre, sentido in cls.TIPOS_EJEMPLO:
            cls.objects.get_or_create(pozo=pozo, nombre=nombre, defaults={'sentido': sentido})

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'sentido': self.sentido,
            'sentido_display': self.get_sentido_display(),
        }


class TicketMalla(models.Model):
    """Ticket de entrega o devolución de mallas (ONE-TRAX: Transfer Ticket Transactions)."""

    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='tickets_malla')
    tipo = models.ForeignKey(TipoTicketMalla, on_delete=models.RESTRICT, related_name='tickets', verbose_name="Tipo")
    numero = models.CharField(max_length=40, blank=True, verbose_name="N° de Ticket")
    pedido_por = models.CharField(max_length=100, blank=True, verbose_name="Pedido por")
    recibido_por = models.CharField(max_length=100, blank=True, verbose_name="Recibido por")
    # Copia del almacén (el catálogo de almacenes del pozo también se guarda recreando filas).
    almacen_codigo = models.CharField(max_length=15, blank=True, verbose_name="Código de Almacén")
    almacen_nombre = models.CharField(max_length=100, blank=True, verbose_name="Almacén")

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ticket de Mallas"
        verbose_name_plural = "Tickets de Mallas"
        ordering = ['id']

    def __str__(self):
        return f"Ticket {self.numero or self.id} - {self.tipo.nombre}"

    def to_dict(self):
        detalles = [d.to_dict() for d in self.detalles.select_related('malla').all()]
        return {
            'id': self.id,
            'tipo_id': self.tipo_id,
            'tipo_nombre': self.tipo.nombre,
            'sentido': self.tipo.sentido,
            'numero': self.numero,
            'pedido_por': self.pedido_por,
            'recibido_por': self.recibido_por,
            'almacen_codigo': self.almacen_codigo,
            'almacen_nombre': self.almacen_nombre,
            'detalles': detalles,
            'total_nuevas': sum(d['nuevas_real'] for d in detalles),
            'total_usadas': sum(d['usadas_real'] for d in detalles),
            'tiene_diferencias': any(d['tiene_diferencia'] for d in detalles),
        }


class TicketMallaDetalle(models.Model):
    """
    Cantidades de una malla en un ticket. Se guarda lo que dice el papel ("según ticket")
    y lo que llegó o salió de verdad ("real"); el inventario usa siempre lo real.
    """

    ticket = models.ForeignKey(TicketMalla, on_delete=models.CASCADE, related_name='detalles')
    malla = models.ForeignKey(MallaZaranda, on_delete=models.PROTECT, related_name='detalles_ticket')
    nuevas_ticket = models.PositiveIntegerField(default=0, verbose_name="Nuevas según ticket")
    nuevas_real = models.PositiveIntegerField(default=0, verbose_name="Nuevas reales")
    usadas_ticket = models.PositiveIntegerField(default=0, verbose_name="Usadas según ticket")
    usadas_real = models.PositiveIntegerField(default=0, verbose_name="Usadas reales")

    class Meta:
        verbose_name = "Detalle de Ticket de Mallas"
        verbose_name_plural = "Detalles de Tickets de Mallas"
        unique_together = ('ticket', 'malla')
        ordering = ['malla__mesh_size', 'malla__codigo']

    def to_dict(self):
        return {
            'malla_id': self.malla_id,
            'malla_codigo': self.malla.codigo,
            'malla_descripcion': self.malla.descripcion,
            'mesh_size': self.malla.mesh_size,
            'nuevas_ticket': self.nuevas_ticket,
            'nuevas_real': self.nuevas_real,
            'usadas_ticket': self.usadas_ticket,
            'usadas_real': self.usadas_real,
            'tiene_diferencia': (self.nuevas_ticket != self.nuevas_real
                                 or self.usadas_ticket != self.usadas_real),
        }


class TransaccionMalla(models.Model):
    """
    Movimiento de una malla en los equipos (ONE-TRAX: Shaker Screen Transactions).

    'secuencia' crece con cada transacción del pozo: la última registrada es la única que
    se puede deshacer (igual que 'Undo Last Transaction' de ONE-TRAX).
    """

    INSTALAR_NUEVA = 'INSTALAR_NUEVA'
    INSTALAR_USADA = 'INSTALAR_USADA'
    A_ALMACEN = 'A_ALMACEN'
    DESECHAR_EQUIPO = 'DESECHAR_EQUIPO'
    DESECHAR_ALMACEN = 'DESECHAR_ALMACEN'

    ACCION_CHOICES = [
        (INSTALAR_NUEVA, 'Instalar malla nueva'),
        (INSTALAR_USADA, 'Instalar malla usada'),
        (A_ALMACEN, 'Pasar al almacén'),
        (DESECHAR_EQUIPO, 'Desechar del equipo'),
        (DESECHAR_ALMACEN, 'Desechar del almacén'),
    ]

    ACCIONES_CON_POSICION = (INSTALAR_NUEVA, INSTALAR_USADA, A_ALMACEN, DESECHAR_EQUIPO)

    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='transacciones_malla')
    secuencia = models.PositiveIntegerField(verbose_name="N° de Transacción")
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES, verbose_name="Acción")
    malla = models.ForeignKey(MallaZaranda, on_delete=models.PROTECT, related_name='transacciones')

    equipo = models.ForeignKey(
        Equipo, on_delete=models.PROTECT, null=True, blank=True, related_name='transacciones_malla'
    )
    equipo_serie = models.CharField(max_length=30, blank=True, verbose_name="N° de Serie del Equipo")
    equipo_descripcion = models.CharField(max_length=150, blank=True, verbose_name="Equipo")
    posicion = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Posición")

    precio_unitario = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Precio Unitario (neto)",
        help_text="Solo en 'Instalar malla nueva': precio neto de la malla en ese momento."
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transacción de Malla"
        verbose_name_plural = "Transacciones de Mallas"
        ordering = ['secuencia']

    def __str__(self):
        return f"#{self.secuencia} {self.get_accion_display()} - {self.malla.codigo}"

    def to_dict(self):
        return {
            'id': self.id,
            'secuencia': self.secuencia,
            'accion': self.accion,
            'accion_display': self.get_accion_display(),
            'malla_id': self.malla_id,
            'malla_codigo': self.malla.codigo,
            'malla_descripcion': self.malla.descripcion,
            'mesh_size': self.malla.mesh_size,
            'equipo_serie': self.equipo_serie,
            'equipo_descripcion': self.equipo_descripcion,
            'posicion': self.posicion,
            'precio_unitario': float(self.precio_unitario),
        }


# =====================================================================
# Fase 2 — Detalle y uso de equipos (ONE-TRAX: Equipment Details and Usage)
# =====================================================================

class UsoEquipoDia(models.Model):
    """
    Lo que hizo un equipo del pozo en el día: rendimiento, costo de renta y paradas.

    Solo se guardan los datos que captura el ingeniero; los volúmenes descargados, el lodo
    perdido en los sólidos y todos los acumulados se CALCULAN (control_solidos.py), porque
    dependen de la profundidad y del diámetro del hoyo, que pueden corregirse después en
    las pestañas 1 y 2.

    El equipo se identifica por el catálogo maestro + su número de serie (la lista de equipos
    activos del pozo se guarda recreando filas). El tipo de pérdida se guarda por código del
    catálogo de pérdidas del pozo, con copia de la descripción, por la misma razón.
    """

    COBRO_COMPLETO = 'COMPLETO'
    COBRO_STANDBY = 'STANDBY'
    COBRO_SIN = 'SIN_COBRO'
    COBRO_CHOICES = [
        (COBRO_COMPLETO, 'Cobro completo'),
        (COBRO_STANDBY, 'Stand-by'),
        (COBRO_SIN, 'Sin cobro'),
    ]

    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='usos_equipo')
    equipo = models.ForeignKey(Equipo, on_delete=models.PROTECT, related_name='usos_diarios')
    equipo_serie = models.CharField(max_length=30, verbose_name="N° de Serie")
    equipo_descripcion = models.CharField(max_length=150, blank=True, verbose_name="Equipo")
    tipo_equipo = models.CharField(max_length=25, blank=True, verbose_name="Tipo de Equipo")

    # --- Rendimiento (datos clave del día) ---
    horas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Horas en operación")
    mud_on_cuttings = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True, verbose_name="Lodo en recortes (bbl/bbl)",
        help_text="Volumen de lodo que sale pegado a cada volumen de recortes descargados."
    )
    porcentaje_recortes = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="% de recortes",
        help_text="Qué parte del hoyo perforado en el día descarga este equipo (100 % = todo)."
    )
    tipo_perdida_codigo = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Tipo de pérdida (código)")
    tipo_perdida_descripcion = models.CharField(max_length=100, blank=True, verbose_name="Tipo de pérdida")
    # Solo centrífugas
    caudal_entrada_gpm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Caudal de entrada (gpm)")
    densidad_entrada = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, verbose_name="Densidad de entrada (lb/gal)")
    densidad_salida = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, verbose_name="Densidad de salida (lb/gal)")
    densidad_descarte = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, verbose_name="Densidad de descarte (lb/gal)")

    # --- Costos ---
    cantidad_usada = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Cantidad usada")
    codigo_cobro = models.CharField(max_length=10, choices=COBRO_CHOICES, default=COBRO_COMPLETO, verbose_name="Código de cobro")
    tarifa = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Tarifa aplicada",
        help_text="Copia de la tarifa del pozo (renta o stand-by) el día que se registró."
    )
    es_fluidos = models.BooleanField(default=False, verbose_name="¿Equipo de fluidos de perforación?")

    # --- Uso y paradas ---
    horas_parada = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Horas de parada")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones de uso")

    class Meta:
        verbose_name = "Uso Diario de Equipo"
        verbose_name_plural = "Usos Diarios de Equipos"
        unique_together = ('reporte', 'equipo_serie')
        ordering = ['tipo_equipo', 'equipo_serie']

    def __str__(self):
        return f"{self.reporte} - {self.equipo_serie}"

    @property
    def costo_diario(self):
        if self.codigo_cobro == self.COBRO_SIN:
            return 0.0
        return round(float(self.cantidad_usada or 0) * float(self.tarifa or 0), 2)


class UsoEquipoPropiedad(models.Model):
    """
    Valor del día de una propiedad adicional del equipo (las definidas en Equipment
    Properties Setup: ángulo de la canasta, fuerza G, velocidad del tazón, etc.).
    Se guarda por descripción: esa configuración también se guarda recreando filas.
    """

    uso = models.ForeignKey(UsoEquipoDia, on_delete=models.CASCADE, related_name='propiedades')
    orden = models.PositiveSmallIntegerField(default=0)
    descripcion = models.CharField(max_length=100, verbose_name="Propiedad")
    unidad = models.CharField(max_length=30, blank=True, verbose_name="Unidad")
    valor = models.CharField(max_length=60, blank=True, verbose_name="Valor")

    class Meta:
        verbose_name = "Propiedad Diaria de Equipo"
        verbose_name_plural = "Propiedades Diarias de Equipos"
        ordering = ['orden', 'id']

    def __str__(self):
        return f"{self.uso} - {self.descripcion}: {self.valor}"
