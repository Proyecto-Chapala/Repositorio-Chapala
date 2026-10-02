# 02 — Arquitectura

> Nombre del sistema: **Smart Mud** (desde el 02-oct-2026). El proyecto Django sigue llamándose `chapala` y la app `operaciones`; no se renombraron para no romper migraciones, rutas ni la base de datos.

## Visión general

CHAPALA es un proyecto Django con **una sola aplicación de negocio: `operaciones`**. El frontend no usa frameworks. Django sirve la página HTML con los datos iniciales y, desde ahí, el JavaScript de cada pantalla llama a una **API JSON** del mismo servidor para leer y guardar.

```
Navegador (HTML + JS vanilla + CSS por pantalla)
      │  fetch JSON  (GET = leer, POST = guardar)
      ▼
Django — operaciones/urls.py  →  vistas (views*.py)
      │                               │
      │                               ├─ Modelos (models*.py)  ──►  PostgreSQL / SQLite
      │                               │
      │                               └─ Motores de cálculo PUROS (sin Django):
      │                                     geometria_pozo.py · hidraulica.py
      │                                     control_solidos.py · volumetria.py
      ▼
reporte_excel.py  →  plantilla .xlsx de ONE-TRAX  →  descarga
recap_pozo.py     →  reporte final del pozo (Excel por código / página imprimible → PDF)
```

## Estructura de carpetas

```
Proyecto CHAPALA/
├── manage.py
├── requirements.txt
├── AGENT.md                      # orden de lectura para retomar el proyecto
├── AGENT.md                      # leer primero (asistentes y desarrolladores)
├── docs/                         # esta documentación (índice en docs/README.md)
├── empaquetado/                  # SmartMud.exe: chapala_app.py, chapala.spec, Construir EXE.bat, íconos
├── .env                          # credenciales de BD (NO versionar)
├── Iniciar Sistema.bat           # acceso directo de arranque
├── chapala/                      # proyecto Django (settings, urls raíz, wsgi/asgi)
├── operaciones/                  # ÚNICA app de negocio
│   ├── models.py                 # Pozo, configuración del pozo, catálogos maestros, Producto
│   ├── models_daily_reports.py   # ReporteDiario y pestañas 1-5 y 7
│   ├── models_control_solidos.py # pestaña 6
│   ├── models_inventario.py      # pestaña 8 (volumetría, inventario, pérdidas)
│   ├── models_opcionales.py      # IFE, muestras, eventos no programados
│   ├── licencia.py, middleware_licencia.py, views_licencia.py  # licencia de prueba del .exe
│   ├── models_recap.py           # RecapPozo (textos del reporte final)
│   ├── views.py                  # inventario de almacén, wizard, setups del pozo, catálogos
│   ├── views_daily_reports.py    # hub, reporte diario, pestañas 1-5 y 7, Excel, reporte de propiedades
│   ├── views_control_solidos.py  # API pestaña 6
│   ├── views_inventario.py       # API pestaña 8 + resumen_costos()
│   ├── views_hidraulica.py       # API hidráulica (solo lectura)
│   ├── views_opcionales.py       # API módulos opcionales + evaluación de benchmark
│   ├── views_recap.py            # reporte final del pozo
│   ├── forms_pozo.py             # formularios de validación de wizard y setups
│   ├── geometria_pozo.py         # MOTOR: perfil del pozo y volúmenes
│   ├── hidraulica.py             # MOTOR: API RP 13D 4ª y 5ª edición
│   ├── control_solidos.py        # MOTOR: inventario de mallas + rendimiento de equipos + hoyo perforado
│   ├── volumetria.py             # MOTOR: volumetría, inventario de productos, costos, concentraciones
│   ├── reporte_excel.py          # generación del Excel diario
│   ├── recap_pozo.py             # datos y Excel del reporte final
│   ├── plantillas/               # plantilla .xlsx de ONE-TRAX + script que la creó
│   ├── admin.py
│   ├── urls.py
│   ├── migrations/               # 0001 … 0027
│   ├── templates/operaciones/
│   │   ├── base.html, index.html, pozos_list.html, catalogos_maestros.html
│   │   ├── componentes/sidebar.html
│   │   ├── inventario/           # parciales del inventario de almacén
│   │   ├── pozos/                # wizard (_paso1..4), spud_date, main, setups, recap, recap_imprimible
│   │   └── avances_19_sep/       # daily_reports_hub.html, reporte_diario_detalle.html, reporte_propiedades.html
│   └── static/operaciones/
│       ├── css/                  # un CSS por pantalla/pestaña
│       ├── img/                  # logo_reporte.png (AOS, reportes), smartmud_icono.png, smartmud_logo.png, favicon.png
│       └── js/                   # un JS por pantalla/pestaña
├── seed_data.py                  # carga el catálogo AOS de productos (seed_propiedades.py es obsoleto)
├── scripts/                      # generar_clave_licencia.py, seed_pozo_prueba.py
└── proyecto chapala - claude/          # copias de trabajo antiguas (no se usan)
```

### Archivos que NO forman parte del sistema

Estos archivos no los importa ninguna parte del código. Son respaldos que conviene mover fuera del proyecto o borrar después de confirmarlo:

- `operaciones/models-1.py`, `operaciones/views-1.py`, `operaciones/admin-1.py`
- `operaciones/templates/operaciones/componentes/sidebar-1.html`
- La carpeta `proyecto chapala - claude/` (versiones viejas del wizard y de la memoria del proyecto)
- `RESUMEN_AVANCE.txt`: describe una versión anterior con la app `mychapala` y los modelos `ReporteDiario`/`RegistroUso` de almacén, que ya no existen.

## Capas

### 1. Modelos (`models*.py`)

Están divididos por área. `models.py` importa al final los demás para que Django los registre. El detalle está en [03_MODELO_DATOS.md](03_MODELO_DATOS.md).

### 2. Vistas

Hay dos tipos:

- **Vistas de página** (`*_view`). Hacen `render()` de una plantilla con el contexto mínimo: el pozo y el reporte.
- **Vistas API** (`api_*`). Reciben y devuelven JSON. Convención de respuesta:

  ```json
  { "ok": true,  ...datos... }
  { "ok": false, "error": "Mensaje en español para el usuario" }   // HTTP 400/404
  ```

  Las vistas de `views.py` usan la clave `success` en lugar de `ok` (`{"success": false, "error": "…", "errores_filas": […]}`). Si unificas, cambia al mismo tiempo el JS que las consume.

  Las de escritura llevan `@csrf_exempt` y `@require_http_methods(["POST"])`. Las de lectura llevan `@require_http_methods(["GET"])`.

### 3. Motores de cálculo (funciones puras)

Son las piezas más importantes del sistema. **No importan Django**: reciben diccionarios y listas, y devuelven diccionarios. Por eso se pueden probar aislados.

| Motor | Qué calcula | Doc |
|---|---|---|
| `geometria_pozo.py` | Perfil de confinamiento (riser, revestidores, liner, hoyo abierto), ubicación de la sarta, volúmenes anular/sarta/bajo mecha, desplazamiento | [11](11_CALCULOS_INGENIERIA.md) |
| `hidraulica.py` | Reología, pérdidas de presión por sección, ECD, velocidad crítica, mecha (HHP, HSI, impacto) | [10](10_HIDRAULICA_API13D.md) |
| `control_solidos.py` | Repite tickets y transacciones de mallas → stock nuevo/usado, posiciones, costo; rendimiento de equipos; **hoyo perforado** (side track y piloto) | [07](07_PESTANA_6_CONTROL_SOLIDOS.md), [20](20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md) |
| `volumetria.py` | Repite movimientos de fluidos y productos → volúmenes por fosa, balance "no contabilizado", inventario, costos, concentraciones | [09](09_PESTANA_8_VOLUMETRIA_INVENTARIO.md) |

### 4. Frontend

- `base.html` define el esqueleto con la barra lateral (`componentes/sidebar.html`) y carga `app.js`, que maneja el colapso del sidebar y las notificaciones *toast*.
- Cada pantalla tiene **su propio CSS y JS** (`pozos.js`, `pits.js`, `general_setup.js`…).
- El **reporte diario** (`reporte_diario_detalle.html`, unas 5.300 líneas) contiene las pestañas 1 a 5 con su JS en línea y carga aparte los archivos de las pestañas nuevas: `reporte_tiempo.*`, `reporte_control_solidos.*`, `reporte_inventario.*`, `reporte_hidraulica.*` y `reporte_opcionales.*`.
- La plantilla define las utilidades globales `POZO_ID`, `REPORTE_ID`, `getCookie`, `showToast` y `switchTab`. `reporte_control_solidos.js` define `csEsc`, `csNum`, `csFmt`, `csDinero` y `csCambiarVista`, que usan también las pestañas 8 y los opcionales. **Por eso importa el orden de carga de los scripts.**

## Patrones de diseño que hay que conocer

### A. Estado derivado por "repetición de la línea de tiempo" (*event replay*)

La **pestaña 6 (mallas)** y la **pestaña 8 (volumetría e inventario)** **no guardan saldos**. Guardan solo los hechos: tickets recibidos o devueltos, transacciones y lo medido. Cada vez que se consulta o se escribe, el motor **repite todos los reportes del pozo en orden de fecha** y obtiene:

- existencias de cada día,
- volúmenes calculados,
- costos diarios y acumulados.

Toda escritura sigue el mismo flujo:

```python
with transaction.atomic():
    guardar_el_cambio()
    simular_todo_el_pozo()        # si algún día (incluso posterior) queda negativo o incoherente...
    # ...el motor lanza ErrorMallas / ErrorVolumetria → _Rechazo → ROLLBACK
```

Consecuencia: **no se puede dejar inventario negativo en ningún día**, ni siquiera al modificar un día viejo que afecta a días posteriores. El mensaje de error dice qué día y qué producto o malla falla.

### B. "Deshacer la última transacción"

Las transacciones de mallas (`TransaccionMalla`) y de volumetría (`TransaccionVolumen`) tienen una `secuencia` que crece **por pozo**. Solo se puede deshacer la última del pozo, y solo desde el reporte al que pertenece. Así funciona *Undo Last Transaction* en ONE-TRAX.

### C. Listas del pozo "borrar y recrear"

Las listas de configuración del pozo se guardan **en bloque**: el endpoint borra todas las filas y crea las que envía la pantalla. Aplica a `MallaActivaPozo`, `EquipoActivoPozo`, `ProductoActivoPozo`, `Fosa`, `TipoFosa`, `AlmacenCodigo`, `TipoDistribucionTiempo`, `CategoriaPerdidaItem` y las propiedades de equipo. Por eso sus `id` **cambian en cada guardado**.

**Regla**: los datos diarios **nunca** tienen llave foránea a esas listas. Guardan una referencia estable (el catálogo maestro, el número de fosa, el código de pérdida o el número de serie del equipo) **más una copia del texto**. Ejemplos: `TransaccionMalla.equipo_serie` + `equipo_descripcion`, `VolumenFosaDia.fosa_numero` + `fosa_descripcion`, `UsoEquipoDia.tipo_perdida_codigo` + `tipo_perdida_descripcion`.

### D. "Obtener o crear" con herencia del día anterior

Al abrir una pestaña por primera vez en un reporte, las funciones `obtener_o_crear_*` (`pumps_bits`, `mud_checks`, `comentarios`, `tiempo`) crean los registros del día. Si existe un reporte anterior, **clonan sus valores**. Si no, usan los valores por defecto de ONE-TRAX.

### E. Pozo plantilla

En el paso 1 del wizard se puede elegir un pozo ACTIVO como plantilla. Se copian **solo datos de configuración**: unidades, moneda, categorías de pérdida, fosas y tipos. Los datos operativos no se copian (`Pozo.clonar_*`).

### F. Anti-caché de estáticos

`_version_estaticos()` en `views.py` toma la fecha de modificación más reciente de los CSS/JS de las pestañas y la agrega como `?v=<timestamp>`. El navegador descarga el archivo nuevo **solo cuando cambió**. `catalogos_maestros.html` usa todavía `?v={% now 'YmdHis' %}`, que descarga en cada visita.

## Configuración (`chapala/settings.py`)

| Parámetro | Valor | Comentario |
|---|---|---|
| `INSTALLED_APPS` | contrib de Django + `operaciones.apps.OperacionesConfig` | |
| `LANGUAGE_CODE` / `TIME_ZONE` | `es-ve` / `America/Caracas` | `USE_TZ = True` |
| `DATABASES` | según `.env` (`USE_POSTGRES`) | |
| `STATIC_ROOT` | `staticfiles/` | para `collectstatic` en producción |
| `DEBUG` | `True` | ⚠ solo desarrollo |
| `ALLOWED_HOSTS` | `['*']` | ⚠ solo desarrollo |
| `SECRET_KEY` | escrita en el código | ⚠ mover al `.env` antes de producción |

Los riesgos de seguridad se detallan en [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md#d-seguridad).

## Navegación del usuario

```
Barra lateral: Pozos · Inventario · Nuevo Pozo · Catálogos Maestros
   │
   ├─ Nuevo Pozo → Wizard (4 pasos) → Spud Date (una sola vez) → Pantalla principal del pozo
   │
   └─ Pozos → Pantalla principal del pozo
                ├─ Información General (Well Header)       ├─ Información de Fosas
                ├─ Intervalos de Revestimiento (Costo)     ├─ Config. Propiedades de Equipo
                ├─ Configuración de Pérdidas               ├─ Configuración General
                ├─ Productos / Equipos / Mallas Activos    └─ Configuración de Benchmark
                │
                ├─ Módulo "Fluidos de Perforación y Equipos" → Hub → Reporte diario (8 pestañas)
                └─ Reporte Final del Pozo (Excel o PDF)
```

Los ítems "Registro Direccional", "Eventos No Programados", "Resumen de Costos", "Módulo RDF", "Fluidos de Completación" y "Tratamiento y Disposición de Desechos" aparecen en la pantalla principal como **"Próximamente"**. El registro direccional (survey) sí existe dentro del hub, y los eventos no programados se registran desde las pestañas 5 y 7.

> En la barra lateral, **"Reportes Diarios"** y **"Fosas / Volumetría"** no tienen enlace (`href`): hoy no llevan a ninguna parte. Se entra al reporte diario desde la pantalla principal del pozo.
