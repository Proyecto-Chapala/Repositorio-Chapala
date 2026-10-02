from django.db import migrations, models


def cerrar_intervalos_anteriores(apps, schema_editor):
    """En los pozos que ya tienen varios intervalos, todos menos el último quedan cerrados."""
    Intervalo = apps.get_model('operaciones', 'IntervaloRevestimiento')
    ultimos = {}
    for itv in Intervalo.objects.order_by('pozo_id', 'numero_intervalo'):
        ultimos[itv.pozo_id] = itv.pk
    Intervalo.objects.exclude(pk__in=list(ultimos.values())).update(cerrado=True)


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0026_textos_smart_mud'),
    ]

    operations = [
        migrations.AddField(
            model_name='intervalorevestimiento',
            name='cerrado',
            field=models.BooleanField(default=False, help_text='Se cierra cuando se baja el revestidor. No se puede abrir otro intervalo mientras este siga abierto.', verbose_name='Intervalo Cerrado'),
        ),
        migrations.AddField(
            model_name='pozo',
            name='moneda_secundaria',
            field=models.CharField(blank=True, default='', max_length=6, verbose_name='Segunda Moneda de Cobro'),
        ),
        migrations.AddField(
            model_name='pozo',
            name='tasa_cambio_secundaria',
            field=models.DecimalField(blank=True, decimal_places=4, help_text='Cuántas unidades de la segunda moneda equivalen a 1 de la moneda del pozo.', max_digits=18, null=True, verbose_name='Tasa de Cambio'),
        ),
        migrations.AddField(
            model_name='pozo',
            name='porcentaje_cobro_secundaria',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='% Cobrado en la Segunda Moneda'),
        ),
        migrations.RunPython(cerrar_intervalos_anteriores, migrations.RunPython.noop),
    ]
