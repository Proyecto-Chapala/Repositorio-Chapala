# Prueba 31 — Sincronización de Spud Date y Tipo de Fluido entre Pantalla Inicial y Well Header Information

Verifica que los datos ingresados en la pantalla de bienvenida/inicial de **Spud Date** (`fecha_primera_captura`, `tipo_fluido_inicial` y `numero_control_logit`) se sincronicen bidireccionalmente y de forma atómica con **Well Header Information** (`spud_date`, `primary_mud_type_codigo`, `numero_control_logit`), asegurando que las sugerencias de fecha y lodo en el Hub de Reportes Diarios y las cabeceras de los reportes se pueblen automáticamente desde el primer día.

---

## Cómo funciona

1. **Al confirmar la pantalla inicial Spud Date (`api_pozo_spud_date`):**
   - Se guardan los datos en el modelo `Pozo` (`fecha_primera_captura`, `tipo_fluido_inicial`, `numero_control_logit`).
   - Se crea o actualiza atómicamente el registro asociado de `WellHeaderInfo` guardando `spud_date = fecha_primera_captura`, `numero_control_logit` y mapeando el tipo de lodo inicial a `primary_mud_type_codigo` y `primary_mud_type_descripcion`.
2. **Sugerencia en el Hub de Reportes Diarios (`daily_reports_hub_view` y `api_reportes_diarios_list`):**
   - Cuando el pozo no tiene reportes previos, la sugerencia de fecha para el primer reporte diario toma el `spud_date` (o en su defecto `pozo.fecha_primera_captura`) en lugar de la fecha de hoy.
   - El tipo de lodo sugerido se mapea inteligentemente al código de `ReporteDiario` (`WBM`, `OBM`, `SBM`, `WBM_CACL2`), activando automáticamente la tarjeta correspondiente en el modal de nuevo reporte.
   - El botón de atajo `⚓ Fecha Inicio` queda activo con la fecha del Spud Date.
3. **Al editar Well Information (`api_well_header_guardar`):**
   - Se mantiene sincronizado el modelo `Pozo` (`fecha_primera_captura` y `numero_control_logit`).
   - Si existen reportes diarios previos, el formulario valida que `spud_date` no sea posterior a la fecha del primer reporte existente, protegiendo la consistencia temporal del pozo.

---

## Pasos para verificar

### Preparación
1. Crear un pozo nuevo (ej. `POZO SYNC TEST`).
2. Completar los pasos del asistente y llegar a la pantalla inicial de **Spud Date**.

### 1. Confirmar Spud Date inicial y verificar Hub
- [ ] Indicar fecha de inicio (ej. `01/11/2026`), tipo de lodo `Base Aceite`, y N° Control Logit `LOGIT-500`.
- [ ] Hacer clic en **Confirmar y Continuar**.
- [ ] Navegar a **Reportes Diarios (Hub)**.
- [ ] Verificar que en el encabezado aparezca: `Inicio de perforación (Spud Date): 01/11/2026`.
- [ ] Hacer clic en `+ Nuevo Reporte Diario`.
- [ ] **Resultado esperado:** El modal sugiere por defecto la fecha `2026-11-01`, la tarjeta de tipo de lodo `Base Aceite (OBM)` aparece seleccionada por defecto, y el botón `⚓ Fecha Inicio` está disponible.

### 2. Verificar sincronización en Well Header Information
- [ ] Ir a **Información del Pozo -> Well Information**.
- [ ] **Resultado esperado:** El campo **Spud Date** muestra `2026-11-01` y **N° Control Logit** muestra `LOGIT-500`.
- [ ] Ir a la pestaña **Marketing Codes**.
- [ ] **Resultado esperado:** En **Primary Mud Type** figura `Base Aceite`.

### 3. Modificar Spud Date en Well Information
- [ ] En **Well Information**, cambiar la fecha Spud a `31/10/2026`.
- [ ] Hacer clic en **Guardar Pestaña**.
- [ ] Regresar al **Hub de Reportes Diarios**.
- [ ] **Resultado esperado:** La fecha de Spud Date reflejada ahora es `31/10/2026` y la sugerencia del primer reporte se actualiza a `31/10/2026`.

### 4. Protección contra fechas Spud posteriores a reportes creados
- [ ] Crear el primer reporte diario fechado el `31/10/2026`.
- [ ] Regresar a **Información del Pozo -> Well Information**.
- [ ] Intentar cambiar la fecha Spud a `05/11/2026` y hacer clic en **Guardar Pestaña**.
- [ ] **Resultado esperado:** El sistema rechaza la modificación indicando: `"La fecha de inicio / Spud Date no puede ser posterior al primer reporte diario existente (31/10/2026)"`.

