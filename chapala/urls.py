"""
================================================================================
ENRUTADOR PRINCIPAL DEL PROYECTO CHAPALA
================================================================================
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reportes/', include('reportes.urls')),
    path('', include('mychapala.urls')),
]
