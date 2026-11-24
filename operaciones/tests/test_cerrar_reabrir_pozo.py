"""
Pruebas de la funcionalidad Cerrar y Reabrir Pozo.
Verifica la transición de estados, protección de reportes y reversibilidad.
"""

from datetime import date
from django.test import TestCase
from operaciones.models import Pozo, ReporteDiario


class CerrarReabrirPozoTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(
            nombre='POZO TEST CIERRE',
            estado='ACTIVO',
            spud_date_completado=True,
        )

    def test_cerrar_pozo_via_api_json(self):
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/cerrar/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['success'])
        self.assertEqual(datos['estado'], 'CERRADO')
        self.pozo.refresh_from_db()
        self.assertEqual(self.pozo.estado, 'CERRADO')

    def test_cerrar_pozo_ya_cerrado_devuelve_error(self):
        self.pozo.estado = 'CERRADO'
        self.pozo.save()
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/cerrar/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['success'])
        self.assertIn('ya está cerrado', datos['error'])

    def test_reabrir_pozo_cerrado(self):
        self.pozo.estado = 'CERRADO'
        self.pozo.save()

        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/reabrir/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['success'])
        self.assertEqual(datos['estado'], 'ACTIVO')
        self.pozo.refresh_from_db()
        self.assertEqual(self.pozo.estado, 'ACTIVO')

    def test_reabrir_pozo_que_no_esta_cerrado(self):
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/reabrir/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['success'])
        self.assertIn('no está cerrado', datos['error'])

    def test_pozo_cerrado_bloquea_crear_reporte_diario(self):
        self.pozo.estado = 'CERRADO'
        self.pozo.save()

        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/reportes-diarios/crear/',
            data='{"fecha": "2026-10-20", "tipo_lodo": "WBM"}',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn('cerrado', datos['error'])

    def test_pozo_cerrado_bloquea_eliminar_reporte_diario(self):
        reporte = ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 19),
            tipo_lodo='WBM',
        )
        self.pozo.estado = 'CERRADO'
        self.pozo.save()

        resp = self.client.delete(
            f'/api/pozos/{self.pozo.pk}/reportes-diarios/{reporte.pk}/eliminar/'
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn('cerrado', datos['error'])

    def test_pantallas_siguen_accesibles_en_modo_lectura(self):
        self.pozo.estado = 'CERRADO'
        self.pozo.save()

        resp_main = self.client.get(f'/pozos/{self.pozo.pk}/')
        self.assertEqual(resp_main.status_code, 200)

        resp_hub = self.client.get(f'/pozos/{self.pozo.pk}/drilling-fluids-equipment/')
        self.assertEqual(resp_hub.status_code, 200)
        self.assertContains(resp_hub, 'Este pozo se encuentra Cerrado')

        resp_recap = self.client.get(f'/pozos/{self.pozo.pk}/reporte-final/')
        self.assertEqual(resp_recap.status_code, 200)
        self.assertContains(resp_recap, 'Pozo Cerrado')

