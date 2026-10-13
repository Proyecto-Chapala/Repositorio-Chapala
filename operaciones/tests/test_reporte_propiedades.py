"""
Reporte de propiedades (reportito), punto 16 de docs/23_CORRECCIONES_REVISION_OCT.md: el comentario se
guarda, el reporte se descarga en Excel con las propiedades, el punto de muestreo, la hora y el
comentario, y las propiedades se editan en la pestaña 3 (no hay una segunda pantalla de edición).
"""

import io
import json
from datetime import date

import openpyxl
from django.test import TestCase

from operaciones.models import Pozo
from operaciones.models_daily_reports import ReporteDiario, ReporteDiarioComentarios, ReporteDiarioMudCheck


class ReportePropiedadesTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA')
        self.reporte = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13), tipo_lodo='WBM')
        ReporteDiarioMudCheck.objects.create(reporte=self.reporte, check_number=1, is_primary=True,
                                             sample_from='Flow line', time_taken='10:00', mud_weight=9.5, ph=9.2)
        self.base = f'/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/propiedades/'

    def guardar_comentario(self, texto):
        return self.client.post(f'/api/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/propiedades/comentario/',
                                json.dumps({'comentario': texto}), content_type='application/json')

    def test_el_comentario_se_guarda_y_vuelve_a_aparecer(self):
        self.assertEqual(self.guardar_comentario('  Agregar barita para subir a 9,8  ').status_code, 200)
        self.assertEqual(ReporteDiarioComentarios.objects.get(reporte=self.reporte).comentario_propiedades,
                         'Agregar barita para subir a 9,8')
        self.assertIn('Agregar barita para subir a 9,8', self.client.get(self.base).content.decode())

    def test_el_comentario_no_borra_los_otros_comentarios_del_dia(self):
        ReporteDiarioComentarios.objects.create(reporte=self.reporte, remarks='Operaciones normales')
        self.guardar_comentario('Nuevo')
        comentarios = ReporteDiarioComentarios.objects.get(reporte=self.reporte)
        self.assertEqual((comentarios.remarks, comentarios.comentario_propiedades), ('Operaciones normales', 'Nuevo'))

    def test_excel_con_propiedades_muestra_hora_y_comentario(self):
        self.guardar_comentario('Mantener pH entre 9 y 10')
        respuesta = self.client.get(self.base + 'excel/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('attachment', respuesta['Content-Disposition'])
        textos = [str(c) for fila in openpyxl.load_workbook(io.BytesIO(respuesta.content)).active.iter_rows(values_only=True)
                  for c in fila if c is not None]
        self.assertIn('Flow line 10:00', textos)        # punto de muestreo y hora elegida
        self.assertIn('Mantener pH entre 9 y 10', textos)
        self.assertIn('pH', textos)

    def test_la_pagina_lleva_a_la_pestana_3_para_editar(self):
        html = self.client.get(self.base).content.decode()
        self.assertIn(f'/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/?pestana=3', html)
