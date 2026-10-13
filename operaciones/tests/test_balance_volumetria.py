"""
El balance de volumetría tiene que cerrar (punto 10 de docs/23_CORRECCIONES_REVISION_OCT.md).

1) Identidad: para cada grupo, las filas que muestra la pantalla (inicial + fluido base + agua +
   químicos + lodo reciclado − devuelto + transferido desde − transferido a − pérdidas) suman
   exactamente el volumen final calculado. Si un movimiento cambiara el calculado sin aparecer
   en una fila, el balance mostraría una diferencia imposible de explicar.
2) Caso del cliente: 1.000 bbl + químicos. Con la gravedad específica el volumen de químicos
   entra al balance y, si el real medido es el que corresponde, no contabilizado = 0.
"""

from django.test import SimpleTestCase

from operaciones import volumetria as vol

ACTIVO, RESERVA, PREMEZCLA = vol.ACTIVO, vol.RESERVA, vol.PREMEZCLA
BARITA, SALMUERA = 1, 2


def tanque(numero, grupo, real=None):
    return {'numero': numero, 'grupo': grupo, 'real': real}


def dia(id_, fosas, transacciones=(), hoyo=0.0, tickets=None):
    tickets = tickets if tickets is not None else [
        {'sentido': 'ENTRADA', 'detalles': [{'producto': BARITA, 'real': 1000, 'ticket': 1000},
                                            {'producto': SALMUERA, 'real': 1000, 'ticket': 1000}]}]
    return {'id': id_, 'fecha_texto': f'dia {id_}', 'fosas': fosas, 'hoyo_fluido': hoyo,
            'tickets': tickets, 'transacciones': list(transacciones), 'manual': {}}


def quimicos(sec, fosa, sacos=0, agua=0.0, aceite=0.0, gravedad=4.2):
    productos = [{'producto': BARITA, 'cantidad': sacos, 'unidad': 'LBS', 'tamano': 100,
                  'gravedad': gravedad, 'precio': 0, 'categoria': 1, 'concentracion': True}] if sacos else []
    return {'secuencia': sec, 'tipo': 'QUIMICOS', 'fosa': fosa, 'aceite': aceite, 'agua': agua, 'productos': productos}


def movimiento(sec, tipo, fosa, volumen, **extra):
    return dict({'secuencia': sec, 'tipo': tipo, 'fosa': fosa, 'volumen': volumen, 'productos': []}, **extra)


def suma_de_filas(inicio, flujos):
    f = lambda k: flujos.get(k, 0.0)
    return (inicio + f('aceite') + f('agua') + f('quimicos') + f('recibido') - f('devuelto')
            + f('entra') - f('sale') - f('perdida'))


class IdentidadDelBalanceTests(SimpleTestCase):

    def test_cada_grupo_cuadra_con_todos_los_tipos_de_movimiento(self):
        fosas = [tanque(1, ACTIVO), tanque(2, ACTIVO), tanque(3, RESERVA), tanque(4, PREMEZCLA)]
        dias = [
            dia(1, [tanque(1, ACTIVO, 500), tanque(2, ACTIVO, 300), tanque(3, RESERVA, 200), tanque(4, PREMEZCLA, 50)],
                [quimicos(1, 1, agua=500), quimicos(2, 2, agua=300), quimicos(3, 3, agua=200), quimicos(4, 4, agua=50)],
                hoyo=120),
            dia(2, fosas, [
                quimicos(5, 1, sacos=20, agua=10, aceite=5),
                movimiento(6, 'LODO_ENTERO', 3, 40, lodo_producto=SALMUERA, lodo_cantidad=40, lodo_precio=0),
                movimiento(7, 'TRANSFERENCIA', 3, 60, destino=1),
                movimiento(8, 'TRANSFERENCIA', 1, 15, destino=2),        # dentro del mismo grupo
                movimiento(9, 'TRANSFERENCIA', 4, 25, destino=1),
                movimiento(10, 'DEVOLUCION', 3, 30),
                movimiento(11, 'PERDIDA', 2, 12, perdida=1),
                movimiento(12, 'PERDIDA', 1, 7.5, perdida=2),
            ], hoyo=150),
        ]
        sim = vol.simular(dias, 2)
        for grupo in (ACTIVO, RESERVA, PREMEZCLA):
            with self.subTest(grupo=grupo):
                self.assertAlmostEqual(suma_de_filas(sim['inicio_grupo'][grupo], sim['flujos'][grupo]),
                                       sim['calc_grupo'][grupo])

    def test_las_transferencias_entre_grupos_se_compensan(self):
        dias = [dia(1, [tanque(1, ACTIVO), tanque(3, RESERVA)],
                    [quimicos(1, 3, agua=100), movimiento(2, 'TRANSFERENCIA', 3, 40, destino=1)])]
        flujos = vol.simular(dias, 1)['flujos']
        self.assertEqual(flujos[RESERVA]['sale'], 40)
        self.assertEqual(flujos[ACTIVO]['entra'], 40)


class CasoDelClienteTests(SimpleTestCase):
    """1.000 bbl en el activo; se agregan 30 sacos de barita de 100 lb (GE 4,2)."""

    VOLUMEN_BARITA = 3000 / (350 * 4.2)   # ≈ 2,04 bbl

    def simular(self, real_dia_2, gravedad=4.2):
        dias = [
            dia(1, [tanque(1, ACTIVO, 1000)], [quimicos(1, 1, agua=1000)]),
            dia(2, [tanque(1, ACTIVO, real_dia_2)], [quimicos(2, 1, sacos=30, gravedad=gravedad)]),
        ]
        return vol.simular(dias, 2)

    def test_el_volumen_de_quimicos_entra_al_balance(self):
        sim = self.simular(1000 + self.VOLUMEN_BARITA)
        self.assertAlmostEqual(sim['flujos'][ACTIVO]['quimicos'], self.VOLUMEN_BARITA)
        self.assertAlmostEqual(sim['no_contabilizado'][ACTIVO], 0.0)

    def test_sin_gravedad_especifica_aparece_la_diferencia(self):
        # Es el desbalance que vio el cliente: el material ocupa volumen, pero el balance no lo ve.
        # Por eso ahora un producto en peso no se guarda sin GE (prueba 02).
        sim = self.simular(1000 + self.VOLUMEN_BARITA, gravedad=0)
        self.assertAlmostEqual(sim['no_contabilizado'][ACTIVO], self.VOLUMEN_BARITA)

    def test_el_hoyo_forma_parte_del_sistema_activo(self):
        # Al perforar, el fluido pasa de los tanques al hoyo: el total no cambia y cuadra.
        dias = [
            dia(1, [tanque(1, ACTIVO, 1000)], [quimicos(1, 1, agua=1100)], hoyo=100),
            dia(2, [tanque(1, ACTIVO, 970)], hoyo=130),
        ]
        sim = vol.simular(dias, 2)
        self.assertAlmostEqual(sim['inicio_grupo'][ACTIVO], 1100)
        self.assertAlmostEqual(sim['no_contabilizado'][ACTIVO], 0.0)
