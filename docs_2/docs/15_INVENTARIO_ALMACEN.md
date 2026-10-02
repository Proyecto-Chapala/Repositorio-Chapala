# 15 — Inventario de almacén (productos químicos)

Pantalla: **Inventario** en la barra lateral, ruta `/`. Archivos: `views.py` (`index`, `api_producto_*`), `models.py` (`Producto`), `templates/operaciones/index.html`, `inventario/_formulario_producto.html`, `inventario/_tabla_productos.html` e `inventario.js/.css`.

## Para qué sirve

Es el **catálogo maestro de productos** del sistema y, además, el registro del **stock del almacén** de AOS.

- Como **catálogo**: en *Productos activos* de cada pozo se eligen productos de esta lista.
- Como **stock**: `Producto.cantidad` es lo que hay en el almacén. **No está conectado** con el inventario del taladro de la pestaña 8 (ver abajo).

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

## Relación con la pestaña 8 (importante)

```
 ALMACÉN (esta pantalla)                         TALADRO / POZO (pestaña 8)
 Producto.cantidad = 500 sacos                   Inventario del pozo = 0 al empezar
         │                                                 ▲
         │   (no hay conexión automática)                  │ sube SOLO con "Tickets de productos"
         └─────────────────────────────────────────────────┘ de tipo ENTRADA (recepción)
```

- La pestaña 8 **no lee ni descuenta** `Producto.cantidad`.
- Para usar un producto en el reporte diario hay que: (1) tenerlo en **Productos activos** del pozo, con su precio y unidad; (2) registrar en la pestaña 8 un **ticket de recepción** con la cantidad **real** recibida en el taladro.
- Consumir productos en la pestaña 8 **no baja** el stock del almacén.

Si se quiere que ambos inventarios se muevan juntos (que un ticket de recepción descuente el almacén), hay que desarrollarlo. Ver [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md).

## Historia

`RESUMEN_AVANCE.txt` y `seed_data.py` describen una versión anterior (app `mychapala`) que tenía reportes diarios de almacén (`ReporteDiario` con N° REP-2026-XXXX, `RegistroUso`), una pestaña "Uso" con precio variable y una planilla de impresión oficial AOS. **Esos modelos y pantallas ya no existen en el código actual.** Hoy `ReporteDiario` es el reporte de fluidos del pozo. Si AOS necesita de nuevo la planilla de salidas de almacén, habría que reconstruirla.
