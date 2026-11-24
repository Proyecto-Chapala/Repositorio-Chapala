"""
Pruebas de la integridad temporal entre el Spud Date (fecha de inicio de perforación)
y los reportes diarios del pozo.

Verifica que no se puedan crear ni datar reportes diarios en fechas anteriores
al Spud Date configurado en Well Header Information.
"""

from datetime import date
import json
from django.test import TestCase
from django.urls import reverse
from operaciones.models import Pozo, WellHeaderInfo, ReporteDiario


class SpudDateReportesTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(
            nombre='POZO TEST SPUD DATE',
            estado='ACTIVO',
        )
        self.header = WellHeaderInfo.objects.create(
            pozo=self.pozo,
            spud_date=date(2026, 10, 10),
            completado=True,
        )

    def test_crear_reporte_antes_de_spud_date_rechazado(self):
        """Intentar crear un reporte con fecha anterior a Spud Date debe retornar 400."""
        url = reverse('operaciones:api_reporte_diario_crear', args=[self.pozo.pk])
        payload = {
            'fecha': '2026-10-09',
            'tipo_lodo': 'WBM',
            'copy_data': False,
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn('no puede ser anterior a la fecha de inicio de perforación / Spud Date', datos['error'])
        self.assertIn('10/10/2026', datos['error'])
        self.assertFalse(ReporteDiario.objects.filter(pozo=self.pozo, fecha='2026-10-09').exists())

    def test_crear_reporte_en_spud_date_permitido(self):
        """Crear un reporte exactamente el día del Spud Date debe ser válido."""
        url = reverse('operaciones:api_reporte_diario_crear', args=[self.pozo.pk])
        payload = {
            'fecha': '2026-10-10',
            'tipo_lodo': 'WBM',
            'copy_data': False,
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(ReporteDiario.objects.filter(pozo=self.pozo, fecha=date(2026, 10, 10)).exists())

    def test_crear_reporte_despues_de_spud_date_permitido(self):
        """Crear un reporte con fecha posterior al Spud Date debe ser válido."""
        url = reverse('operaciones:api_reporte_diario_crear', args=[self.pozo.pk])
        payload = {
            'fecha': '2026-10-15',
            'tipo_lodo': 'WBM',
            'copy_data': False,
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(ReporteDiario.objects.filter(pozo=self.pozo, fecha=date(2026, 10, 15)).exists())

    def test_crear_reporte_pozo_sin_spud_date_es_flexible(self):
        """Si el pozo no tiene configurado Spud Date, se permite crear reportes con cualquier fecha válida."""
        pozo_sin_spud = Pozo.objects.create(nombre='POZO SIN SPUD', estado='ACTIVO')
        url = reverse('operaciones:api_reporte_diario_crear', args=[pozo_sin_spud.pk])
        payload = {
            'fecha': '2026-05-01',
            'tipo_lodo': 'WBM',
            'copy_data': False,
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(ReporteDiario.objects.filter(pozo=pozo_sin_spud, fecha=date(2026, 5, 1)).exists())

    def test_modificar_fecha_reporte_a_antes_de_spud_date_rechazado(self):
        """Al modificar los datos generales de un reporte, no se puede cambiar su fecha a una previa al Spud Date."""
        reporte = ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 12),
            tipo_lodo='WBM',
            numero_reporte=1,
        )
        url = reverse('operaciones:api_reporte_diario_general_guardar', args=[self.pozo.pk, reporte.pk])
        payload = {
            'fecha': '2026-10-05',
            'profundidad_actual': 1500,
            'profundidad_tvd': 1500,
            'bit_depth': 1400,
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn('no puede ser anterior a la fecha de inicio de perforación / Spud Date', datos['error'])
        reporte.refresh_from_db()
        self.assertEqual(reporte.fecha, date(2026, 10, 12))

    def test_modificar_fecha_reporte_a_posterior_o_igual_a_spud_date_permitido(self):
        """Modificar la fecha de un reporte a una fecha válida (>= Spud Date) debe permitirse."""
        reporte = ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 12),
            tipo_lodo='WBM',
            numero_reporte=1,
        )
        url = reverse('operaciones:api_reporte_diario_general_guardar', args=[self.pozo.pk, reporte.pk])
        payload = {
            'fecha': '2026-10-10',
            'profundidad_actual': 1500,
            'profundidad_tvd': 1500,
            'bit_depth': 1400,
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        reporte.refresh_from_db()
        self.assertEqual(reporte.fecha, date(2026, 10, 10))

    def test_hub_html_renderiza_min_atributo_spud_date(self):
        """La vista del Hub de reportes diarios debe incluir min con el spud_date en el input modalFecha."""
        url = reverse('operaciones:daily_reports_hub', args=[self.pozo.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode('utf-8')
        self.assertIn('min="2026-10-10"', html)
        self.assertIn('Inicio de perforación (Spud Date): <strong>2026-10-10</strong>', html)

    def test_api_pozo_spud_date_sincroniza_well_header_info(self):
        """Confirmar Spud Date en la pantalla inicial debe sincronizar WellHeaderInfo y sugerir en el Hub."""
        pozo_nuevo = Pozo.objects.create(nombre='POZO NUEVO SYNC', estado='ACTIVO')
        url = reverse('operaciones:api_pozo_spud_date', args=[pozo_nuevo.pk])
        payload = {
            'fecha_primera_captura': '2026-11-01',
            'tipo_fluido_inicial': 'OIL_BASE',
            'numero_control_logit': 'LOGIT-777',
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['success'])

        pozo_nuevo.refresh_from_db()
        self.assertEqual(pozo_nuevo.fecha_primera_captura, date(2026, 11, 1))
        self.assertEqual(pozo_nuevo.tipo_fluido_inicial, 'OIL_BASE')
        self.assertEqual(pozo_nuevo.numero_control_logit, 'LOGIT-777')

        # Verificar sincronización con WellHeaderInfo
        header = pozo_nuevo.well_header_info
        self.assertEqual(header.spud_date, date(2026, 11, 1))
        self.assertEqual(header.primary_mud_type_codigo, 'OIL_BASE')
        self.assertEqual(header.primary_mud_type_descripcion, 'Base Aceite')
        self.assertEqual(header.numero_control_logit, 'LOGIT-777')

        # Verificar que el Hub y la API de listado sugieran esta fecha y tipo de lodo mapeado (OBM)
        resp_list = self.client.get(reverse('operaciones:api_reportes_diarios_list', args=[pozo_nuevo.pk]))
        self.assertEqual(resp_list.status_code, 200)
        sug = resp_list.json()['sugerencia']
        self.assertEqual(sug['fecha'], '2026-11-01')
        self.assertEqual(sug['tipo_lodo'], 'OBM')

    def test_well_header_info_guardar_sincroniza_pozo(self):
        """Guardar WellHeaderInfo debe sincronizar fecha_primera_captura y numero_control_logit en Pozo."""
        url = reverse('operaciones:api_well_header_guardar', args=[self.pozo.pk])
        payload = {
            'spud_date': '2026-10-12',
            'numero_control_logit': 'LOGIT-888',
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.pozo.refresh_from_db()
        self.assertEqual(self.pozo.fecha_primera_captura, date(2026, 10, 12))
        self.assertEqual(self.pozo.numero_control_logit, 'LOGIT-888')

    def test_well_header_info_guardar_spud_date_posterior_a_reporte_rechazado(self):
        """Intentar cambiar Spud Date a una fecha posterior a un reporte diario existente debe rechazarse."""
        ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 10),
            tipo_lodo='WBM',
            numero_reporte=1,
        )
        url = reverse('operaciones:api_well_header_guardar', args=[self.pozo.pk])
        payload = {
            'spud_date': '2026-10-15',
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['success'])
        self.assertIn('no puede ser posterior al primer reporte diario existente', datos['error'])
        self.header.refresh_from_db()
        self.assertEqual(self.header.spud_date, date(2026, 10, 10))


