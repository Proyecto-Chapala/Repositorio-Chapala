/* =====================================================================
   PESTAÑA 8 — INVENTARIO / HIDRÁULICA / CONCENTRACIONES

   Por ahora solo "Pérdidas del reporte" (Daily Loss Print Selection):
   qué categorías de pérdida (máximo 10, en orden) muestra el reporte
   diario. La selección es del pozo, no del día.

   Depende de las utilidades globales de reporte_diario_detalle.html:
   POZO_ID, getCookie, showToast.
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
