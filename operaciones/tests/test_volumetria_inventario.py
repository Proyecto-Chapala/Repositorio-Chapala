"""
Inventario de productos por pozo (motor volumetria.simular).

Reglas del cliente (revisión de octubre 2026, docs/23_CORRECCIONES_REVISION_OCT.md y docs/26_REDISENO_INVENTARIO_Y_LODO_RECICLADO.md):
- Lo ingresado en el ticket es lo recibido (o devuelto) del día (revisión del 15-oct).
- El inicial del primer día es 0; desde el segundo día es el final del día anterior.
- final = inicial + recibido − devuelto − usado en fluidos (a mano) − usado en otro módulo (a mano) ± ajuste.
- Al día siguiente: recibido = 0 e inicial = final del día anterior.
- Agregar químicos es solo balance de volumen y concentraciones: no descuenta inventario ni genera costos.
"""

import json
from datetime import date
from decimal import Decimal

from django.test import SimpleTestCase, TestCase

from operaciones import volumetria as vol
from operaciones.volumetria import ErrorVolumetria
from operaciones.models import Pozo, Producto, ProductoActivoPozo
from operaciones.models_daily_reports import ReporteDiario
from operaciones.models_inventario import InventarioProductoDia

BARITA = 1
INGENIERO = 2
TANQUE_ACTIVO = {'numero': 1, 'grupo': vol.ACTIVO, 'real': None}


def ticket_recepcion(producto, cantidad_real, cantidad_ticket=None):
    return {'sentido': 'ENTRADA', 'detalles': [{
        'producto': producto, 'real': cantidad_real,
        'ticket': cantidad_real if cantidad_ticket is None else cantidad_ticket,
    }]}


def ticket_devolucion(producto, cantidad):
    return {'sentido': 'SALIDA', 'detalles': [{'producto': producto, 'real': cantidad, 'ticket': cantidad}]}


def agregar_quimico(secuencia, producto, cantidad, precio=0.0):
    return {'secuencia': secuencia, 'tipo': 'QUIMICOS', 'fosa': 1, 'aceite': 0, 'agua': 0,
            'productos': [{'producto': producto, 'cantidad': cantidad, 'unidad': 'LBS',
                           'tamano': 100, 'gravedad': 4.2, 'precio': precio, 'categoria': 1,
                           'concentracion': False}]}


def dia(id_, tickets=(), transacciones=(), manual=None):
    return {'id': id_, 'fecha_texto': f'dia {id_}', 'fosas': [TANQUE_ACTIVO], 'hoyo_fluido': 0,
            'tickets': list(tickets), 'transacciones': list(transacciones), 'manual': manual or {}}


def inventario_del_dia(dias, objetivo_id, producto=BARITA, servicios=None):
    return vol.simular(dias, objetivo_id, servicios=servicios)['inventario'][producto]


class InventarioPorPozoTests(SimpleTestCase):

    def test_el_ticket_de_recepcion_es_lo_recibido_del_dia(self):
        inventario = inventario_del_dia([dia(1, tickets=[ticket_recepcion(BARITA, 35)])], 1)
        self.assertEqual(inventario['inicial'], 0)
        self.assertEqual(inventario['recibido'], 35)
        self.assertEqual(inventario['final'], 35)

    def test_recepciones_posteriores_se_suman_y_el_uso_descuenta(self):
        manual = {BARITA: {'recibido': 100, 'fluido': 35}}
        dias = [
            dia(1, tickets=[ticket_recepcion(BARITA, 35)]),
            dia(2, manual=manual),
        ]
        inventario = inventario_del_dia(dias, 2)
        self.assertEqual(inventario['inicial'], 35)
        self.assertEqual(inventario['recibido'], 100)
        self.assertEqual(inventario['usado_fluido'], 35)
        self.assertEqual(inventario['final'], 100)

    def test_al_dia_siguiente_el_recibido_es_cero_y_el_inicial_es_el_final_anterior(self):
        dias = [dia(1, tickets=[ticket_recepcion(BARITA, 40)]), dia(2)]
        inventario = inventario_del_dia(dias, 2)
        self.assertEqual(inventario['recibido'], 0)
        self.assertEqual(inventario['inicial'], 40)
        self.assertEqual(inventario['final'], 40)

    def test_cadena_multidia_inicial_ticket_y_final_pasa_al_siguiente(self):
        dias = [
            dia(1, tickets=[ticket_recepcion(BARITA, 23)]),
            dia(2, manual={BARITA: {'recibido': 5, 'fluido': 3}}),
            dia(3, manual={BARITA: {'devuelto': 2, 'fluido': 5}}),
            dia(4),
        ]
        # Día 1: inicial 0 + 23 recibido por ticket, sin uso -> final 23
        inv1 = inventario_del_dia(dias, 1)
        self.assertEqual(inv1['inicial'], 0)
        self.assertEqual(inv1['recibido'], 23)
        self.assertEqual(inv1['final'], 23)

        # Día 2: inicial = final día 1 (23), + 5 recibido - 3 usado -> final 25
        inv2 = inventario_del_dia(dias, 2)
        self.assertEqual(inv2['inicial'], 23)
        self.assertEqual(inv2['recibido'], 5)
        self.assertEqual(inv2['usado_fluido'], 3)
        self.assertEqual(inv2['final'], 25)

        # Día 3: inicial = final día 2 (25), - 2 devuelto - 5 usado -> final 18
        inv3 = inventario_del_dia(dias, 3)
        self.assertEqual(inv3['inicial'], 25)
        self.assertEqual(inv3['devuelto'], 2)
        self.assertEqual(inv3['usado_fluido'], 5)
        self.assertEqual(inv3['final'], 18)

        # Día 4: inicial = final día 3 (18), sin movimientos -> final 18
        inv4 = inventario_del_dia(dias, 4)
        self.assertEqual(inv4['inicial'], 18)
        self.assertEqual(inv4['final'], 18)

    def test_ticket_posterior_se_suma_como_recibido_sin_alterar_el_inicial(self):
        dias = [
            dia(1, tickets=[ticket_recepcion(BARITA, 10)]),
            dia(2, tickets=[ticket_recepcion(BARITA, 6)]),
        ]
        inv1 = inventario_del_dia(dias, 1)
        self.assertEqual(inv1['inicial'], 0)
        self.assertEqual(inv1['final'], 10)

        # Día 2: inicial = final del día 1 (10); el ticket nuevo es lo recibido -> final 16
        inv2 = inventario_del_dia(dias, 2)
        self.assertEqual(inv2['inicial'], 10)
        self.assertEqual(inv2['recibido'], 6)
        self.assertEqual(inv2['final'], 16)

    def test_el_ticket_de_devolucion_es_lo_devuelto_del_dia(self):
        dias = [dia(1, tickets=[ticket_recepcion(BARITA, 10)]), dia(2, tickets=[ticket_devolucion(BARITA, 4)])]
        inv2 = inventario_del_dia(dias, 2)
        self.assertEqual(inv2['devuelto'], 4)
        self.assertEqual(inv2['final'], 6)

    def test_formula_completa_del_final(self):
        manual = {BARITA: {'recibido': 50, 'devuelto': 10, 'fluido': 20, 'otro': 5, 'ajuste': 2, 'precio': 0, 'categoria': 1}}
        dias = [dia(1, tickets=[ticket_recepcion(BARITA, 50)], manual=manual)]
        inventario = inventario_del_dia(dias, 1)
        # 0 + 50 (ticket) + 50 (rec manual) − 10 (dev manual) − 20 − 5 + 2 = 67
        self.assertEqual(inventario['inicial'], 0)
        self.assertEqual(inventario['recibido'], 100)
        self.assertEqual(inventario['devuelto'], 10)
        self.assertEqual(inventario['final'], 67)

    def test_la_cantidad_real_manda_sobre_la_del_ticket(self):
        dias = [dia(1, tickets=[ticket_recepcion(BARITA, cantidad_real=25, cantidad_ticket=30)])]
        inventario = inventario_del_dia(dias, 1)
        self.assertEqual(inventario['recibido'], 30)
        self.assertEqual(inventario['recibido_ticket'], 30)
        self.assertEqual(inventario['final'], 30)

    def test_usar_sin_haber_recibido_se_rechaza(self):
        manual = {BARITA: {'fluido': 10}}
        dias = [dia(1, manual=manual)]
        with self.assertRaisesMessage(ErrorVolumetria, 'Registra primero el ticket de recepción'):
            vol.simular(dias, 1)

    def test_usado_en_otro_modulo_descuenta_y_genera_costo(self):
        manual = {BARITA: {'otro': 4, 'ajuste': 0, 'precio': 10, 'categoria': 1}}
        dias = [dia(1, tickets=[ticket_recepcion(BARITA, 10)], manual=manual)]
        inventario = inventario_del_dia(dias, 1)
        self.assertEqual(inventario['final'], 6)
        self.assertEqual(inventario['costo_diario'], 40)

    def test_los_servicios_solo_generan_costo_sin_existencia(self):
        manual = {INGENIERO: {'otro': 1, 'ajuste': 0, 'precio': 500, 'categoria': 2}}
        inventario = inventario_del_dia([dia(1, manual=manual)], 1, producto=INGENIERO,
                                        servicios={INGENIERO})
        self.assertEqual(inventario['final'], 0)
        self.assertEqual(inventario['costo_diario'], 500)

    def test_acumulados_por_columna_se_suman_en_cada_dia(self):
        m1 = {BARITA: {'recibido': 50, 'fluido': 10, 'otro': 3, 'ajuste': 0, 'precio': 10, 'categoria': 1}}
        m2 = {BARITA: {'recibido': 20, 'devuelto': 4, 'fluido': 5, 'otro': 2, 'ajuste': 0, 'precio': 10, 'categoria': 1}}
        dias = [
            dia(1, manual=m1),
            dia(2, manual=m2),
        ]
        inv_dia1 = inventario_del_dia(dias, 1)
        self.assertEqual(inv_dia1['usado_fluido_acum'], 10)
        self.assertEqual(inv_dia1['usado_otro_acum'], 3)
        self.assertEqual(inv_dia1['usado_acum'], 13)
        self.assertEqual(inv_dia1['recibido_acum'], 50)
        self.assertEqual(inv_dia1['devuelto_acum'], 0)

        inv_dia2 = inventario_del_dia(dias, 2)
        self.assertEqual(inv_dia2['usado_fluido_acum'], 15)
        self.assertEqual(inv_dia2['usado_otro_acum'], 5)
        self.assertEqual(inv_dia2['usado_acum'], 20)
        self.assertEqual(inv_dia2['recibido_acum'], 70)
        self.assertEqual(inv_dia2['devuelto_acum'], 4)


class InicialManualTests(SimpleTestCase):

    def test_el_inicial_manual_reemplaza_al_final_del_dia_anterior(self):
        manual = {BARITA: {'inicial': 50, 'fluido': 20, 'otro': 0, 'ajuste': 0, 'precio': 0, 'categoria': 1}}
        dias = [dia(1, tickets=[ticket_recepcion(BARITA, 5)], manual=manual)]
        inventario = inventario_del_dia(dias, 1)
        self.assertEqual(inventario['inicial'], 50)
        self.assertEqual(inventario['inicial_auto'], 0)
        self.assertEqual(inventario['final'], 35)   # 50 + 5 (ticket) − 20

    def test_el_inicial_manual_permite_usar_sin_ticket(self):
        manual = {BARITA: {'inicial': 30, 'fluido': 10, 'otro': 0, 'ajuste': 0, 'precio': 0, 'categoria': 1}}
        inventario = inventario_del_dia([dia(1, manual=manual)], 1)
        self.assertEqual(inventario['final'], 20)

    def test_el_dia_siguiente_parte_del_final_con_el_inicial_manual(self):
        manual = {BARITA: {'inicial': 30, 'otro': 0, 'ajuste': 0, 'precio': 0, 'categoria': 1}}
        inventario = inventario_del_dia([dia(1, manual=manual), dia(2)], 2)
        self.assertEqual(inventario['inicial'], 30)


class QuimicosSeparadosDeInventarioTests(SimpleTestCase):
    """
    Regla nueva Parte C: Agregar químicos es solo balance de volumen y concentraciones.
    El inventario y los costos se gestionan a mano.
    """

    def test_agregar_quimicos_suma_volumen_y_no_toca_inventario_ni_costo(self):
        vol_esperado = 1000 / (350 * 4.2)
        dias = [dia(1, tickets=[ticket_recepcion(BARITA, 20)], transacciones=[agregar_quimico(1, BARITA, 10, precio=50)])]
        sim = vol.simular(dias, 1)
        self.assertAlmostEqual(sim['flujos'][vol.ACTIVO]['quimicos'], vol_esperado)
        inv = sim['inventario'][BARITA]
        self.assertEqual(inv['inicial'], 0)
        self.assertEqual(inv['recibido'], 20)
        self.assertEqual(inv['usado_dia'], 0)
        self.assertEqual(inv['costo_diario'], 0)
        self.assertEqual(inv['final'], 20)

    def test_agregar_quimicos_sin_existencia_no_se_rechaza(self):
        dias = [dia(1, transacciones=[agregar_quimico(1, BARITA, 10)])]
        sim = vol.simular(dias, 1)
        self.assertTrue(sim['flujos'][vol.ACTIVO]['quimicos'] > 0)

    def test_consumo_manual_fluido_y_otro_calcula_costo_y_final(self):
        manual = {BARITA: {'fluido': 4, 'otro': 1, 'precio': 10, 'categoria': 1}}
        inv = inventario_del_dia([dia(1, tickets=[ticket_recepcion(BARITA, 20)], manual=manual)], 1)
        self.assertEqual(inv['final'], 15)
        self.assertEqual(inv['usado_dia'], 5)
        self.assertEqual(inv['costo_diario'], 50)

    def test_fluido_manual_negativo_lanza_error(self):
        manual = {BARITA: {'fluido': 15, 'precio': 10}}
        dias = [dia(1, tickets=[ticket_recepcion(BARITA, 10)], manual=manual)]
        with self.assertRaisesMessage(ErrorVolumetria, 'queda en -5'):
            vol.simular(dias, 1)


class GuardarUsadoFluidoApiTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO INVENTARIO')
        self.reporte = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13))
        self.producto = Producto.objects.create(codigo='BAR', descripcion='Barita', unidad='SACO')
        self.activo = ProductoActivoPozo.objects.create(pozo=self.pozo, producto=self.producto, unidad='SACO', precio=Decimal('20'))
        self.servicio = Producto.objects.create(codigo='ING', descripcion='Ingeniero', unidad='')
        self.activo_serv = ProductoActivoPozo.objects.create(pozo=self.pozo, producto=self.servicio, unidad='', precio=Decimal('500'))
        self.url = f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/volumetria/guardar/'

    def test_guardar_persiste_usado_fluido_en_producto_y_cero_en_servicio(self):
        cuerpo = {
            'inventario': [
                {'producto_id': self.producto.id, 'inicial_manual': 20, 'usado_fluido': 15},
                {'producto_id': self.servicio.id, 'usado_fluido': 10, 'usado_otro': 1},
            ]
        }
        resp = self.client.post(self.url, json.dumps(cuerpo), content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.json())

        inv_prod = InventarioProductoDia.objects.get(reporte=self.reporte, producto_id=self.producto.id)
        self.assertEqual(inv_prod.usado_fluido, Decimal('15.000'))

        inv_serv = InventarioProductoDia.objects.get(reporte=self.reporte, producto_id=self.servicio.id)
        self.assertEqual(inv_serv.usado_fluido, Decimal('0.000'))

    def test_guardar_persiste_recibido_y_devuelto_manual(self):
        cuerpo = {
            'inventario': [
                {'producto_id': self.producto.id, 'recibido': 50, 'devuelto': 5, 'usado_fluido': 10},
                {'producto_id': self.servicio.id, 'recibido': 10, 'devuelto': 2},
            ]
        }
        resp = self.client.post(self.url, json.dumps(cuerpo), content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.json())
        inv_prod = InventarioProductoDia.objects.get(reporte=self.reporte, producto_id=self.producto.id)
        self.assertEqual(inv_prod.recibido, Decimal('50.000'))
        self.assertEqual(inv_prod.devuelto, Decimal('5.000'))
        self.assertEqual(inv_prod.usado_fluido, Decimal('10.000'))
        # En servicios no se guarda recibido ni devuelto
        inv_serv = InventarioProductoDia.objects.filter(reporte=self.reporte, producto_id=self.servicio.id).first()
        self.assertIsNone(inv_serv)


class InventarioExcelYRecapTests(TestCase):
    """
    Verifica que el consumo de inventario escrito a mano (usado_fluido) se refleje
    correctamente en la hoja de inventario del Excel diario (usado 4, costo 40)
    y en el recap del pozo (40 en químicos).
    """

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO EXCEL RECAP')
        self.producto = Producto.objects.create(codigo='BAR', descripcion='Barita', unidad='SACO')
        ProductoActivoPozo.objects.create(
            pozo=self.pozo, producto=self.producto, unidad='SACO',
            precio=Decimal('10.00'), codigo_costo_diario=1,
        )
        self.reporte = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13))
        InventarioProductoDia.objects.create(
            reporte=self.reporte, producto=self.producto, inicial=Decimal('20.00'),
            usado_fluido=Decimal('4.00'), precio=Decimal('10.00'), categoria_costo=1,
        )

    def test_excel_diario_hoja_inventario_muestra_usado_y_costo(self):
        import io
        import openpyxl
        from operaciones.reporte_excel import generar_reporte_excel
        contenido, _ = generar_reporte_excel(self.pozo, self.reporte)
        wb = openpyxl.load_workbook(io.BytesIO(contenido))
        self.assertIn('Inv Quimico (completo)', wb.sheetnames)
        ws = wb['Inv Quimico (completo)']
        self.assertEqual(ws['A11'].value, 'Barita')
        self.assertEqual(ws['F11'].value, 4.0)
        self.assertEqual(ws['M11'].value, 40.0)
        self.assertEqual(ws['F7'].value, 40.0)

    def test_recap_suma_quimicos(self):
        from operaciones.recap_pozo import datos_recap
        costos = datos_recap(self.pozo)['costos']
        self.assertEqual(costos['quimicos'], 40.0)

