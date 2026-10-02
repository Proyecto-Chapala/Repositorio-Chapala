# 15 — Inventario de almacén (productos químicos)

Pantalla: **Inventario** en la barra lateral, ruta `/`. Archivos: `views.py` (`index`, `api_producto_*`), `models.py` (`Producto`), `templates/operaciones/index.html`, `inventario/_formulario_producto.html`, `inventario/_tabla_productos.html` e `inventario.js/.css`.

## Para qué sirve

Es el **catálogo maestro de productos** del sistema y, además, el registro del **stock del almacén** de AOS.

- Como **catálogo**: en *Productos activos* de cada pozo se eligen productos de esta lista.
- Como **existencia única**: `Producto.cantidad` es la existencia que usan los reportes diarios de **todos los pozos** (inventario unificado desde el 25-sep-2026; ver abajo).

## Pantalla

- **Filtros**: Todos, Sólidos o Líquidos, con contadores. Búsqueda por código, descripción o unidad.
- **Listado de existencias**: código, descripción, categoría, unidad, cantidad, costo y estado. Tiene paginación (Inicio, <, >, Fin). Al hacer clic en una fila se abre el detalle.
- **Detalle de producto** (formulario): código*, descripción*, unidad/presentación*, costo unitario ($)*, libraje (lb)*, cantidad (stock)*, gravedad específica*, categoría* (Sólido o Líquido), estado del stock (automático) y observación.

## Reglas

| Regla | Detalle |
|---|---|
| Código único | Sin distinguir mayúsculas y minúsculas: *"Ya existe un producto registrado con el código '…'."* |
| Cantidad ≥ 0 | *"La cantidad no puede ser negativa."* |
| **Estado automático** | Se recalcula al guardar: **0 a 20 → Bajo**, **21 a 50 → Medio**, **más de 50 → Alto** |
| **Eliminar** | Solo si la **cantidad es 0**: *"No se puede eliminar el producto '…' porque tiene N unidades en stock…"* |

## API

| Método | Ruta | Uso |
|---|---|---|
| GET | `/api/productos/?categoria=SOLIDO\|LIQUIDO&estado=ALTO\|MEDIO\|BAJO&search=texto` | Lista y contadores |
| GET | `/api/productos/<id>/` | Detalle |
| POST | `/api/productos/crear/` | Crear |
| POST/PUT | `/api/productos/<id>/modificar/` | Modificar |
| POST/DELETE | `/api/productos/<id>/eliminar/` | Eliminar (solo con cantidad 0) |

## Relación con la pestaña 8 (inventario unificado)

Desde el **25-sep-2026 hay un solo inventario** (migración `0022_inventario_unificado`).

| Acción en el reporte diario | Efecto en la cantidad de esta pantalla |
|---|---|
| Agregar químicos a un tanque | Resta la cantidad usada |
| Agregar lodo reciclado | Resta las unidades del producto de lodo reciclado consumidas |
| "Usado en otro módulo" | Resta |
| Ajuste (+ / −) | Suma o resta |
| Deshacer el último movimiento | Devuelve lo que ese movimiento había restado |
| Cambiar "usado en otro módulo" o el ajuste de un día | Aplica solo la diferencia |
| Borrar un reporte diario o el pozo completo | Devuelve todo lo que esos reportes habían restado |
| Tickets de entrega o devolución | **Nada**: son solo registro |

Si no alcanza la existencia, el reporte rechaza el movimiento: *"Inventario de BARITA (AOS-1010): hay 12 SACOS 100 LBS y se necesitan 40. Actualiza la existencia en la pantalla Inventario."*

Para usar un producto en el reporte diario de un pozo: (1) existir aquí con su cantidad; (2) estar en **Productos activos** del pozo (precio, **unidad**, tamaño, gravedad y código de costo). Si la **unidad queda vacía** es un **servicio** (días de ingeniero): genera costo pero no descuenta existencia.

Las entradas de mercancía (compras, llegadas de proveedor) se registran aquí, editando la cantidad del producto.

**Datos anteriores al cambio:** la cantidad que había el 25-sep-2026 se tomó como correcta y los consumos ya registrados **no se descontaron otra vez** (quedaron marcados como ya aplicados).

Código: `views_inventario._mover_stock`, `consumo_aplicado_reporte`, `devolver_stock_reporte`.

## Pantalla en laptops (02-oct-2026)

En pantallas bajas o angostas el formulario *Nuevo producto* pasa debajo de la tabla y la página se desplaza; ya no hace falta reducir el zoom del navegador.

## Historia

`RESUMEN_AVANCE.txt` y `seed_data.py` describen una versión anterior (app `mychapala`) que tenía reportes diarios de almacén (`ReporteDiario` con N° REP-2026-XXXX, `RegistroUso`), una pestaña "Uso" con precio variable y una planilla de impresión oficial AOS. **Esos modelos y pantallas ya no existen en el código actual.** Hoy `ReporteDiario` es el reporte de fluidos del pozo. Si AOS necesita de nuevo la planilla de salidas de almacén, habría que reconstruirla.
