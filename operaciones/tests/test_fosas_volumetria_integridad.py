"""
Pruebas de integridad física y simetría de respuestas para Fosas, Tipos de Fosa,
Volumetría (Dejar en hoyo) y Listas Activas (Parte 12).
"""

import json
from datetime import date
from decimal import Decimal
from django.test import TestCase

from operaciones.models import (
    Pozo, Fosa, TipoFosa, CategoriaPerdidaItem, Producto, Equipo, MallaZaranda,
    ProductoActivoPozo, EquipoActivoPozo, MallaActivaPozo
)
from operaciones.models_daily_reports import ReporteDiario
from operaciones.models_inventario import VolumenFosaDia, TransaccionVolumen, VolumenHoyoDia


class FosasVolumetriaIntegridadTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(
            nombre='POZO TEST PARTE 12',
            estado='ACTIVO',
            spud_date_completado=True,
            moneda_simbolo='USD',
            moneda_secundaria='VES',
        )
        TipoFosa.sembrar_estandar(self.pozo)
        CategoriaPerdidaItem.sembrar_estandar(self.pozo)
        self.reporte = ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 20),
            tipo_lodo='WBM',
        )
        # Tanque 1 activo (código 1 = ACTIVA)
        self.fosa1 = Fosa.objects.create(
            pozo=self.pozo, numero=1, descripcion='Fosa Activa 1', capacidad=Decimal('500.00')
        )
        VolumenFosaDia.objects.create(
            reporte=self.reporte, fosa_numero=1, fosa_descripcion='Fosa Activa 1',
            capacidad=Decimal('500.00'), tipo_codigo=1, tipo_descripcion='Activa'
        )

        # Catálogos maestros para listas activas
        self.producto = Producto.objects.create(
            codigo='PROD-P12-01',
            descripcion='Bentonita Test',
            unidad='saco',
            libraje=Decimal('50.00'),
            gravedad=Decimal('2.60'),
            costo=Decimal('15.00'),
            cantidad=Decimal('100.00'),
        )
        self.equipo = Equipo.objects.create(
            codigo='EQ-P12-01',
            nombre='Zaranda Primaria',
            tipo_equipo='ZARANDA',
            posiciones_malla=3,
        )
        self.malla = MallaZaranda.objects.create(
            codigo='MAL-P12-01',
            descripcion='Malla API 100',
            mesh_size=100,
        )

    # -------------------------------------------------------------------------
    # 1. Configuración de Fosas / Tanques
    # -------------------------------------------------------------------------

    def test_fosa_guardar_capacidad_negativa_rechazada(self):
        payload = {
            'fosas': [
                {'numero': 1, 'descripcion': 'Pit 1', 'capacidad': -100.0}
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/pits/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertFalse(datos['success'])
        self.assertIn('errores_filas', datos)

    def test_fosa_guardar_numero_cero_o_negativo_rechazado(self):
        payload = {
            'fosas': [
                {'numero': 0, 'descripcion': 'Pit Cero', 'capacidad': 100.0}
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/pits/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertFalse(datos['success'])

    def test_fosa_guardar_valido(self):
        payload = {
            'fosas': [
                {'numero': 1, 'descripcion': 'Pit 1 Modificado', 'capacidad': 450.0},
                {'numero': 2, 'descripcion': 'Pit 2 Reserva', 'capacidad': 300.0},
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/pits/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(datos['success'])
        self.assertEqual(datos['total'], 2)
        self.assertEqual(self.pozo.fosas.count(), 2)

    # -------------------------------------------------------------------------
    # 2. Configuración de Tipos de Fosa (Pit Type Setup)
    # -------------------------------------------------------------------------

    def test_tipos_fosa_guardar_lista_vacia_rechazada(self):
        payload = {'tipos_fosa': []}
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/pit-types/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertFalse(datos['success'])
        self.assertIn('al menos un tipo', datos['error'])

    def test_tipos_fosa_guardar_valido(self):
        payload = {
            'tipos_fosa': [
                {'codigo': 0, 'descripcion': 'Vacía'},
                {'codigo': 1, 'descripcion': 'Activa'},
                {'codigo': 2, 'descripcion': 'Reserva'},
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/pit-types/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(datos['success'])
        self.assertEqual(datos['total'], 3)
        self.assertEqual(self.pozo.tipos_fosa.count(), 3)

    # -------------------------------------------------------------------------
    # 3. Listas Activas: Productos Activos
    # -------------------------------------------------------------------------

    def test_productos_activos_precio_negativo_rechazado(self):
        payload = {
            'productos_activos': [
                {
                    'producto_id': self.producto.pk,
                    'producto_codigo': self.producto.codigo,
                    'abreviatura': 'BENT',
                    'unit_size': 50.0,
                    'unidad': 'saco',
                    'precio': -10.0,
                    'precio_secundaria': 0.0,
                    'gravedad_especifica': 2.6,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/productos-activos/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertFalse(datos['success'])

    def test_productos_activos_guardar_valido(self):
        payload = {
            'productos_activos': [
                {
                    'producto_id': self.producto.pk,
                    'producto_codigo': self.producto.codigo,
                    'abreviatura': 'BENT',
                    'unit_size': 50.0,
                    'unidad': 'LB',
                    'empaque': 'SACO',
                    'precio': 12.50,
                    'precio_secundaria': 500.0,
                    'gravedad_especifica': 2.6,
                    'grupo_producto': 1,
                    'codigo_costo_diario': 1,
                    'categoria_costo_wmgt': 1,
                    'categoria_costo_cf': 1,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/productos-activos/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200, resp.json() if resp.status_code != 200 else None)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(datos['success'])
        self.assertEqual(datos['total'], 1)

    # -------------------------------------------------------------------------
    # 4. Listas Activas: Equipos Activos
    # -------------------------------------------------------------------------

    def test_equipos_activos_tarifas_negativas_rechazadas(self):
        payload = {
            'equipos_activos': [
                {
                    'equipo_id': self.equipo.pk,
                    'numero_serie': 'SN-001',
                    'descripcion': 'Zaranda Principal',
                    'precio_renta': -50.0,
                    'precio_standby': 20.0,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/equipos-activos/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertFalse(datos['success'])

    def test_equipos_activos_guardar_valido(self):
        payload = {
            'equipos_activos': [
                {
                    'equipo_id': self.equipo.pk,
                    'numero_serie': 'SN-001',
                    'descripcion': 'Zaranda Principal',
                    'precio_renta': 150.0,
                    'precio_standby': 75.0,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/equipos-activos/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(datos['success'])
        self.assertEqual(datos['total'], 1)

    # -------------------------------------------------------------------------
    # 5. Listas Activas: Mallas Activas
    # -------------------------------------------------------------------------

    def test_mallas_activas_precio_negativo_rechazado(self):
        payload = {
            'mallas_activas': [
                {
                    'malla_id': self.malla.pk,
                    'precio': -25.0,
                    'precio_secundaria': 0.0,
                    'descuento_porcentaje': 0.0,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/mallas-activas/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertFalse(datos['success'])

    def test_mallas_activas_descuento_excedido_rechazado(self):
        payload = {
            'mallas_activas': [
                {
                    'malla_id': self.malla.pk,
                    'precio': 50.0,
                    'precio_secundaria': 0.0,
                    'descuento_porcentaje': 120.0,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/mallas-activas/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertFalse(datos['success'])

    def test_mallas_activas_guardar_valido(self):
        payload = {
            'mallas_activas': [
                {
                    'malla_id': self.malla.pk,
                    'precio': 65.0,
                    'precio_secundaria': 2600.0,
                    'descuento_porcentaje': 10.0,
                }
            ]
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/mallas-activas/guardar/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(datos['success'])
        self.assertEqual(datos['total'], 1)

    # -------------------------------------------------------------------------
    # 6. Volumetría: Dejar en hoyo y normalización de respuestas
    # -------------------------------------------------------------------------

    def test_dejar_en_hoyo_asigna_categoria_por_defecto_si_se_omite(self):
        payload = {
            'parte': 'bajo_mecha',
            'volumen': 35.0,
            'fosa': 1,
            # Se omite 'perdida_codigo' intencionalmente
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/volumetria/dejar-en-hoyo/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        datos = resp.json()
        self.assertTrue(datos['ok'])
        self.assertTrue(datos['success'])
        self.assertEqual(datos['hoyo']['no_fluido']['bajo_mecha'], 35.0)

        # Verificar que la transacción se creó con la categoría estándar 7
        t = TransaccionVolumen.objects.filter(reporte=self.reporte, tipo=TransaccionVolumen.PERDIDA).first()
        self.assertIsNotNone(t)
        self.assertEqual(t.perdida_codigo, 7)
        self.assertEqual(t.volumen_bbl, Decimal('35.00'))

    def test_volumetria_error_normalizado_con_ok_y_success(self):
        payload = {
            'parte': 'parte_invalida_totalmente',
            'volumen': 20.0,
            'fosa': 1,
        }
        resp = self.client.post(
            f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/volumetria/dejar-en-hoyo/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        datos = resp.json()
        self.assertFalse(datos['ok'])
        self.assertFalse(datos['success'])
        self.assertIn('error', datos)
