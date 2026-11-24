import json
from datetime import date
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse

from operaciones.models import (
    Pozo, Equipo, MallaZaranda, EquipoActivoPozo, MallaActivaPozo,
    CategoriaPerdidaItem
)
from operaciones.models_daily_reports import ReporteDiario
from operaciones.models_control_solidos import TipoTicketMalla, UsoEquipoDia
from operaciones.models_opcionales import AnalisisSolidosEquipo, RetencionRecortes, EventoNoProgramado


class TestControlSolidosOpcionalesIntegridad(TestCase):
    def setUp(self):
        self.client = Client()
        self.pozo = Pozo.objects.create(
            nombre="POZO CONTROL SOLIDOS TEST",
            estado="ACTIVO",
            spud_date_completado=True,
            moneda_simbolo="USD",
        )
        CategoriaPerdidaItem.sembrar_estandar(self.pozo)
        self.reporte = ReporteDiario.objects.create(
            pozo=self.pozo,
            numero_reporte=1,
            fecha=date(2026, 10, 1),
            profundidad_actual=5000.0,
            tipo_lodo="WBM",
        )
        self.equipo = Equipo.objects.create(
            codigo="EQ-ZAR-01",
            nombre="Zaranda Primaria 1",
            tipo_equipo="ZARANDA",
            posiciones_malla=3,
        )
        self.equipo_activo = EquipoActivoPozo.objects.create(
            pozo=self.pozo,
            equipo=self.equipo,
            numero_serie="SN-ZAR-001",
            descripcion="Zaranda Primaria 1",
        )

    def test_api_control_solidos_detail_normalizado(self):
        url = reverse('operaciones:api_control_solidos_detail', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('ok'))
        self.assertTrue(data.get('success'))

    def test_api_tipo_ticket_malla_guardar_normalizado(self):
        url = reverse('operaciones:api_tipo_ticket_malla_guardar', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        # Error: nombre vacio
        res_err = self.client.post(url, data=json.dumps({'nombre': '', 'sentido': 'ENTRADA'}), content_type='application/json')
        self.assertEqual(res_err.status_code, 400)
        data_err = res_err.json()
        self.assertFalse(data_err.get('ok'))
        self.assertFalse(data_err.get('success'))

        # Valido
        res_val = self.client.post(url, data=json.dumps({'nombre': 'Envio de Campo', 'sentido': 'ENTRADA'}), content_type='application/json')
        self.assertEqual(res_val.status_code, 200)
        data_val = res_val.json()
        self.assertTrue(data_val.get('ok'))
        self.assertTrue(data_val.get('success'))

    def test_api_uso_equipos_guardar_normalizado(self):
        url = reverse('operaciones:api_uso_equipos_guardar', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        payload = {
            'equipos': [
                {
                    'serie': 'SN-ZAR-001',
                    'horas': 24.0,
                    'mud_on_cuttings': 5.0,
                    'porcentaje_recortes': 40.0,
                    'caudal_entrada_gpm': 450.0,
                    'densidad_entrada': 10.5,
                    'densidad_salida': 10.4,
                    'densidad_descarte': 18.0,
                    'cantidad_usada': 1.0,
                    'codigo_cobro': 'COMPLETO',
                    'es_fluidos': True,
                    'observaciones': 'Operando sin novedad'
                }
            ]
        }
        res = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('ok'))
        self.assertTrue(data.get('success'))

    def test_api_ife_get_y_post_normalizado(self):
        url = reverse('operaciones:api_ife', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        res_get = self.client.get(url)
        self.assertEqual(res_get.status_code, 200)
        self.assertTrue(res_get.json().get('ok'))
        self.assertTrue(res_get.json().get('success'))

        payload = {
            'fluidos_resumen': 'Resumen de fluidos OK',
            'fluidos_plan': 'Plan de fluidos OK',
            'solidos_resumen': 'Resumen solidos OK',
            'solidos_plan': 'Plan solidos OK',
        }
        res_post = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res_post.status_code, 200)
        self.assertTrue(res_post.json().get('ok'))
        self.assertTrue(res_post.json().get('success'))

    def test_api_muestras_retencion_limites_fisicos(self):
        url_guardar = reverse('operaciones:api_muestras_guardar', kwargs={
            'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk, 'clave': 'retencion'
        })

        base_body = {
            'equipo_serie': 'SN-ZAR-001',
            'hora_inicio': '08:00',
            'hora_fin': '09:00',
            'orden': 1,
            'profundidad_ft': 5000,
        }

        # Invalido 1: celda_humedo < celda_vacia
        inv1 = dict(base_body, datos={
            'celda_vacia': 50.0,
            'celda_humedo': 40.0, # < 50
            'celda_seco': 45.0,
            'sg_fluido_base': 0.84,
            'sg_solidos': 2.6,
            'pct_fluido_base': 15.0,
            'peso_lodo': 10.5,
        })
        res = self.client.post(url_guardar, data=json.dumps(inv1), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json().get('ok'))
        self.assertFalse(res.json().get('success'))
        self.assertIn('celda + húmedo', res.json().get('error', '').lower())

        # Invalido 2: celda_seco > celda_humedo (secar no puede aumentar masa)
        inv2 = dict(base_body, datos={
            'celda_vacia': 50.0,
            'celda_humedo': 100.0,
            'celda_seco': 105.0, # > 100
            'sg_fluido_base': 0.84,
            'sg_solidos': 2.6,
            'pct_fluido_base': 15.0,
            'peso_lodo': 10.5,
        })
        res = self.client.post(url_guardar, data=json.dumps(inv2), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json().get('ok'))
        self.assertIn('celda + húmedo', res.json().get('error', '').lower())

        # Invalido 3: probeta_total < probeta_vacia + agua_cc
        inv3 = dict(base_body, datos={
            'celda_vacia': 50.0,
            'celda_humedo': 100.0,
            'celda_seco': 90.0,
            'probeta_vacia': 30.0,
            'agua_cc': 10.0,
            'probeta_total': 35.0, # < 30 + 10 = 40
            'sg_fluido_base': 0.84,
            'sg_solidos': 2.6,
            'pct_fluido_base': 15.0,
            'peso_lodo': 10.5,
        })
        res = self.client.post(url_guardar, data=json.dumps(inv3), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json().get('ok'))
        self.assertIn('probeta total', res.json().get('error', '').lower())

        # Invalido 4: gravedad especifica <= 0
        inv4 = dict(base_body, datos={
            'celda_vacia': 50.0,
            'celda_humedo': 100.0,
            'celda_seco': 90.0,
            'sg_fluido_base': 0.0, # Invalido
            'sg_solidos': 2.6,
            'pct_fluido_base': 15.0,
            'peso_lodo': 10.5,
        })
        res = self.client.post(url_guardar, data=json.dumps(inv4), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json().get('ok'))
        self.assertIn('gravedad específica', res.json().get('error', '').lower())

        # Valido
        val = dict(base_body, datos={
            'celda_vacia': 50.0,
            'celda_humedo': 100.0,
            'celda_seco': 90.0,
            'probeta_vacia': 30.0,
            'agua_cc': 5.0,
            'probeta_total': 42.0,
            'sg_fluido_base': 0.84,
            'sg_solidos': 2.6,
            'pct_fluido_base': 15.0,
            'peso_lodo': 10.5,
        })
        res_val = self.client.post(url_guardar, data=json.dumps(val), content_type='application/json')
        self.assertEqual(res_val.status_code, 200)
        data_val = res_val.json()
        self.assertTrue(data_val.get('ok'))
        self.assertTrue(data_val.get('success'))
        muestra_id = data_val['id']

        # Eliminar
        url_del = reverse('operaciones:api_muestras_eliminar', kwargs={
            'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk, 'clave': 'retencion', 'muestra_pk': muestra_id
        })
        res_del = self.client.post(url_del)
        self.assertEqual(res_del.status_code, 200)
        self.assertTrue(res_del.json().get('ok'))
        self.assertTrue(res_del.json().get('success'))

    def test_api_muestras_solidos_limites_fisicos(self):
        url_guardar = reverse('operaciones:api_muestras_guardar', kwargs={
            'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk, 'clave': 'solidos'
        })
        base_body = {
            'equipo_serie': 'SN-ZAR-001',
            'hora_inicio': '10:00',
            'hora_fin': '11:00',
            'orden': 1,
            'tipo_lodo': 'WBM',
        }
        # Invalido: water_pct > 100
        inv = dict(base_body, datos={
            'water_pct': 110.0,
            'mud_weight': 10.0,
            'solids_pct': 10.0,
        })
        res = self.client.post(url_guardar, data=json.dumps(inv), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json().get('ok'))
        self.assertIn('porcentaje', res.json().get('error', '').lower())

        # Valido
        val = dict(base_body, datos={
            'water_pct': 85.0,
            'solids_pct': 15.0,
            'mud_weight': 10.2,
            'drill_solids_sg': 2.6,
            'wt_additive_sg': 4.2,
        })
        res_val = self.client.post(url_guardar, data=json.dumps(val), content_type='application/json')
        self.assertEqual(res_val.status_code, 200)
        self.assertTrue(res_val.json().get('ok'))
        self.assertTrue(res_val.json().get('success'))

    def test_api_eventos_limites_y_crud_normalizado(self):
        url_guardar = reverse('operaciones:api_eventos_guardar', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        # Invalido: sin tipo_problema
        inv = {
            'tipo_problema': '',
            'horas_perdidas': 5.0,
        }
        res_inv = self.client.post(url_guardar, data=json.dumps(inv), content_type='application/json')
        self.assertEqual(res_inv.status_code, 400)
        self.assertFalse(res_inv.json().get('ok'))
        self.assertFalse(res_inv.json().get('success'))

        # Valido
        val = {
            'categoria': 'FLUIDOS',
            'tipo_problema': 'Pérdida de circulación',
            'tipo_fluido': 'WBM',
            'descripcion': 'Se perdieron 40 bbl durante maniobra',
            'horas_perdidas': 4.5,
            'volumen_perdido_bbl': 40.0,
            'costo': 2500.0,
        }
        res_val = self.client.post(url_guardar, data=json.dumps(val), content_type='application/json')
        self.assertEqual(res_val.status_code, 200)
        data_val = res_val.json()
        self.assertTrue(data_val.get('ok'))
        self.assertTrue(data_val.get('success'))
        evento_id = data_val['id']

        # Eliminar
        url_del = reverse('operaciones:api_eventos_eliminar', kwargs={
            'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk, 'evento_pk': evento_id
        })
        res_del = self.client.post(url_del)
        self.assertEqual(res_del.status_code, 200)
        self.assertTrue(res_del.json().get('ok'))
        self.assertTrue(res_del.json().get('success'))

    def test_api_benchmark_evaluacion_normalizado(self):
        url = reverse('operaciones:api_benchmark_evaluacion', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json().get('ok'))
        self.assertTrue(res.json().get('success'))

    def test_api_perdidas_reporte_guardar_normalizado(self):
        url = reverse('operaciones:api_perdidas_reporte_guardar', kwargs={'pk': self.pozo.pk})
        # Error: lista vacia
        res_err = self.client.post(url, data=json.dumps({'codigos': []}), content_type='application/json')
        self.assertEqual(res_err.status_code, 400)
        data_err = res_err.json()
        self.assertFalse(data_err.get('ok'))
        self.assertFalse(data_err.get('success'))

        # Valido
        cat = self.pozo.categorias_perdida.first()
        res_val = self.client.post(url, data=json.dumps({'codigos': [cat.codigo]}), content_type='application/json')
        self.assertEqual(res_val.status_code, 200)
        data_val = res_val.json()
        self.assertTrue(data_val.get('ok'))
        self.assertTrue(data_val.get('success'))

