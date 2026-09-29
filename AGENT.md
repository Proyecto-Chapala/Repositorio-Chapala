# AGENT.md — Leer primero (Proyecto CHAPALA)

Si eres un asistente que empieza una conversación nueva sobre el **Proyecto CHAPALA** (sistema Django estilo ONE-TRAX para All Oil Services, C.A.), **antes de responder o tocar código lee los documentos en este orden**.

La documentación completa está en el **Proyecto de Claude "Totalizador"** (claude.ai → Proyectos). Si trabajas desde ahí, léela con la herramienta de Proyectos; las rutas son las de abajo.

1. **`claude/chapala-traspaso-siguiente-conversacion.md`**: estado actual, dónde está cada archivo, la **cadena de migraciones** (la próxima debe depender de `0024_merge`) y las **reglas de trabajo** del usuario.
2. **`docs/16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md`**: qué falta, bugs conocidos, riesgos y lo ya resuelto.
3. **El documento del tema que se vaya a tocar**:

| Tema | Documento |
|---|---|
| Concentraciones, side track, hoyo piloto | `docs/20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md` |
| De dónde salió cada decisión del 27-sep (análisis de imágenes y audios) | `docs/21_ANALISIS_MATERIAL_REVISION_27SEP.md` |
| Pestaña 8 (volumetría, inventario, concentraciones) | `docs/09_PESTANA_8_VOLUMETRIA_INVENTARIO.md` |
| Pestañas 1 a 5 | `docs/06_REPORTE_DIARIO_PESTANAS_1_A_5.md` |
| Pestaña 6 (control de sólidos) | `docs/07_PESTANA_6_CONTROL_SOLIDOS.md` |
| Pestaña 7 (tiempo) | `docs/08_PESTANA_7_DISTRIBUCION_TIEMPO.md` |
| Hidráulica | `docs/10_HIDRAULICA_API13D.md` |
| Fórmulas de geometría, sólidos, survey | `docs/11_CALCULOS_INGENIERIA.md` |
| Excel diario | `docs/14_REPORTE_EXCEL.md` |
| Costos | `docs/13_COSTOS.md` |
| Modelos / URLs / arquitectura | `docs/03_MODELO_DATOS.md`, `docs/04_API_ENDPOINTS.md`, `docs/02_ARQUITECTURA.md` |
| Cómo lo usa el ingeniero | `docs/MANUAL_USUARIO.md` |
| Instalación y arranque | `docs/01_INSTALACION_Y_EJECUCION.md` |
| Índice general | `docs/README.md` |

## Reglas que no se negocian

- **Traer siempre el archivo actual del disco antes de editarlo** (`C:\Users\Admin\Documents\Proyectos\Proyecto CHAPALA`). Un compañero también sube cambios por git. Archivos con CRLF.
- Desde la nube no hay Django ni shell en la máquina del usuario: se valida con `ast.parse`, `node --check` y pruebas de funciones puras; **el usuario corre `migrate` y git** (rama `Refactorizacion`).
- Todo el texto visible en **español**; CSS y JS en archivos aparte, nunca en línea.
- Ir por partes; ante la duda, pedir o revisar la captura del manual ONE-TRAX antes de inventar.
- Si el usuario comparte una imagen del manual, analizarla y **dejar el análisis documentado** en `docs/` (como se hizo en el 21).
- Al terminar un cambio: actualizar el traspaso, el 16 y el documento del tema.
