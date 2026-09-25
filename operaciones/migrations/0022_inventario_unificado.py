"""
Inventario unificado: el reporte diario descuenta y devuelve Producto.cantidad.

Los campos `stock_aplicado` registran cuánto descontó cada consumo, para poder devolverlo al
deshacer un movimiento o borrar un reporte.

Datos existentes: decisión del usuario (25/09/2026) — la cantidad actual del Inventario se
toma como correcta y NO se descuentan otra vez los consumos ya registrados. Por eso los
registros viejos se marcan como "ya aplicados" (stock_aplicado = lo que consumieron): así,
volver a guardar un día viejo no descuenta nada, y deshacer o borrar un consumo viejo sí
devuelve lo que consumió.
"""

from django.db import migrations, models


def _es_servicio(ProductoActivoPozo, cache, pozo_id, producto_id):
    clave = (pozo_id, producto_id)
    if clave not in cache:
        activo = (ProductoActivoPozo.objects
                  .filter(pozo_id=pozo_id, producto_id=producto_id).order_by('id').first())
        cache[clave] = bool(activo) and not (activo.unidad or '').strip()
    return cache[clave]


def marcar_existentes_como_aplicados(apps, schema_editor):
    TransaccionVolumen = apps.get_model('operaciones', 'TransaccionVolumen')
    TransaccionVolumenProducto = apps.get_model('operaciones', 'TransaccionVolumenProducto')
    InventarioProductoDia = apps.get_model('operaciones', 'InventarioProductoDia')
    ProductoActivoPozo = apps.get_model('operaciones', 'ProductoActivoPozo')
    cache = {}

    for p in TransaccionVolumenProducto.objects.filter(es_concentracion=False).exclude(unidad=''):
        p.stock_aplicado = p.cantidad
        p.save(update_fields=['stock_aplicado'])

    for t in TransaccionVolumen.objects.filter(lodo_producto__isnull=False).select_related('reporte'):
        if not _es_servicio(ProductoActivoPozo, cache, t.reporte.pozo_id, t.lodo_producto_id):
            t.lodo_stock_aplicado = t.lodo_cantidad
            t.save(update_fields=['lodo_stock_aplicado'])

    for m in InventarioProductoDia.objects.select_related('reporte'):
        if not _es_servicio(ProductoActivoPozo, cache, m.reporte.pozo_id, m.producto_id):
            m.stock_aplicado = m.usado_otro - m.ajuste
            m.save(update_fields=['stock_aplicado'])


class Migration(migrations.Migration):

    dependencies = [
        ('operaciones', '0021_modulos_opcionales'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaccionvolumen',
            name='lodo_stock_aplicado',
            field=models.DecimalField(
                decimal_places=3, default=0, max_digits=12,
                help_text='Unidades del producto de lodo entero que este movimiento restó de Producto.cantidad.',
                verbose_name='Descontado del inventario general'),
        ),
        migrations.AddField(
            model_name='transaccionvolumenproducto',
            name='stock_aplicado',
            field=models.DecimalField(
                decimal_places=3, default=0, max_digits=12,
                help_text='Cantidad que este movimiento restó de Producto.cantidad (0 en concentraciones y servicios).',
                verbose_name='Descontado del inventario general'),
        ),
        migrations.AddField(
            model_name='inventarioproductodia',
            name='stock_aplicado',
            field=models.DecimalField(
                decimal_places=3, default=0, max_digits=12,
                help_text='Neto (usado en otro módulo − ajuste) ya aplicado a Producto.cantidad.',
                verbose_name='Descontado del inventario general'),
        ),
        migrations.RunPython(marcar_existentes_como_aplicados, migrations.RunPython.noop),
    ]
