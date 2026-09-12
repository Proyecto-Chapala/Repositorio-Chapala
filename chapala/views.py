"""
================================================================================
CONTROLADOR DE VISTAS Y APIS - PANTALLAS FALTANTES (GEOMETRÍA Y VOLUMEN)
PROYECTO CHAPALA / ONE-TRAX
================================================================================
Implementa la lógica de negocio y presentación para:
1. Modelo Geométrico y Capacidades del Hoyo (Geometry Tab)
2. Motor de Contabilidad de Volumen (Volume Accounting Tab)
3. Transacciones Volumétricas (Transaction Buttons)
4. Gestión de Desplazamientos (Displacements Tab)
5. Compendio de Fórmulas y Motor de Cálculo (07_Formulas_Business_Logic.md):
   - Hole Size = Bit Size * (1 + % Washout / 100)
   - Capacidad Total del Hoyo = Annulus + Total DS + Below Bit
   - Volumen Neto de Fluido = Total Hole Volume - Volume Not Fluids
   - Longitud Inversa Drill Pipe = Bit Depth - sum(BHA)
   - Riser Length = Water Depth - Air Gap
   - Régimen de Flujo: AnnRe > 2000 -> Flujo Turbulento, else Laminar
   - % Lodo en Descarga = Mud On Cuttings / (1 + Mud On Cuttings)
   - Distribución de Ripios por Equipo = % Total / Equipos Activos
   - Lodo Perdido en Sólidos = Vol Sólidos * Mud On Cuttings
   - Volumen Sludge = Vol Sólidos + Lodo Perdido
   - Not Accounted = Calc End Volume - Actual End Volume (Regla: == 0.00)
   - Concentración Promedio de Mezcla = (V1*C1 + V2*C2) / (V1 + V2)
   - Costo Diario Equipo = Used Days * Tarifa

Soporta respuesta dual: JSON (API REST / AJAX) y Contexto de Template HTML.
================================================================================
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction

from mychapala.models import (
    Producto,
    ReporteDiario,
    RegistroUso,
    GeometriaHoyo,
    TramoSarta,
    Fosa,
    TransaccionVolumetrica,
    Desplazamiento,
)


# ==============================================================================
# MOTOR DE CÁLCULO Y FÓRMULAS DE NEGOCIO (07_Formulas_Business_Logic.md)
# ==============================================================================

def calcular_hole_size(bit_size, porcentaje_washout=0):
    """
    Hole Size = Bit Size * (1 + % Washout / 100)
    Si Washout es 0, asume hoyo en calibre (gauge hole).
    """
    if bit_size is None:
        return None
    bs = Decimal(str(bit_size))
    wo = Decimal(str(porcentaje_washout or 0))
    factor = Decimal("1.0") + (wo / Decimal("100.0"))
    return (bs * factor).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def calcular_total_hole_volume(volumen_anular, volumen_sarta, volumen_debajo_mecha):
    """
    Total Hole Volume = Annulus + Total DS + Below Bit
    """
    va = Decimal(str(volumen_anular or 0))
    vs = Decimal(str(volumen_sarta or 0))
    vb = Decimal(str(volumen_debajo_mecha or 0))
    return (va + vs + vb).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_fluid_volume(total_hole_volume, volumen_no_fluido=0):
    """
    Fluid Volume = Total Hole Volume - Volume Not Fluids
    """
    thv = Decimal(str(total_hole_volume or 0))
    vnf = Decimal(str(volumen_no_fluido or 0))
    return max(Decimal("0.00"), (thv - vnf).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calcular_longitud_drill_pipe(bit_depth, suma_longitud_bha):
    """
    Cálculo Inverso de Longitud: L_DP = Bit Depth - sum(L_BHA)
    Caso Borde: Si la mecha está en superficie (Bit Depth = 0), arroja valor negativo lógico.
    """
    bd = Decimal(str(bit_depth or 0))
    bha = Decimal(str(suma_longitud_bha or 0))
    return (bd - bha).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_riser_length(water_depth, air_gap):
    """
    Riser Length = Water Depth - Air Gap
    """
    wd = Decimal(str(water_depth or 0))
    ag = Decimal(str(air_gap or 0))
    return max(Decimal("0.00"), (wd - ag).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calcular_regimen_flujo(ann_re):
    """
    Régimen de Flujo:
    Si AnnRe > 2000 -> Flujo Turbulento, else Laminar.
    """
    re = float(ann_re or 0)
    es_turbulento = re > 2000.0
    return {
        "ann_re": re,
        "regimen": "Turbulento" if es_turbulento else "Laminar",
        "es_turbulento": es_turbulento,
    }


def calcular_porcentaje_lodo_descarga(mud_on_cuttings):
    """
    % Lodo = Mud On Cuttings / (1 + Mud On Cuttings) * 100
    Ej: Si Mud On Cuttings = 0.8 -> 0.8 / 1.8 ~= 44.44%
    """
    moc = Decimal(str(mud_on_cuttings or 0))
    if moc <= Decimal("0.00"):
        return Decimal("0.00")
    pct = (moc / (Decimal("1.0") + moc)) * Decimal("100.0")
    return pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_distribucion_solidos(porcentaje_total_removido, equipos_activos):
    """
    % Cuttings Removed (Individual) = % Total Removido / Cantidad de Equipos Activos
    """
    tot = Decimal(str(porcentaje_total_removido or 0))
    eq = int(equipos_activos or 1)
    if eq <= 0:
        return Decimal("0.00")
    return (tot / Decimal(str(eq))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_lodo_perdido_en_solidos(volumen_solidos_removidos, mud_on_cuttings):
    """
    V_lodo_perdido = V_solidos_removidos * Mud On Cuttings
    """
    v_sol = Decimal(str(volumen_solidos_removidos or 0))
    moc = Decimal(str(mud_on_cuttings or 0))
    return (v_sol * moc).quantize(Decimal("0.02"), rounding=ROUND_HALF_UP)


def calcular_volumen_sludge(volumen_solidos_removidos, volumen_lodo_perdido):
    """
    V_sludge = V_solidos_removidos + V_lodo_perdido
    """
    v_sol = Decimal(str(volumen_solidos_removidos or 0))
    v_lp = Decimal(str(volumen_lodo_perdido or 0))
    return (v_sol + v_lp).quantize(Decimal("0.02"), rounding=ROUND_HALF_UP)


def calcular_not_accounted(calc_end_volume, actual_end_volume):
    """
    Not Accounted = Calc End Volume - Actual End Volume
    Regla estricta: debe ser exactamente 0.00 (balance cuadrado).
    """
    calc = Decimal(str(calc_end_volume or 0))
    act = Decimal(str(actual_end_volume or 0))
    diff = (calc - act).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "calc_end_volume": float(calc),
        "actual_end_volume": float(act),
        "not_accounted": float(diff),
        "balance_cuadrado": abs(diff) < Decimal("0.01"),
    }


def calcular_concentracion_mezcla(volumen_destino, concentracion_destino, volumen_transferido, concentracion_origen):
    """
    C_final = (V_destino * C_destino + V_transferido * C_origen) / (V_destino + V_transferido)
    """
    vd = Decimal(str(volumen_destino or 0))
    cd = Decimal(str(concentracion_destino or 0))
    vt = Decimal(str(volumen_transferido or 0))
    co = Decimal(str(concentracion_origen or 0))
    v_total = vd + vt
    if v_total <= Decimal("0.00"):
        return Decimal("0.00")
    c_final = ((vd * cd) + (vt * co)) / v_total
    return c_final.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_costo_diario_equipo(used_days, tarifa):
    """
    Daily Cost = Used Days * Tarifa (Rental o Standby)
    """
    dias = Decimal(str(used_days or 0))
    tf = Decimal(str(tarifa or 0))
    return (dias * tf).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ==============================================================================
# HELPER: OBTENCIÓN Y PREPARACIÓN DE CONTEXTO DEL REPORTE
# ==============================================================================

def obtener_reporte_o_default(reporte_id=None):
    """Recupera el reporte solicitado o el más reciente."""
    if reporte_id:
        return get_object_or_404(ReporteDiario, pk=reporte_id)
    rep = ReporteDiario.objects.filter(codigo_reporte__icontains="REP-2026-0016").first()
    if not rep:
        rep = ReporteDiario.objects.order_by("-fecha", "-id").first()
    return rep


def construir_contexto_geometria_volumen(reporte):
    """
    Compila todas las entidades y ejecuta los cálculos requeridos por las especificaciones:
    - 05_Geometry_Volume_Accounting.md
    - 07_Formulas_Business_Logic.md
    """
    if not reporte:
        return {}

    # 1. Secciones de hoyo
    geometrias = list(reporte.geometrias_hoyo.all().order_by("profundidad_tope"))
    geometrias_data = [g.to_dict() for g in geometrias]

    # 2. Sarta de perforación y cálculo inverso de longitud
    tramos = list(reporte.tramos_sarta.all())
    bha_tramos = [t for t in tramos if not t.es_principal]
    suma_longitud_bha = sum([t.longitud or Decimal("0.00") for t in bha_tramos])
    dp_tramo = next((t for t in tramos if t.es_principal), None)

    # Autocálculo de la longitud de Drill Pipe
    dp_length_calculada = None
    if reporte.bit_depth is not None:
        dp_length_calculada = calcular_longitud_drill_pipe(reporte.bit_depth, suma_longitud_bha)

    tramos_data = []
    for t in tramos:
        d = t.to_dict()
        if t.es_principal and dp_length_calculada is not None:
            d["longitud_calculada"] = float(dp_length_calculada)
            d["longitud"] = float(dp_length_calculada)
        else:
            d["longitud_calculada"] = float(t.longitud) if t.longitud is not None else None
        tramos_data.append(d)

    # 3. Fosas activas y no-transaccionales
    fosas_activas = list(reporte.fosas.filter(es_transaccional=True).order_by("nombre"))
    fosas_pasivas = list(reporte.fosas.filter(es_transaccional=False).order_by("nombre"))

    total_capacidad_activas = sum([f.capacidad for f in fosas_activas])
    total_start_activas = sum([f.volumen_inicial for f in fosas_activas])
    total_calc_end_activas = sum([f.volumen_final_teorico for f in fosas_activas])
    total_actual_end_activas = sum([f.volumen_final_medido for f in fosas_activas])

    fosas_activas_data = [f.to_dict() for f in fosas_activas]
    fosas_pasivas_data = [f.to_dict() for f in fosas_pasivas]

    # 4. Transacciones volumétricas
    transacciones = list(reporte.transacciones_volumetricas.all().order_by("-fecha_hora"))
    transacciones_data = [tx.to_dict() for tx in transacciones]

    # 5. Desplazamientos
    desplazamientos = list(reporte.desplazamientos.all().order_by("orden"))
    desplazamientos_data = [d.to_dict() for d in desplazamientos]

    # 6. Parámetros Offshore y Riser
    riser_calc_length = None
    if not reporte.riserless_drilling and reporte.water_depth is not None and reporte.air_gap is not None:
        riser_calc_length = calcular_riser_length(reporte.water_depth, reporte.air_gap)

    # 7. Conciliación Volumétrica (El Cuadre)
    cuadre = calcular_not_accounted(
        reporte.volumen_teorico_fosas or total_calc_end_activas,
        reporte.volumen_medido_fosas or total_actual_end_activas
    )

    # 8. Consolidación de cálculos
    resumen_calculos = {
        "hole_size": float(reporte.hole_size) if reporte.hole_size is not None else None,
        "total_hole_volume": float(reporte.total_hole_volume),
        "fluid_volume": float(reporte.fluid_volume),
        "suma_longitud_bha": float(suma_longitud_bha),
        "dp_length_calculada": float(dp_length_calculada) if dp_length_calculada is not None else None,
        "riser_length_calculada": float(riser_calc_length) if riser_calc_length is not None else None,
        "not_accounted": cuadre["not_accounted"],
        "balance_cuadrado": cuadre["balance_cuadrado"],
        "total_start_volumen": float(total_start_activas),
        "total_calc_end_volumen": float(total_calc_end_activas),
        "total_actual_end_volumen": float(total_actual_end_activas),
    }

    return {
        "reporte": reporte.to_dict(),
        "geometrias": geometrias_data,
        "tramos_sarta": tramos_data,
        "fosas_activas": fosas_activas_data,
        "fosas_pasivas": fosas_pasivas_data,
        "transacciones": transacciones_data,
        "desplazamientos": desplazamientos_data,
        "cuadre": cuadre,
        "resumen_calculos": resumen_calculos,
    }


# ==============================================================================
# VISTA PRINCIPAL DUAL (TEMPLATE HTML / JSON)
# ==============================================================================

def vista_geometria_volumen(request, reporte_id=None):
    """
    Vista principal de la pantalla de Geometría y Contabilidad de Volumen.
    Soporta retorno Dual:
    - Si request.GET.get('format') == 'json' o cabecera Accept: application/json -> JsonResponse.
    - De lo contrario -> renderiza 'mychapala/geometria_volumen.html'.
    """
    reporte = obtener_reporte_o_default(reporte_id)
    if not reporte:
        if request.GET.get("format") == "json" or request.headers.get("Accept") == "application/json":
            return JsonResponse({"success": False, "error": "No hay reportes disponibles en el sistema."}, status=404)
        return render(request, "mychapala/geometria_volumen.html", {"error": "No hay reportes disponibles."})

    contexto = construir_contexto_geometria_volumen(reporte)

    # Respuesta JSON solicitada por API o Frontend SPA
    if request.GET.get("format") == "json" or "application/json" in request.headers.get("Accept", ""):
        return JsonResponse({
            "success": True,
            "reporte_id": reporte.id,
            "codigo_reporte": reporte.codigo_reporte,
            "data": contexto,
        })

    # Render HTML con contexto inyectado
    try:
        return render(request, "chapala/geometria_volumen.html", contexto)
    except Exception:
        return render(request, "mychapala/geometria_volumen.html", contexto)


# ==============================================================================
# ENDPOINTS RESTful (APIS DE LAS PANTALLAS FALTANTES)
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_geometria(request, reporte_id=None):
    """
    API para la pestaña Geometry (Wellbore Geometry, Drill String, Offshore Params).
    GET: Devuelve las secciones del pozo, componentes de sarta y parámetros calculados.
    POST: Crea o actualiza componentes geométricos o parámetros del reporte.
    """
    reporte = obtener_reporte_o_default(reporte_id)
    if not reporte:
        return JsonResponse({"success": False, "error": "Reporte no encontrado."}, status=404)

    if request.method == "GET":
        contexto = construir_contexto_geometria_volumen(reporte)
        return JsonResponse({
            "success": True,
            "reporte_id": reporte.id,
            "codigo_reporte": reporte.codigo_reporte,
            "hole_size": contexto["resumen_calculos"]["hole_size"],
            "total_hole_volume": contexto["resumen_calculos"]["total_hole_volume"],
            "fluid_volume": contexto["resumen_calculos"]["fluid_volume"],
            "dp_length_calculada": contexto["resumen_calculos"]["dp_length_calculada"],
            "geometrias": contexto["geometrias"],
            "tramos_sarta": contexto["tramos_sarta"],
            "offshore": {
                "riserless_drilling": reporte.riserless_drilling,
                "water_depth": float(reporte.water_depth) if reporte.water_depth else None,
                "air_gap": float(reporte.air_gap) if reporte.air_gap else None,
                "riser_od": float(reporte.riser_od) if reporte.riser_od else None,
                "riser_id": float(reporte.riser_id) if reporte.riser_id else None,
                "riser_length": float(reporte.riser_length) if reporte.riser_length else None,
            }
        })

    elif request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8"))
            action = body.get("action", "update_params")

            if action == "update_params":
                if "bit_depth" in body:
                    reporte.bit_depth = Decimal(str(body["bit_depth"]))
                if "bit_size" in body:
                    reporte.bit_size = Decimal(str(body["bit_size"]))
                if "porcentaje_washout" in body:
                    reporte.porcentaje_washout = Decimal(str(body["porcentaje_washout"]))
                if "water_depth" in body:
                    reporte.water_depth = Decimal(str(body["water_depth"]))
                if "air_gap" in body:
                    reporte.air_gap = Decimal(str(body["air_gap"]))
                if "riserless_drilling" in body:
                    reporte.riserless_drilling = bool(body["riserless_drilling"])
                if not reporte.riserless_drilling and reporte.water_depth and reporte.air_gap:
                    reporte.riser_length = calcular_riser_length(reporte.water_depth, reporte.air_gap)
                reporte.save()

            elif action == "add_seccion_hoyo":
                GeometriaHoyo.objects.create(
                    reporte=reporte,
                    tipo=body.get("tipo", "open_hole"),
                    diametro=Decimal(str(body.get("diametro", "8.5"))),
                    profundidad_tope=Decimal(str(body.get("profundidad_tope", "0.0"))),
                    profundidad_base=Decimal(str(body.get("profundidad_base", "0.0"))),
                    capacidad=Decimal(str(body.get("capacidad", "0.0"))),
                    volumen=Decimal(str(body.get("volumen", "0.0"))),
                )

            elif action == "add_tramo_sarta":
                TramoSarta.objects.create(
                    reporte=reporte,
                    tipo=body.get("tipo", "drill_pipe"),
                    diametro_externo=Decimal(str(body.get("diametro_externo", "5.0"))),
                    diametro_interno=Decimal(str(body.get("diametro_interno", "4.276"))),
                    longitud=Decimal(str(body.get("longitud", "0.0"))) if body.get("longitud") is not None else None,
                    es_principal=bool(body.get("es_principal", False)),
                )

            contexto = construir_contexto_geometria_volumen(reporte)
            return JsonResponse({"success": True, "message": "Datos de geometría actualizados.", "data": contexto})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_volume_accounting(request, reporte_id=None):
    """
    API para la pestaña Volume Accounting (6 Bloques):
    1. Pit Section
    2. Fluids in Hole
    3. Total Loss Breakdown
    4. Fluid Volume (El Cuadre / Not Accounted)
    5. Non-Transactional Pits
    6. Fluids Balance Summary
    """
    reporte = obtener_reporte_o_default(reporte_id)
    if not reporte:
        return JsonResponse({"success": False, "error": "Reporte no encontrado."}, status=404)

    if request.method == "GET":
        contexto = construir_contexto_geometria_volumen(reporte)
        return JsonResponse({
            "success": True,
            "reporte_id": reporte.id,
            "codigo_reporte": reporte.codigo_reporte,
            "bloque_1_pits": contexto["fosas_activas"],
            "bloque_2_fluids_in_hole": {
                "volumen_anular": float(reporte.volumen_anular),
                "volumen_sarta": float(reporte.volumen_sarta),
                "volumen_debajo_mecha": float(reporte.volumen_debajo_mecha),
                "total_hole_volume": float(reporte.total_hole_volume),
                "volumen_no_fluido": float(reporte.volumen_no_fluido),
                "fluid_volume": float(reporte.fluid_volume),
            },
            "bloque_3_loss_breakdown": {
                "superficie": float(reporte.total_perdidas_superficie),
                "subsuelo": float(reporte.total_perdidas_subsuelo),
                "mecanicas": float(reporte.total_perdidas_mecanicas),
                "total_perdidas": float(reporte.total_perdidas_superficie + reporte.total_perdidas_subsuelo + reporte.total_perdidas_mecanicas),
            },
            "bloque_4_cuadre": contexto["cuadre"],
            "bloque_5_non_transactional_pits": contexto["fosas_pasivas"],
            "bloque_6_balance": {
                "start_volume": contexto["resumen_calculos"]["total_start_volumen"],
                "calc_end_volume": contexto["resumen_calculos"]["total_calc_end_volumen"],
                "actual_end_volume": contexto["resumen_calculos"]["total_actual_end_volumen"],
                "not_accounted": contexto["cuadre"]["not_accounted"],
                "balance_cuadrado": contexto["cuadre"]["balance_cuadrado"],
            }
        })

    elif request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8"))
            if "fosas" in body and isinstance(body["fosas"], list):
                for f_data in body["fosas"]:
                    f_id = f_data.get("id")
                    if f_id:
                        fosa = Fosa.objects.filter(id=f_id, reporte=reporte).first()
                        if fosa:
                            if "volumen_final_medido" in f_data:
                                fosa.volumen_final_medido = Decimal(str(f_data["volumen_final_medido"]))
                            if "volumen_final_teorico" in f_data:
                                fosa.volumen_final_teorico = Decimal(str(f_data["volumen_final_teorico"]))
                            if "peso_lodo" in f_data and f_data["peso_lodo"] is not None:
                                fosa.peso_lodo = Decimal(str(f_data["peso_lodo"]))
                            fosa.save()

            if "volumen_medido_fosas" in body:
                reporte.volumen_medido_fosas = Decimal(str(body["volumen_medido_fosas"]))
            if "volumen_teorico_fosas" in body:
                reporte.volumen_teorico_fosas = Decimal(str(body["volumen_teorico_fosas"]))
            if "volumen_no_fluido" in body:
                reporte.volumen_no_fluido = Decimal(str(body["volumen_no_fluido"]))
            reporte.save()

            contexto = construir_contexto_geometria_volumen(reporte)
            return JsonResponse({
                "success": True,
                "message": "Contabilidad volumétrica actualizada.",
                "cuadre": contexto["cuadre"]
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_transacciones_volumetricas(request, reporte_id=None):
    """
    API para Transaction Buttons:
    - add_chemicals (con soporte is_dilution)
    - add_whole_mud (con add_without_charge y cálculo ponderado de concentración)
    - transfer (con soporte all_volume para vaciado exacto)
    - return_back_load (despacho fuera del taladro con aislamiento financiero)
    - equipment_loss (descarte de lodo en sólidos calculado desde equipos)
    """
    reporte = obtener_reporte_o_default(reporte_id)
    if not reporte:
        return JsonResponse({"success": False, "error": "Reporte no encontrado."}, status=404)

    if request.method == "GET":
        transacciones = reporte.transacciones_volumetricas.all().order_by("-fecha_hora")
        return JsonResponse({
            "success": True,
            "reporte_id": reporte.id,
            "total": transacciones.count(),
            "transacciones": [t.to_dict() for t in transacciones],
        })

    elif request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8"))
            tipo = body.get("tipo", "transfer")
            fosa_origen_id = body.get("fosa_origen_id")
            fosa_destino_id = body.get("fosa_destino_id")
            producto_id = body.get("producto_id")
            volumen = Decimal(str(body.get("volumen", "0.00")))
            is_dilution = bool(body.get("is_dilution", False))
            add_without_charge = bool(body.get("add_without_charge", False))
            all_volume = bool(body.get("all_volume", False))
            comentario = body.get("comentario", "").strip()

            fosa_origen = Fosa.objects.filter(id=fosa_origen_id, reporte=reporte).first() if fosa_origen_id else None
            fosa_destino = Fosa.objects.filter(id=fosa_destino_id, reporte=reporte).first() if fosa_destino_id else None
            producto = Producto.objects.filter(id=producto_id).first() if producto_id else None

            if tipo == "transfer" and all_volume and fosa_origen:
                volumen = fosa_origen.volumen_final_teorico
                fosa_origen.volumen_final_teorico = Decimal("0.00")
                fosa_origen.volumen_final_medido = Decimal("0.00")
                fosa_origen.save()
                if fosa_destino:
                    fosa_destino.volumen_final_teorico += volumen
                    fosa_destino.volumen_final_medido += volumen
                    fosa_destino.save()

            if tipo == "equipment_loss":
                vol_solidos = Decimal(str(body.get("volumen_solidos", "0.00")))
                mud_on_cuttings = Decimal(str(body.get("mud_on_cuttings", "0.00")))
                if vol_solidos > 0 and mud_on_cuttings > 0:
                    volumen = calcular_lodo_perdido_en_solidos(vol_solidos, mud_on_cuttings)
                    sludge = calcular_volumen_sludge(vol_solidos, volumen)
                    comentario = f"{comentario} [Solidos: {vol_solidos} bbl, MOC: {mud_on_cuttings}, Sludge: {sludge} bbl]".strip()

            tx = TransaccionVolumetrica.objects.create(
                reporte=reporte,
                tipo=tipo,
                fosa_origen=fosa_origen,
                fosa_destino=fosa_destino,
                producto=producto,
                volumen=volumen,
                is_dilution=is_dilution,
                add_without_charge=add_without_charge,
                all_volume=all_volume,
                comentario=comentario,
            )

            return JsonResponse({
                "success": True,
                "message": "Transacción volumétrica registrada exitosamente.",
                "transaccion": tx.to_dict(),
            }, status=201)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_desplazamientos(request, reporte_id=None):
    """
    API para la pestaña Displacements (Tren de Baches y Reclaimed to Pit).
    """
    reporte = obtener_reporte_o_default(reporte_id)
    if not reporte:
        return JsonResponse({"success": False, "error": "Reporte no encontrado."}, status=404)

    if request.method == "GET":
        desps = reporte.desplazamientos.all().order_by("orden")
        return JsonResponse({
            "success": True,
            "reporte_id": reporte.id,
            "total": desps.count(),
            "desplazamientos": [d.to_dict() for d in desps],
        })

    elif request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8"))
            tipo_componente = body.get("tipo_componente", "spacer")
            descripcion = body.get("descripcion", "").strip()
            volumen = Decimal(str(body.get("volumen", "0.00")))
            reclaimed = bool(body.get("reclaimed", False))
            fosa_origen_id = body.get("fosa_origen_id")
            fosa_retorno_id = body.get("fosa_retorno_id")
            orden = int(body.get("orden", reporte.desplazamientos.count() + 1))
            observaciones = body.get("observaciones", "").strip()

            fosa_origen = Fosa.objects.filter(id=fosa_origen_id, reporte=reporte).first() if fosa_origen_id else None
            fosa_retorno = Fosa.objects.filter(id=fosa_retorno_id, reporte=reporte).first() if fosa_retorno_id else None

            if reclaimed and not fosa_retorno:
                return JsonResponse({
                    "success": False,
                    "error": "Si el bache es recuperado en superficie (Reclaimed), debe declarar el tanque de retorno (Reclaimed to Pit)."
                }, status=400)

            desp = Desplazamiento.objects.create(
                reporte=reporte,
                tipo_componente=tipo_componente,
                descripcion=descripcion,
                fosa_origen=fosa_origen,
                volumen=volumen,
                reclaimed=reclaimed,
                fosa_retorno=fosa_retorno,
                orden=orden,
                observaciones=observaciones,
            )

            return JsonResponse({
                "success": True,
                "message": "Bache de desplazamiento agregado exitosamente.",
                "desplazamiento": desp.to_dict(),
            }, status=201)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)


# ==============================================================================
# MOTOR INTERACTIVO DE FÓRMULAS (07_Formulas_Business_Logic.md)
# ==============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_calcular_formulas(request):
    """
    Endpoint interactivo para evaluar cualquier fórmula de 07_Formulas_Business_Logic.md
    Parámetro 'formula':
    - 'hole_size': bit_size, porcentaje_washout
    - 'total_hole_volume': volumen_anular, volumen_sarta, volumen_debajo_mecha
    - 'fluid_volume': total_hole_volume, volumen_no_fluido
    - 'inverse_drill_pipe': bit_depth, suma_longitud_bha
    - 'riser_length': water_depth, air_gap
    - 'reynolds_flow': ann_re
    - 'porcentaje_lodo': mud_on_cuttings
    - 'distribucion_solidos': porcentaje_total, equipos_activos
    - 'lodo_perdido_solidos': volumen_solidos, mud_on_cuttings
    - 'volumen_sludge': volumen_solidos, lodo_perdido
    - 'not_accounted': calc_end_volume, actual_end_volume
    - 'concentracion_mezcla': volumen_destino, concentracion_destino, volumen_transf, concentracion_origen
    - 'costo_diario_equipo': used_days, tarifa
    """
    params = request.GET.dict() if request.method == "GET" else {}
    if request.method == "POST":
        try:
            params = json.loads(request.body.decode("utf-8"))
        except Exception:
            params = request.POST.dict()

    formula = params.get("formula", "").strip().lower()

    if formula == "hole_size":
        bs = params.get("bit_size")
        wo = params.get("porcentaje_washout", 0)
        res = calcular_hole_size(bs, wo)
        return JsonResponse({
            "success": True,
            "formula": "Hole Size = Bit Size * (1 + % Washout / 100)",
            "inputs": {"bit_size": bs, "porcentaje_washout": wo},
            "resultado": float(res) if res is not None else None,
        })

    elif formula == "total_hole_volume":
        va = params.get("volumen_anular", 0)
        vs = params.get("volumen_sarta", 0)
        vb = params.get("volumen_debajo_mecha", 0)
        res = calcular_total_hole_volume(va, vs, vb)
        return JsonResponse({
            "success": True,
            "formula": "Total Hole Volume = Annulus + Total DS + Below Bit",
            "inputs": {"volumen_anular": va, "volumen_sarta": vs, "volumen_debajo_mecha": vb},
            "resultado": float(res),
        })

    elif formula == "fluid_volume":
        thv = params.get("total_hole_volume", 0)
        vnf = params.get("volumen_no_fluido", 0)
        res = calcular_fluid_volume(thv, vnf)
        return JsonResponse({
            "success": True,
            "formula": "Fluid Volume = Total Hole Volume - Volume Not Fluids",
            "inputs": {"total_hole_volume": thv, "volumen_no_fluido": vnf},
            "resultado": float(res),
        })

    elif formula == "inverse_drill_pipe":
        bd = params.get("bit_depth", 0)
        bha = params.get("suma_longitud_bha", 0)
        res = calcular_longitud_drill_pipe(bd, bha)
        return JsonResponse({
            "success": True,
            "formula": "L_DP = Bit Depth - sum(L_BHA)",
            "inputs": {"bit_depth": bd, "suma_longitud_bha": bha},
            "resultado": float(res),
        })

    elif formula == "riser_length":
        wd = params.get("water_depth", 0)
        ag = params.get("air_gap", 0)
        res = calcular_riser_length(wd, ag)
        return JsonResponse({
            "success": True,
            "formula": "Riser Length = Water Depth - Air Gap",
            "inputs": {"water_depth": wd, "air_gap": ag},
            "resultado": float(res),
        })

    elif formula == "reynolds_flow":
        re = params.get("ann_re", 0)
        res = calcular_regimen_flujo(re)
        return JsonResponse({
            "success": True,
            "formula": "AnnRe > 2000 -> Turbulento, else Laminar",
            "inputs": {"ann_re": re},
            "resultado": res,
        })

    elif formula == "porcentaje_lodo":
        moc = params.get("mud_on_cuttings", 0)
        res = calcular_porcentaje_lodo_descarga(moc)
        return JsonResponse({
            "success": True,
            "formula": "% Lodo = Mud On Cuttings / (1 + Mud On Cuttings) * 100",
            "inputs": {"mud_on_cuttings": moc},
            "resultado_porcentaje": float(res),
        })

    elif formula == "distribucion_solidos":
        tot = params.get("porcentaje_total", 0)
        eq = params.get("equipos_activos", 1)
        res = calcular_distribucion_solidos(tot, eq)
        return JsonResponse({
            "success": True,
            "formula": "% Individual = % Total / Equipos Activos",
            "inputs": {"porcentaje_total": tot, "equipos_activos": eq},
            "resultado": float(res),
        })

    elif formula == "lodo_perdido_solidos":
        v_sol = params.get("volumen_solidos", 0)
        moc = params.get("mud_on_cuttings", 0)
        res = calcular_lodo_perdido_en_solidos(v_sol, moc)
        return JsonResponse({
            "success": True,
            "formula": "V_lodo_perdido = V_solidos * Mud On Cuttings",
            "inputs": {"volumen_solidos": v_sol, "mud_on_cuttings": moc},
            "resultado": float(res),
        })

    elif formula == "volumen_sludge":
        v_sol = params.get("volumen_solidos", 0)
        v_lp = params.get("lodo_perdido", 0)
        res = calcular_volumen_sludge(v_sol, v_lp)
        return JsonResponse({
            "success": True,
            "formula": "V_sludge = V_solidos + V_lodo_perdido",
            "inputs": {"volumen_solidos": v_sol, "lodo_perdido": v_lp},
            "resultado": float(res),
        })

    elif formula == "not_accounted":
        calc = params.get("calc_end_volume", 0)
        act = params.get("actual_end_volume", 0)
        res = calcular_not_accounted(calc, act)
        return JsonResponse({
            "success": True,
            "formula": "Not Accounted = Calc End Volume - Actual End Volume (Regla: == 0.00)",
            "inputs": {"calc_end_volume": calc, "actual_end_volume": act},
            "resultado": res,
        })

    elif formula == "concentracion_mezcla":
        vd = params.get("volumen_destino", 0)
        cd = params.get("concentracion_destino", 0)
        vt = params.get("volumen_transf", 0)
        co = params.get("concentracion_origen", 0)
        res = calcular_concentracion_mezcla(vd, cd, vt, co)
        return JsonResponse({
            "success": True,
            "formula": "C_final = (V_dest * C_dest + V_transf * C_orig) / (V_dest + V_transf)",
            "inputs": {
                "volumen_destino": vd,
                "concentracion_destino": cd,
                "volumen_transf": vt,
                "concentracion_origen": co,
            },
            "resultado": float(res),
        })

    elif formula == "costo_diario_equipo":
        dias = params.get("used_days", 0)
        tf = params.get("tarifa", 0)
        res = calcular_costo_diario_equipo(dias, tf)
        return JsonResponse({
            "success": True,
            "formula": "Daily Cost = Used Days * Tarifa",
            "inputs": {"used_days": dias, "tarifa": tf},
            "resultado": float(res),
        })

    else:
        return JsonResponse({
            "success": True,
            "descripcion": "Motor de Cálculo de Fórmulas y Lógica de Negocio - ONE-TRAX / Chapala",
            "formulas_disponibles": [
                "hole_size",
                "total_hole_volume",
                "fluid_volume",
                "inverse_drill_pipe",
                "riser_length",
                "reynolds_flow",
                "porcentaje_lodo",
                "distribucion_solidos",
                "lodo_perdido_solidos",
                "volumen_sludge",
                "not_accounted",
                "concentracion_mezcla",
                "costo_diario_equipo",
            ]
        })
