from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0013_reportediariomudcheck_adjusted_solids_pct_and_more'),
    ]

    operations = [
        # --- Catálogo maestro global de componentes de sarta ---
        migrations.CreateModel(
            name='ComponenteSarta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=30, unique=True, verbose_name='Código del Componente')),
                ('descripcion', models.CharField(max_length=150, verbose_name='Descripción')),
                ('tipo', models.CharField(choices=[
                    ('MECHA', 'Mecha (Bit)'),
                    ('MOTOR', 'Motor de Fondo / MWD'),
                    ('DRILL_COLLAR', 'Portamecha (Drill Collar)'),
                    ('HEAVY_WEIGHT', 'Tubería Pesada (Heavy Weight)'),
                    ('DRILL_PIPE', 'Tubería de Perforación (Drill Pipe)'),
                    ('ESTABILIZADOR', 'Estabilizador'),
                    ('CROSSOVER', 'Crossover / Nipple'),
                    ('REVESTIDOR', 'Revestidor (bajando casing)'),
                    ('OTROS', 'Otros'),
                ], default='DRILL_PIPE', max_length=20, verbose_name='Tipo de Componente')),
                ('od_in', models.DecimalField(decimal_places=4, max_digits=8, verbose_name='Diámetro Externo — OD (in)')),
                ('id_in', models.DecimalField(decimal_places=4, default=0, help_text='0 para componentes macizos o para la mecha.', max_digits=8, verbose_name='Diámetro Interno — ID (in)')),
                ('tool_joint_od_in', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True, verbose_name='OD de Junta (in)')),
                ('tool_joint_id_in', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True, verbose_name='ID de Junta (in)')),
                ('tool_joint_length_in', models.DecimalField(blank=True, decimal_places=2, help_text='Largo de la junta por tramo, en pulgadas (ONE-TRAX usa 21 in por tramo de 31 ft).', max_digits=8, null=True, verbose_name='Largo de Junta (in)')),
                ('largo_tramo_ft', models.DecimalField(decimal_places=2, default=31.0, help_text='Largo nominal de un tramo (joint). Se usa para ponderar el efecto de la junta.', max_digits=8, verbose_name='Largo de Tramo (ft)')),
            ],
            options={
                'verbose_name': 'Componente de Sarta (Catálogo Maestro)',
                'verbose_name_plural': 'Componentes de Sarta (Catálogo Maestro)',
                'ordering': ['tipo', '-od_in', 'codigo'],
            },
        ),

        # --- Riser en la configuración del pozo ---
        migrations.AddField(
            model_name='wellheaderinfo',
            name='usa_riser',
            field=models.BooleanField(default=False, help_text='Si está activo, el riser se incluye como primer tramo del perfil de confinamiento del pozo.', verbose_name='El pozo usa Riser'),
        ),
        migrations.AddField(
            model_name='wellheaderinfo',
            name='riser_id_in',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True, verbose_name='Diámetro Interno del Riser (in)'),
        ),
        migrations.AddField(
            model_name='wellheaderinfo',
            name='riser_length_ft',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Si se deja vacío se asume Air Gap + Water Depth.', max_digits=10, null=True, verbose_name='Longitud del Riser (ft)'),
        ),

        # --- Campos de Well Geometry en el reporte diario ---
        migrations.AddField(
            model_name='reportediario',
            name='intervalo_costo',
            field=models.ForeignKey(blank=True, help_text='Intervalo del pozo al que se imputan los costos del día.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reportes_asignados', to='operaciones.intervalorevestimiento', verbose_name='Intervalo de Costo (Interval Number)'),
        ),
        migrations.AddField(
            model_name='reportediario',
            name='orden_impresion_intervalo',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Orden de Impresión (Print Order)'),
        ),
        migrations.AddField(
            model_name='reportediario',
            name='pilot_hole_size_in',
            field=models.FloatField(default=0.0, verbose_name='Diámetro del Hoyo Piloto (in)'),
        ),
        migrations.AddField(
            model_name='reportediario',
            name='pilot_hole_depth_ft',
            field=models.FloatField(default=0.0, verbose_name='Profundidad del Hoyo Piloto (ft)'),
        ),

        # --- Sarta de perforación por reporte diario ---
        migrations.CreateModel(
            name='TramoSarta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.PositiveSmallIntegerField(default=1, help_text='Posición desde la mecha hacia superficie.', verbose_name='Orden (1 = mecha)')),
                ('descripcion', models.CharField(blank=True, max_length=150, verbose_name='Descripción / Tipo')),
                ('longitud_ft', models.FloatField(default=0.0, verbose_name='Longitud (ft)')),
                ('od_in', models.FloatField(default=0.0, verbose_name='Diámetro Externo — OD (in)')),
                ('id_in', models.FloatField(default=0.0, verbose_name='Diámetro Interno — ID (in)')),
                ('tool_joint_od_in', models.FloatField(default=0.0, verbose_name='OD de Junta (in)')),
                ('tool_joint_id_in', models.FloatField(default=0.0, verbose_name='ID de Junta (in)')),
                ('tool_joint_length_in', models.FloatField(default=0.0, verbose_name='Largo de Junta (in)')),
                ('largo_tramo_ft', models.FloatField(default=31.0, verbose_name='Largo de Tramo (ft)')),
                ('componente', models.ForeignKey(blank=True, help_text='Opcional: al elegirlo se autocompletan los diámetros, que siguen siendo editables.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tramos_usados', to='operaciones.componentesarta', verbose_name='Componente del Catálogo')),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tramos_sarta', to='operaciones.reportediario')),
            ],
            options={
                'verbose_name': 'Tramo de Sarta de Perforación',
                'verbose_name_plural': 'Tramos de Sarta de Perforación',
                'ordering': ['orden', 'id'],
                'unique_together': {('reporte', 'orden')},
            },
        ),
    ]
