"""
================================================================================
CONTROLADOR DE VISTAS Y APIS - APP 'REPORTES' (ESQUEMA ONE-TRAX)
================================================================================
Interfaz web para el núcleo estructural del sistema (Pozo, SistemaFluido,
Intervalo, TuberiaInstalada, CierreVolumetrico, Producto, ReporteDiario,
matriz de propiedades selectivas y movimientos de inventario/uso).

Deliberadamente NO incluye la geometría interactiva del pozo (queda para el
final, según la estrategia de desarrollo del proyecto) ni un módulo de
Equipos/Comentarios (esos modelos aún no existen).

Sigue el mismo patrón que `mychapala/views.py`: vistas de función,
`@csrf_exempt` + `@require_http_methods` en cada endpoint JSON,
`JsonResponse({"success": bool, ...})`, y serialización vía `to_dict()` en
cada modelo. Así la nueva app se ve y se comporta igual que la ya conocida.
================================================================================
"""

import json
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .models import (
    CierreVolumetrico,
    Comentario,
    Equipo,
    Intervalo,
    InventarioItem,
    MuestraFluido,
    Pozo,
    Producto,
    PropiedadCatalogo,
    PropiedadSistema,
    PropiedadValor,
    ReporteDiario,
    SistemaFluido,
    TuberiaInstalada,
    UsoEquipo,
    UsoMaterial,
)


# ==============================================================================
# UTILIDADES COMUNES
# ==============================================================================

def _parse_body(request):
    """Decodifica el body JSON de la petición. Devuelve un dict vacío si viene
    vacío, para que los .get() de más abajo no truenen."""
    if not request.body:
        return {}
    return json.loads(request.body.decode("utf-8"))


def _error(mensaje, status=400):
    return JsonResponse({"success": False, "error": mensaje}, status=status)


def _decimal(valor, campo):
    """Convierte a Decimal validando que no venga vacío/roto. Lanza ValueError
    con el nombre del campo para poder devolver un mensaje claro al frontend."""
    if valor in (None, ""):
        raise ValueError(f"{campo} es obligatorio.")
    try:
        return Decimal(str(valor))
    except InvalidOperation:
        raise ValueError(f"{campo} debe ser un número válido.")


# ==============================================================================
# VISTA PRINCIPAL (SPA)
# ==============================================================================

@ensure_csrf_cookie
def index(request):
    """Interfaz modular: cada sección (Pozos, Sistemas de Fluido, Intervalos,
    Productos, Reportes Diarios con su matriz de propiedades e inventario) es
    una pestaña independiente que consume su propia porción de la API."""
    return render(request, "reportes/index.html")


# ==============================================================================
# 1. POZOS
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_pozos(request):
    if request.method == "GET":
        pozos = Pozo.objects.all()
        return JsonResponse({"success": True, "pozos": [p.to_dict() for p in pozos]})

    try:
        body = _parse_body(request)
        nombre = body.get("nombre", "").strip()
        operador = body.get("operador", "").strip()
        ubicacion = body.get("ubicacion", "").strip()
        if not nombre:
            return _error("El nombre del pozo es obligatorio.")
        if not operador:
            return _error("El operador es obligatorio.")

        pozo = Pozo.objects.create(
            nombre=nombre,
            operador=operador,
            ubicacion=ubicacion,
            campo_area=body.get("campo_area", "").strip(),
            fecha_spud=body.get("fecha_spud") or None,
        )
        return JsonResponse({"success": True, "pozo": pozo.to_dict()}, status=201)
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except Exception as exc:  # noqa: BLE001 — respuesta homogénea hacia el frontend
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def api_pozo_detalle(request, pk):
    pozo = get_object_or_404(Pozo, pk=pk)

    if request.method == "GET":
        return JsonResponse({"success": True, "pozo": pozo.to_dict()})

    if request.method == "DELETE":
        pozo.delete()
        return JsonResponse({"success": True})

    try:
        body = _parse_body(request)
        for campo in ("nombre", "operador", "ubicacion", "campo_area"):
            if campo in body:
                setattr(pozo, campo, body[campo].strip())
        if "fecha_spud" in body:
            pozo.fecha_spud = body["fecha_spud"] or None
        pozo.full_clean()
        pozo.save()
        return JsonResponse({"success": True, "pozo": pozo.to_dict()})
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


# ==============================================================================
# 2. SISTEMAS DE FLUIDO ("gama de fluidos" — catálogo editable)
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_sistemas_fluido(request):
    if request.method == "GET":
        sistemas = SistemaFluido.objects.all()
        return JsonResponse({"success": True, "sistemas": [s.to_dict() for s in sistemas]})

    try:
        body = _parse_body(request)
        nombre = body.get("nombre", "").strip()
        categoria = body.get("categoria", "").strip()
        if not nombre:
            return _error("El nombre del sistema de fluido es obligatorio.")
        if categoria not in SistemaFluido.Categoria.values:
            return _error(f"Categoría inválida: {categoria}")

        sistema = SistemaFluido.objects.create(
            nombre=nombre,
            categoria=categoria,
            descripcion=body.get("descripcion", "").strip(),
        )
        return JsonResponse({"success": True, "sistema": sistema.to_dict()}, status=201)
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def api_sistema_fluido_detalle(request, pk):
    sistema = get_object_or_404(SistemaFluido, pk=pk)

    if request.method == "GET":
        return JsonResponse({"success": True, "sistema": sistema.to_dict()})

    if request.method == "DELETE":
        sistema.delete()
        return JsonResponse({"success": True})

    try:
        body = _parse_body(request)
        if "nombre" in body:
            sistema.nombre = body["nombre"].strip()
        if "categoria" in body:
            if body["categoria"] not in SistemaFluido.Categoria.values:
                return _error(f"Categoría inválida: {body['categoria']}")
            sistema.categoria = body["categoria"]
        if "descripcion" in body:
            sistema.descripcion = body["descripcion"].strip()
        sistema.full_clean()
        sistema.save()
        return JsonResponse({"success": True, "sistema": sistema.to_dict()})
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


# ==============================================================================
# 3. INTERVALOS (+ TUBERÍA INSTALADA + CIERRE VOLUMÉTRICO)
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_intervalos(request):
    if request.method == "GET":
        intervalos = Intervalo.objects.select_related("pozo", "sistema_fluido")
        pozo_id = request.GET.get("pozo")
        if pozo_id:
            intervalos = intervalos.filter(pozo_id=pozo_id)
        return JsonResponse({"success": True, "intervalos": [i.to_dict() for i in intervalos]})

    try:
        body = _parse_body(request)
        pozo = get_object_or_404(Pozo, pk=body.get("pozo_id"))
        sistema_fluido = get_object_or_404(SistemaFluido, pk=body.get("sistema_fluido_id"))
        numero = body.get("numero")
        if not numero:
            return _error("El número de intervalo es obligatorio.")

        intervalo = Intervalo(
            pozo=pozo,
            sistema_fluido=sistema_fluido,
            numero=int(numero),
            profundidad_inicial=_decimal(body.get("profundidad_inicial"), "Profundidad inicial"),
            diametro=_decimal(body.get("diametro"), "Diámetro"),
        )
        intervalo.full_clean()
        intervalo.save()
        return JsonResponse({"success": True, "intervalo": intervalo.to_dict()}, status=201)
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def api_intervalo_detalle(request, pk):
    intervalo = get_object_or_404(Intervalo.objects.select_related("pozo", "sistema_fluido"), pk=pk)

    if request.method == "GET":
        return JsonResponse({"success": True, "intervalo": intervalo.to_dict()})

    if request.method == "DELETE":
        if intervalo.esta_cerrado:
            return _error("No se puede eliminar un intervalo cerrado.")
        intervalo.delete()
        return JsonResponse({"success": True})

    if intervalo.esta_cerrado:
        return _error("El intervalo está cerrado: no es editable.")

    try:
        body = _parse_body(request)
        if "numero" in body:
            intervalo.numero = int(body["numero"])
        if "sistema_fluido_id" in body:
            intervalo.sistema_fluido = get_object_or_404(SistemaFluido, pk=body["sistema_fluido_id"])
        if "profundidad_inicial" in body:
            intervalo.profundidad_inicial = _decimal(body["profundidad_inicial"], "Profundidad inicial")
        if "profundidad_final" in body:
            intervalo.profundidad_final = (
                _decimal(body["profundidad_final"], "Profundidad final")
                if body["profundidad_final"] not in (None, "") else None
            )
        if "diametro" in body:
            intervalo.diametro = _decimal(body["diametro"], "Diámetro")
        intervalo.full_clean()
        intervalo.save()
        return JsonResponse({"success": True, "intervalo": intervalo.to_dict()})
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_tuberias(request):
    if request.method == "GET":
        tuberias = TuberiaInstalada.objects.all()
        intervalo_id = request.GET.get("intervalo")
        if intervalo_id:
            tuberias = tuberias.filter(intervalo_id=intervalo_id)
        return JsonResponse({"success": True, "tuberias": [t.to_dict() for t in tuberias]})

    try:
        body = _parse_body(request)
        intervalo = get_object_or_404(Intervalo, pk=body.get("intervalo_id"))
        if intervalo.esta_cerrado:
            return _error("El intervalo está cerrado: no se pueden agregar tramos de tubería.")

        tipo = body.get("tipo", TuberiaInstalada.Tipo.REVESTIDOR)
        if tipo not in TuberiaInstalada.Tipo.values:
            return _error(f"Tipo de tubería inválido: {tipo}")

        tuberia = TuberiaInstalada(
            intervalo=intervalo,
            tipo=tipo,
            longitud=_decimal(body.get("longitud"), "Longitud"),
            diametro_externo=_decimal(body.get("diametro_externo"), "Diámetro externo (OD)"),
            diametro_interno=_decimal(body.get("diametro_interno"), "Diámetro interno (ID)"),
        )
        tuberia.full_clean()
        tuberia.save()
        return JsonResponse({"success": True, "tuberia": tuberia.to_dict()}, status=201)
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["DELETE"])
def api_tuberia_detalle(request, pk):
    tuberia = get_object_or_404(TuberiaInstalada, pk=pk)
    if tuberia.intervalo.esta_cerrado:
        return _error("El intervalo está cerrado: no se puede eliminar este tramo.")
    tuberia.delete()
    return JsonResponse({"success": True})


@csrf_exempt
@require_http_methods(["POST"])
def api_cerrar_intervalo(request, pk):
    """Registra el CierreVolumetrico de un intervalo. Al guardarlo, el modelo
    mismo (CierreVolumetrico.save()) marca el Intervalo como 'cerrado' —
    esta vista solo valida la entrada y delega la regla de negocio al modelo."""
    intervalo = get_object_or_404(Intervalo, pk=pk)
    if intervalo.esta_cerrado:
        return _error("Este intervalo ya está cerrado.")

    try:
        body = _parse_body(request)
        usuario = body.get("usuario", "").strip()
        if not usuario:
            return _error("El usuario que registra el cierre es obligatorio.")

        with transaction.atomic():
            cierre = CierreVolumetrico(
                intervalo=intervalo,
                volumen_final=_decimal(body.get("volumen_final"), "Volumen final"),
                volumen_no_fluido=_decimal(body.get("volumen_no_fluido"), "Volumen no fluido"),
                perdida_left_in_hole=_decimal(body.get("perdida_left_in_hole"), "Pérdida (Left in Hole)"),
                usuario=usuario,
            )
            if "profundidad_final" in body and body["profundidad_final"] not in (None, ""):
                intervalo.profundidad_final = _decimal(body["profundidad_final"], "Profundidad final")
                intervalo.full_clean()
                intervalo.save()
            cierre.full_clean()
            cierre.save()

        intervalo.refresh_from_db()
        return JsonResponse(
            {"success": True, "cierre": cierre.to_dict(), "intervalo": intervalo.to_dict()}, status=201
        )
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


# ==============================================================================
# 4. PRODUCTOS
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_productos(request):
    if request.method == "GET":
        productos = Producto.objects.all()
        query = request.GET.get("q", "").strip()
        if query:
            productos = productos.filter(nombre__icontains=query) | productos.filter(codigo__icontains=query)
        return JsonResponse({"success": True, "productos": [p.to_dict() for p in productos]})

    try:
        body = _parse_body(request)
        nombre = body.get("nombre", "").strip()
        codigo = body.get("codigo", "").strip()
        unidad_medida = body.get("unidad_medida", "").strip().upper()
        tipo_empaque = body.get("tipo_empaque", "").strip().upper()

        if not nombre:
            return _error("El nombre del producto es obligatorio.")
        if not codigo:
            return _error("El código del producto es obligatorio.")
        if unidad_medida not in Producto.UnidadMedida.values:
            return _error(f"Unidad de medida inválida: {unidad_medida}")
        if tipo_empaque not in Producto.TipoEmpaque.values:
            return _error(f"Tipo de empaque inválido: {tipo_empaque}")

        producto = Producto(
            nombre=nombre,
            codigo=codigo,
            cantidad_unitaria=_decimal(body.get("cantidad_unitaria"), "Cantidad unitaria"),
            unidad_medida=unidad_medida,
            tipo_empaque=tipo_empaque,
            precio_unitario=_decimal(body.get("precio_unitario"), "Precio unitario"),
            gravedad_especifica=_decimal(body.get("gravedad_especifica"), "Gravedad específica"),
        )
        producto.full_clean()
        producto.save()
        return JsonResponse({"success": True, "producto": producto.to_dict()}, status=201)
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def api_producto_detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "GET":
        return JsonResponse({"success": True, "producto": producto.to_dict()})

    if request.method == "DELETE":
        producto.delete()
        return JsonResponse({"success": True})

    try:
        body = _parse_body(request)
        if "nombre" in body:
            producto.nombre = body["nombre"].strip()
        if "codigo" in body:
            producto.codigo = body["codigo"].strip()
        if "unidad_medida" in body:
            valor = body["unidad_medida"].strip().upper()
            if valor not in Producto.UnidadMedida.values:
                return _error(f"Unidad de medida inválida: {valor}")
            producto.unidad_medida = valor
        if "tipo_empaque" in body:
            valor = body["tipo_empaque"].strip().upper()
            if valor not in Producto.TipoEmpaque.values:
                return _error(f"Tipo de empaque inválido: {valor}")
            producto.tipo_empaque = valor
        if "cantidad_unitaria" in body:
            producto.cantidad_unitaria = _decimal(body["cantidad_unitaria"], "Cantidad unitaria")
        if "precio_unitario" in body:
            producto.precio_unitario = _decimal(body["precio_unitario"], "Precio unitario")
        if "gravedad_especifica" in body:
            producto.gravedad_especifica = _decimal(body["gravedad_especifica"], "Gravedad específica")
        producto.full_clean()
        producto.save()
        return JsonResponse({"success": True, "producto": producto.to_dict()})
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


# ==============================================================================
# 5. REPORTES DIARIOS
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_reportes_diarios(request):
    if request.method == "GET":
        reportes = ReporteDiario.objects.select_related("intervalo__pozo")
        intervalo_id = request.GET.get("intervalo")
        if intervalo_id:
            reportes = reportes.filter(intervalo_id=intervalo_id)
        return JsonResponse({"success": True, "reportes": [r.to_dict() for r in reportes]})

    try:
        body = _parse_body(request)
        intervalo = get_object_or_404(Intervalo, pk=body.get("intervalo_id"))
        fecha = body.get("fecha", "").strip()
        if not fecha:
            return _error("La fecha del reporte es obligatoria.")

        reporte = ReporteDiario(
            intervalo=intervalo,
            fecha=fecha,
            actividad=body.get("actividad", "").strip(),
            peso_lodo=(
                _decimal(body.get("peso_lodo"), "Peso del lodo")
                if body.get("peso_lodo") not in (None, "") else None
            ),
        )
        reporte.save()
        return JsonResponse({"success": True, "reporte": reporte.to_dict()}, status=201)
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["GET"])
def api_reporte_diario_detalle(request, pk):
    reporte = get_object_or_404(ReporteDiario.objects.select_related("intervalo__pozo"), pk=pk)
    return JsonResponse({"success": True, "reporte": reporte.to_dict()})


# ==============================================================================
# 6. MATRIZ DE PROPIEDADES SELECTIVAS (Misión 4) — CATÁLOGO + MUESTRAS + VALORES
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def api_propiedades_catalogo(request):
    """Devuelve el catálogo maestro. Con ?categoria=<agua|polimerico|aceite|
    sintetico|otro> filtra solo las propiedades habilitadas para esa
    categoría (la matriz PropiedadSistema) — así el frontend arma la lista
    de campos a llenar para el sistema de fluido del intervalo activo."""
    categoria = request.GET.get("categoria", "").strip()
    if categoria:
        ids = PropiedadSistema.objects.filter(categoria_sistema=categoria).values_list("propiedad_id", flat=True)
        propiedades = PropiedadCatalogo.objects.filter(id__in=ids)
    else:
        propiedades = PropiedadCatalogo.objects.all()
    return JsonResponse({"success": True, "propiedades": [p.to_dict() for p in propiedades]})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_muestras(request):
    if request.method == "GET":
        muestras = MuestraFluido.objects.select_related("reporte")
        reporte_id = request.GET.get("reporte")
        if reporte_id:
            muestras = muestras.filter(reporte_id=reporte_id)
        return JsonResponse({"success": True, "muestras": [m.to_dict() for m in muestras]})

    try:
        body = _parse_body(request)
        reporte = get_object_or_404(ReporteDiario, pk=body.get("reporte_id"))
        identificador = body.get("identificador", "").strip()
        if not identificador:
            return _error('El identificador de la muestra es obligatorio (ej. "TK 2 20:00").')

        muestra = MuestraFluido(
            reporte=reporte,
            identificador=identificador,
            orden=int(body.get("orden", 0)),
        )
        muestra.full_clean()
        muestra.save()
        return JsonResponse({"success": True, "muestra": muestra.to_dict()}, status=201)
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["DELETE"])
def api_muestra_detalle(request, pk):
    muestra = get_object_or_404(MuestraFluido, pk=pk)
    if muestra.reporte.intervalo.esta_cerrado:
        return _error("El intervalo está cerrado: no se puede eliminar esta muestra.")
    muestra.delete()
    return JsonResponse({"success": True})


@csrf_exempt
@require_http_methods(["POST"])
def api_guardar_valores_muestra(request, pk):
    """Guarda (crea o actualiza) varios PropiedadValor de una muestra en un
    solo llamado — así el frontend manda todo el formulario de la matriz de
    una vez. Body: {"valores": [{"propiedad_id": "...", "valor": "12.3"}, ...]}
    """
    muestra = get_object_or_404(MuestraFluido, pk=pk)
    if muestra.reporte.intervalo.esta_cerrado:
        return _error("El intervalo está cerrado: no se pueden cargar valores.")

    try:
        body = _parse_body(request)
        entradas = body.get("valores", [])
        guardados = []
        with transaction.atomic():
            for entrada in entradas:
                propiedad_id = entrada.get("propiedad_id")
                valor_raw = entrada.get("valor")
                if valor_raw in (None, ""):
                    continue
                propiedad = get_object_or_404(PropiedadCatalogo, pk=propiedad_id)
                valor_obj, _created = PropiedadValor.objects.update_or_create(
                    muestra=muestra,
                    propiedad=propiedad,
                    defaults={"valor": _decimal(valor_raw, propiedad.nombre)},
                )
                guardados.append(valor_obj.to_dict())
        return JsonResponse({"success": True, "valores": guardados})
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


# ==============================================================================
# 7. INVENTARIO Y USO DE MATERIAL (por reporte diario)
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_inventario_items(request):
    if request.method == "GET":
        items = InventarioItem.objects.select_related("producto")
        reporte_id = request.GET.get("reporte")
        if reporte_id:
            items = items.filter(reporte_id=reporte_id)
        return JsonResponse({"success": True, "items": [i.to_dict() for i in items]})

    try:
        body = _parse_body(request)
        reporte = get_object_or_404(ReporteDiario, pk=body.get("reporte_id"))
        producto = get_object_or_404(Producto, pk=body.get("producto_id"))

        item = InventarioItem(
            reporte=reporte,
            producto=producto,
            cantidad_inicial=_decimal(body.get("cantidad_inicial"), "Cantidad inicial"),
            cantidad_entrada=_decimal(body.get("cantidad_entrada", "0"), "Cantidad de entrada"),
        )
        item.save()
        return JsonResponse({"success": True, "item": item.to_dict()}, status=201)
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_uso_material(request):
    if request.method == "GET":
        usos = UsoMaterial.objects.select_related("producto")
        reporte_id = request.GET.get("reporte")
        if reporte_id:
            usos = usos.filter(reporte_id=reporte_id)
        return JsonResponse({"success": True, "usos": [u.to_dict() for u in usos]})

    try:
        body = _parse_body(request)
        reporte = get_object_or_404(ReporteDiario, pk=body.get("reporte_id"))
        producto = get_object_or_404(Producto, pk=body.get("producto_id"))

        uso = UsoMaterial(
            reporte=reporte,
            producto=producto,
            cantidad_usada=_decimal(body.get("cantidad_usada"), "Cantidad usada"),
        )
        uso.save()

        # El stock (InventarioItem) del mismo reporte/producto depende de la
        # suma de usos — si ya existía, se recalcula para que cantidad_final
        # quede consistente sin que el usuario tenga que volver a guardarlo.
        try:
            item = InventarioItem.objects.get(reporte=reporte, producto=producto)
            item.save()
        except InventarioItem.DoesNotExist:
            pass

        return JsonResponse({"success": True, "uso": uso.to_dict()}, status=201)
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["DELETE"])
def api_eliminar_uso(request, pk):
    uso = get_object_or_404(UsoMaterial, pk=pk)
    if uso.reporte.intervalo.esta_cerrado:
        return _error("El intervalo está cerrado: no se puede eliminar este uso.")
    reporte, producto = uso.reporte, uso.producto
    uso.delete()
    try:
        item = InventarioItem.objects.get(reporte=reporte, producto=producto)
        item.save()
    except InventarioItem.DoesNotExist:
        pass
    return JsonResponse({"success": True})


# ==============================================================================
# 8. EQUIPOS (catálogo + uso por reporte diario)
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_equipos(request):
    if request.method == "GET":
        equipos = Equipo.objects.all()
        query = request.GET.get("q", "").strip()
        if query:
            equipos = equipos.filter(nombre__icontains=query) | equipos.filter(codigo__icontains=query)
        return JsonResponse({"success": True, "equipos": [e.to_dict() for e in equipos]})

    try:
        body = _parse_body(request)
        nombre = body.get("nombre", "").strip()
        codigo = body.get("codigo", "").strip()
        if not nombre:
            return _error("El nombre del equipo es obligatorio.")
        if not codigo:
            return _error("El código del equipo es obligatorio.")

        equipo = Equipo(
            nombre=nombre,
            codigo=codigo,
            costo_diario=_decimal(body.get("costo_diario"), "Costo diario"),
        )
        equipo.full_clean()
        equipo.save()
        return JsonResponse({"success": True, "equipo": equipo.to_dict()}, status=201)
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def api_equipo_detalle(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)

    if request.method == "GET":
        return JsonResponse({"success": True, "equipo": equipo.to_dict()})

    if request.method == "DELETE":
        equipo.delete()
        return JsonResponse({"success": True})

    try:
        body = _parse_body(request)
        if "nombre" in body:
            equipo.nombre = body["nombre"].strip()
        if "codigo" in body:
            equipo.codigo = body["codigo"].strip()
        if "costo_diario" in body:
            equipo.costo_diario = _decimal(body["costo_diario"], "Costo diario")
        equipo.full_clean()
        equipo.save()
        return JsonResponse({"success": True, "equipo": equipo.to_dict()})
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_uso_equipo(request):
    if request.method == "GET":
        usos = UsoEquipo.objects.select_related("equipo")
        reporte_id = request.GET.get("reporte")
        if reporte_id:
            usos = usos.filter(reporte_id=reporte_id)
        return JsonResponse({"success": True, "usos": [u.to_dict() for u in usos]})

    try:
        body = _parse_body(request)
        reporte = get_object_or_404(ReporteDiario, pk=body.get("reporte_id"))
        equipo = get_object_or_404(Equipo, pk=body.get("equipo_id"))

        uso = UsoEquipo(
            reporte=reporte,
            equipo=equipo,
            horas_usadas=_decimal(body.get("horas_usadas"), "Horas usadas"),
        )
        uso.save()
        return JsonResponse({"success": True, "uso": uso.to_dict()}, status=201)
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["DELETE"])
def api_eliminar_uso_equipo(request, pk):
    uso = get_object_or_404(UsoEquipo, pk=pk)
    if uso.reporte.intervalo.esta_cerrado:
        return _error("El intervalo está cerrado: no se puede eliminar este uso de equipo.")
    uso.delete()
    return JsonResponse({"success": True})


# ==============================================================================
# 9. COMENTARIOS (por reporte diario)
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_comentarios(request):
    if request.method == "GET":
        comentarios = Comentario.objects.all()
        reporte_id = request.GET.get("reporte")
        if reporte_id:
            comentarios = comentarios.filter(reporte_id=reporte_id)
        return JsonResponse({"success": True, "comentarios": [c.to_dict() for c in comentarios]})

    try:
        body = _parse_body(request)
        reporte = get_object_or_404(ReporteDiario, pk=body.get("reporte_id"))
        texto = body.get("texto", "").strip()
        if not texto:
            return _error("El comentario no puede estar vacío.")

        comentario = Comentario(
            reporte=reporte,
            texto=texto,
            autor=body.get("autor", "").strip(),
        )
        comentario.save()
        return JsonResponse({"success": True, "comentario": comentario.to_dict()}, status=201)
    except ValidationError as exc:
        return _error("; ".join(exc.messages))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@csrf_exempt
@require_http_methods(["DELETE"])
def api_eliminar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    if comentario.reporte.intervalo.esta_cerrado:
        return _error("El intervalo está cerrado: no se puede eliminar este comentario.")
    comentario.delete()
    return JsonResponse({"success": True})
