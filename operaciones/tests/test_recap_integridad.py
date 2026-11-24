import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from operaciones.models import (
    Pozo, Producto, Equipo, MallaZaranda, WellHeaderInfo,
    IntervaloRevestimiento, Fosa, CategoriaPerdidaItem,
    TipoDistribucionTiempo, AlmacenCodigo, ProductoActivoPozo,
    EquipoActivoPozo, MallaActivaPozo, ParametroBenchmark,
    BenchmarkSeleccionado, BenchmarkTarget,
)
from operaciones.models_recap import RecapPozo


class RecapIntegridadTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.pozo_activo = Pozo.objects.create(
            nombre="Pozo Activo Recap",
            estado="ACTIVO",
        )
        self.pozo_cerrado = Pozo.objects.create(
            nombre="Pozo Cerrado Recap",
            estado="CERRADO",
        )

    def test_recap_guardar_textos_pozo_activo(self):
        url = reverse('operaciones:recap_pozo', args=[self.pozo_activo.pk])
        payload = {
            'resumen': 'Resumen operativo inicial',
            'conclusiones': 'Conclusiones del pozo activo',
            'recomendaciones': 'Recomendaciones futuras',
            'lecciones': 'Lecciones aprendidas',
        }
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertIn('guardado=1', response.url)

        recap = RecapPozo.objects.get(pozo=self.pozo_activo)
        self.assertEqual(recap.resumen, 'Resumen operativo inicial')
        self.assertEqual(recap.conclusiones, 'Conclusiones del pozo activo')
        self.assertEqual(recap.recomendaciones, 'Recomendaciones futuras')
        self.assertEqual(recap.lecciones, 'Lecciones aprendidas')

    def test_recap_guardar_textos_pozo_cerrado_rechazado(self):
        # Texto original
        recap = RecapPozo.objects.create(
            pozo=self.pozo_cerrado,
            resumen="Texto inmutable inicial",
            conclusiones="Conclusiones originales",
        )
        url = reverse('operaciones:recap_pozo', args=[self.pozo_cerrado.pk])
        payload = {
            'resumen': 'Intento de modificar resumen cerrado',
            'conclusiones': 'Intento de modificar conclusiones',
            'recomendaciones': 'Intento de recomendacion',
            'lecciones': 'Intento de leccion',
        }
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertIn('error_cerrado=1', response.url)

        # Verificar que no cambió nada en base de datos
        recap.refresh_from_db()
        self.assertEqual(recap.resumen, "Texto inmutable inicial")
        self.assertEqual(recap.conclusiones, "Conclusiones originales")

    def test_recap_render_pozo_activo(self):
        url = reverse('operaciones:recap_pozo', args=[self.pozo_activo.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context.get('error_cerrado'))
        content = response.content.decode('utf-8')
        self.assertNotIn('rc-aviso-error', content)
        self.assertNotIn('readonly', content)

    def test_recap_render_pozo_cerrado(self):
        url = reverse('operaciones:recap_pozo', args=[self.pozo_cerrado.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('readonly', content)
        self.assertIn('disabled', content)
        self.assertIn('rc-aviso-info', content)
        self.assertIn('El pozo está cerrado: los textos del reporte final están protegidos', content)

    def test_recap_render_con_error_cerrado_flag(self):
        url = reverse('operaciones:recap_pozo', args=[self.pozo_cerrado.pk]) + '?error_cerrado=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('error_cerrado'))
        content = response.content.decode('utf-8')
        self.assertIn('rc-aviso-error', content)
        self.assertIn('No se pueden modificar los textos de un pozo cerrado', content)


class SimetriaContratosViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.pozo = Pozo.objects.create(nombre="Pozo Simetria", estado="ACTIVO")
        self.producto = Producto.objects.create(
            codigo="PROD-SIM",
            descripcion="Producto Simetria",
            categoria="SOLIDO",
            unidad="SACO",
            cantidad=Decimal("0.00"),
            costo=Decimal("10.00"),
        )
        self.equipo = Equipo.objects.create(
            codigo="EQ-SIM",
            nombre="Equipo Simetria",
            tipo_equipo="ZARANDA",
        )
        self.malla = MallaZaranda.objects.create(
            codigo="MALLA-SIM",
            descripcion="Malla Simetria",
            mesh_size=100,
        )
        WellHeaderInfo.objects.create(pozo=self.pozo, operador="Operador Test")
        IntervaloRevestimiento.objects.create(
            pozo=self.pozo,
            numero_intervalo=1,
            tipo="CONDUCTOR",
            profundidad_ft=Decimal("500.00"),
        )
        Fosa.objects.create(pozo=self.pozo, numero=1, descripcion="Fosa 1", capacidad=Decimal("200.00"))
        CategoriaPerdidaItem.objects.create(pozo=self.pozo, codigo=1, descripcion="Hueco", tipo="SUPERFICIE")
        TipoDistribucionTiempo.objects.create(pozo=self.pozo, numero=1, descripcion="Perforando", tipo="OPERACIONAL")
        AlmacenCodigo.objects.create(pozo=self.pozo, codigo="ALM-1", nombre="Almacen Central")
        ProductoActivoPozo.objects.create(pozo=self.pozo, producto=self.producto)
        EquipoActivoPozo.objects.create(pozo=self.pozo, equipo=self.equipo, numero_serie="SERIE-1")
        MallaActivaPozo.objects.create(pozo=self.pozo, malla=self.malla)
        param = ParametroBenchmark.objects.create(descripcion="Param BM", grupo="REOLOGIA", unidad="ppg")
        BenchmarkSeleccionado.objects.create(pozo=self.pozo, parametro=param)

    def test_simetria_api_pozo_eliminar(self):
        url = reverse('operaciones:api_pozo_eliminar', args=[self.pozo.pk])

        # 1. JSON inválido
        r1 = self.client.post(url, data="bad-json", content_type="application/json")
        self.assertEqual(r1.status_code, 400)
        d1 = r1.json()
        self.assertIn('success', d1)
        self.assertIn('ok', d1)
        self.assertFalse(d1['success'])
        self.assertFalse(d1['ok'])

        # 2. Confirmación incorrecta
        r2 = self.client.post(url, data=json.dumps({'confirmar': 'Wrong Name'}), content_type="application/json")
        self.assertEqual(r2.status_code, 400)
        d2 = r2.json()
        self.assertFalse(d2['success'])
        self.assertFalse(d2['ok'])

        # 3. Confirmación correcta
        r3 = self.client.post(url, data=json.dumps({'confirmar': self.pozo.nombre}), content_type="application/json")
        self.assertEqual(r3.status_code, 200)
        d3 = r3.json()
        self.assertTrue(d3['success'])
        self.assertTrue(d3['ok'])

    def test_simetria_get_endpoints_views(self):
        endpoints = [
            reverse('operaciones:api_productos_list'),
            reverse('operaciones:api_producto_detail', args=[self.producto.pk]),
            reverse('operaciones:api_pozos_plantillas'),
            reverse('operaciones:api_pozo_detail', args=[self.pozo.pk]),
            reverse('operaciones:api_well_header_detail', args=[self.pozo.pk]),
            reverse('operaciones:api_intervalos_list', args=[self.pozo.pk]),
            reverse('operaciones:api_pits_list', args=[self.pozo.pk]),
            reverse('operaciones:api_categorias_perdida_list', args=[self.pozo.pk]),
            reverse('operaciones:api_general_setup_detail', args=[self.pozo.pk]),
            reverse('operaciones:api_almacenes_list', args=[self.pozo.pk]),
            reverse('operaciones:api_tipos_distribucion_list', args=[self.pozo.pk]),
            reverse('operaciones:api_equipos_list'),
            reverse('operaciones:api_mallas_list'),
            reverse('operaciones:api_productos_activos_list', args=[self.pozo.pk]),
            reverse('operaciones:api_equipos_activos_list', args=[self.pozo.pk]),
            reverse('operaciones:api_mallas_activas_list', args=[self.pozo.pk]),
            reverse('operaciones:api_equipment_properties_detail', args=[self.pozo.pk]),
            reverse('operaciones:api_benchmark_definiciones_detail', args=[self.pozo.pk]),
            reverse('operaciones:api_benchmark_targets_detail', args=[self.pozo.pk]),
        ]

        for url in endpoints:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Falla en {url}")
            data = res.json()
            self.assertTrue(data.get('success'), f"'success' debe ser True en {url}")
            self.assertTrue(data.get('ok'), f"'ok' debe ser True en {url}")

    def test_simetria_producto_mutaciones(self):
        # 1. Crear producto con error de validación
        r_err = self.client.post(
            reverse('operaciones:api_producto_create'),
            data=json.dumps({'codigo': ''}),
            content_type="application/json"
        )
        self.assertEqual(r_err.status_code, 400)
        d_err = r_err.json()
        self.assertFalse(d_err['success'])
        self.assertFalse(d_err['ok'])

        # 2. Crear producto exitoso
        r_ok = self.client.post(
            reverse('operaciones:api_producto_create'),
            data=json.dumps({
                'codigo': 'BARITA-NEW',
                'descripcion': 'Barita Densificante',
                'categoria': 'SOLIDO',
                'unidad': 'SACO',
                'costo': '15.50',
                'cantidad': '10.00',
            }),
            content_type="application/json"
        )
        self.assertEqual(r_ok.status_code, 201)
        d_ok = r_ok.json()
        self.assertTrue(d_ok['success'])
        self.assertTrue(d_ok['ok'])
        nuevo_id = d_ok['producto']['id']

        # 3. Eliminar producto con stock > 0 rechazado
        r_del_err = self.client.delete(reverse('operaciones:api_producto_delete', args=[nuevo_id]))
        self.assertEqual(r_del_err.status_code, 400)
        d_del_err = r_del_err.json()
        self.assertFalse(d_del_err['success'])
        self.assertFalse(d_del_err['ok'])

        # 4. Actualizar producto a stock 0
        r_up = self.client.post(
            reverse('operaciones:api_producto_update', args=[nuevo_id]),
            data=json.dumps({'cantidad': '0.00'}),
            content_type="application/json"
        )
        self.assertEqual(r_up.status_code, 200)
        d_up = r_up.json()
        self.assertTrue(d_up['success'])
        self.assertTrue(d_up['ok'])

        # 5. Eliminar producto con stock 0 exitoso
        r_del_ok = self.client.delete(reverse('operaciones:api_producto_delete', args=[nuevo_id]))
        self.assertEqual(r_del_ok.status_code, 200)
        d_del_ok = r_del_ok.json()
        self.assertTrue(d_del_ok['success'])
        self.assertTrue(d_del_ok['ok'])
