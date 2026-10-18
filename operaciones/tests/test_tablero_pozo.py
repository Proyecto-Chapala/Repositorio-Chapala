"""
Tablero del pozo y lista de pozos (diseño técnico, rama refactorizacion_ui).

El tablero muestra el último reporte, los últimos reportes con su Excel y el avance
de la configuración; la lista de pozos ordena por el reporte más reciente.
"""

from datetime import date

from django.test import TestCase
from django.urls import reverse

from operaciones.models import Pozo, ReporteDiario
from operaciones.navegacion import estado_configuracion


class TableroPozoTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA', estado='ACTIVO', spud_date_completado=True)
        self.reporte = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13),
                                                    profundidad_actual=8450)

    def test_muestra_el_ultimo_reporte_con_su_excel(self):
        html = self.client.get(reverse('operaciones:pozo_main', args=[self.pozo.pk])).content.decode()
        self.assertIn('13/10/2026', html)
        self.assertRegex(html, r'8\D?450<small>ft MD')
        self.assertIn(reverse('operaciones:reporte_diario_excel', args=[self.pozo.pk, self.reporte.pk]), html)

    def test_avance_de_configuracion_cuenta_solo_las_pantallas_medibles(self):
        pantallas = estado_configuracion(self.pozo)
        self.assertEqual(len(pantallas), 8)
        medibles = [p for p in pantallas if p['lista'] is not None]
        self.assertEqual(len(medibles), 6)
        self.assertFalse(any(p['lista'] for p in medibles))

    def test_pozo_sin_reportes_invita_a_crear_el_primero(self):
        self.reporte.delete()
        html = self.client.get(reverse('operaciones:pozo_main', args=[self.pozo.pk])).content.decode()
        self.assertIn('Crea el primer reporte', html)


class ListaPozosTests(TestCase):

    def test_tabla_ordenada_por_el_reporte_mas_reciente(self):
        antiguo = Pozo.objects.create(nombre='AAA ANTIGUO', estado='ACTIVO')
        reciente = Pozo.objects.create(nombre='ZZZ RECIENTE', estado='ACTIVO')
        ReporteDiario.objects.create(pozo=antiguo, fecha=date(2026, 9, 1))
        ReporteDiario.objects.create(pozo=reciente, fecha=date(2026, 10, 17))
        html = self.client.get(reverse('operaciones:pozos_list')).content.decode()
        tabla = html[html.index('id="tablaPozos"'):]
        self.assertLess(tabla.index('ZZZ RECIENTE'), tabla.index('AAA ANTIGUO'))

    def test_sin_pozos_invita_a_crear_el_primero(self):
        html = self.client.get(reverse('operaciones:pozos_list')).content.decode()
        self.assertIn('Crea tu primer pozo', html)
