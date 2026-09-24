"""
API de la hidráulica del reporte diario (pestaña 8 — Hidráulica, API RP 13D 4ª y 5ª edición).

Solo consulta: toma los datos que ya existen en el reporte y no guarda nada.
- Caudal, boquillas (TFA), mecha y equipo de superficie: pestaña 2.
- Peso y reología (chequeo principal): pestaña 3.
- Secciones del pozo y de la sarta: pestaña 4 (motor geometria_pozo).
- TVD: estaciones del Well Survey (o la proporción TVD/MD del reporte).
- Temperatura anular (5ª edición): temperatura de superficie y gradiente del encabezado del pozo.
"""

import math

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Pozo
from .models_daily_reports import ReporteDiario
from . import hidraulica as hid

RPM_VISCOSIMETRO = (600, 300, 200, 100, 6, 3)


def _f(v):
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _chequeo_principal(reporte):
    checks = list(reporte.mud_checks.all().order_by('check_number'))
    con_datos = [c for c in checks if (c.r600 and c.r300) or (c.pv is not None and c.yp is not None)]
    if not con_datos:
        return None
    primario = next((c for c in con_datos if c.is_primary), None)
    return primario or con_datos[0]


def _funcion_tvd(pozo, reporte):
    estaciones = sorted(
        [(s.md_ft, s.tvd_ft) for s in pozo.survey_stations.all() if s.md_ft is not None and s.tvd_ft is not None],
        key=lambda x: x[0])
    if len(estaciones) >= 2:
        if estaciones[0][0] > 0:
            estaciones.insert(0, (0.0, 0.0))

        def tvd(md):
            if md <= estaciones[0][0]:
                return md
            for (m1, t1), (m2, t2) in zip(estaciones, estaciones[1:]):
                if m1 <= md <= m2:
                    return t1 + (t2 - t1) * (md - m1) / (m2 - m1) if m2 > m1 else t1
            m1, t1 = estaciones[-2]
            m2, t2 = estaciones[-1]
            pend = (t2 - t1) / (m2 - m1) if m2 > m1 else 1.0
            return t2 + (md - m2) * pend
        return tvd, 'estaciones del Well Survey'

    md, tv = _f(reporte.profundidad_actual) or 0.0, _f(reporte.profundidad_tvd) or 0.0
    if md > 0 and 0 < tv <= md:
        return (lambda x: x * tv / md), 'proporción TVD/MD del reporte (pestaña 1)'
    return (lambda x: x), 'pozo vertical (sin TVD en la pestaña 1)'


def _funcion_temperatura(pozo):
    info = getattr(pozo, 'well_header_info', None)
    if not info or info.surface_temp_f is None or info.temp_gradient_f_100ft is None:
        return None
    t0, grad = float(info.surface_temp_f), float(info.temp_gradient_f_100ft)
    return lambda tvd: t0 + grad * tvd / 100.0


def _curva(reo, par):
    """Reograma del modelo: lecturas del viscosímetro que predice el modelo a cada rpm."""
    puntos = []
    for rpm in (3, 6, 10, 30, 60, 100, 200, 300, 600, 1000):
        gamma = 1.703 * rpm
        if reo['edicion'] == '4':
            dial = par['k'] * gamma ** par['n'] / 5.11
        else:
            dial = (par['ty'] + par['k'] * gamma ** par['n']) / 1.066
        puntos.append({'rpm': rpm, 'lectura': round(dial, 2)})
    return puntos


def _r(v, n=2):
    return None if v is None else round(v, n)


@require_http_methods(["GET"])
def api_hidraulica_detail(request, pk, reporte_pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    reporte = get_object_or_404(ReporteDiario, pk=reporte_pk, pozo=pozo)
    edicion = '4' if request.GET.get('edicion') == '4' else '5'

    faltan = []
    bit = getattr(reporte, 'bit_data', None)
    q = sum(b.caudal_gpm for b in reporte.bombas.all())
    if q <= 0 and bit:
        q = _f(bit.pump_flow_rate) or 0.0
    if q <= 0:
        faltan.append('el caudal de las bombas (pestaña 2)')
    tfa = sum(b.area_sq_in for b in reporte.boquillas.all())
    if tfa <= 0:
        faltan.append('las boquillas de la mecha (pestaña 2)')
    bit_size = _f(bit.bit_size) if bit else 0.0

    check = _chequeo_principal(reporte)
    rho = _f(check.mud_weight) if check else None
    if not check:
        faltan.append('un chequeo de lodo con reología (pestaña 3)')
    elif not rho:
        faltan.append('el peso del lodo del chequeo principal (pestaña 3)')

    from .views_daily_reports import calcular_geometria_reporte
    try:
        geo, _, _ = calcular_geometria_reporte(pozo, reporte)
        secciones = geo['secciones']
    except Exception:
        secciones = []
    if not any((s.get('od_in') or 0) > 0 for s in secciones):
        faltan.append('la sarta de perforación (pestaña 4)')

    base = {
        'ok': True, 'edicion': edicion, 'faltan': faltan,
        'entrada': {
            'caudal_gpm': _r(q, 1), 'tfa_in2': _r(tfa, 4), 'bit_size_in': bit_size,
            'peso_lodo': rho, 'presion_bomba_real': _f(bit.pump_pressure) if bit else None,
            'chequeo': check.check_number if check else None,
            'temp_reologia': _f(check.rheology_temp) if check else None,
        },
    }
    if faltan:
        return JsonResponse(base)

    datos_check = {k: _f(getattr(check, k)) for k in ('pv', 'yp', 'r600', 'r300', 'r200', 'r100', 'r6', 'r3')}
    try:
        reo = hid.reologia(datos_check, edicion)
    except ValueError as e:
        base['faltan'] = [str(e)]
        return JsonResponse(base)

    tvd_de, fuente_tvd = _funcion_tvd(pozo, reporte)
    temp_de = _funcion_temperatura(pozo) if edicion == '5' else None
    superficie = {
        'codigo': bit.surface_code if bit else '',
        'presion_ref': _f(bit.surface_pressure) if bit else None,
        'caudal_ref': _f(bit.ref_flow_rate) if bit else None,
    }
    res = hid.calcular(secciones, q, rho, reo, tfa, bit_size, tvd_de, superficie, temp_de)

    real = base['entrada']['presion_bomba_real']
    base.update({
        'reologia': {
            'pv': _r(reo['pv'], 1), 'yp': _r(reo['yp'], 1),
            'lecturas': {k: v for k, v in reo['lecturas'].items()},
            'tuberia': {'n': _r(reo['tuberia']['n'], 3), 'k': _r(reo['tuberia']['k'], 3), 'ty': _r(reo['tuberia']['ty'], 2)},
            'anular': {'n': _r(reo['anular']['n'], 3), 'k': _r(reo['anular']['k'], 3), 'ty': _r(reo['anular']['ty'], 2)},
            'unidad_k': 'dina·s^n/cm²' if edicion == '4' else 'lbf·s^n/100 ft²',
            'curva': _curva(reo, reo['tuberia']),
            'puntos': [{'rpm': rpm, 'lectura': reo['lecturas'].get(f"r{rpm}")} for rpm in RPM_VISCOSIMETRO
                       if reo['lecturas'].get(f"r{rpm}")],
        },
        'avisos': reo['avisos'],
        'fuente_tvd': fuente_tvd,
        'temperatura_disponible': temp_de is not None,
        'secciones': [
            {
                'descripcion': s['descripcion'], 'longitud_ft': _r(s['longitud_ft'], 1),
                'diametro_hoyo_in': _r(s['diametro_hoyo_in'], 3), 'od_in': _r(s['od_in'], 3), 'id_in': _r(s['id_in'], 3),
                'vel_sarta': _r(s['vel_sarta'], 0), 'regimen_sarta': s['regimen_sarta'],
                'vel_anular': _r(s['vel_anular'], 0), 'vel_critica': _r(s['vel_critica'], 0),
                'regimen_anular': s['regimen_anular'],
                'perdida_sarta': _r(s['perdida_sarta'], 0), 'perdida_anular': _r(s['perdida_anular'], 0),
                'md_ft': _r(s['md_ft'], 0), 'tvd_ft': _r(s['tvd_ft'], 0), 'ecd': _r(s['ecd'], 2),
                'temp_anular': _r(s['temp_anular'], 0),
                'pv_anular': _r(reo['pv'], 0) if edicion == '5' else None,
                'yp_anular': _r(reo['yp'], 0) if edicion == '5' else None,
            }
            for s in res['secciones']
        ],
        'totales': {
            'sarta': _r(res['perdida_sarta'], 0), 'sarta_secciones': _r(res['perdida_sarta_secciones'], 0),
            'superficie': _r(res['perdida_superficie'], 0), 'nota_superficie': res['nota_superficie'],
            'anular': _r(res['perdida_anular'], 0), 'mecha': _r(res['mecha']['perdida'], 0),
            'total': _r(res['perdida_total'], 0),
            'diferencia_real': _r(real - res['perdida_total'], 0) if real else None,
            'pct': {k: _r(v, 1) for k, v in res['pct'].items()},
            'ecd_fondo': _r(res['ecd_fondo'], 2),
        },
        'mecha': {
            'perdida': _r(res['mecha']['perdida'], 0), 'hhp': _r(res['mecha']['hhp'], 0),
            'hsi': _r(res['mecha']['hsi'], 2), 'vel_chorro': _r(res['mecha']['vel_chorro'], 0),
            'fuerza_impacto': _r(res['mecha']['fuerza_impacto'], 0),
            'pct': _r(res['pct']['mecha'], 1),
        },
    })
    return JsonResponse(base)
