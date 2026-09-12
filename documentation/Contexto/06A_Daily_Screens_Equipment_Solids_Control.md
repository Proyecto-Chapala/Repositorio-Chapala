# Módulo 6A: Mallas de Zaranda, Control de Sólidos y Balance de Descartes (Screens, Equipment & Solids Control)
**Documento de Especificación Arquitectónica (SDD)**
**Módulo:** ONE-TRAX / View Daily Information (Screens Tab & Equipment Tab)
**Referencia:** Manual ONE-TRAX 2.0 (Secciones 4.9 y 4.10, Páginas 104-125) y Mud Report 16 PERLA-1X

---

## 1. Propósito y Alcance del Módulo

El control eficiente de sólidos es el factor determinante en la calidad del fluido de perforación, la prevención de pegas de tubería y la reducción del costo global del pozo.

En ONE-TRAX, la operación diaria de control de sólidos se divide en dos pestañas integradas:
1. **Pestaña de Mallas (`Screens Tab`):** Administra el inventario de mallas en locación, el seguimiento de horas de trabajo por zaranda/limpiador de lodo, y la rotación por rotura o desgaste.
2. **Pestaña de Equipos (`Equipment Tab`):** Registra la tarificación diaria (Full Charge / Stand-by) y ejecuta el **Balance de Masa de Sólidos Descartados**, calculando con precisión matemática el volumen de lodo activo perdido con los ripios ($MOC$) y conectándolo directamente con la pestaña de Contabilidad de Volumen (`Volume Accounting`).

---

## 2. Pestaña de Mallas (Screens Tab - Sección 4.9)

### 2.1 Componentes de la Pantalla
1. **Lista de Equipos (Equipment List):** Árbol expandible a la izquierda que lista exclusivamente los equipos que usan mallas vibratorias:
   - Zarandas / Temblorinas (`Shakers`, ej. Shaker 1, Shaker 2, Shaker 3).
   - Limpiadores de Lodo (`Mud Cleaners`).
2. **Tabla de Mallas Instaladas (Installed Screens Table):** Muestra las mallas montadas actualmente en la máquina seleccionada:
   - Posición / Deck (Tope / Fondo, o consecutiva).
   - Fabricante y Modelo (ej. `M-I SWACO MD-3`, `Derrick Hyperpool`, `Brandt King Cobra`).
   - Malla API RP 13C (`API Mesh Size`, ej. API 100, API 140, API 170, API 200, API 230).
   - Serial de la Malla (identificador trazable único).
   - Horas del Día (`Hours Run` en las últimas 24 hrs).
   - Horas Acumuladas (`Total Hours` acumuladas en el pozo).
3. **Resumen de Inventario (Screen Inventory Summary):** Conteo dinámico de mallas nuevas, usadas y rotas en la bodega de locación.
4. **Tickets de Transferencia de Mallas (Screen Transfer Tickets):** Entradas y devoluciones de mallas hacia base / proveedor.

### 2.2 Ciclo de Vida Operativo de una Malla
- **Instalación (`Install Screen`):** Se selecciona el equipo, el modelo de malla del inventario y la cantidad. La malla pasa a estado `Instalada`.
- **Acumulación de Horas:** En cada nuevo día operativo (`New Day`), las horas del día previo se suman automáticamente a `total_hours`.
- **Desinstalación / Retiro (`Remove Screen`):**
  - Si se retira por rotura o colapso: Se marca como `Desechada (Discarded/Torn)`, se registra el motivo de falla y se descuenta del inventario de mallas útiles.
  - Si se retira por cambio de fase (ej. se requiere malla más fina): Se marca como `Usada Reutilizable (Used Screen)` y regresa al inventario de locación.

---

## 3. Pestaña de Equipos (Equipment Tab - Sección 4.10)

La pestaña de equipos abarca tanto el hardware de control de sólidos como equipos auxiliares:
- Zarandas primarias y secundarias (`Shakers`).
- Limpiadores de Lodo (`Mud Cleaners`).
- Desarenadores (`Desanders`) y Deslimadores (`Desilters`).
- Centrífugas de decantación de alta y baja velocidad (`Centrifuges`).
- Desgasificadores de vacío (`Degassers`).
- Agitadores de fosas (`Agitators`) y Mezcladores de tolva (`Shear Hoppers`).

### 3.1 Utilización y Facturación Diaria (Equipment Utilization)

Cada equipo configurado en el pozo genera un cargo económico en el reporte diario:

#### A. Parámetros de Utilización
- **`status`:** Estado operativo en las últimas 24 hrs:
  - `In Use (En Operación)`: Equipo trabajando en el circuito de fluidos.
  - `Standby (En Espera)`: Equipo disponible en locación pero apagado por condiciones operacionales.
  - `Off Hire / Breakdown (Fuera de Servicio / Dañado)`: No genera cobro a la operadora.
  - `Rig Down (Desmovilizado)`.
- **`used_days`:** Fracción de día operativo (de 0.0 a 1.0 días, típicamente `1.0` o `0.5` días).

#### B. Fórmula de Tarificación Diaria:
$$\text{Daily Equipment Cost} = \text{Used Days} \times \text{Tarifa Vigente}$$

*Donde la tarifa vigente se determina por el estado:*
- Si `status = 'In Use'` $\implies$ Aplica `tarifa_plena` (`Full Charge Rate`, USD/día).
- Si `status = 'Standby'` $\implies$ Aplica `tarifa_espera` (`Standby Rate`, USD/día, típicamente 50% a 70% de la tarifa plena).
- Si `status = 'Off Hire'` $\implies \text{Costo} = 0.00\text{ USD}$.

*El total de esta tabla alimenta la celda de costos de equipos del reporte diario consolidado.*

---

## 4. Balance de Masa y Descartes de Sólidos (Solids Control Mass Balance)

Es el motor de cálculo más avanzado de la pestaña de equipos. Determina exactamente cuánto volumen de lodo activo sale del sistema adherido a los ripios perforados y descartados por cada máquina.

### 4.1 Volumen Teórico de Roca Perforada (Drilled Rock Volume)
A partir del progreso diario de perforación registrado en la pestaña `General` y el diámetro de hoyo de la pestaña `Geometry`:

$$V_{\text{roca\_perforada}} = \frac{\pi}{4} \times D_h^2 \times \text{Progreso Diaro (ft)} \times \frac{1}{970.2} \quad (\text{bbl})$$

*(Constante $970.2 \approx 42 \times 23.1$ para convertir $\text{in}^2 \cdot \text{ft}$ a barriles de 42 galones)*.

*Ejemplo (Hoyo 26 plg con progreso de 100 ft en 24 hrs):*
$$V_{\text{roca}} = 0.7854 \times (26)^2 \times 100 \times \frac{1}{970.2} = 530.93 \times 100 \times 0.0010307 = 54.72\text{ bbl de roca pura}$$

### 4.2 Porcentaje de Remoción por Máquina (% Cuttings Removed)
1. El ingeniero estima la eficiencia global de remoción del tren de sólidos ($E_{\text{sistema}}$, típicamente 75% a 90%).
2. La carga se distribuye entre los equipos que estuvieron activos durante la jornada:
   $$E_i = \frac{E_{\text{sistema}}}{\text{Cantidad de Equipos Activos del Tipo}} \quad (\%)$$

   *Ejemplo ONE-TRAX:*
   - Si 3 zarandas remueven el 90% de los ripios en conjunto $\implies E_i = \frac{90\%}{3} = 30\%$ para cada zaranda.
   - Si 4 zarandas remueven el 75% $\implies E_i = \frac{75\%}{4} = 18.75\%$ por zaranda.

3. Volumen de roca separado por el equipo $i$:
   $$V_{\text{solidos}, i} = V_{\text{roca\_perforada}} \times \left(\frac{E_i}{100}\right) \quad (\text{bbl})$$

### 4.3 Factor Mud On Cuttings ($MOC$)
Es la relación volumétrica entre el lodo líquido adherido y el volumen de roca seca descartada:
$$MOC = \frac{V_{\text{lodo}}}{V_{\text{ripios}}}$$

- Se mide en campo mediante pesaje de descarga o prueba de retorta sobre ripios frescos del descarte.
- **Valores típicos en campo:**
  - Zarandas con mallas gruesas (API 80): $MOC \approx 1.0$ (1 bbl de lodo por 1 bbl de roca).
  - Zarandas con mallas finas (API 200): $MOC \approx 0.6 - 0.8$.
  - Secador de recortes (Cuttings Dryer): $MOC \approx 0.15 - 0.25$.
  - Centrífuga descartando sólidos: $MOC \approx 0.5 - 0.7$.

#### Porcentaje de Lodo en la Descarga:
$$\% \text{Lodo en Descarga} = \left(\frac{MOC}{1 + MOC}\right) \times 100$$
*(Ejemplo: si $MOC = 0.8 \implies \frac{0.8}{1.8} = 44.4\%\text{ lodo y } 55.6\%\text{ roca})*$.

### 4.4 Volumen de Lodo Perdido en Sólidos (Volume of Mud on Solids Discarded)
Para cada equipo $i$:
$$V_{\text{lodo\_perdido}, i} = V_{\text{solidos}, i} \times MOC_i \quad (\text{bbl})$$

### 4.5 Volumen Total Descartado / Lodo Residual (Sludge Volume)
Es el volumen pastoso total de desecho que sale por el canal de descarga hacia los contenedores de ripios (`Cuttings Boxes`):
$$V_{\text{sludge}, i} = V_{\text{solidos}, i} + V_{\text{lodo\_perdido}, i} \quad (\text{bbl})$$

### 4.6 Balance Específico de Centrífugas de Decantación (Centrifuge Performance)
Para cada centrífuga activa:
1. **Volumen de Entrada ($V_{\text{in}}$):** Gasto de alimentación $\times$ Horas de corrida ($Q_{\text{in}} \times \text{Hours Run}$).
2. **Densidad de Entrada ($\rho_{\text{in}}$), Efluente Líquido ($\rho_{\text{out}}$) y Torta de Descarte ($\rho_{\text{discard}}$).**
3. **Volumen de Lodo Recuperado y Retornado al Sistema Activo:**
   $$V_{\text{recuperado}} = V_{\text{in}} \times \left(\frac{\rho_{\text{discard}} - \rho_{\text{in}}}{\rho_{\text{discard}} - \rho_{\text{out}}}\right) \quad (\text{bbl})$$
4. **Volumen de Descarte de la Centrífuga:**
   $$V_{\text{descarte}} = V_{\text{in}} - V_{\text{recuperado}} \quad (\text{bbl})$$

---

## 5. El Botón Crítico: `Create Equipment Loss Transaction`

### 5.1 Propósito
En ONE-TRAX, la pérdida de lodo sobre ripios calculada en la pestaña `Equipment` no se queda como un dato aislado; debe descontarse físicamente de las fosas activas para cuadrar el balance de volumen.

### 5.2 Comportamiento al Pulsar el Botón
Al hacer clic en **`Create Equipment Loss Transaction`**:
1. El sistema calcula la sumatoria total de lodo perdido en sólidos de todas las máquinas activas:
   $$V_{\text{perdida\_equipos\_total}} = \sum_{i} V_{\text{lodo\_perdido}, i} \quad (\text{bbl})$$
2. Abre automáticamente una ventana de confirmación con:
   - **Fosa Origen:** Selector de la fosa activa de la que sale el lodo (por defecto la primera fosa transaccional activa, ej. `Active 1`).
   - **Categoría de Pérdida:** Fija automáticamente en el catálogo la categoría correspondiente (ej. `Shakers / Solids Control Loss`).
   - **Volumen a Descontar:** Precargado exactamente con $V_{\text{perdida\_equipos\_total}}$ (bbl).
   - **Notas:** Texto generado automáticamente: *"Pérdida sobre ripios generada por control de sólidos (Zarandas: X bbl, Centrífugas: Y bbl)"*.
3. Al confirmar, se inserta un registro inmutable en `TransaccionFosa` (`tipo = 'loss'`), reflejándose instantáneamente en la columna `Losses` de la pestaña `Volume Accounting`.

---

## 6. Mapeo a Modelos Django / PostgreSQL

### 6.1 Modelos Existentes y Complementarios
1. **`UsoMalla` (`reportes_usomalla`):**
   - `reporte`: ForeignKey a `ReporteDiario`.
   - `modelo_malla`: ForeignKey a `ModeloMalla`.
   - `equipo`: ForeignKey a `Equipo`.
   - `posicion`: Integer.
   - `horas_dia`: DecimalField(5, 2).
   - `horas_acumuladas`: DecimalField(7, 2).
   - `estado`: CharField (Choices: `instalada`, `descartada_rota`, `removida_usada`).
   - `motivo_descarte`: CharField(150, blank=True).

2. **`UsoEquipo` (`reportes_usoequipo`):**
   - `reporte`: ForeignKey a `ReporteDiario`.
   - `equipo`: ForeignKey a `Equipo`.
   - `estado`: CharField (Choices: `in_use`, `standby`, `off_hire`, `rig_down`).
   - `horas_usadas`: DecimalField(5, 2).
   - `horas_standby`: DecimalField(5, 2).
   - `porcentaje_remocion`: DecimalField(5, 2) (% de ripios procesados).
   - `mud_on_cuttings`: DecimalField(4, 2) (ratio MOC).
   - `volumen_lodo_perdido`: DecimalField(10, 2) (bbl calculados).
   - `volumen_solidos_descarte`: DecimalField(10, 2) (bbl calculados).
   - `costo_diario_calculado`: DecimalField(10, 2) (USD calculados según tarifa).

