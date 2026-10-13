# 16 — Problemas conocidos, riesgos y pendientes

**Estado al 02-oct-2026.** Une la revisión del código del 25-sep, la lista de bugs del usuario (24-sep), la revisión del ingeniero (27-sep) y las observaciones y audios del 02-oct (`docs/fuentes/`). Lo resuelto queda abajo, en la sección F, como historial.

Prioridad: 🔴 alta · 🟠 media · 🟢 baja.

---

## A. Pendiente de probar en pantalla (el usuario)

Nada de esto se vio corriendo todavía. Si algo falla, pedir el traceback completo.

| Qué probar | Dónde | Detalle |
|---|---|---|
| Migración **0027** | consola | `python manage.py migrate` (la 0026 ya se aplicó el 02-oct) |
| `pip install pillow` | consola | Sin Pillow los Excel salen sin el logo de AOS |
| Intervalos abierto/cerrado | Pozo → Intervalos | Crear el 1, intentar el 2 (debe impedirlo), cerrar el 1, crear el 2, reabrir el 2 |
| Segunda moneda | Configuración General → reporte → Pantalla de costos | Elegir VES, tasa y %; revisar el recuadro "Cobro en dos monedas" |
| Hub bloqueado | Fluidos de Perforación y Equipos | Solo *Nuevo Reporte* y *Abrir*; etiquetas con *Modificar etiquetas* |
| Eliminar pozo | Pantalla del pozo | Escribir el nombre; la matriz no debe cambiar |
| **Servicios del pozo** (migración 0035) | Pestaña 8 › Servicios | Guía [pruebas/15](pruebas/15_SERVICIOS_DEL_POZO.md) |
| **Lodo reciclado solo volumen** | Pestaña 8 | Guía [pruebas/16](pruebas/16_LODO_RECICLADO_SOLO_VOLUMEN.md) |
| **Acumulados por columna en inventario** | Pestaña 8 | Guía [pruebas/17](pruebas/17_ACUMULADOS_INVENTARIO.md) |
| **Correcciones de octubre (20 puntos)** | Varias | 13 guías con pasos y casillas en [`pruebas/`](pruebas/README.md) (01 a 13), más verificar los puntos 6 y 19 del [23](23_CORRECCIONES_REVISION_OCT.md) |
| Tanques (antes fosas) | Pestaña 8 y Excel | Textos, mensajes de error y hoja *Contabilidad de Volumen* |
| Excel diario | Botón Excel | Logo AOS arriba a la izquierda, una sola hoja de inventario, **sin páginas 2 y 3 vacías**, "Fecha Inicial" |
| PDF | Reporte de propiedades y reporte final | Logo AOS arriba a la izquierda |
| Pantallas chicas | Inventario | El formulario *Nuevo producto* se ve sin bajar el zoom; revisar que el reporte diario no muestre dos barras de desplazamiento |
| `SmartMud.exe` | `empaquetado\Construir EXE.bat` | Sin consola negra, ícono de gota en la bandeja, *Salir*, segunda apertura solo abre el navegador |
| Lo del 27-sep | Pestañas 3, 4 y 8 y reporte final | Concentraciones, side track, hoyo piloto, reporte de propiedades, recap. Riesgo principal: cruce de concentraciones con el inventario unificado del compañero |

## B. Decisiones abiertas (preguntar a AOS o al ingeniero)

| Tema | Estado |
|---|---|
| ¿El reparto en **dos monedas** debe salir también en el **Excel**? ¿Dónde? | Hoy solo en la pantalla de costos |
| ¿Borrar **solo el último reporte** desde el hub, con confirmación? | El tío quería poder borrar un reporte "empezado mal"; el usuario pidió bloquear el hub. Hoy solo se puede eliminar el pozo completo |
| ~~Comentario del **reporte de propiedades**: ¿se guarda?~~ | **Resuelto (oct-2026):** se guarda (0032) y sale en el Excel del reportito. Ver [pruebas/13](pruebas/13_REPORTITO.md) |
| Paquete de entrega: reporte principal, inventario, concentraciones, volumetría | Confirmar con el ingeniero |
| Error en la hoja a lápiz del ingeniero (ejemplo 3 de concentraciones: 15,83, no 16,7) | **Avisarle** |
| Códigos de costo diario 1-4 | Confirmar con AOS |
| ¿En qué columna del resumen va un servicio de **filtración**? | Hoy se le elige una categoría existente. Ver [25 § 4](25_SERVICIOS_DEL_POZO.md) |
| Campo **"Unidades"** en la renta de equipos y bloqueo por cantidad del almacén | Pendiente (hoy deja poner 7 con 5 en almacén porque el campo no existe) |
| Indicadores **API RP 13C** de la pestaña 6 | Standby hasta que el usuario consiga las fórmulas |
| **SUS** y **DWM**, **Screen Usage** y **Reset** de ONE-TRAX | Sin información; no implementados |
| Tarjetas sin construir: RDF, Completación, Desechos, Resumen de costos | Se quitaron de la pantalla; construir solo si AOS las pide |
| Estado **CERRADO** del pozo | Existe en el modelo, sin pantalla |
| Logo de AOS en mejor calidad | Se recortó de una captura con fondo negro; reemplazar `static/operaciones/img/logo_reporte.png` si llega el original |

## C. Errores y limitaciones conocidas en el código

| # | Prioridad | Problema | Dónde | Qué hacer |
|---|---|---|---|---|
| C1 | 🟠 | **Edición de hidráulica inconsistente**: la pantalla abre en la 5ª y el Excel usa el ajuste del pozo (por defecto 4ª) | `reporte_hidraulica.js` (`hdEdicion='5'`) · `Pozo.usar_api_5ta_edicion_hidraulica` (default `False`) | Que la pantalla arranque con el ajuste del pozo, o cambiar el default a `True` (decisión del usuario: "5ª por defecto") |
| C2 | 🟠 | Los **costos se ponen en 0 en silencio** si la volumetría o las mallas tienen error (el reporte final sí lo avisa) | `resumen_costos` | Mostrar un aviso en la tarjeta de costos |
| C3 | 🟠 | El primer reporte crea **4 chequeos de lodo con datos de ejemplo** (10,5 lb/gal…) que se heredan | `views_daily_reports.py` (~líneas 190-250) | Crearlos vacíos o marcarlos como "ejemplo" |
| C4 | 🟢 | La **ecuación de sólidos** (hoy solo API) se guarda pero no cambia el cálculo | `ReporteDiarioMudConfig.solids_equation` | Implementar la variante API o quitar la opción |
| C5 | 🟢 | **Survey**: si la primera estación no está en MD = 0, su desplazamiento no entra en los acumulados; la "sección vertical" no se proyecta sobre un azimut | `calcular_survey_curvatura_minima` | Estación virtual en (0, 0, 0) y azimut de sección vertical |
| C6 | 🟢 | La hidráulica **no descuenta ΔP de MWD ni del motor** y suma el caudal de las **bombas del riser** | `views_hidraulica.py` | Sumar `dp_mwd`/`dp_motor` y excluir `riser_pump` |
| C7 | 🟢 | El **sistema de unidades** no convierte nada: todo en unidades de campo (salvo concentraciones en kg/m³) | global | Implementar conversión o limitar a *Standard Oilfield* |
| C8 | 🟢 | Dos convenciones de respuesta JSON (`success` en `views.py`, `ok` en el resto) | vistas | Unificar al refactorizar |
| C9 | 🟢 | El **número de reporte** se recalcula: insertar un reporte intermedio cambia los números de los siguientes | `ReporteDiario.numero_reporte` | Decidir si debe ser fijo |
| C10 | 🟢 | La API de borrar reporte no revalida la línea de tiempo de mallas | `api_reporte_diario_eliminar` | Hoy sin botón en pantalla; validar si se vuelve a exponer |
| C11 | 🟢 | Marca/modelo de bombas (pestaña 2) es texto libre con `<datalist>` | `reporte_diario_detalle.html` | Ya se vacía al entrar para mostrar los 15 modelos; un catálogo en BD sería opcional |

## D. Seguridad

> Pensado para **uso local en un solo equipo**. Antes de publicarlo en una red o en internet, atender **todo** lo siguiente.

| # | Riesgo | Detalle | Acción |
|---|---|---|---|
| S1 | 🔴 **Sin autenticación** | Ninguna vista exige inicio de sesión | `LoginRequiredMiddleware` o `@login_required`, y usuarios por rol |
| S2 | 🔴 **CSRF desactivado** | ~77 vistas de escritura con `@csrf_exempt`, aunque el frontend ya envía el token | Quitar `@csrf_exempt` gradualmente |
| S3 | 🟢 Resuelto en el `.exe` (12-oct) | `SECRET_KEY` propia por instalación, `DEBUG=False`, `ALLOWED_HOSTS` solo local. En desarrollo siguen los valores de prueba | — |
| S4 | 🟠 **`.env` con la contraseña real** | Está en `.gitignore`, pero viaja en los zips (ej. `Proyecto CHAPALA.zip` en la raíz) | No compartir zips con el `.env` (ya no hace falta: se usa SQLite) |
| S5 | 🟢 Mensajes de error internos | Algunas vistas devuelven `str(e)` | Registrar y devolver un mensaje genérico |

## E. Deuda técnica y limpieza

- **Archivos sobrantes** (ningún código los importa): `Claude outputs/` y `Proyecto CHAPALA.zip` (36 MB). Los `*-1.py`, `sidebar-1.html` y `proyecto chapala - claude/` ya se quitaron (12-oct, ver [24](24_PAPELERA_Y_TIPOS_DE_DATOS.md)). El script `limpiar_documentacion.ps1` (raíz) borra la documentación vieja y los temporales; estos otros se dejan para que el usuario decida.
- **Carpeta de plantillas `avances_19_sep/`**: nombre temporal. Renombrar (ej. `reporte_diario/`) junto con los `render()`.
- **`reporte_diario_detalle.html` tiene ~5.300 líneas** con el JS de las pestañas 1 a 5 en línea. Extraer a un JS por pestaña.
- **Sin pruebas automáticas.** Los motores son funciones puras. Fijar como pruebas los ejemplos verificados del manual (Gusher #2, mecha 1435 psi, centrífuga 9,2, retención 169,38 g/kg, concentraciones 13,64 / 15,20 / 15,83, side track 62 y 113 bbl, piloto 438 m y 109 bbl). Ver [19](19_GUIA_MANTENIMIENTO.md).
- **Reporte final**: recalcula la volumetría día por día en memoria; con cientos de reportes puede tardar.
- **Datos de prueba en la base** ("Diegui 2", "PIPE PARAO"…): limpiar antes de entregar a AOS.
- **Nombres internos heredados**: `Fosa`, `LODO_ENTERO`, `es_producto_mi`, `ingeniero_miswaco_*`, `mi_representante_*`, plantilla `reporte_diario_onetrax.xlsx`. En pantalla ya no se ven; renombrarlos exige migraciones.

## F. Historial de lo resuelto

### 13-oct-2026 (servicios del pozo; ver [25](25_SERVICIOS_DEL_POZO.md))
- Ingenieros, trailers y demás servicios se cobran en la pestaña 8 › **Servicios**, con categoría y tarifa diaria propias (0035). "Usado en otro módulo" queda para productos transferidos a otra línea. Falta probar en pantalla: [pruebas/15](pruebas/15_SERVICIOS_DEL_POZO.md).


### 12-oct-2026 (revisión de la base de datos; ver [24](24_PAPELERA_Y_TIPOS_DE_DATOS.md))
- Base revisada antes de empaquetar: esquema sincronizado, migra desde cero en SQLite, integridad ok. **SQLite queda como base definitiva.**
- **Papelera de pozos**: eliminar solo oculta; se restaura desde Pozos › Papelera (0034).
- Horas de las muestras como `TimeField` y costo del evento como `DecimalField` (0034). Limpieza de archivos sobrantes.
- **Licencia eliminada por completo** (sin activación). Configuración solo con SQLite.
- `SmartMud.exe` listo para producción de prueba: sin consola, crea y migra la base solo, `DEBUG=False`, y **arranca vacío** (sin productos ni pozos). Catálogo opcional con `cargar_catalogo_productos`.
- Inventario: el formulario del producto ya no se corta en pantallas de 1366 px (ver [24 § 5](24_PAPELERA_Y_TIPOS_DE_DATOS.md)).

### 02-oct-2026 (observaciones y audios del tío; ver [22](22_CAMBIOS_02OCT_SMART_MUD.md))
- Nombre **Smart Mud**, logo de la gota en la barra lateral, favicon, activación y `.exe`; **logo de AOS** en Excel y PDF.
- Sin "M-I" / "M-I SWACO" / "ONE-TRAX" en pantalla; ecuaciones de sólidos solo API (migración 0026).
- **Fosa → tanque** en pantallas, mensajes y Excel; "lodo entero" → **lodo reciclado**.
- Configuración General después de Información General; **monedas** con selector y **segunda moneda de cobro** (0027).
- **Intervalos abierto/cerrado**: no se abre el siguiente con uno abierto (0027).
- **Hub bloqueado** (solo crear y abrir), sin opciones que no se usaban; **eventos no programados** ocultos.
- **Eliminar pozo** con confirmación por nombre (devuelve inventario).
- **Doble clic** en catálogo → lista activa; "Orden de Impresión" completo; cabeceras de tablas legibles (texto blanco sobre azul).
- Inventario usable en pantallas chicas (sin bajar el zoom).
- Excel: una sola hoja de inventario y **sin páginas vacías**; "Fecha Inicial".
- `SmartMud.exe` **sin consola negra** (ícono en la bandeja, log en `datos\smartmud.log`).

### 27-sep-2026
- Reporte de **concentraciones** (pantalla y hoja Excel), contabilidad de volumen, **side track** e **hoyo piloto** (0022), **reporte de propiedades**, **reporte final** Excel/PDF (0023), redondeo en pantallas.

### 25-sep-2026
- **Inventario unificado** (compañero, `0022_inventario_unificado`): el reporte diario descuenta `Producto.cantidad`; tickets solo registro. **Revertido en oct-2026** por `0028_inventario_por_pozo` (ver [23](23_CORRECCIONES_REVISION_OCT.md)).
- `.bat` con `.venv`; `api_producto_delete` captura `ProtectedError`; `seed_data.py` adaptado; plantilla de pozo copia listas activas; código de equipo de superficie corregido en hidráulica; validación al cambiar la fecha de un reporte; tarjetas del pozo con operador y Spud; hojas vacías del Excel; datalist de bombas; logo del Excel (02-oct); barra lateral sin enlaces muertos; `catalogos_maestros.html` sin `{% now %}`.
