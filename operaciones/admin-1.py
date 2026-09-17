from django.contrib import admin
from .models import Producto, Pozo, PropiedadUnidadPozo, CategoriaPerdidaItem


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'categoria', 'unidad', 'cantidad', 'costo', 'estado')
    list_filter = ('categoria', 'estado')
    search_fields = ('codigo', 'descripcion')
    ordering = ('codigo',)


class PropiedadUnidadPozoInline(admin.TabularInline):
    model = PropiedadUnidadPozo
    extra = 0
    fields = ('propiedad', 'unidad')
    # Solo tiene sentido editar esto mientras el pozo está en borrador;
    # una vez activo, las unidades quedan bloqueadas a nivel de negocio.


class CategoriaPerdidaItemInline(admin.TabularInline):
    model = CategoriaPerdidaItem
    extra = 0
    fields = ('codigo', 'descripcion', 'tipo')


@admin.register(Pozo)
class PozoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'estado', 'sistema_unidades', 'unidades_bloqueadas',
        'paso_wizard_actual', 'pozo_plantilla', 'created_at',
    )
    list_filter = ('estado', 'sistema_unidades', 'categoria_perdida_tipo')
    search_fields = ('nombre',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PropiedadUnidadPozoInline, CategoriaPerdidaItemInline]

    fieldsets = (
        ("Identificación", {
            'fields': ('nombre', 'pozo_plantilla', 'estado', 'paso_wizard_actual')
        }),
        ("Unidades", {
            'fields': ('sistema_unidades', 'unidades_bloqueadas')
        }),
        ("Financiero", {
            'fields': (
                'moneda_simbolo', 'moneda_decimales', 'tasa_impuesto',
                'ecuacion_solidos_base_agua', 'ecuacion_solidos_base_aceite',
                'categoria_perdida_tipo',
            )
        }),
        ("Spud Date (pantalla única)", {
            'fields': (
                'spud_date_completado', 'fecha_primera_captura',
                'tipo_fluido_inicial', 'con_tratamiento_disposicion',
                'numero_control_logit',
            )
        }),
        ("Auditoría", {
            'fields': ('creado_por', 'created_at', 'updated_at')
        }),
    )


@admin.register(PropiedadUnidadPozo)
class PropiedadUnidadPozoAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'propiedad', 'unidad')
    list_filter = ('propiedad',)
    search_fields = ('pozo__nombre',)


@admin.register(CategoriaPerdidaItem)
class CategoriaPerdidaItemAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'codigo', 'descripcion', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('pozo__nombre', 'descripcion')
    ordering = ('pozo', 'codigo')
