
"""
================================================================================
RUTAS DE LA APP 'REPORTES' (ESQUEMA ONE-TRAX)
================================================================================
Montada bajo el prefijo /reportes/ en chapala/urls.py, para no chocar con
mychapala (que vive en la raíz '/'). Las dos apps conviven en el mismo
proyecto y comparten el mismo PostgreSQL.
================================================================================
"""

from django.urls import path

from . import views

urlpatterns = [
    # Vista SPA principal
    path("", views.index, name="reportes_index"),

    # Pozos
    path("api/pozos/", views.api_pozos, name="api_pozos"),
    path("api/pozos/<uuid:pk>/", views.api_pozo_detalle, name="api_pozo_detalle"),

    # Sistemas de fluido (catálogo editable / "gama de fluidos")
    path("api/sistemas-fluido/", views.api_sistemas_fluido, name="api_sistemas_fluido"),
    path("api/sistemas-fluido/<uuid:pk>/", views.api_sistema_fluido_detalle, name="api_sistema_fluido_detalle"),

    # Intervalos
    path("api/intervalos/", views.api_intervalos, name="api_intervalos"),
    path("api/intervalos/<uuid:pk>/", views.api_intervalo_detalle, name="api_intervalo_detalle"),
    path("api/intervalos/<uuid:pk>/cerrar/", views.api_cerrar_intervalo, name="api_cerrar_intervalo"),

    # Tubería instalada (revestidor / liner)
    path("api/tuberias/", views.api_tuberias, name="api_tuberias"),
    path("api/tuberias/<uuid:pk>/", views.api_tuberia_detalle, name="api_tuberia_detalle"),

    # Productos
    path("api/productos/", views.api_productos, name="api_productos_reportes"),
    path("api/productos/<uuid:pk>/", views.api_producto_detalle, name="api_producto_detalle_reportes"),

    # Reportes diarios
    path("api/reportes-diarios/", views.api_reportes_diarios, name="api_reportes_diarios"),
    path("api/reportes-diarios/<uuid:pk>/", views.api_reporte_diario_detalle, name="api_reporte_diario_detalle"),

    # Matriz de propiedades selectivas (Misión 4)
    path("api/propiedades-catalogo/", views.api_propiedades_catalogo, name="api_propiedades_catalogo"),
    path("api/muestras/", views.api_muestras, name="api_muestras"),
    path("api/muestras/<uuid:pk>/", views.api_muestra_detalle, name="api_muestra_detalle"),
    path("api/muestras/<uuid:pk>/valores/", views.api_guardar_valores_muestra, name="api_guardar_valores_muestra"),

    # Inventario y uso de material (por reporte diario)
    path("api/inventario-items/", views.api_inventario_items, name="api_inventario_items"),
    path("api/inventario-items/<uuid:pk>/", views.api_eliminar_inventario_item, name="api_eliminar_inventario_item"),
    path("api/uso-material/", views.api_uso_material, name="api_uso_material"),
    path("api/uso-material/<uuid:pk>/", views.api_eliminar_uso, name="api_eliminar_uso_reportes"),

    # Equipos (catálogo + uso por reporte diario)
    path("api/equipos/", views.api_equipos, name="api_equipos"),
    path("api/equipos/<uuid:pk>/", views.api_equipo_detalle, name="api_equipo_detalle"),
    path("api/uso-equipo/", views.api_uso_equipo, name="api_uso_equipo"),
    path("api/uso-equipo/<uuid:pk>/", views.api_eliminar_uso_equipo, name="api_eliminar_uso_equipo"),

    # Comentarios (por reporte diario)
    path("api/comentarios/", views.api_comentarios, name="api_comentarios"),
    path("api/comentarios/<uuid:pk>/", views.api_eliminar_comentario, name="api_eliminar_comentario"),
# Fosas y Transacciones
    path("api/fosas/", views.api_fosas, name="api_fosas"),
    path("api/fosas/<uuid:pk>/", views.api_fosa_detalle, name="api_fosa_detalle"),
    path("api/categorias-perdida/", views.api_categorias_perdida, name="api_categorias_perdida"),
    path("api/lecturas-fosa/", views.api_lecturas_fosa, name="api_lecturas_fosa"),
    path("api/lecturas-fosa/<uuid:pk>/", views.api_lectura_fosa_detalle, name="api_lectura_fosa_detalle"),
    path("api/transacciones-fosa/", views.api_transacciones_fosa, name="api_transacciones_fosa"),
    path("api/transacciones-fosa/<uuid:pk>/", views.api_transaccion_fosa_detalle, name="api_transaccion_fosa_detalle"),
    
    # Geometría
    path("api/geometrias-hoyo/", views.api_geometrias_hoyo, name="api_geometrias_hoyo"),
    path("api/geometrias-hoyo/<uuid:pk>/", views.api_geometria_hoyo_detalle, name="api_geometria_hoyo_detalle"),
]

