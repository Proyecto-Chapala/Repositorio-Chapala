"""Datos que necesitan todas las pantallas (barra lateral, buscador Ctrl+K y selector de pozo)."""

from django.db.models import Count, F, Max

from .models import Pozo
from .navegacion import PANTALLAS_INFO_POZO, pantallas_del_pozo


def pozos_barra_lateral(request):
    """Pozos para el buscador Ctrl+K y el selector de pozo, con cantidad y fecha del último reporte.

    Primero el pozo con el reporte más reciente; los que no tienen reportes van al final.
    En las pantallas de un pozo agrega también sus pantallas de configuración y el selector.
    """
    pozos = (Pozo.objects
             .annotate(cantidad_reportes=Count('reportes_diarios'),
                       ultimo_reporte=Max('reportes_diarios__fecha'))
             .order_by(F('ultimo_reporte').desc(nulls_last=True), 'nombre')
             .only('id', 'nombre'))
    contexto = {'pozos_barra_lateral': pozos, 'version_base': version_base()}

    ruta = getattr(request, 'resolver_match', None)
    pozo_id = ruta.kwargs.get('pk') if ruta else None
    if pozo_id and ruta.url_name in PANTALLAS_CON_POZO:
        contexto['pantallas_info_pozo'] = pantallas_del_pozo(pozo_id)
        contexto['selector_pozo'] = selector_pozo(pozo_id, ruta.url_name)
    return contexto


def selector_pozo(pozo_id, nombre_url):
    """Datos del selector de pozo de la barra superior.

    Al elegir otro pozo se abre la misma pantalla de ese pozo; desde un reporte diario
    (propio de cada pozo) se va a los reportes del otro pozo.
    """
    destino = DESTINO_AL_CAMBIAR_DE_POZO.get(nombre_url, nombre_url)
    return {
        'pozo_id': pozo_id,
        'destino': f'operaciones:{destino}',
        'pantalla': NOMBRE_PANTALLA.get(nombre_url, ''),
    }


def version_base():
    """Versión (?v=) de los CSS y JS que carga base.html: cambia solo cuando se edita alguno,
    así el navegador nunca mezcla archivos viejos de su caché con los nuevos."""
    from .views import _version_estaticos
    return _version_estaticos(*ESTATICOS_BASE)


ESTATICOS_BASE = (
    'operaciones/css/fuentes.css', 'operaciones/css/variables.css', 'operaciones/css/layout.css', 'operaciones/css/styles.css',
    'operaciones/css/pozos.css', 'operaciones/js/app.js', 'operaciones/js/pozos_lista.js',
)


# Pantallas cuyo `pk` es un pozo (las APIs con `pk` de productos o equipos no entran).
PANTALLAS_CON_POZO = {
    'pozo_main', 'daily_reports_hub', 'daily_reports_hub_alias', 'recap_pozo',
    'well_header', 'general_setup', 'casing_intervals', 'loss_setup', 'active_items',
    'benchmark_setup', 'pits', 'equipment_properties_setup', 'reporte_diario_detalle',
}

# Pantallas que no existen tal cual en otro pozo: a dónde ir al cambiar de pozo.
DESTINO_AL_CAMBIAR_DE_POZO = {
    'reporte_diario_detalle': 'daily_reports_hub',
    'daily_reports_hub_alias': 'daily_reports_hub',
}

# Nombre de la pantalla actual para la barra superior (después del pozo).
NOMBRE_PANTALLA = {
    **{nombre_url: etiqueta for nombre_url, etiqueta, _ in PANTALLAS_INFO_POZO},
    'daily_reports_hub': 'Reportes',
    'daily_reports_hub_alias': 'Reportes',
    'recap_pozo': 'Reporte final',
}
