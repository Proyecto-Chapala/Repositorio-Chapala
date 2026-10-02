# 22 — Cambios del 02-oct-2026: Smart Mud

Origen: `fuentes/notas_cliente/2026-10-02_observaciones.md` y los 5 audios de la revisión con el tío (`fuentes/audios_2026-10-02/`). Migraciones nuevas: **0026_textos_smart_mud** y **0027_intervalo_cerrado_moneda_secundaria** (la 0025 es del compañero).

## 1. Qué pidió AOS y dónde quedó

| Pedido (palabras del cliente) | Qué se hizo | Archivos |
|---|---|---|
| "Cambiar el nombre del programa de chapala a smart mud" | Títulos, barra lateral, activación, PDF del recap, "Módulos Smart Mud" | plantillas `*.html` |
| Logo: "una gota de petróleo que llame la atención" | Gota del logo Smart Mud en la barra lateral, favicon, activación (logo completo) y `.exe` | `static/operaciones/img/`, `layout.css`, `licencia.css`, `empaquetado/smartmud.ico/.png` |
| Logo de AOS "para todos los reportes Excel y PDF, esquina superior izquierda" | Excel diario y del recap (todas las hojas, celda A1) y los dos PDF | `reporte_excel.py`, `recap_pozo.py`, `recap_imprimible.html`, `reporte_propiedades.html`, `recap.css`, `reporte_propiedades.css` |
| "Elimínen todo lo que dice M-I SWACO", "que no aparezca MI por ningún lado, déjale la API" | Textos quitados; ecuaciones de sólidos solo **API**; categorías de pérdida "Estándar"; columna "¿Propio?" | `models.py`, `models_daily_reports.py`, plantillas; migración 0026 (pasa datos viejos a API) |
| "Cambiar módulo de ONE-TRAX por módulo Smart Mud" | Sección "Módulos Smart Mud" en la pantalla del pozo; sin "(ONE-TRAX)" en títulos | `pozos/main.html`, `reporte_diario_detalle.html` |
| "Información de fosas → información de tanques; tipo de fosa → tipo de tanque" | En configuración, pestaña 8, mensajes del servidor y Excel | `pits.html/js`, `reporte_inventario.js`, `reporte_diario_detalle.html`, `views_inventario.py`, `volumetria.py`, `reporte_excel.py` (`_textos_tanques`) |
| "Configuración general... después de información general" | Reordenadas las tarjetas | `pozos/main.html` |
| "Otras monedas: bolívares, dólares, euros..." | Selector con 18 monedas en el wizard y en Configuración General (editable) | `Pozo.MONEDAS_COMUNES`, `_paso3_financiero.html`, `general_setup.*`, `GeneralSetupForm` |
| "Un contrato con una parte en bolívares y otra en dólares" | **Segunda moneda de cobro** (moneda, tasa, %) y recuadro en la pantalla de costos | 0027; `views_daily_reports.cobro_dos_monedas`; `reporte_diario_detalle.html`; `daily_reports.css` |
| "Opción de eliminar pozo" ("empecé mal") | Botón con confirmación escribiendo el nombre; devuelve el inventario | `views.api_pozo_eliminar`, `pozo_main.js`, `pozos/main.html` |
| "Dar dos veces click en un producto se ponga en lista activa" | Doble clic en filas del catálogo (productos, equipos, mallas) | `active_items.js`, `pozos.css` |
| "Orden de impres... que salga el nombre completo" | Etiquetas del contexto del pozo sin recorte | `daily_reports.css` |
| "Sale en negro y las letras no se ven" | Causa: `styles.css` da fondo azul a `.custom-table th` y `pozos.css` les ponía letra gris. Ahora letra blanca | `pozos.css` |
| "No pone la pantalla completa, uno tiene que tirar el zoom" | Inventario: formulario debajo de la tabla en pantallas chicas; el área principal se desplaza | `inventario.css`, `layout.css` |
| "Esta página no se toca, tiene que bloquearla" (Fluidos de Perforación) | Hub solo crea y abre; etiquetas bloqueadas con *Modificar etiquetas*; se quitaron opciones sin uso | `daily_reports_hub.html`, `daily_reports.css` |
| "Eventos no programados, eliminado. Que no confunda al ingeniero" | Botones ocultos (el módulo sigue) | `reporte_diario_detalle.html`, `daily_reports.css` |
| Intervalo 2 "me va a cagar la verga" si se abre antes de cerrar el 1 | Estado abierto/cerrado; no se crea otro con uno abierto | 0027; `views.api_intervalo_cerrar/reabrir`; `casing_intervals.*` |
| "Inventario dejar una sola página" | Además de quedar una hoja, se borran las páginas 2 y 3 vacías | `reporte_excel._quitar_paginas_vacias` |
| "Que cada vez que abra no salga la pantallita negra" | `SmartMud.exe` sin consola, con ícono en la bandeja | `empaquetado/` (ver [01 § 9](01_INSTALACION_Y_EJECUCION.md#9-ejecutable-para-los-ingenieros-smartmudexe)) |
| Ya resueltos antes del 02-oct por el usuario | Lodo reciclado, una hoja de inventario, "Fecha inicial", coordinador e ingenieros de fluido 1 y 2, enlace del registro direccional | — |

## 2. Detalles técnicos

- **Ecuaciones de sólidos**: `ECUACION_SOLIDOS_CHOICES = [('API','API')]`, default `API`; `ReporteDiarioMudConfig.EQUATION_CHOICES = [('API','API')]`. La 0026 hace `RunPython` para pasar `MI`/`M-I` a `API`. El badge de la pestaña 3 guarda el valor en `data-valor` (antes se leía el texto visible).
- **Intervalos**: `IntervaloRevestimiento.cerrado` está **excluido** de `IntervaloRevestimientoForm` (si no, cada guardado lo pondría en `False`). La 0027 cierra todos los intervalos menos el último de cada pozo.
- **Segunda moneda**: `GeneralSetupForm.clean()` exige tasa > 0 y % entre 0 y 100 si hay segunda moneda, y que sea distinta de la principal; sin segunda moneda limpia tasa y %.
- **Pillow**: agregado a `requirements.txt`. `reporte_excel._pillow_disponible()` evita que el Excel falle sin Pillow (sale sin logo).
- **Terminología**: solo cambió lo visible. Siguen `Fosa`, `TipoFosa`, `data-fosa`, `vaDatos.fosas`, `LODO_ENTERO`, `es_producto_mi`, `ingeniero_miswaco_*`.

## 3. Pendiente de este lote

Ver [16 § A y B](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md): probar todo en pantalla, correr la 0027, instalar Pillow, decidir si el reparto en dos monedas va al Excel y si se permite borrar el último reporte.
