# Pestaña 2 — Bombas y mecha (Pumps / Bits)

Bombas de lodo, mecha, boquillas, parámetros de perforación y presiones. De aquí salen el **caudal**, el **TFA** y el **diámetro del hoyo** que usan las pestañas 4, 6 y 8.

| | |
|---|---|
| Vistas | `views_daily_reports.api_pumps_bits_detail`, `api_pumps_bits_guardar`, `obtener_o_crear_pumps_bits` |
| Modelos | `ReporteDiarioBomba` (4 por reporte), `ReporteDiarioBitData` (1:1), `ReporteDiarioBoquilla` |
| API | `GET/POST /api/pozos/<pk>/daily-report/<reporte_pk>/pumps-bits/[guardar/]` |

## Primera apertura del día

Si el reporte no tiene datos de esta pestaña, `obtener_o_crear_pumps_bits` los crea:

- **Con reporte anterior**: copia las 4 bombas, la mecha completa y las boquillas.
- **Primer reporte del pozo**: valores de ejemplo de ONE-TRAX: bombas 1 y 2 EMSCO F-1000 6.5" × 12" al 97 % y 80 spm (activas); bomba 3 EMSCO F-1000 6" inactiva; bomba 4 vacía; mecha 12¼" Hycalog X-175 con 5 % de lavado; boquillas 2 × 14/32" y 3 × 13/32".

Conviene revisar y corregir esos valores el primer día.

## Bombas

Siempre son 4 filas (números 1 a 4).

| Campo | Default | Uso |
|---|---|---|
| Marca y modelo | | Texto libre con 15 sugerencias (EMSCO, National, Gardner Denver, Ideco, Wirth, Weatherford) |
| Diámetro de camisa (in) | 6.5 | |
| Largo de carrera (in) | 12 | |
| Diámetro de vástago (dúplex) | 0 | Solo informativo; el cálculo es tríplex |
| Eficiencia % | 97 | |
| Velocidad (spm) | 0 | |
| En reporte | | Si está desmarcada, la bomba no aporta caudal |
| Bomba de riser | | Informativo |

Cálculos (propiedades del modelo, bomba **tríplex**):

```
bbl/embolada = 0.000243 × camisa² × carrera × (eficiencia / 100)
gal/embolada = bbl/embolada × 42
caudal (gpm) = gal/embolada × spm        (0 si la bomba no está "en reporte")
```

Ejemplo: 6.5" × 12" al 97 % → 0.11950 bbl/stk; a 80 spm → 401.5 gpm por bomba; dos bombas → 803 gpm (el caudal del ejemplo del manual).

La lista de modelos es un campo con sugerencias. Al entrar al campo se vacía para mostrar los 15 modelos; si no se elige nada, al salir vuelve el valor anterior.

## Mecha

| Campo | Notas |
|---|---|
| Descripción, número, serie, código IADC, fabricante | Texto |
| Diámetro de la mecha (in) | `bit_size` |
| % de lavado (washout) | `washout_pct` |
| Diámetro con lavado | **Calculado al guardar**: `mecha × √(1 + lavado/100)`. Ej.: 12.25" con 5 % → 12.553" |

El diámetro con lavado es el diámetro de **hoyo abierto** de la pestaña 4 y el que usa la pestaña 6 para el volumen perforado.

## Boquillas

Filas de tamaño (en 32avos de pulgada) y cantidad. Se guardan reemplazando la lista; las filas con tamaño o cantidad 0 se descartan.

```
área de una boquilla (in²) = π/4 × (tamaño/32)²
TFA = Σ cantidad × área
```

Ej.: 2 × 14/32 + 3 × 13/32 → TFA ≈ 0.69 in².

## Parámetros de perforación y presiones

RPM de rotaria, horas rotando, peso sobre la mecha, ROP, caudal de bomba de riser, caudal de bombas, presión de bomba (se compara con la presión calculada en la hidráulica), ΔP MWD, ΔP motor y RPM del motor.

## Datos para ECD / equipo de superficie

| Campo | Uso en la hidráulica (pestaña 8) |
|---|---|
| Código de superficie | Pantalla: 1 = manual; 2 a 5 = combinaciones estándar de standpipe, manguera y swivel (con tabla de ayuda) |
| Presión en superficie (psi) | Presión de referencia medida en el equipo de superficie |
| Caudal de referencia (gpm) | Caudal al que se midió esa presión |
| Presión on/off bottom | Informativo |

Si se dan presión **y** caudal de referencia, la hidráulica escala la pérdida de superficie al caudal actual. Si no, usa la longitud equivalente del código.

Con código 1 y sin caudal de referencia, se usa la presión escrita tal cual. Ver [../HIDRAULICA_API13D.md](../HIDRAULICA_API13D.md#equipo-de-superficie).

## Qué usa esta pestaña después

| Dato | Lo usa |
|---|---|
| bbl/embolada de la primera bomba activa y caudal total | Pestaña 4: emboladas y minutos de fondo arriba |
| Diámetro con lavado | Pestaña 4 (hoyo abierto) y pestaña 6 (volumen perforado) |
| Caudal, TFA, diámetro de mecha, datos de superficie, presión de bomba | Pestaña 8, hidráulica |
