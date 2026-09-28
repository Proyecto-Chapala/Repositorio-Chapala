"""
Reporte final del pozo (recap): textos que escribe el ingeniero al cierre del pozo.
Los números del reporte NO se guardan: salen de los reportes diarios (recap_pozo.py).
"""

from django.db import models

from .models import Pozo


class RecapPozo(models.Model):
    pozo = models.OneToOneField(Pozo, on_delete=models.CASCADE, related_name='recap')
    resumen = models.TextField(blank=True, verbose_name="Resumen del pozo")
    conclusiones = models.TextField(blank=True, verbose_name="Conclusiones")
    recomendaciones = models.TextField(blank=True, verbose_name="Recomendaciones")
    lecciones = models.TextField(blank=True, verbose_name="Lecciones aprendidas / buenas prácticas")
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reporte Final del Pozo"
        verbose_name_plural = "Reportes Finales de Pozo"

    def __str__(self):
        return f"Reporte final — {self.pozo.nombre}"
