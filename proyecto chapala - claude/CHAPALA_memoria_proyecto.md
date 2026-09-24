# CHAPALA — Memoria y contexto del proyecto

> Actualizado: 24-sep-2026. Reemplaza la versión anterior de este archivo (que describía solo el asistente de pozo).
> Léelo completo antes de tocar código. Las próximas sesiones serán sobre todo **ajustes, parches, adiciones y manuales**:
> el grueso del sistema (configuración del pozo + las 8 pestañas del reporte diario + Excel) ya está construido.

---

## 1. Qué es

Sistema Django para **All Oil Services (AOS)** que replica el módulo **"Drilling Fluids and Equipment"** de ONE-TRAX
(M-I SWACO): configuración del pozo + reporte diario de fluidos de perforación y equipos en 8 pestañas + reporte Excel
con el formato del libro de ONE-TRAX. Todo en español, con una UX de menos clics que el original.

- Carpeta: `C:\Users\Admin\Documents\Proyectos\Proyecto CHAPALA`
- Git: rama `Refactorizacion`, remoto `github.com/Proyecto-Chapala/Repositorio-Chapala`. El equipo (p. ej. el compañero "xtal") también sube cambios.
- Python 3.14, Django 6.1.1, `openpyxl`. BD: PostgreSQL `chapala_db` (existe también `db.sqlite3`; revisar en `.env` cuál está activa).
- Arranque: `.venv` + `python manage.py runserver` (el `Iniciar Sistema.bat` apunta a `.\env\`, no a `.venv`).
- Manual ONE-TRAX de referencia: analizado completo hasta la pág. 151 ("End of Drilling Fluids and Equipment module").

---

## 2. Reglas de trabajo (obligatorias)

1. **Todo el texto visible en español** (etiquetas, botones, columnas, mensajes, placeholders, Excel). Excepciones: nombres propios (ONE-TRAX, M-I SWACO, Log-It).
2. **Antes de editar un archivo, volver a leerlo del disco** (el equipo sube cambios por git).
3. **Reutilizar el código existente** si cumple el objetivo; no duplicar.
4. **CSS y JS en archivos aparte**, uno por pestaña/módulo, nunca en línea.
5. Buen diseño, opciones bien ordenadas, ir segmento por segmento; ante la duda, revisar las capturas del manual antes de inventar.
6. Si el usuario pide "analizar" o "un layout primero", no tocar código hasta que diga que se construya.
7. Los archivos usan **CRLF** (Windows): conservarlo al escribir.
8. Los mensajes de error al usuario deben ser claros y en español, diciendo qué dato falta y en qué pestaña.

---

## 3. Arquitectura

- Una sola app: `operaciones`. Vistas basadas en funciones + `JsonResponse` (sin DRF). Frontend vanilla JS tipo SPA.
- La app está en la raíz del sitio (sin prefijo `/operaciones/` en los fetch).
- Guardado del reporte: al cambiar de pestaña, `switchTab()` guarda la pestaña que se deja (modo silencioso: oculta el aviso de éxito, nunca los errores). Botón "Guardar Cambios" → `guardarPestanaActiva()`.
- Anti-caché de estáticos: `_version_estaticos` (en `views.py`) versiona por fecha de modificación; la lista de archivos está en `reporte_diario_detalle_view` (`views_daily_reports.py`). **Cada CSS/JS nuevo del reporte debe agregarse a esa lista.**
- Inputs numéricos en plantillas: siempre con `|unlocalize` (el locale español escribe `7023,5` y el `<input type=number>` lo deja vacío → se guardaba 0).

### Patrones de datos

- **Catálogos maestros globales** (editables por pantalla "Catálogos Maestros", nunca por el admin): `Producto` (del módulo Inventario), `Equipo` (con `tipo_equipo` y `posiciones_malla`), `MallaZaranda`, `PropiedadEquipoTipo`, `ParametroBenchmark`, `ComponenteSarta`.
- **Listas activas por pozo** (`ProductoActivoPozo`, `EquipoActivoPozo`, `MallaActivaPozo`, `Fosa`, `TipoFosa`, `AlmacenCodigo`, `TipoDistribucionTiempo`, `CategoriaPerdidaItem`, propiedades de equipos, benchmark): se guardan **borrando y recreando filas**. Por eso **los datos diarios nunca hacen FK a una lista activa**: referencian el catálogo maestro (`Producto`, `Equipo`, `MallaZaranda`) o un número/código (fosa, tipo de fosa, categoría de pérdida, serie del equipo) **más una copia del texto**.
- **Sembrar estándar** (`sembrar_estandar`): TipoFosa (1 Activa, 2 Reserva, 3 Premix…), CategoriaPerdidaItem (15 estándar), TipoDistribucionTiempo (20 estándar). Tipos de ticket: `TipoTicketMalla.sembrar_ejemplos`.
- **Motores puros** (sin Django, testeables): recalculan TODA la línea de tiempo del pozo. Cada escritura simula hasta el último reporte y hace rollback con mensaje en español si algo no cuadra.

---

## 4. Mapa de archivos (`operaciones/`)

| Área | Archivos |
| --- | --- |
| Modelos | `models.py` (Pozo, WellHeaderInfo, IntervaloRevestimiento, Fosa, catálogos, listas activas; al final importa `models_opcionales`), `models_daily_reports.py` (ReporteDiario, bombas, boquillas, bit_data, mud_checks, sarta, comentarios, tiempo, propiedades extra), `models_control_solidos.py`, `models_inventario.py`, `models_opcionales.py` |
| Motores | `geometria_pozo.py` (volúmenes del hoyo), `control_solidos.py` (mallas, rendimiento de equipos), `volumetria.py` (volúmenes, inventario, concentraciones, costos), `hidraulica.py` (API RP 13D 4ª y 5ª) |
| Vistas | `views.py` (pozo, asistente, configuración, catálogos), `views_daily_reports.py` (reporte diario, pestañas 1-5 y 7, costos, Excel), `views_control_solidos.py` (pestaña 6), `views_inventario.py` (pestaña 8 + `resumen_costos()`), `views_hidraulica.py`, `views_opcionales.py` |
| Excel | `reporte_excel.py` + `plantillas/reporte_diario_onetrax.xlsx` (+ `plantillas/crear_plantilla.py`) |
| Plantilla del reporte | `templates/operaciones/avances_19_sep/reporte_diario_detalle.html` (8 pestañas), `daily_reports_hub.html` |
| Estáticos del reporte | `static/operaciones/js|css/`: `reporte_tiempo.*`, `reporte_control_solidos.*`, `reporte_inventario.*`, `reporte_hidraulica.*`, `reporte_opcionales.*` |
| Migraciones | 0014 geometría/riser, 0015 comentarios, 0016 tiempo, 0017 mallas, 0018 uso de equipos, 0019 pérdidas del reporte, 0020 volumetría, 0021 opcionales — **todas aplicadas (24-sep)** |

---

## 5. Qué está construido

### Configuración del pozo
Asistente de 4 pasos (borrador → activo; unidades y moneda bloqueadas al confirmar), Fecha de Inicio de Captura (una sola vez), Pantalla Principal, Información General (offshore, riser, temperatura superficial y gradiente, códigos de mercadeo), Intervalos de Revestimiento, Fosas y Tipos, Pérdidas, Productos/Equipos/Mallas Activos, Propiedades de Equipo, Benchmark (2 pasos), Configuración General (impuesto, almacenes, distribución de tiempo, "Usar API 5ta Edición"), Catálogos Maestros (5 pestañas).

### Reporte diario (8 pestañas)
1. **General**: profundidad, TVD, barrena, actividad, litología, survey, representantes, balance económico (lectura).
2. **Bombas y Barrenas**: bombas (desplazamiento = 0,000243·camisa²·carrera·eficiencia), boquillas y TFA, código de superficie 1-5, barrena.
3. **Propiedades del Lodo**: hasta 4 chequeos (#1 principal = último del día), reología, análisis de sólidos WBM/OBM (ecuaciones M-I/API).
4. **Geometría**: sarta (fila 1 = abajo), intervalo de costo, hoyo piloto, volúmenes calculados en vivo (verificado contra el manual; ponderación por juntas con tramo de 31 ft).
5. **Comentarios**: especificación (se hereda), resumen del día (una línea), observaciones.
6. **Control de Sólidos**: inventario de mallas (derivado), tickets (según ticket vs real), transacciones (instalar nueva/usada, pasar al almacén, desechar; "Deshacer último"), detalle y uso de equipos (rendimiento, renta por `EquipoActivoPozo.precio_renta/precio_standby`, paradas). Sin stock de mallas nuevas → bloquea.
7. **Distribución de Tiempo**: horas del período 24 editable; si no cuadra → rojo pero guarda.
8. **Inventario/Hidráulica/Concentraciones**: volumetría (fosas con tipo del día y volumen REAL, fluido en el hoyo, movimientos al instante: químicos, lodo entero, transferencia/devolución/pérdida, deshacer), balance por grupo y "No contabilizado", pérdidas por categoría (máx. 10 en el reporte, selección por pozo), inventario de productos, concentración, hidráulica, benchmark.

### Reglas del motor de volumetría
- Grupos por código de tipo de fosa: 1 → ACTIVO, 2 → RESERVA, 3 → PREMEZCLA, otro → OTRAS, 0/None → fuera. El sistema activo incluye el hoyo.
- Volumen de químico = masa/(S.G. × 350), solo para unidades de masa (LB, KG, TN…).
- Producto sin unidad = **servicio**: genera costo, no lleva existencias (días de ingeniero, en "Usado otro módulo").
- Inventario negativo en cualquier día → se rechaza.
- Lleva acumulados por producto (`usado_acum`, `recibido_acum`, `devuelto_acum`) y transferencias entre grupos (`flujos[g]['hacia_<grupo>']`), usados por el Excel.

### Costos (`views_inventario.resumen_costos`)
Códigos de costo diario del producto: 1 Químicos, 2 Ingeniero de fluidos, 3 Ingeniero de control de sólidos, 4 Ingeniero IFE (**falta que AOS lo confirme**). Columnas: `df_chem` = 1+2, `ife_sc` = 3+4, `df_equip` = renta de equipos + mallas nuevas instaladas, `other_cost` = 0. Alimenta la pestaña 1, el modal Resumen de Costos y el Excel.

### Hidráulica (`hidraulica.py`, `views_hidraulica.calcular_hidraulica_reporte`)
4ª ed.: ley de potencia (tubería 600/300, anular 100/3). 5ª ed.: Herschel-Bulkley, τy = 1,066(2R3−R6), temperatura anular por gradiente. Mecha: ΔP = ρQ²/(10858·TFA²), HHP = ΔP·Q/1714, velocidad de chorro = 0,3208·Q/TFA (verificado con el manual: 1435 psi, 672 HHP, HSI 5,7, 373 ft/s). La API acepta `?edicion=4|5`; sin parámetro usa `pozo.usar_api_5ta_edicion_hidraulica`.

### Módulos opcionales (100 % opcionales, no afectan nada)
Observaciones IFE, Análisis de sólidos por equipo, Retención en recortes (pestaña 6), Eventos No Programados (botón en pestañas 5 y 7; se editan solo desde su reporte), Evaluación de benchmark (pestaña 8: objetivo + rango real mín–máx + % dentro, por pozo completo y por intervalo).

### Reporte Excel (`reporte_excel.generar_reporte_excel`)
Llena la plantilla hecha desde el Excel real de ONE-TRAX (Mud Report 16 PERLA-1X) traducida al español. Hojas: reporte de lodo según `reporte.tipo_lodo` (WBM, WBM_CACL2 → CALDRIL, OBM, SBM), propiedades extra (etiquetas 1-8 en el reporte, 9-60 en la hoja extra), contabilidad de volumen, inventario químico (DF, por nombre, completo; hasta 150 productos en 3 páginas), equipos, mallas. Toma los datos de los mismos motores que las pestañas. Logo opcional: `static/operaciones/img/logo_reporte.png`. Para regenerar la plantilla: `python plantillas/crear_plantilla.py <original.xlsx> <destino.xlsx>`.

---

## 6. Lo que FALTA / pendiente (lo importante)

| # | Tema | Estado |
| --- | --- | --- |
| 1 | Campo "Unidades" en renta de equipos y bloqueo por cantidad disponible en almacén (hoy con 5 en almacén deja registrar 7+) | **Pendiente** (decisión del usuario) |
| 2 | Indicadores API RP 13C de la pestaña 6 (SP, sólidos perforados promedio, lodo agregado / volumen perforado) | **En espera** de las fórmulas del usuario; se muestran "—" |
| 3 | SUS (pruebas de cumplimiento) y DWM | Sin información en el manual; botón SUS deshabilitado |
| 4 | "Screen Usage" y "Reset" de ONE-TRAX | No implementados (propósito desconocido) |
| 5 | Confirmar con AOS los códigos de costo 1-4 | Pendiente |
| 6 | Excel: "Inerte/Reactivo" (base agua) y "GE de la Salmuera" (CALDRIL) | En blanco, fórmulas desconocidas |
| 7 | Hidráulica: pérdidas en sarta/anular no verificables con el manual; MOC de retención reconstruido | Validar con datos reales |
| 8 | Pantalla Principal del Pozo: Registro Direccional, Eventos No Programados y Resumen de Costos marcados "Próximamente" (funcionan dentro del reporte) | Pendiente de enlazar |
| 9 | Módulos RDF, Fluidos de Completación, Tratamiento y Disposición de Desechos | Sin analizar |
| 10 | Limpiar datos de prueba de la BD (y la descripción del DC-8.5) | Pendiente |
| 11 | Selector de edición de hidráulica en pantalla: arranca en 5ª; podría arrancar según la configuración del pozo | Mejora menor |
| 12 | Commit en git de pestaña 8, hidráulica, opcionales y Excel; prueba completa con el guion de prueba | Pendiente del usuario |
| 13 | Fuera de alcance por decisión del usuario: integración DIMS | — |

---

## 7. Documentos de apoyo (en el Proyecto de Claude)

- "CHAPALA — Manual de procesos del sistema" (manual de usuario, paso a paso).
- "CHAPALA — Guion de prueba: un día de trabajo completo" (pozo POZO PRUEBA-1, dos días, con valores esperados y hoja de resultados).
- `claude/chapala-traspaso-siguiente-conversacion.md` (traspaso técnico).

---

## 8. Cómo validar cambios sin Django (entorno de Claude)

`ast.parse` para Python, `node --check` para JS, balance de `<div>` en plantillas, Playwright con `fetch` simulado para pantallas, LibreOffice (`soffice --convert-to pdf`) para revisar el Excel generado. El usuario corre `check`, `makemigrations` y `migrate` en su máquina.
