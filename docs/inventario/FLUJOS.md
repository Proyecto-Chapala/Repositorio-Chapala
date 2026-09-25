# Inventario — Flujos y reglas

Código: `operaciones/views.py` (funciones `api_producto_*`), `templates/operaciones/index.html` con sus parciales en `templates/operaciones/inventario/`, y `static/operaciones/js/inventario.js`.

## Pantalla

`/` es una vista de dos columnas:

- **Izquierda**: tabla de existencias (Código, Descripción, Categoría, Unidad, Cantidad, Costo, Estado) y botones **Nuevo**, **Modificar**, **Eliminar**, más navegación **Inicio**, **<**, **>**, **Fin**.
- **Derecha**: formulario del producto seleccionado. Arriba muestra el modo: *Solo Lectura*, creando o editando.
- **Barra superior**: filtros **Todos / Sólidos / Líquidos** con contadores y buscador.

La pantalla funciona con tres modos en JavaScript: `VIEW` (consulta), `CREATE` y `EDIT`. Si hay cambios sin guardar y se hace clic en otra fila, pregunta antes de descartarlos.

## Flujos

### Consultar y buscar

1. Al cargar, `inventario.js` llama `GET /api/productos/`.
2. El filtro de categoría envía `?categoria=SOLIDO` o `LIQUIDO`.
3. El buscador envía `?search=texto` y busca en código, descripción y unidad (sin distinguir mayúsculas).
4. Los contadores de la barra (`totales`) siempre cuentan **todos** los productos, no solo los filtrados.

### Crear

1. **Nuevo** habilita el formulario vacío.
2. El navegador valida que código, descripción y unidad no estén vacíos.
3. `POST /api/productos/crear/`. El servidor valida:
   - código obligatorio y no repetido (sin distinguir mayúsculas),
   - descripción y unidad obligatorias,
   - categoría `SOLIDO` o `LIQUIDO`,
   - libraje, costo y cantidad ≥ 0; gravedad > 0.
4. Si todo está bien responde 201 y el producto aparece en la tabla con su estado calculado.

### Modificar

1. Seleccionar fila → **Modificar**.
2. `PUT /api/productos/<id>/modificar/` con los campos. Mismas validaciones que al crear; la unicidad del código excluye al propio producto.
3. El estado se recalcula con la nueva cantidad.

### Eliminar

1. El botón **Eliminar** solo se habilita si la cantidad es 0 (el navegador lo desactiva y el servidor lo vuelve a comprobar).
2. Pide confirmación.
3. `DELETE /api/productos/<id>/eliminar/`.

Restricción adicional: si el producto está en la lista de productos activos de algún pozo, o se usó en algún movimiento, ticket o inventario diario de un pozo, la base de datos **impide** el borrado (`PROTECT`). La API responde con un mensaje que dice en qué pozos está activo.

## Reglas de negocio

| Regla | Dónde |
|---|---|
| Estado automático: 0-20 Bajo, 21-50 Medio, >50 Alto | `Producto.calcular_estado_automatico()` y `inventario.js` |
| Cantidad nunca negativa | `Producto.clean()` y la API |
| Código único sin distinguir mayúsculas | `Producto.clean()` y la API |
| Solo se borra con cantidad 0 | API y botón |

---

## Relación con el inventario del pozo (pestaña 8)

Desde el **25/09/2026 hay un solo inventario**: la cantidad de esta pantalla (`Producto.cantidad`) es la existencia que usa el reporte diario de **todos los pozos**.

| Acción en el reporte diario | Efecto en la cantidad de esta pantalla |
|---|---|
| Agregar químicos a una fosa | Resta la cantidad usada |
| Agregar lodo entero | Resta las unidades del producto de lodo entero consumidas |
| "Usado en otro módulo" | Resta |
| Ajuste (+ / −) | Suma o resta |
| Deshacer el último movimiento | Devuelve lo que ese movimiento había restado |
| Cambiar "usado en otro módulo" o el ajuste de un día | Aplica solo la diferencia |
| Borrar un reporte diario | Devuelve todo lo que ese reporte había restado |
| Tickets de entrega o devolución | **Nada**: son solo registro (quién pidió, quién recibió, diferencias con el papel) |

Si no alcanza la existencia, el reporte rechaza el movimiento con un mensaje como:

> Inventario de BARITA (AOS-1010): hay 12 SACOS 100 LBS y se necesitan 40. Actualiza la existencia en la pantalla Inventario.

Para que un producto se pueda usar en el reporte diario de un pozo:

1. **Existir aquí** con su cantidad.
2. **Estar activo en el pozo**: Pozo → *Productos / Equipos / Mallas Activos* → Productos (precio, **unidad**, tamaño, gravedad y código de costo del pozo).
   - Si la **unidad queda vacía**, es un **servicio** (días de ingeniero): genera costo pero **no descuenta** existencia.

Las entradas de mercancía (compras, llegadas de proveedor) se registran aquí, editando la cantidad del producto.

```
Inventario (/)  Producto.cantidad = 120 sacos
      │
      ├─ Pozo A, 22/09: agregar químicos 12  → 108
      ├─ Pozo B, 23/09: agregar químicos 8   → 100
      └─ Pozo A, deshacer el movimiento de 12 → 112
```

**Datos anteriores al cambio:** por decisión del usuario, la cantidad que había el 25/09/2026 se tomó como correcta y los consumos ya registrados **no se descontaron otra vez**. Se marcaron como "ya aplicados", así que deshacerlos o borrar su reporte sí devuelve lo que consumieron.
