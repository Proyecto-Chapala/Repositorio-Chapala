"""Datos que necesitan todas las pantallas (barra lateral y buscador Ctrl+K)."""

from django.db.models import Count, F, Max

from .models import Pozo
from .navegacion import pantallas_del_pozo


def pozos_barra_lateral(request):
    """Pozos para el buscador Ctrl+K, con cantidad y fecha del último reporte.

    Primero el pozo con el reporte más reciente; los que no tienen reportes van al final.
    En las pantallas de un pozo agrega también sus pantallas de configuración.
    """
    pozos = (Pozo.objects
             .annotate(cantidad_reportes=Count('reportes_diarios'),
                       ultimo_reporte=Max('reportes_diarios__fecha'))
             .order_by(F('ultimo_reporte').desc(nulls_last=True), 'nombre')
             .only('id', 'nombre'))
    contexto = {'pozos_barra_lateral': pozos}

    ruta = getattr(request, 'resolver_match', None)
    pozo_id = ruta.kwargs.get('pk') if ruta else None
    if pozo_id and ruta.url_name in PANTALLAS_CON_POZO:
        contexto['pantallas_info_pozo'] = pantallas_del_pozo(pozo_id)
    return contexto


# Pantallas cuyo `pk` es un pozo (las APIs con `pk` de productos o equipos no entran).
PANTALLAS_CON_POZO = {
    'pozo_main', 'daily_reports_hub', 'daily_reports_hub_alias', 'recap_pozo',
    'well_header', 'general_setup', 'casing_intervals', 'loss_setup', 'active_items',
    'benchmark_setup', 'pits', 'equipment_properties_setup', 'reporte_diario_detalle',
}
