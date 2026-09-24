"""
API de los módulos OPCIONALES del reporte diario (ver models_opcionales.py).

Todos son independientes: ninguna otra pestaña lee estos datos, así que si no se usan
no cambian nada del reporte.
"""

import json
import re

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Pozo
from .models_daily_reports import ReporteDiario, ReporteDiarioMudCheck
from .models_opcionales import (
    ObservacionesIFE, AnalisisSolidosEquipo, RetencionRecortes, EventoNoProgramado,
)


class _Rechazo(Exception):
    pass


def _obtener(pk, reporte_pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return pozo, get_object_or_404(ReporteDiario, pk=reporte_pk, pozo=pozo)


def _leer(request):
    try:
        return json.loads(request.body)
    except (TypeError, ValueError):
        raise _Rechazo('Datos inválidos.')


def _num(valor, etiqueta, minimo=None, maximo=None):
    if valor in (None, ''):
        return None
    try:
        n = float(str(valor).replace(',', '.'))
    except (TypeError, ValueError):
        raise _Rechazo(f"{etiqueta}: '{valor}' no es un número válido.")
    if n != n or (minimo is not None and n < minimo) or (maximo is not None and n > maximo):
        raise _Rechazo(f"{etiqueta}: valor fuera de rango.")
    return n


def _texto(valor, largo):
    return str(valor or '').strip()[:largo]


def _hora(valor, etiqueta):
    v = _texto(valor, 5)
    if v and (len(v) != 5 or v[2] != ':' or not v.replace(':', '').isdigit()):
        raise _Rechazo(f"{etiqueta}: usa el formato HH:MM.")
    return v


def _error(e):
    return JsonResponse({'ok': False, 'error': str(e)}, status=400)


def _equipos(pozo):
    return [{'serie': e.numero_serie, 'descripcion': e.descripcion or e.equipo.nombre,
             'tipo': e.equipo.get_tipo_equipo_display()}
            for e in pozo.equipos_activos.select_related('equipo').all()]


def _equipo_valido(pozo, serie, previo=None):
    serie = _texto(serie, 30)
    for e in _equipos(pozo):
        if e['serie'] == serie:
            return serie, e['descripcion']
    if previo is not None and previo.equipo_serie == serie:
        return serie, previo.equipo_descripcion
    raise _Rechazo('Elige un equipo de la lista de equipos activos del pozo.')


def _muestra_comun(pozo, body, obj):
    obj.equipo_serie, obj.equipo_descripcion = _equipo_valido(pozo, body.get('equipo_serie'), obj if obj.pk else None)
    obj.equipo_descripcion = obj.equipo_descripcion[:150]
    obj.hora_inicio = _hora(body.get('hora_inicio'), 'Hora de inicio')
    obj.hora_fin = _hora(body.get('hora_fin'), 'Hora de fin')
    obj.orden = int(_num(body.get('orden'), 'Orden', 1, 99) or 1)
    obj.profundidad_ft = _num(body.get('profundidad_ft'), 'Profundidad medida', 0)
    obj.profundidad_perforada_ft = _num(body.get('profundidad_perforada_ft'), 'Profundidad perforada', 0)
    obj.comentarios = _texto(body.get('comentarios'), 255)


def _base_muestra(m):
    return {
        'id': m.id, 'equipo_serie': m.equipo_serie, 'equipo_descripcion': m.equipo_descripcion,
        'hora_inicio': m.hora_inicio, 'hora_fin': m.hora_fin, 'orden': m.orden,
        'profundidad_ft': m.profundidad_ft, 'profundidad_perforada_ft': m.profundidad_perforada_ft,
        'comentarios': m.comentarios,
    }


# =====================================================================
# Observaciones IFE
# =====================================================================

CAMPOS_IFE = ('fluidos_resumen', 'fluidos_plan', 'solidos_resumen', 'solidos_plan')


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_ife(request, pk, reporte_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    obj = getattr(reporte, 'observaciones_ife', None)
    if request.method == 'POST':
        try:
            body = _leer(request)
        except _Rechazo as e:
            return _error(e)
        if obj is None:
            obj = ObservacionesIFE(reporte=reporte)
        for c in CAMPOS_IFE:
            setattr(obj, c, str(body.get(c) or '').strip())
        obj.save()
    return JsonResponse({'ok': True, 'mensaje': 'Observaciones IFE guardadas.' if request.method == 'POST' else None,
                         **{c: getattr(obj, c) if obj else '' for c in CAMPOS_IFE}})


# =====================================================================
# Análisis de sólidos por equipo (reutiliza el cálculo de la pestaña 3)
# =====================================================================

ENTRADAS_WBM = ('mud_weight', 'water_pct', 'oil_pct', 'solids_pct', 'k_from_kcl', 'drill_solids_sg',
                'wt_additive_sg', 'oil_sg', 'frac_bent', 'chem_conc', 'mbt', 'chlorides')
ENTRADAS_OBM = ('mud_weight', 'water_pct', 'oil_pct', 'solids_pct', 'oil_sg', 'wt_additive_sg',
                'drill_solids_sg', 'chlorides')


def calcular_solidos(tipo, datos):
    """Corre el mismo balance de sólidos de la pestaña 3 sobre los datos de la muestra."""
    c = ReporteDiarioMudCheck()
    c.retort_mud_weight = None
    for campo in (ENTRADAS_OBM if tipo == 'OBM' else ENTRADAS_WBM):
        v = datos.get(campo)
        if v is not None:
            setattr(c, campo, v)
    avisos = []
    suma = sum(datos.get(k) or 0 for k in ('water_pct', 'oil_pct', 'solids_pct'))
    if suma and abs(suma - 100) > 0.5:
        avisos.append(f"Agua + aceite + sólidos suman {suma:g} %: deberían sumar 100 %.")
    if tipo == 'OBM':
        c.salt_pct_wt = None
        c.salt_ppb = None
        c.calcular_solids_analysis_obm(salt_type=datos.get('sal') or 'CaCl2')
        claves = ('salt_pct_wt', 'salt_ppb', 'adjusted_solids_pct', 'oil_water_ratio', 'lgs_pct', 'lgs_ppb',
                  'hgs_pct', 'hgs_ppb', 'avg_sg_solids')
    else:
        c.calcular_solids_analysis_wbm()
        c.hgs_ppb = round((c.hgs_pct or 0) * 3.5 * (c.wt_additive_sg or 4.2), 1)
        claves = ('nacl_pct', 'nacl_ppb', 'kcl_pct', 'kcl_ppb', 'lgs_pct', 'lgs_ppb', 'bentonite_pct',
                  'bentonite_ppb', 'drill_solids_pct', 'drill_solids_ppb', 'hgs_pct', 'hgs_ppb')
        lgs, hgs = c.lgs_pct or 0, c.hgs_pct or 0
        if lgs + hgs > 0:
            sg_prom = (lgs * (c.drill_solids_sg or 2.6) + hgs * (c.wt_additive_sg or 4.2)) / (lgs + hgs)
            avisos_res = {'avg_sg_solids': round(sg_prom, 2)}
        else:
            avisos_res = {'avg_sg_solids': None}
        bent, ds = c.bentonite_pct or 0, c.drill_solids_pct or 0
        res = {k: getattr(c, k) for k in claves}
        res.update(avisos_res)
        res['inerte_reactivo'] = round(ds / bent, 2) if bent > 0 else None
        return res, avisos
    return {k: getattr(c, k) for k in claves}, avisos


def _dto_solidos(m):
    res, avisos = calcular_solidos(m.tipo_lodo, m.datos or {})
    return dict(_base_muestra(m), tipo_lodo=m.tipo_lodo, tipo_muestra=m.tipo_muestra,
                datos=m.datos or {}, resultados=res, avisos=avisos)


# =====================================================================
# Retención en recortes
# =====================================================================

ENTRADAS_RET = ('peso_lodo', 'pct_fluido_base', 'sg_fluido_base', 'sg_solidos', 'celda_vacia',
                'celda_humedo', 'celda_seco', 'probeta_vacia', 'agua_cc', 'probeta_total')


def calcular_retencion(d):
    """
    Verificado con el manual (pág. 114): húmedo = celda + húmedo − celda; seco = celda + seco −
    celda; fluido base = probeta llena − probeta − agua; factor de balance =
    (seco + agua + fluido base) / húmedo; g/kg y % en peso sobre recorte húmedo y seco.
    Lodo en recortes (bbl de lodo por bbl de recortes) = volumen de lodo que corresponde al
    fluido base recuperado ÷ volumen de los recortes secos. Esta última es una reconstrucción:
    en el ejemplo del manual da ~1.5 % más que ONE-TRAX.
    """
    g = lambda k: d.get(k)
    r = {k: None for k in ('humedo_g', 'seco_g', 'fluido_base_g', 'factor_balance', 'gkg_humedo',
                            'gkg_seco', 'pct_humedo', 'pct_seco', 'lodo_en_recortes')}
    if g('celda_humedo') is not None and g('celda_vacia') is not None:
        r['humedo_g'] = g('celda_humedo') - g('celda_vacia')
    if g('celda_seco') is not None and g('celda_vacia') is not None:
        r['seco_g'] = g('celda_seco') - g('celda_vacia')
    if None not in (g('probeta_total'), g('probeta_vacia'), g('agua_cc')):
        r['fluido_base_g'] = g('probeta_total') - g('probeta_vacia') - g('agua_cc')
    h, s, fb = r['humedo_g'], r['seco_g'], r['fluido_base_g']
    if h and s is not None and fb is not None:
        r['factor_balance'] = (s + (g('agua_cc') or 0) + fb) / h
    if fb is not None:
        if h:
            r['gkg_humedo'] = fb / h * 1000
            r['pct_humedo'] = fb / h * 100
        if s:
            r['gkg_seco'] = fb / s * 1000
            r['pct_seco'] = fb / s * 100
    if fb and s and g('sg_fluido_base') and g('pct_fluido_base') and g('sg_solidos'):
        vol_lodo = fb / g('sg_fluido_base') / (g('pct_fluido_base') / 100.0)
        vol_recortes = s / g('sg_solidos')
        r['lodo_en_recortes'] = vol_lodo / vol_recortes if vol_recortes else None
    avisos = []
    if r['factor_balance'] is not None and abs(r['factor_balance'] - 1) > 0.05:
        avisos.append(f"El factor de balance es {r['factor_balance']:.3f}: fuera de 0,95-1,05 la prueba no cierra.")
    return {k: (None if v is None else round(v, 3)) for k, v in r.items()}, avisos


def _dto_retencion(m):
    res, avisos = calcular_retencion(m.datos or {})
    return dict(_base_muestra(m), diametro_mecha_in=m.diametro_mecha_in, datos=m.datos or {},
                resultados=res, avisos=avisos)


# ---------- CRUD genérico de muestras ----------

CONFIG_MUESTRAS = {
    'solidos': (AnalisisSolidosEquipo, 'analisis_solidos_equipo', _dto_solidos),
    'retencion': (RetencionRecortes, 'retencion_recortes', _dto_retencion),
}


def _lista(pozo, reporte, clave):
    modelo, rel, dto = CONFIG_MUESTRAS[clave]
    return JsonResponse({'ok': True, 'equipos': _equipos(pozo),
                         'muestras': [dto(m) for m in getattr(reporte, rel).all()]})


@require_http_methods(["GET"])
def api_muestras_detail(request, pk, reporte_pk, clave):
    if clave not in CONFIG_MUESTRAS:
        return _error('Módulo desconocido.')
    pozo, reporte = _obtener(pk, reporte_pk)
    return _lista(pozo, reporte, clave)


@csrf_exempt
@require_http_methods(["POST"])
def api_muestras_guardar(request, pk, reporte_pk, clave):
    if clave not in CONFIG_MUESTRAS:
        return _error('Módulo desconocido.')
    pozo, reporte = _obtener(pk, reporte_pk)
    modelo, rel, dto = CONFIG_MUESTRAS[clave]
    try:
        body = _leer(request)
        obj = getattr(reporte, rel).filter(pk=body.get('id')).first() if body.get('id') else modelo(reporte=reporte)
        if obj is None:
            raise _Rechazo('La muestra no existe en este reporte.')
        _muestra_comun(pozo, body, obj)
        entrada = body.get('datos') or {}
        if clave == 'solidos':
            obj.tipo_lodo = 'OBM' if body.get('tipo_lodo') == 'OBM' else 'WBM'
            obj.tipo_muestra = _texto(body.get('tipo_muestra'), 60)
            campos = ENTRADAS_OBM if obj.tipo_lodo == 'OBM' else ENTRADAS_WBM
            datos = {c: _num(entrada.get(c), c, 0) for c in campos}
            if obj.tipo_lodo == 'OBM':
                datos['sal'] = 'NaCl' if entrada.get('sal') == 'NaCl' else 'CaCl2'
        else:
            obj.diametro_mecha_in = _num(body.get('diametro_mecha_in'), 'Diámetro de mecha', 0, 60)
            datos = {c: _num(entrada.get(c), c, 0) for c in ENTRADAS_RET}
        obj.datos = {k: v for k, v in datos.items() if v is not None}
        obj.save()
    except _Rechazo as e:
        return _error(e)
    respuesta = json.loads(_lista(pozo, reporte, clave).content)
    respuesta.update({'mensaje': 'Muestra guardada.', 'id': obj.id})
    return JsonResponse(respuesta)


@csrf_exempt
@require_http_methods(["POST"])
def api_muestras_eliminar(request, pk, reporte_pk, clave, muestra_pk):
    if clave not in CONFIG_MUESTRAS:
        return _error('Módulo desconocido.')
    pozo, reporte = _obtener(pk, reporte_pk)
    modelo, rel, dto = CONFIG_MUESTRAS[clave]
    getattr(reporte, rel).filter(pk=muestra_pk).delete()
    respuesta = json.loads(_lista(pozo, reporte, clave).content)
    respuesta['mensaje'] = 'Muestra eliminada.'
    return JsonResponse(respuesta)


# =====================================================================
# Eventos no programados
# =====================================================================

def _dto_evento(e):
    return {'id': e.id, 'categoria': e.categoria, 'categoria_display': e.get_categoria_display(),
            'tipo_problema': e.tipo_problema, 'tipo_fluido': e.tipo_fluido, 'descripcion': e.descripcion,
            'causa': e.causa, 'descripcion_perdida': e.descripcion_perdida, 'horas_perdidas': e.horas_perdidas,
            'volumen_perdido_bbl': e.volumen_perdido_bbl, 'costo': e.costo,
            'fecha': e.reporte.fecha.strftime('%d/%m/%Y'), 'es_de_este_reporte': None}


def _estado_eventos(pozo, reporte):
    todos = EventoNoProgramado.objects.filter(reporte__pozo=pozo).select_related('reporte').order_by('reporte__fecha', 'id')
    eventos = []
    for e in todos:
        d = _dto_evento(e)
        d['es_de_este_reporte'] = e.reporte_id == reporte.id
        eventos.append(d)
    return {'ok': True, 'eventos': eventos,
            'categorias': [{'codigo': c, 'nombre': n} for c, n in EventoNoProgramado.CATEGORIA_CHOICES],
            'tipo_fluido_sugerido': reporte.tipo_fluido_display or reporte.get_tipo_lodo_display()}


@require_http_methods(["GET"])
def api_eventos_detail(request, pk, reporte_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    return JsonResponse(_estado_eventos(pozo, reporte))


@csrf_exempt
@require_http_methods(["POST"])
def api_eventos_guardar(request, pk, reporte_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    try:
        body = _leer(request)
        if body.get('id'):
            obj = reporte.eventos_no_programados.filter(pk=body['id']).first()
            if obj is None:
                raise _Rechazo('El evento no existe en este reporte (se edita desde el reporte en que se registró).')
        else:
            obj = EventoNoProgramado(reporte=reporte)
        obj.categoria = body.get('categoria') if body.get('categoria') in dict(EventoNoProgramado.CATEGORIA_CHOICES) else 'FLUIDOS'
        obj.tipo_problema = _texto(body.get('tipo_problema'), 100)
        if not obj.tipo_problema:
            raise _Rechazo('Escribe el tipo de problema (por ejemplo: pérdida de circulación, entrega tardía).')
        obj.tipo_fluido = _texto(body.get('tipo_fluido'), 100)
        obj.descripcion = str(body.get('descripcion') or '').strip()
        obj.causa = str(body.get('causa') or '').strip()
        obj.descripcion_perdida = str(body.get('descripcion_perdida') or '').strip()
        obj.horas_perdidas = _num(body.get('horas_perdidas'), 'Tiempo perdido', 0, 10000)
        obj.volumen_perdido_bbl = _num(body.get('volumen_perdido_bbl'), 'Volumen perdido', 0)
        obj.costo = _num(body.get('costo'), 'Costo', 0)
        obj.save()
    except _Rechazo as e:
        return _error(e)
    datos = _estado_eventos(pozo, reporte)
    datos.update({'mensaje': 'Evento guardado.', 'id': obj.id})
    return JsonResponse(datos)


@csrf_exempt
@require_http_methods(["POST"])
def api_eventos_eliminar(request, pk, reporte_pk, evento_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    reporte.eventos_no_programados.filter(pk=evento_pk).delete()
    datos = _estado_eventos(pozo, reporte)
    datos['mensaje'] = 'Evento eliminado.'
    return JsonResponse(datos)


# =====================================================================
# Evaluación de benchmark (objetivo vs real)
# =====================================================================

# Palabras clave de la descripción del parámetro → campo del chequeo de lodo (pestaña 3).
VINCULOS = [
    (('hthp', 'hpht'), 'hthp_fluid_loss'),
    (('api fluid', 'filtrado api', 'api fl', 'fluid loss', 'filtrado'), 'api_fluid_loss'),
    (('mud weight', 'peso del lodo', 'peso de lodo', 'densidad'), 'mud_weight'),
    (('funnel', 'embudo'), 'funnel_viscosity'),
    (('gel 10s', 'gel 10 s', '10 seg', '10s gel'), 'gel_10s'),
    (('gel 10m', 'gel 10 m', '10 min', '10m gel'), 'gel_10m'),
    (('pv', 'plastic', 'plástica', 'plastica'), 'pv'),
    (('yp', 'yield', 'cedente'), 'yp'),
    (('mbt',), 'mbt'),
    (('sand', 'arena'), 'sand_pct'),
    (('solids', 'sólidos', 'solidos'), 'solids_pct'),
    (('chloride', 'cloruro'), 'chlorides'),
    (('stability', 'estabilidad'), 'electrical_stability'),
    (('ph',), 'ph'),
]

LODOS = {'WBM': ('WBM', 'WBM_CACL2'), 'OBM': ('OBM', 'SBM')}


def _campo_de(descripcion):
    d = ' ' + (descripcion or '').lower().replace('(', ' ').replace(')', ' ') + ' '
    for claves, campo in VINCULOS:
        for c in claves:
            if (f" {c} " in d) if len(c) <= 3 else (c in d):
                return campo
    return None


def _f(v):
    try:
        return float(str(v).replace(',', '.'))
    except (TypeError, ValueError):
        return None


@require_http_methods(["GET"])
def api_benchmark_evaluacion(request, pk, reporte_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    from .views_daily_reports import obtener_intervalos_del_pozo
    intervalos = obtener_intervalos_del_pozo(pozo)
    columnas = [{'clave': 'POZO', 'etiqueta': 'Pozo completo', 'id': None}] + [
        {'clave': f"I{i['id']}", 'etiqueta': f"Intervalo {i['numero']}", 'id': i['id'], 'detalle': i['etiqueta']}
        for i in intervalos]

    reportes = list(pozo.reportes_diarios.filter(fecha__lte=reporte.fecha)
                    .prefetch_related('mud_checks').order_by('fecha'))
    profundidades = {}
    for c in columnas:
        reps = [r for r in reportes if c['id'] is None or r.intervalo_costo_id == c['id']]
        prof = [r.profundidad_actual for r in reps if r.profundidad_actual]
        c['reportes'] = len(reps)
        c['tope_ft'] = min(prof) if prof else None
        c['fondo_ft'] = max(prof) if prof else None
        profundidades[c['clave']] = reps

    targets = {}
    for t in pozo.benchmark_targets.select_related('parametro').all():
        clave = 'POZO' if t.intervalo_id is None else f"I{t.intervalo_id}"
        targets.setdefault(t.parametro_id, {}).setdefault(clave, {})[t.min_max] = t.valor

    filas = []
    for sel in pozo.benchmarks_seleccionados.select_related('parametro').all():
        p = sel.parametro
        campo = _campo_de(p.descripcion)
        tipos_lodo = LODOS.get(p.tipo_fluido)
        celdas = {}
        for c in columnas:
            obj = targets.get(p.id, {}).get(c['clave'], {})
            minimo, maximo = _f(obj.get('MIN')), _f(obj.get('MAX'))
            valor = obj.get('VALOR')
            if valor not in (None, '') and minimo is None and maximo is None:
                # Parámetros separados "... min" / "... max" (como en ONE-TRAX): el valor es un límite.
                texto = re.sub(r'\([^)]*\)', ' ', (p.descripcion or '').lower()).strip()
                if texto.endswith(' min') or texto.endswith('mínimo') or texto.endswith('minimo'):
                    minimo = _f(valor)
                elif texto.endswith(' max') or texto.endswith('máximo') or texto.endswith('maximo'):
                    maximo = _f(valor)
            valores = []
            if campo:
                for r in profundidades[c['clave']]:
                    if tipos_lodo and r.tipo_lodo not in tipos_lodo:
                        continue
                    for ch in r.mud_checks.all():
                        v = getattr(ch, campo, None)
                        if v is not None:
                            valores.append(float(v))
            dentro = None
            if valores and (minimo is not None or maximo is not None):
                ok = [v for v in valores if (minimo is None or v >= minimo) and (maximo is None or v <= maximo)]
                dentro = round(len(ok) / len(valores) * 100, 0)
            celdas[c['clave']] = {
                'minimo': minimo, 'maximo': maximo, 'valor': valor or None,
                'real_min': round(min(valores), 2) if valores else None,
                'real_max': round(max(valores), 2) if valores else None,
                'n': len(valores), 'pct_dentro': dentro,
            }
        filas.append({'id': p.id, 'grupo': p.grupo, 'descripcion': p.descripcion, 'unidad': p.unidad,
                      'tipo_fluido': p.get_tipo_fluido_display(), 'vinculado': campo is not None, 'celdas': celdas})

    for c in columnas:
        c.pop('id', None)
    return JsonResponse({'ok': True, 'columnas': columnas, 'filas': filas, 'fecha': reporte.fecha.strftime('%d/%m/%Y')})
