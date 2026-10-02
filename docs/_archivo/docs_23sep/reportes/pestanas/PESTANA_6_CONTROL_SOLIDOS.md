# Pestaña 6 — Control de sólidos (Solids Equipment)

Dos partes:

- **Fase 1 — Mallas de zaranda**: inventario de mallas nuevas y usadas, tickets de entrega o devolución y movimientos de mallas en los equipos.
- **Fase 2 — Uso de equipos**: rendimiento, costo de renta y paradas de cada equipo del pozo.

| | |
|---|---|
| Motor | `control_solidos.py` (sin Django) |
| Vistas | `views_control_solidos.py` |
| Modelos | `TipoTicketMalla`, `TicketMalla`, `TicketMallaDetalle`, `TransaccionMalla`, `UsoEquipoDia`, `UsoEquipoPropiedad` (`models_control_solidos.py`) |
| JS / CSS | `reporte_control_solidos.js`, `reporte_control_solidos.css` |

## Requisitos previos

En la configuración del pozo (*Productos / Equipos / Mallas Activos*):

- **Mallas activas** con su precio y descuento.
- **Equipos activos** con número de serie y tarifas de renta y stand-by.
- En Catálogos Maestros, los equipos que llevan mallas deben tener **posiciones de malla** > 0 (zaranda BEM 3 = 3, BEM 600 = 5; la posición 1 es la más cercana a la línea de flujo). Solo esos equipos aparecen en el control de mallas.

---

## Fase 1 — Mallas

### Inventario derivado, no guardado

El inventario de mallas **no se guarda**. `control_solidos.simular()` repite, en orden, todos los tickets y transacciones del pozo: el final de ayer es el inicial de hoy. Dentro de un mismo reporte, primero los tickets (lo recibido hoy se puede usar hoy) y luego las transacciones por número de secuencia.

Resultado para el día abierto, por malla:

| Columna | Qué es |
|---|---|
| Nuevas: inicial, recibidas, devueltas, instaladas, final | Mallas nuevas en el almacén del taladro |
| Usadas: inicial, entradas, salidas, final | Mallas usadas guardadas en el almacén del taladro |
| Costo diario y acumulado | Precio neto de las mallas **nuevas instaladas** |

Además: qué malla hay en cada posición de cada equipo.

### Tickets de mallas

Un ticket registra mallas que **entran** o **salen** del pozo.

- **Tipo de ticket**: catálogo del pozo con nombre y sentido (ENTRADA / SALIDA). Se siembran 4 de ejemplo, editables porque AOS no tenía definidos los suyos: *Recepción desde almacén* (entrada), *Devolución a almacén* (salida), *Recepción desde otro pozo* (entrada), *Envío a otro pozo* (salida). No se puede borrar un tipo que tenga tickets.
- Datos: número, pedido por, recibido por, almacén (de los almacenes del pozo).
- Por malla: **nuevas según ticket**, **nuevas reales**, **usadas según ticket**, **usadas reales**. El inventario usa **siempre las reales**; la diferencia con el papel se marca.
- Solo mallas activas del pozo; no se repite una malla en el mismo ticket.

### Movimientos de mallas (Shaker Screen Transactions)

| Acción | Efecto | Validación |
|---|---|---|
| Instalar malla nueva | −1 nueva; ocupa la posición; **genera costo** (precio neto) | Debe haber nuevas en stock; la posición debe estar libre |
| Instalar malla usada | −1 usada; ocupa la posición | Debe haber usadas en el almacén; posición libre |
| Pasar al almacén | Libera la posición; +1 usada | La posición debe tener esa malla |
| Desechar del equipo | Libera la posición | La posición debe tener esa malla |
| Desechar del almacén | −1 usada | Debe haber usadas. Puede ser una malla que ya no está activa |

Para retirar, el sistema toma la malla que hoy está en esa posición.

**Precio neto** = precio × (100 − descuento %) / 100, redondeado a centavos. Se **copia** en el movimiento: si después cambia el precio del pozo, el costo de los días pasados no cambia. Verificado con el manual: el costo acumulado es múltiplo del precio de la malla.

### Validación de toda la línea de tiempo

Cada guardado (ticket, movimiento, deshacer, borrar ticket) se hace dentro de una transacción de base de datos: se guarda, se simula **todo el pozo** y, si algún día (antes o después del que se edita) queda imposible, se deshace y se muestra un mensaje como:

> El 21/09/2026 (transacción #14): no hay mallas nuevas de API 140 (Mesh 140) en stock. Registra primero el ticket de recepción.

### Deshacer

Cada movimiento tiene un número de **secuencia** que crece por pozo. Solo se puede deshacer el **último movimiento del pozo**, y solo desde el reporte al que pertenece.

---

## Fase 2 — Uso de equipos

Una fila por equipo activo, con tres vistas: **Rendimiento**, **Costos de renta** y **Uso y paradas**.

### Datos que se capturan

| Vista | Campos |
|---|---|
| Rendimiento | Horas en operación (0-48), lodo en recortes MOC (bbl/bbl, 0-20), % de recortes (0-100), tipo de pérdida (catálogo del pozo). Centrífugas: caudal de entrada (gpm) y densidades de entrada, salida y descarte (lb/gal) |
| Costos | Cantidad usada, código de cobro (Completo / Stand-by / Sin cobro), "¿equipo de fluidos de perforación?" |
| Uso y paradas | Horas de parada, observaciones y las **propiedades del equipo** definidas en *Configuración de Propiedades de Equipo* (ángulo de canasta, fuerza G, velocidad del tazón...) |

La **tarifa** se copia del equipo activo según el código de cobro (renta o stand-by) el día que se guarda. `costo diario = cantidad usada × tarifa` (0 si es sin cobro).

### Cálculos (verificados con los tres ejemplos del manual, págs. 118-120)

Volumen de hoyo perforado en el día:

```
avance = profundidad de hoy − profundidad del reporte anterior   (pestaña 1)
diámetro = mecha con lavado (pestaña 2) o diámetro de hoyo del intervalo
volumen perforado (bbl) = diámetro² / 1029.4 × avance
```

Zarandas, limpiador de lodo y secador de recortes:

```
recortes    = volumen perforado × % de recortes / 100
descargado  = recortes × (1 + MOC)
lodo perdido = recortes × MOC
```

Centrífugas (balance de masa):

```
Q descarte = Q entrada × (ρ entrada − ρ salida) / (ρ descarte − ρ salida)      (limitado entre 0 y Q entrada)
descargado (bbl) = Q descarte × horas × 60 / 42
lodo perdido = descargado × MOC / (1 + MOC)
recortes = descargado − lodo perdido
```

Ejemplos del manual: lodo = descargado × MOC/(1+MOC) da 1 → 0.6 con MOC 1.463; 9.2 → 4.2 con 0.855; 2.2 → 0.4 con 0.214. Centrífuga: 18.9 gpm × 0.07 / 0.72 = 1.84 gpm; × 22 h = 9.2 m³.

Estos volúmenes **no se guardan**: se recalculan porque dependen de la profundidad y del diámetro, que se pueden corregir después. El mismo cálculo existe en JavaScript (`csCalcularRendimiento`) para ver el resultado mientras se escribe.

### Acumulados

Por número de serie: horas, volumen descargado, lodo perdido y costo de todos los días anteriores más hoy.

### Relación con la pestaña 8

El **lodo perdido** de cada equipo se suma por tipo de pérdida y aparece en la tabla de pérdidas de la volumetría como "descargado por los equipos", como referencia al registrar la pérdida real.

## Costos

Renta de equipos y mallas nuevas instaladas van a la columna **Equipos / Mallas** del resumen de costos (pestaña 1) y al Excel (hojas "Equipos" e "Inventario de Mallas").
