# Prueba 25 — Cerrar y Reabrir Pozo

Documento para verificar en pantalla la funcionalidad de **Cerrar y Reabrir Pozo**.

---

## Cómo funciona

1. **Desde Reporte Final (Recap):**
   - En la tarjeta derecha, abajo de la descarga, aparece el **Paso 3: Estado del pozo**.
   - Con el pozo activo, se pulsa **«🔒 Cerrar pozo»**, se confirma en el modal y el pozo pasa a cerrado.
   - Con el pozo cerrado, se muestra el badge **🔒 Pozo Cerrado** y el botón **«🔓 Reabrir pozo»** que permite reactivarlo.
2. **Desde la Pantalla Principal del Pozo:**
   - En la zona inferior junto a «Eliminar pozo», se puede pulsar «Cerrar pozo» o «Reabrir pozo».
3. **En el Directorio de Pozos (`/pozos/`):**
   - Un pozo cerrado desaparece de la pestaña «Activos» y aparece en la pestaña «Cerrados» con chip gris neutro.
4. **Protección de Reportes Diarios:**
   - En el Hub de reportes diarios, un pozo cerrado muestra un aviso superior y bloquea la creación/eliminación de reportes hasta que sea reabierto.

---

## Pasos para verificar

### 1. Cerrar pozo desde Reporte Final
- [ ] Entrar a un pozo activo y abrir **Reporte final** (`/pozos/<id>/reporte-final/`).
- [ ] Verificar que en el encabezado aparece el chip `Activo` y en la columna derecha aparece la tarjeta **Paso 3: Estado del pozo** con el botón **🔒 Cerrar pozo**.
- [ ] Hacer clic en **🔒 Cerrar pozo**.
- [ ] Comprobar que se abre el modal de confirmación explicando que el pozo pasará al filtro de «Cerrados».
- [ ] Pulsar **Confirmar cierre**.
- [ ] Verificar que la página recarga, muestra el mensaje verde de éxito y ahora la tarjeta muestra **🔒 Pozo Cerrado** y el botón **🔓 Reabrir pozo**.

### 2. Verificar el filtro en el Directorio de Pozos
- [ ] Ir a **OPERACIÓN › Pozos** en el menú lateral.
- [ ] Con el filtro **Activos** seleccionado, verificar que el pozo cerrado ya no aparece en la lista.
- [ ] Hacer clic en el filtro **Cerrados**.
- [ ] Verificar que ahora el pozo cerrado aparece listado, con su chip gris `Cerrado` y el contador de pozos coincide.

### 3. Verificar protección de reportes en el Hub
- [ ] Hacer clic en el pozo cerrado para entrar a su Hub de reportes diarios (`/pozos/<id>/drilling-fluids-equipment/`).
- [ ] Comprobar que en la parte superior se muestra el banner de aviso avisando que el pozo está cerrado.
- [ ] Intentar hacer clic en **+ Nuevo Reporte** o **Eliminar Reporte** y verificar que la aplicación avisa que el pozo debe reabrirse primero.
- [ ] Verificar que los reportes diarios existentes siguen siendo totalmente legibles y se pueden abrir.

### 4. Reabrir el pozo
- [ ] Hacer clic en **🔓 Reabrir pozo** (desde el banner del Hub, desde Reporte final o desde la configuración principal).
- [ ] Confirmar la reapertura.
- [ ] Verificar que el pozo vuelve a estado **Activo**, el banner del Hub desaparece y se vuelve a permitir la carga normal de reportes.
- [ ] Ir a **OPERACIÓN › Pozos** y comprobar que vuelve a salir bajo la pestaña **Activos**.

