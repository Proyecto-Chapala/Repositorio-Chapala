# 00 — Traspaso: estado actual y cómo se trabaja

> **Léelo primero** (después de `AGENT.md`). Actualizado el **02-oct-2026**. Con este archivo, [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md) y el documento del tema se retoma el proyecto sin la conversación anterior.

## 0. Cómo se trabaja (reglas del usuario)

- Proyecto Django en **`C:\Users\SECRETARIA\Documents\Programacion\Personal\Proyecto CHAPALA`** (app única `operaciones`). El sistema se llama **Smart Mud**; "CHAPALA" queda solo como nombre interno (carpeta, proyecto Django `chapala`, base de datos).
- Desde la nube se accede por el puente al equipo del usuario. **Normalmente no hay shell**: traer archivos con `device_stage_files`, editar en la nube y devolver con `device_commit_files` usando `expectedMtimeMs`. Para borrar o mover archivos, dejarle al usuario un script de PowerShell.
- **Siempre volver a traer el archivo del disco antes de editar** (el compañero *xtal* también sube cambios por git). Archivos con **CRLF**: pasar a LF para editar y volver a CRLF al escribir.
- En la nube **no hay Django** (PyPI bloqueado): validar con `ast.parse`, `node --check` y pruebas de funciones puras. LibreOffice sí está: sirve para revisar cómo se ven los Excel. El usuario corre `migrate` y prueba en pantalla.
- **git lo corre el usuario** en PowerShell: rama `Refactorizacion`, remoto `github.com/Proyecto-Chapala/Repositorio-Chapala`.
- Todo el texto visible en **español**; CSS y JS en **archivos aparte**, uno por pestaña o pantalla; estáticos versionados con `_version_estaticos()`.
- **Nada de "M-I", "M-I SWACO" ni "ONE-TRAX" en pantalla ni en reportes.** Se dice **tanque** (no fosa) y **lodo reciclado** (no lodo entero).
- Ir segmento por segmento; ante la duda, revisar el manual ONE-TRAX (`documentation/Manual ONE-TRAX 2.0 (6).pdf`) o preguntar.
- Si el usuario comparte imágenes o audios, **analizarlos y dejar el análisis en `docs/`** (fuentes en `docs/fuentes/`).
- Al terminar un cambio: actualizar este traspaso, el [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md) y el documento del tema, y crear su archivo de prueba en [`pruebas/`](pruebas/README.md).

## 1. Estado (02-oct-2026)

- Escrito en disco: todo lo del 02-oct (ver [22](22_CAMBIOS_02OCT_SMART_MUD.md)). **El usuario todavía no hizo commit** de estos cambios.
- Migraciones aplicadas en la BD del usuario: hasta la **0026** (corrió `migrate` desde cero el 02-oct sin errores). **Falta la 0027.**
- **Falta probar en pantalla** casi todo lo del 27-sep y del 02-oct (lista en [16 § A](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md#a-pendiente-de-probar-en-pantalla-el-usuario)).
- Fecha límite que dio el usuario: listo para el curso a los ingenieros (semana del 28-sep), ya vencida; se está en la ronda de correcciones del cliente.

### Cadena de migraciones

```
0021_modulos_opcionales
 ├─ 0022_inventario_unificado   (compañero xtal)
 └─ 0022_sidetrack → 0023_recap_pozo
        └──────────── 0024_merge
                         └─ 0025_add_empaque_to_producto   (compañero)
                              └─ 0026_textos_smart_mud
                                   └─ 0027_intervalo_cerrado_moneda_secundaria
                                        └─ 0028_inventario_por_pozo
                                             └─ 0029_productoactivopozo_cobro_por
                                                  └─ 0030_alter_reportediario_mi_representante_1_and_more
                                                       └─ 0031_tarifas_dos_monedas
```

- `0022_sidetrack` **depende de 0021** (así quedó aplicada; cambiarla rompe con `InconsistentMigrationHistory`).
- La próxima migración nueva debe depender de **`0031_tarifas_dos_monedas`**.
- La `0030` (generada con `makemigrations` el 12-oct) puso al día los `verbose_name` atrasados. Desde ahí, `makemigrations --check` no detecta cambios: modelos y migraciones están sincronizados.

## 2. Dónde está cada cosa (lo más reciente)

| Tema | Archivos |
|---|---|
| Ejecutable sin consola | `empaquetado/chapala_app.py`, `chapala.spec`, `Construir EXE.bat`, `LEEME_PRUEBAS.txt`, `smartmud.ico/.png` |
| Logos | `operaciones/static/operaciones/img/` (`logo_reporte.png` = AOS para reportes; `smartmud_icono.png`, `smartmud_logo.png`, `favicon.png`) |
| Monedas y segunda moneda | `Pozo.MONEDAS_COMUNES`, `moneda_secundaria`, `cobrar_en_secundaria`, `Pozo.moneda_cobro`/`Pozo.tarifa()`, campos `*_secundaria` de productos, equipos y mallas activos, `GeneralSetupForm`, `general_setup.html/js` (ver [13](13_COSTOS.md)) |
| Intervalos abierto/cerrado | `IntervaloRevestimiento.cerrado`, `views.api_intervalo_cerrar/reabrir`, `casing_intervals.html/js` |
| Eliminar pozo | `views.api_pozo_eliminar`, `pozo_main.js`, `pozos/main.html` |
| Hub bloqueado | `avances_19_sep/daily_reports_hub.html` |
| Tanques (textos) | `pits.*`, `reporte_inventario.js`, `reporte_diario_detalle.html`, `views_inventario.py`, `volumetria.py`, `reporte_excel._textos_tanques` |
| Excel: logo y páginas | `reporte_excel.py` (`_pillow_disponible`, `_quitar_paginas_vacias`, `_textos_tanques`), `recap_pozo.py` |
| Concentraciones, side track, piloto, recap (27-sep) | ver [20](20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md) y [21](21_ANALISIS_MATERIAL_REVISION_27SEP.md) |

## 3. Lo que hay que atacar ahora (prioridad)

1. Que el usuario corra la **0027**, instale **Pillow** y **pruebe en pantalla** ([16 § A](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md)). Si hay error, pedir el traceback completo.
2. Que el usuario corra `limpiar_documentacion.ps1` (borra la documentación vieja ya copiada a `docs/`) y haga commit.
3. Respuestas abiertas de AOS ([16 § B](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md)): dos monedas en el Excel, borrar el último reporte, comentario del reporte de propiedades.
4. Construir `SmartMud.exe` con `Construir EXE.bat` y probarlo en un equipo limpio.

## 4. Decisiones del usuario vigentes

- Módulos opcionales 100 % opcionales; **eventos no programados ocultos**. Tipos de ticket: catálogo editable. Pérdidas impresas por pozo. Sin stock → se bloquea.
- **Inventario por pozo** (oct-2026, reemplaza al unificado): la matriz es solo catálogo; la existencia del pozo sale de sus tickets; el precio lo pone el usuario y arranca en 0. Ver [23](23_CORRECCIONES_REVISION_OCT.md).
- **Pruebas**: `python manage.py test operaciones` (carpeta `operaciones/tests/`). Tienen que pasar antes de dar un cambio por terminado.
- Pestaña 7: horas del período 24 editable; si no cuadra → rojo pero guarda.
- Hidráulica: API 13D 4ª y 5ª, 5ª por defecto. Ecuaciones de sólidos: solo API.
- Redondeo (ingeniero): volúmenes enteros, densidad 1 decimal, costos sin redondear.
- Unidades: todo en campo; concentraciones también en kg/m³.
- Moneda editable (solo cambia el símbolo). Segunda moneda opcional con **tarifas alternativas**: cada ítem tiene precio en las dos y el pozo elige en cuál cobra, sin tasa de cambio. Con reportes, la moneda de cobro queda bloqueada.
- No se crea un intervalo con otro abierto. El hub de reportes no edita ni borra.
- Logos: **AOS** en todos los reportes (Excel y PDF, arriba a la izquierda); **Smart Mud** es el ícono del programa.

## 5. Hallazgos técnicos que no están en el manual

- Las listas activas del pozo se guardan borrando y recreando filas: los datos diarios referencian catálogo maestro o número/código + copia del texto, nunca FK a la lista activa.
- Geometría: ponderación por juntas, tramo de 31 ft, error tipográfico 586,68 → 596,68 (ver [11](11_CALCULOS_INGENIERIA.md)).
- ONE-TRAX sube concentraciones "sin agregar nada" cuando entra lodo más cargado desde otro tanque (caso lodo + lodo); no es un error.
- `styles.css` (global) y `pozos.css` definen ambos `.custom-table th`: cuidado al tocar uno sin el otro.
