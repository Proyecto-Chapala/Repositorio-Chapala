from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'categoria', 'unidad', 'cantidad', 'costo', 'estado')
    list_filter = ('categoria', 'estado')
    search_fields = ('codigo', 'descripcion')
    ordering = ('codigo',)
