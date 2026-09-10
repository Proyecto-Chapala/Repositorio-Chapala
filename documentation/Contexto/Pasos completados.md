# Pasos completados

Estado del proyecto **Sistema de reportes de fluidos de perforación** al 2026-09-07. Este documento resume, en orden cronológico, todo lo que ya está construido y verificado sobre el proyecto real (no diseños en papel: todo lo listado aquí corrió contra la base de datos de `Proyecto CHAPALA` y fue confirmado por el usuario).

## 1. Descubrimiento de los dos codebases

Al retomar el proyecto se detectó que convivían dos sistemas distintos dentro de la misma carpeta `Proyecto CHAPALA`:

- **`mychapala`** — la app Django que ya estaba en uso real, con datos de inventario cargados en PostgreSQL (Producto, ReporteDiario, RegistroUso, esquema plano con IDs enteros).
- **`reportes`** — el esquema completo estilo ONE-TRAX (Pozo → Intervalo → SistemaFluido → ReporteDiario, con UUIDs), diseñado en el chat pero sin app Django creada todavía.

Se decidió que ambas convivan en el mismo proyecto Django (`Proyecto CHAPALA`, mismo `manage.py`, mismo PostgreSQL), como dos apps independientes.

## 2. Separación del "Unit Size" en `mychapala` (Producto)

El campo de texto libre "Unit Size" (ej. `"100. LB BG"`) se separó en 3 campos estructurados: `cantidad_unitaria`, `unidad_medida` (LB/KG/GA/LT/BBL/EA) y `tipo_empaque` (BG/CN/DM/TOTE/BLS/EA). Esto habilita calcular el libraje final (`libraje_final = cantidad_unitaria × cantidad`) en vez de tenerlo como texto no operable.

- Migración de datos escrita a mano (`0004_producto_unit_size_fields.py`) que migró los 53 productos ya cargados, verificados uno a uno contra `seed_data.py`.
- Backend (`views.py`) valida los 3 campos nuevos al crear/editar un producto.
- Frontend (modal de Producto en `mychapala`): 3 campos nuevos + recálculo en vivo del texto "Unidad del producto".
- Migración corrida y confirmada por el usuario. Las 3 columnas nuevas se agregaron también como columnas visibles en la tabla de Inventario.

## 3. Misión 4 — Matriz de propiedades selectivas (diseño de datos)

Catálogo de 42 propiedades extraído directamente de las hojas MUD PROPERTIES del Mud Report 16 PERLA-1X (WBM/CALDRIL Check = agua, OBM Check = aceite, Synthetic-Based Mud = sintético). Se definieron 4 modelos nuevos (`PropiedadCatalogo`, `PropiedadSistema`, `MuestraFluido`, `PropiedadValor`) tras resolver 3 decisiones de diseño con el usuario: varias muestras por reporte (no un solo valor), propiedades compuestas (R600/R300, Pf/Mf, etc.) separadas en campos numéricos individuales, y la categoría "polimérico" reutilizando el catálogo de "agua".

## 4. Misión 0 — Creación de la app `reportes`

Se creó la app Django `reportes` dentro del mismo proyecto que `mychapala` (no un proyecto aparte). Debido a que este entorno de trabajo no tiene acceso a PyPI, el usuario corrió `makemigrations`/`migrate` en su máquina real. Verificación definitiva: conteo de filas de los 13 modelos vía `manage.py shell`, todos consultables. Luego se cargó el catálogo de propiedades con `seed_propiedades.py` (42 propiedades, 122 entradas de matriz `PropiedadSistema` — número que cuadra exacto con el diseño).

## 5. Interfaz web para `reportes`

Se construyó un frontend propio (vanilla JS + API JSON, mismo patrón que `mychapala`) en `/reportes/`, con 5 pestañas: Pozos, Sistemas de Fluido, Intervalos (con tubería instalada y cierre volumétrico), Productos, Reportes Diarios (con muestras, matriz de propiedades dinámica según el sistema de fluido, e inventario/uso de material). No requirió migración nueva — solo métodos `to_dict()` de serialización.

## 6. Equipos, Comentarios y Geometría del Pozo (demo)

Se completaron los dos módulos que faltaban del reporte:

- **Equipo / UsoEquipo** — catálogo de equipos + uso por reporte diario, con costo calculado siempre por fórmula (`costo_diario × horas_usadas / 24`), nunca a mano.
- **Comentario** — observaciones de texto libre por reporte diario.

Migración `0002_equipo_comentario.py` escrita a mano (2 modelos simples) y corrida por el usuario sin errores. Ambos módulos conectados a la interfaz: pestaña "Equipos" (catálogo) + secciones "Uso de Equipos" y "Comentarios" dentro del detalle de cada Reporte Diario.

Se agregó también una pestaña de **Geometría del Pozo**, marcada explícitamente como demo: esquema SVG interactivo que se redibuja en vivo según los datos ingresados (profundidad total, profundidad de zapata, diámetros de hoyo/revestidor/tubería), con los cálculos de capacidad interna y volumen anular ya confirmados (fórmulas de la sección 7.2/7.3 del contexto original). No está conectada todavía a los modelos reales de Intervalo/TuberiaInstalada — es una demostración visual aislada.

## Resumen de lo verificado en la base real

| Hito | Verificado por | Resultado |
|---|---|---|
| Migración `0004` (Unit Size CHAPALA) | Usuario, `migrate` | OK, 53 productos migrados |
| Migración `0001_initial` (`reportes`, 13 modelos) | Usuario, `makemigrations` + `migrate` + conteo por shell | OK, 13 modelos consultables |
| `seed_propiedades.py` | Usuario, ejecución directa | 42 propiedades + 122 entradas de matriz |
| Interfaz `/reportes/` | Usuario, prueba en navegador | Carga y funciona |
| Migración `0002` (Equipo/Comentario) | Usuario, `migrate` | OK |
