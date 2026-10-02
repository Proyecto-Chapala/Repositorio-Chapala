# Plan de reinicio — App `reportes` (Proyecto CHAPALA)

> `mychapala` (inventario) no se toca — sigue en producción tal cual está.
> Este documento reordena SOLO la app `reportes`, basado en lo que quedó confirmado
> en los audios del ingeniero (CHAMBA.txt, 1.txt, 2.txt, 3.txt) más el manual
> resumido ya revisado. La idea es construir en el orden real en que se usa el
> sistema, sin adelantar funcionalidad que el propio ingeniero dice que "todavía
> no, no nos compliquemos con eso".

---

## Principio rector (repetido varias veces en los audios)

Todo el cálculo de volumen usa **una sola fórmula**, siempre:

- Volumen dentro de un tubo (capacidad): `ID² / 1029.4 × longitud`
- Volumen en el espacio anular entre dos diámetros: `(OD_externo² − OD_interno²) / 1029.4 × longitud`

Lo único que cambia es **qué diámetros y qué longitud le metes** según en qué
tramo estés parado. Y el dato que decide "dónde estás parado" es uno solo:
**la profundidad de la mecha (Bit Depth)**. Todo el resto de la geometría se
arma alrededor de ese dato.

---

## Orden de construcción

### Paso 0 — Catálogos base del pozo (una sola vez, antes de perforar)

Esto es "la preparación", como la llama el ingeniero — se llena antes de que
arranque la operación:

1. **Pozo**: datos generales mínimos (nombre/Log-It Number, Rig, Contractor).
2. **Catálogo de componentes de ensamblaje** (NUEVO — esto es lo que el
   ingeniero pide varias veces: *"una tablita para ir metiendo nuestros
   ensamblajes"*): una tabla reutilizable de componentes típicos —
   Mecha, Drill Collar, Heavyweight, Drill Pipe, Crossover — cada uno con
   nombre, diámetro externo y diámetro interno (la longitud NO va en el
   catálogo, esa se define cada vez que se arma un ensamblaje real).
   Esto evita que la persona tenga que escribir los diámetros a mano cada
   vez; los selecciona de la lista.
3. **Fosas (Pits)** y **Categorías de pérdida** — catálogo, tal como ya está
   hecho hoy (esto sí quedó validado, se reutiliza igual).

### Paso 1 — Preparación del Intervalo (el "plan" antes de perforar)

Por cada intervalo, antes de empezar a perforar:

1. Número de intervalo, modo operativo (Drilling/Completion).
2. **Ensamblaje de fondo (BHA) planeado**: se arma seleccionando componentes
   del catálogo del Paso 0, en orden desde la mecha hacia arriba (mecha →
   componentes pesados → tubería de perforación), cada uno con su longitud.
   Editable en cualquier momento durante la perforación (se puede sacar un
   componente y meter otro; queda registrado el cambio).
3. Diámetro del hoyo que se va a perforar en este intervalo.
4. Si viene de un intervalo anterior cerrado: el diámetro/profundidad del
   revestidor ya asentado se hereda automáticamente (eso ya existe, se
   reutiliza el mecanismo de `volumen_inicial`/rollover que ya probamos).

**Fuera de este primer alcance a propósito** (el propio ingeniero lo dice: "no
nos compliquemos con eso todavía"): Top of Liner / Sidetrack. Se deja para una
segunda vuelta cuando el flujo básico esté sólido y en uso real.

### Paso 2 — Reporte Diario → Geometría (el corazón del sistema)

Cada día:

1. Fecha / N° de reporte (consecutivo dentro del intervalo).
2. **Profundidad de la mecha (Bit Depth)** — el único dato que hay que meter
   para que todo se recalcule.
3. Con ese dato más el ensamblaje activo (Paso 1) y el hoyo/revestidor
   activo (Paso 0/cierre anterior), el sistema calcula automáticamente,
   tramo por tramo, con la fórmula única de arriba:
   - Volumen interno de cada componente de la sarta.
   - Volumen anular de cada tramo (contra revestidor si hay, contra hoyo
     abierto si no).
   - Volumen del hoyo abierto por debajo de la mecha (siempre lleno, sin
     tubería).
4. Total: Volumen del hoyo = anular + sarta + debajo de la mecha.

**Fuera de este alcance a propósito**: %Washout (no aparece mencionado en
ningún momento como algo indispensable) y la distinción MD/TVD (el ingeniero
la menciona solo en el contexto puntual de cerrar el intervalo con el
revestidor — se puede agregar ahí después, no hace falta en el día a día).

### Paso 3 — Distribución de tiempo (24 horas)

Tabla simple de actividad + horas, debe sumar 24. Esto ya lo teníamos bien
resuelto, se reutiliza igual.

### Paso 4 — Volumetría / Balance del día

1. Transacciones de fosa: productos agregados (volumen autocalculado por
   fórmula de peso/gravedad específica), pérdidas (obligadas a categoría del
   catálogo), transferencias.
2. Lecturas de fosa (medición manual).
3. Balance: volumen teórico (geometría + productos − pérdidas) vs. volumen
   medido en fosas → diferencia ("Not Accounted").

Esto también ya estaba bien resuelto — se reutiliza el modelo tal cual.

### Paso 5 — Cierre de Intervalo

1. Se baja y cementa el revestidor → its diámetro pasa a ser el nuevo
   "diámetro de confinamiento" para el siguiente intervalo.
2. Si queda volumen atrapado (no fluido), se descarga como pérdida
   "Left in Hole" contra la fosa que se indique.
3. Se exige balance en cero antes de permitir cerrar (única regla dura).
4. Rollover: el volumen final de este cierre es el volumen inicial del
   siguiente intervalo.

Esto también ya estaba bien resuelto — se reutiliza el modelo tal cual.

---

## Qué se descarta / se pospone de lo que ya habíamos construido

- **Top of Liner / Sidetrack** en la configuración del intervalo — se saca
  del alcance inicial. Si más adelante hace falta, se agrega como un modo
  avanzado opcional, no como parte del flujo normal.
- **Hidráulica de bomba** (estrobos, bbl/min, bottoms-up time, lag time) —
  nunca se llegó a construir, y los audios confirman que es trabajo futuro
  explícito ("eso lo vamos a hacer" — todavía no). Se mantiene fuera.

## Qué se conserva sin cambios de los pasos anteriores

- Todo el modelo de catálogos de Fosas y Categorías de Pérdida (Paso 3
  original).
- Todo el modelo de Volumetría/Balance (Paso 6 original).
- Todo el modelo de Distribución de Tiempo (Paso 4 original).
- Todo el modelo de Cierre de Intervalo con Left-in-Hole y Rollover
  (Paso 7 original).

Es decir: el reinicio es realmente sobre el **Paso 1 (config. de intervalo)**
y el **Paso 5 original de geometría/ensamblaje**, que es justo la parte que
—como bien dijiste— se fue enredando. El resto del trabajo ya hecho se
reaprovecha casi intacto, solo reconectado en el orden correcto.

---

## Siguiente paso

Con tu visto bueno a este documento, la reconstrucción sería:

1. Nueva app `reportes` limpia (el código actual se guarda en `reportes_viejo/`
   como referencia, según acordamos).
2. Se reconstruye en el orden de este documento: Paso 0 → 1 → 2 → 3 → 4 → 5.
3. Se reutiliza el código de Distribución de Tiempo, Volumetría y Cierre de
   Intervalo casi tal cual (ya estaban validados), solo se les cambia el
   nombre de app/imports si hace falta.
4. Se construye desde cero el catálogo de componentes de ensamblaje (nuevo)
   y la configuración simplificada de intervalo + geometría diaria.

¿Confirmas este orden, o ajustamos algo antes de empezar a tocar código?
