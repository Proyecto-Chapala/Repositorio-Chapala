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
        # Lo del ticket es lo recibido del día (el campo 'recibido' es solo lo escrito a mano).
        self.assertEqual(fila['inicial'], 0)
        self.assertEqual(fila['recibido_total'], 200)
        self.assertEqual(fila['recibido'], 0)
        self.assertEqual(fila['final'], 200)
        self.assertFalse(datos['tickets'][0]['tiene_diferencias'])

    def test_real_distinta_marca_diferencia_pero_no_cambia_el_inventario(self):
        datos = self._guardar_ticket(200, 190).json()
        fila = self._fila_barita(datos)
        self.assertEqual(fila['recibido_total'], 200)
        self.assertEqual(fila['final'], 200)
        self.assertTrue(datos['tickets'][0]['tiene_diferencias'])

    def test_solo_real_sin_segun_ticket_se_acepta_como_respaldo(self):
        respuesta = self._guardar_ticket('', 50)
        self.assertEqual(respuesta.status_code, 200)
        fila = self._fila_barita(respuesta.json())
        self.assertEqual(fila['recibido_total'], 50)

