"""
================================================================================
ENRUTADOR PRINCIPAL DEL PROYECTO CHAPALA
================================================================================
"""

from django.contrib import admin
from django.urls import path, include
from chapala import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Vistas y APIs de Geometría y Contabilidad de Volumen
    path('geometria-volumen/', views.vista_geometria_volumen, name='geometria_volumen_root'),
    path('geometria-volumen/<int:reporte_id>/', views.vista_geometria_volumen, name='geometria_volumen_detalle_root'),
    path('api/geometria/', views.api_geometria, name='api_geometria_root'),
    path('api/geometria/<int:reporte_id>/', views.api_geometria, name='api_geometria_detalle_root'),
    path('api/volume-accounting/', views.api_volume_accounting, name='api_volume_accounting_root'),
    path('api/volume-accounting/<int:reporte_id>/', views.api_volume_accounting, name='api_volume_accounting_detalle_root'),
    path('api/transacciones-volumetricas/', views.api_transacciones_volumetricas, name='api_transacciones_volumetricas_root'),
    path('api/transacciones-volumetricas/<int:reporte_id>/', views.api_transacciones_volumetricas, name='api_transacciones_volumetricas_detalle_root'),
    path('api/desplazamientos/', views.api_desplazamientos, name='api_desplazamientos_root'),
    path('api/desplazamientos/<int:reporte_id>/', views.api_desplazamientos, name='api_desplazamientos_detalle_root'),
    path('api/calcular-formulas/', views.api_calcular_formulas, name='api_calcular_formulas_root'),

    path('reportes/', include('reportes.urls')),
    path('', include('mychapala.urls')),
]
