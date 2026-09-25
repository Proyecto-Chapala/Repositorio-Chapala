# Pestañas del reporte diario

El reporte diario (`/pozos/<id>/daily-report/<id_reporte>/`) replica la pantalla *Daily Data Input* de ONE-TRAX en 8 pestañas.

| # | Pestaña | Documento | Guarda | Calcula |
|---|---|---|---|---|
| 1 | General | [PESTANA_1_GENERAL.md](PESTANA_1_GENERAL.md) | Profundidades, actividad, representantes | Número de reporte, costos del día |
| 2 | Bombas y mecha | [PESTANA_2_BOMBAS_MECHA.md](PESTANA_2_BOMBAS_MECHA.md) | 4 bombas, mecha, boquillas, parámetros | Caudal, TFA, diámetro con lavado |
| 3 | Propiedades del lodo | [PESTANA_3_PROPIEDADES_LODO.md](PESTANA_3_PROPIEDADES_LODO.md) | Hasta 4 chequeos, configuración, propiedades extra | PV, YP, análisis de sólidos WBM/OBM |
| 4 | Geometría del pozo | [PESTANA_4_GEOMETRIA.md](PESTANA_4_GEOMETRIA.md) | Sarta, intervalo de costo, hoyo piloto | Perfil del pozo, volúmenes, fondo arriba |
| 5 | Comentarios | [PESTANA_5_COMENTARIOS.md](PESTANA_5_COMENTARIOS.md) | Especificación de lodo y 3 textos | — |
| 6 | Control de sólidos | [PESTANA_6_CONTROL_SOLIDOS.md](PESTANA_6_CONTROL_SOLIDOS.md) | Tickets y movimientos de mallas, uso de equipos | Inventario de mallas, rendimiento, costos |
| 7 | Distribución de tiempo | [PESTANA_7_DISTRIBUCION_TIEMPO.md](PESTANA_7_DISTRIBUCION_TIEMPO.md) | Horas por actividad | Total contra período |
| 8 | Inventario / Hidráulica / Conc. | [PESTANA_8_INVENTARIO.md](PESTANA_8_INVENTARIO.md) | Volúmenes reales, movimientos, tickets de productos | Volumetría, inventario, costos, concentraciones, hidráulica, benchmark |

Dependencias entre pestañas:

```
1 (profundidad, mecha) ─┐
2 (bombas, lavado) ─────┼─► 4 (volúmenes) ─┬─► 6 (volumen perforado → equipos)
intervalos + riser ─────┘                  └─► 8 (fluido en el hoyo → volumetría)
3 (reología, peso) ──────────────────────────► 8 (hidráulica, benchmark)
6 (mallas, renta) + 8 (químicos, servicios) ─► 1 (costos) y Excel
```
