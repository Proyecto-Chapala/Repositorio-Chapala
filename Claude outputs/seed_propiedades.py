"""
Seed de la Misión 4 — catálogo maestro de propiedades y su matriz de
aplicabilidad por categoría de SistemaFluido.

Extraído de las hojas MUD PROPERTIES del Mud Report 16 PERLA-1X:
WBM Check (agua), CALDRIL Check (agua), OBM Check (aceite), Synthetic-Based
Mud (sintético). La categoría "polimerico" reutiliza el catálogo de "agua"
(confirmado por el usuario: no hay hoja de referencia separada para polímeros).

Uso: correr una vez creada la app 'reportes' (Misión 0), como
management command o script equivalente a seed_data.py de Proyecto CHAPALA.
"""

from reportes.models import PropiedadCatalogo, PropiedadSistema, SistemaFluido

CATEGORIAS_AGUA = [SistemaFluido.Categoria.AGUA, SistemaFluido.Categoria.POLIMERICO]
CATEGORIAS_ACEITE_SINTETICO = [SistemaFluido.Categoria.ACEITE, SistemaFluido.Categoria.SINTETICO]
CATEGORIAS_TODAS = [
    SistemaFluido.Categoria.AGUA,
    SistemaFluido.Categoria.POLIMERICO,
    SistemaFluido.Categoria.ACEITE,
    SistemaFluido.Categoria.SINTETICO,
]

# (codigo, nombre, unidad, orden, [categorias que la habilitan])
PROPIEDADES = [
    # --- Comunes a todos los sistemas ---
    ("flowline_temp", "Flowline Temp", "°F", 10, CATEGORIAS_TODAS),
    ("mud_weight", "Peso del Lodo", "lb/gal", 20, CATEGORIAS_TODAS),
    ("mud_weight_temp", "Temp. de Muestra (Peso)", "°F", 21, CATEGORIAS_TODAS),
    ("funnel_viscosity", "Viscosidad de Embudo", "s/qt", 30, CATEGORIAS_TODAS),
    ("rheology_temp", "Temp. de Reología", "°F", 40, CATEGORIAS_TODAS),
    ("r600", "Lectura R600", "", 50, CATEGORIAS_TODAS),
    ("r300", "Lectura R300", "", 51, CATEGORIAS_TODAS),
    ("r200", "Lectura R200", "", 52, CATEGORIAS_TODAS),
    ("r100", "Lectura R100", "", 53, CATEGORIAS_TODAS),
    ("r6", "Lectura R6", "", 54, CATEGORIAS_TODAS),
    ("r3", "Lectura R3", "", 55, CATEGORIAS_TODAS),
    ("pv", "Viscosidad Plástica (PV)", "cP", 60, CATEGORIAS_TODAS),
    ("yp", "Punto Cedente (YP)", "lb/100ft²", 61, CATEGORIAS_TODAS),
    ("gel_10s", "Gel 10 seg", "lb/100ft²", 70, CATEGORIAS_TODAS),
    ("gel_10m", "Gel 10 min", "lb/100ft²", 71, CATEGORIAS_TODAS),
    ("gel_30m", "Gel 30 min", "lb/100ft²", 72, CATEGORIAS_TODAS),
    ("api_fluid_loss", "Filtrado API", "cc/30min", 80, CATEGORIAS_TODAS),
    ("hthp_fluid_loss", "Filtrado HTHP", "cc/30min", 81, CATEGORIAS_TODAS),
    ("cake_apt_ht", "Revoque APT/HT", '1/32"', 82, CATEGORIAS_TODAS),

    # --- Solo agua / polimérico (WBM / CALDRIL) ---
    ("solids_pct", "Sólidos", "%Vol", 90, CATEGORIAS_AGUA),
    ("oil_pct_agua", "Aceite (fase, %Vol)", "%Vol", 91, CATEGORIAS_AGUA),
    ("water_pct_agua", "Agua (fase, %Vol)", "%Vol", 92, CATEGORIAS_AGUA),
    ("sand_pct", "Arena", "%Vol", 93, CATEGORIAS_AGUA),
    ("mbt", "MBT", "lb/bbl", 94, CATEGORIAS_AGUA),
    ("ph", "pH", "", 95, CATEGORIAS_AGUA),
    ("ph_temp", "Temp. de pH", "°F", 96, CATEGORIAS_AGUA),
    ("alkal_mud_pm", "Alcalinidad Lodo (Pm)", "", 97, CATEGORIAS_AGUA),
    ("pf", "Alcalinidad Filtrado (Pf)", "", 98, CATEGORIAS_AGUA),
    ("mf", "Alcalinidad Filtrado (Mf)", "", 99, CATEGORIAS_AGUA),
    ("chlorides", "Cloruros", "mg/L", 100, CATEGORIAS_AGUA),
    ("hardness_ca", "Dureza (Ca++)", "mg/L", 101, CATEGORIAS_AGUA),

    # --- Solo aceite / sintético (OBM / SBM) ---
    ("unc_ret_solids_pct", "Sólidos Retenidos sin Corregir", "%Vol", 110, CATEGORIAS_ACEITE_SINTETICO),
    ("correct_solids_pct", "Sólidos Corregidos", "%Vol", 111, CATEGORIAS_ACEITE_SINTETICO),
    ("base_fluid_pct", "Fase Base (Aceite/Sintético, %Vol)", "%Vol", 112, CATEGORIAS_ACEITE_SINTETICO),
    ("uncorr_water_pct", "Agua sin Corregir", "%Vol", 113, CATEGORIAS_ACEITE_SINTETICO),
    ("base_ratio", "Relación Fase Base", "", 114, CATEGORIAS_ACEITE_SINTETICO),
    ("water_ratio", "Relación Agua", "", 115, CATEGORIAS_ACEITE_SINTETICO),
    ("alkal_mud_pom_psm", "Alcalinidad Lodo (Pom/Psm)", "", 116, CATEGORIAS_ACEITE_SINTETICO),
    ("cl_whole_mud", "Cl- Lodo Entero", "mg/L", 117, CATEGORIAS_ACEITE_SINTETICO),
    ("salt_pct", "Sal", "%Wt", 118, CATEGORIAS_ACEITE_SINTETICO),
    ("lime", "Cal", "lb/bbl", 119, CATEGORIAS_ACEITE_SINTETICO),
    ("emul_stability", "Estabilidad de Emulsión", "", 120, CATEGORIAS_ACEITE_SINTETICO),
]


def seed_propiedades():
    creadas = 0
    matriz_creada = 0
    for codigo, nombre, unidad, orden, categorias in PROPIEDADES:
        prop, created = PropiedadCatalogo.objects.update_or_create(
            codigo=codigo,
            defaults={"nombre": nombre, "unidad": unidad, "orden": orden},
        )
        if created:
            creadas += 1
        for categoria in categorias:
            _, m_created = PropiedadSistema.objects.update_or_create(
                propiedad=prop,
                categoria_sistema=categoria,
                defaults={"obligatoria": True},
            )
            if m_created:
                matriz_creada += 1

    print(f"Propiedades: {creadas} nuevas de {len(PROPIEDADES)} totales.")
    print(f"Entradas de matriz (PropiedadSistema): {matriz_creada} nuevas.")


if __name__ == "__main__":
    import os
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    seed_propiedades()
