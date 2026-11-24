# 30 — Modificar pozo (matriz de corrección de parámetros iniciales)

Documento de referencia para la función **Modificar pozo**, añadida el **19-oct-2026** a solicitud de los ingenieros de perforación.

---

## 1. Propósito y necesidad operativa

Durante la creación del pozo mediante el Asistente (Wizard de 4 pasos) y la pantalla de Fecha Inicial (Spud Date), el ingeniero define los parámetros fundacionales del pozo:
- Identificación general (nombre, operador, campo, taladro, contratista).
- Sistema de unidades operacionales.
- Parámetros financieros (moneda base, decimales, tasa de impuesto, moneda secundaria de cobro).
- Parámetros iniciales de operación (fecha Spud / primera captura, tipo de fluido inicial, tratamiento/disposición, control LOGIT).
- Estructura de categorías de pérdidas de fluido.

En la versión anterior, estos datos quedaban bloqueados o divididos en configuraciones separadas, y corregir un error cometido durante el alta (por ejemplo, escribir mal el nombre del pozo, equivocarse en la fecha Spud o elegir un sistema de unidades o tipo de fluido incorrecto) requería intervención directa en base de datos.

La función **Modificar pozo** provee una **matriz técnica centralizada** que reúne todos los parámetros de creación del pozo y permite corregirlos en un único formulario seguro y validado.

---

## 2. Dónde se encuentra y cómo se accede

1. En la **Pantalla Principal del Pozo** (`/pozos/<id>/`), en la barra de acciones superior (junto a *Cerrar pozo* / *Reabrir pozo*, *Eliminar pozo* y *Papelera*):
   - Botón con icono de engranajes: **`⚙️ Modificar pozo`**.
2. URL directa: `/pozos/<id>/modificar/` (`name='pozo_modificar'`).
3. La interfaz cuenta con navegación contextual hacia la pantalla principal del pozo y breadcrumbs claros.

---

## 3. Matriz de parámetros editables

El formulario se organiza en 5 bloques técnicos correspondientes a las secciones del alta del pozo:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MATRIZ DE MODIFICACIÓN                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Identificación del Pozo                                             │
│    - Nombre del pozo (único; valida colisión con activos y papelera)  │
│    - Operador                                                         │
│    - Campo / Área                                                      │
│    - Taladro de perforación                                           │
│    - Contratista                                                       │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Sistema de Unidades                                                 │
│    - Standard Oilfield (ft, in, bbl, gpm, lb/gal, psi)                │
│    - SI Métrico                                                        │
│    - Canadiense (m³, kPa)                                             │
├────────────────────────────────────────────────────────────────────────┤
│ 3. Parámetros Financieros y Monedas                                    │
│    - Moneda principal (USD, VES, EUR, COP, etc.)                      │
│    - Decimales en reportes financieros (0 a 4)                         │
│    - Tasa de impuesto IVA / Sales Tax (%) (0 a 100)                    │
│    - Moneda secundaria de cobro (opcional)                            │
│    - Cobrar en moneda secundaria (casilla)                            │
├────────────────────────────────────────────────────────────────────────┤
│ 4. Parámetros Iniciales y Spud Date                                    │
│    - Fecha Spud / Primera captura (sincronizada en Pozo y Header)      │
│    - Tipo de fluido inicial (Base Agua, Aceite, Sintética, etc.)      │
│    - Con tratamiento y disposición ambiental                           │
│    - Número de control LOGIT                                          │
├────────────────────────────────────────────────────────────────────────┤
│ 5. Clasificación de Pérdidas de Lodo                                   │
│    - Categoría de pérdidas (Estándar MI, UK, Hydro, Statoil, etc.)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Validaciones y reglas de negocio

1. **Unicidad de Nombre:**
   - No permite colisionar con otro pozo activo ni con un pozo en la **Papelera** (`Pozo.todos.filter(nombre__iexact=...)`).
   - Si el usuario conserva el nombre actual del pozo que está modificando, se permite sin conflicto (`.exclude(pk=pozo.pk)`).

2. **Sincronización Atómica entre Modelos:**
   - La información de cabecera reside dividida entre `Pozo` y su modelo relacionado `WellHeaderInfo`.
   - La vista guarda ambos dentro de una transacción atómica:
     - `pozo.nombre` se actualiza en `Pozo`.
     - `operador`, `field_area`, `nombre_taladro` y `contratista` se actualizan en `WellHeaderInfo`.
     - `spud_date` se actualiza en `WellHeaderInfo.spud_date` y en `Pozo.fecha_primera_captura`.
     - `tipo_fluido_inicial` se actualiza en `Pozo.tipo_fluido_inicial` y en `WellHeaderInfo.primary_mud_type_codigo`.

3. **Restricciones de Moneda y Números:**
   - Los decimales deben estar en el rango de 0 a 4.
   - La tasa de impuesto debe estar entre 0.00 % y 100.00 %.
   - Si se activa `cobrar_en_secundaria`, se exige haber seleccionado una `moneda_secundaria` diferente a la moneda principal.
   - **Bloqueo por reportes existentes:** Si el pozo ya tiene reportes diarios registrados, la moneda principal y la opción de cobro en segunda moneda quedan bloqueadas tanto visualmente como en backend para preservar la consistencia contable del histórico.

4. **Protección de Spud Date contra Reportes:**
   - Si el pozo ya tiene reportes diarios, la fecha inicial (`spud_date`) no puede ser modificada a un valor posterior a la fecha del primer reporte diario existente.

5. **Protección de Pozo Cerrado:**
   - Si el pozo se encuentra en estado `CERRADO`, la interfaz muestra un banner de solo lectura y deshabilita todos los campos y el botón de guardar. En el backend, cualquier petición `POST` es rechazada indicando que el pozo debe ser reabierto previamente.

6. **Soporte Híbrido (HTML estándar y AJAX):**
   - El formulario admite tanto envíos web tradicionales `POST` con redirección automática a la pantalla del pozo como llamadas asíncronas JSON vía AJAX / `fetch`.

---

## 5. Archivos involucrados

| Archivo | Qué hace |
|---|---|
| `operaciones/forms_pozo.py` | Clase `PozoModificarForm` con todos los campos, widgets limpios y validaciones de reportes, monedas y Spud Date. |
| `operaciones/views.py` | Vista `pozo_modificar_view` (GET y POST seguro con transacción y rechazo en pozos cerrados). |
| `operaciones/urls.py` | Ruta `pozos/<int:pk>/modificar/`. |
| `operaciones/templates/operaciones/pozos/modificar.html` | Plantilla responsiva con diseño técnico, tarjetas por sección, bloqueo de pozo cerrado y badges de campos bloqueados por reportes. |
| `operaciones/templates/operaciones/pozos/main.html` | Botón de acceso directo `Modificar pozo` en la barra superior. |
| `operaciones/tests/test_modificar_pozo.py` | 11 pruebas unitarias automatizadas cubriendo todas las ramas de edición, pozo cerrado, reportes y validación. |
| `docs/pruebas/26_MODIFICAR_POZO.md` | Guía de verificación paso a paso con casillas de prueba. |

