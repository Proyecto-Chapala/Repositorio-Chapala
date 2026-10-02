# 09 — Pestaña 8: Inventario, Hidráulica y Concentraciones

> **Terminología (02-oct-2026):** en pantalla y en el Excel se dice **tanque** donde antes decía *fosa*, y **lodo reciclado** donde decía *lodo entero*. En el código y la base de datos siguen los nombres internos (`Fosa`, `fosa`, `LODO_ENTERO`).

Archivos: `models_inventario.py` (migraciones 0019 y 0020), `volumetria.py` (motor), `views_inventario.py` (API y `resumen_costos`) y `reporte_inventario.js/.css`. La hidráulica tiene su propio documento ([10](10_HIDRAULICA_API13D.md)) y la evaluación de benchmark está en [12](12_MODULOS_OPCIONALES.md). Concentraciones en detalle y casos especiales (side track, piloto): [20](20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md).

Sub-vistas de la pestaña:

1. **Volumetría e inventario de productos** (*Volume Accounting and Product Inventory*)
2. **Concentración de productos** (consulta)
3. **Hidráulica** (consulta)
4. **Evaluación de benchmark** (consulta)
5. ⚙ **Pérdidas del reporte**: qué categorías de pérdida (máx. 10, en orden) imprime el reporte diario. La selección es **por pozo**. Si no se ha elegido, se usan las 10 primeras por código.

> Estado: migraciones 0019-0021 aplicadas por el usuario. Concentraciones ampliadas el 27-sep (cantidad agregada, kg/m³, hoja de Excel).

---

## 1. Conceptos

### Grupos de fosas

Cada fosa, cada día, tiene un **tipo** (de *Información de Fosas → Tipos de fosa*). El tipo define el grupo del balance:

| Código de tipo | Grupo |
|---|---|
| 0 (Vacía) o sin tipo | ninguno (no se le puede mover fluido) |
| 1 Activa | **ACTIVO** |
| 2 Reserva | **RESERVA** |
| 3 Premix | **PREMEZCLA** |
| 4 o más (Espaciador, Píldora, Rompedor, otros) | **OTRAS** |

El tipo del día se guarda en `VolumenFosaDia`. Si un día no se guardó, se toma el del día anterior, porque el tipo casi nunca cambia.

### El hoyo es parte del sistema activo

- **Inicial del activo** = fosas activas al cierre de ayer + **fluido en el hoyo de ayer**.
- **Real del activo** = fosas activas medidas hoy + **fluido en el hoyo hoy**.
- **Fluido en el hoyo** = volumen del hoyo de la pestaña 4 **menos** el "volumen que no es fluido" (`VolumenHoyoDia`: anular, sarta y bajo mecha, por ejemplo cemento o un tapón). Es el campo que se usa el día del abandono en un **side track**.

Por eso **el calculado de una fosa activa y su real no tienen por qué coincidir** (nota especial del manual, pág. 146).

### Volumen inicial, calculado y real

Para cada fosa:
```
inicial  = real medido el día anterior  (o, si no se midió, el calculado del día anterior)
calculado = inicial + químicos + fluido base + agua + lodo entero ± transferencias − devoluciones − pérdidas
real     = lo que el ingeniero MIDE al cierre (se escribe a mano)
```
**No contabilizado = real − calculado**, por grupo (activo, reserva, premezcla). Al cierre del día debe ser **cero**. El manual insiste en que el volumen real **no se ajusta** para cuadrar: la diferencia se explica con pérdidas o movimientos.

## 2. Movimientos (`TransaccionVolumen`)

Se registran al instante, cada uno con `secuencia` por pozo. **Solo se puede deshacer el último del pozo**, desde su reporte.

| Tipo | Datos | Efecto |
|---|---|---|
| **Agregar químicos** (`QUIMICOS`) | Fosa · cantidades de productos activos · fluido base (bbl) · agua (bbl) | Suma volumen = fluido base + agua + **volumen de químicos**. Descuenta los productos del inventario. Genera costo. Suma masa para concentraciones |
| **Agregar lodo reciclado** (`LODO_ENTERO`; antes "lodo entero") | Fosa · volumen · peso · **producto "lodo reciclado"** (de los activos) · origen · concentraciones del lodo (lb/bbl) | Suma volumen. Consume unidades del producto de lodo reciclado (`volumen / (tamaño × factor de volumen)`) y genera su costo. Las concentraciones solo sirven para calcular concentraciones |
| **Transferencia** (`TRANSFERENCIA`) | Fosa origen · fosa destino · volumen | Mueve volumen (y la masa de productos proporcional). Origen y destino no pueden ser la misma fosa |
| **Devolución** (`DEVOLUCION`) | Fosa · volumen · a dónde (texto obligatorio) | Resta volumen |
| **Pérdida** (`PERDIDA`) | Fosa · volumen · **tipo de pérdida** (categoría del pozo) | Resta volumen y lo suma al total de esa categoría |

Reglas generales: la fosa debe estar en la lista del pozo y tener un tipo distinto de "Vacía"; volúmenes entre 0,01 y 100.000 bbl; solo productos activos del pozo. Si una fosa **no activa** queda con calculado negativo, se muestra un **aviso**, pero el movimiento no se rechaza.

### Volumen de químicos

Solo los productos medidos en **peso** aportan volumen:
```
masa (lb) = cantidad × tamaño de la unidad × factor   (LB=1 · KG=2,20462 · TN/TON/ST=2000 · MT/TM/T=2204,62)
volumen (bbl) = masa / (gravedad específica × 350)
```
Los productos en volumen (BBL, GAL, L) **no** se suman como volumen químico: su volumen se registra como fluido base/agua o como lodo reciclado. En el reporte de concentraciones este volumen aparece como **"Aumento de volumen por material"** (ONE-TRAX: *Incr Vol – Matl Den*).

## 3. Inventario de productos del pozo

```
final = inicial + recibido − devuelto − usado en fluidos − usado en otro módulo ± ajuste
```

| Columna | Origen |
|---|---|
| Inicial | Existencia del inventario general llevada a la fecha (ver recuadro) |
| Recibido / devuelto | **Tickets de productos**: solo registro (cantidad *real* y *según ticket* para comparar) |
| Usado en fluidos | Movimientos *Agregar químicos* y *Lodo entero* |
| Usado en otro módulo | A mano (ej. días de ingeniero, personal de servicio). Genera costo |
| Ajuste | A mano (+/−) |
| En pedido · No imprimir | A mano, informativos |

- **Si la existencia no alcanza, se rechaza** el movimiento (ver recuadro). El chequeo se hace contra el inventario general, que comparten todos los pozos.
- **Servicios**: los productos activos con **unidad vacía** son servicios. Solo generan costo y no llevan existencias (inicial y final siempre 0).
- Los productos usados en el pasado que ya no están activos siguen apareciendo, marcados como inactivos.

> ### Inventario unificado (desde el 25-sep-2026)
> La existencia de cada producto es **una sola**: `Producto.cantidad`, la de la pantalla *Inventario* (almacén). La pestaña 8 la muestra **llevada a la fecha del reporte**: final del día = existencia actual + lo consumido en días posteriores (en **todos** los pozos); inicial = final + lo consumido ese día.
> - *Agregar químicos*, *lodo reciclado*, *usado en otro módulo* y *ajuste* **descuentan** la existencia al guardarse; deshacer el movimiento o borrar el reporte la **devuelve** (campos `stock_aplicado`).
> - Si no alcanza, se rechaza: *"Inventario de BARITA (AOS-1010): hay 12 SACOS 100 LBS y se necesitan 40. Actualiza la existencia en la pantalla Inventario."*
> - Los **tickets de productos** son **solo registro** (quién pidió, quién recibió, diferencias con el papel); no mueven la existencia.
> - Las entradas de mercancía se cargan en la pantalla *Inventario*, editando la cantidad del producto.
> - Código: `views_inventario._mover_stock`, `devolver_stock_reporte`, `_consumo_aplicado_por_fecha`; migración `0022_inventario_unificado` (del compañero *xtal*). Ver [15](15_INVENTARIO_ALMACEN.md).

### Tickets de productos (`TicketProducto`)

Son **solo registro** (no mueven la existencia). Mismo esquema que los de mallas: tipo (catálogo compartido con mallas: se usa el **sentido** ENTRADA/SALIDA), número, pedido por, recibido por, almacén del pozo y, por producto, cantidad según ticket y cantidad real. La pantalla muestra el último número usado de cada tipo y resalta los tickets con diferencias entre ticket y real.

## 4. Lo que se guarda a mano (`api_volumetria_guardar`)

- **Fosas del día**: tipo y **volumen real**, peso y temperatura (`VolumenFosaDia`, por **número** de fosa + copia de descripción y capacidad).
- **Hoyo**: volumen que no es fluido en anular, sarta y bajo mecha (`VolumenHoyoDia`).
- **Inventario**: usado en otro módulo, ajuste, en pedido, no imprimir, precio y categoría de costo (`InventarioProductoDia`).

Todo se valida contra la línea de tiempo completa y se revierte si algo no cuadra.

## 5. Pérdidas

La tabla de pérdidas muestra, por categoría, el volumen perdido por grupo (activo, reserva…) y la columna **"Descargado por equipos"**: el lodo perdido en los sólidos calculado en la **pestaña 6** para los equipos que tienen asignada esa categoría. Esa columna es de **referencia**: no se registra sola como pérdida.

## 6. Concentración de productos

Solo para los productos marcados *Calcular concentración*. Se lleva la **masa (lb)** de cada producto por **compartimento**:
- el **sistema activo** (todas las fosas activas + el hoyo, que se mezclan),
- cada una de las demás fosas por separado.

Concentración (lb/bbl) = masa / volumen del compartimento, al inicio y al cierre del día (1 lb/bbl = 2,85301 kg/m³).

- **Agua o fluido base** diluyen (misma masa, más volumen).
- **Productos** concentran (más masa; el volumen sube por el material).
- **Lodo entero y transferencias** mezclan: mueven masa proporcional al volumen.
- **Pérdidas y devoluciones** se llevan masa proporcional: la concentración no cambia.
- Al pasar al día siguiente, la masa se ajusta al volumen **real** medido (una pérdida no contabilizada también se lleva producto). Si una fosa cambia de grupo (por ejemplo, de reserva a activa), su masa pasa al compartimento nuevo.

Pantalla: selector de compartimento, unidad lb/bbl o kg/m³, volúmenes del día (inicial, final, cambio, fluido base, agua, aumento por material, lodo entero) y por producto: tamaño, **cantidad agregada**, inicial, cambio, final y total. Excel: hoja **Concentraciones** ([14](14_REPORTE_EXCEL.md)). Ejemplos verificados: [20](20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md).

## 7. Costos

Cada producto tiene una **categoría de costo** (código de costo diario del producto activo, editable por día):

| Código | Categoría | Columna del reporte |
|---|---|---|
| 1 | Químicos | Químicos / Personal DF |
| 2 | Ingeniero de fluidos | Químicos / Personal DF |
| 3 | Ingeniero de control de sólidos | Ingeniero IFE / Control de sólidos |
| 4 | Ingeniero IFE | Ingeniero IFE / Control de sólidos |

*(Pendiente confirmar con AOS los códigos 1-4.)* Resumen completo de costos en [13](13_COSTOS.md).

## 8. Modelos

| Modelo | Qué guarda |
|---|---|
| `PerdidaReportePozo` | por pozo · código de pérdida + orden (máx. 10) |
| `VolumenFosaDia` | por reporte y **n° de fosa** · tipo, real, peso, temperatura |
| `VolumenHoyoDia` | por reporte · volumen que no es fluido |
| `TransaccionVolumen` | movimiento · secuencia por pozo · fosas por número + copia de texto · datos según tipo |
| `TransaccionVolumenProducto` | producto del movimiento · cantidad o concentración · **copia** de unidad, tamaño, gravedad, precio y categoría del momento |
| `InventarioProductoDia` | columnas manuales del inventario |
| `TicketProducto` / `TicketProductoDetalle` | tickets de productos |

Lo **calculado no se guarda**: volúmenes, balance, inventario, costos y concentraciones salen del motor en cada consulta.
