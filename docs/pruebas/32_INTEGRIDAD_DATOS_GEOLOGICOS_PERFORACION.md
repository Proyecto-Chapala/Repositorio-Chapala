# Prueba 32 — Transaccionalidad Atómica y Validación de Límites Físicos en Datos Geológicos y de Perforación

Verifica que el guardado de **Formation Tops** (`WellFormationTop`), **Well Survey Stations** (`WellSurveyStation`) y **Bombas / Boquillas / Barrena** (`Pumps / Bits`) aplique validación estricta de límites físicos y geométricos antes de tocar la base de datos, y opere bajo transacciones atómicas (`transaction.atomic()`) para garantizar que ante cualquier error no se pierdan ni borren los registros previamente existentes.

---

## Cómo funciona

1. **Formation Tops (`api_formation_tops_guardar`):**
   - Valida en memoria que `depth_ft >= 0` y que `0 <= porcentaje_arena <= 100`.
   - Si una fila contiene un valor numérico inválido, negativo o fuera de rango, el servidor responde HTTP 400 identificando la fila y el motivo.
   - Solo cuando todas las filas son válidas, abre un bloque atómico (`transaction.atomic()`), elimina los topes anteriores y ejecuta `bulk_create` de los nuevos. Si ocurre algún error en el proceso, la base de datos revierte los cambios y los topes previos quedan intactos.
2. **Well Survey Stations (`api_well_survey_guardar`):**
   - Valida antes del cálculo direccional que `md_ft >= 0`, que la inclinación esté en el rango geométrico $[0^\circ, 180^\circ]$ y que el azimut se encuentre en $[0^\circ, 360^\circ)$.
   - Si alguna estación tiene valores fuera de rango, se rechaza con HTTP 400 sin alterar la base de datos.
   - La eliminación de las estaciones previas y el `bulk_create` de las recalculadas se realiza dentro de `with transaction.atomic():`.
3. **Bombas, Barrena y Boquillas (`api_pumps_bits_guardar`):**
   - Valida que la eficiencia de cada bomba esté en $[0\%, 100\%]$ y que sus dimensiones (camisa, carrera, SPM) no sean negativas.
   - Valida que el tamaño de boquillas y su cantidad no sean negativos.
   - El guardado de bombas, boquillas y barrena ocurre de forma atómica indivisible.

---

## Pasos para verificar

### Preparación
1. Abrir un pozo activo (ej. `POZO TEST GEOLOGIA`).
2. Entrar a un reporte diario existente (Pestaña 1 - General y Pestaña 2 - Pumps/Bits).

### 1. Validación y atomicidad en Formation Tops
- [ ] En la Pestaña 1 (General), localizar la sección de **Formation Tops**.
- [ ] Asegurarse de tener al menos un tope guardado (ej. `TOPE SUPERIOR` a `1500 ft`).
- [ ] Intentar agregar una fila con profundidad negativa (ej. `-500 ft`) o arena inválida (ej. `125%`) y hacer clic en **Guardar Topes**.
- [ ] **Resultado esperado:** Aparece una alerta notificando que la profundidad no puede ser negativa o que el porcentaje de arena debe estar entre 0% y 100%. El guardado es rechazado.
- [ ] Recargar la página:
  - [ ] **Resultado esperado:** El `TOPE SUPERIOR` previamente guardado sigue existiendo intacto sin haberse borrado.
- [ ] Corregir a valores válidos (`2000 ft`, `30%`) y guardar:
  - [ ] **Resultado esperado:** Se guardan exitosamente.

### 2. Validación y atomicidad en Well Survey
- [ ] En la Pestaña 1, abrir la tabla o modal de **Well Survey Stations**.
- [ ] Asegurarse de tener al menos una estación guardada.
- [ ] Intentar ingresar una estación con inclinación inválida (ej. `210°`) o azimut fuera de compás (ej. `400°`) y hacer clic en **Guardar / Recalcular Survey**.
- [ ] **Resultado esperado:** Se rechaza la solicitud indicando los límites geométricos válidos (inclinación 0°-180°, azimut 0°-359.99°).
- [ ] Verificar que las estaciones previas permanecen intactas en la base de datos.
- [ ] Ingresar datos válidos (ej. MD `3000 ft`, Inc `15°`, Az `45°`) y guardar:
  - [ ] **Resultado esperado:** Se calculan TVD, DLS y Sección Vertical y se persisten correctamente.

### 3. Validación y atomicidad en Bombas y Boquillas
- [ ] Ir a la Pestaña 2 (**Pumps / Bits**).
- [ ] En la Bomba 1, ingresar una eficiencia imposible (ej. `150%`) o camisa negativa (ej. `-6.5`) y pulsar **Guardar Bombas e Hidráulica**.
- [ ] **Resultado esperado:** Aparece mensaje de error indicando que la eficiencia debe estar entre 0% y 100% o que el diámetro de camisa no puede ser negativo.
- [ ] En las boquillas, ingresar valores válidos (ej. 3 boquillas de tamaño 14) y valores de bomba válidos (eficiencia 97%).
- [ ] Pulsar **Guardar Bombas e Hidráulica**:
  - [ ] **Resultado esperado:** Se guardan atómicamente y se actualiza el TFA y el caudal total calculado.

