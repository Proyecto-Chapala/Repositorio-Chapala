"""
Pruebas de Número de Reporte Fijo (Punto 8):
- Garantiza que insertar reportes en fechas intermedias no altere los números
  de los reportes ya existentes (campos fijos, no recálculo dinámico).
"""

import json
from datetime import date
from django.test import TestCase

from operaciones.models import Pozo
from operaciones.models_daily_reports import ReporteDiario


class NumeroReporteFijoTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO NUMERO REPORTE TEST')

    def test_creacion_correlativa_y_no_reenumeracion_al_insertar_fecha_intermedia(self):
        # 1. Crear reporte para 01-oct
        r1 = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 1))
        self.assertEqual(r1.numero_reporte, 1)

        # 2. Crear reporte para 03-oct (se salta el 02-oct)
        r3 = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 3))
        self.assertEqual(r3.numero_reporte, 2)

        # 3. Crear reporte para 04-oct
        r4 = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 4))
        self.assertEqual(r4.numero_reporte, 3)

        # 4. Insertar reporte intermedio para 02-oct
        r2 = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 2))

        # 5. Comprobar que los reportes 1, 3 y 4 mantienen sus números fijos
        r1.refresh_from_db()
        r3.refresh_from_db()
        r4.refresh_from_db()
        r2.refresh_from_db()

        self.assertEqual(r1.numero_reporte, 1)
        self.assertEqual(r3.numero_reporte, 2)  # NO debe haber pasado a 3
        self.assertEqual(r4.numero_reporte, 3)  # NO debe haber pasado a 4
        self.assertEqual(r2.numero_reporte, 4)  # El nuevo reporte toma el siguiente correlativo

    def test_especificar_numero_reporte_manual_en_creacion_y_edicion(self):
        # Crear con número explícito
        r_manual = ReporteDiario.objects.create(
            pozo=self.pozo, fecha=date(2026, 10, 10), numero_reporte=10
        )
        self.assertEqual(r_manual.numero_reporte, 10)

        # Modificar mediante API general guardar
        url = f'/api/pozos/{self.pozo.pk}/reportes-diarios/{r_manual.pk}/general/guardar/'
        payload = {
            'fecha': r_manual.fecha.isoformat(),
            'numero_reporte': 15,
            'profundidad_actual': 1000,
            'profundidad_tvd': 1000,
            'bit_depth': 1000,
        }
        resp = self.client.post(url, json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['ok'])

        r_manual.refresh_from_db()
        self.assertEqual(r_manual.numero_reporte, 15)

