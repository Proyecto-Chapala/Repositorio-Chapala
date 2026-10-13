# AGENTS.md — Leer primero (Smart Mud, antes "Proyecto CHAPALA")

Si eres un asistente o un desarrollador que empieza a trabajar en este proyecto (sistema Django de fluidos de perforación para **All Oil Services, C.A.**), **antes de responder o tocar código lee en este orden**:

1. **`docs/00_TRASPASO.md`** — estado actual, reglas de trabajo, cadena de migraciones (la próxima depende de **`0036_inventario_usado_fluido_manual`**) y prioridades.
2. **`docs/16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md`** — qué falta probar, decisiones abiertas, errores conocidos y lo ya resuelto.
3. **El documento del tema** (índice completo en `docs/README.md`):

| Tema | Documento |
|---|---|
| Servicios del pozo: ingenieros y trailers por día (13-oct) | `docs/25_SERVICIOS_DEL_POZO.md` |
| Papelera de pozos y revisión de la base de datos (12-oct) | `docs/24_PAPELERA_Y_TIPOS_DE_DATOS.md` |
| Correcciones de la revisión de octubre (inventario, GE, precios, trailer, sidetrack, reportito) | `docs/23_CORRECCIONES_REVISION_OCT.md` |
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

- Varios compañeros trabajan por git (rama `Refactorizacion`): **traer siempre la versión actual del archivo antes de editarlo**. Archivos con **CRLF**.
- **git y `migrate` los corre la persona**, no la IA: la IA prepara el cambio y avisa qué comando correr.
- Antes de dar un cambio por terminado: `python manage.py test operaciones` (todo debe pasar) y `python manage.py makemigrations --check` (sin cambios pendientes sin migración).
- Todo el texto visible en **español**; CSS y JS en archivos aparte, nunca en línea.
- **Nada de "M-I", "M-I SWACO" ni "ONE-TRAX" en pantalla ni en reportes.** Se dice **tanque** (no fosa) y **lodo reciclado** (no lodo entero). Logo de **AOS** en los reportes; **Smart Mud** es el ícono del programa.
- Ir por partes; ante la duda, revisar el manual ONE-TRAX (`documentation/`) o preguntar antes de inventar.
- Imágenes, audios o notas del cliente: guardar el original en `docs/fuentes/` y **dejar el análisis documentado** en `docs/`.
- **Toda la documentación vive en `docs/`.** No crear otras carpetas de documentación. Lo que queda viejo va a `docs/_archivo/`.
- Al terminar un cambio: actualizar `docs/00_TRASPASO.md`, `docs/16_…` y el documento del tema, y crear su archivo en **`docs/pruebas/`** ("Cómo funciona" + "Pasos para verificar" con casillas) agregándolo al índice `docs/pruebas/README.md`.

## Lo que NO se toca (el sistema ya está en producción de prueba)

Si un arreglo parece exigir alguno de estos cambios, **detenerse y preguntar** a la persona antes de hacerlo.

- **Migraciones ya aplicadas** (`operaciones/migrations/0001` a la última): no se editan, renombran ni borran, ni se cambian sus dependencias. Todo cambio de modelo va en una **migración nueva** que depende de la última (ver `docs/00_TRASPASO.md`). En los equipos de los ingenieros el `.exe` las aplica solo al abrir; una migración rota deja el sistema sin arrancar.
- **No borrar datos de los ingenieros.** Nada de migraciones que eliminen tablas o columnas con información, ni `RunPython` que borre filas, sin acuerdo explícito.
- **Papelera de pozos:** eliminar un pozo solo lo oculta (`Pozo.enviar_a_papelera()`). No usar `pozo.delete()` en vistas. `Pozo.objects` ya excluye los de la papelera; `Pozo.todos` los incluye. Ver `docs/24_PAPELERA_Y_TIPOS_DE_DATOS.md`.
- **Base de datos: SQLite**, decisión final. No volver a agregar PostgreSQL ni otro motor.
- **Sin licencia ni activación**: se quitó a pedido del usuario. No volver a agregarla.
- **El `.exe` arranca vacío** (sin productos ni pozos) y sin consola. No agregar cargas automáticas de datos en `empaquetado/chapala_app.py`.
- **Empaquetado** (`empaquetado/chapala_app.py`, `chapala.spec`, `Construir EXE.bat`): solo se cambia si el arreglo es del propio empaquetado. Después de cambiarlo, construir con `Construir EXE.bat`, que verifica el ejecutable antes de generar el `.zip`.
- **Nunca subir a git** `db.sqlite3`, la carpeta `datos/`, el `.env` ni `empaquetado/dist/` (están en `.gitignore`). Ahí están los datos reales.
- **Dinero e inventario en `DecimalField`**, nunca `FloatField`.

## Reglas esenciales de código (obligatorias)

Nada de parches: una solución que oculta el problema no deja el código limpio ni escalable.

- **Nombres descriptivos** para variables, funciones y clases; evitar abreviaciones ambiguas.
- **Estilo consistente** con el proyecto y sus convenciones (ver las reglas anteriores).
- **DRY**: no duplicar lógica; si dos partes hacen lo mismo, se extrae a un solo lugar.
- **KISS y YAGNI**: la solución más simple que resuelva el caso real; nada de sobreingeniería ni de código "por si acaso".
- **Diseñar para cambios futuros**: separar responsabilidades (lógica pura, datos, interfaz) para que crecer no obligue a reescribir.
- **Causa raíz, no parches**: no aplicar soluciones a corto plazo que oculten problemas; identificar por qué falla y corregir ahí.
- **Pruebas unitarias al día**: todo cambio actualiza o agrega sus pruebas, y la suite debe pasar antes de dar el cambio por terminado.
