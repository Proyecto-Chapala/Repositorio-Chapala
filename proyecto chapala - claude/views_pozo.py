# ============================================================
# AGREGAR a operaciones/views.py
# ============================================================
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from .models import Pozo, PropiedadUnidadPozo, CategoriaPerdidaItem
from .forms_pozo import (
    PozoPaso1Form, PozoPaso2Form, PropiedadUnidadPozoForm,
    PozoPaso3Form, CategoriaPerdidaItemForm, PozoSpudDateForm,
)


def pozo_to_dict(pozo):
    return {
        "id": pozo.id,
        "nombre": pozo.nombre,
        "estado": pozo.estado,
        "paso_wizard_actual": pozo.paso_wizard_actual,
        "pozo_plantilla_id": pozo.pozo_plantilla_id,
        "pozo_plantilla_nombre": pozo.pozo_plantilla.nombre if pozo.pozo_plantilla else None,
        "sistema_unidades": pozo.sistema_unidades,
        "sistema_unidades_display": pozo.get_sistema_unidades_display(),
        "unidades_bloqueadas": pozo.unidades_bloqueadas,
        "unidades_personalizadas": [
            {"propiedad": u.propiedad, "propiedad_display": u.get_propiedad_display(), "unidad": u.unidad}
            for u in pozo.unidades_personalizadas.all()
        ] if pozo.sistema_unidades == 'CUSTOM' else [],
        "moneda_simbolo": pozo.moneda_simbolo,
        "moneda_decimales": pozo.moneda_decimales,
        "tasa_impuesto": float(pozo.tasa_impuesto),
        "ecuacion_solidos_base_agua": pozo.ecuacion_solidos_base_agua,
        "ecuacion_solidos_base_aceite": pozo.ecuacion_solidos_base_aceite,
        "categoria_perdida_tipo": pozo.categoria_perdida_tipo,
        "categorias_perdida": [
            {"id": c.id, "codigo": c.codigo, "descripcion": c.descripcion, "tipo": c.tipo}
            for c in pozo.categorias_perdida.all()
        ] if pozo.categoria_perdida_tipo == 'CUSTOM' else [],
        "spud_date_completado": pozo.spud_date_completado,
        "fecha_primera_captura": pozo.fecha_primera_captura.isoformat() if pozo.fecha_primera_captura else None,
        "tipo_fluido_inicial": pozo.tipo_fluido_inicial,
        "tipo_fluido_inicial_display": pozo.get_tipo_fluido_inicial_display() if pozo.tipo_fluido_inicial else None,
        "con_tratamiento_disposicion": pozo.con_tratamiento_disposicion,
        "numero_control_logit": pozo.numero_control_logit,
    }


def pozo_wizard_view(request, pk=None):
    """Renderiza el shell del wizard (SPA). Si se pasa pk, retoma un borrador existente."""
    return render(request, 'operaciones/pozos/wizard.html', {'pozo_id': pk})


@require_http_methods(["GET"])
def api_pozos_plantillas(request):
    """Lista de pozos ACTIVOS disponibles para usar como plantilla (paso 1)."""
    pozos = Pozo.objects.filter(estado='ACTIVO').order_by('-created_at')[:50]
    return JsonResponse({
        "success": True,
        "pozos": [{"id": p.id, "nombre": p.nombre, "created_at": p.created_at.isoformat()} for p in pozos]
    })


@require_http_methods(["GET"])
def api_pozo_detail(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return JsonResponse({"success": True, "pozo": pozo_to_dict(pozo)})


@csrf_exempt
@require_http_methods(["POST"])
def api_pozo_paso1(request, pk=None):
    """
    Crea el borrador (pk=None) o actualiza uno existente (pk dado).
    Body: {"nombre": "...", "pozo_plantilla_id": 3 | null}
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    instance = get_object_or_404(Pozo, pk=pk) if pk else Pozo()
    if instance.pk and instance.estado != 'BORRADOR':
        return JsonResponse({
            "success": False,
            "error": "Este pozo ya fue creado; no se puede modificar desde el wizard."
        }, status=400)

    form_data = {
        'nombre': data.get('nombre', ''),
        'pozo_plantilla': data.get('pozo_plantilla_id') or None,
    }
    form = PozoPaso1Form(form_data, instance=instance)
    if not form.is_valid():
        return JsonResponse({"success": False, "errores": form.errors, "error": next(iter(form.errors.values()))[0]}, status=400)

    pozo = form.save(commit=False)
    pozo.estado = 'BORRADOR'
    pozo.paso_wizard_actual = max(pozo.paso_wizard_actual or 1, 1)
    pozo.save()

    # Clonar configuración de la plantilla (solo al crear o al cambiar de plantilla)
    if pozo.pozo_plantilla_id:
        pozo.clonar_configuracion_desde_plantilla()
        pozo.save()
        pozo.unidades_personalizadas.all().delete()
        pozo.categorias_perdida.all().delete()
        pozo.clonar_unidades_personalizadas()
        pozo.clonar_categorias_perdida()

    pozo.paso_wizard_actual = max(pozo.paso_wizard_actual, 2)
    pozo.save()

    return JsonResponse({
        "success": True,
        "mensaje": "Datos básicos guardados.",
        "pozo": pozo_to_dict(pozo)
    }, status=201 if not pk else 200)


@csrf_exempt
@require_http_methods(["POST"])
def api_pozo_paso2(request, pk):
    """
    Guarda sistema de unidades. Si es CUSTOM, además reemplaza las filas
    de PropiedadUnidadPozo con las enviadas.
    Body: {"sistema_unidades": "...", "unidades_personalizadas": [{"propiedad":"...", "unidad":"..."}]}
    """
    pozo = get_object_or_404(Pozo, pk=pk)
    if pozo.unidades_bloqueadas:
        return JsonResponse({"success": False, "error": "Las unidades de este pozo ya están bloqueadas."}, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    form = PozoPaso2Form({'sistema_unidades': data.get('sistema_unidades', '')}, instance=pozo)
    if not form.is_valid():
        return JsonResponse({"success": False, "errores": form.errors, "error": next(iter(form.errors.values()))[0]}, status=400)

    with transaction.atomic():
        pozo = form.save(commit=False)

        if pozo.sistema_unidades == 'CUSTOM':
            filas = data.get('unidades_personalizadas', [])
            errores_filas = []
            nuevas = []
            for fila in filas:
                fila_form = PropiedadUnidadPozoForm(fila)
                if not fila_form.is_valid():
                    errores_filas.append({fila.get('propiedad'): fila_form.errors})
                    continue
                nuevas.append(PropiedadUnidadPozo(
                    pozo=pozo,
                    propiedad=fila_form.cleaned_data['propiedad'],
                    unidad=fila_form.cleaned_data['unidad'],
                ))
            if errores_filas:
                return JsonResponse({
                    "success": False,
                    "error": "Hay unidades personalizadas inválidas.",
                    "errores_filas": errores_filas
                }, status=400)
            pozo.unidades_personalizadas.all().delete()
            PropiedadUnidadPozo.objects.bulk_create(nuevas)
        else:
            # Si cambió de Custom a un preset, se limpia el detalle por propiedad.
            pozo.unidades_personalizadas.all().delete()

        pozo.paso_wizard_actual = max(pozo.paso_wizard_actual, 3)
        pozo.save()

    return JsonResponse({"success": True, "mensaje": "Unidades guardadas.", "pozo": pozo_to_dict(pozo)})


@csrf_exempt
@require_http_methods(["POST"])
def api_pozo_paso3(request, pk):
    """
    Guarda ajustes financieros + tipo de categoría de pérdida.
    Si categoria_perdida_tipo = CUSTOM, reemplaza las filas de CategoriaPerdidaItem.
    """
    pozo = get_object_or_404(Pozo, pk=pk)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    form = PozoPaso3Form({
        'moneda_simbolo': data.get('moneda_simbolo', pozo.moneda_simbolo),
        'moneda_decimales': data.get('moneda_decimales', pozo.moneda_decimales),
        'tasa_impuesto': data.get('tasa_impuesto', pozo.tasa_impuesto),
        'ecuacion_solidos_base_agua': data.get('ecuacion_solidos_base_agua', pozo.ecuacion_solidos_base_agua),
        'ecuacion_solidos_base_aceite': data.get('ecuacion_solidos_base_aceite', pozo.ecuacion_solidos_base_aceite),
        'categoria_perdida_tipo': data.get('categoria_perdida_tipo', pozo.categoria_perdida_tipo),
    }, instance=pozo)

    if pozo.unidades_bloqueadas:
        # La moneda queda fija en cuanto el pozo se activa; en borrador sí es editable.
        pass

    if not form.is_valid():
        return JsonResponse({"success": False, "errores": form.errors, "error": next(iter(form.errors.values()))[0]}, status=400)

    with transaction.atomic():
        pozo = form.save(commit=False)

        if pozo.categoria_perdida_tipo == 'CUSTOM':
            filas = data.get('categorias_perdida', [])
            errores_filas = []
            nuevas = []
            for fila in filas:
                fila_form = CategoriaPerdidaItemForm(fila)
                if not fila_form.is_valid():
                    errores_filas.append({fila.get('codigo'): fila_form.errors})
                    continue
                nuevas.append(CategoriaPerdidaItem(
                    pozo=pozo,
                    codigo=fila_form.cleaned_data['codigo'],
                    descripcion=fila_form.cleaned_data['descripcion'],
                    tipo=fila_form.cleaned_data['tipo'],
                ))
            if errores_filas:
                return JsonResponse({
                    "success": False,
                    "error": "Hay categorías de pérdida inválidas.",
                    "errores_filas": errores_filas
                }, status=400)
            pozo.categorias_perdida.all().delete()
            CategoriaPerdidaItem.objects.bulk_create(nuevas)
        else:
            pozo.categorias_perdida.all().delete()

        pozo.paso_wizard_actual = max(pozo.paso_wizard_actual, 4)
        pozo.save()

    return JsonResponse({"success": True, "mensaje": "Ajustes financieros guardados.", "pozo": pozo_to_dict(pozo)})


@csrf_exempt
@require_http_methods(["POST"])
def api_pozo_confirmar(request, pk):
    """Paso 4 — Confirma la creación: bloquea unidades y activa el pozo."""
    pozo = get_object_or_404(Pozo, pk=pk)

    if pozo.estado == 'ACTIVO':
        return JsonResponse({"success": False, "error": "Este pozo ya fue creado."}, status=400)

    if pozo.paso_wizard_actual < 4:
        return JsonResponse({
            "success": False,
            "error": "Faltan pasos por completar antes de crear el pozo. "
                     f"Vas en el paso {pozo.paso_wizard_actual} de 4."
        }, status=400)

    if not pozo.nombre:
        return JsonResponse({"success": False, "error": "Faltan datos básicos del pozo."}, status=400)

    pozo.activar()

    return JsonResponse({
        "success": True,
        "mensaje": f"Pozo '{pozo.nombre}' creado exitosamente.",
        "pozo": pozo_to_dict(pozo)
    })


# ============================================================
# Spud Date — pantalla única al abrir un pozo (estado ACTIVO)
# por primera vez.
# ============================================================

def pozo_spud_date_view(request, pk):
    """
    Renderiza la pantalla de Spud Date. Si el pozo todavía está en
    BORRADOR (wizard sin terminar), redirige a continuar el wizard.
    Si ya fue completada antes, la plantilla muestra la vista de
    solo lectura (spud_date_completado=True se pasa al contexto).
    """
    pozo = get_object_or_404(Pozo, pk=pk)
    if pozo.estado == 'BORRADOR':
        return redirect('operaciones:pozo_wizard_continuar', pk=pozo.pk)
    return render(request, 'operaciones/pozos/spud_date.html', {'pozo': pozo})


@csrf_exempt
@require_http_methods(["POST"])
def api_pozo_spud_date(request, pk):
    """
    Confirma la pantalla Spud Date. fecha_primera_captura y
    tipo_fluido_inicial quedan inmutables después de este llamado.
    """
    pozo = get_object_or_404(Pozo, pk=pk)

    if pozo.estado != 'ACTIVO':
        return JsonResponse({
            "success": False,
            "error": "El pozo debe estar creado (ACTIVO) antes de registrar la fecha de inicio."
        }, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    form = PozoSpudDateForm({
        'fecha_primera_captura': data.get('fecha_primera_captura'),
        'tipo_fluido_inicial': data.get('tipo_fluido_inicial'),
        'con_tratamiento_disposicion': data.get('con_tratamiento_disposicion', False),
        'numero_control_logit': data.get('numero_control_logit', ''),
    }, instance=pozo)

    if not form.is_valid():
        primer_error = next(iter(form.errors.values()))[0]
        return JsonResponse({"success": False, "errores": form.errors, "error": primer_error}, status=400)

    pozo = form.save(commit=False)
    pozo.spud_date_completado = True
    pozo.save()

    return JsonResponse({
        "success": True,
        "mensaje": "Fecha de inicio registrada. El pozo está listo para la captura diaria.",
        "pozo": pozo_to_dict(pozo)
    })
