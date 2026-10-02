# 01 — Instalación y ejecución

## Requisitos

| Componente | Versión | Nota |
|---|---|---|
| Python | **3.12 o superior** | Django 6.1 no funciona con 3.11 o anteriores. El `.venv` actual está construido para 3.12 (`cp312`) y las notas del proyecto mencionan 3.14. |
| PostgreSQL | 13+ recomendado | Opcional: con `USE_POSTGRES=False` se usa SQLite. |
| Navegador | Chrome o Edge actualizados | La interfaz usa JavaScript moderno (`fetch`, `async/await`). |

Dependencias (`requirements.txt`):

```
asgiref==3.12.1
Django==6.1.1
et_xmlfile==2.0.0
openpyxl==3.1.5
psycopg2-binary==2.9.12
pypdf==6.18.1
sqlparse==0.6.0
tzdata==2026.3
```

> ⚠ **El `.venv` incluido en la carpeta NO tiene `openpyxl` ni `pypdf`.** Sin `openpyxl`, Django no arranca: `views_daily_reports.py` lo importa al cargar las rutas. Antes del primer uso, ejecuta `pip install -r requirements.txt` dentro del entorno.

## 1. Preparar el entorno

```bat
cd "C:\Users\SECRETARIA\Documents\Programacion\Personal\Proyecto CHAPALA"
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configurar la base de datos (`.env`)

`chapala/settings.py` lee el archivo `.env` de la raíz, sin librerías externas. Las líneas `CLAVE=valor` se cargan como variables de entorno. Variables:

| Variable | Por defecto | Uso |
|---|---|---|
| `USE_POSTGRES` | `True` | `True/1/yes` → PostgreSQL; cualquier otro valor → SQLite (`db.sqlite3`) |
| `DB_NAME` | `chapala_db` | Nombre de la base PostgreSQL |
| `DB_USER` | `postgres` | Usuario |
| `DB_PASSWORD` | `postgres` | Contraseña |
| `DB_HOST` | `localhost` | Servidor |
| `DB_PORT` | `5432` | Puerto |

Ejemplo:

```ini
USE_POSTGRES=True
DB_NAME=chapala_db
DB_USER=postgres
DB_PASSWORD=********
DB_HOST=localhost
DB_PORT=5432
```

Crear la base en PostgreSQL (una sola vez):

```sql
CREATE DATABASE chapala_db ENCODING 'UTF8';
```

> El `.env` contiene la contraseña real de la base de datos y está correctamente excluido en `.gitignore`. No lo compartas ni lo incluyas en copias o zips que salgan del equipo.

## 3. Migraciones

```bat
python manage.py migrate
python manage.py showmigrations operaciones
```

Deben aparecer las 21 migraciones marcadas, de `0001_initial` a `0021_modulos_opcionales`. Las últimas (`0019`, `0020`, `0021`) corresponden a la pestaña 8 y a los módulos opcionales.

> Actualización 27-sep-2026: ahora hay migraciones hasta la **0024** (`0022_inventario_unificado`, `0022_sidetrack`, `0023_recap_pozo`, `0024_merge`). Ver `claude/chapala-traspaso-siguiente-conversacion.md`.

Comprobación verificada el 25-sep-2026 sobre una copia del proyecto en SQLite: `manage.py check` → sin problemas; `migrate` → aplica las 21; `makemigrations --check` → *No changes detected*, es decir, los modelos y las migraciones están sincronizados.

## 4. Datos iniciales

- **Catálogos por pozo**: no hace falta cargarlos. Al crear un pozo, el sistema siembra automáticamente los 7 tipos de fosa, las 15 categorías de pérdida estándar, las 20 actividades de distribución de tiempo y los tipos de ticket de ejemplo (ver [05](05_CONFIGURACION_POZO.md)).
- **Catálogos maestros globales** (equipos, mallas, componentes de sarta, propiedades, parámetros de benchmark): se cargan desde la pantalla **Catálogos Maestros** o desde `/admin/`.
- **Productos químicos**: desde la pantalla **Inventario**.

> ⚠ Los scripts `seed_data.py` y `seed_propiedades.py` de la raíz **ya no funcionan**. Importan `mychapala.models` y una app `reportes` que no existen en esta versión, porque el modelo `Producto` vive hoy en `operaciones`. Hay que adaptarlos antes de usarlos (ver [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md)).

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

Con el acceso directo **`Iniciar Sistema.bat`**: abre el navegador en `http://127.0.0.1:8000/` y levanta el servidor.

> ⚠ `Iniciar Sistema.bat` ejecuta `.\env\Scripts\python.exe`, pero el entorno que viene con el proyecto se llama **`.venv`**. Si en tu equipo no existe la carpeta `env`, corrige la línea a `".\.venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000`.

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
| `connection refused` o `password authentication failed` | PostgreSQL apagado o credenciales del `.env` erradas | Revisar el servicio y el `.env`, o usar `USE_POSTGRES=False` para probar |
| La pantalla no refleja cambios de JS/CSS | Caché del navegador | `Ctrl + F5`. Las pestañas del reporte diario ya se versionan solas (ver [19](19_GUIA_MANTENIMIENTO.md)) |
| `relation "operaciones_..." does not exist` | Falta migrar | `python manage.py migrate` |
| `InconsistentMigrationHistory` / `Conflicting migrations` | Dos ramas de migraciones | Ver la cadena de migraciones en el traspaso; no cambiar dependencias de migraciones ya aplicadas, usar una migración de unión (`merge`) |
