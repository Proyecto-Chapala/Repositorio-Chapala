from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0019_perdidas_reporte'),
    ]

    operations = [
        migrations.CreateModel(
            name='VolumenFosaDia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fosa_numero', models.PositiveSmallIntegerField(verbose_name='N° de Fosa')),
                ('fosa_descripcion', models.CharField(blank=True, max_length=100, verbose_name='Fosa')),
                ('capacidad', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Capacidad (bbl)')),
                ('tipo_codigo', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Tipo de fosa (código)')),
                ('tipo_descripcion', models.CharField(blank=True, max_length=100, verbose_name='Tipo de fosa')),
                ('volumen_final', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Volumen final real (bbl)')),
                ('peso_fluido', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Peso del fluido (lb/gal)')),
                ('temperatura', models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True, verbose_name='Temperatura (°F)')),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volumenes_fosa', to='operaciones.reportediario')),
            ],
            options={
                'verbose_name': 'Volumen Diario de Fosa',
                'verbose_name_plural': 'Volúmenes Diarios de Fosas',
                'ordering': ['fosa_numero'],
                'unique_together': {('reporte', 'fosa_numero')},
            },
        ),
        migrations.CreateModel(
            name='VolumenHoyoDia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_fluido_anular', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='No fluido — anular (bbl)')),
                ('no_fluido_sarta', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='No fluido — sarta (bbl)')),
                ('no_fluido_bajo_mecha', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='No fluido — bajo la mecha (bbl)')),
                ('reporte', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='volumen_hoyo', to='operaciones.reportediario')),
            ],
            options={
                'verbose_name': 'Volumen del Hoyo del Día',
                'verbose_name_plural': 'Volúmenes del Hoyo por Día',
            },
        ),
        migrations.CreateModel(
            name='TransaccionVolumen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('secuencia', models.PositiveIntegerField(verbose_name='N° de Movimiento')),
                ('tipo', models.CharField(choices=[('QUIMICOS', 'Agregar químicos'), ('LODO_ENTERO', 'Agregar lodo entero'), ('TRANSFERENCIA', 'Transferencia entre fosas'), ('DEVOLUCION', 'Devolución'), ('PERDIDA', 'Pérdida y descarte')], max_length=15, verbose_name='Tipo')),
                ('fosa_numero', models.PositiveSmallIntegerField(verbose_name='Fosa')),
                ('fosa_descripcion', models.CharField(blank=True, max_length=100)),
                ('destino_numero', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Fosa destino')),
                ('destino_descripcion', models.CharField(blank=True, max_length=100)),
                ('volumen_bbl', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Volumen (bbl)')),
                ('aceite_bbl', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Fluido base agregado (bbl)')),
                ('agua_bbl', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Agua agregada (bbl)')),
                ('peso_lodo', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Peso del lodo (lb/gal)')),
                ('lodo_producto_texto', models.CharField(blank=True, max_length=255)),
                ('lodo_cantidad', models.DecimalField(decimal_places=3, default=0, max_digits=12, verbose_name='Cantidad consumida')),
                ('lodo_precio', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('lodo_categoria', models.PositiveSmallIntegerField(default=1)),
                ('origen_destino', models.CharField(blank=True, max_length=120, verbose_name='Recibido de / Devuelto a')),
                ('perdida_codigo', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Tipo de pérdida (código)')),
                ('perdida_descripcion', models.CharField(blank=True, max_length=100)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('lodo_producto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='operaciones.producto')),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transacciones_volumen', to='operaciones.reportediario')),
            ],
            options={
                'verbose_name': 'Movimiento de Volumetría',
                'verbose_name_plural': 'Movimientos de Volumetría',
                'ordering': ['secuencia'],
            },
        ),
        migrations.CreateModel(
            name='TransaccionVolumenProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(blank=True, max_length=255)),
                ('cantidad', models.DecimalField(decimal_places=3, default=0, max_digits=12)),
                ('es_concentracion', models.BooleanField(default=False)),
                ('unidad', models.CharField(blank=True, max_length=30)),
                ('tamano', models.DecimalField(decimal_places=3, default=0, max_digits=12)),
                ('gravedad', models.DecimalField(decimal_places=4, default=0, max_digits=8)),
                ('precio', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('categoria_costo', models.PositiveSmallIntegerField(default=1)),
                ('calcula_concentracion', models.BooleanField(default=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='operaciones.producto')),
                ('transaccion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='operaciones.transaccionvolumen')),
            ],
            options={
                'verbose_name': 'Producto de Movimiento de Volumetría',
                'verbose_name_plural': 'Productos de Movimientos de Volumetría',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='InventarioProductoDia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usado_otro', models.DecimalField(decimal_places=3, default=0, max_digits=12, verbose_name='Usado en otro módulo')),
                ('ajuste', models.DecimalField(decimal_places=3, default=0, max_digits=12, verbose_name='Ajuste (+ suma / − resta)')),
                ('en_pedido', models.DecimalField(decimal_places=3, default=0, max_digits=12, verbose_name='En pedido')),
                ('no_imprimir', models.BooleanField(default=False, verbose_name='No imprimir')),
                ('precio', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Precio aplicado')),
                ('categoria_costo', models.PositiveSmallIntegerField(default=1)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='operaciones.producto')),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventario_productos', to='operaciones.reportediario')),
            ],
            options={
                'verbose_name': 'Inventario Diario de Producto',
                'verbose_name_plural': 'Inventario Diario de Productos',
                'unique_together': {('reporte', 'producto')},
            },
        ),
        migrations.CreateModel(
            name='TicketProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(blank=True, max_length=40)),
                ('pedido_por', models.CharField(blank=True, max_length=100)),
                ('recibido_por', models.CharField(blank=True, max_length=100)),
                ('almacen_codigo', models.CharField(blank=True, max_length=15)),
                ('almacen_nombre', models.CharField(blank=True, max_length=100)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets_producto', to='operaciones.reportediario')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='tickets_producto', to='operaciones.tipoticketmalla')),
            ],
            options={
                'verbose_name': 'Ticket de Productos',
                'verbose_name_plural': 'Tickets de Productos',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='TicketProductoDetalle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_ticket', models.DecimalField(decimal_places=3, default=0, max_digits=12, verbose_name='Según ticket')),
                ('cantidad_real', models.DecimalField(decimal_places=3, default=0, max_digits=12, verbose_name='Real')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='operaciones.producto')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='operaciones.ticketproducto')),
            ],
            options={
                'verbose_name': 'Detalle de Ticket de Productos',
                'verbose_name_plural': 'Detalles de Tickets de Productos',
                'unique_together': {('ticket', 'producto')},
            },
        ),
    ]
