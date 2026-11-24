# Prueba 26 — Modificar Pozo (Matriz de corrección de parámetros iniciales)

Documento para verificar en pantalla la funcionalidad de **Modificar pozo**.

---

## Cómo funciona

1. **Acceso directo desde la pantalla del pozo:**
   - En la cabecera de la Pantalla Principal del pozo (`/pozos/<id>/`), en los botones de acción superiores, se incluye el botón **`⚙️ Modificar pozo`**.
2. **Matriz unificada de parámetros iniciales:**
   - La pantalla presenta agrupados en 5 tarjetas los campos definidos durante el alta del pozo:
     1. Identificación del pozo (Nombre, Operador, Campo/Área, Taladro, Contratista).
     2. Sistema de unidades.
     3. Parámetros financieros y monedas (Moneda principal, Decimales, Impuesto %, Moneda secundaria, Cobrar en secundaria).
     4. Parámetros iniciales y Spud Date (Fecha primera captura, Tipo de fluido inicial, Tratamiento/disposición, LOGIT).
     5. Clasificación de pérdidas de lodo.
3. **Validación de unicidad e integridad:**
   - Al editar el nombre, el sistema verifica que no colisione con otro pozo existente ni con un pozo en la Papelera.
   - Si se conserva el mismo nombre, se permite sin arrojar error.
4. **Sincronización:**
   - Al guardar, los cambios se aplican de forma atómica en el registro `Pozo` y en su cabecera `WellHeaderInfo` (por ejemplo, actualizando simultáneamente el Spud Date y el tipo de fluido inicial).

---

## Pasos para verificar

### 1. Acceso a la pantalla de modificación
- [ ] Entrar al sistema e ingresar a cualquier pozo activo desde la lista (`/pozos/`).
- [ ] En la barra superior de acciones de la Pantalla Principal del pozo, verificar la presencia del botón **`⚙️ Modificar pozo`**.
- [ ] Hacer clic en el botón y verificar que redirige a `/pozos/<id>/modificar/`.
- [ ] Comprobar que los campos aparecen prellenados con la información actual del pozo.

### 2. Edición de campos generales y guardado exitoso
- [ ] Modificar el nombre del pozo (por ejemplo agregando un sufijo `- MOD`).
- [ ] Cambiar o completar los campos de **Operador**, **Campo / Área**, **Taladro** o **Contratista**.
- [ ] Cambiar la **Fecha Spud / Primera captura** a una fecha distinta.
- [ ] Cambiar el **Tipo de fluido inicial** (por ejemplo a *Base Aceite* o *Base Agua*).
- [ ] Modificar la **Tasa de impuesto (%)** a un valor válido (ejemplo `16.00`).
- [ ] Hacer clic en **Guardar modificaciones**.
- [ ] Verificar que el sistema redirige a la Pantalla Principal del pozo mostrando un mensaje de éxito: `Las modificaciones del pozo se guardaron exitosamente.`
- [ ] Comprobar que en el encabezado del pozo el nombre nuevo y los datos modificados se reflejan inmediatamente.

### 3. Validación de colisión de nombre con otro pozo
- [ ] Entrar de nuevo a **Modificar pozo**.
- [ ] Intentar cambiar el nombre por el de otro pozo ya existente en el sistema.
- [ ] Hacer clic en **Guardar modificaciones**.
- [ ] Verificar que el formulario no guarda y muestra el error indicando que ya existe un pozo con ese nombre.

### 4. Conservación del nombre sin falsos positivos
- [ ] En el mismo pozo, volver a colocar su propio nombre actual sin modificarlo y cambiar solo otro campo (ej. el contratista).
- [ ] Hacer clic en **Guardar modificaciones**.
- [ ] Verificar que guarda correctamente sin arrojar error de nombre duplicado.

### 5. Botón Cancelar / Volver
- [ ] Entrar a **Modificar pozo**.
- [ ] Hacer clic en **Cancelar**.
- [ ] Verificar que regresa a la Pantalla Principal del pozo sin alterar nada.

### 6. Protección de Pozo Cerrado
- [ ] Cerrar un pozo desde el Recap o la pantalla principal.
- [ ] Ir a la URL `/pozos/<id>/modificar/`.
- [ ] Verificar que aparece el banner de advertencia: `Pozo Cerrado: Este pozo se encuentra actualmente en estado CERRADO...`
- [ ] Comprobar que todos los campos del formulario aparecen deshabilitados y el botón **Guardar cambios** está bloqueado.

### 7. Bloqueo de monedas en pozo con reportes
- [ ] En un pozo que tenga al menos un reporte diario registrado, ingresar a **Modificar pozo**.
- [ ] Verificar que el selector de **Moneda Principal** y la casilla **Cobrar en la segunda moneda** tienen el indicador `🔒 Bloqueado` y están deshabilitados.
- [ ] Modificar cualquier otro campo (ej. Contratista u Operador) y guardar.
- [ ] Verificar que los demás campos se guardan correctamente preservando la moneda original.

### 8. Validación de Spud Date contra primer reporte
- [ ] En un pozo con un reporte del día 10/10/2026, ingresar a **Modificar pozo**.
- [ ] Intentar colocar en **Fecha Inicial (Spud Date)** una fecha posterior (por ejemplo 15/10/2026).
- [ ] Hacer clic en **Guardar cambios**.
- [ ] Verificar que el formulario rechaza el guardado con el mensaje indicando que la fecha inicial no puede ser posterior al primer reporte.

