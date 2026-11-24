# Prueba 30 — Validación de Fecha de Reportes vs. Spud Date

Verifica que los reportes diarios no puedan crearse ni fecharse antes del inicio oficial de perforación (*Spud Date*) configurado en la información del pozo (*Well Header Information*).

---

## Cómo funciona

1. **En el Hub de Reportes Diarios (`daily_reports_hub.html`):**
   - El input de fecha del modal `#modalFecha` adquiere el atributo `min="YYYY-MM-DD"` correspondiente al Spud Date del pozo si éste existe.
   - Si el operador intenta ingresar manualmente una fecha anterior, el frontend notifica de inmediato: `"La fecha no puede ser anterior a la fecha de inicio / Spud Date (YYYY-MM-DD)"`.
   - Si el operador hace clic en el botón de atajo `⚓ Fecha Inicio`, la fecha se fija exactamente en el Spud Date.
2. **En la Pestaña 1 del Reporte Diario (`reporte_diario_detalle.html`):**
   - El input `#f_fecha` incluye el atributo `min` restrictivo.
   - La función `guardarGeneral` valida que la fecha no sea anterior al Spud Date antes de enviar la solicitud.
3. **En el Backend (`views_daily_reports.py`):**
   - Tanto `api_reporte_diario_crear` como `api_reporte_diario_general_guardar` validan mediante `_validar_fecha_reporte_spud(pozo, fecha_obj)` que la fecha no sea anterior a `pozo.well_header_info.spud_date`.
   - Si se envía una fecha previa, la API responde con HTTP 400 y el mensaje claro:
     `"La fecha del reporte (DD/MM/AAAA) no puede ser anterior a la fecha de inicio de perforación / Spud Date (DD/MM/AAAA)."`
   - Si el pozo aún no tiene Spud Date configurado, el sistema es flexible y permite el registro sin bloqueos.

---

## Pasos para verificar

### Preparación
1. Abrir el sistema y entrar a un pozo activo (ej. `POZO TEST SPUD`).
2. Ir a **Información del Pozo -> Well Information** y verificar que tenga un **Spud Date** configurado (por ejemplo, `15/10/2026`).

### 1. Intentar crear un reporte antes del Spud Date
- [ ] Ir a **Reportes Diarios (Hub)**.
- [ ] Hacer clic en el botón `+ Nuevo Reporte Diario`.
- [ ] En el modal, observar que el input de fecha no permite navegar hacia atrás del `15/10/2026` debido al atributo `min`.
- [ ] Forzar o tipear una fecha anterior (ej. `10/10/2026`) y hacer clic en `OK (Crear Reporte)`.
- [ ] **Resultado esperado:** Aparece una notificación flotante indicando que la fecha no puede ser anterior a la fecha de inicio / Spud Date y la creación es rechazada sin llamar al servidor o recibiendo rechazo 400.

### 2. Crear un reporte en la fecha del Spud Date y posterior
- [ ] En el modal, hacer clic en el botón `⚓ Fecha Inicio`. La fecha se fija en `15/10/2026`.
- [ ] Hacer clic en `OK (Crear Reporte)`.
- [ ] **Resultado esperado:** El reporte para `15/10/2026` se crea exitosamente.
- [ ] Crear otro reporte para el día siguiente (`16/10/2026`).
- [ ] **Resultado esperado:** Se crea exitosamente sin inconvenientes.

### 3. Intentar editar la fecha de un reporte a una anterior al Spud Date
- [ ] Entrar al reporte del `16/10/2026` (Pestaña 1 - General).
- [ ] En el campo **Fecha**, intentar cambiarla a `05/10/2026`.
- [ ] Hacer clic en **Guardar Pestaña**.
- [ ] **Resultado esperado:** Se rechaza el guardado con aviso de que la fecha no puede ser anterior al Spud Date.
- [ ] Cambiar la fecha a `17/10/2026` y guardar.
- [ ] **Resultado esperado:** Se guarda correctamente.

