"""
Reporte diario en Excel con el formato del libro de ONE-TRAX (Mud Report), en español.

Parte de la plantilla operaciones/plantillas/reporte_diario_onetrax.xlsx (formato, combinaciones,
anchos y áreas de impresión del original) y la llena con los datos del reporte. No calcula nada
propio: toma los resultados de los mismos motores que usan las pestañas (volumetría, control de
sólidos, geometría, hidráulica y costos), así el Excel siempre coincide con la pantalla.

Hojas: reporte de lodo (la variante del tipo de lodo del reporte: base agua, CALDRIL, base aceite
o base sintética), propiedades extra, contabilidad de volumen, inventario químico (DF, por nombre
y completo), uso y costo de equipos e inventario de mallas.
"""

import io
import os
from datetime import datetime

import openpyxl

PLANTILLA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plantillas', 'reporte_diario_onetrax.xlsx')
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'operaciones', 'img', 'logo_reporte.png')

HOJA_LODO = {'WBM': 'Lodo Base Agua', 'WBM_CACL2': 'Lodo CALDRIL', 'OBM': 'Lodo Base Aceite', 'SBM': 'Lodo Base Sintetica'}
HOJA_EXTRA = {'WBM': 'Prop Extra Base Agua', 'WBM_CACL2': 'Prop Extra Base Agua',
              'OBM': 'Prop Extra Aceite-Sint', 'SBM': 'Prop Extra Aceite-Sint'}
FILAS_INV = [range(11, 61), range(71, 121), range(131, 181)]   # 3 páginas de 50 productos


# ---------------------------------------------------------------- formato de números

def _f(v):
    try:
        return None if v is None or v == '' else float(v)
    except (TypeError, ValueError):
        return None


def _t(v, dec=0):
    """Número como texto con coma decimal (como lo imprime ONE-TRAX en español)."""
    v = _f(v)
    if v is None:
        return ''
    texto = f"{v:.{dec}f}"
    return texto.replace('.', ',')


def _g(v):
    """Número corto sin ceros de más (6,5 / 12 / 0,25)."""
    v = _f(v)
    if v is None:
        return ''
    return f"{v:g}".replace('.', ',')


def _par(a, b, dec_a=0, dec_b=0, sep='/'):
    if _f(a) is None and _f(b) is None:
        return ''
    return f"{_t(a, dec_a)}{sep}{_t(b, dec_b)}"


def _num(v, dec=2):
    v = _f(v)
    return None if v is None else round(v, dec)


def _poner(ws, celda, valor):
    if valor is None or valor == '':
        return
    ws[celda].value = valor
    if isinstance(valor, datetime):
        ws[celda].number_format = 'DD/MM/YYYY'


def _fecha(ws, celda, fecha):
    if fecha:
        _poner(ws, celda, datetime(fecha.year, fecha.month, fecha.day))


# ---------------------------------------------------------------- recolección de datos

def _datos(pozo, reporte):
    from .views_daily_reports import calcular_geometria_reporte, obtener_hidraulica_bombas
    from .views_inventario import _estado_volumetria, resumen_costos
    from .views_control_solidos import _resumen as resumen_mallas, _resumen_equipos
    from .views_hidraulica import calcular_hidraulica_reporte

    d = {'pozo': pozo, 'reporte': reporte}
    d['header'] = getattr(pozo, 'well_header_info', None)
    d['anterior'] = pozo.reportes_diarios.filter(fecha__lt=reporte.fecha).order_by('-fecha').first()
    d['bit'] = getattr(reporte, 'bit_data', None)
    d['bombas'] = list(reporte.bombas.all().order_by('numero_bomba'))
    d['boquillas'] = list(reporte.boquillas.all())
    d['checks'] = list(reporte.mud_checks.all().order_by('check_number'))[:4]
    d['comentarios'] = getattr(reporte, 'comentarios', None)
    d['tramos'] = list(reporte.tramos_sarta.all().order_by('orden'))
    d['actividades'] = list(reporte.actividades_tiempo.all().order_by('orden', 'id'))
    try:
        geo, _, _ = calcular_geometria_reporte(pozo, reporte)
    except Exception:
        geo = {'secciones': [], 'totales': {}}
    d['geo'] = geo
    d['bbl_stk'], d['caudal'] = obtener_hidraulica_bombas(reporte)
    d['vol'] = _estado_volumetria(pozo, reporte)
    d['costo_dia'], d['costo_acum'], _ = resumen_costos(pozo, reporte)
    d['mallas'] = resumen_mallas(pozo, reporte)
    d['equipos'] = _resumen_equipos(pozo, reporte)
    from .models_control_solidos import TransaccionMalla
    usadas = {}
    for t in TransaccionMalla.objects.filter(reporte__pozo=pozo, reporte__fecha__lte=reporte.fecha,
                                             accion=TransaccionMalla.INSTALAR_NUEVA):
        usadas[t.malla_id] = usadas.get(t.malla_id, 0) + 1
    d['mallas_usadas_pozo'] = usadas
    edicion = '5' if pozo.usar_api_5ta_edicion_hidraulica else '4'
    try:
        d['hid'] = calcular_hidraulica_reporte(pozo, reporte, edicion)
    except Exception:
        d['hid'] = {'faltan': ['error']}
    extras = {}
    for p in pozo.propiedades_extra.filter(orden_impresion__gt=0).order_by('orden_impresion', 'numero'):
        extras.setdefault(p.tipo_fluido, []).append(p)
    d['extras'] = extras
    valores = {}
    for c in d['checks']:
        for v in c.extra_values.all():
            valores[(c.id, v.propiedad_extra_id)] = v.valor
    d['valores_extra'] = valores
    return d


def _tipo_extra(reporte):
    return 'WBM' if reporte.tipo_lodo in ('WBM', 'WBM_CACL2') else 'OBM'


# ---------------------------------------------------------------- encabezado común

def _encabezado_lodo(ws, d, titulo):
    pozo, rep, h = d['pozo'], d['reporte'], d['header']
    ws['J2'].value = f"{titulo}{rep.numero_reporte}"
    _poner(ws, 'B3', h.operador if h else '')
    _poner(ws, 'E3', h.field_area if h else '')
    ws['I3'].value = f"{_t(rep.profundidad_actual)} ft /"
    ws['J3'].value = f"{_t(rep.profundidad_tvd)} ft"
    _poner(ws, 'B4', rep.operador_representante)
    _poner(ws, 'E4', h.descripcion if h else '')
    _fecha(ws, 'I4', rep.fecha)
    _poner(ws, 'B5', pozo.nombre)
    _poner(ws, 'E5', h.ubicacion if h else '')
    spud = (h.spud_date if h and h.spud_date else None) or getattr(pozo, 'fecha_primera_captura', None)
    _fecha(ws, 'I5', spud)
    _poner(ws, 'B6', h.contratista if h else '')
    if h and h.water_depth_ft is not None:
        ws['E6'].value = f"{_g(h.water_depth_ft)} ft"
    _poner(ws, 'I6', rep.tipo_fluido_display)
    _poner(ws, 'B7', rep.contratista_representante)
    _poner(ws, 'E7', h.nombre_taladro if h else '')
    _poner(ws, 'I7', rep.actividad_actual)


def _encabezado_corto(ws, d, celdas):
    """Encabezado de las hojas de equipos y mallas (operador, pozo, fecha, etc.)."""
    pozo, rep, h = d['pozo'], d['reporte'], d['header']
    spud = (h.spud_date if h and h.spud_date else None) or getattr(pozo, 'fecha_primera_captura', None)
    valores = {
        'operador': h.operador if h else '', 'pozo': pozo.nombre,
        'fecha': datetime(rep.fecha.year, rep.fecha.month, rep.fecha.day),
        'rep1': rep.operador_representante, 'campo': h.field_area if h else '',
        'spud': datetime(spud.year, spud.month, spud.day) if spud else None,
        'contratista': h.contratista if h else '', 'ubicacion': h.ubicacion if h else '',
        'lodo': rep.tipo_fluido_display, 'rep2': rep.contratista_representante, 'actividad': rep.actividad_actual,
    }
    for clave, celda in celdas.items():
        _poner(ws, celda, valores.get(clave))


# ---------------------------------------------------------------- reporte de lodo

def _sarta_y_revestidor(ws, d):
    lineas = []
    # De superficie hacia abajo; la mecha va aparte en su propia línea.
    for t in reversed(d['tramos']):
        texto = (t.descripcion or '').lower()
        if not t.longitud_ft or any(p in texto for p in ('mecha', 'barrena', 'bit')):
            continue
        lineas.append(f"{_g(t.longitud_ft)} ft, {_g(t.od_in)}-in {t.descripcion or ''}".strip())
    for i, texto in enumerate(lineas[:6]):
        ws[f'A{9 + i}'].value = texto
    if d['boquillas']:
        partes = [f"{b.cantidad}x{b.size_32nds}" for b in d['boquillas']]
        ws['A15'].value = f"Boquillas {'/'.join(partes)} 1/32\""
    bit = d['bit']
    if bit:
        ws['A16'].value = f"Mecha {_g(bit.bit_size)}-in {bit.bit_description or ''}".strip()

    prof = _f(d['reporte'].profundidad_actual) or 0.0
    revest = []
    for iv in d['pozo'].intervalos_revestimiento.all().order_by('numero_intervalo'):
        p = _f(iv.profundidad_ft)
        if not iv.casing_od_in or p is None or (prof and p > prof + 0.5):
            continue
        tvd = _f(iv.tvd_ft)
        revest.append(f"{_g(iv.casing_od_in)}-in @{_g(p)} ft" + (f" ({_g(tvd)} TVD)" if tvd else ''))
    for i, texto in enumerate(revest[-4:]):
        ws[f'C{9 + i}'].value = texto


def _volumen_y_circulacion(ws, d):
    vol = d['vol']
    hoyo = _f((vol.get('hoyo') or {}).get('total_fluido')) or 0.0
    activas = sum(_f(f.get('real')) or 0.0 for f in vol.get('fosas', []) if f.get('grupo') == 'ACTIVO')
    ws['E10'].value = round(hoyo, 0)
    ws['F10'].value = round(activas, 0)
    total = hoyo + activas
    ws['E12'].value = round(total, 0)
    anterior = d['anterior']
    avance = max((_f(d['reporte'].profundidad_actual) or 0) - (_f(anterior.profundidad_actual) or 0 if anterior else 0), 0)
    if not anterior:
        avance = 0.0
    ws['E14'].value = round(avance, 0)
    ws['F14'].value = 'ft'
    vol_perf = (d['equipos'].get('contexto') or {}).get('volumen_hoyo_bbl') or 0.0
    ws['E16'].value = round(vol_perf, 1)
    ws['F16'].value = 'bbl'

    bombas = d['bombas'][:2]
    for b, col in zip(bombas, ('I', 'J')):
        _poner(ws, f'{col}9', b.make_model)
        ws[f'{col}10'].value = f"{_g(b.liner_diameter)}x{_g(b.stroke_length)} in"
        ws[f'{col}11'].value = round(b.desplazamiento_gal_stk, 3)
        ws[f'{col}12'].value = f"{_g(b.pump_rate_spm)}@{_g(b.eficiencia_pct)}%"
    ws['H11'].value = 'Capacidad gal/emb'
    caudal = d['caudal']
    ws['I13'].value = round(caudal, 0)
    ws['J13'].value = 'gal/min'
    if d['bit'] and _f(d['bit'].pump_pressure):
        ws['I14'].value = round(_f(d['bit'].pump_pressure), 0)
    ws['J14'].value = 'psi'
    t = d['geo'].get('totales') or {}
    if t.get('bottom_up_minutos'):
        ws['I15'].value = f"{_t(t['bottom_up_minutos'], 1)} min     {_t(t.get('bottom_up_emboladas'))} emb"
    if caudal > 0 and total > 0:
        minutos = total * 42.0 / caudal
        emb = total / d['bbl_stk'] if d['bbl_stk'] else 0
        ws['I16'].value = f"{_t(minutos, 1)} min     {_t(emb)} emb"


def _propiedades(ws, d, variante):
    unidades_wbm = {19: '°F', 20: 'ft', 21: 'lb/gal', 22: 's/qt', 23: '°F', 27: 'cP', 28: 'lb/100ft²',
                    29: 'lb/100ft²', 30: 'cc/30min', 31: 'cc/30min', 32: '1/32"', 33: '%Vol', 34: '%Vol',
                    35: '%Vol', 36: 'lb/bbl', 40: 'mg/L'}
    unidades_obm = {19: '°F', 20: 'ft', 21: 'lb/gal', 22: 's/qt', 23: '°F', 27: 'cP', 28: 'lb/100ft²',
                    29: 'lb/100ft²', 30: 'cc/30min', 31: 'cc/30min', 32: '1/32"', 33: '%Vol', 34: '%Vol',
                    35: '%Vol', 36: '%Vol', 39: 'mg/L', 40: '%peso', 41: 'lb/bbl', 42: 'V'}
    base_agua = variante in ('WBM', 'WBM_CACL2')
    for fila, u in (unidades_wbm if base_agua else unidades_obm).items():
        ws[f'B{fila}'].value = u

    for c, col in zip(d['checks'], ('C', 'D', 'E', 'F')):
        comun = {
            18: f"{c.sample_from or ''} {c.time_taken or ''}".strip(),
            19: _num(c.flowline_temp, 0),
            20: _par(c.depth, c.tvd),
            21: f"{_t(c.mud_weight, 1)}@{_t(c.mw_temp)}" if _f(c.mud_weight) is not None else '',
            22: _num(c.funnel_viscosity, 0),
            23: _num(c.rheology_temp, 0),
            24: _par(c.r600, c.r300), 25: _par(c.r200, c.r100), 26: _par(c.r6, c.r3),
            27: _num(c.pv, 0), 28: _num(c.yp, 0),
            29: (f"{_t(c.gel_10s)}/{_t(c.gel_10m)}/{_t(c.gel_30m)}"
                 if any(_f(x) is not None for x in (c.gel_10s, c.gel_10m, c.gel_30m)) else ''),
            30: _num(c.api_fluid_loss, 1),
            31: _t(c.hthp_fluid_loss, 1),
            32: _par(c.cake_api, c.cake_hthp),
        }
        if base_agua:
            comun.update({
                33: _num(c.solids_pct, 1), 34: _par(c.oil_pct, c.water_pct), 35: _num(c.sand_pct, 2),
                36: _num(c.mbt, 1), 37: f"{_t(c.ph, 1)}@{_t(c.ph_temp)}" if _f(c.ph) is not None else '',
                38: _num(c.pm, 2), 39: _par(c.pf, c.mf, 2, 2), 40: _num(c.chlorides, 0),
                41: _num(c.calcium_hardness, 0),
            })
        else:
            comun.update({
                33: _num(c.solids_pct, 1), 34: _num(c.adjusted_solids_pct, 1), 35: _num(c.oil_pct, 1),
                36: _num(c.water_pct, 1), 37: c.oil_water_ratio or '', 38: _num(c.pm, 2),
                39: _num(c.chlorides, 0), 40: _num(c.salt_pct_wt, 1), 41: _num(c.excess_lime, 2),
                42: _num(c.electrical_stability, 0),
            })
        for fila, valor in comun.items():
            if valor not in (None, ''):
                ws[f'{col}{fila}'].value = valor

    # Propiedades extra 1-8 debajo de las fijas
    primera = 42 if base_agua else 43
    extras = [p for p in d['extras'].get(_tipo_extra(d['reporte']), []) if p.numero <= 8][:8]
    for i, p in enumerate(extras):
        fila = primera + i
        ws[f'A{fila}'].value = p.etiqueta
        _poner(ws, f'B{fila}', p.unidad)
        for c, col in zip(d['checks'], ('C', 'D', 'E', 'F')):
            _poner(ws, f'{col}{fila}', d['valores_extra'].get((c.id, p.id)))


def _productos_y_equipos(ws, d):
    usados = [p for p in d['vol'].get('inventario', []) if (p.get('usado_dia') or 0) > 0]
    for i, p in enumerate(usados[:15]):
        fila = 19 + i
        ws[f'G{fila}'].value = p['descripcion']
        ws[f'I{fila}'].value = _texto_tamano(p)
        ws[f'J{fila}'].value = _num(p['usado_dia'], 2)

    # Modelo/mallas: mallas instaladas hoy en cada equipo ("4X170", "2X140 2X100")
    mallas_por_serie = {}
    for e in d['mallas'].get('equipos', []):
        conteo = []
        for pos in e['posiciones']:
            m = pos.get('mesh_size')
            if not m:
                continue
            for item in conteo:
                if item[0] == m:
                    item[1] += 1
                    break
            else:
                conteo.append([m, 1])
        mallas_por_serie[e['serie']] = ' '.join(f"{n}X{m}" for m, n in conteo)
    filas = [e for e in d['equipos'].get('equipos', []) if e.get('guardado') and (_f(e['datos'].get('horas')) or 0) > 0]
    for i, e in enumerate(filas[:11]):
        fila = 36 + i
        ws[f'G{fila}'].value = e['descripcion']
        _poner(ws, f'I{fila}', mallas_por_serie.get(e['serie']))
        ws[f'J{fila}'].value = _num(e['datos'].get('horas'), 1)


def _texto_tamano(p):
    unidad = (p.get('unidad') or '').strip()
    if not unidad:
        return '1 servicio'
    tam = _g(p.get('tamano')) or '1'
    return f"{tam} {unidad} {p.get('empaque') or ''}".strip()


def _especificacion_y_textos(ws, d, variante):
    cm = d['comentarios']
    principal = next((c for c in d['checks'] if c.is_primary), d['checks'][0] if d['checks'] else None)
    if cm:
        _poner(ws, 'H48', cm.spec_mud_weight)
        _poner(ws, 'H49', cm.spec_viscosidad)
        _poner(ws, 'H50', cm.spec_filtrado)
    if principal:
        _poner(ws, 'J48', _num(principal.mud_weight, 1))
        _poner(ws, 'J49', _num(principal.funnel_viscosity, 0))
        filtrado = principal.api_fluid_loss if variante in ('WBM', 'WBM_CACL2') else principal.hthp_fluid_loss
        _poner(ws, 'J50', _num(filtrado, 1))
    base_agua = variante in ('WBM', 'WBM_CACL2')
    fila_res = 50 if base_agua else 51
    reserva = sum(_f(f.get('real')) or 0.0 for f in d['vol'].get('fosas', []) if f.get('grupo') in ('RESERVA', 'PREMEZCLA'))
    ws[f'B{fila_res}'].value = 'bbl'
    ws[f'C{fila_res}'].value = round(reserva, 0)
    fila_txt = 52 if base_agua else 53
    if cm:
        _poner(ws, f'A{fila_txt}', cm.remarks_and_treatment)
        _poner(ws, f'E{fila_txt}', cm.remarks)


def _bloques_inferiores(ws, d, variante):
    base_agua = variante in ('WBM', 'WBM_CACL2')
    r0 = 54 if base_agua else 55          # primera fila de datos de los 4 bloques

    # Distribución de tiempo (10 filas)
    for i, a in enumerate(d['actividades'][:10]):
        ws[f'A{r0 + i}'].value = a.descripcion
        ws[f'B{r0 + i}'].value = _num(a.horas, 2)

    # Contabilidad de volumen del día (todas las fosas) + pérdidas por categoría (hasta 10)
    grupos = d['vol'].get('grupos', [])
    suma = lambda k: sum(_f(g['flujos'].get(k)) or 0.0 for g in grupos)
    ws[f'D{r0}'].value = round(suma('aceite'), 1)
    ws[f'D{r0 + 1}'].value = round(suma('agua'), 1)
    ws[f'D{r0 + 2}'].value = round(suma('recibido'), 1)
    ws[f'D{r0 + 3}'].value = round(suma('devuelto'), 1)
    perdidas = [p for p in d['vol'].get('perdidas', [])][:10]
    for i, p in enumerate(perdidas):
        ws[f'C{r0 + 4 + i}'].value = p['descripcion']
        ws[f'D{r0 + 4 + i}'].value = _num(p['subtotal'], 1)
    unidad = 'bbl'
    ws[f'C{r0 - 1}'].value = f"CONTAB. DE VOLUMEN ({unidad})"

    # Análisis de sólidos del chequeo principal
    principal = next((c for c in d['checks'] if c.is_primary), d['checks'][0] if d['checks'] else None)
    if principal:
        c = principal
        par = lambda a, b: (f"{_t(a, 1)}/ {_t(b, 1)}" if _f(a) is not None or _f(b) is not None else '')
        if variante == 'WBM':
            valores = [par(c.nacl_pct, c.nacl_ppb), par(c.kcl_pct, c.kcl_ppb), par(c.lgs_pct, c.lgs_ppb),
                       par(c.bentonite_pct, c.bentonite_ppb), par(c.drill_solids_pct, c.drill_solids_ppb),
                       par(c.hgs_pct, c.hgs_ppb), f" -  /  {_t(c.chem_conc, 1)}" if _f(c.chem_conc) else '',
                       '', _t(c.avg_sg_solids, 2)]
        elif variante == 'WBM_CACL2':
            valores = [_t(c.salt_ppb, 1), _t(c.salt_pct_wt, 1), '', _t(c.adjusted_solids_pct, 1),
                       _t(c.avg_sg_solids, 2), _t(c.lgs_pct, 1), _t(c.lgs_ppb, 1), _t(c.hgs_pct, 1), _t(c.hgs_ppb, 1)]
        else:
            valores = [_t(c.salt_pct_wt, 1), _t(c.salt_ppb, 1), _t(c.adjusted_solids_pct, 1), c.oil_water_ratio or '',
                       _t(c.avg_sg_solids, 2), _t(c.lgs_pct, 1), _t(c.lgs_ppb, 1), _t(c.hgs_pct, 1), _t(c.hgs_ppb, 1)]
        for i, v in enumerate(valores):
            _poner(ws, f'G{r0 + i}', v)
        if variante == 'WBM_CACL2':
            ws[f'E{r0}'].value = 'Cloruro de Calcio (lb/bbl)'
            ws[f'E{r0 + 6}'].value = 'Sólidos Baja Gravedad (lb/bbl)'
            ws[f'E{r0 + 8}'].value = 'Sólidos Alta Gravedad (lb/bbl)'
        if base_agua:
            ws[f'E{r0 - 1}'].value = 'ANÁLISIS DE SÓLIDOS (%/lb/bbl)' if variante == 'WBM' else 'ANÁLISIS DE SÓLIDOS'

    # Reología e hidráulica
    hid = d['hid']
    if not hid.get('faltan') and hid.get('reologia'):
        reo, m, secs = hid['reologia'], hid['mecha'], hid.get('secciones', [])
        ws[f'J{r0}'].value = f"{_t(reo['tuberia']['n'], 3)}/{_t(reo['anular']['n'], 3)}"
        ws[f'J{r0 + 1}'].value = f"{_t(reo['tuberia']['k'], 3)}/{_t(reo['anular']['k'], 3)}"
        ws[f'J{r0 + 2}'].value = f"{_t(m['perdida'])} / {_t(m['pct'], 1)}"
        ws[f'J{r0 + 3}'].value = f"{_t(m['hhp'])} / {_t(m['hsi'], 2)}"
        ws[f'J{r0 + 4}'].value = _num(m['vel_chorro'], 0)
        tuberia, collar = _secciones_tipo(d, secs)
        if tuberia:
            ws[f'J{r0 + 5}'].value = _num(tuberia['vel_anular'], 1)
            ws[f'J{r0 + 7}'].value = _num(tuberia['vel_critica'], 0)
        if collar:
            ws[f'J{r0 + 6}'].value = _num(collar['vel_anular'], 1)
            ws[f'J{r0 + 8}'].value = _num(collar['vel_critica'], 0)
        zapata = _ecd_zapata(d, secs)
        _poner(ws, f'J{r0 + 9}', zapata)
        _poner(ws, f'J{r0 + 10}', _num(hid['totales'].get('ecd_fondo'), 2))

    # Costos (diario / acumulado) y contactos
    rc = 67 if base_agua else 68
    cd, ca = d['costo_dia'], d['costo_acum']
    for i, (dia, acu) in enumerate([(cd['df_chem'], ca['df_chem']), (cd['ife_sc'], ca['ife_sc']),
                                    (cd['df_equip'], ca['df_equip'])]):
        ws[f'G{rc + i}'].value = dia
        ws[f'I{rc + i}'].value = acu
    ws[f'G{rc + 3}'].value = cd['total']
    ws[f'I{rc + 3}'].value = ca['total']
    rep = d['reporte']
    ingenieros = ' / '.join(x for x in (rep.mi_representante_1, rep.mi_representante_2) if x)
    fila_con = rc + 2
    _poner(ws, f'A{fila_con}', ingenieros)
    _poner(ws, f'C{fila_con}', rep.telefono_taladro)
    _poner(ws, f'D{fila_con}', rep.telefono_almacen)
    _poner(ws, f'A{fila_con + 1}', rep.telefonos)


def _secciones_tipo(d, secciones):
    """Sección representativa de tubería y de portamechas (la más profunda de cada tipo)."""
    con_junta = {(t.descripcion or '').strip() for t in d['tramos'] if (_f(t.tool_joint_length_in) or 0) > 0}
    sin_junta = {(t.descripcion or '').strip() for t in d['tramos'][1:] if (_f(t.tool_joint_length_in) or 0) == 0}
    tuberia = collar = None
    for s in secciones:
        if s.get('vel_anular') is None:
            continue
        comp = (s.get('descripcion') or '').split(' / ')[0].strip()
        if comp in con_junta:
            tuberia = s
        elif comp in sin_junta:
            collar = s
    return tuberia, collar


def _ecd_zapata(d, secciones):
    prof = _f(d['reporte'].profundidad_actual) or 0.0
    zapatas = [_f(iv.profundidad_ft) for iv in d['pozo'].intervalos_revestimiento.all()
               if _f(iv.profundidad_ft) and (not prof or _f(iv.profundidad_ft) <= prof + 0.5)]
    if not zapatas or not secciones:
        return None
    zapata = max(zapatas)
    mejor = None
    for s in secciones:
        if s.get('md_ft') is not None and s['md_ft'] <= zapata + 1:
            mejor = s
    return _num(mejor['ecd'], 2) if mejor and mejor.get('ecd') is not None else None


def _hoja_lodo(ws, d, variante):
    titulos = {'WBM': 'REPORTE DE LODO BASE AGUA N° ', 'WBM_CACL2': 'REPORTE DE LODO CALDRIL N° ',
               'OBM': 'REPORTE DE LODO BASE ACEITE N° ', 'SBM': 'REPORTE DE LODO BASE SINTÉTICA N° '}
    _encabezado_lodo(ws, d, titulos[variante])
    ws['E8'].value = 'VOLUMEN DE LODO (bbl)'
    _sarta_y_revestidor(ws, d)
    _volumen_y_circulacion(ws, d)
    _propiedades(ws, d, variante)
    _productos_y_equipos(ws, d)
    _especificacion_y_textos(ws, d, variante)
    _bloques_inferiores(ws, d, variante)


# ---------------------------------------------------------------- propiedades extra (9 a 60)

def _hoja_extra(ws, d, variante):
    titulo = 'PROPIEDADES EXTRA BASE AGUA N° ' if variante in ('WBM', 'WBM_CACL2') else 'PROPIEDADES EXTRA ACEITE/SINTÉTICO N° '
    _encabezado_lodo(ws, d, titulo)
    for c, col in zip(d['checks'], ('C', 'D', 'E', 'F')):
        ws[f'{col}9'].value = f"{c.sample_from or ''} {c.time_taken or ''}".strip()
    extras = [p for p in d['extras'].get(_tipo_extra(d['reporte']), []) if p.numero > 8][:52]
    for i, p in enumerate(extras):
        fila = 10 + i
        ws[f'A{fila}'].value = p.etiqueta
        _poner(ws, f'B{fila}', p.unidad)
        for c, col in zip(d['checks'], ('C', 'D', 'E', 'F')):
            _poner(ws, f'{col}{fila}', d['valores_extra'].get((c.id, p.id)))
    rep = d['reporte']
    _poner(ws, 'A63', ' / '.join(x for x in (rep.mi_representante_1, rep.mi_representante_2) if x))
    _poner(ws, 'A64', rep.telefonos)
    _poner(ws, 'C64', rep.telefono_taladro)
    _poner(ws, 'E64', rep.telefono_almacen)
    ws['G64'].value = d['costo_dia']['total']
    ws['I64'].value = d['costo_acum']['total']


# ---------------------------------------------------------------- contabilidad de volumen

def _hoja_volumen(ws, d):
    pozo, rep, h, vol = d['pozo'], d['reporte'], d['header'], d['vol']
    _poner(ws, 'B5', h.operador if h else '')
    _poner(ws, 'B6', pozo.nombre)
    _fecha(ws, 'F5', rep.fecha)
    ws['F6'].value = rep.numero_reporte
    ws['B9'].value = 'bbl'
    ws['C9'].value = 'lb/gal'
    ws['D9'].value = 'bbl'
    fosas = vol.get('fosas', [])
    for i, f in enumerate(fosas[:30]):
        fila = 10 + i
        ws[f'A{fila}'].value = f['descripcion']
        ws[f'B{fila}'].value = _num(f.get('capacidad'), 0)
        _poner(ws, f'C{fila}', _num(f.get('peso'), 1))
        valor = f.get('real') if f.get('real') is not None else f.get('calculado')
        _poner(ws, f'D{fila}', _num(valor, 1))
        _poner(ws, f'F{fila}', f.get('tipo_descripcion'))

    grupos = {g['grupo']: g for g in vol.get('grupos', [])}
    ws['H10'].value = 'bbl'
    for fila, clave in ((11, 'ACTIVO'), (12, 'RESERVA'), (13, 'PREMEZCLA')):
        g = grupos.get(clave)
        if g:
            real = g['real'] if g['real'] is not None else g['calculado']
            if clave == 'ACTIVO':   # suma de fosas: sin el hoyo
                real = sum((_f(f.get('real')) or 0.0) for f in fosas if f.get('grupo') == 'ACTIVO')
            ws[f'H{fila}'].value = _num(real, 1)
    for i, o in enumerate(vol.get('otras_por_tipo', [])[:14]):
        ws[f'G{15 + i}'].value = o['tipo']
        ws[f'H{15 + i}'].value = _num(o['volumen'], 1)

    hoyo = vol.get('hoyo') or {}
    vtot, vnf = hoyo.get('volumen') or {}, hoyo.get('no_fluido') or {}
    for col, k in (('B', 'anular'), ('C', 'sarta'), ('E', 'bajo_mecha')):
        ws[f'{col}43'].value = _num(vtot.get(k), 1)
        ws[f'{col}44'].value = _num(vnf.get(k), 1)
        ws[f'{col}45'].value = _num((_f(vtot.get(k)) or 0) - (_f(vnf.get(k)) or 0), 1)
    ws['G43'].value = _num(hoyo.get('total_volumen'), 1)
    ws['G44'].value = _num(hoyo.get('total_no_fluido'), 1)
    ws['G45'].value = _num(hoyo.get('total_fluido'), 1)

    cols = {'ACTIVO': 'C', 'RESERVA': 'D', 'PREMEZCLA': 'E'}
    tot = {}
    for clave, col in cols.items():
        g = grupos.get(clave)
        if not g:
            continue
        fl = g['flujos']
        v = lambda k: _f(fl.get(k)) or 0.0
        construido = v('aceite') + v('agua') + v('quimicos')
        filas = {50: g['inicio'], 51: v('aceite'), 52: v('agua'), 53: v('quimicos'), 54: 0.0,
                 55: construido, 56: v('recibido'), 57: v('devuelto'), 61: v('perdida'), 62: g['calculado']}
        for fila, valor in filas.items():
            ws[f'{col}{fila}'].value = _num(valor, 1)
            tot[fila] = tot.get(fila, 0.0) + (_f(valor) or 0.0)
    # Transferencias entre grupos: fila = grupo de origen, columna = grupo destino
    for fila, origen in ((58, 'ACTIVO'), (59, 'RESERVA'), (60, 'PREMEZCLA')):
        g = grupos.get(origen)
        if not g:
            continue
        suma = 0.0
        for destino, col in cols.items():
            if destino == origen:
                continue
            valor = _f(g['flujos'].get('hacia_' + destino)) or 0.0
            ws[f'{col}{fila}'].value = _num(valor, 1)
            suma += valor
        ws[f'F{fila}'].value = _num(suma, 1)
    for fila, valor in tot.items():
        ws[f'F{fila}'].value = _num(valor, 1)

    perdidas = vol.get('perdidas', [])
    for i, p in enumerate(perdidas[:14]):
        ws[f'G{48 + i}'].value = p['descripcion']
        ws[f'H{48 + i}'].value = _num(p['subtotal'], 1)
    ws['H62'].value = _num((vol.get('perdidas_totales') or {}).get('total'), 1)


# ---------------------------------------------------------------- inventario químico

def _hoja_inventario(ws, d, productos):
    pozo, rep, h = d['pozo'], d['reporte'], d['header']
    tasa = _f(getattr(pozo, 'tasa_impuesto', 0)) or 0.0
    costo_dia = round(sum(_f(p.get('costo_diario')) or 0.0 for p in productos), 2)
    costo_acum = round(sum(_f(p.get('costo_acumulado')) or 0.0 for p in productos), 2)
    paginas = max(1, min(3, (len(productos) + 49) // 50))
    for pag in range(paginas):
        base = pag * 60
        _poner(ws, f'C{3 + base}', h.operador if h else '')
        _fecha(ws, f'J{3 + base}', rep.fecha)
        ws[f'C{4 + base}'].value = pozo.nombre
        ws[f'J{4 + base}'].value = rep.numero_reporte
        _poner(ws, f'C{5 + base}', h.ubicacion if h else '')
        ws[f'J{5 + base}'].value = pag + 1
        ws[f'F{7 + base}'].value = costo_dia
        ws[f'K{7 + base}'].value = round(costo_dia * tasa / 100.0, 2) if tasa else None
        ws[f'F{8 + base}'].value = costo_acum
        for i, fila in enumerate(FILAS_INV[pag]):
            k = pag * 50 + i
            if k >= len(productos):
                break
            p = productos[k]
            ws[f'A{fila}'].value = p['descripcion']
            ws[f'C{fila}'].value = _texto_tamano(p)
            ws[f'D{fila}'].value = _num(p.get('precio'), 2)
            servicio = p.get('servicio')
            valores = {
                'E': None if servicio else p.get('inicial'), 'F': p.get('usado_dia'), 'G': p.get('usado_acum'),
                'H': p.get('recibido'), 'I': p.get('recibido_acum'), 'J': p.get('devuelto'),
                'K': p.get('devuelto_acum'), 'L': None if servicio else p.get('final'), 'M': p.get('costo_diario'),
            }
            for col, v in valores.items():
                v = _f(v)
                if v:
                    ws[f'{col}{fila}'].value = round(v, 2)
    ws.print_area = f'A1:M{paginas * 60}'


def _listas_inventario(d):
    inv = d['vol'].get('inventario', [])
    con_movimiento = lambda p: any((_f(p.get(k)) or 0) for k in ('inicial', 'final', 'recibido', 'devuelto',
                                                                    'usado_dia', 'usado_acum', 'recibido_acum'))
    completo = sorted([p for p in inv if con_movimiento(p) or p.get('activo')], key=lambda p: (p.get('codigo') or ''))
    df = [p for p in completo if not p.get('no_imprimir') and con_movimiento(p)]
    por_nombre = sorted(df, key=lambda p: (p.get('descripcion') or '').upper())
    return df, por_nombre, completo


# ---------------------------------------------------------------- equipos y mallas

def _hoja_equipos(ws, d):
    _encabezado_corto(ws, d, {'operador': 'B3', 'pozo': 'F3', 'fecha': 'J3', 'rep1': 'B4', 'campo': 'F4',
                              'spud': 'J4', 'contratista': 'B5', 'ubicacion': 'F5', 'lodo': 'J5',
                              'rep2': 'B6', 'actividad': 'J6'})
    ws['J9'].value = f"Costo ({d['pozo'].moneda_simbolo or 'USD'})"
    grupos = {0: 0.0, 1: 0.0, 3: 0.0}
    filas = [e for e in d['equipos'].get('equipos', []) if e.get('activo') or e.get('guardado')]
    for i, e in enumerate(filas[:36]):
        fila = 10 + i
        dat = e['datos']
        tarifas = e.get('tarifas_pozo') or {}
        cobro = dat.get('codigo_cobro')
        ws[f'A{fila}'].value = f"{e['descripcion']} ({e['serie']})"
        _poner(ws, f'E{fila}', _num(tarifas.get('COMPLETO'), 2))
        _poner(ws, f'F{fila}', _num(tarifas.get('STANDBY'), 2))
        ws[f'G{fila}'].value = {'COMPLETO': 'C', 'STANDBY': 'S'}.get(cobro, '-')
        usado = _f(dat.get('cantidad_usada')) if e.get('guardado') else 0.0
        ws[f'H{fila}'].value = usado or 0
        codigo = 0 if dat.get('es_fluidos') else 1
        ws[f'I{fila}'].value = codigo
        costo = (usado or 0) * (_f(e.get('tarifa')) or 0) if e.get('guardado') and cobro != 'SIN_COBRO' else 0.0
        ws[f'J{fila}'].value = round(costo, 2)
        grupos[codigo] = grupos.get(codigo, 0.0) + costo
    ws['E47'].value = round(grupos[0], 2)
    ws['E48'].value = round(grupos[1], 2)
    ws['E49'].value = round(grupos[3], 2)
    ws['E50'].value = round(sum(grupos.values()), 2)


def _hoja_mallas(ws, d):
    _encabezado_corto(ws, d, {'operador': 'B3', 'pozo': 'H3', 'fecha': 'M3', 'rep1': 'B4', 'campo': 'H4',
                              'spud': 'M4', 'contratista': 'B5', 'ubicacion': 'H5', 'lodo': 'M5',
                              'rep2': 'B6', 'actividad': 'M6'})
    usadas_pozo = d.get('mallas_usadas_pozo', {})
    inv = [m for m in d['mallas'].get('inventario', [])
           if m.get('activa') or m.get('nuevas_inicial') or m.get('usadas_inicial') or m.get('nuevas_final')
           or m.get('usadas_final') or m.get('costo_acumulado')]
    tot = {c: 0.0 for c in 'DEFGHIJKMN'}
    for i, m in enumerate(inv[:39]):
        fila = 10 + i
        ws[f'A{fila}'].value = m['descripcion'] or m['codigo']
        ws[f'C{fila}'].value = m['mesh_size']
        valores = {'D': m['nuevas_inicial'], 'E': m['usadas_inicial'], 'F': m['nuevas_recibidas'],
                   'G': m['nuevas_devueltas'], 'H': m['nuevas_instaladas'], 'I': m['usadas_salidas'],
                   'J': m['nuevas_final'], 'K': m['usadas_final'], 'M': m['costo_diario'],
                   'N': usadas_pozo.get(m['malla_id'], 0)}
        for col, v in valores.items():
            ws[f'{col}{fila}'].value = v
            tot[col] += _f(v) or 0.0
        _poner(ws, f'L{fila}', _num(m.get('precio_neto'), 2))
    for col, v in tot.items():
        ws[f'{col}49'].value = round(v, 2)
    ws['B51'].value = (d['mallas'].get('totales') or {}).get('costo_diario')
    ws['B52'].value = (d['mallas'].get('totales') or {}).get('costo_acumulado')


# ---------------------------------------------------------------- libro completo

def generar_reporte_excel(pozo, reporte):
    """Devuelve (bytes del .xlsx, nombre de archivo)."""
    d = _datos(pozo, reporte)
    variante = reporte.tipo_lodo if reporte.tipo_lodo in HOJA_LODO else 'WBM'
    wb = openpyxl.load_workbook(PLANTILLA)

    hoja_lodo, hoja_extra = HOJA_LODO[variante], HOJA_EXTRA[variante]
    for nombre in list(HOJA_LODO.values()) + ['Prop Extra Base Agua', 'Prop Extra Aceite-Sint']:
        if nombre not in (hoja_lodo, hoja_extra) and nombre in wb.sheetnames:
            wb.remove(wb[nombre])

    _hoja_lodo(wb[hoja_lodo], d, variante)
    _hoja_extra(wb[hoja_extra], d, variante)
    _hoja_volumen(wb['Contabilidad de Volumen'], d)
    df, por_nombre, completo = _listas_inventario(d)
    _hoja_inventario(wb['Inv Quimico (DF)'], d, df)
    _hoja_inventario(wb['Inv Quimico (por nombre)'], d, por_nombre)
    _hoja_inventario(wb['Inv Quimico (completo)'], d, completo)
    _hoja_equipos(wb['Equipos'], d)
    _hoja_mallas(wb['Inventario de Mallas'], d)

    if os.path.exists(LOGO):
        from openpyxl.drawing.image import Image
        for ws in wb.worksheets:
            img = Image(LOGO)
            escala = 40.0 / img.height if img.height else 1
            img.height, img.width = img.height * escala, img.width * escala
            ws.add_image(img, 'A1')

    wb.active = 0
    salida = io.BytesIO()
    wb.save(salida)
    nombre = f"Reporte_{reporte.numero_reporte}_{pozo.nombre}_{reporte.fecha.strftime('%Y%m%d')}.xlsx".replace(' ', '_')
    return salida.getvalue(), nombre
