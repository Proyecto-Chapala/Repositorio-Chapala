"""
Pérdidas, transferencias y devoluciones modificables (punto 11 de docs/23_CORRECCIONES_REVISION_OCT.md):
cualquier movimiento del reporte se puede eliminar, y los que solo mueven volumen se pueden editar.
Cada cambio repite toda la línea de tiempo del pozo; si algo deja de ser posible, no se guarda.
"""

import json
from datetime import date
from decimal import Decimal
from unittest import mock

from django.test import TestCase

from operaciones import licencia
from operaciones.models import CategoriaPerdidaItem, Fosa, Pozo, TipoFosa
from operaciones.models_daily_reports import ReporteDiario
from operaciones.models_inventario import TransaccionVolumen, VolumenFosaDia

ACTIVA, RESERVA, VACIA = 1, 2, 0


class EditarMovimientosTests(TestCase):

    def setUp(self):
        # La licencia no es lo que se prueba aquí: se simula activa para llegar a la API.
        parche = mock.patch.object(licencia, 'estado_licencia',
                                   return_value={'estado': licencia.ACTIVA, 'aviso': False, 'dias_restantes': None})
        parche.start()
        self.addCleanup(parche.stop)

        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA')
        TipoFosa.sembrar_estandar(self.pozo)
        CategoriaPerdidaItem.sembrar_estandar(self.pozo)
        self.reporte = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13))
        for numero, nombre, tipo in ((1, 'Activo 1', ACTIVA), (2, 'Reserva 1', RESERVA), (3, 'Vacío', VACIA)):
            Fosa.objects.create(pozo=self.pozo, numero=numero, descripcion=nombre, capacidad=Decimal('500'))
            VolumenFosaDia.objects.create(reporte=self.reporte, fosa_numero=numero, fosa_descripcion=nombre,
                                          tipo_codigo=tipo)
        self.codigo_perdida = self.pozo.categorias_perdida.order_by('codigo').first().codigo
        self.base = f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/volumetria/transaccion/'
        self.post('', {'tipo': 'QUIMICOS', 'fosa': 2, 'agua': 300})                                  # #1
        self.post('', {'tipo': 'TRANSFERENCIA', 'fosa': 2, 'destino': 1, 'volumen': 100})            # #2
        self.post('', {'tipo': 'PERDIDA', 'fosa': 1, 'volumen': 20, 'perdida_codigo': self.codigo_perdida})  # #3
        self.post('', {'tipo': 'DEVOLUCION', 'fosa': 2, 'volumen': 10, 'destino_texto': 'Almacén'})  # #4

    def post(self, ruta, datos=None):
        respuesta = self.client.post(self.base + ruta, json.dumps(datos or {}), content_type='application/json')
        return respuesta.status_code, respuesta.json()

    def calculado(self, datos, grupo):
        return next(g for g in datos['grupos'] if g['grupo'] == grupo)['calculado']

    def test_editar_un_movimiento_que_no_es_el_ultimo(self):
        estado, datos = self.post('2/editar/', {'fosa': 2, 'destino': 1, 'volumen': 150})
        self.assertEqual(estado, 200, datos)
        self.assertEqual(TransaccionVolumen.objects.get(secuencia=2).volumen_bbl, Decimal('150.00'))
        self.assertEqual(self.calculado(datos, 'ACTIVO'), 130)      # 150 − 20 de pérdida
        self.assertEqual(self.calculado(datos, 'RESERVA'), 140)     # 300 − 150 − 10

    def test_editar_el_tipo_de_perdida_y_el_tanque(self):
        otra = self.pozo.categorias_perdida.order_by('codigo')[1].codigo
        estado, datos = self.post('3/editar/', {'fosa': 2, 'volumen': 5, 'perdida_codigo': otra})
        self.assertEqual(estado, 200, datos)
        perdida = TransaccionVolumen.objects.get(secuencia=3)
        self.assertEqual((perdida.fosa_numero, perdida.perdida_codigo), (2, otra))
        self.assertEqual(self.calculado(datos, 'ACTIVO'), 100)

    def test_eliminar_un_movimiento_que_no_es_el_ultimo(self):
        estado, datos = self.post('2/eliminar/')
        self.assertEqual(estado, 200, datos)
        self.assertFalse(TransaccionVolumen.objects.filter(secuencia=2).exists())
        self.assertEqual([m['secuencia'] for m in datos['movimientos']], [1, 3, 4])

    def test_un_cambio_imposible_no_se_guarda(self):
        estado, datos = self.post('2/editar/', {'fosa': 2, 'destino': 3, 'volumen': 100})   # tanque sin tipo
        self.assertEqual(estado, 400)
        self.assertIn('No se puede modificar', datos['error'])
        self.assertEqual(TransaccionVolumen.objects.get(secuencia=2).destino_numero, 1)

    def test_quimicos_no_se_editan_pero_se_eliminan(self):
        estado, datos = self.post('1/editar/', {'fosa': 2, 'volumen': 10})
        self.assertEqual(estado, 400)
        self.assertIn('elimínalo y cárgalo de nuevo', datos['error'])
        estado_actual = self.client.get(self.base.replace('transaccion/', '')).json()
        editables = {m['secuencia']: m['editable'] for m in estado_actual['movimientos']}
        self.assertEqual(editables, {1: False, 2: True, 3: True, 4: True})
        estado, datos = self.post('1/eliminar/')
        self.assertEqual(estado, 200, datos)

    def test_validaciones_iguales_al_registro(self):
        estado, datos = self.post('2/editar/', {'fosa': 2, 'destino': 2, 'volumen': 10})
        self.assertEqual(estado, 400)
        self.assertIn('el mismo', datos['error'])
        estado, datos = self.post('4/editar/', {'fosa': 2, 'volumen': 10, 'destino_texto': ''})
        self.assertEqual(estado, 400)
        self.assertIn('a dónde se devuelve', datos['error'])

    def test_solo_movimientos_de_este_reporte(self):
        estado, datos = self.post('99/eliminar/')
        self.assertEqual(estado, 400)
        self.assertIn('no es de este reporte', datos['error'])
