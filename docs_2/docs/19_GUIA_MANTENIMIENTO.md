# 19 — Guía de mantenimiento para desarrolladores

## Reglas del proyecto (acordadas con el usuario)

1. **Todo el texto visible en español.** Los nombres de ONE-TRAX en inglés solo van entre paréntesis como referencia.
2. **Buen diseño y opciones bien ordenadas.** Antes de inventar una pantalla, revisar las capturas y el manual de ONE-TRAX.
3. **Reutilizar código**: motores puros, utilidades JS compartidas (`csEsc`, `csNum`, `csFmt`, `csDinero`).
4. **CSS y JS en archivos aparte, uno por pestaña o pantalla** (`reporte_tiempo.*`, `reporte_control_solidos.*`, `reporte_inventario.*`, `reporte_hidraulica.*`, `reporte_opcionales.*`). No agregar más JS en línea a `reporte_diario_detalle.html`.
5. **Versionar los estáticos** de las pestañas con `_version_estaticos()` (ver abajo).
6. **Trabajar segmento por segmento** y probar cada uno antes de seguir.
7. **Los archivos usan fin de línea CRLF (Windows).** Respetarlo al editar para no generar diferencias falsas en git.
8. **Antes de editar un archivo, releerlo del disco**: pudo cambiar desde la última vez.
9. Rama de git de trabajo: `Refactorizacion`.

## Agregar una pestaña o sub-vista al reporte diario

1. **Modelos** en un archivo propio (`models_<area>.py`) e importarlo al final de `models.py` (`from .models_<area> import *`).
2. Si la lista depende de configuración del pozo que se guarda "borrando y recreando", **no usar FK a esa lista**: guardar número, código o serie más una copia del texto (ver [02 § C](02_ARQUITECTURA.md)).
3. `python manage.py makemigrations operaciones` → revisar el archivo → `migrate`.
4. **Motor** (si hay cálculos): funciones puras, sin Django, en `<area>.py`. Si hay saldos que dependen del orden de los días, **repetir la línea de tiempo** y lanzar una excepción con un mensaje en español que diga el día y el elemento que fallan.
5. **Vistas API** en `views_<area>.py`:
   - lectura: `@require_http_methods(["GET"])` → `JsonResponse({'ok': True, ...})`
   - escritura: validar → `with transaction.atomic(): guardar; simular; si falla → excepción → rollback` → devolver **el estado completo** de la pestaña
   - errores: `JsonResponse({'ok': False, 'error': '…'}, status=400)`
6. **Rutas** en `operaciones/urls.py`, bajo `api/pozos/<int:pk>/daily-report/<int:reporte_pk>/<area>/…`.
7. **Frontend**: `static/operaciones/js/reporte_<area>.js` y `css/reporte_<area>.css`. Cargarlos en `reporte_diario_detalle.html` **después** de `reporte_control_solidos.js`, con `?v={{ version_estaticos }}`, y agregar sus rutas a la llamada `_version_estaticos(...)` de `reporte_diario_detalle_view`.
8. Si el dato va al Excel, agregarlo en `reporte_excel._datos()` y en la hoja que corresponda.
9. Si genera costo, integrarlo en `views_inventario.resumen_costos()` (única fuente de costos).
10. **Documentar**: actualizar el documento de la pestaña, [03](03_MODELO_DATOS.md), [04](04_API_ENDPOINTS.md) y [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md).

## Agregar un campo a un modelo existente

1. Agregar el campo con `null=True, blank=True` o un `default`, para no romper registros existentes.
2. `makemigrations` / `migrate`.
3. Incluirlo en el `to_dict()` o en la respuesta de la API, en el guardado de la vista y en el JS.
4. Si el reporte se hereda del día anterior (`obtener_o_crear_*`), agregar el campo a la copia.

## Anti-caché de estáticos

`views._version_estaticos(*rutas)` devuelve la fecha de modificación más reciente de esos archivos. En la plantilla:

```django
<script src="{% static 'operaciones/js/reporte_tiempo.js' %}?v={{ version_estaticos }}"></script>
```

El navegador descarga el archivo **solo cuando cambió**. No usar `{% now %}`, que obliga a descargarlo en cada visita.

## Pruebas

No hay pruebas en el proyecto. En `docs/herramientas/test_motores.py` hay **8 pruebas de los motores** con los ejemplos del manual: mecha 1435 psi / 672 HHP / 373 ft/s, junta 0,056452, centrífuga, zaranda, stock y costo de mallas, volumen químico. **Pasan contra el código actual** (verificado el 25-sep-2026). Para activarlas:

```bat
mkdir operaciones\tests
type nul > operaciones\tests\__init__.py
copy docs\herramientas\test_motores.py operaciones\tests\
python manage.py test operaciones
```

Pruebas recomendadas para agregar:
- Volumetría completa de un pozo de 3 días: no contabilizado en 0, inventario negativo rechazado.
- Geometría del ejemplo Gusher #2 del manual.
- Retención en recortes (30,7 / 20,7 / 5,2 → 169,38 y 251,21 g/kg).
- Vistas: crear un reporte, un ticket y una transacción, y deshacerla (con `django.test.Client`).

Comprobaciones rápidas antes de entregar:

```bat
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test operaciones
```

## Regenerar la documentación del modelo de datos

Las tablas de [03](03_MODELO_DATOS.md) y [04](04_API_ENDPOINTS.md) se generaron desde el código:

```bat
python manage.py shell < docs/herramientas/generar_referencia.py
```

El script crea `docs/herramientas/salida/modelos.md` y `api.md`. Copia su contenido sobre la sección "Detalle por modelo" o "Rutas por módulo" del documento correspondiente.

## Respaldo de la base de datos

PostgreSQL:
```bat
pg_dump -U postgres -F c -f chapala_AAAAMMDD.backup chapala_db
pg_restore -U postgres -d chapala_db --clean chapala_AAAAMMDD.backup
```
O, independiente del motor: `python manage.py dumpdata operaciones --indent 2 > respaldo.json`.

## Pasar a producción (lista mínima)

1. `SECRET_KEY`, `DEBUG=False` y `ALLOWED_HOSTS` desde el `.env`.
2. Autenticación en todas las vistas y quitar `@csrf_exempt` (ver [16 § C](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md#c-seguridad)).
3. `python manage.py collectstatic` y servir `staticfiles/` con el servidor web.
4. Servidor WSGI (por ejemplo `waitress` en Windows) en lugar de `runserver`.
5. Respaldos automáticos de PostgreSQL.
6. Limpiar los datos de prueba.
