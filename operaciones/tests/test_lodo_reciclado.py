"""
Lodo reciclado solo como volumen (docs/26_REDISENO_INVENTARIO_Y_LODO_RECICLADO.md, Parte A).

1. Suma volumen al tanque y flujos[ACTIVO]['recibido'].
2. No descuenta inventario ni genera costo, incluso con datos viejos (lodo_producto/lodo_cantidad).
3. Aporta masa para las concentraciones de los productos en lb/bbl.
4. La API registra LODO_ENTERO sin requerir lodo_producto_id.
"""

import json
from datetime import date
from decimal import Decimal

from django.test import SimpleTestCase, TestCase

from operaciones import volumetria as vol
from operaciones.models import CategoriaPerdidaItem, Fosa, Pozo, TipoFosa
from operaciones.models_daily_reports import ReporteDiario
from operaciones.models_inventario import TransaccionVolumen, VolumenFosaDia

ACTIVO, RESERVA = vol.ACTIVO, vol.RESERVA
BARITA = 1


def tanque(numero, grupo, real=None):
    return {'numero': numero, 'grupo': grupo, 'real': real}


def dia(id_, fosas, transacciones=(), hoyo=0.0, tickets=None, manual=None):
    return {
        'id': id_,
        'fecha_texto': f'dia {id_}',
        'fosas': fosas,
        'hoyo_fluido': hoyo,
        'tickets': tickets or [],
        'transacciones': list(transacciones),
        'manual': manual or {},
    }


class LodoRecicladoSimulacionTests(SimpleTestCase):

    def test_lodo_reciclado_suma_volumen_y_flujo_recibido(self):
        # 1. Un LODO_ENTERO de 100 bbl en un tanque activo suma 100 al volumen calculado del tanque y 100 a flujos[ACTIVO]['recibido'].
        tr = {
            'secuencia': 1, 'tipo': 'LODO_ENTERO', 'fosa': 1, 'volumen': 100.0,
            'productos': [],
        }
        dias = [dia(1, [tanque(1, ACTIVO)], [tr])]
        sim = vol.simular(dias, 1)
        self.assertEqual(sim['calc_fosa'][1], 100.0)
        self.assertEqual(sim['flujos'][ACTIVO]['recibido'], 100.0)

    def test_lodo_reciclado_con_datos_viejos_no_genera_consumo_ni_costo(self):
        # 2. Si la transacción trae (por datos viejos) lodo_producto y lodo_cantidad, no aparece consumo en sim['inventario'] ni costo en sim['costo_dia_cat'].
        tr = {
            'secuencia': 1, 'tipo': 'LODO_ENTERO', 'fosa': 1, 'volumen': 100.0,
            'lodo_producto': BARITA, 'lodo_cantidad': 100.0, 'lodo_precio': 25.0,
            'lodo_categoria': 1, 'productos': [],
        }
        tickets = [{'sentido': 'ENTRADA', 'detalles': [{'producto': BARITA, 'real': 500, 'ticket': 500}]}]
        dias = [dia(1, [tanque(1, ACTIVO)], [tr], tickets=tickets)]
        sim = vol.simular(dias, 1)

        inv = sim['inventario'][BARITA]
        self.assertEqual(inv['usado_fluido'], 0.0)
        self.assertEqual(inv['final'], 500.0)
        self.assertEqual(sim['costo_dia_cat'].get(1, 0.0), 0.0)

    def test_lodo_reciclado_aporta_masa_a_concentraciones(self):
        # 3. Las concentraciones del lodo (lb/bbl × volumen) siguen entrando en la masa del compartimento.
        tr = {
            'secuencia': 1, 'tipo': 'LODO_ENTERO', 'fosa': 1, 'volumen': 100.0,
            'productos': [{
                'producto': BARITA, 'cantidad': 15.0, 'unidad': 'LBS', 'tamano': 100,
                'gravedad': 4.2, 'precio': 0, 'categoria': 1, 'concentracion': True,
            }],
        }
        dias = [dia(1, [tanque(1, ACTIVO)], [tr])]
        sim = vol.simular(dias, 1)

        conc_activo = sim['concentraciones'][ACTIVO]
        self.assertEqual(conc_activo['vol_fin'], 100.0)
        self.assertAlmostEqual(conc_activo['fin'][BARITA], 15.0)


class LodoRecicladoApiTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO LODO')
        TipoFosa.sembrar_estandar(self.pozo)
        CategoriaPerdidaItem.sembrar_estandar(self.pozo)
        self.reporte = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13))
        Fosa.objects.create(pozo=self.pozo, numero=1, descripcion='Activo 1', capacidad=Decimal('500'))
        VolumenFosaDia.objects.create(reporte=self.reporte, fosa_numero=1, fosa_descripcion='Activo 1',
                                      tipo_codigo=1)  # ACTIVA = 1
        self.url = f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/volumetria/transaccion/'

    def test_registrar_lodo_reciclado_sin_lodo_producto_id_responde_ok(self):
        payload = {
            'tipo': 'LODO_ENTERO',
            'fosa': 1,
            'volumen': 120,
            'peso': 11.5,
            'origen': 'Planta central',
            'concentraciones': [],
        }
        resp = self.client.post(self.url, json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos.get('ok'))

        t = TransaccionVolumen.objects.get(reporte=self.reporte, secuencia=1)
        self.assertEqual(t.tipo, TransaccionVolumen.LODO_ENTERO)
        self.assertEqual(t.volumen_bbl, Decimal('120.00'))
        self.assertIsNone(t.lodo_producto)
        self.assertEqual(t.lodo_cantidad, Decimal('0.000'))
        self.assertEqual(t.origen_destino, 'Planta central')
