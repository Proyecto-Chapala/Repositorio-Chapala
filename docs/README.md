# Proyecto CHAPALA — Documentación

Sistema web de **All Oil Services, C.A. (AOS)** para dos trabajos:

1. **Inventario de productos químicos**: catálogo maestro de productos con su stock, costo y estado.
2. **Reportes diarios de fluidos de perforación**, al estilo **ONE-TRAX** (M-I SWACO): pozos, configuración del pozo y un reporte diario de 8 pestañas con volumetría, control de sólidos, hidráulica API 13D y exportación a Excel.

Estado al **23/09/2026**: proyecto cerrado en su versión funcional. Los pendientes y los posibles errores conocidos están en [PENDIENTES_Y_DECISIONES.md](PENDIENTES_Y_DECISIONES.md).

---

## Índice de la documentación

| Documento | Para quién | Qué contiene |
|---|---|---|
| [README.md](README.md) | Todos | Este archivo: instalación y arranque |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Desarrollo | App, carpetas, motores de cálculo, convenciones |
| [API_ENDPOINTS.md](API_ENDPOINTS.md) | Desarrollo | Todas las rutas, métodos y cuerpos JSON |
| [PENDIENTES_Y_DECISIONES.md](PENDIENTES_Y_DECISIONES.md) | Todos | Decisiones tomadas, bugs conocidos y trabajo pendiente |
| **Inventario** | | |
| [inventario/MODELO_DATOS.md](inventario/MODELO_DATOS.md) | Desarrollo | Modelo `Producto` y cómo se relaciona con los pozos |
| [inventario/FLUJOS.md](inventario/FLUJOS.md) | Desarrollo / soporte | Alta, edición, borrado, reglas de estado y relación con la pestaña 8 |
| [inventario/MANUAL_USUARIO.md](inventario/MANUAL_USUARIO.md) | Personal de AOS | Cómo usar la pantalla de Inventario |
| **Reportes (ONE-TRAX)** | | |
| [reportes/MODELO_DATOS.md](reportes/MODELO_DATOS.md) | Desarrollo | Todos los modelos del pozo y del reporte diario, por migración |
| [reportes/WIZARD_POZO.md](reportes/WIZARD_POZO.md) | Desarrollo / soporte | Creación del pozo (4 pasos), Spud Date y pantallas de configuración |
| [reportes/pestanas/](reportes/pestanas/) | Desarrollo / soporte | Un documento por cada pestaña del reporte diario (1 a 8) |
| [reportes/HIDRAULICA_API13D.md](reportes/HIDRAULICA_API13D.md) | Ingeniería | Fórmulas de 4ª y 5ª edición y verificación contra el manual |
| [reportes/VOLUMETRIA.md](reportes/VOLUMETRIA.md) | Ingeniería / desarrollo | Motor de volumetría, inventario de productos y concentraciones |
| [reportes/MODULOS_OPCIONALES.md](reportes/MODULOS_OPCIONALES.md) | Ingeniería | IFE, análisis de sólidos, retención en recortes, eventos y benchmark |
| [reportes/MANUAL_USUARIO.md](reportes/MANUAL_USUARIO.md) | Personal de AOS | Guía paso a paso del reporte diario |

---

## Requisitos

| Componente | Versión usada |
|---|---|
| Python | 3.14 (según el reporte de avances del 22/09/2026) |
| Django | 6.1.1 |
| PostgreSQL | Cualquier versión compatible con `psycopg2-binary 2.9.12` |
| Navegador | Chrome o Edge actualizados |

Dependencias exactas (`requirements.txt`):

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

`openpyxl` genera el Excel del reporte diario. `pypdf` no se usa en el código actual de `operaciones`.

---

## Instalación en un equipo nuevo

```bat
cd "C:\ruta\Proyecto CHAPALA"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Base de datos

La configuración se lee de un archivo `.env` en la raíz del proyecto (`chapala/settings.py` lo carga a mano, sin librerías extra). Variables:

| Variable | Default si falta | Uso |
|---|---|---|
| `USE_POSTGRES` | `True` | `True` = PostgreSQL. `False` = SQLite (`db.sqlite3`) |
| `DB_NAME` | `chapala_db` | Nombre de la base PostgreSQL |
| `DB_USER` | `postgres` | Usuario |
| `DB_PASSWORD` | `postgres` | Contraseña |
| `DB_HOST` | `localhost` | Servidor |
| `DB_PORT` | `5432` | Puerto |

El `.env` está en `.gitignore` y no debe subirse al repositorio.

Crear las tablas:

```bat
python manage.py migrate
python manage.py createsuperuser   (opcional, para /admin/)
```

Las migraciones de la app `operaciones` van de la `0001` a la `0022`. Ver [reportes/MODELO_DATOS.md](reportes/MODELO_DATOS.md).

### Datos iniciales

No hace falta cargar nada para empezar a usar los pozos: al crear un pozo el sistema **siembra automáticamente** sus catálogos (15 categorías de pérdida, 7 tipos de fosa, 20 actividades de distribución de tiempo y 4 tipos de ticket).

Los productos del inventario se cargan desde la pantalla de Inventario o desde `/admin/`.

Para cargar el catálogo AOS de productos: `python seed_data.py`. Solo crea los productos que no existen; no modifica los que ya están.

> `seed_propiedades.py` pertenece a la app antigua `reportes` (en `_legacy/`) y **no funciona** con la versión actual.

---

## Cómo arrancar el sistema

### Opción 1: doble clic en `Iniciar Sistema.bat`

Abre el navegador en `http://127.0.0.1:8000/` y levanta el servidor.

El `.bat` usa el entorno virtual `.venv\` de la raíz del proyecto.

### Opción 2: consola

```bat
.venv\Scripts\activate
python manage.py runserver 127.0.0.1:8000
```

### Pantallas principales

| URL | Pantalla |
|---|---|
| `/` | Inventario de productos |
| `/pozos/` | Lista de pozos |
| `/pozos/nuevo/` | Asistente para crear un pozo |
| `/pozos/<id>/` | Pantalla principal del pozo |
| `/pozos/<id>/drilling-fluids-equipment/` | Historial de reportes diarios del pozo |
| `/pozos/<id>/daily-report/<id_reporte>/` | Reporte diario (8 pestañas) |
| `/catalogos-maestros/` | Catálogos globales: equipos, mallas, propiedades, benchmark y componentes de sarta |
| `/admin/` | Administración de Django |

---

## Advertencias de seguridad

El proyecto está configurado para **uso local en un solo equipo**, no para publicarse en internet:

- `DEBUG = True` y `ALLOWED_HOSTS = ['*']`.
- La `SECRET_KEY` está escrita en `settings.py`.
- No hay inicio de sesión en las pantallas; cualquiera que abra la URL puede editar.
- Casi todas las APIs de escritura llevan `@csrf_exempt`.

Si algún día se expone en red, hay que corregir esos cuatro puntos antes.
