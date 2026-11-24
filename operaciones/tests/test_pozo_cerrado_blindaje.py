"""
Pruebas exhaustivas de blindaje contra mutaciones en pozos CERRADOS.
Verifica que todos los endpoints de guardado de configuración (8 pantallas de pozo)
y de pestañas de reporte diario (1 a 8 y módulos opcionales) rechacen modificaciones con 400.
"""

from datetime import date
from django.test import TestCase
from django.urls import reverse
from operaciones.models import Pozo, ReporteDiario, WellHeaderInfo


class BlindajePozoCerradoTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(
            nombre='POZO BLINDAJE TEST',
            estado='CERRADO',
            spud_date_completado=True,
        )
        self.header = WellHeaderInfo.objects.create(pozo=self.pozo)
        self.reporte = ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 19),
            tipo_lodo='WBM',
        )

    # ------------------------------------------------------------
    # 1. Configuración del Pozo (views.py)
    # ------------------------------------------------------------

    def test_well_header_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_well_header_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"operador": "TEST OP"}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))
        self.assertIn('cerrado', datos.get('error', '').lower())

    def test_marketing_codes_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_marketing_codes_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"pais": "VE"}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))
        self.assertIn('cerrado', datos.get('error', '').lower())

    def test_fosas_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_fosas_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"fosas": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))

    def test_tipos_fosa_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_tipos_fosa_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"tipos": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))

    def test_categorias_perdida_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_categorias_perdida_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"categorias": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))

    def test_general_setup_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_general_setup_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"sistema_unidades": "API"}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))

    def test_almacenes_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_almacenes_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"almacenes": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))

    def test_tipos_distribucion_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_tipos_distribucion_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"tipos": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))

    def test_productos_activos_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_productos_activos_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"productos_activos": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))

    def test_equipos_activos_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_equipos_activos_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"equipos_activos": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))

    def test_mallas_activas_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_mallas_activas_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"mallas_activas": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))

    def test_equipment_properties_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_equipment_properties_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"propiedades_seleccionadas": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))

    def test_benchmark_definiciones_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_benchmark_definiciones_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"parametro_ids": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))

    def test_benchmark_targets_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_benchmark_targets_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"targets": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('success', True))

    # ------------------------------------------------------------
    # 2. Pestañas de Reporte Diario (views_daily_reports.py)
    # ------------------------------------------------------------

    def test_reporte_general_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_reporte_diario_general_guardar', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{"profundidad_actual": 1000}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    def test_well_survey_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_well_survey_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"estaciones": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    def test_formation_tops_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_formation_tops_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"formation_tops": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    def test_pumps_bits_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_pumps_bits_guardar', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{"bombas": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    def test_mud_properties_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_mud_properties_guardar', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{"config": {}}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    def test_well_geometry_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_well_geometry_guardar', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{"sarta": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    def test_comentarios_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_comentarios_guardar', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{"remarks": "test"}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    def test_tiempo_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_tiempo_guardar', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{"horas_periodo": 24}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    # ------------------------------------------------------------
    # 3. Pestaña 8 — Volumetría, Inventario y Servicios (views_inventario.py)
    # ------------------------------------------------------------

    def test_volumetria_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_volumetria_guardar', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{"fosas": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    def test_servicio_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_servicio_guardar', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{"descripcion": "Ingeniero", "categoria_costo": 1, "tarifa_diaria": 100}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    def test_volumetria_transaccion_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_volumetria_transaccion', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{"tipo": "QUIMICOS"}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    def test_ticket_producto_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_ticket_producto_guardar', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    # ------------------------------------------------------------
    # 4. Control de Sólidos (views_control_solidos.py) y Módulos Opcionales
    # ------------------------------------------------------------

    def test_uso_equipos_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_uso_equipos_guardar', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{"equipos": []}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    def test_eventos_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_eventos_guardar', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{"tipo_problema": "problema test"}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))

    def test_hidraulica_guardar_rechaza_pozo_cerrado(self):
        url = reverse('operaciones:api_hidraulica_detail', args=[self.pozo.pk, self.reporte.pk])
        resp = self.client.post(url, data='{"edicion": "5"}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos.get('ok', True))
        self.assertFalse(datos.get('success', True))
        self.assertIn('cerrado', datos.get('error', '').lower())

    # ------------------------------------------------------------
    # 5. Al reabrir el pozo se permite la modificación
    # ------------------------------------------------------------

    def test_reabrir_pozo_permite_guardar(self):
        self.pozo.estado = 'ACTIVO'
        self.pozo.save()

        url = reverse('operaciones:api_well_header_guardar', args=[self.pozo.pk])
        resp = self.client.post(url, data='{"operador": "NUEVO OPERADOR"}', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos.get('success', False))
