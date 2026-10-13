"""
Gravedad específica (GE): volumen que aporta un químico = lb / (350 × GE).
Sin GE ni tamaño de unidad el volumen sale en cero y la volumetría no cuadra, así que el
producto activo medido en peso no se puede guardar sin ellos.
"""

from decimal import Decimal

from django.test import SimpleTestCase, TestCase

from operaciones import volumetria as vol
from operaciones.forms_pozo import ProductoActivoPozoForm
from operaciones.models import Producto


class VolumenQuimicoTests(SimpleTestCase):

    def test_volumen_por_gravedad_especifica(self):
        # 10 sacos de 100 lb de barita (GE 4.2) = 1000 lb / (350 × 4.2)
        self.assertAlmostEqual(vol.volumen_quimico_bbl(10, 'LBS', 100, 4.2), 1000 / 1470)

    def test_los_kilos_se_pasan_a_libras(self):
        self.assertAlmostEqual(vol.volumen_quimico_bbl(1, 'KG', 25, 1.0), 25 * 2.20462 / 350)

    def test_productos_en_volumen_no_aportan_volumen_quimico(self):
        self.assertEqual(vol.volumen_quimico_bbl(5, 'GAL', 55, 0.9), 0.0)

    def test_se_mide_en_peso(self):
        self.assertTrue(vol.se_mide_en_peso(' lbs. '))
        self.assertFalse(vol.se_mide_en_peso('BBL'))
        self.assertFalse(vol.se_mide_en_peso(''))


class ProductoActivoGravedadTests(TestCase):

    def setUp(self):
        self.barita = Producto.objects.create(codigo='BARITA-325', descripcion='Barita', unidad='LBS')

    def formulario(self, **cambios):
        datos = {'producto': self.barita.id, 'unidad': 'LBS', 'unit_size': '100',
                 'gravedad_especifica': '4.2', 'grupo_producto': 1, 'codigo_costo_diario': 1,
                 'categoria_costo_wmgt': 1, 'categoria_costo_cf': 1}
        datos.update(cambios)
        return ProductoActivoPozoForm(datos)

    def test_producto_en_peso_completo_es_valido(self):
        self.assertTrue(self.formulario().is_valid())

    def test_producto_en_peso_sin_gravedad_especifica_se_rechaza(self):
        form = self.formulario(gravedad_especifica='')
        self.assertFalse(form.is_valid())
        self.assertIn('gravedad_especifica', form.errors)

    def test_producto_en_peso_sin_tamano_de_unidad_se_rechaza(self):
        form = self.formulario(unit_size='0')
        self.assertFalse(form.is_valid())
        self.assertIn('unit_size', form.errors)

    def test_producto_en_volumen_o_servicio_no_necesita_gravedad(self):
        self.assertTrue(self.formulario(unidad='BBL', gravedad_especifica='', unit_size='').is_valid())
        self.assertTrue(self.formulario(unidad='', gravedad_especifica='', unit_size='').is_valid())
