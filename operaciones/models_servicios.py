"""
Servicios del pozo (pestaña 8, "Servicios"): ingenieros, trailers, filtración, etc.

Son la parte contable del contrato que se cobra por día con una tarifa: no son productos,
no llevan existencias ni entran en la volumetría ni en las concentraciones. Cada servicio
tiene su categoría de costo (volumetria.CATEGORIAS_SERVICIO), que decide en qué columna del
resumen de costos suma.

Cada día guarda los días cobrados y una COPIA de la tarifa y la categoría: así, si la tarifa
del contrato cambia, los días ya cargados (y el pozo cerrado) conservan su costo.
"""

from collections import defaultdict
from decimal import Decimal

from django.db import models

from . import volumetria as vol
from .models import Pozo
from .models_daily_reports import ReporteDiario

CATEGORIA_CHOICES = list(vol.CATEGORIAS_SERVICIO.items())


class ServicioPozo(models.Model):
    """Servicio contratado en el pozo, con su tarifa diaria en la moneda de cobro del pozo."""

    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='servicios')
    descripcion = models.CharField(max_length=150, verbose_name="Descripción")
    categoria_costo = models.PositiveSmallIntegerField(choices=CATEGORIA_CHOICES, verbose_name="Categoría de costo")
    tarifa_diaria = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="Tarifa diaria")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Servicio del Pozo"
        verbose_name_plural = "Servicios del Pozo"
        ordering = ['categoria_costo', 'id']

    def __str__(self):
        return f"{self.pozo.nombre} — {self.descripcion}"


class ServicioDia(models.Model):
    """Días cobrados de un servicio en un reporte, con la tarifa y la categoría de ese día."""

    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='servicios_dia')
    servicio = models.ForeignKey(ServicioPozo, on_delete=models.PROTECT, related_name='dias')
    dias = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Días cobrados")
    tarifa = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="Tarifa aplicada")
    categoria_costo = models.PositiveSmallIntegerField(choices=CATEGORIA_CHOICES, verbose_name="Categoría de costo")

    class Meta:
        verbose_name = "Servicio del Día"
        verbose_name_plural = "Servicios del Día"
        unique_together = ('reporte', 'servicio')

    @property
    def costo(self):
        return self.dias * self.tarifa


def costos_servicios(pozo, reporte):
    """
    Costo de los servicios hasta el día del reporte: (del día por categoría, acumulado por
    categoría, filas del día (ServicioDia del reporte), acumulado por servicio).
    """
    diario, acumulado, por_servicio = defaultdict(Decimal), defaultdict(Decimal), defaultdict(Decimal)
    filas_dia = []
    for fila in (ServicioDia.objects.filter(reporte__pozo=pozo, reporte__fecha__lte=reporte.fecha)
                 .select_related('servicio')):
        acumulado[fila.categoria_costo] += fila.costo
        por_servicio[fila.servicio_id] += fila.costo
        if fila.reporte_id == reporte.id:
            diario[fila.categoria_costo] += fila.costo
            filas_dia.append(fila)
    return diario, acumulado, filas_dia, por_servicio
