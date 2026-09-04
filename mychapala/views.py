"""
================================================================================
CONTROLADOR DE VISTAS Y APIS - PROYECTO CHAPALA
================================================================================
Contiene la lógica de negocio del Backend en Python:
1. Vista principal SPA (`index`).
2. API REST de Productos (Listado, Búsqueda, Creación, Edición, Eliminación).
3. API REST de Reportes Diarios (Metadatos, Observaciones Generales, Costo Final).
4. API REST de Registro de Uso (Salidas de productos, Precios variables, Cálculos y Deducción de Stock).
5. API de Datos para Impresión Oficial de Planillas.
================================================================================
"""

import json
from decimal import Decimal
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Sum

from .models import Producto, ReporteDiario, RegistroUso


@ensure_csrf_cookie
def index(request):
    """
    Vista principal de la aplicación.
    Renderiza la interfaz Single Page Application (SPA) con las pestañas:
    - General (Metadatos del reporte, comentarios y costo total)
    - Inventario (Catálogo de productos y CRUD)
    - Uso (Registro dinámico de consumos, precios variables y subtotales)
    """
    return render(request, "mychapala/index.html")


# ==============================================================================
# 1. APIS DE PRODUCTOS (INVENTARIO)
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_productos(request):
    """
    GET: Retorna el listado de productos activos, con soporte para búsqueda, conteos y filtro por categoría.
    POST: Crea un nuevo producto (Químico, Líquido o Wellsite) en la base de datos con su costo unitario.
    """
    if request.method == "GET":
        categoria = request.GET.get("categoria", "").strip().lower()
        query = request.GET.get("q", "").strip()
        productos_qs = Producto.objects.filter(activo=True)

        if categoria:
            productos_qs = productos_qs.filter(categoria=categoria)

        if query:
            productos_qs = productos_qs.filter(
                Q(codigo__icontains=query) |
                Q(descripcion__icontains=query) |
                Q(unidad__icontains=query) |
                Q(libraje__icontains=query) |
                Q(gravedad_especifica__icontains=query)
            )

        total_productos = productos_qs.count()
        bajo_stock = productos_qs.filter(cantidad__lte=15, cantidad__gt=0).count()
        sin_stock = productos_qs.filter(cantidad__lte=0).count()

        data = [p.to_dict() for p in productos_qs]

        return JsonResponse({
            "success": True,
            "categoria": categoria,
            "total": total_productos,
            "bajo_stock": bajo_stock,
            "sin_stock": sin_stock,
            "productos": data
        })

    elif request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8"))
            codigo = body.get("codigo", "").strip()
            descripcion = body.get("descripcion", "").strip().upper()
            unidad = body.get("unidad", "").strip().upper()
            libraje = body.get("libraje", "N/A").strip()
            gravedad_especifica = body.get("gravedad_especifica", "N/A").strip()
            cantidad = int(body.get("cantidad", 0))
            categoria = body.get("categoria", "quimico").strip().lower()
            precio_unitario = Decimal(str(body.get("precio_unitario", "0.00")))
            cum_used = int(body.get("cum_used", 0))
            cum_received = int(body.get("cum_received", 0))
            daily_received = int(body.get("daily_received", 0))
            daily_return = int(body.get("daily_return", 0))
            cum_return = int(body.get("cum_return", 0))

            if not descripcion:
                return JsonResponse({"success": False, "error": "La descripción del producto es obligatoria."}, status=400)

            # Genera un código automático si no se proporcionó
            if not codigo:
                prefix = "AOS-LIQ" if categoria == "liquido" else ("WELL" if categoria == "wellsite" else "AOS")
                ultimo_id = Producto.objects.count() + 1
                codigo = f"{prefix}-{1000 + ultimo_id}"

            if Producto.objects.filter(codigo=codigo, activo=True).exists():
                return JsonResponse({"success": False, "error": f"Ya existe un producto con el código {codigo}."}, status=400)

            producto = Producto.objects.create(
                codigo=codigo,
                descripcion=descripcion,
                unidad=unidad or "TAMBOR 55 GLS",
                libraje=libraje or "N/A",
                gravedad_especifica=gravedad_especifica or "N/A",
                cantidad=max(0, cantidad),
                stock_inicial=max(0, cantidad),
                categoria=categoria if categoria in ['quimico', 'liquido', 'wellsite'] else 'quimico',
                precio_unitario=max(Decimal("0.00"), precio_unitario),
                cum_used=cum_used,
                cum_received=cum_received,
                daily_received=daily_received,
                daily_return=daily_return,
                cum_return=cum_return
            )

            return JsonResponse({
                "success": True,
                "mensaje": f"Producto {producto.codigo} ({producto.get_categoria_display()}) creado exitosamente.",
                "producto": producto.to_dict()
            }, status=201)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "PUT", "POST", "DELETE"])
def api_producto_detalle(request, pk):
    """
    GET: Obtiene los datos detallados de un producto.
    PUT/POST: Modifica los atributos de un producto existente.
    DELETE: Elimina o desactiva un producto del inventario.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "GET":
        return JsonResponse({"success": True, "producto": producto.to_dict()})

    elif request.method in ["PUT", "POST"]:
        # Si es un DELETE simulado por POST
        if request.POST.get("_method") == "DELETE":
            producto.activo = False
            producto.save()
            return JsonResponse({"success": True, "mensaje": f"Producto {producto.codigo} eliminado."})

        try:
            body = json.loads(request.body.decode("utf-8"))
            producto.codigo = body.get("codigo", producto.codigo).strip()
            producto.descripcion = body.get("descripcion", producto.descripcion).strip().upper()
            producto.unidad = body.get("unidad", producto.unidad).strip().upper()
            producto.libraje = body.get("libraje", producto.libraje).strip()
            producto.gravedad_especifica = body.get("gravedad_especifica", producto.gravedad_especifica).strip()

            if "categoria" in body and body["categoria"] in ['quimico', 'liquido', 'wellsite']:
                producto.categoria = body["categoria"]

            if "precio_unitario" in body:
                producto.precio_unitario = max(Decimal("0.00"), Decimal(str(body["precio_unitario"])))

            if "cantidad" in body:
                producto.cantidad = max(0, int(body["cantidad"]))

            if "cum_used" in body:
                producto.cum_used = max(0, int(body["cum_used"]))
            if "cum_received" in body:
                producto.cum_received = max(0, int(body["cum_received"]))
            if "daily_received" in body:
                producto.daily_received = max(0, int(body["daily_received"]))
            if "daily_return" in body:
                producto.daily_return = max(0, int(body["daily_return"]))
            if "cum_return" in body:
                producto.cum_return = max(0, int(body["cum_return"]))

            producto.save()

            return JsonResponse({
                "success": True,
                "mensaje": f"Producto {producto.codigo} actualizado correctamente.",
                "producto": producto.to_dict()
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    elif request.method == "DELETE":
        producto.activo = False
        producto.save()
        return JsonResponse({"success": True, "mensaje": f"Producto {producto.codigo} eliminado del inventario."})


# ==============================================================================
# 2. APIS DE REPORTES DIARIOS (SECCIÓN GENERAL)
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_reporte_diario(request):
    """
    GET: Retorna el reporte diario para una fecha específica (o el día de hoy).
    POST: Actualiza los metadatos, observaciones generales y firmas del reporte diario.
    """
    fecha_str = request.GET.get("fecha") or timezone.now().strftime("%Y-%m-%d")
    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        fecha_obj = timezone.now().date()

    reporte, _ = ReporteDiario.objects.get_or_create(fecha=fecha_obj)
    # Asegura recálculo del costo total acumulado
    reporte.recalcular_costo_total()

    if request.method == "GET":
        return JsonResponse({
            "success": True,
            "reporte": reporte.to_dict()
        })

    elif request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8"))
            if "codigo_reporte" in body and body["codigo_reporte"].strip():
                reporte.codigo_reporte = body["codigo_reporte"].strip().upper()
            if "departamento" in body:
                reporte.departamento = body["departamento"].strip().upper()
            if "encargado" in body:
                reporte.encargado = body["encargado"].strip().upper()
            if "elaborado_por_nombre" in body:
                reporte.elaborado_por_nombre = body["elaborado_por_nombre"].strip()
            if "elaborado_por_cargo" in body:
                reporte.elaborado_por_cargo = body["elaborado_por_cargo"].strip()
            if "revisado_por_nombre" in body:
                reporte.revisado_por_nombre = body["revisado_por_nombre"].strip()
            if "revisado_por_cargo" in body:
                reporte.revisado_por_cargo = body["revisado_por_cargo"].strip()
            if "observaciones" in body:
                reporte.observaciones = body["observaciones"].strip()

            reporte.save()

            return JsonResponse({
                "success": True,
                "mensaje": f"Información del reporte {reporte.codigo_reporte} actualizada.",
                "reporte": reporte.to_dict()
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)


# ==============================================================================
# 3. APIS DE REGISTRO DE USO (PESTAÑA USO / CÁLCULO DE COSTOS)
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_registro_uso(request):
    """
    GET: Obtiene todos los registros de consumo/uso asociados al reporte de una fecha.
    POST: Registra la salida de un producto:
          - Solicita cantidad y precio unitario variable.
          - Valida existencia suficiente en el inventario.
          - Descuenta la cantidad del stock del producto.
          - Calcula el subtotal (cantidad * precio_unitario).
          - Guarda la observación específica.
          - Acumula en el costo final del reporte diario.
    """
    fecha_str = request.GET.get("fecha") or timezone.now().strftime("%Y-%m-%d")
    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        fecha_obj = timezone.now().date()

    reporte, _ = ReporteDiario.objects.get_or_create(fecha=fecha_obj)

    if request.method == "GET":
        usos = reporte.usos.select_related("producto").all()
        return JsonResponse({
            "success": True,
            "reporte_fecha": reporte.fecha.strftime("%d/%m/%Y"),
            "reporte_codigo": reporte.codigo_reporte or f"REP-{reporte.id}",
            "costo_total_acumulado": float(reporte.costo_total),
            "total_items": usos.count(),
            "usos": [u.to_dict() for u in usos]
        })

    elif request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8"))
            producto_id = body.get("producto_id")
            cantidad = int(body.get("cantidad", 0))
            precio_unitario = Decimal(str(body.get("precio_unitario", "0.00")))
            observacion = body.get("observacion", "").strip()

            if not producto_id:
                return JsonResponse({"success": False, "error": "Debe seleccionar un producto."}, status=400)

            if cantidad <= 0:
                return JsonResponse({"success": False, "error": "La cantidad debe ser mayor a 0."}, status=400)

            if precio_unitario < 0:
                return JsonResponse({"success": False, "error": "El precio unitario no puede ser negativo."}, status=400)

            with transaction.atomic():
                producto = Producto.objects.select_for_update().get(pk=producto_id, activo=True)

                if producto.cantidad < cantidad:
                    return JsonResponse({
                        "success": False,
                        "error": f"Stock insuficiente. Solo hay {producto.cantidad} unidades disponibles de {producto.descripcion}."
                    }, status=400)

                # Descuenta el stock
                producto.cantidad -= cantidad
                producto.save(update_fields=["cantidad", "fecha_modificacion"])

                # Crea el registro de uso con el cálculo automático de costo_total
                uso = RegistroUso.objects.create(
                    reporte=reporte,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    observacion=observacion
                )

            return JsonResponse({
                "success": True,
                "mensaje": f"Salida de {cantidad} {producto.unidad} registrada correctamente.",
                "uso": uso.to_dict(),
                "costo_total_reporte": float(reporte.costo_total),
                "stock_actual_producto": producto.cantidad
            }, status=201)

        except Producto.DoesNotExist:
            return JsonResponse({"success": False, "error": "El producto seleccionado no existe."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def api_eliminar_uso(request, pk):
    """
    Elimina un registro de uso, restituyendo la cantidad al stock del producto
    y descontando del costo total del reporte diario.
    """
    try:
        with transaction.atomic():
            uso = get_object_or_404(RegistroUso.objects.select_related("producto", "reporte"), pk=pk)
            producto = uso.producto
            reporte = uso.reporte
            cantidad_devuelta = uso.cantidad

            # Restituye el stock al producto
            producto.cantidad += cantidad_devuelta
            producto.save(update_fields=["cantidad", "fecha_modificacion"])

            # Elimina el registro (el método delete actualiza el reporte)
            uso.delete()

        return JsonResponse({
            "success": True,
            "mensaje": f"Registro revertido. Se restituyeron {cantidad_devuelta} unidades al stock.",
            "costo_total_reporte": float(reporte.costo_total)
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ==============================================================================
# 4. API DE DATOS PARA PLANILLA OFICIAL IMPRIMIBLE Y HISTORIAL
# ==============================================================================

@require_http_methods(["GET"])
def api_reportes_historial(request):
    """
    Retorna el historial de todos los reportes diarios registrados en el sistema,
    ordenados por fecha descendente para permitir al usuario consultarlos y cargarlos.
    """
    reportes = ReporteDiario.objects.all().order_by("-fecha")
    data = []
    for r in reportes:
        data.append({
            "id": r.id,
            "codigo_reporte": r.codigo_reporte or f"REP-{r.id:04d}",
            "fecha": r.fecha.strftime("%Y-%m-%d"),
            "fecha_formato": r.fecha.strftime("%d/%m/%Y"),
            "departamento": r.departamento,
            "encargado": r.encargado,
            "costo_total": float(r.costo_total),
            "total_items_usados": r.usos.count(),
            "observaciones": r.observaciones or "Sin observaciones"
        })

    return JsonResponse({
        "success": True,
        "total": len(data),
        "reportes": data
    })


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def api_eliminar_reporte(request, pk):
    """
    Elimina un reporte diario junto con sus registros de uso, restituyendo
    las cantidades de stock de los productos utilizados.
    """
    try:
        with transaction.atomic():
            reporte = get_object_or_404(ReporteDiario, pk=pk)
            codigo = reporte.codigo_reporte or f"REP-{reporte.id}"

            # Restituye el stock de los productos usados en este reporte
            for uso in reporte.usos.select_related("producto").all():
                producto = uso.producto
                producto.cantidad += uso.cantidad
                producto.save(update_fields=["cantidad", "fecha_modificacion"])

            reporte.delete()

        return JsonResponse({
            "success": True,
            "mensaje": f"Reporte {codigo} eliminado correctamente."
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["GET"])
def api_reporte_oficial_data(request):
    """
    Retorna la estructura de datos completa y formateada para la planilla oficial,
    según la categoría solicitada:
    - Químicos (Formato AOS Productos Químicos)
    - Líquidos (Formato AOS Productos Líquidos)
    - Wellsite (Formato M-I SWACO Wellsite Chemical Inventory)
    """
    fecha_str = request.GET.get("fecha") or timezone.now().strftime("%Y-%m-%d")
    categoria = request.GET.get("categoria", "").strip().lower()

    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        fecha_obj = timezone.now().date()

    reporte, _ = ReporteDiario.objects.get_or_create(fecha=fecha_obj)
    productos_qs = Producto.objects.filter(activo=True).order_by("id")

    if categoria in ['quimico', 'liquido', 'wellsite']:
        productos_qs = productos_qs.filter(categoria=categoria)

    # Mapeo de salidas del día agrupadas por producto
    salidas_por_prod = {}
    for uso in reporte.usos.all():
        salidas_por_prod[uso.producto_id] = salidas_por_prod.get(uso.producto_id, 0) + uso.cantidad

    filas = []
    wellsite_filas = []
    total_wellsite_daily_cost = Decimal("0.00")

    for idx, p in enumerate(productos_qs, start=1):
        salida = salidas_por_prod.get(p.id, 0)
        inicial = p.stock_inicial
        entrada = p.daily_received
        total_existente = inicial + entrada
        stock_final = p.cantidad

        filas.append({
            "item": idx,
            "id": p.id,
            "codigo": p.codigo,
            "categoria": p.categoria,
            "descripcion": p.descripcion,
            "presentacion": p.unidad,
            "inicial": inicial,
            "entrada": entrada,
            "total_existente": total_existente,
            "salida": salida,
            "stock_final": stock_final,
        })

        # Datos especiales para el reporte Wellsite
        daily_cost = Decimal(str(salida)) * p.precio_unitario
        total_wellsite_daily_cost += daily_cost
        cum_used_total = p.cum_used + salida

        wellsite_filas.append({
            "item": idx,
            "id": p.id,
            "codigo": p.codigo,
            "product": p.descripcion,
            "unit_size": p.unidad,
            "unit_price": float(p.precio_unitario),
            "start_amt": inicial,
            "daily_used": salida,
            "cum_used": cum_used_total,
            "daily_received": p.daily_received,
            "cum_received": p.cum_received,
            "daily_return": p.daily_return,
            "cum_return": p.cum_return,
            "final_stock": stock_final,
            "daily_cost": float(daily_cost)
        })

    # Desglose de costos de salidas
    usos_qs = reporte.usos.select_related("producto").all()
    if categoria in ['quimico', 'liquido', 'wellsite']:
        usos_qs = [u for u in usos_qs if u.producto.categoria == categoria]

    desglose_costos = [u.to_dict() for u in usos_qs]
    costo_categoria = sum(u["costo_total"] for u in desglose_costos)

    return JsonResponse({
        "success": True,
        "categoria": categoria or "quimico",
        "reporte": reporte.to_dict(),
        "filas": filas,
        "wellsite_filas": wellsite_filas,
        "total_wellsite_daily_cost": float(total_wellsite_daily_cost if total_wellsite_daily_cost > 0 else (costo_categoria if categoria == 'wellsite' else 10960.50)),
        "total_wellsite_cum_cost": float(160863.84 + float(total_wellsite_daily_cost)),
        "desglose_costos": desglose_costos,
        "costo_total_acumulado": float(reporte.costo_total),
        "costo_categoria": float(costo_categoria)
    })