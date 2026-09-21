"""
================================================================================
ADMINISTRACIÓN DJANGO - PROYECTO CHAPALA
================================================================================
Configuración del panel de administración de Django para los modelos:
- Producto
- ReporteDiario
- RegistroUso
================================================================================
"""

from django.contrib import admin
from .models import Producto, ReporteDiario, RegistroUso


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descripcion", "unidad", "libraje", "gravedad_especifica", "cantidad", "activo")
    search_fields = ("codigo", "descripcion", "unidad")
    list_filter = ("activo",)
    ordering = ("id",)


class RegistroUsoInline(admin.TabularInline):
    model = RegistroUso
    extra = 0
    fields = ("producto", "cantidad", "precio_unitario", "costo_total", "observacion", "fecha_hora")
    readonly_fields = ("costo_total", "fecha_hora")


@admin.register(ReporteDiario)
class ReporteDiarioAdmin(admin.ModelAdmin):
    list_display = ("fecha", "departamento", "encargado", "costo_total", "fecha_actualizacion")
    search_fields = ("departamento", "encargado", "observaciones")
    list_filter = ("fecha", "departamento")
    inlines = [RegistroUsoInline]


@admin.register(RegistroUso)
class RegistroUsoAdmin(admin.ModelAdmin):
    list_display = ("fecha_hora", "reporte", "producto", "cantidad", "precio_unitario", "costo_total")
    search_fields = ("producto__codigo", "producto__descripcion", "observacion")
    list_filter = ("reporte__fecha",)
