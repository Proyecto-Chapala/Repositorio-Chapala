"""
Motor de la volumetría e inventario de productos (pestaña 8).

Función pura, sin Django. Repite, día por día y en orden, los movimientos de todo el pozo:

- Volumen de cada fosa: inicial (= real medido del día anterior, o el calculado si no se
  midió) + químicos, fluido base y agua, lodo entero, transferencias, devoluciones y pérdidas.
- Sistema activo: incluye el HOYO. Inicial = fosas activas + fluido en el hoyo del día
  anterior. Real = fosas activas medidas + fluido en el hoyo de hoy. Por eso el calculado de
  la fosa activa y su volumen real NO tienen que coincidir (nota especial del manual, pág. 146).
- "No contabilizado" = real − calculado, por grupo (activo, reserva, premezcla). Al cierre
  de cada día debe ser cero.
- Inventario de productos: inicial + recibido − devuelto − usado en fluidos − usado en otro
  módulo ± ajuste. Si algún día queda negativo se rechaza (misma regla que las mallas).
- Costos por categoría y concentración de cada producto (lb/bbl) por compartimento: el sistema
  activo (fosas activas + hoyo, que se mezclan) y cada una de las demás fosas.

Servicios (productos sin unidad, como los días de ingeniero de fluidos): solo generan costo;
no llevan existencias (en el manual su inicial y final siempre son 0).

Volumen de químicos: solo aportan volumen los productos que se miden en PESO (lb, kg, t):
volumen = peso / (gravedad específica × 350 lb/bbl). Los productos en unidades de volumen
(bbl, gal, l) no se suman aquí: su volumen se registra como fluido base/agua o como lodo
entero (en el ejemplo del manual el DF-1 Base Oil aparece como producto y como fluido base).
"""

from collections import defaultdict

ACTIVO = 'ACTIVO'
RESERVA = 'RESERVA'
PREMEZCLA = 'PREMEZCLA'
OTRAS = 'OTRAS'
GRUPOS = (ACTIVO, RESERVA, PREMEZCLA, OTRAS)

LB_POR_BBL_AGUA = 350.0
EPS = 0.005

# Tipo de fosa (código de TipoFosa) → grupo del balance.
GRUPO_POR_TIPO = {1: ACTIVO, 2: RESERVA, 3: PREMEZCLA}

FACTOR_MASA = {'LB': 1.0, 'LBS': 1.0, 'KG': 2.20462, 'TN': 2000.0, 'TON': 2000.0,
               'ST': 2000.0, 'MT': 2204.62, 'TM': 2204.62, 'T': 2204.62}
FACTOR_VOLUMEN_BBL = {'BL': 1.0, 'BBL': 1.0, 'GA': 1 / 42.0, 'GAL': 1 / 42.0,
                      'LT': 1 / 158.987, 'L': 1 / 158.987}

CATEGORIAS_COSTO = {
    1: 'Químicos',
    2: 'Ingeniero de fluidos',
    3: 'Ingeniero de control de sólidos',
    4: 'Ingeniero IFE',
}


class ErrorVolumetria(Exception):
    """Movimiento imposible (inventario negativo, fosa inexistente...). Mensaje para el usuario."""


def grupo_de_tipo(tipo_codigo):
    if tipo_codigo is None or tipo_codigo == 0:
        return None
    return GRUPO_POR_TIPO.get(tipo_codigo, OTRAS)


def _unidad(texto):
    return (texto or '').strip().upper().rstrip('.')


def masa_lb(cantidad, unidad, tamano):
    """Peso en lb de una cantidad de producto, o None si el producto no se mide en peso."""
    f = FACTOR_MASA.get(_unidad(unidad))
    if f is None:
        return None
    return float(cantidad or 0) * float(tamano or 0) * f


def volumen_quimico_bbl(cantidad, unidad, tamano, gravedad):
    m = masa_lb(cantidad, unidad, tamano)
    g = float(gravedad or 0)
    if m is None or g <= 0:
        return 0.0
    return m / (g * LB_POR_BBL_AGUA)


def consumo_lodo_entero(volumen_bbl, unidad, tamano):
    """Unidades del producto 'lodo entero' que se consumen al agregar un volumen de lodo."""
    f = FACTOR_VOLUMEN_BBL.get(_unidad(unidad))
    t = float(tamano or 0) or 1.0
    if f is None:
        return float(volumen_bbl or 0)
    return float(volumen_bbl or 0) / (t * f)


def _flujos():
    return {g: defaultdict(float) for g in GRUPOS}


def simular(dias, objetivo_id=None, nombres_producto=None, nombres_fosa=None, servicios=None):
    """
    dias: lista ordenada por fecha de dicts
      {
        'id', 'fecha_texto',
        'fosas': [{'numero', 'grupo' (ACTIVO/RESERVA/... o None), 'real' (float o None)}],
        'hoyo_fluido': float,                  # fluido del sistema activo dentro del hoyo hoy
        'transacciones': [{'secuencia', 'tipo', 'fosa', 'destino', 'volumen', 'aceite', 'agua',
                           'perdida', 'lodo_producto', 'lodo_cantidad', 'lodo_precio',
                           'lodo_categoria',
                           'productos': [{'producto', 'cantidad', 'es_concentracion', 'unidad',
                                          'tamano', 'gravedad', 'precio', 'categoria',
                                          'concentracion'}]}],
        'tickets': [{'sentido', 'detalles': [{'producto', 'real', 'ticket'}]}],
        'manual': {producto_id: {'otro', 'ajuste', 'precio', 'categoria'}},
      }
    servicios: ids de productos que son servicios (unidad vacía, como los días de ingeniero):
    solo generan costo, no llevan existencias.
    Devuelve el estado del día objetivo (ver final de la función).
    """
    servicios = set(servicios or ())
    nombres_producto = nombres_producto or {}
    nombres_fosa = nombres_fosa or {}

    def np(p):
        return nombres_producto.get(p, f"producto {p}")

    def nf(n):
        return nombres_fosa.get(n, f"fosa {n}")

    fin_fosa = {}                     # volumen final (real o calculado) por fosa
    hoyo_prev = 0.0
    stock = defaultdict(float)
    costo_acum_cat = defaultdict(float)
    costo_acum_prod = defaultdict(float)
    masa = defaultdict(lambda: defaultdict(float))   # compartimento → producto → lb
    comp_prev = {}                    # fosa → compartimento del día anterior
    vol_comp_prev = {}                # compartimento → volumen final del día anterior

    resultado = None

    for dia in dias:
        es_obj = dia['id'] == objetivo_id
        fecha = dia.get('fecha_texto', '')
        fosas = {f['numero']: f for f in dia.get('fosas', [])}
        grupo = {n: f.get('grupo') for n, f in fosas.items()}

        inicio = {n: fin_fosa.get(n, 0.0) for n in fosas}
        activas = [n for n in fosas if grupo[n] == ACTIVO]
        inicio_grupo = {g: 0.0 for g in GRUPOS}
        for n, v in inicio.items():
            if grupo[n]:
                inicio_grupo[grupo[n]] += v
        inicio_grupo[ACTIVO] += hoyo_prev

        # ---- Compartimentos para concentraciones ----
        def comp_de(n):
            return ACTIVO if grupo.get(n) == ACTIVO else ('F', n)

        for n in fosas:
            nuevo, viejo = comp_de(n), comp_prev.get(n)
            if viejo is not None and viejo != nuevo and inicio[n] > EPS:
                vol_viejo = vol_comp_prev.get(viejo, 0.0)
                if vol_viejo > EPS:
                    fr = min(inicio[n] / vol_viejo, 1.0)
                    for p in list(masa[viejo]):
                        mv = masa[viejo][p] * fr
                        masa[viejo][p] -= mv
                        masa[nuevo][p] += mv
        vol_comp = defaultdict(float)
        for n in fosas:
            vol_comp[comp_de(n)] += inicio[n]
        vol_comp[ACTIVO] += hoyo_prev
        masa_inicio = {c: dict(masa[c]) for c in list(masa)}
        vol_inicio_comp = dict(vol_comp)

        delta = defaultdict(float)
        flujos = _flujos()
        perdidas = defaultdict(lambda: defaultdict(float))   # código → grupo → bbl
        usado_fluido = defaultdict(float)
        costo_dia_prod = defaultdict(float)
        costo_dia_cat = defaultdict(float)
        recibido = defaultdict(float)
        devuelto = defaultdict(float)
        recibido_ticket = defaultdict(float)
        devuelto_ticket = defaultdict(float)
        avisos = []

        def g_de(n, etiqueta):
            if n not in fosas:
                raise ErrorVolumetria(f"El {fecha}: {etiqueta} ({nf(n)}) ya no está en la lista de fosas del pozo.")
            if grupo[n] is None:
                raise ErrorVolumetria(
                    f"El {fecha}: {nf(n)} no tiene tipo asignado (o es 'Vacía'). Asígnale un tipo antes de moverle fluido.")
            return grupo[n]

        def quitar_masa(c, vol):
            v = vol_comp[c]
            if v <= EPS:
                return
            fr = min(vol / v, 1.0)
            for p in list(masa[c]):
                masa[c][p] -= masa[c][p] * fr

        # ---- Tickets de productos ----
        for t in dia.get('tickets', []):
            for d in t.get('detalles', []):
                if t['sentido'] == 'ENTRADA':
                    recibido[d['producto']] += float(d.get('real') or 0)
                    recibido_ticket[d['producto']] += float(d.get('ticket') or 0)
                else:
                    devuelto[d['producto']] += float(d.get('real') or 0)
                    devuelto_ticket[d['producto']] += float(d.get('ticket') or 0)

        # ---- Movimientos ----
        for tr in sorted(dia.get('transacciones', []), key=lambda x: x['secuencia']):
            tipo = tr['tipo']
            n = tr['fosa']
            g = g_de(n, 'la fosa')
            c = comp_de(n)
            vol = float(tr.get('volumen') or 0)

            if tipo == 'QUIMICOS':
                aceite = float(tr.get('aceite') or 0)
                agua = float(tr.get('agua') or 0)
                vq = 0.0
                for p in tr.get('productos', []):
                    cant = float(p.get('cantidad') or 0)
                    usado_fluido[p['producto']] += cant
                    costo = cant * float(p.get('precio') or 0)
                    costo_dia_prod[p['producto']] += costo
                    costo_dia_cat[p.get('categoria') or 1] += costo
                    vq += volumen_quimico_bbl(cant, p.get('unidad'), p.get('tamano'), p.get('gravedad'))
                    if p.get('concentracion', True):
                        m = masa_lb(cant, p.get('unidad'), p.get('tamano'))
                        if m:
                            masa[c][p['producto']] += m
                total = aceite + agua + vq
                delta[n] += total
                vol_comp[c] += total
                flujos[g]['aceite'] += aceite
                flujos[g]['agua'] += agua
                flujos[g]['quimicos'] += vq

            elif tipo == 'LODO_ENTERO':
                lp = tr.get('lodo_producto')
                if lp:
                    cant = float(tr.get('lodo_cantidad') or 0)
                    usado_fluido[lp] += cant
                    costo = cant * float(tr.get('lodo_precio') or 0)
                    costo_dia_prod[lp] += costo
                    costo_dia_cat[tr.get('lodo_categoria') or 1] += costo
                for p in tr.get('productos', []):
                    if p.get('concentracion', True):
                        masa[c][p['producto']] += float(p.get('cantidad') or 0) * vol
                delta[n] += vol
                vol_comp[c] += vol
                flujos[g]['recibido'] += vol

            elif tipo == 'TRANSFERENCIA':
                d = tr.get('destino')
                gd = g_de(d, 'la fosa destino')
                cd = comp_de(d)
                if c != cd and vol_comp[c] > EPS:
                    fr = min(vol / vol_comp[c], 1.0)
                    for p in list(masa[c]):
                        mv = masa[c][p] * fr
                        masa[c][p] -= mv
                        masa[cd][p] += mv
                delta[n] -= vol
                delta[d] += vol
                vol_comp[c] -= vol
                vol_comp[cd] += vol
                if g != gd:
                    flujos[g]['sale'] += vol
                    flujos[gd]['entra'] += vol

            elif tipo in ('DEVOLUCION', 'PERDIDA'):
                quitar_masa(c, vol)
                delta[n] -= vol
                vol_comp[c] -= vol
                if tipo == 'DEVOLUCION':
                    flujos[g]['devuelto'] += vol
                else:
                    flujos[g]['perdida'] += vol
                    perdidas[tr.get('perdida')][g] += vol
            else:
                raise ErrorVolumetria(f"Movimiento desconocido: {tipo}")

            if g != ACTIVO and inicio.get(n, 0) + delta[n] < -EPS:
                avisos.append(f"Movimiento #{tr['secuencia']}: {nf(n)} queda con volumen calculado negativo "
                              f"({inicio[n] + delta[n]:.1f} bbl).")

        # ---- Volúmenes finales ----
        calc = {n: inicio[n] + delta[n] for n in fosas}
        calc_grupo = {g: inicio_grupo[g] for g in GRUPOS}
        for n in fosas:
            if grupo[n]:
                calc_grupo[grupo[n]] += delta[n]

        hoyo = float(dia.get('hoyo_fluido') or 0)
        real_grupo = {}
        faltan = {}
        for g in GRUPOS:
            miembros = [n for n in fosas if grupo[n] == g]
            sin = [n for n in miembros if fosas[n].get('real') is None]
            faltan[g] = sin
            real = sum(float(fosas[n]['real']) for n in miembros if fosas[n].get('real') is not None)
            if g == ACTIVO:
                real += hoyo
            real_grupo[g] = None if sin else real

        # ---- Inventario de productos ----
        manual = dia.get('manual', {})
        ids = set(stock) | set(usado_fluido) | set(recibido) | set(devuelto) | set(manual)
        inventario = {}
        for p in ids:
            m = manual.get(p, {})
            otro = float(m.get('otro') or 0)
            ajuste = float(m.get('ajuste') or 0)
            if otro:
                costo = otro * float(m.get('precio') or 0)
                costo_dia_prod[p] += costo
                costo_dia_cat[m.get('categoria') or 1] += costo
            ini = stock[p]
            if p in servicios:
                fin = ini
            else:
                fin = ini + recibido[p] - devuelto[p] - usado_fluido[p] - otro + ajuste
            if fin < -EPS:
                raise ErrorVolumetria(
                    f"El {fecha}: el inventario de {np(p)} queda en {fin:g}. "
                    f"Hay {ini + recibido[p]:g} disponibles y se usan o devuelven "
                    f"{usado_fluido[p] + otro + devuelto[p] - ajuste:g}. Registra primero el ticket de recepción.")
            stock[p] = fin
            costo_acum_prod[p] += costo_dia_prod[p]
            inventario[p] = {
                'inicial': ini, 'recibido': recibido[p], 'devuelto': devuelto[p],
                'recibido_ticket': recibido_ticket[p], 'devuelto_ticket': devuelto_ticket[p],
                'usado_fluido': usado_fluido[p], 'usado_otro': otro, 'ajuste': ajuste,
                'final': fin, 'usado_dia': usado_fluido[p] + otro,
                'costo_diario': round(costo_dia_prod[p], 2),
                'costo_acumulado': round(costo_acum_prod[p], 2),
            }
        for cat, v in costo_dia_cat.items():
            costo_acum_cat[cat] += v

        # ---- Concentraciones al cierre (sobre el volumen calculado) ----
        vol_fin_comp = dict(vol_comp)
        masa_fin = {cc: dict(masa[cc]) for cc in list(masa)}

        if es_obj:
            resultado = {
                'inicio_fosa': inicio, 'calc_fosa': calc,
                'inicio_grupo': inicio_grupo, 'calc_grupo': calc_grupo, 'real_grupo': real_grupo,
                'no_contabilizado': {g: (None if real_grupo[g] is None else real_grupo[g] - calc_grupo[g]) for g in GRUPOS},
                'fosas_sin_real': faltan,
                'hoyo_inicio': hoyo_prev, 'hoyo_fin': hoyo,
                'flujos': {g: dict(flujos[g]) for g in GRUPOS},
                'perdidas': {k: dict(v) for k, v in perdidas.items()},
                'inventario': inventario,
                'costo_dia_cat': dict(costo_dia_cat), 'costo_acum_cat': dict(costo_acum_cat),
                'concentraciones': {
                    cc: {
                        'vol_inicio': vol_inicio_comp.get(cc, 0.0), 'vol_fin': vol_fin_comp.get(cc, 0.0),
                        'inicio': {p: (m / vol_inicio_comp[cc] if vol_inicio_comp.get(cc, 0) > EPS else 0.0)
                                   for p, m in masa_inicio.get(cc, {}).items()},
                        'fin': {p: (m / vol_fin_comp[cc] if vol_fin_comp.get(cc, 0) > EPS else 0.0)
                                for p, m in masa_fin.get(cc, {}).items()},
                    }
                    for cc in set(masa_inicio) | set(masa_fin)
                },
                'avisos': avisos,
            }

        # ---- Pasar al día siguiente ----
        for n in fosas:
            r = fosas[n].get('real')
            fin_fosa[n] = float(r) if r is not None else calc[n]
        # La masa se ajusta al volumen real medido: una pérdida no contabilizada se lleva producto.
        for cc in list(masa):
            if cc == ACTIVO:
                real = real_grupo[ACTIVO]
            else:
                r = fosas.get(cc[1], {}).get('real')
                real = float(r) if r is not None else None
            v = vol_comp.get(cc, 0.0)
            if real is not None and v > EPS:
                f = max(real, 0.0) / v
                for p in list(masa[cc]):
                    masa[cc][p] *= f
        comp_prev = {n: comp_de(n) for n in fosas}
        vol_comp_prev = defaultdict(float)
        for n in fosas:
            vol_comp_prev[comp_de(n)] += fin_fosa[n]
        vol_comp_prev[ACTIVO] += hoyo
        hoyo_prev = hoyo

    return resultado
