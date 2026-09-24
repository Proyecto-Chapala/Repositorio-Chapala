"""
Pestaña 8 del reporte diario — Inventario, Hidráulica y Concentraciones
(ONE-TRAX: Inv/Hyd/Conc).

Por ahora solo la configuración "Pérdidas del reporte" (Daily Loss Print Selection).
La volumetría, la hidráulica y la concentración de productos se agregan en segmentos
siguientes, cuando se revisen sus páginas del manual.
"""

from django.db import models

from .models import Pozo


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
