# Volumetría, inventario de productos y concentraciones

Motor de la pestaña 8 (ONE-TRAX: *Volume Accounting and Product Inventory*).

| | |
|---|---|
| Motor | `operaciones/volumetria.py`, función `simular()` (sin Django) |
| Adaptador | `views_inventario.py`: `_linea_de_tiempo`, `_simular_pozo`, `_validar`, `_estado_volumetria` |
| Modelos | `VolumenFosaDia`, `VolumenHoyoDia`, `TransaccionVolumen`, `TransaccionVolumenProducto`, `InventarioProductoDia`, `TicketProducto`, `TicketProductoDetalle` |

## Idea central

**No se guardan volúmenes calculados, inventarios, costos ni concentraciones.** Se guarda solo lo que el ingeniero captura:

- el tipo de cada fosa en el día y su volumen **real medido**,
- el volumen del hoyo que no es fluido del sistema,
- los **movimientos** (químicos, lodo entero, transferencias, devoluciones, pérdidas),
- los **tickets** de productos,
- las columnas manuales del inventario (usado en otro módulo, ajuste, en pedido, no imprimir).

Para ver cualquier día, `simular()` repite **día por día y en orden** toda la historia del pozo. Así, corregir un dato de un día viejo actualiza solo todos los días siguientes.

---

## Entrada del motor

`_linea_de_tiempo(pozo, objetivo)` arma una lista de días ordenada por fecha, hasta el reporte objetivo:

```python
{
  'id', 'fecha_texto',
  'fosas': [{'numero', 'grupo', 'real'}],       # grupo según el tipo del día; real = medido o None
  'hoyo_fluido': float,                          # fluido del sistema activo dentro del hoyo
  'transacciones': [...],                        # ordenadas por secuencia
  'tickets': [{'sentido', 'detalles': [{'producto', 'real', 'ticket'}]}],
  'manual': {producto_id: {'otro', 'ajuste', 'precio', 'categoria'}},
}
```

- **Fosas del día**: las guardadas ese día; si no hay, las del pozo con el **tipo del día anterior** (el tipo casi nunca cambia). Las fosas guardadas que ya no están en la lista del pozo se conservan para no romper la historia.
- **Fluido en el hoyo**: volumen anular + sarta + bajo la mecha de la pestaña 4, menos lo que el ingeniero marcó como "no fluido" (cada parte con mínimo 0).
- **Productos**: datos de la lista de productos activos del pozo (primera fila de cada producto). Si un producto ya no está activo pero se usó antes, se completa desde el catálogo maestro.
- **Servicios**: productos activos con unidad vacía.

## Grupos de fosas

| Tipo de fosa (código) | Grupo |
|---|---|
| 1 Activa | Sistema activo |
| 2 Reserva | Reserva |
| 3 Premix | Premezcla |
| 4, 5, 6 y cualquier tipo agregado | Otras |
| 0 Vacía o sin tipo | Ninguno: no puede mover fluido |

El **sistema activo incluye el hoyo**:

- Inicial del sistema activo = fosas activas + fluido en el hoyo del día anterior.
- Real del sistema activo = fosas activas medidas + fluido en el hoyo de hoy.

Por eso el calculado de una fosa activa y su real **no tienen que coincidir** (nota especial del manual, pág. 146).

---

## Reglas día por día

### 1. Volumen inicial

Inicial de cada fosa = final del día anterior: el **real** si se midió; si no, el **calculado**.

### 2. Tickets

Suman (ENTRADA) o restan (SALIDA) al inventario del producto usando la cantidad **real**; la "según ticket" se informa aparte.

### 3. Movimientos (por número de secuencia)

| Tipo | Volumen | Inventario y costo |
|---|---|---|
| Químicos | + fluido base + agua + volumen de químicos | Cada producto: usado en fluidos += cantidad; costo = cantidad × precio |
| Lodo entero | + volumen | Producto de lodo entero: usado += unidades consumidas; costo |
| Transferencia | − origen, + destino | — |
| Devolución | − volumen | — |
| Pérdida | − volumen, sumado a la categoría de pérdida y al grupo | — |

**Volumen de los químicos**: solo aportan volumen los productos medidos en **peso**:

```
masa (lb) = cantidad × tamaño de unidad × factor
     factor: LB 1 · KG 2.20462 · TN/TON/ST 2000 · MT/TM/T 2204.62
volumen (bbl) = masa / (gravedad específica × 350)
```

Los productos en unidades de volumen (bbl, gal, l) no suman volumen aquí: su volumen se registra como fluido base, agua o lodo entero (en el manual, el DF-1 Base Oil aparece como producto y como fluido base).

**Consumo de lodo entero**:

```
unidades = volumen (bbl) / (tamaño × factor a bbl)      factor: BL/BBL 1 · GA/GAL 1/42 · LT/L 1/158.987
```

Si la unidad no es de volumen, las unidades consumidas = barriles.

Aviso (no bloquea): una fosa que no es del sistema activo queda con volumen calculado negativo.

### 4. Volúmenes finales y balance

```
calculado de la fosa = inicial + movimientos
calculado del grupo  = inicial del grupo + movimientos de sus fosas
real del grupo       = Σ reales de sus fosas (+ hoyo si es el activo)     (vacío si falta medir alguna)
no contabilizado     = real − calculado
```

Al cierre de cada día el no contabilizado debería ser cero; si no lo es, queda a la vista. El volumen real **no se ajusta** para cuadrar.

Flujos por grupo que se informan: fluido base, agua, químicos, recibido (lodo entero), devuelto, pérdida, entra y sale por transferencias entre grupos.

### 5. Inventario de productos

```
final = inicial + recibido − devuelto − usado en fluidos − usado en otro módulo + ajuste
```

- "Usado en otro módulo" también genera costo (con el precio guardado ese día).
- **Servicios**: final = inicial (siempre 0); solo generan costo.
- **Inventario unificado (25/09/2026):** las vistas llaman a `simular(..., validar_stock=False)`, así que este inventario "del pozo" ya no rechaza negativos ni define la existencia. El motor sigue calculando usos, costos, acumulados y concentraciones. La existencia real es `Producto.cantidad`:
  - `views_inventario._mover_stock()` la descuenta al registrar químicos, lodo entero, usado en otro módulo o ajuste, y rechaza si no alcanza: "Inventario de BARITA (AOS-1010): hay 12 SACOS 100 LBS y se necesitan 40".
  - Deshacer un movimiento o borrar el reporte (`devolver_stock_reporte`) la devuelve.
  - Los campos `stock_aplicado` (`TransaccionVolumenProducto`, `InventarioProductoDia`) y `lodo_stock_aplicado` (`TransaccionVolumen`) guardan cuánto se descontó.
  - En pantalla, inicial y final se reemplazan por la existencia general llevada a la fecha del reporte.
  - Los tickets solo se muestran como recibido/devuelto.

Acumulados por producto: usado, recibido y devuelto del pozo; costo acumulado.

### 6. Costos por categoría

Según el código de costo diario del producto activo: 1 Químicos, 2 Ingeniero de fluidos, 3 Ingeniero de control de sólidos, 4 Ingeniero IFE. Diario y acumulado.

### 7. Paso al día siguiente

El final de cada fosa es su real (si se midió) o su calculado. La masa de producto disuelta se **escala al volumen real medido**: una pérdida no contabilizada también se lleva producto.

---

## Concentraciones

Para cada **compartimento** (el sistema activo, que se mezcla con el hoyo, y cada una de las demás fosas por separado) se lleva la **masa** de cada producto:

| Evento | Masa |
|---|---|
| Químicos (producto que "calcula concentración" y se mide en peso) | + masa en lb al compartimento de la fosa |
| Lodo entero | + concentración (lb/bbl) × volumen |
| Transferencia entre compartimentos | Pasa la fracción volumen / volumen del compartimento de origen |
| Devolución o pérdida | Sale la fracción volumen / volumen del compartimento |
| Cambio de tipo de una fosa (entra o sale del sistema activo) | Se lleva su parte de masa al nuevo compartimento |
| Cierre del día | Se escala al volumen real medido |

```
concentración (lb/bbl) = masa / volumen del compartimento
```

Se informa al **inicio** y al **cierre** del día. Se omiten los productos con concentración casi cero.

---

## Validación de toda la línea de tiempo

Cada guardado de la pestaña 8 (datos medidos, movimiento, deshacer, ticket, borrar ticket) se ejecuta dentro de una transacción de base de datos:

1. guarda,
2. `_validar()` simula **todo el pozo hasta el último reporte**,
3. si algún día falla (inventario negativo, fosa inexistente, fosa sin tipo), se deshace el guardado y se muestra el mensaje.

Al consultar (GET), si la línea de tiempo tiene un error, la respuesta trae `error_linea_tiempo` con el mensaje y los datos calculados vacíos, para que el ingeniero sepa qué corregir.

## Deshacer

Solo el **último movimiento del pozo** (mayor secuencia) y solo desde su reporte:

> El último movimiento del pozo (#27) es del reporte del 22/09/2026. Deshazlo desde ese reporte.

---

## Constantes

| Constante | Valor | Uso |
|---|---|---|
| `LB_POR_BBL_AGUA` | 350 | Peso de un barril de agua en lb |
| `EPS` | 0.005 | Tolerancia para negativos y volúmenes nulos |
| `GRUPO_POR_TIPO` | {1: activo, 2: reserva, 3: premezcla} | |
| `CATEGORIAS_COSTO` | 1-4 | Ver arriba |
