"""
Propiedades extra que se guardan pero no aparecen (punto 15 de docs/23_CORRECCIONES_REVISION_OCT.md).

Causas: la grilla de la pestaña 3 nunca mostraba las propiedades extra, y el reporte de propiedades
solo imprimía las 1-8 con orden de impresión > 0. Ahora una sola regla
(models_daily_reports.propiedades_extra_del_reporte) decide qué se muestra: las del tipo de fluido
del reporte, con etiqueta, que tienen orden de impresión o un valor cargado ese día.
"""

from datetime import date

from django.test import TestCase

from operaciones.models import Pozo
from operaciones.models_daily_reports import (PropiedadExtraFluido, ReporteDiario, ReporteDiarioMudCheck,
                                              ReporteDiarioMudExtraValue, propiedades_extra_del_reporte)


class PropiedadesExtraTests(TestCase):

    def setUp(self):
        self.pozo = Pozo.objects.create(nombre='POZO PRUEBA')
        self.reporte = ReporteDiario.objects.create(pozo=self.pozo, fecha=date(2026, 10, 13), tipo_lodo='WBM')
        self.checks = [ReporteDiarioMudCheck.objects.create(reporte=self.reporte, check_number=n) for n in (1, 2, 3, 4)]
        crear = lambda **d: PropiedadExtraFluido.objects.create(pozo=self.pozo, **d)
        self.carbonato = crear(tipo_fluido='WBM', numero=12, etiqueta='% Carbonato', unidad='%', orden_impresion=0)
        self.impresa = crear(tipo_fluido='WBM', numero=3, etiqueta='Sulfuros', unidad='mg/L', orden_impresion=1)
        self.sin_uso = crear(tipo_fluido='WBM', numero=5, etiqueta='Sin uso', orden_impresion=0)
        self.de_aceite = crear(tipo_fluido='OBM', numero=1, etiqueta='Solo aceite', orden_impresion=1)

    def cargar(self, propiedad, chequeo, valor):
        ReporteDiarioMudExtraValue.objects.create(mud_check=self.checks[chequeo - 1], propiedad_extra=propiedad,
                                                  valor=valor)

    def test_un_valor_cargado_aparece_aunque_no_tenga_orden_ni_numero_bajo(self):
        self.cargar(self.carbonato, 4, '20')     # el caso del cliente: en la última prueba
        filas = propiedades_extra_del_reporte(self.reporte, self.checks)
        carbonato = next(f for f in filas if f['id'] == self.carbonato.id)
        self.assertEqual(carbonato['valores'], ['', '', '', '20'])
        self.assertEqual((carbonato['etiqueta'], carbonato['unidad']), ('% Carbonato', '%'))

    def test_que_se_muestra_y_en_que_orden(self):
        self.cargar(self.carbonato, 1, '20')
        filas = propiedades_extra_del_reporte(self.reporte, self.checks)
        # Primero las de orden de impresión, luego las que solo tienen valor. Sin valor ni orden: no.
        # Las del otro tipo de fluido: no.
        self.assertEqual([f['etiqueta'] for f in filas], ['Sulfuros', '% Carbonato'])

    def test_valor_vacio_no_cuenta_como_cargado(self):
        self.cargar(self.carbonato, 1, '   ')
        etiquetas = [f['etiqueta'] for f in propiedades_extra_del_reporte(self.reporte, self.checks)]
        self.assertNotIn('% Carbonato', etiquetas)

    def test_reporte_de_lodo_aceite_usa_sus_propiedades(self):
        self.reporte.tipo_lodo = 'OBM'
        self.reporte.save()
        etiquetas = [f['etiqueta'] for f in propiedades_extra_del_reporte(self.reporte, self.checks)]
        self.assertEqual(etiquetas, ['Solo aceite'])

    def test_aparece_en_la_grilla_de_la_pestana_3(self):
        self.cargar(self.carbonato, 4, '20')
        html = self.client.get(f'/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/').content.decode()
        self.assertIn('Propiedades Extra', html)
        self.assertIn(f'data-extra-prop="{self.carbonato.id}" data-check="4" value="20"', html)

    def test_aparece_en_el_reporte_de_propiedades(self):
        self.cargar(self.carbonato, 4, '20')
        html = self.client.get(f'/pozos/{self.pozo.pk}/daily-report/{self.reporte.pk}/propiedades/').content.decode()
        self.assertIn('% Carbonato', html)
