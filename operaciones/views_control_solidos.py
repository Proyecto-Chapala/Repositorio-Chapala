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

from .models import Pozo, MallaZaranda, Equipo, PropiedadEquipoTipo
from .models_daily_reports import ReporteDiario
from .models_control_solidos import (
    TipoTicketMalla, TicketMalla, TicketMallaDetalle, TransaccionMalla,
    UsoEquipoDia, UsoEquipoPropiedad,
)
from .control_solidos import (
    simular, ErrorMallas, volumen_hoyo_perforado, calcular_rendimiento,
    TIPOS_POR_RECORTES, TIPOS_CENTRIFUGA,
)


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


# =====================================================================
# Fase 2 — Detalle y uso de equipos
# =====================================================================

# Orden del árbol de equipos (el mismo de ONE-TRAX: centrífugas, limpiador, zarandas...).
ORDEN_TIPOS = ['CENTRIFUGA', 'LIMPIADOR_LODO', 'ZARANDA', 'SECADOR_RECORTES',
               'OTROS', 'SISTEMA_VACIO', 'CONTENEDOR_RECORTES']

# Tipo de pérdida sugerido por tipo de equipo (códigos estándar de Configuración de Pérdidas).
PERDIDA_SUGERIDA = {'ZARANDA': 1, 'SECADOR_RECORTES': 2, 'CENTRIFUGA': 3, 'LIMPIADOR_LODO': 12}

# Datos que se heredan del día anterior al abrir un reporte nuevo (casi no cambian).
CAMPOS_HEREDADOS = ('mud_on_cuttings', 'porcentaje_recortes', 'tipo_perdida_codigo',
                    'cantidad_usada', 'codigo_cobro', 'es_fluidos')

# (campo, etiqueta, mínimo, máximo) de los datos numéricos del día.
CAMPOS_NUMERICOS = (
    ('horas', 'Horas en operación', 0, 48),
    ('mud_on_cuttings', 'Lodo en recortes', 0, 20),
    ('porcentaje_recortes', '% de recortes', 0, 100),
    ('caudal_entrada_gpm', 'Caudal de entrada', 0, 5000),
    ('densidad_entrada', 'Densidad de entrada', 0, 30),
    ('densidad_salida', 'Densidad de salida', 0, 30),
    ('densidad_descarte', 'Densidad de descarte', 0, 30),
    ('horas_parada', 'Horas de parada', 0, 48),
)


def _num(valor):
    return float(valor) if valor is not None else None


def _contexto_hoyo(reporte, anterior):
    """Avance del día, diámetro del hoyo y volumen de hoyo perforado (bbl)."""
    profundidad = float(reporte.profundidad_actual or 0)
    profundidad_anterior = float(anterior.profundidad_actual or 0) if anterior else 0.0
    avance = max(profundidad - profundidad_anterior, 0.0)

    diametro = 0.0
    fuente = ''
    bit = getattr(reporte, 'bit_data', None)
    if bit:
        diametro = float(bit.washout_hole_size or 0) or float(bit.bit_size or 0)
        fuente = 'pestaña 2 (mecha con lavado)' if diametro else ''
    if diametro <= 0 and reporte.intervalo_costo_id:
        diametro = float(reporte.intervalo_costo.hole_size_in or 0)
        fuente = 'intervalo de revestimiento' if diametro else ''

    return {
        'profundidad_ft': profundidad,
        'profundidad_anterior_ft': profundidad_anterior,
        'hay_reporte_anterior': anterior is not None,
        'avance_ft': avance,
        'diametro_in': diametro,
        'fuente_diametro': fuente,
        'volumen_hoyo_bbl': volumen_hoyo_perforado(diametro, avance),
    }


def _datos_uso(uso):
    return {
        'horas': _num(uso.horas),
        'mud_on_cuttings': _num(uso.mud_on_cuttings),
        'porcentaje_recortes': _num(uso.porcentaje_recortes),
        'tipo_perdida_codigo': uso.tipo_perdida_codigo,
        'caudal_entrada_gpm': _num(uso.caudal_entrada_gpm),
        'densidad_entrada': _num(uso.densidad_entrada),
        'densidad_salida': _num(uso.densidad_salida),
        'densidad_descarte': _num(uso.densidad_descarte),
        'cantidad_usada': float(uso.cantidad_usada or 0),
        'codigo_cobro': uso.codigo_cobro,
        'es_fluidos': uso.es_fluidos,
        'horas_parada': _num(uso.horas_parada),
        'observaciones': uso.observaciones,
    }


def _tarifa_actual(equipo_activo, codigo_cobro):
    if equipo_activo is None or codigo_cobro == UsoEquipoDia.COBRO_SIN:
        return 0.0
    if codigo_cobro == UsoEquipoDia.COBRO_STANDBY:
        return float(equipo_activo.precio_standby or 0)
    return float(equipo_activo.precio_renta or 0)


def _acumulados_previos(pozo, reporte):
    """Horas, volúmenes y costos de los días ANTERIORES, por número de serie."""
    previos = {}
    anterior = None
    reportes = (
        pozo.reportes_diarios.filter(fecha__lt=reporte.fecha).order_by('fecha')
        .select_related('bit_data', 'intervalo_costo').prefetch_related('usos_equipo')
    )
    for rep in reportes:
        vol = _contexto_hoyo(rep, anterior)['volumen_hoyo_bbl']
        for uso in rep.usos_equipo.all():
            calc = calcular_rendimiento(uso.tipo_equipo, _datos_uso(uso), vol)
            acc = previos.setdefault(uso.equipo_serie, {'horas': 0.0, 'descargado_bbl': 0.0,
                                                         'lodo_bbl': 0.0, 'costo': 0.0})
            acc['horas'] += float(uso.horas or 0)
            acc['descargado_bbl'] += calc['descargado_bbl'] or 0.0
            acc['lodo_bbl'] += calc['lodo_bbl'] or 0.0
            acc['costo'] += uso.costo_diario
        anterior = rep
    return previos


def _propiedades_por_tipo(pozo):
    """Propiedades adicionales configuradas en Equipment Properties Setup, por tipo."""
    por_tipo = {}
    seleccionadas = (
        pozo.propiedades_equipo_seleccionadas.select_related('propiedad')
        .order_by('tipo_equipo', 'propiedad__orden', 'propiedad__descripcion')
    )
    for sel in seleccionadas:
        por_tipo.setdefault(sel.tipo_equipo, []).append(
            {'descripcion': sel.propiedad.descripcion, 'unidad': sel.propiedad.unidad})
    for extra in pozo.propiedades_equipo_extra.all():
        por_tipo.setdefault(extra.tipo_equipo, []).append(
            {'descripcion': extra.descripcion, 'unidad': extra.unidad})
    return por_tipo


def _resumen_equipos(pozo, reporte):
    anterior = pozo.reportes_diarios.filter(fecha__lt=reporte.fecha).order_by('-fecha').first()
    contexto = _contexto_hoyo(reporte, anterior)
    tiempo = getattr(reporte, 'distribucion_tiempo', None)
    contexto['horas_periodo'] = float(tiempo.horas_periodo) if tiempo else 24.0

    categorias = [{'codigo': c.codigo, 'descripcion': c.descripcion}
                  for c in pozo.categorias_perdida.all().order_by('codigo')]
    codigos_perdida = {c['codigo'] for c in categorias}

    previos = _acumulados_previos(pozo, reporte)
    propiedades_tipo = _propiedades_por_tipo(pozo)
    tipos_display = dict(Equipo.TIPO_EQUIPO_CHOICES)

    hoy = {u.equipo_serie: u for u in reporte.usos_equipo.prefetch_related('propiedades')}
    ultimo_previo = {}
    if anterior:
        for uso in UsoEquipoDia.objects.filter(
                reporte__pozo=pozo, reporte__fecha__lt=reporte.fecha).order_by('reporte__fecha'):
            ultimo_previo[uso.equipo_serie] = uso

    def fila(serie, equipo, descripcion, equipo_activo, uso):
        tipo = equipo.tipo_equipo
        if uso:
            datos = _datos_uso(uso)
            tarifa = float(uso.tarifa or 0)
            valores_prop = {p.descripcion: p.valor for p in uso.propiedades.all()}
            heredado = False
        else:
            base = ultimo_previo.get(serie)
            datos = {
                'horas': None, 'mud_on_cuttings': None, 'porcentaje_recortes': None,
                'tipo_perdida_codigo': PERDIDA_SUGERIDA.get(tipo) if PERDIDA_SUGERIDA.get(tipo) in codigos_perdida else None,
                'caudal_entrada_gpm': None, 'densidad_entrada': None, 'densidad_salida': None,
                'densidad_descarte': None, 'cantidad_usada': 1.0,
                'codigo_cobro': UsoEquipoDia.COBRO_COMPLETO, 'es_fluidos': False,
                'horas_parada': None, 'observaciones': '',
            }
            if base:
                previo = _datos_uso(base)
                for campo in CAMPOS_HEREDADOS:
                    datos[campo] = previo[campo]
            tarifa = _tarifa_actual(equipo_activo, datos['codigo_cobro'])
            valores_prop = {}
            heredado = base is not None

        propiedades = [
            dict(p, valor=valores_prop.get(p['descripcion'], ''))
            for p in propiedades_tipo.get(tipo, [])
        ]
        # Propiedades guardadas que ya no están en la configuración: se conservan al final.
        configuradas = {p['descripcion'] for p in propiedades}
        if uso:
            for p in uso.propiedades.all():
                if p.descripcion not in configuradas and p.valor:
                    propiedades.append({'descripcion': p.descripcion, 'unidad': p.unidad,
                                        'valor': p.valor, 'fuera_de_configuracion': True})

        return {
            'serie': serie,
            'descripcion': descripcion,
            'equipo_nombre': equipo.nombre,
            'tipo_equipo': tipo,
            'tipo_display': tipos_display.get(tipo, tipo),
            'usa_recortes': tipo in TIPOS_POR_RECORTES,
            'es_centrifuga': tipo in TIPOS_CENTRIFUGA,
            'activo': equipo_activo is not None,
            'guardado': uso is not None,
            'heredado': heredado,
            'datos': datos,
            'tarifa': tarifa,
            'tarifas_pozo': {
                'COMPLETO': _tarifa_actual(equipo_activo, UsoEquipoDia.COBRO_COMPLETO),
                'STANDBY': _tarifa_actual(equipo_activo, UsoEquipoDia.COBRO_STANDBY),
            } if equipo_activo else None,
            'propiedades': propiedades,
            'previo': previos.get(serie, {'horas': 0.0, 'descargado_bbl': 0.0, 'lodo_bbl': 0.0, 'costo': 0.0}),
        }

    filas = []
    vistos = set()
    for ea in pozo.equipos_activos.select_related('equipo').all():
        vistos.add(ea.numero_serie)
        filas.append(fila(ea.numero_serie, ea.equipo, ea.descripcion or ea.equipo.nombre,
                          ea, hoy.get(ea.numero_serie)))
    for serie, uso in hoy.items():
        if serie not in vistos:
            filas.append(fila(serie, uso.equipo, uso.equipo_descripcion or uso.equipo.nombre, None, uso))

    filas.sort(key=lambda f: (ORDEN_TIPOS.index(f['tipo_equipo']) if f['tipo_equipo'] in ORDEN_TIPOS else 99,
                              f['serie']))

    return {
        'ok': True,
        'contexto': contexto,
        'equipos': filas,
        'categorias_perdida': categorias,
        'hay_guardado': bool(hoy),
        'enlaces': {
            'equipos_activos': reverse('operaciones:active_items', args=[pozo.pk]),
            'propiedades': reverse('operaciones:equipment_properties_setup', args=[pozo.pk]),
            'perdidas': reverse('operaciones:loss_setup', args=[pozo.pk]),
        },
    }


@require_http_methods(["GET"])
def api_uso_equipos_detail(request, pk, reporte_pk):
    pozo, reporte = _obtener(pk, reporte_pk)
    return JsonResponse(_resumen_equipos(pozo, reporte))


def _decimal_rango(valor, etiqueta, minimo, maximo):
    if valor in (None, ''):
        return None
    try:
        n = float(str(valor).replace(',', '.'))
    except (TypeError, ValueError):
        raise _Rechazo(f"{etiqueta}: '{valor}' no es un número válido.")
    if n != n or n < minimo or n > maximo:
        raise _Rechazo(f"{etiqueta}: debe estar entre {minimo:g} y {maximo:g}.")
    return Decimal(str(round(n, 3)))


@csrf_exempt
@require_http_methods(["POST"])
def api_uso_equipos_guardar(request, pk, reporte_pk):
    """Guarda el rendimiento, los costos y las paradas del día de todos los equipos."""
    pozo, reporte = _obtener(pk, reporte_pk)
    try:
        body = _leer_json(request)
        activos = {e.numero_serie: e for e in pozo.equipos_activos.select_related('equipo')}
        previos_hoy = {u.equipo_serie: u for u in reporte.usos_equipo.select_related('equipo')}
        categorias = {c.codigo: c.descripcion for c in pozo.categorias_perdida.all()}

        nuevos = []
        vistos = set()
        for item in body.get('equipos') or []:
            serie = str(item.get('serie') or '').strip()
            if not serie or serie in vistos:
                continue
            vistos.add(serie)
            activo = activos.get(serie)
            previo = previos_hoy.get(serie)
            if activo is None and previo is None:
                raise _Rechazo(f"El equipo {serie} no está en los equipos activos del pozo.")
            equipo = activo.equipo if activo else previo.equipo
            nombre = (activo.descripcion or activo.equipo.nombre) if activo else previo.equipo_descripcion
            etiqueta = f"{nombre} ({serie})"

            uso = UsoEquipoDia(
                reporte=reporte, equipo=equipo, equipo_serie=serie[:30],
                equipo_descripcion=(nombre or '')[:150], tipo_equipo=equipo.tipo_equipo,
            )
            for campo, texto, minimo, maximo in CAMPOS_NUMERICOS:
                setattr(uso, campo, _decimal_rango(item.get(campo), f"{etiqueta} — {texto}", minimo, maximo))

            codigo_perdida = item.get('tipo_perdida_codigo')
            if codigo_perdida not in (None, ''):
                codigo_perdida = _entero(codigo_perdida, f"{etiqueta} — tipo de pérdida", minimo=1)
                if codigo_perdida in categorias:
                    uso.tipo_perdida_descripcion = categorias[codigo_perdida][:100]
                elif previo and previo.tipo_perdida_codigo == codigo_perdida:
                    uso.tipo_perdida_descripcion = previo.tipo_perdida_descripcion
                else:
                    raise _Rechazo(f"{etiqueta}: el tipo de pérdida no existe en la configuración del pozo.")
                uso.tipo_perdida_codigo = codigo_perdida

            cantidad = _decimal_rango(item.get('cantidad_usada'), f"{etiqueta} — cantidad usada", 0, 9999)
            uso.cantidad_usada = cantidad if cantidad is not None else Decimal('0')
            codigo = str(item.get('codigo_cobro') or UsoEquipoDia.COBRO_COMPLETO)
            if codigo not in dict(UsoEquipoDia.COBRO_CHOICES):
                raise _Rechazo(f"{etiqueta}: código de cobro no válido.")
            uso.codigo_cobro = codigo
            # La tarifa se copia del pozo al registrar el día y se conserva mientras no
            # cambie el código de cobro: editar un día viejo no le cambia el precio.
            if previo and previo.codigo_cobro == codigo:
                uso.tarifa = previo.tarifa
            else:
                uso.tarifa = Decimal(str(_tarifa_actual(activo, codigo)))
            uso.es_fluidos = bool(item.get('es_fluidos'))
            uso.observaciones = str(item.get('observaciones') or '').strip()

            propiedades = []
            for i, prop in enumerate(item.get('propiedades') or []):
                descripcion = str(prop.get('descripcion') or '').strip()[:100]
                valor = str(prop.get('valor') or '').strip()[:60]
                if descripcion and valor:
                    propiedades.append(UsoEquipoPropiedad(
                        orden=i, descripcion=descripcion,
                        unidad=str(prop.get('unidad') or '').strip()[:30], valor=valor))
            nuevos.append((uso, propiedades))

        with transaction.atomic():
            # Los equipos guardados que no vinieron en el envío se conservan.
            reporte.usos_equipo.filter(equipo_serie__in=vistos).delete()
            for uso, propiedades in nuevos:
                uso.save()
                for p in propiedades:
                    p.uso = uso
                UsoEquipoPropiedad.objects.bulk_create(propiedades)
    except _Rechazo as e:
        return _error(str(e))

    datos = _resumen_equipos(pozo, reporte)
    datos['mensaje'] = 'Detalle y uso de equipos guardado.'
    return JsonResponse(datos)
