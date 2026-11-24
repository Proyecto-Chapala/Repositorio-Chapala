from decimal import Decimal

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
        qs = Pozo.todos.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        existente = qs.first()
        if existente and existente.en_papelera:
            raise forms.ValidationError(
                f"Ya existe un pozo '{nombre}' en la papelera. Restáuralo desde Pozos › Papelera o usa otro nombre.")
        if existente:
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

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo is not None and codigo <= 0:
            raise forms.ValidationError("El código debe ser un entero positivo mayor a cero.")
        return codigo


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


class PozoModificarForm(forms.Form):
    """
    Matriz de modificación del pozo: permite corregir errores cometidos
    durante la creación (Wizard pasos 1-3 y Spud Date).
    """
    # Identificación básica
    nombre = forms.CharField(max_length=150, required=True, label="Nombre del Pozo")
    operador = forms.CharField(max_length=120, required=False, label="Operador")
    field_area = forms.CharField(max_length=120, required=False, label="Campo / Área")
    nombre_taladro = forms.CharField(max_length=120, required=False, label="Nombre del Taladro")
    contratista = forms.CharField(max_length=120, required=False, label="Contratista")

    # Sistema de unidades
    sistema_unidades = forms.ChoiceField(
        choices=Pozo.SISTEMA_UNIDADES_CHOICES,
        label="Sistema de Unidades"
    )

    # Financiero y monedas
    moneda_simbolo = forms.CharField(max_length=10, required=True, label="Moneda Principal")
    moneda_decimales = forms.IntegerField(min_value=0, max_value=4, initial=2, label="Decimales de Moneda")
    tasa_impuesto = forms.DecimalField(min_value=0, max_value=100, decimal_places=2, initial=0, label="Tasa de Impuesto (%)")
    moneda_secundaria = forms.CharField(max_length=10, required=False, label="Segunda Moneda")
    cobrar_en_secundaria = forms.BooleanField(required=False, label="Cobrar en Segunda Moneda")

    # Datos iniciales (Spud Date)
    spud_date = forms.DateField(required=False, label="Fecha Inicial / Spud Date", widget=forms.DateInput(format='%Y-%m-%d'))
    tipo_fluido_inicial = forms.ChoiceField(
        choices=[('', '— Sin definir —')] + list(Pozo.TIPO_FLUIDO_INICIAL_CHOICES),
        required=False,
        label="Tipo de Fluido Inicial"
    )
    con_tratamiento_disposicion = forms.BooleanField(required=False, label="Con Tratamiento y Disposición")
    numero_control_logit = forms.CharField(max_length=50, required=False, label="N° de Control Log-It")

    # Categorías de pérdida
    categoria_perdida_tipo = forms.ChoiceField(
        choices=Pozo.CATEGORIA_PERDIDA_CHOICES,
        label="Categorías de Pérdida"
    )

    def __init__(self, *args, **kwargs):
        self.pozo = kwargs.pop('pozo', None)
        super().__init__(*args, **kwargs)
        if self.pozo and self.pozo.reportes_diarios.exists():
            self.fields['moneda_simbolo'].required = False

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if not nombre:
            raise forms.ValidationError("El nombre del pozo es obligatorio.")
        qs = Pozo.todos.filter(nombre__iexact=nombre)
        if self.pozo:
            qs = qs.exclude(pk=self.pozo.pk)
        existente = qs.first()
        if existente and existente.en_papelera:
            raise forms.ValidationError(
                f"Ya existe un pozo '{nombre}' en la papelera. Restáuralo desde Pozos › Papelera o usa otro nombre."
            )
        if existente:
            raise forms.ValidationError(f"Ya existe un pozo con el nombre '{nombre}'.")
        return nombre

    def clean_moneda_simbolo(self):
        return (self.cleaned_data.get('moneda_simbolo') or '').strip().upper()

    def clean_moneda_secundaria(self):
        return (self.cleaned_data.get('moneda_secundaria') or '').strip().upper()

    def clean(self):
        cleaned = super().clean()
        moneda_sec = cleaned.get('moneda_secundaria')
        cobrar_sec = cleaned.get('cobrar_en_secundaria')
        moneda_pri = (cleaned.get('moneda_simbolo') or (self.pozo.moneda_simbolo if self.pozo else '')).strip().upper()

        if cobrar_sec and not moneda_sec:
            raise forms.ValidationError({
                'moneda_secundaria': "Para cobrar en la segunda moneda debes indicar el código de la moneda."
            })
        if moneda_sec and moneda_sec == moneda_pri:
            self.add_error('moneda_secundaria', "La segunda moneda debe ser distinta a la moneda del pozo.")

        if self.pozo and self.pozo.reportes_diarios.exists():
            # Si el campo vino omitido (input disabled en frontend), conservar la moneda del pozo
            if not cleaned.get('moneda_simbolo'):
                cleaned['moneda_simbolo'] = self.pozo.moneda_simbolo
            elif cleaned.get('moneda_simbolo') != self.pozo.moneda_simbolo:
                self.add_error('moneda_simbolo', "El pozo ya tiene reportes registrados: la moneda principal no se puede modificar.")

            # Si el checkbox vino en el POST, validar que no cambie la moneda de cobro
            if 'cobrar_en_secundaria' in self.data:
                nuevo_cobro = bool(cleaned.get('cobrar_en_secundaria'))
                if nuevo_cobro != self.pozo.cobrar_en_secundaria:
                    self.add_error(
                        'cobrar_en_secundaria',
                        f"El pozo ya tiene reportes diarios y cobra en {self.pozo.moneda_cobro}: "
                        "la moneda de cobro no se puede cambiar."
                    )
            else:
                cleaned['cobrar_en_secundaria'] = self.pozo.cobrar_en_secundaria

            # Validar que Spud Date no sea posterior al primer reporte existente
            spud = cleaned.get('spud_date')
            if spud:
                primer_rep = self.pozo.reportes_diarios.order_by('fecha').first()
                if primer_rep and spud > primer_rep.fecha:
                    self.add_error(
                        'spud_date',
                        f"La fecha inicial ({spud.strftime('%d/%m/%Y')}) no puede ser posterior a la fecha del primer reporte diario ({primer_rep.fecha.strftime('%d/%m/%Y')})."
                    )

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

        nueva_spud = cleaned.get('spud_date')
        if nueva_spud and hasattr(self.instance, 'pozo') and self.instance.pozo_id:
            primer_reporte = self.instance.pozo.reportes_diarios.order_by('fecha').first()
            if primer_reporte and nueva_spud > primer_reporte.fecha:
                raise forms.ValidationError({
                    'spud_date': (
                        f"La fecha de inicio / Spud Date ({nueva_spud.strftime('%d/%m/%Y')}) no puede ser posterior "
                        f"al primer reporte diario existente ({primer_reporte.fecha.strftime('%d/%m/%Y')})."
                    )
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
        # 'cerrado' solo cambia con los botones Cerrar / Reabrir intervalo
        exclude = ['pozo', 'created_at', 'updated_at', 'cerrado']

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

    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if numero is not None and numero <= 0:
            raise forms.ValidationError("El número de fosa debe ser un entero positivo mayor a cero.")
        return numero

    def clean_capacidad(self):
        capacidad = self.cleaned_data.get('capacidad')
        if capacidad is not None and capacidad < 0:
            raise forms.ValidationError("La capacidad no puede ser negativa.")
        return capacidad


class TipoFosaForm(forms.ModelForm):
    class Meta:
        model = TipoFosa
        fields = ['codigo', 'descripcion']

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo is not None and codigo < 0:
            raise forms.ValidationError("El código no puede ser negativo.")
        return codigo


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
            'moneda_simbolo', 'moneda_secundaria', 'cobrar_en_secundaria',
            'tasa_impuesto', 'con_tratamiento_disposicion',
            'usar_api_5ta_edicion_hidraulica',
            'ecuacion_solidos_base_agua', 'ecuacion_solidos_base_aceite',
        ]

    def clean_moneda_simbolo(self):
        simbolo = (self.cleaned_data.get('moneda_simbolo') or '').strip().upper()
        if not simbolo:
            raise forms.ValidationError("Indica la moneda del pozo.")
        return simbolo

    def clean_tasa_impuesto(self):
        tasa = self.cleaned_data['tasa_impuesto']
        if tasa < 0 or tasa > 100:
            raise forms.ValidationError("La tasa de impuesto debe estar entre 0 y 100.")
        return tasa

    def clean(self):
        """
        Los nombres de las monedas se pueden corregir, pero la elección de en cuál se cobra no
        cambia cuando el pozo ya tiene reportes: los movimientos guardan el precio del momento y
        los costos viejos quedarían en otra moneda.
        """
        datos = super().clean()
        segunda = (datos.get('moneda_secundaria') or '').strip().upper()
        datos['moneda_secundaria'] = segunda
        if not segunda:
            datos['cobrar_en_secundaria'] = False
        elif segunda == (datos.get('moneda_simbolo') or '').strip().upper():
            self.add_error('moneda_secundaria', "La segunda moneda debe ser distinta a la moneda del pozo.")

        pozo = self.instance
        if (pozo.pk and bool(datos.get('cobrar_en_secundaria')) != pozo.cobrar_en_secundaria
                and pozo.reportes_diarios.exists()):
            self.add_error('cobrar_en_secundaria',
                           f"El pozo ya tiene reportes y cobra en {pozo.moneda_cobro}: "
                           "la moneda de cobro no se puede cambiar.")
        return datos


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
            'producto', 'abreviatura', 'unit_size', 'unidad', 'empaque', 'precio', 'precio_secundaria', 'cobro_por',
            'gravedad_especifica', 'calcular_concentracion', 'es_producto_mi',
            'grupo_producto', 'codigo_costo_diario', 'calcular_wmgt_conc',
            'categoria_costo_wmgt', 'categoria_costo_cf',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cobro_por'].required = False

    def clean_cobro_por(self):
        """Si no se indica, se cobra por unidad (como se hacía antes de existir el campo)."""
        return self.cleaned_data.get('cobro_por') or ProductoActivoPozo.COBRO_UNIDAD

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio

    def clean_precio_secundaria(self):
        precio = self.cleaned_data.get('precio_secundaria')
        if precio is not None and precio < 0:
            raise forms.ValidationError("El precio en moneda secundaria no puede ser negativo.")
        return precio

    def clean(self):
        """
        Un producto medido en peso necesita tamaño de unidad y gravedad específica: sin ellos el
        volumen que aporta al fluido (lb / (350 × GE)) sale en cero y la volumetría no cuadra.
        """
        from .volumetria import se_mide_en_peso, barriles_por_unidad
        datos = super().clean()
        if se_mide_en_peso(datos.get('unidad')):
            if not datos.get('unit_size') or datos['unit_size'] <= 0:
                self.add_error('unit_size', "Falta el tamaño de unidad (lb por saco, tambor...).")
            if not datos.get('gravedad_especifica') or datos['gravedad_especifica'] <= 0:
                self.add_error('gravedad_especifica', "Falta la gravedad específica: sin ella no se calcula el volumen.")
        if (datos.get('cobro_por') == ProductoActivoPozo.COBRO_BARRIL and not self.errors
                and barriles_por_unidad(datos.get('unidad'), datos.get('unit_size'),
                                        datos.get('gravedad_especifica')) is None):
            self.add_error('cobro_por', "Para cobrar por barril la unidad tiene que ser de peso (lb, kg, t) "
                                        "o de volumen (bbl, gal, l), con su tamaño de unidad.")
        return datos


class TarifaSecundariaOpcionalMixin:
    """
    Las tarifas en la segunda moneda solo se llenan si el pozo tiene segunda moneda: si no vienen,
    quedan en 0. Cada formulario indica sus campos en CAMPOS_TARIFA_SECUNDARIA.
    """

    CAMPOS_TARIFA_SECUNDARIA = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.CAMPOS_TARIFA_SECUNDARIA:
            self.fields[campo].required = False

    def clean(self):
        datos = super().clean()
        for campo in self.CAMPOS_TARIFA_SECUNDARIA:
            if datos.get(campo) is None:
                datos[campo] = Decimal('0')
        return datos


class EquipoActivoPozoForm(TarifaSecundariaOpcionalMixin, forms.ModelForm):
    CAMPOS_TARIFA_SECUNDARIA = ('precio_renta_secundaria', 'precio_standby_secundaria')

    class Meta:
        model = EquipoActivoPozo
        fields = ['equipo', 'numero_serie', 'descripcion', 'precio_renta', 'precio_standby',
                  'precio_renta_secundaria', 'precio_standby_secundaria']

    def clean_numero_serie(self):
        numero = self.cleaned_data['numero_serie'].strip()
        if not numero:
            raise forms.ValidationError("El número de serie es obligatorio.")
        return numero

    def clean(self):
        datos = super().clean()
        for campo, label in [
            ('precio_renta', 'El precio de renta'),
            ('precio_standby', 'El precio de standby'),
            ('precio_renta_secundaria', 'El precio de renta secundaria'),
            ('precio_standby_secundaria', 'El precio de standby secundaria'),
        ]:
            val = datos.get(campo)
            if val is not None and val < 0:
                self.add_error(campo, f"{label} no puede ser negativo.")
        return datos


class MallaActivaPozoForm(TarifaSecundariaOpcionalMixin, forms.ModelForm):
    CAMPOS_TARIFA_SECUNDARIA = ('precio_secundaria',)

    class Meta:
        model = MallaActivaPozo
        fields = ['malla', 'precio', 'precio_secundaria', 'descuento_porcentaje']

    def clean(self):
        datos = super().clean()
        for campo, label in [
            ('precio', 'El precio'),
            ('precio_secundaria', 'El precio en moneda secundaria'),
        ]:
            val = datos.get(campo)
            if val is not None and val < 0:
                self.add_error(campo, f"{label} no puede ser negativo.")
        desc = datos.get('descuento_porcentaje')
        if desc is not None and (desc < 0 or desc > 100):
            self.add_error('descuento_porcentaje', "El descuento debe estar entre 0 y 100%.")
        return datos


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
