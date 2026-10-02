# 07 — Pestaña 6: Control de sólidos

Archivos: `models_control_solidos.py` (migraciones 0017 y 0018), `control_solidos.py` (motor), `views_control_solidos.py` (API) y `reporte_control_solidos.js/.css`.

La pestaña tiene una **sub-navegación**:

| Vista | Qué hace |
|---|---|
| **Inventario de mallas** | Existencias nuevas/usadas por malla, costo diario y acumulado, y **tickets** de entrega y devolución |
| **Transacciones de mallas** | Instalar, retirar y desechar mallas en las posiciones de cada equipo |
| **Detalle y uso de equipos** | Rendimiento, renta y paradas del día de cada equipo activo |
| **Opcionales** | Análisis de sólidos por equipo, Retención en recortes, Observaciones IFE (ver [12](12_MODULOS_OPCIONALES.md)). El botón *Pruebas SUS* está deshabilitado porque el manual no trae información |
| Indicadores API RP 13C | Sólidos perforados promedio, desempeño del sistema de remoción (SP), lodo agregado / volumen de hoyo. **En standby** hasta tener las fórmulas |

> A diferencia del resto del reporte, **aquí no hay botón "Guardar" para mallas**: cada ticket y cada transacción se registra al momento, el servidor valida toda la línea de tiempo y devuelve el resumen completo. El bloque de uso de equipos sí tiene su botón de guardar.

---

## 1. Inventario de mallas

### Qué es "stock"

- **Nuevas**: mallas sin usar en el almacén del taladro. **Entran** por tickets de entrada y **salen** al instalarlas o por tickets de salida.
- **Usadas**: mallas que se retiraron de un equipo y se guardaron. **Entran** con la acción *Pasar al almacén* o por ticket y **salen** al reinstalarlas, al desecharlas o por ticket.
- **En equipos**: cuántas están instaladas ahora.

Ninguno de estos saldos se guarda: el motor `control_solidos.simular()` los obtiene **repitiendo** los tickets y transacciones de todos los reportes del pozo en orden de fecha. Dentro de un mismo día, primero se aplican los tickets (lo recibido se puede usar ese mismo día) y luego las transacciones por su número de secuencia.

### Costo

**Una malla nueva genera costo al instalarla**, no al recibirla. El costo es el **precio neto** de la lista de mallas activas: `precio × (1 − descuento%)`, redondeado a centavos. Queda **congelado** en la transacción (`precio_unitario`): cambiar después el precio del pozo no altera los días ya registrados. Instalar una malla usada no cuesta. Así funciona ONE-TRAX según el manual: el costo acumulado es múltiplo del precio de la malla.

### Tickets (entrega y devolución)

`TicketMalla` + `TicketMallaDetalle`:

| Campo | Nota |
|---|---|
| Tipo de ticket | Catálogo **editable por pozo**. Trae 4 ejemplos: Recepción desde almacén (ENTRADA), Devolución a almacén (SALIDA), Recepción desde otro pozo (ENTRADA), Envío a otro pozo (SALIDA). Para el cálculo solo importa el **sentido** |
| N° de ticket, pedido por, recibido por | Texto |
| Almacén | Debe existir en los **códigos de almacén** del pozo (Configuración General). Se guarda código + nombre |
| Detalle por malla | **Nuevas** y **usadas**, "según ticket" y "real". **El inventario usa siempre lo real** |

Reglas: solo mallas de la lista de mallas activas, sin mallas repetidas y con al menos una cantidad. Un tipo de ticket que ya se usó no se puede eliminar. El mismo catálogo de tipos lo usan los **tickets de productos** de la pestaña 8.

## 2. Transacciones de mallas

Solo aparecen los equipos activos cuyo modelo tiene **posiciones de malla > 0** (máx. 12).

| Acción (`accion`) | Efecto | Validación |
|---|---|---|
| `INSTALAR_NUEVA` | Nuevas −1, ocupa la posición, **suma costo** | Posición libre y stock de nuevas > 0 |
| `INSTALAR_USADA` | Usadas −1, ocupa la posición | Posición libre y stock de usadas > 0 |
| `A_ALMACEN` | Libera la posición, usadas +1 | La posición debe tener esa malla |
| `DESECHAR_EQUIPO` | Libera la posición; la malla se pierde | La posición debe tener esa malla |
| `DESECHAR_ALMACEN` | Usadas −1 | Stock de usadas > 0 (puede ser una malla que ya no está activa) |

Al retirar, el usuario no elige la malla: el servidor toma **la que está en esa posición ese día**.

**Deshacer**: solo la **última transacción del pozo** (la de mayor `secuencia`) y solo desde el reporte al que pertenece.

### Validación de toda la línea de tiempo

Cada escritura se hace dentro de `transaction.atomic()`: se guarda, se simula **todo** el pozo y, si cualquier día falla, se revierte. Por eso un cambio en un día viejo que deja sin stock a un día posterior **se rechaza**. Mensajes típicos:

- *"El 12/09/2026 (transacción #14): no hay mallas nuevas de 180 Mesh en stock. Registra primero el ticket de recepción."*
- *"… la posición 2 del equipo ZAR-01 ya tiene 140 Mesh. Retírala antes de instalar otra."*
- *"El … : el ticket devuelve 5 mallas nuevas de … pero solo hay 3 en stock."*

Si hay datos viejos inconsistentes (por ejemplo, tras borrar un reporte), la pantalla muestra el aviso `error_linea_tiempo` en vez de romperse.

Si se reducen las posiciones de un equipo en el catálogo maestro y quedan mallas en posiciones que ya no existen, se listan como *fuera de rango* para poder retirarlas.

## 3. Detalle y uso de equipos (`UsoEquipoDia`)

Una fila por **equipo activo** (identificado por su **número de serie**). Si el equipo no tiene datos ese día, se proponen los del último día anterior.

| Campo | Uso |
|---|---|
| Horas | Horas de operación |
| **MOC** (*mud on cuttings*) | Relación lodo/recortes |
| % de recortes | Zarandas, limpiador de lodo, secador |
| Caudal de entrada (gpm), densidades de entrada, salida y descarte | Centrífuga |
| Tipo de pérdida | Categoría de pérdida del pozo. Se sugiere según el tipo: Zaranda → 1, Secador → 2, Centrífuga → 3, Limpiador → 12. **Alimenta las pérdidas de la volumetría (pestaña 8)** |
| Cantidad usada · **Código de cobro** | `COMPLETO` (tarifa de renta), `STANDBY` (tarifa standby), `SIN_COBRO` |
| ¿Es de fluidos? | Marca |
| Horas de parada · observaciones | |
| Propiedades adicionales | Las configuradas en *Configuración de Propiedades de Equipo* para su tipo (ángulo de canasta, fuerza G, velocidad del tazón…). Se guardan por descripción |

### Cálculo del rendimiento (`calcular_rendimiento`)

Volumen de hoyo perforado en el día: `V_hoyo = D² / 1029.4 × avance`, donde D es el diámetro del hoyo en pulgadas y el avance es la profundidad de hoy menos la del reporte anterior, en ft.

**Zaranda, limpiador de lodo, secador de recortes** (por recortes):
```
recortes   = V_hoyo × %recortes / 100
descargado = recortes × (1 + MOC)
lodo       = recortes × MOC
```

**Centrífuga** (balance de masa):
```
Q_descarte = Q_entrada × (ρ_entrada − ρ_salida) / (ρ_descarte − ρ_salida)   (acotado entre 0 y Q_entrada)
descargado = Q_descarte × horas × 60 / 42     (bbl)
lodo       = descargado × MOC / (1 + MOC)
recortes   = descargado − lodo
```

Verificado con los 3 ejemplos del manual (págs. 118-120). Por ejemplo, 18,9 gpm × 0,07 / 0,72 = 1,84 gpm → × 22 h = 9,2; lodo 4,2 con MOC 0,855.

Si falta un dato necesario, el resultado queda vacío: no se inventan valores.

### Costo del equipo

`costo_diario = cantidad_usada × tarifa`, o 0 con `SIN_COBRO`. La **tarifa se copia del pozo el día que se registra** y se conserva mientras no cambie el código de cobro: editar un día viejo no cambia su precio. También se muestran acumulados de horas, descargado, lodo y costo por serie.

> **Pendiente del usuario:** agregar un campo **"Unidades"** en la renta de equipos y bloquear según la cantidad disponible en el almacén. Hoy se puede indicar una cantidad mayor a la existente, porque ese campo no existe.

## 4. Modelos

| Modelo | Clave |
|---|---|
| `TipoTicketMalla` | por pozo · `nombre` único · `sentido` ENTRADA/SALIDA |
| `TicketMalla` | por reporte · tipo, número, personas, almacén (copia) |
| `TicketMallaDetalle` | malla maestra · nuevas/usadas según ticket y reales |
| `TransaccionMalla` | por reporte · `secuencia` (por pozo), acción, malla, equipo maestro + **serie** + descripción (copia), posición, precio unitario |
| `UsoEquipoDia` | por reporte · serie + copia de datos del equipo · datos capturados. Los volúmenes **no se guardan** |
| `UsoEquipoPropiedad` | valores diarios de propiedades adicionales |

Detalle campo por campo en [03](03_MODELO_DATOS.md).
