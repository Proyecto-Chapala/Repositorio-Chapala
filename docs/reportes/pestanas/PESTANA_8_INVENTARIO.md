# Pestaña 8 — Inventario / Hidráulica / Concentraciones

La pestaña más grande. Se divide en secciones:

| Grupo | Sección | Documento de detalle |
|---|---|---|
| Captura | **1 Volumetría e inventario de productos** | [../VOLUMETRIA.md](../VOLUMETRIA.md) |
| Consultas | **2 Concentración de productos** | [../VOLUMETRIA.md](../VOLUMETRIA.md#concentraciones) |
| Consultas | **3 Hidráulica** | [../HIDRAULICA_API13D.md](../HIDRAULICA_API13D.md) |
| Consultas | **4 Evaluación de benchmark** | [../MODULOS_OPCIONALES.md](../MODULOS_OPCIONALES.md#evaluación-de-benchmark) |
| Consultas | Retención en recortes (enlace) | [../MODULOS_OPCIONALES.md](../MODULOS_OPCIONALES.md) |
| Configuración | ⚙ Pérdidas del reporte | Abajo |

| | |
|---|---|
| Motores | `volumetria.py`, `hidraulica.py` |
| Vistas | `views_inventario.py`, `views_hidraulica.py`, `views_opcionales.api_benchmark_evaluacion` |
| Modelos | `models_inventario.py` |
| JS / CSS | `reporte_inventario.js` / `.css`, `reporte_hidraulica.js` / `.css`, `reporte_opcionales.js` / `.css` |

---

## 1. Volumetría e inventario de productos

Tres vistas: **Volúmenes de fosas**, **Balance de volumen** e **Inventario de productos**, y cuatro acciones de movimiento: **Agregar químicos**, **Agregar lodo entero**, **Transferencia / pérdida** y **Movimientos del día** (con *Deshacer último*).

### Requisitos previos

- **Fosas** del pozo (Información de Fosas) con capacidad.
- **Productos activos** del pozo con unidad, tamaño, precio, gravedad y código de costo diario.
- Existencia en la pantalla **Inventario** (es el único inventario, compartido por todos los pozos).

### Volúmenes de fosas

Por cada fosa del pozo:

| Columna | Quién la llena |
|---|---|
| Tipo del día (Activa, Reserva, Premix...) | Ingeniero. Si no se toca, se hereda el tipo del día anterior |
| Inicial | Calculado: el real medido ayer (o el calculado si ayer no se midió) |
| Calculado | Calculado: inicial + movimientos del día |
| **Real** (volumen final medido) | Ingeniero |
| Peso (lb/gal) y temperatura (°F) | Ingeniero |

Una fosa de tipo **Vacía** (código 0) o sin tipo no puede recibir ni entregar fluido.

**Volumen del hoyo** (de la pestaña 4): anular, sarta y bajo la mecha. El ingeniero indica cuánto de ese volumen **no** es fluido del sistema activo (por ejemplo, cemento o píldora); el resto se suma al sistema activo.

### Balance de volumen

Por grupo: **Sistema activo** (fosas activas + hoyo), **Reserva**, **Premezcla** y **Otras fosas**. Para cada uno: inicial, entradas y salidas por concepto, calculado, real y **no contabilizado** (real − calculado).

El manual es claro: el volumen real **no se cambia** para cuadrar el balance. La diferencia queda a la vista como "no contabilizado".

### Inventario de productos

Por producto activo del pozo. La existencia es la del **Inventario general** (`Producto.cantidad`), una sola para todos los pozos:

```
final del día = existencia actual + lo consumido después de ese día (todos los pozos)
inicial       = final + lo consumido ese día (todos los pozos)
```

| Columna | Origen |
|---|---|
| Inicial / final | Inventario general llevado a la fecha del reporte (ver arriba) |
| Recibido / devuelto | Tickets de productos. **Solo registro**: no cambian la existencia |
| Usado en fluidos | Movimientos "Agregar químicos" y consumo de "lodo entero" |
| Usado en otro módulo | A mano (por ejemplo, días de ingeniero cargados en otro módulo) |
| Ajuste | A mano, positivo o negativo |
| En pedido | A mano, informativo |
| No imprimir | A mano; se hereda del último día en que se marcó |
| Costo diario y acumulado | Cantidad usada × precio |
| Peso (lb) | Para productos medidos en peso |

Usado en fluidos, usado en otro módulo y el ajuste **descuentan la existencia del Inventario general al guardarse** (el ajuste positivo suma). Si no alcanza, el guardado se rechaza: "Inventario de BARITA (AOS-1010): hay 12 SACOS 100 LBS y se necesitan 40". Deshacer un movimiento o borrar el reporte devuelve lo descontado.

Los productos **servicio** (sin unidad en la lista activa) solo generan costo: su inicial y final siempre son 0.

Detalle en [../../inventario/FLUJOS.md](../../inventario/FLUJOS.md#relación-con-el-inventario-del-pozo-pestaña-8).

### Movimientos

| Movimiento | Datos | Efecto |
|---|---|---|
| **Agregar químicos** | Fosa; fluido base (bbl); agua (bbl); productos y cantidades | Suma volumen a la fosa (fluido base + agua + volumen de los químicos medidos en peso); descuenta inventario; genera costo |
| **Agregar lodo entero** | Fosa; volumen; peso; producto "lodo entero" (de los activos); origen; concentraciones del lodo (lb/bbl por producto) | Suma volumen; descuenta del inventario las unidades del producto de lodo entero; las concentraciones solo sirven para el cálculo de concentraciones |
| **Transferencia** | Fosa origen, fosa destino, volumen | Mueve volumen (y producto disuelto) entre fosas |
| **Devolución** | Fosa, volumen, destino (texto obligatorio: almacén u otro taladro) | Saca volumen del pozo |
| **Pérdida y descarte** | Fosa, volumen, tipo de pérdida | Saca volumen y lo suma a la categoría de pérdida |

Cada movimiento lleva un número de **secuencia** del pozo. Solo el último del pozo se puede deshacer, y desde su reporte. Cada guardado valida toda la línea de tiempo del pozo.

### Tickets de productos

**Solo registro** (no mueven la existencia). Igual que los de mallas y con los **mismos tipos** de ticket (sentido ENTRADA o SALIDA): número, pedido por, recibido por, almacén y, por producto, cantidad según ticket y real. La pantalla muestra también el último número de ticket usado de cada tipo.

### Pérdidas

Tabla por categoría de pérdida: volumen perdido por grupo, subtotal, y el **lodo descargado por los equipos** calculado en la pestaña 6 (como referencia). Totales de superficie, subsuelo y general.

### Costos

Por categoría: 1 Químicos, 2 Ingeniero de fluidos, 3 Ingeniero de control de sólidos, 4 Ingeniero IFE. Diario y acumulado.

---

## 2. Concentración de productos

Solo consulta. Concentración (lb/bbl) de cada producto al inicio y al cierre del día, en el **sistema activo** (fosas activas + hoyo) y en cada una de las demás fosas. Detalle en [../VOLUMETRIA.md](../VOLUMETRIA.md#concentraciones).

## 3. Hidráulica

Solo consulta. Se elige **4ª edición** (ley de potencia) o **5ª edición** (Herschel-Bulkley); por defecto la que diga *Configuración General → usar API 5ª edición*. Detalle en [../HIDRAULICA_API13D.md](../HIDRAULICA_API13D.md).

Si falta algo, la pantalla dice qué y en qué pestaña: caudal y boquillas (2), chequeo con reología y peso (3), sarta (4).

## 4. Evaluación de benchmark

Solo consulta. Compara los objetivos del Benchmark Setup del pozo con los chequeos de lodo. Ver [../MODULOS_OPCIONALES.md](../MODULOS_OPCIONALES.md#evaluación-de-benchmark).

---

## Pérdidas del reporte (configuración)

El pozo puede tener hasta 20 categorías de pérdida, pero el reporte diario imprime **máximo 10**. Aquí se eligen cuáles y en qué orden. La selección es **por pozo** (decisión del usuario), se guarda por código de categoría y, si no hay selección, se usan las 10 primeras por código.

Una categoría con movimientos en el día aparece en la tabla de pérdidas aunque no esté en la selección.
