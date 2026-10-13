"""
Inventario por pozo (revisión con el cliente, octubre 2026): revierte el inventario unificado
de la 0022. La matriz (Producto) vuelve a ser solo catálogo y el reporte diario ya no descuenta
Producto.cantidad, así que los campos `stock_aplicado` dejan de tener uso.

La existencia del pozo la calcula el motor (volumetria.py) a partir de los tickets de recepción.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0027_intervalo_cerrado_moneda_secundaria'),
    ]

    operations = [
        migrations.RemoveField(model_name='transaccionvolumen', name='lodo_stock_aplicado'),
        migrations.RemoveField(model_name='transaccionvolumenproducto', name='stock_aplicado'),
        migrations.RemoveField(model_name='inventarioproductodia', name='stock_aplicado'),
    ]
