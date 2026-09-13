"""
Migración escrita a mano (mismo criterio que 0002-0006).

Implementa el Paso 4 del "manual resumido, esquema.pdf" (Daily -> General):

  - Modelo nuevo `DistribucionTiempo` (Time Distribution, 4.1): desglose de
    las 24 horas del día en actividades del taladro.

Date/Report# (correlativos automáticos) y Default Interval/Default Fluid
System ya existen en el esquema actual (ReporteDiario.fecha/numero_reporte
e Intervalo.numero/sistema_fluido, respectivamente — cada reporte cuelga de
un único intervalo fijo) y no requieren campos ni migración nueva; se
exponen en `ReporteDiario.to_dict()` como información de cabecera.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reportes", "0006_volume_accounting"),
    ]

    operations = [
        migrations.CreateModel(
            name="DistribucionTiempo",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "actividad",
                    models.CharField(
                        max_length=100,
                        help_text='Ej. "Rotary Drilling", "Circulating", "Tripping In".',
                    ),
                ),
                (
                    "horas",
                    models.DecimalField(
                        max_digits=4, decimal_places=2,
                        help_text="Horas dedicadas a esta actividad (mayor a 0, hasta 24).",
                    ),
                ),
                ("notas", models.TextField(blank=True)),
                (
                    "orden",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "reporte",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="distribucion_tiempo", to="reportes.reportediario",
                    ),
                ),
            ],
            options={
                "ordering": ["reporte", "orden"],
                "verbose_name": "Distribución de tiempo",
                "verbose_name_plural": "Distribución de tiempo (Time Distribution)",
            },
        ),
    ]
