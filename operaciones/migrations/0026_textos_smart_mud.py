from django.db import migrations, models


def ecuaciones_a_api(apps, schema_editor):
    """Pedido del cliente: que no aparezca M-I. Las ecuaciones de sólidos quedan solo en API."""
    Pozo = apps.get_model('operaciones', 'Pozo')
    Pozo.objects.exclude(ecuacion_solidos_base_agua='API').update(ecuacion_solidos_base_agua='API')
    Pozo.objects.exclude(ecuacion_solidos_base_aceite='API').update(ecuacion_solidos_base_aceite='API')
    MudConfig = apps.get_model('operaciones', 'ReporteDiarioMudConfig')
    MudConfig.objects.exclude(solids_equation='API').update(solids_equation='API')


class Migration(migrations.Migration):
    """Smart Mud: se quita "M-I" de etiquetas y opciones. Las ecuaciones de sólidos pasan a API."""

    dependencies = [
        ('operaciones', '0025_add_empaque_to_producto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pozo',
            name='ecuacion_solidos_base_agua',
            field=models.CharField(choices=[('API', 'API')], default='API', max_length=5, verbose_name='Ecuación de Sólidos — Base Agua'),
        ),
        migrations.AlterField(
            model_name='pozo',
            name='ecuacion_solidos_base_aceite',
            field=models.CharField(choices=[('API', 'API')], default='API', max_length=5, verbose_name='Ecuación de Sólidos — Base Aceite/Sintética'),
        ),
        migrations.AlterField(
            model_name='pozo',
            name='categoria_perdida_tipo',
            field=models.CharField(choices=[('MI', 'Estándar'), ('UK', 'UK'), ('HYDRO', 'Hydro'), ('STATOIL', 'Statoil'), ('IFE', 'IFE'), ('COMPLETION_FLUIDS', 'Completion Fluids'), ('CUSTOM', 'Personalizado')], default='MI', max_length=20, verbose_name='Categorías de Pérdida'),
        ),
        migrations.AlterField(
            model_name='productoactivopozo',
            name='es_producto_mi',
            field=models.BooleanField(default=True, verbose_name='¿Producto propio?'),
        ),
        migrations.AlterField(
            model_name='reportediariomudconfig',
            name='solids_equation',
            field=models.CharField(choices=[('API', 'API')], default='API', max_length=20, verbose_name='Current Solids Analysis Equations'),
        ),
        migrations.RunPython(ecuaciones_a_api, migrations.RunPython.noop),
    ]
