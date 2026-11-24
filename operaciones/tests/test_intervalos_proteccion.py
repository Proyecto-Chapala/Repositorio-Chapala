"""
Pruebas de protección e integridad de Intervalos de Revestimiento:
- Bloqueo de eliminación si el intervalo tiene reportes diarios asignados.
- Bloqueo de creación, modificación, cierre, reapertura y eliminación si el pozo está CERRADO.
- Coexistencia de claves 'success' y 'ok' en las respuestas JSON.
"""

from datetime import date
from decimal import Decimal
import json
from django.test import TestCase

from operaciones.models import IntervaloRevestimiento, Pozo, ReporteDiario


class IntervalosProteccionTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PROTECCION INTERVALOS', estado='ACTIVO')
        self.intervalo = IntervaloRevestimiento.objects.create(
            pozo=self.pozo,
            numero_intervalo=1,
            tipo='CONDUCTOR',
            profundidad_ft=Decimal('1500'),
            cerrado=True,
        )

    def test_eliminar_intervalo_sin_reportes_exitoso(self):
        resp = self.client.delete(f'/api/pozos/{self.pozo.pk}/casing-intervals/{self.intervalo.pk}/eliminar/')
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['success'])
        self.assertTrue(datos['ok'])
        self.assertFalse(IntervaloRevestimiento.objects.filter(pk=self.intervalo.pk).exists())

    def test_eliminar_intervalo_con_reportes_asignados_rechazado(self):
        # Crear un reporte diario imputado al intervalo
        ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 1),
            tipo_lodo='WBM',
            intervalo_costo=self.intervalo,
        )

        resp = self.client.delete(f'/api/pozos/{self.pozo.pk}/casing-intervals/{self.intervalo.pk}/eliminar/')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['success'])
        self.assertFalse(datos['ok'])
        self.assertIn('reporte(s) diario(s) asignado(s)', datos['error'])
        # Asegurar que el intervalo no fue eliminado
        self.assertTrue(IntervaloRevestimiento.objects.filter(pk=self.intervalo.pk).exists())

    def test_pozo_cerrado_bloquea_eliminar_intervalo(self):
        self.pozo.estado = 'CERRADO'
        self.pozo.save()

        resp = self.client.delete(f'/api/pozos/{self.pozo.pk}/casing-intervals/{self.intervalo.pk}/eliminar/')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['success'])
        self.assertFalse(datos['ok'])
        self.assertIn('cerrado', datos['error'])

    def test_pozo_cerrado_bloquea_crear_intervalo(self):
        self.pozo.estado = 'CERRADO'
        self.pozo.save()

        payload = {
            'numero_intervalo': 2,
            'tipo': 'SUPERFICIE',
            'profundidad_ft': 3500,
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/casing-intervals/crear/',
            json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['success'])
        self.assertFalse(datos['ok'])
        self.assertIn('cerrado', datos['error'])

    def test_pozo_cerrado_bloquea_actualizar_intervalo(self):
        self.pozo.estado = 'CERRADO'
        self.pozo.save()

        payload = {'numero_intervalo': 1, 'tipo': 'CONDUCTOR', 'profundidad_ft': 1600}
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/casing-intervals/{self.intervalo.pk}/',
            json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['success'])
        self.assertFalse(datos['ok'])
        self.assertIn('cerrado', datos['error'])

    def test_pozo_cerrado_bloquea_cerrar_intervalo(self):
        self.intervalo.cerrado = False
        self.intervalo.save()
        self.pozo.estado = 'CERRADO'
        self.pozo.save()

        payload = {'numero_intervalo': 1, 'tipo': 'CONDUCTOR', 'profundidad_ft': 1500}
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/casing-intervals/{self.intervalo.pk}/cerrar/',
            json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['success'])
        self.assertFalse(datos['ok'])
        self.assertIn('cerrado', datos['error'])

    def test_pozo_cerrado_bloquea_reabrir_intervalo(self):
        self.pozo.estado = 'CERRADO'
        self.pozo.save()

        resp = self.client.post(f'/api/pozos/{self.pozo.pk}/casing-intervals/{self.intervalo.pk}/reabrir/')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['success'])
        self.assertFalse(datos['ok'])
        self.assertIn('cerrado', datos['error'])

    def test_eliminar_intervalo_intermedio_rechazado_por_regla_lifo(self):
        """No se puede eliminar un intervalo si existen intervalos posteriores (regla LIFO)."""
        intervalo_2 = IntervaloRevestimiento.objects.create(
            pozo=self.pozo,
            numero_intervalo=2,
            tipo='SUPERFICIE',
            profundidad_ft=Decimal('3500'),
            cerrado=False,
        )

        resp = self.client.delete(f'/api/pozos/{self.pozo.pk}/casing-intervals/{self.intervalo.pk}/eliminar/')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['success'])
        self.assertFalse(datos['ok'])
        self.assertIn('Solo se puede eliminar el último intervalo registrado', datos['error'])
        self.assertIn('Intervalo 2', datos['error'])
        self.assertTrue(IntervaloRevestimiento.objects.filter(pk=self.intervalo.pk).exists())

    def test_eliminar_ultimo_intervalo_exitoso_en_secuencia_lifo(self):
        """Eliminar el último intervalo en secuencia estricta LIFO debe permitirse."""
        intervalo_2 = IntervaloRevestimiento.objects.create(
            pozo=self.pozo,
            numero_intervalo=2,
            tipo='SUPERFICIE',
            profundidad_ft=Decimal('3500'),
            cerrado=False,
        )

        # Eliminar el 2 (último) -> permitido
        resp2 = self.client.delete(f'/api/pozos/{self.pozo.pk}/casing-intervals/{intervalo_2.pk}/eliminar/')
        self.assertEqual(resp2.status_code, 200)
        self.assertFalse(IntervaloRevestimiento.objects.filter(pk=intervalo_2.pk).exists())

        # Ahora el 1 vuelve a ser el último -> permitido
        resp1 = self.client.delete(f'/api/pozos/{self.pozo.pk}/casing-intervals/{self.intervalo.pk}/eliminar/')
        self.assertEqual(resp1.status_code, 200)
        self.assertFalse(IntervaloRevestimiento.objects.filter(pk=self.intervalo.pk).exists())

    def test_casing_intervals_html_dinterval_es_readonly(self):
        """El campo de número de intervalo en el formulario debe ser de solo lectura."""
        resp = self.client.get(f'/pozos/{self.pozo.pk}/casing-intervals/')
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode('utf-8')
        self.assertIn('id="dInterval" class="form-input" readonly', html)


