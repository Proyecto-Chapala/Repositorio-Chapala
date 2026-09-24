/* =====================================================================
   PESTAÑA 8 — HIDRÁULICA (API RP 13D, 4ª y 5ª edición)

   Solo consulta. Los cálculos se hacen en el servidor (hidraulica.py); esta
   pantalla dibuja los resultados, la distribución de la presión de bomba y
   el reograma. Se recarga cada vez que se abre la sección, para reflejar lo
   último guardado en las pestañas 2, 3 y 4.

   Depende de: POZO_ID, REPORTE_ID, showToast (reporte_diario_detalle.html)
   y csEsc, csFmt (reporte_control_solidos.js).
   ===================================================================== */

const HD_API = `/api/pozos/${POZO_ID}/daily-report/${REPORTE_ID}/hidraulica/`;
let hdEdicion = '5';
let hdDatos = null;

async function cargarHidraulica(){
  document.getElementById('hdResultado').innerHTML = '<div class="report-card-modern"><div class="cs-vacio cs-vacio-centrado">Calculando…</div></div>';
  try {
    const res = await fetch(`${HD_API}?edicion=${hdEdicion}`);
    hdDatos = await res.json();
    if(!hdDatos.ok) throw new Error();
    hdRender();
  } catch(e){
    document.getElementById('hdResultado').innerHTML = '<div class="report-card-modern"><div class="cs-vacio">No se pudo calcular la hidráulica.</div></div>';
    showToast('No se pudo calcular la hidráulica.', false);
  }
}

function hdRender(){
  const d = hdDatos;
  const e = d.entrada;
  document.getElementById('hdEntrada').innerHTML = `
    <div class="hd-entrada">
      <div class="cs-eq-dato"><span>Caudal</span><strong>${e.caudal_gpm ? csFmt(e.caudal_gpm, 1) + ' gpm' : '—'}</strong><small>pestaña 2</small></div>
      <div class="cs-eq-dato"><span>Peso del lodo</span><strong>${e.peso_lodo ? csFmt(e.peso_lodo, 2) + ' lb/gal' : '—'}</strong><small>${e.chequeo ? 'chequeo #' + e.chequeo : 'pestaña 3'}</small></div>
      <div class="cs-eq-dato"><span>TFA</span><strong>${e.tfa_in2 ? csFmt(e.tfa_in2, 4) + ' in²' : '—'}</strong><small>boquillas</small></div>
      <div class="cs-eq-dato"><span>Mecha</span><strong>${e.bit_size_in ? csFmt(e.bit_size_in, 3) + ' in' : '—'}</strong><small>pestaña 2</small></div>
      <div class="cs-eq-dato"><span>Presión de bomba real</span><strong>${e.presion_bomba_real ? csFmt(e.presion_bomba_real, 0) + ' psi' : '—'}</strong><small>pestaña 2</small></div>
      ${d.reologia ? `<div class="cs-eq-dato"><span>PV / YP</span><strong>${csFmt(d.reologia.pv, 0)} cP / ${csFmt(d.reologia.yp, 0)}</strong><small>lb/100 ft²${e.temp_reologia ? ` a ${csFmt(e.temp_reologia, 0)} °F` : ''}</small></div>` : ''}
    </div>`;

  const cont = document.getElementById('hdResultado');
  if(d.faltan && d.faltan.length){
    cont.innerHTML = `<div class="report-card-modern"><div class="cs-vacio">
      <strong>Para calcular la hidráulica falta:</strong>
      ${d.faltan.map(f => `<span>• ${csEsc(f)}</span>`).join('')}
    </div></div>`;
    return;
  }

  const t = d.totales, m = d.mecha, r = d.reologia;
  const quinta = d.edicion === '5';
  const avisos = (d.avisos || []).slice();
  if(quinta && !d.temperatura_disponible) avisos.push('Sin temperatura de superficie y gradiente en el encabezado del pozo: no se muestra la temperatura anular.');
  if(quinta) avisos.push('La PV y el YP no se corrigen por temperatura ni presión: hace falta la reología medida a varias temperaturas.');

  const dif = t.diferencia_real;
  cont.innerHTML = `
    ${avisos.length ? `<div class="cs-avisos">${avisos.map(a => `<div class="cs-aviso-item">${csEsc(a)}</div>`).join('')}</div>` : ''}

    <div class="report-card-modern hd-kpis">
      <div class="va-kpi va-kpi-neutro"><span>Pérdida en la sarta</span><strong>${csFmt(t.sarta, 0)} psi</strong><small>${csFmt(t.pct.sarta, 1)} % · incluye ${csFmt(t.superficie, 0)} psi de superficie</small></div>
      <div class="va-kpi va-kpi-neutro"><span>Pérdida en el anular</span><strong>${csFmt(t.anular, 0)} psi</strong><small>${csFmt(t.pct.anular, 1)} %</small></div>
      <div class="va-kpi va-kpi-neutro"><span>Pérdida en la mecha</span><strong>${csFmt(t.mecha, 0)} psi</strong><small>${csFmt(t.pct.mecha, 1)} %</small></div>
      <div class="va-kpi ${dif === null ? 'va-kpi-neutro' : (Math.abs(dif) <= 0.1 * t.total ? 'va-kpi-ok' : 'va-kpi-pendiente')}"><span>Presión de bomba calculada</span><strong>${csFmt(t.total, 0)} psi</strong>
        <small>${dif === null ? 'sin presión real para comparar' : `real ${csFmt(t.total + dif, 0)} psi (${dif > 0 ? '+' : ''}${csFmt(dif, 0)})`}</small></div>
      <div class="va-kpi va-kpi-neutro"><span>ECD en el fondo</span><strong>${csFmt(t.ecd_fondo, 2)} lb/gal</strong><small>TVD: ${csEsc(d.fuente_tvd)}</small></div>
    </div>

    <div class="report-card-modern">
      <div class="cs-card-titulo">Resultados por sección</div>
      <div class="cs-tabla-wrapper">
        <table class="cs-tabla hd-tabla">
          <thead>
            <tr>
              <th class="cs-num">Sec.</th><th>Descripción</th><th class="cs-num">Largo (ft)</th><th class="cs-num">Hoyo (in)</th>
              <th class="cs-num">OD (in)</th><th class="cs-num">ID (in)</th>
              <th class="cs-num">Pérdida sarta (psi)</th><th class="cs-num">Vel. anular (ft/min)</th><th class="cs-num">Vel. crítica (ft/min)</th>
              <th>Régimen anular</th><th class="cs-num">Pérdida anular (psi)</th><th class="cs-num">MD (ft)</th><th class="cs-num">ECD (lb/gal)</th>
              ${quinta ? '<th class="cs-num">Temp. anular (°F)</th><th class="cs-num">PV anular</th><th class="cs-num">YP anular</th>' : ''}
            </tr>
          </thead>
          <tbody>${d.secciones.map((s, i) => `
            <tr>
              <td class="cs-num cs-codigo">${i + 1}</td><td>${csEsc(s.descripcion)}</td>
              <td class="cs-num">${csFmt(s.longitud_ft, 0)}</td><td class="cs-num">${csFmt(s.diametro_hoyo_in, 3)}</td>
              <td class="cs-num">${csFmt(s.od_in, 3)}</td><td class="cs-num">${csFmt(s.id_in, 3)}</td>
              <td class="cs-num cs-final">${csFmt(s.perdida_sarta, 0)}</td>
              <td class="cs-num ${s.vel_anular > s.vel_critica ? 'hd-turbulento' : ''}">${csFmt(s.vel_anular, 0)}</td>
              <td class="cs-num">${csFmt(s.vel_critica, 0)}</td>
              <td><span class="hd-regimen hd-regimen-${s.regimen_anular.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')}">${csEsc(s.regimen_anular)}</span></td>
              <td class="cs-num cs-final">${csFmt(s.perdida_anular, 0)}</td>
              <td class="cs-num">${csFmt(s.md_ft, 0)}</td><td class="cs-num cs-final">${csFmt(s.ecd, 2)}</td>
              ${quinta ? `<td class="cs-num">${s.temp_anular === null ? '—' : csFmt(s.temp_anular, 0)}</td><td class="cs-num">${csFmt(s.pv_anular, 0)}</td><td class="cs-num">${csFmt(s.yp_anular, 0)}</td>` : ''}
            </tr>`).join('')}</tbody>
          <tfoot><tr class="cs-fila-total">
            <td colspan="6">Totales</td><td class="cs-num">${csFmt(t.sarta_secciones, 0)}</td><td colspan="3"></td>
            <td class="cs-num">${csFmt(t.anular, 0)}</td><td colspan="${quinta ? 5 : 2}"></td>
          </tr></tfoot>
        </table>
      </div>
      <p class="cs-nota">${csEsc(t.nota_superficie)} La velocidad anular en verde supera la crítica (flujo fuera de laminar).</p>
    </div>

    <div class="va-grid-2">
      <div class="report-card-modern">
        <div class="cs-card-titulo">Hidráulica de la mecha</div>
        <div class="va-datos">
          <div class="cs-eq-dato"><span>Pérdida en la mecha</span><strong>${csFmt(m.perdida, 0)} psi</strong><small>${csFmt(m.pct, 1)} % de la presión de bomba</small></div>
          <div class="cs-eq-dato"><span>Potencia hidráulica (HHP)</span><strong>${csFmt(m.hhp, 0)} hp</strong></div>
          <div class="cs-eq-dato"><span>HSI</span><strong>${csFmt(m.hsi, 2)} hp/in²</strong></div>
          <div class="cs-eq-dato"><span>Velocidad de chorro</span><strong>${csFmt(m.vel_chorro, 0)} ft/s</strong></div>
          <div class="cs-eq-dato"><span>Fuerza de impacto</span><strong>${csFmt(m.fuerza_impacto, 0)} lbf</strong></div>
        </div>
        <div class="cs-subtitulo">Distribución de la presión de bomba</div>
        <div class="hd-barra">
          <span class="hd-seg hd-seg-sarta" style="flex-grow:${t.sarta}" title="Sarta ${csFmt(t.pct.sarta, 1)} %"></span>
          <span class="hd-seg hd-seg-anular" style="flex-grow:${t.anular}" title="Anular ${csFmt(t.pct.anular, 1)} %"></span>
          <span class="hd-seg hd-seg-mecha" style="flex-grow:${t.mecha}" title="Mecha ${csFmt(t.pct.mecha, 1)} %"></span>
        </div>
        <div class="tt-leyenda">
          <span class="tt-leyenda-item"><span class="tt-punto hd-seg-sarta"></span>Sarta <strong>${csFmt(t.pct.sarta, 1)} %</strong></span>
          <span class="tt-leyenda-item"><span class="tt-punto hd-seg-anular"></span>Anular <strong>${csFmt(t.pct.anular, 1)} %</strong></span>
          <span class="tt-leyenda-item"><span class="tt-punto hd-seg-mecha"></span>Mecha <strong>${csFmt(t.pct.mecha, 1)} %</strong></span>
        </div>
      </div>
      <div class="report-card-modern">
        <div class="cs-card-titulo">Reograma &bull; ${d.edicion === '4' ? 'ley de potencia' : 'Herschel-Bulkley'}</div>
        ${hdReograma(r)}
        <div class="va-datos">
          <div class="cs-eq-dato"><span>n tubería / anular</span><strong>${csFmt(r.tuberia.n, 3)} / ${csFmt(r.anular.n, 3)}</strong></div>
          <div class="cs-eq-dato"><span>K tubería / anular</span><strong>${csFmt(r.tuberia.k, 3)} / ${csFmt(r.anular.k, 3)}</strong><small>${csEsc(r.unidad_k)}</small></div>
          ${quinta ? `<div class="cs-eq-dato"><span>τy (punto cedente verdadero)</span><strong>${csFmt(r.tuberia.ty, 2)}</strong><small>lbf/100 ft²</small></div>` : ''}
        </div>
      </div>
    </div>`;
}

/* Reograma log-log: lecturas medidas (puntos) y curva del modelo. */
function hdReograma(r){
  const W = 420, H = 220, M = { l: 44, r: 12, t: 10, b: 30 };
  const xs = [1, 1000], lecturas = r.curva.map(p => p.lectura).concat(r.puntos.map(p => p.lectura)).filter(v => v > 0);
  const ymin = Math.pow(10, Math.floor(Math.log10(Math.max(Math.min(...lecturas), 0.5))));
  const ymax = Math.pow(10, Math.ceil(Math.log10(Math.max(...lecturas))));
  const x = v => M.l + (Math.log10(v) - Math.log10(xs[0])) / (Math.log10(xs[1]) - Math.log10(xs[0])) * (W - M.l - M.r);
  const y = v => H - M.b - (Math.log10(v) - Math.log10(ymin)) / (Math.log10(ymax) - Math.log10(ymin)) * (H - M.t - M.b);
  let grid = '';
  for(let d = 1; d <= 1000; d *= 10){
    grid += `<line x1="${x(d)}" y1="${M.t}" x2="${x(d)}" y2="${H - M.b}" class="hd-grid"/><text x="${x(d)}" y="${H - 10}" class="hd-eje" text-anchor="middle">${d}</text>`;
  }
  for(let d = ymin; d <= ymax; d *= 10){
    grid += `<line x1="${M.l}" y1="${y(d)}" x2="${W - M.r}" y2="${y(d)}" class="hd-grid"/><text x="${M.l - 6}" y="${y(d) + 4}" class="hd-eje" text-anchor="end">${d}</text>`;
  }
  const curva = r.curva.filter(p => p.lectura > 0).map((p, i) => `${i ? 'L' : 'M'}${x(p.rpm).toFixed(1)},${y(p.lectura).toFixed(1)}`).join(' ');
  const puntos = r.puntos.map(p => `<circle cx="${x(p.rpm)}" cy="${y(p.lectura)}" r="4" class="hd-punto"><title>${p.rpm} rpm: ${p.lectura}</title></circle>`).join('');
  return `<svg class="hd-reograma" viewBox="0 0 ${W} ${H}" role="img" aria-label="Reograma">
    ${grid}<path d="${curva}" class="hd-curva"/>${puntos}
    <text x="${(W + M.l) / 2}" y="${H}" class="hd-eje" text-anchor="middle">rpm del viscosímetro</text>
  </svg>`;
}

document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('[data-hd-edicion]').forEach(b => b.addEventListener('click', function(){
    hdEdicion = b.dataset.hdEdicion;
    document.querySelectorAll('[data-hd-edicion]').forEach(x => x.classList.toggle('is-active', x === b));
    cargarHidraulica();
  }));
});
