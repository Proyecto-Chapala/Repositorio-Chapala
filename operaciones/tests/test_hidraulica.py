"""
Pruebas de Hidráulica (API RP 13D, Pestaña 8):
- Caída de presión en herramientas de fondo (MWD y Motor de fondo PDM).
- Sincronización de edición de norma (4ª y 5ª edición).
"""

from datetime import date
from django.test import TestCase

from operaciones import hidraulica as hid
from operaciones.models import Pozo
from operaciones.models_daily_reports import (
    ReporteDiario,
    ReporteDiarioBitData,
    ReporteDiarioMudCheck,
    ReporteDiarioBoquilla,
    ReporteDiarioBomba,
    TramoSarta,
)
from operaciones.views_hidraulica import calcular_hidraulica_reporte


class HidraulicaHerramientasTests(TestCase):

    def test_calcular_hidraulica_puro_incluye_mwd_y_motor(self):
        secciones = [{
            'desde_ft': 0, 'hasta_ft': 1000, 'longitud_ft': 1000,
            'diametro_hoyo_in': 8.5, 'od_in': 5.0, 'id_in': 4.276,
            'descripcion': 'DP 5"', 'es_bajo_mecha': False
        }]
        reo = {
            'edicion': '4',
            'tuberia': {'n': 0.6, 'k': 1.0, 'ty': 0.0},
            'anular': {'n': 0.6, 'k': 1.0, 'ty': 0.0},
        }
        # Sin herramientas
        res_sin = hid.calcular(secciones, q=400, rho=10.0, reo=reo, tfa=0.5, bit_size=8.5, tvd_de=lambda md: md)
        self.assertEqual(res_sin['perdida_herramientas'], 0.0)

        # Con MWD = 100 y Motor = 200 a caudal de referencia 400
        herr = {'dp_mwd': 100.0, 'dp_motor': 200.0, 'caudal_ref': 400.0}
        res_con = hid.calcular(secciones, q=400, rho=10.0, reo=reo, tfa=0.5, bit_size=8.5, tvd_de=lambda md: md, herramientas=herr)
        self.assertEqual(res_con['perdida_mwd'], 100.0)
        self.assertEqual(res_con['perdida_motor'], 200.0)
        self.assertEqual(res_con['perdida_herramientas'], 300.0)
        self.assertAlmostEqual(res_con['perdida_sarta'], res_sin['perdida_sarta'] + 300.0, places=2)
        self.assertAlmostEqual(res_con['perdida_total'], res_sin['perdida_total'] + 300.0, places=2)

    def test_calcular_hidraulica_reporte_integra_herramientas(self):
        pozo = Pozo.objects.create(nombre='POZO HIDRAULICA')
        reporte = ReporteDiario.objects.create(
            pozo=pozo, fecha=date(2026, 10, 13), tipo_lodo='WBM',
            bit_depth=1000.0, profundidad_actual=1000.0
        )
        ReporteDiarioMudCheck.objects.create(
            reporte=reporte, check_number=1, is_primary=True,
            mud_weight=10.0, pv=15.0, yp=10.0, r600=40, r300=25
        )
        ReporteDiarioBoquilla.objects.create(reporte=reporte, size_32nds=12, cantidad=3)
        ReporteDiarioBomba.objects.create(
            reporte=reporte, numero_bomba=1, pump_rate_spm=60, liner_diameter=6.0,
            stroke_length=12.0, eficiencia_pct=100.0, pump_on_report=True
        )
        TramoSarta.objects.create(
            reporte=reporte, orden=1, descripcion='DP 5"', od_in=5.0, id_in=4.276, longitud_ft=1000.0
        )
        ReporteDiarioBitData.objects.create(
            reporte=reporte, bit_size=8.5, dp_mwd=120.0, dp_motor=250.0, ref_flow_rate=300.0
        )

        res = calcular_hidraulica_reporte(pozo, reporte, edicion='4')
        self.assertTrue(res['ok'])
        tot = res['totales']
        self.assertGreater(tot['herramientas'], 0.0)
        self.assertGreater(tot['mwd'], 0.0)
        self.assertGreater(tot['motor'], 0.0)
        self.assertEqual(res['entrada']['dp_mwd'], 120.0)
        self.assertEqual(res['entrada']['dp_motor'], 250.0)

    def test_calcular_hidraulica_excluye_bomba_riser_de_sarta_y_mecha(self):
        pozo = Pozo.objects.create(nombre='POZO RISER')
        reporte = ReporteDiario.objects.create(
            pozo=pozo, fecha=date(2026, 10, 13), tipo_lodo='WBM',
            bit_depth=1000.0, profundidad_actual=1000.0
        )
        ReporteDiarioMudCheck.objects.create(
            reporte=reporte, check_number=1, is_primary=True,
            mud_weight=10.0, pv=15.0, yp=10.0, r600=40, r300=25
        )
        ReporteDiarioBoquilla.objects.create(reporte=reporte, size_32nds=12, cantidad=3)
        # Bomba 1 de perforación activa
        b1 = ReporteDiarioBomba.objects.create(
            reporte=reporte, numero_bomba=1, pump_rate_spm=60, liner_diameter=6.0,
            stroke_length=12.0, eficiencia_pct=100.0, pump_on_report=True, riser_pump=False
        )
        # Bomba 2 de riser activa
        b2 = ReporteDiarioBomba.objects.create(
            reporte=reporte, numero_bomba=2, pump_rate_spm=40, liner_diameter=6.0,
            stroke_length=12.0, eficiencia_pct=100.0, pump_on_report=True, riser_pump=True
        )
        TramoSarta.objects.create(
            reporte=reporte, orden=1, descripcion='DP 5"', od_in=5.0, id_in=4.276, longitud_ft=1000.0
        )
        ReporteDiarioBitData.objects.create(reporte=reporte, bit_size=8.5)

        # 1. Verificar obtener_hidraulica_bombas (Bottoms up)
        from operaciones.views_daily_reports import obtener_hidraulica_bombas
        bbl_stk, caudal_gpm = obtener_hidraulica_bombas(reporte)
        self.assertAlmostEqual(caudal_gpm, b1.caudal_gpm, places=1)
        self.assertNotEqual(caudal_gpm, b1.caudal_gpm + b2.caudal_gpm)

        # 2. Verificar calcular_hidraulica_reporte
        res = calcular_hidraulica_reporte(pozo, reporte, edicion='4')
        self.assertTrue(res['ok'])
        # El caudal de perforación debe ser solo de b1
        self.assertAlmostEqual(res['entrada']['caudal_gpm'], round(b1.caudal_gpm, 1), places=1)
        # El caudal de riser debe ser b2
        self.assertAlmostEqual(res['entrada']['caudal_riser_gpm'], round(b2.caudal_gpm, 1), places=1)

