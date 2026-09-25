# Manual de usuario — Inventario de productos

Guía para el personal de AOS que registra y consulta los productos químicos del almacén.

## Entrar

1. Encienda el sistema con doble clic en **Iniciar Sistema.bat** (se abre el navegador solo).
2. Si el navegador no se abre, escriba en la barra de direcciones: `http://127.0.0.1:8000/`
3. La primera pantalla es **Inventario de Productos**. También se llega con el botón 📦 **Inventario** de la barra lateral.

> Deje abierta la ventana negra del servidor mientras use el sistema. Si la cierra, el sistema deja de responder.

## La pantalla

```
┌──────────────────────────────────────────────────────────────────────┐
│ Inventario de Productos   [Todos (38)] [Sólidos (30)] [Líquidos (8)] │  🔍 Buscar...
├───────────────────────────────────────┬──────────────────────────────┤
│ Listado de Existencias                │ Detalle de Producto          │
│ Código │ Descripción │ ... │ Estado   │ Código, Descripción,         │
│ ...                                   │ Unidad, Costo, Libraje,      │
│                                       │ Cantidad, Gravedad,          │
│ [Nuevo] [Modificar] [Eliminar]        │ Categoría, Estado,           │
│ [Inicio] [<] [>] [Fin]                │ Observación                  │
│                                       │         [Cancelar] [Guardar] │
└───────────────────────────────────────┴──────────────────────────────┘
```

## Buscar un producto

- Escriba en **Buscar** parte del código, del nombre o de la presentación. La lista se filtra sola.
- Use **Sólidos** o **Líquidos** para ver solo esa categoría. **Todos** quita el filtro.
- Haga clic en una fila para ver el detalle a la derecha.
- Con **Inicio**, **<**, **>** y **Fin** se recorre la lista producto por producto.

## Agregar un producto

1. Pulse **➕ Nuevo**.
2. Llene los campos. Los que tienen * son obligatorios:

| Campo | Qué poner | Ejemplo |
|---|---|---|
| Código * | Código único del producto | `AOS-1002` |
| Descripción * | Nombre completo | `ACETATO DE POTASIO (SACOS DE 25 KG)` |
| Unidad * | Presentación | `SACOS 55 LBS` |
| Costo Unitario ($) * | Precio de una unidad | `45.00` |
| Libraje (LBS) * | Peso de una unidad en libras | `55` |
| Cantidad (Stock) * | Unidades en el almacén | `120` |
| Gravedad Específica * | Densidad relativa al agua | `1.57` |
| Categoría * | Sólido o Líquido | Sólido |
| Observación | Notas (opcional) | |

3. Pulse **💾 Guardar**. Aparece un aviso verde en la esquina si se guardó.

No se puede repetir un código: `AOS-1002` y `aos-1002` cuentan como el mismo.

## Cambiar un producto (por ejemplo, actualizar la existencia)

1. Haga clic en el producto.
2. Pulse **✏️ Modificar**.
3. Cambie lo que necesite y pulse **💾 Guardar**. **Cancelar** descarta los cambios.

## El estado del stock

El sistema pone el estado solo, según la cantidad. No se puede elegir a mano:

| Cantidad | Estado |
|---|---|
| 0 a 20 | 🔴 Stock Bajo |
| 21 a 50 | 🟡 Stock Medio |
| Más de 50 | 🟢 Stock Alto |

## Eliminar un producto

Solo se puede eliminar un producto con **cantidad 0**. Si tiene existencia, el botón **🗑️ Eliminar** aparece desactivado.

1. Modifique la cantidad a 0 y guarde (si corresponde).
2. Seleccione el producto y pulse **🗑️ Eliminar**.
3. Confirme.

Si el producto se está usando en algún pozo, el sistema no dejará borrarlo aunque tenga cantidad 0.

## Preguntas frecuentes

**¿El reporte diario usa esta misma cantidad?**
Sí. Hay un solo inventario. Cuando el ingeniero agrega químicos o lodo en el reporte diario de cualquier pozo, la cantidad de aquí baja; si deshace el movimiento o borra el reporte, vuelve. Ver [FLUJOS.md](FLUJOS.md#relación-con-el-inventario-del-pozo-pestaña-8).

**¿Y los tickets de recepción del reporte diario?**
Son solo registro; no cambian la cantidad. Cuando llega mercancía nueva, súmela aquí con **Modificar**.

**Guardé y no veo el cambio.**
Pulse `Ctrl + F5` para recargar la página sin la memoria del navegador.

**Sale "Error de conexión con el servidor".**
La ventana negra del servidor está cerrada. Vuelva a abrir **Iniciar Sistema.bat**.
