# Propuesta de esquema — Misión 4: Matriz de propiedades selectivas

Pendiente de confirmación del usuario antes de crear modelos (regla de Misión 4 en `PASOS_ANTIGRAVITY.md`). Corresponde al esquema ONE-TRAX (Pozo/Intervalo/SistemaFluido), no a CHAPALA.

## Fuente: catálogo real extraído de las hojas MUD PROPERTIES del Mud Report 16 PERLA-1X

Se revisaron `WBM Check`, `CALDRIL Check`, `OBM Check` y `Synthetic-Based Mud` (data_only). Las 4 comparten un bloque de propiedades comunes y luego se separan en dos familias: base agua (WBM/CALDRIL) y base aceite/sintético (OBM/SBM — prácticamente idénticas entre sí, solo cambian nombres: "Oil" vs "Synthetic", "Pom" vs "Psm").

### Propiedades comunes a todos los sistemas

| código           | nombre                   | unidad    |
| ---------------- | ------------------------ | --------- |
| flowline_temp    | Flowline Temp            | °F        |
| mud_weight       | Peso del Lodo            | lb/gal    |
| funnel_viscosity | Viscosidad Embudo        | s/qt      |
| rheology_temp    | Temp. Reología           | °F        |
| r600_r300        | R600/R300                | —         |
| r200_r100        | R200/R100                | —         |
| r6_r3            | R6/R3                    | —         |
| pv               | Viscosidad Plástica (PV) | cP        |
| yp               | Punto Cedente (YP)       | lb/100ft² |
| gel_10s_10m_30m  | Geles 10s/10m/30m        | lb/100ft² |
| api_fluid_loss   | Filtrado API             | cc/30min  |
| hthp_fluid_loss  | Filtrado HTHP            | cc/30min  |
| cake_apt_ht      | Revoque APT/HT           | 1/32"     |

### Solo base agua (categoría `agua`, aplica también a CALDRIL)

| código        | nombre                | unidad |
| ------------- | --------------------- | ------ |
| solids_pct    | Sólidos               | %Vol   |
| oil_water_pct | Aceite/Agua           | %Vol   |
| sand_pct      | Arena                 | %Vol   |
| mbt           | MBT                   | lb/bbl |
| ph_temp       | pH/Temp               | —      |
| alkal_mud_pm  | Alcalinidad Lodo (Pm) | —      |
| pf_mf         | Pf/Mf                 | —      |
| chlorides     | Cloruros              | mg/L   |
| hardness_ca   | Dureza (Ca++)         | mg/L   |

### Solo base aceite / sintético (categorías `aceite` y `sintetico`)

| código             | nombre                             | unidad |
| ------------------ | ---------------------------------- | ------ |
| unc_ret_solids_pct | Sólidos Retenidos sin Corregir     | %Vol   |
| correct_solids_pct | Sólidos Corregidos                 | %Vol   |
| base_fluid_pct     | % Vol de fase base (Oil/Synthetic) | %Vol   |
| uncorr_water_pct   | Agua sin Corregir                  | %Vol   |
| base_water_ratio   | Relación fase base / Agua          | —      |
| alkal_mud_pom_psm  | Alcalinidad Lodo (Pom/Psm)         | —      |
| cl_whole_mud       | Cl- Lodo Entero                    | mg/L   |
| salt_pct           | Sal                                | %Wt    |
| lime               | Cal                                | lb/bbl |
| emul_stability     | Estabilidad de Emulsión            | —      |

**Fuera de alcance de esta misión** (no está en la sección "MUD PROPERTIES", pertenece a otra parte del reporte): los bloques "SOLIDS ANALYSIS" y "RHEOLOGY & HYDRAULICS" de la hoja CALDRIL (Calcium Chloride, Brine Specific Gravity, ECD, Jet Velocity, etc.) — esos son cálculos de volumen/hidráulica, corresponden a la Misión 5, no a la matriz de propiedades.

## Hallazgo importante: múltiples muestras por reporte

Cada mud report NO tiene un solo valor por propiedad — tiene una fila "Sample From" con 2 a 4 muestras por día (ej. "TK 2 20:00", "TK 2 12:00" en WBM; "TK1 12:00", "TK1 0:00", "TK3 12:00", "TK3 0:00" en SBM/OBM), y cada muestra tiene su propio valor para cada propiedad activa. El contexto original (sección 4) no mencionaba esto explícitamente — decía "matriz con las propiedades activas... de ahí sale el listado que puede llenarse en el reporte de ese día", sin precisar si es un valor único o varios por muestra.

## Esquema propuesto (4 modelos)

```
PropiedadCatalogo
  id (UUID)
  codigo (slug único, ej. "mud_weight")
  nombre (ej. "Peso del Lodo")
  unidad (ej. "lb/gal", puede ser "" para las que son pares tipo "R600/R300")
  orden (int, orden de aparición en el reporte)

PropiedadSistema  (la "matriz": qué propiedad aplica a qué categoría de sistema)
  id
  propiedad (FK -> PropiedadCatalogo)
  categoria_sistema (choice, igual a SistemaFluido.Categoria: agua/polimerico/aceite/sintetico/otro)
  obligatoria (bool — si debe estar cargada para poder cerrar el reporte/intervalo)
  unique_together (propiedad, categoria_sistema)

MuestraFluido  (una muestra tomada en el día, ej. "TK 2 20:00")
  id
  reporte (FK -> ReporteDiario)
  identificador (texto libre, ej. "TK 2 20:00")
  orden (int, orden de la muestra en el día)

PropiedadValor  (el valor de una propiedad en una muestra concreta)
  id
  muestra (FK -> MuestraFluido)
  propiedad (FK -> PropiedadCatalogo)
  valor (CharField — ver nota de tipo de dato abajo)
  unique_together (muestra, propiedad)
```

`PropiedadValor.clean()` validaría que `propiedad` esté habilitada (vía `PropiedadSistema`) para la `categoria_sistema` del `SistemaFluido` del intervalo del reporte de la muestra — así se aplica la selectividad.

## 3 decisiones pendientes de tu confirmación

1. **¿Modelamos varias muestras por reporte (como el Excel real) o simplificamos a un solo valor por propiedad por día?** La primera opción (`MuestraFluido` + `PropiedadValor`) es más fiel al mud report real pero más compleja de operar/llenar. La segunda es más simple pero pierde la granularidad de "mañana/tarde" que sí se usa en producción.
2. **¿El valor de cada propiedad se guarda como texto libre (CharField) o separamos las propiedades compuestas (R600/R300, R200/R100, R6/R3, Pf/Mf) en dos campos numéricos cada una** (ej. `r600` y `r300` en vez de un solo "R600/R300")? Separarlas permite calcular con ellas directamente; dejarlas como texto es más fiel al formato del Excel pero no son operables sin parsear.
3. **¿La categoría `polimérico` usa el mismo catálogo que `agua` (WBM), o necesita su propio subconjunto?** El Mud Report de referencia no tiene una hoja "Polymer Check" separada — solo WBM, OBM, SBM y CALDRIL — así que no tengo una fuente real para diferenciarlo todavía.
