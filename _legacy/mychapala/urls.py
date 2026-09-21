"""
================================================================================
RUTAS DE LA APLICACIÓN MYCHAPALA
================================================================================
Enruta las vistas HTML y los endpoints de la API REST JSON:
- /                             -> Vista SPA principal
- /api/productos/               -> GET (listar) / POST (crear)
- /api/productos/<id>/          -> GET / PUT / DELETE
- /api/reporte-diario/          -> GET / POST (metadatos y observaciones)
- /api/registro-uso/            -> GET / POST (salida de producto, cálculo precio*cantidad)
- /api/registro-uso/<id>/       -> DELETE (eliminar salida y restituir stock)
- /api/reporte-oficial/         -> GET (datos para planilla imprimible)
================================================================================
"""

from django.urls import path
from . import views

urlpatterns = [
    # Vista principal
    path('', views.index, name='index'),

    # APIs de Productos (Inventario)
    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/productos/<int:pk>/', views.api_producto_detalle, name='api_producto_detalle'),

    # APIs de Reporte Diario (Sección General)
    path('api/reporte-diario/', views.api_reporte_diario, name='api_reporte_diario'),

    # APIs de Uso (Pestaña Uso y cálculo de costos)
    path('api/registro-uso/', views.api_registro_uso, name='api_registro_uso'),
    path('api/registro-uso/<int:pk>/', views.api_eliminar_uso, name='api_eliminar_uso'),

    # API para formato oficial imprimible e historial de reportes
    path('api/reporte-oficial/', views.api_reporte_oficial_data, name='api_reporte_oficial_data'),
    path('api/reportes-historial/', views.api_reportes_historial, name='api_reportes_historial'),
    path('api/reportes-historial/<int:pk>/', views.api_eliminar_reporte, name='api_eliminar_reporte'),
]

