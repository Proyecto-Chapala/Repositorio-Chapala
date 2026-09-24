/* =====================================================================
   MÓDULOS OPCIONALES DEL REPORTE DIARIO

   - Pestaña 6: Observaciones IFE, Análisis de sólidos por equipo y
     Retención en recortes (se abren desde los botones "Opcionales").
   - Pestaña 8: Evaluación de benchmark (consulta).
   - Pestañas 5 y 7: Eventos no programados (ventana).

   Ninguna otra pestaña usa estos datos. Depende de POZO_ID, REPORTE_ID,
   getCookie, showToast, switchTab y de csEsc, csNum, csFmt, csDinero,
   csCambiarVista (reporte_control_solidos.js).
   ===================================================================== */

const OP_BASE = `/api/pozos/${POZO_ID}/daily-report/${REPORTE_ID}/`;
const opCargado = {};
const opDatos = { solidos: null, retencion: null };
const opSel = { solidos: null, retencion: null };

async function opPost(ruta, payload){
  try {
    const res = await fetch(OP_BASE + ruta, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify(payload || {})
    });
    const data = await res.json();
    if(!data.ok){ showToast(data.error || 'No se pudo guardar.', false); return null; }
    if(data.mensaje) showToast(data.mensaje);
    return data;
  } catch(e){
    showToast('Error de conexión con el servidor.', false);
    return null;
  }
}

function opValor(v){ return v === null || v === undefined ? '' : v; }

function inicializarOpcionalSolidos(vista){
  if(vista === 'ife') opCargarIfe();
  if(vista === 'solidos_eq') opCargarMuestras('solidos');
  if(vista === 'retencion') opCargarMuestras('retencion');
}

/* ---------- Observaciones IFE ---------- */

async function opCargarIfe(){
  if(opCargado.ife) return;
  try {
    const data = await (await fetch(OP_BASE + 'ife/')).json();
    document.querySelectorAll('.op-ife').forEach(el => { el.value = data[el.dataset.campo] || ''; });
    opCargado.ife = true;
  } catch(e){ showToast('No se pudieron cargar las observaciones IFE.', false); }
}

async function opGuardarIfe(){
  const payload = {};
  document.querySelectorAll('.op-ife').forEach(el => { payload[el.dataset.campo] = el.value; });
  await opPost('ife/', payload);
}

/* ---------- Muestras por equipo (sólidos y retención) ---------- */

const OP_CAMPOS = {
  WBM: [['mud_weight', 'Peso del lodo', 'lb/gal'], ['water_pct', 'Agua', '% vol'], ['oil_pct', 'Aceite', '% vol'],
        ['solids_pct', 'Sólidos', '% vol'], ['k_from_kcl', 'K+ de KCl', 'mg/l'], ['chlorides', 'Cloruros', 'mg/l'],
        ['mbt', 'MBT', 'lb/bbl'], ['drill_solids_sg', 'SG sólidos perforados', ''], ['wt_additive_sg', 'SG densificante', ''],
        ['oil_sg', 'SG aceite', ''], ['frac_bent', 'Fracción de bentonita', ''], ['chem_conc', 'Conc. de químicos', 'lb/bbl']],
  OBM: [['mud_weight', 'Peso del lodo', 'lb/gal'], ['water_pct', 'Agua', '% vol'], ['oil_pct', 'Aceite / fluido base', '% vol'],
        ['solids_pct', 'Sólidos', '% vol'], ['chlorides', 'Cloruros (lodo entero)', 'mg/l'], ['oil_sg', 'SG fluido base', ''],
        ['wt_additive_sg', 'SG sólidos de alta gravedad', ''], ['drill_solids_sg', 'SG sólidos de baja gravedad', '']],
  RET: [['peso_lodo', 'Peso del lodo', 'lb/gal'], ['pct_fluido_base', 'Fluido base en retorta', '% vol'],
        ['sg_fluido_base', 'SG fluido base', ''], ['sg_solidos', 'SG de los sólidos', ''],
        ['celda_vacia', 'Celda vacía', 'g'], ['celda_humedo', 'Celda + recorte húmedo', 'g'], ['celda_seco', 'Celda + recorte seco', 'g'],
        ['probeta_vacia', 'Probeta vacía', 'g'], ['agua_cc', 'Agua recuperada', 'cc'], ['probeta_total', 'Probeta + agua + fluido base', 'g']],
};

const OP_RESULTADOS = {
  WBM: [['nacl_pct', 'NaCl', '% vol'], ['nacl_ppb', 'NaCl', 'lb/bbl'], ['kcl_pct', 'KCl', '% vol'], ['kcl_ppb', 'KCl', 'lb/bbl'],
        ['lgs_pct', 'Sólidos de baja gravedad', '% vol'], ['lgs_ppb', 'Sólidos de baja gravedad', 'lb/bbl'],
        ['bentonite_pct', 'Bentonita', '% vol'], ['bentonite_ppb', 'Bentonita', 'lb/bbl'],
        ['drill_solids_pct', 'Sólidos perforados', '% vol'], ['drill_solids_ppb', 'Sólidos perforados', 'lb/bbl'],
        ['hgs_pct', 'Sólidos de alta gravedad', '% vol'], ['hgs_ppb', 'Sólidos de alta gravedad', 'lb/bbl'],
        ['inerte_reactivo', 'Relación inerte / reactivo', ''], ['avg_sg_solids', 'SG promedio de sólidos', '']],
  OBM: [['salt_pct_wt', 'Sal', '% peso'], ['salt_ppb', 'Sal', 'lb/bbl'], ['adjusted_solids_pct', 'Sólidos corregidos', '% vol'],
        ['oil_water_ratio', 'Relación aceite / agua', ''], ['lgs_pct', 'Sólidos de baja gravedad', '% vol'],
        ['lgs_ppb', 'Sólidos de baja gravedad', 'lb/bbl'], ['hgs_pct', 'Sólidos de alta gravedad', '% vol'],
        ['hgs_ppb', 'Sólidos de alta gravedad', 'lb/bbl'], ['avg_sg_solids', 'SG promedio de sólidos', '']],
  RET: [['humedo_g', 'Recorte húmedo', 'g'], ['seco_g', 'Recorte seco', 'g'], ['fluido_base_g', 'Fluido base recuperado', 'g'],
        ['factor_balance', 'Factor de balance', ''], ['gkg_humedo', 'Fluido en recorte húmedo', 'g/kg'],
        ['gkg_seco', 'Fluido en recorte seco', 'g/kg'], ['pct_humedo', 'Fluido en recorte húmedo', '% peso'],
        ['pct_seco', 'Fluido en recorte seco', '% peso'], ['lodo_en_recortes', 'Lodo en recortes', 'bbl/bbl']],
};

async function opCargarMuestras(clave, forzar = false){
  if(opCargado[clave] && !forzar) return;
  try {
    const data = await (await fetch(OP_BASE + `muestras/${clave}/`)).json();
    opAplicarMuestras(clave, data);
    opCargado[clave] = true;
  } catch(e){ showToast('No se pudieron cargar las muestras.', false); }
}

function opAplicarMuestras(clave, data, seleccion){
  opDatos[clave] = data;
  if(seleccion !== undefined) opSel[clave] = seleccion;
  if(opSel[clave] && !data.muestras.some(m => m.id === opSel[clave])) opSel[clave] = null;
  if(opSel[clave] === null && data.muestras.length && seleccion === undefined) opSel[clave] = data.muestras[0].id;
  opRenderLista(clave);
  opRenderFicha(clave);
}

function opRenderLista(clave){
  const cont = document.getElementById(clave === 'solidos' ? 'opListaSolidos' : 'opListaRetencion');
  const ms = opDatos[clave].muestras;
  cont.innerHTML = ms.length ? ms.map(m => `
    <button type="button" class="cs-tk-item ${m.id === opSel[clave] ? 'is-active' : ''}" data-op-muestra="${clave}:${m.id}">
      <span class="cs-tk-item-tipo">${csEsc(m.equipo_descripcion)} · ${csEsc(m.equipo_serie)}</span>
      <span class="cs-tk-item-num">${m.hora_inicio || '--:--'} – ${m.hora_fin || '--:--'}</span>
      <span class="cs-tk-item-meta">${clave === 'solidos' ? (m.tipo_lodo === 'OBM' ? 'Base aceite' : 'Base agua') + (m.tipo_muestra ? ' · ' + csEsc(m.tipo_muestra) : '')
        : (m.resultados.lodo_en_recortes !== null ? `Lodo en recortes: ${csFmt(m.resultados.lodo_en_recortes, 3)} bbl/bbl` : 'Sin resultado')}</span>
    </button>`).join('') : '<div class="cs-vacio">Sin muestras en este reporte.</div>';
}

function opCampo(clave, campo, etiqueta, unidad, valor, tipo = 'number'){
  return `<label class="cs-campo"><span class="cs-campo-label">${etiqueta}${unidad ? ` <em>(${unidad})</em>` : ''}</span>
    <input type="${tipo}" class="report-input op-in" ${tipo === 'number' ? 'step="any" min="0"' : ''} data-op-campo="${campo}" value="${csEsc(opValor(valor))}"></label>`;
}

function opRenderFicha(clave){
  const cont = document.getElementById(clave === 'solidos' ? 'opFichaSolidos' : 'opFichaRetencion');
  const d = opDatos[clave];
  const m = d.muestras.find(x => x.id === opSel[clave])
    || { datos: {}, resultados: {}, avisos: [], tipo_lodo: d._tipoNueva || 'WBM', orden: d.muestras.length + 1 };
  const nueva = !m.id;
  if(!d.equipos.length){
    cont.innerHTML = '<div class="cs-vacio">El pozo no tiene equipos activos. Agrégalos en Productos, Equipos y Mallas Activos.</div>';
    return;
  }
  const equipos = d.equipos.map(e => `<option value="${csEsc(e.serie)}" ${e.serie === m.equipo_serie ? 'selected' : ''}>${csEsc(e.descripcion)} · ${csEsc(e.serie)} (${csEsc(e.tipo)})</option>`).join('')
    + (m.equipo_serie && !d.equipos.some(e => e.serie === m.equipo_serie) ? `<option value="${csEsc(m.equipo_serie)}" selected>${csEsc(m.equipo_descripcion)} · ${csEsc(m.equipo_serie)} (inactivo)</option>` : '');
  const tipo = clave === 'solidos' ? m.tipo_lodo : 'RET';
  const campos = OP_CAMPOS[tipo].map(([c, e, u]) => opCampo(clave, 'datos.' + c, e, u, m.datos[c])).join('');
  const res = OP_RESULTADOS[tipo].map(([c, e, u]) => {
    const v = m.resultados[c];
    return `<div class="cs-resultado"><span>${e}${u ? ` (${u})` : ''}</span><strong>${v === null || v === undefined ? '—' : (typeof v === 'number' ? csFmt(v, c === 'factor_balance' || c === 'lodo_en_recortes' ? 3 : 2) : csEsc(v))}</strong></div>`;
  }).join('');

  cont.innerHTML = `
    <div class="cs-card-cabecera">
      <div>
        <span class="cs-card-titulo">${nueva ? 'Nueva muestra' : csEsc(m.equipo_descripcion)}</span>
        <span class="cs-card-subtitulo">${clave === 'solidos' ? 'Análisis de sólidos con el mismo balance de la pestaña 3.' : 'Prueba de retorta sobre los recortes que descarga el equipo.'} Módulo opcional.</span>
      </div>
    </div>
    <div class="cs-campos op-cabecera">
      <label class="cs-campo"><span class="cs-campo-label">Equipo</span><select class="report-input op-in" data-op-campo="equipo_serie"><option value="">Elige…</option>${equipos}</select></label>
      ${opCampo(clave, 'hora_inicio', 'Hora de inicio', 'HH:MM', m.hora_inicio, 'text')}
      ${opCampo(clave, 'hora_fin', 'Hora de fin', 'HH:MM', m.hora_fin, 'text')}
      ${opCampo(clave, 'orden', 'Orden de impresión', '', m.orden)}
      ${opCampo(clave, 'profundidad_ft', 'Profundidad medida', 'ft', m.profundidad_ft)}
      ${opCampo(clave, 'profundidad_perforada_ft', 'Profundidad perforada representada', 'ft', m.profundidad_perforada_ft)}
      ${clave === 'solidos'
        ? `${opCampo(clave, 'tipo_muestra', 'Tipo de muestra', 'ej. descarga', m.tipo_muestra, 'text')}
           <div class="cs-campo"><span class="cs-campo-label">Tipo de lodo</span>
             <div class="cs-condicion"><button type="button" class="cs-condicion-btn ${m.tipo_lodo !== 'OBM' ? 'is-active' : ''}" data-op-lodo="WBM">Base agua</button>
             <button type="button" class="cs-condicion-btn ${m.tipo_lodo === 'OBM' ? 'is-active' : ''}" data-op-lodo="OBM">Base aceite</button></div></div>`
        : opCampo(clave, 'diametro_mecha_in', 'Diámetro de mecha', 'in', m.diametro_mecha_in)}
    </div>
    <label class="cs-campo op-comentarios"><span class="cs-campo-label">Comentarios</span><input type="text" maxlength="255" class="report-input op-in" data-op-campo="comentarios" value="${csEsc(opValor(m.comentarios))}"></label>
    <div class="cs-subtitulo">Datos de la muestra</div>
    <div class="cs-campos">${campos}
      ${tipo === 'OBM' ? `<label class="cs-campo"><span class="cs-campo-label">Sal de la fase interna</span><select class="report-input op-in" data-op-campo="datos.sal">
        <option value="CaCl2" ${m.datos.sal !== 'NaCl' ? 'selected' : ''}>CaCl2</option><option value="NaCl" ${m.datos.sal === 'NaCl' ? 'selected' : ''}>NaCl</option></select></label>` : ''}
    </div>
    ${(m.avisos || []).map(a => `<div class="cs-aviso-item">${csEsc(a)}</div>`).join('')}
    <div class="cs-subtitulo">Resultados ${nueva ? '(se calculan al guardar)' : ''}</div>
    <div class="cs-resultados">${res}</div>
    ${clave === 'retencion' ? '<p class="cs-nota">El "lodo en recortes" es una reconstrucción de la fórmula de ONE-TRAX (en el ejemplo del manual da ~1,5 % más). Puedes usarlo como referencia en el rendimiento de equipos.</p>' : ''}
    <div class="cs-tk-acciones">
      ${nueva ? '' : `<button type="button" class="btn-modern-secondary btn-sm cs-btn-peligro" data-op-eliminar="${clave}:${m.id}"><span>&#128465;</span><span>Eliminar</span></button>`}
      <span class="cs-flex"></span>
      <button type="button" class="btn-modern-primary btn-sm" data-op-guardar="${clave}"><span>&#128190;</span><span>Guardar y calcular</span></button>
    </div>`;
  cont.dataset.tipoLodo = m.tipo_lodo || 'WBM';
}

async function opGuardarMuestra(clave){
  const cont = document.getElementById(clave === 'solidos' ? 'opFichaSolidos' : 'opFichaRetencion');
  const payload = { id: opSel[clave], datos: {}, tipo_lodo: cont.dataset.tipoLodo };
  cont.querySelectorAll('.op-in').forEach(el => {
    const c = el.dataset.opCampo;
    if(c.startsWith('datos.')) payload.datos[c.slice(6)] = el.value;
    else payload[c] = el.value;
  });
  const data = await opPost(`muestras/${clave}/guardar/`, payload);
  if(data) opAplicarMuestras(clave, data, data.id);
}

/* ---------- Evaluación de benchmark ---------- */

async function cargarBenchmark(){
  const cont = document.getElementById('opBenchmark');
  cont.innerHTML = '<div class="cs-vacio cs-vacio-centrado">Calculando…</div>';
  try {
    const d = await (await fetch(OP_BASE + 'benchmark/')).json();
    if(!d.filas.length){
      cont.innerHTML = '<div class="cs-vacio">El pozo no tiene parámetros de benchmark seleccionados. Defínelos en el Benchmark Setup del pozo.</div>';
      return;
    }
    const celda = c => {
      const obj = c.minimo !== null || c.maximo !== null
        ? `${c.minimo === null ? '—' : csFmt(c.minimo, 2)} – ${c.maximo === null ? '—' : csFmt(c.maximo, 2)}`
        : (c.valor ? csEsc(c.valor) : '<span class="cs-tenue">sin objetivo</span>');
      const real = c.n ? (c.real_min === c.real_max ? csFmt(c.real_min, 2) : `${csFmt(c.real_min, 2)} – ${csFmt(c.real_max, 2)}`) : '<span class="cs-tenue">sin datos</span>';
      const pct = c.pct_dentro === null ? '' : `<span class="op-pct ${c.pct_dentro >= 90 ? 'op-pct-ok' : (c.pct_dentro >= 60 ? 'op-pct-medio' : 'op-pct-bajo')}">${csFmt(c.pct_dentro, 0)} % dentro</span>`;
      return `<td><div class="op-bm-obj">Objetivo: <strong>${obj}</strong></div><div class="op-bm-real">Real: <strong>${real}</strong> ${c.n ? `<span class="cs-tenue">(${c.n})</span>` : ''}</div>${pct}</td>`;
    };
    cont.innerHTML = `<div class="cs-tabla-wrapper"><table class="cs-tabla op-bm-tabla">
      <thead><tr><th>Parámetro</th>${d.columnas.map(c => `<th>${csEsc(c.etiqueta)}<div class="cs-tenue">${c.detalle ? csEsc(c.detalle) + ' · ' : ''}${c.reportes} reporte(s)${c.tope_ft !== null ? ` · ${csFmt(c.tope_ft, 0)}–${csFmt(c.fondo_ft, 0)} ft` : ''}</div></th>`).join('')}</tr></thead>
      <tbody>${d.filas.map(f => `<tr><td><strong>${csEsc(f.descripcion)}</strong><div class="cs-tenue">${csEsc(f.grupo)} · ${csEsc(f.tipo_fluido)}${f.unidad ? ' · ' + csEsc(f.unidad) : ''}</div>
        ${f.vinculado ? '' : '<div class="op-sin-vinculo">No se reconoce la propiedad de la pestaña 3</div>'}</td>
        ${d.columnas.map(c => celda(f.celdas[c.clave])).join('')}</tr>`).join('')}</tbody></table></div>
      <p class="cs-nota">La propiedad medida se reconoce por el nombre del parámetro (peso del lodo, PV, YP, filtrado API o HTHP, embudo, geles, MBT, pH, arena, sólidos, cloruros, estabilidad eléctrica). Los parámetros de base agua o aceite solo cuentan los reportes con ese tipo de lodo.</p>`;
  } catch(e){
    cont.innerHTML = '<div class="cs-vacio">No se pudo calcular la evaluación de benchmark.</div>';
  }
}

/* ---------- Eventos no programados ---------- */

let enDatos = null;
let enSel = null;

async function enCargar(abrir = false){
  try {
    enDatos = await (await fetch(OP_BASE + 'eventos/')).json();
    document.querySelectorAll('[data-en-badge]').forEach(b => { b.textContent = enDatos.eventos.length; b.hidden = !enDatos.eventos.length; });
    if(abrir){
      const propios = enDatos.eventos.filter(e => e.es_de_este_reporte);
      enSel = propios.length ? propios[propios.length - 1].id : null;
      document.getElementById('enModal').hidden = false;
    }
    if(!document.getElementById('enModal').hidden) enRender();
  } catch(e){ if(abrir) showToast('No se pudieron cargar los eventos.', false); }
}

function enRender(){
  const e = enDatos.eventos.find(x => x.id === enSel) || null;
  const editable = !e || e.es_de_este_reporte;
  const v = k => csEsc(opValor(e ? e[k] : (k === 'tipo_fluido' ? enDatos.tipo_fluido_sugerido : '')));
  const dis = editable ? '' : 'disabled';
  document.getElementById('enCuerpo').innerHTML = `
    <aside class="cs-tk-lista">
      <button type="button" class="btn-modern-primary btn-sm cs-tk-nuevo" id="enNuevo"><span>&#10133;</span><span>Nuevo evento</span></button>
      ${enDatos.eventos.length ? enDatos.eventos.map(x => `
        <button type="button" class="cs-tk-item ${x.id === enSel ? 'is-active' : ''}" data-en-evento="${x.id}">
          <span class="cs-tk-item-tipo">${csEsc(x.categoria_display)}</span>
          <span class="cs-tk-item-num">${csEsc(x.tipo_problema)}</span>
          <span class="cs-tk-item-meta">${x.fecha}${x.es_de_este_reporte ? ' · este reporte' : ''}</span>
        </button>`).join('') : '<div class="cs-vacio">El pozo no tiene eventos no programados.</div>'}
    </aside>
    <section class="cs-tk-form">
      ${editable ? '' : `<div class="cs-aviso-item">Evento del reporte del ${e.fecha}: se edita desde ese reporte.</div>`}
      <div class="cs-tk-encabezado">
        <label class="cs-campo"><span class="cs-campo-label">Categoría</span><select class="report-input en-in" data-en-campo="categoria" ${dis}>
          ${enDatos.categorias.map(c => `<option value="${c.codigo}" ${e && e.categoria === c.codigo ? 'selected' : ''}>${csEsc(c.nombre)}</option>`).join('')}</select></label>
        <label class="cs-campo"><span class="cs-campo-label">Tipo de problema</span><input type="text" maxlength="100" class="report-input en-in" data-en-campo="tipo_problema" value="${v('tipo_problema')}" placeholder="Ej.: pérdida de circulación" ${dis}></label>
        <label class="cs-campo"><span class="cs-campo-label">Tipo de fluido</span><input type="text" maxlength="100" class="report-input en-in" data-en-campo="tipo_fluido" value="${v('tipo_fluido')}" ${dis}></label>
        <label class="cs-campo"><span class="cs-campo-label">Tiempo perdido <em>(h)</em></span><input type="number" min="0" step="any" class="report-input en-in" data-en-campo="horas_perdidas" value="${v('horas_perdidas')}" ${dis}></label>
        <label class="cs-campo"><span class="cs-campo-label">Volumen perdido <em>(bbl)</em></span><input type="number" min="0" step="any" class="report-input en-in" data-en-campo="volumen_perdido_bbl" value="${v('volumen_perdido_bbl')}" ${dis}></label>
        <label class="cs-campo"><span class="cs-campo-label">Costo estimado</span><input type="number" min="0" step="any" class="report-input en-in" data-en-campo="costo" value="${v('costo')}" ${dis}></label>
      </div>
      <label class="cs-campo"><span class="cs-campo-label">Descripción</span><textarea class="cm-textarea en-in" rows="3" data-en-campo="descripcion" ${dis}>${v('descripcion')}</textarea></label>
      <label class="cs-campo"><span class="cs-campo-label">Causa sospechada</span><textarea class="cm-textarea en-in" rows="2" data-en-campo="causa" ${dis}>${v('causa')}</textarea></label>
      <label class="cs-campo"><span class="cs-campo-label">Descripción de la pérdida</span><textarea class="cm-textarea en-in" rows="2" data-en-campo="descripcion_perdida" ${dis}>${v('descripcion_perdida')}</textarea></label>
    </section>`;
  document.getElementById('enPie').innerHTML = `
    ${e && editable ? '<button type="button" class="btn-modern-secondary btn-sm cs-btn-peligro" id="enEliminar"><span>&#128465;</span><span>Eliminar evento</span></button>' : ''}
    <span class="cs-flex"></span>
    ${editable ? '<button type="button" class="btn-modern-primary btn-sm" id="enGuardar"><span>&#128190;</span><span>Guardar evento</span></button>' : ''}`;
}

/* ---------- Eventos ---------- */

document.addEventListener('DOMContentLoaded', function(){
  const ife = document.getElementById('opIfeGuardar');
  if(ife) ife.addEventListener('click', opGuardarIfe);

  const panel = document.getElementById('tabContent-solidos');
  if(panel){
    panel.addEventListener('click', function(ev){
      const nueva = ev.target.closest('[data-op-nueva]');
      if(nueva){ opDatos[nueva.dataset.opNueva]._tipoNueva = 'WBM'; opAplicarMuestras(nueva.dataset.opNueva, opDatos[nueva.dataset.opNueva], null); return; }
      const item = ev.target.closest('[data-op-muestra]');
      if(item){ const [c, id] = item.dataset.opMuestra.split(':'); opAplicarMuestras(c, opDatos[c], Number(id)); return; }
      const lodo = ev.target.closest('[data-op-lodo]');
      if(lodo){
        const m = opDatos.solidos.muestras.find(x => x.id === opSel.solidos);
        if(m) m.tipo_lodo = lodo.dataset.opLodo;
        else opDatos.solidos._tipoNueva = lodo.dataset.opLodo;
        opRenderFicha('solidos');
        return;
      }
      const g = ev.target.closest('[data-op-guardar]');
      if(g){ opGuardarMuestra(g.dataset.opGuardar); return; }
      const del = ev.target.closest('[data-op-eliminar]');
      if(del && window.confirm('¿Eliminar esta muestra?')){
        const [c, id] = del.dataset.opEliminar.split(':');
        opPost(`muestras/${c}/${id}/eliminar/`, {}).then(d => { if(d) opAplicarMuestras(c, d, null); });
      }
    });
  }

  const irRet = document.getElementById('opIrRetencion');
  if(irRet) irRet.addEventListener('click', function(){ switchTab(6); inicializarControlSolidos(); csCambiarVista('retencion'); });

  document.querySelectorAll('[data-en-abrir]').forEach(b => b.addEventListener('click', () => enCargar(true)));
  const modal = document.getElementById('enModal');
  if(modal){
    document.getElementById('enCerrar').addEventListener('click', () => { modal.hidden = true; });
    modal.addEventListener('click', async function(ev){
      if(ev.target === modal){ modal.hidden = true; return; }
      const it = ev.target.closest('[data-en-evento]');
      if(it){ enSel = Number(it.dataset.enEvento); enRender(); return; }
      const id = ev.target.closest('button')?.id;
      if(id === 'enNuevo'){ enSel = null; enRender(); }
      else if(id === 'enGuardar'){
        const payload = { id: enSel };
        modal.querySelectorAll('.en-in').forEach(el => { payload[el.dataset.enCampo] = el.value; });
        const d = await opPost('eventos/guardar/', payload);
        if(d){ enDatos = d; enSel = d.id; enRender(); document.querySelectorAll('[data-en-badge]').forEach(b => { b.textContent = d.eventos.length; b.hidden = !d.eventos.length; }); }
      } else if(id === 'enEliminar' && window.confirm('¿Eliminar este evento?')){
        const d = await opPost(`eventos/${enSel}/eliminar/`, {});
        if(d){ enDatos = d; enSel = null; enRender(); document.querySelectorAll('[data-en-badge]').forEach(b => { b.textContent = d.eventos.length; b.hidden = !d.eventos.length; }); }
      }
    });
    document.addEventListener('keydown', ev => { if(ev.key === 'Escape' && !modal.hidden) modal.hidden = true; });
    enCargar(false);
  }
});
