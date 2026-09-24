from django.db import migrations, models
import django.db.models.deletion


TIPOS_EQUIPO = [
    ('CENTRIFUGA', 'Centrífuga'),
    ('LIMPIADOR_LODO', 'Limpiador de Lodo (Mud Cleaner)'),
    ('ZARANDA', 'Zaranda (Shale Shaker)'),
    ('SECADOR_RECORTES', 'Secador de Recortes (Cuttings Dryer)'),
    ('SISTEMA_VACIO', 'Sistema de Vacío'),
    ('CONTENEDOR_RECORTES', 'Contenedor de Recortes'),
    ('OTROS', 'Otros'),
]


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0017_control_solidos_mallas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipo',
            name='tipo_equipo',
            field=models.CharField(choices=TIPOS_EQUIPO, default='OTROS', help_text="Agrupa el equipo para 'Equipment Properties Setup' (Centrífuga, Mud Cleaner, Shale Shaker, etc.).", max_length=25, verbose_name='Tipo de Equipo'),
        ),
        migrations.AlterField(
            model_name='propiedadequipotipo',
            name='tipo_equipo',
            field=models.CharField(choices=TIPOS_EQUIPO, max_length=25, verbose_name='Tipo de Equipo'),
        ),
        migrations.AlterField(
            model_name='equipopropiedadseleccionada',
            name='tipo_equipo',
            field=models.CharField(choices=TIPOS_EQUIPO, max_length=25, verbose_name='Tipo de Equipo'),
        ),
        migrations.AlterField(
            model_name='equipopropiedadextra',
            name='tipo_equipo',
            field=models.CharField(choices=TIPOS_EQUIPO, max_length=25, verbose_name='Tipo de Equipo'),
        ),
        migrations.CreateModel(
            name='UsoEquipoDia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('equipo_serie', models.CharField(max_length=30, verbose_name='N° de Serie')),
                ('equipo_descripcion', models.CharField(blank=True, max_length=150, verbose_name='Equipo')),
                ('tipo_equipo', models.CharField(blank=True, max_length=25, verbose_name='Tipo de Equipo')),
                ('horas', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Horas en operación')),
                ('mud_on_cuttings', models.DecimalField(blank=True, decimal_places=3, help_text='Volumen de lodo que sale pegado a cada volumen de recortes descargados.', max_digits=8, null=True, verbose_name='Lodo en recortes (bbl/bbl)')),
                ('porcentaje_recortes', models.DecimalField(blank=True, decimal_places=2, help_text='Qué parte del hoyo perforado en el día descarga este equipo (100 % = todo).', max_digits=5, null=True, verbose_name='% de recortes')),
                ('tipo_perdida_codigo', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Tipo de pérdida (código)')),
                ('tipo_perdida_descripcion', models.CharField(blank=True, max_length=100, verbose_name='Tipo de pérdida')),
                ('caudal_entrada_gpm', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Caudal de entrada (gpm)')),
                ('densidad_entrada', models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True, verbose_name='Densidad de entrada (lb/gal)')),
                ('densidad_salida', models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True, verbose_name='Densidad de salida (lb/gal)')),
                ('densidad_descarte', models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True, verbose_name='Densidad de descarte (lb/gal)')),
                ('cantidad_usada', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Cantidad usada')),
                ('codigo_cobro', models.CharField(choices=[('COMPLETO', 'Cobro completo'), ('STANDBY', 'Stand-by'), ('SIN_COBRO', 'Sin cobro')], default='COMPLETO', max_length=10, verbose_name='Código de cobro')),
                ('tarifa', models.DecimalField(decimal_places=2, default=0, help_text='Copia de la tarifa del pozo (renta o stand-by) el día que se registró.', max_digits=12, verbose_name='Tarifa aplicada')),
                ('es_fluidos', models.BooleanField(default=False, verbose_name='¿Equipo de fluidos de perforación?')),
                ('horas_parada', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Horas de parada')),
                ('observaciones', models.TextField(blank=True, verbose_name='Observaciones de uso')),
                ('equipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='usos_diarios', to='operaciones.equipo')),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usos_equipo', to='operaciones.reportediario')),
            ],
            options={
                'verbose_name': 'Uso Diario de Equipo',
                'verbose_name_plural': 'Usos Diarios de Equipos',
                'ordering': ['tipo_equipo', 'equipo_serie'],
                'unique_together': {('reporte', 'equipo_serie')},
            },
        ),
        migrations.CreateModel(
            name='UsoEquipoPropiedad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.PositiveSmallIntegerField(default=0)),
                ('descripcion', models.CharField(max_length=100, verbose_name='Propiedad')),
                ('unidad', models.CharField(blank=True, max_length=30, verbose_name='Unidad')),
                ('valor', models.CharField(blank=True, max_length=60, verbose_name='Valor')),
                ('uso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='propiedades', to='operaciones.usoequipodia')),
            ],
            options={
                'verbose_name': 'Propiedad Diaria de Equipo',
                'verbose_name_plural': 'Propiedades Diarias de Equipos',
                'ordering': ['orden', 'id'],
            },
        ),
    ]
