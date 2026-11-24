import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse

from operaciones.models import (
    Pozo, WellHeaderInfo,
    Equipo, MallaZaranda, PropiedadEquipoTipo, ParametroBenchmark, ComponenteSarta
)
from operaciones.forms_pozo import CategoriaPerdidaItemForm


class TestCatalogosMaestrosComponentesIntegridad(TestCase):
    def setUp(self):
        self.client = Client()
        self.pozo = Pozo.objects.create(
            nombre="POZO CAT TEST",
            estado="CONFIGURACION",
            moneda_simbolo="USD",
        )

    def test_categoria_perdida_form_codigo_positivo(self):
        form_invalido = CategoriaPerdidaItemForm(data={'codigo': 0, 'descripcion': 'Perdida Cero', 'tipo': 'SUPERFICIE'})
        self.assertFalse(form_invalido.is_valid())
        self.assertIn('codigo', form_invalido.errors)

        form_negativo = CategoriaPerdidaItemForm(data={'codigo': -5, 'descripcion': 'Perdida Neg', 'tipo': 'SUPERFICIE'})
        self.assertFalse(form_negativo.is_valid())
        self.assertIn('codigo', form_negativo.errors)

        form_valido = CategoriaPerdidaItemForm(data={'codigo': 10, 'descripcion': 'Perdida Valida', 'tipo': 'SUPERFICIE'})
        self.assertTrue(form_valido.is_valid())

    def test_api_categorias_perdida_rechaza_lista_vacia(self):
        url = reverse('operaciones:api_categorias_perdida_guardar', kwargs={'pk': self.pozo.pk})
        res = self.client.post(url, data=json.dumps({'categorias': []}), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertFalse(data.get('success'))
        self.assertFalse(data.get('ok'))
        self.assertIn('al menos una categoría', data.get('error', '').lower())

    def test_api_categorias_perdida_guardar_valido(self):
        url = reverse('operaciones:api_categorias_perdida_guardar', kwargs={'pk': self.pozo.pk})
        payload = {
            'categorias': [
                {'codigo': 1, 'descripcion': 'Superficie', 'tipo': 'SUPERFICIE'},
                {'codigo': 2, 'descripcion': 'Subsuelo', 'tipo': 'SUBSUELO'},
            ]
        }
        res = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(data.get('ok'))
        self.assertEqual(self.pozo.categorias_perdida.count(), 2)

    def test_api_marketing_codes_guardar_normalizado(self):
        url = reverse('operaciones:api_marketing_codes_guardar', kwargs={'pk': self.pozo.pk})
        payload = {
            'primary_mud_type_codigo': 'WBM',
            'primary_mud_type_descripcion': 'Base Agua',
            'well_type_codigo': 'DEV',
            'well_type_descripcion': 'Desviado',
            'contract_type_codigo': 'DAY',
            'contract_type_descripcion': 'Tarifa Diaria',
            'completion_fluid_type_codigo': '',
            'completion_fluid_type_descripcion': ''
        }
        res = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(data.get('ok'))
        info = WellHeaderInfo.objects.get(pozo=self.pozo)
        self.assertEqual(info.primary_mud_type_codigo, 'WBM')
        self.assertTrue(info.marketing_codes_completado)

    def test_api_equipment_properties_guardar_normalizado(self):
        prop_def = PropiedadEquipoTipo.objects.create(
            tipo_equipo="ZARANDA", descripcion="Velocidad", unidad="RPM", orden=1
        )
        url = reverse('operaciones:api_equipment_properties_guardar', kwargs={'pk': self.pozo.pk})
        payload = {
            'propiedades': [
                {'propiedad_def_id': prop_def.pk, 'valor': '1200'}
            ]
        }
        res = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(data.get('ok'))

    def test_api_benchmark_guardar_normalizado(self):
        param = ParametroBenchmark.objects.create(
            grupo="COSTO", descripcion="Costo Objetivo", unidad="USD",
            tipo_fluido="AMBOS", tipo_dato="NUMERICO"
        )
        url_def = reverse('operaciones:api_benchmark_definiciones_guardar', kwargs={'pk': self.pozo.pk})
        payload_def = {'definiciones': [{'parametro_def_id': param.pk, 'orden': 1}]}
        res_def = self.client.post(url_def, data=json.dumps(payload_def), content_type='application/json')
        self.assertEqual(res_def.status_code, 200)
        self.assertTrue(res_def.json().get('ok'))

        url_tar = reverse('operaciones:api_benchmark_targets_guardar', kwargs={'pk': self.pozo.pk})
        payload_tar = {'targets': [{'parametro_def_id': param.pk, 'target_value': '5000'}]}
        res_tar = self.client.post(url_tar, data=json.dumps(payload_tar), content_type='application/json')
        self.assertEqual(res_tar.status_code, 200)
        self.assertTrue(res_tar.json().get('ok'))

    def test_api_equipo_crud_normalizado(self):
        url_create = reverse('operaciones:api_equipo_create')
        res = self.client.post(url_create, data=json.dumps({
            'codigo': 'EQ-TEST-01', 'nombre': 'Centrifuga de Alta Velocidad', 'tipo_equipo': 'CENTRIFUGA'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(data.get('ok'))
        equipo_id = data['equipo']['id']

        url_update = reverse('operaciones:api_equipo_update', kwargs={'pk': equipo_id})
        res_up = self.client.post(url_update, data=json.dumps({
            'codigo': 'EQ-TEST-01', 'nombre': 'Centrifuga Modificada', 'tipo_equipo': 'CENTRIFUGA'
        }), content_type='application/json')
        self.assertEqual(res_up.status_code, 200)
        self.assertTrue(res_up.json().get('ok'))

        url_del = reverse('operaciones:api_equipo_delete', kwargs={'pk': equipo_id})
        res_del = self.client.post(url_del)
        self.assertEqual(res_del.status_code, 200)
        self.assertTrue(res_del.json().get('ok'))

    def test_api_malla_crud_normalizado(self):
        url_create = reverse('operaciones:api_malla_create')
        res = self.client.post(url_create, data=json.dumps({
            'codigo': 'MAL-100', 'descripcion': 'Malla 100 mesh', 'mesh_size': 100
        }), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(data.get('ok'))
        malla_id = data['malla']['id']

        url_update = reverse('operaciones:api_malla_update', kwargs={'pk': malla_id})
        res_up = self.client.post(url_update, data=json.dumps({
            'codigo': 'MAL-100', 'descripcion': 'Malla 100 mesh extra', 'mesh_size': 105
        }), content_type='application/json')
        self.assertEqual(res_up.status_code, 200)
        self.assertTrue(res_up.json().get('ok'))

        url_del = reverse('operaciones:api_malla_delete', kwargs={'pk': malla_id})
        res_del = self.client.post(url_del)
        self.assertEqual(res_del.status_code, 200)
        self.assertTrue(res_del.json().get('ok'))

    def test_api_propiedad_equipo_crud_normalizado(self):
        url_create = reverse('operaciones:api_propiedad_equipo_create')
        res = self.client.post(url_create, data=json.dumps({
            'tipo_equipo': 'ZARANDA', 'descripcion': 'Presion Maxima', 'unidad': 'PSI', 'orden': 1
        }), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(data.get('ok'))
        prop_id = data['propiedad']['id']

        url_update = reverse('operaciones:api_propiedad_equipo_update', kwargs={'pk': prop_id})
        res_up = self.client.post(url_update, data=json.dumps({
            'tipo_equipo': 'ZARANDA', 'descripcion': 'Presion de Trabajo Maxima', 'unidad': 'PSI', 'orden': 2
        }), content_type='application/json')
        self.assertEqual(res_up.status_code, 200)
        self.assertTrue(res_up.json().get('ok'))

        url_del = reverse('operaciones:api_propiedad_equipo_delete', kwargs={'pk': prop_id})
        res_del = self.client.post(url_del)
        self.assertEqual(res_del.status_code, 200)
        self.assertTrue(res_del.json().get('ok'))

    def test_api_parametro_benchmark_crud_normalizado(self):
        url_create = reverse('operaciones:api_parametro_benchmark_create')
        res = self.client.post(url_create, data=json.dumps({
            'grupo': 'COSTO', 'descripcion': 'ROP Promedio', 'unidad': 'ft/hr',
            'tipo_fluido': 'AMBOS', 'tipo_dato': 'NUMERICO'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(data.get('ok'))
        param_id = data['parametro']['id']

        url_update = reverse('operaciones:api_parametro_benchmark_update', kwargs={'pk': param_id})
        res_up = self.client.post(url_update, data=json.dumps({
            'grupo': 'COSTO', 'descripcion': 'ROP Promedio Seccion', 'unidad': 'ft/hr',
            'tipo_fluido': 'AMBOS', 'tipo_dato': 'NUMERICO'
        }), content_type='application/json')
        self.assertEqual(res_up.status_code, 200)
        self.assertTrue(res_up.json().get('ok'))

        url_del = reverse('operaciones:api_parametro_benchmark_delete', kwargs={'pk': param_id})
        res_del = self.client.post(url_del)
        self.assertEqual(res_del.status_code, 200)
        self.assertTrue(res_del.json().get('ok'))

    def test_componente_sarta_geometria_tool_joint_y_crud_normalizado(self):
        url_create = reverse('operaciones:api_componente_sarta_create')
        # Invalido: tool_joint_id >= tool_joint_od
        payload_inv = {
            'codigo': 'DP-5-INV',
            'descripcion': 'Drill Pipe 5 pulg Invalido',
            'tipo': 'DRILL_PIPE',
            'od_in': '5.000',
            'id_in': '4.276',
            'tool_joint_od_in': '6.500',
            'tool_joint_id_in': '6.625',  # Invalido: tj_id > tj_od
            'tool_joint_length_in': '24.0',
            'largo_tramo_ft': '31.0',
        }
        res_inv = self.client.post(url_create, data=json.dumps(payload_inv), content_type='application/json')
        self.assertEqual(res_inv.status_code, 400)
        data_inv = res_inv.json()
        self.assertFalse(data_inv.get('ok'))
        self.assertIn('tool_joint_id_in', data_inv.get('errores', {}))

        # Valido: tool_joint_id < tool_joint_od
        payload_val = {
            'codigo': 'DP-5-VAL',
            'descripcion': 'Drill Pipe 5 pulg Valido',
            'tipo': 'DRILL_PIPE',
            'od_in': '5.000',
            'id_in': '4.276',
            'tool_joint_od_in': '6.500',
            'tool_joint_id_in': '3.250',
            'tool_joint_length_in': '24.0',
            'largo_tramo_ft': '31.0',
        }
        res_val = self.client.post(url_create, data=json.dumps(payload_val), content_type='application/json')
        self.assertEqual(res_val.status_code, 201)
        data_val = res_val.json()
        self.assertTrue(data_val.get('ok'))
        self.assertTrue(data_val.get('success'))
        comp_id = data_val['componente']['id']

        # Update
        url_update = reverse('operaciones:api_componente_sarta_update', kwargs={'pk': comp_id})
        payload_val['descripcion'] = 'Drill Pipe 5 pulg Actualizado'
        res_up = self.client.post(url_update, data=json.dumps(payload_val), content_type='application/json')
        self.assertEqual(res_up.status_code, 200)
        self.assertTrue(res_up.json().get('ok'))

        # Delete
        url_del = reverse('operaciones:api_componente_sarta_delete', kwargs={'pk': comp_id})
        res_del = self.client.post(url_del)
        self.assertEqual(res_del.status_code, 200)
        self.assertTrue(res_del.json().get('ok'))

