"""
================================================================================
ENRUTADOR PRINCIPAL DEL PROYECTO CHAPALA
================================================================================
"""

from django.contrib import admin
from django.urls import path, include

from operaciones.views_licencia import licencia_activar_view

urlpatterns = [
    path('licencia/', licencia_activar_view, name='licencia_activar'),
    path('admin/', admin.site.urls),
    path('', include('operaciones.urls')),
]

