# Módulo 6B: Desplazamientos y Filtración de Salmueras (Displacements & Filtration)
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / View Daily Information (Displacements Tab & Filtration Tab)
**Referencia:** Manual ONE-TRAX 2.0 (Secciones 4.12 y 4.13, Páginas 148-155)

---

## 1. Módulo 4.12: Desplazamientos de Pozo (Displacements Tab)

### 1.1 Propósito y Cuándo se Utiliza
El módulo `Displacements` se activa cuando el pozo cambia la columna de fluido hidrostático en el hoyo (ej. transición de lodo base aceite OBM/SBM a salmuera limpia de completación, o desplazamiento de fluido de perforación a lodo de empaque / fluido de prueba de casing).

ONE-TRAX permite modelar el **tren de baches espaciadores y lavadores (Spacer Train)**, controlar el régimen de bombeo y reconciliar los volúmenes desplazados con la contabilidad de tanques (`Volume Accounting`).

### 1.2 Estructura del Desplazamiento
Cada desplazamiento se compone de dos secciones fundamentales:
1. **Información General del Desplazamiento (Displacement Section):**
   - `fluido_inicial`: Sistema de fluido en el hoyo al iniciar (ej. VERSACLEAN OBM).
   - `fluido_final`: Sistema de fluido entrante (ej. Salmuera $CaCl_2$ 11.5 ppg).
   - `tipo_desplazamiento`: Catálogo (`Casing Cleanout`, `Direct Displacement`, `Indirect Displacement`, `Drill-in Fluid Displacement`).
   - `fecha`: Fecha operativa.
   - `volumen_total_desplazado`: Capacidad total del hoyo a desplazar (bbl).
   - `tiempo_bombeo_total`: Horas totales de bombeo.
   - `presion_bombeo_promedio`: psi.
   - `datos_circulacion` (`Circulation Data Window`): Registro secuencial de presiones de bombeo, volúmenes de retorno observados y cortes de densidad en superficie.

2. **Componentes del Tren de Baches (Displacement Components Section):**
   Los baches se preparan previamente en fosas usando la opción `Mix Mud/Chemicals` de `Volume Accounting`. Cada bache se agrega secuencialmente con el botón `Add Component`:
   - `numero_orden`: Secuencia en el tren (Bache 1, 2, 3...).
   - `descripcion`: Nombre del bache (ej. `Bache Lavador Químico (Surfactant / Solvent)`, `Bache Viscoso (Hi-Vis Spacer)`, `Bache Pesado (Weighted Spacer)`, `Píldora Limpiadora (Scavenger Pill)`).
   - `fosa_origen`: Fosa de succión donde se mezcló el bache (ej. `Premix 1` o `Reserve 2`).
   - `volumen_bache`: Volumen formulado y bombeado (bbl).
   - `densidad_bache`: lb/gal (ppg).
   - `tasa_bombeo`: GPM o bbl/min.
   - `destino_retorno`:
     - `Reclaimed to Pit`: Recuperado hacia una fosa de superficie (no contaminada).
     - `Dumped / Discarded`: Desechado directamente a presas de descarte o barcaza/cuttings box.
   - `tabla_reologia`: Viscosidades a 600, 300, 200, 100, 6, 3 rpm del bache.
   - `parametros_breaker` (solo si el componente es un bache disruptor / desintegrador de revoque - *Breaker Pill*):
     - `tipo_breaker`: `Ácido (HCl / Acético)`, `Enzimático`, `Oxidante`.
     - `concentracion_aditivo`: lb/bbl o gal/bbl.
     - `tiempo_remojo` (`Soak Time`): Horas estáticas en fondo.
     - `viscosidad_residual`: cP.

### 1.3 Enlace Automático con Contabilidad de Volumen
Al guardar cada componente del desplazamiento:
- ONE-TRAX genera **automáticamente la transacción volumétrica correspondiente en `TransaccionFosa`**:
  - Si se bombea desde `Premix 1`, descuenta el volumen de esa fosa.
  - Si se descarta en superficie, registra la pérdida bajo la categoría `Displacement Loss / Dump`.
  - Si se recupera en `Reserve 1`, incrementa el volumen en dicha fosa.

---

## 2. Módulo 4.13: Filtración de Salmueras de Completación (Filtration Tab)

### 2.1 Responsabilidad Operativa
En pozos marinos y de alta productividad, el lodo de perforación daña irreversiblemente la permeabilidad de la arena productora. Por ello, la completación se realiza con **salmueras libres de sólidos (Clear Brines)** tratadas mediante unidades de filtración (Prensa de Hojas / Diatomeas DE y Unidades de Cartuchos de Pulido).

El Ingeniero de Fluidos recolecta la planilla del Técnico de Filtración e ingresa los ciclos diarios en la pestaña `Filtration`.

### 2.2 Ciclos de Filtración (Filtration Cycles)
Cada jornada puede contener de 1 a $N$ ciclos de filtración. Cada ciclo se despliega en una pestaña independiente dentro del módulo:

#### A. Parámetros del Ciclo:
1. **`numero_ciclo`:** Consecutivo diario (Ciclo 1, Ciclo 2, Ciclo 3...).
2. **`actividad_taladro` (`rig_activity`):** Operación en curso durante el ciclo (ej. `Circulando para Limpieza de Casing`, `Acondicionando Salmuera`, `Prueba de Completación`).
3. **`sistema_fluido`:** Salmuera activa (ej. $NaCl, KCl, CaCl_2, CaBr_2, NaBr$).
4. **`densidad_salmuera`:** lb/gal (ppg, con precisión de 2 decimales).
5. **`fosa_succion`:** Fosa o tanque desde donde la unidad de filtración toma la salmuera sucia (ej. `Reserve 1`).
6. **`fosa_descarga`:** Fosa destino donde se entrega la salmuera limpia y filtrada (ej. `Active 1` o `Brine Storage`).
7. **`volumen_filtrado`:** Barriles netos procesados en el ciclo (bbl).
8. **`volumen_no_filtrable` (`unfilterable_volume`):** Fondos de tanque o salmuera excesivamente contaminada que no pudo filtrarse (bbl).
9. **Tasas de Flujo (Flow Rates):**
   - `gasto_inicio`: GPM al arrancar el ciclo.
   - `gasto_final`: GPM al término (saturación de torta).
   - `gasto_promedio`: GPM promedio durante el ciclo.
10. **Tiempos:**
    - `hora_inicio` y `hora_fin` (duración del ciclo en horas).
11. **Insumos y Consumibles Utilizados:**
    - `cartuchos_usados`: Cantidad de cartuchos de polipropileno/fibra reemplazados (unidades).
    - `sacos_de_usados`: Sacos de tierra diatomea (DE - Diatomaceous Earth) pre-capa y cuerpo de alimentación consumidos (sacos).

### 2.3 Muestreo de Calidad y Turbidez (Quality & Turbidity Samples)
Para cada ciclo, es **estrictamente obligatorio** registrar la calidad al inicio (Succión) y al final (Descarga), y el sistema permite hasta **10 muestras intermedias**:
- **Turbidez en NTU (Nephelometric Turbidity Units):**
  - Mide la dispersión de luz producida por partículas coloidales microscópicas.
  - *Criterio de Aceptación Operativa:*
    - $\text{NTU} > 100$: Salmuera turbia e inaceptable para completación.
    - $30 \le \text{NTU} \le 100$: Calidad intermedia en proceso de recirculación.
    - $\text{NTU} < 20 - 30$: **Salmuera limpia aprobada para ingresar al yacimiento.**
- **Porcentaje de Sólidos (% Solids by Volume):**
  - Determinado mediante centrífuga manual con tubos API de vástago capilar ($< 0.05\%$).

### 2.4 Registro de Fallas y Tiempos No Productivos (Filtration Downtime & NPT)
Si ocurre una interrupción durante el ciclo de filtración:
- **`motivo_falla` (`downtime_reason`):** Selector de causas estandarizadas:
  - `Filter Cake Breakthrough (Ruptura de precapa DE)`.
  - `Cartridge Plugging (Taponamiento prematuro de cartuchos)`.
  - `Pump Failure (Falla de bomba de alimentación)`.
  - `Hose Leak (Fuga en mangueras de transferencia)`.
  - `Rig Power Failure (Corte de energía del taladro)`.
- **`hora_evento` y `duracion`:** Tiempo en minutos/horas que la unidad estuvo inoperativa.
- **`horas_npt`:** Horas imputadas a Tiempo No Productivo cargadas a la empresa de filtración o al taladro.

---

## 3. Mapeo a Modelos Django / PostgreSQL

### 3.1 Modelos Existentes en el Sistema
- **`OperacionFiltracion` (`reportes_operacionfiltracion`):**
  - `id`: UUID (PK).
  - `reporte`: ForeignKey a `ReporteDiario`.
  - `volumen_filtrado`: DecimalField(10, 2).
  - `horas_operacion`: DecimalField(5, 2).
  - `ntu_inicial`: DecimalField(6, 2).
  - `ntu_final`: DecimalField(6, 2).
  - `cartuchos_usados`: IntegerField(default=0).
  - `de_sacks_usados`: IntegerField(default=0).
  - `npt_horas`: DecimalField(5, 2, default=0).
  - `observaciones`: TextField(blank=True).

