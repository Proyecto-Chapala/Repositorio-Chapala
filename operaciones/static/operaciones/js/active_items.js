/* ============================================================
   active_items.js — Productos / Equipos / Mallas Activos
   ============================================================ */

(function () {
  'use strict';

  const state = {
    productosActivos: [],
    equiposActivos: [],
    mallasActivas: [],
  };

  function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
  }

  async function apiFetch(url, options = {}) {
    const opts = Object.assign({ headers: {} }, options);
    opts.headers['Content-Type'] = 'application/json';
    opts.headers['X-CSRFToken'] = getCookie('csrftoken');
    const res = await fetch(url, opts);
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw { data, status: res.status };
    }
    return data;
  }

  function showToast(mensaje, tipo) {
    const container = document.getElementById('toastContainer');
    if (!container) { window.alert(mensaje); return; }
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + (tipo || 'info');
    toast.textContent = mensaje;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  }

  function debounce(fn, ms) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), ms);
    };
  }

  /* ---------- Tabs ---------- */

  function initTabs() {
    document.querySelectorAll('.tab-nav-item').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-nav-item').forEach((b) => b.classList.remove('is-active'));
        document.querySelectorAll('.tab-panel').forEach((p) => { p.hidden = true; });
        btn.classList.add('is-active');
        document.querySelector(`.tab-panel[data-tab="${btn.dataset.tab}"]`).hidden = false;
      });
    });
  }

  /* ---------- Pestaña 1: Productos ---------- */

  async function buscarProductos(texto) {
    const data = await apiFetch(`/api/productos/?search=${encodeURIComponent(texto || '')}`);
    const tbody = document.getElementById('masterProductosBody');
    tbody.innerHTML = '';
    data.productos.slice(0, 50).forEach((p) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${p.codigo}</td><td>${p.descripcion}</td><td>${p.unidad || ''}</td>
        <td><button type="button" class="btn-add-row" title="Agregar a la lista activa">+</button></td>
      `;
      tr.querySelector('.btn-add-row').addEventListener('click', () => agregarProductoActivo(p));
      tbody.appendChild(tr);
    });
  }

  function agregarProductoActivo(p) {
    state.productosActivos.push({
      producto_id: p.id, producto_codigo: p.codigo, producto_nombre: p.descripcion,
      abreviatura: '', unit_size: p.libraje, unidad: p.unidad, empaque: '',
      precio: p.costo, gravedad_especifica: p.gravedad,
      calcular_concentracion: true, es_producto_mi: true, grupo_producto: 1,
      codigo_costo_diario: 1, calcular_wmgt_conc: true,
      categoria_costo_wmgt: 1, categoria_costo_cf: 1,
    });
    renderProductosActivos();
  }

  function renderProductosActivos() {
    const tbody = document.getElementById('activosProductosBody');
    tbody.innerHTML = '';
    state.productosActivos.forEach((item, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${item.producto_codigo}</td>
        <td>${item.producto_nombre}</td>
        <td><input type="text" class="p-abrev" value="${item.abreviatura || ''}"></td>
        <td><input type="number" step="0.01" class="p-unitsize" value="${item.unit_size ?? ''}"></td>
        <td><input type="text" class="p-unidad" value="${item.unidad || ''}"></td>
        <td><input type="text" class="p-empaque" value="${item.empaque || ''}"></td>
        <td><input type="number" step="0.01" class="p-precio" value="${item.precio ?? ''}"></td>
        <td><input type="number" step="0.0001" class="p-sg" value="${item.gravedad_especifica ?? ''}"></td>
        <td style="text-align:center;"><input type="checkbox" class="p-conc" ${item.calcular_concentracion ? 'checked' : ''}></td>
        <td style="text-align:center;"><input type="checkbox" class="p-mi" ${item.es_producto_mi ? 'checked' : ''}></td>
        <td><input type="number" class="p-grupo" value="${item.grupo_producto}"></td>
        <td><input type="number" class="p-costodiario" value="${item.codigo_costo_diario}"></td>
        <td style="text-align:center;"><input type="checkbox" class="p-wmgt" ${item.calcular_wmgt_conc ? 'checked' : ''}></td>
        <td><input type="number" class="p-catwmgt" value="${item.categoria_costo_wmgt}"></td>
        <td><input type="number" class="p-catcf" value="${item.categoria_costo_cf}"></td>
        <td><button type="button" class="btn-remove-row" data-idx="${idx}" title="Eliminar">&times;</button></td>
      `;
      tr.querySelector('.btn-remove-row').addEventListener('click', () => {
        state.productosActivos.splice(idx, 1);
        renderProductosActivos();
      });
      tbody.appendChild(tr);
    });
  }

  function leerProductosActivos() {
    const filas = [];
    document.querySelectorAll('#activosProductosBody tr').forEach((tr, idx) => {
      const original = state.productosActivos[idx];
      filas.push({
        producto_id: original.producto_id,
        abreviatura: tr.querySelector('.p-abrev').value,
        unit_size: tr.querySelector('.p-unitsize').value || null,
        unidad: tr.querySelector('.p-unidad').value,
        empaque: tr.querySelector('.p-empaque').value,
        precio: tr.querySelector('.p-precio').value || null,
        gravedad_especifica: tr.querySelector('.p-sg').value || null,
        calcular_concentracion: tr.querySelector('.p-conc').checked,
        es_producto_mi: tr.querySelector('.p-mi').checked,
        grupo_producto: tr.querySelector('.p-grupo').value || 1,
        codigo_costo_diario: tr.querySelector('.p-costodiario').value || 1,
        calcular_wmgt_conc: tr.querySelector('.p-wmgt').checked,
        categoria_costo_wmgt: tr.querySelector('.p-catwmgt').value || 1,
        categoria_costo_cf: tr.querySelector('.p-catcf').value || 1,
      });
    });
    return filas;
  }

  async function cargarProductosActivos() {
    const data = await apiFetch(`/api/pozos/${window.POZO_ID}/productos-activos/`);
    state.productosActivos = data.productos_activos;
    renderProductosActivos();
  }

  async function guardarProductosActivos() {
    try {
      await apiFetch(`/api/pozos/${window.POZO_ID}/productos-activos/guardar/`, {
        method: 'POST', body: JSON.stringify({ productos_activos: leerProductosActivos() }),
      });
      showToast('Productos Activos guardados.', 'success');
      await cargarProductosActivos();
    } catch (err) {
      showToast((err.data && err.data.error) || 'No se pudieron guardar los productos activos.', 'error');
    }
  }

  /* ---------- Pestaña 2: Equipos ---------- */

  async function buscarEquipos(texto) {
    const data = await apiFetch(`/api/equipos/?search=${encodeURIComponent(texto || '')}`);
    const tbody = document.getElementById('masterEquiposBody');
    tbody.innerHTML = '';
    data.equipos.slice(0, 50).forEach((e) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${e.codigo}</td><td>${e.nombre}</td>
        <td><button type="button" class="btn-add-row" title="Agregar a la lista activa">+</button></td>
      `;
      tr.querySelector('.btn-add-row').addEventListener('click', () => agregarEquipoActivo(e));
      tbody.appendChild(tr);
    });
  }

  function agregarEquipoActivo(e) {
    state.equiposActivos.push({
      equipo_id: e.id, equipo_codigo: e.codigo, equipo_nombre: e.nombre,
      numero_serie: '', descripcion: e.nombre, precio_renta: 0, precio_standby: 0,
    });
    renderEquiposActivos();
  }

  function renderEquiposActivos() {
    const tbody = document.getElementById('activosEquiposBody');
    tbody.innerHTML = '';
    state.equiposActivos.forEach((item, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${item.equipo_codigo}</td>
        <td><input type="text" class="e-serie" value="${item.numero_serie || ''}"></td>
        <td><input type="text" class="e-desc" value="${item.descripcion || ''}"></td>
        <td><input type="number" step="0.01" class="e-renta" value="${item.precio_renta}"></td>
        <td><input type="number" step="0.01" class="e-standby" value="${item.precio_standby}"></td>
        <td><button type="button" class="btn-remove-row" data-idx="${idx}" title="Eliminar">&times;</button></td>
      `;
      tr.querySelector('.btn-remove-row').addEventListener('click', () => {
        state.equiposActivos.splice(idx, 1);
        renderEquiposActivos();
      });
      tbody.appendChild(tr);
    });
  }

  function leerEquiposActivos() {
    const filas = [];
    document.querySelectorAll('#activosEquiposBody tr').forEach((tr, idx) => {
      const original = state.equiposActivos[idx];
      filas.push({
        equipo_id: original.equipo_id,
        numero_serie: tr.querySelector('.e-serie').value,
        descripcion: tr.querySelector('.e-desc').value,
        precio_renta: tr.querySelector('.e-renta').value || 0,
        precio_standby: tr.querySelector('.e-standby').value || 0,
      });
    });
    return filas;
  }

  async function cargarEquiposActivos() {
    const data = await apiFetch(`/api/pozos/${window.POZO_ID}/equipos-activos/`);
    state.equiposActivos = data.equipos_activos;
    renderEquiposActivos();
  }

  async function guardarEquiposActivos() {
    try {
      await apiFetch(`/api/pozos/${window.POZO_ID}/equipos-activos/guardar/`, {
        method: 'POST', body: JSON.stringify({ equipos_activos: leerEquiposActivos() }),
      });
      showToast('Equipos Activos guardados.', 'success');
      await cargarEquiposActivos();
    } catch (err) {
      showToast((err.data && err.data.error) || 'No se pudieron guardar los equipos activos.', 'error');
    }
  }

  /* ---------- Pestaña 3: Mallas ---------- */

  async function buscarMallas(texto) {
    const data = await apiFetch(`/api/mallas/?search=${encodeURIComponent(texto || '')}`);
    const tbody = document.getElementById('masterMallasBody');
    tbody.innerHTML = '';
    data.mallas.slice(0, 50).forEach((m) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${m.codigo}</td><td>${m.descripcion}</td><td>${m.mesh_size}</td>
        <td><button type="button" class="btn-add-row" title="Agregar a la lista activa">+</button></td>
      `;
      tr.querySelector('.btn-add-row').addEventListener('click', () => agregarMallaActiva(m));
      tbody.appendChild(tr);
    });
  }

  function agregarMallaActiva(m) {
    state.mallasActivas.push({
      malla_id: m.id, malla_codigo: m.codigo, malla_descripcion: m.descripcion,
      mesh_size: m.mesh_size, precio: 0, descuento_porcentaje: 0,
    });
    renderMallasActivas();
  }

  function renderMallasActivas() {
    const tbody = document.getElementById('activosMallasBody');
    tbody.innerHTML = '';
    state.mallasActivas.forEach((item, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${item.malla_codigo}</td>
        <td>${item.malla_descripcion}</td>
        <td>${item.mesh_size}</td>
        <td><input type="number" step="0.01" class="m-precio" value="${item.precio}"></td>
        <td><input type="number" step="0.01" class="m-descuento" value="${item.descuento_porcentaje}"></td>
        <td><button type="button" class="btn-remove-row" data-idx="${idx}" title="Eliminar">&times;</button></td>
      `;
      tr.querySelector('.btn-remove-row').addEventListener('click', () => {
        state.mallasActivas.splice(idx, 1);
        renderMallasActivas();
      });
      tbody.appendChild(tr);
    });
  }

  function leerMallasActivas() {
    const filas = [];
    document.querySelectorAll('#activosMallasBody tr').forEach((tr, idx) => {
      const original = state.mallasActivas[idx];
      filas.push({
        malla_id: original.malla_id,
        precio: tr.querySelector('.m-precio').value || 0,
        descuento_porcentaje: tr.querySelector('.m-descuento').value || 0,
      });
    });
    return filas;
  }

  async function cargarMallasActivas() {
    const data = await apiFetch(`/api/pozos/${window.POZO_ID}/mallas-activas/`);
    state.mallasActivas = data.mallas_activas;
    renderMallasActivas();
  }

  async function guardarMallasActivas() {
    try {
      await apiFetch(`/api/pozos/${window.POZO_ID}/mallas-activas/guardar/`, {
        method: 'POST', body: JSON.stringify({ mallas_activas: leerMallasActivas() }),
      });
      showToast('Mallas Activas guardadas.', 'success');
      await cargarMallasActivas();
    } catch (err) {
      showToast((err.data && err.data.error) || 'No se pudieron guardar las mallas activas.', 'error');
    }
  }

  /* ---------- Init ---------- */

  document.addEventListener('DOMContentLoaded', async () => {
    initTabs();

    const buscarProductosDeb = debounce((v) => buscarProductos(v), 250);
    document.getElementById('buscarProducto').addEventListener('input', (ev) => buscarProductosDeb(ev.target.value));
    document.getElementById('btnGuardarProductos').addEventListener('click', guardarProductosActivos);

    const buscarEquiposDeb = debounce((v) => buscarEquipos(v), 250);
    document.getElementById('buscarEquipo').addEventListener('input', (ev) => buscarEquiposDeb(ev.target.value));
    document.getElementById('btnGuardarEquipos').addEventListener('click', guardarEquiposActivos);

    const buscarMallasDeb = debounce((v) => buscarMallas(v), 250);
    document.getElementById('buscarMalla').addEventListener('input', (ev) => buscarMallasDeb(ev.target.value));
    document.getElementById('btnGuardarMallas').addEventListener('click', guardarMallasActivas);

    try {
      await Promise.all([
        buscarProductos(''), cargarProductosActivos(),
        buscarEquipos(''), cargarEquiposActivos(),
        buscarMallas(''), cargarMallasActivas(),
      ]);
    } catch (err) {
      showToast('No se pudo cargar la información de Productos/Equipos/Mallas.', 'error');
    }
  });
})();
