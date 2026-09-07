# AGENTS.md — Sistema de reportes de fluidos de perforación

Este archivo define cómo debe trabajar cualquier agente de IA (Antigravity, Claude Code, etc.)
en este repositorio. Léelo completo antes de tocar código.

## 1. Qué es este proyecto

Sistema de reportes diarios de fluidos de perforación, inspirado en la lógica de ONE-TRAX
(M-I SWACO). Varias secciones conectadas entre sí van llenando un mismo reporte diario.
El sistema es **modular y configurable**: no todos los campos aplican siempre, dependen del
tipo de sistema de fluido (agua / aceite / sintético) y del estado del intervalo.

## 2. Stack

- **Backend:** Python + Django + PostgreSQL.
- **Frontend:** templates de Django + JavaScript **solo** donde sea estrictamente necesario
  (la geometría interactiva del pozo). No introducir un framework de frontend (React, Vue,
  etc.) salvo que se pida explícitamente — mantener esto simple.
- **Sin dependencias nuevas sin avisar.** Si crees que hace falta una librería externa
  (por ejemplo, para gráficos), decláralo en el plan/artefacto antes de instalarla.

## 3. Orden de trabajo (no te lo saltes)

El proyecto se construye deliberadamente de lo simple a lo complejo. No adelantes trabajo
de una fase sin haber cerrado la anterior, y no inventes tablas o campos que no estén en el
DER aprobado.

1. `Pozo`
2. `Intervalo` (+ `TuberiaInstalada`, `CierreVolumetrico`)
3. `ReporteDiario` (encabezado)
4. Conectar `InventarioItem` / `UsoMaterial` existentes a `ReporteDiario`
5. Matriz de propiedades selectivas (catálogo + reglas por tipo de sistema)
6. Volumen y balance de pérdidas (tanques, transacciones, categorías de pérdida)
7. Geometría interactiva del pozo (JS) — **al final, no antes**

El detalle paso a paso de cómo ejecutar cada fase está en `PASOS_ANTIGRAVITY.md`.

## 4. Reglas de dominio que NO se pueden romper

Estas reglas ya fueron validadas con el usuario. Cualquier cambio de modelo debe seguir
respetándolas o requiere confirmación explícita antes de tocarlas:

- Un **Intervalo** puede tener **varios** tramos de `TuberiaInstalada` (uno a muchos).
- `CierreVolumetrico` es **uno a uno** con `Intervalo`, y solo existe cuando el intervalo
  está cerrado.
- **No se puede crear ni editar** un `ReporteDiario`, `InventarioItem` ni `UsoMaterial` si
  el `Intervalo` al que pertenecen está `cerrado`. Esta validación vive en `clean()` de los
  modelos, no solo en el admin ni en las vistas — no la quites ni la muevas solo a
  formularios.
- `numero_reporte` es **correlativo por Pozo** (no se reinicia entre intervalos). Se calcula
  en `save()` con `select_for_update()` dentro de una transacción — si cambias esta lógica,
  mantén la protección de concurrencia.
- Al guardar un `CierreVolumetrico`, el `Intervalo` relacionado debe pasar automáticamente a
  `estado='cerrado'`. Nunca debe quedar un cierre sin que el intervalo lo refleje.
- El sistema trabaja en **unidades inglesas** (ft, in, bbl, lb) en todo el dominio de
  perforación/volumen. No mezclar con métrico salvo que el usuario lo pida para un campo
  específico.
- Los precios de productos **no son fijos**: el costo siempre se calcula
  (`cantidad × precio_unitario`), nunca se pide como input manual.

## 5. Fórmulas de dominio (usar exactamente estas, no aproximar)

```
libraje_final = libraje_unitario × cantidad
volumen (bbl) = libraje_final / (gravedad_específica × 350)

capacidad_tuberia (bbl) = (ID_tuberia² / 1029.4) × longitud

volumen_anular (bbl) = ((ID_hoyo_o_revestidor)² − (OD_tuberia)²) / 1029.4 × longitud
```

Si necesitas implementar cualquiera de estas, pon la constante (`350`, `1029.4`) como
constante nombrada en el código (ej. `LB_POR_BBL_AGUA = 350`), no como número mágico suelto.

## 6. Convenciones de código

- **Nombres de modelos y campos en español**, coincidiendo exactamente con el DER aprobado
  (`Pozo`, `Intervalo`, `TuberiaInstalada`, `CierreVolumetrico`, `ReporteDiario`, `Producto`,
  `InventarioItem`, `UsoMaterial`). No traduzcas al inglés ni abrevies distinto a como ya
  están.
- PK de todos los modelos: `UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`.
- Toda validación de negocio va en `clean()` del modelo, y `save()` debe llamar a
  `full_clean()` antes de guardar (salvo campos calculados marcados `editable=False`, que se
  excluyen explícitamente como en `ReporteDiario.save()`).
- Usa `models.TextChoices` para campos de estado/tipo (`estado`, `tipo`), no strings sueltos
  ni `choices=[...]` inline.
- Cambios de esquema van siempre acompañados de su migración (`makemigrations`). Nunca edites
  una migración ya aplicada en la base compartida; crea una nueva.

## 7. Qué NO hacer

- No agregues campos, tablas o relaciones fuera del DER sin señalarlo explícitamente en el
  plan/artefacto y pedir confirmación.
- No implementes la geometría interactiva del pozo antes de que el núcleo (pasos 1-4) esté
  probado con datos reales en el admin.
- No relajes las validaciones de intervalo cerrado "para probar más rápido" — si estorban
  durante desarrollo, créalas con un intervalo abierto, no quites la regla.
- No cambies las fórmulas de volumen/capacidad ni las constantes (350, 1029.4) sin que el
  usuario lo pida explícitamente.
- No introduzcas un ORM, librería de gráficos o framework de frontend nuevo sin aprobación.

## 8. Verificación antes de dar por terminada una fase

Para cada fase de `PASOS_ANTIGRAVITY.md`:

1. `python manage.py makemigrations --check` no debe reportar cambios pendientes sin migrar.
2. `python manage.py migrate` corre sin errores.
3. Se puede crear un registro de prueba end-to-end desde el admin (o un shell de Django)
   respetando las reglas de la sección 4.
4. Si la regla es "no se puede editar un intervalo cerrado", **pruébalo intentando romperlo**
   (crear un reporte en un intervalo cerrado) y confirma que lanza `ValidationError`.
5. Documenta en el artefacto/plan qué se probó y el resultado, no solo que "se implementó".

## 9. Archivos de referencia en este repositorio

- `contexto_proyecto_sistema_reportes_lodos.md` — contexto funcional completo del proyecto.
- `der_pozo_reportes.html` — DER aprobado del núcleo (Pozo → Intervalo → ReporteDiario).
- `models.py` / `admin.py` — implementación de referencia del núcleo, ya validada con el
  usuario. Úsalos como base, no los reescribas desde cero.
- `PASOS_ANTIGRAVITY.md` — plan de ejecución paso a paso para las siguientes fases.
