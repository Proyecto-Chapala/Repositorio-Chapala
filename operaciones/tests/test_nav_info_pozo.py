"""
Barra de navegación de Información del Pozo (docs/05_CONFIGURACION_POZO.md).

Cada pantalla de Información del Pozo muestra una barra con todas las demás y la
pantalla principal, marcando la actual.
"""

from django.test import TestCase
from django.urls import reverse

from operaciones.models import Pozo

PANTALLAS_INFO_POZO = [
    'well_header', 'general_setup', 'casing_intervals', 'loss_setup',
    'active_items', 'benchmark_setup', 'pits', 'equipment_properties_setup',
]


class NavInfoPozoTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA')

    def test_cada_pantalla_enlaza_a_las_demas_y_marca_la_actual(self):
        enlaces = [reverse(f'operaciones:{nombre}', args=[self.pozo.pk]) for nombre in PANTALLAS_INFO_POZO]
        principal = reverse('operaciones:pozo_main', args=[self.pozo.pk])
        for nombre, url_actual in zip(PANTALLAS_INFO_POZO, enlaces):
            with self.subTest(pantalla=nombre):
                html = self.client.get(url_actual).content.decode()
                self.assertIn('class="info-pozo-nav"', html)
                self.assertIn(f'href="{principal}"', html)
                for url in enlaces:
                    self.assertIn(f'href="{url}"', html)
                self.assertIn(f'href="{url_actual}" aria-current="page"', html)
                self.assertEqual(html.count('aria-current="page"'), 1)
