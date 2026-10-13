"""
Cerrar un intervalo como side track (punto 14 de docs/23_CORRECCIONES_REVISION_OCT.md).

Causa del error: "Cerrar intervalo" cerraba con los datos YA guardados. Si el usuario cambió el tipo a
Side Track en el formulario y pulsó Cerrar sin Guardar, el cambio se perdía y quedaba "Producción".
Ahora Cerrar guarda lo que está en el formulario y cierra en la misma operación.
"""

import json
from decimal import Decimal

from django.test import TestCase

from operaciones.models import IntervaloRevestimiento, Pozo


class CerrarIntervaloTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA')
        self.intervalo = IntervaloRevestimiento.objects.create(
            pozo=self.pozo, numero_intervalo=1, tipo='PRODUCCION', profundidad_ft=Decimal('5000'))

    def cerrar(self, **formulario):
        datos = {'numero_intervalo': 1, 'tipo': 'PRODUCCION', 'profundidad_ft': 5000}
        datos.update(formulario)
        respuesta = self.client.post(f'/api/pozos/{self.pozo.pk}/casing-intervals/{self.intervalo.pk}/cerrar/',
                                     json.dumps(datos), content_type='application/json')
        self.intervalo.refresh_from_db()
        return respuesta.status_code, respuesta.json()

    def test_cerrar_como_side_track_sin_guardar_antes(self):
        estado, datos = self.cerrar(tipo='SIDETRACK', profundidad_ft=5500)
        self.assertEqual(estado, 200, datos)
        self.assertTrue(self.intervalo.cerrado)
        self.assertEqual(self.intervalo.tipo, 'SIDETRACK')
        self.assertEqual(self.intervalo.profundidad_ft, Decimal('5500'))
        self.assertIn('Side Track', datos['mensaje'])

    def test_sin_tipo_no_se_cierra_ni_se_guarda(self):
        estado, datos = self.cerrar(tipo='')
        self.assertEqual(estado, 400)
        self.assertIn('el tipo', datos['error'])
        self.assertFalse(self.intervalo.cerrado)
        self.assertEqual(self.intervalo.tipo, 'PRODUCCION')

    def test_datos_invalidos_no_cierran(self):
        estado, _ = self.cerrar(profundidad_ft='abc')
        self.assertEqual(estado, 400)
        self.assertFalse(self.intervalo.cerrado)

    def test_un_intervalo_cerrado_no_se_vuelve_a_cerrar(self):
        self.cerrar()
        estado, datos = self.cerrar(tipo='SIDETRACK')
        self.assertEqual(estado, 400)
        self.assertIn('ya está cerrado', datos['error'])
        self.assertEqual(self.intervalo.tipo, 'PRODUCCION')
