"""
Servicios del pozo (pestaña 8, "Servicios"; docs/25_SERVICIOS_DEL_POZO.md): ingenieros, trailers y
demás servicios del contrato se cobran por día con su tarifa, aparte del inventario de químicos,
y suman en la columna del resumen de costos que corresponde a su categoría.
"""

import json
from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from operaciones import volumetria as vol
from operaciones.models import Pozo
from operaciones.models_daily_reports import ReporteDiario
from operaciones.models_servicios import ServicioPozo, ServicioDia
from operaciones.recap_pozo import datos_recap
from operaciones.views_inventario import resumen_costos

FLUIDOS, SOLIDOS, TRAILER = 2, 3, 5


class ServiciosDelPozoTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO SERVICIOS')
        self.dia1 = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 12))
        self.dia2 = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13))
        self.fluidos = ServicioPozo.objects.create(pozo=self.pozo, descripcion='Ingeniería de fluidos',
                                                   categoria_costo=FLUIDOS, tarifa_diaria=Decimal('1500'))
        self.solidos = ServicioPozo.objects.create(pozo=self.pozo, descripcion='Control de sólidos',
                                                   categoria_costo=SOLIDOS, tarifa_diaria=Decimal('800'))

    def _url(self, nombre, reporte, **extra):
        return reverse(f'operaciones:{nombre}', kwargs={'pk': self.pozo.pk, 'reporte_pk': reporte.pk, **extra})

    def _post(self, nombre, reporte, cuerpo, **extra):
        return self.client.post(self._url(nombre, reporte, **extra), json.dumps(cuerpo), content_type='application/json')

    def _cobrar(self, reporte, *filas):
        return self._post('api_volumetria_guardar', reporte, {'servicios': [
            {'servicio_id': s.id, 'dias': dias, 'tarifa': tarifa} for s, dias, tarifa in filas]})

    def test_quimicos_no_es_categoria_de_servicio(self):
        self.assertNotIn(vol.CATEGORIA_QUIMICOS, vol.CATEGORIAS_SERVICIO)
        self.assertEqual(set(vol.CATEGORIAS_SERVICIO), {2, 3, 4, 5})

    def test_guardar_dias_cobrados_genera_costo_diario_y_acumulado(self):
        self.assertTrue(self._cobrar(self.dia1, (self.fluidos, 1, None), (self.solidos, 1, None)).json()['ok'])
        datos = self._cobrar(self.dia2, (self.fluidos, 1, None)).json()
        fila = next(s for s in datos['servicios'] if s['servicio_id'] == self.fluidos.id)
        self.assertEqual(fila['costo_diario'], 1500)
        self.assertEqual(fila['costo_acumulado'], 3000)
        costos = {c['categoria']: c for c in datos['costos']}
        self.assertEqual(costos[FLUIDOS]['diario'], 1500)
        self.assertEqual(costos[SOLIDOS]['diario'], 0)
        self.assertEqual(costos[SOLIDOS]['acumulado'], 800)

    def test_dia_sin_cobro_no_guarda_fila(self):
        self._cobrar(self.dia1, (self.fluidos, 0, None))
        self.assertFalse(ServicioDia.objects.exists())

    def test_tarifa_del_dia_se_conserva_si_cambia_el_contrato(self):
        self._cobrar(self.dia1, (self.fluidos, 1, None))
        self._post('api_servicio_guardar', self.dia2, {'id': self.fluidos.id, 'descripcion': 'Ingeniería de fluidos',
                                                       'categoria_costo': FLUIDOS, 'tarifa_diaria': 2000})
        dia = ServicioDia.objects.get(reporte=self.dia1)
        self.assertEqual(dia.tarifa, Decimal('1500'))
        self.assertEqual(dia.costo, Decimal('1500'))

    def test_tarifa_corregida_para_un_dia(self):
        self._cobrar(self.dia1, (self.fluidos, 1, 1200))
        self.assertEqual(ServicioDia.objects.get(reporte=self.dia1).costo, Decimal('1200'))

    def test_resumen_de_costos_por_columna(self):
        trailer = ServicioPozo.objects.create(pozo=self.pozo, descripcion='Trailer', categoria_costo=TRAILER,
                                              tarifa_diaria=Decimal('250'))
        self._cobrar(self.dia1, (self.fluidos, 1, None), (self.solidos, 1, None), (trailer, 1, None))
        self._cobrar(self.dia2, (self.fluidos, 1, None))
        diario, acumulado, items = resumen_costos(self.pozo, self.dia2)
        self.assertEqual(diario['df_chem'], 1500)
        self.assertEqual(diario['ife_sc'], 0)
        self.assertEqual(acumulado['df_chem'], 3000)
        self.assertEqual(acumulado['ife_sc'], 800)
        self.assertEqual(acumulado['other_cost'], 250)
        self.assertEqual(acumulado['total'], 4050)
        self.assertEqual([(i['descripcion'], i['unidad']) for i in items], [('Ingeniería de fluidos', 'días')])

    def test_recap_del_pozo(self):
        self._cobrar(self.dia1, (self.fluidos, 1, None), (self.solidos, 1, None))
        self._cobrar(self.dia2, (self.fluidos, 1, None))
        costos = datos_recap(self.pozo)['costos']
        self.assertEqual(costos['total'], 3800)

    def test_crear_servicio_valida_categoria_y_tarifa(self):
        sin_categoria = self._post('api_servicio_guardar', self.dia1, {'descripcion': 'Filtración', 'tarifa_diaria': 100})
        self.assertEqual(sin_categoria.status_code, 400)
        quimicos = self._post('api_servicio_guardar', self.dia1, {'descripcion': 'X', 'categoria_costo': 1, 'tarifa_diaria': 1})
        self.assertEqual(quimicos.status_code, 400)
        ok = self._post('api_servicio_guardar', self.dia1, {'descripcion': 'Filtración', 'categoria_costo': SOLIDOS,
                                                            'tarifa_diaria': 300})
        self.assertTrue(ok.json()['ok'])
        self.assertTrue(ServicioPozo.objects.filter(descripcion='Filtración', tarifa_diaria=300).exists())

    def test_quitar_servicio_con_dias_solo_lo_desactiva(self):
        self._cobrar(self.dia1, (self.fluidos, 1, None))
        self._post('api_servicio_eliminar', self.dia2, {}, servicio_pk=self.fluidos.id)
        self.fluidos.refresh_from_db()
        self.assertFalse(self.fluidos.activo)
        self.assertEqual(resumen_costos(self.pozo, self.dia2)[1]['df_chem'], 1500)
        self._post('api_servicio_eliminar', self.dia2, {}, servicio_pk=self.solidos.id)
        self.assertFalse(ServicioPozo.objects.filter(pk=self.solidos.id).exists())

    def test_servicio_inactivo_no_aparece_si_no_tiene_dias_en_el_reporte(self):
        self._cobrar(self.dia1, (self.fluidos, 1, None))
        self.fluidos.activo = False
        self.fluidos.save()
        ids_dia1 = [s['servicio_id'] for s in self.client.get(self._url('api_volumetria_detail', self.dia1)).json()['servicios']]
        ids_dia2 = [s['servicio_id'] for s in self.client.get(self._url('api_volumetria_detail', self.dia2)).json()['servicios']]
        self.assertIn(self.fluidos.id, ids_dia1)
        self.assertNotIn(self.fluidos.id, ids_dia2)

    def test_servicio_de_otro_pozo_se_rechaza(self):
        otro = Pozo.objects.create(nombre='OTRO')
        ajeno = ServicioPozo.objects.create(pozo=otro, descripcion='Ajeno', categoria_costo=FLUIDOS, tarifa_diaria=1)
        self.assertEqual(self._cobrar(self.dia1, (ajeno, 1, None)).status_code, 400)
