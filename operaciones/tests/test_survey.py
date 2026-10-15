"""
Pruebas de Trayectoria Direccional / Well Survey (Curvatura Mínima API).
- Amarre virtual en superficie (MD = 0) ante surveys que inician en MD > 0.
- Proyección de Sección Vertical sobre azimut específico y por defecto (distancia de cierre).
- Endpoint API de guardado y recálculo.
"""

from django.test import TestCase
from django.urls import reverse

from operaciones.models import Pozo
from operaciones.views_daily_reports import calcular_survey_curvatura_minima


class WellSurveyTests(TestCase):

    def test_survey_estacion_inicial_en_cero(self):
        raw = [
            {'md_ft': 0, 'inclinacion_deg': 0, 'azimut_deg': 0},
            {'md_ft': 1000, 'inclinacion_deg': 10, 'azimut_deg': 90},
        ]
        res = calcular_survey_curvatura_minima(raw)
        self.assertEqual(len(res), 2)
        # Estación 1 (superficie)
        self.assertEqual(res[0]['md_ft'], 0.0)
        self.assertEqual(res[0]['tvd_ft'], 0.0)
        self.assertEqual(res[0]['seccion_vertical_ft'], 0.0)
        # Estación 2 (1000 ft)
        self.assertAlmostEqual(res[1]['tvd_ft'], 994.9, places=0)
        self.assertAlmostEqual(res[1]['este_ft'], 87.0, places=0)
        self.assertAlmostEqual(res[1]['norte_ft'], 0.0, places=0)
        self.assertAlmostEqual(res[1]['seccion_vertical_ft'], 87.0, places=0)

    def test_survey_estacion_inicial_sin_cero_acumula_correctamente(self):
        # Usuario ingresa directamente a 1000 ft sin ingresar fila 0
        raw = [
            {'md_ft': 1000, 'inclinacion_deg': 10, 'azimut_deg': 90},
            {'md_ft': 2000, 'inclinacion_deg': 10, 'azimut_deg': 90},
        ]
        res = calcular_survey_curvatura_minima(raw)
        self.assertEqual(len(res), 2)
        # La estación 1 debe acumular desde superficie, no poner Norte y Este en 0
        self.assertGreater(res[0]['este_ft'], 80.0)
        self.assertAlmostEqual(res[0]['seccion_vertical_ft'], res[0]['este_ft'], places=1)
        # La estación 2 debe acumular sobre la estación 1
        self.assertGreater(res[1]['este_ft'], res[0]['este_ft'])

    def test_survey_proyeccion_seccion_vertical(self):
        raw = [
            {'md_ft': 0, 'inclinacion_deg': 0, 'azimut_deg': 0},
            {'md_ft': 1000, 'inclinacion_deg': 90, 'azimut_deg': 90}, # Se desvía hacia el Este
        ]
        # 1. Proyectado sobre Azimut 90° (en la misma dirección del pozo)
        res_90 = calcular_survey_curvatura_minima(raw, vs_azimuth=90.0)
        vs_90 = res_90[1]['seccion_vertical_ft']
        self.assertGreater(vs_90, 500.0)

        # 2. Proyectado sobre Azimut 0° (Norte, perpendicular al pozo)
        res_0 = calcular_survey_curvatura_minima(raw, vs_azimuth=0.0)
        vs_0 = res_0[1]['seccion_vertical_ft']
        self.assertAlmostEqual(vs_0, 0.0, places=1)

        # 3. Sin azimut (default distancia de cierre)
        res_none = calcular_survey_curvatura_minima(raw, vs_azimuth=None)
        self.assertAlmostEqual(res_none[1]['seccion_vertical_ft'], vs_90, places=1)

    def test_api_well_survey_guardar(self):
        pozo = Pozo.objects.create(nombre='POZO SURVEY TEST')
        url = reverse('operaciones:api_well_survey_guardar', kwargs={'pk': pozo.pk})
        payload = {
            'estaciones': [
                {'md_ft': 0, 'inclinacion_deg': 0, 'azimut_deg': 0, 'comentarios': 'Tie-in'},
                {'md_ft': 1500, 'inclinacion_deg': 5, 'azimut_deg': 45, 'comentarios': 'Survey 1'},
            ],
            'vs_azimuth': 45.0
        }
        resp = self.client.post(url, data=payload, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['ok'])
        self.assertEqual(len(data['estaciones']), 2)
        self.assertEqual(pozo.survey_stations.count(), 2)

