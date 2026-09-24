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
