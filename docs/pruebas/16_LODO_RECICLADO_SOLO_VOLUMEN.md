# 16 — Lodo reciclado solo como volumen

**Documento:** [26](../26_REDISENO_INVENTARIO_Y_LODO_RECICLADO.md) · **Migración:** — · **Estado:** sin probar

## Cómo funciona

- Al agregar lodo reciclado a un tanque desde la pestaña 8, ya **no se selecciona un producto de lodo reciclado**.
- El movimiento solo pide: Tanque, Recibido de (origen), Volumen (bbl), Peso del lodo (lb/gal, opcional) y Concentración de productos en el lodo (lb/bbl, opcional).
- Suma volumen al tanque y cuenta como "recibido" en el balance de volumen.
- Las concentraciones cargadas en lb/bbl aportan masa para el cálculo de concentraciones de productos.
- **No consume inventario** de ningún producto y **no genera costo**.

## Pasos para verificar

- [ ] **Modal de agregar lodo.** En la pestaña 8, pulsar **Agregar lodo reciclado** → la ventana ya no muestra el campo "2. Producto de lodo reciclado" ni la lista de selección de producto.
- [ ] **Campos visibles.** La ventana muestra: 1. Tanque, 2. Recibido de, 3. Volumen (bbl) y Peso del lodo (lb/gal), y 4. Concentración de productos en el lodo (lb/bbl).
- [ ] **Registro de lodo.** Seleccionar un tanque activo, origen "Planta", volumen 100 bbl, peso 10,5 lb/gal y registrar → el movimiento se guarda sin errores.
- [ ] **Balance de volumen.** El volumen calculado del tanque aumenta en 100 bbl y la fila *Lodo reciclado recibido* del grupo suma 100 bbl.
- [ ] **Inventario intacto.** En la tabla *Inventario diario de productos*, ningún producto tiene consumo (`Usado fluidos` permanece en 0 o en lo que tenía antes).
- [ ] **Costo cero.** En el *Resumen de costos* de la pestaña 8 y en la pestaña 1, el movimiento de lodo reciclado no genera ningún costo.
- [ ] **Lista de movimientos.** En la ventana de movimientos registrados, el movimiento aparece como "100 bbl de lodo reciclado de 10.5 lb/gal agregados a [Tanque] desde Planta", sin mención entre paréntesis de ningún producto.
- [ ] **Concentraciones.** Si se escribió una concentración (por ejemplo, 15 lb/bbl de Barita), en la tabla de concentraciones la Barita suma esa masa al sistema.

**Notas de la prueba:**
