import json
import os
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, models
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from .models import (
    Producto, Pozo, PropiedadUnidadPozo, CategoriaPerdidaItem,
    WellHeaderInfo, IntervaloRevestimiento, TipoFosa, Fosa,
    AlmacenCodigo, TipoDistribucionTiempo,
    Equipo, MallaZaranda, ProductoActivoPozo, EquipoActivoPozo, MallaActivaPozo,
    PropiedadEquipoTipo, EquipoPropiedadSeleccionada, EquipoPropiedadExtra,
    CentrifugaUnidadConfig, ParametroBenchmark, BenchmarkSeleccionado, BenchmarkTarget,
    ComponenteSarta,
)
from .forms_pozo import (
    PozoPaso1Form, PozoPaso2Form, PropiedadUnidadPozoForm,
    PozoPaso3Form, CategoriaPerdidaItemForm, PozoSpudDateForm,
    WellHeaderInfoForm, MarketingCodesForm, IntervaloRevestimientoForm,
    FosaForm, TipoFosaForm, GeneralSetupForm, AlmacenCodigoForm,
    TipoDistribucionTiempoForm, ProductoActivoPozoForm, EquipoActivoPozoForm,
    MallaActivaPozoForm, PropiedadEquipoTipoForm, ParametroBenchmarkForm,
    CentrifugaUnidadConfigForm,
)


def index(request):
    """Renderiza la SPA principal de Operaciones."""
    return render(request, 'operaciones/index.html')


@require_http_methods(["GET"])
def api_productos_list(request):
    """
    Lista los productos con filtros opcionales de categoría, estado y búsqueda.
    """
    categoria = request.GET.get('categoria', '').strip().upper()
    estado = request.GET.get('estado', '').strip().upper()
    search = request.GET.get('search', '').strip()

    qs = Producto.objects.all()

    if categoria in ['SOLIDO', 'LIQUIDO']:
        qs = qs.filter(categoria=categoria)

    if estado in ['ALTO', 'MEDIO', 'BAJO']:
        qs = qs.filter(estado=estado)

    if search:
        qs = qs.filter(
            Q(codigo__icontains=search) | 
            Q(descripcion__icontains=search) |
            Q(unidad__icontains=search)
        )

    # Ordenamiento por código
    qs = qs.order_by('codigo')

    productos = [p.to_dict() for p in qs]

    # Estadísticas para chips o badges superiores
    total_solidos = Producto.objects.filter(categoria='SOLIDO').count()
    total_liquidos = Producto.objects.filter(categoria='LIQUIDO').count()
    total_productos = Producto.objects.count()

    return JsonResponse({
        "success": True,
        "productos": productos,
        "totales": {
            "total": total_productos,
            "solidos": total_solidos,
            "liquidos": total_liquidos
        }
    })


@require_http_methods(["GET"])
def api_producto_detail(request, pk):
    """Obtiene el detalle de un producto por su ID."""
    producto = get_object_or_404(Producto, pk=pk)
    return JsonResponse({
        "success": True,
        "producto": producto.to_dict()
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_producto_create(request):
    """Crea un nuevo producto en el inventario con validaciones estrictas."""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    codigo = str(data.get('codigo', '')).strip()
    descripcion = str(data.get('descripcion', '')).strip()
    unidad = str(data.get('unidad', '')).strip()
    categoria = str(data.get('categoria', 'SOLIDO')).strip().upper()
    estado = str(data.get('estado', 'ALTO')).strip().upper()
    observacion = str(data.get('observacion', '')).strip()

    # Validaciones obligatorias
    errores = {}
    if not codigo:
        errores['codigo'] = "El código del producto es obligatorio."
    elif Producto.objects.filter(codigo__iexact=codigo).exists():
        errores['codigo'] = f"Ya existe un producto con el código '{codigo}'."

    if not descripcion:
        errores['descripcion'] = "La descripción es obligatoria."

    if not unidad:
        errores['unidad'] = "La unidad/presentación es obligatoria."

    if categoria not in ['SOLIDO', 'LIQUIDO']:
        errores['categoria'] = "La categoría debe ser 'SOLIDO' o 'LIQUIDO'."

    if estado not in ['ALTO', 'MEDIO', 'BAJO']:
        errores['estado'] = "El estado debe ser 'ALTO', 'MEDIO' o 'BAJO'."

    # Números
    try:
        libraje = Decimal(str(data.get('libraje', 0)))
        if libraje < 0:
            errores['libraje'] = "El libraje no puede ser negativo."
    except Exception:
        errores['libraje'] = "El libraje debe ser un número válido."

    try:
        gravedad = Decimal(str(data.get('gravedad', 1.0)))
        if gravedad <= 0:
            errores['gravedad'] = "La gravedad específica debe ser mayor a 0."
    except Exception:
        errores['gravedad'] = "La gravedad específica debe ser un número válido."

    try:
        costo = Decimal(str(data.get('costo', 0)))
        if costo < 0:
            errores['costo'] = "El costo no puede ser negativo."
    except Exception:
        errores['costo'] = "El costo debe ser un número válido."

    try:
        cantidad = Decimal(str(data.get('cantidad', 0)))
        if cantidad < 0:
            errores['cantidad'] = "La cantidad no puede ser negativa."
    except Exception:
        errores['cantidad'] = "La cantidad debe ser un número válido."

    if errores:
        return JsonResponse({"success": False, "errores": errores, "error": next(iter(errores.values()))}, status=400)

    producto = Producto.objects.create(
        codigo=codigo,
        descripcion=descripcion,
        unidad=unidad,
        libraje=libraje,
        gravedad=gravedad,
        costo=costo,
        cantidad=cantidad,
        categoria=categoria,
        estado=estado,
        observacion=observacion or None
    )

    return JsonResponse({
        "success": True,
        "mensaje": f"Producto '{producto.codigo}' creado exitosamente.",
        "producto": producto.to_dict()
    }, status=201)


@csrf_exempt
@require_http_methods(["PUT", "POST"])
def api_producto_update(request, pk):
    """Modifica un producto existente."""
    producto = get_object_or_404(Producto, pk=pk)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    codigo = str(data.get('codigo', producto.codigo)).strip()
    descripcion = str(data.get('descripcion', producto.descripcion)).strip()
    unidad = str(data.get('unidad', producto.unidad)).strip()
    categoria = str(data.get('categoria', producto.categoria)).strip().upper()
    estado = str(data.get('estado', producto.estado)).strip().upper()
    observacion = str(data.get('observacion', producto.observacion or '')).strip()

    errores = {}
    if not codigo:
        errores['codigo'] = "El código del producto es obligatorio."
    elif Producto.objects.filter(codigo__iexact=codigo).exclude(pk=producto.pk).exists():
        errores['codigo'] = f"Ya existe otro producto con el código '{codigo}'."

    if not descripcion:
        errores['descripcion'] = "La descripción es obligatoria."

    if not unidad:
        errores['unidad'] = "La unidad/presentación es obligatoria."

    if categoria not in ['SOLIDO', 'LIQUIDO']:
        errores['categoria'] = "La categoría debe ser 'SOLIDO' o 'LIQUIDO'."

    if estado not in ['ALTO', 'MEDIO', 'BAJO']:
        errores['estado'] = "El estado debe ser 'ALTO', 'MEDIO' o 'BAJO'."

    try:
        libraje = Decimal(str(data.get('libraje', producto.libraje)))
        if libraje < 0:
            errores['libraje'] = "El libraje no puede ser negativo."
    except Exception:
        errores['libraje'] = "El libraje debe ser un número válido."

    try:
        gravedad = Decimal(str(data.get('gravedad', producto.gravedad)))
        if gravedad <= 0:
            errores['gravedad'] = "La gravedad específica debe ser mayor a 0."
    except Exception:
        errores['gravedad'] = "La gravedad específica debe ser un número válido."

    try:
        costo = Decimal(str(data.get('costo', producto.costo)))
        if costo < 0:
            errores['costo'] = "El costo no puede ser negativo."
    except Exception:
        errores['costo'] = "El costo debe ser un número válido."

    try:
        cantidad = Decimal(str(data.get('cantidad', producto.cantidad)))
        if cantidad < 0:
            errores['cantidad'] = "La cantidad no puede ser negativa."
    except Exception:
        errores['cantidad'] = "La cantidad debe ser un número válido."

    if errores:
        return JsonResponse({"success": False, "errores": errores, "error": next(iter(errores.values()))}, status=400)

    producto.codigo = codigo
    producto.descripcion = descripcion
    producto.unidad = unidad
    producto.libraje = libraje
    producto.gravedad = gravedad
    producto.costo = costo
    producto.cantidad = cantidad
    producto.categoria = categoria
    producto.estado = estado
    producto.observacion = observacion or None
    producto.save()

    return JsonResponse({
        "success": True,
        "mensaje": f"Producto '{producto.codigo}' actualizado correctamente.",
        "producto": producto.to_dict()
    })


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def api_producto_delete(request, pk):
    """
    Elimina un producto siempre y cuando su cantidad disponible sea 0.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if producto.cantidad > 0:
        return JsonResponse({
            "success": False,
            "error": f"No se puede eliminar el producto '{producto.codigo}' porque tiene {producto.cantidad} unidades en stock disponible. La cantidad debe ser 0 para permitir su eliminación."
        }, status=400)

    codigo = producto.codigo
    try:
        producto.delete()
    except ProtectedError:
        pozos = sorted(set(
            producto.activos_en_pozos.values_list('pozo__nombre', flat=True)
        ))
        if pozos:
            motivo = (f"está activo en: {', '.join(pozos)}. "
                      "Quítelo primero de los productos activos de esos pozos.")
        else:
            motivo = "tiene movimientos, tickets o inventarios registrados en reportes diarios."
        return JsonResponse({
            "success": False,
            "error": f"No se puede eliminar el producto '{codigo}' porque {motivo}"
        }, status=400)

    return JsonResponse({
        "success": True,
        "mensaje": f"Producto '{codigo}' eliminado satisfactoriamente."
    })


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
        # Productos, equipos y mallas activos (lo que promete la pantalla del paso 1).
        pozo.clonar_listas_activas()

    # Categorías de pérdida (Loss Setup): se clonan de la plantilla si existe, o
    # se siembran las estándar de ONE-TRAX si el pozo aún no tiene ninguna.
    pozo.clonar_categorias_perdida()

    # Fosas y tipos de fosa: se clonan de la plantilla si existe, o se
    # siembran los 7 tipos estándar de ONE-TRAX si el pozo aún no tiene ninguno.
    pozo.clonar_fosas_y_tipos()

    # Configuración General (Time Distribution Setup): siembra el catálogo
    # estándar de actividades de taladro si el pozo aún no tiene ninguna.
    if not pozo.tipos_distribucion_tiempo.exists():
        TipoDistribucionTiempo.sembrar_estandar(pozo)

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
        # Si no es CUSTOM, se dejan las categorías tal cual están (editables
        # después desde la pantalla independiente de Configuración de Pérdidas).

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


# ============================================================
# Project Main Screen — landing del pozo activo
# ============================================================

def pozo_main_view(request, pk):
    """
    Pantalla principal del pozo (equivalente al 'Project Main Screen' de
    ONE-TRAX). Solo accesible para pozos ACTIVOS; si el pozo sigue en
    BORRADOR redirige al wizard, y si le falta Spud Date redirige allá.
    """
    pozo = get_object_or_404(Pozo, pk=pk)
    if pozo.estado == 'BORRADOR':
        return redirect('operaciones:pozo_wizard_continuar', pk=pozo.pk)
    if not pozo.spud_date_completado:
        return redirect('operaciones:pozo_spud_date', pk=pozo.pk)
    return render(request, 'operaciones/pozos/main.html', {'pozo': pozo})




def pozos_list_view(request):
    """Vista temporal/placeholder para la lista de pozos en el sidebar."""
    from .models import Pozo
    pozos = Pozo.objects.all()
    return render(request, 'operaciones/pozos_list.html', {'pozos': pozos})


# ============================================================
# Well Header Information (2 pestañas)
# ============================================================

def well_header_view(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return render(request, 'operaciones/pozos/well_header.html', {'pozo': pozo})


def _well_header_to_dict(info):
    campos = [
        'es_offshore', 'air_gap_ft', 'water_depth_ft', 'sea_floor_temp_f',
        'usa_riser', 'riser_id_in', 'riser_length_ft',
        'operador', 'field_area', 'descripcion', 'ubicacion', 'almacen',
        'contratista', 'nombre_taladro', 'ingeniero_proyecto',
        'ingeniero_miswaco_1', 'ingeniero_miswaco_2',
        'td_days', 're_entry_depth_ft', 'latitud_ns_indicador', 'longitud_ew_indicador',
        'surface_temp_f', 'temp_gradient_f_100ft',
        'total_depth_ft', 'total_days', 'maximum_temperature_f', 'tvd_ft',
        'total_cost', 'horiz_displacement_ft', 'comentarios', 'numero_control_logit',
        'primary_mud_type_codigo', 'primary_mud_type_descripcion',
        'well_type_codigo', 'well_type_descripcion',
        'contract_type_codigo', 'contract_type_descripcion',
        'completion_fluid_type_codigo', 'completion_fluid_type_descripcion',
        'completado', 'marketing_codes_completado',
    ]
    data = {}
    for campo in campos:
        valor = getattr(info, campo)
        data[campo] = float(valor) if isinstance(valor, Decimal) else valor
    for campo_fecha in ['spud_date', 'td_date', 'end_date']:
        valor = getattr(info, campo_fecha)
        data[campo_fecha] = valor.isoformat() if valor else None
    return data


@require_http_methods(["GET"])
def api_well_header_detail(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    info, _ = WellHeaderInfo.objects.get_or_create(pozo=pozo)
    return JsonResponse({"success": True, "well_header": _well_header_to_dict(info)})


@csrf_exempt
@require_http_methods(["POST"])
def api_well_header_guardar(request, pk):
    """Guarda la pestaña 1 (Well Information)."""
    pozo = get_object_or_404(Pozo, pk=pk)
    info, _ = WellHeaderInfo.objects.get_or_create(pozo=pozo)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    form = WellHeaderInfoForm(data, instance=info)
    if not form.is_valid():
        return JsonResponse({
            "success": False, "errores": form.errors,
            "error": next(iter(form.errors.values()))[0]
        }, status=400)

    info = form.save(commit=False)
    info.completado = True
    info.save()

    return JsonResponse({
        "success": True, "mensaje": "Well Information guardada.",
        "well_header": _well_header_to_dict(info)
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_marketing_codes_guardar(request, pk):
    """Guarda la pestaña 2 (Marketing Codes)."""
    pozo = get_object_or_404(Pozo, pk=pk)
    info, _ = WellHeaderInfo.objects.get_or_create(pozo=pozo)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    form = MarketingCodesForm(data, instance=info)
    if not form.is_valid():
        return JsonResponse({
            "success": False, "errores": form.errors,
            "error": next(iter(form.errors.values()))[0]
        }, status=400)

    info = form.save(commit=False)
    info.marketing_codes_completado = True
    info.save()

    return JsonResponse({
        "success": True, "mensaje": "Marketing Codes guardado.",
        "well_header": _well_header_to_dict(info)
    })


# ============================================================
# Well Casing Intervals (Cost)
# ============================================================

def casing_intervals_view(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return render(request, 'operaciones/pozos/casing_intervals.html', {'pozo': pozo})


def _intervalo_to_dict(intervalo):
    campos = [
        'id', 'numero_intervalo', 'tipo', 'casing_od_in', 'casing_id_in', 'hole_size_in',
        'profundidad_ft', 'tvd_ft', 'top_of_liner_ft', 'maximum_density_lb_gal',
        'max_bht_f', 'maximum_angle', 'interval_days', 'planned_days', 'planned_length_ft',
        'interval_cost', 'planned_cost', 'frac_grad_lb_gal', 'fluid_type_code_1',
        'fluid_type_code_2', 'observaciones_recomendaciones', 'comentarios_recap',
    ]
    data = {}
    for campo in campos:
        valor = getattr(intervalo, campo)
        data[campo] = float(valor) if isinstance(valor, Decimal) else valor
    data['tipo_display'] = intervalo.get_tipo_display() if intervalo.tipo else ''
    return data


@require_http_methods(["GET"])
def api_intervalos_list(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    intervalos = pozo.intervalos_revestimiento.all()
    return JsonResponse({
        "success": True,
        "intervalos": [_intervalo_to_dict(i) for i in intervalos],
        "tipo_choices": IntervaloRevestimiento.TIPO_CHOICES,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_intervalo_crear(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    siguiente = (pozo.intervalos_revestimiento.aggregate(models.Max('numero_intervalo'))['numero_intervalo__max'] or 0) + 1
    data.setdefault('numero_intervalo', siguiente)

    # Se instancia con el pozo ya asignado para que la validación de
    # unique_together(pozo, numero_intervalo) compare contra el pozo correcto.
    form = IntervaloRevestimientoForm(data, instance=IntervaloRevestimiento(pozo=pozo))
    if not form.is_valid():
        return JsonResponse({
            "success": False, "errores": form.errors,
            "error": next(iter(form.errors.values()))[0]
        }, status=400)

    intervalo = form.save(commit=False)
    intervalo.pozo = pozo
    intervalo.save()

    return JsonResponse({
        "success": True, "mensaje": f"Intervalo {intervalo.numero_intervalo} creado.",
        "intervalo": _intervalo_to_dict(intervalo)
    }, status=201)


@csrf_exempt
@require_http_methods(["POST", "PUT"])
def api_intervalo_actualizar(request, pk, intervalo_pk):
    intervalo = get_object_or_404(IntervaloRevestimiento, pk=intervalo_pk, pozo_id=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    form = IntervaloRevestimientoForm(data, instance=intervalo)
    if not form.is_valid():
        return JsonResponse({
            "success": False, "errores": form.errors,
            "error": next(iter(form.errors.values()))[0]
        }, status=400)

    intervalo = form.save()
    return JsonResponse({
        "success": True, "mensaje": "Intervalo actualizado.",
        "intervalo": _intervalo_to_dict(intervalo)
    })


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def api_intervalo_eliminar(request, pk, intervalo_pk):
    intervalo = get_object_or_404(IntervaloRevestimiento, pk=intervalo_pk, pozo_id=pk)
    numero = intervalo.numero_intervalo
    intervalo.delete()
    return JsonResponse({"success": True, "mensaje": f"Intervalo {numero} eliminado."})


# ============================================================
# Pit Information (Fosas + Pit Type Setup)
# ============================================================

def pits_view(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    if not pozo.tipos_fosa.exists():
        TipoFosa.sembrar_estandar(pozo)
    return render(request, 'operaciones/pozos/pits.html', {'pozo': pozo})


@require_http_methods(["GET"])
def api_pits_list(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    fosas = pozo.fosas.all()
    tipos = pozo.tipos_fosa.all()
    return JsonResponse({
        "success": True,
        "fosas": [
            {"id": f.id, "numero": f.numero, "descripcion": f.descripcion, "capacidad": float(f.capacidad)}
            for f in fosas
        ],
        "tipos_fosa": [
            {"id": t.id, "codigo": t.codigo, "descripcion": t.descripcion}
            for t in tipos
        ],
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_fosas_guardar(request, pk):
    """Reemplaza el listado completo de fosas del pozo (guardado en bloque, como la grilla de ONE-TRAX)."""
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    filas = data.get('fosas', [])
    errores = []
    nuevas = []
    numeros_vistos = set()
    for fila in filas:
        f_form = FosaForm(fila)
        if not f_form.is_valid():
            errores.append({fila.get('numero'): f_form.errors})
            continue
        numero = f_form.cleaned_data['numero']
        if numero in numeros_vistos:
            errores.append({numero: "Número de Pit repetido."})
            continue
        numeros_vistos.add(numero)
        nuevas.append(Fosa(
            pozo=pozo, numero=numero,
            descripcion=f_form.cleaned_data['descripcion'],
            capacidad=f_form.cleaned_data['capacidad'],
        ))

    if errores:
        return JsonResponse({"success": False, "error": "Hay fosas inválidas.", "errores_filas": errores}, status=400)

    with transaction.atomic():
        pozo.fosas.all().delete()
        Fosa.objects.bulk_create(nuevas)

    return JsonResponse({"success": True, "mensaje": "Fosas guardadas.", "total": len(nuevas)})


@csrf_exempt
@require_http_methods(["POST"])
def api_tipos_fosa_guardar(request, pk):
    """Reemplaza el listado completo de Pit Type Setup del pozo."""
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    filas = data.get('tipos_fosa', [])
    errores = []
    nuevas = []
    codigos_vistos = set()
    for fila in filas:
        t_form = TipoFosaForm(fila)
        if not t_form.is_valid():
            errores.append({fila.get('codigo'): t_form.errors})
            continue
        codigo = t_form.cleaned_data['codigo']
        if codigo in codigos_vistos:
            errores.append({codigo: "Código de tipo repetido."})
            continue
        codigos_vistos.add(codigo)
        nuevas.append(TipoFosa(pozo=pozo, codigo=codigo, descripcion=t_form.cleaned_data['descripcion']))

    if errores:
        return JsonResponse({"success": False, "error": "Hay tipos de fosa inválidos.", "errores_filas": errores}, status=400)

    with transaction.atomic():
        pozo.tipos_fosa.all().delete()
        TipoFosa.objects.bulk_create(nuevas)

    return JsonResponse({"success": True, "mensaje": "Pit Type Setup guardado.", "total": len(nuevas)})


# ============================================================
# Configuración de Pérdidas (Loss Setup)
# ============================================================

def loss_setup_view(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    if not pozo.categorias_perdida.exists():
        CategoriaPerdidaItem.sembrar_estandar(pozo)
    return render(request, 'operaciones/pozos/loss_setup.html', {'pozo': pozo})


@require_http_methods(["GET"])
def api_categorias_perdida_list(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    categorias = pozo.categorias_perdida.all()
    return JsonResponse({
        "success": True,
        "categorias": [
            {"id": c.id, "codigo": c.codigo, "descripcion": c.descripcion, "tipo": c.tipo}
            for c in categorias
        ],
        "tipo_choices": CategoriaPerdidaItem.TIPO_CHOICES,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_categorias_perdida_guardar(request, pk):
    """Reemplaza el listado completo de categorías de pérdida del pozo."""
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    filas = data.get('categorias', [])
    errores = []
    nuevas = []
    codigos_vistos = set()
    for fila in filas:
        c_form = CategoriaPerdidaItemForm(fila)
        if not c_form.is_valid():
            errores.append({fila.get('codigo'): c_form.errors})
            continue
        codigo = c_form.cleaned_data['codigo']
        if codigo in codigos_vistos:
            errores.append({codigo: "Código repetido."})
            continue
        codigos_vistos.add(codigo)
        nuevas.append(CategoriaPerdidaItem(
            pozo=pozo, codigo=codigo,
            descripcion=c_form.cleaned_data['descripcion'],
            tipo=c_form.cleaned_data['tipo'],
        ))

    if errores:
        return JsonResponse({"success": False, "error": "Hay categorías inválidas.", "errores_filas": errores}, status=400)

    with transaction.atomic():
        pozo.categorias_perdida.all().delete()
        CategoriaPerdidaItem.objects.bulk_create(nuevas)

    return JsonResponse({"success": True, "mensaje": "Categorías de pérdida guardadas.", "total": len(nuevas)})


# ============================================================
# Configuración General (General Setup)
# ============================================================

def general_setup_view(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    if not pozo.tipos_distribucion_tiempo.exists():
        TipoDistribucionTiempo.sembrar_estandar(pozo)
    return render(request, 'operaciones/pozos/general_setup.html', {'pozo': pozo})


@require_http_methods(["GET"])
def api_general_setup_detail(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return JsonResponse({
        "success": True,
        "general_setup": {
            "moneda_simbolo": pozo.moneda_simbolo,
            "moneda_decimales": pozo.moneda_decimales,
            "tasa_impuesto": float(pozo.tasa_impuesto),
            "con_tratamiento_disposicion": pozo.con_tratamiento_disposicion,
            "usar_api_5ta_edicion_hidraulica": pozo.usar_api_5ta_edicion_hidraulica,
            "ecuacion_solidos_base_agua": pozo.ecuacion_solidos_base_agua,
            "ecuacion_solidos_base_aceite": pozo.ecuacion_solidos_base_aceite,
        },
        "ecuacion_solidos_choices": Pozo.ECUACION_SOLIDOS_CHOICES,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_general_setup_guardar(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    form = GeneralSetupForm(data, instance=pozo)
    if not form.is_valid():
        return JsonResponse({
            "success": False, "errores": form.errors,
            "error": next(iter(form.errors.values()))[0]
        }, status=400)

    pozo = form.save()
    return JsonResponse({
        "success": True, "mensaje": "Configuración General guardada.",
        "general_setup": {
            "moneda_simbolo": pozo.moneda_simbolo,
            "moneda_decimales": pozo.moneda_decimales,
            "tasa_impuesto": float(pozo.tasa_impuesto),
            "con_tratamiento_disposicion": pozo.con_tratamiento_disposicion,
            "usar_api_5ta_edicion_hidraulica": pozo.usar_api_5ta_edicion_hidraulica,
            "ecuacion_solidos_base_agua": pozo.ecuacion_solidos_base_agua,
            "ecuacion_solidos_base_aceite": pozo.ecuacion_solidos_base_aceite,
        }
    })


@require_http_methods(["GET"])
def api_almacenes_list(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return JsonResponse({
        "success": True,
        "almacenes": [
            {"id": a.id, "codigo": a.codigo, "nombre": a.nombre}
            for a in pozo.almacenes.all()
        ],
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_almacenes_guardar(request, pk):
    """Reemplaza el listado completo de códigos de almacén del pozo."""
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    filas = data.get('almacenes', [])
    errores = []
    nuevas = []
    codigos_vistos = set()
    for fila in filas:
        a_form = AlmacenCodigoForm(fila)
        if not a_form.is_valid():
            errores.append({fila.get('codigo'): a_form.errors})
            continue
        codigo = a_form.cleaned_data['codigo']
        if codigo in codigos_vistos:
            errores.append({codigo: "Código de almacén repetido."})
            continue
        codigos_vistos.add(codigo)
        nuevas.append(AlmacenCodigo(pozo=pozo, codigo=codigo, nombre=a_form.cleaned_data['nombre']))

    if errores:
        return JsonResponse({"success": False, "error": "Hay almacenes inválidos.", "errores_filas": errores}, status=400)

    with transaction.atomic():
        pozo.almacenes.all().delete()
        AlmacenCodigo.objects.bulk_create(nuevas)

    return JsonResponse({"success": True, "mensaje": "Códigos de almacén guardados.", "total": len(nuevas)})


@require_http_methods(["GET"])
def api_tipos_distribucion_list(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return JsonResponse({
        "success": True,
        "tipos_distribucion": [
            {"id": t.id, "numero": t.numero, "descripcion": t.descripcion, "tipo": t.tipo}
            for t in pozo.tipos_distribucion_tiempo.all()
        ],
        "tipo_choices": TipoDistribucionTiempo.TIPO_CHOICES,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_tipos_distribucion_guardar(request, pk):
    """Reemplaza el listado completo de Time Distribution Setup del pozo."""
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    filas = data.get('tipos_distribucion', [])
    errores = []
    nuevas = []
    numeros_vistos = set()
    for fila in filas:
        t_form = TipoDistribucionTiempoForm(fila)
        if not t_form.is_valid():
            errores.append({fila.get('numero'): t_form.errors})
            continue
        numero = t_form.cleaned_data['numero']
        if numero in numeros_vistos:
            errores.append({numero: "Número repetido."})
            continue
        numeros_vistos.add(numero)
        nuevas.append(TipoDistribucionTiempo(
            pozo=pozo, numero=numero,
            descripcion=t_form.cleaned_data['descripcion'],
            tipo=t_form.cleaned_data['tipo'],
        ))

    if errores:
        return JsonResponse({"success": False, "error": "Hay tipos inválidos.", "errores_filas": errores}, status=400)

    with transaction.atomic():
        pozo.tipos_distribucion_tiempo.all().delete()
        TipoDistribucionTiempo.objects.bulk_create(nuevas)

    return JsonResponse({"success": True, "mensaje": "Time Distribution Setup guardado.", "total": len(nuevas)})


# ============================================================
# Productos / Equipos / Mallas Activos
# (Active Products/Equipment/Screens)
# ============================================================

def active_items_view(request, pk):
    """
    Pantalla de 3 pestañas: Productos Activos, Equipos Activos y Mallas
    Activas del pozo. Los catálogos maestros (Producto, Equipo,
    MallaZaranda) son globales y compartidos entre todos los pozos.
    """
    pozo = get_object_or_404(Pozo, pk=pk)
    return render(request, 'operaciones/pozos/active_items.html', {'pozo': pozo})


@require_http_methods(["GET"])
def api_equipos_list(request):
    """Master Equipment List — catálogo maestro global de equipos."""
    search = request.GET.get('search', '').strip()
    tipo_equipo = request.GET.get('tipo_equipo', '').strip()
    qs = Equipo.objects.all()
    if search:
        qs = qs.filter(Q(codigo__icontains=search) | Q(nombre__icontains=search))
    if tipo_equipo:
        qs = qs.filter(tipo_equipo=tipo_equipo)
    return JsonResponse({"success": True, "equipos": [e.to_dict() for e in qs]})


@require_http_methods(["GET"])
def api_mallas_list(request):
    """Master Screen List — catálogo maestro global de mallas de zaranda."""
    search = request.GET.get('search', '').strip()
    qs = MallaZaranda.objects.all()
    if search:
        qs = qs.filter(Q(codigo__icontains=search) | Q(descripcion__icontains=search))
    return JsonResponse({"success": True, "mallas": [m.to_dict() for m in qs]})


@require_http_methods(["GET"])
def api_productos_activos_list(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return JsonResponse({
        "success": True,
        "productos_activos": [p.to_dict() for p in pozo.productos_activos.select_related('producto').all()],
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_productos_activos_guardar(request, pk):
    """Reemplaza el listado completo de productos activos del pozo."""
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    filas = data.get('productos_activos', [])
    errores = []
    nuevas = []
    for fila in filas:
        fila = dict(fila)
        fila['producto'] = fila.get('producto_id')
        p_form = ProductoActivoPozoForm(fila)
        if not p_form.is_valid():
            errores.append({fila.get('producto_id'): p_form.errors})
            continue
        item = p_form.save(commit=False)
        item.pozo = pozo
        nuevas.append(item)

    if errores:
        return JsonResponse({"success": False, "error": "Hay productos activos inválidos.", "errores_filas": errores}, status=400)

    with transaction.atomic():
        pozo.productos_activos.all().delete()
        ProductoActivoPozo.objects.bulk_create(nuevas)

    return JsonResponse({"success": True, "mensaje": "Productos Activos guardados.", "total": len(nuevas)})


@require_http_methods(["GET"])
def api_equipos_activos_list(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return JsonResponse({
        "success": True,
        "equipos_activos": [e.to_dict() for e in pozo.equipos_activos.select_related('equipo').all()],
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_equipos_activos_guardar(request, pk):
    """Reemplaza el listado completo de equipos activos del pozo."""
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    filas = data.get('equipos_activos', [])
    errores = []
    nuevas = []
    series_vistas = set()
    for fila in filas:
        fila = dict(fila)
        fila['equipo'] = fila.get('equipo_id')
        e_form = EquipoActivoPozoForm(fila)
        if not e_form.is_valid():
            errores.append({fila.get('numero_serie'): e_form.errors})
            continue
        numero_serie = e_form.cleaned_data['numero_serie']
        if numero_serie in series_vistas:
            errores.append({numero_serie: "Número de serie repetido."})
            continue
        series_vistas.add(numero_serie)
        item = e_form.save(commit=False)
        item.pozo = pozo
        nuevas.append(item)

    if errores:
        return JsonResponse({"success": False, "error": "Hay equipos activos inválidos.", "errores_filas": errores}, status=400)

    with transaction.atomic():
        pozo.equipos_activos.all().delete()
        EquipoActivoPozo.objects.bulk_create(nuevas)

    return JsonResponse({"success": True, "mensaje": "Equipos Activos guardados.", "total": len(nuevas)})


@require_http_methods(["GET"])
def api_mallas_activas_list(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return JsonResponse({
        "success": True,
        "mallas_activas": [m.to_dict() for m in pozo.mallas_activas.select_related('malla').all()],
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_mallas_activas_guardar(request, pk):
    """Reemplaza el listado completo de mallas activas del pozo."""
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    filas = data.get('mallas_activas', [])
    errores = []
    nuevas = []
    mallas_vistas = set()
    for fila in filas:
        fila = dict(fila)
        fila['malla'] = fila.get('malla_id')
        m_form = MallaActivaPozoForm(fila)
        if not m_form.is_valid():
            errores.append({fila.get('malla_id'): m_form.errors})
            continue
        malla_id = m_form.cleaned_data['malla'].id
        if malla_id in mallas_vistas:
            errores.append({malla_id: "Malla repetida."})
            continue
        mallas_vistas.add(malla_id)
        item = m_form.save(commit=False)
        item.pozo = pozo
        nuevas.append(item)

    if errores:
        return JsonResponse({"success": False, "error": "Hay mallas activas inválidas.", "errores_filas": errores}, status=400)

    with transaction.atomic():
        pozo.mallas_activas.all().delete()
        MallaActivaPozo.objects.bulk_create(nuevas)

    return JsonResponse({"success": True, "mensaje": "Mallas Activas guardadas.", "total": len(nuevas)})


# ============================================================
# Catálogos Maestros — Equipos y Mallas de Zaranda
# (pantalla de captura para los ingenieros; sin depender del admin)
# ============================================================

def _version_estaticos(*rutas):
    """
    Versión para invalidar la caché del navegador (?v=...) en CSS y JS.

    Usa la fecha de modificación de los propios archivos: la versión cambia solo cuando
    alguien edita el archivo. Así el navegador descarga la versión nueva apenas cambia
    (el problema que motivó el anti-caché) pero sigue usando su caché el resto del
    tiempo, en vez de descargarlo en cada visita como pasaba con {% now %}.
    """
    marcas = []
    try:
        from django.contrib.staticfiles import finders
        for ruta in rutas:
            encontrado = finders.find(ruta)
            if isinstance(encontrado, (list, tuple)):
                encontrado = encontrado[0] if encontrado else None
            if encontrado:
                marcas.append(int(os.path.getmtime(encontrado)))
    except Exception:
        pass
    return str(max(marcas)) if marcas else "1"


def catalogos_maestros_view(request):
    counts = {
        'equipos': Equipo.objects.count(),
        'mallas': MallaZaranda.objects.count(),
        'propiedades': PropiedadEquipoTipo.objects.count(),
        'benchmark': ParametroBenchmark.objects.count(),
        'componentes': ComponenteSarta.objects.count(),
    }
    version_estaticos = _version_estaticos(
        'operaciones/css/catalogos_maestros.css',
        'operaciones/js/catalogos_maestros.js',
    )
    return render(request, 'operaciones/catalogos_maestros.html', {
        'counts': counts,
        'version_estaticos': version_estaticos,
    })


def _leer_posiciones_malla(data, actual=0):
    """Posiciones de malla de un equipo (0 a 12). Devuelve (valor, error)."""
    valor = data.get('posiciones_malla', actual)
    if valor in (None, ''):
        return 0, None
    try:
        valor = int(str(valor).strip())
    except (TypeError, ValueError):
        return actual, "Las posiciones de malla deben ser un número entero."
    if valor < 0 or valor > Equipo.POSICIONES_MALLA_MAX:
        return actual, f"Las posiciones de malla van de 0 a {Equipo.POSICIONES_MALLA_MAX}."
    return valor, None


@csrf_exempt
@require_http_methods(["POST"])
def api_equipo_create(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    codigo = str(data.get('codigo', '')).strip()
    nombre = str(data.get('nombre', '')).strip()
    tipo_equipo = str(data.get('tipo_equipo', '')).strip()

    errores = {}
    if not codigo:
        errores['codigo'] = "El código del equipo es obligatorio."
    elif Equipo.objects.filter(codigo__iexact=codigo).exists():
        errores['codigo'] = f"Ya existe un equipo con el código '{codigo}'."
    if not nombre:
        errores['nombre'] = "El nombre oficial es obligatorio."
    if tipo_equipo not in dict(Equipo.TIPO_EQUIPO_CHOICES):
        errores['tipo_equipo'] = "Selecciona un tipo de equipo válido."
    posiciones_malla, error_pos = _leer_posiciones_malla(data)
    if error_pos:
        errores['posiciones_malla'] = error_pos

    if errores:
        return JsonResponse({"success": False, "errores": errores, "error": next(iter(errores.values()))}, status=400)

    equipo = Equipo.objects.create(
        codigo=codigo, nombre=nombre, tipo_equipo=tipo_equipo, posiciones_malla=posiciones_malla
    )
    return JsonResponse({
        "success": True, "mensaje": f"Equipo '{equipo.codigo}' creado.",
        "equipo": equipo.to_dict()
    }, status=201)


@csrf_exempt
@require_http_methods(["PUT", "POST"])
def api_equipo_update(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    codigo = str(data.get('codigo', equipo.codigo)).strip()
    nombre = str(data.get('nombre', equipo.nombre)).strip()
    tipo_equipo = str(data.get('tipo_equipo', equipo.tipo_equipo)).strip()

    errores = {}
    if not codigo:
        errores['codigo'] = "El código del equipo es obligatorio."
    elif Equipo.objects.filter(codigo__iexact=codigo).exclude(pk=equipo.pk).exists():
        errores['codigo'] = f"Ya existe otro equipo con el código '{codigo}'."
    if not nombre:
        errores['nombre'] = "El nombre oficial es obligatorio."
    if tipo_equipo not in dict(Equipo.TIPO_EQUIPO_CHOICES):
        errores['tipo_equipo'] = "Selecciona un tipo de equipo válido."
    posiciones_malla, error_pos = _leer_posiciones_malla(data, equipo.posiciones_malla)
    if error_pos:
        errores['posiciones_malla'] = error_pos

    if errores:
        return JsonResponse({"success": False, "errores": errores, "error": next(iter(errores.values()))}, status=400)

    equipo.codigo = codigo
    equipo.nombre = nombre
    equipo.tipo_equipo = tipo_equipo
    equipo.posiciones_malla = posiciones_malla
    equipo.save()
    return JsonResponse({
        "success": True, "mensaje": f"Equipo '{equipo.codigo}' actualizado.",
        "equipo": equipo.to_dict()
    })


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def api_equipo_delete(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    codigo = equipo.codigo
    try:
        equipo.delete()
    except ProtectedError:
        return JsonResponse({
            "success": False,
            "error": f"No se puede eliminar el equipo '{codigo}' porque ya está en uso en la lista activa de uno o más pozos."
        }, status=400)
    return JsonResponse({"success": True, "mensaje": f"Equipo '{codigo}' eliminado."})


@csrf_exempt
@require_http_methods(["POST"])
def api_malla_create(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    codigo = str(data.get('codigo', '')).strip()
    descripcion = str(data.get('descripcion', '')).strip()

    errores = {}
    if not codigo:
        errores['codigo'] = "El código de la malla es obligatorio."
    elif MallaZaranda.objects.filter(codigo__iexact=codigo).exists():
        errores['codigo'] = f"Ya existe una malla con el código '{codigo}'."
    if not descripcion:
        errores['descripcion'] = "La descripción es obligatoria."
    try:
        mesh_size = int(data.get('mesh_size', 0))
        if mesh_size <= 0:
            errores['mesh_size'] = "El tamaño de malla (mesh) debe ser mayor a 0."
    except Exception:
        errores['mesh_size'] = "El tamaño de malla (mesh) debe ser un número válido."

    if errores:
        return JsonResponse({"success": False, "errores": errores, "error": next(iter(errores.values()))}, status=400)

    malla = MallaZaranda.objects.create(codigo=codigo, descripcion=descripcion, mesh_size=mesh_size)
    return JsonResponse({
        "success": True, "mensaje": f"Malla '{malla.codigo}' creada.",
        "malla": malla.to_dict()
    }, status=201)


@csrf_exempt
@require_http_methods(["PUT", "POST"])
def api_malla_update(request, pk):
    malla = get_object_or_404(MallaZaranda, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    codigo = str(data.get('codigo', malla.codigo)).strip()
    descripcion = str(data.get('descripcion', malla.descripcion)).strip()

    errores = {}
    if not codigo:
        errores['codigo'] = "El código de la malla es obligatorio."
    elif MallaZaranda.objects.filter(codigo__iexact=codigo).exclude(pk=malla.pk).exists():
        errores['codigo'] = f"Ya existe otra malla con el código '{codigo}'."
    if not descripcion:
        errores['descripcion'] = "La descripción es obligatoria."
    try:
        mesh_size = int(data.get('mesh_size', malla.mesh_size))
        if mesh_size <= 0:
            errores['mesh_size'] = "El tamaño de malla (mesh) debe ser mayor a 0."
    except Exception:
        errores['mesh_size'] = "El tamaño de malla (mesh) debe ser un número válido."

    if errores:
        return JsonResponse({"success": False, "errores": errores, "error": next(iter(errores.values()))}, status=400)

    malla.codigo = codigo
    malla.descripcion = descripcion
    malla.mesh_size = mesh_size
    malla.save()
    return JsonResponse({
        "success": True, "mensaje": f"Malla '{malla.codigo}' actualizada.",
        "malla": malla.to_dict()
    })


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def api_malla_delete(request, pk):
    malla = get_object_or_404(MallaZaranda, pk=pk)
    codigo = malla.codigo
    try:
        malla.delete()
    except ProtectedError:
        return JsonResponse({
            "success": False,
            "error": f"No se puede eliminar la malla '{codigo}' porque ya está en uso en la lista activa de uno o más pozos."
        }, status=400)
    return JsonResponse({"success": True, "mensaje": f"Malla '{codigo}' eliminada."})


# ============================================================
# Catálogos Maestros — Propiedades de Equipo y Parámetros de Benchmark
# ============================================================

@require_http_methods(["GET"])
def api_propiedades_equipo_list(request):
    """Catálogo maestro global (editable) de propiedades por Tipo de Equipo."""
    search = request.GET.get('search', '').strip()
    tipo_equipo = request.GET.get('tipo_equipo', '').strip()
    qs = PropiedadEquipoTipo.objects.all()
    if search:
        qs = qs.filter(descripcion__icontains=search)
    if tipo_equipo:
        qs = qs.filter(tipo_equipo=tipo_equipo)
    return JsonResponse({"success": True, "propiedades": [p.to_dict() for p in qs]})


@csrf_exempt
@require_http_methods(["POST"])
def api_propiedad_equipo_create(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    form = PropiedadEquipoTipoForm(data)
    if not form.is_valid():
        primer_error = next(iter(form.errors.values()))[0]
        return JsonResponse({"success": False, "errores": form.errors, "error": primer_error}, status=400)

    propiedad = form.save()
    return JsonResponse({
        "success": True, "mensaje": f"Propiedad '{propiedad.descripcion}' creada.",
        "propiedad": propiedad.to_dict()
    }, status=201)


@csrf_exempt
@require_http_methods(["POST", "PUT"])
def api_propiedad_equipo_update(request, pk):
    propiedad = get_object_or_404(PropiedadEquipoTipo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    form = PropiedadEquipoTipoForm(data, instance=propiedad)
    if not form.is_valid():
        primer_error = next(iter(form.errors.values()))[0]
        return JsonResponse({"success": False, "errores": form.errors, "error": primer_error}, status=400)

    propiedad = form.save()
    return JsonResponse({
        "success": True, "mensaje": f"Propiedad '{propiedad.descripcion}' actualizada.",
        "propiedad": propiedad.to_dict()
    })


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def api_propiedad_equipo_delete(request, pk):
    propiedad = get_object_or_404(PropiedadEquipoTipo, pk=pk)
    descripcion = propiedad.descripcion
    try:
        propiedad.delete()
    except ProtectedError:
        return JsonResponse({
            "success": False,
            "error": f"No se puede eliminar '{descripcion}' porque ya está seleccionada en uno o más pozos."
        }, status=400)
    return JsonResponse({"success": True, "mensaje": f"Propiedad '{descripcion}' eliminada."})


@require_http_methods(["GET"])
def api_parametros_benchmark_list(request):
    """Catálogo maestro global (editable) de parámetros de Benchmark."""
    search = request.GET.get('search', '').strip()
    grupo = request.GET.get('grupo', '').strip()
    qs = ParametroBenchmark.objects.all()
    if search:
        qs = qs.filter(descripcion__icontains=search)
    if grupo:
        qs = qs.filter(grupo=grupo)
    return JsonResponse({"success": True, "parametros": [p.to_dict() for p in qs]})


@csrf_exempt
@require_http_methods(["POST"])
def api_parametro_benchmark_create(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    form = ParametroBenchmarkForm(data)
    if not form.is_valid():
        primer_error = next(iter(form.errors.values()))[0]
        return JsonResponse({"success": False, "errores": form.errors, "error": primer_error}, status=400)

    parametro = form.save()
    return JsonResponse({
        "success": True, "mensaje": f"Parámetro '{parametro.descripcion}' creado.",
        "parametro": parametro.to_dict()
    }, status=201)


@csrf_exempt
@require_http_methods(["POST", "PUT"])
def api_parametro_benchmark_update(request, pk):
    parametro = get_object_or_404(ParametroBenchmark, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    form = ParametroBenchmarkForm(data, instance=parametro)
    if not form.is_valid():
        primer_error = next(iter(form.errors.values()))[0]
        return JsonResponse({"success": False, "errores": form.errors, "error": primer_error}, status=400)

    parametro = form.save()
    return JsonResponse({
        "success": True, "mensaje": f"Parámetro '{parametro.descripcion}' actualizado.",
        "parametro": parametro.to_dict()
    })


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def api_parametro_benchmark_delete(request, pk):
    parametro = get_object_or_404(ParametroBenchmark, pk=pk)
    descripcion = parametro.descripcion
    try:
        parametro.delete()
    except ProtectedError:
        return JsonResponse({
            "success": False,
            "error": f"No se puede eliminar '{descripcion}' porque ya está en uso en uno o más pozos."
        }, status=400)
    return JsonResponse({"success": True, "mensaje": f"Parámetro '{descripcion}' eliminado."})


# ============================================================
# Equipment Properties Setup
# ============================================================

def equipment_properties_setup_view(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return render(request, 'operaciones/pozos/equipment_properties_setup.html', {'pozo': pozo})


@require_http_methods(["GET"])
def api_equipment_properties_detail(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)

    tipos_activos = list(
        Equipo.objects.filter(activos_en_pozos__pozo=pozo)
        .values_list('tipo_equipo', flat=True).distinct()
    )

    if not tipos_activos:
        return JsonResponse({
            "success": True, "sin_equipo_activo": True, "tipos": [],
        })

    tipos_dict = dict(Equipo.TIPO_EQUIPO_CHOICES)
    seleccionadas_ids = set(
        pozo.propiedades_equipo_seleccionadas.values_list('propiedad_id', flat=True)
    )

    tipos = []
    for tipo_equipo in tipos_activos:
        propiedades = PropiedadEquipoTipo.objects.filter(tipo_equipo=tipo_equipo)
        extras = pozo.propiedades_equipo_extra.filter(tipo_equipo=tipo_equipo)
        tipos.append({
            "tipo_equipo": tipo_equipo,
            "tipo_equipo_display": tipos_dict.get(tipo_equipo, tipo_equipo),
            "propiedades": [
                dict(p.to_dict(), seleccionada=(p.id in seleccionadas_ids)) for p in propiedades
            ],
            "extras": [e.to_dict() for e in extras],
        })

    centrifuga_config = None
    if 'CENTRIFUGA' in tipos_activos:
        cfg, _ = CentrifugaUnidadConfig.objects.get_or_create(pozo=pozo)
        centrifuga_config = cfg.to_dict()

    return JsonResponse({
        "success": True, "sin_equipo_activo": False,
        "tipos": tipos, "centrifuga_config": centrifuga_config,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_equipment_properties_guardar(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    propiedades_seleccionadas = data.get('propiedades_seleccionadas', [])
    extras = data.get('extras', [])
    centrifuga_config = data.get('centrifuga_config')

    nuevas_seleccionadas = []
    for fila in propiedades_seleccionadas:
        propiedad_id = fila.get('propiedad_id')
        tipo_equipo = fila.get('tipo_equipo', '')
        if not propiedad_id or tipo_equipo not in dict(Equipo.TIPO_EQUIPO_CHOICES):
            continue
        nuevas_seleccionadas.append(EquipoPropiedadSeleccionada(
            pozo=pozo, tipo_equipo=tipo_equipo, propiedad_id=propiedad_id
        ))

    nuevas_extras = []
    errores = []
    for fila in extras:
        descripcion = str(fila.get('descripcion', '')).strip()
        tipo_equipo = fila.get('tipo_equipo', '')
        if not descripcion:
            continue
        if tipo_equipo not in dict(Equipo.TIPO_EQUIPO_CHOICES):
            errores.append({"tipo_equipo": "Tipo de equipo inválido en propiedad extra."})
            continue
        nuevas_extras.append(EquipoPropiedadExtra(
            pozo=pozo, tipo_equipo=tipo_equipo,
            descripcion=descripcion, unidad=str(fila.get('unidad', '')).strip()
        ))

    if errores:
        return JsonResponse({"success": False, "error": "Hay propiedades extra inválidas.", "errores_filas": errores}, status=400)

    with transaction.atomic():
        pozo.propiedades_equipo_seleccionadas.all().delete()
        EquipoPropiedadSeleccionada.objects.bulk_create(nuevas_seleccionadas)
        pozo.propiedades_equipo_extra.all().delete()
        EquipoPropiedadExtra.objects.bulk_create(nuevas_extras)

        if centrifuga_config:
            cfg, _ = CentrifugaUnidadConfig.objects.get_or_create(pozo=pozo)
            form = CentrifugaUnidadConfigForm(centrifuga_config, instance=cfg)
            if form.is_valid():
                form.save()

    return JsonResponse({"success": True, "mensaje": "Configuración de Propiedades de Equipo guardada."})


# ============================================================
# Benchmark Setup
# ============================================================

def benchmark_setup_view(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    return render(request, 'operaciones/pozos/benchmark_setup.html', {'pozo': pozo})


@require_http_methods(["GET"])
def api_benchmark_definiciones_detail(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)
    search = request.GET.get('search', '').strip()
    grupo = request.GET.get('grupo', '').strip()

    qs = ParametroBenchmark.objects.all()
    if search:
        qs = qs.filter(descripcion__icontains=search)
    if grupo:
        qs = qs.filter(grupo=grupo)

    seleccionados_ids = set(pozo.benchmarks_seleccionados.values_list('parametro_id', flat=True))
    grupos = list(ParametroBenchmark.objects.order_by('grupo').values_list('grupo', flat=True).distinct())

    return JsonResponse({
        "success": True,
        "grupos": grupos,
        "parametros": [dict(p.to_dict(), seleccionado=(p.id in seleccionados_ids)) for p in qs],
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_benchmark_definiciones_guardar(request, pk):
    """Reemplaza el listado completo de parámetros de benchmark elegidos para el pozo."""
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    parametro_ids = data.get('parametro_ids', [])
    nuevas = [BenchmarkSeleccionado(pozo=pozo, parametro_id=pid) for pid in parametro_ids]

    with transaction.atomic():
        # Al quitar un parámetro también se eliminan sus objetivos ya capturados.
        ids_actuales = set(pozo.benchmarks_seleccionados.values_list('parametro_id', flat=True))
        ids_nuevos = set(parametro_ids)
        ids_removidos = ids_actuales - ids_nuevos
        if ids_removidos:
            pozo.benchmark_targets.filter(parametro_id__in=ids_removidos).delete()
        pozo.benchmarks_seleccionados.all().delete()
        BenchmarkSeleccionado.objects.bulk_create(nuevas)

    return JsonResponse({"success": True, "mensaje": "Definiciones de Benchmark guardadas.", "total": len(nuevas)})


@require_http_methods(["GET"])
def api_benchmark_targets_detail(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)

    parametros = ParametroBenchmark.objects.filter(seleccionados_en_pozos__pozo=pozo).order_by('grupo', 'descripcion')
    intervalos = [
        {"id": i.id, "numero_intervalo": i.numero_intervalo, "tipo": i.tipo}
        for i in pozo.intervalos_revestimiento.all()
    ]

    targets = {}
    for t in pozo.benchmark_targets.all():
        clave = f"{t.parametro_id}:{t.intervalo_id or 'whole'}:{t.min_max}"
        targets[clave] = t.valor

    return JsonResponse({
        "success": True,
        "parametros": [p.to_dict() for p in parametros],
        "intervalos": intervalos,
        "targets": targets,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_benchmark_targets_guardar(request, pk):
    """Reemplaza el listado completo de objetivos (Target Entry) del pozo."""
    pozo = get_object_or_404(Pozo, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    filas = data.get('targets', [])
    nuevas = []
    for fila in filas:
        valor = str(fila.get('valor', '')).strip()
        if not valor:
            continue
        nuevas.append(BenchmarkTarget(
            pozo=pozo,
            parametro_id=fila.get('parametro_id'),
            intervalo_id=fila.get('intervalo_id') or None,
            min_max=fila.get('min_max', 'VALOR'),
            valor=valor,
        ))

    with transaction.atomic():
        pozo.benchmark_targets.all().delete()
        BenchmarkTarget.objects.bulk_create(nuevas)

    return JsonResponse({"success": True, "mensaje": "Objetivos de Benchmark guardados.", "total": len(nuevas)})


# ============================================================
# Catálogo Maestro — Componentes de Sarta de Perforación
# ============================================================

def _parse_decimal_opcional(valor, campo, errores, obligatorio=False, minimo=None):
    """Convierte un valor a Decimal validando; devuelve None si viene vacío."""
    if valor in (None, '', 'null'):
        if obligatorio:
            errores[campo] = "Este campo es obligatorio."
        return None
    try:
        numero = Decimal(str(valor))
    except Exception:
        errores[campo] = "Debe ser un número válido."
        return None
    if minimo is not None and numero < minimo:
        errores[campo] = f"Debe ser mayor o igual a {minimo}."
        return None
    return numero


def _validar_componente_sarta(data, instancia=None):
    """Valida y normaliza el payload de un componente de sarta."""
    errores = {}

    codigo = str(data.get('codigo', instancia.codigo if instancia else '')).strip()
    descripcion = str(data.get('descripcion', instancia.descripcion if instancia else '')).strip()
    tipo = str(data.get('tipo', instancia.tipo if instancia else 'DRILL_PIPE')).strip()

    if not codigo:
        errores['codigo'] = "El código del componente es obligatorio."
    else:
        qs = ComponenteSarta.objects.filter(codigo__iexact=codigo)
        if instancia:
            qs = qs.exclude(pk=instancia.pk)
        if qs.exists():
            errores['codigo'] = f"Ya existe un componente con el código '{codigo}'."

    if not descripcion:
        errores['descripcion'] = "La descripción es obligatoria."

    tipos_validos = [t[0] for t in ComponenteSarta.TIPO_CHOICES]
    if tipo not in tipos_validos:
        errores['tipo'] = "Tipo de componente no válido."

    od = _parse_decimal_opcional(data.get('od_in'), 'od_in', errores, obligatorio=True, minimo=0)
    diam_int = _parse_decimal_opcional(data.get('id_in'), 'id_in', errores, minimo=0)
    if diam_int is None and 'id_in' not in errores:
        diam_int = Decimal('0')

    tj_od = _parse_decimal_opcional(data.get('tool_joint_od_in'), 'tool_joint_od_in', errores, minimo=0)
    tj_id = _parse_decimal_opcional(data.get('tool_joint_id_in'), 'tool_joint_id_in', errores, minimo=0)
    tj_len = _parse_decimal_opcional(data.get('tool_joint_length_in'), 'tool_joint_length_in', errores, minimo=0)
    largo_tramo = _parse_decimal_opcional(data.get('largo_tramo_ft'), 'largo_tramo_ft', errores, minimo=0)
    if largo_tramo is None and 'largo_tramo_ft' not in errores:
        largo_tramo = Decimal('31')

    if od is not None and diam_int is not None and diam_int >= od and od > 0:
        errores['id_in'] = "El diámetro interno debe ser menor que el externo."

    if tj_len and tj_len > 0 and (not largo_tramo or largo_tramo <= 0):
        errores['largo_tramo_ft'] = "Para ponderar la junta se necesita el largo del tramo."

    return {
        'codigo': codigo,
        'descripcion': descripcion,
        'tipo': tipo,
        'od_in': od,
        'id_in': diam_int,
        'tool_joint_od_in': tj_od,
        'tool_joint_id_in': tj_id,
        'tool_joint_length_in': tj_len,
        'largo_tramo_ft': largo_tramo,
    }, errores


@require_http_methods(["GET"])
def api_componentes_sarta_list(request):
    """Catálogo maestro global de componentes de sarta de perforación."""
    search = request.GET.get('search', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    qs = ComponenteSarta.objects.all()
    if search:
        qs = qs.filter(Q(codigo__icontains=search) | Q(descripcion__icontains=search))
    if tipo:
        qs = qs.filter(tipo=tipo)
    return JsonResponse({
        "success": True,
        "componentes": [c.to_dict() for c in qs],
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_componente_sarta_create(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    valores, errores = _validar_componente_sarta(data)
    if errores:
        return JsonResponse(
            {"success": False, "errores": errores, "error": next(iter(errores.values()))}, status=400
        )

    componente = ComponenteSarta.objects.create(**valores)
    return JsonResponse({
        "success": True,
        "mensaje": f"Componente '{componente.codigo}' creado.",
        "componente": componente.to_dict(),
    }, status=201)


@csrf_exempt
@require_http_methods(["PUT", "POST"])
def api_componente_sarta_update(request, pk):
    componente = get_object_or_404(ComponenteSarta, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"success": False, "error": "Datos JSON inválidos."}, status=400)

    valores, errores = _validar_componente_sarta(data, instancia=componente)
    if errores:
        return JsonResponse(
            {"success": False, "errores": errores, "error": next(iter(errores.values()))}, status=400
        )

    for campo, valor in valores.items():
        setattr(componente, campo, valor)
    componente.save()
    return JsonResponse({
        "success": True,
        "mensaje": f"Componente '{componente.codigo}' actualizado.",
        "componente": componente.to_dict(),
    })


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def api_componente_sarta_delete(request, pk):
    componente = get_object_or_404(ComponenteSarta, pk=pk)
    codigo = componente.codigo
    try:
        componente.delete()
    except ProtectedError:
        return JsonResponse({
            "success": False,
            "error": f"No se puede eliminar el componente '{codigo}' porque ya está en uso en la sarta de uno o más reportes diarios."
        }, status=400)
    return JsonResponse({"success": True, "mensaje": f"Componente '{codigo}' eliminado."})
