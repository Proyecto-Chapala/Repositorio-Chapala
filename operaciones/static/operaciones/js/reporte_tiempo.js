/* =====================================================================
   PESTAÑA 7 — DISTRIBUCIÓN DE TIEMPO (TIME DISTRIBUTION)

   Horas por actividad del taladro durante el período del reporte, según la
   hoja IADC. Las 4 actividades principales se muestran siempre; el resto se
   agregan desde el catálogo del pozo (Configuración General).

   El total se compara contra las "horas del período" (24 por defecto). Si no
   coincide se marca en rojo, pero se deja guardar: en campo hay días que no
   cuadran (primer o último día del pozo, cambio de hora de corte).

   Depende de las constantes y utilidades globales definidas en
   reporte_diario_detalle.html: POZO_ID, REPORTE_ID, getCookie, showToast.
   ===================================================================== */

const API_TIEMPO_DETAIL = `/api/pozos/${POZO_ID}/daily-report/${REPORTE_ID}/tiempo/`;
const API_TIEMPO_GUARDAR = `/api/pozos/${POZO_ID}/daily-report/${REPORTE_ID}/tiempo/guardar/`;

const TT_TOLERANCIA = 0.01;
const TT_COLORES = 10; // clases tt-color-0 … tt-color-9 en reporte_tiempo.css

let ttCargado = false;
// ttListo: los datos ya llegaron del servidor. Antes de eso guardar borraría las actividades.
let ttListo = false;
let ttFilas = [];     // [{tipo_numero, descripcion, horas, es_fija}]
let ttCatalogo = [];  // [{numero, descripcion}] actividades opcionales del pozo

/* ---------- Utilidades ---------- */

function ttNumero(valor){
  const n = parseFloat(String(valor ?? '').replace(',', '.'));
  return Number.isFinite(n) && n > 0 ? n : 0;
}

function ttFormato(n, decimales = 2){
  return Number(n || 0).toFixed(decimales);
}

function ttEscapar(texto){
  const div = document.createElement('div');
  div.textContent = texto == null ? '' : String(texto);
  return div.innerHTML;
}

function ttHorasPeriodo(){
  return ttNumero(document.getElementById('ttHorasPeriodo').value);
}

function ttTotal(){
  return ttFilas.reduce((acc, f) => acc + ttNumero(f.horas), 0);
}

/* ---------- Carga ---------- */

async function inicializarTiempo(){
  if(ttCargado) return;
  ttCargado = true;

  const panel = document.getElementById('tabContent-tiempo');
  const link = document.getElementById('ttLinkConfig');
  if(panel && link && panel.dataset.urlConfig) link.href = panel.dataset.urlConfig;

  try {
    const res = await fetch(API_TIEMPO_DETAIL);
    const data = await res.json();
    if(!data.ok) throw new Error(data.error || 'respuesta inválida');
    ttAplicarEstado(data);
    ttListo = true;
  } catch(e){
    ttCargado = false;
    document.getElementById('ttFilas').innerHTML =
      '<tr class="tt-fila-vacia"><td colspan="6">No se pudo cargar la distribución de tiempo.</td></tr>';
    showToast('No se pudo cargar la distribución de tiempo.', false);
  }
}

function ttAplicarEstado(data){
  ttFilas = (data.actividades || []).map(f => ({
    tipo_numero: f.tipo_numero,
    descripcion: f.descripcion,
    horas: f.horas ? ttFormato(f.horas) : '',
    es_fija: !!f.es_fija
  }));
  ttCatalogo = data.catalogo || [];
  document.getElementById('ttHorasPeriodo').value = ttFormato(data.horas_periodo ?? 24);
  ttRenderFilas();
}

/* ---------- Render de la tabla ---------- */

function ttOpcionesDisponibles(numeroActual){
  const usados = new Set(ttFilas.map(f => f.tipo_numero).filter(n => n !== numeroActual));
  return ttCatalogo.filter(c => !usados.has(c.numero));
}

function ttRenderFilas(){
  const tbody = document.getElementById('ttFilas');
  tbody.innerHTML = '';

  ttFilas.forEach(function(fila, i){
    const tr = document.createElement('tr');
    tr.className = fila.es_fija ? 'tt-fila-fija' : 'tt-fila-opcional';

    let celdaActividad;
    if(fila.es_fija){
      celdaActividad = `<span class="tt-actividad">${ttEscapar(fila.descripcion)}</span>`;
    } else {
      const opciones = ttOpcionesDisponibles(fila.tipo_numero);
      // Si la actividad guardada ya no está en el catálogo, se conserva como opción.
      const enCatalogo = opciones.some(o => o.numero === fila.tipo_numero);
      const lista = enCatalogo || fila.tipo_numero == null
        ? opciones
        : [{numero: fila.tipo_numero, descripcion: fila.descripcion}].concat(opciones);
      celdaActividad =
        `<select class="tt-select" data-i="${i}">` +
        (fila.tipo_numero == null ? '<option value="" selected disabled>Selecciona una actividad…</option>' : '') +
        lista.map(o =>
          `<option value="${o.numero}" ${o.numero === fila.tipo_numero ? 'selected' : ''}>${ttEscapar(o.descripcion)}</option>`
        ).join('') +
        `</select>`;
    }

    tr.innerHTML =
      `<td class="tt-col-color"><span class="tt-punto tt-color-${i % TT_COLORES}"></span></td>` +
      `<td>${celdaActividad}</td>` +
      `<td class="tt-col-horas"><input type="number" class="tt-input-horas" data-i="${i}" min="0" max="48" step="0.25" placeholder="0.00" value="${fila.horas}"></td>` +
      `<td class="tt-td-num tt-pct" data-i="${i}"></td>` +
      `<td class="tt-col-dist"><div class="tt-mini-barra"><span class="tt-mini-relleno tt-color-${i % TT_COLORES}" data-i="${i}"></span></div></td>` +
      `<td class="tt-col-acciones">` +
      (fila.es_fija
        ? ''
        : `<button type="button" class="tt-btn-quitar" data-i="${i}" title="Quitar actividad">&times;</button>`) +
      `</td>`;
    tbody.appendChild(tr);
  });

  const btnAgregar = document.getElementById('ttBtnAgregar');
  const quedan = ttOpcionesDisponibles(null).length > 0;
  const hayPendiente = ttFilas.some(f => f.tipo_numero == null);
  btnAgregar.disabled = !quedan || hayPendiente;
  btnAgregar.title = !quedan
    ? 'Ya se usaron todas las actividades del catálogo del pozo'
    : (hayPendiente ? 'Primero elige la actividad de la fila nueva' : 'Agregar otra actividad del catálogo del pozo');

  ttRecalcular();
}

/* ---------- Cálculo en vivo ---------- */

function ttRecalcular(){
  const periodo = ttHorasPeriodo();
  const total = ttTotal();
  const diferencia = total - periodo;
  const cuadra = periodo > 0 && Math.abs(diferencia) < TT_TOLERANCIA;

  document.getElementById('ttTotal').textContent = `${ttFormato(total)} h`;
  document.getElementById('ttTotal').classList.toggle('tt-valor-error', periodo > 0 && !cuadra);
  document.getElementById('ttTotalPie').textContent = ttFormato(total);
  document.getElementById('ttPctPie').textContent =
    periodo > 0 ? `${ttFormato(total / periodo * 100, 1)} %` : '—';

  const estado = document.getElementById('ttEstado');
  estado.classList.remove('tt-chip-ok', 'tt-chip-error', 'tt-chip-neutro');
  if(periodo <= 0){
    estado.classList.add('tt-chip-error');
    estado.textContent = 'Indica las horas del período';
  } else if(cuadra){
    estado.classList.add('tt-chip-ok');
    estado.textContent = 'Cuadra con el período';
  } else if(diferencia < 0){
    estado.classList.add('tt-chip-error');
    estado.textContent = `Faltan ${ttFormato(-diferencia)} h`;
  } else {
    estado.classList.add('tt-chip-error');
    estado.textContent = `Sobran ${ttFormato(diferencia)} h`;
  }

  const pie = document.querySelector('.tt-fila-total');
  if(pie) pie.classList.toggle('tt-total-error', periodo > 0 && !cuadra);

  // Porcentaje y mini barra de cada fila (sobre el período, o sobre el total si se pasa).
  const base = Math.max(periodo, total) || 1;
  ttFilas.forEach(function(fila, i){
    const horas = ttNumero(fila.horas);
    const pct = document.querySelector(`.tt-pct[data-i="${i}"]`);
    if(pct) pct.textContent = horas > 0 && periodo > 0 ? `${ttFormato(horas / periodo * 100, 1)} %` : '';
    const relleno = document.querySelector(`.tt-mini-relleno[data-i="${i}"]`);
    if(relleno) relleno.style.width = `${Math.min(horas / base * 100, 100)}%`;
  });

  ttRenderBarra(periodo, total);
}

function ttRenderBarra(periodo, total){
  const barra = document.getElementById('ttBarra');
  const leyenda = document.getElementById('ttLeyenda');
  const base = Math.max(periodo, total) || 1;

  let segmentos = '';
  let items = '';
  ttFilas.forEach(function(fila, i){
    const horas = ttNumero(fila.horas);
    if(horas <= 0 || fila.tipo_numero == null) return;
    const titulo = `${fila.descripcion}: ${ttFormato(horas)} h`;
    segmentos += `<span class="tt-segmento tt-color-${i % TT_COLORES}" style="flex-grow:${horas}" title="${ttEscapar(titulo)}"></span>`;
    items += `<span class="tt-leyenda-item"><span class="tt-punto tt-color-${i % TT_COLORES}"></span>${ttEscapar(fila.descripcion)} <strong>${ttFormato(horas)} h</strong></span>`;
  });

  const faltante = periodo - total;
  if(faltante >= TT_TOLERANCIA){
    segmentos += `<span class="tt-segmento tt-segmento-faltante" style="flex-grow:${faltante}" title="Sin registrar: ${ttFormato(faltante)} h"></span>`;
    items += `<span class="tt-leyenda-item tt-leyenda-faltante"><span class="tt-punto tt-punto-faltante"></span>Sin registrar <strong>${ttFormato(faltante)} h</strong></span>`;
  }

  // El ancho total de la barra representa el mayor entre el período y lo registrado.
  barra.innerHTML = segmentos || '<span class="tt-segmento tt-segmento-faltante" style="flex-grow:1"></span>';
  barra.classList.toggle('tt-barra-excedida', total - periodo >= TT_TOLERANCIA);
  barra.style.setProperty('--tt-ancho-periodo', `${Math.min(periodo / base * 100, 100)}%`);
  leyenda.innerHTML = items || '<span class="tt-leyenda-vacia">Todavía no hay horas registradas.</span>';
}

/* ---------- Guardar ---------- */

async function guardarTiempo(silent = false){
  if(!ttListo){
    if(!silent) showToast('La distribución de tiempo todavía no terminó de cargar. Espera un momento o recarga la página.', false);
    return;
  }

  const payload = {
    horas_periodo: document.getElementById('ttHorasPeriodo').value,
    actividades: ttFilas
      .filter(f => f.tipo_numero != null)
      .map(f => ({ tipo_numero: f.tipo_numero, horas: f.horas }))
  };

  try {
    const res = await fetch(API_TIEMPO_GUARDAR, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if(data.ok){
      ttAplicarEstado(data);
      if(!silent){
        showToast(data.cuadra
          ? 'Distribución de tiempo guardada correctamente'
          : 'Guardado. Ojo: el total no coincide con las horas del período', data.cuadra);
      }
    } else {
      showToast(data.error || 'Error al guardar la distribución de tiempo', false);
    }
  } catch(e){
    showToast('Error de conexión al guardar la distribución de tiempo', false);
  }
}

/* ---------- Eventos ---------- */

document.addEventListener('DOMContentLoaded', function(){
  const tbody = document.getElementById('ttFilas');
  if(!tbody) return;

  tbody.addEventListener('input', function(ev){
    const el = ev.target;
    if(!el.classList.contains('tt-input-horas')) return;
    const fila = ttFilas[parseInt(el.dataset.i, 10)];
    if(fila){
      fila.horas = el.value;
      ttRecalcular();
    }
  });

  tbody.addEventListener('change', function(ev){
    const el = ev.target;
    if(el.classList.contains('tt-select')){
      const fila = ttFilas[parseInt(el.dataset.i, 10)];
      const numero = parseInt(el.value, 10);
      const item = ttCatalogo.find(c => c.numero === numero);
      if(fila && item){
        fila.tipo_numero = item.numero;
        fila.descripcion = item.descripcion;
        ttRenderFilas();
      }
    } else if(el.classList.contains('tt-input-horas') && el.value !== ''){
      el.value = ttFormato(ttNumero(el.value));
      const fila = ttFilas[parseInt(el.dataset.i, 10)];
      if(fila) fila.horas = el.value;
    }
  });

  tbody.addEventListener('click', function(ev){
    const btn = ev.target.closest('.tt-btn-quitar');
    if(!btn) return;
    ttFilas.splice(parseInt(btn.dataset.i, 10), 1);
    ttRenderFilas();
  });

  document.getElementById('ttBtnAgregar').addEventListener('click', function(){
    ttFilas.push({ tipo_numero: null, descripcion: '', horas: '', es_fija: false });
    ttRenderFilas();
    const selects = tbody.querySelectorAll('.tt-select');
    if(selects.length) selects[selects.length - 1].focus();
  });

  const periodo = document.getElementById('ttHorasPeriodo');
  periodo.addEventListener('input', ttRecalcular);
  periodo.addEventListener('change', function(){
    if(periodo.value !== '') periodo.value = ttFormato(ttNumero(periodo.value));
    ttRecalcular();
  });
});
