# Manual de Usuario Maestro — Sistema CHAPALA
### Plataforma Integral de Ingeniería, Inventario y Reportes Diarios de Fluidos (Estilo ONE-TRAX)
**All Oil Services, C.A. (AOS) &bull; División de Operaciones de Fluidos de Perforación**

---

## 📌 Introducción y Arquitectura Operativa

El sistema **CHAPALA** es una solución integral diseñada para emular y modernizar la lógica operativa, matemática y contable de **ONE-TRAX (M-I SWACO)** en una plataforma web ágil, multiusuario y de alto rendimiento.

El flujo de trabajo se divide en dos grandes entornos operativos:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              ARQUITECTURA DEL SISTEMA CHAPALA                          │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│   1. VISTA DE PROYECTO (PROJECT VIEW)     │     2. VISTA DIARIA (DAILY INFORMATION)    │
│   (Parametrización estática previa)       │     (Matrices dinámicas y balances de lodo)│
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ • Asistente de Creación (Wizard 4 pasos) │ • General Diaria (Profundidades, Survey)   │
│ • Spud Date (Fecha única de inicio)       │ • Bombas, Mecha e Hidráulica               │
│ • Well Header (Datos generales y mercadeo)│ • Chequeos Reológicos y Retorta (WBM/OBM)  │
│ • Intervalos de Revestimiento y Costos    │ • Geometría del Pozo y Capacidades         │
│ • Fosas y Tanques (Pit Setup)             │ • Comentarios y Resumen Diario             │
│ • Catálogo Activo (Productos, Mallas)     │ • Control de Sólidos y Descartes           │
│ • Propiedades de Equipos y Benchmark      │ • Distribución de Tiempo (24h IADC)        │
│                                           │ • Pestaña 8: Volumetría, Inventario y Conc.│
└───────────────────────────────────────────┴────────────────────────────────────────────┘
```

### 🧭 Menú de Navegación Lateral (Sidebar)
* 💧 **Pozos:** Directorio central de pozos creados y acceso al Project View y Daily View de cada uno.
* 📦 **Inventario:** Catálogo global de productos químicos de AOS (stock, empaque, costos y propiedades).
* 🏗️ **Nuevo Pozo:** Asistente guiado de configuración de un nuevo proyecto.
* 🗂️ **Catálogos Maestros:** Base corporativa de modelos de zarandas, mallas, equipos de control de sólidos y parámetros.

---

## 🏗️ Fase 1: Creación del Proyecto y Parámetros Globales (Setup Inicial)

### 1.1 Asistente de Nuevo Pozo (Wizard de 4 Pasos)
Ruta: Menú Lateral → 🏗️ **Nuevo Pozo**.

| Paso | Parámetros a Configurar | Reglas Estrictas y Validación |
|---|---|---|
| **Paso 1: Datos Básicos** | Nombre oficial del pozo (ej. `POZO-LC-115`). Opción de clonar configuración de un pozo existente como plantilla. | El nombre es único en la base de datos. Si se usa plantilla, arrastra unidades, fosas e intervalos. |
| **Paso 2: Unidades** | Selección del sistema de unidades: **Campos Petroleros (Oilfield)**, **Métrico (Metric)** o **Personalizado (Custom)**. | > [!CAUTION]<br>**Regla irreversible:** Una vez confirmado el pozo, el sistema de unidades queda bloqueado permanentemente en la base de datos y no puede modificarse. |
| **Paso 3: Financiero y Opciones** | Moneda base (USD), decimales, tasa de impuesto (%), modelo de sólidos (M-I SWACO o API) y categorías de pérdida. | La moneda se bloquea al crear el pozo. La tasa de impuesto sí puede editarse posteriormente. |
| **Paso 4: Resumen y Confirmación** | Auditoría visual de los parámetros preseleccionados antes de consolidar el pozo. | Al pulsar **Crear Pozo**, se inicializan automáticamente los catálogos base en la base de datos. |

---

### 1.2 Fecha de Inicio Operativo (Spud Date)
> [!IMPORTANT]
> Esta pantalla se presenta **una sola vez** al ingresar por primera vez a un pozo recién creado.
* **Primera Fecha de Datos:** Fecha calendario en la que inician los reportes diarios.
* **Tipo de Fluido Inicial:** Selección del sistema de lodo primario con el que inicia la perforación.
* Al confirmar, se consolida la línea de tiempo operativa y se habilita la **Vista Principal del Pozo (Project View)**.

---

### 1.3 Información General del Pozo (Well Header Dashboard)
Ruta: Menú Lateral → 💧 **Pozos** → Seleccionar Pozo → **Información General del Pozo**.

El nuevo diseño del Well Header se organiza en un **Dashboard balanceado a dos columnas** que optimiza el espacio en pantalla para verse perfectamente al 100% de zoom en cualquier monitor:

#### Pestaña 1: Información del Pozo
* **Columna Izquierda (Datos del Pozo):**
  * Operador, Campo/Área, Descripción del Proyecto, Ubicación geográfica.
  * Almacén base de despacho, Contratista de perforación, Nombre del Taladro.
  * Coordinador de Fluido, Ingenieros de Fluidos / AOS en campo (1 y 2).
  * Fecha de Spud, Fecha de TD, Días de TD, Profundidad de reentrada, Coordenadas (Lat N/S, Lon E/O).
* **Columna Derecha (Parámetros Especiales y Control):**
  * 🌊 **Proyecto Offshore & Riser:**
    * Checkbox *Proyecto Offshore*: activa campos obligatorios de **Altura Libre (Air Gap en ft)**, **Profundidad de Agua (ft)** y **Temperatura del Lecho Marino (°F)**.
    * Checkbox *El pozo usa Riser*: habilita el **Diámetro Interno (ID en in)** y **Longitud del Riser (ft)**. Si se deja en blanco, la longitud asume automáticamente `Air Gap + Profundidad de Agua`.
  * 🌡️ **API 5ª Edición:**
    * *Temperatura Superficial (°F)* y *Gradiente de Temperatura (°F/100ft)*: requeridos para los cálculos dinámicos de reología e hidráulica de fondo.
  * 🏁 **Fin del Pozo:**
    * Profundidad Total (ft), TVD final, Días totales, Fecha de fin, Temperatura máxima de fondo y Costo total del proyecto.
  * 💬 **Comentarios y Control de Proyecto:**
    * Notas generales del pozo y **Número de Control Log-It** (código único corporativo).

#### Pestaña 2: Códigos de Mercadeo y Clasificación ONE-TRAX
Campos estandarizados para reportes ejecutivos centrales y licitaciones:
* Tipo de Lodo Principal (Código y Descripción).
* Tipo de Pozo (Código y Descripción).
* Tipo de Contrato (Código y Descripción).
* Fluido de Completación (Código y Descripción).

---

### 1.4 Catálogo Maestro e Inventario Global de Productos
Ruta: Menú Lateral → 📦 **Inventario**.

El inventario es una entidad centralizada compartida. Cada producto cuenta con campos normalizados para su control de stock y formulación química:

| Campo | Descripción | Ejemplo / Valores Válidos |
|---|---|---|
| **Código** | Identificador único del producto | `AOS-1002`, `BARITE-4.2` |
| **Descripción** | Nombre comercial y técnico completo | `CARBONATO DE CALCIO MEDIANO` |
| **Empaque** | Tipo de contenedor físico oficial | `SACOS`, `TAMBOR`, `TOTE`, `LATA`, `GRANEL` |
| **Unidad** | Unidad de medida pura | `LBS`, `GAL`, `BBL`, `KG`, `L` |
| **Libraje / Tamaño** | Capacidad o peso unitario del empaque en libras | `55` (saco de 55 lb), `400` (tambor de 55 gal) |
| **Gravedad Específica ($SG$)** | Densidad relativa del producto respecto al agua ($1.00$) | `4.20` (Barita), `2.70` (Carbonato), `0.84` (Aceite) |
| **Costo Unitario ($)** | Precio de compra/facturación por unidad | `$18.50` |
| **Cantidad (Stock)** | Saldo físico actual en el almacén central | Unidades enteras en existencia |

---

### 1.5 Configuración de Catálogo Activo en el Pozo
Ruta: **Project View** del Pozo:
1. **Productos Activos:** Selecciona qué químicos del inventario general están autorizados en este pozo. Define el precio acordado con el cliente, el **Código de Costo Diario** (1: Químicos, 2: Ing. Fluidos, 3: Ing. Sólidos) y la casilla **Show Conc?** (activa el cálculo dinámico de concentración en piscinas en lb/bbl).
2. **Equipos Activos:** Da de alta los equipos mecánicos presentes en taladro (Zarandas, Desarenadores, Centrífugas, Limpiadores). Requiere ingresar el **Número de Serie**, tarifa de renta operativa diaria y tarifa en reserva (*Stand-by*).
3. **Mallas Activas:** Asocia los modelos de mallas homologadas para las zarandas en locación, indicando precio y porcentaje de descuento pactado.

---

### 1.6 Configuración de Tanques y Fosas (Pit Setup)
Ruta: **Project View** → **Información de Fosas**.

Se registran todas las fosas y tanques de superficie disponibles en el taladro:
* **Fosas Transaccionales (Activas en Balance):** Aquellas que participan directamente en el circuito de perforación o tratamiento de fluidos. Cualquier adición de productos o transferencia altera su volumen y concentración.
* **Fosas No Transaccionales (Almacenamiento Pasivo):** Tanques dedicados a reserva estratégica (salmuera cruda, gasoil a granel) que no deben afectar el balance diario ni facturarse hasta su dosificación.
* **Tipos de Fosas:**
  * `Activa (Active)`: Integrada al circuito cerrado de circulación del hoyo.
  * `Reserva (Reserve)`: Almacenamiento de lodo tratado listo para reemplazo.
  * `Premezcla (Premix)`: Preparación de píldoras o fluidos densificados.
  * `Píldora (Pill)` / `Espaciador (Spacer)`: Volúmenes segregados para baches operativos.
  * `Vacía (Empty)`: Tanque fuera de servicio.

---

### 1.7 Configuración de Intervalos de Revestimiento y Pérdidas
* **Intervalos de Costo:** Se define cada sección perforada (Conductor, Superficie, Intermedio, Producción, Liner).
  * Diámetro Externo (Casing OD) y Diámetro Interno (Casing ID en pulgadas).
  * Diámetro de Hoyo Abierto (Bit / Hole Size en pulgadas).
  * Profundidad de la zapata (Shoe Depth en ft) y tope de liner si aplica.
  * Días estimados, longitud planeada y Gradiente de Fractura ($lpg$).
* **Pérdidas de Fluido (Loss Setup):** Mapeo de categorías predefinidas clasificadas en:
  * *Superficiales:* Descartes por zarandas, hidrociclones, evaporación, botes en bombas.
  * *Subsuperficiales:* Filtración a la formación, pérdidas parciales, cavernas, detrás del revestidor.

---

## 📅 Fase 2: Vista Diaria Operativa (Daily Information View)

### 2.1 Apertura del Día Operativo
Ruta: **Project View** → **Fluidos de Perforación y Equipos** → **+ Nuevo Reporte**.
1. **Fecha Operativa:** Consecutiva al último reporte emitido (o la fecha de Spud si es el primero).
2. **Intervalo de Costo por Defecto:** Fase en curso a la cual se imputarán contablemente los costos químicos del día.
3. **Sistema de Lodo Principal:** Base del fluido activo en perforación.
4. **Casilla "Copiar datos del reporte anterior":** Arrastra automáticamente la última geometría cargada, personal, representantes y lecturas de referencia para evitar recaptura redundante.

---

### 2.2 Pestaña 1: General Diaria
* **Profundidades Operativas:** Profundidad Medida (MD en ft), Profundidad Verdadera Vertical (TVD en ft) y **Profundidad de la Mecha (Bit Depth en ft)**.
* **Actividad y Operaciones:** Resumen de la operación en progreso (perforando, bajando sarta, viaje corto, registro).
* **Distribución de Tiempo (Matriz 24h IADC):**
  > [!WARNING]
  > **Regla estricta:** La sumatoria de horas registradas en las actividades IADC del período debe ser exactamente **24.0 horas** (salvo el día de inicio/cierre con horas parciales). Si la suma difiere, el sistema resalta el total en rojo.
* **Registro Direccional (Survey):** Matriz de estaciones con MD, Inclinación (°) y Azimut (°). El motor calcula automáticamente el TVD resultante, Dogleg Severity (DLS) y sección vertical.
* **Problemas Operacionales:** Bitácora de tiempos no productivos (NPT), pega de tubería, pérdidas masivas o embolamiento de mecha.

---

### 2.3 Pestaña 2: Bombas, Mecha e Hidráulica
* **Matriz de Bombas:**
  * Diámetro de camisa (*Liner* en pulgadas), longitud de carrera (*Stroke* en pulgadas).
  * Eficiencia volumétrica (%) y velocidad operativa (*Pump Rate* en SPM).
  * El sistema computa el caudal total entregado en galones por minuto ($GPM$).
* **Información de la Mecha (Bit Data):**
  * Diámetro de la mecha, marca, tipo y distribución de boquillas (*Nozzles* en 32avos de pulgada).
  * Cálculo instantáneo del **Área Total de Flujo (TFA en $in^2$)**.
* **Parámetros de Perforación:**
  * Peso sobre la mecha ($WOB$), RPM de mesa/top-drive, horas de rotación, Tasa de Penetración ($ROP$ promedio), presión de bombeo de superficie ($SPP$) y caídas de presión en herramientas de fondo (MWD, motor de lodo).

---

### 2.4 Pestaña 3: Propiedades y Chequeos del Fluido (Fluid Checks)
Permite documentar hasta 4 chequeos diarios completos (mañana, tarde, noche y chequeo especial):
* **Chequeo Principal:** Selección obligatoria del chequeo que gobierna el reporte impreso y la hidráulica de fondo.
* **Matriz Reológica Fann:**
  * Lecturas de viscosímetro: $\theta_{600}, \theta_{300}, \theta_{200}, \theta_{100}, \theta_6, \theta_3$.
  * Temperatura de medición del fluido (°F).
  * **Cálculo automático:**
    $$\text{Viscosidad Plástica (PV, cP)} = \theta_{600} - \theta_{300}$$
    $$\text{Punto Cedente (YP, lb/100ft}^2\text{)} = \theta_{300} - \text{PV}$$
  * Lectura de geles a 10 segundos, 10 minutos y 30 minutos ($lb/100ft^2$).
* **Análisis de Sólidos y Retorta:**
  * **Lodos Base Agua (WBM):** Ingreso de % Agua, % Aceite y % Sólidos totales por retorta, Gravedad Específica de la Barita ($SG$), fracción de arcilla bentonítica comercial (*Frac Bent*) y sólidos químicos disueltos (*Chem Conc*).
    * Computa automáticamente: % Sólidos de Baja Gravedad (%LGS), % Sólidos de Alta Gravedad (%HGS) y % Sólidos Perforados (%Drill Solids).
  * **Lodos Base Aceite o Sintéticos (OBM/SBM):** Ajuste del volumen de retorta por dilatación térmica, $SG$ del aceite base, salinidad de la fase acuosa (cloruros, CaCl₂ o NaCl) y Relación Aceite/Agua ($O/W\ Ratio$).

---

### 2.5 Pestaña 4: Geometría Mecánica del Pozo
Ensambla el circuito hidráulico integral desde el fondo hasta la superficie:
1. **Perfil del Hoyo:** Tramos de revestidor, liner y hoyo abierto con su factor de ensanchamiento o lavado (**% Washout**).
2. **Sarta de Perforación (Drill String):**
   * Configuración **desde la mecha hacia arriba** (Fila 1 = Mecha).
   * Componentes: Mecha, Motores de fondo, Estabilizadores, Drill Collars (DC), Heavy Weight (HWDP) y Tubería de Perforación (DP).
   * Parámetros: Tipo, longitud (ft), Diámetro Externo (OD in), Diámetro Interno (ID in) y dimensiones de acoples (*Tool Joints*).
3. **Módulo de Desvíos (Side-Track):**
   * Control específico para aislar la profundidad de ventana de arranque y calcular exclusivamente el nuevo volumen anular perforado.
4. **Matriz de Capacidad Hidráulica Calculada:**
   * Volumen interno de la sarta (**DS Volume**, bbl).
   * Volumen en el espacio anular (**Annular Volume**, bbl).
   * Volumen bajo la mecha (**Under-bit Volume**, bbl).
   * Emboladas de retorno de fondo a superficie (**Bottoms-Up Strokes** y tiempo en minutos).
   * Desplazamiento metálico de tubería.

---

### 2.6 Pestaña 5: Comentarios y Resumen Operativo
* **Especificaciones del Lodo:** Rangos operacionales tolerados para densidad, viscosidad de embudo, PV, YP y pH.
* **Resumen del Día:** Resumen conciso de **una sola línea** que se consolida directamente en el dossier final del pozo (*Recap Report*).
* **Observaciones y Tratamiento Químico:** Descripción técnica de píldoras bombeadas, tratamientos de alcalinidad, baches de limpieza y notas operativas IADC.

---

### 2.7 Pestaña 6: Desempeño de Equipos y Mallas de Control de Sólidos
#### Gestión de Mallas (Shaker Screens):
1. **Ticket de Recepción:** Ingreso físico de mallas recibidas en locación (nuevas o reutilizables).
2. **Matriz de Posición en Zarandas:** Muestra las zarandas activas y sus camas numeradas (posiciones 1 a 12, donde 1 es la más cercana a la línea de flujo).
3. **Acciones Operativas:**
   * *Install New / Used:* Instala una malla en una posición libre. Si es nueva, genera el cargo financiero al costo diario.
   * *Remove & Reuse:* Retira la malla en buen estado y la regresa al almacén de usados.
   * *Remove & Dispose:* Descarte definitivo por rotura o fin de vida útil.
   * *Undo:* Revierte el último movimiento en caso de error de captura sin afectar el balance histórico.

#### Desempeño de Equipos Mecánicos:
* Horas trabajadas por zarandas primarias, desarenadores, deslimpiadores y centrífugas decantadoras.
* **Cálculo de Lodo Descartado con Ripios:**
  * El usuario estima el % de ripios descartados por equipo y la relación de lodo adherido en ripios (*Mud on Cuttings*, lb/lb o vol/vol).
  * El motor multiplica el volumen de hoyo perforado del día por el porcentaje asignado y calcula el volumen neto de lodo perdido en ripios húmedos.
* **Tarifas de Facturación:** Asignación de cobro operativo (*Full Charge*), reserva (*Stand-by*) o sin costo (*No Charge*).

---

## ⚗️ Fase 3: Balance Volumétrico e Inventario (Volume Accounting - Pestaña 8)

La Pestaña 8 es el **motor contable y volumétrico central** de CHAPALA. Gobierna el balance de materia de todos los fluidos y productos químicos.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        FLUJO TRANSACCIONAL DE LA PESTAÑA 8                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   [Volumen Inicial en Fosas]                                                           │
│              +                                                                         │
│   [Transacciones del Día] ──► (Químicos preparados, Lodo reciclado recibido)              │
│              -                                                                         │
│   [Pérdidas y Salidas]    ──► (Zarandas, filtración, transferencias externas)          │
│              =                                                                         │
│   [Volumen Teórico Calculado]                                                          │
│              vs                                                                        │
│   [Volumen Físico Real Medido al Cierre]                                               │
│              ║                                                                         │
│              ▼                                                                         │
│   [Balance / Not Accounted] ──► ¡Debe ser estrictamente 0.00 bbl!                     │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Matriz de Fosas y Estado del Hueco
* **Volumen de Cierre (End Volume):** Medición de nivel físico real en barriles ($bbl$) en cada piscina al corte de las 24:00 horas.
* **Fluidos en el Hoyo (Fluids in Hole):** Volumen teórico ocupado dentro del pozo calculado por la geometría mecánica.
* **Volumen Fuera del Sistema (Volume Not Fluids):** Volumen dentro del pozo que no está ocupado por el lodo en circulación (por ejemplo, salmuera detrás de una válvula o agua de desplazamiento) para no desfasar el balance contable.

---

### 3.2 Botones Transaccionales (Motor Contable)

#### 1. ⚗️ Agregar Químicos (Add Chemicals):
* Incorpora agua o aceite base más cantidades exactas de productos químicos a un tanque transaccional específico.
* **Volumen físico generado:** El motor calcula el volumen añadido mediante la densidad y gravedad específica ($SG$) de los aditivos dosificados:
  $$\text{Volumen Aportado (bbl)} = \frac{\text{Unidades} \times \text{Libraje por Unidad}}{SG \times 350.5}$$
* **Descuento en Inventario:** Descuenta automáticamente las unidades en la columna *Used for Fluid* del inventario del pozo y rebaja el stock del almacén central.
* **Asignación de Costo:** Imputa el monto en dólares al Intervalo de Costo activo.
* **Casilla "Is Dilution":** Identifica si el tratamiento tuvo fines de dilución para abatir LGS en los KPIs operacionales.

#### 2. 🛢️ Agregar Lodo Reciclado (Add Whole Mud):
* Registra el ingreso de lodo formulado previamente, traído de una planta de mezcla central o transferido desde otro pozo.
* Requiere densidad del lodo recibido ($lpg$) y concentraciones de productos para asimilarlo al balance de materia.

#### 3. ⇆ Transferencias (Transfer):
* Desplaza volumen de fluido entre tanques transaccionales (ej. de Fosa de Mezcla a Fosa Activa) sin alterar los costos totales del día.

#### 4. 📉 Pérdidas de Fluido (Loss):
* Declara volúmenes perdidos imputados a las categorías de superficie o subsuperficie.

#### 5. 🤖 Pérdidas Automáticas de Equipos (Create Equipment Loss Transaction):
* Lee la pérdida teórica de lodo calculada en la Pestaña 6 (control de sólidos en ripios húmedos) y genera la transacción contable de pérdida con un solo clic, sin intervención manual.

---

### 3.3 Regla de Oro: Balance Cero (Not Accounted = 0.00 bbl)
* El cuadro de **Balance de Fluidos (Fluids Balance)** compara el volumen final teórico deducido por las transacciones contra la medición física real efectuada en tanques y hoyo.
* > [!IMPORTANT]
  > **Regla contable estricta:** Para que el día operativo se considere cerrado y válido, la casilla **Not Accounted** debe ser estrictamente **`0.00 bbl`**.
  > Si presenta un valor diferente de cero:
  > * Si es positivo (+): Se midió más volumen del que ingresó formalmente (falta registrar agua de adición, lodo recibido o influjo).
  > * Si es negativo (-): Hay una pérdida no declarada o una transferencia incompleta.
  > * **Nunca altere artificialmente el volumen real medido en tanques para forzar el balance a cero.**

---

### 3.4 Motor de Concentraciones Químicas (lb/bbl)
Calcula en tiempo real la concentración residual de cada producto activo presente en el fluido:
* El agua y los fluidos base **diluyen** las concentraciones existentes.
* La dosificación de productos químicos **incrementa** la concentración de ese compuesto.
* El lodo reciclado y las transferencias internas **mezclan** proporcionalmente las concentraciones entre tanques.
* Las pérdidas de lodo o descartes en zarandas **reducen el volumen total pero preservan la concentración** ($lb/bbl$) del fluido remanente.

---

### 3.5 Motor de Modelado Hidráulico API 13D
Permite alternar entre las especificaciones **API 4ª Edición** y **API 5ª Edición**:
* Modela la reología mediante el modelo de Ley de Potencia Modificada (Herschel-Bulkley).
* Determina la velocidad crítica de flujo y régimen (Laminar, Transición, Turbulento) para cada sección del espacio anular y sarta.
* Genera la matriz analítica de caídas de presión por fricción:
  * Pérdidas en sarta de perforación (**DS Loss**, psi).
  * Pérdidas en espacio anular (**Annular Loss**, psi).
  * Caída de presión en boquillas de la mecha (**Bit Loss**, psi).
* Computa la **Densidad Circulante Equivalente (ECD en lpg)** a nivel de zapata y a profundidad total.
* Entrega los indicadores de potencia hidráulica de impacto: Potencia Hidráulica en Mecha (**HHP**) y Fuerza de Impacto por pulgada cuadrada (**HSI**).

---

## 📊 Fase 4: Reportes, Recaps y Cierre de Pozo (Closeout)

### 4.1 Generación de Reportes Diarios y Libro Excel ONE-TRAX
Desde la barra de navegación superior del reporte diario, el botón **Excel** compila y descarga automáticamente el libro oficial en formato `.xlsx` con todas las hojas corporativas parametrizadas en español:
1. **Reporte de Lodo (Daily Mud Report):** Formato ejecutivo adaptado al tipo de fluido (WBM, OBM o Sintético).
2. **Propiedades Extra:** Historial de las 60 variables analíticas de laboratorio.
3. **Contabilidad de Volumen (Volume Accounting):** Detalle de inventario de tanques, transacciones y balance diario.
4. **Inventario Químico:** 3 hojas con desglose DF, consolidado alfabético y matriz de balance general.
5. **Control de Sólidos:** Equipos de superficie, horas de marcha, pérdidas en ripios y vida útil de mallas.
6. **Inventario de Mallas:** Trazabilidad de recepción, instalaciones y descartes.

---

### 4.2 Cierre Final del Pozo (Project Closeout & Recap)
Ruta: **Project View** → **Reporte Final del Pozo (Recap)**.
Al alcanzar la profundidad objetivo (TD) y finalizar la operación:
1. **Auditoría de Integridad:** El sistema valida que no existan balances desfasados en los días operativos, que todos los intervalos tengan sus volúmenes y costos cerrados y que el stock consumido coincida con las salidas de inventario.
2. **Emisión del Dossier Final (Recap):**
   * **Reporte Final Imprimible (PDF):** Documento encuadernable con portada oficial, resumen ejecutivo, estadísticas de consumo por fase, indicadores de desempeño de mallas, gráfica de avance diario y análisis de costo por pie perforado ($/ft).
   * **Libro Maestro Excel Recap:** Archivo maestro consolidado para su archivo histórico y envío a la gerencia de operaciones de AOS.

---

## 🛠️ Guía Rápida de Solución de Problemas Frecuentes

| Mensaje de Error / Síntoma | Causa Técnica | Solución Rápida |
|---|---|---|
| **Not Accounted $\neq 0.00$ en Pestaña 8** | El volumen teórico de transacciones no coincide con el volumen físico medido al cierre. | Revise las transacciones con **Gestionar Transacciones**: verifique si faltó ingresar agua de adición, un bache preparado o una pérdida hacia zarandas. |
| **"Inventario de X: hay N y se necesitan M"** | El almacén central no tiene unidades suficientes del producto que intenta añadir. | Vaya a la pantalla central de 📦 **Inventario**, busque el producto y actualice la existencia real con **✏️ Modificar**. |
| **"Registra primero el ticket de recepción" (Mallas)** | Se intentó instalar una malla en una zaranda sin haber registrado su ingreso previo al taladro. | En la Pestaña 6, ingrese primero el Ticket de Recepción de mallas (fecha, tipo y cantidad recibida). |
| **"La posición X del equipo Y ya tiene una malla"** | Se intenta montar una malla sobre una cama que ya tiene una en uso. | Debe retirar primero la malla actual marcándola como *Remove & Dispose* o *Remove & Reuse*. |
| **Volúmenes del pozo salen en 0 bbl (Pestaña 4)** | Falta definir la profundidad de la mecha, la sarta o los diámetros del revestidor. | Asegúrese de: 1) Guardar la profundidad de mecha en Pestaña 1; 2) Cargar la sarta en Pestaña 4; 3) Haber configurado los intervalos de revestidor con su ID en el Project View. |
| **La hidráulica muestra aviso de datos incompletos** | Alguna variable esencial para el modelo reológico API no fue completada. | El sistema indica exactamente qué falta: complete el caudal de bombas (Pestaña 2), el chequeo principal con viscosímetro (Pestaña 3) y la sarta con ID/OD (Pestaña 4). |
| **Las horas del día aparecen en rojo (Pestaña 1 / 7)** | La distribución horaria IADC no totaliza exactamente 24.0 horas. | Ajuste la matriz de distribución de tiempo para que la sumatoria dé exactamente 24 horas. |
