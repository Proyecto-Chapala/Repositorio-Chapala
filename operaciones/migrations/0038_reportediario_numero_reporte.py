from django.db import migrations, models


def poblar_numeros_reporte(apps, schema_editor):
    ReporteDiario = apps.get_model('operaciones', 'ReporteDiario')
    Pozo = apps.get_model('operaciones', 'Pozo')
    for pozo in Pozo.objects.all():
        reportes = ReporteDiario.objects.filter(pozo=pozo).order_by('fecha', 'id')
        for idx, rep in enumerate(reportes, start=1):
            if not rep.numero_reporte:
                rep.numero_reporte = idx
                rep.save(update_fields=['numero_reporte'])


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0037_inventarioproductodia_devuelto_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportediario',
            name='numero_reporte',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Número correlativo fijo del reporte para el pozo.',
                null=True,
                verbose_name='Número de Reporte'
            ),
        ),
        migrations.RunPython(poblar_numeros_reporte, reverse_code=migrations.RunPython.noop),
    ]

