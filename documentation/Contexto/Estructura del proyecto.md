# Estructura del proyecto

## Stack técnico

- **Backend:** Python + Django + PostgreSQL.
- **Frontend:** vanilla JavaScript (sin frameworks) + HTML/CSS servidos por Django templates. Cada app tiene su propia SPA ligera que consume una API JSON propia.
- **JavaScript adicional:** usado puntualmente para la geometría del pozo (gráfico que se redibuja en vivo), tal como se acordó desde el inicio del proyecto.

## Un proyecto Django, dos apps

Todo vive dentro de un mismo proyecto Django (carpeta raíz `Proyecto CHAPALA`, un solo `manage.py`, una sola base PostgreSQL vía `.env`). Dentro conviven dos apps independientes:

```
Proyecto CHAPALA/
├── chapala/                  # Configuración del proyecto Django (settings, urls raíz)
│   ├── settings.py
│   └── urls.py                # incluye mychapala.urls en '/' y reportes.urls en '/reportes/'
├── mychapala/                 # App 1: Inventario CHAPALA (la que ya estaba en producción)
│   ├── models.py              # Producto, ReporteDiario, RegistroUso
│   ├── views.py                # API JSON + vista índice
│   ├── urls.py
│   ├── templates/mychapala/
│   └── static/mychapala/
├── reportes/                  # App 2: Sistema de reportes ONE-TRAX
│   ├── models.py              # Pozo, Intervalo, SistemaFluido, ReporteDiario, etc. (ver "Estructura de las tablas.md")
│   ├── views.py                # API JSON + vista índice
│   ├── urls.py
│   ├── admin.py                 # Registro de todos los modelos en /admin/
│   ├── migrations/
│   ├── templates/reportes/
│   └── static/reportes/
│       ├── css/style.css
│       ├── js/app.js            # Lógica de las 5 pestañas principales (CRUD)
│       └── js/geometria.js      # Módulo aislado: demo de geometría interactiva
├── manage.py
├── seed_data.py                # Carga inicial de productos de mychapala
├── seed_propiedades.py         # Carga inicial del catálogo de propiedades de reportes
├── .env / .env.example          # Credenciales de base de datos
└── documentation/                # Archivos de referencia (Excel, PPTX) y esta documentación
```

## Por qué dos apps y no un proyecto separado

`mychapala` ya estaba corriendo con datos reales y PostgreSQL configurado. En vez de duplicar credenciales e infraestructura, `reportes` se agregó como una segunda app Django dentro del mismo proyecto — comparten base de datos (pero no tablas: cada modelo de `reportes` es independiente de los de `mychapala`, aunque ambos tengan, por ejemplo, un modelo `Producto` con nombre igual pero contenido distinto).

## Cómo se enrutan las dos interfaces

- `http://127.0.0.1:8000/` → Inventario CHAPALA (`mychapala`), la interfaz original.
- `http://127.0.0.1:8000/reportes/` → Sistema de reportes ONE-TRAX (`reportes`), la interfaz nueva.
- `http://127.0.0.1:8000/admin/` → Admin de Django, con secciones para ambas apps (útil como respaldo/gestión de bajo nivel, pero el uso normal es a través de las dos interfaces de arriba).

## Patrón de cada app (backend)

Ambas apps siguen el mismo patrón de vistas de función en `views.py`:

- `@csrf_exempt` + `@require_http_methods([...])` en cada endpoint.
- Respuestas `JsonResponse({"success": bool, ...})`, con `"error"` cuando `success` es `false`.
- Cada modelo tiene un método `to_dict()` que arma su representación JSON — así el frontend nunca depende de los nombres internos de los campos del modelo directamente.
- Validación de reglas de negocio dentro de `clean()`/`save()` de los modelos (no solo en las vistas), para que también se respeten desde el admin de Django.

## Patrón de cada app (frontend)

SPA de una sola página por app, organizada en pestañas (`<section class="panel">`), cada una con su propio módulo de JavaScript (objeto con `init()`, `cargar()`, etc.) que solo llama a su porción de la API. No hay build step ni dependencias externas — son archivos estáticos servidos directo por Django (`{% static %}`).

## Cosas que están deliberadamente fuera del alcance actual

- La geometría del pozo real (conectada a `Intervalo`/`TuberiaInstalada`, con múltiples revestidores apilados) — hoy es una demo visual aislada.
- Autenticación/permisos en las APIs — todos los endpoints son `@csrf_exempt` y sin control de acceso, aceptable mientras el sistema no esté en producción real.
- Cálculo automático de volumen a partir de libraje y gravedad específica (Misión 5) — hoy esos campos se ingresan a mano en el Cierre Volumétrico.
