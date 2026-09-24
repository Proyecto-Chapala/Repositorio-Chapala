/* =====================================================================
   PESTAÑA 6 — CONTROL DE SÓLIDOS (SOLIDS EQUIPMENT) · Fase 1: mallas

   1. Inventario de mallas (derivado) + tickets de entrega/devolución.
   2. Transacciones de mallas: instalar nueva/usada, pasar al almacén,
      desechar del equipo o del almacén, deshacer la última.

   A diferencia de las demás pestañas, aquí no hay "Guardar": cada movimiento
   y cada ticket se registran al momento y el servidor valida toda la línea
   de tiempo del pozo (stock y posiciones). Cada respuesta trae el resumen
   completo y la pantalla se vuelve a dibujar con él.

   Depende de las utilidades globales de reporte_diario_detalle.html:
   POZO_ID, REPORTE_ID, getCookie, showToast.
   ===================================================================== */

const CS_BASE = `/api/pozos/${POZO_ID}/daily-report/${REPORTE_ID}/control-solidos/`;

let csCargado = false;
let csDatos = null;
let csVista = 'inventario';
let csEquipoSel = null;     // serie del equipo seleccionado
let csPosicionSel = null;   // número de posición seleccionada
let csCondicion = 'NUEVA';  // NUEVA | USADA para instalar
let csTicketSel = null;     // id del ticket en edición (null = nuevo)
let csOcupado = false;      // evita dobles clics mientras responde el servidor

/* ---------- Utilidades ---------- */

function csEsc(texto){
  const div = document.createElement('div');
  div.textContent = texto == null ? '' : String(texto);
  return div.innerHTML;
}

function csDinero(n){
  return Number(n || 0).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function csCant(n){
  return n ? String(n) : '<span class="cs-cero">0</span>';
}

async function csPost(ruta, payload){
  if(csOcupado) return null;
  csOcupado = true;
  try {
    const res = await fetch(CS_BASE + ruta, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify(payload || {})
    });
    const data = await res.json();
    if(!data.ok){
      showToast(data.error || 'No se pudo completar la operación.', false);
      return null;
    }
    csAplicar(data);
    if(data.mensaje) showToast(data.mensaje);
    return data;
  } catch(e){
    showToast('Error de conexión con el servidor.', false);
    return null;
  } finally {
    csOcupado = false;
  }
}

/* ---------- Carga y render general ---------- */

async function inicializarControlSolidos(){
  if(csCargado) return;
  csCargado = true;
  try {
    const res = await fetch(CS_BASE);
    const data = await res.json();
    if(!data.ok) throw new Error(data.error || 'respuesta inválida');
    csAplicar(data);
  } catch(e){
    csCargado = false;
    document.getElementById('csFilasInventario').innerHTML =
      '<tr class="cs-fila-vacia"><td colspan="16">No se pudo cargar el control de sólidos.</td></tr>';
    showToast('No se pudo cargar el control de sólidos.', false);
  }
}

function csAplicar(data){
  csDatos = data;
  const alerta = document.getElementById('csAlerta');
  const series = new Set(data.equipos.map(e => e.serie));
  const huerfanas = (data.fuera_de_rango || []).filter(f => !series.has(f.serie));
  if(data.error_linea_tiempo){
    alerta.textContent = `Hay datos de mallas inconsistentes en el pozo: ${data.error_linea_tiempo}`;
    alerta.hidden = false;
  } else if(huerfanas.length){
    alerta.textContent = 'Hay mallas instaladas en equipos que ya no están activos en el pozo o ya no llevan mallas: ' +
      huerfanas.map(f => `${f.malla_texto} (serie ${f.serie}, posición ${f.posicion})`).join('; ') +
      '. Vuelve a activar el equipo para poder retirarlas.';
    alerta.hidden = false;
  } else {
    alerta.hidden = true;
  }
  if(csEquipoSel && !data.equipos.some(e => e.serie === csEquipoSel)) csEquipoSel = null;
  if(!csEquipoSel && data.equipos.length) csEquipoSel = data.equipos[0].serie;

  csRenderInventario();
  csRenderEquipos();
  csRenderDetalleEquipo();
  csRenderMovimientos();
  csRenderAlmacenUsadas();
  if(!document.getElementById('csModalTickets').hidden){
    csRenderListaTickets();
    csRenderListaTipos();
  }
}

function csCambiarVista(vista){
  csVista = vista;
  document.querySelectorAll('.cs-subnav-btn[data-vista]').forEach(b =>
    b.classList.toggle('is-active', b.dataset.vista === vista));
  document.querySelectorAll('#tabContent-solidos .cs-vista[data-vista]').forEach(sec => { sec.hidden = sec.dataset.vista !== vista; });
  if(vista === 'equipos') inicializarUsoEquipos();
  if(typeof inicializarOpcionalSolidos === 'function') inicializarOpcionalSolidos(vista);
}

/* ---------- 1. Inventario ---------- */

function csRenderInventario(){
  const d = csDatos;
  const t = d.totales;
  document.getElementById('csResumenInventario').innerHTML = `
    <div class="cs-resumen-item cs-resumen-destacado"><span>Costo del día</span><strong>${csDinero(t.costo_diario)}</strong></div>
    <div class="cs-resumen-item"><span>Costo acumulado</span><strong>${csDinero(t.costo_acumulado)}</strong></div>
    <div class="cs-resumen-item"><span>Nuevas en stock</span><strong>${t.nuevas_final}</strong></div>
    <div class="cs-resumen-item"><span>Usadas en almacén</span><strong>${t.usadas_final}</strong></div>
    <div class="cs-resumen-item"><span>Instaladas en equipos</span><strong>${t.en_equipos}</strong></div>`;

  const badge = document.getElementById('csBadgeTickets');
  badge.textContent = d.tickets.length;
  badge.hidden = d.tickets.length === 0;

  const tbody = document.getElementById('csFilasInventario');
  if(!d.inventario.length){
    tbody.innerHTML = `<tr class="cs-fila-vacia"><td colspan="16">
      El pozo todavía no tiene mallas activas.
      <a href="${d.enlaces.equipos_activos}" target="_blank" rel="noopener">Agrégalas en Productos, Equipos y Mallas Activos &rarr;</a>
    </td></tr>`;
    document.getElementById('csPieInventario').innerHTML = '';
    return;
  }

  tbody.innerHTML = d.inventario.map(f => `
    <tr class="${f.activa ? '' : 'cs-fila-inactiva'}" ${f.activa ? '' : 'title="Esta malla ya no está en la lista activa del pozo"'}>
      <td class="cs-codigo">${csEsc(f.codigo)}</td>
      <td>${csEsc(f.descripcion)}</td>
      <td class="cs-num">${f.mesh_size}</td>
      <td class="cs-num cs-grupo-nuevas">${csCant(f.nuevas_inicial)}</td>
      <td class="cs-num cs-grupo-nuevas cs-mas">${csCant(f.nuevas_recibidas)}</td>
      <td class="cs-num cs-grupo-nuevas cs-menos">${csCant(f.nuevas_devueltas)}</td>
      <td class="cs-num cs-grupo-nuevas cs-menos">${csCant(f.nuevas_instaladas)}</td>
      <td class="cs-num cs-grupo-nuevas cs-final ${f.nuevas_final === 0 ? 'cs-agotado' : ''}">${f.nuevas_final}</td>
      <td class="cs-num cs-grupo-usadas">${csCant(f.usadas_inicial)}</td>
      <td class="cs-num cs-grupo-usadas cs-mas">${csCant(f.usadas_entradas)}</td>
      <td class="cs-num cs-grupo-usadas cs-menos">${csCant(f.usadas_salidas)}</td>
      <td class="cs-num cs-grupo-usadas cs-final">${f.usadas_final}</td>
      <td class="cs-num cs-grupo-equipos">${csCant(f.en_equipos)}</td>
      <td class="cs-num cs-grupo-costos">${f.precio_neto == null ? '—' : csDinero(f.precio_neto)}</td>
      <td class="cs-num cs-grupo-costos">${f.costo_diario ? csDinero(f.costo_diario) : '<span class="cs-cero">0,00</span>'}</td>
      <td class="cs-num cs-grupo-costos cs-final">${csDinero(f.costo_acumulado)}</td>
    </tr>`).join('');

  const suma = k => d.inventario.reduce((a, f) => a + (f[k] || 0), 0);
  document.getElementById('csPieInventario').innerHTML = `
    <tr class="cs-fila-total">
      <td colspan="3">Total</td>
      <td class="cs-num">${suma('nuevas_inicial')}</td>
      <td class="cs-num">${suma('nuevas_recibidas')}</td>
      <td class="cs-num">${suma('nuevas_devueltas')}</td>
      <td class="cs-num">${suma('nuevas_instaladas')}</td>
      <td class="cs-num">${suma('nuevas_final')}</td>
      <td class="cs-num">${suma('usadas_inicial')}</td>
      <td class="cs-num">${suma('usadas_entradas')}</td>
      <td class="cs-num">${suma('usadas_salidas')}</td>
      <td class="cs-num">${suma('usadas_final')}</td>
      <td class="cs-num">${suma('en_equipos')}</td>
      <td></td>
      <td class="cs-num">${csDinero(t.costo_diario)}</td>
      <td class="cs-num">${csDinero(t.costo_acumulado)}</td>
    </tr>`;
}

/* ---------- 2. Transacciones: equipos y posiciones ---------- */

function csRenderEquipos(){
  const cont = document.getElementById('csListaEquipos');
  const d = csDatos;
  if(!d.equipos.length){
    cont.innerHTML = `<div class="cs-vacio">
      <strong>Ningún equipo del pozo lleva mallas todavía.</strong>
      <span>1. Indica cuántas mallas lleva cada modelo en
        <a href="${d.enlaces.catalogos}" target="_blank" rel="noopener">Catálogos Maestros &rarr; Equipos</a> (campo "Posiciones de malla").</span>
      <span>2. Verifica que el equipo esté en
        <a href="${d.enlaces.equipos_activos}" target="_blank" rel="noopener">los equipos activos del pozo</a>.</span>
    </div>`;
    return;
  }
  cont.innerHTML = d.equipos.map(e => `
    <button type="button" class="cs-equipo ${e.serie === csEquipoSel ? 'is-active' : ''}" data-serie="${csEsc(e.serie)}">
      <span class="cs-equipo-nombre">${csEsc(e.descripcion)}</span>
      <span class="cs-equipo-meta">${csEsc(e.tipo_display)} &bull; Serie ${csEsc(e.serie)}</span>
      <span class="cs-equipo-ocupacion">
        ${Array.from({length: e.posiciones_total}, (_, i) =>
          `<span class="cs-ocup-punto ${e.posiciones[i].malla_id ? 'is-llena' : ''}"></span>`).join('')}
        <span class="cs-ocup-texto">${e.posiciones_ocupadas}/${e.posiciones_total}</span>
      </span>
    </button>`).join('');
}

function csEquipoActual(){
  return csDatos && csDatos.equipos.find(e => e.serie === csEquipoSel) || null;
}

function csRenderDetalleEquipo(){
  const cont = document.getElementById('csDetalleEquipo');
  const eq = csEquipoActual();
  if(!eq){
    cont.innerHTML = '<div class="cs-vacio cs-vacio-centrado">Selecciona un equipo para ver sus mallas.</div>';
    return;
  }
  if(csPosicionSel && csPosicionSel > eq.posiciones_total) csPosicionSel = null;

  const fuera = (csDatos.fuera_de_rango || []).filter(f => f.serie === eq.serie);
  const avisoFuera = fuera.length
    ? `<div class="cs-aviso">Hay mallas en posiciones que el modelo ya no tiene:
        ${fuera.map(f => `posición ${f.posicion} (${csEsc(f.malla_texto)})`).join(', ')}.
        Sube el número de posiciones en Catálogos Maestros para poder retirarlas.</div>`
    : '';

  cont.innerHTML = `
    <div class="cs-card-cabecera">
      <div>
        <span class="cs-card-titulo">${csEsc(eq.descripcion)}</span>
        <span class="cs-card-subtitulo">${csEsc(eq.equipo_nombre)} &bull; Serie ${csEsc(eq.serie)} &bull; ${eq.posiciones_total} posiciones</span>
      </div>
    </div>
    ${avisoFuera}
    <div class="cs-flujo"><span>Línea de flujo</span><span class="cs-flujo-flecha"></span><span>Descarga</span></div>
    <div class="cs-posiciones">
      ${eq.posiciones.map(p => `
        <button type="button" class="cs-posicion ${p.malla_id ? 'is-llena' : 'is-vacia'} ${p.posicion === csPosicionSel ? 'is-sel' : ''}" data-pos="${p.posicion}">
          <span class="cs-pos-num">${p.posicion}</span>
          <span class="cs-pos-malla">${p.malla_id ? csEsc(p.malla_texto) : 'Vacía'}</span>
          ${p.malla_id ? `<span class="cs-pos-codigo">${csEsc(p.malla_codigo)}</span>` : ''}
        </button>`).join('')}
    </div>
    <div class="cs-accion" id="csPanelAccion">${csPanelAccion(eq)}</div>`;
}

function csPanelAccion(eq){
  if(!csPosicionSel){
    return '<div class="cs-accion-ayuda">Haz clic en una posición para instalar o retirar una malla. La posición 1 es la más cercana a la línea de flujo.</div>';
  }
  const pos = eq.posiciones[csPosicionSel - 1];

  if(pos.malla_id){
    return `
      <div class="cs-accion-titulo">Posición ${pos.posicion} &bull; ${csEsc(pos.malla_texto)}</div>
      <div class="cs-accion-botones">
        <button type="button" class="btn-modern-secondary btn-sm" data-accion="A_ALMACEN">
          <span>&#128230;</span><span>Pasar al almacén (queda como usada)</span>
        </button>
        <button type="button" class="btn-modern-secondary btn-sm cs-btn-peligro" data-accion="DESECHAR_EQUIPO">
          <span>&#128465;</span><span>Desechar</span>
        </button>
      </div>`;
  }

  const usada = csCondicion === 'USADA';
  const opciones = csDatos.mallas_disponibles.map(m => {
    const stock = usada ? m.stock_usadas : m.stock_nuevas;
    const detalle = usada ? `${stock} en almacén` : `${stock} en stock · ${csDinero(m.precio_neto)}`;
    return `<option value="${m.malla_id}" ${stock <= 0 ? 'disabled' : ''}>${csEsc(m.texto)} — ${detalle}</option>`;
  });
  const hayStock = csDatos.mallas_disponibles.some(m => (usada ? m.stock_usadas : m.stock_nuevas) > 0);

  return `
    <div class="cs-accion-titulo">Posición ${pos.posicion} &bull; Vacía</div>
    <div class="cs-condicion" role="radiogroup" aria-label="Condición de la malla">
      <button type="button" class="cs-condicion-btn ${!usada ? 'is-active' : ''}" data-condicion="NUEVA">Malla nueva</button>
      <button type="button" class="cs-condicion-btn ${usada ? 'is-active' : ''}" data-condicion="USADA">Malla usada</button>
    </div>
    <div class="cs-accion-fila">
      <select id="csMallaInstalar" class="report-input cs-select-malla" ${hayStock ? '' : 'disabled'}>
        ${hayStock ? '<option value="">Elige la malla…</option>' : `<option value="">${usada ? 'No hay mallas usadas en el almacén' : 'No hay mallas nuevas en stock'}</option>`}
        ${opciones.join('')}
      </select>
      <button type="button" class="btn-modern-primary btn-sm" data-accion="${usada ? 'INSTALAR_USADA' : 'INSTALAR_NUEVA'}" ${hayStock ? '' : 'disabled'}>
        <span>&#10004;</span><span>Instalar</span>
      </button>
    </div>
    ${!usada && !hayStock ? '<div class="cs-accion-ayuda">Registra primero la recepción en "Tickets de entrega / devolución" (Inventario de mallas).</div>' : ''}`;
}

async function csEjecutarAccion(accion){
  const eq = csEquipoActual();
  const payload = { accion, serie: eq ? eq.serie : '', posicion: csPosicionSel };
  if(accion === 'INSTALAR_NUEVA' || accion === 'INSTALAR_USADA'){
    const sel = document.getElementById('csMallaInstalar');
    if(!sel || !sel.value){
      showToast('Elige la malla que vas a instalar.', false);
      return;
    }
    payload.malla_id = parseInt(sel.value, 10);
  }
  if(accion === 'DESECHAR_EQUIPO'){
    const pos = eq.posiciones[csPosicionSel - 1];
    if(!window.confirm(`¿Desechar la malla ${pos.malla_texto} de la posición ${pos.posicion}? No vuelve al almacén.`)) return;
  }
  await csPost('transaccion/', payload);
}

/* ---------- 2. Transacciones: movimientos del día y almacén ---------- */

function csRenderMovimientos(){
  const tbody = document.getElementById('csFilasMovimientos');
  const d = csDatos;
  if(!d.transacciones.length){
    tbody.innerHTML = '<tr class="cs-fila-vacia"><td colspan="7">Sin movimientos de mallas en este reporte.</td></tr>';
  } else {
    tbody.innerHTML = d.transacciones.map(t => `
      <tr>
        <td class="cs-num cs-codigo">${t.secuencia}</td>
        <td><span class="cs-accion-chip cs-accion-${t.accion.toLowerCase()}">${csEsc(t.accion_display)}</span></td>
        <td>${csEsc(t.malla_descripcion)} <span class="cs-tenue">(Mesh ${t.mesh_size})</span></td>
        <td class="cs-codigo">${csEsc(t.malla_codigo)}</td>
        <td>${csEsc(t.equipo_serie || '—')}</td>
        <td>${csEsc(t.equipo_descripcion || 'Almacén')}</td>
        <td class="cs-num">${t.posicion || '—'}</td>
      </tr>`).join('');
  }

  const btn = document.getElementById('csBtnDeshacer');
  const nota = document.getElementById('csNotaDeshacer');
  const u = d.ultima_transaccion;
  btn.disabled = !(u && u.es_de_este_reporte);
  if(!u){
    nota.textContent = '';
  } else if(u.es_de_este_reporte){
    nota.textContent = `"Deshacer último" borra la transacción #${u.secuencia}, la última registrada en el pozo.`;
  } else {
    nota.textContent = `La última transacción del pozo (#${u.secuencia}) es del ${u.fecha}; solo se puede deshacer desde ese reporte.`;
  }
}

function csRenderAlmacenUsadas(){
  const cont = document.getElementById('csAlmacenUsadas');
  const filas = csDatos.inventario.filter(f => f.usadas_final > 0);
  if(!filas.length){
    cont.innerHTML = '<div class="cs-vacio">No hay mallas usadas en el almacén. Llegan aquí con "Pasar al almacén".</div>';
    return;
  }
  cont.innerHTML = `<ul class="cs-almacen">${filas.map(f => `
    <li>
      <span class="cs-almacen-cant">${f.usadas_final}</span>
      <span class="cs-almacen-texto">${csEsc(f.descripcion)} <span class="cs-tenue">(Mesh ${f.mesh_size})</span></span>
      <button type="button" class="cs-link-boton cs-link-peligro" data-desechar="${f.malla_id}" title="Desechar una malla usada del almacén">Desechar 1</button>
    </li>`).join('')}</ul>`;
}

/* ---------- Tickets ---------- */

function csAbrirTickets(){
  const modal = document.getElementById('csModalTickets');
  document.getElementById('csModalTicketsFecha').textContent =
    `Reporte del ${document.getElementById('tabContent-solidos').dataset.fecha}`;
  modal.hidden = false;
  document.getElementById('csPanelTipos').hidden = true;
  csRenderListaTickets();
  csCargarTicketEnFormulario(csDatos.tickets.length ? csDatos.tickets[0].id : null);
}

function csCerrarTickets(){
  document.getElementById('csModalTickets').hidden = true;
}

function csRenderListaTickets(){
  const cont = document.getElementById('csListaTickets');
  const tickets = csDatos.tickets;
  if(!tickets.length){
    cont.innerHTML = '<div class="cs-vacio">Sin tickets en este reporte.</div>';
    return;
  }
  cont.innerHTML = tickets.map(t => `
    <button type="button" class="cs-tk-item ${t.id === csTicketSel ? 'is-active' : ''}" data-ticket="${t.id}">
      <span class="cs-tk-item-tipo cs-sentido-${t.sentido.toLowerCase()}">${csEsc(t.tipo_nombre)}</span>
      <span class="cs-tk-item-num">${t.numero ? 'N° ' + csEsc(t.numero) : 'Sin número'}</span>
      <span class="cs-tk-item-meta">${t.total_nuevas} nuevas &bull; ${t.total_usadas} usadas
        ${t.tiene_diferencias ? '<span class="cs-dif-chip">Con diferencias</span>' : ''}</span>
    </button>`).join('');
}

function csOpcionesTipo(seleccion){
  return csDatos.tipos_ticket.map(t =>
    `<option value="${t.id}" ${t.id === seleccion ? 'selected' : ''}>${csEsc(t.nombre)} — ${t.sentido === 'ENTRADA' ? 'entrada' : 'salida'}</option>`
  ).join('');
}

function csCargarTicketEnFormulario(id){
  csTicketSel = id;
  const t = csDatos.tickets.find(x => x.id === id) || null;

  document.getElementById('csTkTipo').innerHTML = csOpcionesTipo(t ? t.tipo_id : (csDatos.tipos_ticket[0] || {}).id);
  document.getElementById('csTkNumero').value = t ? t.numero : '';
  document.getElementById('csTkPedido').value = t ? t.pedido_por : '';
  document.getElementById('csTkRecibido').value = t ? t.recibido_por : '';

  const almacen = document.getElementById('csTkAlmacen');
  const codigo = t ? t.almacen_codigo : '';
  let opciones = '<option value="">— Sin almacén —</option>' + csDatos.almacenes.map(a =>
    `<option value="${csEsc(a.codigo)}" ${a.codigo === codigo ? 'selected' : ''}>${csEsc(a.codigo)} — ${csEsc(a.nombre)}</option>`).join('');
  if(codigo && !csDatos.almacenes.some(a => a.codigo === codigo)){
    opciones += `<option value="${csEsc(codigo)}" selected>${csEsc(codigo)} — ${csEsc(t.almacen_nombre)} (ya no está en la configuración)</option>`;
  }
  almacen.innerHTML = opciones;

  const porMalla = {};
  if(t) t.detalles.forEach(d => { porMalla[d.malla_id] = d; });
  const tbody = document.getElementById('csFilasTicket');
  if(!csDatos.mallas_disponibles.length){
    tbody.innerHTML = '<tr class="cs-fila-vacia"><td colspan="6">El pozo no tiene mallas activas.</td></tr>';
  } else {
    tbody.innerHTML = csDatos.mallas_disponibles.map(m => {
      const d = porMalla[m.malla_id] || {};
      const celda = (campo) => `<td class="cs-num ${campo.startsWith('nuevas') ? 'cs-grupo-nuevas' : 'cs-grupo-usadas'}">
        <input type="number" class="cs-input-cant" min="0" step="1" data-malla="${m.malla_id}" data-campo="${campo}" value="${d[campo] || ''}" placeholder="0"></td>`;
      return `<tr data-malla="${m.malla_id}">
        <td>${csEsc(m.texto)}</td>
        <td class="cs-num">${m.mesh_size}</td>
        ${celda('nuevas_ticket')}${celda('nuevas_real')}${celda('usadas_ticket')}${celda('usadas_real')}
      </tr>`;
    }).join('');
  }

  document.getElementById('csBtnEliminarTicket').hidden = !t;
  csMarcarDiferencias();
  csRenderListaTickets();
}

function csMarcarDiferencias(){
  document.querySelectorAll('#csFilasTicket tr[data-malla]').forEach(tr => {
    const v = campo => parseInt((tr.querySelector(`[data-campo="${campo}"]`) || {}).value || '0', 10) || 0;
    tr.querySelectorAll('[data-campo="nuevas_real"]').forEach(el =>
      el.classList.toggle('cs-dif', v('nuevas_ticket') !== v('nuevas_real')));
    tr.querySelectorAll('[data-campo="usadas_real"]').forEach(el =>
      el.classList.toggle('cs-dif', v('usadas_ticket') !== v('usadas_real')));
  });
}

async function csGuardarTicket(){
  const detalles = [];
  document.querySelectorAll('#csFilasTicket tr[data-malla]').forEach(tr => {
    const fila = { malla_id: parseInt(tr.dataset.malla, 10) };
    tr.querySelectorAll('.cs-input-cant').forEach(el => { fila[el.dataset.campo] = el.value; });
    detalles.push(fila);
  });
  const payload = {
    id: csTicketSel,
    tipo_id: document.getElementById('csTkTipo').value,
    numero: document.getElementById('csTkNumero').value,
    pedido_por: document.getElementById('csTkPedido').value,
    recibido_por: document.getElementById('csTkRecibido').value,
    almacen_codigo: document.getElementById('csTkAlmacen').value,
    detalles
  };
  const data = await csPost('ticket/guardar/', payload);
  if(data) csCargarTicketEnFormulario(data.ticket_id);
}

async function csEliminarTicket(){
  if(!csTicketSel) return;
  if(!window.confirm('¿Eliminar este ticket? Sus cantidades salen del inventario.')) return;
  const data = await csPost(`ticket/${csTicketSel}/eliminar/`, {});
  if(data) csCargarTicketEnFormulario(data.tickets.length ? data.tickets[0].id : null);
}

/* ---------- Tipos de ticket ---------- */

function csRenderListaTipos(){
  const cont = document.getElementById('csListaTipos');
  cont.innerHTML = csDatos.tipos_ticket.map(t => `
    <div class="cs-tipo-fila" data-tipo="${t.id}">
      <input type="text" class="report-input" maxlength="80" value="${csEsc(t.nombre)}" data-campo="nombre">
      <select class="report-input" data-campo="sentido">
        <option value="ENTRADA" ${t.sentido === 'ENTRADA' ? 'selected' : ''}>Entrada al pozo</option>
        <option value="SALIDA" ${t.sentido === 'SALIDA' ? 'selected' : ''}>Salida del pozo</option>
      </select>
      <button type="button" class="btn-modern-secondary btn-sm" data-guardar-tipo="${t.id}">Guardar</button>
      <button type="button" class="cs-btn-quitar" data-eliminar-tipo="${t.id}" title="Eliminar tipo">&times;</button>
    </div>`).join('');
}

async function csGuardarTipo(id){
  const fila = document.querySelector(`.cs-tipo-fila[data-tipo="${id}"]`);
  const data = await csPost('tipo-ticket/guardar/', {
    id,
    nombre: fila.querySelector('[data-campo="nombre"]').value,
    sentido: fila.querySelector('[data-campo="sentido"]').value
  });
  if(data) csCargarTicketEnFormulario(csTicketSel);
}

/* ---------- Eventos ---------- */

document.addEventListener('DOMContentLoaded', function(){
  const panel = document.getElementById('tabContent-solidos');
  if(!panel) return;

  document.querySelectorAll('.cs-subnav-btn[data-vista]').forEach(b =>
    b.addEventListener('click', () => csCambiarVista(b.dataset.vista)));

  document.getElementById('csListaEquipos').addEventListener('click', function(ev){
    const btn = ev.target.closest('.cs-equipo');
    if(!btn) return;
    csEquipoSel = btn.dataset.serie;
    csPosicionSel = null;
    csRenderEquipos();
    csRenderDetalleEquipo();
  });

  document.getElementById('csDetalleEquipo').addEventListener('click', function(ev){
    const pos = ev.target.closest('.cs-posicion');
    if(pos){
      csPosicionSel = parseInt(pos.dataset.pos, 10);
      csRenderDetalleEquipo();
      return;
    }
    const cond = ev.target.closest('.cs-condicion-btn');
    if(cond){
      csCondicion = cond.dataset.condicion;
      csRenderDetalleEquipo();
      return;
    }
    const acc = ev.target.closest('[data-accion]');
    if(acc && !acc.disabled) csEjecutarAccion(acc.dataset.accion);
  });

  document.getElementById('csBtnDeshacer').addEventListener('click', function(){
    const u = csDatos && csDatos.ultima_transaccion;
    if(!u) return;
    if(!window.confirm(`¿Deshacer la transacción #${u.secuencia}?`)) return;
    csPost('transaccion/deshacer/', {});
  });

  document.getElementById('csAlmacenUsadas').addEventListener('click', function(ev){
    const btn = ev.target.closest('[data-desechar]');
    if(!btn) return;
    csPost('transaccion/', { accion: 'DESECHAR_ALMACEN', malla_id: parseInt(btn.dataset.desechar, 10) });
  });

  // Tickets
  document.getElementById('csBtnTickets').addEventListener('click', csAbrirTickets);
  document.getElementById('csCerrarTickets').addEventListener('click', csCerrarTickets);
  document.getElementById('csModalTickets').addEventListener('click', function(ev){
    if(ev.target === this) csCerrarTickets();
  });
  document.addEventListener('keydown', function(ev){
    if(ev.key === 'Escape' && !document.getElementById('csModalTickets').hidden) csCerrarTickets();
  });
  document.getElementById('csBtnNuevoTicket').addEventListener('click', () => csCargarTicketEnFormulario(null));
  document.getElementById('csListaTickets').addEventListener('click', function(ev){
    const item = ev.target.closest('[data-ticket]');
    if(item) csCargarTicketEnFormulario(parseInt(item.dataset.ticket, 10));
  });
  document.getElementById('csFilasTicket').addEventListener('input', csMarcarDiferencias);
  document.getElementById('csBtnGuardarTicket').addEventListener('click', csGuardarTicket);
  document.getElementById('csBtnEliminarTicket').addEventListener('click', csEliminarTicket);

  // Tipos de ticket
  document.getElementById('csBtnTiposTicket').addEventListener('click', function(){
    csRenderListaTipos();
    document.getElementById('csPanelTipos').hidden = false;
  });
  document.getElementById('csCerrarTipos').addEventListener('click', () => {
    document.getElementById('csPanelTipos').hidden = true;
  });
  document.getElementById('csListaTipos').addEventListener('click', async function(ev){
    const guardar = ev.target.closest('[data-guardar-tipo]');
    if(guardar){
      csGuardarTipo(parseInt(guardar.dataset.guardarTipo, 10));
      return;
    }
    const eliminar = ev.target.closest('[data-eliminar-tipo]');
    if(eliminar){
      const id = parseInt(eliminar.dataset.eliminarTipo, 10);
      if(!window.confirm('¿Eliminar este tipo de ticket?')) return;
      const data = await csPost(`tipo-ticket/${id}/eliminar/`, {});
      if(data) csCargarTicketEnFormulario(csTicketSel);
    }
  });
  document.getElementById('csBtnAgregarTipo').addEventListener('click', async function(){
    const nombre = document.getElementById('csTipoNuevoNombre');
    const data = await csPost('tipo-ticket/guardar/', {
      nombre: nombre.value,
      sentido: document.getElementById('csTipoNuevoSentido').value
    });
    if(data){
      nombre.value = '';
      csCargarTicketEnFormulario(csTicketSel);
    }
  });
});


/* =====================================================================
   3. DETALLE Y USO DE EQUIPOS (Equipment Details and Usage)

   Formulario del día para todos los equipos del pozo: rendimiento (datos
   clave para el volumen descargado y el lodo perdido), costos de renta y
   paradas. Se guarda con "Guardar equipos" (o el Guardar general, o al salir
   de la pestaña si hay cambios).

   El cálculo en vivo replica control_solidos.calcular_rendimiento (Python).
   ===================================================================== */

const CS_EQ_CONSTANTE = 1029.4;
const CS_EQ_GAL_BBL = 42;
const CS_EQ_POR_RECORTES = ['ZARANDA', 'LIMPIADOR_LODO', 'SECADOR_RECORTES'];

let csEqCargado = false;
let csEqListo = false;
let csEqDatos = null;       // respuesta del servidor
let csEqSel = null;         // serie seleccionada en Rendimiento
let csEqVista = 'rendimiento';
let csEqSucio = false;

function csEqPendiente(){
  return csEqListo && csEqSucio;
}

function csNum(v){
  if(v === null || v === undefined || v === '') return null;
  const n = parseFloat(String(v).replace(',', '.'));
  return Number.isFinite(n) ? n : null;
}

function csFmt(n, dec = 2){
  if(n === null || n === undefined || !Number.isFinite(n)) return '—';
  return n.toLocaleString('es-VE', { minimumFractionDigits: dec, maximumFractionDigits: dec });
}

function csValor(v){
  return v === null || v === undefined ? '' : String(v);
}

function csCalcularRendimiento(fila, volHoyo){
  const d = fila.datos;
  const moc = csNum(d.mud_on_cuttings) || 0;
  const horas = csNum(d.horas) || 0;
  const r = { recortes: null, descargado: null, lodo: null, qDescarte: null, qSalida: null };

  if(CS_EQ_POR_RECORTES.includes(fila.tipo_equipo)){
    const pct = csNum(d.porcentaje_recortes);
    if(pct === null) return r;
    r.recortes = volHoyo * pct / 100;
    r.descargado = r.recortes * (1 + moc);
    r.lodo = r.recortes * moc;
  } else if(fila.tipo_equipo === 'CENTRIFUGA'){
    const qIn = csNum(d.caudal_entrada_gpm);
    const re = csNum(d.densidad_entrada), rs = csNum(d.densidad_salida), rd = csNum(d.densidad_descarte);
    if([qIn, re, rs, rd].includes(null) || rd <= rs) return r;
    let q = qIn * (re - rs) / (rd - rs);
    q = Math.min(Math.max(q, 0), qIn);
    r.qDescarte = q;
    r.qSalida = qIn - q;
    r.descargado = q * horas * 60 / CS_EQ_GAL_BBL;
    r.lodo = r.descargado * moc / (1 + moc);
    r.recortes = r.descargado - r.lodo;
  }
  return r;
}

function csCostoDiario(fila){
  if(fila.datos.codigo_cobro === 'SIN_COBRO') return 0;
  return (csNum(fila.datos.cantidad_usada) || 0) * (fila.tarifa || 0);
}

function csMarcarSucio(){
  csEqSucio = true;
  document.getElementById('csEqTagCambios').hidden = false;
  document.getElementById('csEqEstado').textContent = 'Hay cambios sin guardar';
}

/* ---------- Carga ---------- */

async function inicializarUsoEquipos(){
  if(csEqCargado) return;
  csEqCargado = true;
  try {
    const res = await fetch(CS_BASE + 'equipos/');
    const data = await res.json();
    if(!data.ok) throw new Error(data.error || 'respuesta inválida');
    csEqAplicar(data);
    csEqListo = true;
  } catch(e){
    csEqCargado = false;
    document.getElementById('csEqContexto').innerHTML = '<div class="cs-vacio">No se pudo cargar el detalle de equipos.</div>';
    showToast('No se pudo cargar el detalle de equipos.', false);
  }
}

function csEqAplicar(data){
  csEqDatos = data;
  if(csEqSel && !data.equipos.some(e => e.serie === csEqSel)) csEqSel = null;
  if(!csEqSel && data.equipos.length) csEqSel = data.equipos[0].serie;
  csEqSucio = false;
  document.getElementById('csEqTagCambios').hidden = true;
  const heredados = data.equipos.some(e => e.heredado);
  document.getElementById('csEqEstado').textContent = data.hay_guardado
    ? 'Guardado'
    : (heredados ? 'Sin guardar · datos precargados del reporte anterior' : 'Sin guardar');
  csEqRenderContexto();
  csEqRenderTodo();
}

function csEqRenderTodo(){
  csEqRenderAvisos();
  if(csEqVista === 'rendimiento'){
    csEqRenderArbol();
    csEqRenderFicha();
    csEqRenderResumen();
  } else if(csEqVista === 'costos'){
    csEqRenderCostos();
  } else {
    csEqRenderUso();
  }
}

function csEqCambiarVista(vista){
  csEqVista = vista;
  document.querySelectorAll('.cs-eq-tab').forEach(b => b.classList.toggle('is-active', b.dataset.eqVista === vista));
  document.getElementById('csEqPanelRendimiento').hidden = vista !== 'rendimiento';
  document.getElementById('csEqPanelCostos').hidden = vista !== 'costos';
  document.getElementById('csEqPanelUso').hidden = vista !== 'uso';
  csEqRenderTodo();
}

/* ---------- Contexto del hoyo ---------- */

function csEqRenderContexto(){
  const c = csEqDatos.contexto;
  const sinDiametro = c.diametro_in <= 0;
  document.getElementById('csEqContexto').innerHTML = `
    <div class="cs-eq-dato"><span>Profundidad hoy</span><strong>${csFmt(c.profundidad_ft, 0)} ft</strong></div>
    <div class="cs-eq-dato"><span>Avance del día</span><strong>${csFmt(c.avance_ft, 0)} ft</strong>
      <small>${c.hay_reporte_anterior ? `desde ${csFmt(c.profundidad_anterior_ft, 0)} ft` : 'primer reporte: desde superficie'}</small></div>
    <div class="cs-eq-dato ${sinDiametro ? 'cs-eq-dato-alerta' : ''}"><span>Diámetro del hoyo</span>
      <strong>${sinDiametro ? 'Sin dato' : csFmt(c.diametro_in, 3) + ' in'}</strong>
      <small>${sinDiametro ? 'Captúralo en la pestaña 2' : csEsc(c.fuente_diametro)}</small></div>
    <div class="cs-eq-dato cs-eq-dato-destacado"><span>Volumen de hoyo perforado</span><strong>${csFmt(c.volumen_hoyo_bbl)} bbl</strong>
      <small>base para el % de recortes</small></div>
    <div class="cs-eq-dato"><span>Horas del período</span><strong>${csFmt(c.horas_periodo)} h</strong><small>pestaña 7</small></div>`;
}

/* ---------- Avisos ---------- */

function csEqRenderAvisos(){
  const avisos = [];
  const c = csEqDatos.contexto;
  const filas = csEqDatos.equipos;

  const zarandas = filas.filter(f => f.tipo_equipo === 'ZARANDA' || f.tipo_equipo === 'LIMPIADOR_LODO');
  const sumaZarandas = zarandas.reduce((a, f) => a + (csNum(f.datos.porcentaje_recortes) || 0), 0);
  if(sumaZarandas > 100.001){
    avisos.push(`Las zarandas y el limpiador de lodo suman ${csFmt(sumaZarandas, 1)} % de recortes; no pueden descargar más del 100 % de lo perforado.`);
  }
  filas.filter(f => f.tipo_equipo === 'SECADOR_RECORTES').forEach(f => {
    const pct = csNum(f.datos.porcentaje_recortes);
    if(pct !== null && zarandas.length && pct > sumaZarandas + 0.001){
      avisos.push(`El secador ${csEsc(f.descripcion)} (${csFmt(pct, 1)} %) no puede descargar más que lo que le entregan las zarandas (${csFmt(sumaZarandas, 1)} %). Lo normal está entre 55 y 70 %.`);
    }
  });
  filas.forEach(f => {
    const h = csNum(f.datos.horas);
    if(h !== null && h > c.horas_periodo + 0.001){
      avisos.push(`${csEsc(f.descripcion)} (${csEsc(f.serie)}): ${csFmt(h)} h en operación supera las ${csFmt(c.horas_periodo)} h del período.`);
    }
    const hp = csNum(f.datos.horas_parada);
    if(h !== null && hp !== null && h + hp > c.horas_periodo + 0.001){
      avisos.push(`${csEsc(f.descripcion)} (${csEsc(f.serie)}): operación + parada (${csFmt(h + hp)} h) supera el período.`);
    }
    if(f.es_centrifuga){
      const rs = csNum(f.datos.densidad_salida), rd = csNum(f.datos.densidad_descarte), re = csNum(f.datos.densidad_entrada);
      if(rs !== null && rd !== null && rd <= rs){
        avisos.push(`${csEsc(f.descripcion)} (${csEsc(f.serie)}): la densidad de descarte debe ser mayor que la de salida.`);
      }
      if(rs !== null && re !== null && rs > re){
        avisos.push(`${csEsc(f.descripcion)} (${csEsc(f.serie)}): la densidad de salida es mayor que la de entrada; revisa las lecturas.`);
      }
    }
  });
  if(c.diametro_in <= 0 && filas.some(f => f.usa_recortes)){
    avisos.push('Sin diámetro del hoyo no se puede calcular lo que descargan zarandas y secadores. Captura la mecha en la pestaña 2.');
  }

  document.getElementById('csEqAvisos').innerHTML = avisos.map(a => `<div class="cs-aviso-item">${a}</div>`).join('');
}

/* ---------- Rendimiento: árbol y ficha ---------- */

function csEqRenderArbol(){
  const cont = document.getElementById('csEqArbol');
  const filas = csEqDatos.equipos;
  if(!filas.length){
    cont.innerHTML = `<div class="cs-vacio">El pozo no tiene equipos activos.
      <a href="${csEqDatos.enlaces.equipos_activos}" target="_blank" rel="noopener">Agrégalos en Productos, Equipos y Mallas Activos &rarr;</a></div>`;
    return;
  }
  let html = '';
  let tipoActual = null;
  filas.forEach(f => {
    if(f.tipo_equipo !== tipoActual){
      if(tipoActual !== null) html += '</div>';
      tipoActual = f.tipo_equipo;
      html += `<div class="cs-arbol-grupo"><div class="cs-arbol-tipo">${csEsc(f.tipo_display)}</div>`;
    }
    const completo = csNum(f.datos.horas) !== null;
    html += `<button type="button" class="cs-arbol-item ${f.serie === csEqSel ? 'is-active' : ''} ${f.activo ? '' : 'is-inactivo'}" data-eq-serie="${csEsc(f.serie)}">
      <span class="cs-arbol-punto ${completo ? 'is-completo' : ''}"></span>
      <span class="cs-arbol-texto"><strong>${csEsc(f.serie)}</strong> &middot; ${csEsc(f.descripcion)}</span>
    </button>`;
  });
  html += '</div>';
  cont.innerHTML = html;
}

function csEqFila(serie){
  return csEqDatos.equipos.find(e => e.serie === serie) || null;
}

function csCampo(fila, campo, etiqueta, unidad, opciones = {}){
  const paso = opciones.paso || 'any';
  const ayuda = opciones.ayuda ? `<small class="cs-campo-ayuda">${opciones.ayuda}</small>` : '';
  return `<label class="cs-campo">
    <span class="cs-campo-label">${etiqueta}${unidad ? ` <em>(${unidad})</em>` : ''}</span>
    <input type="number" class="report-input cs-eq-input" step="${paso}" min="0"
           data-eq-serie="${csEsc(fila.serie)}" data-campo="${campo}" value="${csValor(fila.datos[campo])}">
    ${ayuda}
  </label>`;
}

function csEqRenderFicha(){
  const cont = document.getElementById('csEqFicha');
  const f = csEqFila(csEqSel);
  if(!f){
    cont.innerHTML = '<div class="cs-vacio cs-vacio-centrado">Selecciona un equipo.</div>';
    return;
  }
  const perdidas = '<option value="">— Sin asignar —</option>' + csEqDatos.categorias_perdida.map(cat =>
    `<option value="${cat.codigo}" ${cat.codigo === f.datos.tipo_perdida_codigo ? 'selected' : ''}>${cat.codigo} · ${csEsc(cat.descripcion)}</option>`
  ).join('');

  let campos = csCampo(f, 'horas', f.es_centrifuga ? 'Horas centrifugando' : 'Horas en operación', 'h', { paso: '0.25' });
  if(f.usa_recortes || f.es_centrifuga){
    campos += csCampo(f, 'mud_on_cuttings', 'Lodo en recortes', 'bbl/bbl',
      { ayuda: 'De la prueba de retención en recortes o de pozos vecinos.' });
  }
  if(f.usa_recortes){
    campos += csCampo(f, 'porcentaje_recortes', '% de recortes', '%',
      { ayuda: f.tipo_equipo === 'SECADOR_RECORTES'
        ? 'Menor que lo que suman las zarandas (normal 55-70 %).'
        : 'Parte de lo perforado hoy que descarga este equipo. Ej.: 4 zarandas con 80 % → 20 % cada una.' });
  }
  if(f.es_centrifuga){
    campos += csCampo(f, 'caudal_entrada_gpm', 'Caudal de entrada', 'gpm');
    campos += csCampo(f, 'densidad_entrada', 'Densidad de entrada', 'lb/gal', { paso: '0.01' });
    campos += csCampo(f, 'densidad_salida', 'Densidad de salida', 'lb/gal', { paso: '0.01' });
    campos += csCampo(f, 'densidad_descarte', 'Densidad de descarte', 'lb/gal', { paso: '0.01' });
  }
  if(f.usa_recortes || f.es_centrifuga){
    campos += `<label class="cs-campo">
      <span class="cs-campo-label">Tipo de pérdida</span>
      <select class="report-input cs-eq-input" data-eq-serie="${csEsc(f.serie)}" data-campo="tipo_perdida_codigo">${perdidas}</select>
      <small class="cs-campo-ayuda">Categoría en la que entra este lodo en la volumetría (pestaña 8).</small>
    </label>`;
  }

  const props = f.propiedades.length
    ? `<div class="cs-props">${f.propiedades.map((p, i) => `
        <label class="cs-campo">
          <span class="cs-campo-label">${csEsc(p.descripcion)}${p.unidad ? ` <em>(${csEsc(p.unidad)})</em>` : ''}${p.fuera_de_configuracion ? ' <em class="cs-tenue">· ya no está en la configuración</em>' : ''}</span>
          <input type="text" class="report-input cs-eq-prop" maxlength="60" data-eq-serie="${csEsc(f.serie)}" data-prop="${i}" value="${csEsc(p.valor)}">
        </label>`).join('')}</div>`
    : `<div class="cs-accion-ayuda">Este tipo de equipo no tiene propiedades adicionales configuradas.
        <a class="cs-enlace" href="${csEqDatos.enlaces.propiedades}" target="_blank" rel="noopener">Configurarlas en Propiedades de Equipos &rarr;</a></div>`;

  cont.innerHTML = `
    <div class="cs-card-cabecera">
      <div>
        <span class="cs-card-titulo">${csEsc(f.descripcion)}</span>
        <span class="cs-card-subtitulo">${csEsc(f.tipo_display)} &bull; ${csEsc(f.equipo_nombre)} &bull; Serie ${csEsc(f.serie)}${f.activo ? '' : ' &bull; <strong>ya no está activo en el pozo</strong>'}</span>
      </div>
      ${f.heredado ? '<span class="cs-chip-heredado" title="Lodo en recortes, % de recortes, tipo de pérdida y datos de cobro vienen del reporte anterior">Precargado de ayer</span>' : ''}
    </div>
    <div class="cs-subtitulo">Datos clave del día</div>
    <div class="cs-campos">${campos}</div>
    <div class="cs-resultados" id="csEqResultados"></div>
    <div class="cs-subtitulo">Propiedades adicionales</div>
    ${props}`;
  csEqRenderResultados();
}

function csEqRenderResultados(){
  const cont = document.getElementById('csEqResultados');
  const f = csEqFila(csEqSel);
  if(!cont || !f) return;
  const calc = csCalcularRendimiento(f, csEqDatos.contexto.volumen_hoyo_bbl);
  const horas = csNum(f.datos.horas) || 0;
  const tile = (etiqueta, dia, acumulado, unidad) => `
    <div class="cs-resultado">
      <span>${etiqueta}</span>
      <strong>${csFmt(dia)} <em>${unidad}</em></strong>
      ${acumulado !== undefined ? `<small>Acumulado: ${csFmt(acumulado)} ${unidad}</small>` : ''}
    </div>`;
  if(f.usa_recortes || f.es_centrifuga){
    cont.innerHTML =
      tile('Volumen descargado', calc.descargado, (f.previo.descargado_bbl || 0) + (calc.descargado || 0), 'bbl') +
      tile('Lodo perdido en los sólidos', calc.lodo, (f.previo.lodo_bbl || 0) + (calc.lodo || 0), 'bbl') +
      tile('Recortes descargados', calc.recortes, undefined, 'bbl') +
      (f.es_centrifuga ? tile('Caudal de descarte', calc.qDescarte, undefined, 'gpm') + tile('Caudal de salida', calc.qSalida, undefined, 'gpm') : '') +
      tile('Horas en el día', horas, (f.previo.horas || 0) + horas, 'h');
  } else {
    cont.innerHTML = tile('Horas en el día', horas, (f.previo.horas || 0) + horas, 'h');
  }
}

function csEqRenderResumen(){
  const c = csEqDatos.contexto;
  const filas = csEqDatos.equipos.filter(f => f.usa_recortes || f.es_centrifuga || csNum(f.datos.horas) !== null);
  const tbody = document.getElementById('csEqResumen');
  const porPerdida = {};
  let totalDesc = 0, totalLodo = 0;

  if(!filas.length){
    tbody.innerHTML = '<tr class="cs-fila-vacia"><td colspan="8">Sin equipos de control de sólidos.</td></tr>';
  } else {
    tbody.innerHTML = filas.map(f => {
      const r = csCalcularRendimiento(f, c.volumen_hoyo_bbl);
      totalDesc += r.descargado || 0;
      totalLodo += r.lodo || 0;
      const cat = csEqDatos.categorias_perdida.find(x => x.codigo === f.datos.tipo_perdida_codigo);
      if(r.lodo){
        const k = cat ? cat.descripcion : 'Sin asignar';
        porPerdida[k] = (porPerdida[k] || 0) + r.lodo;
      }
      return `<tr class="cs-fila-click" data-eq-serie="${csEsc(f.serie)}">
        <td>${csEsc(f.descripcion)}</td>
        <td class="cs-codigo">${csEsc(f.serie)}</td>
        <td class="cs-num">${csFmt(csNum(f.datos.horas))}</td>
        <td class="cs-num">${f.usa_recortes ? csFmt(csNum(f.datos.porcentaje_recortes), 1) : '—'}</td>
        <td class="cs-num">${csFmt(csNum(f.datos.mud_on_cuttings), 3)}</td>
        <td class="cs-num cs-final">${csFmt(r.descargado)}</td>
        <td class="cs-num cs-final">${csFmt(r.lodo)}</td>
        <td>${cat ? csEsc(cat.descripcion) : '<span class="cs-tenue">Sin asignar</span>'}</td>
      </tr>`;
    }).join('');
  }
  document.getElementById('csEqResumenPie').innerHTML = `<tr class="cs-fila-total">
    <td colspan="5">Total del día</td>
    <td class="cs-num">${csFmt(totalDesc)}</td>
    <td class="cs-num">${csFmt(totalLodo)}</td>
    <td></td></tr>`;
  document.getElementById('csEqPerdidas').innerHTML = Object.keys(porPerdida).map(k =>
    `<span class="cs-chip-perdida">${csEsc(k)}: <strong>${csFmt(porPerdida[k])} bbl</strong></span>`).join('');
}

/* ---------- Costos ---------- */

function csEqRenderCostos(){
  const soloFluidos = document.getElementById('csEqSoloFluidos').checked;
  const filas = csEqDatos.equipos.filter(f => !soloFluidos || f.datos.es_fluidos);
  const tbody = document.getElementById('csEqCostos');
  if(!filas.length){
    tbody.innerHTML = `<tr class="cs-fila-vacia"><td colspan="8">${soloFluidos ? 'Ningún equipo está marcado como de fluidos de perforación.' : 'El pozo no tiene equipos activos.'}</td></tr>`;
  } else {
    tbody.innerHTML = filas.map(f => {
      const dia = csCostoDiario(f);
      const s = csEsc(f.serie);
      const tarifaNueva = f.tarifas_pozo && f.guardado && f.tarifas_pozo[f.datos.codigo_cobro] !== undefined
        && Math.abs(f.tarifas_pozo[f.datos.codigo_cobro] - f.tarifa) > 0.004;
      return `<tr class="${f.datos.codigo_cobro === 'SIN_COBRO' ? 'cs-fila-sin-cobro' : ''}">
        <td class="cs-codigo">${s}</td>
        <td>${csEsc(f.descripcion)}${f.activo ? '' : ' <span class="cs-tenue">(inactivo)</span>'}</td>
        <td class="cs-num"><input type="number" class="cs-input-cant cs-eq-input" min="0" step="1" data-eq-serie="${s}" data-campo="cantidad_usada" value="${csValor(f.datos.cantidad_usada)}"></td>
        <td><select class="report-input cs-eq-input cs-select-cobro" data-eq-serie="${s}" data-campo="codigo_cobro">
          <option value="COMPLETO" ${f.datos.codigo_cobro === 'COMPLETO' ? 'selected' : ''}>Cobro completo</option>
          <option value="STANDBY" ${f.datos.codigo_cobro === 'STANDBY' ? 'selected' : ''}>Stand-by</option>
          <option value="SIN_COBRO" ${f.datos.codigo_cobro === 'SIN_COBRO' ? 'selected' : ''}>Sin cobro</option>
        </select></td>
        <td class="cs-centro"><input type="checkbox" class="cs-eq-input" data-eq-serie="${s}" data-campo="es_fluidos" ${f.datos.es_fluidos ? 'checked' : ''}></td>
        <td class="cs-num">${csDinero(f.tarifa)}${tarifaNueva ? ` <span class="cs-tenue" title="La tarifa actual del pozo es distinta; este día conserva la tarifa con la que se registró">(pozo: ${csDinero(f.tarifas_pozo[f.datos.codigo_cobro])})</span>` : ''}</td>
        <td class="cs-num cs-final" data-eq-dia="${s}">${csDinero(dia)}</td>
        <td class="cs-num" data-eq-acum="${s}">${csDinero((f.previo.costo || 0) + dia)}</td>
      </tr>`;
    }).join('');
  }

  csEqRenderCostosTotales();
}

function csEqRenderCostosTotales(){
  let totalDia = 0, totalAcum = 0, fluDia = 0, fluAcum = 0;
  csEqDatos.equipos.forEach(f => {
    const dia = csCostoDiario(f);
    const acum = (f.previo.costo || 0) + dia;
    totalDia += dia; totalAcum += acum;
    if(f.datos.es_fluidos){ fluDia += dia; fluAcum += acum; }
    const celdaDia = document.querySelector(`[data-eq-dia="${CSS.escape(f.serie)}"]`);
    if(celdaDia) celdaDia.textContent = csDinero(dia);
    const celdaAcum = document.querySelector(`[data-eq-acum="${CSS.escape(f.serie)}"]`);
    if(celdaAcum) celdaAcum.textContent = csDinero(acum);
  });
  document.getElementById('csEqCostosPie').innerHTML = `
    <tr class="cs-fila-total cs-fila-subtotal"><td colspan="6">Fluidos de perforación</td>
      <td class="cs-num">${csDinero(fluDia)}</td><td class="cs-num">${csDinero(fluAcum)}</td></tr>
    <tr class="cs-fila-total"><td colspan="6">Total</td>
      <td class="cs-num">${csDinero(totalDia)}</td><td class="cs-num">${csDinero(totalAcum)}</td></tr>`;
}

/* ---------- Uso y paradas ---------- */

function csEqRenderUso(){
  const tbody = document.getElementById('csEqUso');
  const filas = csEqDatos.equipos;
  if(!filas.length){
    tbody.innerHTML = '<tr class="cs-fila-vacia"><td colspan="5">El pozo no tiene equipos activos.</td></tr>';
    return;
  }
  tbody.innerHTML = filas.map(f => {
    const s = csEsc(f.serie);
    return `<tr>
      <td class="cs-codigo">${s}</td>
      <td>${csEsc(f.descripcion)}</td>
      <td class="cs-num">${csFmt(csNum(f.datos.horas))}</td>
      <td class="cs-num"><input type="number" class="cs-input-cant cs-eq-input" min="0" max="48" step="0.25" data-eq-serie="${s}" data-campo="horas_parada" value="${csValor(f.datos.horas_parada)}"></td>
      <td><input type="text" class="report-input cs-eq-input cs-input-obs" maxlength="500" data-eq-serie="${s}" data-campo="observaciones" value="${csEsc(f.datos.observaciones || '')}" placeholder="Ej.: cambio de rodamientos, espera de repuesto"></td>
    </tr>`;
  }).join('');
}

/* ---------- Guardar ---------- */

async function guardarUsoEquipos(silent = false){
  if(!csEqListo){
    if(!silent) showToast('El detalle de equipos todavía no terminó de cargar.', false);
    return;
  }
  const payload = {
    equipos: csEqDatos.equipos.map(f => Object.assign({ serie: f.serie, propiedades: f.propiedades }, f.datos))
  };
  try {
    const res = await fetch(CS_BASE + 'equipos/guardar/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if(data.ok){
      csEqAplicar(data);
      if(!silent) showToast(data.mensaje || 'Detalle de equipos guardado.');
    } else {
      showToast(data.error || 'No se pudo guardar el detalle de equipos.', false);
    }
  } catch(e){
    showToast('Error de conexión al guardar el detalle de equipos.', false);
  }
}

/* ---------- Eventos ---------- */

document.addEventListener('DOMContentLoaded', function(){
  const vista = document.getElementById('csVistaEquipos');
  if(!vista) return;

  document.querySelectorAll('.cs-eq-tab').forEach(b =>
    b.addEventListener('click', () => csEqCambiarVista(b.dataset.eqVista)));
  document.getElementById('csEqGuardar').addEventListener('click', () => guardarUsoEquipos());
  document.getElementById('csEqSoloFluidos').addEventListener('change', csEqRenderCostos);

  vista.addEventListener('click', function(ev){
    const item = ev.target.closest('.cs-arbol-item, .cs-fila-click');
    if(item && item.dataset.eqSerie){
      csEqSel = item.dataset.eqSerie;
      csEqRenderArbol();
      csEqRenderFicha();
    }
  });

  function actualizarCampo(el, alTerminar){
    const fila = csEqFila(el.dataset.eqSerie);
    if(!fila) return;
    if(el.classList.contains('cs-eq-prop')){
      fila.propiedades[parseInt(el.dataset.prop, 10)].valor = el.value;
      csMarcarSucio();
      return;
    }
    const campo = el.dataset.campo;
    if(!campo) return;
    let valor;
    if(el.type === 'checkbox') valor = el.checked;
    else if(campo === 'tipo_perdida_codigo') valor = el.value ? parseInt(el.value, 10) : null;
    else if(campo === 'codigo_cobro' || campo === 'observaciones') valor = el.value;
    else valor = el.value === '' ? null : el.value;
    fila.datos[campo] = valor;
    if(campo === 'codigo_cobro'){
      // Al cambiar el código, la tarifa pasa a la vigente del pozo para ese código.
      fila.tarifa = valor === 'SIN_COBRO' ? 0 : (fila.tarifas_pozo ? (fila.tarifas_pozo[valor] || 0) : fila.tarifa);
    }
    csMarcarSucio();
    if(alTerminar) alTerminar(campo);
  }

  // Mientras se escribe solo se recalculan resultados y totales: el campo activo no se redibuja.
  vista.addEventListener('input', function(ev){
    const el = ev.target;
    if(el.tagName === 'SELECT' || el.type === 'checkbox') return;  // esos se atienden en 'change'
    if(!el.classList.contains('cs-eq-input') && !el.classList.contains('cs-eq-prop')) return;
    actualizarCampo(el, function(){
      csEqRenderAvisos();
      if(csEqVista === 'rendimiento'){
        csEqRenderResultados();
        csEqRenderResumen();
      } else if(csEqVista === 'costos'){
        csEqRenderCostosTotales();
      }
    });
  });

  vista.addEventListener('change', function(ev){
    const el = ev.target;
    if(el.tagName === 'SELECT' || el.type === 'checkbox'){
      if(!el.classList.contains('cs-eq-input')) return;
      actualizarCampo(el, function(){ csEqRenderTodo(); });
    } else if(el.classList.contains('cs-eq-input') && el.dataset.campo === 'horas'){
      csEqRenderArbol();
    }
  });
});
