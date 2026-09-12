# Antigravity Operating Rules - ONE-TRAX Reconstruction

## Reglas Obligatorias:
1. TRABAJO ATÓMICO: Ejecuta única y exclusivamente la tarea asignada en el prompt actual. No modifiques archivos fuera del alcance inmediato.
2. PRESERVACIÓN: No sobrescribas ni borres funciones, modelos o configuraciones preexistentes sin indicación explícita.
3. ENTORNOS Y DB: Estamos trabajando sobre Django con SQLite local (`db.sqlite3`). No utilices extensiones exclusivas de PostgreSQL que provoquen fallos en las migraciones locales.
4. VALIDACIÓN CONTINUA: Tras modificar o crear modelos, verifica que `python manage.py makemigrations` y `python manage.py check` pasen sin errores.