# Módulo 4A: Apertura del Día Operativo, Información General y Distribución de Tiempo
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / View Daily Information (General Tab & Time Distribution)
**Referencia:** Manual ONE-TRAX 2.0 (Secciones 4.1, 4.2 y 4.3) y Mud Report 16 PERLA-1X

---

## 1. Ciclo de Vida y Creación del Día Operativo (Starting a New Day)

El reporte diario es la unidad fundamental de captura de operaciones en ONE-TRAX. Todo cálculo volumétrico, hidráulico, de inventario y facturación se estructura alrededor del día operativo (00:00 a 24:00 hrs).

### 1.1 Creación del Primer Día del Proyecto (Day 1)
Al iniciar las operaciones del pozo:
1. **Fecha de Reporte (`Date`):** Se inicializa con la fecha actual del sistema, pero el usuario puede ajustarla a la fecha real de inicio de operaciones (Spud Date o inicio de reporte).
2. **Intervalo por Defecto (`Default Interval`):** Asigna el intervalo inicial activo (ej. Intervalo 1 o Intervalo 0). Afecta directamente la contabilidad de costos y el consumo de productos del tramo.
3. **Sistema de Fluido por Defecto (`Default Fluid System`):** Se selecciona de la lista configurada en el proyecto. **Regla de Filtrado:** Solo se muestran los sistemas de fluido cuyo `operational_mode` coincida estrictamente con el del intervalo seleccionado (`Drilling` o `Completion`).
4. **Regla de Bloqueo Permanente (Hard Lock Irreversible):**
   Al confirmar la creación del **primer reporte diario** del pozo, quedan **bloqueados permanentemente** para edición en la base de datos:
   - `unit_set`: Sistema de unidades (`Standard Oilfield` o `Metric`).
   - `es_offshore`: Flag de operaciones marinas.
   - `usa_riser`: Flag de uso de columna marina/riser.
   *Razón técnica:* Cambiar las unidades o la arquitectura marina a mitad de proyecto corrompe irreversiblemente el histórico de volúmenes, capacidades y costos acumulados.

### 1.2 Creación de Días Subsecuentes (Day 2 .. N)
A partir del segundo día, la creación se realiza mediante la opción `New Day`:
1. **Correlativo Automático de Reporte (`Report Number`):**
   - El número de reporte (`numero_reporte`) se incrementa automáticamente en $+1$ respecto al último día del pozo.
   - **Regla de Pozo:** Es estrictamente correlativo **a nivel de Pozo**, nunca se reinicia al cambiar o abrir un nuevo intervalo dentro del mismo pozo.
2. **Avance de Fecha:**
   - Se fija automáticamente en `fecha_anterior + 1 día`.
3. **Clonación Operativa (`Copy Data From Prior Day?`):**
   - Checkbox activo por defecto. Copia automáticamente desde el día anterior:
     - Bombas de lodo activas y sus dimensiones mecánicas (Liner, Stroke, SPM).
     - Equipos de control de sólidos activos y configurados.
     - Mallas instaladas en zarandas (horas acumuladas incrementadas).
     - Componentes de la sarta de perforación / BHA.
4. **Herencia Volumétrica Obligatoria (Rollover de Fosas):**
   $$\text{Start Volume}_{\text{Día } N} = \text{Actual End Volume}_{\text{Día } N-1}$$
   - El volumen inicial de cada fosa (y del sistema activo total) del nuevo día toma de forma exacta la medición física final (`Actual End Volume`) registrada el día anterior.
   - No se permite discrepancia ni ingreso manual de volumen de arranque para días subsecuentes.

### 1.3 Cambio de Intervalo durante la Jornada (`Change Default Interval`)
- Si durante el transcurso del día el pozo cambia de intervalo (ej. se termina la perforación de hoyo abierto e inicia la bajada de revestidor):
  - El usuario puede actualizar el `Default Interval` en la pestaña General.
  - **Inmutabilidad Transaccional:** El cambio **no altera** el intervalo de las transacciones volumétricas ni de uso de materiales ya registradas previamente ese día; solo se aplica a las transacciones creadas a partir de ese momento.

---

## 2. Pestaña General: Información Actual y Profundidades (General Tab)

### 2.1 Identificación y Estado Operativo
- **Pozo / Well Name:** Identificador del pozo (ej. PERLA-1X).
- **Fecha (`date`):** Fecha del día operativo.
- **Número de Reporte (`numero_reporte`):** Consecutivo del pozo (ej. Report No. 9).
- **Intervalo Activo (`intervalo`):** Tramo geológico/operativo actual.
- **Sistema de Fluido Activo (`sistema_fluido`):** Gama de lodo en uso (ej. WBM, CALDRIL, VERSACLEAN).
- **Actividad Presente (`present_activity`):** Texto descriptivo de la operación a las 24:00 (corte del día). Ej: *"Perforando hoyo de 26 pulgadas con BHA #1 de 2,100 ft a 2,880 ft. Circulando para viaje."*

### 2.2 Registro de Profundidades (Depths)
| Variable | Nombre Técnico | Unidad | Descripción |
|---|---|---|---|
| `bit_depth` | Bit Depth | ft | Profundidad actual de la mecha al corte de medianoche. Alimenta el cálculo de longitud de Drill Pipe. |
| `total_depth` | Total Depth (MD) | ft | Profundidad total medida alcanzada por el pozo al corte. |
| `tvd` | True Vertical Depth | ft | Profundidad vertical verdadera. Requerida para cálculo de presión hidrostática y gradientes. |
| `midnight_depth` | Midnight Depth | ft | Profundidad al inicio de la jornada (00:00 hrs). |
| `daily_progress` | Progress Last 24 hr | ft | **Calculado:** $\text{Total Depth} - \text{Midnight Depth}$. Pies perforados en las últimas 24 hrs. |

### 2.3 Horas Operativas del Fluido
- **`rotating_hours` (Horas Rotando):** Horas netas de perforación / fondo.
- **`circulating_hours` (Horas Circulando):** Horas totales de bombeo y circulación del lodo.

---

## 3. Distribución de Tiempo de Actividades (Time Distribution Table)

### 3.1 Propósito
La tabla `Time Distribution` desglosa con exactitud matemática las 24 horas del día operativo en las actividades realizadas por el equipo de perforación.

### 3.2 Catálogo Estandarizado de Actividades (Rig Activities)
Cada fila registra una actividad del catálogo y su duración en horas (con precisión de 2 decimales):
1. `Drilling Actual` (Perforación efectiva rotaria / motor de fondo)
2. `Reaming / Washing` (Repasado y lavado de hoyo)
3. `Circulating & Conditioning Mud` (Circulación para limpieza y homogenización)
4. `Tripping In (TIH)` (Viaje de tubería hacia el fondo)
5. `Tripping Out (TOH)` (Viaje de tubería hacia superficie)
6. `Running Casing / Liner` (Bajada de tubería de revestimiento)
7. `Cementing Operations` (Operaciones de cementación de casing/liner)
8. `Wait on Cement (WOC)` (Espera de fraguado de cemento)
9. `BHA Make-Up / Break-Out` (Armado o desarme de herramientas de fondo)
10. `Rig Repair & Maintenance` (Mantenimiento o reparación del taladro)
11. `Logging & Wireline` (Toma de registros eléctricos / registros con guaya)
12. `Directional Survey` (Toma de levantamientos direccionales)
13. `Formation Testing / Coring` (Pruebas de formación o toma de núcleos)
14. `Well Control Operations` (Control de arremetidas / desgasificación)
15. `Rig Service` (Mantenimiento preventivo de rutina del taladro)
16. `Other Rig Activities` (Otras operaciones de superficie o subsuelo)

### 3.3 Regla de Validación Estricta: Suma Obligatoria de 24.00 Horas
$$\sum_{i=1}^{n} \text{Horas}_{i} = 24.00\text{ hrs}$$

**Comportamiento Visual en UI:**
- **Si $\sum < 24.00$ hrs:**
  - El total se resalta con **color rojo** (`color: #dc3545; font-weight: bold;`).
  - Indica al operador que el balance de tiempo está incompleto.
- **Si $\sum == 24.00$ hrs:**
  - El total cambia a **color verde / texto estándar válido** (`color: #198754;` o `#212529;`).
  - Cumple la validación horaria del día.
- **Si $\sum > 24.00$ hrs:**
  - Se activa una **alerta bloqueante** (`Warning: The total hours entered is greater than 24 hours`).
  - El sistema prohíbe exceder las 24 horas astronómicas del día.

---

## 4. Registro de Problemas Operativos y de Fluidos (Problems & NPT)

Documenta contingencias que originan tiempo no productivo (NPT - *Non-Productive Time*) o impactan la calidad del fluido:

- **Categorías de Problema:**
  - `Lost Circulation` (Pérdida parcial o total de circulación)
  - `Stuck Pipe` (Pega diferencial, mecánica o por empaquetamiento)
  - `Wellbore Instability` (Derrumbe de lutitas, hoyo cerrado o ensanchado)
  - `Kick / Well Control` (Influjo de gas, petróleo o agua salada)
  - `Mud Contamination` (Contaminación por cemento, yeso, sal o sólidos finos)
  - `Solids Control Failure` (Fallo mecánico en zarandas, centrífugas o desarenador)
  - `Hydraulic Limitation` (Limitación de presión de bomba o standpipe)
- **Campos de Registro:**
  - `Event Description`: Tipo de problema.
  - `Duration (hrs)`: Tiempo de retraso o combate del problema.
  - `Corrective Action`: Tratamiento químico o maniobra operativa ejecutada.

---

## 5. Personal y Facturación Diaria en Sitio (Representatives)

Gestiona los ingenieros de lodo y especialistas presentes en la locación:
- **Campos:**
  - `Representative Name`: Ingeniero seleccionado del catálogo de Personal del proyecto.
  - `Daily Charge Qty`: Cantidad de días de servicio a facturar (por defecto `1.0`; acepta fracciones como `0.5` si el turno inició a mitad de jornada).
- **Cálculo de Facturación Diaria:**
  $$\text{Costo Día Personal} = \text{Daily Charge Qty} \times \text{Daily Charge Amount}$$

---

## 6. Comentarios y Observaciones (Remarks & Comments)

- **Comentarios Operativos (24 hrs):**
  - Resumen secuencial de las maniobras realizadas con el fluido (ej. adiciones de densificante, tratamientos de viscosidad, diluciones, cambios de zaranda).
- **Recomendaciones para el Turno Siguiente:**
  - Instrucciones técnicas para el ingeniero de relevo o supervisión de operadora.

---

## 7. Mapeo al Esquema de Base de Datos y APIs

### 7.1 Modelo `ReporteDiario` (`reportes` y `mychapala`)
- `pozo`: Relación o contexto de pozo.
- `intervalo`: FK a `Intervalo`.
- `fecha`: DateField (`(intervalo, fecha)` único).
- `numero_reporte`: PositiveIntegerField (correlativo por pozo).
- `bit_depth`, `total_depth`, `tvd`, `midnight_depth`: DecimalField(8, 2).
- `rotating_hours`, `circulating_hours`: DecimalField(5, 2).
- `actividad_presente`: TextField.
- `estado_intervalo`: Hereda protección; bloqueado si `intervalo.estado == 'cerrado'`.

### 7.2 Modelo `DistribucionTiempo`
- `reporte`: FK a `ReporteDiario` (`on_delete=CASCADE`).
- `actividad`: CharField con catálogo de actividades.
- `horas`: DecimalField(4, 2), min 0.01, max 24.00.
- `comentarios`: CharField(max_length=200, blank=True).

### 7.3 Endpoints API Requeridos
1. `POST /reportes/api/reportes/crear/`:
   - Valida datos de inicio de día (fecha, intervalo, sistema de fluido).
   - Bloquea parámetros del pozo (`unit_set`, `es_offshore`, `usa_riser`).
   - Copia bombas, equipos y transfiere volúmenes de fosas del día previo.
2. `GET/POST /reportes/api/reportes/<id>/distribucion-tiempo/`:
   - Lista y añade actividades del día.
   - Retorna la sumatoria actual y el estado de validación (`valido_24h: bool`).
3. `PUT /reportes/api/reportes/<id>/general/`:
   - Actualiza profundidades (`bit_depth`, `total_depth`, `tvd`, etc.) y actividad presente.
