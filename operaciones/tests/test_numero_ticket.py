"""Número de ticket en el inventario del pozo (punto 5 de docs/23_CORRECCIONES_REVISION_OCT.md)."""

from datetime import date
from decimal import Decimal

from django.test import TestCase

from operaciones.models import Pozo, Producto
from operaciones.models_control_solidos import TipoTicketMalla
from operaciones.models_daily_reports import ReporteDiario
from operaciones.models_inventario import TicketProducto, TicketProductoDetalle
from operaciones.views_inventario import numeros_ticket_por_producto


class NumeroTicketTests(TestCase):

    def setUp(self):
        pozo = Pozo.objects.create(nombre='POZO PRUEBA')
        self.reporte = ReporteDiario.objects.create(pozo=pozo, fecha=date(2026, 10, 13))
        self.recepcion = TipoTicketMalla.objects.create(pozo=pozo, nombre='Recepción', sentido='ENTRADA')
        self.devolucion = TipoTicketMalla.objects.create(pozo=pozo, nombre='Devolución', sentido='SALIDA')
        self.barita = Producto.objects.create(codigo='BARITA', descripcion='Barita', unidad='LBS')
        self.gel = Producto.objects.create(codigo='GEL', descripcion='Gel', unidad='LBS')

    def ticket(self, tipo, numero, *productos):
        t = TicketProducto.objects.create(reporte=self.reporte, tipo=tipo, numero=numero)
        for producto in productos:
            TicketProductoDetalle.objects.create(ticket=t, producto=producto,
                                                 cantidad_ticket=Decimal('10'), cantidad_real=Decimal('10'))

    def test_cada_producto_muestra_el_numero_de_su_ticket(self):
        self.ticket(self.recepcion, '8888', self.barita, self.gel)
        self.ticket(self.devolucion, 'D-12', self.gel)
        numeros = numeros_ticket_por_producto(self.reporte)
        self.assertEqual(numeros['ENTRADA'], {self.barita.id: ['8888'], self.gel.id: ['8888']})
        self.assertEqual(numeros['SALIDA'], {self.gel.id: ['D-12']})

    def test_varios_tickets_del_mismo_producto_en_el_dia(self):
        self.ticket(self.recepcion, '8888', self.barita)
        self.ticket(self.recepcion, '8889', self.barita)
        self.assertEqual(numeros_ticket_por_producto(self.reporte)['ENTRADA'][self.barita.id], ['8888', '8889'])

    def test_los_tickets_sin_numero_no_aparecen(self):
        self.ticket(self.recepcion, '', self.barita)
        self.assertEqual(numeros_ticket_por_producto(self.reporte)['ENTRADA'], {})
