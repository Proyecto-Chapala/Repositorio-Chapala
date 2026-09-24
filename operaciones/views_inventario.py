"""
API de la pestaña 8 del reporte diario — Inventario, Hidráulica y Concentraciones.

Por ahora: "Pérdidas del reporte" (ONE-TRAX: Daily Loss Print Selection), por pozo.
"""

import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Pozo, CategoriaPerdidaItem
from .models_inventario import PerdidaReportePozo


def _estado_perdidas(pozo):
    if not pozo.categorias_perdida.exists():
        CategoriaPerdidaItem.sembrar_estandar(pozo)
    categorias = list(pozo.categorias_perdida.all().order_by('codigo'))
    por_codigo = {c.codigo: c for c in categorias}

    guardadas = [p.codigo for p in pozo.perdidas_reporte.all() if p.codigo in por_codigo]
    personalizado = pozo.perdidas_reporte.exists()
    if not personalizado:
        guardadas = [c.codigo for c in categorias[:PerdidaReportePozo.MAXIMO_EN_REPORTE]]

    def dto(c):
        return {'codigo': c.codigo, 'descripcion': c.descripcion,
                'tipo': c.tipo, 'tipo_display': c.get_tipo_display()}

    return {
        'ok': True,
        'maximo': PerdidaReportePozo.MAXIMO_EN_REPORTE,
        'personalizado': personalizado,
        'disponibles': [dto(c) for c in categorias],
        'seleccionadas': guardadas,
        'enlace_configuracion': reverse('operaciones:loss_setup', args=[pozo.pk]),
    }


@require_http_methods(["GET"])
def api_perdidas_reporte_detail(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return JsonResponse(_estado_perdidas(pozo))


@csrf_exempt
@require_http_methods(["POST"])
def api_perdidas_reporte_guardar(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        body = json.loads(request.body)
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Datos inválidos.'}, status=400)

    existentes = set(pozo.categorias_perdida.values_list('codigo', flat=True))
    codigos = []
    for valor in body.get('codigos') or []:
        try:
            codigo = int(valor)
        except (TypeError, ValueError):
            return JsonResponse({'ok': False, 'error': 'Código de pérdida inválido.'}, status=400)
        if codigo not in existentes:
            return JsonResponse({'ok': False, 'error': f'La categoría {codigo} ya no existe en la configuración del pozo.'}, status=400)
        if codigo not in codigos:
            codigos.append(codigo)

    if not codigos:
        return JsonResponse({'ok': False, 'error': 'Elige al menos una categoría para el reporte.'}, status=400)
    if len(codigos) > PerdidaReportePozo.MAXIMO_EN_REPORTE:
        return JsonResponse({'ok': False, 'error': f'El reporte diario admite como máximo {PerdidaReportePozo.MAXIMO_EN_REPORTE} categorías.'}, status=400)

    with transaction.atomic():
        pozo.perdidas_reporte.all().delete()
        PerdidaReportePozo.objects.bulk_create([
            PerdidaReportePozo(pozo=pozo, codigo=c, orden=i) for i, c in enumerate(codigos)
        ])

    datos = _estado_perdidas(pozo)
    datos['mensaje'] = 'Pérdidas del reporte guardadas.'
    return JsonResponse(datos)


# =====================================================================
# Volumetría e inventario de productos (Volume Accounting and Product Inventory)
# =====================================================================

from decimal import Decimal

from django.db.models import Max
from django.db.models.deletion import RestrictedError, ProtectedError

from .models import Producto, TipoFosa
from .models_daily_reports import ReporteDiario
from .models_control_solidos import TipoTicketMalla, UsoEquipoDia
from .models_inventario import (
    VolumenFosaDia, VolumenHoyoDia, TransaccionVolumen, TransaccionVolumenProducto,
    InventarioProductoDia, TicketProducto, TicketProductoDetalle,
)
from . import volumetria as vol
from .volumetria import ErrorVolumetria, ACTIVO, RESERVA, PREMEZCLA, OTRAS, GRUPOS


class _Rechazo(Exception):
    """Validación con mensaje para el usuario; provoca el rollback."""


NOMBRE_GRUPO = {ACTIVO: 'Sistema activo', RESERVA: 'Reserva', PREMEZCLA: 'Premezcla', OTRAS: 'Otras fosas'}


def _obtener(pk, reporte_pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    reporte = get_object_or_404(ReporteDiario, pk=reporte_pk, pozo=pozo)
    return pozo, reporte


def _error(mensaje, status=400):
    return JsonResponse({'ok': False, 'error': mensaje}, status=status)


def _num(valor, etiqueta, minimo=None, maximo=None, permitir_vacio=True):
    if valor in (None, ''):
        if permitir_vacio:
            return None
        raise _Rechazo(f"{etiqueta}: falta el dato.")
    try:
        n = float(str(valor).replace(',', '.'))
    except (TypeError, ValueError):
        raise _Rechazo(f"{etiqueta}: '{valor}' no es un número válido.")
    if n != n:
        raise _Rechazo(f"{etiqueta}: no es un número válido.")
    if minimo is not None and n < minimo:
        raise _Rechazo(f"{etiqueta}: no puede ser menor que {minimo:g}.")
    if maximo is not None and n > maximo:
        raise _Rechazo(f"{etiqueta}: no puede ser mayor que {maximo:g}.")
    return n


def _dec(n, lugares=3):
    return Decimal(str(round(n or 0, lugares)))


def _leer(request):
    try:
        return json.loads(request.body)
    except (TypeError, ValueError):
        raise _Rechazo('Datos inválidos.')


# ---------- Productos del pozo ----------

def _productos_pozo(pozo):
    """Productos activos del pozo por id del catálogo maestro (primera fila de cada uno)."""
    datos = {}
    for a in pozo.productos_activos.select_related('producto').order_by('id'):
        if a.producto_id in datos:
            continue
        p = a.producto
        unidad = (a.unidad or '').strip()
        categoria = a.codigo_costo_diario if a.codigo_costo_diario in vol.CATEGORIAS_COSTO else 1
        datos[p.id] = {
            'producto_id': p.id,
            'codigo': p.codigo,
            'descripcion': p.descripcion,
            'unidad': unidad,
            'tamano': float(a.unit_size) if a.unit_size is not None else 0.0,
            'empaque': a.empaque,
            'precio': float(a.precio) if a.precio is not None else float(p.costo or 0),
            'gravedad': float(a.gravedad_especifica) if a.gravedad_especifica is not None else float(p.gravedad or 0),
            'concentracion': bool(a.calcular_concentracion),
            'categoria': categoria,
            'servicio': unidad == '',
            'activo': True,
        }
    return datos


def _completar_productos(datos, ids):
    """Agrega los productos usados en el pasado que ya no están activos en el pozo."""
    faltan = [i for i in ids if i not in datos]
    for p in Producto.objects.filter(id__in=faltan):
        datos[p.id] = {
            'producto_id': p.id, 'codigo': p.codigo, 'descripcion': p.descripcion,
            'unidad': '', 'tamano': 0.0, 'empaque': '', 'precio': float(p.costo or 0),
            'gravedad': float(p.gravedad or 0), 'concentracion': False, 'categoria': 1,
            'servicio': False, 'activo': False,
        }
    return datos


# ---------- Línea de tiempo del pozo ----------

def _hoyo_del_reporte(pozo, reporte):
    """Volumen del hoyo (pestaña 4) y el fluido del sistema activo que hay dentro."""
    from .views_daily_reports import calcular_geometria_reporte
    try:
        resultado, _, _ = calcular_geometria_reporte(pozo, reporte)
        t = resultado['totales']
        anular, sarta, bajo = t['volumen_anular_bbl'], t['volumen_sarta_bbl'], t['volumen_bajo_mecha_bbl']
    except Exception:
        anular = sarta = bajo = 0.0
    h = getattr(reporte, 'volumen_hoyo', None)
    nf = {
        'anular': float(h.no_fluido_anular) if h else 0.0,
        'sarta': float(h.no_fluido_sarta) if h else 0.0,
        'bajo_mecha': float(h.no_fluido_bajo_mecha) if h else 0.0,
    }
    volumen = {'anular': anular, 'sarta': sarta, 'bajo_mecha': bajo}
    fluido = {k: max(volumen[k] - nf[k], 0.0) for k in volumen}
    return {
        'volumen': volumen, 'no_fluido': nf, 'fluido': fluido,
        'total_volumen': sum(volumen.values()), 'total_no_fluido': sum(nf.values()),
        'total_fluido': sum(fluido.values()),
    }


def _tipos_fosa(pozo):
    if not pozo.tipos_fosa.exists():
        TipoFosa.sembrar_estandar(pozo)
    return {t.codigo: t.descripcion for t in pozo.tipos_fosa.all()}


def _fosas_del_dia(pozo, reporte, previas, tipos):
    """
    Fosas del reporte: las guardadas ese día o, si no hay, las del pozo con el tipo del día
    anterior (el tipo casi nunca cambia de un día a otro). previas: {numero: VolumenFosaDia}.
    """
    guardadas = {v.fosa_numero: v for v in reporte.volumenes_fosa.all()}
    filas = {}
    for f in pozo.fosas.all():
        g = guardadas.get(f.numero)
        base = g or previas.get(f.numero)
        tipo = base.tipo_codigo if base else None
        filas[f.numero] = {
            'numero': f.numero, 'descripcion': f.descripcion, 'capacidad': float(f.capacidad or 0),
            'tipo_codigo': tipo, 'tipo_descripcion': tipos.get(tipo, base.tipo_descripcion if base else ''),
            'real': float(g.volumen_final) if g and g.volumen_final is not None else None,
            'peso': float(g.peso_fluido) if g and g.peso_fluido is not None else None,
            'temperatura': float(g.temperatura) if g and g.temperatura is not None else None,
            'en_pozo': True,
        }
    # Fosas guardadas que ya no están en la lista del pozo: se conservan para no romper el histórico.
    for n, g in guardadas.items():
        if n not in filas:
            filas[n] = {
                'numero': n, 'descripcion': g.fosa_descripcion, 'capacidad': float(g.capacidad or 0),
                'tipo_codigo': g.tipo_codigo, 'tipo_descripcion': g.tipo_descripcion,
                'real': float(g.volumen_final) if g.volumen_final is not None else None,
                'peso': float(g.peso_fluido) if g.peso_fluido is not None else None,
                'temperatura': float(g.temperatura) if g.temperatura is not None else None,
                'en_pozo': False,
            }
    for f in filas.values():
        f['grupo'] = vol.grupo_de_tipo(f['tipo_codigo'])
    return [filas[n] for n in sorted(filas)], guardadas


def _dto_transaccion(t):
    return {
        'secuencia': t.secuencia, 'tipo': t.tipo, 'fosa': t.fosa_numero, 'destino': t.destino_numero,
        'volumen': float(t.volumen_bbl), 'aceite': float(t.aceite_bbl), 'agua': float(t.agua_bbl),
        'perdida': t.perdida_codigo, 'lodo_producto': t.lodo_producto_id,
        'lodo_cantidad': float(t.lodo_cantidad), 'lodo_precio': float(t.lodo_precio),
        'lodo_categoria': t.lodo_categoria,
        'productos': [
            {'producto': p.producto_id, 'cantidad': float(p.cantidad), 'es_concentracion': p.es_concentracion,
             'unidad': p.unidad, 'tamano': float(p.tamano), 'gravedad': float(p.gravedad),
             'precio': float(p.precio), 'categoria': p.categoria_costo,
             'concentracion': p.calcula_concentracion}
            for p in t.productos.all()
        ],
    }


def _linea_de_tiempo(pozo, objetivo):
    """Arma la entrada del motor para todos los reportes del pozo y datos de apoyo del objetivo."""
    tipos = _tipos_fosa(pozo)
    reportes = (
        pozo.reportes_diarios.order_by('fecha')
        .select_related('bit_data', 'intervalo_costo', 'volumen_hoyo')
        .prefetch_related('volumenes_fosa', 'transacciones_volumen__productos',
                          'tickets_producto__tipo', 'tickets_producto__detalles',
                          'inventario_productos')
    )
    dias = []
    previas = {}
    extra = {}
    ids_producto = set()
    for rep in reportes:
        fosas, guardadas = _fosas_del_dia(pozo, rep, previas, tipos)
        previas.update(guardadas)
        hoyo = _hoyo_del_reporte(pozo, rep)
        transacciones = [_dto_transaccion(t) for t in rep.transacciones_volumen.all()]
        tickets = [
            {'sentido': t.tipo.sentido,
             'detalles': [{'producto': d.producto_id, 'real': float(d.cantidad_real),
                           'ticket': float(d.cantidad_ticket)} for d in t.detalles.all()]}
            for t in rep.tickets_producto.all()
        ]
        manual = {
            m.producto_id: {'otro': float(m.usado_otro), 'ajuste': float(m.ajuste),
                            'precio': float(m.precio), 'categoria': m.categoria_costo}
            for m in rep.inventario_productos.all()
        }
        for t in transacciones:
            ids_producto.update(p['producto'] for p in t['productos'])
            if t['lodo_producto']:
                ids_producto.add(t['lodo_producto'])
        for t in tickets:
            ids_producto.update(d['producto'] for d in t['detalles'])
        ids_producto.update(manual)
        dias.append({
            'id': rep.id, 'fecha_texto': rep.fecha.strftime('%d/%m/%Y'),
            'fosas': [{'numero': f['numero'], 'grupo': f['grupo'], 'real': f['real']} for f in fosas],
            'hoyo_fluido': hoyo['total_fluido'],
            'transacciones': transacciones, 'tickets': tickets, 'manual': manual,
        })
        if rep.id == objetivo.id:
            extra = {'fosas': fosas, 'hoyo': hoyo}
            break
    return dias, extra, tipos, ids_producto


def _simular_pozo(pozo, reporte):
    """Estado de la volumetría al cierre del reporte. Lanza ErrorVolumetria si algo no cuadra."""
    dias, extra, tipos, ids = _linea_de_tiempo(pozo, reporte)
    productos = _completar_productos(_productos_pozo(pozo), ids)
    nombres_p = {i: f"{p['descripcion']} ({p['codigo']})" for i, p in productos.items()}
    nombres_f = {f['numero']: f['descripcion'] for f in extra.get('fosas', [])}
    servicios = {i for i, p in productos.items() if p['servicio']}
    sim = vol.simular(dias, reporte.id, nombres_p, nombres_f, servicios)
    return sim, extra, tipos, productos


def _validar(pozo, reporte):
    """Repite toda la línea de tiempo hasta el último reporte del pozo; rechaza si algún día falla."""
    ultimo = pozo.reportes_diarios.order_by('-fecha').first() or reporte
    try:
        dias, _, _, ids = _linea_de_tiempo(pozo, ultimo)
        productos = _completar_productos(_productos_pozo(pozo), ids)
        nombres_p = {i: f"{p['descripcion']} ({p['codigo']})" for i, p in productos.items()}
        servicios = {i for i, p in productos.items() if p['servicio']}
        vol.simular(dias, ultimo.id, nombres_p, {f.numero: f.descripcion for f in pozo.fosas.all()}, servicios)
    except ErrorVolumetria as e:
        raise _Rechazo(str(e))


# ---------- Datos de apoyo ----------

def _descarga_equipos(pozo, reporte):
    """Lodo perdido en los sólidos por tipo de pérdida, calculado en la pestaña 6."""
    from .views_control_solidos import _contexto_hoyo, _datos_uso
    from .control_solidos import calcular_rendimiento
    anterior = pozo.reportes_diarios.filter(fecha__lt=reporte.fecha).order_by('-fecha').first()
    vol_hoyo = _contexto_hoyo(reporte, anterior)['volumen_hoyo_bbl']
    por_codigo = {}
    for uso in reporte.usos_equipo.all():
        if uso.tipo_perdida_codigo is None:
            continue
        r = calcular_rendimiento(uso.tipo_equipo, _datos_uso(uso), vol_hoyo)
        if r['lodo_bbl']:
            por_codigo[uso.tipo_perdida_codigo] = por_codigo.get(uso.tipo_perdida_codigo, 0.0) + r['lodo_bbl']
    return por_codigo


def _texto_movimiento(t, fosas):
    nombre = lambda n, respaldo: fosas.get(n, respaldo) or f"Fosa {n}"
    origen = nombre(t.fosa_numero, t.fosa_descripcion)
    v = f"{float(t.volumen_bbl):g} bbl"
    if t.tipo == TransaccionVolumen.QUIMICOS:
        lineas = []
        if t.aceite_bbl:
            lineas.append(f"{float(t.aceite_bbl):g} bbl de fluido base")
        if t.agua_bbl:
            lineas.append(f"{float(t.agua_bbl):g} bbl de agua")
        lineas += [f"{float(p.cantidad):g} {p.descripcion}" for p in t.productos.all()]
        return f"Químicos agregados a {origen}", lineas
    if t.tipo == TransaccionVolumen.LODO_ENTERO:
        lineas = [f"{float(p.cantidad):g} lb/bbl {p.descripcion}" for p in t.productos.all()]
        desde = f" desde {t.origen_destino}" if t.origen_destino else ''
        peso = f" de {float(t.peso_lodo):g} lb/gal" if t.peso_lodo else ''
        return f"{v} de lodo entero{peso} ({t.lodo_producto_texto}) agregados a {origen}{desde}", lineas
    if t.tipo == TransaccionVolumen.TRANSFERENCIA:
        return f"Transferidos {v} de {origen} a {nombre(t.destino_numero, t.destino_descripcion)}", []
    if t.tipo == TransaccionVolumen.DEVOLUCION:
        return f"Devueltos {v} de {origen} a {t.origen_destino or 'destino sin indicar'}", []
    return f"Perdidos y descartados {v} de {origen} ({t.perdida_descripcion or 'sin tipo'})", []


def _redondear(d, n=2):
    return {k: (None if v is None else round(v, n)) for k, v in d.items()}


def _estado_volumetria(pozo, reporte):
    error = None
    try:
        sim, extra, tipos, productos = _simular_pozo(pozo, reporte)
    except ErrorVolumetria as e:
        error = str(e)
        dias, extra, tipos, ids = _linea_de_tiempo(pozo, reporte)
        productos = _completar_productos(_productos_pozo(pozo), ids)
        sim = None

    fosas = extra.get('fosas', [])
    hoyo = extra.get('hoyo') or _hoyo_del_reporte(pozo, reporte)
    nombres_fosa = {f['numero']: f['descripcion'] for f in fosas}

    filas_fosa = []
    for f in fosas:
        filas_fosa.append(dict(
            f,
            inicio=round(sim['inicio_fosa'].get(f['numero'], 0.0), 2) if sim else None,
            calculado=round(sim['calc_fosa'].get(f['numero'], 0.0), 2) if sim else None,
        ))

    grupos = []
    if sim:
        for g in GRUPOS:
            grupos.append({
                'grupo': g, 'nombre': NOMBRE_GRUPO[g],
                'inicio': round(sim['inicio_grupo'][g], 2),
                'calculado': round(sim['calc_grupo'][g], 2),
                'real': None if sim['real_grupo'][g] is None else round(sim['real_grupo'][g], 2),
                'no_contabilizado': None if sim['no_contabilizado'][g] is None else round(sim['no_contabilizado'][g], 2),
                'fosas_sin_real': [nombres_fosa.get(n, n) for n in sim['fosas_sin_real'][g]],
                'flujos': _redondear(sim['flujos'][g]),
                'tiene_fosas': any(f['grupo'] == g for f in fosas),
            })

    otras_por_tipo = {}
    for f in fosas:
        if f['grupo'] == OTRAS:
            v = f['real'] if f['real'] is not None else (sim['calc_fosa'].get(f['numero'], 0.0) if sim else 0.0)
            otras_por_tipo[f['tipo_descripcion'] or 'Sin tipo'] = otras_por_tipo.get(f['tipo_descripcion'] or 'Sin tipo', 0.0) + v

    # Pérdidas por categoría (las del reporte + cualquiera con movimiento)
    estado_p = _estado_perdidas(pozo)
    cats = {c['codigo']: c for c in estado_p['disponibles']}
    descarga = _descarga_equipos(pozo, reporte)
    codigos = list(estado_p['seleccionadas'])
    for c in list((sim or {}).get('perdidas', {}).keys()) + list(descarga.keys()):
        if c is not None and c not in codigos:
            codigos.append(c)
    perdidas = []
    tot = {'SUPERFICIE': 0.0, 'SUBSUELO': 0.0}
    for c in codigos:
        por_g = (sim or {}).get('perdidas', {}).get(c, {})
        sub = sum(por_g.values())
        cat = cats.get(c)
        tipo = cat['tipo'] if cat else 'SUPERFICIE'
        tot[tipo] = tot.get(tipo, 0.0) + sub
        perdidas.append({
            'codigo': c, 'descripcion': cat['descripcion'] if cat else f"Categoría {c}",
            'tipo': tipo, 'tipo_display': cat['tipo_display'] if cat else '',
            'por_grupo': _redondear({g: por_g.get(g, 0.0) for g in GRUPOS}),
            'subtotal': round(sub, 2), 'descargado': round(descarga.get(c, 0.0), 2),
        })

    # Inventario
    manual_hoy = {m.producto_id: m for m in reporte.inventario_productos.all()}
    ultimo_manual = {}
    for m in InventarioProductoDia.objects.filter(reporte__pozo=pozo, reporte__fecha__lt=reporte.fecha).order_by('reporte__fecha'):
        ultimo_manual[m.producto_id] = m
    inv_sim = (sim or {}).get('inventario', {})
    inventario = []
    ids_inv = [i for i, p in productos.items() if p['activo']] + [i for i in inv_sim if not productos.get(i, {}).get('activo')]
    peso_total = 0.0
    for pid in ids_inv:
        p = productos.get(pid)
        if not p:
            continue
        s = inv_sim.get(pid, {})
        m = manual_hoy.get(pid)
        base_ni = m or ultimo_manual.get(pid)
        peso = vol.masa_lb(s.get('final', 0.0), p['unidad'], p['tamano'])
        if peso:
            peso_total += peso
        inventario.append(dict(
            p,
            inicial=round(s.get('inicial', 0.0), 3), recibido=round(s.get('recibido', 0.0), 3),
            devuelto=round(s.get('devuelto', 0.0), 3),
            recibido_ticket=round(s.get('recibido_ticket', 0.0), 3),
            devuelto_ticket=round(s.get('devuelto_ticket', 0.0), 3),
            usado_fluido=round(s.get('usado_fluido', 0.0), 3),
            usado_otro=float(m.usado_otro) if m else 0.0,
            ajuste=float(m.ajuste) if m else 0.0,
            en_pedido=float(m.en_pedido) if m else 0.0,
            no_imprimir=bool(base_ni.no_imprimir) if base_ni else False,
            final=round(s.get('final', 0.0), 3), usado_dia=round(s.get('usado_dia', 0.0), 3),
            usado_acum=round(s.get('usado_acum', 0.0), 3), recibido_acum=round(s.get('recibido_acum', 0.0), 3),
            devuelto_acum=round(s.get('devuelto_acum', 0.0), 3),
            costo_diario=s.get('costo_diario', 0.0), costo_acumulado=s.get('costo_acumulado', 0.0),
            peso_lb=round(peso, 1) if peso is not None else None,
        ))

    costos = []
    if sim:
        for cat, nombre in vol.CATEGORIAS_COSTO.items():
            costos.append({'categoria': cat, 'nombre': nombre,
                           'diario': round(sim['costo_dia_cat'].get(cat, 0.0), 2),
                           'acumulado': round(sim['costo_acum_cat'].get(cat, 0.0), 2)})

    # Concentraciones
    concentraciones = []
    if sim:
        for clave, c in sim['concentraciones'].items():
            if clave == ACTIVO:
                etiqueta, orden = 'Sistema activo (fosas activas + hoyo)', (0, 0)
            else:
                etiqueta, orden = nombres_fosa.get(clave[1], f"Fosa {clave[1]}"), (1, clave[1])
            filas = []
            for pid in sorted(set(c['inicio']) | set(c['fin']), key=lambda i: productos.get(i, {}).get('descripcion', '')):
                ini, fin = c['inicio'].get(pid, 0.0), c['fin'].get(pid, 0.0)
                if abs(ini) < 1e-4 and abs(fin) < 1e-4:
                    continue
                p = productos.get(pid, {})
                filas.append({'producto_id': pid, 'descripcion': p.get('descripcion', pid), 'codigo': p.get('codigo', ''),
                              'inicio': round(ini, 3), 'fin': round(fin, 3)})
            if filas:
                concentraciones.append({'clave': 'ACTIVO' if clave == ACTIVO else f"F{clave[1]}", 'etiqueta': etiqueta,
                                        'orden': orden, 'vol_inicio': round(c['vol_inicio'], 2),
                                        'vol_fin': round(c['vol_fin'], 2), 'productos': filas})
        concentraciones.sort(key=lambda x: x['orden'])
        for c in concentraciones:
            c.pop('orden')

    movimientos = []
    for t in reporte.transacciones_volumen.prefetch_related('productos').order_by('secuencia'):
        titulo, lineas = _texto_movimiento(t, nombres_fosa)
        movimientos.append({'secuencia': t.secuencia, 'tipo': t.tipo, 'tipo_display': t.get_tipo_display(),
                            'titulo': titulo, 'lineas': lineas})
    ultima = (TransaccionVolumen.objects.filter(reporte__pozo=pozo)
              .select_related('reporte').order_by('-secuencia').first())

    tipos_ticket = list(pozo.tipos_ticket_malla.all())
    if not tipos_ticket:
        TipoTicketMalla.sembrar_ejemplos(pozo)
        tipos_ticket = list(pozo.tipos_ticket_malla.all())
    ultimos_tickets = []
    for tt in tipos_ticket:
        t = (TicketProducto.objects.filter(reporte__pozo=pozo, reporte__fecha__lte=reporte.fecha, tipo=tt)
             .exclude(numero='').order_by('-reporte__fecha', '-id').first())
        ultimos_tickets.append({'tipo': tt.nombre, 'numero': t.numero if t else ''})

    tickets = []
    for t in reporte.tickets_producto.select_related('tipo').prefetch_related('detalles'):
        det = [{'producto_id': d.producto_id, 'cantidad_ticket': float(d.cantidad_ticket),
                'cantidad_real': float(d.cantidad_real)} for d in t.detalles.all()]
        tickets.append({
            'id': t.id, 'tipo_id': t.tipo_id, 'tipo_nombre': t.tipo.nombre, 'sentido': t.tipo.sentido,
            'numero': t.numero, 'pedido_por': t.pedido_por, 'recibido_por': t.recibido_por,
            'almacen_codigo': t.almacen_codigo, 'almacen_nombre': t.almacen_nombre, 'detalles': det,
            'tiene_diferencias': any(abs(d['cantidad_ticket'] - d['cantidad_real']) > 1e-6 for d in det),
        })

    vol_quimicos = sum(g['flujos'].get('quimicos', 0.0) or 0.0 for g in grupos)

    return {
        'ok': True,
        'error_linea_tiempo': error,
        'fecha': reporte.fecha.strftime('%d/%m/%Y'),
        'moneda': pozo.moneda_simbolo or 'USD',
        'tipos_fosa': [{'codigo': c, 'descripcion': d} for c, d in sorted(tipos.items())],
        'fosas': filas_fosa,
        'hoyo': {k: (_redondear(v) if isinstance(v, dict) else round(v, 2)) for k, v in hoyo.items()},
        'hoyo_inicio': round(sim['hoyo_inicio'], 2) if sim else None,
        'grupos': grupos,
        'otras_por_tipo': [{'tipo': k, 'volumen': round(v, 2)} for k, v in otras_por_tipo.items()],
        'perdidas': perdidas,
        'perdidas_totales': {'superficie': round(tot.get('SUPERFICIE', 0.0), 2),
                             'subsuelo': round(tot.get('SUBSUELO', 0.0), 2),
                             'total': round(sum(tot.values()), 2)},
        'categorias_perdida': [{'codigo': c['codigo'], 'descripcion': c['descripcion']} for c in estado_p['disponibles']],
        'descarga_equipos': {str(k): round(v, 2) for k, v in descarga.items()},
        'inventario': inventario,
        'costos': costos,
        'peso_quimicos_lb': round(peso_total, 1),
        'volumen_quimicos_bbl': round(vol_quimicos, 2),
        'ultimos_tickets': ultimos_tickets,
        'concentraciones': concentraciones,
        'movimientos': movimientos,
        'ultima_transaccion': {'secuencia': ultima.secuencia, 'fecha': ultima.reporte.fecha.strftime('%d/%m/%Y'),
                               'es_de_este_reporte': ultima.reporte_id == reporte.id} if ultima else None,
        'tickets': tickets,
        'tipos_ticket': [t.to_dict() for t in tipos_ticket],
        'almacenes': [{'codigo': a.codigo, 'nombre': a.nombre} for a in pozo.almacenes.all()],
        'avisos': (sim or {}).get('avisos', []),
        'enlaces': {
            'fosas': reverse('operaciones:pits', args=[pozo.pk]),
            'productos': reverse('operaciones:active_items', args=[pozo.pk]),
        },
    }


def _respuesta(pozo, reporte, mensaje=None):
    datos = _estado_volumetria(pozo, reporte)
    if mensaje:
        datos['mensaje'] = mensaje
    return JsonResponse(datos)


@require_http_methods(["GET"])
def api_volumetria_detail(request, pk, reporte_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    return _respuesta(pozo, reporte)


@csrf_exempt
@require_http_methods(["POST"])
def api_volumetria_guardar(request, pk, reporte_pk):
    """Guarda lo que se mide o se escribe a mano: tipo y volumen real de fosas, hoyo e inventario."""
    pozo, reporte = _obtener(pk, reporte_pk)
    try:
        body = _leer(request)
        tipos = _tipos_fosa(pozo)
        fosas_pozo = {f.numero: f for f in pozo.fosas.all()}
        previas = {v.fosa_numero: v for v in reporte.volumenes_fosa.all()}
        productos = _productos_pozo(pozo)

        filas_fosa = []
        for item in body.get('fosas') or []:
            try:
                n = int(item.get('numero'))
            except (TypeError, ValueError):
                raise _Rechazo('Fosa inválida.')
            f = fosas_pozo.get(n)
            prev = previas.get(n)
            if f is None and prev is None:
                continue
            nombre = f.descripcion if f else prev.fosa_descripcion
            tipo = item.get('tipo_codigo')
            try:
                tipo = None if tipo in (None, '') else int(tipo)
            except (TypeError, ValueError):
                raise _Rechazo(f"{nombre}: tipo de fosa inválido.")
            if tipo is not None and tipo not in tipos:
                raise _Rechazo(f"{nombre}: el tipo de fosa no existe en la configuración del pozo.")
            real = _num(item.get('real'), f"{nombre} — volumen real", 0, 100000)
            capacidad = float(f.capacidad or 0) if f else float(prev.capacidad or 0)
            filas_fosa.append(VolumenFosaDia(
                reporte=reporte, fosa_numero=n, fosa_descripcion=nombre[:100], capacidad=_dec(capacidad, 2),
                tipo_codigo=tipo, tipo_descripcion=tipos.get(tipo, '')[:100],
                volumen_final=None if real is None else _dec(real, 2),
                peso_fluido=None if (x := _num(item.get('peso'), f"{nombre} — peso", 0, 30)) is None else _dec(x, 2),
                temperatura=None if (y := _num(item.get('temperatura'), f"{nombre} — temperatura", -50, 500)) is None else _dec(y, 1),
            ))

        h = body.get('hoyo') or {}
        no_fluido = {k: _num(h.get(k), f"Volumen no ocupado por fluido ({etq})", 0, 100000) or 0.0
                     for k, etq in (('anular', 'anular'), ('sarta', 'sarta'), ('bajo_mecha', 'bajo la mecha'))}

        filas_inv = []
        for item in body.get('inventario') or []:
            try:
                pid = int(item.get('producto_id'))
            except (TypeError, ValueError):
                raise _Rechazo('Producto inválido.')
            p = productos.get(pid)
            if p is None:
                continue
            etq = f"{p['descripcion']} ({p['codigo']})"
            otro = _num(item.get('usado_otro'), f"{etq} — usado en otro módulo", 0) or 0.0
            ajuste = _num(item.get('ajuste'), f"{etq} — ajuste") or 0.0
            pedido = _num(item.get('en_pedido'), f"{etq} — en pedido", 0) or 0.0
            no_imp = bool(item.get('no_imprimir'))
            if not (otro or ajuste or pedido or no_imp):
                continue
            filas_inv.append(InventarioProductoDia(
                reporte=reporte, producto_id=pid, usado_otro=_dec(otro), ajuste=_dec(ajuste),
                en_pedido=_dec(pedido), no_imprimir=no_imp, precio=_dec(p['precio'], 2),
                categoria_costo=p['categoria'],
            ))

        with transaction.atomic():
            enviados = [f.fosa_numero for f in filas_fosa]
            reporte.volumenes_fosa.filter(fosa_numero__in=enviados).delete()
            VolumenFosaDia.objects.bulk_create(filas_fosa)
            VolumenHoyoDia.objects.update_or_create(reporte=reporte, defaults={
                'no_fluido_anular': _dec(no_fluido['anular'], 2),
                'no_fluido_sarta': _dec(no_fluido['sarta'], 2),
                'no_fluido_bajo_mecha': _dec(no_fluido['bajo_mecha'], 2),
            })
            reporte.inventario_productos.all().delete()
            InventarioProductoDia.objects.bulk_create(filas_inv)
            _validar(pozo, reporte)
    except _Rechazo as e:
        return _error(str(e))
    return _respuesta(pozo, reporte, 'Volumetría guardada.')


def _fosa_valida(pozo, reporte, numero, etiqueta):
    try:
        n = int(numero)
    except (TypeError, ValueError):
        raise _Rechazo(f"Elige {etiqueta}.")
    f = pozo.fosas.filter(numero=n).first()
    if f is None:
        raise _Rechazo(f"{etiqueta.capitalize()} no existe en la lista de fosas del pozo.")
    return f


@csrf_exempt
@require_http_methods(["POST"])
def api_volumetria_transaccion(request, pk, reporte_pk):
    """Registra un movimiento: químicos, lodo entero, transferencia, devolución o pérdida."""
    pozo, reporte = _obtener(pk, reporte_pk)
    try:
        body = _leer(request)
        tipo = str(body.get('tipo') or '')
        if tipo not in dict(TransaccionVolumen.TIPO_CHOICES):
            raise _Rechazo('Tipo de movimiento no válido.')
        fosa = _fosa_valida(pozo, reporte, body.get('fosa'), 'la fosa')
        t = TransaccionVolumen(reporte=reporte, tipo=tipo, fosa_numero=fosa.numero,
                               fosa_descripcion=fosa.descripcion[:100])
        productos = _productos_pozo(pozo)
        lineas = []

        if tipo == TransaccionVolumen.QUIMICOS:
            aceite = _num(body.get('aceite'), 'Fluido base agregado', 0, 100000) or 0.0
            agua = _num(body.get('agua'), 'Agua agregada', 0, 100000) or 0.0
            t.aceite_bbl, t.agua_bbl = _dec(aceite, 2), _dec(agua, 2)
            for item in body.get('productos') or []:
                pid = int(item.get('producto_id') or 0)
                p = productos.get(pid)
                if p is None:
                    raise _Rechazo('Solo se pueden agregar productos activos del pozo.')
                cant = _num(item.get('cantidad'), f"{p['descripcion']} — cantidad", 0, 1e7) or 0.0
                if cant > 0:
                    lineas.append((p, cant))
            if not lineas and not aceite and not agua:
                raise _Rechazo('Escribe al menos una cantidad de producto, fluido base o agua.')

        elif tipo == TransaccionVolumen.LODO_ENTERO:
            v = _num(body.get('volumen'), 'Volumen de lodo', 0.01, 100000, permitir_vacio=False)
            t.volumen_bbl = _dec(v, 2)
            peso = _num(body.get('peso'), 'Peso del lodo', 0, 30)
            t.peso_lodo = None if peso is None else _dec(peso, 2)
            lp = productos.get(int(body.get('lodo_producto_id') or 0))
            if lp is None:
                raise _Rechazo('Elige el producto de lodo entero (de los productos activos del pozo).')
            t.lodo_producto_id = lp['producto_id']
            t.lodo_producto_texto = f"{lp['descripcion']}"[:255]
            t.lodo_cantidad = _dec(vol.consumo_lodo_entero(v, lp['unidad'], lp['tamano']))
            t.lodo_precio = _dec(lp['precio'], 2)
            t.lodo_categoria = lp['categoria']
            t.origen_destino = str(body.get('origen') or '').strip()[:120]
            for item in body.get('concentraciones') or []:
                pid = int(item.get('producto_id') or 0)
                p = productos.get(pid)
                if p is None:
                    continue
                c = _num(item.get('concentracion'), f"{p['descripcion']} — concentración", 0, 5000) or 0.0
                if c > 0:
                    lineas.append((p, c))

        elif tipo in (TransaccionVolumen.TRANSFERENCIA, TransaccionVolumen.DEVOLUCION, TransaccionVolumen.PERDIDA):
            v = _num(body.get('volumen'), 'Volumen', 0.01, 100000, permitir_vacio=False)
            t.volumen_bbl = _dec(v, 2)
            if tipo == TransaccionVolumen.TRANSFERENCIA:
                destino = _fosa_valida(pozo, reporte, body.get('destino'), 'la fosa destino')
                if destino.numero == fosa.numero:
                    raise _Rechazo('La fosa de origen y la de destino son la misma.')
                t.destino_numero, t.destino_descripcion = destino.numero, destino.descripcion[:100]
            elif tipo == TransaccionVolumen.DEVOLUCION:
                t.origen_destino = str(body.get('destino_texto') or '').strip()[:120]
                if not t.origen_destino:
                    raise _Rechazo('Indica a dónde se devuelve el fluido (almacén u otro taladro).')
            else:
                codigo = int(body.get('perdida_codigo') or 0)
                cat = pozo.categorias_perdida.filter(codigo=codigo).first()
                if cat is None:
                    raise _Rechazo('Elige el tipo de pérdida.')
                t.perdida_codigo, t.perdida_descripcion = cat.codigo, cat.descripcion[:100]

        with transaction.atomic():
            ultima = TransaccionVolumen.objects.filter(reporte__pozo=pozo).aggregate(m=Max('secuencia'))['m'] or 0
            t.secuencia = ultima + 1
            t.save()
            TransaccionVolumenProducto.objects.bulk_create([
                TransaccionVolumenProducto(
                    transaccion=t, producto_id=p['producto_id'], descripcion=p['descripcion'][:255],
                    cantidad=_dec(c), es_concentracion=(tipo == TransaccionVolumen.LODO_ENTERO),
                    unidad=p['unidad'][:30], tamano=_dec(p['tamano']), gravedad=_dec(p['gravedad'], 4),
                    precio=_dec(p['precio'], 2), categoria_costo=p['categoria'],
                    calcula_concentracion=p['concentracion'],
                ) for p, c in lineas
            ])
            _validar(pozo, reporte)
    except (TypeError, ValueError):
        return _error('Datos inválidos en el movimiento.')
    except _Rechazo as e:
        return _error(str(e))
    return _respuesta(pozo, reporte, 'Movimiento registrado.')


@csrf_exempt
@require_http_methods(["POST"])
def api_volumetria_deshacer(request, pk, reporte_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    ultima = (TransaccionVolumen.objects.filter(reporte__pozo=pozo)
              .select_related('reporte').order_by('-secuencia').first())
    if ultima is None:
        return _error('No hay movimientos para deshacer.')
    if ultima.reporte_id != reporte.id:
        return _error(f"El último movimiento del pozo (#{ultima.secuencia}) es del reporte del "
                      f"{ultima.reporte.fecha.strftime('%d/%m/%Y')}. Deshazlo desde ese reporte.")
    try:
        with transaction.atomic():
            ultima.delete()
            _validar(pozo, reporte)
    except _Rechazo as e:
        return _error(f"No se puede deshacer: {e}")
    return _respuesta(pozo, reporte, f"Movimiento #{ultima.secuencia} deshecho.")


@csrf_exempt
@require_http_methods(["POST"])
def api_ticket_producto_guardar(request, pk, reporte_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    try:
        body = _leer(request)
        tipo = pozo.tipos_ticket_malla.filter(pk=body.get('tipo_id') or 0).first()
        if tipo is None:
            raise _Rechazo('Elige el tipo de ticket.')
        codigo = str(body.get('almacen_codigo') or '').strip()
        nombre_alm = ''
        if codigo:
            alm = pozo.almacenes.filter(codigo=codigo).first()
            if alm is None:
                raise _Rechazo('El almacén elegido no existe en la configuración del pozo.')
            nombre_alm = alm.nombre
        productos = _productos_pozo(pozo)
        lineas = []
        vistos = set()
        for item in body.get('detalles') or []:
            pid = int(item.get('producto_id') or 0)
            if pid in vistos:
                raise _Rechazo('Hay un producto repetido en el ticket.')
            vistos.add(pid)
            p = productos.get(pid)
            etq = f"{p['descripcion']}" if p else f"producto {pid}"
            ct = _num(item.get('cantidad_ticket'), f"{etq} — según ticket", 0) or 0.0
            cr = _num(item.get('cantidad_real'), f"{etq} — real", 0) or 0.0
            if not (ct or cr):
                continue
            if p is None:
                raise _Rechazo('Solo se pueden usar productos activos del pozo.')
            lineas.append((pid, ct, cr))
        if not lineas:
            raise _Rechazo('El ticket no tiene cantidades. Escribe al menos una.')

        with transaction.atomic():
            tid = body.get('id')
            if tid:
                ticket = reporte.tickets_producto.filter(pk=tid).first()
                if ticket is None:
                    raise _Rechazo('El ticket no existe en este reporte.')
            else:
                ticket = TicketProducto(reporte=reporte)
            ticket.tipo = tipo
            ticket.numero = str(body.get('numero') or '').strip()[:40]
            ticket.pedido_por = str(body.get('pedido_por') or '').strip()[:100]
            ticket.recibido_por = str(body.get('recibido_por') or '').strip()[:100]
            ticket.almacen_codigo, ticket.almacen_nombre = codigo[:15], nombre_alm[:100]
            ticket.save()
            ticket.detalles.all().delete()
            TicketProductoDetalle.objects.bulk_create([
                TicketProductoDetalle(ticket=ticket, producto_id=pid, cantidad_ticket=_dec(ct), cantidad_real=_dec(cr))
                for pid, ct, cr in lineas
            ])
            _validar(pozo, reporte)
    except _Rechazo as e:
        return _error(str(e))
    datos = _estado_volumetria(pozo, reporte)
    datos['mensaje'] = 'Ticket guardado.'
    datos['ticket_id'] = ticket.id
    return JsonResponse(datos)


@csrf_exempt
@require_http_methods(["POST"])
def api_ticket_producto_eliminar(request, pk, reporte_pk, ticket_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    ticket = get_object_or_404(TicketProducto, pk=ticket_pk, reporte=reporte)
    try:
        with transaction.atomic():
            ticket.delete()
            _validar(pozo, reporte)
    except _Rechazo as e:
        return _error(f"No se puede eliminar el ticket: {e}")
    return _respuesta(pozo, reporte, 'Ticket eliminado.')


# =====================================================================
# Resumen de costos del reporte (pestaña 1 y "Resumen de Costos")
# =====================================================================

def resumen_costos(pozo, reporte):
    """
    Costos reales del día y acumulados, en las columnas del reporte de ONE-TRAX:
    Químicos/Personal DF (químicos + ingeniero de fluidos), Ingeniero IFE/Control de sólidos,
    Total perforación, Equipos/Mallas (pestaña 6) y Otros (DWM/CF, sin módulo todavía).
    """
    from .views_control_solidos import _simular as simular_mallas
    from .control_solidos import ErrorMallas

    diario = {'df_chem': 0.0, 'ife_sc': 0.0, 'df_equip': 0.0, 'other_cost': 0.0}
    acumulado = dict(diario)
    items = []

    try:
        sim, _, _, productos = _simular_pozo(pozo, reporte)
    except ErrorVolumetria:
        sim, productos = None, {}
    if sim:
        for cat in vol.CATEGORIAS_COSTO:
            clave = 'df_chem' if cat in (1, 2) else 'ife_sc'
            diario[clave] += sim['costo_dia_cat'].get(cat, 0.0)
            acumulado[clave] += sim['costo_acum_cat'].get(cat, 0.0)
        for pid, s in sim['inventario'].items():
            if s['costo_diario']:
                p = productos.get(pid, {})
                cat = p.get('categoria', 1)
                items.append({
                    'categoria': 'Químicos / Personal DF' if cat in (1, 2) else 'Ingeniero IFE / Control de sólidos',
                    'descripcion': p.get('descripcion', ''), 'cantidad': round(s['usado_dia'], 3),
                    'unidad': p.get('unidad') or 'servicio',
                    'costo_unitario': round(s['costo_diario'] / s['usado_dia'], 2) if s['usado_dia'] else 0.0,
                    'costo_total': round(s['costo_diario'], 2),
                })

    for uso in reporte.usos_equipo.all():
        c = uso.costo_diario
        diario['df_equip'] += c
        if c:
            items.append({'categoria': 'Equipos / Mallas', 'descripcion': f"Renta {uso.equipo_descripcion} ({uso.equipo_serie})",
                          'cantidad': float(uso.cantidad_usada), 'unidad': uso.get_codigo_cobro_display(),
                          'costo_unitario': float(uso.tarifa), 'costo_total': round(c, 2)})
    acumulado['df_equip'] += sum(u.costo_diario for u in UsoEquipoDia.objects.filter(
        reporte__pozo=pozo, reporte__fecha__lte=reporte.fecha))
    try:
        from .models import MallaZaranda
        mallas = simular_mallas(pozo, reporte)
        nombres_malla = {m.id: m.descripcion for m in MallaZaranda.objects.filter(id__in=list(mallas['movimientos']))}
        for malla_id, m in mallas['movimientos'].items():
            diario['df_equip'] += m['costo_diario']
            acumulado['df_equip'] += m['costo_acumulado']
            if m['costo_diario']:
                items.append({'categoria': 'Equipos / Mallas', 'descripcion': f"Mallas nuevas instaladas: {nombres_malla.get(malla_id, malla_id)}",
                              'cantidad': m['nuevas_instaladas'], 'unidad': 'mallas',
                              'costo_unitario': round(m['costo_diario'] / m['nuevas_instaladas'], 2) if m['nuevas_instaladas'] else 0.0,
                              'costo_total': round(m['costo_diario'], 2)})
    except ErrorMallas:
        pass

    for d in (diario, acumulado):
        d['drilling_total'] = d['df_chem'] + d['ife_sc']
        d['total'] = d['drilling_total'] + d['df_equip'] + d['other_cost']
        for k in d:
            d[k] = round(d[k], 2)
    return diario, acumulado, items
