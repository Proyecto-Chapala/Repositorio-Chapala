# Contexto — Proyecto CHAPALA (para continuar en una conversación nueva)

Pega este archivo completo como primer mensaje de la nueva conversación para
que Claude tenga todo el contexto necesario.

---

## 1. Qué es el proyecto

Proyecto CHAPALA: sistema Django para **All Oil Services, C.A. (AOS)**, en la
carpeta `Proyecto CHAPALA` de la máquina Windows del usuario
(`C:\Users\SECRETARIA\Documents\Programacion\Personal\Proyecto CHAPALA`).
Usa Django + PostgreSQL/SQLite. Dos apps conviven en el mismo proyecto:

- **`mychapala`** — inventario químico. **Ya está en producción real y
  dominado por el usuario. No se toca.**
- **`reportes`** — sistema de reportes de fluidos de perforación estilo
  ONE-TRAX (M-I SWACO): Pozo → Intervalo → ReporteDiario, con UUIDs como
  primary key. **Esta es la app que se está reconstruyendo desde cero.**

Repositorio con git, ramas `main` y `Archivos-de-contexto` (quedaron
divergentes en algún momento por subir documentación vía GitHub web; si
vuelve a pasar, resolver con merge de main hacia Archivos-de-contexto).

Esta sesión de Claude (cloud) **no tiene acceso a PyPI ni puede correr
Django** (no hay `makemigrations`/`migrate` aquí). Las migraciones se
escriben a mano y el usuario las corre él mismo (`python manage.py migrate`)
en su máquina real. Validación en esta sesión: `python3 -m py_compile` para
Python, `node --check` para JS.

## 2. Historial de `reportes` (versión anterior, ya construida Pasos 1-7)

Se había construido completo el manual ONE-TRAX resumido (Pasos 1 a 7):
configuración de Pozo, configuración de Intervalo (incluyendo Top of
Liner/Sidetrack), catálogos de Fosas y Categorías de Pérdida, Geometría de
Hoyo y Sarta (con un esquema SVG dinámico agregado al final), Contabilidad
Volumétrica (Volume Accounting), Distribución de Tiempo (24h) y Cierre de
Intervalo (con Left-in-Hole real conectado al catálogo de pérdidas y
Rollover de volumen al siguiente intervalo).

## 3. Por qué se reinicia `reportes`

El usuario compartió 4 audios/transcripciones reales de un ingeniero de
fluidos explicando cómo funciona ONE-TRAX de verdad. Del análisis salió que
el núcleo del sistema (fórmula única de volumen, ensamblaje como lista de
componentes, bit depth como dato que dispara todo el cálculo, cierre de
intervalo al bajar revestidor, balance volumétrico, distribución de tiempo,
pérdidas categorizadas) coincide con lo ya construido — pero la app se había
ido enredando en el camino, y el usuario decidió **reiniciar `reportes` de
forma ordenada**, dejando el código actual guardado aparte como referencia
en una carpeta `reportes_viejo/` (no se borra, se reaprovechará bastante de
ahí).

## 4. Plan de reconstrucción acordado (documento ya entregado al usuario:
`PLAN_REINICIO_REPORTES.md`)

Principio rector: una sola fórmula de volumen siempre —
capacidad interna = `ID² / 1029.4 × longitud`;
anular = `(OD_externo² − OD_interno²) / 1029.4 × longitud`.
Lo único que cambia es qué diámetros y qué longitud según el tramo. El dato
que decide "dónde estás parado" es la **profundidad de la mecha (Bit
Depth)**.

Orden de construcción:

- **Paso 0 — Catálogos base del pozo** (una vez, antes de perforar): datos
  generales del Pozo; **catálogo NUEVO de componentes de ensamblaje**
  (Mecha, Drill Collar, Heavyweight, Drill Pipe, Crossover — cada uno con
  nombre, OD, ID; la longitud NO va en el catálogo, se define al armar el
  ensamblaje real); catálogo de Fosas y Categorías de Pérdida (se reutiliza
  igual que antes).
- **Paso 1 — Preparación del Intervalo**: número, modo operativo; **BHA
  planeado** armado seleccionando componentes del catálogo del Paso 0, en
  orden desde la mecha hacia arriba, cada uno con su longitud, editable en
  cualquier momento; diámetro del hoyo a perforar; hereda automáticamente el
  revestidor del intervalo anterior si aplica (reutiliza el mecanismo de
  `volumen_inicial`/rollover ya probado). **Fuera de alcance a propósito:
  Top of Liner / Sidetrack** (el propio ingeniero dijo "no nos compliquemos
  con eso todavía" — se deja para una segunda vuelta).
- **Paso 2 — Reporte Diario → Geometría**: Bit Depth es el único dato que
  hay que ingresar; con eso + ensamblaje activo + hoyo/revestidor activo se
  recalcula automáticamente todo (volumen interno por componente, volumen
  anular por tramo, volumen bajo la mecha). **Fuera de alcance a propósito:
  %Washout y distinción MD/TVD en el día a día** (TVD solo aplicaría en el
  cierre de intervalo, no es indispensable ahora).
- **Paso 3 — Distribución de tiempo (24h)**: se reutiliza tal cual estaba.
- **Paso 4 — Volumetría/Balance del día**: transacciones de fosa (productos,
  pérdidas categorizadas, transferencias), lecturas de fosa, balance teórico
  vs. medido ("Not Accounted"). Se reutiliza tal cual estaba.
- **Paso 5 — Cierre de Intervalo**: bajar/cementar revestidor fija el nuevo
  diámetro de confinamiento; Left-in-Hole si aplica; exige balance en cero;
  rollover de volumen al siguiente intervalo. Se reutiliza tal cual estaba.

**Explícitamente descartado/pospuesto de la versión anterior**: Top of
Liner/Sidetrack (Paso 1 nuevo) y la hidráulica de bomba (estrobos, bbl/min,
bottoms-up time, lag time — nunca se llegó a construir, confirmado como
trabajo futuro por el propio ingeniero en los audios).

**Se conserva casi intacto**: catálogos de Fosas/Categorías de Pérdida,
modelo de Volumetría/Balance, modelo de Distribución de Tiempo, modelo de
Cierre de Intervalo con Left-in-Hole y Rollover — es decir, el reinicio real
es sobre la configuración de Intervalo y la Geometría/Ensamblaje diario, que
es justo la parte que se había enredado.

**Este plan fue enviado al usuario para su revisión y todavía no ha
confirmado si lo aprueba tal cual o quiere ajustar algo antes de tocar
código.**

## 5. Pendiente sin resolver (aparte del reinicio)

El usuario cambió de PC y en esa máquina nueva **PostgreSQL no está
corriendo en localhost** (settings.py usa `USE_POSTGRES=True` por defecto,
leyendo `.env` si existe). El usuario pospuso este tema explícitamente
("olvidémoslo, sigamos con lo que teníamos pendiente") y no se ha vuelto a
tocar. Hay que resolver si usará un Postgres compartido/remoto o SQLite
local en esa máquina antes de poder correr `migrate` ahí.

## 6. Cómo se ha estado trabajando en esta sesión cloud

Sin acceso al dispositivo del usuario en la mayoría de los casos (el bridge
remoto ha estado intermitente/desconectado), el flujo ha sido: escribir/
editar archivos en el entorno cloud, validar sintaxis (`py_compile` /
`node --check`), y entregar los archivos cambiados al usuario como zip para
que él mismo los reemplace en su carpeta real del proyecto, indicándole
exactamente qué archivo va en qué ruta. Las migraciones son escritas a mano
(esta sesión no puede correr `makemigrations`).

## 7. Siguiente paso inmediato

Esperar la confirmación (o ajustes) del usuario sobre `PLAN_REINICIO_REPORTES.md`
y, con luz verde, empezar a reconstruir `reportes` en el orden ahí descrito,
reaprovechando el código ya validado de Distribución de Tiempo, Volumetría y
Cierre de Intervalo, y construyendo desde cero el catálogo de componentes de
ensamblaje y la configuración simplificada de Intervalo + Geometría diaria.
