"""
Pruebas de visualización del Operador y Taladro en el modelo Pozo y en el Hub
de Fluidos de Perforación y Equipos (daily_reports_hub).
"""

from django.test import TestCase, Client
from django.urls import reverse
from operaciones.models import Pozo, WellHeaderInfo


class OperadorHubTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_pozo_operador_y_taladro_sin_well_header_info(self):
        pozo = Pozo.objects.create(nombre="POZO SIN HEADER")
        self.assertEqual(pozo.operador, "")
        self.assertEqual(pozo.taladro, "")

    def test_pozo_operador_y_taladro_con_well_header_info(self):
        pozo = Pozo.objects.create(nombre="POZO CON HEADER")
        WellHeaderInfo.objects.create(
            pozo=pozo,
            operador="CHEVRON OPERACIONES",
            nombre_taladro="RIG-101"
        )
        self.assertEqual(pozo.operador, "CHEVRON OPERACIONES")
        self.assertEqual(pozo.taladro, "RIG-101")

    def test_daily_reports_hub_muestra_operador(self):
        pozo = Pozo.objects.create(nombre="POZO PRUEBA HUB")
        WellHeaderInfo.objects.create(
            pozo=pozo,
            operador="PDVSA PETROLEO",
            nombre_taladro="TALADRO PETROPIAR"
        )
        url = reverse('operaciones:daily_reports_hub', args=[pozo.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PDVSA PETROLEO")
        self.assertContains(response, "POZO PRUEBA HUB")

