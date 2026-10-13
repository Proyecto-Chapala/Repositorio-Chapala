"""
Recuadro "Datos del inventario" (punto 12 de docs/23_CORRECCIONES_REVISION_OCT.md): recepción desde
almacén u otro pozo y envíos a almacén u otro pozo del día, sacados de los movimientos de volumetría.
"""

from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase

from operaciones.models_inventario import TransaccionVolumen
from operaciones.views_inventario import ORIGEN_OTRO_POZO, fluido_externo_del_dia


def movimiento(tipo, volumen, origen_destino=''):
    return SimpleNamespace(tipo=tipo, volumen_bbl=Decimal(str(volumen)), origen_destino=origen_destino)


class FluidoExternoTests(SimpleTestCase):

    def test_recepciones_y_envios_del_dia(self):
        totales = fluido_externo_del_dia([
            movimiento(TransaccionVolumen.LODO_ENTERO, 80, ORIGEN_OTRO_POZO),
            movimiento(TransaccionVolumen.LODO_ENTERO, 20, ORIGEN_OTRO_POZO),
            movimiento(TransaccionVolumen.LODO_ENTERO, 50, 'Almacén ALM-01 — Almacén Anaco'),
            movimiento(TransaccionVolumen.DEVOLUCION, 30, ORIGEN_OTRO_POZO),
            movimiento(TransaccionVolumen.DEVOLUCION, 15, 'Almacén ALM-03 — Almacén Patio'),
        ])
        self.assertEqual(totales, {'recibido_almacen': 50, 'recibido_otro_pozo': 100,
                                   'enviado_almacen': 15, 'enviado_otro_pozo': 30})

    def test_transferencias_perdidas_y_quimicos_no_cuentan(self):
        totales = fluido_externo_del_dia([
            movimiento(TransaccionVolumen.TRANSFERENCIA, 100),
            movimiento(TransaccionVolumen.PERDIDA, 10),
            movimiento(TransaccionVolumen.QUIMICOS, 0),
        ])
        self.assertEqual(sum(totales.values()), 0)

    def test_origen_sin_indicar_no_se_clasifica(self):
        totales = fluido_externo_del_dia([movimiento(TransaccionVolumen.LODO_ENTERO, 40, '')])
        self.assertEqual(sum(totales.values()), 0)
