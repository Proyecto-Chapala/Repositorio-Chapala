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
- **Cerrar y Reabrir Pozo (19-oct-2026):** implementado el ciclo completo entre `ACTIVO` y `CERRADO`. Disponible en **Reporte Final (Recap)** y en la **Pantalla Principal del Pozo** con confirmación. Un pozo cerrado pasa al filtro *Cerrados* de la lista principal, bloquea la creación/eliminación de reportes diarios en el Hub y backend para proteger el histórico, y puede reabrirse en cualquier momento de forma reversible. Sin migraciones. Ver [29](29_CERRAR_Y_REABRIR_POZOS.md) y [pruebas/25](pruebas/25_CERRAR_Y_REABRIR_POZO.md).
- **Modificar Pozo (19-oct-2026):** matriz técnica centralizada para corregir errores cometidos durante el alta del pozo (identificación, unidades, financiero/monedas, spud date/fluido inicial, pérdidas). Disponible desde el botón superior *Modificar pozo* en la pantalla principal del pozo (`/pozos/<id>/modificar/`). Validación de unicidad de nombre excluyendo el pozo actual y rechazando papelera, sincronización atómica con `WellHeaderInfo`, protección de pozo cerrado, bloqueo de moneda cuando ya existen reportes diarios y validación de Spud Date contra el primer reporte. Sin migraciones. Ver [30](30_MODIFICAR_POZO.md) y [pruebas/26](pruebas/26_MODIFICAR_POZO.md).
- **Homogeneización de Catálogos Maestros (19-oct-2026):** las 5 pestañas de `/catalogos-maestros/` (Equipos ECS, Mallas, Propiedades de equipo, Benchmark y Componentes de sarta) inician sus paneles laterales en estado `Bloqueado` (`catalogos-mode-badge bloqueado`), evitando ediciones accidentales. Se habilitan al pulsar `+ Nuevo ...` o seleccionar una fila, y regresan a bloqueado tras guardar, cancelar o eliminar. Sin migraciones.
- **Eliminación Segura de Reportes Diarios con regla LIFO (19-oct-2026):** implementada la regla LIFO estricta en el Hub y backend (`api_reporte_diario_eliminar`), resolviendo el pendiente histórico C10. Solo se permite eliminar el último reporte cronológico del pozo para proteger la cadena de continuidad volumétrica (cálculo de fosas) y de inventario (químicos, tickets y mallas). Los reportes intermedios quedan bloqueados en pantalla y son rechazados con HTTP 400 por la API. Sin migraciones. Ver [pruebas/27](pruebas/27_ELIMINAR_REPORTE_LIFO.md).
- **Protección e Integridad de Intervalos de Revestimiento (19-oct-2026):** se aplica la regla LIFO estricta en la eliminación de intervalos (`api_intervalo_eliminar` y frontend `casing_intervals.js`), impidiendo eliminar intervalos intermedios si existen posteriores para proteger la correlatividad y la geometría; se bloquea la eliminación si el intervalo tiene reportes diarios imputados (`intervalo.reportes_asignados.exists()`); se fija el campo `#dInterval` como `readonly`; se blindan las operaciones de crear, modificar, cerrar, reabrir y eliminar intervalos ante pozos cerrados (`pozo.estado == 'CERRADO'`); se incluye vista de solo lectura en la interfaz y se unifican las respuestas JSON con `success` y `ok`. Sin migraciones. Ver [pruebas/28](pruebas/28_PROTECCION_INTERVALOS.md).
- **Blindaje Integral contra Mutaciones en Pozos Cerrados (19-oct-2026):** implementado el bloqueo sistemático en backend (`_validar_pozo_abierto(pozo)`) en todas las operaciones `POST` de guardado de las 8 pantallas de configuración del pozo (`views.py`) y de todas las pestañas 1 a 8 de reportes diarios, control de sólidos, inventario, volumetría, servicios y módulos opcionales (`views_daily_reports.py`, `views_inventario.py`, `views_control_solidos.py`, `views_opcionales.py`). La barra secundaria compartida de configuración (`_nav_info_pozo.html`) despliega de forma uniforme el banner rojo de advertencia de solo lectura cuando `pozo.estado == 'CERRADO'`. Sin migraciones. Ver [pruebas/29](pruebas/29_BLINDAJE_POZO_CERRADO.md).
- **Integridad Temporal entre Spud Date y Reportes Diarios (19-oct-2026):** se prohíbe crear o editar reportes diarios con fecha anterior a la fecha de inicio de perforación (*Spud Date*) configurada en Well Header Information. El backend (`api_reporte_diario_crear` y `api_reporte_diario_general_guardar`) rechaza fechas previas con HTTP 400 y mensaje descriptivo, y los selectores de fecha en frontend (Hub y Pestaña 1) incorporan la restricción `min` y validación en cliente. Si el pozo no tiene Spud Date configurado se mantiene flexible. Sin migraciones. Ver [pruebas/30](pruebas/30_VALIDACION_FECHA_SPUD_REPORTE.md).
- **Sincronización Bidireccional de Spud Date y Tipo de Fluido Inicial (19-oct-2026):** la pantalla inicial de bienvenida de Spud Date (`api_pozo_spud_date`) sincroniza atómicamente con `WellHeaderInfo` (`spud_date`, `numero_control_logit` y `primary_mud_type_codigo`/`descripcion`). La sugerencia del primer reporte diario en el Hub y en la API de listado adopta automáticamente el Spud Date y el tipo de fluido inicial mapeado inteligentemente a las opciones estándar de `ReporteDiario` (`WBM`, `OBM`, `SBM`, `WBM_CACL2`), activando de inmediato el botón `⚓ Fecha Inicio` y la tarjeta de lodo correspondiente. Guardar Well Header Information mantiene sincronizado el modelo `Pozo` y rechaza fechas Spud posteriores a reportes diarios existentes. Sin migraciones. Ver [pruebas/31](pruebas/31_SINCRONIZACION_SPUD_DATE_WELL_HEADER.md).
- **Integridad y Transaccionalidad Atómica en Datos Geológicos y de Perforación (19-oct-2026):** en `Formation Tops` (`api_formation_tops_guardar`), `Well Survey` (`api_well_survey_guardar`) y `Pumps / Bits` (`api_pumps_bits_guardar`), se reemplazó la eliminación prematura de registros por validación en memoria y transacciones atómicas seguras (`transaction.atomic()`), impidiendo pérdidas de datos si ocurre un fallo. Se incorporaron validaciones estrictas de límites físicos y geométricos (profundidades no negativas, porcentaje de arena entre 0 y 100%, inclinación entre 0° y 180°, azimut entre 0° y 359.99°, y eficiencias de bombas entre 0% y 100%). Sin migraciones. Ver [pruebas/32](pruebas/32_INTEGRIDAD_DATOS_GEOLOGICOS_PERFORACION.md).
- **Restauración de Papelera, Cierre de Pozos e Integridad en Propiedades de Lodo (19-oct-2026):**
  - En `api_pozo_restaurar`, se valida preventivamente la no existencia de otro pozo activo o cerrado con el mismo nombre (`nombre__iexact`), previniendo caídas no controladas `IntegrityError` (500) en SQLite.
  - En `api_pozo_cerrar`, se restringe el cierre exclusivamente a pozos con estado `ACTIVO`, rechazando con HTTP 400 el cierre de pozos en `BORRADOR`.
  - En `api_mud_properties_guardar`, se valida en memoria la consistencia física de propiedades de lodo (densidades, viscosidades, lecturas reológicas $\ge 0$, porcentajes de retorta $0-100\%$, $pH$ entre 0 y 14, gravedades de configuración $> 0$) y se envuelve la persistencia de configuración, chequeos y propiedades extra en `transaction.atomic()`, con respuestas normalizadas (`success` y `ok`). Sin migraciones. Ver [pruebas/33](pruebas/33_RESTAURAR_PAPELERA_Y_PROPIEDADES_LODO.md).
- **Consistencia Geométrica en Sarta y Transaccionalidad Atómica en Propiedades Extra (19-oct-2026):**
  - En `api_well_geometry_guardar`, se valida en memoria que longitudes y diámetros sean no negativos ($\ge 0$), y la consistencia geométrica física ($ID < OD$ y $ID_{tj} < OD_{tj}$), evitando cálculos de desplazamiento y volumen matemáticamente absurdos. Además, la actualización de campos del reporte diario (`intervalo_costo`, `pilot_hole`, `kickoff_sidetrack`) se integró dentro del bloque indivisible `with transaction.atomic():` junto a la recreación de tramos de sarta.
  - En `api_propiedades_extra_guardar`, se protegió el ciclo de actualización y borrado con `transaction.atomic()` y validación de enteros positivos en número de propiedad.
  - Respuestas normalizadas simétricamente con `ok` y `success` en `api_well_geometry_guardar`, `api_propiedades_extra_guardar`, `api_comentarios_guardar` y `api_reporte_propiedades_comentario`. Sin migraciones. Ver [pruebas/34](pruebas/34_GEOMETRIA_SARTA_Y_PROPIEDADES_EXTRA.md).
- **Integridad en Tanques, Volumetría y Listas Activas (19-oct-2026):**
  - En `api_fosas_guardar` y `FosaForm`, se impone la no negatividad en capacidades de tanque ($\ge 0$) y numeración positiva ($> 0$), evitando corromper la volumetría de la Pestaña 8.
  - En `api_tipos_fosa_guardar` y `TipoFosaForm`, se prohíbe el envío de listas vacías y se validan códigos no negativos ($\ge 0$), con respuestas simétricas `ok` y `success`.
  - En `api_volumetria_dejar_en_hoyo`, se asigna por defecto la categoría 7 ("Detrás del Revestimiento / En el Hoyo") si la petición omite `perdida_codigo`, y se normalizan las respuestas de `_error` y `_estado_volumetria`.
  - En `ProductoActivoPozoForm`, `EquipoActivoPozoForm` y `MallaActivaPozoForm`, se validan precios, tarifas de renta/standby no negativas y descuentos entre $0\%$ y $100\%$, con respuestas estandarizadas `ok` y `success`. Sin migraciones. Ver [pruebas/35](pruebas/35_FOSAS_Y_VOLUMETRIA_INTEGRIDAD.md).
- **Integridad en Catálogos Maestros, Configuración de Pérdidas y Componentes de Sarta (19-oct-2026):**
  - En `_validar_componente_sarta`, validación geométrica física de juntas de conexión ($ID_{tj} < OD_{tj}$) cuando $OD_{tj} > 0$.
  - En `api_categorias_perdida_guardar`, protección contra listas vacías de categorías y validación de código positivo ($> 0$) en `CategoriaPerdidaItemForm.clean_codigo`.
  - Normalización simétrica de respuestas con `ok` y `success` en `api_marketing_codes_guardar`, `api_categorias_perdida_guardar`, `api_equipment_properties_guardar`, `api_benchmark_definiciones_guardar`, `api_benchmark_targets_guardar`, `api_equipo_*`, `api_malla_*`, `api_propiedad_equipo_*`, `api_parametro_benchmark_*` y `api_componente_sarta_*`. Sin migraciones. Ver [pruebas/36](pruebas/36_CATALOGOS_MAESTROS_Y_COMPONENTES_SARTA.md).
- **Integridad en Control de Sólidos, Módulos Opcionales y Pérdidas del Reporte (19-oct-2026):**
  - En `api_muestras_guardar`, validación de consistencia física en Retención de Recortes (masas no negativas, desecación coherente $celda\_seco \le celda\_humedo$, destilado en probeta coherente, $sg > 0$ y porcentajes entre $0\%$ y $100\%$) y en Análisis de Sólidos de Retorta (porcentajes de retorta $0-100\%$, gravedades $> 0$, densidad $> 0$).
  - En `api_eventos_guardar`, validación de campos obligatorios y valores no negativos en horas perdidas, volumen y costo ($\ge 0$).
  - En `api_perdidas_reporte_guardar`, protección contra listas vacías de categorías en el reporte diario.
  - Normalización simétrica de respuestas con `ok` y `success` en todos los endpoints de Control de Sólidos (Pestaña 6), Módulos Opcionales (IFE, muestras, eventos, evaluación de benchmark) y Pérdidas del Reporte. Sin migraciones. Ver [pruebas/37](pruebas/37_CONTROL_SOLIDOS_Y_MODULOS_OPCIONALES.md).
- **Integridad en Hidráulica, Distribución de Tiempo y Reportes Diarios (19-oct-2026):**
  - En `api_hidraulica_detail`, blindaje de mutación contra pozos cerrados (`_validar_pozo_abierto(pozo)`) al recibir peticiones `POST` para cambiar la edición API RP 13D.
  - En `calcular_hidraulica_reporte`, normalización simétrica de respuesta con `ok: True` y `success: True`.
  - En `views_daily_reports.py`, normalización simétrica integral de respuestas (`ok` y `success` tanto en éxito como en error) en `api_cost_overview_detail`, `api_tiempo_detail`, `api_tiempo_guardar`, `api_sarta_reporte_anterior`, `api_comentarios_detail`, `api_reporte_diario_crear`, `api_reporte_diario_eliminar`, `api_reporte_diario_general_guardar`, `api_well_survey_guardar`, `api_formation_tops_guardar`, `api_pumps_bits_guardar`, `api_propiedades_extra_list`, `api_reportes_diarios_list`, `api_well_survey_list`, `api_formation_tops_list`, `api_pumps_bits_detail`, `api_mud_properties_detail` y `api_well_geometry_detail`. Sin migraciones. Ver [pruebas/38](pruebas/38_HIDRAULICA_Y_TIEMPO_INTEGRIDAD.md).
- **Blindaje de Reporte Final (Recap) y Simetría 100% en Views (19-oct-2026):**
  - En `recap_view` y plantilla `recap.html`, blindaje total de conclusiones, recomendaciones y lecciones aprendidas ante pozos cerrados (`pozo.estado == 'CERRADO'`), bloqueando peticiones `POST` con redirección informativa (`?error_cerrado=1`), renderizando textareas como `readonly`, deshabilitando el botón de guardado e incorporando banner de protección.
  - Normalización total de contratos JSON en `operaciones/views.py`: simetría completa con `ok` y `success` simultáneos en `api_pozo_eliminar`, `api_productos_list`, `api_producto_detail`, `api_producto_create`, `api_producto_update`, `api_producto_delete`, `api_pozos_plantillas`, `api_pozo_detail`, `api_pozo_paso1`, `paso2`, `paso3`, `confirmar`, `spud_date`, `pozo_modificar_view`, `api_well_header_detail`, `api_intervalos_list`, `api_pits_list`, `api_categorias_perdida_list`, `api_general_setup_detail`, `api_almacenes_list`, `api_tipos_distribucion_list`, `api_equipos_list`, `api_mallas_list`, `api_productos_activos_list`, `api_equipos_activos_list`, `api_mallas_activas_list`, `api_equipment_properties_detail`, `api_benchmark_definiciones_detail` y `api_benchmark_targets_detail`. Con esto, el **100% de las respuestas JSON del sistema Smart Mud son estrictamente simétricas**. Sin migraciones. Ver [pruebas/39](pruebas/39_RECAP_Y_SIMETRIA_VIEWS.md).
- **Productos Usados, Hoja Única de Inventario y Rediseño Visual en Excel (20-oct-2026):**
  - Corrección de productos usados en hoja de Lodo (Lodo Base Agua, etc., filas 19 a 33): el consumo de las últimas 24 horas ahora computa tanto usado_fluido (manual en inventario) como gregado_balance (dosificado en tanques de lodo). Se eliminaron los residuos de ceros de la plantilla limpiando las celdas vacías a None.
  - Se conserva la hoja única oficial de inventario químico de locación (Inv Quimico (completo)), eliminando las vacías/redundantes (Inv Quimico (DF) y por nombre).
  - Rediseño visual corporativo: pestañas coloreadas según función (Azul corporativo #1E3A8A, Cobalto #2563EB, Teal #0D9488, Celeste #0284C7, Esmeralda #059669, Púrpura #7C3AED, Índigo #4F46E5) y cuadrículas activadas (showGridLines = True) en todas las hojas. Sin migraciones. Ver [14](14_REPORTE_EXCEL.md) y [pruebas/40](pruebas/40_EXCEL_INVENTARIO_Y_PRODUCTOS_USADOS.md).
- **Pruebas automáticas:** 332, todas pasan (python manage.py test operaciones).
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
| Cerrar y reabrir pozo | `views.api_pozo_cerrar/api_pozo_reabrir`, `recap.html/js`, `pozos/main.html`, `pozo_main.js`, `daily_reports_hub.html`, `views_daily_reports.py` (ver [29](29_CERRAR_Y_REABRIR_POZOS.md)) |
| Modificar pozo (matriz inicial) | `forms_pozo.PozoModificarForm`, `views.pozo_modificar_view`, `pozos/modificar.html`, `pozos/main.html` (ver [30](30_MODIFICAR_POZO.md)) |
| Barra de Información del Pozo | `pozos/_nav_info_pozo.html` (incluida en las 8 pantallas con `seccion_activa`), `.info-pozo-nav` en `pozos.css` (ver [05](05_CONFIGURACION_POZO.md)) |
| Rediseño técnico (rama `refactorizacion_ui`) | `base.html` (barra superior), `componentes/sidebar.html`, `componentes/iconos.html`, `componentes/buscador.html` (Ctrl+K), `navegacion.py` (pantallas del pozo), `context_processors.py`, `pozos_list.html`, `pozos/main.html` (tablero), `variables.css`, `layout.css`, `pozos.css` (ver [28](28_REDISENO_UI_TECNICO.md)) |
| Hub bloqueado | `avances_19_sep/daily_reports_hub.html` |
| Tanques (textos) | `pits.*`, `reporte_inventario.js`, `reporte_diario_detalle.html`, `views_inventario.py`, `volumetria.py`, `reporte_excel._textos_tanques` |
| Excel: formato Carta (Letter), logo y páginas | `reporte_excel.py` (ajuste Carta Letter fitToWidth=1, cuadrículas activas, hoja única `Inv Quimico (completo)`, productos usados 24h), `recap_pozo.py` |
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
