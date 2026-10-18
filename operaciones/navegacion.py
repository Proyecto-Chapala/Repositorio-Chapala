"""Pantallas de configuración del pozo, en un solo lugar.

Las usan la barra de configuración (pozos/_nav_info_pozo.html), el buscador Ctrl+K
y el tablero del pozo (pozos/main.html).
"""

from django.urls import reverse

# (nombre de la URL, etiqueta corta, ícono)
PANTALLAS_INFO_POZO = [
    ('well_header', 'Información general', 'i-reporte'),
    ('general_setup', 'Configuración general', 'i-ajustes'),
    ('casing_intervals', 'Intervalos de revestimiento', 'i-ajustes'),
    ('loss_setup', 'Pérdidas', 'i-ajustes'),
    ('active_items', 'Productos / equipos / mallas', 'i-inventario'),
    ('benchmark_setup', 'Benchmark', 'i-ajustes'),
    ('pits', 'Tanques', 'i-ajustes'),
    ('equipment_properties_setup', 'Propiedades de equipo', 'i-ajustes'),
]


def pantallas_del_pozo(pozo_id):
    """Las pantallas de configuración con su URL ya armada para un pozo."""
    return [{'nombre_url': nombre_url, 'etiqueta': etiqueta, 'icono': icono,
             'url': reverse(f'operaciones:{nombre_url}', args=[pozo_id])}
            for nombre_url, etiqueta, icono in PANTALLAS_INFO_POZO]


def estado_configuracion(pozo):
    """Qué pantallas del pozo ya tienen datos. None = la pantalla no tiene un "listo" medible."""
    cargado = {
        'well_header': bool(getattr(getattr(pozo, 'well_header_info', None), 'completado', False)),
        'casing_intervals': pozo.intervalos_revestimiento.exists(),
        'loss_setup': pozo.categorias_perdida.exists(),
        'active_items': pozo.productos_activos.exists(),
        'benchmark_setup': pozo.benchmarks_seleccionados.exists(),
        'pits': pozo.fosas.exists(),
    }
    pantallas = pantallas_del_pozo(pozo.pk)
    for pantalla in pantallas:
        pantalla['lista'] = cargado.get(pantalla['nombre_url'])
    return pantallas
