# ============================================================
# CREAR: operaciones/forms_pozo.py
# ============================================================
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
