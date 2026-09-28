from django.db import migrations


class Migration(migrations.Migration):
    """Une las dos ramas: inventario unificado (0022) y side track + reporte final (0022-0023)."""

    dependencies = [
        ('operaciones', '0022_inventario_unificado'),
        ('operaciones', '0023_recap_pozo'),
    ]

    operations = []
