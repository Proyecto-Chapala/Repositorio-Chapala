/*
================================================================================
GEOMETRÍA INTERACTIVA DEL POZO — DEMO
================================================================================
Módulo independiente y autocontenido (no depende de app.js ni de la API):
dibuja un esquema del pozo en SVG que se recalcula y redibuja en vivo según
los controles, y muestra los cálculos de capacidad/volumen anular con las
fórmulas ya confirmadas (secciones 7.2 y 7.3 del contexto del proyecto).

Es una demostración, no la lógica final: modela un solo tramo de revestidor
+ hoyo abierto por debajo (no múltiples intervalos apilados) y una sola
sarta de perforación. La integración con Intervalo/TuberiaInstalada real
(múltiples revestidores, cierre volumétrico, etc.) queda para más adelante.

Convención de diámetros (aclarada por el usuario):
  - "Diámetro externo (OD)" de hoyo/revestidor = el borde de lo que se
    perforó o se metió de hierro — define el ancho del dibujo.
  - "Diámetro interno (ID)" de la sarta de perforación = el del taladro/
    tubería que va adentro — el que se usa para capacidad y volumen anular.
================================================================================
*/

(function () {
  "use strict";

  const panel = document.getElementById("panel-geometria");
  if (!panel) return; // esta página no tiene la pestaña de geometría

  const ids = [
    "geo-prof-total", "geo-prof-zapata",
    "geo-od-hoyo", "geo-od-revestidor", "geo-id-revestidor",
    "geo-od-tuberia", "geo-id-tuberia",
  ];

  function getValores() {
    const v = {};
    ids.forEach((id) => {
      const rango = document.getElementById(id);
      v[id] = parseFloat(rango.value) || 0;
    });
    return {
      profTotal: v["geo-prof-total"],
      profZapata: Math.min(v["geo-prof-zapata"], v["geo-prof-total"]),
      odHoyo: v["geo-od-hoyo"],
      odRevestidor: v["geo-od-revestidor"],
      idRevestidor: v["geo-id-revestidor"],
      odTuberia: v["geo-od-tuberia"],
      idTuberia: v["geo-id-tuberia"],
    };
  }

  // Sincroniza cada par slider <-> input numérico (cualquiera de los dos
  // que cambie actualiza al otro y dispara el redibujo).
  function sincronizarPares() {
    ids.forEach((id) => {
      const rango = document.getElementById(id);
      const numero = document.getElementById(id + "-num");
      if (!rango || !numero) return;

      rango.addEventListener("input", () => {
        numero.value = rango.value;
        redibujar();
      });
      numero.addEventListener("input", () => {
        const val = parseFloat(numero.value);
        if (!isNaN(val)) {
          const min = parseFloat(rango.min);
          const max = parseFloat(rango.max);
          rango.value = Math.min(Math.max(val, min), max);
        }
        redibujar();
      });
    });
  }

  function fmt(n) {
    return n.toLocaleString("es-VE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function calcular(v) {
    const largoRevestido = v.profZapata;
    const largoHoyoAbierto = v.profTotal - v.profZapata;

    const capacidadTuberia = (Math.pow(v.idTuberia, 2) / 1029.4) * v.profTotal;
    const anularRevestido = Math.max(0, (Math.pow(v.idRevestidor, 2) - Math.pow(v.odTuberia, 2)) / 1029.4) * largoRevestido;
    const anularHoyoAbierto = Math.max(0, (Math.pow(v.odHoyo, 2) - Math.pow(v.odTuberia, 2)) / 1029.4) * largoHoyoAbierto;
    const volumenTotal = capacidadTuberia + anularRevestido + anularHoyoAbierto;

    return { capacidadTuberia, anularRevestido, anularHoyoAbierto, volumenTotal, largoRevestido, largoHoyoAbierto };
  }

  function renderResultados(v, r) {
    const tbody = document.querySelector("#geo-tabla-resultados tbody");
    if (!tbody) return;
    tbody.innerHTML = `
      <tr><td>Tramo revestido</td><td>${fmt(r.largoRevestido)} ft</td></tr>
      <tr><td>Tramo hoyo abierto</td><td>${fmt(r.largoHoyoAbierto)} ft</td></tr>
      <tr><td>Capacidad interna de tubería</td><td>${fmt(r.capacidadTuberia)} bbl</td></tr>
      <tr><td>Volumen anular (sección revestida)</td><td>${fmt(r.anularRevestido)} bbl</td></tr>
      <tr><td>Volumen anular (hoyo abierto)</td><td>${fmt(r.anularHoyoAbierto)} bbl</td></tr>
      <tr><td><strong>Volumen total</strong></td><td><strong>${fmt(r.volumenTotal)} bbl</strong></td></tr>
    `;
  }

  function renderSVG(v) {
    const wrap = document.getElementById("geo-svg-wrap");
    if (!wrap) return;

    const width = 380;
    const height = 520;
    const margenSuperior = 20;
    const margenInferior = 20;
    const altoDibujo = height - margenSuperior - margenInferior;
    const centroX = width / 2;

    const maxDiametro = Math.max(v.odHoyo, v.odRevestidor, v.odTuberia, 1);
    const anchoMaxPx = width * 0.42; // mitad del ancho disponible desde el centro
    const escalaDiametro = anchoMaxPx / (maxDiametro / 2);

    const profTotalSegura = Math.max(v.profTotal, 1);
    const escalaProfundidad = altoDibujo / profTotalSegura;

    const yZapata = margenSuperior + v.profZapata * escalaProfundidad;
    const yFondo = margenSuperior + profTotalSegura * escalaProfundidad;

    function rectCentrado(diametro, yTop, yBottom, fill, stroke) {
      const anchoPx = diametro * escalaDiametro;
      const x = centroX - anchoPx / 2;
      const alto = Math.max(yBottom - yTop, 0);
      return `<rect x="${x.toFixed(1)}" y="${yTop.toFixed(1)}" width="${anchoPx.toFixed(1)}" height="${alto.toFixed(1)}" fill="${fill}" stroke="${stroke}" stroke-width="1" />`;
    }

    let svg = "";

    // Hoyo abierto (OD) — de la zapata al fondo
    svg += rectCentrado(v.odHoyo, yZapata, yFondo, "#e7d4b5", "#b8985f");

    // Revestidor: pared exterior (OD) llena, e interior (ID) hueca — de superficie a zapata
    svg += rectCentrado(v.odRevestidor, margenSuperior, yZapata, "#9ca3af", "#4b5563");
    svg += rectCentrado(v.idRevestidor, margenSuperior, yZapata, "#f3f4f6", "#9ca3af");

    // Sarta de perforación (tubería): OD sólido con ID hueco, de superficie a fondo
    svg += rectCentrado(v.odTuberia, margenSuperior, yFondo, "#374151", "#111827");
    svg += rectCentrado(v.idTuberia, margenSuperior, yFondo, "#ffffff", "#6b7280");

    // Línea de zapata
    svg += `<line x1="10" y1="${yZapata.toFixed(1)}" x2="${width - 10}" y2="${yZapata.toFixed(1)}" stroke="#dc2626" stroke-width="1" stroke-dasharray="4 3" />`;
    svg += `<text x="${width - 10}" y="${(yZapata - 4).toFixed(1)}" font-size="10" text-anchor="end" fill="#dc2626">Zapata @ ${fmt(v.profZapata)} ft</text>`;

    // Etiqueta de fondo
    svg += `<text x="${width - 10}" y="${(yFondo - 4).toFixed(1)}" font-size="10" text-anchor="end" fill="#374151">Fondo @ ${fmt(v.profTotal)} ft</text>`;

    // Eje de referencia central
    svg += `<line x1="${centroX}" y1="${margenSuperior}" x2="${centroX}" y2="${yFondo}" stroke="#d1d5db" stroke-width="1" stroke-dasharray="2 2" />`;

    wrap.innerHTML = `<svg viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">${svg}</svg>`;
  }

  function redibujar() {
    const v = getValores();
    const r = calcular(v);
    renderSVG(v);
    renderResultados(v, r);
  }

  document.addEventListener("DOMContentLoaded", () => {
    sincronizarPares();
    redibujar();
  });
})();
