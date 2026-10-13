"""
Papelera de pozos (docs/24_PAPELERA_Y_TIPOS_DE_DATOS.md).

Eliminar un pozo ya no borra nada: lo oculta de todas las pantallas y sus reportes quedan
intactos. Desde Pozos › Papelera se restaura tal como estaba.
"""

import json
from datetime import date

from django.test import TestCase

from operaciones.forms_pozo import PozoPaso1Form
from operaciones.models import Pozo, ReporteDiario


class PapeleraPozosTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA')
        ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13))

    def eliminar(self, confirmar):
        respuesta = self.client.post(f'/api/pozos/{self.pozo.pk}/eliminar/',
                                     json.dumps({'confirmar': confirmar}), content_type='application/json')
        return respuesta.status_code, respuesta.json()

    def test_sin_el_nombre_exacto_no_elimina(self):
        estado, _ = self.eliminar('pozo prueba')
        self.assertEqual(estado, 400)
        self.assertTrue(Pozo.objects.filter(pk=self.pozo.pk).exists())

    def test_eliminar_oculta_el_pozo_y_conserva_sus_reportes(self):
        estado, datos = self.eliminar('POZO PRUEBA')
        self.assertEqual(estado, 200, datos)
        self.assertFalse(Pozo.objects.filter(pk=self.pozo.pk).exists())
        self.assertIsNotNone(Pozo.todos.get(pk=self.pozo.pk).eliminado_en)
        self.assertEqual(ReporteDiario.objects.filter(pozo_id=self.pozo.pk).count(), 1)
        self.assertEqual(self.client.get(f'/pozos/{self.pozo.pk}/').status_code, 404)

    def test_la_papelera_lista_el_pozo_y_restaurar_lo_devuelve(self):
        self.eliminar('POZO PRUEBA')
        pagina = self.client.get('/pozos/papelera/')
        self.assertContains(pagina, 'POZO PRUEBA')
        respuesta = self.client.post(f'/api/pozos/{self.pozo.pk}/restaurar/')
        self.assertEqual(respuesta.status_code, 200)
        restaurado = Pozo.objects.get(pk=self.pozo.pk)
        self.assertIsNone(restaurado.eliminado_en)
        self.assertEqual(restaurado.reportes_diarios.count(), 1)

    def test_restaurar_un_pozo_que_no_esta_en_la_papelera_da_404(self):
        self.assertEqual(self.client.post(f'/api/pozos/{self.pozo.pk}/restaurar/').status_code, 404)

    def test_no_se_puede_crear_otro_pozo_con_el_nombre_de_uno_en_la_papelera(self):
        self.pozo.enviar_a_papelera()
        formulario = PozoPaso1Form({'nombre': 'pozo prueba'})
        self.assertFalse(formulario.is_valid())
        self.assertIn('papelera', formulario.errors['nombre'][0])
