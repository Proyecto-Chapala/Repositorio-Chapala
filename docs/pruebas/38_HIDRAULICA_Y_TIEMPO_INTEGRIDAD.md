# 38 — Integridad en Hidráulica, Distribución de Tiempo y Reportes Diarios

Blindaje de mutación contra pozos cerrados en el módulo de Hidráulica (API RP 13D 4ª y 5ª edición), y normalización simétrica de respuestas (`ok: True/False` y `success: True/False`) en Hidráulica, Cost Overview, Distribución de Tiempo y ciclo de vida de Reportes Diarios.

---

## Cómo funciona

1. **Blindaje de Pozos Cerrados en Hidráulica (`api_hidraulica_detail`):**
   - El endpoint `api_hidraulica_detail` (`/api/pozos/<id>/daily-report/<reporte_id>/hidraulica/`) admite peticiones `POST` para conmutar la edición de cálculo de la norma API RP 13D (4ª vs 5ª edición).
   - Ahora, al recibir un `POST`, invoca `_validar_pozo_abierto(pozo)`. Si el pozo se encuentra en estado `CERRADO`, rechaza la mutación inmediatamente con código HTTP 400 y mensaje en español: `"El pozo '<nombre>' está cerrado. No se permiten modificaciones."`.
   - Se protege el atributo `pozo.usar_api_5ta_edicion_hidraulica` en la base de datos contra modificaciones no autorizadas en pozos archivados.

2. **Normalización Simétrica de Respuestas JSON (`ok` y `success`):**
   - **Hidráulica (`calcular_hidraulica_reporte`):** el diccionario base devuelto por el motor de cálculo incluye `'ok': True` y `'success': True`.
   - **Cost Overview (`api_cost_overview_detail`):** incluye `'ok': True` y `'success': True`.
   - **Distribución de Tiempo (`api_tiempo_detail`, `api_tiempo_guardar`):**
     - En consulta exitosa: `'ok': True`, `'success': True`.
     - En guardado exitoso: `'ok': True`, `'success': True`.
     - En error de validación física o de horas del período: `'ok': False`, `'success': False`.
   - **Ciclo de Vida del Reporte Diario (`api_reporte_diario_crear`, `api_reporte_diario_eliminar`, `api_reporte_diario_general_guardar`):**
     - En éxito: `'ok': True`, `'success': True`.
     - En rechazo (pozo cerrado, fecha inválida, duplicada, regla LIFO): `'ok': False`, `'success': False`.
   - **Listados y Detalles de Contexto (`api_well_survey_guardar`, `api_formation_tops_guardar`, `api_pumps_bits_guardar`, `api_sarta_reporte_anterior`, `api_comentarios_detail`):**
     - Respuestas normalizadas con `'ok'` y `'success'` en todas las ramas de éxito y error.

---

## Pasos para verificar

### 1. Preparación
- [ ] Ejecutar el servidor o correr la suite de pruebas unitarias:
  ```bash
  python manage.py test operaciones.tests.test_hidraulica_tiempo_integridad
  python manage.py test operaciones.tests.test_pozo_cerrado_blindaje
  ```
  Comprobar que todas las pruebas pasen con `OK`.

### 2. Blindaje de Pozo Cerrado en Hidráulica
- [ ] Acceder a un pozo activo, generar un reporte diario e ingresar a la **Pestaña 8 (Hidráulica)**.
- [ ] Cambiar la edición de cálculo entre 4ª y 5ª edición: verificar que el cambio se guarde y la respuesta sea 200 con `ok: true` y `success: true`.
- [ ] Cerrar el pozo operacionalmente desde la pantalla de Reporte Final (Recap) o Pantalla Principal.
- [ ] Intentar enviar una petición `POST` al endpoint de hidráulica:
  - Verificar que la petición sea rechazada con código HTTP 400.
  - Verificar que el JSON retorne `{"ok": false, "success": false, "error": "El pozo '...' está cerrado. No se permiten modificaciones."}`.
  - Verificar que en la base de datos no se altere la edición de cálculo del pozo.

### 3. Distribución de Tiempo y Cost Overview
- [ ] Abrir el modal de **Cost Overview** en la cabecera del reporte: verificar que los datos carguen correctamente y la respuesta devuelva `ok: true` y `success: true`.
- [ ] Ingresar a la **Pestaña 7 (Distribución de Tiempo)**:
  - Guardar una distribución válida (ej. 24 h): verificar mensaje exitoso y `success: true`.
  - Intentar guardar horas del período inválidas o negativas (ej. `-5`): verificar respuesta 400 con `ok: false` y `success: false`.

