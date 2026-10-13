"""
Tarifas en dos monedas (punto 9 de docs/23_CORRECCIONES_REVISION_OCT.md): cada producto, equipo y
malla tiene su tarifa en cada moneda (la del contrato, sin tasa de cambio) y el pozo elige en cuál
cobra. Los costos nunca mezclan monedas.
"""

from datetime import date
from decimal import Decimal

from django.test import TestCase

from operaciones.forms_pozo import EquipoActivoPozoForm, GeneralSetupForm, MallaActivaPozoForm
from operaciones.models import (Equipo, EquipoActivoPozo, MallaActivaPozo, MallaZaranda, Pozo, Producto,
                                ProductoActivoPozo)
from operaciones.models_daily_reports import ReporteDiario
from operaciones.views_control_solidos import _precio_neto, _tarifa_actual
from operaciones.models_control_solidos import UsoEquipoDia
from operaciones.views_inventario import _productos_pozo


def configuracion(**cambios):
    datos = {'moneda_simbolo': 'USD', 'moneda_secundaria': 'VES', 'cobrar_en_secundaria': False,
             'tasa_impuesto': 0, 'con_tratamiento_disposicion': False,
             'usar_api_5ta_edicion_hidraulica': True,
             'ecuacion_solidos_base_agua': 'API', 'ecuacion_solidos_base_aceite': 'API'}
    datos.update(cambios)
    return datos


class MonedaDeCobroTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA', moneda_simbolo='USD', moneda_secundaria='VES')

    def test_por_defecto_cobra_en_la_moneda_principal(self):
        self.assertEqual(self.pozo.moneda_cobro, 'USD')
        self.assertEqual(self.pozo.tarifa(30, 1200), 30)

    def test_cobrando_en_la_segunda_moneda(self):
        self.pozo.cobrar_en_secundaria = True
        self.assertEqual(self.pozo.moneda_cobro, 'VES')
        self.assertEqual(self.pozo.tarifa(30, 1200), 1200)

    def test_sin_segunda_moneda_no_se_puede_cobrar_en_ella(self):
        form = GeneralSetupForm(configuracion(moneda_secundaria='', cobrar_en_secundaria=True), instance=self.pozo)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertFalse(form.save().cobrar_en_secundaria)

    def test_la_segunda_moneda_debe_ser_distinta(self):
        form = GeneralSetupForm(configuracion(moneda_secundaria='USD'), instance=self.pozo)
        self.assertFalse(form.is_valid())
        self.assertIn('moneda_secundaria', form.errors)

    def test_sin_reportes_se_puede_cambiar_la_moneda_de_cobro(self):
        form = GeneralSetupForm(configuracion(cobrar_en_secundaria=True), instance=self.pozo)
        self.assertTrue(form.is_valid(), form.errors)

    def test_con_reportes_la_moneda_de_cobro_queda_bloqueada(self):
        ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13))
        form = GeneralSetupForm(configuracion(cobrar_en_secundaria=True), instance=self.pozo)
        self.assertFalse(form.is_valid())
        self.assertIn('cobrar_en_secundaria', form.errors)

    def test_con_reportes_se_puede_corregir_el_nombre_de_la_moneda(self):
        ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13))
        form = GeneralSetupForm(configuracion(moneda_secundaria='BS'), instance=self.pozo)
        self.assertTrue(form.is_valid(), form.errors)


class TarifasEnCostosTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA', moneda_simbolo='USD', moneda_secundaria='VES')
        salmuera = Producto.objects.create(codigo='SALMUERA', descripcion='Salmuera 8.5', unidad='BBL')
        self.producto_id = salmuera.id
        ProductoActivoPozo.objects.create(pozo=self.pozo, producto=salmuera, unidad='BBL', unit_size=Decimal('1'),
                                          precio=Decimal('30'), precio_secundaria=Decimal('1200'))
        equipo = Equipo.objects.create(codigo='CENTRF', nombre='Centrífuga')
        self.equipo = EquipoActivoPozo.objects.create(
            pozo=self.pozo, equipo=equipo, numero_serie='S1', precio_renta=Decimal('500'),
            precio_standby=Decimal('250'), precio_renta_secundaria=Decimal('20000'),
            precio_standby_secundaria=Decimal('10000'))
        malla = MallaZaranda.objects.create(codigo='M170', descripcion='Malla 170', mesh_size=170)
        self.malla = MallaActivaPozo.objects.create(pozo=self.pozo, malla=malla, precio=Decimal('100'),
                                                    precio_secundaria=Decimal('4000'),
                                                    descuento_porcentaje=Decimal('10'))

    def cobrar_en_secundaria(self):
        self.pozo.cobrar_en_secundaria = True
        self.pozo.save()
        self.equipo.refresh_from_db()
        self.malla.refresh_from_db()

    def test_productos_en_moneda_principal(self):
        self.assertEqual(_productos_pozo(self.pozo)[self.producto_id]['precio'], 30)

    def test_productos_en_segunda_moneda(self):
        self.cobrar_en_secundaria()
        self.assertEqual(_productos_pozo(self.pozo)[self.producto_id]['precio'], 1200)

    def test_equipos_en_cada_moneda(self):
        self.assertEqual(_tarifa_actual(self.equipo, UsoEquipoDia.COBRO_STANDBY), 250)
        self.cobrar_en_secundaria()
        self.assertEqual(_tarifa_actual(self.equipo, UsoEquipoDia.COBRO_STANDBY), 10000)
        self.assertEqual(_tarifa_actual(self.equipo, UsoEquipoDia.COBRO_SIN), 0)

    def test_mallas_en_cada_moneda_con_descuento(self):
        self.assertEqual(_precio_neto(self.malla), Decimal('90.00'))
        self.cobrar_en_secundaria()
        self.assertEqual(_precio_neto(self.malla), Decimal('3600.00'))

    def test_tarifas_secundarias_opcionales_en_formularios(self):
        equipo = EquipoActivoPozoForm({'equipo': self.equipo.equipo_id, 'numero_serie': 'S2',
                                       'precio_renta': '1', 'precio_standby': '1'})
        self.assertTrue(equipo.is_valid(), equipo.errors)
        self.assertEqual(equipo.cleaned_data['precio_renta_secundaria'], 0)
        malla = MallaActivaPozoForm({'malla': self.malla.malla_id, 'precio': '1', 'descuento_porcentaje': '0'})
        self.assertTrue(malla.is_valid(), malla.errors)
        self.assertEqual(malla.cleaned_data['precio_secundaria'], 0)
