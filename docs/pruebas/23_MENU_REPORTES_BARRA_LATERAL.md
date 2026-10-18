# 23 — Panel "Reportes" en la barra lateral (18-oct-2026) — reemplazado

> En la rama `refactorizacion_ui` este panel se reemplazó por el buscador Ctrl+K. Probar con [pruebas/24](24_REDISENO_UI_TECNICO.md).

## Cómo funciona

En la barra lateral, debajo de **Pozos**, hay un botón **📄 Reportes**. Al pulsarlo se abre un panel junto a la barra con un buscador y una línea por pozo, "Reportes pozo X", con la fecha del último reporte y la cantidad de reportes. Pulsar una línea abre directamente el historial de reportes de ese pozo (Fluidos de Perforación y Equipos).

Los pozos con el reporte más reciente van arriba y los que no tienen reportes, al final. Los pozos enviados a la papelera no aparecen. Así, aunque haya 100 pozos o más, la barra lateral no se llena: se busca por nombre.

## Pasos para verificar

- [ ] Recargar con **Ctrl + F5** la primera vez (para que el navegador tome los archivos nuevos).
- [ ] Pulsar **📄 Reportes**: se abre el panel y el cursor queda en el buscador.
- [ ] Escribir parte del nombre de un pozo: la lista se filtra al escribir.
- [ ] Escribir algo que no existe: aparece "Ningún pozo coincide con la búsqueda."
- [ ] Pulsar Enter con un filtro: abre el primer pozo de la lista.
- [ ] Pulsar un pozo: abre su historial de reportes, el botón Reportes queda resaltado y, al reabrir el panel, ese pozo aparece marcado.
- [ ] El pozo con el reporte más reciente aparece primero; los que no tienen reportes dicen "Sin reportes todavía" y van al final.
- [ ] Cerrar el panel con ×, con Escape y haciendo clic fuera.
- [ ] Enviar un pozo a la papelera: deja de aparecer. Al restaurarlo vuelve.
- [ ] Con la barra lateral colapsada, el panel se abre pegado a ella.
