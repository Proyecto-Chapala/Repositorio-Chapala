"""
Migración escrita a mano (igual que mychapala/migrations/0004): agrega los
modelos Equipo, UsoEquipo y Comentario (sección 3, puntos 7 y 8 del contexto
del proyecto — Equipos y Comentarios), que quedaron pendientes en la
migración inicial de la app 'reportes'.

Se escribe a mano porque son 3 modelos nuevos y simples (a diferencia de la
migración 0001_initial, que tenía 13 modelos interdependientes y sí requería
que Django la autogenerara). Los campos coinciden exactamente con los
definidos en models.py.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reportes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Equipo",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=150)),
                ("codigo", models.CharField(max_length=50, unique=True)),
                (
                    "costo_diario",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        help_text="Tarifa diaria vigente. Puede cambiar entre reportes, igual que el precio de un producto.",
                    ),
                ),
            ],
            options={
                "ordering": ["nombre"],
            },
        ),
        migrations.CreateModel(
            name="Comentario",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("texto", models.TextField()),
                ("autor", models.CharField(blank=True, max_length=120)),
                ("fecha_hora", models.DateTimeField(auto_now_add=True)),
                (
                    "reporte",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comentarios",
                        to="reportes.reportediario",
                    ),
                ),
            ],
            options={
                "ordering": ["reporte", "fecha_hora"],
            },
        ),
        migrations.CreateModel(
            name="UsoEquipo",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("horas_usadas", models.DecimalField(decimal_places=2, max_digits=5)),
                (
                    "equipo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="usos",
                        to="reportes.equipo",
                    ),
                ),
                (
                    "reporte",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="usos_equipo",
                        to="reportes.reportediario",
                    ),
                ),
            ],
            options={
                "ordering": ["reporte", "id"],
            },
        ),
    ]
