"""
Pruebas de integridad para ciclo de vida de pozos y propiedades de lodo (Parte 10).
- Colisión al restaurar pozo desde la papelera.
- Rechazo de cierre para pozos en BORRADOR.
- Validación física y transaccionalidad atómica en api_mud_properties_guardar.
"""

import json
from datetime import date
from django.test import TestCase

from operaciones.models import Pozo
from operaciones.models_daily_reports import (
    ReporteDiario, ReporteDiarioMudCheck, ReporteDiarioMudConfig
)


class PozoLifecycleAndMudIntegrityTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(
            nombre='POZO TEST PARTE 10',
            estado='ACTIVO',
            spud_date_completado=True,
        )
        self.reporte = ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 20),
            tipo_lodo='WBM',
        )

    # -------------------------------------------------------------------------
    # 1. Restaurar pozo y prevención de colisiones
    # -------------------------------------------------------------------------

    def test_restaurar_pozo_sin_colision_exitoso(self):
        self.pozo.enviar_a_papelera()
        self.assertFalse(Pozo.objects.filter(pk=self.pozo.pk).exists())
        self.assertTrue(Pozo.todos.filter(pk=self.pozo.pk, eliminado_en__isnull=False).exists())

        resp = self.client.post(f'/api/pozos/{self.pozo.pk}/restaurar/')
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['success'])
        self.assertTrue(datos['ok'])
        self.pozo.refresh_from_db()
        self.assertIsNone(self.pozo.eliminado_en)
        self.assertTrue(Pozo.objects.filter(pk=self.pozo.pk).exists())

    def test_restaurar_pozo_con_colision_nombre_activo_devuelve_400(self):
        self.pozo.enviar_a_papelera()
        # En SQLite el índice UNIQUE es case-sensitive a nivel tabla, pero nuestra lógica
        # de negocio es case-insensitive (__iexact). Si existe un pozo activo con diferente casing,
        # la restauración se bloquea de forma segura antes de corromper la unicidad en la UI.
        Pozo.todos.create(
            nombre='pozo test parte 10',
            estado='ACTIVO',
            spud_date_completado=True,
        )

        resp = self.client.post(f'/api/pozos/{self.pozo.pk}/restaurar/')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['success'])
        self.assertFalse(datos['ok'])
        self.assertIn("ya existe un pozo activo o cerrado con el nombre", datos['error'])

    # -------------------------------------------------------------------------
    # 2. Cierre de pozos: solo permitido si estado == ACTIVO
    # -------------------------------------------------------------------------

    def test_cerrar_pozo_en_borrador_devuelve_400_ajax(self):
        pozo_borrador = Pozo.objects.create(
            nombre='POZO EN CREACION',
            estado='BORRADOR',
            spud_date_completado=False,
        )

        resp = self.client.post(
            f'/api/pozos/{pozo_borrador.pk}/cerrar/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['success'])
        self.assertFalse(datos['ok'])
        self.assertIn("Solo se pueden cerrar pozos que se encuentren en estado ACTIVO", datos['error'])
        pozo_borrador.refresh_from_db()
        self.assertEqual(pozo_borrador.estado, 'BORRADOR')

    def test_cerrar_pozo_en_borrador_no_ajax_redirecciona_con_error(self):
        pozo_borrador = Pozo.objects.create(
            nombre='POZO EN CREACION 2',
            estado='BORRADOR',
            spud_date_completado=False,
        )

        resp = self.client.post(f'/api/pozos/{pozo_borrador.pk}/cerrar/')
        self.assertEqual(resp.status_code, 302)
        pozo_borrador.refresh_from_db()
        self.assertEqual(pozo_borrador.estado, 'BORRADOR')

    # -------------------------------------------------------------------------
    # 3. Propiedades de Lodo: Guardado válido y cálculos automáticos
    # -------------------------------------------------------------------------

    def test_mud_properties_guardar_valido(self):
        payload = {
            'config': {
                'sg_base_oil': 0.84,
                'sg_weight_material': 4.20,
                'sg_drill_solids': 2.60,
                'is_weighted': True,
            },
            'checks': [
                {
                    'check_number': 1,
                    'depth': 5000.0,
                    'tvd': 4800.0,
                    'mud_weight': 10.5,
                    'mw_temp': 120.0,
                    'funnel_viscosity': 45.0,
                    'r600': 50.0,
                    'r300': 30.0,
                    'gel_10s': 4.0,
                    'gel_10m': 12.0,
                    'solids_pct': 15.0,
                    'water_pct': 85.0,
                    'ph': 9.5,
                }
            ],
            'primary_check_number': 1,
            'extra_values': [],
        }

        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/mud-properties/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(datos['success'])

        # Verificar base de datos
        check1 = ReporteDiarioMudCheck.objects.get(reporte=self.reporte, check_number=1)
        self.assertEqual(check1.mud_weight, 10.5)
        self.assertEqual(check1.pv, 20.0)  # r600 (50) - r300 (30)
        self.assertEqual(check1.yp, 10.0)  # r300 (30) - pv (20)
        self.assertEqual(check1.ph, 9.5)
        self.assertTrue(check1.is_primary)

    # -------------------------------------------------------------------------
    # 4. Propiedades de Lodo: Validación de límites físicos
    # -------------------------------------------------------------------------

    def test_mud_properties_rechaza_densidad_negativa(self):
        payload = {
            'checks': [
                {
                    'check_number': 1,
                    'mud_weight': -10.5,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/mud-properties/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn("no puede ser negativo", datos['error'])

    def test_mud_properties_rechaza_reologia_negativa(self):
        payload = {
            'checks': [
                {
                    'check_number': 1,
                    'r600': -15.0,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/mud-properties/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn("no puede ser negativo", datos['error'])

    def test_mud_properties_rechaza_retorta_porcentual_fuera_de_rango(self):
        payload = {
            'checks': [
                {
                    'check_number': 1,
                    'solids_pct': 105.0,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/mud-properties/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn("debe estar entre 0% y 100%", datos['error'])

    def test_mud_properties_rechaza_ph_fuera_de_escala(self):
        payload = {
            'checks': [
                {
                    'check_number': 1,
                    'ph': 15.0,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/mud-properties/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn("pH debe estar entre 0 y 14", datos['error'])

    def test_mud_properties_rechaza_config_sg_no_positiva(self):
        payload = {
            'config': {
                'sg_base_oil': -0.80,
            },
            'checks': []
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/mud-properties/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn("debe ser mayor a cero", datos['error'])

    def test_mud_properties_atomicidad_rollback_si_chequeo_falla(self):
        # Chequeo 1 válido, chequeo 2 con gel negativo
        payload = {
            'checks': [
                {
                    'check_number': 1,
                    'mud_weight': 12.0,
                },
                {
                    'check_number': 2,
                    'gel_10s': -5.0,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/mud-properties/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        # Rollback: ni el chequeo 1 ni el 2 deben haberse creado
        self.assertFalse(ReporteDiarioMudCheck.objects.filter(reporte=self.reporte).exists())

    def test_mud_properties_bloqueado_si_pozo_cerrado(self):
        self.pozo.estado = 'CERRADO'
        self.pozo.save()

        payload = {'checks': [{'check_number': 1, 'mud_weight': 10.0}]}
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/mud-properties/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn("cerrado", datos['error'])
