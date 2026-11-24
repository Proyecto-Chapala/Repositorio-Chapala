# Prueba 28 — Protección e Integridad de Intervalos de Revestimiento

> **Documento de referencia:** [05](../05_CONFIGURACION_POZO.md), [16](../16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md) y [00](../00_TRASPASO.md).  
> **Migración:** No requiere.

---

## Cómo funciona

Los intervalos de revestimiento (`IntervaloRevestimiento`) estructuran la geometría del pozo y permiten imputar los costos y consumos de los reportes diarios a una fase específica de perforación (`ReporteDiario.intervalo_costo`).

Para evitar pérdida de datos y desajustes en el histórico y en el Recap:
1. **Regla LIFO estricta en eliminación:**
   - Los intervalos de revestimiento son etapas secuenciales de perforación (1, 2, 3...). No se permite eliminar un intervalo intermedio si existen intervalos posteriores, evitando dejar huecos en la numeración correlativa.
   - Solo se puede eliminar el último intervalo registrado (`numero_intervalo === max`). En el frontend, el botón **`Eliminar`** se oculta automáticamente si el intervalo seleccionado no es el último. En el backend, `api_intervalo_eliminar` rechaza la solicitud con HTTP 400 y mensaje en español si existen intervalos posteriores.
2. **Bloqueo de eliminación con reportes imputados:**
   - Si un intervalo ya tiene uno o más reportes diarios asignados, la API `/api/pozos/<id>/casing-intervals/<intervalo_id>/eliminar/` rechaza el borrado con código HTTP 400 y mensaje en español indicando la cantidad de reportes asignados.
   - De esta manera se evita que los reportes queden con `intervalo_costo = None` y se descalibre la contabilidad por intervalo.
3. **Número de intervalo correlativo y protegido:**
   - El campo `#dInterval` en el panel de detalle es de solo lectura (`readonly`), impidiendo modificaciones manuales que desincronicen la correlatividad del pozo.
4. **Protección de pozo cerrado:**
   - Si el pozo se encuentra en estado `CERRADO`:
     - La pantalla de intervalos muestra un banner rojo de advertencia indicando que el pozo está cerrado.
     - El botón **`+ Nuevo`** está deshabilitado.
     - Al abrir el detalle de cualquier intervalo, el panel se muestra en modo **Solo lectura**, con todos sus inputs deshabilitados y los botones de Guardar, Cerrar, Reabrir y Eliminar ocultos/bloqueados.
     - Las APIs de creación, modificación, cierre, reapertura y eliminación responden con error HTTP 400 si el pozo está cerrado.
5. **Unificación de respuestas:**
   - Las respuestas JSON retornan simultáneamente `"success"` y `"ok"` para total interoperabilidad.

---

## Pasos para verificar

### 1. Regla LIFO: Bloqueo de eliminación de intervalos intermedios
- [ ] En un pozo activo con 2 o más intervalos creados (ej. Intervalo 1 e Intervalo 2, sin reportes).
- [ ] Hacer clic en el **Intervalo 1**:
  - [ ] Verificar que el campo **Número de Intervalo** está en modo de solo lectura (`readonly`).
  - [ ] Verificar que el botón **`Eliminar`** está oculto (porque no es el último intervalo).
- [ ] Intentar forzar la eliminación del Intervalo 1 por API:
  - [ ] Verificar que el servidor responde HTTP 400 con el mensaje: *"Solo se puede eliminar el último intervalo registrado (Intervalo 2). Para eliminar el intervalo 1 debes eliminar los intervalos posteriores primero."*
- [ ] Hacer clic en el **Intervalo 2** (el último):
  - [ ] Verificar que el botón **`Eliminar`** está visible.
  - [ ] Eliminar el Intervalo 2: se elimina exitosamente.
  - [ ] Ahora el Intervalo 1 pasa a ser el último: su botón **`Eliminar`** se vuelve visible.

### 2. Bloqueo de eliminación cuando el intervalo tiene reportes
- [ ] En un pozo activo, asegurarse de que un intervalo de revestimiento esté seleccionado como intervalo de costo en al menos un reporte diario (pestaña 4 › *Interval Number*).
- [ ] Ir a **Información del Pozo** › **Intervalos de revestimiento**.
- [ ] Hacer clic en el intervalo para abrir su detalle y pulsar **`Eliminar`**.
- [ ] Confirmar la eliminación: verificar que aparece un toast de error indicando: *"No se puede eliminar el intervalo X porque tiene Y reporte(s) diario(s) asignado(s)..."*.
- [ ] Verificar que el intervalo sigue existiendo intacto en la tabla.

### 3. Bloqueo en pozo cerrado
- [ ] Cerrar el pozo (desde el Recap o la pantalla principal).
- [ ] Entrar a **Intervalos de revestimiento**:
  - [ ] Verificar que aparece el banner: *"Este pozo se encuentra CERRADO. La configuración de intervalos de revestimiento está protegida contra modificaciones..."*.
  - [ ] Verificar que el botón **`+ Nuevo`** está deshabilitado.
- [ ] Hacer clic en un intervalo de la tabla:
  - [ ] Verificar que el título dice *"Intervalo X (Solo lectura)"*.
  - [ ] Verificar que los campos están deshabilitados.
  - [ ] Verificar que no aparecen botones de Guardar, Eliminar ni Cerrar intervalo.

