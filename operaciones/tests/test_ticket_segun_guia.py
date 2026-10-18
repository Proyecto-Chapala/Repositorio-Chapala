"""
El inventario del pozo usa la cantidad "según ticket" (la de la guía), tanto en recepción como en
devolución. La cantidad "real" es opcional y solo marca diferencias (docs/pruebas/19_TICKET_SEGUN_GUIA.md).
"""

import json
from datetime import date
from decimal import Decimal

from django.test import TestCase

from operaciones.models import Pozo, Producto, ProductoActivoPozo
from operaciones.models_control_solidos import TipoTicketMalla
from operaciones.models_daily_reports import ReporteDiario


class TicketSegunGuiaTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO GUIAS')
        self.reporte = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13))
        self.recepcion = TipoTicketMalla.objects.create(pozo=self.pozo, nombre='Recepción', sentido='ENTRADA')
        self.barita = Producto.objects.create(codigo='BARITA', descripcion='Barita', unidad='SACO')
        ProductoActivoPozo.objects.create(pozo=self.pozo, producto=self.barita, unidad='SACO', precio=Decimal('10'))
        self.base = f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/volumetria/'

    def _guardar_ticket(self, cantidad_ticket, cantidad_real=''):
        cuerpo = {'tipo_id': self.recepcion.id, 'numero': 'G-1',
                  'detalles': [{'producto_id': self.barita.id, 'cantidad_ticket': cantidad_ticket,
                                'cantidad_real': cantidad_real}]}
        return self.client.post(self.base + 'ticket/guardar/', json.dumps(cuerpo), content_type='application/json')

    def _fila_barita(self, datos):
        return next(r for r in datos['inventario'] if r['producto_id'] == self.barita.id)

    def test_solo_segun_ticket_entra_al_inventario_sin_diferencias(self):
        datos = self._guardar_ticket(200).json()
        self.assertTrue(datos['ok'])
        fila = self._fila_barita(datos)
        # Lo del ticket se plasma en el campo recibido (200), recibido_manual es 0, y el total es 200.
        self.assertEqual(fila['inicial'], 0)
        self.assertEqual(fila['recibido_total'], 200)
        self.assertEqual(fila['recibido'], 200)
        self.assertEqual(fila['recibido_manual'], 0)
        self.assertEqual(fila['final'], 200)
        self.assertFalse(datos['tickets'][0]['tiene_diferencias'])

    def test_real_distinta_marca_diferencia_pero_no_cambia_el_inventario(self):
        datos = self._guardar_ticket(200, 190).json()
        fila = self._fila_barita(datos)
        self.assertEqual(fila['recibido_total'], 200)
        self.assertEqual(fila['recibido'], 200)
        self.assertEqual(fila['final'], 200)
        self.assertTrue(datos['tickets'][0]['tiene_diferencias'])

    def test_solo_real_sin_segun_ticket_se_acepta_como_respaldo(self):
        respuesta = self._guardar_ticket('', 50)
        self.assertEqual(respuesta.status_code, 200)
        fila = self._fila_barita(respuesta.json())
        self.assertEqual(fila['recibido_total'], 50)
        self.assertEqual(fila['recibido'], 50)

    def test_guardar_inventario_con_ticket_no_duplica_y_admite_manual(self):
        # 1. Se registra un ticket de entrada de 200 sacos
        datos = self._guardar_ticket(200).json()
        fila = self._fila_barita(datos)
        self.assertEqual(fila['recibido'], 200)
        self.assertEqual(fila['final'], 200)

        # 2. Guardar la volumetría con el valor del campo (200) no duplica la existencia
        cuerpo = {
            'inventario': [
                {'producto_id': self.barita.id, 'recibido': 200, 'devuelto': 0}
            ]
        }
        resp = self.client.post(self.base + 'guardar/', json.dumps(cuerpo), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        datos_guardados = resp.json()
        fila = self._fila_barita(datos_guardados)
        self.assertEqual(fila['recibido'], 200)
        self.assertEqual(fila['recibido_manual'], 0)
        self.assertEqual(fila['recibido_total'], 200)
        self.assertEqual(fila['final'], 200)

        # 3. Si el usuario escribe 210 (200 de ticket + 10 adicionales a mano sin ticket)
        cuerpo['inventario'][0]['recibido'] = 210
        resp = self.client.post(self.base + 'guardar/', json.dumps(cuerpo), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        fila = self._fila_barita(resp.json())
        self.assertEqual(fila['recibido'], 210)
        self.assertEqual(fila['recibido_manual'], 10)
        self.assertEqual(fila['recibido_total'], 210)
        self.assertEqual(fila['final'], 210)

    def test_ticket_salida_devuelto_se_plasma_en_campo_y_no_duplica(self):
        salida = TipoTicketMalla.objects.create(pozo=self.pozo, nombre='Devolución', sentido='SALIDA')
        # Primero fijamos existencia inicial a 200 para poder devolver
        cuerpo_ini = {
            'inventario': [
                {'producto_id': self.barita.id, 'inicial_manual': 200}
            ]
        }
        self.client.post(self.base + 'guardar/', json.dumps(cuerpo_ini), content_type='application/json')

        # Se registra un ticket de salida de 30 sacos
        cuerpo_tk = {'tipo_id': salida.id, 'numero': 'S-1',
                     'detalles': [{'producto_id': self.barita.id, 'cantidad_ticket': 30, 'cantidad_real': ''}]}
        resp_tk = self.client.post(self.base + 'ticket/guardar/', json.dumps(cuerpo_tk), content_type='application/json')
        fila = self._fila_barita(resp_tk.json())
        self.assertEqual(fila['devuelto'], 30)
        self.assertEqual(fila['devuelto_total'], 30)
        self.assertEqual(fila['final'], 170)

        # Guardar inventario con 30 no duplica
        cuerpo_save = {
            'inventario': [
                {'producto_id': self.barita.id, 'inicial_manual': 200, 'devuelto': 30}
            ]
        }
        resp_save = self.client.post(self.base + 'guardar/', json.dumps(cuerpo_save), content_type='application/json')
        fila = self._fila_barita(resp_save.json())
        self.assertEqual(fila['devuelto'], 30)
        self.assertEqual(fila['devuelto_manual'], 0)
        self.assertEqual(fila['final'], 170)




