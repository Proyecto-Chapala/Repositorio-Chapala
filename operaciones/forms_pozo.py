from django import forms
from .models import Pozo, PropiedadUnidadPozo, CategoriaPerdidaItem


class PozoPaso1Form(forms.ModelForm):
    """Paso 1 — Datos Básicos + plantilla."""

    class Meta:
        model = Pozo
        fields = ['nombre', 'pozo_plantilla']

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if not nombre:
            raise forms.ValidationError("El nombre del pozo es obligatorio.")
        qs = Pozo.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Ya existe un pozo con el nombre '{nombre}'.")
        return nombre

    def clean_pozo_plantilla(self):
        plantilla = self.cleaned_data.get('pozo_plantilla')
        if plantilla and plantilla.estado != 'ACTIVO':
            raise forms.ValidationError("Solo se puede usar como plantilla un pozo ACTIVO.")
        return plantilla


class PozoPaso2Form(forms.ModelForm):
    """Paso 2 — Sistema de Unidades (el detalle Custom se maneja aparte, por fila)."""

    class Meta:
        model = Pozo
        fields = ['sistema_unidades']

    def clean(self):
        cleaned = super().clean()
        if self.instance.unidades_bloqueadas:
            raise forms.ValidationError(
                "Las unidades de este pozo ya fueron confirmadas y no se pueden modificar."
            )
        return cleaned


class PropiedadUnidadPozoForm(forms.ModelForm):
    """Una fila de la tabla de unidades personalizadas (paso 2, modo Custom)."""

    class Meta:
        model = PropiedadUnidadPozo
        fields = ['propiedad', 'unidad']

    def clean(self):
        cleaned = super().clean()
        propiedad = cleaned.get('propiedad')
        unidad = cleaned.get('unidad')
        opciones = PropiedadUnidadPozo.OPCIONES_UNIDAD.get(propiedad, [])
        if opciones and unidad not in opciones:
            raise forms.ValidationError(
                f"'{unidad}' no es válida para {propiedad}. Opciones: {', '.join(opciones)}."
            )
        return cleaned


class PozoPaso3Form(forms.ModelForm):
    """Paso 3 — Financiero + tipo de categorías de pérdida."""

    class Meta:
        model = Pozo
        fields = [
            'moneda_simbolo', 'moneda_decimales', 'tasa_impuesto',
            'ecuacion_solidos_base_agua', 'ecuacion_solidos_base_aceite',
            'categoria_perdida_tipo',
        ]

    def clean_tasa_impuesto(self):
        tasa = self.cleaned_data['tasa_impuesto']
        if tasa < 0 or tasa > 100:
            raise forms.ValidationError("La tasa de impuesto debe estar entre 0 y 100.")
        return tasa

    def clean_moneda_decimales(self):
        dec = self.cleaned_data['moneda_decimales']
        if dec < 0 or dec > 4:
            raise forms.ValidationError("Los decimales de moneda deben estar entre 0 y 4.")
        return dec


class CategoriaPerdidaItemForm(forms.ModelForm):
    """Una fila de categoría de pérdida personalizada (paso 3, modo Custom)."""

    class Meta:
        model = CategoriaPerdidaItem
        fields = ['codigo', 'descripcion', 'tipo']


class PozoSpudDateForm(forms.ModelForm):
    """
    Pantalla única 'Spud Date' — aparece solo la primera vez que se
    abre un pozo ya creado (estado ACTIVO). fecha_primera_captura y
    tipo_fluido_inicial quedan INMUTABLES tras confirmar; el checkbox
    de tratamiento/disposición se puede modificar después en otra
    pantalla (no forma parte de este bloqueo).
    """

    class Meta:
        model = Pozo
        fields = [
            'fecha_primera_captura', 'tipo_fluido_inicial',
            'con_tratamiento_disposicion', 'numero_control_logit',
        ]
        widgets = {
            'fecha_primera_captura': forms.DateInput(format='%Y-%m-%d'),
        }

    def clean(self):
        cleaned = super().clean()
        if self.instance.spud_date_completado:
            raise forms.ValidationError(
                "Esta pantalla ya fue confirmada para este pozo y no se puede repetir."
            )
        if not cleaned.get('fecha_primera_captura'):
            raise forms.ValidationError({'fecha_primera_captura': "La fecha es obligatoria."})
        if not cleaned.get('tipo_fluido_inicial'):
            raise forms.ValidationError({'tipo_fluido_inicial': "El tipo de fluido es obligatorio."})
        return cleaned


# ============================================================
# Well Header Information (2 pestañas)
# ============================================================
from .models import WellHeaderInfo, IntervaloRevestimiento, TipoFosa, Fosa


class WellHeaderInfoForm(forms.ModelForm):
    """Tab 1 — Well Information."""

    class Meta:
        model = WellHeaderInfo
        exclude = ['pozo', 'completado', 'marketing_codes_completado', 'created_at', 'updated_at',
                   'primary_mud_type_codigo', 'primary_mud_type_descripcion',
                   'well_type_codigo', 'well_type_descripcion',
                   'contract_type_codigo', 'contract_type_descripcion',
                   'completion_fluid_type_codigo', 'completion_fluid_type_descripcion']
        widgets = {
            'spud_date': forms.DateInput(format='%Y-%m-%d'),
            'td_date': forms.DateInput(format='%Y-%m-%d'),
            'end_date': forms.DateInput(format='%Y-%m-%d'),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('es_offshore'):
            faltantes = []
            if cleaned.get('air_gap_ft') is None:
                faltantes.append("Air Gap")
            if cleaned.get('water_depth_ft') is None:
                faltantes.append("Water Depth")
            if cleaned.get('sea_floor_temp_f') is None:
                faltantes.append("Sea Floor Temp")
            if faltantes:
                raise forms.ValidationError(
                    "Los proyectos Offshore deben completar: " + ", ".join(faltantes) + "."
                )

            # El riser solo entra al perfil del pozo si tiene diámetro interno; sin él
            # los volúmenes anulares de ese tramo saldrían mal sin avisar.
            if cleaned.get('usa_riser'):
                riser_id = cleaned.get('riser_id_in')
                if riser_id is None or riser_id <= 0:
                    raise forms.ValidationError({
                        'riser_id_in': "Indica el diámetro interno del riser; sin él no se "
                                       "puede calcular el volumen anular de ese tramo."
                    })
                longitud = cleaned.get('riser_length_ft')
                if longitud is None or longitud <= 0:
                    # Se asume Altura Libre + Profundidad de Agua (mesa rotaria al lecho marino).
                    auto = (cleaned.get('air_gap_ft') or 0) + (cleaned.get('water_depth_ft') or 0)
                    if auto <= 0:
                        raise forms.ValidationError({
                            'riser_length_ft': "Indica la longitud del riser, o completa Altura "
                                               "Libre y Profundidad de Agua para deducirla."
                        })
        elif cleaned.get('usa_riser'):
            raise forms.ValidationError({
                'usa_riser': "El riser solo aplica a proyectos Offshore."
            })
        return cleaned


class MarketingCodesForm(forms.ModelForm):
    """Tab 2 — Marketing Codes."""

    class Meta:
        model = WellHeaderInfo
        fields = [
            'primary_mud_type_codigo', 'primary_mud_type_descripcion',
            'well_type_codigo', 'well_type_descripcion',
            'contract_type_codigo', 'contract_type_descripcion',
            'completion_fluid_type_codigo', 'completion_fluid_type_descripcion',
        ]


# ============================================================
# Well Casing Intervals (Cost)
# ============================================================

class IntervaloRevestimientoForm(forms.ModelForm):
    class Meta:
        model = IntervaloRevestimiento
        exclude = ['pozo', 'created_at', 'updated_at']

    def clean_comentarios_recap(self):
        texto = self.cleaned_data.get('comentarios_recap', '') or ''
        if len(texto) > 10000:
            raise forms.ValidationError("Máximo 10,000 caracteres.")
        return texto


# ============================================================
# Pit Information
# ============================================================

class FosaForm(forms.ModelForm):
    class Meta:
        model = Fosa
        fields = ['numero', 'descripcion', 'capacidad']


class TipoFosaForm(forms.ModelForm):
    class Meta:
        model = TipoFosa
        fields = ['codigo', 'descripcion']


# ============================================================
# Loss Setup (Configuración de Pérdidas) — pantalla independiente
# ============================================================
# Reutiliza CategoriaPerdidaItemForm, ya definido arriba.


# ============================================================
# General Setup — datos del pozo + Warehouse Code Setup +
# Time Distribution Setup
# ============================================================
from .models import AlmacenCodigo, TipoDistribucionTiempo


class GeneralSetupForm(forms.ModelForm):
    """Bloque principal de la pantalla 'Configuración General'."""

    class Meta:
        model = Pozo
        fields = [
            'tasa_impuesto', 'con_tratamiento_disposicion',
            'usar_api_5ta_edicion_hidraulica',
            'ecuacion_solidos_base_agua', 'ecuacion_solidos_base_aceite',
        ]

    def clean_tasa_impuesto(self):
        tasa = self.cleaned_data['tasa_impuesto']
        if tasa < 0 or tasa > 100:
            raise forms.ValidationError("La tasa de impuesto debe estar entre 0 y 100.")
        return tasa


class AlmacenCodigoForm(forms.ModelForm):
    class Meta:
        model = AlmacenCodigo
        fields = ['codigo', 'nombre']


class TipoDistribucionTiempoForm(forms.ModelForm):
    class Meta:
        model = TipoDistribucionTiempo
        fields = ['numero', 'descripcion', 'tipo']


# ============================================================
# Productos / Equipos / Mallas Activos
# ============================================================
from .models import ProductoActivoPozo, EquipoActivoPozo, MallaActivaPozo


class ProductoActivoPozoForm(forms.ModelForm):
    class Meta:
        model = ProductoActivoPozo
        fields = [
            'producto', 'abreviatura', 'unit_size', 'unidad', 'empaque', 'precio',
            'gravedad_especifica', 'calcular_concentracion', 'es_producto_mi',
            'grupo_producto', 'codigo_costo_diario', 'calcular_wmgt_conc',
            'categoria_costo_wmgt', 'categoria_costo_cf',
        ]


class EquipoActivoPozoForm(forms.ModelForm):
    class Meta:
        model = EquipoActivoPozo
        fields = ['equipo', 'numero_serie', 'descripcion', 'precio_renta', 'precio_standby']

    def clean_numero_serie(self):
        numero = self.cleaned_data['numero_serie'].strip()
        if not numero:
            raise forms.ValidationError("El número de serie es obligatorio.")
        return numero


class MallaActivaPozoForm(forms.ModelForm):
    class Meta:
        model = MallaActivaPozo
        fields = ['malla', 'precio', 'descuento_porcentaje']


# ============================================================
# Equipment Properties Setup
# ============================================================
from .models import (
    PropiedadEquipoTipo, EquipoPropiedadSeleccionada, EquipoPropiedadExtra,
    CentrifugaUnidadConfig,
)


class PropiedadEquipoTipoForm(forms.ModelForm):
    class Meta:
        model = PropiedadEquipoTipo
        fields = ['tipo_equipo', 'descripcion', 'unidad', 'orden']


class EquipoPropiedadSeleccionadaForm(forms.ModelForm):
    class Meta:
        model = EquipoPropiedadSeleccionada
        fields = ['tipo_equipo', 'propiedad']


class EquipoPropiedadExtraForm(forms.ModelForm):
    class Meta:
        model = EquipoPropiedadExtra
        fields = ['tipo_equipo', 'descripcion', 'unidad']


class CentrifugaUnidadConfigForm(forms.ModelForm):
    class Meta:
        model = CentrifugaUnidadConfig
        fields = ['unidad_flow_rate', 'unidad_mass']


# ============================================================
# Benchmark Setup
# ============================================================
from .models import ParametroBenchmark, BenchmarkSeleccionado, BenchmarkTarget


class ParametroBenchmarkForm(forms.ModelForm):
    class Meta:
        model = ParametroBenchmark
        fields = ['grupo', 'descripcion', 'unidad', 'tipo_fluido', 'tipo_dato']


class BenchmarkSeleccionadoForm(forms.ModelForm):
    class Meta:
        model = BenchmarkSeleccionado
        fields = ['parametro']


class BenchmarkTargetForm(forms.ModelForm):
    class Meta:
        model = BenchmarkTarget
        fields = ['parametro', 'intervalo', 'min_max', 'valor']
