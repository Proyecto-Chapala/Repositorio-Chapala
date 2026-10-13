"""La matriz (Producto) es solo catálogo: no aporta precio ni existencia al pozo."""

from decimal import Decimal

from django.test import TestCase

from operaciones.models import Pozo, Producto, ProductoActivoPozo
from operaciones.views_inventario import _completar_productos, _productos_pozo


class ProductosDelPozoTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA')
        self.barita = Producto.objects.create(
            codigo='BARITA-325', descripcion='Barita', unidad='LBS',
            cantidad=Decimal('500'), costo=Decimal('18'), gravedad=Decimal('4.2'),
        )

    def test_el_precio_sin_cargar_es_cero_y_no_viene_de_la_matriz(self):
        ProductoActivoPozo.objects.create(pozo=self.pozo, producto=self.barita, unidad='LBS', precio=None)
        self.assertEqual(_productos_pozo(self.pozo)[self.barita.id]['precio'], 0.0)

    def test_el_precio_es_el_que_carga_el_usuario(self):
        ProductoActivoPozo.objects.create(pozo=self.pozo, producto=self.barita, unidad='LBS',
                                          precio=Decimal('21.50'))
        self.assertEqual(_productos_pozo(self.pozo)[self.barita.id]['precio'], 21.5)

    def test_un_producto_inactivo_tampoco_toma_el_precio_de_la_matriz(self):
        productos = _completar_productos({}, [self.barita.id])
        self.assertEqual(productos[self.barita.id]['precio'], 0.0)
