# 05 — Configuración del pozo

Este documento cubre todo lo que se hace **antes** de llenar reportes diarios: el wizard, la pantalla Spud Date, la pantalla principal del pozo con sus 8 setups y los catálogos maestros globales.

## 1. Ciclo de vida de un pozo

```
BORRADOR  ──(wizard paso 4: confirmar)──►  ACTIVO  ──(sin pantalla aún)──►  CERRADO
   │                                          │
   └─ se puede retomar en                     └─ la 1ª vez que se abre → pantalla Spud Date (una sola vez)
      /pozos/<id>/continuar/
```

- Mientras está en **BORRADOR**, cada paso del wizard se guarda solo, y `paso_wizard_actual` recuerda dónde quedó el usuario.
- Si alguien entra a `/pozos/<id>/` (pantalla principal) o a Spud Date con el pozo en borrador, el sistema lo **redirige al wizard**.
- **CERRADO** existe como opción del modelo, pero ninguna pantalla lo asigna.

## 2. Wizard de creación (`/pozos/nuevo/`)

SPA con 4 pasos (`pozos/wizard.html`, `_paso1..4`, `pozos.js`). Cada paso hace `POST` a su API.

### Paso 1 — Datos básicos (`api/pozos/paso1/`)

| Campo | Regla |
|---|---|
| Nombre del pozo | Obligatorio y **único** |
| Pozo plantilla (opcional) | Solo pozos **ACTIVOS**. Al elegirlo se copian su configuración (unidades, moneda, impuestos, ecuaciones de sólidos), sus unidades personalizadas, sus categorías de pérdida, sus tanques y tipos de tanque y sus productos, equipos y mallas activos con precios |

Al crear el borrador también se siembra el catálogo estándar de **distribución de tiempo** (20 actividades).

### Paso 2 — Sistema de unidades (`paso2/`)

Opciones: Standard Oilfield, Standard 1 (lb/ft³), Standard 2 (m), Standard 3 (m, m/min), SI Métrico, Métrico 1 a 5 y **Personalizado**.
Con *Personalizado* se elige la unidad de 12 propiedades: profundidad, hoyo/tubería, volumen, caudal, boquilla, velocidad, presión, factor K, peso del fluido, viscosidad plástica, punto cedente/geles y velocidad de chorro. Cada una se guarda como fila `PropiedadUnidadPozo` y se valida contra su lista de unidades permitidas.

> ⚠ Los cálculos del sistema (geometría, hidráulica, volumetría) trabajan **en unidades de campo estándar** (ft, in, bbl, gpm, lb/gal, psi). El sistema de unidades elegido se guarda y se muestra, pero **no convierte** los valores (ver [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md)).

### Paso 3 — Financiero y pérdidas (`paso3/`)

| Campo | Regla / valores |
|---|---|
| Moneda | Selector de 18 monedas comunes (USD, VES, EUR, COP, MXN, BRL…); por defecto `USD` |
| Decimales de moneda | 0 a 4 |
| Tasa de impuesto (%) | 0 a 100 |
| Ecuación de sólidos base agua / base aceite | Solo `API` (desde el 02-oct-2026) |
| Tipo de categorías de pérdida | Estándar (valor interno `MI`), UK, Hydro, Statoil, IFE, Completion Fluids o **Personalizado** (en ese caso se editan las filas código/descripción/tipo SUPERFICIE o SUBSUELO) |

### Paso 4 — Resumen y confirmación (`confirmar/`)

Muestra el resumen. Al confirmar se ejecuta `Pozo.activar()`: **bloquea las unidades** (`unidades_bloqueadas=True`) y pasa el pozo a **ACTIVO**.

## 3. Fecha inicial (antes "Spud Date") (`/pozos/<id>/spud-date/`)

Aparece **una sola vez**, la primera vez que se abre un pozo recién activado.

| Campo | Regla |
|---|---|
| Fecha de primera captura | Obligatoria. **Inmutable** después |
| Tipo de fluido inicial | Base Agua, Base Agua (CaCl2), Base Aceite, Base Sintética, Fluidos de Completación. Obligatorio. **Inmutable** |
| Con tratamiento y disposición | Casilla; se puede cambiar después en Configuración General |
| N° de control LOGIT | Opcional |

Si se intenta confirmar de nuevo, responde: *"Esta pantalla ya fue confirmada para este pozo y no se puede repetir."*

## 4. Pantalla principal del pozo (`/pozos/<id>/`)

Es el equivalente al *Project Main Screen* de ONE-TRAX. Muestra tarjetas con su estado (Listo/Pendiente o cantidad de registros):

| Tarjeta | URL | Qué configura |
|---|---|---|
| 📋 Información General del Pozo | `well-header/` | Datos del pozo y códigos de mercadeo |
| 🧾 Configuración General | `general-setup/` | Moneda (y segunda moneda de cobro), impuesto, hidráulica, ecuaciones, almacenes y actividades de tiempo |
| 🛢️ Intervalos de Revestimiento (Costo) | `casing-intervals/` | Revestidores e intervalos de costo |
| 📉 Configuración de Pérdidas | `loss-setup/` | Categorías de pérdida de fluido |
| 🧰 Productos / Equipos / Mallas Activos | `active-items/` | Qué productos, equipos y mallas se usan en el pozo, con sus precios |
| 📊 Configuración de Benchmark | `benchmark-setup/` | Parámetros a vigilar y sus objetivos |
| 🪣 Información de Tanques | `pits/` | Tanques y tipos de tanque |
| ⚙️ Config. Propiedades de Equipo | `equipment-properties-setup/` | Propiedades a registrar por tipo de equipo |
| 💧 **Fluidos de Perforación y Equipos** | `drilling-fluids-equipment/` | **Entrada al reporte diario** (sección "Módulos Smart Mud") |
| 📑 Reporte Final del Pozo | `reporte-final/` | Recap en Excel o PDF |

**Orden (02-oct-2026):** Configuración General va justo después de Información General, a pedido de AOS (primero los datos del pozo, luego unidades y moneda).

**Eliminar pozo (02-oct-2026):** botón rojo en el encabezado. Abre una ventana que exige escribir el nombre exacto del pozo; llama a `api_pozo_eliminar`, que dentro de una transacción devuelve al inventario general lo consumido por cada reporte (`devolver_stock_reporte`) y borra el pozo. JS: `static/operaciones/js/pozo_main.js`.

Las tarjetas "Próximamente" ya no se muestran.

### 4.1 Información General del Pozo (Well Header) — 2 pestañas

**Pestaña 1: Información del pozo.** Operador, campo/área, descripción, ubicación, almacén, contratista, taladro, **coordinador de fluido** e **ingenieros de fluido 1 y 2** (campos internos `project_engineer`, `ingeniero_miswaco_1/2`), fechas (inicial, TD, fin), profundidad total, TVD, desplazamiento horizontal, temperaturas (superficie, gradiente °F/100 ft, máxima), días, costo total y comentarios.

- **Offshore**: si se marca, **exige** Air Gap, Water Depth y Sea Floor Temp.
- **Riser**: solo para offshore. Exige el **ID del riser**. Si no se da la longitud, se asume **Air Gap + Water Depth**, y si ambos son 0, lo pide.
- El **gradiente de temperatura** y la temperatura de superficie se usan en la hidráulica de la 5ª edición (temperatura anular).

**Pestaña 2: Códigos de mercadeo.** Tipo de lodo principal, tipo de pozo, tipo de contrato y tipo de fluido de completación (código + descripción).

### 4.2 Intervalos de Revestimiento (Costo)

Una fila por intervalo. Campos: número, **estado** (abierto/cerrado), tipo (Conductor, Superficie, Intermedio, Producción, Liner, Casing, Hoyo abierto, Side Track), OD/ID del revestidor, diámetro de hoyo, profundidad MD y TVD, tope del liner, densidad máxima, BHT máx., ángulo máx., gradiente de fractura, días (reales y planeados), longitud planeada, costos (real y planeado), tipos de fluido, observaciones y comentarios del recap (máx. 10.000 caracteres).

Se usan para:
- **Pestaña 4**: el perfil de revestidores define el diámetro que confina el fluido a cada profundidad.
- **Asignar el intervalo de costo** a cada reporte y comparar planeado contra real.
- **Benchmark**: los objetivos pueden ser por intervalo.

**Abierto / cerrado (02-oct-2026).** Un intervalo se **cierra** cuando se baja el revestidor (botón *Cerrar intervalo*; exige tipo y profundidad guardados). **No se puede crear el siguiente mientras haya uno abierto**: el botón *+ Nuevo* se desactiva con un aviso y el servidor también lo rechaza. *Reabrir intervalo* solo funciona con el último. El campo `cerrado` no lo toca el formulario de edición. Pedido de AOS para no abrir por error el intervalo 2 mientras se perfora el 1.

### 4.3 Configuración de Pérdidas

Categorías de pérdida (código, descripción, SUPERFICIE/SUBSUELO). Si el pozo no trae categorías, se siembran las **15 estándar**: Zarandas, Otros Sólidos, Centrífuga, Viajes, Evaporación, Retornado, Detrás del revestimiento / en el hoyo, Perdido en formación, Cajas de recortes, Barridos (piso marino), Descargado, Limpiador de lodo, Líneas de superficie, Interfase y Unidad de filtración.
Los códigos no pueden repetirse. En la pestaña 8, ⚙ *Pérdidas del reporte* elige **cuáles 10** se imprimen en el reporte diario.

### 4.4 Productos / Equipos / Mallas Activos — 3 pestañas

Cada lista toma sus elementos de un **catálogo maestro global** y les agrega los datos propios del pozo. **Doble clic** en una fila del catálogo la pasa a la lista activa (productos y mallas no se duplican; equipos sí, porque puede haber varias unidades):

| Lista | Datos del pozo |
|---|---|
| **Productos activos** | Abreviatura, tamaño de la unidad (`unit_size`), **unidad**, empaque, **precio**, gravedad específica, ¿calcular concentración?, ¿producto propio?, grupo, **código de costo diario (1-4)**, códigos WMGT/CF |
| **Equipos activos** | **N° de serie** (obligatorio), descripción, **tarifa de renta** y **tarifa standby** |
| **Mallas activas** | **Precio** y **% de descuento** (el precio neto se usa al instalar mallas nuevas) |

> **Importante sobre productos:**
> - La **unidad** decide cómo se comporta el producto en la pestaña 8. Con unidad de peso (lb, kg, t), el producto aporta volumen al lodo. Con unidad de volumen (bbl, gal, l), no aporta volumen químico. **Con la unidad vacía, se trata como un SERVICIO**: solo genera costo y no lleva existencias (ejemplo: días de ingeniero).
> - El **código de costo diario** reparte el costo: 1 = Químicos, 2 = Ingeniero de fluidos, 3 = Ingeniero de control de sólidos, 4 = Ingeniero IFE. *(Pendiente confirmar con AOS.)*
> - La lista se guarda **borrando y recreando** filas (ver [02 § C](02_ARQUITECTURA.md)).

### 4.5 Configuración de Benchmark

1. **Definiciones**: se eligen parámetros del catálogo maestro (por ejemplo Mud Weight (WBM), PV, YP (OBM)).
2. **Objetivos (Target Entry)**: para cada parámetro y cada sección (**pozo completo** o un **intervalo**), un valor, un mínimo o un máximo.

La evaluación contra los chequeos de lodo se ve en la pestaña 8 → *Evaluación de benchmark* (ver [12](12_MODULOS_OPCIONALES.md)).

### 4.6 Información de Tanques — 2 bloques

> En pantalla dice **tanque**; en el código y la base sigue siendo `Fosa` / `TipoFosa`.

- **Tanques**: número, descripción y capacidad (bbl). El nombre es descriptivo: el **uso del día** (activa, reserva…) se elige en la volumetría de la pestaña 8.
- **Tipos de tanque**: se siembran 7 estándar: 0 Vacía, 1 **Activa**, 2 **Reserva**, 3 **Premix**, 4 Espaciador, 5 Píldora, 6 Rompedor. Se pueden agregar otros (Base Oil, Brine…). Para el balance de volumetría, el código 1 cuenta como sistema **activo**, el 2 como **reserva**, el 3 como **premezcla** y el resto como **otras**.

### 4.7 Configuración de Propiedades de Equipo

Por **tipo de equipo** (Centrífuga, Limpiador de lodo, Zaranda, Secador de recortes, Sistema de vacío, Contenedor de recortes, Otros):
- se marcan las propiedades estándar del catálogo maestro que se quieren registrar,
- se agregan propiedades extra de texto libre,
- para la centrífuga, se eligen las unidades de caudal (gal/min, bbl/min, bbl/hr, L/min, m³/hr) y de masa (Ton, lb, kg, bbl).

Estas propiedades aparecen como columnas adicionales en *Uso de equipos* de la pestaña 6.

### 4.8 Configuración General

| Bloque | Contenido |
|---|---|
| **Moneda** | Moneda del pozo (selector con 18 monedas comunes; cambiarla solo cambia el símbolo, no convierte montos) |
| **Segunda moneda (opcional)** | Moneda, **tasa de cambio** (unidades por 1 de la moneda del pozo) y **% cobrado** en ella. La pantalla de costos del reporte muestra el reparto (día y acumulado). El Excel todavía no lo muestra |
| **Setup** | Tasa de impuesto, ¿con tratamiento y disposición?, **¿usar API 13D 5ª edición en hidráulica?**, ecuaciones de sólidos (solo **API** desde el 02-oct) |
| **Códigos de almacén** | Código y nombre de cada almacén o bodega. No trae datos precargados. Se usan en los tickets de mallas y productos |
| **Distribución de tiempo** | Catálogo de actividades del taladro (número, descripción, tipo DF, CF o DF/CF). Trae 20 estándar precargadas. La pestaña 7 usa las de tipo DF y DF/CF |

## 5. Catálogos maestros globales (`/catalogos-maestros/`)

Compartidos por **todos** los pozos. La pantalla tiene 5 pestañas con buscador y vista dividida (tabla a la izquierda, formulario a la derecha):

| Catálogo | Campos |
|---|---|
| ⚙️ **Equipos** | Código (único), nombre, tipo de equipo, **posiciones de malla (0 a 12)**: con 0, el equipo no lleva mallas y no aparece en las transacciones de mallas |
| ▦ **Mallas de zaranda** | Código (único), descripción, mesh |
| 📋 **Propiedades de equipo** | Tipo de equipo, descripción, unidad, orden |
| 📊 **Parámetros de benchmark** | Grupo, descripción, unidad, tipo de fluido (WBM, OBM, Ambos, N/A), tipo de dato (numérico, mín/máx, texto) |
| 🔩 **Componentes de sarta** | Código, descripción, tipo (Mecha, Motor, Drill collar, Heavy weight, Drill pipe, Estabilizador, Crossover, Revestidor, Otros), OD, ID y **junta** (OD, ID y largo de la junta en pulgadas, largo del tramo en pies, por defecto 31 ft) |

Los componentes de sarta alimentan la sarta de la pestaña 4: se escogen de la lista y se copian sus diámetros.

El **catálogo de productos** es el del módulo **Inventario** (ver [15](15_INVENTARIO_ALMACEN.md)).
