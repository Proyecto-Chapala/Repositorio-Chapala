# PASOS_ANTIGRAVITY.md — Plan de ejecución por misiones

Este documento está pensado para usarse dentro de Antigravity: cada sección de abajo es una
**misión** independiente que se le puede dar al Agent Manager. No lances la siguiente misión
hasta que la anterior tenga su artefacto de verificación aprobado.

Antes de empezar cualquier misión: el agente debe leer `AGENTS.md` completo.

---

## Misión 0 — Preparar el proyecto base

**Objetivo:** tener un proyecto Django funcional donde meter las siguientes fases.

**Instrucciones para el agente:**
1. Crear el proyecto Django y una app llamada `reportes`.
2. Configurar `DATABASES` para PostgreSQL (pedir al usuario las credenciales/host si no están
   en variables de entorno; no inventar credenciales).
3. Copiar `models.py` y `admin.py` (ya provistos en el repositorio) dentro de `reportes/`.
4. Agregar `reportes` a `INSTALLED_APPS`.

**Verificación (debe quedar como artefacto):**
- `python manage.py check` sin errores.
- `python manage.py makemigrations reportes` genera la migración inicial sin advertencias
  inesperadas.
- `python manage.py migrate` corre limpio contra PostgreSQL.
- Se crea un superusuario y se entra al `/admin/` sin errores 500.

---

## Misión 1 — Núcleo: Pozo, Intervalo, Tubería, Cierre

**Objetivo:** validar el núcleo de datos ya modelado en `models.py`.

**Instrucciones para el agente:**
1. No reescribir los modelos — ya están definidos y aprobados. Solo ajustar lo mínimo
   necesario para que corran en el proyecto (imports, `app_label`, etc.).
2. Desde el admin, crear:
   - Un `Pozo` de prueba.
   - Dos `Intervalo` para ese pozo (número 1 y número 2).
   - Al menos un `TuberiaInstalada` para el intervalo 1 (probar que se puede agregar más de
     uno).
   - Un `CierreVolumetrico` para el intervalo 1.

**Verificación (artefacto obligatorio, con capturas o log del shell):**
- Confirmar que al guardar el `CierreVolumetrico`, el `Intervalo` 1 pasó automáticamente a
  `estado='cerrado'` (revisar en el admin o con `Intervalo.objects.get(numero=1).estado`).
- Intentar crear un segundo `TuberiaInstalada` para el mismo intervalo y confirmar que **sí**
  se permite (uno a muchos).
- Intentar crear un segundo `CierreVolumetrico` para el mismo intervalo y confirmar que
  **falla** (uno a uno).

**No avanzar a la Misión 2 si alguna de estas verificaciones no pasa.**

---

## Misión 2 — Reporte diario + bloqueo por intervalo cerrado

**Objetivo:** validar `ReporteDiario` y su correlativo por pozo.

**Instrucciones para el agente:**
1. Crear 2-3 `ReporteDiario` para el intervalo 2 (que sigue abierto) del pozo de prueba, en
   fechas distintas.
2. Intentar crear un `ReporteDiario` para el intervalo 1 (ya cerrado en la Misión 1).

**Verificación (artefacto obligatorio):**
- Los reportes del intervalo 2 deben tener `numero_reporte` correlativo (1, 2, 3…) **a nivel
  de pozo**, no reiniciado por intervalo. Si el pozo ya tenía reportes previos en el
  intervalo 1, el correlativo debe continuar desde ahí.
- El intento de crear un reporte en el intervalo 1 (cerrado) debe lanzar `ValidationError`.
  Pegar el traceback o el mensaje de error en el artefacto como evidencia — no basta con
  decir "funciona".
- Probar la concurrencia mínimamente: documentar que `save()` usa
  `select_for_update()` dentro de una transacción (revisión de código, no hace falta un test
  de carga en esta fase).

---

## Misión 3 — Conectar Inventario y Uso de Material existentes

**Objetivo:** migrar las tablas de inventario que el usuario ya tenía construidas para que
cuelguen de `ReporteDiario`.

**Instrucciones para el agente:**
1. Revisar el código de inventario existente del usuario (pedirlo si no está en el
   repositorio) antes de modificar nada.
2. Ajustar las FKs para que apunten a `ReporteDiario` en vez de estar sueltas o apuntar
   directo al pozo.
3. Migrar datos existentes si los hay (escribir una migración de datos, no solo de esquema,
   si hay registros previos que preservar).

**Verificación:**
- Cargar un `InventarioItem` y varios `UsoMaterial` del mismo producto en el mismo
  `ReporteDiario` (simulando uso de mañana y tarde).
- Confirmar que `InventarioItem.cantidad_final` se recalcula solo y refleja la suma de
  **todos** los `UsoMaterial` de ese producto en ese reporte, no solo el último.
- Repetir el intento de crear un `UsoMaterial` en un intervalo cerrado y confirmar que
  también falla (la validación es compartida vía `MovimientoProducto`).

---

## Misión 4 — Matriz de propiedades selectivas

**Objetivo:** modelar el catálogo de propiedades y qué propiedades aplica cada tipo de
sistema (agua / aceite / sintético).

**Instrucciones para el agente:**
1. Antes de crear modelos nuevos, proponer el esquema (nombres de tabla y campos) en el
   artefacto de plan y esperar confirmación — esta fase no tiene un DER aprobado todavía
   como el núcleo.
2. Un `Producto` o propiedad activa en un `ReporteDiario` debe poder guardar su valor
   solamente si esa propiedad está habilitada para el tipo de sistema de ese reporte/pozo.

**Verificación:**
- Crear un sistema tipo "sintético" y confirmar que solo aparecen/pueden guardarse las
  propiedades marcadas como aplicables a sintético en el catálogo.
- Documentar en el artefacto qué propiedades se usaron de referencia (comparar contra la
  hoja `Synthetic-Based Mud` del mud report de referencia, ya descrita en
  `contexto_proyecto_sistema_reportes_lodos.md`).

---

## Misión 5 — Volumen y balance de pérdidas

**Objetivo:** tanques, transacciones de volumen y categorías de pérdida estandarizadas.

**Instrucciones para el agente:**
1. Proponer el esquema en el artefacto de plan antes de crear modelos (mismo criterio que
   Misión 4).
2. Implementar las fórmulas de la sección 5 de `AGENTS.md` como funciones o métodos
   reutilizables, con las constantes nombradas — no repetir el cálculo inline en varios
   lugares.

**Verificación:**
- Probar el ejemplo ya validado: tubería OD 5", ID 4.276", hoyo 7", longitud 2900 ft →
  capacidad interna ≈ 51.5 bbl, volumen anular ≈ 67.6 bbl. Si el cálculo no da estos números
  (con margen de redondeo razonable), hay un error en la implementación.
- Confirmar que las categorías de pérdida (superficie, tanque, hoyo, shakers, evaporación,
  centrífuga, formación, dejado en hoyo, descargado, limpieza de pit) están cargadas como
  catálogo, no como texto libre.

---

## Misión 6 — Geometría interactiva del pozo (al final)

**Objetivo:** vista con el esquema del pozo que se redibuja en vivo, basada en el prototipo
ya validado con el usuario.

**Instrucciones para el agente:**
1. No empezar esta misión si las Misiones 1 a 5 no están verificadas y aprobadas por el
   usuario.
2. Usar JavaScript solo para el redibujado del esquema (SVG o canvas); los cálculos de
   volumen deben reusar la misma lógica de la Misión 5 (idealmente expuesta vía un endpoint o
   replicada explícitamente documentando que es una copia intencional para el cliente).
3. Basarse en el prototipo ya mostrado al usuario (sliders de profundidad total, profundidad
   de zapata, diámetros de hoyo/revestidor/tubería) como referencia de comportamiento
   esperado, extendiéndolo a **múltiples intervalos de revestidor apilados**.

**Verificación:**
- El esquema se reescala correctamente al cambiar cualquier input (no solo al cargar la
  página).
- Los números mostrados en pantalla (capacidad, volumen anular) coinciden con los calculados
  en el backend para los mismos valores.
- Probar con un intervalo cerrado: el esquema debe mostrarse pero no permitir edición de sus
  valores.

---

## Regla general para todas las misiones

Si en cualquier punto el agente necesita **inventar** un campo, una regla de negocio o un
valor que no está en `AGENTS.md`, `contexto_proyecto_sistema_reportes_lodos.md` o el DER
aprobado, debe detenerse y dejarlo como pregunta explícita en el artefacto en vez de asumir
y continuar.
