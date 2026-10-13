"""
Inventario de productos por pozo (motor volumetria.simular).

Reglas del cliente (revisión de octubre 2026, docs/23_CORRECCIONES_REVISION_OCT.md):
- El inicial sale de lo recibido por ticket; cada recepción nueva se suma.
- final = inicial + recibido − devuelto − usado en fluidos − usado en otro módulo ± ajuste.
- Al día siguiente: recibido = 0 e inicial = final del día anterior.
"""

from django.test import SimpleTestCase

from operaciones import volumetria as vol
from operaciones.volumetria import ErrorVolumetria

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
            'productos': [{'producto': producto, 'cantidad': cantidad, 'unidad': 'SACO',
                           'tamano': 100, 'gravedad': 4.2, 'precio': precio, 'categoria': 1,
                           'concentracion': False}]}


def dia(id_, tickets=(), transacciones=(), manual=None):
    return {'id': id_, 'fecha_texto': f'dia {id_}', 'fosas': [TANQUE_ACTIVO], 'hoyo_fluido': 0,
            'tickets': list(tickets), 'transacciones': list(transacciones), 'manual': manual or {}}


def inventario_del_dia(dias, objetivo_id, producto=BARITA, servicios=None):
    return vol.simular(dias, objetivo_id, servicios=servicios)['inventario'][producto]


class InventarioPorPozoTests(SimpleTestCase):

    def test_la_primera_recepcion_es_la_existencia_inicial_del_pozo(self):
        inventario = inventario_del_dia([dia(1, tickets=[ticket_recepcion(BARITA, 35)])], 1)
        self.assertEqual(inventario['inicial'], 0)
        self.assertEqual(inventario['recibido'], 35)
        self.assertEqual(inventario['final'], 35)

    def test_recepciones_posteriores_se_suman_y_el_uso_descuenta(self):
        dias = [
            dia(1, tickets=[ticket_recepcion(BARITA, 35)]),
            dia(2, tickets=[ticket_recepcion(BARITA, 100)], transacciones=[agregar_quimico(1, BARITA, 35)]),
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

    def test_formula_completa_del_final(self):
        manual = {BARITA: {'otro': 5, 'ajuste': 2, 'precio': 0, 'categoria': 1}}
        dias = [dia(1, tickets=[ticket_recepcion(BARITA, 100), ticket_devolucion(BARITA, 10)],
                    transacciones=[agregar_quimico(1, BARITA, 20)], manual=manual)]
        inventario = inventario_del_dia(dias, 1)
        # 0 + 100 − 10 − 20 − 5 + 2
        self.assertEqual(inventario['final'], 67)

    def test_la_cantidad_real_manda_sobre_la_del_ticket(self):
        dias = [dia(1, tickets=[ticket_recepcion(BARITA, cantidad_real=25, cantidad_ticket=30)])]
        inventario = inventario_del_dia(dias, 1)
        self.assertEqual(inventario['recibido'], 25)
        self.assertEqual(inventario['recibido_ticket'], 30)
        self.assertEqual(inventario['final'], 25)

    def test_usar_sin_haber_recibido_se_rechaza(self):
        dias = [dia(1, transacciones=[agregar_quimico(1, BARITA, 10)])]
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


class InicialManualTests(SimpleTestCase):

    def test_el_inicial_manual_reemplaza_al_final_del_dia_anterior(self):
        manual = {BARITA: {'inicial': 50, 'otro': 0, 'ajuste': 0, 'precio': 0, 'categoria': 1}}
        dias = [dia(1, tickets=[ticket_recepcion(BARITA, 5)], transacciones=[agregar_quimico(1, BARITA, 20)], manual=manual)]
        inventario = inventario_del_dia(dias, 1)
        self.assertEqual(inventario['inicial'], 50)
        self.assertEqual(inventario['inicial_auto'], 0)
        self.assertEqual(inventario['final'], 35)   # 50 + 5 − 20

    def test_el_inicial_manual_permite_usar_sin_ticket(self):
        manual = {BARITA: {'inicial': 30, 'otro': 0, 'ajuste': 0, 'precio': 0, 'categoria': 1}}
        inventario = inventario_del_dia([dia(1, transacciones=[agregar_quimico(1, BARITA, 10)], manual=manual)], 1)
        self.assertEqual(inventario['final'], 20)

    def test_el_dia_siguiente_parte_del_final_con_el_inicial_manual(self):
        manual = {BARITA: {'inicial': 30, 'otro': 0, 'ajuste': 0, 'precio': 0, 'categoria': 1}}
        inventario = inventario_del_dia([dia(1, manual=manual), dia(2)], 2)
        self.assertEqual(inventario['inicial'], 30)
