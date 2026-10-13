"""
Tarifas en dos monedas (revisión con el cliente, octubre 2026, punto 9). Reemplaza el reparto por
tasa y porcentaje de la 0027: ahora cada producto, equipo y malla tiene su tarifa en la segunda
moneda (fijada por el contrato) y el pozo elige en cuál cobra.

Los pozos existentes siguen cobrando en su moneda principal (cobrar_en_secundaria = False).
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0030_alter_reportediario_mi_representante_1_and_more'),
    ]

    operations = [
        migrations.RemoveField(model_name='pozo', name='tasa_cambio_secundaria'),
        migrations.RemoveField(model_name='pozo', name='porcentaje_cobro_secundaria'),
        migrations.AlterField(
            model_name='pozo', name='moneda_secundaria',
            field=models.CharField(blank=True, default='', max_length=6, verbose_name='Segunda Moneda'),
        ),
        migrations.AddField(
            model_name='pozo', name='cobrar_en_secundaria',
            field=models.BooleanField(
                default=False, verbose_name='Cobrar en la Segunda Moneda',
                help_text='Si está marcado, los costos usan las tarifas en la segunda moneda.'),
        ),
        migrations.AddField(
            model_name='productoactivopozo', name='precio_secundaria',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True,
                                      verbose_name='Precio en la Segunda Moneda'),
        ),
        migrations.AddField(
            model_name='equipoactivopozo', name='precio_renta_secundaria',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12,
                                      verbose_name='Precio de Renta en la Segunda Moneda'),
        ),
        migrations.AddField(
            model_name='equipoactivopozo', name='precio_standby_secundaria',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12,
                                      verbose_name='Precio Stand-By en la Segunda Moneda'),
        ),
        migrations.AddField(
            model_name='mallaactivapozo', name='precio_secundaria',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12,
                                      verbose_name='Precio en la Segunda Moneda'),
        ),
    ]
