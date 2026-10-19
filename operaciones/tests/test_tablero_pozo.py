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

    def test_los_estaticos_de_la_base_llevan_version_contra_la_cache(self):
        html = self.client.get(reverse('operaciones:pozos_list')).content.decode()
        self.assertRegex(html, r'css/layout\.css\?v=\d+')
        self.assertRegex(html, r'js/app\.js\?v=\d+')

    def test_sin_pozos_invita_a_crear_el_primero(self):
        html = self.client.get(reverse('operaciones:pozos_list')).content.decode()
        self.assertIn('Crea tu primer pozo', html)


class CabeceraReporteTests(TestCase):

    def test_reporte_con_ubicacion_excel_y_ocho_pestanas(self):
        pozo = Pozo.objects.create(nombre='POZO PRUEBA', estado='ACTIVO', spud_date_completado=True)
        reporte = ReporteDiario.objects.create(pozo=pozo, fecha=date(2026, 10, 17))
        html = self.client.get(reverse('operaciones:reporte_diario_detalle', args=[pozo.pk, reporte.pk])).content.decode()
        self.assertEqual(html.count('role="tab"'), 8)
        self.assertIn('<span class="migas-actual dato">17/10/2026</span>', html)
        self.assertIn(reverse('operaciones:reporte_diario_excel', args=[pozo.pk, reporte.pk]), html)


class InventarioYCatalogosTests(TestCase):

    def test_hojas_de_estilo_con_version_contra_la_cache(self):
        for nombre_url in ('operaciones:index', 'operaciones:catalogos_maestros'):
            with self.subTest(pantalla=nombre_url):
                html = self.client.get(reverse(nombre_url)).content.decode()
                self.assertRegex(html, r'css/inventario\.css\?v=\d+')
                self.assertIn('class="modulo-cabecera"', html)


class EstilosEnLineaReporteTests(TestCase):
    """El reporte no lleva estilos en línea, salvo el estado que maneja el JavaScript."""

    PERMITIDOS = {'display:none;', 'width:0%;'}

    def test_solo_quedan_los_estilos_que_maneja_el_javascript(self):
        import re
        from pathlib import Path
        plantilla = Path(__file__).resolve().parents[1] / 'templates/operaciones/avances_19_sep/reporte_diario_detalle.html'
        estilos = set(re.findall(r'style="([^"]*)"', plantilla.read_text(encoding='utf-8')))
        self.assertEqual(estilos - self.PERMITIDOS, set())


class FuentesSinInternetTests(TestCase):
    """SmartMud.exe trabaja sin internet: las fuentes van dentro del proyecto."""

    def test_ninguna_plantilla_pide_fuentes_a_internet(self):
        from pathlib import Path
        plantillas = (Path(__file__).resolve().parents[1] / 'templates').rglob('*.html')
        externas = [p.name for p in plantillas if 'fonts.googleapis.com' in p.read_text(encoding='utf-8')]
        self.assertEqual(externas, [])

    def test_los_archivos_de_fuente_estan_en_el_proyecto(self):
        from django.contrib.staticfiles import finders
        for archivo in ('ibm-plex-sans-latin.woff2', 'jetbrains-mono-latin.woff2'):
            with self.subTest(archivo=archivo):
                self.assertIsNotNone(finders.find(f'operaciones/fonts/{archivo}'))
