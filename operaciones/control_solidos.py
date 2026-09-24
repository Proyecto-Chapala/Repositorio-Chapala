"""
Motor del inventario de mallas de zaranda (pestaña 6 — Control de Sólidos).

Función pura, sin Django: recibe los tickets y las transacciones del pozo ya ordenados por
reporte y los repite en orden. De esa repetición salen:

- el inventario de mallas NUEVAS y USADAS (en el almacén del taladro) de cualquier día,
- qué malla hay en cada posición de cada equipo,
- el costo diario y acumulado (las mallas nuevas se cargan al instalarlas: verificado con el
  manual de ONE-TRAX, el costo acumulado es múltiplo del precio de la malla).

Además valida TODA la línea de tiempo: si un cambio en un día viejo deja sin stock a un día
posterior, o intenta instalar en una posición que un día posterior ya ocupa, se rechaza con
un mensaje que dice qué día y qué malla. Las vistas usan esto dentro de una transacción de
base de datos: guardan, simulan, y si hay error deshacen el guardado.

Orden dentro de un mismo reporte: primero los tickets (lo recibido en el día se puede usar
ese mismo día) y luego las transacciones por su número de secuencia.
"""

from collections import defaultdict

INSTALAR_NUEVA = 'INSTALAR_NUEVA'
INSTALAR_USADA = 'INSTALAR_USADA'
A_ALMACEN = 'A_ALMACEN'
DESECHAR_EQUIPO = 'DESECHAR_EQUIPO'
DESECHAR_ALMACEN = 'DESECHAR_ALMACEN'


class ErrorMallas(Exception):
    """Movimiento imposible (sin stock, posición ocupada o vacía). El mensaje va al usuario."""


def _movimientos_vacios():
    return {
        'nuevas_inicial': 0, 'nuevas_recibidas': 0, 'nuevas_devueltas': 0,
        'nuevas_instaladas': 0, 'nuevas_final': 0,
        'usadas_inicial': 0, 'usadas_entradas': 0, 'usadas_salidas': 0, 'usadas_final': 0,
        'costo_diario': 0.0, 'costo_acumulado': 0.0,
    }


def simular(reportes, reporte_objetivo_id=None, nombres_malla=None):
    """
    reportes: lista ordenada por fecha de dicts
        {
          'id': int, 'fecha_texto': 'dd/mm/aaaa',
          'tickets': [{'sentido': 'ENTRADA'|'SALIDA',
                       'detalles': [{'malla_id', 'nuevas', 'usadas'}]}],
          'transacciones': [{'secuencia', 'accion', 'malla_id', 'serie', 'posicion', 'precio'}],
        }
    reporte_objetivo_id: reporte cuyo inventario y estado se quieren ver.
    nombres_malla: {malla_id: 'texto legible'} para los mensajes de error.

    Devuelve {'movimientos': {malla_id: {...}}, 'posiciones': {(serie, posicion): malla_id},
              'nuevas': {malla_id: stock}, 'usadas': {malla_id: stock}}
    con el estado al FINAL del reporte objetivo. Lanza ErrorMallas si cualquier día
    (antes o después del objetivo) no cuadra.
    """
    nombres_malla = nombres_malla or {}

    def nombre(malla_id):
        return nombres_malla.get(malla_id, f"malla {malla_id}")

    nuevas = defaultdict(int)
    usadas = defaultdict(int)
    posiciones = {}
    costo_acumulado = defaultdict(float)

    resultado = None

    for rep in reportes:
        es_objetivo = rep['id'] == reporte_objetivo_id
        dia = rep.get('fecha_texto', '')
        mov = defaultdict(_movimientos_vacios)

        if es_objetivo:
            for malla_id in set(nuevas) | set(usadas):
                mov[malla_id]['nuevas_inicial'] = nuevas[malla_id]
                mov[malla_id]['usadas_inicial'] = usadas[malla_id]

        # 1) Tickets del día
        for ticket in rep.get('tickets', []):
            entrada = ticket['sentido'] == 'ENTRADA'
            for det in ticket.get('detalles', []):
                m = det['malla_id']
                n = int(det.get('nuevas') or 0)
                u = int(det.get('usadas') or 0)
                mov[m]  # asegura la fila
                if entrada:
                    nuevas[m] += n
                    usadas[m] += u
                    mov[m]['nuevas_recibidas'] += n
                    mov[m]['usadas_entradas'] += u
                else:
                    if n > nuevas[m]:
                        raise ErrorMallas(
                            f"El {dia}: el ticket devuelve {n} mallas nuevas de {nombre(m)} "
                            f"pero solo hay {nuevas[m]} en stock."
                        )
                    if u > usadas[m]:
                        raise ErrorMallas(
                            f"El {dia}: el ticket devuelve {u} mallas usadas de {nombre(m)} "
                            f"pero solo hay {usadas[m]} en el almacén."
                        )
                    nuevas[m] -= n
                    usadas[m] -= u
                    mov[m]['nuevas_devueltas'] += n
                    mov[m]['usadas_salidas'] += u

        # 2) Transacciones del día
        for tr in sorted(rep.get('transacciones', []), key=lambda t: t['secuencia']):
            accion = tr['accion']
            m = tr['malla_id']
            clave = (tr.get('serie') or '', tr.get('posicion'))
            etiqueta = f"la posición {tr.get('posicion')} del equipo {tr.get('serie')}"
            mov[m]

            if accion in (INSTALAR_NUEVA, INSTALAR_USADA):
                if clave in posiciones:
                    raise ErrorMallas(
                        f"El {dia} (transacción #{tr['secuencia']}): {etiqueta} ya tiene "
                        f"{nombre(posiciones[clave])}. Retírala antes de instalar otra."
                    )
                if accion == INSTALAR_NUEVA:
                    if nuevas[m] <= 0:
                        raise ErrorMallas(
                            f"El {dia} (transacción #{tr['secuencia']}): no hay mallas nuevas de "
                            f"{nombre(m)} en stock. Registra primero el ticket de recepción."
                        )
                    nuevas[m] -= 1
                    precio = float(tr.get('precio') or 0)
                    mov[m]['nuevas_instaladas'] += 1
                    mov[m]['costo_diario'] += precio
                    costo_acumulado[m] += precio
                else:
                    if usadas[m] <= 0:
                        raise ErrorMallas(
                            f"El {dia} (transacción #{tr['secuencia']}): no hay mallas usadas de "
                            f"{nombre(m)} en el almacén."
                        )
                    usadas[m] -= 1
                    mov[m]['usadas_salidas'] += 1
                posiciones[clave] = m

            elif accion in (A_ALMACEN, DESECHAR_EQUIPO):
                actual = posiciones.get(clave)
                if actual is None:
                    raise ErrorMallas(
                        f"El {dia} (transacción #{tr['secuencia']}): {etiqueta} está vacía, "
                        f"no hay malla que retirar."
                    )
                if actual != m:
                    raise ErrorMallas(
                        f"El {dia} (transacción #{tr['secuencia']}): {etiqueta} tiene "
                        f"{nombre(actual)}, no {nombre(m)}."
                    )
                del posiciones[clave]
                if accion == A_ALMACEN:
                    usadas[m] += 1
                    mov[m]['usadas_entradas'] += 1

            elif accion == DESECHAR_ALMACEN:
                if usadas[m] <= 0:
                    raise ErrorMallas(
                        f"El {dia} (transacción #{tr['secuencia']}): no hay mallas usadas de "
                        f"{nombre(m)} en el almacén para desechar."
                    )
                usadas[m] -= 1
                mov[m]['usadas_salidas'] += 1

            else:
                raise ErrorMallas(f"Acción desconocida: {accion}")

        if es_objetivo:
            for malla_id, fila in mov.items():
                fila['nuevas_final'] = nuevas[malla_id]
                fila['usadas_final'] = usadas[malla_id]
                fila['costo_acumulado'] = round(costo_acumulado[malla_id], 2)
                fila['costo_diario'] = round(fila['costo_diario'], 2)
            # Mallas sin movimiento hoy pero con costo acumulado de días anteriores.
            for malla_id, costo in costo_acumulado.items():
                if malla_id not in mov:
                    fila = mov[malla_id]
                    fila['nuevas_inicial'] = fila['nuevas_final'] = nuevas[malla_id]
                    fila['usadas_inicial'] = fila['usadas_final'] = usadas[malla_id]
                    fila['costo_acumulado'] = round(costo, 2)
            resultado = {
                'movimientos': {k: dict(v) for k, v in mov.items()},
                'posiciones': dict(posiciones),
                'nuevas': dict(nuevas),
                'usadas': dict(usadas),
            }

    if resultado is None:
        resultado = {
            'movimientos': {},
            'posiciones': dict(posiciones),
            'nuevas': dict(nuevas),
            'usadas': dict(usadas),
        }
    return resultado


# =====================================================================
# Fase 2 — Rendimiento de los equipos de control de sólidos
#
# Fórmulas verificadas con los tres ejemplos del manual (págs. 118-120):
#   - Lo que descarga un equipo son recortes + el lodo pegado a ellos. Con
#     MOC = lodo / recortes:  lodo = descargado × MOC / (1 + MOC)
#     (1 → 0.6 con MOC 1.463; 9.2 → 4.2 con 0.855; 2.2 → 0.4 con 0.214).
#   - Zarandas, limpiador de lodo y secador: recortes = volumen de hoyo perforado
#     en el día × % de recortes; descargado = recortes × (1 + MOC).
#   - Centrífuga, por balance de masa: Q_descarte = Q_entrada × (ρe − ρs) / (ρd − ρs);
#     descargado = Q_descarte × horas (18.9 × 0.07 / 0.72 = 1.84 gpm; × 22 h = 9.2 m³).
# Espejo en JavaScript: reporte_control_solidos.js (csCalcularRendimiento).
# =====================================================================

CAPACIDAD_CONSTANTE = 1029.4       # in² → bbl/ft
GALONES_POR_BARRIL = 42.0

TIPOS_POR_RECORTES = ('ZARANDA', 'LIMPIADOR_LODO', 'SECADOR_RECORTES')
TIPOS_CENTRIFUGA = ('CENTRIFUGA',)


def volumen_hoyo_perforado(diametro_in, avance_ft):
    """Volumen (bbl) del hoyo abierto perforado en el día."""
    d = float(diametro_in or 0)
    avance = float(avance_ft or 0)
    if d <= 0 or avance <= 0:
        return 0.0
    return d * d / CAPACIDAD_CONSTANTE * avance


def _f(valor):
    try:
        return float(valor) if valor not in (None, '') else None
    except (TypeError, ValueError):
        return None


def calcular_rendimiento(tipo_equipo, datos, vol_hoyo_bbl):
    """
    datos: dict con horas, mud_on_cuttings, porcentaje_recortes, caudal_entrada_gpm,
    densidad_entrada, densidad_salida, densidad_descarte (pueden venir vacíos).
    Devuelve los volúmenes del día en bbl (None cuando falta un dato para calcular).
    """
    moc = _f(datos.get('mud_on_cuttings')) or 0.0
    horas = _f(datos.get('horas')) or 0.0
    r = {
        'recortes_bbl': None, 'descargado_bbl': None, 'lodo_bbl': None,
        'caudal_descarte_gpm': None, 'caudal_salida_gpm': None,
    }

    if tipo_equipo in TIPOS_POR_RECORTES:
        pct = _f(datos.get('porcentaje_recortes'))
        if pct is None:
            return r
        recortes = vol_hoyo_bbl * pct / 100.0
        r['recortes_bbl'] = recortes
        r['descargado_bbl'] = recortes * (1.0 + moc)
        r['lodo_bbl'] = recortes * moc

    elif tipo_equipo in TIPOS_CENTRIFUGA:
        q_in = _f(datos.get('caudal_entrada_gpm'))
        rho_e = _f(datos.get('densidad_entrada'))
        rho_s = _f(datos.get('densidad_salida'))
        rho_d = _f(datos.get('densidad_descarte'))
        if None in (q_in, rho_e, rho_s, rho_d) or rho_d <= rho_s:
            return r
        q_desc = q_in * (rho_e - rho_s) / (rho_d - rho_s)
        q_desc = min(max(q_desc, 0.0), q_in)
        descargado = q_desc * horas * 60.0 / GALONES_POR_BARRIL
        r['caudal_descarte_gpm'] = q_desc
        r['caudal_salida_gpm'] = q_in - q_desc
        r['descargado_bbl'] = descargado
        r['lodo_bbl'] = descargado * moc / (1.0 + moc)
        r['recortes_bbl'] = descargado - r['lodo_bbl']

    return r
