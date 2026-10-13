# 01 — Instalación y ejecución

## Requisitos

| Componente | Versión | Nota |
|---|---|---|
| Python | **3.12 o superior** | Django 6.1 no funciona con 3.11 o anteriores. El `.venv` actual está construido para 3.12 (`cp312`) y las notas del proyecto mencionan 3.14. |
| Navegador | Chrome o Edge actualizados | La interfaz usa JavaScript moderno (`fetch`, `async/await`). |

Dependencias (`requirements.txt`):

```
asgiref==3.12.1
Django==6.1.1
et_xmlfile==2.0.0
openpyxl==3.1.5
pillow
pystray
pypdf==6.18.1
sqlparse==0.6.0
tzdata==2026.3
```

> Antes del primer uso, ejecuta `pip install -r requirements.txt` dentro del entorno. Sin `openpyxl` Django no arranca (`views_daily_reports.py` lo importa al cargar las rutas). **`pillow`** (agregado el 02-oct-2026) lo usa `openpyxl` para poner el **logo de AOS** en los Excel; sin él los Excel salen sin logo.

## 1. Preparar el entorno

```bat
cd "C:\Users\SECRETARIA\Documents\Programacion\Personal\Proyecto CHAPALA"
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Base de datos y `.env`

La base de datos es **SQLite** (un solo archivo, sin servidor). En desarrollo es `db.sqlite3` en la raíz; `SmartMud.exe` usa la suya en `datos\chapala_pruebas.sqlite3`. PostgreSQL se descartó el 12-oct-2026 (ver [24](24_PAPELERA_Y_TIPOS_DE_DATOS.md)).

`chapala/settings.py` lee el archivo `.env` de la raíz si existe (opcional). Variables:

| Variable | Por defecto | Uso |
|---|---|---|
| `CHAPALA_DB_PATH` | `db.sqlite3` de la raíz | Ruta del archivo SQLite |
| `DJANGO_DEBUG` | `True` | `False` en el `.exe` (sin páginas técnicas de error) |
| `DJANGO_SECRET_KEY` | clave de desarrollo | El `.exe` crea una propia en `datos\clave_secreta.txt` |

## 3. Migraciones

```bat
python manage.py migrate
python manage.py showmigrations operaciones
```

Deben aparecer marcadas de `0001_initial` a **`0027_intervalo_cerrado_moneda_secundaria`** (estado al 02-oct-2026). La cadena completa y qué hace cada una está en [03](03_MODELO_DATOS.md#historial-de-migraciones) y en el [traspaso](00_TRASPASO.md).

> El 02-oct-2026 el usuario corrió `migrate` desde cero hasta la 0026 sin errores.

## 4. Datos iniciales

- **Catálogos por pozo**: no hace falta cargarlos. Al crear un pozo, el sistema siembra automáticamente los 7 tipos de tanque (fosa), las 15 categorías de pérdida estándar, las 20 actividades de distribución de tiempo y los tipos de ticket de ejemplo (ver [05](05_CONFIGURACION_POZO.md)).
- **Catálogos maestros globales** (equipos, mallas, componentes de sarta, propiedades, parámetros de benchmark): se cargan desde la pantalla **Catálogos Maestros** o desde `/admin/`.
- **Productos químicos**: desde la pantalla **Inventario**.

- **Catálogo AOS de productos**: `python manage.py cargar_catalogo_productos` (53 productos; solo crea los que no existen, con precio y existencia en 0). Es opcional: el `.exe` **no** lo corre (arranca con el inventario vacío).
- **Pozo de prueba**: `python manage.py seed_pozo_prueba` crea el pozo `PRUEBA-001` (solo para desarrollo; el `.exe` arranca sin pozos).

## 5. Superusuario (para `/admin/`)

```bat
python manage.py createsuperuser
```

El panel `/admin/` registra los modelos de `operaciones` (`operaciones/admin.py`). Sirve para corregir datos puntuales. No reemplaza a las pantallas del sistema.

## 6. Arrancar el servidor

Manual:

```bat
python manage.py runserver 127.0.0.1:8000
```

Con el acceso directo **`Iniciar Sistema.bat`** (usa `.venv`): abre el navegador en `http://127.0.0.1:8000/` y levanta el servidor en una ventana de consola. Es el modo de **desarrollo**; a los ingenieros se les entrega el `.exe` (sección 9).

## 7. Direcciones principales

| URL | Pantalla |
|---|---|
| `/` | Inventario de almacén (productos químicos) |
| `/pozos/` | Lista de pozos |
| `/pozos/nuevo/` | Wizard de creación de pozo |
| `/pozos/<id>/` | Pantalla principal del pozo |
| `/pozos/<id>/drilling-fluids-equipment/` | Hub de Fluidos de Perforación y Equipos (lista de reportes diarios) |
| `/pozos/<id>/daily-report/<id_reporte>/` | Reporte diario (8 pestañas) |
| `/pozos/<id>/reporte-final/` | Reporte final del pozo (Excel o PDF) |
| `/catalogos-maestros/` | Catálogos maestros globales |
| `/admin/` | Administración de Django |

## 8. Problemas frecuentes de arranque

| Síntoma | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'openpyxl'` | Faltan dependencias en el entorno | `pip install -r requirements.txt` |
| `Couldn't import Django` | No se activó el entorno virtual | `.venv\Scripts\activate` |
| La pantalla no refleja cambios de JS/CSS | Caché del navegador | `Ctrl + F5`. Las pestañas del reporte diario ya se versionan solas (ver [19](19_GUIA_MANTENIMIENTO.md)) |
| `no such table: operaciones_...` | Falta migrar | `python manage.py migrate` |
| `InconsistentMigrationHistory` / `Conflicting migrations` | Dos ramas de migraciones | Ver la cadena de migraciones en el traspaso; no cambiar dependencias de migraciones ya aplicadas, usar una migración de unión (`merge`) |

## 9. Ejecutable para los ingenieros (`SmartMud.exe`)

Carpeta `empaquetado/`. Se construye con doble clic en **`Construir EXE.bat`**, que:

1. instala en el `.venv` PyInstaller, `pystray` y `pillow`;
2. verifica el proyecto con Python (base temporal, no toca datos);
3. construye `dist\SmartMud\SmartMud.exe` con `chapala.spec`;
4. verifica el ejecutable (el resultado queda en `empaquetado\verificacion_exe.log` y se muestra en la consola);
5. comprime `dist\SmartMud_Pruebas.zip` con `LEEME_PRUEBAS.txt`.

Cómo funciona el `.exe` (`empaquetado/chapala_app.py`, actualizado el 02-oct-2026):

| Tema | Comportamiento |
|---|---|
| Ventana | **Sin consola negra** (`console=False`). El sistema vive en un **ícono de gota** en la bandeja de Windows: *Abrir Smart Mud* / *Salir* |
| Base de datos | SQLite propia en `datos\chapala_pruebas.sqlite3`, junto al `.exe`. Se crea y migra sola en cada arranque (no hace falta `migrate`); **arranca vacía: sin productos ni pozos** |
| Segunda vez | Si ya está abierto (`datos\servidor_en_uso.txt` + puerto que responde), solo abre el navegador |
| Servidor | `django.core.servers.basehttp.run` en un hilo, con `StaticFilesHandler`; puerto libre entre 8000 y 8019 |
| Errores | Todo lo que antes salía en consola va a `datos\smartmud.log` (se reinicia al pasar 5 MB). Si no arranca, cuadro de mensaje de Windows con el error |
| Ícono | `empaquetado\smartmud.ico` / `smartmud.png` (la gota del logo Smart Mud) |
| Verificación | `SmartMud.exe --verificar --log <archivo>` (sale con código 1 si algo falla) |
| Modo | `DEBUG=False`, solo escucha en `127.0.0.1`, clave secreta propia en `datos\clave_secreta.txt`. **Sin licencia ni activación** (se quitó el 12-oct-2026) |
| Respaldo | Salir del sistema y copiar la carpeta `datos` |

Para cambiar el ícono basta con reemplazar `smartmud.ico` y `smartmud.png` y volver a construir.
