# Estructura de las tablas

Esquema de base de datos de las dos apps. Todos los modelos de `reportes` usan `UUID` como llave primaria; los de `mychapala` usan enteros autoincrementales (esquema heredado, no se tocó).

---

## App `mychapala` (Inventario CHAPALA)

### `Producto`

| Campo | Tipo | Notas |
|---|---|---|
| id | Integer (PK) | autoincremental |
| codigo | CharField, único | ej. `AOS-1001` |
| descripcion | CharField | nombre del producto |
| categoria | CharField | químico / líquido / wellsite |
| unidad | CharField | texto libre legado |
| libraje | CharField | texto libre legado, no operable |
| gravedad_especifica | CharField | texto libre — **ver alerta de calidad de datos en "Cosas a tener en cuenta.md"** |
| cantidad | Integer | stock actual |
| precio_unitario | Decimal | por unidad de empaque |
| cum_used / cum_received / daily_received / daily_return / cum_return | Integer | acumulados de movimiento |
| activo | Boolean | soft-delete |
| **cantidad_unitaria** | Decimal, nullable | agregado — cantidad por unidad de empaque |
| **unidad_medida** | CharField (choices: LB/KG/GA/LT/BBL/EA) | agregado |
| **tipo_empaque** | CharField (choices: BG/CN/DM/TOTE/BLS/EA) | agregado |

### `ReporteDiario`

Encabezado del reporte del día (metadatos generales, observaciones, costo total). Ver `mychapala/models.py` para el detalle exacto de campos — no se modificó en este ciclo de trabajo.

### `RegistroUso`

Transacción individual de salida de un producto, ligada a `ReporteDiario` y `Producto`. Tiene `libraje_usado` como propiedad calculada (no columna).

---

## App `reportes` (esquema ONE-TRAX)

### `Pozo`
| Campo | Tipo |
|---|---|
| id | UUID (PK) |
| nombre | CharField |
| operador | CharField |
| ubicacion | CharField |
| campo_area | CharField, opcional |
| fecha_spud | Date, opcional |

### `SistemaFluido` (catálogo editable — "gama de fluidos")
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| nombre | CharField, único | ej. "Lodo Polimérico KCl" |
| categoria | CharField (choices) | `agua` / `polimerico` / `aceite` / `sintetico` / `otro` — define qué propiedades aplican |
| descripcion | TextField, opcional | |

### `Intervalo`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| pozo | FK → Pozo | `on_delete=PROTECT` |
| numero | PositiveInteger | único por pozo |
| sistema_fluido | FK → SistemaFluido | `on_delete=PROTECT`, fijo mientras el intervalo está abierto |
| profundidad_inicial | Decimal | ft |
| profundidad_final | Decimal, opcional | ft — se fija al cerrar |
| diametro | Decimal | in — diámetro de hoyo o revestidor |
| estado | CharField (choices) | `abierto` / `cerrado` |
| fecha_apertura | Date, automática | |
| fecha_cierre | Date, opcional | se llena al cerrar |

Restricción: `(pozo, numero)` único.

### `TuberiaInstalada`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| intervalo | FK → Intervalo | `on_delete=CASCADE` — varios tramos por intervalo |
| tipo | CharField (choices) | `revestidor` / `liner` / `otro` |
| longitud | Decimal | ft |
| diametro_externo | Decimal | in (OD) |
| diametro_interno | Decimal | in (ID) |

### `CierreVolumetrico`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| intervalo | OneToOne → Intervalo | `on_delete=PROTECT` — uno solo por intervalo |
| volumen_final | Decimal | bbl |
| volumen_no_fluido | Decimal | bbl — lo atrapado bajo la profundidad de cierre |
| perdida_left_in_hole | Decimal | bbl — pérdida registrada para que el balance cuadre |
| usuario | CharField | quien registra el cierre |
| fecha_cierre | DateTime, automática | |

Al guardarse, marca automáticamente `Intervalo.estado = 'cerrado'`.

### `Producto` (catálogo propio de `reportes`, independiente del de `mychapala`)
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| nombre | CharField | |
| codigo | CharField, único | |
| cantidad_unitaria | Decimal | |
| unidad_medida | CharField (choices: LB/KG/GA/EA) | |
| tipo_empaque | CharField (choices: BG/CN/DM/TOTE/BLS/EA) | |
| precio_unitario | Decimal | puede cambiar entre reportes |
| gravedad_especifica | Decimal | |

### `ReporteDiario`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| intervalo | FK → Intervalo | `on_delete=PROTECT` — no directamente a Pozo |
| fecha | Date | |
| numero_reporte | PositiveInteger, no editable | correlativo **por pozo**, asignado automáticamente |
| actividad | CharField, opcional | |
| peso_lodo | Decimal, opcional | lb/gal |

Restricción: `(intervalo, fecha)` único. Bloqueado si `intervalo.estado == 'cerrado'`.

### `InventarioItem`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| reporte | FK → ReporteDiario | |
| producto | FK → Producto | `on_delete=PROTECT` |
| cantidad_inicial | Decimal | |
| cantidad_entrada | Decimal, default 0 | |
| cantidad_final | Decimal, no editable | calculada: inicial + entrada − suma de usos del día |

Restricción: `(reporte, producto)` único.

### `UsoMaterial`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| reporte | FK → ReporteDiario | |
| producto | FK → Producto | `on_delete=PROTECT` |
| cantidad_usada | Decimal | |
| hora_registro | Time, automática | |

### `PropiedadCatalogo` (catálogo maestro — Misión 4)
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| codigo | SlugField, único | ej. `mud_weight`, `pv`, `r600` |
| nombre | CharField | ej. "Peso del Lodo" |
| unidad | CharField, opcional | ej. "lb/gal"; vacío para adimensionales |
| orden | PositiveInteger | orden de aparición en el reporte |

### `PropiedadSistema` (la "matriz")
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| propiedad | FK → PropiedadCatalogo | |
| categoria_sistema | CharField (choices) | igual a `SistemaFluido.Categoria` |
| obligatoria | Boolean, default True | |

Restricción: `(propiedad, categoria_sistema)` único.

### `MuestraFluido`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| reporte | FK → ReporteDiario | |
| identificador | CharField | ej. "TK 2 20:00" |
| orden | PositiveInteger, default 0 | |

### `PropiedadValor`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| muestra | FK → MuestraFluido | |
| propiedad | FK → PropiedadCatalogo | `on_delete=PROTECT` |
| valor | Decimal (12,4) | |

Restricción: `(muestra, propiedad)` único. `clean()` valida que la propiedad esté habilitada para la categoría del sistema de fluido del intervalo del reporte.

### `Equipo` (catálogo)
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| nombre | CharField | |
| codigo | CharField, único | |
| costo_diario | Decimal | tarifa vigente, puede cambiar entre reportes |

### `UsoEquipo`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| reporte | FK → ReporteDiario | |
| equipo | FK → Equipo | `on_delete=PROTECT` |
| horas_usadas | Decimal (5,2) | |

`subtotal_costo` (propiedad calculada, no columna) = `costo_diario × horas_usadas / 24`.

### `Comentario`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID (PK) | |
| reporte | FK → ReporteDiario | |
| texto | TextField | |
| autor | CharField, opcional | |
| fecha_hora | DateTime, automática | |

---

## Relaciones — vista general (`reportes`)

```
Pozo
 └── Intervalo (1:N)
      ├── TuberiaInstalada (1:N)
      ├── CierreVolumetrico (1:1)
      └── ReporteDiario (1:N)
           ├── MuestraFluido (1:N)
           │    └── PropiedadValor (1:N) → PropiedadCatalogo
           ├── InventarioItem (1:N) → Producto
           ├── UsoMaterial (1:N) → Producto
           ├── UsoEquipo (1:N) → Equipo
           └── Comentario (1:N)

SistemaFluido ← referenciado por Intervalo
PropiedadCatalogo ← referenciado por PropiedadSistema (matriz) y PropiedadValor
```

Todos los modelos que cuelgan de `ReporteDiario` (directa o indirectamente vía `Intervalo`) quedan bloqueados para creación/edición en cuanto `Intervalo.estado == 'cerrado'`.
