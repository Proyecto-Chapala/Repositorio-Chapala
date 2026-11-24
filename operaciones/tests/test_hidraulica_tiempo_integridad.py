import json
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse

from operaciones.models import Pozo, WellHeaderInfo, TipoDistribucionTiempo
from operaciones.models_daily_reports import (
    ReporteDiario, ReporteDiarioBomba, ReporteDiarioBoquilla,
    ReporteDiarioBitData, ReporteDiarioMudCheck, ReporteDiarioComentarios,
    ReporteDiarioTiempo, ReporteDiarioActividadTiempo
)


class TestHidraulicaTiempoIntegridad(TestCase):
    def setUp(self):
        self.client = Client()
        self.pozo = Pozo.objects.create(
            nombre="POZO HIDRAULICA TEST",
            estado="ACTIVO",
            spud_date_completado=True,
            usar_api_5ta_edicion_hidraulica=False,
            moneda_simbolo="USD",
        )
        self.header = WellHeaderInfo.objects.create(
            pozo=self.pozo,
            surface_temp_f=80.0,
            temp_gradient_f_100ft=1.5,
        )
        self.reporte = ReporteDiario.objects.create(
            pozo=self.pozo,
            numero_reporte=1,
            fecha=date(2026, 10, 1),
            profundidad_actual=5000.0,
            profundidad_tvd=5000.0,
            tipo_lodo="WBM",
        )
        TipoDistribucionTiempo.sembrar_estandar(self.pozo)

    def test_hidraulica_rechaza_pozo_cerrado_en_post(self):
        self.pozo.estado = 'CERRADO'
        self.pozo.save()

        url = reverse('operaciones:api_hidraulica_detail', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        res = self.client.post(url, data=json.dumps({'edicion': '5'}), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertFalse(data.get('ok', True))
        self.assertFalse(data.get('success', True))
        self.assertIn('cerrado', data.get('error', '').lower())

        self.pozo.refresh_from_db()
        self.assertFalse(self.pozo.usar_api_5ta_edicion_hidraulica)

    def test_hidraulica_permite_post_en_pozo_activo(self):
        url = reverse('operaciones:api_hidraulica_detail', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        res = self.client.post(url, data=json.dumps({'edicion': '5'}), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('ok'))
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('edicion'), '5')

        self.pozo.refresh_from_db()
        self.assertTrue(self.pozo.usar_api_5ta_edicion_hidraulica)

    def test_hidraulica_get_normalizado(self):
        url = reverse('operaciones:api_hidraulica_detail', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('ok'))
        self.assertTrue(data.get('success'))
        self.assertIn('faltan', data)

    def test_cost_overview_detail_normalizado(self):
        url = reverse('operaciones:api_cost_overview_detail', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('ok'))
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('pozo'), self.pozo.nombre)

    def test_tiempo_detail_normalizado(self):
        url = reverse('operaciones:api_tiempo_detail', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('ok'))
        self.assertTrue(data.get('success'))
        self.assertIn('actividades', data)

    def test_tiempo_guardar_exitoso_normalizado(self):
        url = reverse('operaciones:api_tiempo_guardar', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        payload = {
            'horas_periodo': 24.0,
            'actividades': [
                {'tipo_numero': 1, 'horas': 12.0},
                {'tipo_numero': 2, 'horas': 12.0},
            ]
        }
        res = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('ok'))
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('horas_periodo'), 24.0)

    def test_tiempo_guardar_error_normalizado(self):
        url = reverse('operaciones:api_tiempo_guardar', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        payload = {
            'horas_periodo': -5.0,
            'actividades': []
        }
        res = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertFalse(data.get('ok', True))
        self.assertFalse(data.get('success', True))
        self.assertIn('error', data)

    def test_sarta_reporte_anterior_normalizado(self):
        url = reverse('operaciones:api_sarta_reporte_anterior', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('ok'))
        self.assertTrue(data.get('success'))

    def test_comentarios_detail_normalizado(self):
        url = reverse('operaciones:api_comentarios_detail', kwargs={'pk': self.pozo.pk, 'reporte_pk': self.reporte.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('ok'))
        self.assertTrue(data.get('success'))
        self.assertIn('comentarios', data)

    def test_reporte_diario_crear_y_eliminar_normalizado(self):
        # Crear reporte normalizado
        url_crear = reverse('operaciones:api_reporte_diario_crear', kwargs={'pk': self.pozo.pk})
        res_crear = self.client.post(
            url_crear,
            data=json.dumps({'fecha': '2026-10-02', 'tipo_lodo': 'WBM', 'numero_reporte': 2}),
            content_type='application/json'
        )
        self.assertEqual(res_crear.status_code, 200)
        data_crear = res_crear.json()
        self.assertTrue(data_crear.get('ok'))
        self.assertTrue(data_crear.get('success'))
        rep2_id = data_crear.get('id')

        # Error en creación (fecha duplicada)
        res_dup = self.client.post(
            url_crear,
            data=json.dumps({'fecha': '2026-10-02', 'tipo_lodo': 'WBM'}),
            content_type='application/json'
        )
        self.assertEqual(res_dup.status_code, 400)
        data_dup = res_dup.json()
        self.assertFalse(data_dup.get('ok', True))
        self.assertFalse(data_dup.get('success', True))

        # Eliminar reporte (LIFO) normalizado
        url_elim = reverse('operaciones:api_reporte_diario_eliminar', kwargs={'pk': self.pozo.pk, 'reporte_pk': rep2_id})
        res_elim = self.client.delete(url_elim)
        self.assertEqual(res_elim.status_code, 200)
        data_elim = res_elim.json()
        self.assertTrue(data_elim.get('ok'))
        self.assertTrue(data_elim.get('success'))

