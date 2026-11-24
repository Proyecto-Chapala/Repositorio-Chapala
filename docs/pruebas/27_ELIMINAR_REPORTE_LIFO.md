# Prueba 27 — Eliminación Segura de Reportes Diarios (Regla LIFO)

> **Documento de referencia:** [06](../06_REPORTE_DIARIO_PESTANAS_1_A_5.md), [16](../16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md) (item C10) y [00](../00_TRASPASO.md).  
> **Migración:** No requiere.

---

## Cómo funciona

En Smart Mud, los reportes diarios están encadenados cronológicamente: el volumen final (`calc_fosa`) de un día pasa como volumen inicial (`inicio_fosa`) del siguiente, y el inventario final de químicos pasa como inventario inicial.

Para proteger la integridad de los cálculos y evitar estados huérfanos o negativos:
1. **Regla LIFO (Last-In, First-Out):** Solo se permite eliminar el **último reporte diario** registrado en el pozo.
2. Si un pozo tiene reportes 1, 2 y 3, únicamente el reporte 3 puede ser eliminado. Si se requiere borrar el reporte 2, debe eliminarse primero el 3.
3. En el Hub de Reportes Diarios (`/pozos/<id>/daily-reports/`), al activar el botón **`🗑️ Eliminar Reporte`**:
   - El último reporte muestra el botón rojo **`🗑️ Eliminar`** activo.
   - Todos los reportes anteriores muestran un indicador **`🔒 Bloqueado`** (con tooltip explicativo).
   - El banner superior aclara que solo el último reporte puede ser eliminado.
   - Si no existen reportes, el botón avisa con un mensaje toast sin abrir el modo eliminación.
4. En el backend, el endpoint `/api/pozos/<id>/reportes-diarios/<reporte_id>/eliminar/` rechaza cualquier intento de borrar un reporte que no sea el último con un error HTTP 400 y mensaje en español indicando el número y fecha del último reporte.

---

## Pasos para verificar

### 1. Activar modo eliminación en un pozo con varios reportes
- [ ] Entrar al Hub de Reportes Diarios de un pozo que tenga 2 o más reportes.
- [ ] Hacer clic en el botón **`🗑️ Eliminar Reporte`** en el encabezado del historial.
- [ ] Verificar que aparece el banner con el texto: *"Modo de Eliminación Activo (Regla LIFO)"*.
- [ ] Verificar que en la tabla, **solo la primera fila** (el último reporte registrado) tiene el botón rojo **`🗑️ Eliminar`** habilitado.
- [ ] Verificar que las filas inferiores muestran el estado **`🔒 Bloqueado`**.

### 2. Confirmación y borrado del último reporte
- [ ] Hacer clic en **`🗑️ Eliminar`** del último reporte.
- [ ] Verificar que se abre el modal de confirmación indicando el número de reporte y fecha correspondiente.
- [ ] Confirmar la eliminación pulsando **`🗑️ Sí, Eliminar Reporte`**.
- [ ] Verificar que el reporte se elimina, la tabla se actualiza y el reporte que era el penúltimo ahora pasa a ser el último.

### 3. Pozo sin reportes o pozo cerrado
- [ ] En un pozo sin reportes diarios, pulsar **`🗑️ Eliminar Reporte`**: verificar que muestra la advertencia *"No hay reportes registrados para eliminar"*.
- [ ] En un pozo con estado `CERRADO`, pulsar **`🗑️ Eliminar Reporte`**: verificar que muestra el aviso de que el pozo está cerrado y debe reabrirse primero.

