"""
Migración escrita a mano (mismo criterio que 0002-0007).

Implementa el Paso 7 del "manual resumido, esquema.pdf" (Interval Closeout):

  - `Intervalo.volumen_inicial` (Start Volume, 7.2 Rollover): se puebla
    automáticamente con el Final Volume del cierre del intervalo anterior.
  - `CierreVolumetrico` se conecta de verdad al catálogo de pérdidas (7.1.3):
    se elimina el monto libre `perdida_left_in_hole` y se agregan
    `fosa_origen`, `categoria_perdida` y `transaccion_left_in_hole`, que
    apuntan a la TransaccionFosa (tipo Loss, categoría "Left in Hole") real
    que ejecuta el descargo del volumen atrapado.

NOTA: `perdida_left_in_hole` pasa a ser una propiedad Python (no columna) en
el modelo, así que se elimina la columna de la base de datos. Como el
proyecto está en desarrollo (sin datos de cierre reales todavía, según lo
conversado), no se necesita una migración de datos para preservar valores
existentes.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reportes", "0007_distribucion_tiempo"),
    ]

    operations = [
        migrations.AddField(
            model_name="intervalo",
            name="volumen_inicial",
            field=models.DecimalField(
                max_digits=10, decimal_places=2, null=True, blank=True,
                help_text=(
                    "Start Volume (bbl). Se puebla automáticamente al crear el intervalo con el "
                    "Final Volume del cierre del intervalo anterior del mismo pozo (Rollover, manual "
                    "7.2). Para el primer intervalo del pozo se ingresa a mano."
                ),
            ),
        ),
        migrations.RemoveField(
            model_name="cierrevolumetrico",
            name="perdida_left_in_hole",
        ),
        migrations.AddField(
            model_name="cierrevolumetrico",
            name="fosa_origen",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, null=True, blank=True,
                related_name="cierres_left_in_hole", to="reportes.pit",
                help_text="Fosa de la que se descuenta el volumen atrapado. Obligatoria si volumen_no_fluido > 0.",
            ),
        ),
        migrations.AddField(
            model_name="cierrevolumetrico",
            name="categoria_perdida",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, null=True, blank=True,
                to="reportes.categoriaperdida",
                help_text='Categoría de pérdida usada para el descargo (debe ser "Left in Hole").',
            ),
        ),
        migrations.AddField(
            model_name="cierrevolumetrico",
            name="transaccion_left_in_hole",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT, null=True, blank=True,
                related_name="cierre_origen", to="reportes.transaccionfosa",
                help_text="La TransaccionFosa (tipo Loss) que realmente ejecutó el descargo, para trazabilidad.",
            ),
        ),
    ]
