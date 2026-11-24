"""
Pruebas para el reporte de Excel:
1. Productos usados en 'Lodo Base Agua' (filas 19 a 33) considerando usado_fluido y agregado_balance.
2. Hoja única de inventario químico: 'Inv Quimico (completo)' (se eliminan 'Inv Quimico (DF)' y 'por nombre').
3. Limpieza de filas vacías (sin residuos ni ceros).
4. Rediseño visual: colores de pestañas y cuadrículas visibles.
"""

import io
from datetime import date
from decimal import Decimal

import openpyxl
from django.test import TestCase

from operaciones.models import Fosa, Pozo, Producto, ProductoActivoPozo, TipoFosa
from operaciones.models_daily_reports import ReporteDiario
from operaciones.models_inventario import InventarioProductoDia, TransaccionVolumen, TransaccionVolumenProducto
from operaciones.reporte_excel import generar_reporte_excel


class ExcelInventarioYProductosUsadosTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO TEST EXCEL INV')
        TipoFosa.sembrar_estandar(self.pozo)
        Fosa.objects.create(pozo=self.pozo, numero=1, descripcion='Activo 1', capacidad=Decimal('1000'))

        self.reporte = ReporteDiario.objects.create(
            pozo=self.pozo,
            fecha=date(2026, 10, 18),
            tipo_lodo='Agua',
            numero_reporte=1,
        )

        # Producto 1: Barita (utilizado en el lodo del programa)
        self.prod_barita = Producto.objects.create(
            codigo='BAR-01', descripcion='Barita Alta Densidad', unidad='SACO'
        )
        self.activo_barita = ProductoActivoPozo.objects.create(
            pozo=self.pozo, producto=self.prod_barita, unidad='SACO', unit_size=Decimal('100'),
            precio=Decimal('25.50'), codigo_costo_diario=1
        )

        # Producto 2: Soda Cáustica (utilizado en el lodo)
        self.prod_soda = Producto.objects.create(
            codigo='SOD-01', descripcion='Soda Caustica', unidad='SACO'
        )
        self.activo_soda = ProductoActivoPozo.objects.create(
            pozo=self.pozo, producto=self.prod_soda, unidad='SACO', unit_size=Decimal('50'),
            precio=Decimal('40.00'), codigo_costo_diario=1
        )

        # Inventario del día:
        # Barita: 10 sacos usados en fluido
        InventarioProductoDia.objects.create(
            reporte=self.reporte, producto=self.prod_barita,
            inicial=Decimal('100'), usado_fluido=Decimal('10'),
            precio=Decimal('25.50'), categoria_costo=1
        )
        # Soda: 2 sacos usados en fluido
        InventarioProductoDia.objects.create(
            reporte=self.reporte, producto=self.prod_soda,
            inicial=Decimal('20'), usado_fluido=Decimal('2'),
            precio=Decimal('40.00'), categoria_costo=1
        )

    def test_productos_usados_aparecen_en_hoja_lodo_base_agua(self):
        """Verifica que los productos usados aparezcan en las filas 19..33 de Lodo Base Agua."""
        contenido, _ = generar_reporte_excel(self.pozo, self.reporte)
        wb = openpyxl.load_workbook(io.BytesIO(contenido))
        self.assertIn('Lodo Base Agua', wb.sheetnames)
        ws = wb['Lodo Base Agua']

        # Fila 19: Primer producto usado
        self.assertEqual(ws['G19'].value, 'Barita Alta Densidad')
        self.assertEqual(ws['J19'].value, 10.0)

        # Fila 20: Segundo producto usado
        self.assertEqual(ws['G20'].value, 'Soda Caustica')
        self.assertEqual(ws['J20'].value, 2.0)

        # Fila 21 a 33: Deben estar limpias (None) sin ceros residuales
        for fila in range(21, 34):
            self.assertIsNone(ws[f'G{fila}'].value, f"Fila G{fila} debio ser None")
            self.assertIsNone(ws[f'J{fila}'].value, f"Fila J{fila} debio ser None")

    def test_productos_agregados_en_tanque_balance_aparecen_en_lodo_base_agua(self):
        """
        Verifica que químicos agregados a un tanque (QUIMICOS / agregado_balance)
        también aparezcan en las filas 19..33 de Lodo Base Agua aunque usado_fluido esté en 0.
        """
        rep2 = ReporteDiario.objects.create(
            pozo=self.pozo, fecha=date(2026, 10, 19), tipo_lodo='Agua', numero_reporte=2
        )
        # Transacción QUIMICOS con Barita dosificada en tanque
        tx = TransaccionVolumen.objects.create(
            reporte=rep2, secuencia=1, tipo='QUIMICOS', fosa_numero=1, fosa_descripcion='Activo 1',
            agua_bbl=Decimal('100.0')
        )
        TransaccionVolumenProducto.objects.create(
            transaccion=tx, producto=self.prod_barita, descripcion='Barita Alta Densidad',
            cantidad=Decimal('35.0'), unidad='SACO', tamano=Decimal('100'), gravedad=Decimal('4.2')
        )
        contenido, _ = generar_reporte_excel(self.pozo, rep2)
        wb = openpyxl.load_workbook(io.BytesIO(contenido))
        ws = wb['Lodo Base Agua']

        self.assertEqual(ws['G19'].value, 'Barita Alta Densidad')
        self.assertEqual(ws['J19'].value, 35.0)

    def test_hoja_unica_inventario_quimico_completo(self):
        """Verifica que se conserve únicamente 'Inv Quimico (completo)' como la hoja de inventario."""
        contenido, _ = generar_reporte_excel(self.pozo, self.reporte)
        wb = openpyxl.load_workbook(io.BytesIO(contenido))

        # Solo debe quedar 'Inv Quimico (completo)'
        self.assertIn('Inv Quimico (completo)', wb.sheetnames)
        self.assertNotIn('Inv Quimico (DF)', wb.sheetnames)
        self.assertNotIn('Inv Quimico (por nombre)', wb.sheetnames)

        ws_comp = wb['Inv Quimico (completo)']
        descripciones = [ws_comp[f'A{f}'].value for f in range(11, 61) if ws_comp[f'A{f}'].value]
        self.assertIn('Barita Alta Densidad', descripciones)
        self.assertIn('Soda Caustica', descripciones)

    def test_diseno_visual_colores_y_cuadricula(self):
        """Verifica que las pestañas tengan colores corporativos y la cuadrícula esté visible."""
        contenido, _ = generar_reporte_excel(self.pozo, self.reporte)
        wb = openpyxl.load_workbook(io.BytesIO(contenido))

        # Colores de pestañas (formato ARGB de openpyxl)
        ws_lodo = wb['Lodo Base Agua']
        self.assertIsNotNone(ws_lodo.sheet_properties.tabColor)
        self.assertTrue(ws_lodo.sheet_properties.tabColor.rgb.endswith('1E3A8A'))

        ws_comp = wb['Inv Quimico (completo)']
        self.assertTrue(ws_comp.sheet_properties.tabColor.rgb.endswith('059669'))

        # Cuadrículas visibles en todas las hojas
        for ws in wb.worksheets:
            self.assertTrue(ws.views.sheetView[0].showGridLines, f"Cuadrícula no visible en hoja {ws.title}")

    def test_ajuste_impresion_tamano_carta(self):
        """Verifica que todas las hojas estén configuradas para impresión en hoja Carta (Letter)."""
        contenido, _ = generar_reporte_excel(self.pozo, self.reporte)
        wb = openpyxl.load_workbook(io.BytesIO(contenido))

        for ws in wb.worksheets:
            self.assertEqual(str(ws.page_setup.paperSize), '1', f"PaperSize no es Carta en {ws.title}")
            self.assertTrue(ws.sheet_properties.pageSetUpPr.fitToPage, f"fitToPage no es True en {ws.title}")
            self.assertEqual(ws.page_setup.fitToWidth, 1, f"fitToWidth no es 1 en {ws.title}")
            self.assertIsNone(ws.page_setup.scale, f"scale debió ser None en {ws.title}")

        ws_lodo = wb['Lodo Base Agua']
        self.assertEqual(ws_lodo.page_setup.fitToHeight, 1)

        ws_inv = wb['Inv Quimico (completo)']
        self.assertEqual(ws_inv.page_setup.fitToHeight, 0)

    def test_reporte_base_aceite_genera_hoja_lodo_base_aceite(self):
        """Verifica que si el reporte es OBM, se genera la hoja Lodo Base Aceite y se descarta Base Agua."""
        rep_obm = ReporteDiario.objects.create(
            pozo=self.pozo, fecha=date(2026, 10, 20), tipo_lodo='OBM', numero_reporte=3
        )
        contenido, _ = generar_reporte_excel(self.pozo, rep_obm)
        wb = openpyxl.load_workbook(io.BytesIO(contenido))

        self.assertIn('Lodo Base Aceite', wb.sheetnames)
        self.assertIn('Prop Extra Aceite-Sint', wb.sheetnames)
        self.assertNotIn('Lodo Base Agua', wb.sheetnames)
        self.assertNotIn('Prop Extra Base Agua', wb.sheetnames)

        ws_obm = wb['Lodo Base Aceite']
        self.assertIn('REPORTE DE LODO BASE ACEITE', ws_obm['J2'].value)
        self.assertEqual(str(ws_obm.page_setup.paperSize), '1')
        self.assertEqual(ws_obm.page_setup.fitToWidth, 1)
        self.assertEqual(ws_obm.page_setup.fitToHeight, 1)
