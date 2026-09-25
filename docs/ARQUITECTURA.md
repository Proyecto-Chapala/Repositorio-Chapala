# Arquitectura

## Visión general

El proyecto es **un solo proyecto Django (`chapala`) con una sola app instalada: `operaciones`**. Esa app contiene los dos sistemas:

- **Inventario** de productos químicos (modelo `Producto`, pantalla `/`).
- **Reportes diarios estilo ONE-TRAX** (pozos, configuración y reporte diario de 8 pestañas).

Los dos sistemas comparten el catálogo `Producto`: es el "Master Product List" que el pozo usa para armar su lista de productos activos.

```
Navegador (HTML + JavaScript sin frameworks)
        │  fetch() JSON
        ▼
Vistas Django (operaciones/views*.py)  ──►  Motores de cálculo puros (sin Django)
        │                                   geometria_pozo.py · hidraulica.py
        │                                   control_solidos.py · volumetria.py
        ▼
Modelos (operaciones/models*.py)  ──►  PostgreSQL (o SQLite)
```

### Historia: de dos apps a una

Al principio había dos apps separadas, que siguen guardadas en `_legacy/`:

| App antigua | Qué hacía | Estado |
|---|---|---|
| `_legacy/mychapala` | Inventario + reporte diario de almacén (pestañas General, Inventario, Uso; planilla impresa AOS) | **No instalada.** Su `Producto` pasó a `operaciones`. El reporte de almacén y los registros de "Uso" no se migraron. |
| `_legacy/reportes` | Primera versión de los reportes ONE-TRAX (migraciones 0001-0008) | **No instalada.** Reescrita dentro de `operaciones`. |

`INSTALLED_APPS` solo tiene `operaciones.apps.OperacionesConfig`. La carpeta `reportes/` de la raíz solo contiene `__pycache__` de la versión vieja y se puede borrar.

---

## Estructura de carpetas

```
Proyecto CHAPALA/
├── chapala/                  Configuración del proyecto Django
│   ├── settings.py           Lee .env; PostgreSQL o SQLite; idioma es-ve; zona America/Caracas
│   └── urls.py               /admin/ y todo lo demás → operaciones.urls
├── operaciones/              LA app
│   ├── models.py             Producto, Pozo y toda la configuración del pozo; al final importa los demás models_*
│   ├── models_daily_reports.py   ReporteDiario y pestañas 1 a 5 y 7
│   ├── models_control_solidos.py Pestaña 6 (mallas, tickets, uso de equipos)
│   ├── models_inventario.py      Pestaña 8 (pérdidas, volumetría, inventario del pozo, tickets de productos)
│   ├── models_opcionales.py      IFE, análisis de sólidos, retención, eventos no programados
│   ├── views.py              Inventario, wizard del pozo, pantallas de configuración, catálogos maestros
│   ├── views_daily_reports.py    Hub y detalle del reporte, pestañas 1 a 5 y 7, Excel, costos
│   ├── views_control_solidos.py  Pestaña 6
│   ├── views_inventario.py       Pestaña 8 (volumetría) y resumen de costos
│   ├── views_hidraulica.py       Pestaña 8 (hidráulica)
│   ├── views_opcionales.py       Módulos opcionales y evaluación de benchmark
│   ├── geometria_pozo.py     Motor: perfil del pozo y volúmenes (pestaña 4)
│   ├── hidraulica.py         Motor: API RP 13D 4ª y 5ª edición
│   ├── control_solidos.py    Motor: inventario de mallas y rendimiento de equipos
│   ├── volumetria.py         Motor: volumetría, inventario de productos, costos y concentraciones
│   ├── reporte_excel.py      Llena la plantilla Excel ONE-TRAX en español
│   ├── forms_pozo.py         ModelForms de validación del pozo y su configuración
│   ├── admin.py              Registro en /admin/
│   ├── plantillas/
│   │   ├── reporte_diario_onetrax.xlsx   Plantilla del Excel
│   │   └── crear_plantilla.py            Script (se corre una vez) que creó la plantilla desde el Mud Report original
│   ├── migrations/           0001 a 0022
│   ├── templates/operaciones/
│   │   ├── base.html, index.html (inventario), catalogos_maestros.html, pozos_list.html
│   │   ├── componentes/sidebar.html
│   │   ├── inventario/       Parciales de la pantalla de inventario
│   │   ├── pozos/            Wizard, Spud Date, pantalla principal y pantallas de configuración
│   │   └── avances_19_sep/   daily_reports_hub.html y reporte_diario_detalle.html (las 8 pestañas)
│   └── static/operaciones/
│       ├── css/              Un CSS por pantalla o pestaña
│       └── js/               Un JS por pantalla o pestaña
├── _legacy/                  Apps antiguas (no instaladas)
├── documentation/            Material de referencia: manual ONE-TRAX, Mud Report PERLA-1X, inventario físico, presentaciones
├── docs/                     Esta documentación
├── .env                      Variables de base de datos (no versionado)
├── Iniciar Sistema.bat       Arranque con doble clic
├── manage.py
└── requirements.txt
```

Archivos sobrantes que no se usan: `operaciones/admin-1.py`, `operaciones/models-1.py`, `operaciones/views-1.py` (copias viejas) y `templates/operaciones/componentes/sidebar-1.html`.

---

## Principios de diseño

Estas reglas se repiten en todo el código. Quien toque el sistema debe respetarlas.

### 1. Los resultados se calculan; no se guardan

Volúmenes, inventarios de mallas y productos, costos acumulados y concentraciones **no se guardan en la base de datos**. Se guardan solo los datos que el ingeniero captura (movimientos, tickets, medidas reales) y cada vez se **repite la historia completa del pozo en orden** para obtener el estado de cualquier día.

Ventaja: si se corrige un dato de un día viejo, todos los días siguientes se recalculan solos. Nunca hay que "recalcular" a mano, y un error no se arrastra sin que nadie lo vea.

Esto aplica a:

- Inventario de mallas (`control_solidos.simular`)
- Volumetría e inventario de productos del pozo (`volumetria.simular`)
- Geometría del pozo (`geometria_pozo.calcular_geometria`)
- Hidráulica (`hidraulica.calcular`)

### 2. Se valida toda la línea de tiempo antes de confirmar

Cuando el usuario guarda un movimiento (malla, ticket, transacción de volumen), la vista:

1. abre una transacción de base de datos,
2. guarda el cambio,
3. simula **todo el pozo hasta el último reporte**,
4. si algún día queda imposible (stock negativo, posición ocupada, fosa sin tipo), **deshace el guardado** y devuelve un mensaje que dice qué día y qué producto o malla.

Así un cambio en un día viejo no puede dejar sin stock a un día posterior.

### 3. Las listas del pozo se guardan "borrando y recreando"

Las pantallas de configuración tipo grilla (fosas, tipos de fosa, categorías de pérdida, almacenes, distribución de tiempo, productos, equipos y mallas activos, propiedades de equipo, benchmark) guardan **reemplazando todas las filas**: borran las del pozo y crean las nuevas en bloque.

Consecuencia: **los datos diarios no apuntan a esas filas con llave foránea**, porque la llave se perdería (o borraría la historia) en cada edición. En su lugar guardan:

- el **número o código** del elemento (número de fosa, código de categoría de pérdida, número de actividad, número de serie del equipo), y
- una **copia del texto** (descripción de la fosa, del tipo de pérdida, del equipo).

Cuando sí hace falta llave foránea se apunta al **catálogo maestro global** (`Producto`, `Equipo`, `MallaZaranda`, `ComponenteSarta`), que no se recrea.

### 4. Los precios se copian al momento del uso

El precio de una malla instalada, el de un producto agregado y la tarifa de un equipo se copian en el movimiento. Si después cambia el precio en el pozo, el costo de los días pasados no cambia.

### 5. Solo se deshace el último movimiento

Transacciones de mallas y de volumen llevan un número de `secuencia` que crece por pozo. Solo el último movimiento del pozo se puede deshacer ("Deshacer último", igual que *Undo Last Transaction* de ONE-TRAX), y solo desde el reporte al que pertenece.

### 6. Motores de cálculo sin Django

`geometria_pozo.py`, `hidraulica.py`, `control_solidos.py` y `volumetria.py` reciben diccionarios y devuelven diccionarios. No importan Django. Se pueden probar solos y replicar en JavaScript (por ejemplo, `reporte_control_solidos.js` tiene `csCalcularRendimiento`, espejo del cálculo en Python).

### 7. Herencia del día anterior

Al abrir un reporte por primera vez, varias pestañas copian datos del reporte anterior: bombas, mecha y boquillas (pestaña 2), chequeos de lodo (pestaña 3), especificación de lodo (pestaña 5), tipos de fosa (pestaña 8). La sarta (pestaña 4) se hereda con un botón. Los textos de comentarios **no** se heredan.

---

## Convenciones del código

| Tema | Convención |
|---|---|
| Idioma | Código, mensajes y comentarios en español. Nombres de ONE-TRAX en inglés entre paréntesis cuando ayuda. |
| Finales de línea | **CRLF** (Windows) en todos los archivos. |
| Frontend | HTML de Django + JavaScript sin frameworks + CSS propio. **Un CSS y un JS por pantalla o por pestaña** (`reporte_tiempo.js`, `reporte_control_solidos.js`, `reporte_inventario.js`, `reporte_hidraulica.js`, `reporte_opcionales.js`...). Las pestañas 1 a 5 viven dentro de `reporte_diario_detalle.html`. |
| Caché del navegador | Los CSS/JS se enlazan con `?v=<versión>`. `views._version_estaticos()` calcula la versión con la **fecha de modificación de los propios archivos**: el navegador descarga el archivo nuevo apenas cambia y usa la caché el resto del tiempo. Lo usan el reporte diario y Catálogos Maestros. |
| APIs | JSON. Las del inventario y el wizard responden `{"success": true/false, ...}`; las del reporte diario responden `{"ok": true/false, ...}`. Errores con `"error": "mensaje para el usuario"` y HTTP 400. |
| Números | Se acepta coma decimal en horas y volúmenes (`"20,5"`). Vacío = sin dato. |
| Fechas | ISO `AAAA-MM-DD` en la API; `dd/mm/aaaa` en mensajes y Excel. |
| Unidades internas | Unidades de campo: ft, in, bbl, gal/min, lb/gal, psi. El sistema de unidades del pozo se guarda pero los cálculos trabajan en unidades de campo. |

---

## Flujo de datos del reporte diario

```
Pestaña 1 (profundidad, mecha) ─┐
Pestaña 2 (bombas, mecha, boquillas) ─┼─► Pestaña 4: geometría y volumen del hoyo
Intervalos de revestimiento + riser ─┘            │
                                                   ├─► Pestaña 6: volumen perforado → rendimiento de equipos
                                                   ├─► Pestaña 8: volumen de fluido en el hoyo → volumetría
Pestaña 3 (reología, peso) ───────────────────────┴─► Pestaña 8: hidráulica
Pestaña 6 (mallas, renta de equipos) ─┐
Pestaña 8 (químicos, servicios) ──────┴─► Resumen de costos (pestaña 1) y Excel
```

---

## Dónde está cada cosa (referencia rápida)

| Necesito cambiar... | Archivo |
|---|---|
| Una fórmula de volumen del hoyo | `geometria_pozo.py` |
| Hidráulica, ECD, pérdidas de presión | `hidraulica.py` y `views_hidraulica.py` |
| Balance de sólidos (retorta) | `ReporteDiarioMudCheck.calcular_solids_analysis_*` en `models_daily_reports.py` |
| Reglas de inventario de mallas | `control_solidos.py` |
| Reglas de volumetría o inventario del pozo | `volumetria.py` |
| Costos del día | `views_inventario.resumen_costos` |
| Qué sale en el Excel | `reporte_excel.py` |
| Catálogos que se siembran al crear un pozo | `CATEGORIAS_ESTANDAR`, `TIPOS_ESTANDAR`, `TIPOS_EJEMPLO` en los modelos |
| Una ruta | `operaciones/urls.py` |
