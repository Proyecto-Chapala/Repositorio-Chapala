"""
Panel "Reportes" de la barra lateral (docs/06_REPORTE_DIARIO_PESTANAS_1_A_5.md).

Lista cada pozo como "Reportes pozo X" con acceso directo a su historial de reportes,
primero el de reporte más reciente. Los pozos de la papelera no aparecen.
"""

from datetime import date

from django.test import TestCase
from django.urls import reverse

from operaciones.models import Pozo, ReporteDiario


class ReportesBarraLateralTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA')
        ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13))
        self.pozo_borrado = Pozo.objects.create(nombre='POZO BORRADO')
        self.pozo_borrado.enviar_a_papelera()

    def test_lista_los_pozos_con_enlace_a_sus_reportes(self):
        html = self.client.get(reverse('operaciones:pozos_list')).content.decode()
        self.assertIn('title="Reportes pozo POZO PRUEBA"', html)
        self.assertIn(f'href="{reverse("operaciones:daily_reports_hub", args=[self.pozo.pk])}"', html)
        self.assertIn('Último: 13/10/2026', html)
        self.assertNotIn('POZO BORRADO', html)

    def test_en_los_reportes_del_pozo_ese_pozo_queda_resaltado(self):
        html = self.client.get(reverse('operaciones:daily_reports_hub', args=[self.pozo.pk])).content.decode()
        self.assertIn('class="panel-reportes-item active"', html)

    def test_primero_el_pozo_con_el_reporte_mas_reciente(self):
        Pozo.objects.create(nombre='AAA SIN REPORTES')
        reciente = Pozo.objects.create(nombre='ZZZ RECIENTE')
        ReporteDiario.objects.create(pozo=reciente, fecha=date(2026, 10, 17))
        html = self.client.get(reverse('operaciones:pozos_list')).content.decode()
        posiciones = [html.index(f'title="Reportes pozo {nombre}"')
                      for nombre in ('ZZZ RECIENTE', 'POZO PRUEBA', 'AAA SIN REPORTES')]
        self.assertEqual(posiciones, sorted(posiciones))
