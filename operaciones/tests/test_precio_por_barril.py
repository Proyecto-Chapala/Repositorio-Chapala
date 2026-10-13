"""
Precio por unidad o por barril (punto 8 de docs/23_CORRECCIONES_REVISION_OCT.md).
El motor siempre trabaja con precio por unidad; el precio por barril se convierte con los
barriles que ocupa una unidad del producto.
"""

from decimal import Decimal

from django.test import SimpleTestCase, TestCase

from operaciones import volumetria as vol
from operaciones.forms_pozo import ProductoActivoPozoForm
from operaciones.models import Pozo, Producto, ProductoActivoPozo
from operaciones.views_inventario import _productos_pozo


class PrecioPorUnidadTests(SimpleTestCase):

    def test_cobro_por_unidad_deja_el_precio_igual(self):
        self.assertEqual(vol.precio_por_unidad(18, 'UNIDAD', 'LBS', 100, 4.2), 18.0)

    def test_producto_en_barriles_cobrado_por_barril(self):
        # Salmuera 8.5 en barriles: 1 unidad = 1 bbl
        self.assertEqual(vol.precio_por_unidad(30, vol.COBRO_BARRIL, 'BBL', 1, None), 30.0)

    def test_producto_en_galones_cobrado_por_barril(self):
        # Tambor de 42 gal = 1 bbl
        self.assertAlmostEqual(vol.precio_por_unidad(30, vol.COBRO_BARRIL, 'GAL', 42, None), 30.0)

    def test_producto_en_libras_cobrado_por_barril_usa_la_gravedad(self):
        # Saco de 100 lb con GE 1.0 ocupa 100/350 bbl
        self.assertAlmostEqual(vol.precio_por_unidad(350, vol.COBRO_BARRIL, 'LBS', 100, 1.0), 100.0)

    def test_sin_datos_para_convertir_no_hay_barriles(self):
        self.assertIsNone(vol.barriles_por_unidad('SACO', 50, 1.0))
        self.assertIsNone(vol.barriles_por_unidad('LBS', 100, None))
        self.assertIsNone(vol.barriles_por_unidad('BBL', 0, None))

    def test_costo_del_dia_con_precio_por_barril(self):
        # 50 bbl de salmuera a 30 por barril
        dias = [{'id': 1, 'fecha_texto': 'dia 1', 'hoyo_fluido': 0, 'manual': {},
                 'fosas': [{'numero': 1, 'grupo': vol.ACTIVO, 'real': None}],
                 'tickets': [{'sentido': 'ENTRADA', 'detalles': [{'producto': 1, 'real': 100, 'ticket': 100}]}],
                 'transacciones': [{'secuencia': 1, 'tipo': 'QUIMICOS', 'fosa': 1, 'aceite': 0, 'agua': 0,
                                    'productos': [{'producto': 1, 'cantidad': 50, 'unidad': 'BBL', 'tamano': 1,
                                                   'gravedad': 0,
                                                   'precio': vol.precio_por_unidad(30, vol.COBRO_BARRIL, 'BBL', 1, 0),
                                                   'categoria': 1, 'concentracion': False}]}]}]
        self.assertEqual(vol.simular(dias, 1)['inventario'][1]['costo_diario'], 1500)


class CobroPorBarrilEnPozoTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA')
        self.producto = Producto.objects.create(codigo='KCL', descripcion='KCl', unidad='LBS')

    def formulario(self, **cambios):
        datos = {'producto': self.producto.id, 'unidad': 'LBS', 'unit_size': '100',
                 'gravedad_especifica': '1.0', 'precio': '350', 'cobro_por': 'BARRIL',
                 'grupo_producto': 1, 'codigo_costo_diario': 1,
                 'categoria_costo_wmgt': 1, 'categoria_costo_cf': 1}
        datos.update(cambios)
        return ProductoActivoPozoForm(datos)

    def test_cobro_por_barril_valido(self):
        self.assertTrue(self.formulario().is_valid())

    def test_cobro_por_barril_con_unidad_sin_conversion_se_rechaza(self):
        form = self.formulario(unidad='SACO', gravedad_especifica='')
        self.assertFalse(form.is_valid())
        self.assertIn('cobro_por', form.errors)

    def test_el_pozo_usa_el_precio_por_unidad_equivalente(self):
        ProductoActivoPozo.objects.create(
            pozo=self.pozo, producto=self.producto, unidad='LBS', unit_size=Decimal('100'),
            gravedad_especifica=Decimal('1.0'), precio=Decimal('350'), cobro_por=ProductoActivoPozo.COBRO_BARRIL,
        )
        datos = _productos_pozo(self.pozo)[self.producto.id]
        self.assertAlmostEqual(datos['precio'], 100.0)
        self.assertEqual(datos['precio_cargado'], 350.0)
        self.assertEqual(datos['cobro_por'], ProductoActivoPozo.COBRO_BARRIL)
