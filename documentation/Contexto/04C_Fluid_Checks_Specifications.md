# Módulo 4C: Análisis de Fluido, Especificaciones y Control de Sólidos (Fluid Checks & Specifications)
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / View Daily Information (Fluid Checks Tab)
**Referencia:** Manual ONE-TRAX 2.0 (Sección 4.5, Páginas 78-92) y Mud Report 16 PERLA-1X

---

## 1. Arquitectura de Muestreo Diario (Multi-Check Framework)

En las operaciones de campo, las propiedades físico-químicas del lodo de perforación varían dinámicamente según la litología perforada, la tasa de penetración y las adiciones químicas. Por ello, ONE-TRAX permite capturar **múltiples chequeos de fluido por día (hasta 4 chequeos diarios)**, comúnmente distribuidos en horarios de guardia (ej. 00:00, 06:00, 12:00, 18:00) o por puntos de toma (Presa de Succión vs Línea de Flujo / Temblorinas).

### 1.1 Metadatos de la Muestra
Cada chequeo de fluido registra obligatoriamente:
- **`numero_muestra`:** Entero del 1 al 4 (Check 1, Check 2, Check 3, Check 4).
- **`hora_muestra`:** Hora exacta de toma de muestra (ej. `12:00`).
- **`origen_muestra` (`sample_from`):** Ubicación física de la toma. Opciones: `Suction Pit (Presa de Succión)`, `Flowline (Línea de Flujo)`, `Reserve Pit`, `Premix Pit`, `Active System`.
- **`profundidad_medida`:** Profundidad del hoyo al momento de la prueba (MD en ft).
- **`tvd_muestra`:** Profundidad vertical verdadera al momento de la prueba (TVD en ft).
- **`temperatura_flujo` (`flowline_temp`):** Temperatura del lodo en la línea de flujo (°F).

### 1.2 Regla del Control Primario (Primary Fluid Check)
De todos los chequeos registrados en la jornada:
1. **Unicidad:** Exactamente **un chequeo debe ser designado como el "Primary Fluid Check"** mediante el botón `Make Primary`.
2. **Impacto en Hidráulica:** La densidad (`mud_weight`), viscosidad plástica (`PV`), punto de cedencia (`YP`) y geles del **Primary Check** son los únicos que alimentan el cálculo de caídas de presión, velocidad anular, ECD y Reynolds en la pestaña `Pumps/Bits` y `Geometry`.
3. **Exportación Externa:** Únicamente las propiedades del Primary Check se exportan en los paquetes de enlace a operadoras (WITSML XML y OpenWells TXT).

---

## 2. Reología y Parámetros de Flujo (Rheology Section)

ONE-TRAX implementa el protocolo estándar API RP 13B-1 (WBM) y API RP 13B-2 (OBM/SBM) para viscosímetros rotacionales de cilindros concéntricos (Fann 35 de 6 velocidades).

### 2.1 Mediciones del Viscosímetro Rotacional
| Lectura | RPM | Tasa de Corte ($\dot{\gamma}$, $\text{s}^{-1}$) | Descripción Operativa |
|---|---|---|---|
| $\theta_{600}$ | 600 rpm | $1,021.8\text{ s}^{-1}$ | Lectura a alta tasa de corte. |
| $\theta_{300}$ | 300 rpm | $510.9\text{ s}^{-1}$ | Lectura a velocidad estándar API. |
| $\theta_{200}$ | 200 rpm | $340.6\text{ s}^{-1}$ | Lectura intermedia. |
| $\theta_{100}$ | 100 rpm | $170.3\text{ s}^{-1}$ | Lectura a velocidad media. |
| $\theta_{6}$ | 6 rpm | $10.2\text{ s}^{-1}$ | Lectura a baja tasa de corte (LSRV). Clave para transporte de recortes en anular. |
| $\theta_{3}$ | 3 rpm | $5.1\text{ s}^{-1}$ | Lectura a muy baja tasa de corte. Clave para suspensión estática. |

### 2.2 Fórmulas Reológicas Obligatorias (Modelo Plástico de Bingham)

#### A. Viscosidad Plástica (Plastic Viscosity, $PV$):
$$PV = \theta_{600} - \theta_{300} \quad (\text{cP o mPa}\cdot\text{s})$$
- Representa la fricción mecánica interna entre sólidos y partículas de la fase líquida.
- **Regla de Validación:** $\theta_{600}$ debe ser estrictamente mayor o igual a $\theta_{300}$. Si $\theta_{600} < \theta_{300}$, la celda se resalta en rojo por lectura instrumental errónea.

#### B. Punto de Cedencia (Yield Point, $YP$):
$$YP = \theta_{300} - PV = 2 \times \theta_{300} - \theta_{600} \quad (\text{lb}/100\text{ ft}^2)$$
- Representa las fuerzas electroquímicas de atracción entre partículas en movimiento.

#### C. Esfuerzos de Gel (Gel Strengths):
- **Gel 10 Segundos (`gel_10s`):** Lectura máxima instantánea al arrancar a 3 rpm tras 10 s de reposo ($\text{lb}/100\text{ ft}^2$).
- **Gel 10 Minutos (`gel_10m`):** Lectura máxima al arrancar a 3 rpm tras 10 min de reposo ($\text{lb}/100\text{ ft}^2$).
- **Gel 30 Minutos (`gel_30m`):** Lectura opcional tras 30 min de reposo ($\text{lb}/100\text{ ft}^2$).
- *Criterio de Evaluación:*
  - Geles planos (ej. 8/10/12): Estructura tixotrópica ideal (buena suspensión sin sobrepresiones al romper circulación).
  - Geles progresivos (ej. 6/24/45): Peligro de arremetida o pistoneo / fractura de formación al reiniciar bombeo.

### 2.3 Múltiples Corridas de Temperatura (`No of Rheologies`)
El sistema permite registrar hasta **3 corridas reológicas a diferentes temperaturas** en una misma muestra (ej. 120°F, 150°F y 175°F) para simular la degradación o adelgazamiento térmico del fluido a condiciones de fondo.

---

## 3. Filtración y Formación de Revoque (Filtration Section)

Evalúa la capacidad del fluido para sellar las paredes permeables del hoyo y minimizar la invasión de filtrado a la formación productora.

### 3.1 Filtrado API (Baja Presión - Temperatura Ambiente)
- **Condiciones de Ensayo:** Prensa API estándar a 100 psi de presión diferencial y temperatura ambiente durante 30 minutos.
- **`api_fluid_loss`:** Volumen de filtrado recolectado en probeta graduada en 30 min (ml o $\text{cm}^3$).
- **`api_cake_thickness`:** Espesor del revoque depositado sobre el papel filtro Whatman No. 50, medido en 32avos de pulgada ($1/32"$).
  - *Criterio:* Revoque delgado, liso y compresible ($1/32"$ a $2/32"$).

### 3.2 Filtrado HTHP (Alta Presión - Alta Temperatura)
- **Condiciones de Ensayo:** Celda encamisada a 500 psi de presión diferencial y temperatura representativa de fondo (típicamente 250°F a 350°F).
- **`hthp_fluid_loss`:** Volumen total de filtrado duplicado (filtrado API HTHP estándar $= \text{volumen recolectado a 30 min} \times 2$), en ml.
- **`hthp_cake_thickness`:** Espesor del revoque HTHP en 32avos de pulgada ($1/32"$).

---

## 4. Análisis de Retorta y Balance de Sólidos (Retort & Solids Analysis)

Es el análisis cuantitativo más riguroso del lodo. Mediante destilación térmica en retorta (celda de 10 ml, 20 ml o 50 ml), se vaporizan las fases líquidas y se condensan en probeta graduada, dejando los sólidos secos en la cámara.

### 4.1 Lecturas Directas de la Probeta
- **Volumen Total de Retorta ($V_{\text{retort}}$):** Típicamente $10\text{ ml}$.
- **Volumen de Agua ($V_w$):** ml de agua condensada.
- **Volumen de Aceite ($V_o$):** ml de aceite base condensado (en lodos OBM/SBM).
- **Densidad de Retorta ($\rho_{\text{retort}}$):** Densidad medida del lodo colocado dentro de la copa de la retorta (ppg).

### 4.2 Porcentajes Volumétricos Primarios
$$\% \text{Agua} = \left(\frac{V_w}{V_{\text{retort}}}\right) \times 100$$

$$\% \text{Aceite} = \left(\frac{V_o}{V_{\text{retort}}}\right) \times 100$$

$$\% \text{Sólidos No Corregidos} = 100 - \% \text{Agua} - \% \text{Aceite}$$

### 4.3 Corrección por Salinidad y Químicos Solubles
Cuando el lodo contiene sales disueltas ($NaCl, KCl, CaCl_2$) o químicos solubles, estas sustancias se evaporan y precipitan como polvo sólido en la retorta, aumentando falsamente los sólidos medidos:
$$V_{\text{sal}} (\text{ml}) = \frac{\text{Cloruros (mg/L)} \times V_w}{1000 \times \rho_{\text{sal}}}$$

$$\% \text{Sólidos Corregidos} = \% \text{Sólidos No Corregidos} - \left(\frac{V_{\text{sal}}}{V_{\text{retort}}} \times 100\right)$$

### 4.4 Partición de Sólidos: Baja Gravedad (LGS) vs Alta Gravedad (HGS)

#### A. Densidad Promedio de los Sólidos ($\rho_{\text{solidos}}$):
$$\rho_{\text{solidos}} = \frac{\rho_{\text{retort}} - \left(\frac{\% \text{Agua}}{100} \times 8.33\right) - \left(\frac{\% \text{Aceite}}{100} \times \rho_o\right)}{\frac{\% \text{Sólidos Corregidos}}{100}} \quad (\text{ppg})$$

Convertida a gravedad específica ($SG$ en $\text{g/cm}^3$):
$$SG_{\text{solidos}} = \frac{\rho_{\text{solidos}}}{8.345}$$

#### B. Fracción y Porcentaje de Barita / HGS ($SG_{\text{HGS}} = 4.20$):
$$\% \text{HGS} = \left(\frac{SG_{\text{solidos}} - SG_{\text{LGS}}}{SG_{\text{HGS}} - SG_{\text{LGS}}}\right) \times \% \text{Sólidos Corregidos}$$
*(con $SG_{\text{LGS}} = 2.60$ para sólidos de perforación / arcillas comerciales)*.

#### C. Fracción y Porcentaje de Sólidos de Baja Gravedad (LGS):
$$\% \text{LGS} = \% \text{Sólidos Corregidos} - \% \text{HGS}$$

#### D. Concentraciones en lb/bbl:
$$\text{Concentración HGS} = \% \text{HGS} \times 14.7 \quad (\text{lb/bbl})$$
$$\text{Concentración LGS} = \% \text{LGS} \times 9.1 \quad (\text{lb/bbl})$$

#### E. Regla de Alerta Roja por Error de Balance:
- Si el cálculo arroja $\% \text{LGS} < 0.0$ o $\% \text{HGS} < 0.0$, el sistema coloca **inmediatamente un borde rojo** sobre la celda de LGS.
- *Causa:* Discrepancia entre la densidad de la copa de retorta y las lecturas de condensado (el lodo no puede tener menos de cero sólidos de baja gravedad).

---

## 5. Análisis Químico del Filtrado y del Lodo (Chemical Properties)

| Propiedad | Campo Técnico | Unidad | Reactivos / Procedimiento API |
|---|---|---|---|
| **pH** | `ph` | escala 0-14 | Medidor potenciómetro calibrado o tiras indicadoras. |
| **$P_m$** | `pm_alkalinity` | ml $H_2SO_4$ 0.02N | Alcalinidad de 1 ml de lodo completo al punto final de fenolftaleína ($pH = 8.3$). |
| **$P_f$** | `pf_alkalinity` | ml $H_2SO_4$ 0.02N | Alcalinidad de 1 ml de filtrado al punto final de fenolftaleína ($pH = 8.3$). |
| **$M_f$** | `mf_alkalinity` | ml $H_2SO_4$ 0.02N | Alcalinidad de 1 ml de filtrado al punto final de naranja de metilo ($pH = 4.3$). |
| **Cloruros** | `chlorides` | mg/L (ppm) | Titulación con nitrato de plata ($AgNO_3$ 0.1N o 0.282N) con indicador cromato de potasio. |
| **Dureza Total** | `total_hardness` | mg/L como $CaCO_3$ | Titulación complexométrica con EDTA 0.01M o 0.1M con indicador Calmagite / Negro de Eriocromo T. |
| **Calcio ($Ca^{2+}$)** | `calcium` | mg/L | Titulación con EDTA a $pH > 12$ con indicador murexida. |
| **Potasio ($K^+$)** | `potassium` | % en peso o mg/L | Centrifugación con tetrafenilborato de sodio o electrodo selectivo de iones. |
| **Exceso de Cal** | `excess_lime` | lb/bbl | Calculado: $0.26 \times (P_m - (F_w \times P_f))$ en lodos cálcicos. |
| **MBT** | `mbt_capacity` | lb/bbl equiv. bentonita | Capacidad de azul de metileno: titulación con azul de metileno para cuantificar arcillas activas reactivas. |

---

## 6. Especificaciones de Propiedades Diarias y Alertas Visuales (Daily Properties Specifications)

El manual ONE-TRAX define en la sección 4.5.4 una ventana de especificaciones operativas (`Daily Properties Specifications`) donde el Ingeniero de Proyecto o Superintendente fija los rangos admisibles de trabajo:

### 6.1 Matriz de Tolerancia Min / Max
Cada propiedad activa del catálogo maestro puede tener asociada:
- `min_value`: Límite inferior permisible (ej. Densidad mínima 9.0 ppg, pH mínimo 9.5).
- `max_value`: Límite superior permisible (ej. Densidad máxima 9.4 ppg, LGS máximo 6.0%).
- `comment`: Comentario u objetivo operativo (ej. "Mantener YP alto para limpieza en hoyo de 26 plg").

### 6.2 Regla Estricta de Visualización: Celdas con Borde Rojo (`red-outline`)
En la pantalla del chequeo diario:
$$\text{Si } Valor < Min \quad \lor \quad Valor > Max \implies \mathbf{Borde\ Rojo\ Obligatorio\ en\ la\ Celda}$$
- El borde rojo alerta visualmente al ingeniero y a la operadora de una propiedad fuera de programa operacional.
- Al corregir la dosificación química o el valor ingresado dentro del rango, el borde rojo desaparece automáticamente.

---

## 7. Tabla de Propiedades Extra y Personalizadas (Extra Fluid Properties)

La sección 4.5.3 del manual provee soporte para:
1. **Catálogo de Propiedades Secundarias:** Propiedades adicionales definidas en la base de datos (ej. Sulfatos, Lubricidad, Actividad de agua $a_w$, Contenido de arena % Sand Content).
2. **10 Propiedades Personalizables por el Usuario (User Defined Extra 1 .. 10):**
   - El usuario puede escribir su propio rótulo (ej. "Polímero Residual", "Concentración de Biocida").
   - **Regla de Persistencia:** Una vez nombrada y usada en un reporte, **no se debe eliminar ni renombrar** para preservar el histórico de reportes pasados. Si ya no se necesita, simplemente se fija su `print_order = 0`.
3. **Columna `print_order`:** Define la posición en la que la propiedad saldrá impresa en el PDF/Excel oficial. Si es `0` o está vacía, no se imprime en el reporte exportable.

---

## 8. Mapeo a Modelos Django / PostgreSQL

Los modelos ya existentes en `reportes/models.py` (`MuestraFluido`, `PropiedadValor`, `PropiedadSistema`, `PropiedadCatalogo`) soportan esta estructura. Se consolidan las siguientes relaciones:

1. **`MuestraFluido`:**
   - `reporte`: ForeignKey a `ReporteDiario`.
   - `numero_muestra`: Integer (1 a 4).
   - `hora_muestra`: TimeField.
   - `origen`: CharField(60).
   - `es_primaria`: BooleanField(default=False). Exactamente una `True` por reporte.
   - `profundidad`: DecimalField(10, 2).
   - `densidad`: DecimalField(5, 2).
   - `viscosidad_embudo`: DecimalField(5, 1).
   - `temperatura_flujo`: DecimalField(5, 1).
   - `pv`: DecimalField(5, 2).
   - `yp`: DecimalField(5, 2).
   - `gel_10s`: DecimalField(5, 2).
   - `gel_10m`: DecimalField(5, 2).
   - `gel_30m`: DecimalField(5, 2).
   - `ph`: DecimalField(4, 2).
   - `api_filtrado`: DecimalField(5, 2).
   - `api_revoque`: DecimalField(4, 1).
   - `retorta_agua`: DecimalField(5, 2).
   - `retorta_aceite`: DecimalField(5, 2).
   - `retorta_solidos`: DecimalField(5, 2).
   - `solidos_lgs`: DecimalField(5, 2).
   - `solidos_hgs`: DecimalField(5, 2).
   - `cloruros`: DecimalField(10, 2).
   - `dureza_total`: DecimalField(10, 2).
   - `calcio`: DecimalField(10, 2).

2. **`PropiedadSistema` (Especificaciones Min / Max):**
   - `sistema`: ForeignKey a `SistemaFluido`.
   - `propiedad`: ForeignKey a `PropiedadCatalogo`.
   - `min_value`: DecimalField(null=True, blank=True).
   - `max_value`: DecimalField(null=True, blank=True).
   - `comentario`: CharField(max_length=200, blank=True).

