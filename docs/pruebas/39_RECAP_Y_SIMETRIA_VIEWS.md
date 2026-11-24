# Guía de Prueba 39 — Blindaje del Reporte Final (Recap) y Simetría 100% en Views

## Objetivo
Verificar la protección integral de las conclusiones y recomendaciones del pozo en la pantalla de Reporte Final (Recap) cuando el pozo está en estado `CERRADO`, y validar la simetría 100% de los contratos API (`ok` y `success` simultáneos) en todos los endpoints de `operaciones/views.py`.

---

## Cómo Funciona

1. **Protección de Textos de Recap ante Pozo Cerrado (`recap_view` & `recap.html`):**
   - Cuando un pozo pasa a estado `CERRADO`, sus conclusiones, resumen, recomendaciones y lecciones aprendidas quedan blindados contra mutaciones.
   - En la vista HTML (`/pozos/<id>/reporte-final/`), los 4 `<textarea>` se renderizan con atributo `readonly`, el botón «Guardar textos» se deshabilita (`disabled`), y se presenta un banner informativo azul: *"El pozo está cerrado: los textos del reporte final están protegidos contra modificaciones. Para editarlos, reabre el pozo en el Paso 3."*
   - A nivel backend en `recap_view`, cualquier petición `POST` enviada a un pozo `CERRADO` es interceptada y rechazada, impidiendo cualquier sobreescritura en la base de datos y redirigiendo con el parámetro `?error_cerrado=1`.
2. **Simetría 100% de Respuestas JSON (`views.py`):**
   - Se completó la estandarización de todas las respuestas JSON de `operaciones/views.py`.
   - `api_pozo_eliminar` retorna `{"success": False, "ok": False, "error": ...}` ante datos erróneos y `{"success": True, "ok": True, "mensaje": ...}` al confirmar la eliminación a la papelera.
   - Todos los endpoints de catálogos y consultas GET (`api_productos_list`, `api_producto_detail`, `api_pozos_plantillas`, `api_pozo_detail`, `api_well_header_detail`, `api_intervalos_list`, `api_pits_list`, `api_categorias_perdida_list`, `api_general_setup_detail`, `api_almacenes_list`, `api_tipos_distribucion_list`, `api_equipos_list`, `api_mallas_list`, `api_productos_activos_list`, `api_equipos_activos_list`, `api_mallas_activas_list`, `api_equipment_properties_detail`, `api_benchmark_definiciones_detail`, `api_benchmark_targets_detail`) devuelven siempre tanto `success: True` como `ok: True`.
   - Las mutaciones de productos (`api_producto_create`, `api_producto_update`, `api_producto_delete`) y el wizard de pozos (`api_pozo_paso1`, `paso2`, `paso3`, `confirmar`, `spud_date`) responden de forma completamente simétrica con `success` y `ok`.

---

## Pasos para Verificar

### Caso 1: Edición de Recap en Pozo Activo
- [ ] 1. Ingresar a un pozo en estado `ACTIVO` y dirigirse a **Reporte Final** (`/pozos/<id>/reporte-final/`).
- [ ] 2. Escribir textos en Resumen, Conclusiones, Recomendaciones y Lecciones aprendidas.
- [ ] 3. Pulsar **Guardar textos**.
- [ ] 4. Comprobar que la página recarga mostrando el aviso verde *"Conclusiones y recomendaciones guardadas"* y los textos persisten.

### Caso 2: Blindaje de Recap en Pozo Cerrado
- [ ] 1. Cerrar el pozo desde el Paso 3 (**Cerrar pozo**).
- [ ] 2. Observar que en la pantalla de Reporte Final los campos de texto se muestran en modo de solo lectura (fondo atenuado y cursor no permitido).
- [ ] 3. Comprobar que el botón «Guardar textos» está deshabilitado.
- [ ] 4. Visualizar el banner informativo azul indicando que el pozo está cerrado y los textos protegidos.
- [ ] 5. Intentar enviar una petición `POST` manual o por consola y verificar que el backend no altera los datos y redirige con aviso de rechazo.

### Caso 3: Reapertura y Restauración de Edición
- [ ] 1. En el Paso 3, pulsar **Reabrir pozo** y confirmar.
- [ ] 2. Comprobar que los campos de texto vuelven a estar habilitados y el botón «Guardar textos» permite guardar cambios con éxito.

### Caso 4: Simetría de Contratos JSON
- [ ] 1. Ejecutar la suite automatizada:
  ```bash
  python manage.py test operaciones.tests.test_recap_integridad
  ```
- [ ] 2. Verificar que las 8 pruebas pasan exitosamente (`OK`), comprobando `ok` y `success` simultáneos en todos los endpoints de `views.py`.

