from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0018_uso_equipos'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerdidaReportePozo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.PositiveSmallIntegerField(verbose_name='Código de la categoría de pérdida')),
                ('orden', models.PositiveSmallIntegerField(default=0, verbose_name='Orden en el reporte')),
                ('pozo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='perdidas_reporte', to='operaciones.pozo')),
            ],
            options={
                'verbose_name': 'Pérdida Mostrada en el Reporte',
                'verbose_name_plural': 'Pérdidas Mostradas en el Reporte',
                'ordering': ['orden', 'codigo'],
                'unique_together': {('pozo', 'codigo')},
            },
        ),
    ]
