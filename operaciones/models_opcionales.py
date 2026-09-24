"""
Módulos OPCIONALES del reporte diario (AOS al parecer no los usa; nada de lo demás depende
de ellos y, si están vacíos, no afectan ningún cálculo):

- Observaciones IFE (pestaña 6).
- Análisis de sólidos por equipo (pestaña 6).
- Retención en recortes (pestaña 6; consulta en la 8).
- Eventos no programados (pestañas 5 y 7).
La evaluación de benchmark (pestaña 8) no guarda nada: compara los objetivos del Benchmark
Setup del pozo con los chequeos de lodo de la pestaña 3.

Los equipos se guardan por número de serie + copia del nombre (la lista de equipos activos
del pozo se guarda recreando filas).
"""

from django.db import models

from .models_daily_reports import ReporteDiario


class ObservacionesIFE(models.Model):
    """Los cuatro textos "IFE Remarks" de la pantalla principal de Solids Equipment."""

    reporte = models.OneToOneField(ReporteDiario, on_delete=models.CASCADE, related_name='observaciones_ife')
    fluidos_resumen = models.TextField(blank=True, verbose_name="Fluidos de perforación — resumen")
    fluidos_plan = models.TextField(blank=True, verbose_name="Fluidos de perforación — plan siguiente")
    solidos_resumen = models.TextField(blank=True, verbose_name="Control de sólidos — resumen")
    solidos_plan = models.TextField(blank=True, verbose_name="Control de sólidos — plan siguiente")

    class Meta:
        verbose_name = "Observaciones IFE"
        verbose_name_plural = "Observaciones IFE"


class _MuestraEquipo(models.Model):
    """Datos comunes de una muestra tomada en un equipo (cada hija define su 'reporte')."""

    equipo_serie = models.CharField(max_length=30, verbose_name="N° de Serie")
    equipo_descripcion = models.CharField(max_length=150, blank=True, verbose_name="Equipo")
    hora_inicio = models.CharField(max_length=5, blank=True, verbose_name="Hora de inicio")
    hora_fin = models.CharField(max_length=5, blank=True, verbose_name="Hora de fin")
    orden = models.PositiveSmallIntegerField(default=1, verbose_name="Orden de impresión")
    profundidad_ft = models.FloatField(null=True, blank=True, verbose_name="Profundidad medida (ft)")
    profundidad_perforada_ft = models.FloatField(null=True, blank=True, verbose_name="Profundidad perforada representada (ft)")
    comentarios = models.CharField(max_length=255, blank=True, verbose_name="Comentarios")

    class Meta:
        abstract = True
        ordering = ['orden', 'id']


class AnalisisSolidosEquipo(_MuestraEquipo):
    """Análisis de sólidos de una muestra tomada en un equipo (Equipment Solids Analysis)."""

    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='analisis_solidos_equipo')
    tipo_lodo = models.CharField(max_length=3, choices=[('WBM', 'Base agua'), ('OBM', 'Base aceite')], default='WBM')
    tipo_muestra = models.CharField(max_length=60, blank=True, verbose_name="Tipo de muestra (ej. descarga)")
    datos = models.JSONField(default=dict, verbose_name="Datos de la muestra")

    class Meta(_MuestraEquipo.Meta):
        verbose_name = "Análisis de Sólidos por Equipo"
        verbose_name_plural = "Análisis de Sólidos por Equipo"


class RetencionRecortes(_MuestraEquipo):
    """Prueba de retención de fluido en recortes (Cuttings Retention)."""

    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='retencion_recortes')
    diametro_mecha_in = models.FloatField(null=True, blank=True, verbose_name="Diámetro de mecha (in)")
    datos = models.JSONField(default=dict, verbose_name="Datos de la prueba")

    class Meta(_MuestraEquipo.Meta):
        verbose_name = "Retención en Recortes"
        verbose_name_plural = "Retención en Recortes"


class EventoNoProgramado(models.Model):
    """Evento no programado del pozo (Unscheduled Events), registrado en un reporte."""

    CATEGORIA_CHOICES = [
        ('FLUIDOS', 'Fluidos y perforación'),
        ('CALIDAD', 'Calidad de producto'),
        ('LOGISTICA', 'Logística'),
        ('EQUIPO', 'Falla de equipo'),
    ]

    reporte = models.ForeignKey(ReporteDiario, on_delete=models.CASCADE, related_name='eventos_no_programados')
    categoria = models.CharField(max_length=10, choices=CATEGORIA_CHOICES, default='FLUIDOS')
    tipo_problema = models.CharField(max_length=100, verbose_name="Tipo de problema")
    tipo_fluido = models.CharField(max_length=100, blank=True, verbose_name="Tipo de fluido")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    causa = models.TextField(blank=True, verbose_name="Causa sospechada")
    descripcion_perdida = models.TextField(blank=True, verbose_name="Descripción de la pérdida")
    horas_perdidas = models.FloatField(null=True, blank=True, verbose_name="Tiempo perdido (h)")
    volumen_perdido_bbl = models.FloatField(null=True, blank=True, verbose_name="Volumen perdido (bbl)")
    costo = models.FloatField(null=True, blank=True, verbose_name="Costo estimado")

    class Meta:
        verbose_name = "Evento No Programado"
        verbose_name_plural = "Eventos No Programados"
        ordering = ['id']
