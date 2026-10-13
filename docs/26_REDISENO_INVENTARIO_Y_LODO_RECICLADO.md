# 26 — Rediseño del inventario de productos y del lodo reciclado (pestaña 8)

**Fecha:** 13-oct-2026 · **Estado:** instrucciones para ejecutar, partes A a D (A hecha). Avance en el § 7.

Este documento es la **orden de trabajo** para el asistente que programa el cambio. Quien lo ejecute debe leer antes `AGENTS.md`, `docs/00_TRASPASO.md` y `docs/09_PESTANA_8_VOLUMETRIA_INVENTARIO.md`.

---

## 1. Qué pidió el cliente (13-oct-2026)

Hoy el inventario y la volumetría están mezclados. El cliente quiere **separarlos**:

- **Inventario de productos = registro de consumo, nada más.** Recibido (el ticket de recepción), devuelto, usado en fluidos, usado en otro módulo y ajuste. Cada columna lleva su **acumulado**, para que el ingeniero sepa cuánto lleva recibido, devuelto, usado y transferido a otras líneas. No depende de la volumetría ni de las concentraciones.
- **Balance de volumen = volumetría y concentraciones.** *Agregar químicos* calcula el volumen con la gravedad específica, lo suma al tanque (activo o reserva), a "Volumen de químicos agregados" y a las concentraciones.
- **Lodo reciclado = solo volumen.** No consume inventario ni genera costo. El cliente lo aprobó ("chévere").
- Las transferencias a otro taladro son volumetría, no consumo (ya es así; no se toca).

## 2. Reglas obligatorias para quien ejecute

1. **No tocar migraciones existentes** (`0001` a `0035`). Las partes A y B **no necesitan migración**: no se agregan ni se borran campos. Al final, `python manage.py makemigrations --check` debe decir `No changes detected`.
2. **No borrar campos ni datos.** Los campos `lodo_producto`, `lodo_producto_texto`, `lodo_cantidad`, `lodo_precio` y `lodo_categoria` de `TransaccionVolumen` **se quedan** en el modelo; solo dejan de usarse.
3. Archivos con **CRLF**: conservar los finales de línea al editar.
4. Todo texto visible en **español**. Nada de "M-I", "M-I SWACO" ni "ONE-TRAX" en pantalla. Se dice **tanque** (no fosa) y **lodo reciclado** (no lodo entero).
5. CSS y JS en sus archivos (`reporte_inventario.css`, `reporte_inventario.js`); nada en línea en la plantilla.
6. **No correr `git` ni `migrate`.** Lo hace la persona.
7. Hacer **una parte a la vez** (A, luego B). Al terminar cada parte: `python manage.py test operaciones` tiene que pasar entero, y hay que avisar para revisión antes de seguir.
8. Si algo de estas instrucciones no cuadra con el código, **parar y preguntar**. No inventar.
9. Causa raíz, sin parches; no duplicar lógica (DRY).

---

## 3. Parte A — Lodo reciclado solo como volumen

### Resultado esperado

*Agregar lodo reciclado* suma volumen al tanque (y masa para concentraciones si se escriben las lb/bbl del lodo), y cuenta como "recibido" en los flujos del balance. **No** descuenta ningún producto del inventario y **no** genera costo. Ya no se elige "producto de lodo reciclado".

Aplica también a los movimientos de lodo reciclado ya guardados: el motor deja de leer `lodo_producto`, así que su consumo y su costo dejan de contarse. Es lo acordado.

### Pasos

**A1. `operaciones/volumetria.py`**
- En `simular()`, rama `elif tipo == 'LODO_ENTERO':` (cerca de la línea 299): **borrar** el bloque `lp = tr.get('lodo_producto')` / `if lp: ...` completo (las líneas que suman a `usado_fluido`, `costo_dia_prod` y `costo_dia_cat`). Lo demás de la rama (masa de concentraciones, `delta`, `vol_comp`, `flujos[g]['recibido']`) queda igual.
- En el docstring de `simular()`, quitar `'lodo_producto', 'lodo_cantidad', 'lodo_precio', 'lodo_categoria'` de la descripción de `transacciones`.
- **Borrar** la función `consumo_lodo_entero()`. Antes, buscar con grep que nadie más la use (hoy solo `views_inventario.py`).

**A2. `operaciones/views_inventario.py`**
- `_dto_transaccion()` (cerca de la línea 270): quitar las claves `lodo_producto`, `lodo_cantidad`, `lodo_precio` y `lodo_categoria` del diccionario.
- `_linea_de_tiempo()` (cerca de la línea 321): quitar `if t['lodo_producto']: ids_producto.add(t['lodo_producto'])`.
- `api_volumetria_transaccion()`, rama `elif tipo == TransaccionVolumen.LODO_ENTERO:` (cerca de la línea 956): quitar la lectura de `lodo_producto_id`, el rechazo "Elige el producto de lodo reciclado…" y las asignaciones `t.lodo_producto_id`, `t.lodo_producto_texto`, `t.lodo_cantidad`, `t.lodo_precio` y `t.lodo_categoria`. Esos campos quedan con su valor por defecto.
- `_texto_movimiento()` (cerca de la línea 392): el título del lodo reciclado ya no lleva `({t.lodo_producto_texto})`. Si un movimiento viejo lo tiene, no mostrarlo; el título queda `"{v} de lodo reciclado{peso} agregados a {origen}{desde}"`.

**A3. `operaciones/static/operaciones/js/reporte_inventario.js`**
- En `vaRenderModal()`, bloque `vaModalTipo === 'lodo'` (cerca de la línea 897): quitar el campo "2. Producto de lodo reciclado" (`vaLProducto`, su ayuda "Se descuenta del inventario…" y la variable `lodos`). Renumerar los rótulos que siguen: "2. Recibido de", "3. Volumen".
- En `vaRegistrarLodo()` (cerca de la línea 1036): quitar `lodo_producto_id` del cuerpo enviado.

**A4. Pruebas**
- `operaciones/tests/test_balance_volumetria.py` línea ~58: el movimiento `LODO_ENTERO` ya no necesita `lodo_producto`, `lodo_cantidad` ni `lodo_precio`; quitarlos del llamado y revisar que la prueba siga verificando lo mismo del balance.
- Revisar `operaciones/tests/test_fluido_externo.py` y cualquier otra prueba que mencione `lodo_producto` o `consumo_lodo_entero` (`grep -rn "lodo_producto\|consumo_lodo" operaciones/tests`).
- **Agregar** en `operaciones/tests/test_volumetria_inventario.py` (o en un archivo nuevo `test_lodo_reciclado.py`), con funciones puras de `vol.simular`:
  1. Un `LODO_ENTERO` de 100 bbl en un tanque activo suma 100 al volumen calculado del tanque y 100 a `flujos[ACTIVO]['recibido']`.
  2. Si la transacción trae (por datos viejos) `lodo_producto` y `lodo_cantidad`, **no** aparece consumo en `sim['inventario']` ni costo en `sim['costo_dia_cat']`.
  3. Las concentraciones del lodo (lb/bbl × volumen) siguen entrando en la masa del compartimento.
- Una prueba de la API (`TestCase`): `POST .../volumetria/transaccion/` con `tipo: 'LODO_ENTERO'`, tanque, volumen y **sin** `lodo_producto_id` responde `ok: true`.

**A5. Documentación**
- `docs/09_PESTANA_8_VOLUMETRIA_INVENTARIO.md`, fila **Agregar lodo reciclado** (línea ~60): describirla como "Tanque · volumen · peso · origen · concentraciones del lodo (lb/bbl). Suma volumen. No toca el inventario ni genera costo."
- Crear `docs/pruebas/16_LODO_RECICLADO_SOLO_VOLUMEN.md` con "Cómo funciona" y "Pasos para verificar" con casillas (mismo formato que `pruebas/15`), y agregarlo al índice `docs/pruebas/README.md`.
- Marcar la parte A como hecha en el § 7 de este documento.

---

## 4. Parte B — Acumulados por columna en el inventario

### Resultado esperado

La tabla *Inventario diario de productos* muestra, además de lo del día, el **acumulado del pozo hasta este reporte** de: **Recibido, Devuelto, Usado en fluidos y Usado en otro módulo**. El de *usado en otro módulo* es lo que el ingeniero lleva transferido a otras líneas (por ejemplo, cementación).

### Pasos

**B1. `operaciones/volumetria.py`** (función `simular`, bloque del inventario, cerca de la línea 370)
- Hoy existen `acum_usado` (fluidos + otro módulo juntos), `acum_recibido` y `acum_devuelto`. **Agregar** `acum_usado_fluido` y `acum_usado_otro` (inicializados igual que los otros acumulados, antes del bucle de días; buscar dónde se crea `acum_usado`).
- En cada día: `acum_usado_fluido[p] += usado_fluido[p]` y `acum_usado_otro[p] += otro`.
- En `inventario[p]` agregar las claves `'usado_fluido_acum'` y `'usado_otro_acum'`. **No** quitar `usado_acum`: lo usa el Excel (`reporte_excel.py`, columna G).
- Los servicios viejos (productos sin unidad) siguen igual.

**B2. `operaciones/views_inventario.py`** (`_estado_volumetria`, armado de `inventario`, cerca de la línea 548)
- Agregar `usado_fluido_acum=round(s.get('usado_fluido_acum', 0.0), 3)` y `usado_otro_acum=round(s.get('usado_otro_acum', 0.0), 3)` al lado de `recibido_acum` y `devuelto_acum`.

**B3. Plantilla** `operaciones/templates/operaciones/avances_19_sep/reporte_diario_detalle.html` (tabla `va-tabla-inv`, cerca de la línea 2390)
- En la fila de grupos agregar después de "Costos" un grupo `<th colspan="4" class="cs-grupo-acumulados">Acumulado del pozo</th>`.
- En la fila de títulos, en ese lugar: "Recibido", "Devuelto", "Usado en fluidos", "Usado otro módulo" (todos `cs-num cs-grupo-acumulados`).

**B4. `reporte_inventario.js`** (`vaRenderInventario`, cerca de la línea 593)
- Después de las 3 celdas de costos, agregar 4 celdas `cs-num cs-grupo-acumulados` con `vaCant(r.recibido_acum)`, `vaCant(r.devuelto_acum)`, `vaCant(r.usado_fluido_acum)` y el de otro módulo **en vivo**: `r.usado_otro_acum - r._otro_guardado + (csNum(r.usado_otro) || 0)`, con un `data-inv-otro-acum="${id}"` para actualizarlo en el manejador `input` (donde hoy se actualizan `data-inv-final`, `data-inv-usado` y `data-inv-costo`, cerca de la línea 1133).
- Cambiar el `colspan="18"` de la fila vacía a `22`.
- En el filtro "Solo con existencia o movimiento", considerar también `r.usado_otro_acum`.

**B5. `reporte_inventario.css`**
- Agregar `.cs-grupo-acumulados` con el mismo estilo que `.cs-grupo-costos` (buscar esa clase en `reporte_control_solidos.css` y copiar solo el color de fondo, con otro tono suave, usando las variables de color ya definidas).

**B6. Pruebas** (en `test_volumetria_inventario.py`, funciones puras)
- Dos días: el día 1 usa 10 en fluidos y 3 en otro módulo; el día 2 usa 5 y 2 → en el día 2, `usado_fluido_acum = 15`, `usado_otro_acum = 5` y `usado_acum = 20`.
- En la misma prueba, con un ticket de entrada de 50 el día 1 y otro de 20 el día 2 (y una devolución de 4 el día 2): `recibido_acum = 70` y `devuelto_acum = 4` en el día 2. Hoy no hay prueba de estos acumulados.

**B7. Documentación**
- `docs/09_PESTANA_8_VOLUMETRIA_INVENTARIO.md`: en la tabla de columnas del inventario agregar "Acumulado del pozo (recibido, devuelto, usado en fluidos, usado otro módulo)".
- Crear `docs/pruebas/17_ACUMULADOS_INVENTARIO.md` y agregarlo al índice.
- `docs/MANUAL_USUARIO.md`, paso del inventario: mencionar los acumulados.
- Marcar la parte B como hecha en el § 7.

### Fuera de alcance de la parte B

- **No** cambiar el Excel diario (`reporte_excel.py`) en esta parte.
- **No** volver manual Usado en fluidos: eso es la parte C (§ 5).

---

## 5. Parte C — Inventario de consumo separado del balance de volumen

**Ejecutar después de la parte B** (usa sus acumulados). Lleva **una migración nueva**.

### Respuestas del cliente (13-oct-2026)

1. **El costo de los químicos sale del inventario:** *Usado en fluidos* (escrito a mano) × precio, igual que *Usado otro módulo*. *Agregar químicos* deja de generar costo.
2. **Tickets:** el ticket de **recepción** llena *Recibido* y el ticket de **devolución** llena *Devuelto*. Eso ya existe (tipos de ticket con sentido `ENTRADA`/`SALIDA`: "Recepción desde almacén", "Devolución a almacén", etc.) y **no se cambia**. La entrada "a mano" de recibido y devuelto **es el ticket**. Lo que pasa a escribirse en la tabla es **Usado en fluidos**.
3. **Gravedad específica:** se sigue cargando en *Productos activos* (la "formulación"). En *Agregar químicos* (balance de volumen) se toma la cantidad del producto que se agrega y con su GE se calcula el volumen, que suma en **Volumen de químicos agregados** y en las concentraciones. Eso ya lo hace el motor; la ventana debe **mostrar la GE** de cada producto.
4. **Pozos con datos:** se aplica a todos. Los consumos que hoy salen de *Agregar químicos* dejan de descontar inventario y de costar; esos pozos quedan sin consumo hasta que se escriba a mano. Aceptado por el cliente.

### Resultado esperado

- *Agregar químicos*: suma volumen (con la GE) al tanque, a "Volumen de químicos agregados" y a las concentraciones. **No** descuenta inventario, **no** genera costo y **no** se rechaza por falta de existencia.
- Inventario: `Final = Inicial + Recibido (tickets) − Devuelto (tickets) − Usado en fluidos (a mano) − Usado otro módulo (a mano) ± Ajuste`. Si el final queda negativo, se rechaza al guardar (regla actual).
- Costo del producto en el día = (Usado en fluidos + Usado otro módulo) × precio del día. Suma en la categoría del producto como hoy.

### Pasos

**C1. Modelo y migración**
- `operaciones/models_inventario.py`, `InventarioProductoDia`: agregar `usado_fluido = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name="Usado en fluidos")`, al lado de `usado_otro`. Actualizar el docstring de la clase y el del módulo (la fórmula del final).
- Crear la migración con `python manage.py makemigrations operaciones -n inventario_usado_fluido_manual`. Debe salir **`0036_inventario_usado_fluido_manual`** y depender de **`0035_servicios_del_pozo`**. Solo debe contener el `AddField`. No la aplica la IA: avisar a la persona que corra `migrate`.

**C2. Motor** `operaciones/volumetria.py`, `simular()`
- Rama `if tipo == 'QUIMICOS':` quitar `usado_fluido[p['producto']] += cant` y las 3 líneas del costo (`costo`, `costo_dia_prod`, `costo_dia_cat`). Se queda el volumen (`vq`) y la masa de concentraciones.
- En el bloque del inventario (donde hoy se lee `otro = float(m.get('otro') or 0)`): leer también `fluido = float(m.get('fluido') or 0)` y usarlo como el usado en fluidos del día (reemplaza al `usado_fluido[p]` que venía de los movimientos; la variable `usado_fluido` del día puede quedar eliminada si ya no se usa).
- Costo del día: `(fluido + otro) * precio` (un solo cálculo, no dos copias).
- Servicios viejos (productos sin unidad): igual que hoy, solo costo.
- Actualizar el docstring del módulo (líneas de "Inventario de productos") y el de `simular()` (`'manual': {producto_id: {'inicial', 'fluido', 'otro', 'ajuste', 'precio', 'categoria'}}`).
- El mensaje de error de inventario negativo queda igual.

**C3. Vistas** `operaciones/views_inventario.py`
- `_linea_de_tiempo()`, diccionario `manual`: agregar `'fluido': float(m.usado_fluido)`.
- `api_volumetria_guardar()`, bucle del inventario: leer `fluido = _num(item.get('usado_fluido'), f"{etq} — usado en fluidos", 0) or 0.0`. Para servicios (`p['servicio']`) forzar `0.0`. Incluir `fluido` en la condición que decide si se guarda la fila y pasarlo a `InventarioProductoDia(usado_fluido=_dec(fluido), ...)`.
- `_estado_volumetria()`, armado de `inventario`: `usado_fluido` sigue viniendo de la simulación (`s.get('usado_fluido')`), ahora es lo escrito a mano. Agregar `agregado_balance`: la cantidad de ese producto agregada hoy con *Agregar químicos* (sumar `p.cantidad` de los `TransaccionVolumenProducto` del reporte con `transaccion__tipo='QUIMICOS'` y `es_concentracion=False`). Es **solo de referencia** para el ingeniero; no entra en ningún cálculo.

**C4. Pantalla** `reporte_inventario.js` y la plantilla
- Tabla del inventario: la celda *Usado en fluidos* pasa a ser un `<input type="number" class="cs-input-cant va-input" min="0" step="any" data-inv="${id}" data-campo="usado_fluido">`, deshabilitada para servicios (como *Ajuste*). Si `r.agregado_balance` es mayor que 0, mostrar debajo un texto chico gris (`cs-tenue`): "Balance: {cantidad}".
- `vaAplicar()`: guardar `r._fluido_guardado = r.usado_fluido` y conservar `usado_fluido` en el bloque `previo` (igual que `usado_otro`).
- `vaCapturar()`: enviar `usado_fluido`.
- `vaFinalVivo()`, `vaCostoVivo()`, la celda *Usado hoy* (`data-inv-usado`) y el acumulado en vivo de la parte B: usar el valor escrito de `usado_fluido` menos `_fluido_guardado`, igual que se hace con `usado_otro`. **Extraer** una función `vaUsadoVivo(r)` = fluido escrito + otro escrito, y usarla en esos lugares para no repetir la fórmula.
- Filtro "Solo con existencia o movimiento": considerar `csNum(r.usado_fluido)`.
- Ventana *Agregar químicos* (`vaRenderModal`, bloque `quimicos`):
  - Agregar la columna **GE** (después de *Unidad*) con `r.gravedad ? csFmt(r.gravedad, 2) : '—'`.
  - Quitar la columna *Disponible* y la marca `cs-dif` por pasarse de la existencia (ya no descuenta inventario).
  - En `vaQRecalcular()`, quitar "Costo de los productos" del resumen.
  - Cambiar la nota del pie a: "El volumen de cada producto se calcula con su gravedad específica (lb / (350 × GE)) y suma en el volumen de químicos agregados y en las concentraciones. No descuenta inventario: el consumo se escribe en *Inventario de productos*."
- Plantilla `reporte_diario_detalle.html`: el subtítulo de *Inventario diario de productos* debe decir que recibido y devuelto salen de los tickets de recepción y devolución, y que usado en fluidos, usado otro módulo y ajuste se escriben a mano. Revisar que ningún texto diga que *Agregar químicos* descuenta inventario.

**C5. Pruebas**
- Muchas pruebas actuales suponen que *Agregar químicos* consume inventario y cuesta (`grep -ln "QUIMICOS" operaciones/tests`: `test_balance_volumetria`, `test_editar_movimientos`, `test_fluido_externo`, `test_precio_por_barril`, `test_servicios_pozo`, `test_trailer`, `test_volumetria_inventario`). Corregirlas **cambiando lo que esperan según la regla nueva**, no borrando verificaciones. Donde una prueba quería probar el consumo o el costo de un producto, pasar la cantidad a `manual[producto]['fluido']`.
- En `test_precio_por_barril`, el costo por barril se debe seguir probando, ahora con el usado escrito a mano.
- **Agregar** (funciones puras):
  1. *Agregar químicos* con 10 sacos suma su volumen al tanque y a `flujos[ACTIVO]['quimicos']`, y deja el inventario y el costo del producto sin cambios.
  2. Un *Agregar químicos* sin existencia del producto **no** se rechaza.
  3. `manual = {p: {'fluido': 4, 'otro': 1, 'precio': 10}}` con 20 recibidos → final 15, `usado_dia` 5, costo del día 50.
  4. `fluido` que deja el final negativo → `ErrorVolumetria`.
- **Agregar** (API): guardar la volumetría con `usado_fluido` en un producto lo persiste en `InventarioProductoDia.usado_fluido`, y en un servicio se guarda en 0.

**C6. Documentación**
- `docs/09_PESTANA_8_VOLUMETRIA_INVENTARIO.md`: la fila de *Agregar químicos* ("suma volumen y concentraciones; no toca inventario ni costo"), la tabla de columnas del inventario (*Usado en fluidos*: a mano; recibido/devuelto: tickets) y la fórmula.
- `docs/13_COSTOS.md`: el costo de químicos sale del inventario (usado en fluidos + otro módulo) × precio.
- `docs/03_MODELO_DATOS.md`: el campo nuevo `usado_fluido`.
- `docs/MANUAL_USUARIO.md`: el paso del inventario.
- `docs/00_TRASPASO.md`: cadena de migraciones con la **0036** y "la próxima depende de 0036"; `AGENTS.md`, la misma referencia.
- Crear `docs/pruebas/18_INVENTARIO_DE_CONSUMO.md` y agregarlo al índice.
- Marcar la parte C en el § 7.

## 6. Parte D — Excel y recap

**Ejecutar después de la parte C.** Sin migración.

- El Excel diario (`reporte_excel.py`, hoja de inventario) y el recap (`recap_pozo.py`) toman los números de la simulación, así que deberían quedar bien solos. **Verificar** con una prueba por cada uno: con un producto con usado en fluidos manual de 4 a precio 10, la hoja de inventario muestra 4 en *usado* y 40 en *costo diario*, y el recap suma 40 en químicos.
- Si en la hoja de inventario hay un texto que diga que el consumo sale de los movimientos, corregirlo.
- Crear o ampliar la guía `docs/pruebas/18_…` con los pasos del Excel y el recap.
- Marcar la parte D en el § 7.

## 7. Avance

- [x] Parte A — Lodo reciclado solo como volumen
- [x] Parte B — Acumulados por columna
- [x] Parte C — Inventario de consumo separado del balance (migración 0036)
- [x] Parte D — Excel y recap


