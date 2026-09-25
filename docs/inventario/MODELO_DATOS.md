# Inventario — Modelo de datos

El inventario tiene **un solo modelo propio**: `Producto` (`operaciones/models.py`, migración `0001_initial`). Es a la vez:

- el inventario del almacén de AOS (pantalla `/`), y
- el **catálogo maestro de productos** ("Master Product List" de ONE-TRAX) del que cada pozo elige sus productos activos.

## `Producto`

| Campo | Tipo | Reglas |
|---|---|---|
| `codigo` | Texto (50), **único** | Obligatorio. Se recorta; la unicidad se valida **sin distinguir mayúsculas** (`AOS-1001` = `aos-1001`) |
| `descripcion` | Texto (255) | Obligatorio |
| `unidad` | Texto (50) | Obligatorio. Presentación: `SACOS 55 LBS`, `TAMBOR 55 GLS`, `TOTE`... |
| `libraje` | Decimal (12,2) | Peso unitario en lb. ≥ 0. Default 0 |
| `gravedad` | Decimal (8,4) | Gravedad específica. > 0. Default 1.0 |
| `costo` | Decimal (14,2) | Costo unitario en $. ≥ 0. Default 0 |
| `cantidad` | Decimal (14,2) | Existencia en almacén. ≥ 0. Default 0 |
| `categoria` | `SOLIDO` / `LIQUIDO` | Default `SOLIDO` |
| `estado` | `ALTO` / `MEDIO` / `BAJO` | **Calculado** al guardar; ver abajo |
| `observacion` | Texto largo, opcional | |
| `created_at`, `updated_at` | Fecha y hora | Automáticos |

Orden por defecto: `codigo`.

### Estado del stock (automático)

`Producto.save()` llama a `calcular_estado_automatico()` **siempre**, así que el estado que envíe el usuario se ignora:

| Cantidad | Estado |
|---|---|
| 0 a 20 | `BAJO` (Stock Bajo) |
| más de 20 y hasta 50 | `MEDIO` (Stock Medio) |
| más de 50 | `ALTO` (Stock Alto) |

La pantalla calcula lo mismo en JavaScript para mostrar el color mientras se escribe.

### `to_dict()`

Formato que devuelve la API: todos los campos anteriores como números, más `categoria_display`, `estado_display` y `puede_eliminar` (`true` solo si `cantidad == 0`).

---

## Relación con los pozos

`Producto` es referenciado por los modelos del reporte diario. Todas estas llaves usan `on_delete=PROTECT`: **un producto no se puede borrar mientras algún pozo lo use.**

| Modelo | Campo | Para qué |
|---|---|---|
| `ProductoActivoPozo` | `producto` | Lista de productos activos de un pozo, con **datos propios del pozo**: abreviatura, tamaño de unidad (`unit_size`), unidad, empaque, precio, gravedad, categoría de costo, si calcula concentración |
| `TransaccionVolumen` | `lodo_producto` | Producto "lodo entero" consumido al agregar lodo a una fosa |
| `TransaccionVolumenProducto` | `producto` | Químicos agregados (o concentraciones del lodo entero) |
| `InventarioProductoDia` | `producto` | Ajustes manuales del inventario del pozo en un día |
| `TicketProductoDetalle` | `producto` | Cantidades de un ticket de entrega o devolución al pozo |

```
Producto (almacén AOS, catálogo maestro)
   │
   ├── ProductoActivoPozo ── Pozo       (qué productos usa el pozo y a qué precio)
   │
   └── Transacciones / Inventario diario ── ReporteDiario
                (descuentan Producto.cantidad; `stock_aplicado` guarda cuánto, para devolverlo)
```

### Qué datos se usan en el pozo

Cuando la pestaña 8 necesita un producto, toma los datos de `ProductoActivoPozo` y solo si faltan recurre al maestro:

| Dato | De dónde sale |
|---|---|
| Precio | `ProductoActivoPozo.precio`; si está vacío, `Producto.costo` |
| Gravedad específica | `ProductoActivoPozo.gravedad_especifica`; si está vacía, `Producto.gravedad` |
| Unidad y tamaño | Solo de `ProductoActivoPozo` (`unidad`, `unit_size`). Si la unidad está vacía el producto se trata como **servicio** (sin existencias) |
| Existencia | **`Producto.cantidad`**: inventario único. Los consumos del reporte la descuentan (ver [FLUJOS.md](FLUJOS.md#relación-con-el-inventario-del-pozo-pestaña-8)) |

Detalle en [FLUJOS.md](FLUJOS.md) y en [../reportes/VOLUMETRIA.md](../reportes/VOLUMETRIA.md).

---

## Modelo antiguo (no instalado)

La primera versión (`_legacy/mychapala/models.py`) tenía además:

- `ReporteDiario` del almacén (código `REP-2026-0001`, departamento, encargado, firmas, observaciones, costo total),
- `RegistroUso` (salidas con precio unitario variable y costo calculado),
- en `Producto`: `stock_inicial`, `activo` y campos acumulados.

Esos modelos **no existen** en `operaciones`. Si se quiere recuperar el reporte de almacén hay que migrarlo; ver [../PENDIENTES_Y_DECISIONES.md](../PENDIENTES_Y_DECISIONES.md).
