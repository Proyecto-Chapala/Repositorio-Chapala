from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0015_reportediariocomentarios'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReporteDiarioTiempo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('horas_periodo', models.DecimalField(decimal_places=2, default=24, help_text='24 por defecto. Se cambia solo en días especiales (inicio, fin o cambio de hora de corte).', max_digits=5, verbose_name='Horas del Período')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('reporte', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='distribucion_tiempo', to='operaciones.reportediario')),
            ],
            options={
                'verbose_name': 'Distribución de Tiempo del Reporte',
                'verbose_name_plural': 'Distribuciones de Tiempo de Reportes',
            },
        ),
        migrations.CreateModel(
            name='ReporteDiarioActividadTiempo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.PositiveSmallIntegerField(default=0, verbose_name='Orden')),
                ('tipo_numero', models.PositiveIntegerField(verbose_name='Número de Actividad (catálogo del pozo)')),
                ('descripcion', models.CharField(max_length=120, verbose_name='Actividad')),
                ('horas', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Horas')),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actividades_tiempo', to='operaciones.reportediario')),
            ],
            options={
                'verbose_name': 'Actividad de Distribución de Tiempo',
                'verbose_name_plural': 'Actividades de Distribución de Tiempo',
                'ordering': ['orden', 'id'],
                'unique_together': {('reporte', 'tipo_numero')},
            },
        ),
    ]
