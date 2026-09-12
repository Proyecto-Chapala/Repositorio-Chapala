# Manual del Sistema de Reportes de Fluidos de Perforación (Proyecto CHAPALA)

## Qué es esto y para qué sirve

Este módulo (la app `reportes` dentro de Proyecto CHAPALA) es un sistema de reportes diarios de fluidos de perforación para All Oil Services, C.A. (AOS), construido siguiendo la lógica del software comercial **ONE-TRAX** de M-I SWACO — el estándar de la industria para llevar el control de lodos de perforación.

La idea central es simple: cada pozo se perfora por tramos (intervalos), y cada día de trabajo se genera un reporte que registra qué pasó ese día — profundidad, geometría del hoyo, volúmenes de fluido, químicos usados, pérdidas, horas de actividad, etc. Al final de cada tramo, se hace un cierre formal que concilia todos los números.

Este documento explica, paso a paso, cómo funciona cada pieza y en qué orden se usan.

---

## La jerarquía de datos (de lo general a lo específico)

```
Pozo
 └── Intervalo (tramo del pozo, ej. "Sección de 12¼\"")
      ├── Tubería Instalada (revestidor/liner de ese tramo)
      ├── Fosas y Categorías de Pérdida (catálogos, se configuran una vez por pozo)
      └── Reporte Diario (uno por cada día de trabajo)
           ├── Distribución de Tiempo (horas del día)
           ├── Geometría de Sarta (tubulares metidos ese día)
           ├── Transacciones de Fosa (químicos, pérdidas, transferencias)
           ├── Lecturas de Fosa (medición física de volumen)
           ├── Muestras de fluido y sus propiedades
           ├── Inventario y uso de materiales
           ├── Uso de equipos
           └── Comentarios
```

Cuando un Intervalo se **cierra**, todo lo que cuelga de él (reportes, tuberías, transacciones) queda bloqueado permanentemente para edición.

---

## El flujo de trabajo completo (Pasos 1 a 7)

El manual ONE-TRAX real organiza la captura de datos en 7 pasos. Así se ven implementados en este sistema:

### Paso 1 — Configuración Inicial del Pozo (`Project → General`)

**Dónde:** pestaña "Pozos".

Es lo primero que se llena al abrir un pozo nuevo. Dos grupos de datos:

- **Identificación:** Log-It Number (número de seguimiento corporativo M-I SWACO, obligatorio), Operador, Nombre del Pozo, Campo/Bloque, Nombre del Taladro, Contratista, Fecha de Spud.
- **Parámetros base:**
  - Surface Temp y Temp Gradient (para cálculos térmicos/reológicos).
  - Unit Set: **Oilfield** (ft, in, bbl, lb/gal) o **Metric**.
  - Is Offshore / Uses Riser, y si aplica: Air Gap, Water Depth, Sea Floor Temp.

**Regla importante — Congelamiento Base:** en cuanto se crea el primer Reporte Diario del pozo, el **Unit Set** y las casillas **Is Offshore/Uses Riser** quedan bloqueadas para siempre. Esto es a propósito: evita que a mitad de un pozo alguien cambie de unidades y arruine el histórico. Configúralos bien desde el principio.

### Paso 2 — Estructura de Intervalos (`Project → Intervals`)

**Dónde:** pestaña "Intervalos" (eliges el pozo primero).

Un pozo se perfora en tramos. Cada Intervalo define:

- **Número** correlativo (0, 1, 2…).
- **Operational Mode:** Drilling o Completion.
- **Type:** Casing, Liner, u Open Hole.
- **Top Of Liner / Sidetrack:** obligatorio solo si el tipo es Liner, o si el intervalo nace de un desvío del pozo (sidetrack).
- Profundidad inicial, profundidad final (se llena al cerrar), diámetro.
- **Start Volume:** el volumen de lodo con el que arranca el intervalo. Normalmente **no lo llenas a mano** — el sistema lo hereda automáticamente del cierre del intervalo anterior (ver Paso 7). Solo el primer intervalo del pozo lo pides manualmente.

**Regla de Sidetrack:** si marcas "Es Side Track", la profundidad inicial del nuevo intervalo se fija automáticamente en el "Top Of Liner/Sidetrack" que indiques (el tope del tapón de cemento) — no la escribes tú directamente.

Cada Intervalo también tiene un **Sistema de Fluido** asignado (agua, polimérico, aceite, etc.), fijo mientras el intervalo esté abierto.

### Paso 3 — Catálogos de Fosas y Pérdidas (`Pits Setup & Loss Setup`)

**Dónde:** pestaña "Fosas y Pérdidas" (por pozo). Se configura **una vez por pozo**, antes de empezar a operar.

Dos catálogos independientes:

**3.1 — Fosas y Tanques (Pits):**
Cada fosa tiene: nombre único (ej. "Active 1", "Reserve 1"), capacidad en bbl, y un tipo — Active, Reserve, Premix, Spacer, Storage, o Dead Volume. Además, cada fosa se marca como:
- **Transaccional:** participa del balance diario de lodo activo (recibe/envía volumen en las transacciones del día a día).
- **No transaccional:** almacenamiento aislado (ej. "Base Oil Storage") que solo se controla visualmente, sin afectar el balance.

**3.2 — Categorías de Pérdida (catálogo cerrado, no texto libre):**
Las pérdidas de fluido no se escriben como texto libre — se eligen de una lista cerrada, separada por modo operativo (Drilling / Completion):

| Dominio | Categorías típicas |
|---|---|
| Superficial | Shakers, Centrifuges, Surface/Dumped, Evaporation |
| Subsuperficial | Losses to Formation, **Left in Hole** |

> **Importante:** la categoría **"Left in Hole"** (Subsuperficial) es la que usa automáticamente el cierre de intervalo (Paso 7). Créala para cada pozo/modo operativo desde el principio, o el cierre no va a poder ejecutarse.

### Paso 4 — Apertura del Día Operativo (`Daily → General`)

**Dónde:** al crear un Reporte Diario, y dentro de su detalle (sección "Distribución de Tiempo").

Cada Reporte Diario trae automáticamente:
- **Date y Report #:** correlativo automático por pozo, tú no lo asignas.
- **Default Interval / Default Fluid System:** se muestran como información de cabecera, heredados directamente del Intervalo al que pertenece el reporte.

Lo que sí llenas manualmente es la **Time Distribution**: un desglose libre de las 24 horas del día en actividades del taladro (ej. "Rotary Drilling: 8h", "Circulating: 4h", "Tripping In: 6h"…). El sistema te muestra un indicador:
- ✓ **Cuadrado** si el total suma exactamente 24.00 hrs.
- ⚠ **No cuadra** si suma menos o más.

Esto es solo informativo — no bloquea el reporte, es una alerta para que corrijas antes de terminar de llenar el día.

### Paso 5 — Geometría de Hoyo y Sarta (`Daily → Geometry`)

**Dónde:** dentro del detalle del Reporte Diario, primera sección técnica.

Dos tablas:

**5.1 — Wellbore Geometry (geometría del hoyo):**
Se cargan Bit Depth (profundidad de la mecha), Bit Size (diámetro de la mecha) y % Washout (ensanchamiento del hoyo). Con eso, el sistema calcula:

```
Hole Size = Bit Size × (1 + %Washout / 100)
```

Si no hay revestidor instalado en ese tramo, el "diámetro de confinamiento" para los cálculos de volumen anular es este Hole Size; si ya hay tubería instalada, se usa el ID de esa tubería.

**5.2 — Drill String Geometry (geometría de la sarta):**
Se carga tubular por tubular lo que está metido en el pozo ese día (Drill Pipe, Heavy Weight, Drill Collar, Sub), cada uno con su OD/ID.

La fila de **Drill Pipe principal** no lleva longitud manual — se calcula sola:

```
Longitud Drill Pipe = Bit Depth − Σ(longitud de los demás tubulares)
```

Con esas longitudes, cada tramo calcula su volumen:

```
Capacidad interna (bbl) = Pipe ID² / 1029.4 × Longitud
Volumen anular (bbl)    = (ID_hoyo_o_revestidor² − Pipe OD²) / 1029.4 × Longitud
```

### Paso 6 — Contabilidad Volumétrica (`Daily → Volume Accounting`)

**Dónde:** dentro del detalle del Reporte Diario, después de la geometría. Es el corazón del control de lodo.

**6.1 — Volumen del hoyo:**
```
Total Hole Volume = Vol. Anular + Vol. Sarta + Vol. Debajo de la Mecha
Fluid Volume       = Total Hole Volume − Volume Not Fluids
```
"Volume Not Fluids" es cualquier volumen atrapado en el hoyo que no es parte del fluido activo (ej. agua salada de la perforación inicial).

**6.2 — Transacciones de fosa:**
Todo movimiento de lodo se registra como una de estas 3 transacciones:

| Tipo | Qué hace | Cómo se calcula el volumen |
|---|---|---|
| **Add Chemicals** | Agrega un producto a una fosa | `(Cantidad Usada × Cantidad Unitaria) / (Gravedad Específica × 350)` — automático, nunca a mano |
| **Loss** | Sale fluido físicamente de una fosa | Manual, obligatoriamente con una categoría del catálogo de pérdidas (Paso 3) |
| **Transfer** | Mueve volumen entre dos fosas | Manual — no afecta el balance total (se cancela solo) |

Si marcas "Is Dilution" en un Add Chemicals, indica que lo que agregaste es agua/base líquida para diluir (afecta la concentración de esa fosa).

**6.3 — Inmutabilidad:** cada transacción guarda de forma fija a qué intervalo pertenecía al momento de crearse. Aunque después cambie algo en la cabecera del día, esa transacción no se reasigna.

**6.4 — Reconciliación "Not Accounted = 0":**
Además de las transacciones, cada día se registran **Lecturas de Fosa**: la medición física real (con cinta/dip) del volumen en cada fosa. El sistema compara:

```
Volumen Teórico  = suma de libros (Add Chemicals − Loss, acumulado desde el inicio)
Volumen Medido   = suma de las lecturas físicas del día
Not Accounted    = Volumen Teórico − Volumen Medido
```

Un indicador verde/rojo muestra si esto cuadra en 0.00. Si no cuadra, hay un volumen que no se explicó — y debe imputarse a una pérdida antes de cerrar el intervalo (ver Paso 7).

### Paso 7 — Cierre Volumétrico del Intervalo (`Interval Closeout`)

**Dónde:** pestaña "Intervalos", botón "Cerrar Intervalo" en cada tarjeta.

Este es el paso final de cada tramo del pozo, y el único punto del sistema donde el balance se exige de forma **estricta** (bloqueante):

1. Se fija la **profundidad final** (zapata o tope de cemento).
2. La tubería instalada definitiva ya debe estar cargada (Paso 2/tabla de tuberías).
3. Si queda **Volume Not Fluids** atrapado, el sistema genera automáticamente una transacción real de tipo **Loss** contra la categoría **"Left in Hole"**, descontada de la fosa que elijas. No es un monto libre — queda contabilizado como una pérdida real, trazable.
4. **El sistema no te deja cerrar** si el "Not Accounted" del último reporte diario no está en exactamente 0.00. Tienes que ajustar lecturas de fosa o el Volume Not Fluids antes de poder cerrar.

Al cerrar:
- El Intervalo pasa a estado **Cerrado** y queda bloqueado — nadie puede editar reportes, tuberías, ni transacciones de ese intervalo nunca más.
- **Rollover:** cuando creas el siguiente intervalo del mismo pozo, su **Start Volume** se llena automáticamente con el **Final Volume** del intervalo recién cerrado — así el balance de lodo continúa sin discontinuidad entre tramos.

---

## Resumen visual del ciclo de vida de un pozo

```
1. Crear Pozo (Log-It #, unidades, offshore/riser — se congela al primer reporte)
2. Crear Intervalo 1 (modo, tipo, sistema de fluido, Start Volume manual)
3. Configurar catálogo de Fosas y catálogo de Pérdidas (una vez, incluye "Left in Hole")
4. Por cada día de perforación:
     a. Crear Reporte Diario (fecha/número automáticos)
     b. Llenar Distribución de Tiempo (24 hrs)
     c. Actualizar Geometría de Hoyo y Sarta (Bit Depth, tubulares)
     d. Registrar transacciones de fosa (Add Chemicals / Loss / Transfer)
     e. Registrar lecturas de fosa (medición física)
     f. Revisar que "Not Accounted" cuadre en 0.00
     g. (Muestras de fluido, inventario, uso de equipos, comentarios)
5. Al terminar el tramo: Cerrar Intervalo
     - Se fija profundidad final
     - Se descarga el Volume Not Fluids como pérdida "Left in Hole"
     - Se exige balance en 0.00
     - Intervalo queda bloqueado
6. Crear Intervalo 2 → su Start Volume hereda el Final Volume del Intervalo 1
7. Repetir hasta terminar el pozo
```

---

## Preguntas frecuentes rápidas

**¿Por qué no puedo cambiar el Unit Set de un pozo?**
Porque ya se creó al menos un Reporte Diario en ese pozo. Es una regla de integridad de datos: mezclar unidades a mitad de pozo generaría errores de cálculo imposibles de rastrear.

**¿Por qué el sistema no me deja escribir libremente el motivo de una pérdida?**
Porque el manual ONE-TRAX exige un catálogo cerrado y estandarizado de categorías de pérdida (Loss Setup), para que los reportes de distintos pozos y taladros sean comparables entre sí.

**¿Qué pasa si el "Not Accounted" no cuadra un día cualquiera (no al cerrar el intervalo)?**
Nada se bloquea todavía — es solo una alerta visual para que el equipo lo revise. La regla dura de balance en 0.00 solo aplica al **cerrar el intervalo completo** (Paso 7).

**¿Puedo editar algo de un intervalo ya cerrado?**
No. El cierre es definitivo y bloquea en cascada todo lo que cuelga de ese intervalo (reportes, transacciones, tuberías, muestras, etc.).

---

*Documento de referencia interno — Proyecto CHAPALA, basado en el "manual resumido, esquema.pdf" (adaptación del manual ONE-TRAX de M-I SWACO) y en la implementación real del sistema (Pasos 1 a 7 completos).*
