from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0014_componentesarta_tramosarta_riser_pilothole'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReporteDiarioComentarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spec_mud_weight', models.CharField(blank=True, help_text='Rango objetivo acordado, por ejemplo 11.5-12.0', max_length=50, verbose_name='Peso del Lodo — Especificación')),
                ('spec_viscosidad', models.CharField(blank=True, max_length=50, verbose_name='Viscosidad — Especificación')),
                ('spec_filtrado', models.CharField(blank=True, help_text='Rango objetivo acordado, por ejemplo 3.0-5.0', max_length=50, verbose_name='Filtrado — Especificación')),
                ('mud_recap_remarks', models.TextField(blank=True, help_text='Una sola línea: es lo que se imprime en el Well Recap del pozo.', verbose_name='Resumen del Día (Mud Recap Remarks)')),
                ('remarks_and_treatment', models.TextField(blank=True, help_text='Actividad y servicio de fluidos prestado durante el día.', verbose_name='Observaciones y Tratamiento')),
                ('remarks', models.TextField(blank=True, help_text='Operaciones generales del taladro; normalmente se toma de la hoja IADC.', verbose_name='Observaciones de Operaciones')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('reporte', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='operaciones.reportediario')),
            ],
            options={
                'verbose_name': 'Comentarios del Reporte Diario',
                'verbose_name_plural': 'Comentarios de Reportes Diarios',
            },
        ),
    ]
