# 00 — Traspaso: estado actual y cómo se trabaja

> **Léelo primero** (después de `AGENTS.md`). Actualizado el **18-oct-2026**. Con este archivo, [16](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md) y el documento del tema se retoma el proyecto sin la conversación anterior.

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

## 1. Estado (13-oct-2026)

- **Inventario y lodo reciclado (13-oct):** lodo reciclado solo volumen (Parte A), acumulados por columna en la tabla de inventario (Parte B) y consumo separado del balance de volumen con usado en fluidos manual (Parte C de [26](26_REDISENO_INVENTARIO_Y_LODO_RECICLADO.md), migración **0036**). Ver [pruebas/16](pruebas/16_LODO_RECICLADO_SOLO_VOLUMEN.md), [pruebas/17](pruebas/17_ACUMULADOS_INVENTARIO.md) y [pruebas/18](pruebas/18_INVENTARIO_DE_CONSUMO.md).
- **Servicios del pozo (13-oct):** ingenieros, trailers y demás servicios se cobran por día en la pestaña 8 › **Servicios**, con categoría y tarifa propias (migración **0035**). "Usado en otro módulo" queda solo para productos transferidos a otra línea (por ejemplo, cementación). Ver [25](25_SERVICIOS_DEL_POZO.md) y [pruebas/15](pruebas/15_SERVICIOS_DEL_POZO.md).
- **Programadas todas las correcciones de la revisión de octubre** (20 puntos): ver [23](23_CORRECCIONES_REVISION_OCT.md). Fuentes: `docs/fuentes/transcripciones_revision_oct/` (usar las `*_mejorado.txt`).
- **Base de datos revisada** antes de empaquetar y **papelera de pozos** (eliminar ya no borra): ver [24](24_PAPELERA_Y_TIPOS_DE_DATOS.md). **La base definitiva es SQLite.** **Licencia eliminada** y `SmartMud.exe` listo para la prueba en producción (`empaquetado\dist\SmartMud_Pruebas.zip`).
- **Inventario y tickets (14-oct):** los tickets de entrada alimentan la dotación en la columna **Inicial** del pozo; **Recibido** y **Devuelto** se escriben a mano en la tabla diaria (migración **0037**). Al guardar, el Final pasa al Inicial del día siguiente. Ver [pruebas/19](pruebas/19_INVENTARIO_TICKETS_Y_MANUAL.md).
- **Eliminar reporte en Hub (14-oct):** se reincorporó el botón **`🗑️ Eliminar Reporte`** en el encabezado del historial junto a *+ Nuevo Reporte* con confirmación segura, sin botones invasivos en la tabla.
- **Optimizaciones de lógica y cálculos de reportes (15-oct-2026):** completado el plan de 8 puntos críticos:
  1. Hidráulica: sincronización bidireccional y persistencia de edición de norma API 4ª / 5ª.
  2. Costos: banner explicativo en Pestaña 1 y modal de costos ante inconsistencias en inventario previo en lugar de $0 silencioso.
  3. Validación física: advertencia en vivo y en API cuando `bit_depth > profundidad_actual`.
  4. Pérdida de presión en herramientas de fondo: MWD y Motor PDM escalados por caudal en sarta y pérdida total.
  5. Bombas de riser: excluidas del circuito de circulación de perforación hacia la sarta y mecha (Bottoms Up e hidráulica).
  6. Well Survey: amarre virtual en superficie en (0, 0, 0) y proyección de Sección Vertical ($VS$) sobre azimut.
  7. Ecuación de sólidos: anclada fijamente a la Norma API RP 13B como estándar oficial.
  8. Número de reporte fijo: almacenado en base de datos (`numero_reporte`, migración **0038**), inmune a reenumeraciones por inserción de fechas intermedias.
- **Visualización de Operador y Taladro (15-oct-2026):** propiedades directas en el modelo `Pozo` (`pozo.operador`, `pozo.taladro`) conectadas de forma segura a `WellHeaderInfo`. Resuelve la ausencia del operador (`—`) en el Hub "Fluidos de Perforación y Equipos" y en el encabezado del reporte diario.
- **Continuidad del balance volumétrico y pérdidas del sistema circulante (15-oct-2026):**
  - El volumen final calculado del reporte $N$ (`calc_fosa`) pasa directamente como volumen inicial (`inicio_fosa`) del reporte $N+1$, garantizando que las pérdidas operacionales y adiciones queden descontadas en la línea de tiempo en vez de reiniciarse al aforo (`real`).
  - En el modal de registro de pérdidas, se preselecciona automáticamente el tanque activo del sistema circulante (`vaFosasActivas()`) y se actualiza la etiqueta a *"Tanque de la pérdida (volumen circulante)"*, evitando descuentos accidentales en tanques de reserva.
- **Revisión del cliente del 15-oct (18-oct-2026):** el Excel diario muestra lo **calculado** en *Tanques activos* y *Volumen total de circulación* (era la causa de que al día siguiente apareciera el real); los **tickets se plasman directamente en el campo Recibido/Devuelto** (no quedan en 0) junto a su chip de ticket; al guardar la volumetría se descuenta automáticamente el ticket para no duplicar existencias y admitir cantidades adicionales a mano; el inicial es el final del día anterior; las **pérdidas solo se registran en tanques del sistema activo**; *Agregar químicos* muestra existencia y cuánto queda. Sin migraciones. Ver [27](27_VOLUMEN_CALCULADO_TICKETS_Y_PERDIDAS.md) y [pruebas/21](pruebas/21_VOLUMEN_CALCULADO_TICKETS_PERDIDAS.md).
- **Pruebas automáticas:** 149, todas pasan (`python manage.py test operaciones`).
- **Migraciones:** el usuario aplicó hasta la **0034**. Faltan por aplicar: `0035_servicios_del_pozo`, `0036_inventario_usado_fluido_manual`, `0037_inventarioproductodia_devuelto_and_more` y `0038_reportediario_numero_reporte` (`python manage.py migrate`).

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
                                                            └─ 0032_comentario_propiedades
                                                                 └─ 0033_inventario_inicial_manual
                                                                      └─ 0034_papelera_pozos_y_tipos_opcionales
                                                                           └─ 0035_servicios_del_pozo
                                                                                └─ 0036_inventario_usado_fluido_manual
                                                                                     └─ 0037_inventarioproductodia_devuelto_and_more
                                                                                          └─ 0038_reportediario_numero_reporte
```

- `0022_sidetrack` **depende de 0021** (así quedó aplicada; cambiarla rompe con `InconsistentMigrationHistory`).
- La `0038` agrega `numero_reporte` fijo a `ReporteDiario` y puebla registros históricos.
- `makemigrations --check` no detecta cambios: modelos y migraciones están sincronizados.

## 2. Dónde está cada cosa (lo más reciente)

| Tema | Archivos |
|---|---|
| Ejecutable sin consola | `empaquetado/chapala_app.py`, `chapala.spec`, `Construir EXE.bat`, `LEEME_PRUEBAS.txt`, `smartmud.ico/.png` |
| Logos | `operaciones/static/operaciones/img/` (`logo_reporte.png` = AOS para reportes; `smartmud_icono.png`, `smartmud_logo.png`, `favicon.png`) |
| Monedas y segunda moneda | `Pozo.MONEDAS_COMUNES`, `moneda_secundaria`, `cobrar_en_secundaria`, `Pozo.moneda_cobro`/`Pozo.tarifa()`, campos `*_secundaria` de productos, equipos y mallas activos, `GeneralSetupForm`, `general_setup.html/js` (ver [13](13_COSTOS.md)) |
| Intervalos abierto/cerrado | `IntervaloRevestimiento.cerrado`, `views.api_intervalo_cerrar/reabrir`, `casing_intervals.html/js` |
| Servicios del pozo (ingenieros, trailers) | `models_servicios.py`, `views_inventario._servicios_del_dia/api_servicio_guardar/api_servicio_eliminar`, `resumen_costos`, `recap_pozo.py`, pestaña `vaPanelServicios` en `reporte_diario_detalle.html`, `reporte_inventario.js/css` (ver [25](25_SERVICIOS_DEL_POZO.md)) |
| Eliminar pozo y papelera | `Pozo.objects` excluye la papelera (`Pozo.todos` la incluye); `views.api_pozo_eliminar/api_pozo_restaurar/pozos_papelera_view`, `pozo_main.js`, `pozos_papelera.js`, `pozos/main.html`, `pozos/papelera.html` |
| Hub bloqueado | `avances_19_sep/daily_reports_hub.html` |
| Tanques (textos) | `pits.*`, `reporte_inventario.js`, `reporte_diario_detalle.html`, `views_inventario.py`, `volumetria.py`, `reporte_excel._textos_tanques` |
| Excel: logo y páginas | `reporte_excel.py` (`_pillow_disponible`, `_quitar_paginas_vacias`, `_textos_tanques`), `recap_pozo.py` |
| Concentraciones, side track, piloto, recap (27-sep) | ver [20](20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md) y [21](21_ANALISIS_MATERIAL_REVISION_27SEP.md) |

## 3. Lo que hay que atacar ahora (prioridad)

1. Que el usuario haga **commit** de los cambios de octubre.
2. **Pruebas en pantalla** con las guías de [`pruebas/`](pruebas/README.md) (01 a 14), en orden y en un pozo nuevo. Marcar las casillas y anotar los fallos en cada guía; corregir lo que falle (si hay error, pedir el traceback completo). Atención especial a la prueba 12 (grilla de propiedades extra) y al formato de los Excel (pruebas 05 y 13).
3. Verificar en pantalla los puntos **6** ("usado en otro módulo" no afecta las concentraciones) y **19** (tickets sin precio) del [23](23_CORRECCIONES_REVISION_OCT.md).
4. Pendientes sin código: cargar el **catálogo de herramientas** (punto 20) y preguntar a **administración** la codificación de los números de guía/ticket (punto 19).
5. Respuestas abiertas de AOS ([16 § B](16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md)): borrar el último reporte; si más adelante quieren conversión automática de monedas con la tasa del día.
6. `SmartMud.exe` ya construido y verificado: probarlo en un equipo limpio (otra PC, sin Python).

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
