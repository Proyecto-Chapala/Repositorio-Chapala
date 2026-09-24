from django.db import migrations, models
import django.db.models.deletion


def _muestra():
    return [
        ('equipo_serie', models.CharField(max_length=30, verbose_name='N° de Serie')),
        ('equipo_descripcion', models.CharField(blank=True, max_length=150, verbose_name='Equipo')),
        ('hora_inicio', models.CharField(blank=True, max_length=5, verbose_name='Hora de inicio')),
        ('hora_fin', models.CharField(blank=True, max_length=5, verbose_name='Hora de fin')),
        ('orden', models.PositiveSmallIntegerField(default=1, verbose_name='Orden de impresión')),
        ('profundidad_ft', models.FloatField(blank=True, null=True, verbose_name='Profundidad medida (ft)')),
        ('profundidad_perforada_ft', models.FloatField(blank=True, null=True, verbose_name='Profundidad perforada representada (ft)')),
        ('comentarios', models.CharField(blank=True, max_length=255, verbose_name='Comentarios')),
    ]


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0020_volumetria'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObservacionesIFE',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fluidos_resumen', models.TextField(blank=True, verbose_name='Fluidos de perforación — resumen')),
                ('fluidos_plan', models.TextField(blank=True, verbose_name='Fluidos de perforación — plan siguiente')),
                ('solidos_resumen', models.TextField(blank=True, verbose_name='Control de sólidos — resumen')),
                ('solidos_plan', models.TextField(blank=True, verbose_name='Control de sólidos — plan siguiente')),
                ('reporte', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='observaciones_ife', to='operaciones.reportediario')),
            ],
            options={'verbose_name': 'Observaciones IFE', 'verbose_name_plural': 'Observaciones IFE'},
        ),
        migrations.CreateModel(
            name='AnalisisSolidosEquipo',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'))] + _muestra() + [
                ('tipo_lodo', models.CharField(choices=[('WBM', 'Base agua'), ('OBM', 'Base aceite')], default='WBM', max_length=3)),
                ('tipo_muestra', models.CharField(blank=True, max_length=60, verbose_name='Tipo de muestra (ej. descarga)')),
                ('datos', models.JSONField(default=dict, verbose_name='Datos de la muestra')),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analisis_solidos_equipo', to='operaciones.reportediario')),
            ],
            options={'verbose_name': 'Análisis de Sólidos por Equipo', 'verbose_name_plural': 'Análisis de Sólidos por Equipo', 'ordering': ['orden', 'id'], 'abstract': False},
        ),
        migrations.CreateModel(
            name='RetencionRecortes',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'))] + _muestra() + [
                ('diametro_mecha_in', models.FloatField(blank=True, null=True, verbose_name='Diámetro de mecha (in)')),
                ('datos', models.JSONField(default=dict, verbose_name='Datos de la prueba')),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retencion_recortes', to='operaciones.reportediario')),
            ],
            options={'verbose_name': 'Retención en Recortes', 'verbose_name_plural': 'Retención en Recortes', 'ordering': ['orden', 'id'], 'abstract': False},
        ),
        migrations.CreateModel(
            name='EventoNoProgramado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoria', models.CharField(choices=[('FLUIDOS', 'Fluidos y perforación'), ('CALIDAD', 'Calidad de producto'), ('LOGISTICA', 'Logística'), ('EQUIPO', 'Falla de equipo')], default='FLUIDOS', max_length=10)),
                ('tipo_problema', models.CharField(max_length=100, verbose_name='Tipo de problema')),
                ('tipo_fluido', models.CharField(blank=True, max_length=100, verbose_name='Tipo de fluido')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('causa', models.TextField(blank=True, verbose_name='Causa sospechada')),
                ('descripcion_perdida', models.TextField(blank=True, verbose_name='Descripción de la pérdida')),
                ('horas_perdidas', models.FloatField(blank=True, null=True, verbose_name='Tiempo perdido (h)')),
                ('volumen_perdido_bbl', models.FloatField(blank=True, null=True, verbose_name='Volumen perdido (bbl)')),
                ('costo', models.FloatField(blank=True, null=True, verbose_name='Costo estimado')),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eventos_no_programados', to='operaciones.reportediario')),
            ],
            options={'verbose_name': 'Evento No Programado', 'verbose_name_plural': 'Eventos No Programados', 'ordering': ['id']},
        ),
    ]
