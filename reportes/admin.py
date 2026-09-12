"""
Registro en el admin de Django de todos los modelos de la app 'reportes'.
Sirve como respaldo/gestión de bajo nivel — la interfaz principal para el
día a día es la SPA en /reportes/ (reportes/views.py + templates/reportes/).
"""

from django.contrib import admin

from .models import (
    CategoriaPerdida,
    CierreVolumetrico,
    Comentario,
    DistribucionTiempo,
    Equipo,
    Intervalo,
    InventarioItem,
    LecturaFosa,
    MuestraFluido,
    Pit,
    Pozo,
    Producto,
    PropiedadCatalogo,
    PropiedadSistema,
    PropiedadValor,
    ReporteDiario,
    SistemaFluido,
    TramoSarta,
    TransaccionFosa,
    TuberiaInstalada,
    UsoEquipo,
    UsoMaterial,
)


@admin.register(Pozo)
class PozoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre", "numero_logit", "operador", "ubicacion", "campo_area",
        "nombre_taladro", "fecha_spud", "unit_set", "es_offshore",
    )
    list_filter = ("unit_set", "es_offshore")
    search_fields = ("nombre", "numero_logit", "operador", "ubicacion")


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
    list_display = (
        "pozo", "numero", "modo_operativo", "tipo", "sistema_fluido", "estado",
        "profundidad_inicial", "profundidad_final", "es_sidetrack", "volumen_inicial",
    )
    list_filter = ("estado", "modo_operativo", "tipo", "sistema_fluido__categoria")
    search_fields = ("pozo__nombre",)
    inlines = [TuberiaInstaladaInline, CierreVolumetricoInline]


@admin.register(TuberiaInstalada)
class TuberiaInstaladaAdmin(admin.ModelAdmin):
    list_display = ("intervalo", "tipo", "longitud", "profundidad_tvd", "diametro_externo", "diametro_interno")
    list_filter = ("tipo",)


@admin.register(TramoSarta)
class TramoSartaAdmin(admin.ModelAdmin):
    list_display = ("reporte", "tipo", "es_principal", "longitud", "diametro_externo", "diametro_interno", "orden")
    list_filter = ("tipo", "es_principal")


@admin.register(Pit)
class PitAdmin(admin.ModelAdmin):
    list_display = ("pozo", "descripcion", "tipo", "capacidad", "es_transaccional")
    list_filter = ("tipo", "es_transaccional")
    search_fields = ("descripcion", "pozo__nombre")


@admin.register(CategoriaPerdida)
class CategoriaPerdidaAdmin(admin.ModelAdmin):
    list_display = ("pozo", "nombre", "modo_operativo", "dominio")
    list_filter = ("modo_operativo", "dominio")
    search_fields = ("nombre", "pozo__nombre")


@admin.register(CierreVolumetrico)
class CierreVolumetricoAdmin(admin.ModelAdmin):
    list_display = (
        "intervalo", "volumen_final", "volumen_no_fluido", "fosa_origen", "categoria_perdida",
        "usuario", "fecha_cierre",
    )
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


class TransaccionFosaInline(admin.TabularInline):
    model = TransaccionFosa
    extra = 0
    readonly_fields = ("intervalo", "hora_registro")


class LecturaFosaInline(admin.TabularInline):
    model = LecturaFosa
    extra = 0


class DistribucionTiempoInline(admin.TabularInline):
    model = DistribucionTiempo
    extra = 0


@admin.register(ReporteDiario)
class ReporteDiarioAdmin(admin.ModelAdmin):
    list_display = (
        "numero_reporte", "intervalo", "fecha", "actividad", "peso_lodo",
        "volumen_total_hoyo", "volumen_no_contabilizado", "horas_totales_distribucion",
    )
    list_filter = ("intervalo__pozo",)
    readonly_fields = ("numero_reporte",)
    inlines = [
        MuestraFluidoInline, InventarioItemInline, UsoMaterialInline, UsoEquipoInline,
        TransaccionFosaInline, LecturaFosaInline, DistribucionTiempoInline, ComentarioInline,
    ]


@admin.register(DistribucionTiempo)
class DistribucionTiempoAdmin(admin.ModelAdmin):
    list_display = ("reporte", "actividad", "horas", "orden")


@admin.register(TransaccionFosa)
class TransaccionFosaAdmin(admin.ModelAdmin):
    list_display = ("reporte", "tipo", "fosa_origen", "fosa_destino", "producto", "categoria_perdida", "volumen", "hora_registro")
    list_filter = ("tipo",)
    readonly_fields = ("intervalo", "volumen", "hora_registro")


@admin.register(LecturaFosa)
class LecturaFosaAdmin(admin.ModelAdmin):
    list_display = ("reporte", "fosa", "volumen_medido")


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
