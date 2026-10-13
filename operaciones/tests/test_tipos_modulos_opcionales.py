"""
Tipos de datos de los módulos opcionales (docs/24_PAPELERA_Y_TIPOS_DE_DATOS.md):
las horas de las muestras se guardan como hora (no texto) y el costo del evento como dinero (Decimal).
"""

import json
from datetime import date, time
from decimal import Decimal

from django.test import SimpleTestCase, TestCase

from operaciones.models import EventoNoProgramado, Pozo, ReporteDiario
from operaciones.views_opcionales import _Rechazo, _hora, _hora_texto


class HoraMuestraTests(SimpleTestCase):

    def test_hora_valida(self):
        self.assertEqual(_hora('08:30', 'Hora'), time(8, 30))

    def test_vacia_es_nula(self):
        self.assertIsNone(_hora('', 'Hora'))
        self.assertEqual(_hora_texto(None), '')

    def test_hora_fuera_de_rango_se_rechaza(self):
        with self.assertRaises(_Rechazo):
            _hora('25:99', 'Hora')

    def test_se_muestra_como_hh_mm(self):
        self.assertEqual(_hora_texto(time(7, 5)), '07:05')


class CostoEventoTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA')
        self.reporte = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13))

    def test_el_costo_se_guarda_como_dinero_con_dos_decimales(self):
        respuesta = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/eventos/guardar/',
            json.dumps({'tipo_problema': 'Pérdida de circulación', 'costo': '1234.567'}),
            content_type='application/json')
        self.assertEqual(respuesta.status_code, 200, respuesta.json())
        self.assertEqual(EventoNoProgramado.objects.get().costo, Decimal('1234.57'))
        self.assertEqual(respuesta.json()['eventos'][0]['costo'], 1234.57)
