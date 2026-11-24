"""
Pruebas de la Matriz de Modificación del Pozo (/pozos/<pk>/modificar/).
Permite corregir errores cometidos durante la creación del pozo (Wizard y Spud Date).
"""

from datetime import date
from decimal import Decimal
from django.test import TestCase
from operaciones.models import Pozo, WellHeaderInfo
from operaciones.models_daily_reports import ReporteDiario


class ModificarPozoTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(
            nombre='POZO ORIGINAL',
            estado='ACTIVO',
            sistema_unidades='STANDARD_OILFIELD',
            moneda_simbolo='USD',
            moneda_decimales=2,
            tasa_impuesto=Decimal('16.00'),
            spud_date_completado=True,
            fecha_primera_captura=date(2026, 10, 1),
            tipo_fluido_inicial='WATER_BASE',
            categoria_perdida_tipo='MI',
        )
        self.info = WellHeaderInfo.objects.create(
            pozo=self.pozo,
            operador='OPERADOR A',
            field_area='CAMPO A',
            nombre_taladro='TALADRO-01',
            contratista='CONTRATISTA A',
            spud_date=date(2026, 10, 1),
        )

    def test_get_pantalla_modificar_muestra_datos_actuales(self):
        resp = self.client.get(f'/pozos/{self.pozo.pk}/modificar/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'POZO ORIGINAL')
        self.assertContains(resp, 'OPERADOR A')
        self.assertContains(resp, 'CAMPO A')
        self.assertContains(resp, 'TALADRO-01')

    def test_post_modificar_corrige_datos_exitosamente(self):
        datos = {
            'nombre': 'POZO CORREGIDO',
            'operador': 'NUEVO OPERADOR',
            'field_area': 'NUEVO CAMPO',
            'nombre_taladro': 'TALADRO-99',
            'contratista': 'NUEVO CONTRATISTA',
            'sistema_unidades': 'SI_METRIC',
            'moneda_simbolo': 'EUR',
            'moneda_decimales': '3',
            'tasa_impuesto': '12.50',
            'moneda_secundaria': 'USD',
            'cobrar_en_secundaria': 'on',
            'spud_date': '2026-10-05',
            'tipo_fluido_inicial': 'OIL_BASE',
            'con_tratamiento_disposicion': 'on',
            'numero_control_logit': 'LOG-777',
            'categoria_perdida_tipo': 'UK',
        }
        resp = self.client.post(f'/pozos/{self.pozo.pk}/modificar/', data=datos)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(f'/pozos/{self.pozo.pk}/', resp.url)

        self.pozo.refresh_from_db()
        self.info.refresh_from_db()

        self.assertEqual(self.pozo.nombre, 'POZO CORREGIDO')
        self.assertEqual(self.pozo.sistema_unidades, 'SI_METRIC')
        self.assertEqual(self.pozo.moneda_simbolo, 'EUR')
        self.assertEqual(self.pozo.moneda_decimales, 3)
        self.assertEqual(self.pozo.tasa_impuesto, Decimal('12.50'))
        self.assertEqual(self.pozo.moneda_secundaria, 'USD')
        self.assertTrue(self.pozo.cobrar_en_secundaria)
        self.assertEqual(self.pozo.fecha_primera_captura, date(2026, 10, 5))
        self.assertEqual(self.pozo.tipo_fluido_inicial, 'OIL_BASE')
        self.assertTrue(self.pozo.con_tratamiento_disposicion)
        self.assertEqual(self.pozo.numero_control_logit, 'LOG-777')
        self.assertEqual(self.pozo.categoria_perdida_tipo, 'UK')

        self.assertEqual(self.info.operador, 'NUEVO OPERADOR')
        self.assertEqual(self.info.field_area, 'NUEVO CAMPO')
        self.assertEqual(self.info.nombre_taladro, 'TALADRO-99')
        self.assertEqual(self.info.contratista, 'NUEVO CONTRATISTA')
        self.assertEqual(self.info.spud_date, date(2026, 10, 5))
        self.assertEqual(self.info.primary_mud_type_codigo, 'OIL_BASE')
        self.assertEqual(self.info.primary_mud_type_descripcion, 'Base Aceite')

    def test_nombre_duplicado_rechazado(self):
        Pozo.objects.create(nombre='OTRO POZO')
        datos = {
            'nombre': 'OTRO POZO',
            'sistema_unidades': 'STANDARD_OILFIELD',
            'moneda_simbolo': 'USD',
            'moneda_decimales': '2',
            'tasa_impuesto': '0',
            'categoria_perdida_tipo': 'MI',
        }
        resp = self.client.post(f'/pozos/{self.pozo.pk}/modificar/', data=datos)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Ya existe un pozo con el nombre', resp.context['form'].errors['nombre'][0])

    def test_nombre_en_papelera_rechazado(self):
        p_papelera = Pozo.objects.create(nombre='POZO EN PAPELERA')
        p_papelera.enviar_a_papelera()

        datos = {
            'nombre': 'POZO EN PAPELERA',
            'sistema_unidades': 'STANDARD_OILFIELD',
            'moneda_simbolo': 'USD',
            'moneda_decimales': '2',
            'tasa_impuesto': '0',
            'categoria_perdida_tipo': 'MI',
        }
        resp = self.client.post(f'/pozos/{self.pozo.pk}/modificar/', data=datos)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('en la papelera', resp.context['form'].errors['nombre'][0])

    def test_tasa_impuesto_fuera_de_rango(self):
        datos = {
            'nombre': 'POZO VALIDO',
            'sistema_unidades': 'STANDARD_OILFIELD',
            'moneda_simbolo': 'USD',
            'moneda_decimales': '2',
            'tasa_impuesto': '150',  # > 100
            'categoria_perdida_tipo': 'MI',
        }
        resp = self.client.post(f'/pozos/{self.pozo.pk}/modificar/', data=datos)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['form'].errors['tasa_impuesto'])

    def test_modificar_pozo_cerrado_rechazado_por_post(self):
        self.pozo.estado = 'CERRADO'
        self.pozo.save()
        datos = {
            'nombre': 'INTENTO EN CERRADO',
            'sistema_unidades': 'STANDARD_OILFIELD',
            'moneda_simbolo': 'USD',
            'moneda_decimales': '2',
            'tasa_impuesto': '0',
            'categoria_perdida_tipo': 'MI',
        }
        # Petición normal redirige
        resp = self.client.post(f'/pozos/{self.pozo.pk}/modificar/', data=datos)
        self.assertEqual(resp.status_code, 302)
        self.pozo.refresh_from_db()
        self.assertEqual(self.pozo.nombre, 'POZO ORIGINAL')

        # Petición AJAX / JSON devuelve 400
        resp_ajax = self.client.post(
            f'/pozos/{self.pozo.pk}/modificar/',
            data=datos,
            headers={'x-requested-with': 'XMLHttpRequest'}
        )
        self.assertEqual(resp_ajax.status_code, 400)
        self.assertIn('cerrado', resp_ajax.json()['error'])

    def test_modificar_pozo_cerrado_pantalla_deshabilita_guardado(self):
        self.pozo.estado = 'CERRADO'
        self.pozo.save()
        resp = self.client.get(f'/pozos/{self.pozo.pk}/modificar/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['pozo_cerrado'])
        self.assertContains(resp, 'Este pozo se encuentra actualmente en estado')
        self.assertContains(resp, 'disabled')

    def test_modificar_pozo_con_reportes_bloquea_moneda_principal(self):
        ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 10), profundidad_actual=1000)
        datos = {
            'nombre': 'POZO ORIGINAL',
            'sistema_unidades': 'STANDARD_OILFIELD',
            'moneda_simbolo': 'EUR',  # Cambio de USD a EUR
            'moneda_decimales': '2',
            'tasa_impuesto': '0',
            'categoria_perdida_tipo': 'MI',
        }
        resp = self.client.post(f'/pozos/{self.pozo.pk}/modificar/', data=datos)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('ya tiene reportes registrados', resp.context['form'].errors['moneda_simbolo'][0])

    def test_modificar_pozo_con_reportes_bloquea_cobrar_en_secundaria(self):
        ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 10), profundidad_actual=1000)
        datos = {
            'nombre': 'POZO ORIGINAL',
            'sistema_unidades': 'STANDARD_OILFIELD',
            'moneda_simbolo': 'USD',
            'moneda_decimales': '2',
            'tasa_impuesto': '0',
            'moneda_secundaria': 'VES',
            'cobrar_en_secundaria': 'on',  # Cambio de False a True
            'categoria_perdida_tipo': 'MI',
        }
        resp = self.client.post(f'/pozos/{self.pozo.pk}/modificar/', data=datos)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('la moneda de cobro no se puede cambiar', resp.context['form'].errors['cobrar_en_secundaria'][0])

    def test_modificar_pozo_con_reportes_rechaza_spud_date_posterior(self):
        ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 10), profundidad_actual=1000)
        datos = {
            'nombre': 'POZO ORIGINAL',
            'sistema_unidades': 'STANDARD_OILFIELD',
            'moneda_simbolo': 'USD',
            'moneda_decimales': '2',
            'tasa_impuesto': '0',
            'spud_date': '2026-10-15',  # Posterior al 10/10/2026
            'categoria_perdida_tipo': 'MI',
        }
        resp = self.client.post(f'/pozos/{self.pozo.pk}/modificar/', data=datos)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('no puede ser posterior a la fecha del primer reporte', resp.context['form'].errors['spud_date'][0])

    def test_modificar_pozo_con_reportes_permite_otros_campos_con_moneda_omitida(self):
        ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 10), profundidad_actual=1000)
        # Simulamos POST desde frontend con input moneda_simbolo disabled (no enviado en el POST)
        datos = {
            'nombre': 'POZO CON NOMBRE ACTUALIZADO',
            'operador': 'NUEVO OPERADOR PETROLERO',
            'sistema_unidades': 'STANDARD_OILFIELD',
            'moneda_decimales': '2',
            'tasa_impuesto': '0',
            'spud_date': '2026-10-01',  # Anterior o igual al primer reporte
            'categoria_perdida_tipo': 'MI',
        }
        resp = self.client.post(f'/pozos/{self.pozo.pk}/modificar/', data=datos)
        self.assertEqual(resp.status_code, 302)

        self.pozo.refresh_from_db()
        self.info.refresh_from_db()
        self.assertEqual(self.pozo.nombre, 'POZO CON NOMBRE ACTUALIZADO')
        self.assertEqual(self.info.operador, 'NUEVO OPERADOR PETROLERO')
        self.assertEqual(self.pozo.moneda_simbolo, 'USD')  # Conservada sin alteración
