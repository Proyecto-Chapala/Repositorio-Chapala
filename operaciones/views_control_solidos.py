"""
API de la pestaña 6 del reporte diario — Control de Sólidos (fase 1: mallas de zaranda).

Todas las escrituras siguen el mismo patrón: dentro de una transacción de base de datos se
guarda el cambio y se repite TODA la línea de tiempo de mallas del pozo con el motor de
control_solidos.py. Si algún día (antes o después) queda sin stock o con una posición
imposible, se deshace el guardado y se devuelve el mensaje del motor.

Cada respuesta devuelve el resumen completo de la pestaña, para que la pantalla se vuelva a
dibujar con el estado real del servidor.
"""

import json
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Max, ProtectedError, RestrictedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Pozo, MallaZaranda
from .models_daily_reports import ReporteDiario
from .models_control_solidos import (
    TipoTicketMalla, TicketMalla, TicketMallaDetalle, TransaccionMalla,
)
from .control_solidos import simular, ErrorMallas


class _Rechazo(Exception):
    """Error de validación con mensaje para el usuario (provoca el rollback)."""


# =====================================================================
# Utilidades
# =====================================================================

def _precio_neto(malla_activa):
    """Precio con el descuento del pozo aplicado, redondeado a centavos."""
    precio = Decimal(malla_activa.precio or 0)
    descuento = Decimal(malla_activa.descuento_porcentaje or 0)
    neto = precio * (Decimal(100) - descuento) / Decimal(100)
    return neto.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _texto_malla(malla):
    return f"{malla.descripcion} (Mesh {malla.mesh_size})"


def _eventos_pozo(pozo):
    """Tickets y transacciones de todos los reportes del pozo, en el formato del motor."""
    reportes = (
        pozo.reportes_diarios.order_by('fecha')
        .prefetch_related('tickets_malla__tipo', 'tickets_malla__detalles', 'transacciones_malla')
    )
    eventos = []
    for rep in reportes:
        eventos.append({
            'id': rep.id,
            'fecha_texto': rep.fecha.strftime('%d/%m/%Y'),
            'tickets': [
                {
                    'sentido': t.tipo.sentido,
                    'detalles': [
                        {'malla_id': d.malla_id, 'nuevas': d.nuevas_real, 'usadas': d.usadas_real}
                        for d in t.detalles.all()
                    ],
                }
                for t in rep.tickets_malla.all()
            ],
            'transacciones': [
                {
                    'secuencia': tr.secuencia, 'accion': tr.accion, 'malla_id': tr.malla_id,
                    'serie': tr.equipo_serie, 'posicion': tr.posicion,
                    'precio': float(tr.precio_unitario),
                }
                for tr in rep.transacciones_malla.all()
            ],
        })
    return eventos


def _nombres_malla(pozo):
    ids = set(pozo.mallas_activas.values_list('malla_id', flat=True))
    ids |= set(TransaccionMalla.objects.filter(reporte__pozo=pozo).values_list('malla_id', flat=True))
    ids |= set(TicketMallaDetalle.objects.filter(ticket__reporte__pozo=pozo).values_list('malla_id', flat=True))
    return {m.id: _texto_malla(m) for m in MallaZaranda.objects.filter(id__in=ids)}


def _simular(pozo, reporte):
    """Estado al final del reporte. Lanza ErrorMallas si la línea de tiempo no cuadra."""
    return simular(_eventos_pozo(pozo), reporte.id, _nombres_malla(pozo))


def _validar_o_rechazar(pozo, reporte):
    try:
        return _simular(pozo, reporte)
    except ErrorMallas as e:
        raise _Rechazo(str(e))


def _tipos_ticket(pozo):
    if not pozo.tipos_ticket_malla.exists():
        TipoTicketMalla.sembrar_ejemplos(pozo)
    return list(pozo.tipos_ticket_malla.all())


def _equipos_con_mallas(pozo):
    """Equipos activos del pozo cuyo modelo lleva mallas, en orden de tipo y serie."""
    return [
        e for e in pozo.equipos_activos.select_related('equipo').all()
        if e.equipo.posiciones_malla > 0
    ]


def _leer_json(request):
    try:
        return json.loads(request.body)
    except (TypeError, ValueError):
        raise _Rechazo('Datos inválidos.')


def _entero(valor, etiqueta, minimo=0):
    if valor in (None, ''):
        if minimo > 0:
            raise _Rechazo(f"{etiqueta}: falta el dato.")
        return 0
    try:
        n = int(str(valor).strip())
    except (TypeError, ValueError):
        raise _Rechazo(f"{etiqueta}: '{valor}' no es un número entero.")
    if n < minimo:
        raise _Rechazo(f"{etiqueta}: no puede ser menor que {minimo}.")
    return n


# =====================================================================
# Resumen de la pestaña
# =====================================================================

def _resumen(pozo, reporte):
    error_linea_tiempo = None
    try:
        sim = _simular(pozo, reporte)
    except ErrorMallas as e:
        # No debería pasar (cada escritura valida), pero si hay datos viejos inconsistentes
        # se muestra el aviso en vez de romper la pantalla.
        error_linea_tiempo = str(e)
        sim = {'movimientos': {}, 'posiciones': {}, 'nuevas': {}, 'usadas': {}}

    activas = list(pozo.mallas_activas.select_related('malla').all())
    activas_por_malla = {a.malla_id: a for a in activas}
    movimientos = sim['movimientos']
    en_equipos = {}
    for malla_id in sim['posiciones'].values():
        en_equipos[malla_id] = en_equipos.get(malla_id, 0) + 1

    ids_inventario = set(activas_por_malla) | set(movimientos) | set(en_equipos)
    mallas = {m.id: m for m in MallaZaranda.objects.filter(id__in=ids_inventario)}

    inventario = []
    for malla_id in sorted(ids_inventario, key=lambda i: (mallas[i].mesh_size, mallas[i].codigo)):
        malla = mallas[malla_id]
        activa = activas_por_malla.get(malla_id)
        fila = {
            'malla_id': malla_id,
            'codigo': malla.codigo,
            'descripcion': malla.descripcion,
            'mesh_size': malla.mesh_size,
            'activa': activa is not None,
            'precio_bruto': float(activa.precio) if activa else None,
            'descuento_porcentaje': float(activa.descuento_porcentaje) if activa else None,
            'precio_neto': float(_precio_neto(activa)) if activa else None,
            'en_equipos': en_equipos.get(malla_id, 0),
        }
        mov = movimientos.get(malla_id)
        if mov is None:
            stock_n = sim['nuevas'].get(malla_id, 0)
            stock_u = sim['usadas'].get(malla_id, 0)
            mov = {
                'nuevas_inicial': stock_n, 'nuevas_recibidas': 0, 'nuevas_devueltas': 0,
                'nuevas_instaladas': 0, 'nuevas_final': stock_n,
                'usadas_inicial': stock_u, 'usadas_entradas': 0, 'usadas_salidas': 0,
                'usadas_final': stock_u, 'costo_diario': 0.0, 'costo_acumulado': 0.0,
            }
        fila.update(mov)
        inventario.append(fila)

    equipos = []
    for e in _equipos_con_mallas(pozo):
        total = min(e.equipo.posiciones_malla, e.equipo.POSICIONES_MALLA_MAX)
        posiciones = []
        for p in range(1, total + 1):
            malla_id = sim['posiciones'].get((e.numero_serie, p))
            malla = mallas.get(malla_id) if malla_id else None
            posiciones.append({
                'posicion': p,
                'malla_id': malla_id,
                'malla_codigo': malla.codigo if malla else None,
                'malla_texto': _texto_malla(malla) if malla else None,
                'mesh_size': malla.mesh_size if malla else None,
            })
        equipos.append({
            'serie': e.numero_serie,
            'descripcion': e.descripcion or e.equipo.nombre,
            'equipo_nombre': e.equipo.nombre,
            'tipo_display': e.equipo.get_tipo_equipo_display(),
            'posiciones_total': total,
            'posiciones_ocupadas': sum(1 for p in posiciones if p['malla_id']),
            'posiciones': posiciones,
        })
    # Mallas en posiciones que ya no caben (se bajó el número de posiciones del modelo).
    series_visibles = {(e['serie'], p['posicion']) for e in equipos for p in e['posiciones']}
    fuera_de_rango = [
        {'serie': s, 'posicion': p, 'malla_texto': _texto_malla(mallas[m]) if m in mallas else str(m)}
        for (s, p), m in sim['posiciones'].items() if (s, p) not in series_visibles
    ]

    mallas_disponibles = [
        {
            'malla_id': a.malla_id,
            'texto': _texto_malla(a.malla),
            'codigo': a.malla.codigo,
            'mesh_size': a.malla.mesh_size,
            'precio_neto': float(_precio_neto(a)),
            'stock_nuevas': sim['nuevas'].get(a.malla_id, 0),
            'stock_usadas': sim['usadas'].get(a.malla_id, 0),
        }
        for a in activas
    ]

    ultima = (
        TransaccionMalla.objects.filter(reporte__pozo=pozo)
        .select_related('reporte').order_by('-secuencia').first()
    )

    transacciones = [
        t.to_dict() for t in reporte.transacciones_malla.select_related('malla').order_by('secuencia')
    ]
    costo_diario = round(sum(f['costo_diario'] for f in inventario), 2)
    costo_acumulado = round(sum(f['costo_acumulado'] for f in inventario), 2)

    return {
        'ok': True,
        'error_linea_tiempo': error_linea_tiempo,
        'inventario': inventario,
        'totales': {
            'costo_diario': costo_diario,
            'costo_acumulado': costo_acumulado,
            'nuevas_final': sum(f['nuevas_final'] for f in inventario),
            'usadas_final': sum(f['usadas_final'] for f in inventario),
            'en_equipos': sum(f['en_equipos'] for f in inventario),
        },
        'equipos': equipos,
        'fuera_de_rango': fuera_de_rango,
        'mallas_disponibles': mallas_disponibles,
        'transacciones': transacciones,
        'ultima_transaccion': {
            'secuencia': ultima.secuencia,
            'fecha': ultima.reporte.fecha.strftime('%d/%m/%Y'),
            'es_de_este_reporte': ultima.reporte_id == reporte.id,
        } if ultima else None,
        'tickets': [t.to_dict() for t in reporte.tickets_malla.select_related('tipo').order_by('id')],
        'tipos_ticket': [t.to_dict() for t in _tipos_ticket(pozo)],
        'almacenes': [{'codigo': a.codigo, 'nombre': a.nombre} for a in pozo.almacenes.all()],
        'enlaces': {
            'equipos_activos': reverse('operaciones:active_items', args=[pozo.pk]),
            'catalogos': reverse('operaciones:catalogos_maestros'),
        },
    }


def _respuesta(pozo, reporte, mensaje=None):
    datos = _resumen(pozo, reporte)
    if mensaje:
        datos['mensaje'] = mensaje
    return JsonResponse(datos)


def _obtener(pk, reporte_pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    reporte = get_object_or_404(ReporteDiario, pk=reporte_pk, pozo=pozo)
    return pozo, reporte


def _error(mensaje, status=400):
    return JsonResponse({'ok': False, 'error': mensaje}, status=status)


@require_http_methods(["GET"])
def api_control_solidos_detail(request, pk, reporte_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    return _respuesta(pozo, reporte)


# =====================================================================
# Transacciones de mallas
# =====================================================================

@csrf_exempt
@require_http_methods(["POST"])
def api_transaccion_malla_crear(request, pk, reporte_pk):
    """Registra un movimiento de malla: instalar, pasar al almacén o desechar."""
    pozo, reporte = _obtener(pk, reporte_pk)
    try:
        body = _leer_json(request)
        accion = str(body.get('accion') or '')
        if accion not in dict(TransaccionMalla.ACCION_CHOICES):
            raise _Rechazo('Acción no válida.')

        datos = {'reporte': reporte, 'accion': accion}

        if accion in TransaccionMalla.ACCIONES_CON_POSICION:
            serie = str(body.get('serie') or '').strip()
            equipo_activo = next((e for e in _equipos_con_mallas(pozo) if e.numero_serie == serie), None)
            if equipo_activo is None:
                raise _Rechazo('El equipo no está en la lista de equipos activos del pozo o no lleva mallas.')
            posicion = _entero(body.get('posicion'), 'Posición', minimo=1)
            if posicion > equipo_activo.equipo.posiciones_malla:
                raise _Rechazo(
                    f"El equipo {serie} tiene {equipo_activo.equipo.posiciones_malla} posiciones; "
                    f"la posición {posicion} no existe."
                )
            datos.update({
                'equipo': equipo_activo.equipo,
                'equipo_serie': serie,
                'equipo_descripcion': (equipo_activo.descripcion or equipo_activo.equipo.nombre)[:150],
                'posicion': posicion,
            })

        if accion == TransaccionMalla.DESECHAR_ALMACEN:
            # Puede ser una malla que ya no está activa pero quedó en el almacén.
            malla = MallaZaranda.objects.filter(pk=_entero(body.get('malla_id'), 'Malla', minimo=1)).first()
            if malla is None:
                raise _Rechazo('Elige la malla usada que se va a desechar.')
            datos['malla'] = malla
        elif accion in (TransaccionMalla.INSTALAR_NUEVA, TransaccionMalla.INSTALAR_USADA):
            malla_id = _entero(body.get('malla_id'), 'Malla', minimo=1)
            activa = pozo.mallas_activas.select_related('malla').filter(malla_id=malla_id).first()
            if activa is None:
                raise _Rechazo('Elige una malla de la lista de mallas activas del pozo.')
            datos['malla'] = activa.malla
            if accion == TransaccionMalla.INSTALAR_NUEVA:
                datos['precio_unitario'] = _precio_neto(activa)
        else:
            # Retirar del equipo: la malla es la que está hoy en esa posición.
            estado = _validar_o_rechazar(pozo, reporte)
            malla_id = estado['posiciones'].get((datos['equipo_serie'], datos['posicion']))
            if not malla_id:
                raise _Rechazo(f"La posición {datos['posicion']} del equipo {datos['equipo_serie']} está vacía.")
            datos['malla'] = MallaZaranda.objects.get(pk=malla_id)

        with transaction.atomic():
            ultima = (TransaccionMalla.objects.filter(reporte__pozo=pozo)
                      .aggregate(m=Max('secuencia'))['m'] or 0)
            TransaccionMalla.objects.create(secuencia=ultima + 1, **datos)
            _validar_o_rechazar(pozo, reporte)
    except _Rechazo as e:
        return _error(str(e))

    return _respuesta(pozo, reporte, 'Movimiento registrado.')


@csrf_exempt
@require_http_methods(["POST"])
def api_transaccion_malla_deshacer(request, pk, reporte_pk):
    """Deshace la última transacción del pozo, solo si pertenece a este reporte."""
    pozo, reporte = _obtener(pk, reporte_pk)
    ultima = (TransaccionMalla.objects.filter(reporte__pozo=pozo)
              .select_related('reporte').order_by('-secuencia').first())
    if ultima is None:
        return _error('No hay transacciones de mallas para deshacer.')
    if ultima.reporte_id != reporte.id:
        return _error(
            f"La última transacción del pozo (#{ultima.secuencia}) es del reporte del "
            f"{ultima.reporte.fecha.strftime('%d/%m/%Y')}. Deshazla desde ese reporte."
        )
    try:
        with transaction.atomic():
            ultima.delete()
            _validar_o_rechazar(pozo, reporte)
    except _Rechazo as e:
        return _error(f"No se puede deshacer: {e}")
    return _respuesta(pozo, reporte, f"Transacción #{ultima.secuencia} deshecha.")


# =====================================================================
# Tickets de entrega / devolución
# =====================================================================

@csrf_exempt
@require_http_methods(["POST"])
def api_ticket_malla_guardar(request, pk, reporte_pk):
    """Crea o actualiza un ticket con sus cantidades por malla."""
    pozo, reporte = _obtener(pk, reporte_pk)
    try:
        body = _leer_json(request)

        tipo = pozo.tipos_ticket_malla.filter(pk=_entero(body.get('tipo_id'), 'Tipo', minimo=1)).first()
        if tipo is None:
            raise _Rechazo('Elige el tipo de ticket.')

        almacen_codigo = str(body.get('almacen_codigo') or '').strip()
        almacen_nombre = ''
        if almacen_codigo:
            almacen = pozo.almacenes.filter(codigo=almacen_codigo).first()
            if almacen is None:
                raise _Rechazo('El almacén elegido no existe en la configuración del pozo.')
            almacen_nombre = almacen.nombre

        activas = {a.malla_id: a.malla for a in pozo.mallas_activas.select_related('malla')}
        lineas = []
        vistas = set()
        for item in body.get('detalles') or []:
            malla_id = _entero(item.get('malla_id'), 'Malla', minimo=1)
            if malla_id in vistas:
                raise _Rechazo('Hay una malla repetida en el ticket.')
            vistas.add(malla_id)
            texto = _texto_malla(activas[malla_id]) if malla_id in activas else f"malla {malla_id}"
            cantidades = {
                campo: _entero(item.get(campo), f"{texto} — {etiqueta}")
                for campo, etiqueta in (
                    ('nuevas_ticket', 'nuevas según ticket'), ('nuevas_real', 'nuevas reales'),
                    ('usadas_ticket', 'usadas según ticket'), ('usadas_real', 'usadas reales'),
                )
            }
            if not any(cantidades.values()):
                continue
            if malla_id not in activas:
                raise _Rechazo('Solo se pueden usar mallas de la lista de mallas activas del pozo.')
            lineas.append((activas[malla_id], cantidades))

        if not lineas:
            raise _Rechazo('El ticket no tiene cantidades. Escribe al menos una.')

        with transaction.atomic():
            ticket_id = body.get('id')
            if ticket_id:
                ticket = reporte.tickets_malla.filter(pk=ticket_id).first()
                if ticket is None:
                    raise _Rechazo('El ticket no existe en este reporte.')
            else:
                ticket = TicketMalla(reporte=reporte)
            ticket.tipo = tipo
            ticket.numero = str(body.get('numero') or '').strip()[:40]
            ticket.pedido_por = str(body.get('pedido_por') or '').strip()[:100]
            ticket.recibido_por = str(body.get('recibido_por') or '').strip()[:100]
            ticket.almacen_codigo = almacen_codigo[:15]
            ticket.almacen_nombre = almacen_nombre[:100]
            ticket.save()
            ticket.detalles.all().delete()
            TicketMallaDetalle.objects.bulk_create([
                TicketMallaDetalle(ticket=ticket, malla=malla, **cant) for malla, cant in lineas
            ])
            _validar_o_rechazar(pozo, reporte)
    except _Rechazo as e:
        return _error(str(e))

    datos = _resumen(pozo, reporte)
    datos['mensaje'] = 'Ticket guardado.'
    datos['ticket_id'] = ticket.id
    return JsonResponse(datos)


@csrf_exempt
@require_http_methods(["POST"])
def api_ticket_malla_eliminar(request, pk, reporte_pk, ticket_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    ticket = get_object_or_404(TicketMalla, pk=ticket_pk, reporte=reporte)
    try:
        with transaction.atomic():
            ticket.delete()
            _validar_o_rechazar(pozo, reporte)
    except _Rechazo as e:
        return _error(f"No se puede eliminar el ticket: {e}")
    return _respuesta(pozo, reporte, 'Ticket eliminado.')


# =====================================================================
# Tipos de ticket (catálogo editable del pozo)
# =====================================================================

@csrf_exempt
@require_http_methods(["POST"])
def api_tipo_ticket_malla_guardar(request, pk, reporte_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    try:
        body = _leer_json(request)
        nombre = ' '.join(str(body.get('nombre') or '').split())[:80]
        sentido = str(body.get('sentido') or '')
        if not nombre:
            raise _Rechazo('Escribe el nombre del tipo de ticket.')
        if sentido not in dict(TipoTicketMalla.SENTIDO_CHOICES):
            raise _Rechazo('Elige si el ticket entra o saca mallas del pozo.')

        tipo_id = body.get('id')
        repetido = pozo.tipos_ticket_malla.filter(nombre__iexact=nombre)
        if tipo_id:
            repetido = repetido.exclude(pk=tipo_id)
        if repetido.exists():
            raise _Rechazo(f"Ya existe el tipo de ticket '{nombre}'.")

        with transaction.atomic():
            if tipo_id:
                tipo = pozo.tipos_ticket_malla.filter(pk=tipo_id).first()
                if tipo is None:
                    raise _Rechazo('El tipo de ticket no existe.')
            else:
                tipo = TipoTicketMalla(pozo=pozo)
            tipo.nombre = nombre
            tipo.sentido = sentido
            tipo.save()
            # Cambiar el sentido de un tipo ya usado cambia el inventario histórico.
            _validar_o_rechazar(pozo, reporte)
    except _Rechazo as e:
        return _error(str(e))
    return _respuesta(pozo, reporte, 'Tipo de ticket guardado.')


@csrf_exempt
@require_http_methods(["POST"])
def api_tipo_ticket_malla_eliminar(request, pk, reporte_pk, tipo_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    tipo = get_object_or_404(TipoTicketMalla, pk=tipo_pk, pozo=pozo)
    try:
        tipo.delete()
    except (ProtectedError, RestrictedError):
        return _error(f"El tipo '{tipo.nombre}' ya se usa en tickets; no se puede eliminar.")
    return _respuesta(pozo, reporte, 'Tipo de ticket eliminado.')
