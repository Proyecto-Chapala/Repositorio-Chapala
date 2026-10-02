# 16 — Problemas conocidos, riesgos y pendientes

Revisión del código hecha el **25-sep-2026** sobre la copia completa del proyecto, más la lista de bugs del usuario (*"Lista de Posibles Bugs, cosas por revisar.md"*, 24-sep). Actualizado el **27-sep-2026** con lo pedido por el ingeniero en la revisión (concentraciones, side track, reportes, redondeo). Cada punto indica **causa**, **impacto** y **qué hacer**.

Prioridad: 🔴 alta · 🟠 media · 🟢 baja.

---

## A. Bugs reportados por el usuario

### 1. 🟢 Marca/modelo de bombas: "la lista solo muestra lo escrito" (pestaña 2)

- **Causa**: el campo es un `<input list="lista-modelos-bombas">` con un `<datalist>` de 15 modelos (EMSCO, National, Gardner Denver, Ideco, Wirth, Weatherford). Así funciona el HTML nativo: el navegador **filtra las sugerencias por el texto que ya tiene el campo**. Si el campo dice "EMSCO F-1000", solo sugiere lo que coincide con eso. No es un problema de datos: el texto libre se guarda bien.
- **Qué hacer**: para ver todas las opciones, borrar el campo y hacer clic o presionar ↓. Si se quiere un desplegable real, cambiar a `<select>` con opción "Otro…" o a un combo propio. Opcional: guardar un catálogo de modelos de bomba en BD en lugar de la lista fija del HTML. El ingeniero confirmó que el nombre editable está bien y que se usan de 2 a 4 bombas.

### 2. 🔴 Inventario en 0 en la pestaña 8

- **Causa**: **no hay dos inventarios mezclados por error**: el sistema tiene **dos inventarios distintos a propósito**.
  - *Inventario* (pantalla del menú) = stock del **almacén** (`Producto.cantidad`).
  - *Pestaña 8* = inventario **del taladro de ese pozo**. Arranca en 0 y **solo sube con tickets de recepción de productos** (réplica de ONE-TRAX). El motor `volumetria.simular()` parte de `stock = 0` y nunca lee `Producto.cantidad`.
  - Por eso la pestaña 8 rechaza el uso: *"el inventario de X queda en −N… Registra primero el ticket de recepción."*
- **Qué hacer (uso)**: en la pestaña 8 → *Tickets de productos* → tipo "Recepción desde almacén" → cantidades reales. Después ya se puede usar el producto.
- **Qué hacer (desarrollo, si AOS lo quiere)**: definir la regla de negocio y conectar ambos inventarios. Por ejemplo, que un ticket de ENTRADA al pozo descuente `Producto.cantidad` y uno de SALIDA lo devuelva, validando que el almacén tenga stock.
- También revisar en *Productos activos* que cada producto tenga **unidad** (si la unidad está vacía, se trata como servicio sin existencias) y **precio**.

### 3. 🟠 Excel con hojas o páginas repetidas sin datos

- **Causa**: no viene de otros pozos, porque el Excel siempre es de **un** pozo y **un** reporte. Hay tres razones: (a) tres hojas de inventario químico con los mismos datos en otro orden o filtro (DF, por nombre, completo), como en ONE-TRAX; (b) la plantilla trae **3 páginas pre-dibujadas** por hoja de inventario, y las no usadas quedan con encabezado vacío (el área de impresión sí se recorta); (c) *Equipos* y *Mallas* salen aunque no haya datos. Detalle en [14](14_REPORTE_EXCEL.md).
- **Qué hacer**: en `reporte_excel.py`, después de llenar, borrar las filas de las páginas no usadas (`ws.delete_rows`) y eliminar hojas vacías u ofrecer un selector de hojas.

---

## B. Errores encontrados en la revisión del código

| # | Prioridad | Problema | Dónde | Qué hacer |
|---|---|---|---|---|
| B1 | 🔴 | **El entorno `.venv` no tiene `openpyxl` ni `pypdf`**, y sin `openpyxl` Django no arranca | `.venv` | `pip install -r requirements.txt` |
| B2 | 🔴 | `Iniciar Sistema.bat` usa `.\env\Scripts\python.exe`, pero el entorno se llama `.venv` | `.bat` | Cambiar la ruta o verificar qué carpeta existe en el equipo |
| B3 | 🟠 | **Eliminar un producto usado en algún pozo da error 500**: las llaves foráneas son `PROTECT` y `api_producto_delete` no captura `ProtectedError`. Las demás eliminaciones de catálogos sí lo capturan | `views.py` `api_producto_delete` | Capturar `ProtectedError` y responder *"El producto se usa en pozos; no se puede eliminar"* |
| B4 | 🟠 | **Edición de hidráulica inconsistente**: la pantalla abre en la 5ª y el Excel usa el ajuste del pozo (por defecto 4ª) | `reporte_hidraulica.js` (`hdEdicion='5'`) · `reporte_excel.py` | Que la pantalla arranque con el ajuste del pozo, o cambiar el default del modelo a `True` (decisión del usuario: "5ª por defecto") |
| B5 | 🟠 | **Borrar un reporte no valida la línea de tiempo**: si tenía tickets de entrada, los días posteriores quedan con stock negativo y los costos de esos días pasan a 0 en silencio | `api_reporte_diario_eliminar` | Simular mallas y volumetría del pozo antes de borrar y rechazar si falla, o advertir |
| B6 | 🟠 | Los **costos se ponen en 0 en silencio** si la volumetría o las mallas tienen error (el reporte final sí lo avisa) | `resumen_costos` | Mostrar un aviso en la tarjeta de costos |
| B7 | 🟢 | La **ecuación de sólidos M-I / API** se guarda, pero no cambia el cálculo | `ReporteDiarioMudCheck` | Implementar la variante API o quitar la opción |
| B8 | 🟢 | En WBM no se calcula `HGS lb/bbl` en la pestaña 3 (el análisis por equipo sí lo calcula) | `calcular_solids_analysis_wbm` | Agregar `self.hgs_ppb = hgs_pct × 3.5 × GE_HGS` |
| B9 | 🟢 | **Survey**: si la primera estación no está en MD = 0, su desplazamiento horizontal no entra en los acumulados, y la "sección vertical" es el desplazamiento total (no se proyecta sobre un azimut) | `calcular_survey_curvatura_minima` | Insertar una estación virtual en (0, 0, 0) y, si hace falta, agregar el azimut de sección vertical |
| B10 | 🟢 | La hidráulica **no descuenta ΔP de MWD ni del motor**, y suma el caudal de las **bombas del riser** | `views_hidraulica.py` | Sumar `dp_mwd`/`dp_motor` al total y excluir `riser_pump` del caudal por la sarta |
| B11 | 🟢 | El **sistema de unidades** del pozo no convierte nada: todo se calcula y muestra en unidades de campo (excepción: las concentraciones se muestran también en kg/m³ y los volúmenes del reporte de concentraciones en m³) | global | Documentado. Implementar conversión o limitar las opciones a *Standard Oilfield* |
| B12 | 🟢 | En la barra lateral, "Reportes Diarios" y "Fosas / Volumetría" no tienen enlace | `componentes/sidebar.html` | Enlazarlos o quitarlos |
| B13 | 🟢 | Falta el logo del Excel: no existe `static/operaciones/img/logo_reporte.png` | `reporte_excel.py` | Agregar la imagen (el código ya la usa si existe) |
| B14 | 🟢 | `seed_data.py` y `seed_propiedades.py` importan `mychapala` y `reportes`, que ya no existen | raíz | Adaptarlos a `operaciones` o borrarlos |
| B15 | 🟢 | Dos convenciones de respuesta JSON (`success` en `views.py`, `ok` en el resto) | vistas | Unificar al refactorizar |
| B16 | 🟢 | `catalogos_maestros.html` usa `?v={% now %}`, que descarga JS y CSS en cada visita | plantilla | Usar `_version_estaticos()` como el reporte diario |
| B17 | 🟢 | El número de reporte se recalcula: insertar o borrar un reporte intermedio **cambia los números** de los siguientes | `ReporteDiario.numero_reporte` | Decidir si debe ser fijo; si sí, guardarlo en un campo |

---

## C. Seguridad

> El sistema hoy está pensado para **uso local en un solo equipo**. Antes de publicarlo en una red o en internet, hay que atender **todo** lo siguiente.

| # | Riesgo | Detalle | Acción |
|---|---|---|---|
| S1 | 🔴 **Sin autenticación** | Ninguna vista exige inicio de sesión: cualquiera con acceso a la URL puede ver, crear y borrar | `LoginRequiredMiddleware` (Django 5.1+) o `@login_required`, y usuarios por rol |
| S2 | 🔴 **CSRF desactivado** | 69 vistas de escritura con `@csrf_exempt`, aunque el frontend ya envía el token | Quitar `@csrf_exempt` gradualmente y probar cada pantalla |
| S3 | 🔴 **`SECRET_KEY` en el código** y `DEBUG = True`, `ALLOWED_HOSTS = ['*']` | `chapala/settings.py` | Leerlos del `.env` y en producción poner `DEBUG=False` con hosts explícitos |
| S4 | 🟠 **`.env` con la contraseña real** dentro de la carpeta | Está en `.gitignore` (bien), pero viaja en los zips del proyecto | No compartir zips con el `.env`. **Si el zip se compartió fuera del equipo, cambiar la contraseña de PostgreSQL** |
| S5 | 🟢 Mensajes de error internos | Algunas vistas devuelven `str(e)` al cliente | Registrar el error y devolver un mensaje genérico |

---

## D. Deuda técnica y limpieza

- **Archivos sobrantes** (ningún código los importa): `operaciones/models-1.py`, `views-1.py`, `admin-1.py`, `componentes/sidebar-1.html`, la carpeta `proyecto chapala - claude/` (incluye un `files.zip`) y `RESUMEN_AVANCE.txt` (describe una versión que ya no existe). Moverlos a una carpeta de archivo fuera del proyecto.
- **Carpeta de plantillas `avances_19_sep/`**: el nombre es temporal. Renombrar, por ejemplo a `reporte_diario/`, junto con los `render()` que la usan.
- **`reporte_diario_detalle.html` tiene unas 5.300 líneas** con el JS de las pestañas 1 a 5 en línea. Para mantenerlo mejor, extraerlo a `reporte_general.js`, `reporte_bombas.js`, etc., siguiendo la regla "un JS por pestaña".
- **Sin pruebas automáticas**: no hay `tests.py`. Los motores (`geometria_pozo`, `hidraulica`, `control_solidos`, `volumetria`) son funciones puras y fáciles de probar. Conviene fijar como pruebas los ejemplos verificados del manual: Gusher #2, mecha 1435 psi, centrífuga 9,2, retención 169,38 g/kg y, desde el 27-sep, los de [20](20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md) (concentraciones 13,64 / 15,20 / 15,83; side track 62 y 113 bbl; piloto 438 m y 109 bbl). Ver [19](19_GUIA_MANTENIMIENTO.md).
- **Reporte final**: recalcula la volumetría del pozo una vez por día (en memoria). Con pozos de varios cientos de reportes puede tardar; si hace falta, guardar un resumen diario en caché.
- **Datos de prueba en PostgreSQL**: registros como *"Diegui 2"*, *"PIPE PARAO"*, etc. **Limpiar antes de entregar a AOS.**

---

## E. Pendientes y decisiones abiertas

| Tema | Estado |
|---|---|
| Correr `migrate` (**0022** side track y **0023** reporte final) y probar todo lo del 27-sep en pantalla | Pendiente del usuario |
| **Prueba final** por las personas encargadas de AOS, antes del curso a los ingenieros | Pendiente |
| Confirmar con el ingeniero el paquete de entrega: reporte principal, inventario, concentraciones y volumetría | Pendiente |
| ¿El comentario del **reporte de propiedades** debe quedar guardado en el sistema? | Hoy no se guarda (se escribe e imprime). Preguntar al ingeniero |
| Campo **"Unidades"** en la renta de equipos y bloqueo por cantidad del almacén | Pendiente (hoy deja poner 7 con 5 en almacén porque el campo no existe) |
| Indicadores **API RP 13C** de la pestaña 6 (SP, sólidos perforados, dilución) | Standby hasta que el usuario consiga las fórmulas |
| **SUS** y **DWM** | Sin información en el manual; el botón SUS queda deshabilitado |
| **Screen Usage** y **Reset** de ONE-TRAX | No implementados |
| Confirmar con AOS los **códigos de costo diario 1-4** | Pendiente |
| Tarjetas "Próximamente" de la pantalla principal (RDF, Completación, Desechos, Resumen de costos) | Sin construir |
| Estado **CERRADO** del pozo | Existe en el modelo, sin pantalla |

### Resuelto el 27-sep-2026

- **Reporte de concentraciones** (pantalla con lb/bbl ↔ kg/m³ y cantidad agregada; hoja "Concentraciones" en el Excel).
- **Contabilidad de volumen** comparada con el *Mud Volume Accounting* de ONE-TRAX; balance y hoyo sin decimales.
- **Side track** (kick-off del día, tipo de intervalo "Side Track", hoyo perforado correcto) y **ampliación de hoyo piloto**. Migración 0022.
- **Reporte corto de propiedades del lodo** (botón en la pestaña 3, página imprimible → PDF).
- **Reporte final del pozo (recap)** en **Excel o PDF** a elección, con secciones seleccionables y conclusiones/recomendaciones guardadas en el pozo (`RecapPozo`, migración 0023; `recap_pozo.py`, `views_recap.py`).
- **Redondeo en pantallas**: volúmenes de balance, hoyo y pérdidas sin decimales (pestaña 8), tarjetas de volumen de la pestaña 4 en enteros con el valor exacto en el tooltip; *No contabilizado* y fosas con 1 decimal; costos sin cambios.
- Error en la hoja a lápiz del ingeniero (ejemplo 3 de concentraciones: 15,83, no 16,7) — **avisarle**.
