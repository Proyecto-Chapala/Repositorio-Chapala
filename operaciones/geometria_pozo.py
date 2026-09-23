"""
Motor de cálculo de geometría y volúmenes del pozo (Tab #4 - Well Geometry).

Equivale a la pantalla "Hole Volume Results" de ONE-TRAX, que se abre con el botón
"Daily Casing / Volume". Es información de solo lectura: todo se deriva del perfil
de revestidores del pozo, de la sarta de perforación del día y de la profundidad de
la mecha.

Fórmulas base (el ingeniero de fluidos las enuncia como "diámetro al cuadrado entre
1029.4 por la altura"):

    Capacidad interna  (bbl/ft) = ID²  / 1029.4
    Capacidad anular   (bbl/ft) = (D_confinamiento² - OD²) / 1029.4
    Desplazamiento     (bbl/ft) = (OD² - ID²) / 1029.4

Corrección por juntas (tool joints): en tubería de perforación y heavy weight, la
junta tiene ID más pequeño y OD más grande que el cuerpo del tubo, así que reduce
tanto la capacidad interna como la anular. ONE-TRAX pondera linealmente por la
fracción de longitud ocupada por juntas:

    capacidad_efectiva = capacidad_cuerpo * (1 - f) + capacidad_junta * f
    f = largo_junta_in / (largo_tramo_ft * 12)

Con los valores del manual (junta de 21 in en tramos de 31 ft, f = 0.056452) esta
ponderación reproduce exactamente los valores del ejemplo del pozo Gusher #2.

El módulo no importa Django: recibe diccionarios simples y devuelve diccionarios
simples, para poder probarse de forma aislada y para que el mismo algoritmo pueda
replicarse en JavaScript para el cálculo en vivo.
"""

CONSTANTE_CAPACIDAD = 1029.4

# Tolerancia para descartar sub-tramos de longitud despreciable al cortar secciones.
EPSILON_FT = 0.0005


def capacidad_interna(diametro_interno_in):
    """Capacidad interna de un tubo, en bbl/ft."""
    d = float(diametro_interno_in or 0.0)
    if d <= 0:
        return 0.0
    return (d * d) / CONSTANTE_CAPACIDAD


def capacidad_anular(diametro_confinamiento_in, diametro_externo_in):
    """Capacidad del espacio anular entre el hoyo/revestidor y la tubería, en bbl/ft."""
    d_conf = float(diametro_confinamiento_in or 0.0)
    d_ext = float(diametro_externo_in or 0.0)
    if d_conf <= 0:
        return 0.0
    area = (d_conf * d_conf) - (d_ext * d_ext)
    if area <= 0:
        return 0.0
    return area / CONSTANTE_CAPACIDAD


def capacidad_desplazamiento(diametro_externo_in, diametro_interno_in):
    """Volumen de acero desplazado por el tubo, en bbl/ft."""
    d_ext = float(diametro_externo_in or 0.0)
    d_int = float(diametro_interno_in or 0.0)
    if d_ext <= 0:
        return 0.0
    area = (d_ext * d_ext) - (d_int * d_int)
    if area <= 0:
        return 0.0
    return area / CONSTANTE_CAPACIDAD


def fraccion_junta(tramo):
    """Fracción de la longitud del tramo ocupada por juntas (tool joints)."""
    largo_tramo_ft = float(tramo.get('largo_tramo_ft') or 0.0)
    largo_junta_in = float(tramo.get('tool_joint_length_in') or 0.0)
    largo_tramo_in = largo_tramo_ft * 12.0
    if largo_tramo_in <= 0 or largo_junta_in <= 0:
        return 0.0
    return min(1.0, largo_junta_in / largo_tramo_in)


def _ponderar(valor_cuerpo, valor_junta, f):
    if f <= 0:
        return valor_cuerpo
    return valor_cuerpo * (1.0 - f) + valor_junta * f


def capacidad_interna_efectiva(tramo):
    """Capacidad interna del tramo en bbl/ft, ponderada por el efecto de las juntas."""
    f = fraccion_junta(tramo)
    cuerpo = capacidad_interna(tramo.get('id_in'))
    if f <= 0:
        return cuerpo
    tj_id = float(tramo.get('tool_joint_id_in') or 0.0)
    junta = capacidad_interna(tj_id) if tj_id > 0 else cuerpo
    return _ponderar(cuerpo, junta, f)


def capacidad_anular_efectiva(tramo, diametro_confinamiento_in):
    """Capacidad anular del tramo en bbl/ft, ponderada por el efecto de las juntas."""
    f = fraccion_junta(tramo)
    cuerpo = capacidad_anular(diametro_confinamiento_in, tramo.get('od_in'))
    if f <= 0:
        return cuerpo
    tj_od = float(tramo.get('tool_joint_od_in') or 0.0)
    junta = capacidad_anular(diametro_confinamiento_in, tj_od) if tj_od > 0 else cuerpo
    return _ponderar(cuerpo, junta, f)


def capacidad_desplazamiento_efectiva(tramo):
    """Desplazamiento de acero del tramo en bbl/ft, ponderado por el efecto de las juntas."""
    f = fraccion_junta(tramo)
    cuerpo = capacidad_desplazamiento(tramo.get('od_in'), tramo.get('id_in'))
    if f <= 0:
        return cuerpo
    tj_od = float(tramo.get('tool_joint_od_in') or 0.0)
    tj_id = float(tramo.get('tool_joint_id_in') or 0.0)
    if tj_od <= 0:
        return cuerpo
    junta = capacidad_desplazamiento(tj_od, tj_id)
    return _ponderar(cuerpo, junta, f)


# ---------------------------------------------------------------------------
# Perfil de confinamiento del pozo
# ---------------------------------------------------------------------------

def construir_perfil_confinamiento(riser, intervalos, fondo_hoyo_ft,
                                   hole_size_in, pilot_hole=None):
    """
    Arma el perfil del pozo de superficie hacia abajo: qué diámetro confina el fluido
    a cada profundidad.

    Parámetros
    ----------
    riser : dict o None
        {'longitud_ft': float, 'id_in': float} cuando el pozo usa riser.
    intervalos : lista de dict
        Intervalos de revestimiento del pozo, cada uno con
        {'numero': int, 'casing_id_in': float, 'profundidad_ft': float,
         'top_of_liner_ft': float, 'hole_size_in': float, 'etiqueta': str}.
        Un intervalo con top_of_liner_ft > 0 se trata como liner (no llega a superficie).
    fondo_hoyo_ft : float
        Profundidad total del hoyo en la fecha del reporte.
    hole_size_in : float
        Diámetro del hoyo abierto (normalmente el bit size corregido por washout).
    pilot_hole : dict o None
        {'hole_size_in': float, 'depth_ft': float}. El hoyo piloto ocupa el tramo más
        profundo, desde el fondo del hoyo principal hasta su propia profundidad.

    Devuelve
    --------
    Lista ordenada de {'desde_ft', 'hasta_ft', 'diametro_in', 'etiqueta', 'es_hoyo_abierto'}.
    """
    fondo_hoyo_ft = float(fondo_hoyo_ft or 0.0)
    if fondo_hoyo_ft <= 0:
        return []

    # Fronteras candidatas: cada cambio de confinamiento.
    fronteras = {0.0, fondo_hoyo_ft}

    riser_len = 0.0
    riser_id = 0.0
    if riser:
        riser_len = float(riser.get('longitud_ft') or 0.0)
        riser_id = float(riser.get('id_in') or 0.0)
        if riser_len > 0 and riser_id > 0:
            fronteras.add(min(riser_len, fondo_hoyo_ft))

    intervalos_validos = []
    for itv in (intervalos or []):
        casing_id = float(itv.get('casing_id_in') or 0.0)
        shoe = float(itv.get('profundidad_ft') or 0.0)
        if casing_id <= 0 or shoe <= 0:
            continue
        top = float(itv.get('top_of_liner_ft') or 0.0)
        intervalos_validos.append({
            'numero': itv.get('numero'),
            'casing_id_in': casing_id,
            'top_ft': top,
            'shoe_ft': shoe,
            'etiqueta': itv.get('etiqueta') or f"Revestidor #{itv.get('numero')}",
        })
        if 0 < top < fondo_hoyo_ft:
            fronteras.add(top)
        if 0 < shoe < fondo_hoyo_ft:
            fronteras.add(shoe)

    # El hoyo piloto ocupa el tramo más profundo: desde el fondo del hoyo principal
    # (pilot_hole['desde_ft']) hasta su propia profundidad.
    pilot_desde = 0.0
    pilot_hasta = 0.0
    pilot_size = 0.0
    if pilot_hole:
        pilot_size = float(pilot_hole.get('hole_size_in') or 0.0)
        pilot_hasta = float(pilot_hole.get('depth_ft') or 0.0)
        pilot_desde = float(pilot_hole.get('desde_ft') or 0.0)
        if pilot_size > 0 and pilot_hasta > pilot_desde:
            if 0 < pilot_desde < fondo_hoyo_ft:
                fronteras.add(pilot_desde)
            if 0 < pilot_hasta < fondo_hoyo_ft:
                fronteras.add(pilot_hasta)
        else:
            pilot_size = 0.0

    limites = sorted(x for x in fronteras if 0.0 <= x <= fondo_hoyo_ft)

    perfil = []
    for i in range(len(limites) - 1):
        desde = limites[i]
        hasta = limites[i + 1]
        if (hasta - desde) <= EPSILON_FT:
            continue
        medio = (desde + hasta) / 2.0

        # 1) Riser: siempre manda en el tramo superior.
        if riser_len > 0 and riser_id > 0 and medio <= riser_len:
            perfil.append({
                'desde_ft': desde, 'hasta_ft': hasta,
                'diametro_in': riser_id, 'etiqueta': 'Riser',
                'es_hoyo_abierto': False,
            })
            continue

        # 2) Revestidores presentes a esta profundidad: manda el de menor ID (el interno).
        candidatos = [
            c for c in intervalos_validos
            if c['top_ft'] <= medio <= c['shoe_ft']
        ]
        if candidatos:
            interno = min(candidatos, key=lambda c: c['casing_id_in'])
            perfil.append({
                'desde_ft': desde, 'hasta_ft': hasta,
                'diametro_in': interno['casing_id_in'],
                'etiqueta': interno['etiqueta'],
                'es_hoyo_abierto': False,
            })
            continue

        # 3) Hoyo abierto (o piloto si estamos por debajo de su tope).
        diam = float(hole_size_in or 0.0)
        etiqueta = 'Hoyo Abierto'
        if pilot_size > 0 and pilot_desde <= medio <= pilot_hasta:
            diam = pilot_size
            etiqueta = 'Hoyo Piloto'
        perfil.append({
            'desde_ft': desde, 'hasta_ft': hasta,
            'diametro_in': diam, 'etiqueta': etiqueta,
            'es_hoyo_abierto': True,
        })

    return perfil


def construir_perfil_sarta(tramos, bit_depth_ft):
    """
    Ubica cada tramo de la sarta en profundidad, apilando desde la mecha hacia arriba.

    `tramos` viene ordenado por 'orden' (1 = mecha). El primer tramo tiene su base en
    la profundidad de la mecha; cada tramo siguiente se apila encima.

    Devuelve lista de {'tramo', 'desde_ft' (tope), 'hasta_ft' (base)} ordenada de
    superficie hacia abajo.
    """
    bit_depth_ft = float(bit_depth_ft or 0.0)
    base = bit_depth_ft
    ubicados = []
    for tramo in sorted(tramos or [], key=lambda t: t.get('orden', 0)):
        longitud = float(tramo.get('longitud_ft') or 0.0)
        if longitud <= 0:
            continue
        tope = base - longitud
        ubicados.append({'tramo': tramo, 'desde_ft': tope, 'hasta_ft': base})
        base = tope
    ubicados.sort(key=lambda u: u['desde_ft'])
    return ubicados


# ---------------------------------------------------------------------------
# Cálculo principal
# ---------------------------------------------------------------------------

def calcular_geometria(perfil_pozo, tramos, bit_depth_ft, fondo_hoyo_ft,
                       bbl_por_embolada=0.0, caudal_gpm=0.0):
    """
    Corta el pozo en secciones y calcula los volúmenes, replicando la pantalla
    "Hole Volume Results" de ONE-TRAX.

    Se corta en cada frontera de confinamiento Y en cada frontera de componente de la
    sarta, lo que ocurra primero. Por eso una sola tubería de perforación puede
    aparecer partida en varias filas (DP/Riser, DP/Revestidor, DP/Hoyo Abierto).
    """
    bit_depth_ft = float(bit_depth_ft or 0.0)
    fondo_hoyo_ft = float(fondo_hoyo_ft or 0.0)

    sarta_ubicada = construir_perfil_sarta(tramos, bit_depth_ft)

    tope_sarta = sarta_ubicada[0]['desde_ft'] if sarta_ubicada else bit_depth_ft
    longitud_sarta = sum(
        float(t.get('longitud_ft') or 0.0) for t in (tramos or [])
    )

    # Fronteras: todo cambio de confinamiento + todo cambio de componente.
    fronteras = set()
    for seg in perfil_pozo:
        fronteras.add(seg['desde_ft'])
        fronteras.add(seg['hasta_ft'])
    for ub in sarta_ubicada:
        fronteras.add(ub['desde_ft'])
        fronteras.add(ub['hasta_ft'])
    fronteras.add(0.0)
    if fondo_hoyo_ft > 0:
        fronteras.add(fondo_hoyo_ft)

    limites = sorted(x for x in fronteras if 0.0 <= x <= max(fondo_hoyo_ft, bit_depth_ft))

    secciones = []
    total_ds = 0.0
    total_anular = 0.0
    total_bajo_mecha = 0.0
    total_desplazamiento = 0.0

    for i in range(len(limites) - 1):
        desde = limites[i]
        hasta = limites[i + 1]
        longitud = hasta - desde
        if longitud <= EPSILON_FT:
            continue
        medio = (desde + hasta) / 2.0

        seg_pozo = next(
            (s for s in perfil_pozo if s['desde_ft'] <= medio <= s['hasta_ft']), None
        )
        if seg_pozo is None:
            continue
        d_conf = seg_pozo['diametro_in']

        ub = next(
            (u for u in sarta_ubicada if u['desde_ft'] <= medio <= u['hasta_ft']), None
        )

        if ub is None:
            # Sin tubería a esta profundidad: todo el hoyo es volumen abierto.
            capacidad = capacidad_interna(d_conf)
            vol = capacidad * longitud
            es_bajo_mecha = medio > bit_depth_ft
            if es_bajo_mecha:
                total_bajo_mecha += vol
            else:
                total_anular += vol
            secciones.append({
                'desde_ft': round(desde, 2),
                'hasta_ft': round(hasta, 2),
                'longitud_ft': round(longitud, 2),
                'diametro_hoyo_in': round(d_conf, 3),
                'od_in': None,
                'id_in': None,
                'tool_joint_od_in': None,
                'descripcion': ('Bajo la Mecha / ' if es_bajo_mecha else 'Sin Tubería / ') + seg_pozo['etiqueta'],
                'vol_sarta_bbl': 0.0,
                'vol_anular_bbl': round(vol, 2),
                'es_bajo_mecha': es_bajo_mecha,
            })
            continue

        tramo = ub['tramo']
        cap_int = capacidad_interna_efectiva(tramo)
        cap_ann = capacidad_anular_efectiva(tramo, d_conf)
        cap_desp = capacidad_desplazamiento_efectiva(tramo)

        vol_int = cap_int * longitud
        vol_ann = cap_ann * longitud
        vol_desp = cap_desp * longitud

        total_ds += vol_int
        total_anular += vol_ann
        total_desplazamiento += vol_desp

        secciones.append({
            'desde_ft': round(desde, 2),
            'hasta_ft': round(hasta, 2),
            'longitud_ft': round(longitud, 2),
            'diametro_hoyo_in': round(d_conf, 3),
            'od_in': round(float(tramo.get('od_in') or 0.0), 3),
            'id_in': round(float(tramo.get('id_in') or 0.0), 3),
            'tool_joint_od_in': round(float(tramo.get('tool_joint_od_in') or 0.0), 3) or None,
            'descripcion': f"{tramo.get('descripcion') or 'Tramo'} / {seg_pozo['etiqueta']}",
            'vol_sarta_bbl': round(vol_int, 2),
            'vol_anular_bbl': round(vol_ann, 2),
            'es_bajo_mecha': False,
        })

    volumen_total = total_ds + total_anular + total_bajo_mecha

    # Hidráulica: emboladas y minutos para circular el anular (fondo arriba).
    bbl_por_embolada = float(bbl_por_embolada or 0.0)
    caudal_gpm = float(caudal_gpm or 0.0)
    bottom_up_stks = (total_anular / bbl_por_embolada) if bbl_por_embolada > 0 else 0.0
    caudal_bbl_min = caudal_gpm / 42.0
    bottom_up_min = (total_anular / caudal_bbl_min) if caudal_bbl_min > 0 else 0.0

    avisos = []
    if bit_depth_ft > 0 and longitud_sarta > 0:
        diferencia = bit_depth_ft - longitud_sarta
        if abs(diferencia) > 1.0:
            if diferencia > 0:
                avisos.append(
                    f"La sarta no llega a la mecha: faltan {diferencia:,.0f} ft. "
                    "Revisa la longitud de la tubería de perforación."
                )
            else:
                avisos.append(
                    f"La sarta excede la profundidad de la mecha en {abs(diferencia):,.0f} ft."
                )
    if bit_depth_ft <= 0:
        avisos.append("La profundidad de la mecha es 0. Captúrala en la pestaña 1 (General).")
    if fondo_hoyo_ft > 0 and bit_depth_ft > fondo_hoyo_ft + 1.0:
        avisos.append("La mecha está más profunda que el fondo del hoyo registrado.")

    return {
        'secciones': secciones,
        'totales': {
            'longitud_sarta_ft': round(longitud_sarta, 2),
            'tope_sarta_ft': round(tope_sarta, 2),
            'bit_depth_ft': round(bit_depth_ft, 2),
            'fondo_hoyo_ft': round(fondo_hoyo_ft, 2),
            'volumen_sarta_bbl': round(total_ds, 2),
            'volumen_anular_bbl': round(total_anular, 2),
            'volumen_bajo_mecha_bbl': round(total_bajo_mecha, 2),
            'volumen_total_bbl': round(volumen_total, 2),
            'desplazamiento_bbl': round(total_desplazamiento, 2),
            'bottom_up_emboladas': round(bottom_up_stks, 0),
            'bottom_up_minutos': round(bottom_up_min, 1),
            'bbl_por_embolada': round(bbl_por_embolada, 5),
            'caudal_gpm': round(caudal_gpm, 1),
        },
        'avisos': avisos,
    }
