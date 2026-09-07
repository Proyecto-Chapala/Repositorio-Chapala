from django.contrib import admin

from .models import (
    CierreVolumetrico,
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
    UsoMaterial,
)


class TuberiaInstaladaInline(admin.TabularInline):
    model = TuberiaInstalada
    extra = 1


class CierreVolumetricoInline(admin.StackedInline):
    model = CierreVolumetrico
    extra = 0
    can_delete = False


@admin.register(Pozo)
class PozoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "operador", "ubicacion", "fecha_spud")
    search_fields = ("nombre", "operador")


@admin.register(SistemaFluido)
class SistemaFluidoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria")
    list_filter = ("categoria",)
    search_fields = ("nombre",)


@admin.register(Intervalo)
class IntervaloAdmin(admin.ModelAdmin):
    list_display = (
        "pozo", "numero", "sistema_fluido", "estado",
        "profundidad_inicial", "profundidad_final", "diametro",
    )
    list_filter = ("estado", "pozo", "sistema_fluido__categoria")
    ordering = ("pozo", "numero")
    inlines = [TuberiaInstaladaInline, CierreVolumetricoInline]

    def get_readonly_fields(self, request, obj=None):
        # Un intervalo cerrado no debería poder reabrirse a mano desde el admin.
        if obj and obj.esta_cerrado:
            return ("estado", "sistema_fluido", "profundidad_inicial", "profundidad_final", "diametro")
        return ()


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
    list_display = (
        "nombre", "codigo", "presentacion", "cantidad_unitaria", "unidad_medida",
        "tipo_empaque", "precio_unitario", "gravedad_especifica",
    )
    list_filter = ("unidad_medida", "tipo_empaque")
    search_fields = ("nombre", "codigo")


class InventarioItemInline(admin.TabularInline):
    model = InventarioItem
    extra = 1
    readonly_fields = ("cantidad_final", "libraje_final")


class UsoMaterialInline(admin.TabularInline):
    model = UsoMaterial
    extra = 1
    readonly_fields = ("hora_registro", "libraje_usado", "subtotal_costo")


class MuestraFluidoInline(admin.TabularInline):
    model = MuestraFluido
    extra = 1


@admin.register(ReporteDiario)
class ReporteDiarioAdmin(admin.ModelAdmin):
    list_display = ("numero_reporte", "intervalo", "fecha", "actividad", "peso_lodo")
    list_filter = ("intervalo__pozo", "fecha")
    ordering = ("-fecha",)
    readonly_fields = ("numero_reporte",)
    inlines = [InventarioItemInline, UsoMaterialInline, MuestraFluidoInline]


@admin.register(PropiedadCatalogo)
class PropiedadCatalogoAdmin(admin.ModelAdmin):
    list_display = ("orden", "codigo", "nombre", "unidad")
    search_fields = ("codigo", "nombre")
    ordering = ("orden",)


@admin.register(PropiedadSistema)
class PropiedadSistemaAdmin(admin.ModelAdmin):
    list_display = ("propiedad", "categoria_sistema", "obligatoria")
    list_filter = ("categoria_sistema", "obligatoria")
    ordering = ("categoria_sistema", "propiedad__orden")


class PropiedadValorInline(admin.TabularInline):
    model = PropiedadValor
    extra = 1


@admin.register(MuestraFluido)
class MuestraFluidoAdmin(admin.ModelAdmin):
    list_display = ("identificador", "reporte", "orden")
    list_filter = ("reporte__intervalo__pozo",)
    ordering = ("reporte", "orden")
    inlines = [PropiedadValorInline]


@admin.register(PropiedadValor)
class PropiedadValorAdmin(admin.ModelAdmin):
    list_display = ("muestra", "propiedad", "valor")
    list_filter = ("propiedad",)
    search_fields = ("propiedad__nombre",)
