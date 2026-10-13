"""Catálogo de productos de AOS que SmartMud.exe carga en una base nueva."""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from operaciones.management.commands.cargar_catalogo_productos import CATALOGO_AOS
from operaciones.models import Producto


class CatalogoProductosTests(TestCase):

    def cargar(self):
        call_command('cargar_catalogo_productos', stdout=StringIO())

    def test_carga_todo_el_catalogo_con_precio_y_existencia_en_cero(self):
        self.cargar()
        self.assertEqual(Producto.objects.count(), len(CATALOGO_AOS))
        self.assertFalse(Producto.objects.exclude(costo=0).exists())
        self.assertFalse(Producto.objects.exclude(cantidad=0).exists())

    def test_repetirlo_no_duplica_ni_pisa_lo_editado(self):
        self.cargar()
        producto = Producto.objects.get(codigo=CATALOGO_AOS[0][0])
        producto.costo = 99
        producto.save()
        self.cargar()
        self.assertEqual(Producto.objects.count(), len(CATALOGO_AOS))
        producto.refresh_from_db()
        self.assertEqual(producto.costo, 99)
