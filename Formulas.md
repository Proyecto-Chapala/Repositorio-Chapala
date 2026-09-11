# Módulo Extra: Compendio de Fórmulas y Lógica de Negocio
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / Core Calculation Engine

Este documento centraliza todas las fórmulas matemáticas, cálculos de balance de masa y reglas de negocio extraídas del manual[cite: 2]. Sirve como guía de referencia para la programación de los controladores y servicios en el backend (PostgreSQL/Python).

---

## 1. Geometría y Volúmenes del Hoyo
**Módulo / Pestaña:** `View Daily Information` -> `Geometry Tab`

### A. Volumen Neto de Fluido en el Pozo
$$Fluid\ Volume = Total\ Hole\ Volume - Volume\ Not\ Fluids$$

*   **Cómo se usa:** El usuario ingresa manualmente el `Volume Not Fluids` (ej. agua de mar o aire) y el sistema lo resta del volumen geométrico total del hoyo[cite: 2].
*   **Para qué sirve:** Para saber exactamente cuántos barriles del sistema activo están en el subsuelo y reflejarlo en la sección `Fluids in Hole` de `Volume Accounting`[cite: 2]. Si no se resta, el balance volumétrico de los tanques en superficie arrojará un error[cite: 2].

### B. Capacidad Total del Hoyo
$$Total\ Hole\ Volume = Annulus + Total\ DS + Below\ Bit$$

*   **Cómo se usa:** El sistema suma el volumen del espacio anular, el volumen interno de la sarta de perforación (`DS`) y el volumen por debajo de la mecha[cite: 2].
*   **Para qué sirve:** Define la capacidad máxima de fluidos que puede contener la arquitectura del pozo en un momento dado[cite: 2].

---

## 2. Hidráulica y Reología
**Módulo / Pestaña:** `View Daily Information` -> `Pumps/Bits Tab` & `Fluid Checks Tab`

### A. Régimen de Flujo (Número de Reynolds)
*   **Regla Lógica:** Si $AnnRe > 2000 \rightarrow Flujo\ Turbulento$
*   **Cómo se usa:** El sistema calcula el Número de Reynolds Anular (`AnnRe`) para cada sección transversal del pozo[cite: 2].
*   **Para qué sirve:** Determina si el flujo es laminar o turbulento, lo cual es crítico para calcular la limpieza del hoyo y predecir la velocidad crítica anular (`AnnVCritical`)[cite: 2].

---

## 3. Balance de Masa: Descartes y Control de Sólidos
**Módulo / Pestaña:** `View Daily Information` -> `Equipment Tab`

### A. Porcentaje de Lodo en Descarga
$$\%\ Lodo = \frac{Mud\ On\ Cuttings}{1 + Mud\ On\ Cuttings}$$

*   **Cómo se usa:** Si el usuario ingresa un `Mud On Cuttings` de $0.8$ (0.8 bbl de lodo por cada 1.0 bbl de ripio), la fórmula calcula: $\frac{0.8}{1.8} \approx 44\%$[cite: 2].
*   **Para qué sirve:** Traduce la relación ingresada por el operario a un porcentaje real de pérdida volumétrica[cite: 2].

### B. Distribución de Ripios por Equipo
$$\%\ Cuttings\ Removed\ (Individual) = \frac{\%\ Total\ Removido\ por\ el\ Sistema}{Cantidad\ de\ Equipos\ Activos}$$

*   **Cómo se usa:** Si 3 zarandas (Shakers) remueven en conjunto el $90\%$ de los sólidos, el usuario debe ingresar $30\%$ para cada zaranda individual[cite: 2].
*   **Para qué sirve:** Reparte la carga másica de los ripios perforados entre el hardware disponible para calcular eficiencias individuales[cite: 2].

### C. Lodo Perdido en Sólidos (Volume of Mud On Solids Discarded)
$$V_{lodo\_perdido} = V_{solidos\_removidos} \times Mud\ On\ Cuttings$$

*   **Cómo se usa:** Toma los barriles de roca sólida que separó la máquina y los multiplica por el factor de retención de humedad ingresado por el usuario[cite: 2].
*   **Para qué sirve:** Es la fórmula más crítica del control de sólidos. Este resultado exacto se importa a `Volume Accounting` mediante el botón `Create Equipment Loss Transaction` para descontar el lodo del sistema activo[cite: 2].

### D. Volumen Diario Descartado (Sludge)
$$V_{sludge} = V_{solidos\_removidos} + V_{lodo\_perdido}$$

*   **Cómo se usa:** Suma la roca sólida y el lodo líquido adherido a ella[cite: 2].
*   **Para qué sirve:** Determina el volumen total de desechos (pasta húmeda) que debe gestionarse ambientalmente o enviarse a cajas de recortes (`Cuttings Box`)[cite: 2].

---

## 4. Contabilidad de Volumen (El Gran Cuadre)
**Módulo / Pestaña:** `View Daily Information` -> `Volume Accounting Tab`

### A. Conciliación Volumétrica Diaria
$$Not\ Accounted = Calc\ End\ Volume - Actual\ End\ Volume$$

*   **Regla Lógica Estricta:** El resultado debe ser **exactamente $0.00$**[cite: 2].
*   **Cómo se usa:** El sistema compara el volumen que *debería* tener el tanque (según ingresos, pérdidas y transferencias) contra la medición física (`Actual`) que el ingeniero hizo con la cinta métrica[cite: 2].
*   **Para qué sirve:** Es el mecanismo de auditoría principal. Si hay una discrepancia, el software bloquea lógicamente la cuadratura y obliga al usuario a ingresar una transacción (pérdida, adición o transferencia) que justifique los barriles faltantes o sobrantes[cite: 2].

### B. Concentración Promedio por Transferencia/Mezcla
$$C_{final} = \frac{(V_{destino} \times C_{destino}) + (V_{transferido} \times C_{origen})}{V_{destino} + V_{transferido}}$$

*   **Cómo se usa:** Al usar `Transfer` o `Add Whole Mud`, pondera la concentración química (lb/bbl) cruzando los volúmenes involucrados[cite: 2].
*   **Para qué sirve:** Actualiza las concentraciones químicas de los tanques dinámicamente sin necesidad de descontar sacos de la bodega, manteniendo la fidelidad del reporte químico (`Product Concentrations`)[cite: 2].

---

## 5. Facturación y Utilización de Equipos
**Módulo / Pestaña:** `View Daily Information` -> `Equipment Tab` -> `Equipment Utilization`

### A. Costo Diario por Equipo
$$Daily\ Cost = Used\ Days \times Tarifa\ (Rental\ o\ Standby)$$

*   **Cómo se usa:** Multiplica la cantidad de días (acepta fracciones como $0.5$) por el precio de tarifa plena (`Full Charge`) o tarifa de espera (`Stand-By`)[cite: 2].
*   **Para qué sirve:** Genera el cargo económico diario para la operadora[cite: 2]. Esta sumatoria alimenta el renglón de "Equipos" en la barra inferior de costos totales del reporte[cite: 2].