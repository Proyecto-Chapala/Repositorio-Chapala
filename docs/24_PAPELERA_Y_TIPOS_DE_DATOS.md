# 24 — Papelera de pozos y revisión de la base de datos (12-oct-2026)

Revisión de la base de datos antes de empaquetar el sistema para la prueba en producción. Migración **`0034_papelera_pozos_y_tipos_opcionales`**.

## Resultado de la revisión

- `manage.py check` sin errores y `makemigrations --check` sin cambios: modelos y migraciones están sincronizados.
- Una base **SQLite vacía** migra de la 0001 a la 0034 sin errores (así arranca el `.exe` la primera vez).
- `db.sqlite3` del usuario: `PRAGMA integrity_check` = ok, sin claves foráneas rotas.
- Catálogos (Producto, Equipo, Malla, Tipo de ticket) protegidos con `PROTECT`/`RESTRICT`; los datos del pozo y del reporte cuelgan en `CASCADE`. Reglas de unicidad en los lugares correctos (un reporte por pozo y fecha, un producto por reporte, etc.). Dinero e inventario en `DecimalField`.
- **Base de datos definitiva: SQLite.** PostgreSQL fue la idea inicial; para el volumen de AOS no hace falta.

## Cambios

### 1. Papelera de pozos

**Antes:** "Eliminar pozo" borraba el pozo y, en cascada, todos sus reportes. No se podía deshacer.

**Ahora:** eliminar **solo oculta** el pozo (`Pozo.eliminado_en`, `Pozo.eliminado_por`). Todo lo suyo queda intacto.

- `Pozo.objects` (manager por defecto, `PozoVigenteManager`) **excluye** los pozos en la papelera. Por eso ninguna pantalla, lista ni `get_object_or_404(Pozo, …)` los ve, sin tocar cada consulta. Para verlos se usa `Pozo.todos`.
- La confirmación pide escribir el nombre exacto del pozo y muestra cuántos reportes diarios tiene.
- **Pozos › Papelera (N)** (`/pozos/papelera/`): lista los pozos eliminados con fecha, usuario y número de reportes, y el botón **Restaurar**.
- El nombre sigue reservado: no se puede crear otro pozo con el nombre de uno que está en la papelera (el formulario lo avisa).
- No existe borrado definitivo desde pantalla (no se pidió).

Archivos: `models.py` (`PozoVigenteManager`, `enviar_a_papelera`, `restaurar`), `views.api_pozo_eliminar`, `views.pozos_papelera_view`, `views.api_pozo_restaurar`, `forms_pozo.PozoPaso1Form.clean_nombre`, `pozos/papelera.html`, `pozos_papelera.js`, `pozos/main.html`, `pozos_list.html`, `pozos.css`.

### 2. Tipos de datos de los módulos opcionales

| Campo | Antes | Ahora |
|---|---|---|
| `hora_inicio`, `hora_fin` (análisis de sólidos y retención de recortes) | texto `HH:MM` (aceptaba `25:99`) | `TimeField` (nulo si está vacío) |
| `EventoNoProgramado.costo` | `FloatField` | `DecimalField(14,2)` |

La migración primero limpia las horas vacías o inválidas (quedan vacías) y luego cambia el tipo. La API sigue recibiendo y devolviendo `HH:MM`.

### 3. Limpieza

Se quitaron del repositorio (siguen en el historial de git): `operaciones/models-1.py`, `views-1.py`, `admin-1.py`, `componentes/sidebar-1.html` y la carpeta `proyecto chapala - claude/`.

### 4. Licencia eliminada y empaquetado para producción de prueba

- **Licencia quitada por completo**: `licencia.py`, `middleware_licencia.py`, `views_licencia.py`, la pantalla de activación, su CSS, la ruta `/licencia/` y `scripts/generar_clave_licencia.py`.
- `settings.py`: solo SQLite; `DEBUG`, `SECRET_KEY` y `ALLOWED_HOSTS` desde variables de entorno; errores de Django a la salida (en el `.exe`, a `datos\smartmud.log`). Se quitó `psycopg2` de `requirements.txt` y se agregó `pystray`.
- `SmartMud.exe`: `DEBUG=False`, clave secreta propia en `datos\clave_secreta.txt`, crea y migra la base solo. **Arranca vacía: sin productos ni pozos** (pedido del usuario al probarlo; el catálogo y `PRUEBA-001` solo se cargan en la base temporal de la verificación).
- **Catálogo de productos como comando opcional**: el `seed_data.py` se había borrado en el commit `f27f979` y el lanzador lo seguía importando. Ahora es `python manage.py cargar_catalogo_productos` (53 productos con precio y existencia en 0), para cargarlo a mano si se quiere.
- Construido y verificado: `SmartMud.exe --verificar` todo correcto; arranque real probado (base nueva, páginas, estáticos y 404 sin página técnica). Entregable: `empaquetado\dist\SmartMud_Pruebas.zip`.

### 5. Inventario: el formulario se cortaba

En Inventario, el formulario del producto (columna derecha) quedaba cortado y había que bajar el zoom. **Causa:** las celdas de la tabla no parten línea (`white-space: nowrap`) y la columna `1.2fr` del grid crecía hasta el ancho de la descripción más larga. **Arreglo** (`inventario.css` y su copia en `styles.css`): `grid-template-columns: minmax(0, 1.2fr) minmax(340px, 0.8fr)`, `min-width: 0` en la columna izquierda y desplazamiento horizontal dentro de la tabla. Es el mismo patrón que ya usa `catalogos_maestros.css`. Verificado a 1366×768.

## Pruebas

- Automáticas: `test_papelera_pozos.py`, `test_tipos_modulos_opcionales.py` y `test_catalogo_productos.py` (98 en total).
- En pantalla: [pruebas/14_PAPELERA_POZOS.md](pruebas/14_PAPELERA_POZOS.md).
