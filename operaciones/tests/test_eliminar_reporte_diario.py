"""
Pruebas de la eliminación segura de reportes diarios bajo la regla LIFO.
Verifica que solo se pueda eliminar el último reporte cronológico del pozo
y que los reportes intermedios queden protegidos contra borrado.
"""

from datetime import date
from django.test import TestCase
from operaciones.models import Pozo, ReporteDiario


class EliminarReporteDiarioLIFOTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(
            nombre='POZO TEST LIFO',
            estado='ACTIVO',
            spud_date_completado=True,
        )
        self.r1 = ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 1),
            tipo_lodo='WBM',
            numero_reporte=1,
        )
        self.r2 = ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 2),
            tipo_lodo='WBM',
            numero_reporte=2,
        )
        self.r3 = ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 3),
            tipo_lodo='WBM',
            numero_reporte=3,
        )

    def test_eliminar_reporte_intermedio_rechazado(self):
        """Intentar eliminar el reporte 1 o 2 cuando existe el 3 debe rechazarse con 400."""
        resp = self.client.delete(
            f'/api/pozos/{self.pozo.pk}/reportes-diarios/{self.r1.pk}/eliminar/'
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn('Solo se puede eliminar el último reporte diario del pozo', datos['error'])
        self.assertIn('03/10/2026', datos['error'])
        # Asegurar que no se borró
        self.assertTrue(ReporteDiario.objects.filter(pk=self.r1.pk).exists())

    def test_eliminar_ultimo_reporte_exitoso(self):
        """Eliminar el reporte 3 (el último) debe permitirse."""
        resp = self.client.delete(
            f'/api/pozos/{self.pozo.pk}/reportes-diarios/{self.r3.pk}/eliminar/'
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertFalse(ReporteDiario.objects.filter(pk=self.r3.pk).exists())
        self.assertEqual(self.pozo.reportes_diarios.count(), 2)

    def test_eliminacion_secuencial_inversa(self):
        """Permite eliminar en orden cronológico inverso: 3, luego 2, luego 1."""
        resp3 = self.client.delete(f'/api/pozos/{self.pozo.pk}/reportes-diarios/{self.r3.pk}/eliminar/')
        self.assertEqual(resp3.status_code, 200)

        # Ahora el último es el 2
        resp2 = self.client.delete(f'/api/pozos/{self.pozo.pk}/reportes-diarios/{self.r2.pk}/eliminar/')
        self.assertEqual(resp2.status_code, 200)

        # Ahora el último es el 1
        resp1 = self.client.delete(f'/api/pozos/{self.pozo.pk}/reportes-diarios/{self.r1.pk}/eliminar/')
        self.assertEqual(resp1.status_code, 200)

        self.assertEqual(self.pozo.reportes_diarios.count(), 0)

    def test_eliminar_reporte_en_pozo_cerrado_rechazado(self):
        """Un pozo cerrado no permite eliminar ningún reporte."""
        self.pozo.estado = 'CERRADO'
        self.pozo.save()

        resp = self.client.delete(
            f'/api/pozos/{self.pozo.pk}/reportes-diarios/{self.r3.pk}/eliminar/'
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertIn('cerrado', datos['error'])

    def test_api_lista_reportes_incluye_numero_reporte(self):
        """La lista de reportes en el Hub debe exponer numero_reporte."""
        resp = self.client.get(f'/api/pozos/{self.pozo.pk}/reportes-diarios/')
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertEqual(len(datos['reportes']), 3)
        self.assertEqual(datos['reportes'][0]['numero_reporte'], 3)

