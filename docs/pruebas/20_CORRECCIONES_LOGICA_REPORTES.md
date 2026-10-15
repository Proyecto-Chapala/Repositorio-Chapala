# 20 — Correcciones de Lógica y Cálculos en Reportes Diarios

Pruebas en pantalla para el paquete de 8 correcciones de lógica y cálculo aplicado el **15-oct-2026**.

## Cómo funciona

1. **Sincronización de edición de hidráulica (API 4ª vs 5ª):**
   - Al cambiar la edición en la Pestaña 8 con los botones `4ª Edición (Bingham/Power Law)` y `5ª Edición (Herschel-Bulkley)`, el ajuste se persiste automáticamente en la base de datos (`pozo.usar_api_5ta_edicion_hidraulica`).
   - Al recargar la página o generar el reporte Excel, ambos respetan la misma edición seleccionada sin discrepancias.
2. **Costos no silenciados ante error de inventario previo:**
   - Si un día anterior tiene error de inventario (línea de tiempo o volumetría inválida), los costos diarios ya no se muestran en $0.00 en silencio.
   - Aparece un banner explicativo ámbar en la Pestaña 1 y en el modal de costos indicando claramente que los costos están en espera de la resolución del inventario previo.
3. **Validación física Mecha vs Hoyo:**
   - En la Pestaña 1, si se ingresa una profundidad de mecha (`bit_depth`) mayor a la profundidad actual del hoyo (`profundidad_actual`), aparece una advertencia en tiempo real y el guardado notifica un toast de advertencia.
4. **Caída de presión en herramientas de fondo (MWD y Motor PDM):**
   - En la Pestaña 2 (Pumps/Bits), los campos `dp_mwd` y `dp_motor` se escalan con el caudal según la norma API RP 13D y se suman a la pérdida de la sarta y a la presión total en la Pestaña 8.
5. **Caudal de bombas de Riser:**
   - Las bombas marcadas como `riser_pump` se excluyen de la circulación interna de perforación (sarta, mecha, boquillas y Bottoms Up).
   - Su caudal se maneja como booster y se sincroniza en el campo `riser_pump_flow_rate`.
6. **Survey direccional (Curvatura Mínima):**
   - Si la primera estación tiene $MD > 0$, el motor conecta un punto de amarre en superficie (0, 0, 0) para que el Norte y Este acumulados no se pierdan.
   - La Sección Vertical ($VS$) se proyecta a lo largo del acimut especificado en la casilla `Azimut SV (°)`.
7. **Ecuación de sólidos única:**
   - La ecuación de análisis de sólidos se fija permanentemente en la Norma API RP 13B, eliminando selectores interactivos sin efecto.
8. **Número de reporte fijo:**
   - `numero_reporte` es un campo fijo en base de datos. Si se inserta un reporte intermedio (ej. fecha atrasada), los reportes posteriores no se reenumeran automáticamente.
9. **Visualización de Operador y Taladro:**
   - Propiedades directas en el modelo `Pozo` (`pozo.operador`, `pozo.taladro`) conectadas de forma segura a `WellHeaderInfo` para mostrar el operador en el Hub y encabezados.
10. **Continuidad del balance volumétrico y pérdidas del sistema circulante:**
   - El volumen final calculado del reporte $N$ pasa directamente como volumen inicial del reporte $N+1$, garantizando que las pérdidas operacionales y adiciones queden reflejadas en la línea de tiempo.
   - En el modal de registro de pérdidas, se preselecciona automáticamente el tanque activo del sistema circulante y se actualiza la etiqueta a *"Tanque de la pérdida (volumen circulante)"*.

---

## Pasos para verificar

### 1. Hidráulica 4ª vs 5ª Edición
- [ ] Entrar al reporte diario y navegar a la **Pestaña 8 (Hidráulica)**.
- [ ] Hacer clic en el botón `4ª Edición`. Verificar que se actualicen las pérdidas.
- [ ] Recargar la página (F5): verificar que la pestaña permanezca en `4ª Edición`.
- [ ] Hacer clic en `5ª Edición`. Recargar la página (F5): verificar que continúe en `5ª Edición`.

### 2. Aviso de inconsistencia de costos
- [ ] En un pozo con reporte donde el día anterior presente un error de inventario, revisar la tarjeta de costos en la Pestaña 1.
- [ ] Verificar que muestre el banner explicativo de advertencia indicando la causa en vez de mostrar un simple $0.00 sin explicación.

### 3. Validación de Mecha vs Hoyo
- [ ] En la **Pestaña 1 (General)**, colocar `Profundidad = 3000 ft` y `Mecha = 3500 ft`.
- [ ] Verificar que aparezca el aviso interactivo ámbar debajo del campo de mecha: *"La profundidad de la barrena supera la profundidad actual del hoyo"*.
- [ ] Hacer clic en **Guardar Datos Generales**: verificar que el toast muestre la advertencia.

### 4. Herramientas de fondo e Hidráulica
- [ ] En la **Pestaña 2 (Pumps/Bits)**, ingresar `dP MWD = 100` y `dP Motor = 200`. Guardar.
- [ ] Ir a la **Pestaña 8 (Hidráulica)**: verificar que en las entradas aparezca `dP Herramientas: 300 psi` y que en el KPI de pérdida de sarta se indique el desglose con herramientas.

### 5. Bombas de Riser
- [ ] En la **Pestaña 2**, marcar una de las bombas activas como `Bomba Riser`.
- [ ] Hacer clic en **Copiar Caudal**: verificar que el caudal de perforación solo sume las bombas no-riser y que el caudal de la bomba riser vaya a `Caudal Bomba Riser`.
- [ ] En la Pestaña 8, verificar que la velocidad de chorro y pérdida en boquillas de la mecha usen únicamente el caudal de perforación.

### 6. Survey Direccional
- [ ] Abrir el modal de **Well Survey** en la Pestaña 1.
- [ ] Ingresar una estación directamente en `MD = 1500`, `Inc = 10`, `Az = 90`.
- [ ] Ingresar en `Azimut SV (°)` el valor `90`. Hacer clic en **Recalcular TVD / DLS**.
- [ ] Verificar que la sección vertical y el desplazamiento Este acumulen correctamente desde superficie.

### 7. Análisis de Sólidos API
- [ ] En la **Pestaña 3 (Propiedades)**, abrir el modal de **Especificaciones GE**.
- [ ] Verificar que el tipo de ecuación muestre la etiqueta fija `API RP 13B` en lugar de un selector desplegable.

### 8. Número de Reporte Fijo
- [ ] Crear tres reportes para las fechas: 01-oct, 03-oct y 04-oct. Verificar que queden numerados como Reporte #1, #2 y #3.
- [ ] Crear un nuevo reporte con fecha intermedia: 02-oct.
- [ ] Entrar al reporte del 03-oct: verificar que siga siendo el **Reporte #2** (no se reenumera a #3).
- [ ] Entrar al reporte del 04-oct: verificar que siga siendo el **Reporte #3** (no se reenumera a #4).

### 9. Visualización del Operador y Taladro
- [ ] En la pantalla principal del pozo, entrar en **Información General del Pozo** (`well-header/`).
- [ ] Ingresar el nombre del operador (ej. `CHEVRON`) y del taladro (ej. `TALADRO-01`), y hacer clic en **Guardar**.
- [ ] Entrar al Hub **Fluidos de Perforación y Equipos**: verificar que en la barra superior, el campo **Operador** muestre `CHEVRON` en lugar del guión `—`.
- [ ] Abrir cualquier reporte diario: verificar que en el título aparezca `(Pozo: NOMBRE • CHEVRON)` y en la tarjeta del taladro aparezca `Taladro • TALADRO-01`.

### 10. Continuidad del Balance Volumétrico y Pérdidas
- [ ] En un reporte (Día 1), agregar a un tanque activo 400 bbl de agua y químicos.
- [ ] Registrar pérdidas operacionales (ej. Evaporación 18 bbl y Formación 50 bbl): verificar que el modal rotule el campo como *"Tanque de la pérdida (volumen circulante)"* y preseleccione el tanque activo.
- [ ] Verificar en el Balance de Fluidos que las pérdidas resten en la columna **Sistema Activo** (-68 bbl) y que el **Volumen final calculado** del Sistema Activo refleje el descuento (ej. 344 bbl).
- [ ] Guardar la volumetría y pasar al reporte del día siguiente (Día 2).
- [ ] En el Día 2, verificar que el **Volumen Inicial** del tanque y del Sistema Activo arranque con el volumen final calculado de ayer (344 bbl) y no con el aforo anterior.


