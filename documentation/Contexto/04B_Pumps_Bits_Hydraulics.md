# Módulo 4B: Bombas, Mechas, Parámetros de Perforación e Hidráulica (Pumps / Bits / Hydraulics)
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / View Daily Information (Pumps/Bits Tab & Hydraulics Engine)
**Referencia:** Manual ONE-TRAX 2.0 (Sección 4.4, Páginas 74-77), Manual de Fórmulas y Mud Report 16 PERLA-1X

---

## 1. Propósito y Alcance del Módulo

La pestaña **Pumps/Bits Tab** captura los parámetros mecánicos del equipo de bombeo, la mecha instalada en el BHA, las condiciones operativas de perforación (WOB, RPM, ROP, presiones y temperaturas) y las pérdidas de carga en superficie. 

Estos datos son el insumo directo del **Motor de Hidráulica (Hydraulics Engine)** de ONE-TRAX para calcular:
1. Gasto volumétrico total ($Q$) en GPM y bbl/min.
2. Tiempos y emboladas de circulación (Superficie a Mecha, Bottoms Up y Circulación Total).
3. Área total de flujo de boquillas (TFA) y variables de impacto en el fondo (HHP, HSI, Fuerza de Impacto).
4. Pérdidas de presión desglosadas (Superficie, Sarta, Herramientas de fondo MWD/Motor, Mecha y Espacio Anular).
5. Régimen de flujo (Número de Reynolds $AnnRe$, Velocidad Crítica $V_c$ y velocidad anular $AV$) por cada tramo de la geometría del hoyo.
6. Densidad Equivalente de Circulación ($ECD$) y Eficiencia de Limpieza del Hoyo ($HCI$).

---

## 2. Sección 4.4.1: Tabla de Datos de Bombas (Pump Data Table)

El sistema soporta hasta 4 bombas de lodo (Triplex o Duplex). En la mayoría de los reportes estándar (como el de PERLA-1X), se configuran activamente las Bombas 1 y 2.

### 2.1 Variables y Parámetros por Bomba
| Variable | Campo Técnico | Tipo | Unidad | Descripción / Regla de Negocio |
|---|---|---|---|---|
| `bomba_numero` | `pump_number` | Integer | - | Identificador de bomba (1, 2, 3 o 4). |
| `marca_modelo` | `make_model` | String | - | Catálogo seleccionable (ej. `NATIONAL 12P-160`, `GARDNER DENVER PZ-11`, `LEWCO W-1712`, `EMSCO FB-1600`) o ingreso manual. |
| `diametro_camisa` | `liner_size` | Decimal | pulgadas (in) | Diámetro interno de la camisa (ej. 6.000", 6.500", 7.000"). Al seleccionar modelo se precarga, pero es editable. |
| `longitud_carrera` | `stroke_length` | Decimal | pulgadas (in) | Carrera del pistón (ej. 12.000"). Al seleccionar modelo se precarga, pero es editable. |
| `diametro_vastago` | `rod_diameter` | Decimal | pulgadas (in) | Diámetro del vástago (solo para bombas Duplex de doble efecto, por defecto `0.00`). |
| `eficiencia_volumetrica` | `volumetric_efficiency` | Decimal | % | Eficiencia volumétrica del pistón. Por defecto **97.00%** ($0.97$). Rango válido: 80.00% a 100.00%. |
| `capacidad_embolada_bbl` | `output_bbl_stk` | Decimal | bbl/stk | **Calculado (Amarillo):** Barriles desplazados por embolada simple. |
| `capacidad_embolada_gal` | `output_gal_stk` | Decimal | gal/stk | **Calculado (Amarillo):** Galones desplazados por embolada simple ($= \text{bbl/stk} \times 42$). |
| `emboladas_por_minuto` | `spm` | Decimal | stk/min | Emboladas por minuto operadas en la bomba durante la circulación (0 a 180 SPM). |
| `presion_bomba` | `pump_pressure` | Decimal | psi | Presión de descarga en el manifold de la bomba (ej. 3,200 psi). |
| `gasto_gpm` | `flow_rate_gpm` | Decimal | GPM | **Calculado (Amarillo):** Gasto individual de la bomba en galones por minuto. |
| `gasto_bbl_min` | `flow_rate_bbl_min` | Decimal | bbl/min | **Calculado (Amarillo):** Gasto individual en barriles por minuto. |
| `conectada_al_riser` | `connected_to_riser` | Boolean | - | Flag condicional: **Solo activa si `es_offshore = True`**. Indica si la bomba alimenta la línea de booster del riser marino. |

### 2.2 Fórmulas Matemáticas de Bombeo

#### A. Capacidad por Embolada (Pump Displacement / Output)
Para bombas Triplex de simple efecto (estándar en la industria moderna):
$$PO_{\text{bbl/stk}} = 0.000243 \times d_L^2 \times L_S \times \left(\frac{\eta_v}{100}\right)$$

$$PO_{\text{gal/stk}} = PO_{\text{bbl/stk}} \times 42 = 0.010206 \times d_L^2 \times L_S \times \left(\frac{\eta_v}{100}\right)$$

*Donde:*
- $d_L$: Diámetro de camisa (`liner_size`) en pulgadas.
- $L_S$: Longitud de carrera (`stroke_length`) en pulgadas.
- $\eta_v$: Eficiencia volumétrica (`volumetric_efficiency`) en porcentaje (ej. 97).

*Ejemplo (PERLA-1X, Bomba National 12P-160 con camisa 6.5" y carrera 12"):*
$$PO_{\text{bbl/stk}} = 0.000243 \times (6.5)^2 \times 12 \times 0.97 = 0.000243 \times 42.25 \times 12 \times 0.97 = 0.11943\text{ bbl/stk}$$
$$PO_{\text{gal/stk}} = 0.11943 \times 42 = 5.016\text{ gal/stk}$$
*(Coincide con la celda exacta de 5.016 gal/emb de la hoja CALDRIL Check en PERLA-1X)*.

#### B. Gasto Total del Sistema (Total Flow Rate)
$$Q_{\text{GPM}} = \sum_{i=1}^{n} \left( PO_{\text{gal/stk}, i} \times \text{SPM}_i \right)$$

$$Q_{\text{bbl/min}} = \sum_{i=1}^{n} \left( PO_{\text{bbl/stk}, i} \times \text{SPM}_i \right) = \frac{Q_{\text{GPM}}}{42}$$

$$\text{Total SPM} = \sum_{i=1}^{n} \text{SPM}_i$$

#### C. Tiempos y Emboladas de Circulación (Circulation Hydraulics)
Cruzando los datos de bombas con los volúmenes del hoyo calculados en la pestaña `Geometry`:
1. **Superficie a Mecha (Surface to Bit):**
   $$\text{Strokes}_{\text{Surf-to-Bit}} = \frac{V_{\text{sarta\_interior}} (\text{bbl})}{PO_{\text{total\_promedio}} (\text{bbl/stk})}$$
   $$\text{Time}_{\text{Surf-to-Bit}} (\text{min}) = \frac{V_{\text{sarta\_interior}} (\text{bbl})}{Q_{\text{bbl/min}}}$$

2. **Fondo a Superficie (Bottoms Up):**
   $$\text{Strokes}_{\text{Bottoms-Up}} = \frac{V_{\text{anular}} (\text{bbl})}{PO_{\text{total\_promedio}} (\text{bbl/stk})}$$
   $$\text{Time}_{\text{Bottoms-Up}} (\text{min}) = \frac{V_{\text{anular}} (\text{bbl})}{Q_{\text{bbl/min}}}$$

3. **Circulación Total (Total Circulation):**
   $$\text{Strokes}_{\text{Total}} = \text{Strokes}_{\text{Surf-to-Bit}} + \text{Strokes}_{\text{Bottoms-Up}}$$
   $$\text{Time}_{\text{Total}} (\text{min}) = \text{Time}_{\text{Surf-to-Bit}} + \text{Time}_{\text{Bottoms-Up}}$$

---

## 3. Sección 4.4.2: Información de la Mecha (Bit Information Section)

### 3.1 Variables y Catálogo
- **`bit_number` (Número de Mecha):** Consecutivo entero (ej. Bit #1, #2, #3...). Lleva el recuento de mechas empleadas a lo largo de todo el proyecto.
- **`bit_size` (Diámetro de Mecha):** Tamaño nominal en pulgadas (ej. 26.000", 17.500", 12.250", 8.500"). **Heredado y sincronizado automáticamente** con el `bit_size` de la pestaña `General` y `Geometry`.
- **`bit_manufacturer` (Fabricante):** Selector con catálogo: `Smith Bits / Schlumberger`, `Baker Hughes`, `Halliburton / Security DBS`, `NOV ReedHycalog`, `Varel`, `Ulterra`, `National Oilwell Varco`, `Other`.
- **`bit_type` (Tipo de Mecha):** Selector: `PDC`, `Roller Cone (Tricona)`, `Bi-Center`, `Diamond Impregnated`, `Core Head`.
- **`bit_serial` / `bit_name` (Serial / Nombre):** Identificador alfanumérico grabado por el fabricante (ej. `MDS1616SS`, `FX65D`).
- **`jet_nozzles` (Boquillas / Chorros):** Hasta 5 tamaños fraccionales configurables, medidos en 32avos de pulgada ($1/32"$).

### 3.2 Configuración de Boquillas y Cálculo de TFA
Las boquillas se configuran como pares de `(Cantidad, Tamaño en 32avos)`:
- Ejemplo: Tres boquillas de $12/32"$ y dos de $13/32" \implies (3 \times 12) + (2 \times 13)$.

#### Fórmula de Área Total de Flujo (TFA - Total Flow Area):
$$\text{TFA} = \sum_{k=1}^{m} c_k \times \frac{\pi}{4} \left(\frac{d_k}{32}\right)^2 \quad (\text{in}^2)$$

*Equivalente simplificado:*
$$\text{TFA} = \frac{\pi}{4 \times 1024} \sum_{k=1}^{m} c_k \cdot d_k^2 = 0.00076699 \sum_{k=1}^{m} c_k \cdot d_k^2 \quad (\text{in}^2)$$

*Regla de Interfaz:*
- El usuario puede ingresar las boquillas y el sistema calcula automáticamente el `TFA` (mostrado con 4 decimales).
- Alternativamente, si no se conocen los tamaños individuales de boquillas, el usuario puede ingresar directamente el valor de `TFA` de la hoja de especificaciones de la mecha.

### 3.3 Dinámica de Fluidos en la Mecha (Jet Hydraulics)

#### A. Velocidad de Salida en Boquillas (Nozzle Velocity, $V_n$)
$$V_n = \frac{Q_{\text{GPM}}}{3.117 \times \text{TFA}} \quad (\text{ft/sec})$$

#### B. Caída de Presión en la Mecha (Bit Pressure Drop, $\Delta P_{\text{bit}}$)
$$\Delta P_{\text{bit}} = \frac{\rho \times Q_{\text{GPM}}^2}{10858 \times \text{TFA}^2} \quad (\text{psi})$$

*Donde:*
- $\rho$: Densidad del lodo activo (`mud_weight`) en lb/gal (ppg).
- $Q$: Gasto de bombeo en GPM.
- $\text{TFA}$: Área total de boquillas en $\text{in}^2$.
- $10858$: Constante estándar con coeficiente de descarga $C_d = 0.95$.

#### C. Potencia Hidráulica en la Mecha (Bit Hydraulic Horsepower, $HHP$)
$$HHP_{\text{bit}} = \frac{\Delta P_{\text{bit}} \times Q_{\text{GPM}}}{1714} \quad (\text{hp})$$

#### D. Potencia Hidráulica por Pulgada Cuadrada (HSI)
$$HSI = \frac{HHP_{\text{bit}}}{\frac{\pi}{4} \times D_{\text{bit}}^2} = \frac{1.2732 \times HHP_{\text{bit}}}{D_{\text{bit}}^2} \quad (\text{hp/in}^2)$$

*Criterio Operativo Industrial:*
- $HSI < 2.0$: Limpieza de fondo deficiente (riesgo de embolamiento de mecha / bit balling).
- $2.5 \le HSI \le 5.0$: Rango óptimo de perforación rotaria y PDC.
- $HSI > 6.0$: Alto riesgo de erosión prematura de la formación o de los cortadores.

#### E. Fuerza de Impacto del Chorro (Jet Impact Force, $F_{\text{impact}}$)
$$F_{\text{impact}} = 0.01823 \times C_d \times Q_{\text{GPM}} \times \sqrt{\rho \times \Delta P_{\text{bit}}} \quad (\text{lbf})$$
*(con $C_d = 0.95$, constante $\approx 0.01732$)*.

#### F. Porcentaje de Caída de Presión en la Mecha (% Bit Pressure Loss)
$$\% \Delta P_{\text{bit}} = \left(\frac{\Delta P_{\text{bit}}}{P_{\text{standpipe}}}\right) \times 100$$
*(Celda reportada en el renglón 56 de PERLA-1X, idealmente entre 50% y 65% para optimizar energía hidráulica en el fondo)*.

---

## 4. Sección 4.4.3: Parámetros de Perforación (Drilling Data Section)

Datos operativos transferidos habitualmente del reporte IADC o cabina de mud logging (Pason / Totco):

| Parámetro | Campo Técnico | Unidad | Rango Típico | Propósito |
|---|---|---|---|---|
| **WOB** | `weight_on_bit` | klbs ($10^3$ lb) | 0 a 80 | Peso sobre la mecha aplicado por la sarta. |
| **Rotary RPM** | `rotary_rpm` | rpm | 0 a 200 | Revoluciones por minuto de la mesa rotaria o Top Drive. |
| **Motor RPM** | `motor_rpm` | rpm | 0 a 300 | RPM adicionales generadas por el motor de fondo (PDM). |
| **Total RPM** | `total_rpm` | rpm | - | **Calculado:** $\text{Rotary RPM} + \text{Motor RPM}$. |
| **Rotary Torque** | `rotary_torque` | ft-lbs o psi | 0 a 30,000 | Torque de perforación en superficie. |
| **ROP** | `rate_of_penetration` | ft/hr | 0 a 250 | Velocidad de penetración instantánea o promedio del tramo. |
| **Standpipe Pressure** | `standpipe_pressure` | psi | 0 a 5,000 | Presión total en el tubo vertical (SPP). Punto de partida del balance de presiones. |
| **Choke / Casing Pressure** | `casing_pressure` | psi | 0 a 2,500 | Presión en el cabezal o choque (si aplica). |
| **Motor Differential Press** | `motor_diff_press` | psi | 0 a 1,000 | Caída de presión a través del motor de fondo bajo carga. |
| **MWD Pressure Drop** | `mwd_pressure_drop` | psi | 0 a 500 | Pérdida de carga a través de la herramienta de telemetría por pulsos de lodo. |
| **Surface Temperature** | `temp_surface` | °F o °C | 60 a 120 °F | Temperatura del lodo en la línea de flujo / presa de succión. |
| **BHCT** | `temp_bhct` | °F o °C | 100 a 350 °F | Temperatura de Circulación en Fondo (Bottomhole Circulating Temperature). Clave para reología HTHP. |

---

## 5. Sección 4.4.4: Pérdidas de Presión en Superficie (Extra Pressure Loss Information)

El equipo superficial (standpipe, manguera de perforación, unión giratoria / Top Drive y kelly) genera una pérdida de presión por fricción antes de que el lodo ingrese a la sarta.

### 5.1 Catálogo de Códigos de Superficie (Surface Equipment Codes)
ONE-TRAX estandariza 4 configuraciones mecánicas API:

| Código | Standpipe | Kelly Hose | Swivel / Top Drive | Kelly / Pipe Saver | Longitud Equivalente ($L_{\text{eq}}$) |
|---|---|---|---|---|---|
| **Code 1** | 40 ft (3.5" ID) | 45 ft (2.0" ID) | 4 ft (2.0" ID) | 40 ft (2.25" ID) | Alta restricción (taladros pequeños) |
| **Code 2** | 40 ft (3.5" ID) | 55 ft (2.5" ID) | 5 ft (2.5" ID) | 40 ft (3.25" ID) | Restricción media |
| **Code 3** | 45 ft (4.0" ID) | 55 ft (3.0" ID) | 5 ft (2.5" ID) | 40 ft (3.25" ID) | Típico taladro moderno de 1,500 HP |
| **Code 4** | 45 ft (4.0" ID) | 55 ft (3.0" ID) | 6 ft (3.0" ID) | 40 ft (4.00" ID) | Baja restricción (taladros de 2,000-3,000 HP / Deepwater) |
| **User Defined** | Personalizado | Personalizado | Personalizado | Personalizado | Campo `surface_loss_psi` editable libremente |

*Regla de Interfaz:*
- Si se selecciona `Code 1`, `Code 2`, `Code 3` o `Code 4`, el campo `surface_loss_psi` queda bloqueado en solo lectura y se autocalcula en función del gasto $Q$ y densidad $\rho$:
  $$\Delta P_{\text{surface}} = c_{\text{code}} \times \rho^{0.8} \times Q^{1.8} \times \mu_p^{0.2}$$
- Si se selecciona `User Defined`, el campo se habilita en fondo blanco para ingreso manual de psi.

---

## 6. Sección 4.4.5: Resultados Hidráulicos del Hoyo (Hydraulic Results)

Al pulsar el botón **`Calculate Hydraulics`**, el sistema cruza los datos de esta pestaña con la sarta de tubería (`TramoSarta`), las tuberías instaladas (`TuberiaInstalada`), la reología activa (`MuestraFluido`) y calcula el perfil hidráulico tramo a tramo.

### 6.1 Desglose de Caída de Presión en el Sistema
$$P_{\text{total}} = \Delta P_{\text{surface}} + \Delta P_{\text{sarta}} + \Delta P_{\text{motor/MWD}} + \Delta P_{\text{bit}} + \Delta P_{\text{anular}}$$

Todas las 5 celdas anteriores se muestran con **fondo amarillo (solo lectura)** en la ventana de resultados de hidráulica.

### 6.2 Velocidad Anular ($AV$) y Regímenes de Flujo por Sección
Para cada tramo $j$ del espacio anular (entre el diámetro interno del hoyo/casing $D_{h, j}$ y el diámetro externo de la tubería $D_{po, j}$):

#### A. Velocidad Anular ($AV$):
$$AV_j = \frac{24.51 \times Q_{\text{GPM}}}{D_{h, j}^2 - D_{po, j}^2} \quad (\text{ft/min})$$

#### B. Número de Reynolds Anular ($AnnRe$):
Bajo el modelo plástico de Bingham:
$$AnnRe_j = \frac{2.96 \times \rho \times AV_j \times (D_{h, j} - D_{po, j})}{PV}$$

*Regla Lógica de Transición de Régimen:*
- **Si $AnnRe_j > 2000 \implies$ Flujo Turbulento (Turbulent Flow).**
- **Si $AnnRe_j \le 2000 \implies$ Flujo Laminar (Laminar Flow).**

#### C. Velocidad Crítica Anular ($AnnVCritical$):
Es la velocidad exacta a la que el fluido pasa de laminar a turbulento ($AnnRe = 2000$):
$$V_{c, j} = \frac{2000 \times PV}{2.96 \times \rho \times (D_{h, j} - D_{po, j})} \quad (\text{ft/min})$$

### 6.3 Densidad Equivalente de Circulación (ECD - Equivalent Circulating Density)
Refleja la presión total ejercida en el fondo del pozo durante la circulación (presión hidrostática + fricción anular):

$$ECD = \rho + \frac{\Delta P_{\text{anular}}}{0.052 \times TVD} \quad (\text{ppg})$$

*Donde:*
- $\rho$: Densidad del lodo estático en ppg.
- $\Delta P_{\text{anular}}$: Pérdida total de presión en el espacio anular (psi).
- $TVD$: Profundidad vertical verdadera de la mecha (ft).

### 6.4 Parámetros de Limpieza del Hoyo (Hole Cleaning & Transport Ratio)
En la sección `Hole Cleaning Parameters`, el usuario selecciona el tamaño representativo del ripio (`cuttings_size`):
- Opciones: `Fine (0.05 in)`, `Medium (0.15 in)`, `Coarse (0.25 in)`, `Large (0.50 in)`.
- El sistema calcula la **Velocidad de Deslizamiento del Ripio** ($V_s$ - Slip Velocity) usando las correlaciones de Chien / Moore.
- **Índice de Transporte (Transport Ratio, $TR$):**
  $$TR = \left(1 - \frac{V_s}{AV}\right) \times 100\%$$
- Criterio: $TR \ge 50\%$ garantiza remoción efectiva de ripios y previene empaquetamiento del hoyo.

---

## 7. Modelo de Datos Relacional para Implementación

Para almacenar fielmente la estructura de Pumps/Bits en la base de datos PostgreSQL del proyecto:

### 7.1 Modelo `BombaLodo` (`reportes_bombalodo`)
- `id`: UUID (PK).
- `reporte`: ForeignKey (`ReporteDiario`, on_delete=CASCADE, related_name="bombas").
- `numero_bomba`: Integer (1 a 4).
- `marca_modelo`: CharField(100) (ej. "NATIONAL 12P-160").
- `liner_size`: Decimal(5, 3) (pulgadas, ej. 6.500).
- `stroke_length`: Decimal(5, 2) (pulgadas, ej. 12.00).
- `eficiencia`: Decimal(5, 2) (default 97.00).
- `spm`: Decimal(5, 1) (default 0.0).
- `presion`: Decimal(6, 1) (psi, default 0.0).
- `conectada_al_riser`: Boolean (default False).
- `orden`: Integer (default 1).

### 7.2 Modelo `MechaPerforacion` (`reportes_mechaperforacion`)
- `id`: UUID (PK).
- `reporte`: OneToOneField (`ReporteDiario`, on_delete=CASCADE, related_name="mecha").
- `numero_mecha`: Integer (ej. 1).
- `diametro`: Decimal(6, 3) (pulgadas, ej. 26.000).
- `fabricante`: CharField(100).
- `tipo_mecha`: CharField(50) (PDC, Roller Cone, etc.).
- `serial`: CharField(80).
- `nozzles_config`: JSONField (ej. `[{"count": 3, "size": 12}, {"count": 2, "size": 13}]`).
- `tfa`: Decimal(6, 4) (in²).

### 7.3 Modelo `ParametrosPerforacion` (`reportes_parametrosperforacion`)
- `id`: UUID (PK).
- `reporte`: OneToOneField (`ReporteDiario`, on_delete=CASCADE, related_name="parametros_perforacion").
- `wob`: Decimal(6, 2) (klbs).
- `rotary_rpm`: Decimal(5, 1).
- `motor_rpm`: Decimal(5, 1) (default 0.0).
- `torque`: Decimal(7, 1) (ft-lbs).
- `rop`: Decimal(6, 2) (ft/hr).
- `standpipe_pressure`: Decimal(6, 1) (psi).
- `casing_pressure`: Decimal(6, 1) (psi, default 0.0).
- `motor_diff_press`: Decimal(6, 1) (psi, default 0.0).
- `mwd_pressure_drop`: Decimal(6, 1) (psi, default 0.0).
- `temp_superficie`: Decimal(5, 2) (°F).
- `temp_bhct`: Decimal(5, 2) (°F).
- `codigo_superficie`: CharField(20) (Choices: code_1, code_2, code_3, code_4, user_defined).
- `perdida_superficie_psi`: Decimal(6, 1) (psi).

---

## 8. Lógica de Herencia del Día Anterior (`Copy Data From Prior Day`)

Cuando el usuario crea el **Día $N$** con la opción activa `copiar_dia_anterior = True`:
1. **Bombas:** Se clonan las bombas activas del Día $N-1$ (mismo `marca_modelo`, `liner_size`, `stroke_length`, `eficiencia`). Los campos operativos instantáneos (`spm` y `presion`) se conservan como base pero el usuario puede actualizarlos.
2. **Mecha:** Si no se reportó cambio de mecha en la jornada anterior, se conserva el `numero_mecha`, `diametro`, `fabricante`, `tipo_mecha`, `serial`, boquillas y `tfa`.
3. **Parámetros:** Se copian el `codigo_superficie` y las temperaturas base.

---

## 9. Reglas Visuales y de Validación (UI Rules)

1. **Campos Calculados (Fondo Amarillo - Read-Only):**
   - `output_bbl_stk`, `output_gal_stk`, `flow_rate_gpm`, `flow_rate_bbl_min`.
   - `tfa` (cuando se ingresan boquillas fraccionales).
   - $\Delta P_{\text{surface}}$, $\Delta P_{\text{string}}$, $\Delta P_{\text{bit}}$, $\Delta P_{\text{annular}}$, $\Delta P_{\text{total}}$.
   - $V_n$, $HHP_{\text{bit}}$, $HSI$, $F_{\text{impact}}$, $ECD$.
2. **Campos Requeridos con Borde Rojo:**
   - Si una bomba tiene `spm > 0`, su `liner_size`, `stroke_length` y `eficiencia` son obligatorios (borde rojo si están vacíos o en 0).
   - `bit_size` y `tfa` son obligatorios para ejecutar el cálculo hidráulico.
   - `standpipe_pressure` es obligatorio para contrastar el cálculo teórico vs la medición real del manómetro.
3. **Alerta de Inconsistencia de Presión:**
   - Si $|\Delta P_{\text{total}} - P_{\text{standpipe}}| > 15\% \times P_{\text{standpipe}}$, se muestra una advertencia visual amarilla indicando discrepancia entre la presión calculada teórica y la presión medida en el standpipe.

