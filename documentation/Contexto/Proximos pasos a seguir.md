# Próximos pasos a seguir

## 1. Pruebas pendientes del flujo actual

Antes de seguir agregando funcionalidad nueva, conviene validar a fondo lo que ya existe. Puntos concretos a probar (ver también "Cosas a tener en cuenta.md"):

- Que un segundo `CierreVolumetrico` sobre el mismo intervalo falle (relación uno-a-uno).
- Que no se pueda crear ni editar `ReporteDiario`, `MuestraFluido`, `UsoMaterial`, `UsoEquipo` ni `Comentario` sobre un intervalo cerrado.
- Que `numero_reporte` sea correlativo por pozo y no se reinicie al abrir un segundo intervalo del mismo pozo.
- Que la matriz de propiedades muestre solo las propiedades correctas según la categoría del sistema de fluido del intervalo (probar con un intervalo "agua" y otro "aceite"/"sintético").
- Que `InventarioItem.cantidad_final` se recalcule bien con varios `UsoMaterial` encadenados sobre el mismo producto en el mismo reporte.
- Que `UsoEquipo.subtotal_costo` y `UsoMaterial.subtotal_costo` salgan siempre de la fórmula, nunca editables a mano.

## 2. Formalizar el cierre volumétrico contra el manual de ONE-TRAX

Sigue pendiente desde hace varias sesiones: validar con el manual de ONE-TRAX (mencionado por el experto que revisó la lógica) el detalle exacto de qué debe registrar un cierre — hoy el modelo pide profundidad final + volumen final + volumen no fluido + pérdida (Left in Hole) + usuario, pero no está confirmado que sea exactamente lo que exige el procedimiento real.

## 3. Misión 5 — Cálculo de volumen

Implementar la fórmula ya confirmada:

```
Volumen (bbl) = Libraje Final / (Gravedad Específica × 350)
```

Esto afecta principalmente a `InventarioItem`/`UsoMaterial` (volumen generado por movimiento de producto) y eventualmente al balance de volumen del intervalo. Requiere antes resolver la alerta de calidad de datos sobre `gravedad_especifica` en productos líquidos de CHAPALA (ver "Cosas a tener en cuenta.md").

También corresponde a esta misión formalizar el **catálogo de categorías de pérdida** (superficie, tanque, hoyo, shakers, evaporación, centrífuga, formación, dejado en hoyo, descargado, limpieza de pit — sección 7.4 del contexto original), hoy solo existe como texto libre implícito ("Left in Hole" en `CierreVolumetrico`).

## 4. Conectar la geometría del pozo a los datos reales

La pestaña "Geometría del Pozo" es hoy una demo aislada (un solo revestidor + hoyo abierto, sin backend). Pendiente:

- Extender a **múltiples intervalos de revestidor apilados** (uno por cada `Intervalo`/`TuberiaInstalada` real del pozo, no un único tramo fijo).
- Leer los datos desde la API en vez de valores por defecto hardcodeados.
- Integrar con la lógica de cierre de intervalos: cuando un intervalo se cierra, su tramo del dibujo debería "congelarse" igual que el resto de sus datos.

## 5. Módulos que aún no existen

Revisando la estructura completa del reporte original (sección 3 del contexto), todo lo estructural ya está cubierto. Lo que falta, si se decide implementarlo:

- Reportes/exportación en el formato "oficial" imprimible (como ya existe para `mychapala` con `api_reporte_oficial_data`).
- Historial/consulta de reportes cerrados de un pozo completo (todos los intervalos, no solo el activo).

## 6. Endurecer las APIs antes de producción

Hoy todos los endpoints de `reportes` (igual que los de `mychapala`) son `@csrf_exempt` y sin control de acceso. Mientras el sistema no vaya a producción real esto es aceptable, pero antes de ese paso conviene:

- Agregar autenticación (sesión de Django ya disponible, o tokens).
- Reemplazar `@csrf_exempt` por manejo correcto de CSRF en el frontend.
- Revisar permisos: quién puede cerrar un intervalo, quién puede eliminar registros, etc.

## 7. Decisión pendiente de alcance

Definir si el sistema `reportes` reemplaza eventualmente a `mychapala`, o si van a convivir permanentemente como dos módulos del mismo proyecto (uno más simple para inventario diario, otro más completo estilo ONE-TRAX). Esto determina si vale la pena, más adelante, migrar los datos históricos de `mychapala` hacia el esquema de `reportes`.
