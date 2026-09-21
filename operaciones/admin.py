from django.contrib import admin
from .models import (
    Producto, Pozo, PropiedadUnidadPozo, CategoriaPerdidaItem,
    WellHeaderInfo, IntervaloRevestimiento, TipoFosa, Fosa,
    AlmacenCodigo, TipoDistribucionTiempo,
    Equipo, MallaZaranda, ProductoActivoPozo, EquipoActivoPozo, MallaActivaPozo,
    PropiedadEquipoTipo, EquipoPropiedadSeleccionada, EquipoPropiedadExtra,
    CentrifugaUnidadConfig, ParametroBenchmark, BenchmarkSeleccionado, BenchmarkTarget,
)


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


@admin.register(WellHeaderInfo)
class WellHeaderInfoAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'operador', 'es_offshore', 'completado', 'marketing_codes_completado')
    list_filter = ('es_offshore', 'completado', 'marketing_codes_completado')
    search_fields = ('pozo__nombre', 'operador', 'field_area')


@admin.register(IntervaloRevestimiento)
class IntervaloRevestimientoAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'numero_intervalo', 'tipo', 'profundidad_ft', 'interval_cost')
    list_filter = ('tipo',)
    search_fields = ('pozo__nombre',)
    ordering = ('pozo', 'numero_intervalo')


class FosaInline(admin.TabularInline):
    model = Fosa
    extra = 0
    fields = ('numero', 'descripcion', 'capacidad')


class TipoFosaInline(admin.TabularInline):
    model = TipoFosa
    extra = 0
    fields = ('codigo', 'descripcion')


@admin.register(Fosa)
class FosaAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'numero', 'descripcion', 'capacidad')
    search_fields = ('pozo__nombre', 'descripcion')
    ordering = ('pozo', 'numero')


@admin.register(TipoFosa)
class TipoFosaAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'codigo', 'descripcion')
    search_fields = ('pozo__nombre', 'descripcion')
    ordering = ('pozo', 'codigo')


@admin.register(AlmacenCodigo)
class AlmacenCodigoAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'codigo', 'nombre')
    search_fields = ('pozo__nombre', 'codigo', 'nombre')
    ordering = ('pozo', 'codigo')


@admin.register(TipoDistribucionTiempo)
class TipoDistribucionTiempoAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'numero', 'descripcion', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('pozo__nombre', 'descripcion')
    ordering = ('pozo', 'numero')


# ============================================================
# Productos / Equipos / Mallas Activos
# ============================================================

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')
    ordering = ('codigo',)


@admin.register(MallaZaranda)
class MallaZarandaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'mesh_size')
    search_fields = ('codigo', 'descripcion')
    ordering = ('mesh_size', 'codigo')


@admin.register(ProductoActivoPozo)
class ProductoActivoPozoAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'producto', 'abreviatura', 'precio', 'codigo_costo_diario')
    search_fields = ('pozo__nombre', 'producto__codigo', 'producto__descripcion')
    ordering = ('pozo', 'producto__codigo')


@admin.register(EquipoActivoPozo)
class EquipoActivoPozoAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'equipo', 'numero_serie', 'precio_renta', 'precio_standby')
    search_fields = ('pozo__nombre', 'equipo__codigo', 'numero_serie')
    ordering = ('pozo', 'equipo__codigo')


@admin.register(MallaActivaPozo)
class MallaActivaPozoAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'malla', 'precio', 'descuento_porcentaje')
    search_fields = ('pozo__nombre', 'malla__codigo')
    ordering = ('pozo', 'malla__mesh_size')


# ============================================================
# Equipment Properties Setup
# ============================================================

@admin.register(PropiedadEquipoTipo)
class PropiedadEquipoTipoAdmin(admin.ModelAdmin):
    list_display = ('tipo_equipo', 'descripcion', 'unidad', 'orden')
    list_filter = ('tipo_equipo',)
    search_fields = ('descripcion',)
    ordering = ('tipo_equipo', 'orden')


@admin.register(EquipoPropiedadSeleccionada)
class EquipoPropiedadSeleccionadaAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'tipo_equipo', 'propiedad')
    list_filter = ('tipo_equipo',)
    search_fields = ('pozo__nombre',)


@admin.register(EquipoPropiedadExtra)
class EquipoPropiedadExtraAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'tipo_equipo', 'descripcion', 'unidad')
    list_filter = ('tipo_equipo',)
    search_fields = ('pozo__nombre', 'descripcion')


@admin.register(CentrifugaUnidadConfig)
class CentrifugaUnidadConfigAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'unidad_flow_rate', 'unidad_mass')
    search_fields = ('pozo__nombre',)


# ============================================================
# Benchmark Setup
# ============================================================

@admin.register(ParametroBenchmark)
class ParametroBenchmarkAdmin(admin.ModelAdmin):
    list_display = ('grupo', 'descripcion', 'unidad', 'tipo_fluido', 'tipo_dato')
    list_filter = ('grupo', 'tipo_fluido', 'tipo_dato')
    search_fields = ('descripcion', 'grupo')
    ordering = ('grupo', 'descripcion')


@admin.register(BenchmarkSeleccionado)
class BenchmarkSeleccionadoAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'parametro')
    search_fields = ('pozo__nombre',)


@admin.register(BenchmarkTarget)
class BenchmarkTargetAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'parametro', 'intervalo', 'min_max', 'valor')
    list_filter = ('min_max',)
    search_fields = ('pozo__nombre',)
