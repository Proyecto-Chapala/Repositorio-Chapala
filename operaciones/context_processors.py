"""Datos que necesitan todas las pantallas (barra lateral)."""

from django.db.models import Count, F, Max

from .models import Pozo


def pozos_barra_lateral(request):
    """Pozos para el panel "Reportes" de la barra lateral, con cantidad y fecha del último reporte.

    Primero el pozo con el reporte más reciente; los que no tienen reportes van al final.
    """
    pozos = (Pozo.objects
             .annotate(cantidad_reportes=Count('reportes_diarios'),
                       ultimo_reporte=Max('reportes_diarios__fecha'))
             .order_by(F('ultimo_reporte').desc(nulls_last=True), 'nombre')
             .only('id', 'nombre'))
    return {'pozos_barra_lateral': pozos}
