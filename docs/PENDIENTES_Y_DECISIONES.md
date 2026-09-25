# Pendientes, decisiones y errores conocidos

Estado al cierre del proyecto (**23/09/2026**). Este documento reúne:

1. las decisiones de diseño que tomó el usuario y que explican por qué el sistema se comporta como se comporta,
2. los errores reportados por el usuario (`Lista de Posibles Bugs, cosas por revisar.md`, 24/09/2026) con su diagnóstico,
3. los problemas encontrados al revisar el código para escribir esta documentación,
4. lo que quedó sin construir o en espera (standby).

---

## 1. Decisiones del usuario

| Tema | Decisión | Dónde se ve |
|---|---|---|
| Inventario | **Uno solo** (`Producto.cantidad`) para almacén y todos los pozos; tickets de productos solo registro; consumos anteriores al 25/09/2026 no se descuentan de nuevo | `views_inventario._mover_stock`, migración 0022 |
| Unidades del pozo | Se eligen en el wizard y **no se pueden cambiar** después de activar el pozo | `Pozo.unidades_bloqueadas`, `PozoPaso2Form` |
| Moneda | Queda fija al activar el pozo. La tasa de impuesto sí se puede editar después | Configuración General no expone la moneda |
| Spud Date | La primera fecha de datos y el tipo de fluido inicial se confirman **una sola vez** | `PozoSpudDateForm` |
| Diámetros de la sarta | Al elegir un componente del catálogo se autocompletan, pero **siguen siendo editables** ("esos números podrían ser modificables") | `ComponenteSarta`, pestaña 4 |
| Distribución de tiempo | Si el total de horas no coincide con las horas del período, la pantalla avisa en rojo **pero deja guardar** ("en campo siempre pasa algo distinto") | `ReporteDiarioTiempo`, pestaña 7 |
| Período del reporte | 24 h por defecto, editable para días especiales (inicio, fin, cambio de hora de corte). Máximo 48 h | `TIEMPO_HORAS_MAXIMAS` |
| Pérdidas en el reporte | La selección de las (máximo) 10 categorías que salen impresas es **por pozo**, no por reporte | `PerdidaReportePozo` |
| Tipos de ticket de mallas | El usuario no sabía qué tipos maneja AOS, así que se siembran 4 de ejemplo **editables** | `TipoTicketMalla.TIPOS_EJEMPLO` |
| Tickets de productos | Usan los **mismos tipos** de ticket que las mallas | `TicketProducto.tipo` |
| Módulos opcionales | IFE, análisis de sólidos, retención en recortes y eventos no programados se construyeron completos, pero AOS **al parecer no los usa**. Si están vacíos no afectan ningún cálculo | `models_opcionales.py` |
| Volumen real | El volumen real de una fosa es lo que se midió; **no se ajusta para cuadrar el balance** (regla del manual ONE-TRAX). La diferencia se muestra como "No contabilizado" | `volumetria.py` |
| Listas del pozo | Se guardan borrando y recreando las filas; por eso los datos diarios guardan número o código + copia del texto | [ARQUITECTURA.md](ARQUITECTURA.md) |

---

## 2. Errores reportados por el usuario

### 2.1 Marca y modelo en la pestaña de bombas

**Síntoma:** el campo "Marca y Modelo" parece un menú con muchas bombas, pero al abrirlo solo aparece la que ya está escrita.

**Diagnóstico:** no es un menú (`<select>`). Es un campo de texto con una lista de sugerencias (`<datalist id="lista-modelos-bombas">`, 15 modelos: EMSCO, National, Gardner Denver, Ideco, Wirth, Weatherford). El navegador **filtra** las sugerencias con el texto que ya tiene el campo: si dice "EMSCO F-1000", solo sugiere "EMSCO F-1000". Si se borra el campo, aparecen todas. Lo que se escribe se guarda tal cual (texto libre), por eso cambiar el nombre funciona.

Las 4 bombas son fijas: el formulario y el guardado recorren siempre las bombas 1 a 4.

✅ **Corregido (25/09/2026):** al entrar al campo se vacía y aparecen los 15 modelos; si no se elige nada, al salir vuelve el valor anterior.

### 2.2 El inventario de la pestaña 8 muestra 0 aunque el Inventario general tiene existencias

**Diagnóstico:** había dos inventarios. La pestaña 8 nunca leía `Producto.cantidad`: cada pozo empezaba en 0 y solo subía con tickets de recepción.

✅ **Corregido (25/09/2026) — inventario unificado.** Decisiones del usuario:

- `Producto.cantidad` es la **única existencia**. Los consumos del reporte diario (químicos, lodo entero, usado en otro módulo, ajustes) la descuentan; deshacer o borrar el reporte la devuelve.
- Los tickets de productos son **solo registro**.
- Los consumos registrados antes del cambio **no se descontaron otra vez** (la cantidad de ese día se tomó como correcta).

Detalle en [inventario/FLUJOS.md](inventario/FLUJOS.md#relación-con-el-inventario-del-pozo-pestaña-8). Migración `0022_inventario_unificado`.

### 2.3 Hojas del Excel repetidas y vacías

**Síntoma:** al descargar el Excel aparecen hojas que se repiten sin datos. Se sospechaba que eran otros pozos.

**Diagnóstico:** el Excel **no mezcla pozos**: `generar_reporte_excel(pozo, reporte)` trabaja solo con el pozo y el reporte abiertos. Lo que se ve es el formato del libro ONE-TRAX, que trae:

- **Tres hojas de inventario químico** con los mismos datos en distinto orden o filtro: "Inv Quimico (DF)" (solo con movimiento y sin "no imprimir"), "Inv Quimico (por nombre)" (la misma, ordenada por nombre) y "Inv Quimico (completo)". Con el inventario en 0 (ver 2.2) las tres salen vacías y parecen repetidas.
- Cada hoja de inventario tiene hasta 3 páginas de 50 productos con encabezado repetido.
- "Equipos" e "Inventario de Mallas" salen vacías si no hay uso de equipos ni mallas ese día.

Las hojas de lodo y de propiedades extra que no corresponden al tipo de lodo del reporte sí se eliminan.

✅ **Corregido (25/09/2026):** las hojas de inventario químico sin productos, "Equipos" sin equipos e "Inventario de Mallas" sin mallas se quitan del libro.

---

## 3. Problemas encontrados en la revisión del código

| # | Problema | Efecto | Corrección |
|---|---|---|---|
| 3.1 | `Pozo.clonar_configuracion_desde_plantilla()` hace `self.unidades_personalizadas = origen.unidades_personalizadas`. En Django no se puede asignar directamente a una relación inversa | Crear un pozo **usando otro como plantilla** probablemente falla con `TypeError` en el paso 1 | ✅ **Corregido (25/09/2026).** Se quitó la línea |
| 3.2 | El paso 1 del wizard dice que la plantilla "copia mallas, productos, tanques y configuración de pérdidas", pero el código solo copia configuración, unidades, categorías de pérdida, fosas y tipos de fosa | Productos, equipos y mallas activos hay que cargarlos a mano en el pozo nuevo | ✅ **Corregido (25/09/2026).** `Pozo.clonar_listas_activas()` copia productos, equipos y mallas activos con sus precios |
| 3.3 | Código de equipo de superficie: la pestaña 2 numera **1 = manual** y **2 a 5 = casos estándar**; `hidraulica.py` usa **1 a 4 = casos API** (2600, 946, 610 y 424 ft equivalentes). Además, "manual" solo funciona si se llenan presión **y** caudal de referencia | Elegir en pantalla el caso 2 calcula con el caso API 2 en vez del 1 (y así con los demás); el código 5 no calcula nada; el código 1 sin caudal de referencia calcula como caso API 1 | ✅ **Corregido (25/09/2026).** `hidraulica.py` usa `{'2': 2600, '3': 946, '4': 610, '5': 424}`; el código 1 usa la presión escrita tal cual (sin presión: 0 y aviso) |
| 3.4 | El primer reporte de un pozo crea bombas, mecha, boquillas y **4 chequeos de lodo con datos de ejemplo** (lodo de 10.5 lb/gal, reología completa en el chequeo 1). Esos valores se heredan a los días siguientes | Hidráulica y benchmark calculan con datos inventados si el ingeniero no los reemplaza | Crear los chequeos vacíos (dejar solo número y hora) o marcarlos visualmente como "ejemplo" |
| 3.5 | `Iniciar Sistema.bat` usa `.\env\Scripts\python.exe`, pero el entorno está en `.venv\` | El doble clic falla si no existe la carpeta `env` | ✅ **Corregido (25/09/2026).** |
| 3.6 | `seed_data.py` y `seed_propiedades.py` importan `mychapala` y `reportes` (apps en `_legacy/`, no instaladas). `seed_data.py` además usa `gravedad_especifica`, que hoy se llama `gravedad` | Los scripts no corren | ✅ **Corregido `seed_data.py` (25/09/2026):** usa `operaciones.models.Producto` y solo crea productos que no existen (no pisa existencias). `seed_propiedades.py` sigue pendiente de mover a `_legacy/` |
| 3.7 | `pozos_list.html` muestra `pozo.operador` y `pozo.spud_date`, que no existen en `Pozo` (están en `WellHeaderInfo`) | Las tarjetas siempre dicen "Operador no definido" y nunca muestran el Spud | ✅ **Corregido (25/09/2026).** |
| 3.8 | La pestaña 1 permite cambiar la **fecha** del reporte sin revalidar | Si se pone una fecha que ya existe, el error llega como texto técnico de la base de datos; mover un reporte de lugar cambia el orden de la línea de tiempo sin validar mallas ni volumetría | ✅ **Corregido (25/09/2026).** Se valida el formato y que la fecha no exista; al cambiarla se revalidan mallas y volumetría dentro de una transacción y se deshace si algún día deja de cuadrar |
| 3.9 | La pantalla principal del pozo marca "Registro Direccional" como "Próximamente", pero la API de survey (`/api/pozos/<pk>/survey-stations/`) ya existe y se usa desde el reporte | Confusión | ✅ **Corregido (25/09/2026).** La tarjeta lleva al historial de reportes y muestra cuántas estaciones hay |
| 3.10 | Copias viejas en el código: `operaciones/admin-1.py`, `models-1.py`, `views-1.py`, `componentes/sidebar-1.html`; carpeta raíz `reportes/` con solo `__pycache__` | Ruido; riesgo de editar el archivo equivocado | Borrar |
| 3.11 | `api_producto_delete` no captura `ProtectedError`. Un producto con cantidad 0 que está activo en un pozo (o se usó en movimientos) no se puede borrar por `PROTECT`, y la API responde con error 500 | El usuario ve "Error de red al intentar eliminar" sin explicación | ✅ **Corregido (25/09/2026).** Responde 400 con el nombre de los pozos donde está activo |
| 3.12 | Seguridad: `DEBUG = True`, `ALLOWED_HOSTS = ['*']`, `SECRET_KEY` en el código, sin inicio de sesión, APIs con `@csrf_exempt` | Aceptable solo en un equipo local | Corregir antes de publicar en red |

---

## 4. Pendiente o en espera (standby)

### Módulos marcados "Próximamente" en la pantalla principal del pozo

- Eventos No Programados (como pantalla del pozo; hoy se capturan desde las pestañas 5 y 7 del reporte)
- Resumen de Costos (como pantalla del pozo; hoy existe el modal de costos en la pestaña 1)
- Módulo RDF
- Fluidos de Completación
- Tratamiento y Disposición de Desechos

### Barra lateral

- "Reportes Diarios" y "Fosas / Volumetría" no llevan a ningún lado (se llega a ambos desde el pozo).

### Funcionalidad

| Tema | Estado |
|---|---|
| Sistema de unidades | Se guarda la elección (incluido el modo personalizado por propiedad), pero **todos los cálculos y pantallas trabajan en unidades de campo** (ft, in, bbl, gpm, lb/gal, psi). No hay conversión |
| Códigos de mercadeo | Se capturan código y descripción a mano; falta el catálogo |
| Costo total del pozo | `WellHeaderInfo.total_cost` es manual |
| Columna "Otros" de costos (DWM/CF) | Siempre 0; no hay módulo que la alimente |
| Corrección de reología por temperatura y presión (5ª edición) | No se hace: requiere lecturas del viscosímetro a varias temperaturas que el reporte no captura |
| Lodo en recortes (retención) | Reconstrucción propia; en el ejemplo del manual da ~1.5 % más que ONE-TRAX |
| Reporte de almacén de la app antigua (`mychapala`): pestaña "Uso", precio variable por salida, historial de reportes de almacén, planilla impresa AOS con firmas | **No migrado** a `operaciones`. El código sigue en `_legacy/mychapala` |
| Conexión entre inventario general y de pozo | ✅ Unificado (ver 2.2). Borrar un **pozo completo** desde `/admin/` no devuelve la existencia; borrar sus reportes uno por uno sí |
| Pruebas automáticas | No hay pruebas en `operaciones` (solo `_legacy/mychapala/tests.py`) |
