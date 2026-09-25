# Creación y configuración del pozo

Un **pozo** es la unidad de trabajo del sistema (equivale al archivo `.MDB` de ONE-TRAX). Todo lo diario cuelga de él. Antes de escribir el primer reporte diario hay que pasar por tres etapas:

1. **Wizard de 4 pasos** → el pozo queda ACTIVO.
2. **Spud Date** (pantalla única) → queda lista la captura diaria.
3. **Pantallas de configuración** desde la pantalla principal del pozo.

```
/pozos/nuevo/  ──► paso 1 ─► paso 2 ─► paso 3 ─► paso 4 "Crear Pozo"
                   (BORRADOR, se autoguarda en cada paso)        │
                                                                 ▼ estado = ACTIVO, unidades bloqueadas
                                              /pozos/<id>/spud-date/  (una sola vez)
                                                                 │
                                                                 ▼
                                              /pozos/<id>/  Pantalla principal del pozo
```

Código: `views.py` (funciones `pozo_wizard_view`, `api_pozo_paso1..3`, `api_pozo_confirmar`, `api_pozo_spud_date`, `pozo_main_view`), `forms_pozo.py`, `templates/operaciones/pozos/`, `static/operaciones/js/pozos.js` y `spud_date.js`.

---

## Wizard

Mientras el wizard está en curso el pozo existe en estado **BORRADOR** y se guarda en cada paso ("Guardar y Continuar"). Si se cierra la ventana, se retoma en `/pozos/<id>/continuar/`. `paso_wizard_actual` recuerda hasta dónde se llegó; nunca retrocede.

Un pozo en BORRADOR no abre su pantalla principal ni Spud Date: el sistema redirige al wizard.

### Paso 1 — Datos básicos

| Campo | Regla |
|---|---|
| Nombre del pozo | Obligatorio. Único sin distinguir mayúsculas |
| Usar un pozo anterior como plantilla | Opcional. Solo pozos **ACTIVOS** |

Al guardar el paso 1 el sistema **siembra o clona** los catálogos del pozo:

| Qué | Con plantilla | Sin plantilla |
|---|---|---|
| Unidades, moneda, impuesto, ecuaciones, tipo de categorías de pérdida | Se copian de la plantilla | Defaults |
| Unidades personalizadas | Se copian (si la plantilla es CUSTOM) | — |
| Categorías de pérdida | Se copian de la plantilla | Se siembran las **15 estándar** |
| Tipos de fosa | Se copian de la plantilla | Se siembran los **7 estándar** |
| Fosas | Se copian de la plantilla | Ninguna |
| Productos, equipos y mallas activos (con precios) | Se copian de la plantilla (`clonar_listas_activas`) | Ninguno |
| Distribución de tiempo | Se siembran las **20 actividades estándar** si el pozo no tiene | Igual |

Categorías de pérdida estándar (código, descripción, tipo): 1 Zarandas, 2 Otros Sólidos, 3 Centrífuga, 4 Viajes, 5 Evaporación, 6 Retornado (superficie); 7 Detrás del Revestimiento / En el Hoyo, 8 Perdido en Formación (subsuelo); 9 Cajas de Recortes (superficie); 10 Barridos (Piso Marino) (subsuelo); 11 Descargado, 12 Limpiador de Lodo, 13 Líneas de Superficie, 14 Interfase, 15 Unidad de Filtración (superficie).

Tipos de fosa estándar: 0 Vacía, 1 Activa, 2 Reserva, 3 Premix, 4 Espaciador, 5 Píldora, 6 Rompedor.

### Paso 2 — Sistema de unidades

Se elige uno de los sistemas predefinidos (Standard Oilfield, Standard 1-3, SI Métrico, Métrico 1-5) o **Personalizado**. En personalizado se elige una unidad para cada una de 16 propiedades (profundidad, diámetro de hoyo/tubería, volumen, caudal, boquilla, velocidad, presión, factor K, peso de fluido, viscosidad plástica, cedencia y geles, velocidad de chorro, concentración, fuerza, temperatura, espesor de revoque). El servidor valida cada unidad contra `PropiedadUnidadPozo.OPCIONES_UNIDAD`.

Después de activar el pozo **no se puede cambiar** (`unidades_bloqueadas`).

> Hoy la elección se guarda pero **no cambia los cálculos ni las pantallas**: todo trabaja en unidades de campo (ft, in, bbl, gpm, lb/gal, psi).

### Paso 3 — Financiero

| Campo | Regla |
|---|---|
| Símbolo de moneda | Obligatorio (USD por defecto). **Fijo** después de activar |
| Decimales de moneda | 0 a 4 |
| Tasa de impuesto (%) | 0 a 100. Editable después en Configuración General |
| Ecuación de sólidos base agua / base aceite | M-I o API |
| Categorías de pérdida | M-I, UK, Hydro, Statoil, IFE, Completion Fluids o Personalizado. En Personalizado se escriben las filas (código, descripción, superficie/subsuelo) y reemplazan a las sembradas |

### Paso 4 — Confirmar

Muestra el resumen. **Crear Pozo** llama `api_pozo_confirmar`, que exige haber pasado los 3 pasos anteriores y ejecuta `Pozo.activar()`: `estado = ACTIVO`, `unidades_bloqueadas = True`.

---

## Spud Date (fecha de inicio de captura)

Se muestra la primera vez que se abre un pozo ACTIVO. Mientras no se confirme, la pantalla principal del pozo redirige aquí.

| Campo | Regla |
|---|---|
| Primera fecha de este archivo | Obligatoria. Puede ser anterior al spud real. **Inmutable** |
| Tipo de fluido para el primer chequeo | Obligatorio. **Inmutable** |
| Con tratamiento y disposición de desechos | Opcional; se puede cambiar después en Configuración General |
| Número de control Log-It | Opcional |

Al confirmar, `spud_date_completado = True` y la pantalla pasa a modo solo lectura para siempre.

> La fecha de Spud que usa el reporte diario (para sugerir la fecha del primer reporte y calcular días) es otra: `WellHeaderInfo.spud_date`, que se captura en Información General del Pozo.

---

## Pantalla principal del pozo

`/pozos/<id>/` muestra el nombre, el sistema de unidades, la moneda, el estado y dos grupos de tarjetas.

### Información del pozo

| Tarjeta | Ruta | Qué se configura |
|---|---|---|
| Información General del Pozo | `well-header/` | Dos pestañas: **Well Information** (offshore, riser, operador, campo, taladro, ingenieros, spud, TD, temperatura de superficie y gradiente, datos de cierre) y **Marketing Codes**. Marca "Listo" cuando se guardó al menos una vez |
| Intervalos de Revestimiento (Costo) | `casing-intervals/` | Un intervalo por revestidor: tipo, OD/ID, diámetro de hoyo, zapata, TVD, tope de liner, costos y días planeados y reales |
| Configuración de Pérdidas | `loss-setup/` | Categorías de pérdida (código, descripción, superficie/subsuelo) |
| Productos / Equipos / Mallas Activos | `active-items/` | Tres pestañas: productos, renta de equipos y mallas. Se eligen del catálogo maestro y se les pone precio y datos del pozo |
| Registro Direccional del Pozo | — | Marcado "Próximamente" (las estaciones se capturan desde el reporte) |
| Configuración de Benchmark | `benchmark-setup/` | Parámetros a monitorear y valores objetivo por pozo completo o por intervalo |
| Información de Fosas | `pits/` | Fosas y tanques (número, descripción, capacidad) y tipos de fosa |
| Configuración de Propiedades de Equipo | `equipment-properties-setup/` | Qué propiedades se capturan cada día por tipo de equipo; unidades de la centrífuga |
| Configuración General | `general-setup/` | Tasa de impuesto, tratamiento y disposición, **hidráulica API 5ª edición**, ecuaciones de sólidos, almacenes y distribución de tiempo |
| Eventos No Programados, Resumen de Costos | — | "Próximamente" como pantallas del pozo |

### Módulos ONE-TRAX

| Tarjeta | Estado |
|---|---|
| **Fluidos de Perforación y Equipos** | Activo: lleva al historial de reportes diarios |
| Módulo RDF, Fluidos de Completación, Tratamiento y Disposición de Desechos | Próximamente |

### Reglas importantes de la configuración

- **Offshore**: si se marca, son obligatorios Air Gap, Water Depth y Sea Floor Temp.
- **Riser**: solo en offshore. Exige el diámetro interno. Si no se da la longitud, se toma Air Gap + Water Depth. El riser se vuelve el primer tramo del perfil del pozo en la pestaña 4.
- **Intervalos**: el número se asigna solo (el siguiente libre). Un intervalo con **tope de liner** mayor que 0 se trata como liner (no llega a superficie).
- **Equipos activos**: el número de serie es obligatorio y único en el pozo. Es la identidad del equipo en los reportes diarios.
- **Productos activos**: si la **unidad** queda vacía, el producto es un **servicio** (sin existencias, solo costo). El **código de costo diario** decide la categoría de costo: 1 Químicos, 2 Ingeniero de fluidos, 3 Ingeniero de control de sólidos, 4 Ingeniero IFE.
- Todas estas grillas se guardan **reemplazando la lista completa**.

---

## Catálogos maestros

`/catalogos-maestros/` (barra lateral → 🗂️ Catálogos Maestros). Son **globales**: sirven a todos los pozos. Cinco pestañas con tabla a la izquierda y formulario a la derecha:

| Pestaña | Modelo | Notas |
|---|---|---|
| ⚙️ Equipos | `Equipo` | Código, nombre oficial, tipo, **posiciones de malla** (0-12). Sin posiciones, el equipo no aparece en el control de mallas |
| ▦ Mallas de Zaranda | `MallaZaranda` | Código, descripción, mesh |
| 📋 Propiedades de Equipo | `PropiedadEquipoTipo` | Propiedades disponibles por tipo de equipo |
| 📊 Parámetros de Benchmark | `ParametroBenchmark` | Grupo, descripción, unidad, tipo de fluido, tipo de dato |
| 🔩 Componentes de Sarta | `ComponenteSarta` | OD, ID, junta (OD, ID, largo) y largo de tramo (31 ft por defecto) |

Los contadores de las pestañas se calculan en el servidor. No se puede borrar un elemento que algún pozo esté usando.

Los productos no están aquí: su catálogo maestro es la pantalla de **Inventario**.
