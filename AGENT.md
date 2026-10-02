# AGENT.md — Leer primero (Smart Mud, antes "Proyecto CHAPALA")

Si eres un asistente o un desarrollador que empieza a trabajar en este proyecto (sistema Django de fluidos de perforación para **All Oil Services, C.A.**), **antes de responder o tocar código lee en este orden**:

1. **`docs/00_TRASPASO.md`** — estado actual, reglas de trabajo, cadena de migraciones (la próxima depende de **`0027_intervalo_cerrado_moneda_secundaria`**) y prioridades.
2. **`docs/16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md`** — qué falta probar, decisiones abiertas, errores conocidos y lo ya resuelto.
3. **El documento del tema** (índice completo en `docs/README.md`):

| Tema | Documento |
|---|---|
| Cambios del 02-oct (Smart Mud, logos, tanques, monedas, intervalos, hub, `.exe`) | `docs/22_CAMBIOS_02OCT_SMART_MUD.md` |
| Concentraciones, side track, hoyo piloto | `docs/20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md` |
| Decisiones del 27-sep (imágenes y audios) | `docs/21_ANALISIS_MATERIAL_REVISION_27SEP.md` |
| Pestaña 8 (volumetría, inventario, concentraciones) | `docs/09_PESTANA_8_VOLUMETRIA_INVENTARIO.md` |
| Pestañas 1 a 5 y hub | `docs/06_REPORTE_DIARIO_PESTANAS_1_A_5.md` |
| Pestaña 6 / Pestaña 7 | `docs/07_…`, `docs/08_…` |
| Hidráulica / fórmulas | `docs/10_HIDRAULICA_API13D.md`, `docs/11_CALCULOS_INGENIERIA.md` |
| Excel diario / costos | `docs/14_REPORTE_EXCEL.md`, `docs/13_COSTOS.md` |
| Configuración del pozo | `docs/05_CONFIGURACION_POZO.md` |
| Modelos / URLs / arquitectura | `docs/03_MODELO_DATOS.md`, `docs/04_API_ENDPOINTS.md`, `docs/02_ARQUITECTURA.md` |
| Instalación, arranque y `SmartMud.exe` | `docs/01_INSTALACION_Y_EJECUCION.md` |
| Cómo lo usa el ingeniero | `docs/MANUAL_USUARIO.md` |

## Reglas que no se negocian

- Ruta del proyecto: **`C:\Users\SECRETARIA\Documents\Programacion\Personal\Proyecto CHAPALA`**. **Traer siempre el archivo actual del disco antes de editarlo**: un compañero también sube cambios por git. Archivos con CRLF.
- Desde la nube no hay Django: se valida con `ast.parse`, `node --check` y pruebas de funciones puras. **El usuario corre `migrate` y git** (rama `Refactorizacion`).
- Todo el texto visible en **español**; CSS y JS en archivos aparte, nunca en línea.
- **Nada de "M-I", "M-I SWACO" ni "ONE-TRAX" en pantalla ni en reportes.** Se dice **tanque** (no fosa) y **lodo reciclado** (no lodo entero). Logo de **AOS** en los reportes; **Smart Mud** es el ícono del programa.
- Ir por partes; ante la duda, revisar el manual ONE-TRAX (`documentation/`) o preguntar antes de inventar.
- Imágenes, audios o notas del cliente: guardar el original en `docs/fuentes/` y **dejar el análisis documentado** en `docs/`.
- **Toda la documentación vive en `docs/`.** No crear otras carpetas de documentación. Lo que queda viejo va a `docs/_archivo/`.
- Al terminar un cambio: actualizar `docs/00_TRASPASO.md`, `docs/16_…` y el documento del tema.
