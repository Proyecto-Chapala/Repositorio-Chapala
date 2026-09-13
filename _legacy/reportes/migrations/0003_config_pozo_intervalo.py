"""
Migración escrita a mano (mismo criterio que 0002_equipo_comentario: campos
simples y sin dependencias complejas, no requiere que Django la autogenere).

Implementa el Paso 1 (Project -> General) y el Paso 2 (Project -> Intervals)
del "manual resumido, esquema.pdf":

  - Pozo: identificación (Log-It Number, Rig Name, Contractor), parámetros
    térmicos (Surface Temp, Temp Gradient), configuración marina (Air Gap,
    Water Depth, Sea Floor Temp) y las 3 variables que se congelan
    permanentemente al primer reporte diario (Unit Set, Is Offshore?,
    Uses Riser).
  - Intervalo: Operational Mode (Drilling/Completion), Type (Casing/Liner/
    Open Hole), y el par es_sidetrack + profundidad_tope_liner_sidetrack
    (Top Of Liner / Sidetrack) que dispara "Reset Start Depth for Sidetrack".

Los campos nuevos de Pozo se agregan con `null=True` (además de blank=True
donde aplica) para no romper los pozos ya cargados: `numero_logit` es único
y no puede tener un valor por defecto no nulo; el resto son opcionales por
diseño. `unit_set` sí lleva un default no nulo (oilfield) porque todo el
sistema ya trabaja en unidades inglesas (ver "Cosas a tener en cuenta.md").
`Intervalo.tipo` y `modo_operativo` llevan default para los intervalos ya
existentes (open_hole / drilling, los valores más neutros).
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reportes", "0002_equipo_comentario"),
    ]

    operations = [
        # --- Pozo (Paso 1) ---
        migrations.AddField(
            model_name="pozo",
            name="numero_logit",
            field=models.CharField(
                max_length=60, unique=True, null=True, blank=True,
                help_text="Log-It Number: identificador único de seguimiento corporativo.",
            ),
        ),
        migrations.AddField(
            model_name="pozo",
            name="nombre_taladro",
            field=models.CharField(max_length=120, blank=True, default="", help_text="Rig Name."),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pozo",
            name="contratista",
            field=models.CharField(max_length=120, blank=True, default="", help_text="Contractor."),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pozo",
            name="surface_temp",
            field=models.DecimalField(
                max_digits=6, decimal_places=2, null=True, blank=True, help_text="Surface Temp, en °F.",
            ),
        ),
        migrations.AddField(
            model_name="pozo",
            name="temp_gradient",
            field=models.DecimalField(
                max_digits=6, decimal_places=2, null=True, blank=True, help_text="Temp Gradient, en °F/100ft.",
            ),
        ),
        migrations.AddField(
            model_name="pozo",
            name="unit_set",
            field=models.CharField(
                max_length=10,
                choices=[("oilfield", "Standard Oilfield (ft, in, bbl, lb/gal)"), ("metric", "Metric")],
                default="oilfield",
                help_text="Se bloquea permanentemente al crear el primer reporte diario.",
            ),
        ),
        migrations.AddField(
            model_name="pozo",
            name="es_offshore",
            field=models.BooleanField(
                default=False, verbose_name="¿Es offshore?",
                help_text="Se bloquea permanentemente al crear el primer reporte diario.",
            ),
        ),
        migrations.AddField(
            model_name="pozo",
            name="usa_riser",
            field=models.BooleanField(
                default=False, verbose_name="Usa riser",
                help_text="Se bloquea permanentemente al crear el primer reporte diario.",
            ),
        ),
        migrations.AddField(
            model_name="pozo",
            name="air_gap",
            field=models.DecimalField(
                max_digits=8, decimal_places=2, null=True, blank=True, help_text="Air Gap, en ft.",
            ),
        ),
        migrations.AddField(
            model_name="pozo",
            name="water_depth",
            field=models.DecimalField(
                max_digits=8, decimal_places=2, null=True, blank=True, help_text="Water Depth, en ft.",
            ),
        ),
        migrations.AddField(
            model_name="pozo",
            name="sea_floor_temp",
            field=models.DecimalField(
                max_digits=6, decimal_places=2, null=True, blank=True, help_text="Sea Floor Temp, en °F.",
            ),
        ),
        # --- Intervalo (Paso 2) ---
        migrations.AddField(
            model_name="intervalo",
            name="modo_operativo",
            field=models.CharField(
                max_length=12,
                choices=[("drilling", "Drilling"), ("completion", "Completion")],
                default="drilling",
                help_text="Operational Mode: Drilling o Completion.",
            ),
        ),
        migrations.AddField(
            model_name="intervalo",
            name="tipo",
            field=models.CharField(
                max_length=10,
                choices=[("casing", "Casing"), ("liner", "Liner"), ("open_hole", "Open Hole")],
                default="open_hole",
                help_text="Type: Casing, Liner u Open Hole.",
            ),
        ),
        migrations.AddField(
            model_name="intervalo",
            name="es_sidetrack",
            field=models.BooleanField(
                default=False,
                help_text="Si este intervalo se abre por un desvío (side track) del hoyo.",
            ),
        ),
        migrations.AddField(
            model_name="intervalo",
            name="profundidad_tope_liner_sidetrack",
            field=models.DecimalField(
                max_digits=10, decimal_places=2, null=True, blank=True,
                help_text="Top Of Liner / Sidetrack (ft). Obligatorio si tipo=Liner o es_sidetrack=True.",
            ),
        ),
    ]
