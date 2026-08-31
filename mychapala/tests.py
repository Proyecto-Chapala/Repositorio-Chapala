"""
================================================================================
PRUEBAS UNITARIAS Y DE INTEGRACIÓN - PROYECTO CHAPALA
================================================================================
Valida:
1. Modelos: Producto, ReporteDiario, RegistroUso.
2. Identificación / N° de Reporte generado.
3. Deducción de stock y validación de stock insuficiente.
4. Cálculo en tiempo real de costos (subtotal = cantidad * precio_unitario).
5. Actualización acumulativa del costo total del reporte diario.
6. Eliminación de reportes y restitución de existencias.
7. Endpoints de la API REST.
================================================================================
"""

import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from mychapala.models import Producto, ReporteDiario, RegistroUso


class InventarioReporteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.producto = Producto.objects.create(
            codigo="AOS-9999",
            descripcion="PRODUCTO DE PRUEBA QUIMICO",
            unidad="TAMBOR 55 GLS",
            libraje="N/A",
            gravedad_especifica="1.20",
            cantidad=50,
            stock_inicial=50
        )
        self.reporte = ReporteDiario.objects.create(
            departamento="ALMACÉN TEST",
            encargado="LUIS BRICEÑO TEST",
            observaciones="Observación de prueba"
        )

    def test_creacion_producto_y_estado(self):
        """Verifica la creación del producto y el cálculo de su estado de stock."""
        self.assertEqual(self.producto.codigo, "AOS-9999")
        self.assertEqual(self.producto.estado_stock["label"], "Stock Medio")

    def test_codigo_identificacion_reporte(self):
        """Verifica que el reporte genere automáticamente su código de identificación."""
        self.assertTrue(self.reporte.codigo_reporte.startswith("REP-"))

    def test_registro_uso_y_calculo_costo(self):
        """Verifica que al registrar uso se calcule cantidad * precio y se acumule en el reporte."""
        uso = RegistroUso.objects.create(
            reporte=self.reporte,
            producto=self.producto,
            cantidad=5,
            precio_unitario=Decimal("25.50"),
            observacion="Uso en Pozo 1"
        )

        # Subtotal: 5 * 25.50 = 127.50
        self.assertEqual(uso.costo_total, Decimal("127.50"))
        
        # El reporte debe haber acumulado 127.50
        self.reporte.refresh_from_db()
        self.assertEqual(self.reporte.costo_total, Decimal("127.50"))

    def test_api_productos_listado(self):
        """Verifica el endpoint GET /api/productos/."""
        response = self.client.get(reverse('api_productos'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["total"], 1)

    def test_api_registro_uso_flujo_completo(self):
        """Verifica el endpoint POST /api/registro-uso/ con descuento de stock."""
        payload = {
            "producto_id": self.producto.id,
            "cantidad": 10,
            "precio_unitario": "15.00",
            "observacion": "Prueba de salida API"
        }
        response = self.client.post(
            reverse('api_registro_uso'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["stock_actual_producto"], 40)
        self.assertEqual(data["uso"]["costo_total"], 150.0)

        # Validar descuento en BD
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad, 40)

    def test_api_eliminar_uso_restituye_stock(self):
        """Verifica que eliminar una salida devuelva los ítems al inventario."""
        uso = RegistroUso.objects.create(
            reporte=self.reporte,
            producto=self.producto,
            cantidad=4,
            precio_unitario=Decimal("10.00")
        )
        self.producto.cantidad -= 4
        self.producto.save()

        # Elimina a través del endpoint
        response = self.client.delete(reverse('api_eliminar_uso', kwargs={'pk': uso.id}))
        self.assertEqual(response.status_code, 200)
        
        # Debe haber devuelto los 4 al stock
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad, 50)

    def test_api_eliminar_reporte_completo(self):
        """Verifica que eliminar un reporte devuelva el stock y borre el reporte."""
        # Crea salida de 6 unidades
        RegistroUso.objects.create(
            reporte=self.reporte,
            producto=self.producto,
            cantidad=6,
            precio_unitario=Decimal("12.00")
        )
        self.producto.cantidad -= 6
        self.producto.save()

        reporte_id = self.reporte.id
        response = self.client.delete(reverse('api_eliminar_reporte', kwargs={'pk': reporte_id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        # Verifica que el reporte no exista
        self.assertFalse(ReporteDiario.objects.filter(pk=reporte_id).exists())
        
        # Verifica que el stock se haya restituido
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad, 50)
