# Smart Mud — Documentación

**Smart Mud** (*Fluid Management Software*) es el sistema web en Django de **All Oil Services, C.A. (AOS)** para los reportes diarios de fluidos de perforación y equipos, más el inventario de productos químicos. Sigue la lógica del módulo *Drilling Fluids and Equipment* del manual de ONE-TRAX, en español. Hasta el 02-oct-2026 se llamó "Proyecto CHAPALA"; ese nombre queda en la carpeta, en el proyecto Django (`chapala`) y en la base de datos.

> **Estado al 02-oct-2026:** pestañas 1 a 8, módulos opcionales, concentraciones, side track, hoyo piloto, reporte de propiedades, reporte final y correcciones del cliente del 02-oct construidos. Migraciones hasta la **0027**. Falta la prueba en pantalla. Ver [00_TRASPASO](00_TRASPASO.md) y [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md).

---

## ¿Por dónde empiezo?

| Si eres… | Lee |
|---|---|
| **Ingeniero de AOS** (usuario) | [MANUAL_USUARIO](MANUAL_USUARIO.md) → [18 Preguntas frecuentes](18_PREGUNTAS_FRECUENTES.md) → [17 Glosario](17_GLOSARIO.md) |
| **Desarrollador o asistente que retoma el proyecto** | `../AGENT.md` → [00 Traspaso](00_TRASPASO.md) → [16 Pendientes](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md) → el documento del tema |
| **Quien instala o empaqueta** | [01 Instalación y ejecución](01_INSTALACION_Y_EJECUCION.md) (incluye `SmartMud.exe`) |

---

## Índice

### Estado del proyecto

| # | Documento | Contenido |
|---|---|---|
| 00 | [Traspaso](00_TRASPASO.md) | Estado actual, reglas de trabajo, cadena de migraciones, prioridades |
| 16 | [Problemas conocidos y pendientes](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md) | Qué probar, decisiones abiertas, errores conocidos, seguridad, historial de lo resuelto |
| 21 | [Análisis de la revisión del 27-sep](21_ANALISIS_MATERIAL_REVISION_27SEP.md) | De dónde salió cada decisión del 27-sep (imágenes y audios) |
| 22 | [Cambios del 02-oct: Smart Mud](22_CAMBIOS_02OCT_SMART_MUD.md) | Nombre, logos, tanques, monedas, intervalos, hub bloqueado, `.exe` sin consola |

### Usuario

| Documento | Contenido |
|---|---|
| [MANUAL_USUARIO](MANUAL_USUARIO.md) | Paso a paso: abrir el sistema, crear y configurar un pozo, reporte diario, casos especiales, reportes que se entregan |
| [17 Glosario](17_GLOSARIO.md) | ONE-TRAX (inglés) ↔ Smart Mud (español) y siglas del oficio |
| [18 Preguntas frecuentes](18_PREGUNTAS_FRECUENTES.md) | Dudas comunes y mensajes de error |

### Técnico

| # | Documento | Contenido |
|---|---|---|
| 01 | [Instalación y ejecución](01_INSTALACION_Y_EJECUCION.md) | Requisitos, `.env`, migraciones, arranque, `SmartMud.exe` |
| 02 | [Arquitectura](02_ARQUITECTURA.md) | Carpetas, capas, motores de cálculo, patrones |
| 03 | [Modelo de datos](03_MODELO_DATOS.md) | Modelos campo por campo e historial de migraciones |
| 04 | [API y rutas](04_API_ENDPOINTS.md) | URLs, métodos y vistas |
| 05 | [Configuración del pozo](05_CONFIGURACION_POZO.md) | Wizard, fecha inicial, pantalla del pozo y sus configuraciones, catálogos maestros |
| 06 | [Reporte diario: hub y pestañas 1 a 5](06_REPORTE_DIARIO_PESTANAS_1_A_5.md) | Hub (bloqueado), General, Bombas, Lodo, Geometría, Comentarios |
| 07 | [Pestaña 6: control de sólidos](07_PESTANA_6_CONTROL_SOLIDOS.md) | Mallas, tickets, transacciones, uso de equipos |
| 08 | [Pestaña 7: distribución de tiempo](08_PESTANA_7_DISTRIBUCION_TIEMPO.md) | Horas por actividad |
| 09 | [Pestaña 8: volumetría e inventario](09_PESTANA_8_VOLUMETRIA_INVENTARIO.md) | Tanques, movimientos, inventario unificado, concentraciones, pérdidas |
| 10 | [Hidráulica API RP 13D](10_HIDRAULICA_API13D.md) | 4ª y 5ª edición |
| 11 | [Cálculos de ingeniería](11_CALCULOS_INGENIERIA.md) | Geometría, survey, bombas, reología, sólidos |
| 12 | [Módulos opcionales](12_MODULOS_OPCIONALES.md) | IFE, análisis de sólidos, retención, eventos (ocultos), benchmark |
| 13 | [Costos](13_COSTOS.md) | Origen de cada costo y cobro en dos monedas |
| 14 | [Reporte Excel](14_REPORTE_EXCEL.md) | Plantilla, hojas, logo, páginas |
| 15 | [Inventario de almacén](15_INVENTARIO_ALMACEN.md) | Pantalla Inventario e inventario unificado |
| 19 | [Guía de mantenimiento](19_GUIA_MANTENIMIENTO.md) | Reglas del proyecto, cómo agregar pestañas o campos, pruebas, despliegue |
| 20 | [Concentraciones y casos especiales](20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md) | Concentraciones, side track, hoyo piloto, CaCO₃ |

---

## Carpetas dentro de `docs/`

| Carpeta | Qué hay | ¿Está al día? |
|---|---|---|
| `docs/` (raíz) | Los documentos de arriba | **Sí** — es la documentación oficial |
| `manuales/` | `GUIA_DIA_OPERATIVO` (HTML y PDF), `MANUAL_USUARIO.html` y `convertir_a_pdf.py` | **No**: se generaron el 23/24-sep desde el manual viejo. Regenerar desde `MANUAL_USUARIO.md` antes de repartirlos |
| `fuentes/` | Material del cliente: audios transcritos del 02-oct, observaciones, lista de bugs, avances | Material original, no se edita |
| `_archivo/` | Documentación reemplazada: la de `docs/` del 23-sep, memoria y traspasos viejos de Claude, `RESUMEN_AVANCE` de la app vieja | Solo como historia; **no usar como referencia** |

## Tecnología

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12+ · Django 6.1.1 |
| Base de datos | PostgreSQL (`psycopg2-binary`) o SQLite (según `.env`); el `.exe` usa SQLite |
| Frontend | Plantillas Django + JavaScript sin frameworks + CSS |
| Excel | `openpyxl` (+ `pillow` para el logo) sobre `operaciones/plantillas/reporte_diario_onetrax.xlsx` |
| Ejecutable | PyInstaller + `pystray` (ícono en la bandeja) |
| Idioma / zona | `es-ve`, `America/Caracas` |

Desarrollado para All Oil Services, C.A. Referencia funcional: manual de ONE-TRAX, módulo *Drilling Fluids and Equipment*.
