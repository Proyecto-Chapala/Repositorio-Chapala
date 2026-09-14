import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Producto


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
    producto.delete()

    return JsonResponse({
        "success": True,
        "mensaje": f"Producto '{codigo}' eliminado satisfactoriamente."
    })
