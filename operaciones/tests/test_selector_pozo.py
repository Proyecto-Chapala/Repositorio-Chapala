"""
Selector de pozo de la barra superior (docs/28_REDISENO_UI_TECNICO.md).

Al elegir otro pozo se abre la misma pantalla de ese pozo; desde un reporte diario,
los reportes del otro pozo. Fuera de las pantallas de un pozo no aparece.
"""

from datetime import date

from django.test import TestCase
from django.urls import reverse

from operaciones.models import Pozo, ReporteDiario


class SelectorPozoTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO A', estado='ACTIVO', spud_date_completado=True)
        self.otro = Pozo.objects.create(nombre='POZO B', estado='ACTIVO', spud_date_completado=True)

    def html(self, nombre_url, *args):
        return self.client.get(reverse(nombre_url, args=args)).content.decode()

    def test_desde_tanques_lleva_a_tanques_del_otro_pozo(self):
        html = self.html('operaciones:pits', self.pozo.pk)
        self.assertIn('id="selectorPozoBoton"', html)
        self.assertIn(f'href="{reverse("operaciones:pits", args=[self.otro.pk])}"', html)
        self.assertIn('<span class="migas-actual">Tanques</span>', html)

    def test_desde_un_reporte_lleva_a_los_reportes_del_otro_pozo(self):
        reporte = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 17))
        html = self.html('operaciones:reporte_diario_detalle', self.pozo.pk, reporte.pk)
        self.assertIn(f'href="{reverse("operaciones:daily_reports_hub", args=[self.otro.pk])}"', html)

    def test_marca_el_pozo_actual(self):
        html = self.html('operaciones:pozo_main', self.pozo.pk)
        actual = f'href="{reverse("operaciones:pozo_main", args=[self.pozo.pk])}" aria-selected="true"'
        self.assertIn(actual, html)

    def test_fuera_de_un_pozo_no_aparece(self):
        self.assertNotIn('id="selectorPozoBoton"', self.html('operaciones:pozos_list'))
