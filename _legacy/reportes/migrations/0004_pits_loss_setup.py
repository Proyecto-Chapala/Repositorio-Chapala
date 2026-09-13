"""
Migración escrita a mano (mismo criterio que 0002 y 0003: modelos nuevos
simples, sin dependencias complejas entre sí — no requiere que Django la
autogenere).

Implementa el Paso 3 del "manual resumido, esquema.pdf" (Project -> Pits
Setup & Loss Setup): los catálogos maestros `Pit` (fosas/tanques) y
`CategoriaPerdida` (Loss Setup), ambos por Pozo. Ver los docstrings de
ambos modelos en models.py para el detalle de las reglas de negocio.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reportes", "0003_config_pozo_intervalo"),
    ]

    operations = [
        migrations.CreateModel(
            name="Pit",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "descripcion",
                    models.CharField(
                        max_length=80,
                        help_text='Nombre único de la fosa, ej. "Active 1", "Reserve 1", "Premix 1".',
                    ),
                ),
                (
                    "capacidad",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, help_text="Capacidad volumétrica máxima, en bbl.",
                    ),
                ),
                (
                    "tipo",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("active", "Active"),
                            ("reserve", "Reserve"),
                            ("premix", "Premix"),
                            ("spacer", "Spacer"),
                            ("storage", "Storage"),
                            ("dead_volume", "Dead Volume"),
                        ],
                        default="active",
                    ),
                ),
                (
                    "es_transaccional",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "Si es False, es una fosa/tanque no transaccional (almacenamiento aislado, "
                            "ej. Base Oil Storage): no participa del balance diario de lodo activo."
                        ),
                    ),
                ),
                (
                    "pozo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="pits",
                        to="reportes.pozo",
                    ),
                ),
            ],
            options={
                "ordering": ["pozo", "descripcion"],
                "verbose_name": "Fosa / Tanque",
                "verbose_name_plural": "Fosas / Tanques",
            },
        ),
        migrations.AddConstraint(
            model_name="pit",
            constraint=models.UniqueConstraint(fields=["pozo", "descripcion"], name="unica_descripcion_fosa_por_pozo"),
        ),
        migrations.CreateModel(
            name="CategoriaPerdida",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "modo_operativo",
                    models.CharField(
                        max_length=12,
                        choices=[("drilling", "Drilling"), ("completion", "Completion")],
                    ),
                ),
                ("nombre", models.CharField(max_length=80, help_text='Ej. "Shakers", "Evaporation", "Left in Hole".')),
                (
                    "dominio",
                    models.CharField(
                        max_length=20,
                        choices=[("superficial", "Superficial"), ("subsuperficial", "Subsuperficial")],
                    ),
                ),
                ("descripcion", models.TextField(blank=True)),
                (
                    "pozo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="categorias_perdida",
                        to="reportes.pozo",
                    ),
                ),
            ],
            options={
                "ordering": ["pozo", "modo_operativo", "dominio", "nombre"],
                "verbose_name": "Categoría de pérdida",
                "verbose_name_plural": "Categorías de pérdida (Loss Setup)",
            },
        ),
        migrations.AddConstraint(
            model_name="categoriaperdida",
            constraint=models.UniqueConstraint(
                fields=["pozo", "modo_operativo", "nombre"], name="unica_categoria_perdida_por_pozo_y_modo"
            ),
        ),
    ]
