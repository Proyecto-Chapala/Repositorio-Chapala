"""
Pruebas de integridad física y transaccionalidad atómica para Geometría de Sarta y Propiedades Extra (Parte 11).
- Validación de diámetros y longitudes de tramos de sarta (ID < OD, ID_junta < OD_junta).
- Transaccionalidad atómica y rollback en api_well_geometry_guardar.
- Validación de números y guardado atómico en api_propiedades_extra_guardar.
- Normalización de respuestas JSON en comentarios.
"""

import json
from datetime import date
from django.test import TestCase

from operaciones.models import Pozo
from operaciones.models_daily_reports import (
    ReporteDiario, TramoSarta, PropiedadExtraFluido, ReporteDiarioComentarios
)


class GeometriaSartaYPropiedadesExtraTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(
            nombre='POZO TEST PARTE 11',
            estado='ACTIVO',
            spud_date_completado=True,
        )
        self.reporte = ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 20),
            tipo_lodo='WBM',
            profundidad_actual=5000.0,
            pilot_hole_size_in=8.5,
            pilot_hole_depth_ft=4000.0,
        )

    # -------------------------------------------------------------------------
    # 1. Propiedades Extra de Fluidos
    # -------------------------------------------------------------------------

    def test_propiedades_extra_guardar_valido(self):
        payload = {
            'items': [
                {
                    'tipo_fluido': 'WBM',
                    'numero': 1,
                    'etiqueta': 'Salinidad KCl',
                    'unidad': 'mg/L',
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/propiedades-extra/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(datos['success'])
        self.assertEqual(datos['guardados'], 1)

        prop = PropiedadExtraFluido.objects.get(pozo=self.pozo, tipo_fluido='WBM', numero=1)
        self.assertEqual(prop.etiqueta, 'Salinidad KCl')
        self.assertEqual(prop.unidad, 'mg/L')

    def test_propiedades_extra_rechaza_numero_invalido(self):
        payload = {
            'items': [
                {
                    'tipo_fluido': 'WBM',
                    'numero': 'no_es_numero',
                    'etiqueta': 'Invalido',
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/propiedades-extra/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertFalse(datos['success'])
        self.assertIn("número de propiedad inválido", datos['error'])

    def test_propiedades_extra_elimina_al_enviar_vacio(self):
        PropiedadExtraFluido.objects.create(
            pozo=self.pozo, tipo_fluido='WBM', numero=1, etiqueta='Existente'
        )
        self.assertTrue(PropiedadExtraFluido.objects.filter(pozo=self.pozo, numero=1).exists())

        payload = {
            'items': [
                {
                    'tipo_fluido': 'WBM',
                    'numero': 1,
                    'etiqueta': '',
                    'unidad': '',
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/propiedades-extra/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(PropiedadExtraFluido.objects.filter(pozo=self.pozo, numero=1).exists())

    # -------------------------------------------------------------------------
    # 2. Geometría del Pozo y Sarta
    # -------------------------------------------------------------------------

    def test_well_geometry_guardar_valido(self):
        payload = {
            'pilot_hole_size_in': 9.875,
            'pilot_hole_depth_ft': 4500.0,
            'tramos': [
                {
                    'descripcion': 'Drill Pipe 5"',
                    'longitud_ft': 1500.0,
                    'od_in': 5.0,
                    'id_in': 4.276,
                    'tool_joint_od_in': 6.5,
                    'tool_joint_id_in': 3.75,
                    'tool_joint_length_in': 21.0,
                    'largo_tramo_ft': 31.0,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/well-geometry/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(datos['success'])

        self.reporte.refresh_from_db()
        self.assertEqual(self.reporte.pilot_hole_size_in, 9.875)
        self.assertEqual(self.reporte.tramos_sarta.count(), 1)
        tramo = self.reporte.tramos_sarta.first()
        self.assertEqual(tramo.od_in, 5.0)
        self.assertEqual(tramo.id_in, 4.276)

    def test_well_geometry_rechaza_longitud_negativa(self):
        payload = {
            'tramos': [
                {
                    'descripcion': 'Tubo',
                    'longitud_ft': -100.0,
                    'od_in': 5.0,
                    'id_in': 4.0,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/well-geometry/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn("no puede ser negativa", datos['error'])

    def test_well_geometry_rechaza_od_negativo(self):
        payload = {
            'tramos': [
                {
                    'descripcion': 'Tubo',
                    'longitud_ft': 100.0,
                    'od_in': -5.0,
                    'id_in': 4.0,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/well-geometry/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn("no puede ser negativo", datos['error'])

    def test_well_geometry_rechaza_id_mayor_o_igual_a_od(self):
        payload = {
            'tramos': [
                {
                    'descripcion': 'Tubo Imposible',
                    'longitud_ft': 100.0,
                    'od_in': 4.5,
                    'id_in': 5.0,  # ID mayor que OD
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/well-geometry/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn("debe ser menor que el diámetro exterior", datos['error'])

    def test_well_geometry_rechaza_junta_id_mayor_o_igual_a_od(self):
        payload = {
            'tramos': [
                {
                    'descripcion': 'Junta Invalida',
                    'longitud_ft': 100.0,
                    'od_in': 5.0,
                    'id_in': 4.0,
                    'tool_joint_od_in': 6.0,
                    'tool_joint_id_in': 6.5,  # TJ ID mayor que TJ OD
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/well-geometry/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn("el ID de junta", datos['error'])

    def test_well_geometry_rechaza_hoyo_piloto_negativo(self):
        payload = {
            'pilot_hole_size_in': -8.5,
            'tramos': []
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/well-geometry/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn("no pueden ser negativas", datos['error'])

    def test_well_geometry_atomicidad_rollback_si_sarta_falla(self):
        self.assertEqual(self.reporte.pilot_hole_size_in, 8.5)

        # Se intenta actualizar pilot_hole_size_in a 12.25 pero con sarta inválida
        payload = {
            'pilot_hole_size_in': 12.25,
            'tramos': [
                {
                    'descripcion': 'Tubo malo',
                    'longitud_ft': 100.0,
                    'od_in': 4.5,
                    'id_in': 5.0,  # Falla validación
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/well-geometry/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)

        # Comprobar que el reporte NO fue modificado parcialmente
        self.reporte.refresh_from_db()
        self.assertEqual(self.reporte.pilot_hole_size_in, 8.5)

    # -------------------------------------------------------------------------
    # 3. Comentarios
    # -------------------------------------------------------------------------

    def test_comentarios_guardar_valido(self):
        payload = {
            'spec_mud_weight': '9.5 - 10.0',
            'spec_viscosidad': '40 - 45',
            'spec_filtrado': '< 10',
            'mud_recap_remarks': 'Perforando sin novedades.',
            'remarks_and_treatment': 'Se agregaron 20 sacos de bentonita.',
            'remarks': 'Turno diurno normal.',
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/comentarios/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(datos['success'])

        com = ReporteDiarioComentarios.objects.get(reporte=self.reporte)
        self.assertEqual(com.spec_mud_weight, '9.5 - 10.0')
        self.assertEqual(com.mud_recap_remarks, 'Perforando sin novedades.')

    def test_reporte_propiedades_comentario_valido(self):
        payload = {'comentario': 'Comentario de reología matutina.'}
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/propiedades/comentario/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(datos['success'])

        com = ReporteDiarioComentarios.objects.get(reporte=self.reporte)
        self.assertEqual(com.comentario_propiedades, 'Comentario de reología matutina.')
