from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0016_distribucion_tiempo'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipo',
            name='posiciones_malla',
            field=models.PositiveSmallIntegerField(default=0, help_text='Cuántas mallas lleva el equipo (0 = no usa mallas; máximo 12). Ej.: zaranda BEM 3 = 3, BEM 600 = 5. La posición 1 es la más cercana a la línea de flujo.', verbose_name='Posiciones de Malla'),
        ),
        migrations.CreateModel(
            name='TipoTicketMalla',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80, verbose_name='Tipo de Ticket')),
                ('sentido', models.CharField(choices=[('ENTRADA', 'Entrada al pozo'), ('SALIDA', 'Salida del pozo')], default='ENTRADA', max_length=8, verbose_name='Sentido')),
                ('pozo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tipos_ticket_malla', to='operaciones.pozo')),
            ],
            options={
                'verbose_name': 'Tipo de Ticket de Mallas',
                'verbose_name_plural': 'Tipos de Ticket de Mallas',
                'ordering': ['sentido', 'nombre'],
                'unique_together': {('pozo', 'nombre')},
            },
        ),
        migrations.CreateModel(
            name='TicketMalla',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(blank=True, max_length=40, verbose_name='N° de Ticket')),
                ('pedido_por', models.CharField(blank=True, max_length=100, verbose_name='Pedido por')),
                ('recibido_por', models.CharField(blank=True, max_length=100, verbose_name='Recibido por')),
                ('almacen_codigo', models.CharField(blank=True, max_length=15, verbose_name='Código de Almacén')),
                ('almacen_nombre', models.CharField(blank=True, max_length=100, verbose_name='Almacén')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets_malla', to='operaciones.reportediario')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='tickets', to='operaciones.tipoticketmalla', verbose_name='Tipo')),
            ],
            options={
                'verbose_name': 'Ticket de Mallas',
                'verbose_name_plural': 'Tickets de Mallas',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='TicketMallaDetalle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nuevas_ticket', models.PositiveIntegerField(default=0, verbose_name='Nuevas según ticket')),
                ('nuevas_real', models.PositiveIntegerField(default=0, verbose_name='Nuevas reales')),
                ('usadas_ticket', models.PositiveIntegerField(default=0, verbose_name='Usadas según ticket')),
                ('usadas_real', models.PositiveIntegerField(default=0, verbose_name='Usadas reales')),
                ('malla', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detalles_ticket', to='operaciones.mallazaranda')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='operaciones.ticketmalla')),
            ],
            options={
                'verbose_name': 'Detalle de Ticket de Mallas',
                'verbose_name_plural': 'Detalles de Tickets de Mallas',
                'ordering': ['malla__mesh_size', 'malla__codigo'],
                'unique_together': {('ticket', 'malla')},
            },
        ),
        migrations.CreateModel(
            name='TransaccionMalla',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('secuencia', models.PositiveIntegerField(verbose_name='N° de Transacción')),
                ('accion', models.CharField(choices=[('INSTALAR_NUEVA', 'Instalar malla nueva'), ('INSTALAR_USADA', 'Instalar malla usada'), ('A_ALMACEN', 'Pasar al almacén'), ('DESECHAR_EQUIPO', 'Desechar del equipo'), ('DESECHAR_ALMACEN', 'Desechar del almacén')], max_length=20, verbose_name='Acción')),
                ('equipo_serie', models.CharField(blank=True, max_length=30, verbose_name='N° de Serie del Equipo')),
                ('equipo_descripcion', models.CharField(blank=True, max_length=150, verbose_name='Equipo')),
                ('posicion', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Posición')),
                ('precio_unitario', models.DecimalField(decimal_places=2, default=0, help_text="Solo en 'Instalar malla nueva': precio neto de la malla en ese momento.", max_digits=12, verbose_name='Precio Unitario (neto)')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('equipo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='transacciones_malla', to='operaciones.equipo')),
                ('malla', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transacciones', to='operaciones.mallazaranda')),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transacciones_malla', to='operaciones.reportediario')),
            ],
            options={
                'verbose_name': 'Transacción de Malla',
                'verbose_name_plural': 'Transacciones de Mallas',
                'ordering': ['secuencia'],
            },
        ),
    ]
