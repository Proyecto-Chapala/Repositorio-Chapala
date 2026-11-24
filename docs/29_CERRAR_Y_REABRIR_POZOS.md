# 29 — Cerrar y Reabrir Pozos

Documento del cambio implementado el **19-oct-2026** para habilitar el flujo completo de cierre y reapertura de pozos en Smart Mud.

---

## 1. Contexto y Necesidad
En el modelo de datos de Django (`Pozo.ESTADO_CHOICES`), existían tres estados:
- `BORRADOR` (Borrador en creación)
- `ACTIVO` (Activo durante la perforación)
- `CERRADO` (Pozo finalizado con recap emitido)

En la interfaz existía ya el botón de filtro rápido **«Cerrados»** en el directorio de pozos (`/pozos/`), pero **ninguna pantalla tenía el botón o endpoint para pasar el pozo a Cerrado** (estaba registrado en `docs/16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md` como: *"Estado CERRADO del pozo: existe en el modelo, sin pantalla"*).

---

## 2. Solución Implementada

### A. Pantalla de Reporte Final (Recap)
- En la tarjeta lateral de la pantalla de Reporte Final (`/pozos/<id>/reporte-final/`), se agregó la sección **Paso 3: Estado del pozo**.
- Si el pozo está **ACTIVO**:
  - Muestra la explicación operativa y el botón **`🔒 Cerrar pozo`**.
  - Al pulsar el botón, un modal de confirmación limpio pide confirmar el cierre.
  - Al confirmar, el pozo pasa a estado `CERRADO`.
- Si el pozo está **CERRADO**:
  - Muestra el distintivo **`🔒 Pozo Cerrado`**.
  - Muestra el botón **`🔓 Reabrir pozo`**, con su respectivo modal de confirmación para reactivarlo a `ACTIVO`.
- La cabecera del Reporte Final muestra el chip de estado: `● Activo` o `🔒 Cerrado`.

### B. Pantalla Principal de Configuración del Pozo (`/pozos/<id>/`)
- En el encabezado del pozo se muestra el chip de estado (`estado-ok` para activo o `estado-cerrado` para cerrado).
- En la barra de acciones inferiores (*zona de peligro*), se incorporó el botón **Cerrar pozo** / **Reabrir pozo** con modales de confirmación interactivos.

### C. Protección de Datos en el Hub de Reportes Diarios
- Si el pozo está `CERRADO`, en el Hub (`/pozos/<id>/drilling-fluids-equipment/`):
  - Se muestra un banner informativo superior advirtiendo que el pozo está cerrado y ofreciendo un botón directo para **Reabrir pozo**.
  - Los botones de **+ Nuevo Reporte** y **Eliminar Reporte** muestran un aviso impidiendo la acción mientras el pozo permanezca cerrado.
  - A nivel backend en `api_reporte_diario_crear` y `api_reporte_diario_eliminar`, se bloquea cualquier intento devolviendo código 400 y mensaje amigable.
  - Toda la información histórica, propiedades, volumetría, inventario y exportaciones Excel/PDF siguen 100% legibles y descargables.

### D. Directorio de Pozos (`/pozos/`)
- Al pulsar el filtro **«Cerrados»**, ahora se listan de inmediato los pozos cerrados con el chip `estado-cerrado` en gris neutro.
- Desaparecen de la vista **«Activos»** para mantener despejada la lista de trabajo diaria.

### E. Blindaje Integral contra Mutaciones en Configuración y Reportes
- En las 8 pantallas de configuración del pozo, la barra compartida (`_nav_info_pozo.html`) muestra de inmediato un banner rojo de solo lectura informando que el pozo está cerrado.
- En el backend, mediante la función `_validar_pozo_abierto(pozo)` se bloquea con código 400 cualquier petición `POST` de guardado o modificación en:
  - Todas las pantallas de configuración (`views.py`): Well Header, Marketing Codes, Tanques, Pérdidas, Configuración General, Almacenes, Tiempos, Productos Activos, Equipos Activos, Mallas Activas, Propiedades de Equipos, Benchmarks e Intervalos de Revestimiento.
  - Todas las pestañas de reporte diario (`views_daily_reports.py`, `views_inventario.py`, `views_control_solidos.py`, `views_opcionales.py`): General (1), Survey/Litología (2), Bombas/Barrena (3), Propiedades de lodo (4), Geometría (5), Control de Sólidos/Equipos (6), Distribución de tiempo (7), Volumetría/Inventario/Servicios (8) y módulos opcionales (muestras y eventos).

---

## 3. Detalles Técnicos
- **Migraciones:** No requirió migraciones (el campo `estado` ya tenía `'CERRADO'` desde la migración inicial).
- **Archivos modificados:**
  - `operaciones/views.py`: funciones `api_pozo_cerrar`, `api_pozo_reabrir`, `_validar_pozo_abierto` y guardias en todos los endpoints de guardado de setup.
  - `operaciones/urls.py`: rutas `api/pozos/<id>/cerrar/` y `api/pozos/<id>/reabrir/`.
  - `operaciones/views_daily_reports.py`, `operaciones/views_inventario.py`, `operaciones/views_control_solidos.py`, `operaciones/views_opcionales.py`: guardias `_validar_pozo_abierto` en endpoints de guardado.
  - `operaciones/views_recap.py`: flags `cerrado` y `reabierto` y versionado de `recap.js`.
  - `operaciones/templates/operaciones/pozos/_nav_info_pozo.html`: banner visual compartido de pozo cerrado.
  - `operaciones/templates/operaciones/pozos/recap.html`: tarjeta de estado, modales y chip.
  - `operaciones/static/operaciones/css/recap.css`: estilos de tarjeta paso 3, botones y chips.
  - `operaciones/static/operaciones/js/recap.js`: lógica de modales sin scripts en línea.
  - `operaciones/templates/operaciones/pozos/main.html`: chip de estado y botón/modal en zona de peligro.
  - `operaciones/static/operaciones/js/pozo_main.js`: manejadores de cerrar y reabrir.
  - `operaciones/templates/operaciones/avances_19_sep/daily_reports_hub.html`: banner de aviso y guardias en JS.
  - `operaciones/templates/operaciones/pozos_list.html`: clase `estado-cerrado`.
  - `operaciones/static/operaciones/css/pozos.css`: estilos `.estado-chip.estado-cerrado`.
  - `operaciones/tests/test_cerrar_reabrir_pozo.py`: 7 pruebas unitarias.
  - `operaciones/tests/test_pozo_cerrado_blindaje.py`: 29 pruebas unitarias exhaustivas de blindaje.
  - `docs/pruebas/29_BLINDAJE_POZO_CERRADO.md`: guía de prueba con pasos verificables.

