"""
Motor de hidráulica (pestaña 8 — Hidráulica). Función pura, sin Django.

Dos métodos, como ONE-TRAX, elegibles en pantalla:

- API RP 13D 4ª edición — ley de potencia.
    Tubería:  n = 3.32·log(θ600/θ300),  K = 5.11·θ600 / 1022^n
    Anular:   n = 0.657·log(θ100/θ3),   K = 5.11·θ100 / 170.2^n
    Viscosidad efectiva, Reynolds y factor de fricción de Fanning (laminar 16/Re,
    turbulento a/Re^b con a = (log n + 3.93)/50, b = (1.75 − log n)/7, transición lineal).

- API RP 13D 5ª edición — Herschel-Bulkley.
    τy = 1.066·(2·θ3 − θ6);  n = 3.32·log((2PV + YP − τy)/(PV + YP − τy));
    k = 1.066·(PV + YP − τy)/511^n.
    Esfuerzo en la pared con factor geométrico (α = 0 tubería, α = 1 anular),
    Re = ρ·V² / (19.36·τw) y fricción combinada laminar / transición / turbulenta.
    Además informa la temperatura anular (gradiente del encabezado del pozo) y la PV/YP
    con que se calculó cada sección. La reología NO se corrige por temperatura ni presión:
    eso exige lecturas del viscosímetro a varias temperaturas, que el reporte no captura.

Unidades de campo: Q gal/min, D in, V ft/min, ρ lb/gal, L ft, ΔP psi.
    V = 24.48·Q / D²;  ΔP = 1.076e-5 · f · ρ · V² · L / D
Mecha (Cd = 0.95): ΔP = ρ·Q² / (10858·TFA²); HHP = ΔP·Q/1714; HSI = HHP/área de la mecha;
    velocidad de chorro = 0.3208·Q/TFA; fuerza de impacto = ρ·Q·Vj/1932.
    Verificado con el manual (pág. 130): 803 gpm, 11.5 lb/gal, TFA 0.69 → 1435 psi, 672 HHP,
    5.7 HSI, 373 ft/s.
"""

import math

C_PERDIDA = 1.076e-5
C_MECHA = 10858.0
EQUIV_SUPERFICIE_FT = {'1': 2600.0, '2': 946.0, '3': 610.0, '4': 424.0}   # de tubería de 3.826" ID
ID_EQUIV_SUPERFICIE = 3.826


def _log(x):
    return math.log10(x) if x and x > 0 else 0.0


# ---------------------------------------------------------------------------
# Reología
# ---------------------------------------------------------------------------

def lecturas_de(check):
    """Completa las lecturas del viscosímetro. Devuelve (lecturas, avisos)."""
    avisos = []
    pv, yp = check.get('pv'), check.get('yp')
    r = {k: check.get(k) for k in ('r600', 'r300', 'r200', 'r100', 'r6', 'r3')}
    if not r['r600'] and pv is not None and yp is not None:
        r['r600'] = 2 * pv + yp
    if not r['r300'] and pv is not None and yp is not None:
        r['r300'] = pv + yp
    if r['r600'] and r['r300']:
        pv = r['r600'] - r['r300'] if pv is None else pv
        yp = 2 * r['r300'] - r['r600'] if yp is None else yp
    return r, pv, yp, avisos


def reologia(check, edicion):
    """Parámetros del modelo para tubería y anular."""
    r, pv, yp, avisos = lecturas_de(check)
    if not r['r600'] or not r['r300'] or r['r600'] <= r['r300']:
        raise ValueError('Faltan las lecturas R600 y R300 (o PV y YP) del chequeo de lodo de la pestaña 3.')

    if edicion == '4':
        n_p = 3.32 * _log(r['r600'] / r['r300'])
        k_p = 5.11 * r['r600'] / 1022 ** n_p
        if r['r100'] and r['r3'] and r['r100'] > r['r3']:
            n_a = 0.657 * _log(r['r100'] / r['r3'])
            k_a = 5.11 * r['r100'] / 170.2 ** n_a
        else:
            n_a, k_a = n_p, k_p
            avisos.append('Sin lecturas R100 y R3: en el anular se usaron los parámetros de la tubería.')
        return {'edicion': '4', 'pv': pv, 'yp': yp, 'lecturas': r,
                'tuberia': {'n': n_p, 'k': k_p, 'ty': 0.0}, 'anular': {'n': n_a, 'k': k_a, 'ty': 0.0},
                'avisos': avisos}

    if r['r3'] is not None and r['r6'] is not None and r['r6'] >= r['r3']:
        ty = max(1.066 * (2 * r['r3'] - r['r6']), 0.0)
    else:
        ty = 0.0
        avisos.append('Sin lecturas R6 y R3: se tomó punto cedente verdadero (τy) igual a cero.')
    base = pv + yp
    ty = min(ty, 0.99 * base * 1.066)
    ty_dial = ty / 1.066
    n = 3.32 * _log((2 * pv + yp - ty_dial) / (pv + yp - ty_dial)) if pv + yp - ty_dial > 0 else 1.0
    k = 1.066 * (pv + yp - ty_dial) / 511 ** n
    par = {'n': n, 'k': k, 'ty': ty}
    return {'edicion': '5', 'pv': pv, 'yp': yp, 'lecturas': r,
            'tuberia': par, 'anular': dict(par), 'avisos': avisos}


# ---------------------------------------------------------------------------
# Fricción
# ---------------------------------------------------------------------------

def _f_turb(re, n):
    a = (_log(n) + 3.93) / 50.0
    b = (1.75 - _log(n)) / 7.0
    return a / re ** b


def _friccion_4(re, n):
    re_l, re_t = 3470 - 1370 * n, 4270 - 1370 * n
    if re <= 0:
        return 0.0, 'Sin flujo'
    if re < re_l:
        return 16.0 / re, 'Laminar'
    if re > re_t:
        return _f_turb(re, n), 'Turbulento'
    fl = 16.0 / re_l
    ft = _f_turb(re_t, n)
    return fl + (re - re_l) / 800.0 * (ft - fl), 'Transición'


def _friccion_5(re, n):
    if re <= 0:
        return 0.0, 'Sin flujo'
    re_l, re_t = 3470 - 1370 * n, 4270 - 1370 * n
    f_lam = 16.0 / re
    f_tr = 16.0 * re / re_l ** 2
    f_tu = _f_turb(re, n)
    f = (f_lam ** 12 + (f_tr ** -8 + f_tu ** -8) ** -1.5) ** (1.0 / 12.0)
    regimen = 'Laminar' if re < re_l else ('Turbulento' if re > re_t else 'Transición')
    return f, regimen


def _flujo(q, d_ext, d_int, rho, par, edicion, anular):
    """Velocidad, Reynolds, fricción y gradiente de pérdida (psi/ft) de un conducto."""
    if anular:
        area = d_ext ** 2 - d_int ** 2
        d_h = d_ext - d_int
    else:
        area = d_ext ** 2
        d_h = d_ext
    if area <= 0 or d_h <= 0 or q <= 0:
        return {'v': 0.0, 're': 0.0, 'f': 0.0, 'regimen': 'Sin flujo', 'grad': 0.0, 'dh': d_h}
    v = 24.48 * q / area
    n, k, ty = par['n'], par['k'], par['ty']

    if edicion == '4':
        if anular:
            mu = 100 * k * (144 * v / d_h) ** (n - 1) * ((2 * n + 1) / (3 * n)) ** n
        else:
            mu = 100 * k * (96 * v / d_h) ** (n - 1) * ((3 * n + 1) / (4 * n)) ** n
        re = 15.467 * v * d_h * rho / mu if mu > 0 else 0.0
        f, regimen = _friccion_4(re, n)
    else:
        alfa = 1.0 if anular else 0.0
        g = ((3 - alfa) * n + 1) / ((4 - alfa) * n) * (1 + alfa / 2)
        gamma_w = 1.6 * g * v / d_h
        tau_w = ((4 - alfa) / (3 - alfa)) ** n * ty + k * gamma_w ** n
        re = rho * v ** 2 / (19.36 * tau_w) if tau_w > 0 else 0.0
        f, regimen = _friccion_5(re, n)

    grad = C_PERDIDA * f * rho * v ** 2 / d_h
    return {'v': v, 're': re, 'f': f, 'regimen': regimen, 'grad': grad, 'dh': d_h}


def velocidad_critica(d_ext, d_int, rho, par, edicion):
    """Velocidad anular (ft/min) a la que el flujo deja de ser laminar."""
    n = par['n']
    re_l = 3470 - 1370 * n
    bajo, alto = 0.0, 20000.0
    area = d_ext ** 2 - d_int ** 2
    if area <= 0:
        return 0.0
    for _ in range(60):
        medio = (bajo + alto) / 2
        q = medio * area / 24.48
        r = _flujo(q, d_ext, d_int, rho, par, edicion, True)
        if r['re'] < re_l:
            bajo = medio
        else:
            alto = medio
    return (bajo + alto) / 2


# ---------------------------------------------------------------------------
# Cálculo completo
# ---------------------------------------------------------------------------

def calcular(secciones, q, rho, reo, tfa, bit_size, tvd_de, superficie=None, temp_de=None):
    """
    secciones: [{'desde_ft','hasta_ft','longitud_ft','diametro_hoyo_in','od_in','id_in',
                 'descripcion','es_bajo_mecha'}] de la pestaña 4 (de superficie hacia abajo).
    tvd_de(md) → TVD; temp_de(tvd) → °F o None.
    superficie: {'codigo', 'presion_ref', 'caudal_ref'}.
    """
    edicion = reo['edicion']
    filas = []
    ann_acum = 0.0
    total_ds = total_ann = 0.0
    for s in secciones:
        largo = s['longitud_ft']
        od, id_ = s.get('od_in') or 0.0, s.get('id_in') or 0.0
        dh = s['diametro_hoyo_in']
        if s.get('es_bajo_mecha') or not od:
            continue
        p = _flujo(q, id_, 0.0, rho, reo['tuberia'], edicion, False) if id_ > 0 else None
        a = _flujo(q, dh, od, rho, reo['anular'], edicion, True)
        dp_ds = p['grad'] * largo if p else 0.0
        dp_ann = a['grad'] * largo
        total_ds += dp_ds
        total_ann += dp_ann
        ann_acum += dp_ann
        tvd = tvd_de(s['hasta_ft'])
        ecd = rho + ann_acum / (0.052 * tvd) if tvd > 0 else rho
        tvd_medio = tvd_de((s['desde_ft'] + s['hasta_ft']) / 2)
        filas.append({
            'descripcion': s['descripcion'], 'longitud_ft': largo,
            'desde_ft': s['desde_ft'], 'hasta_ft': s['hasta_ft'],
            'diametro_hoyo_in': dh, 'od_in': od, 'id_in': id_,
            'vel_sarta': p['v'] if p else 0.0, 'regimen_sarta': p['regimen'] if p else '—',
            'vel_anular': a['v'], 'vel_critica': velocidad_critica(dh, od, rho, reo['anular'], edicion),
            'regimen_anular': a['regimen'],
            'perdida_sarta': dp_ds, 'perdida_anular': dp_ann, 'md_ft': s['hasta_ft'], 'tvd_ft': tvd,
            'ecd': ecd,
            'temp_anular': temp_de(tvd_medio) if temp_de else None,
        })

    # Equipo de superficie
    dp_sup, nota_sup = 0.0, ''
    sup = superficie or {}
    codigo = str(sup.get('codigo') or '').strip()
    if sup.get('presion_ref') and sup.get('caudal_ref'):
        dp_sup = sup['presion_ref'] * (q / sup['caudal_ref']) ** 1.86
        nota_sup = f"Escalada de {sup['presion_ref']:g} psi a {sup['caudal_ref']:g} gpm (pestaña 2)."
    elif codigo in EQUIV_SUPERFICIE_FT:
        r = _flujo(q, ID_EQUIV_SUPERFICIE, 0.0, rho, reo['tuberia'], edicion, False)
        dp_sup = r['grad'] * EQUIV_SUPERFICIE_FT[codigo]
        nota_sup = f"Caso de equipo de superficie {codigo}: {EQUIV_SUPERFICIE_FT[codigo]:g} ft equivalentes de tubería de 3.826\"."
    else:
        nota_sup = 'Sin datos de equipo de superficie (código 1-4 o presión de referencia en la pestaña 2).'

    # Mecha
    mecha = {'perdida': 0.0, 'hhp': 0.0, 'hsi': 0.0, 'vel_chorro': 0.0, 'fuerza_impacto': 0.0}
    if tfa > 0 and q > 0:
        dpb = rho * q ** 2 / (C_MECHA * tfa ** 2)
        vj = 0.3208 * q / tfa
        hhp = dpb * q / 1714.0
        area_mecha = math.pi / 4 * bit_size ** 2 if bit_size else 0.0
        mecha = {'perdida': dpb, 'hhp': hhp, 'hsi': hhp / area_mecha if area_mecha else 0.0,
                 'vel_chorro': vj, 'fuerza_impacto': rho * q * vj / 1932.0}

    total_sarta = total_ds + dp_sup
    total = total_sarta + total_ann + mecha['perdida']
    return {
        'edicion': edicion, 'secciones': filas,
        'perdida_superficie': dp_sup, 'nota_superficie': nota_sup,
        'perdida_sarta_secciones': total_ds, 'perdida_sarta': total_sarta,
        'perdida_anular': total_ann, 'mecha': mecha, 'perdida_total': total,
        'pct': {
            'sarta': total_sarta / total * 100 if total else 0.0,
            'anular': total_ann / total * 100 if total else 0.0,
            'mecha': mecha['perdida'] / total * 100 if total else 0.0,
        },
        'ecd_fondo': filas[-1]['ecd'] if filas else rho,
    }
