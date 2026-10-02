# Proyecto CHAPALA — Sistema de Operaciones de Fluidos de Perforación (AOS)

Sistema web desarrollado en **Django** para **All Oil Services, C.A. (AOS)**. Replica, en español y con la lógica del manual oficial, el módulo **"Drilling Fluids and Equipment"** del programa **ONE-TRAX** de M-I SWACO. Además incluye un inventario de productos químicos de almacén.

Con el sistema se puede:

- Crear y configurar **pozos** con un asistente de 4 pasos: unidades, moneda, categorías de pérdida y plantilla.
- Mantener los **catálogos maestros** de equipos, mallas de zaranda, componentes de sarta, propiedades de equipo y parámetros de benchmark.
- Llenar el **reporte diario** de 8 pestañas: general, bombas y barrena, propiedades del lodo, geometría del pozo, comentarios, control de sólidos, distribución de tiempo y volumetría/inventario/hidráulica.
- Calcular **volúmenes del hoyo, hidráulica API RP 13D (4ª y 5ª edición), balance de sólidos, volumetría, concentraciones de productos, inventario de productos y mallas, costos diarios y acumulados**.
- Registrar los casos especiales del manual: **side track** y **hoyo piloto**.
- Descargar el **reporte diario en Excel** con el formato del libro de ONE-TRAX.

> Estado al 27-sep-2026: pestañas 1 a 8, módulos opcionales, concentraciones (pantalla + hoja de Excel) y casos especiales (side track, hoyo piloto) construidos. Migraciones hasta la **0022**. Falta la prueba final de las personas encargadas. Ver [docs/16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md](docs/16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md).

---

## Inicio rápido

```bat
cd "C:\Users\Admin\Documents\Proyectos\Proyecto CHAPALA"
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Luego abre <http://127.0.0.1:8000/pozos/>. El detalle está en [docs/01_INSTALACION_Y_EJECUCION.md](docs/01_INSTALACION_Y_EJECUCION.md).

---

## Índice de la documentación

### Para usuarios (personal de AOS)

| Documento | Contenido |
|---|---|
| [MANUAL_USUARIO.md](docs/MANUAL_USUARIO.md) | Guía paso a paso: crear un pozo, configurarlo, llenar el reporte diario y casos especiales (side track, hoyo piloto) |
| [17_GLOSARIO.md](docs/17_GLOSARIO.md) | Términos ONE-TRAX (inglés) ↔ CHAPALA (español) y siglas del oficio |
| [18_PREGUNTAS_FRECUENTES.md](docs/18_PREGUNTAS_FRECUENTES.md) | "¿Por qué el producto aparece en 0 en la pestaña 8?" y otras dudas comunes |

### Para desarrolladores

| # | Documento | Contenido |
|---|---|---|
| 01 | [Instalación y ejecución](docs/01_INSTALACION_Y_EJECUCION.md) | Requisitos, `.env`, PostgreSQL/SQLite, migraciones, arranque |
| 02 | [Arquitectura](docs/02_ARQUITECTURA.md) | Estructura de carpetas, capas, motores de cálculo, patrones del código |
| 03 | [Modelo de datos](docs/03_MODELO_DATOS.md) | Los modelos, campo por campo, con migración y relaciones |
| 04 | [API y rutas](docs/04_API_ENDPOINTS.md) | Todas las URLs, métodos HTTP y vistas |
| 05 | [Configuración del pozo](docs/05_CONFIGURACION_POZO.md) | Wizard, Spud Date, pantalla principal, setups y catálogos maestros |
| 06 | [Reporte diario — Hub y pestañas 1 a 5](docs/06_REPORTE_DIARIO_PESTANAS_1_A_5.md) | Creación del reporte, General, Bombas/Barrena, Lodo, Geometría, Comentarios |
| 07 | [Pestaña 6 — Control de sólidos](docs/07_PESTANA_6_CONTROL_SOLIDOS.md) | Mallas, tickets, transacciones, uso de equipos, rendimiento |
| 08 | [Pestaña 7 — Distribución de tiempo](docs/08_PESTANA_7_DISTRIBUCION_TIEMPO.md) | Horas por actividad IADC |
| 09 | [Pestaña 8 — Volumetría e inventario](docs/09_PESTANA_8_VOLUMETRIA_INVENTARIO.md) | Fosas, movimientos, inventario de productos, concentraciones, pérdidas |
| 10 | [Hidráulica API RP 13D](docs/10_HIDRAULICA_API13D.md) | Fórmulas de 4ª y 5ª edición, mecha, superficie, verificación |
| 11 | [Cálculos de ingeniería](docs/11_CALCULOS_INGENIERIA.md) | Geometría y volúmenes, survey, bombas, reología, balance de sólidos |
| 12 | [Módulos opcionales](docs/12_MODULOS_OPCIONALES.md) | IFE, análisis de sólidos, retención en recortes, eventos no programados, benchmark |
| 13 | [Costos](docs/13_COSTOS.md) | De dónde sale cada costo diario y acumulado |
| 14 | [Reporte Excel](docs/14_REPORTE_EXCEL.md) | Plantilla, hojas y cómo se llena |
| 15 | [Inventario de almacén](docs/15_INVENTARIO_ALMACEN.md) | Módulo de productos químicos (pantalla "Inventario") |
| 16 | [Problemas conocidos y pendientes](docs/16_PROBLEMAS_CONOCIDOS_Y_PENDIENTES.md) | Bugs reportados con su causa, riesgos, deuda técnica y decisiones pendientes |
| 19 | [Guía de mantenimiento](docs/19_GUIA_MANTENIMIENTO.md) | Convenciones, cómo agregar una pestaña o campo, pruebas, despliegue |
| 20 | [Concentraciones y casos especiales](docs/20_CONCENTRACIONES_Y_CASOS_ESPECIALES.md) | Los 3 casos de concentración, side track, hoyo piloto, CaCO₃ — con verificación contra el manual |

---

## Tecnología

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12+ · Django 6.1.1 |
| Base de datos | PostgreSQL (`psycopg2-binary`) o SQLite (según `.env`) |
| Frontend | HTML de plantillas Django + JavaScript "vanilla" + CSS, sin frameworks |
| Excel | `openpyxl` sobre la plantilla `operaciones/plantillas/reporte_diario_onetrax.xlsx` |
| Idioma / zona | `es-ve`, `America/Caracas` |

## Créditos

Desarrollado para All Oil Services, C.A. (RIF J-31267150-5). Referencia funcional: manual de ONE-TRAX, módulo *Drilling Fluids and Equipment* (M-I SWACO).
