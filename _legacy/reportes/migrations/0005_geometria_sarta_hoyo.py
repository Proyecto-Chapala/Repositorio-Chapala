"""
Migración escrita a mano (mismo criterio que 0002-0004: modelo nuevo simple
+ campos agregados, sin dependencias complejas).

Implementa el Paso 5 del "manual resumido, esquema.pdf" (Daily -> Geometry):

  - `TuberiaInstalada.profundidad_tvd`: columna "TVD" que le faltaba a la
    tabla Wellbore Geometry (Type/Casing OD/Casing ID/Depth/TVD) — el resto
    de esas columnas ya existían (tipo, diametro_externo, diametro_interno,
    longitud=Depth).
  - `ReporteDiario.bit_depth` / `bit_size` / `porcentaje_washout`: inputs
    para calcular Hole Size (Bit Size ajustado por %Washout) — viven en el
    reporte diario, no en el intervalo, porque cambian día a día.
  - Modelo nuevo `TramoSarta` (Drill String Geometry): tubular por tubular
    de la sarta de perforación del día, con la fórmula de longitud
    automática del "Drill Pipe" principal.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reportes", "0004_pits_loss_setup"),
    ]

    operations = [
        migrations.AddField(
            model_name="tuberiainstalada",
            name="profundidad_tvd",
            field=models.DecimalField(
                max_digits=10, decimal_places=2, null=True, blank=True,
                help_text="TVD (profundidad vertical verdadera) de la zapata, en pies. Opcional en pozos verticales.",
            ),
        ),
        migrations.AddField(
            model_name="reportediario",
            name="bit_depth",
            field=models.DecimalField(
                max_digits=10, decimal_places=2, null=True, blank=True,
                help_text="Bit Depth: profundidad actual de la mecha, en ft.",
            ),
        ),
        migrations.AddField(
            model_name="reportediario",
            name="bit_size",
            field=models.DecimalField(
                max_digits=6, decimal_places=3, null=True, blank=True,
                help_text="Bit Size: diámetro nominal de la mecha, en pulgadas.",
            ),
        ),
        migrations.AddField(
            model_name="reportediario",
            name="porcentaje_washout",
            field=models.DecimalField(
                max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                help_text="% Washout (ensanchamiento del hoyo). 0 = hoyo en calibre (gauge hole).",
            ),
        ),
        migrations.CreateModel(
            name="TramoSarta",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "tipo",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("drill_pipe", "Drill Pipe"),
                            ("heavy_weight", "Heavy Weight"),
                            ("drill_collar", "Drill Collar"),
                            ("sub", "Sub"),
                        ],
                        default="drill_pipe",
                    ),
                ),
                (
                    "es_principal",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "Tramo con longitud autocalculada (Bit Depth − resto de la sarta). "
                            "Como máximo uno por reporte."
                        ),
                    ),
                ),
                (
                    "longitud",
                    models.DecimalField(
                        max_digits=10, decimal_places=2, null=True, blank=True,
                        help_text=(
                            "Longitud (ft). Si es_principal=True se recalcula siempre al guardar; "
                            "el valor enviado se ignora."
                        ),
                    ),
                ),
                ("diametro_externo", models.DecimalField(decimal_places=3, max_digits=6, help_text="Pipe OD, en pulgadas.")),
                ("diametro_interno", models.DecimalField(decimal_places=3, max_digits=6, help_text="Pipe ID, en pulgadas.")),
                (
                    "tool_joint_od",
                    models.DecimalField(
                        max_digits=6, decimal_places=3, null=True, blank=True, help_text="Tool Jt OD, en pulgadas.",
                    ),
                ),
                (
                    "tool_joint_id",
                    models.DecimalField(
                        max_digits=6, decimal_places=3, null=True, blank=True, help_text="Tool Jt ID, en pulgadas.",
                    ),
                ),
                (
                    "longitud_tool_joint",
                    models.DecimalField(
                        max_digits=6, decimal_places=2, null=True, blank=True, help_text="TJ Length, en pulgadas.",
                    ),
                ),
                (
                    "orden",
                    models.PositiveIntegerField(default=0, help_text="Orden de la tabla, de arriba (superficie) hacia abajo."),
                ),
                (
                    "reporte",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tramos_sarta",
                        to="reportes.reportediario",
                    ),
                ),
            ],
            options={
                "ordering": ["reporte", "orden"],
                "verbose_name": "Tramo de sarta",
                "verbose_name_plural": "Tramos de sarta (Drill String Geometry)",
            },
        ),
    ]
