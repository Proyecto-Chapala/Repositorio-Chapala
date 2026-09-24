/* =====================================================================
   PESTAÑA 8 — INVENTARIO / HIDRÁULICA / CONCENTRACIONES

   1. Volumetría e inventario de productos (más abajo, prefijo "va").
   2. Concentración de productos (consulta).
   ⚙ Pérdidas del reporte: qué categorías de pérdida (máximo 10, en orden)
     muestra el reporte diario. La selección es del pozo, no del día.

   Depende de las utilidades globales de reporte_diario_detalle.html
   (POZO_ID, REPORTE_ID, getCookie, showToast) y de reporte_control_solidos.js
   (csEsc, csNum, csFmt, csDinero), que se carga antes.
   ===================================================================== */

const IV_API_PERDIDAS = `/api/pozos/${POZO_ID}/perdidas-reporte/`;

let ivCargado = false;
let ivListo = false;
let ivDatos = null;
let ivSeleccion = [];        // códigos en el orden del reporte
let ivMarcaDisponible = null;
let ivMarcaSeleccion = null;
let ivSucio = false;

function ivEsc(texto){
  const div = document.createElement('div');
  div.textContent = texto == null ? '' : String(texto);
  return div.innerHTML;
}

async function inicializarInventario(){
  inicializarVolumetria();
  cargarPerdidasReporte();
}

async function cargarPerdidasReporte(){
  if(ivCargado) return;
  ivCargado = true;
  try {
    const res = await fetch(IV_API_PERDIDAS);
    const data = await res.json();
    if(!data.ok) throw new Error(data.error || 'respuesta inválida');
    ivAplicar(data);
    ivListo = true;
  } catch(e){
    ivCargado = false;
    showToast('No se pudo cargar la configuración de pérdidas del reporte.', false);
  }
}

function ivAplicar(data){
  ivDatos = data;
  ivSeleccion = data.seleccionadas.slice();
  ivSucio = false;
  document.getElementById('ivLinkConfigPerdidas').href = data.enlace_configuracion;
  ivRender();
}

function ivCategoria(codigo){
  return ivDatos.disponibles.find(c => c.codigo === codigo);
}

function ivItem(c, marcado){
  return `<li class="iv-item ${marcado ? 'is-marcado' : ''}" data-codigo="${c.codigo}" tabindex="0">
    <span class="iv-item-codigo">${c.codigo}</span>
    <span class="iv-item-texto">${ivEsc(c.descripcion)}</span>
    <span class="iv-item-tipo iv-tipo-${c.tipo.toLowerCase()}">${ivEsc(c.tipo_display)}</span>
  </li>`;
}

function ivRender(){
  const max = ivDatos.maximo;
  const libres = ivDatos.disponibles.filter(c => !ivSeleccion.includes(c.codigo));

  document.getElementById('ivDisponibles').innerHTML = libres.length
    ? libres.map(c => ivItem(c, c.codigo === ivMarcaDisponible)).join('')
    : '<li class="iv-vacio">Todas las categorías están en el reporte.</li>';
  document.getElementById('ivSeleccionadas').innerHTML = ivSeleccion.length
    ? ivSeleccion.map(cod => ivCategoria(cod)).filter(Boolean).map(c => ivItem(c, c.codigo === ivMarcaSeleccion)).join('')
    : '<li class="iv-vacio">Agrega al menos una categoría.</li>';

  document.getElementById('ivContDisponibles').textContent = `${ivDatos.disponibles.length} de 20`;
  const cont = document.getElementById('ivContSeleccionadas');
  cont.textContent = `${ivSeleccion.length} de ${max}`;
  cont.classList.toggle('is-lleno', ivSeleccion.length >= max);

  const lleno = ivSeleccion.length >= max;
  document.getElementById('ivAgregar').disabled = lleno || ivMarcaDisponible === null;
  document.getElementById('ivAgregarTodas').disabled = lleno || !libres.length;
  document.getElementById('ivQuitar').disabled = ivMarcaSeleccion === null;
  const pos = ivSeleccion.indexOf(ivMarcaSeleccion);
  document.getElementById('ivSubir').disabled = pos <= 0;
  document.getElementById('ivBajar').disabled = pos < 0 || pos >= ivSeleccion.length - 1;

  const nota = document.getElementById('ivNotaPerdidas');
  if(ivSucio) nota.textContent = 'Hay cambios sin guardar.';
  else if(!ivDatos.personalizado) nota.textContent = 'Todavía no hay selección guardada: se muestran las 10 primeras categorías por código.';
  else nota.textContent = 'Selección guardada para este pozo.';
}

function ivCambio(){
  ivSucio = true;
  ivRender();
}

async function guardarPerdidasReporte(silent = false){
  if(!ivListo){
    if(!silent) showToast('La configuración de pérdidas todavía no terminó de cargar.', false);
    return;
  }
  try {
    const res = await fetch(IV_API_PERDIDAS + 'guardar/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify({ codigos: ivSeleccion })
    });
    const data = await res.json();
    if(data.ok){
      ivAplicar(data);
      if(!silent) showToast(data.mensaje || 'Pérdidas del reporte guardadas.');
    } else {
      showToast(data.error || 'No se pudo guardar la selección.', false);
    }
  } catch(e){
    showToast('Error de conexión al guardar la selección de pérdidas.', false);
  }
}

document.addEventListener('DOMContentLoaded', function(){
  const panel = document.getElementById('ivVistaPerdidas');
  if(!panel) return;

  document.getElementById('ivDisponibles').addEventListener('click', function(ev){
    const li = ev.target.closest('.iv-item');
    if(!li) return;
    ivMarcaDisponible = parseInt(li.dataset.codigo, 10);
    ivRender();
  });
  document.getElementById('ivDisponibles').addEventListener('dblclick', function(ev){
    const li = ev.target.closest('.iv-item');
    if(!li || ivSeleccion.length >= ivDatos.maximo) return;
    ivSeleccion.push(parseInt(li.dataset.codigo, 10));
    ivMarcaDisponible = null;
    ivCambio();
  });
  document.getElementById('ivSeleccionadas').addEventListener('click', function(ev){
    const li = ev.target.closest('.iv-item');
    if(!li) return;
    ivMarcaSeleccion = parseInt(li.dataset.codigo, 10);
    ivRender();
  });
  document.getElementById('ivSeleccionadas').addEventListener('dblclick', function(ev){
    const li = ev.target.closest('.iv-item');
    if(!li) return;
    ivSeleccion = ivSeleccion.filter(c => c !== parseInt(li.dataset.codigo, 10));
    ivMarcaSeleccion = null;
    ivCambio();
  });

  document.getElementById('ivAgregar').addEventListener('click', function(){
    if(ivMarcaDisponible === null || ivSeleccion.length >= ivDatos.maximo) return;
    ivSeleccion.push(ivMarcaDisponible);
    ivMarcaDisponible = null;
    ivCambio();
  });
  document.getElementById('ivQuitar').addEventListener('click', function(){
    if(ivMarcaSeleccion === null) return;
    ivSeleccion = ivSeleccion.filter(c => c !== ivMarcaSeleccion);
    ivMarcaSeleccion = null;
    ivCambio();
  });
  document.getElementById('ivAgregarTodas').addEventListener('click', function(){
    for(const c of ivDatos.disponibles){
      if(ivSeleccion.length >= ivDatos.maximo) break;
      if(!ivSeleccion.includes(c.codigo)) ivSeleccion.push(c.codigo);
    }
    ivCambio();
  });
  function mover(delta){
    const i = ivSeleccion.indexOf(ivMarcaSeleccion);
    const j = i + delta;
    if(i < 0 || j < 0 || j >= ivSeleccion.length) return;
    [ivSeleccion[i], ivSeleccion[j]] = [ivSeleccion[j], ivSeleccion[i]];
    ivCambio();
  }
  document.getElementById('ivSubir').addEventListener('click', () => mover(-1));
  document.getElementById('ivBajar').addEventListener('click', () => mover(1));
  document.getElementById('ivGuardarPerdidas').addEventListener('click', () => guardarPerdidasReporte());
});

/* =====================================================================
   NAVEGACIÓN DE LA PESTAÑA 8 Y GUARDADO
   ===================================================================== */

let ivVista = 'volumetria';

function ivCambiarVista(vista){
  ivVista = vista;
  document.querySelectorAll('[data-iv-vista]').forEach(b => b.classList.toggle('is-active', b.dataset.ivVista === vista));
  document.getElementById('ivVistaVolumetria').hidden = vista !== 'volumetria';
  document.getElementById('ivVistaConcentracion').hidden = vista !== 'concentracion';
  document.getElementById('ivVistaPerdidas').hidden = vista !== 'perdidas';
  if(vista === 'concentracion' && vaDatos) vaRenderConcentracion();
}

async function guardarPestanaInventario(silent = false){
  const algo = (typeof vaSucio !== 'undefined' && vaSucio) || ivSucio;
  if(vaSucio || (!silent && ivVista === 'volumetria')) await guardarVolumetria(silent);
  if(ivSucio || (!silent && ivVista === 'perdidas')) await guardarPerdidasReporte(silent);
  if(!silent && !algo && ivVista === 'concentracion') showToast('La concentración de productos es solo de consulta.');
}

/* =====================================================================
   1. VOLUMETRÍA E INVENTARIO DE PRODUCTOS

   Lo medido y escrito a mano (tipo y volumen real de fosas, hoyo e
   inventario) se guarda con "Guardar volumetría". Los movimientos
   (químicos, lodo entero, transferencias, devoluciones, pérdidas) y los
   tickets se registran al momento y el servidor valida toda la línea de
   tiempo del pozo. Espejo de volumetria.py: vaVolumenQuimico / vaMasaLb.
   ===================================================================== */

const VA_BASE = `/api/pozos/${POZO_ID}/daily-report/${REPORTE_ID}/volumetria/`;
const VA_GRUPOS = ['ACTIVO', 'RESERVA', 'PREMEZCLA', 'OTRAS'];
const VA_FACTOR_MASA = { LB: 1, LBS: 1, KG: 2.20462, TN: 2000, TON: 2000, ST: 2000, MT: 2204.62, TM: 2204.62, T: 2204.62 };
const VA_LB_POR_BBL = 350;
const VA_OTRO_DESTINO = 'Otro taladro / pozo';

let vaCargado = false;
let vaListo = false;
let vaDatos = null;
let vaSucio = false;
let vaTiposCambiados = false;
let vaTab = 'fosas';
let vaModalTipo = null;
let vaTicketSel = null;
let vaOcupado = false;

function vaGrupoDeTipo(codigo){
  if(codigo === null || codigo === undefined || codigo === '' || Number(codigo) === 0) return null;
  return ({1: 'ACTIVO', 2: 'RESERVA', 3: 'PREMEZCLA'})[Number(codigo)] || 'OTRAS';
}

function vaMasaLb(cantidad, unidad, tamano){
  const f = VA_FACTOR_MASA[(unidad || '').trim().toUpperCase().replace(/\.$/, '')];
  if(f === undefined) return null;
  return (csNum(cantidad) || 0) * (csNum(tamano) || 0) * f;
}

function vaVolumenQuimico(cantidad, unidad, tamano, gravedad){
  const m = vaMasaLb(cantidad, unidad, tamano);
  const g = csNum(gravedad) || 0;
  return m === null || g <= 0 ? 0 : m / (g * VA_LB_POR_BBL);
}

function vaCant(n, dec = 2){
  return n ? csFmt(n, dec) : '<span class="cs-cero">0</span>';
}

function vaMarcarSucio(){
  vaSucio = true;
  document.getElementById('vaTagCambios').hidden = false;
  document.getElementById('vaEstado').textContent = vaTiposCambiados
    ? 'Cambios sin guardar · guarda para recalcular los grupos'
    : 'Hay cambios sin guardar';
}

async function vaPost(ruta, payload){
  if(vaOcupado) return null;
  vaOcupado = true;
  try {
    const res = await fetch(VA_BASE + ruta, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify(payload || {})
    });
    const data = await res.json();
    if(!data.ok){
      showToast(data.error || 'No se pudo completar la operación.', false);
      return null;
    }
    vaAplicar(data, true);
    if(data.mensaje) showToast(data.mensaje);
    return data;
  } catch(e){
    showToast('Error de conexión con el servidor.', false);
    return null;
  } finally {
    vaOcupado = false;
  }
}

async function inicializarVolumetria(){
  if(vaCargado) return;
  vaCargado = true;
  try {
    const res = await fetch(VA_BASE);
    const data = await res.json();
    if(!data.ok) throw new Error(data.error || 'respuesta inválida');
    vaAplicar(data, false);
    vaListo = true;
  } catch(e){
    vaCargado = false;
    document.getElementById('vaKpis').innerHTML = '<div class="cs-vacio">No se pudo cargar la volumetría.</div>';
    showToast('No se pudo cargar la volumetría.', false);
  }
}

/* Aplica la respuesta del servidor. Si hay cambios sin guardar en el formulario y la
   respuesta viene de un movimiento, se conservan los valores escritos. */
function vaAplicar(data, conservar){
  const previo = conservar && vaSucio && vaDatos ? vaCapturar() : null;
  vaDatos = data;
  if(previo){
    vaDatos.fosas.forEach(f => {
      const p = previo.fosas.find(x => x.numero === f.numero);
      if(p){ f.real = csNum(p.real); f.peso = csNum(p.peso); f.temperatura = csNum(p.temperatura); }
    });
    ['anular', 'sarta', 'bajo_mecha'].forEach(k => { vaDatos.hoyo.no_fluido[k] = csNum(previo.hoyo[k]) || 0; });
    vaDatos.inventario.forEach(r => {
      const p = previo.inventario.find(x => x.producto_id === r.producto_id);
      if(p){ r.usado_otro = csNum(p.usado_otro) || 0; r.ajuste = csNum(p.ajuste) || 0; r.en_pedido = csNum(p.en_pedido) || 0; r.no_imprimir = p.no_imprimir; }
    });
  } else {
    vaSucio = false;
    vaTiposCambiados = false;
    document.getElementById('vaTagCambios').hidden = true;
    document.getElementById('vaEstado').textContent = '';
  }
  vaDatos.inventario.forEach(r => { r._otro_guardado = r.usado_otro; r._ajuste_guardado = r.ajuste; });
  vaDatos.fosas.forEach(f => { f._tipo_guardado = f.tipo_codigo; });

  const alerta = document.getElementById('vaAlerta');
  alerta.hidden = !data.error_linea_tiempo;
  alerta.textContent = data.error_linea_tiempo ? `Hay movimientos inconsistentes en el pozo: ${data.error_linea_tiempo}` : '';
  document.getElementById('vaLinkFosas').href = data.enlaces.fosas;

  const bm = document.getElementById('vaBadgeMov');
  bm.textContent = data.movimientos.length; bm.hidden = !data.movimientos.length;
  const bt = document.getElementById('vaBadgeTickets');
  bt.textContent = data.tickets.length; bt.hidden = !data.tickets.length;

  vaRenderTodo();
  if(!document.getElementById('vaModal').hidden) vaRenderModal();
}

function vaCapturar(){
  return {
    fosas: vaDatos.fosas.map(f => ({ numero: f.numero, tipo_codigo: f.tipo_codigo, real: f.real, peso: f.peso, temperatura: f.temperatura })),
    hoyo: Object.assign({}, vaDatos.hoyo.no_fluido),
    inventario: vaDatos.inventario.map(r => ({ producto_id: r.producto_id, usado_otro: r.usado_otro, ajuste: r.ajuste, en_pedido: r.en_pedido, no_imprimir: r.no_imprimir }))
  };
}

function vaRenderTodo(){
  vaRenderKpis();
  vaRenderAvisos();
  if(vaTab === 'fosas'){ vaRenderFosas(); vaRenderResumen(); vaRenderOtras(); }
  else if(vaTab === 'balance'){ vaRenderHoyo(); vaRenderBalance(); vaRenderPerdidas(); }
  else { vaRenderInventario(); vaRenderCostos(); }
  if(ivVista === 'concentracion') vaRenderConcentracion();
}

function vaCambiarTab(tab){
  vaTab = tab;
  document.querySelectorAll('[data-va-tab]').forEach(b => b.classList.toggle('is-active', b.dataset.vaTab === tab));
  document.getElementById('vaPanelFosas').hidden = tab !== 'fosas';
  document.getElementById('vaPanelBalance').hidden = tab !== 'balance';
  document.getElementById('vaPanelInventario').hidden = tab !== 'inventario';
  vaRenderTodo();
}

/* ---------- Cálculos en vivo del cierre ---------- */

function vaFluidoHoyo(){
  const h = vaDatos.hoyo;
  return ['anular', 'sarta', 'bajo_mecha'].reduce((a, k) => a + Math.max((h.volumen[k] || 0) - (csNum(h.no_fluido[k]) || 0), 0), 0);
}

function vaCierre(){
  // Real y no contabilizado por grupo con lo que está escrito en pantalla.
  const out = {};
  VA_GRUPOS.forEach(g => {
    const srv = vaDatos.grupos.find(x => x.grupo === g) || { calculado: 0 };
    const miembros = vaDatos.fosas.filter(f => vaGrupoDeTipo(f._tipo_guardado) === g);
    const sin = miembros.filter(f => csNum(f.real) === null).map(f => f.descripcion);
    let real = miembros.reduce((a, f) => a + (csNum(f.real) || 0), 0);
    if(g === 'ACTIVO') real += vaFluidoHoyo();
    out[g] = { calculado: srv.calculado, real: sin.length ? null : real, sin,
               na: sin.length ? null : real - srv.calculado, tiene: miembros.length > 0 };
  });
  return out;
}

/* ---------- KPIs y avisos ---------- */

function vaRenderKpis(){
  const c = vaCierre();
  const chip = (g, nombre) => {
    const x = c[g];
    if(!x.tiene) return '';
    let clase = 'va-kpi-ok', valor = '0,00 bbl', nota = 'Cuadra';
    if(x.na === null){ clase = 'va-kpi-pendiente'; valor = '—'; nota = `Falta el volumen real de ${x.sin.length} fosa(s)`; }
    else if(Math.abs(x.na) >= 0.005){ clase = 'va-kpi-error'; valor = `${csFmt(x.na)} bbl`; nota = x.na > 0 ? 'Sobra fluido real' : 'Falta fluido real'; }
    return `<div class="va-kpi ${clase}"><span>No contabilizado · ${nombre}</span><strong>${valor}</strong><small>${nota}</small></div>`;
  };
  const act = c.ACTIVO;
  document.getElementById('vaKpis').innerHTML =
    chip('ACTIVO', 'Sistema activo') + chip('RESERVA', 'Reserva') + chip('PREMEZCLA', 'Premezcla') +
    `<div class="va-kpi va-kpi-neutro"><span>Sistema activo calculado</span><strong>${csFmt(act.calculado)} bbl</strong><small>real: ${act.real === null ? '—' : csFmt(act.real) + ' bbl'}</small></div>` +
    `<div class="va-kpi va-kpi-neutro"><span>Fluido en el hoyo</span><strong>${csFmt(vaFluidoHoyo())} bbl</strong><small>de ${csFmt(vaDatos.hoyo.total_volumen)} bbl de hoyo (pestaña 4)</small></div>`;
}

function vaRenderAvisos(){
  const avisos = (vaDatos.avisos || []).slice();
  if(!vaDatos.fosas.length) avisos.push('El pozo no tiene fosas. Agrégalas en la configuración de fosas del pozo.');
  vaDatos.fosas.forEach(f => {
    const r = csNum(f.real);
    if(r !== null && f.capacidad > 0 && r > f.capacidad + 0.005) avisos.push(`${csEsc(f.descripcion)}: el volumen real (${csFmt(r)}) supera la capacidad (${csFmt(f.capacidad)}).`);
    if(r !== null && r > 0 && vaGrupoDeTipo(f.tipo_codigo) === null) avisos.push(`${csEsc(f.descripcion)} tiene volumen pero no tiene tipo (o es "Vacía"): no entra en ningún grupo del balance.`);
  });
  if(vaTiposCambiados) avisos.push('Cambiaste el tipo de alguna fosa: guarda la volumetría para recalcular los grupos.');
  document.getElementById('vaAvisos').innerHTML = avisos.map(a => `<div class="cs-aviso-item">${a}</div>`).join('');
}

/* ---------- Volúmenes de fosas ---------- */

function vaRenderFosas(){
  const tbody = document.getElementById('vaFilasFosas');
  if(!vaDatos.fosas.length){
    tbody.innerHTML = `<tr class="cs-fila-vacia"><td colspan="9">El pozo no tiene fosas. <a href="${vaDatos.enlaces.fosas}" target="_blank" rel="noopener">Configurarlas &rarr;</a></td></tr>`;
    return;
  }
  const opciones = (sel) => '<option value="">— Sin tipo —</option>' + vaDatos.tipos_fosa.map(t =>
    `<option value="${t.codigo}" ${Number(sel) === t.codigo && sel !== null && sel !== '' ? 'selected' : ''}>${csEsc(t.descripcion)}</option>`).join('');
  tbody.innerHTML = vaDatos.fosas.map(f => {
    const g = vaGrupoDeTipo(f._tipo_guardado);
    const r = csNum(f.real);
    const pct = f.capacidad > 0 && r !== null ? Math.min(r / f.capacidad * 100, 100) : 0;
    const calc = g === 'ACTIVO' ? '<span class="cs-tenue" title="Se calcula en el sistema activo, junto con el hoyo">en el sistema</span>' : (f.calculado === null ? '—' : csFmt(f.calculado));
    return `<tr class="va-fila-${(g || 'ninguno').toLowerCase()}">
      <td><span class="va-punto va-grupo-${(g || 'ninguno').toLowerCase()}"></span>${csEsc(f.descripcion)}${f.en_pozo ? '' : ' <span class="cs-tenue">(ya no está en el pozo)</span>'}</td>
      <td class="cs-num">${csFmt(f.capacidad, 0)}</td>
      <td><select class="report-input va-input va-select-tipo" data-fosa="${f.numero}" data-campo="tipo_codigo">${opciones(f.tipo_codigo)}</select></td>
      <td class="cs-num">${f.inicio === null ? '—' : csFmt(f.inicio)}</td>
      <td class="cs-num">${calc}</td>
      <td class="cs-num"><input type="number" class="cs-input-cant va-input va-input-vol" min="0" step="any" data-fosa="${f.numero}" data-campo="real" value="${f.real ?? ''}" placeholder="—"></td>
      <td class="va-col-llenado"><div class="tt-mini-barra"><span class="tt-mini-relleno va-relleno" data-fosa-barra="${f.numero}" style="width:${pct}%"></span></div></td>
      <td class="cs-num"><input type="number" class="cs-input-cant va-input" min="0" step="0.1" data-fosa="${f.numero}" data-campo="peso" value="${f.peso ?? ''}"></td>
      <td class="cs-num"><input type="number" class="cs-input-cant va-input" step="1" data-fosa="${f.numero}" data-campo="temperatura" value="${f.temperatura ?? ''}"></td>
    </tr>`;
  }).join('');
}

function vaRenderResumen(){
  const c = vaCierre();
  const na = (x) => x.na === null ? `<span class="cs-tenue" title="Falta el volumen real de: ${csEsc(x.sin.join(', '))}">falta real</span>`
    : `<span class="${Math.abs(x.na) < 0.005 ? 'va-ok' : 'va-error'}">${csFmt(x.na)}</span>`;
  const real = (x) => x.real === null ? '—' : csFmt(x.real);
  const act = c.ACTIVO;
  const realPits = vaDatos.fosas.filter(f => vaGrupoDeTipo(f._tipo_guardado) === 'ACTIVO').reduce((a, f) => a + (csNum(f.real) || 0), 0);
  let html = '';
  if(c.RESERVA.tiene) html += `<tr><td>Fosas de reserva</td><td class="cs-num">${csFmt(c.RESERVA.calculado)}</td><td class="cs-num">${real(c.RESERVA)}</td><td class="cs-num">${na(c.RESERVA)}</td></tr>`;
  if(c.PREMEZCLA.tiene) html += `<tr><td>Fosas de premezcla</td><td class="cs-num">${csFmt(c.PREMEZCLA.calculado)}</td><td class="cs-num">${real(c.PREMEZCLA)}</td><td class="cs-num">${na(c.PREMEZCLA)}</td></tr>`;
  html += `<tr class="va-fila-sub"><td>Fosas activas (sin hoyo)</td><td></td><td class="cs-num">${csFmt(realPits)}</td><td></td></tr>`;
  html += `<tr class="va-fila-sub"><td>Fluido en el hoyo</td><td></td><td class="cs-num">${csFmt(vaFluidoHoyo())}</td><td></td></tr>`;
  html += `<tr class="cs-fila-total"><td>Sistema activo (con hoyo)</td><td class="cs-num">${csFmt(act.calculado)}</td><td class="cs-num">${real(act)}</td><td class="cs-num">${na(act)}</td></tr>`;
  document.getElementById('vaResumen').innerHTML = html;
}

function vaRenderOtras(){
  const cont = document.getElementById('vaOtras');
  const filas = vaDatos.otras_por_tipo || [];
  cont.innerHTML = filas.length
    ? `<ul class="cs-almacen">${filas.map(o => `<li><span class="cs-almacen-texto">${csEsc(o.tipo)}</span><strong>${csFmt(o.volumen)} bbl</strong></li>`).join('')}</ul>`
    : '<div class="cs-vacio">No hay fosas de otros tipos (fluido base, salmuera, píldora, espaciador...).</div>';
}

/* ---------- Balance ---------- */

function vaRenderHoyo(){
  const h = vaDatos.hoyo;
  const ks = ['anular', 'sarta', 'bajo_mecha'];
  const inp = k => `<input type="number" class="cs-input-cant va-input" min="0" step="any" data-hoyo="${k}" value="${h.no_fluido[k] || ''}" placeholder="0">`;
  const fl = k => Math.max((h.volumen[k] || 0) - (csNum(h.no_fluido[k]) || 0), 0);
  document.getElementById('vaHoyo').innerHTML = `
    <tr><td>Volumen del hoyo</td>${ks.map(k => `<td class="cs-num">${csFmt(h.volumen[k])}</td>`).join('')}<td class="cs-num cs-final">${csFmt(h.total_volumen)}</td></tr>
    <tr><td>No ocupado por fluido</td>${ks.map(k => `<td class="cs-num">${inp(k)}</td>`).join('')}<td class="cs-num" id="vaHoyoNoFluido">${csFmt(ks.reduce((a, k) => a + (csNum(h.no_fluido[k]) || 0), 0))}</td></tr>
    <tr class="cs-fila-total"><td>Fluido en el hoyo</td>${ks.map(k => `<td class="cs-num" data-hoyo-fluido="${k}">${csFmt(fl(k))}</td>`).join('')}<td class="cs-num" id="vaHoyoFluido">${csFmt(vaFluidoHoyo())}</td></tr>`;
}

function vaRenderBalance(){
  const G = VA_GRUPOS.map(g => vaDatos.grupos.find(x => x.grupo === g) || { flujos: {}, inicio: 0, calculado: 0 });
  const c = vaCierre();
  const v = (g, k) => (g.flujos[k] || 0);
  const fila = (etq, fn, clase = '') => {
    const vals = G.map(fn);
    const total = vals.reduce((a, x) => a + (x || 0), 0);
    return `<tr class="${clase}"><td>${etq}</td>${vals.map(x => `<td class="cs-num">${vaCant(x)}</td>`).join('')}<td class="cs-num cs-final">${vaCant(total)}</td></tr>`;
  };
  const construido = g => v(g, 'aceite') + v(g, 'agua') + v(g, 'quimicos');
  const reales = VA_GRUPOS.map(g => c[g].real);
  const nas = VA_GRUPOS.map(g => c[g].na);
  const filaNullable = (etq, vals, clase) => {
    const total = vals.some(x => x === null) ? null : vals.reduce((a, x) => a + x, 0);
    const celda = x => x === null ? '<span class="cs-tenue">—</span>' : csFmt(x);
    return `<tr class="${clase}"><td>${etq}</td>${vals.map(x => `<td class="cs-num">${celda(x)}</td>`).join('')}<td class="cs-num cs-final">${celda(total)}</td></tr>`;
  };
  document.getElementById('vaBalance').innerHTML =
    fila('Volumen inicial', g => g.inicio, 'va-fila-base') +
    fila('Fluido base agregado', g => v(g, 'aceite')) +
    fila('Agua agregada', g => v(g, 'agua')) +
    fila('Volumen de químicos agregados', g => v(g, 'quimicos')) +
    fila('Total construido', construido, 'va-fila-sub') +
    fila('Lodo entero recibido', g => v(g, 'recibido')) +
    fila('Devuelto', g => -v(g, 'devuelto')) +
    fila('Transferido desde otros grupos', g => v(g, 'entra')) +
    fila('Transferido a otros grupos', g => -v(g, 'sale')) +
    fila('Pérdidas y descartes', g => -v(g, 'perdida')) +
    fila('Volumen final calculado', g => g.calculado, 'cs-fila-total') +
    filaNullable('Volumen final real', reales, 'va-fila-base') +
    filaNullable('No contabilizado', nas, 'va-fila-na');
}

function vaRenderPerdidas(){
  const filas = vaDatos.perdidas;
  document.getElementById('vaPerdidas').innerHTML = filas.length ? filas.map(p => `
    <tr>
      <td><span class="cs-codigo">${p.codigo}</span> · ${csEsc(p.descripcion)} <span class="iv-item-tipo iv-tipo-${p.tipo.toLowerCase()}">${csEsc(p.tipo_display)}</span></td>
      <td class="cs-num">${vaCant(p.por_grupo.ACTIVO)}</td>
      <td class="cs-num">${vaCant(p.por_grupo.RESERVA)}</td>
      <td class="cs-num">${vaCant(p.por_grupo.PREMEZCLA)}</td>
      <td class="cs-num cs-final">${vaCant(p.subtotal)}</td>
      <td class="cs-num ${p.descargado && Math.abs(p.descargado - p.subtotal) > 0.05 ? 'va-dif' : ''}">${vaCant(p.descargado)}</td>
    </tr>`).join('') : '<tr class="cs-fila-vacia"><td colspan="6">No hay categorías de pérdida.</td></tr>';
  const t = vaDatos.perdidas_totales;
  document.getElementById('vaPerdidasPie').innerHTML = `
    <tr class="cs-fila-total cs-fila-subtotal"><td colspan="4">Pérdida de subsuelo</td><td class="cs-num">${csFmt(t.subsuelo)}</td><td></td></tr>
    <tr class="cs-fila-total cs-fila-subtotal"><td colspan="4">Pérdida de superficie</td><td class="cs-num">${csFmt(t.superficie)}</td><td></td></tr>
    <tr class="cs-fila-total"><td colspan="4">Pérdida total</td><td class="cs-num">${csFmt(t.total)}</td><td></td></tr>`;
}

/* ---------- Inventario ---------- */

function vaFinalVivo(r){
  if(r.servicio) return 0;
  return r.final - (csNum(r.usado_otro) || 0) + r._otro_guardado + (csNum(r.ajuste) || 0) - r._ajuste_guardado;
}

function vaCostoVivo(r){
  return r.costo_diario + ((csNum(r.usado_otro) || 0) - r._otro_guardado) * r.precio;
}

function vaRenderInventario(){
  const solo = document.getElementById('vaSoloMovimiento').checked;
  const filas = vaDatos.inventario.filter(r => !solo || r.inicial || r.final || r.usado_dia || r.recibido || r.devuelto || csNum(r.usado_otro) || r.costo_acumulado);
  const tbody = document.getElementById('vaFilasInv');
  if(!filas.length){
    tbody.innerHTML = `<tr class="cs-fila-vacia"><td colspan="17">${vaDatos.inventario.length ? 'Ningún producto con existencia o movimiento.' : `El pozo no tiene productos activos. <a href="${vaDatos.enlaces.productos}" target="_blank" rel="noopener">Agrégalos &rarr;</a>`}</td></tr>`;
    return;
  }
  tbody.innerHTML = filas.map(r => {
    const id = r.producto_id;
    const dif = (a, b) => Math.abs(a - b) > 1e-6;
    return `<tr class="${r.activo ? '' : 'cs-fila-inactiva'} ${r.no_imprimir ? 'va-no-imprimir' : ''}">
      <td class="cs-codigo">${csEsc(r.codigo)}</td>
      <td>${csEsc(r.descripcion)}${r.servicio ? ' <span class="va-chip-servicio">Servicio</span>' : ''}</td>
      <td>${csEsc(r.unidad ? `${r.tamano ? csFmt(r.tamano, r.tamano % 1 ? 2 : 0) + ' ' : ''}${r.unidad}` : '—')}${r.empaque ? ` <span class="cs-tenue">${csEsc(r.empaque)}</span>` : ''}</td>
      <td class="cs-num">${csDinero(r.precio)}</td>
      <td class="cs-num cs-grupo-nuevas">${vaCant(r.inicial)}</td>
      <td class="cs-num cs-grupo-nuevas cs-mas" ${dif(r.recibido, r.recibido_ticket) ? `title="Según ticket: ${csFmt(r.recibido_ticket)}"` : ''}>${vaCant(r.recibido)}${dif(r.recibido, r.recibido_ticket) ? ' <span class="cs-dif-chip">≠ ticket</span>' : ''}</td>
      <td class="cs-num cs-grupo-nuevas cs-menos">${vaCant(r.devuelto)}</td>
      <td class="cs-num cs-grupo-nuevas cs-menos">${vaCant(r.usado_fluido)}</td>
      <td class="cs-num cs-grupo-nuevas"><input type="number" class="cs-input-cant va-input" min="0" step="any" data-inv="${id}" data-campo="usado_otro" value="${r.usado_otro || ''}" placeholder="0"></td>
      <td class="cs-num cs-grupo-nuevas"><input type="number" class="cs-input-cant va-input" step="any" data-inv="${id}" data-campo="ajuste" value="${r.ajuste || ''}" placeholder="0" ${r.servicio ? 'disabled title="Los servicios no llevan existencias"' : ''}></td>
      <td class="cs-num cs-grupo-nuevas cs-final" data-inv-final="${id}">${r.servicio ? '—' : csFmt(vaFinalVivo(r))}</td>
      <td class="cs-num cs-grupo-costos" data-inv-usado="${id}">${vaCant(r.usado_fluido + (csNum(r.usado_otro) || 0))}</td>
      <td class="cs-num cs-grupo-costos cs-final" data-inv-costo="${id}">${csDinero(vaCostoVivo(r))}</td>
      <td class="cs-num cs-grupo-costos">${csDinero(r.costo_acumulado - r.costo_diario + vaCostoVivo(r))}</td>
      <td class="cs-num">${r.peso_lb === null ? '—' : csFmt(r.peso_lb, 0)}</td>
      <td class="cs-num"><input type="number" class="cs-input-cant va-input" min="0" step="any" data-inv="${id}" data-campo="en_pedido" value="${r.en_pedido || ''}" placeholder="0"></td>
      <td class="cs-centro"><input type="checkbox" class="va-input" data-inv="${id}" data-campo="no_imprimir" ${r.no_imprimir ? 'checked' : ''}></td>
    </tr>`;
  }).join('');
}

function vaRenderCostos(){
  let diario = 0, acum = 0;
  const vivo = {};
  vaDatos.inventario.forEach(r => { vivo[r.categoria] = (vivo[r.categoria] || 0) + (vaCostoVivo(r) - r.costo_diario); });
  document.getElementById('vaCostos').innerHTML = vaDatos.costos.map(c => {
    const d = c.diario + (vivo[c.categoria] || 0);
    const a = c.acumulado + (vivo[c.categoria] || 0);
    diario += d; acum += a;
    return `<tr><td>${csEsc(c.nombre)}</td><td class="cs-num">${csDinero(d)}</td><td class="cs-num">${csDinero(a)}</td></tr>`;
  }).join('');
  document.getElementById('vaCostosPie').innerHTML = `<tr class="cs-fila-total"><td>Subtotal (${csEsc(vaDatos.moneda)})</td><td class="cs-num">${csDinero(diario)}</td><td class="cs-num">${csDinero(acum)}</td></tr>`;
  document.getElementById('vaDatosInv').innerHTML = `
    <div class="cs-eq-dato"><span>Peso de químicos en inventario</span><strong>${csFmt(vaDatos.peso_quimicos_lb, 0)} lb</strong></div>
    <div class="cs-eq-dato"><span>Volumen de químicos para fluidos (hoy)</span><strong>${csFmt(vaDatos.volumen_quimicos_bbl)} bbl</strong></div>`;
  document.getElementById('vaUltimosTickets').innerHTML = vaDatos.ultimos_tickets.map(t =>
    `<div class="cs-eq-dato"><span>${csEsc(t.tipo)}</span><strong>${t.numero ? csEsc(t.numero) : '—'}</strong></div>`).join('');
}

/* ---------- Concentración ---------- */

function vaRenderConcentracion(){
  const sel = document.getElementById('vaConcFosa');
  const lista = vaDatos.concentraciones;
  const actual = sel.value;
  sel.innerHTML = lista.length ? lista.map(c => `<option value="${c.clave}" ${c.clave === actual ? 'selected' : ''}>${csEsc(c.etiqueta)}</option>`).join('') : '<option value="">Sin datos</option>';
  const c = lista.find(x => x.clave === sel.value) || lista[0];
  const cont = document.getElementById('vaConcentracion');
  if(!c){
    cont.innerHTML = '<div class="cs-vacio">Todavía no hay productos con concentración. Aparecen al agregar químicos medidos en peso o lodo entero con su concentración.</div>';
    return;
  }
  cont.innerHTML = `
    <div class="va-datos va-datos-fila">
      <div class="cs-eq-dato"><span>Volumen inicial</span><strong>${csFmt(c.vol_inicio)} bbl</strong></div>
      <div class="cs-eq-dato"><span>Volumen final calculado</span><strong>${csFmt(c.vol_fin)} bbl</strong></div>
    </div>
    <div class="cs-tabla-wrapper">
      <table class="cs-tabla">
        <thead><tr><th>Producto</th><th>Código</th><th class="cs-num">Inicial (lb/bbl)</th><th class="cs-num">Final (lb/bbl)</th><th class="cs-num">Cambio</th></tr></thead>
        <tbody>${c.productos.map(p => {
          const d = p.fin - p.inicio;
          return `<tr><td>${csEsc(p.descripcion)}</td><td class="cs-codigo">${csEsc(p.codigo)}</td>
            <td class="cs-num">${vaCant(p.inicio, 3)}</td><td class="cs-num cs-final">${vaCant(p.fin, 3)}</td>
            <td class="cs-num ${d > 0.0005 ? 'cs-mas' : (d < -0.0005 ? 'cs-menos' : '')}">${Math.abs(d) < 0.0005 ? '—' : (d > 0 ? '+' : '') + csFmt(d, 3)}</td></tr>`;
        }).join('')}</tbody>
      </table>
    </div>`;
}

/* ---------- Guardar ---------- */

async function guardarVolumetria(silent = false){
  if(!vaListo){
    if(!silent) showToast('La volumetría todavía no terminó de cargar.', false);
    return;
  }
  try {
    const res = await fetch(VA_BASE + 'guardar/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify(vaCapturar())
    });
    const data = await res.json();
    if(data.ok){
      vaAplicar(data, false);
      if(!silent) showToast(data.mensaje || 'Volumetría guardada.');
    } else {
      showToast(data.error || 'No se pudo guardar la volumetría.', false);
    }
  } catch(e){
    showToast('Error de conexión al guardar la volumetría.', false);
  }
}

/* =====================================================================
   MODALES: químicos, lodo entero, transferencia/pérdida, movimientos, tickets
   ===================================================================== */

function vaFosasConTipo(){
  return vaDatos.fosas.filter(f => vaGrupoDeTipo(f._tipo_guardado) !== null && f.en_pozo);
}

function vaOpcionesFosa(seleccion){
  const fs = vaFosasConTipo();
  if(!fs.length) return '<option value="">No hay fosas con tipo asignado</option>';
  return fs.map(f => `<option value="${f.numero}" ${f.numero === seleccion ? 'selected' : ''}>${csEsc(f.descripcion)} — ${csEsc(f.tipo_descripcion || vaDatos.tipos_fosa.find(t => t.codigo === f._tipo_guardado)?.descripcion || '')}</option>`).join('');
}

function vaOpcionesDestinoExterno(){
  return '<option value="">Elige…</option>' +
    vaDatos.almacenes.map(a => `<option value="Almacén ${csEsc(a.codigo)} — ${csEsc(a.nombre)}">Almacén ${csEsc(a.codigo)} — ${csEsc(a.nombre)}</option>`).join('') +
    `<option value="${VA_OTRO_DESTINO}">${VA_OTRO_DESTINO}</option>`;
}

function vaAbrirModal(tipo){
  if(!vaDatos) return;
  if(vaSucio && ['quimicos', 'lodo', 'transferencia'].includes(tipo) && vaTiposCambiados){
    showToast('Guarda primero los cambios de tipo de fosa: los movimientos usan los tipos guardados.', false);
    return;
  }
  vaModalTipo = tipo;
  if(tipo === 'tickets') vaTicketSel = vaDatos.tickets.length ? vaDatos.tickets[0].id : null;
  document.getElementById('vaModal').hidden = false;
  vaRenderModal(true);
}

function vaCerrarModal(){
  document.getElementById('vaModal').hidden = true;
  vaModalTipo = null;
}

function vaRenderModal(inicial = false){
  const titulo = document.getElementById('vaModalTitulo');
  const sub = document.getElementById('vaModalSubtitulo');
  const cuerpo = document.getElementById('vaModalCuerpo');
  const pie = document.getElementById('vaModalPie');
  sub.textContent = `Reporte del ${vaDatos.fecha}`;
  const caja = document.querySelector('.va-modal-caja');
  caja.classList.toggle('va-modal-ancho', ['quimicos', 'lodo', 'tickets'].includes(vaModalTipo));

  if(vaModalTipo === 'quimicos'){
    if(!inicial) return;
    titulo.textContent = 'Agregar químicos a una fosa';
    const prods = vaDatos.inventario.filter(r => r.activo && !r.servicio);
    cuerpo.innerHTML = `
      <div class="va-form-fila">
        <label class="cs-campo"><span class="cs-campo-label">1. Fosa</span><select id="vaQFosa" class="report-input">${vaOpcionesFosa()}</select></label>
        <label class="cs-campo"><span class="cs-campo-label">2. Fluido base agregado <em>(bbl)</em></span><input type="number" id="vaQAceite" class="report-input" min="0" step="any"></label>
        <label class="cs-campo"><span class="cs-campo-label">Agua agregada <em>(bbl)</em></span><input type="number" id="vaQAgua" class="report-input" min="0" step="any"></label>
        <label class="cs-campo"><span class="cs-campo-label">Buscar producto</span><input type="search" id="vaQBuscar" class="report-input" placeholder="Código o descripción"></label>
      </div>
      <div class="cs-tabla-wrapper va-tabla-scroll">
        <table class="cs-tabla">
          <thead><tr><th>Código</th><th>Descripción</th><th>Unidad</th><th class="cs-num">Disponible</th><th class="cs-num">3. Cantidad</th><th class="cs-num">Volumen (bbl)</th></tr></thead>
          <tbody id="vaQFilas">${prods.map(r => `
            <tr data-buscar="${csEsc((r.codigo + ' ' + r.descripcion).toLowerCase())}">
              <td class="cs-codigo">${csEsc(r.codigo)}</td><td>${csEsc(r.descripcion)}</td>
              <td>${csEsc(r.unidad ? `${r.tamano ? csFmt(r.tamano, r.tamano % 1 ? 2 : 0) + ' ' : ''}${r.unidad}` : '—')}</td>
              <td class="cs-num ${r.final <= 0 ? 'cs-agotado' : ''}">${csFmt(r.final)}</td>
              <td class="cs-num"><input type="number" class="cs-input-cant va-q-cant" min="0" step="any" data-prod="${r.producto_id}" placeholder="0"></td>
              <td class="cs-num" data-q-vol="${r.producto_id}">—</td>
            </tr>`).join('') || '<tr class="cs-fila-vacia"><td colspan="6">No hay productos activos que se agreguen a fosas.</td></tr>'}</tbody>
        </table>
      </div>
      <div class="va-resumen-mov" id="vaQResumen"></div>
      <p class="cs-nota">Solo aportan volumen los productos medidos en peso (lb, kg, t), con su gravedad específica. El fluido base y el agua se escriben arriba en bbl.</p>`;
    pie.innerHTML = `<span class="cs-flex"></span><button type="button" class="btn-modern-secondary btn-sm" data-va-cerrar>Cancelar</button>
      <button type="button" class="btn-modern-primary btn-sm" id="vaQRegistrar"><span>&#10004;</span><span>Registrar químicos</span></button>`;
    vaQRecalcular();

  } else if(vaModalTipo === 'lodo'){
    if(!inicial) return;
    titulo.textContent = 'Agregar lodo entero a una fosa';
    const prods = vaDatos.inventario.filter(r => r.activo && !r.servicio);
    const lodos = prods.slice().sort((a, b) => ((b.unidad || '').toUpperCase().startsWith('B') ? 1 : 0) - ((a.unidad || '').toUpperCase().startsWith('B') ? 1 : 0));
    const conc = prods.filter(r => r.concentracion && vaMasaLb(1, r.unidad, r.tamano) !== null);
    cuerpo.innerHTML = `
      <div class="va-grid-2 va-grid-lodo">
        <div>
          <label class="cs-campo"><span class="cs-campo-label">1. Fosa</span><select id="vaLFosa" class="report-input">${vaOpcionesFosa()}</select></label>
          <label class="cs-campo"><span class="cs-campo-label">2. Producto de lodo entero</span><select id="vaLProducto" class="report-input">
            <option value="">Elige…</option>${lodos.map(r => `<option value="${r.producto_id}">${csEsc(r.descripcion)} (${csEsc(r.codigo)}) — ${csFmt(r.final)} ${csEsc(r.unidad || '')} disponibles</option>`).join('')}</select>
            <small class="cs-campo-ayuda">Se descuenta del inventario el volumen agregado.</small></label>
          <label class="cs-campo"><span class="cs-campo-label">3. Recibido de</span><select id="vaLOrigen" class="report-input">${vaOpcionesDestinoExterno()}</select></label>
          <div class="va-form-fila">
            <label class="cs-campo"><span class="cs-campo-label">4. Volumen <em>(bbl)</em></span><input type="number" id="vaLVolumen" class="report-input" min="0" step="any"></label>
            <label class="cs-campo"><span class="cs-campo-label">Peso del lodo <em>(lb/gal)</em></span><input type="number" id="vaLPeso" class="report-input" min="0" step="0.1"></label>
          </div>
        </div>
        <div>
          <div class="cs-subtitulo">5. Concentración de productos en el lodo (lb/bbl)</div>
          <div class="cs-tabla-wrapper va-tabla-scroll">
            <table class="cs-tabla">
              <thead><tr><th>Producto</th><th class="cs-num">lb/bbl</th></tr></thead>
              <tbody>${conc.map(r => `<tr><td>${csEsc(r.descripcion)} <span class="cs-tenue">${csEsc(r.codigo)}</span></td>
                <td class="cs-num"><input type="number" class="cs-input-cant va-l-conc" min="0" step="any" data-prod="${r.producto_id}" placeholder="0"></td></tr>`).join('') || '<tr class="cs-fila-vacia"><td colspan="2">Ningún producto activo calcula concentración.</td></tr>'}</tbody>
            </table>
          </div>
          <p class="cs-nota">Opcional: solo sirve para la concentración de productos del sistema.</p>
        </div>
      </div>`;
    pie.innerHTML = `<span class="cs-flex"></span><button type="button" class="btn-modern-secondary btn-sm" data-va-cerrar>Cancelar</button>
      <button type="button" class="btn-modern-primary btn-sm" id="vaLRegistrar"><span>&#10004;</span><span>Registrar lodo entero</span></button>`;

  } else if(vaModalTipo === 'transferencia'){
    if(!inicial) return;
    titulo.textContent = 'Transferencia, devolución o pérdida';
    cuerpo.innerHTML = `
      <div class="cs-condicion va-opciones" role="radiogroup">
        <button type="button" class="cs-condicion-btn is-active" data-va-op="TRANSFERENCIA">Entre fosas</button>
        <button type="button" class="cs-condicion-btn" data-va-op="DEVOLUCION">Devolución</button>
        <button type="button" class="cs-condicion-btn" data-va-op="PERDIDA">Pérdida y descarte</button>
      </div>
      <div class="va-form-col">
        <label class="cs-campo"><span class="cs-campo-label">Fosa de origen</span><select id="vaTFosa" class="report-input">${vaOpcionesFosa()}</select></label>
        <label class="cs-campo" id="vaTCampoDestino"><span class="cs-campo-label">Fosa destino</span><select id="vaTDestino" class="report-input">${vaOpcionesFosa()}</select></label>
        <label class="cs-campo" id="vaTCampoDevuelto" hidden><span class="cs-campo-label">Devuelto a</span><select id="vaTDevuelto" class="report-input">${vaOpcionesDestinoExterno()}</select></label>
        <label class="cs-campo" id="vaTCampoPerdida" hidden><span class="cs-campo-label">Tipo de pérdida</span><select id="vaTPerdida" class="report-input">
          <option value="">Elige…</option>${vaDatos.categorias_perdida.map(c => {
            const d = vaDatos.descarga_equipos[String(c.codigo)];
            return `<option value="${c.codigo}">${c.codigo} · ${csEsc(c.descripcion)}${d ? ` — equipos: ${csFmt(d)} bbl` : ''}</option>`;
          }).join('')}</select>
          <small class="cs-campo-ayuda" id="vaTAyudaPerdida">Si la pestaña 6 calculó lodo perdido para esta categoría, se sugiere ese volumen.</small></label>
        <label class="cs-campo"><span class="cs-campo-label">Volumen <em>(bbl)</em></span><input type="number" id="vaTVolumen" class="report-input" min="0" step="any"></label>
      </div>`;
    cuerpo.dataset.op = 'TRANSFERENCIA';
    pie.innerHTML = `<span class="cs-flex"></span><button type="button" class="btn-modern-secondary btn-sm" data-va-cerrar>Cancelar</button>
      <button type="button" class="btn-modern-primary btn-sm" id="vaTRegistrar"><span>&#10004;</span><span>Registrar</span></button>`;

  } else if(vaModalTipo === 'movimientos'){
    titulo.textContent = 'Movimientos de fluidos del día';
    const u = vaDatos.ultima_transaccion;
    cuerpo.innerHTML = vaDatos.movimientos.length ? `<ol class="va-log">${vaDatos.movimientos.map(m => `
      <li><span class="va-log-num">${m.secuencia}</span>
        <div><span class="cs-accion-chip va-mov-${m.tipo.toLowerCase()}">${csEsc(m.tipo_display)}</span> ${csEsc(m.titulo)}
          ${m.lineas.length ? `<ul>${m.lineas.map(l => `<li>${csEsc(l)}</li>`).join('')}</ul>` : ''}</div></li>`).join('')}</ol>`
      : '<div class="cs-vacio">Sin movimientos en este reporte.</div>';
    const nota = !u ? '' : (u.es_de_este_reporte ? `Deshace el movimiento #${u.secuencia}, el último del pozo.` : `El último movimiento del pozo (#${u.secuencia}) es del ${u.fecha}; solo se deshace desde ese reporte.`);
    pie.innerHTML = `<span class="cs-nota va-pie-nota">${nota}</span><span class="cs-flex"></span>
      <button type="button" class="btn-modern-secondary btn-sm" id="vaDeshacer" ${u && u.es_de_este_reporte ? '' : 'disabled'}><span>&#8630;</span><span>Deshacer último</span></button>
      <button type="button" class="btn-modern-secondary btn-sm" onclick="window.print()"><span>&#128438;</span><span>Imprimir</span></button>`;

  } else if(vaModalTipo === 'tickets'){
    titulo.textContent = 'Tickets de entrega y devolución de productos';
    vaRenderTickets();
  }
}

function vaQRecalcular(){
  let vq = 0, costo = 0;
  document.querySelectorAll('.va-q-cant').forEach(el => {
    const r = vaDatos.inventario.find(x => x.producto_id === Number(el.dataset.prod));
    const cant = csNum(el.value) || 0;
    const v = r ? vaVolumenQuimico(cant, r.unidad, r.tamano, r.gravedad) : 0;
    vq += v;
    costo += r ? cant * r.precio : 0;
    const celda = document.querySelector(`[data-q-vol="${el.dataset.prod}"]`);
    if(celda) celda.textContent = cant ? csFmt(v, 2) : '—';
    el.classList.toggle('cs-dif', !!r && cant > r.final + 1e-6);
  });
  const aceite = csNum(document.getElementById('vaQAceite')?.value) || 0;
  const agua = csNum(document.getElementById('vaQAgua')?.value) || 0;
  const res = document.getElementById('vaQResumen');
  if(res) res.innerHTML = `
    <div class="cs-resultado"><span>Volumen de químicos</span><strong>${csFmt(vq)} <em>bbl</em></strong></div>
    <div class="cs-resultado"><span>Volumen total agregado</span><strong>${csFmt(vq + aceite + agua)} <em>bbl</em></strong></div>
    <div class="cs-resultado"><span>Costo de los productos</span><strong>${csDinero(costo)}</strong></div>`;
}

async function vaRegistrarQuimicos(){
  const productos = [];
  document.querySelectorAll('.va-q-cant').forEach(el => { if(csNum(el.value)) productos.push({ producto_id: Number(el.dataset.prod), cantidad: el.value }); });
  const data = await vaPost('transaccion/', {
    tipo: 'QUIMICOS', fosa: document.getElementById('vaQFosa').value,
    aceite: document.getElementById('vaQAceite').value, agua: document.getElementById('vaQAgua').value, productos
  });
  if(data) vaCerrarModal();
}

async function vaRegistrarLodo(){
  const concentraciones = [];
  document.querySelectorAll('.va-l-conc').forEach(el => { if(csNum(el.value)) concentraciones.push({ producto_id: Number(el.dataset.prod), concentracion: el.value }); });
  const data = await vaPost('transaccion/', {
    tipo: 'LODO_ENTERO', fosa: document.getElementById('vaLFosa').value,
    lodo_producto_id: document.getElementById('vaLProducto').value, origen: document.getElementById('vaLOrigen').value,
    volumen: document.getElementById('vaLVolumen').value, peso: document.getElementById('vaLPeso').value, concentraciones
  });
  if(data) vaCerrarModal();
}

function vaCambiarOperacion(op){
  const cuerpo = document.getElementById('vaModalCuerpo');
  cuerpo.dataset.op = op;
  cuerpo.querySelectorAll('[data-va-op]').forEach(b => b.classList.toggle('is-active', b.dataset.vaOp === op));
  document.getElementById('vaTCampoDestino').hidden = op !== 'TRANSFERENCIA';
  document.getElementById('vaTCampoDevuelto').hidden = op !== 'DEVOLUCION';
  document.getElementById('vaTCampoPerdida').hidden = op !== 'PERDIDA';
}

async function vaRegistrarTransferencia(){
  const op = document.getElementById('vaModalCuerpo').dataset.op;
  const payload = { tipo: op, fosa: document.getElementById('vaTFosa').value, volumen: document.getElementById('vaTVolumen').value };
  if(op === 'TRANSFERENCIA') payload.destino = document.getElementById('vaTDestino').value;
  if(op === 'DEVOLUCION') payload.destino_texto = document.getElementById('vaTDevuelto').value;
  if(op === 'PERDIDA') payload.perdida_codigo = document.getElementById('vaTPerdida').value;
  const data = await vaPost('transaccion/', payload);
  if(data) vaCerrarModal();
}

/* ---------- Tickets de productos ---------- */

function vaRenderTickets(){
  const cuerpo = document.getElementById('vaModalCuerpo');
  const pie = document.getElementById('vaModalPie');
  const t = vaDatos.tickets.find(x => x.id === vaTicketSel) || null;
  const porProd = {};
  if(t) t.detalles.forEach(d => { porProd[d.producto_id] = d; });
  const almacen = t ? t.almacen_codigo : '';
  const prods = vaDatos.inventario.filter(r => r.activo && !r.servicio);
  cuerpo.innerHTML = `
    <div class="cs-tk-grid">
      <aside class="cs-tk-lista">
        <button type="button" class="btn-modern-primary btn-sm cs-tk-nuevo" id="vaTkNuevo"><span>&#10133;</span><span>Nuevo ticket</span></button>
        ${vaDatos.tickets.length ? vaDatos.tickets.map(x => `
          <button type="button" class="cs-tk-item ${x.id === vaTicketSel ? 'is-active' : ''}" data-va-ticket="${x.id}">
            <span class="cs-tk-item-tipo cs-sentido-${x.sentido.toLowerCase()}">${csEsc(x.tipo_nombre)}</span>
            <span class="cs-tk-item-num">${x.numero ? 'N° ' + csEsc(x.numero) : 'Sin número'}</span>
            <span class="cs-tk-item-meta">${x.detalles.length} producto(s)${x.tiene_diferencias ? ' <span class="cs-dif-chip">Con diferencias</span>' : ''}</span>
          </button>`).join('') : '<div class="cs-vacio">Sin tickets en este reporte.</div>'}
        <p class="cs-nota">Los tipos de ticket son los mismos de las mallas (pestaña 6 → Tickets → Administrar tipos).</p>
      </aside>
      <section class="cs-tk-form">
        <div class="cs-tk-encabezado">
          <label class="cs-campo"><span class="cs-campo-label">Tipo de ticket</span><select id="vaTkTipo" class="report-input">${vaDatos.tipos_ticket.map(x =>
            `<option value="${x.id}" ${t && t.tipo_id === x.id ? 'selected' : ''}>${csEsc(x.nombre)} — ${x.sentido === 'ENTRADA' ? 'entrada' : 'salida'}</option>`).join('')}</select></label>
          <label class="cs-campo"><span class="cs-campo-label">N° de ticket</span><input type="text" id="vaTkNumero" class="report-input" maxlength="40" value="${t ? csEsc(t.numero) : ''}"></label>
          <label class="cs-campo"><span class="cs-campo-label">Pedido por</span><input type="text" id="vaTkPedido" class="report-input" maxlength="100" value="${t ? csEsc(t.pedido_por) : ''}"></label>
          <label class="cs-campo"><span class="cs-campo-label">Recibido por</span><input type="text" id="vaTkRecibido" class="report-input" maxlength="100" value="${t ? csEsc(t.recibido_por) : ''}"></label>
          <label class="cs-campo"><span class="cs-campo-label">Almacén</span><select id="vaTkAlmacen" class="report-input"><option value="">— Sin almacén —</option>${vaDatos.almacenes.map(a =>
            `<option value="${csEsc(a.codigo)}" ${a.codigo === almacen ? 'selected' : ''}>${csEsc(a.codigo)} — ${csEsc(a.nombre)}</option>`).join('')}</select></label>
          <label class="cs-campo"><span class="cs-campo-label">Buscar producto</span><input type="search" id="vaTkBuscar" class="report-input" placeholder="Código o descripción"></label>
        </div>
        <div class="cs-tabla-wrapper va-tabla-scroll">
          <table class="cs-tabla">
            <thead><tr><th>Producto</th><th>Unidad</th><th class="cs-num">Precio</th><th class="cs-num">Según ticket</th><th class="cs-num">Real</th></tr></thead>
            <tbody id="vaTkFilas">${prods.map(r => {
              const d = porProd[r.producto_id] || {};
              return `<tr data-prod="${r.producto_id}" data-buscar="${csEsc((r.codigo + ' ' + r.descripcion).toLowerCase())}">
                <td>${csEsc(r.descripcion)} <span class="cs-tenue">${csEsc(r.codigo)}</span></td>
                <td>${csEsc(r.unidad || '—')}</td><td class="cs-num">${csDinero(r.precio)}</td>
                <td class="cs-num"><input type="number" class="cs-input-cant va-tk-cant" min="0" step="any" data-campo="cantidad_ticket" value="${d.cantidad_ticket || ''}" placeholder="0"></td>
                <td class="cs-num"><input type="number" class="cs-input-cant va-tk-cant" min="0" step="any" data-campo="cantidad_real" value="${d.cantidad_real || ''}" placeholder="0"></td>
              </tr>`;
            }).join('') || '<tr class="cs-fila-vacia"><td colspan="5">El pozo no tiene productos activos.</td></tr>'}</tbody>
          </table>
        </div>
        <p class="cs-nota">"Según ticket" es lo que dice el papel; "Real" es lo que llegó o salió de verdad. El inventario usa la cantidad real; las diferencias se marcan en ámbar.</p>
      </section>
    </div>`;
  pie.innerHTML = `${t ? '<button type="button" class="btn-modern-secondary btn-sm cs-btn-peligro" id="vaTkEliminar"><span>&#128465;</span><span>Eliminar ticket</span></button>' : ''}
    <span class="cs-flex"></span>
    <button type="button" class="btn-modern-primary btn-sm" id="vaTkGuardar"><span>&#128190;</span><span>Guardar ticket</span></button>`;
  vaTkMarcarDiferencias();
}

function vaTkMarcarDiferencias(){
  document.querySelectorAll('#vaTkFilas tr[data-prod]').forEach(tr => {
    const v = c => csNum(tr.querySelector(`[data-campo="${c}"]`).value) || 0;
    tr.querySelector('[data-campo="cantidad_real"]').classList.toggle('cs-dif', Math.abs(v('cantidad_ticket') - v('cantidad_real')) > 1e-6);
  });
}

async function vaGuardarTicket(){
  const detalles = [];
  document.querySelectorAll('#vaTkFilas tr[data-prod]').forEach(tr => {
    const ct = tr.querySelector('[data-campo="cantidad_ticket"]').value;
    const cr = tr.querySelector('[data-campo="cantidad_real"]').value;
    if(csNum(ct) || csNum(cr)) detalles.push({ producto_id: Number(tr.dataset.prod), cantidad_ticket: ct, cantidad_real: cr });
  });
  const data = await vaPost('ticket/guardar/', {
    id: vaTicketSel, tipo_id: document.getElementById('vaTkTipo').value,
    numero: document.getElementById('vaTkNumero').value, pedido_por: document.getElementById('vaTkPedido').value,
    recibido_por: document.getElementById('vaTkRecibido').value, almacen_codigo: document.getElementById('vaTkAlmacen').value, detalles
  });
  if(data){ vaTicketSel = data.ticket_id; vaRenderModal(); }
}

/* ---------- Eventos ---------- */

function vaFiltrar(tbodyId, texto){
  const q = (texto || '').trim().toLowerCase();
  document.querySelectorAll(`#${tbodyId} tr[data-buscar]`).forEach(tr => { tr.hidden = q && !tr.dataset.buscar.includes(q); });
}

document.addEventListener('DOMContentLoaded', function(){
  const vista = document.getElementById('ivVistaVolumetria');
  if(!vista) return;

  document.querySelectorAll('[data-iv-vista]').forEach(b => b.addEventListener('click', () => ivCambiarVista(b.dataset.ivVista)));
  document.querySelectorAll('[data-va-tab]').forEach(b => b.addEventListener('click', () => vaCambiarTab(b.dataset.vaTab)));
  document.querySelectorAll('[data-va-modal]').forEach(b => b.addEventListener('click', () => vaAbrirModal(b.dataset.vaModal)));
  document.getElementById('vaGuardar').addEventListener('click', () => guardarVolumetria());
  document.getElementById('vaSoloMovimiento').addEventListener('change', vaRenderInventario);
  document.getElementById('vaConcFosa').addEventListener('change', vaRenderConcentracion);

  // Edición en las tablas: no se redibuja el campo activo; solo lo que depende de él.
  document.getElementById('ivVistaVolumetria').addEventListener('input', function(ev){
    const el = ev.target;
    if(!el.classList.contains('va-input') || el.tagName === 'SELECT' || el.type === 'checkbox') return;
    if(el.dataset.fosa){
      const f = vaDatos.fosas.find(x => x.numero === Number(el.dataset.fosa));
      f[el.dataset.campo] = el.value === '' ? null : el.value;
      if(el.dataset.campo === 'real'){
        const barra = document.querySelector(`[data-fosa-barra="${f.numero}"]`);
        const r = csNum(el.value);
        if(barra) barra.style.width = `${f.capacidad > 0 && r !== null ? Math.min(r / f.capacidad * 100, 100) : 0}%`;
      }
    } else if(el.dataset.hoyo){
      vaDatos.hoyo.no_fluido[el.dataset.hoyo] = el.value;
      const ks = ['anular', 'sarta', 'bajo_mecha'];
      ks.forEach(k => {
        const c = document.querySelector(`[data-hoyo-fluido="${k}"]`);
        if(c) c.textContent = csFmt(Math.max((vaDatos.hoyo.volumen[k] || 0) - (csNum(vaDatos.hoyo.no_fluido[k]) || 0), 0));
      });
      document.getElementById('vaHoyoFluido').textContent = csFmt(vaFluidoHoyo());
      document.getElementById('vaHoyoNoFluido').textContent = csFmt(ks.reduce((a, k) => a + (csNum(vaDatos.hoyo.no_fluido[k]) || 0), 0));
      vaRenderBalance();
    } else if(el.dataset.inv){
      const r = vaDatos.inventario.find(x => x.producto_id === Number(el.dataset.inv));
      r[el.dataset.campo] = el.value;
      const id = r.producto_id;
      const fin = document.querySelector(`[data-inv-final="${id}"]`);
      if(fin && !r.servicio){ fin.textContent = csFmt(vaFinalVivo(r)); fin.classList.toggle('cs-agotado', vaFinalVivo(r) < 0); }
      const us = document.querySelector(`[data-inv-usado="${id}"]`);
      if(us) us.innerHTML = vaCant(r.usado_fluido + (csNum(r.usado_otro) || 0));
      const co = document.querySelector(`[data-inv-costo="${id}"]`);
      if(co) co.textContent = csDinero(vaCostoVivo(r));
      vaRenderCostos();
    }
    vaMarcarSucio();
    vaRenderKpis();
    if(vaTab === 'fosas') vaRenderResumen();
  });

  document.getElementById('ivVistaVolumetria').addEventListener('change', function(ev){
    const el = ev.target;
    if(!el.classList.contains('va-input')) return;
    if(el.tagName === 'SELECT' && el.dataset.fosa){
      const f = vaDatos.fosas.find(x => x.numero === Number(el.dataset.fosa));
      f.tipo_codigo = el.value === '' ? null : Number(el.value);
      vaTiposCambiados = vaDatos.fosas.some(x => (x.tipo_codigo ?? null) !== (x._tipo_guardado ?? null));
      vaMarcarSucio();
      vaRenderAvisos();
    } else if(el.type === 'checkbox' && el.dataset.inv){
      const r = vaDatos.inventario.find(x => x.producto_id === Number(el.dataset.inv));
      r.no_imprimir = el.checked;
      el.closest('tr').classList.toggle('va-no-imprimir', el.checked);
      vaMarcarSucio();
    }
  });

  // Modal
  const modal = document.getElementById('vaModal');
  document.getElementById('vaModalCerrar').addEventListener('click', vaCerrarModal);
  modal.addEventListener('click', function(ev){
    if(ev.target === modal || ev.target.closest('[data-va-cerrar]')) { vaCerrarModal(); return; }
    const id = ev.target.closest('button')?.id;
    if(id === 'vaQRegistrar') vaRegistrarQuimicos();
    else if(id === 'vaLRegistrar') vaRegistrarLodo();
    else if(id === 'vaTRegistrar') vaRegistrarTransferencia();
    else if(id === 'vaDeshacer'){
      const u = vaDatos.ultima_transaccion;
      if(u && window.confirm(`¿Deshacer el movimiento #${u.secuencia}?`)) vaPost('transaccion/deshacer/', {});
    }
    else if(id === 'vaTkNuevo'){ vaTicketSel = null; vaRenderModal(); }
    else if(id === 'vaTkGuardar') vaGuardarTicket();
    else if(id === 'vaTkEliminar'){
      if(window.confirm('¿Eliminar este ticket? Sus cantidades salen del inventario.')){
        vaPost(`ticket/${vaTicketSel}/eliminar/`, {}).then(d => { if(d){ vaTicketSel = d.tickets.length ? d.tickets[0].id : null; vaRenderModal(); } });
      }
    }
    const tk = ev.target.closest('[data-va-ticket]');
    if(tk){ vaTicketSel = Number(tk.dataset.vaTicket); vaRenderModal(); }
    const op = ev.target.closest('[data-va-op]');
    if(op) vaCambiarOperacion(op.dataset.vaOp);
  });
  modal.addEventListener('input', function(ev){
    const el = ev.target;
    if(el.classList.contains('va-q-cant') || el.id === 'vaQAceite' || el.id === 'vaQAgua') vaQRecalcular();
    else if(el.id === 'vaQBuscar') vaFiltrar('vaQFilas', el.value);
    else if(el.id === 'vaTkBuscar') vaFiltrar('vaTkFilas', el.value);
    else if(el.classList.contains('va-tk-cant')) vaTkMarcarDiferencias();
  });
  modal.addEventListener('change', function(ev){
    if(ev.target.id === 'vaTPerdida'){
      const d = vaDatos.descarga_equipos[ev.target.value];
      const vol = document.getElementById('vaTVolumen');
      if(d && !vol.value) vol.value = d.toFixed(2);
    }
  });
  document.addEventListener('keydown', function(ev){
    if(ev.key === 'Escape' && !modal.hidden) vaCerrarModal();
  });

  cargarCostosGenerales();
});

/* =====================================================================
   PESTAÑA 1 — Resumen de costos del día (datos reales de las pestañas 6 y 8)
   ===================================================================== */

async function cargarCostosGenerales(){
  if(!document.getElementById('cost_df_chem')) return;
  try {
    const res = await fetch(`/api/pozos/${POZO_ID}/daily-report/${REPORTE_ID}/cost-overview/`);
    const data = await res.json();
    if(!data.ok) return;
    const f = n => Number(n || 0).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const mapa = { df_chem: 'df_chem', ife_sc: 'ife_sc', drilling_total: 'drilling_total', df_equip: 'df_equip', other: 'other_cost', daily_total: 'total' };
    Object.keys(mapa).forEach(k => {
      const d = document.getElementById(`cost_${k}`);
      const c = document.getElementById(`cum_${k}`);
      if(d) d.textContent = f(data.daily[mapa[k]]);
      if(c) c.textContent = f(data.cumulative[mapa[k]]);
    });
  } catch(e){ /* el resumen de costos no bloquea la pestaña */ }
}
