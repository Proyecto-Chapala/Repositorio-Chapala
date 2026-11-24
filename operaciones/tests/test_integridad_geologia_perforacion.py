"""
Pruebas de integridad transaccional y límites físicos para datos geológicos y de perforación:
- Formation Tops (WellFormationTop): atomicidad ante fallos, rechazo de profundidades negativas y porcentajes inválidos.
- Well Survey Stations (WellSurveyStation): atomicidad ante fallos, rechazo de MD negativo, inclinaciones fuera de [0, 180] y azimuts fuera de [0, 360).
- Bombas y Boquillas (Pumps / Bits): atomicidad ante fallos, rechazo de eficiencias fuera de [0, 100] y dimensiones negativas.
"""

from datetime import date
from decimal import Decimal
import json
from django.test import TestCase
from django.urls import reverse

from operaciones.models import Pozo
from operaciones.models_daily_reports import (
    ReporteDiario, WellFormationTop, WellSurveyStation,
    ReporteDiarioBomba, ReporteDiarioBoquilla, ReporteDiarioBitData
)


class IntegridadGeologiaPerforacionTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO TEST GEOLOGIA', estado='ACTIVO')
        self.reporte = ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 15),
            tipo_lodo='WBM',
            numero_reporte=1,
            profundidad_actual=5000.0,
        )

        # Crear datos iniciales preexistentes
        self.top_existente = WellFormationTop.objects.create(
            pozo=self.pozo,
            formation_top='TOPE INICIAL',
            depth_ft=1000.0,
            lithology='Lutita',
            porcentaje_arena=15.0
        )
        self.station_existente = WellSurveyStation.objects.create(
            pozo=self.pozo,
            estacion=1,
            md_ft=0.0,
            inclinacion_deg=0.0,
            azimut_deg=0.0,
            tvd_ft=0.0,
            dls_deg_100ft=0.0,
            seccion_vertical_ft=0.0
        )
        self.boquilla_existente = ReporteDiarioBoquilla.objects.create(
            reporte=self.reporte,
            size_32nds=14,
            cantidad=3
        )

    # =========================================================================
    # FORMATION TOPS
    # =========================================================================

    def test_guardar_formation_tops_valido(self):
        url = reverse('operaciones:api_formation_tops_guardar', args=[self.pozo.pk])
        payload = {
            'formation_tops': [
                {'formation_top': 'TOPE A', 'depth_ft': 1500, 'lithology': 'Arenisca', 'porcentaje_arena': 40},
                {'formation_top': 'TOPE B', 'depth_ft': 3000, 'lithology': 'Lutita', 'porcentaje_arena': 10},
            ]
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['ok'])
        self.assertEqual(self.pozo.formation_tops.count(), 2)

    def test_formation_top_profundidad_negativa_rechazado_preserva_existente(self):
        url = reverse('operaciones:api_formation_tops_guardar', args=[self.pozo.pk])
        payload = {
            'formation_tops': [
                {'formation_top': 'TOPE ERRONEO', 'depth_ft': -500, 'lithology': 'Lutita', 'porcentaje_arena': 10}
            ]
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('no puede ser negativa', resp.json()['error'])
        # La transacción no borró el tope previo
        self.assertTrue(WellFormationTop.objects.filter(pk=self.top_existente.pk).exists())

    def test_formation_top_porcentaje_arena_fuera_de_rango_rechazado(self):
        url = reverse('operaciones:api_formation_tops_guardar', args=[self.pozo.pk])
        payload = {
            'formation_tops': [
                {'formation_top': 'TOPE ARENA', 'depth_ft': 2000, 'lithology': 'Arenisca', 'porcentaje_arena': 120}
            ]
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('debe estar entre 0% y 100%', resp.json()['error'])
        self.assertTrue(WellFormationTop.objects.filter(pk=self.top_existente.pk).exists())

    # =========================================================================
    # WELL SURVEY STATIONS
    # =========================================================================

    def test_guardar_survey_valido(self):
        url = reverse('operaciones:api_well_survey_guardar', args=[self.pozo.pk])
        payload = {
            'estaciones': [
                {'estacion': 1, 'md_ft': 0, 'inclinacion_deg': 0, 'azimut_deg': 0, 'comentarios': ''},
                {'estacion': 2, 'md_ft': 1000, 'inclinacion_deg': 5, 'azimut_deg': 45, 'comentarios': 'KOP'},
            ],
            'vs_azimuth': 45.0
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertEqual(len(datos['estaciones']), 2)
        self.assertGreater(datos['ultimo_tvd'], 0)

    def test_survey_md_negativo_rechazado_preserva_existente(self):
        url = reverse('operaciones:api_well_survey_guardar', args=[self.pozo.pk])
        payload = {
            'estaciones': [
                {'estacion': 1, 'md_ft': -100, 'inclinacion_deg': 0, 'azimut_deg': 0}
            ]
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('no puede ser negativa', resp.json()['error'])
        self.assertTrue(WellSurveyStation.objects.filter(pk=self.station_existente.pk).exists())

    def test_survey_inclinacion_fuera_de_rango_rechazado(self):
        url = reverse('operaciones:api_well_survey_guardar', args=[self.pozo.pk])
        payload = {
            'estaciones': [
                {'estacion': 1, 'md_ft': 1000, 'inclinacion_deg': 195, 'azimut_deg': 50}
            ]
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('inclinación debe estar entre 0° y 180°', resp.json()['error'])
        self.assertTrue(WellSurveyStation.objects.filter(pk=self.station_existente.pk).exists())

    def test_survey_azimut_fuera_de_rango_rechazado(self):
        url = reverse('operaciones:api_well_survey_guardar', args=[self.pozo.pk])
        payload = {
            'estaciones': [
                {'estacion': 1, 'md_ft': 1000, 'inclinacion_deg': 10, 'azimut_deg': 365}
            ]
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('azimut debe estar entre 0° y 359.99°', resp.json()['error'])
        self.assertTrue(WellSurveyStation.objects.filter(pk=self.station_existente.pk).exists())

    # =========================================================================
    # PUMPS / BITS / BOQUILLAS
    # =========================================================================

    def test_pumps_eficiencia_invalida_rechazada(self):
        url = reverse('operaciones:api_pumps_bits_guardar', args=[self.pozo.pk, self.reporte.pk])
        payload = {
            'bombas': [
                {'numero_bomba': 1, 'eficiencia_pct': 115.0}
            ]
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('eficiencia debe estar entre 0% y 100%', resp.json()['error'])

    def test_pumps_dimensiones_negativas_rechazadas(self):
        url = reverse('operaciones:api_pumps_bits_guardar', args=[self.pozo.pk, self.reporte.pk])
        payload = {
            'bombas': [
                {'numero_bomba': 1, 'liner_diameter': -6.5}
            ]
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('diámetro de camisa no puede ser negativo', resp.json()['error'])

    def test_boquillas_negativas_rechazadas_preserva_existente(self):
        url = reverse('operaciones:api_pumps_bits_guardar', args=[self.pozo.pk, self.reporte.pk])
        payload = {
            'boquillas': [
                {'size_32nds': -14, 'cantidad': 3}
            ]
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('no pueden ser negativos', resp.json()['error'])
        self.assertTrue(ReporteDiarioBoquilla.objects.filter(pk=self.boquilla_existente.pk).exists())

