# CHAPALA — Traspaso a la siguiente conversación (actualizado 27-sep-2026, noche)

> **Léelo primero.** Con este archivo + `docs/16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md` + `docs/20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md` se retoma el proyecto sin la conversación anterior.

## 0. Cómo se trabaja (reglas del usuario)

- Proyecto Django en `C:\Users\Admin\Documents\Proyectos\Proyecto CHAPALA` (app única `operaciones`). Se accede por el puente al equipo del usuario (**sin shell**: traer archivos con `device_stage_files`, editar en la nube, devolver con `device_commit_files` usando `expectedMtimeMs`).
- **Siempre volver a traer el archivo del disco antes de editar** (el compañero *xtal* también sube cambios por git). Archivos con **CRLF**: convertir a LF para editar y volver a CRLF al escribir.
- En la nube **no hay Django** (PyPI bloqueado): validar con `ast.parse`, `node --check` y pruebas de funciones puras. El usuario corre `migrate` y prueba en pantalla.
- **No se puede hacer git desde aquí**: el usuario corre `git add/commit/pull --rebase/push` en su PowerShell. Rama `Refactorizacion`, remoto `github.com/Proyecto-Chapala/Repositorio-Chapala`.
- Todo el texto visible en **español**; CSS y JS en **archivos aparte** (nada de estilos en línea); un JS/CSS por pestaña; versionado anti-caché con `_version_estaticos()` (views.py).
- Ir segmento por segmento; ante la duda, revisar las capturas del manual ONE-TRAX antes de inventar.

## 1. Estado (27-sep-2026)

Todo lo de abajo está **escrito en disco, commiteado y subido** (último commit `1cc4594`, working tree limpio). Migraciones aplicadas en la BD del usuario hasta la **0024**. **Falta la prueba en pantalla** de todo lo del 27-sep (nada de esto se vio corriendo).

### Cadena de migraciones (¡ojo!)
```
0021_modulos_opcionales
 ├─ 0022_inventario_unificado   (del compañero xtal: el reporte diario descuenta Producto.cantidad)
 └─ 0022_sidetrack → 0023_recap_pozo
        └──────────── 0024_merge  (une ambas ramas; operations = [])
```
- `0022_sidetrack` **debe depender de 0021** (ya estaba aplicada así en la BD del usuario; cambiarla rompe con `InconsistentMigrationHistory`).
- La próxima migración nueva debe depender de **`0024_merge`**.

## 2. Qué se hizo el 27-sep (dónde está cada cosa)

| Tema | Archivos | Notas |
|---|---|---|
| **Concentraciones** (pestaña 8) | `volumetria.py` (`simular`: por compartimento `agregado` y `entradas`), `views_inventario.py` (`_estado_volumetria` → `concentraciones[]` con unidad/tamaño/agregado/aceite/agua/vol_quimicos/lodo), `static/.../js/reporte_inventario.js` (`vaRenderConcentracion`, selector lb/bbl↔kg/m³), `css/reporte_inventario.css` | Verificado: 13,64 / 15,20 / 15,83 / pérdida no cambia. La hoja a lápiz del ingeniero tiene un error (ej. 3 = 15,83, no 16,7) |
| **Hoja Excel "Concentraciones"** | `reporte_excel.py` → `_hoja_concentraciones()` (creada por código, no en la plantilla) | Un bloque por compartimento, lb/bbl y kg/m³ |
| **Contabilidad de volumen** | `reporte_excel.py` → `_hoja_volumen()` | Balance, hoyo y pérdidas sin decimales |
| **Side track** | `models_daily_reports.py` (`ReporteDiario.kickoff_sidetrack_ft`), `models.py` (tipo `SIDETRACK` en `IntervaloRevestimiento`), `control_solidos.py` (`hoyo_perforado()` pura), `views_control_solidos.py` (`_contexto_hoyo`, `_zapata_mas_profunda`), `views_daily_reports.py` (`_hoyo_perforado_dia`, validación de kick-off en `api_well_geometry_guardar`), plantilla `avances_19_sep/reporte_diario_detalle.html` (bloque Side Track + ayuda + tarjeta Hoyo Perforado), `css/daily_reports.css` | Verificado con el manual: 62,5 y 113,3 bbl. Día del abandono = Volumen no fluido + pérdida código 7 "Detrás del Revestimiento / En el Hoyo" |
| **Hoyo piloto** (ampliación) | `control_solidos.hoyo_perforado()` | Dentro del piloto se corta el anillo (D²−d²); primer día desde la zapata. Verificado: 438 m / 108,6 bbl |
| **Reporte corto de propiedades del lodo** | `views_daily_reports.reporte_propiedades_view`, url `reporte_propiedades`, plantilla `avances_19_sep/reporte_propiedades.html`, `css/reporte_propiedades.css`, botón en pestaña 3 | Página imprimible → PDF. El comentario **no se guarda** (pendiente preguntar) |
| **Reporte final del pozo (recap)** | `models_recap.py` (`RecapPozo`: resumen, conclusiones, recomendaciones, lecciones), `recap_pozo.py` (`datos_recap()`, `generar_recap_excel()`, `SECCIONES`), `views_recap.py` (3 vistas), urls `recap_pozo` / `recap_excel` / `recap_imprimible`, plantillas `pozos/recap.html` y `pozos/recap_imprimible.html`, `css/recap.css`, tarjeta en `pozos/main.html` | Excel o PDF a elección, secciones seleccionables, "hasta fecha". Simula la volumetría y las mallas una vez y consulta día por día en memoria |
| **Redondeo en pantallas** | `reporte_inventario.js` (`vaVol()` = 0 decimales en balance/hoyo/pérdidas; no contabilizado y fosas 1 decimal), `reporte_diario_detalle.html` (`wgVolTarjeta()`: tarjetas de pestaña 4 en enteros, exacto en tooltip) | Costos sin tocar |
| **Documentación** | `docs/20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md` (nuevo), `MANUAL_USUARIO.md` (6.6 casos especiales, 8 reportes que se entregan), 09, 14, 16, README | |

## 3. Lo que hay que atacar ahora (prioridad)

1. **Probar en pantalla** (el usuario): pestaña 8 (químico → concentraciones → que baje el inventario del almacén: **ahí se cruzan mis cambios con `0022_inventario_unificado` del compañero**, riesgo principal), pestaña 4 (side track + hoyo perforado), pestaña 3 (reporte de propiedades), reporte final Excel y PDF. Si hay error, pedir el traceback completo.
2. Revisar que el commit del compañero (inventario unificado) no choque con `volumetria.py` / `views_inventario.py`: el rebase fusionó sin conflicto, pero no está probado. Si algo falla ahí, **traer ambos archivos del disco** y leer su lógica de `stock_aplicado` antes de tocar nada.
3. Confirmar con el ingeniero: comentario del reporte de propiedades (¿guardar?), error de su hoja a lápiz, paquete de entrega (general, inventario, concentraciones, volumetría).
4. Pendientes viejos: ver `docs/16` sección E (unidades en renta de equipos, API RP 13C, SUS/DWM, códigos de costo 1-4, limpiar datos de prueba, seguridad antes de publicar en red).

## 4. Decisiones del usuario vigentes

- Opcionales 100 % opcionales. Tipos de ticket: catálogo editable. Pérdidas por pozo. Sin stock → se bloquea.
- Pestaña 7: horas del período 24 editable; si no cuadra → rojo pero guarda.
- Hidráulica: API 13D 4ª y 5ª, 5ª por defecto.
- Redondeo (ingeniero): volúmenes enteros, densidad 1 decimal, costos no se redondean.
- Unidades: todo en campo; concentraciones también en kg/m³.
- Plazo: listo antes del curso a los ingenieros (semana del 28-sep).

## 5. Hallazgos técnicos que no están en el manual

- Listas activas del pozo se guardan borrando y recreando filas → los datos diarios referencian catálogo maestro o número/código + copia del texto, nunca FK a la lista activa.
- Geometría: ponderación por juntas, tramo de 31 ft, error tipográfico 586,68→596,68 (ver `docs/11`).
- ONE-TRAX sube concentraciones "sin agregar nada" cuando entra lodo más cargado desde otra fosa (caso lodo+lodo), no es un error.
