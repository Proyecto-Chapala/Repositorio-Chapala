"""
Precio por unidad o por barril (revisión con el cliente, octubre 2026, punto 8).
Los productos existentes quedan "por unidad", que es como se cobraban hasta ahora.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0028_inventario_por_pozo'),
    ]

    operations = [
        migrations.AddField(
            model_name='productoactivopozo',
            name='cobro_por',
            field=models.CharField(
                choices=[('UNIDAD', 'Por unidad'), ('BARRIL', 'Por barril')], default='UNIDAD',
                help_text='Por unidad (lb, saco, tambor...) o por barril de volumen que aporta el producto.',
                max_length=6, verbose_name='Cobrar por'),
        ),
    ]
