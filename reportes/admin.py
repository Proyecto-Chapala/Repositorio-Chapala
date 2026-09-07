"""
Registro en el admin de Django de todos los modelos de la app 'reportes'.
Sirve como respaldo/gestión de bajo nivel — la interfaz principal para el
día a día es la SPA en /reportes/ (reportes/views.py + templates/reportes/).
"""

from django.contrib import admin

from .models import (
    CierreVolumetrico,
    Comentario,
    Equipo,
    Intervalo,
    InventarioItem,
    MuestraFluido,
    Pozo,
    Producto,
    PropiedadCatalogo,
    PropiedadSistema,
    PropiedadValor,
    ReporteDiario,
    SistemaFluido,
    TuberiaInstalada,
    UsoEquipo,
    UsoMaterial,
)


@admin.register(Pozo)
class PozoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "operador", "ubicacion", "campo_area", "fecha_spud")
    search_fields = ("nombre", "operador", "ubicacion")


@admin.register(SistemaFluido)
class SistemaFluidoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria")
    list_filter = ("categoria",)
    search_fields = ("nombre",)


class TuberiaInstaladaInline(admin.TabularInline):
    model = TuberiaInstalada
    extra = 0


class CierreVolumetricoInline(admin.StackedInline):
    model = CierreVolumetrico
    extra = 0


@admin.register(Intervalo)
class IntervaloAdmin(admin.ModelAdmin):
    list_display = ("pozo", "numero", "sistema_fluido", "estado", "profundidad_inicial", "profundidad_final")
    list_filter = ("estado", "sistema_fluido__categoria")
    search_fields = ("pozo__nombre",)
    inlines = [TuberiaInstaladaInline, CierreVolumetricoInline]


@admin.register(TuberiaInstalada)
class TuberiaInstaladaAdmin(admin.ModelAdmin):
    list_display = ("intervalo", "tipo", "longitud", "diametro_externo", "diametro_interno")
    list_filter = ("tipo",)


@admin.register(CierreVolumetrico)
class CierreVolumetricoAdmin(admin.ModelAdmin):
    list_display = ("intervalo", "volumen_final", "volumen_no_fluido", "perdida_left_in_hole", "usuario", "fecha_cierre")
    readonly_fields = ("fecha_cierre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "cantidad_unitaria", "unidad_medida", "tipo_empaque", "precio_unitario", "gravedad_especifica")
    search_fields = ("codigo", "nombre")


class MuestraFluidoInline(admin.TabularInline):
    model = MuestraFluido
    extra = 0


class UsoMaterialInline(admin.TabularInline):
    model = UsoMaterial
    extra = 0
    readonly_fields = ("hora_registro",)


class InventarioItemInline(admin.TabularInline):
    model = InventarioItem
    extra = 0
    readonly_fields = ("cantidad_final",)


class UsoEquipoInline(admin.TabularInline):
    model = UsoEquipo
    extra = 0


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    readonly_fields = ("fecha_hora",)


@admin.register(ReporteDiario)
class ReporteDiarioAdmin(admin.ModelAdmin):
    list_display = ("numero_reporte", "intervalo", "fecha", "actividad", "peso_lodo")
    list_filter = ("intervalo__pozo",)
    readonly_fields = ("numero_reporte",)
    inlines = [MuestraFluidoInline, InventarioItemInline, UsoMaterialInline, UsoEquipoInline, ComentarioInline]


@admin.register(PropiedadCatalogo)
class PropiedadCatalogoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "unidad", "orden")
    search_fields = ("nombre", "codigo")


@admin.register(PropiedadSistema)
class PropiedadSistemaAdmin(admin.ModelAdmin):
    list_display = ("propiedad", "categoria_sistema", "obligatoria")
    list_filter = ("categoria_sistema",)


class PropiedadValorInline(admin.TabularInline):
    model = PropiedadValor
    extra = 0


@admin.register(MuestraFluido)
class MuestraFluidoAdmin(admin.ModelAdmin):
    list_display = ("identificador", "reporte", "orden")
    inlines = [PropiedadValorInline]


@admin.register(PropiedadValor)
class PropiedadValorAdmin(admin.ModelAdmin):
    list_display = ("muestra", "propiedad", "valor")
    list_filter = ("propiedad",)


@admin.register(InventarioItem)
class InventarioItemAdmin(admin.ModelAdmin):
    list_display = ("reporte", "producto", "cantidad_inicial", "cantidad_entrada", "cantidad_final")
    readonly_fields = ("cantidad_final",)


@admin.register(UsoMaterial)
class UsoMaterialAdmin(admin.ModelAdmin):
    list_display = ("reporte", "producto", "cantidad_usada", "hora_registro")
    readonly_fields = ("hora_registro",)


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "costo_diario")
    search_fields = ("codigo", "nombre")


@admin.register(UsoEquipo)
class UsoEquipoAdmin(admin.ModelAdmin):
    list_display = ("reporte", "equipo", "horas_usadas")


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("reporte", "autor", "fecha_hora")
    readonly_fields = ("fecha_hora",)
