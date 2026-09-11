"""
Migración escrita a mano (mismo criterio que 0002-0005).

Implementa el Paso 6 del "manual resumido, esquema.pdf" (Daily -> Volume
Accounting):

  - `ReporteDiario.volumen_debajo_mecha` / `volumen_no_fluido`: entradas de
    Total Hole Volume / Volume Not Fluids (6.1).
  - Modelo nuevo `TransaccionFosa` (Add Chemicals / Loss / Transfer, 6.2),
    con snapshot inmutable de `intervalo` (6.3).
  - Modelo nuevo `LecturaFosa` (Volumen Medido en Fosas, para la
    reconciliación "Not Accounted = 0" de 6.4).
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reportes", "0005_geometria_sarta_hoyo"),
    ]

    operations = [
        migrations.AddField(
            model_name="reportediario",
            name="volumen_debajo_mecha",
            field=models.DecimalField(
                max_digits=10, decimal_places=2, default=0,
                help_text=(
                    "Vol. Debajo de la Mecha (bbl): hoyo abierto por debajo de la broca, "
                    "no cubierto por la sarta."
                ),
            ),
        ),
        migrations.AddField(
            model_name="reportediario",
            name="volumen_no_fluido",
            field=models.DecimalField(
                max_digits=10, decimal_places=2, default=0,
                help_text=(
                    "Volume Not Fluids (bbl): volumen dentro del hoyo que no pertenece al "
                    "fluido circulante activo (ej. agua salada de perforación inicial, lodo "
                    "previo en proceso de desplazamiento). Se resta del Total Hole Volume "
                    "para obtener el Fluid Volume."
                ),
            ),
        ),
        migrations.CreateModel(
            name="TransaccionFosa",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "tipo",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("add_chemicals", "Add Chemicals"),
                            ("loss", "Loss"),
                            ("transfer", "Transfer"),
                        ],
                    ),
                ),
                (
                    "cantidad_usada",
                    models.DecimalField(
                        max_digits=10, decimal_places=2, null=True, blank=True,
                        help_text="Cantidad de empaques usados (sacos/tambores/etc.). Solo para Add Chemicals.",
                    ),
                ),
                (
                    "es_dilucion",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "Is Dilution: el producto agregado es agua/base líquida usada para "
                            "diluir la fosa destino."
                        ),
                    ),
                ),
                (
                    "volumen",
                    models.DecimalField(
                        max_digits=12, decimal_places=4,
                        help_text=(
                            "Volumen desplazado, en bbl. Para Add Chemicals se recalcula siempre "
                            "al guardar (el valor enviado se ignora); para Loss y Transfer es un "
                            "dato medido/manual."
                        ),
                    ),
                ),
                ("notas", models.TextField(blank=True)),
                ("hora_registro", models.DateTimeField(auto_now_add=True)),
                (
                    "categoria_perdida",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, null=True, blank=True,
                        to="reportes.categoriaperdida",
                        help_text="Obligatoria para Loss; debe pertenecer al mismo pozo y modo operativo del intervalo.",
                    ),
                ),
                (
                    "fosa_destino",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, null=True, blank=True,
                        related_name="transacciones_entrada", to="reportes.pit",
                        help_text="Fosa a la que entra el volumen (Add Chemicals, Transfer).",
                    ),
                ),
                (
                    "fosa_origen",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, null=True, blank=True,
                        related_name="transacciones_salida", to="reportes.pit",
                        help_text="Fosa de la que sale el volumen (Loss, Transfer).",
                    ),
                ),
                (
                    "intervalo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, editable=False,
                        related_name="transacciones_fosa", to="reportes.intervalo",
                        help_text="Snapshot inmutable de reporte.intervalo al momento de crear la transacción (manual 6.3).",
                    ),
                ),
                (
                    "producto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, null=True, blank=True,
                        to="reportes.producto", help_text="Solo para Add Chemicals.",
                    ),
                ),
                (
                    "reporte",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transacciones_fosa", to="reportes.reportediario",
                    ),
                ),
            ],
            options={
                "ordering": ["reporte", "hora_registro"],
                "verbose_name": "Transacción de fosa",
                "verbose_name_plural": "Transacciones de fosa (Volume Accounting)",
            },
        ),
        migrations.CreateModel(
            name="LecturaFosa",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "volumen_medido",
                    models.DecimalField(max_digits=12, decimal_places=4, help_text="Lectura física de la fosa, en bbl."),
                ),
                (
                    "fosa",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="lecturas", to="reportes.pit",
                    ),
                ),
                (
                    "reporte",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lecturas_fosa", to="reportes.reportediario",
                    ),
                ),
            ],
            options={
                "ordering": ["reporte", "fosa"],
                "verbose_name": "Lectura de fosa",
                "verbose_name_plural": "Lecturas de fosa (Volumen Medido)",
            },
        ),
        migrations.AddConstraint(
            model_name="lecturafosa",
            constraint=models.UniqueConstraint(fields=["reporte", "fosa"], name="unica_lectura_por_reporte_y_fosa"),
        ),
    ]
