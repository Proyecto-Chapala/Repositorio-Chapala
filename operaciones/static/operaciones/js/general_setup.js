/* ============================================================
   general_setup.js — Configuración General
   (Setup + Warehouse Code Setup + Time Distribution Setup)
   ============================================================ */

(function () {
  'use strict';

  const state = {
    almacenes: [],
    distribucion: [],
    tipoDistribucionChoices: [],
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

  /* ---------- Bloque principal: Setup ---------- */

  async function cargarGeneralSetup() {
    const data = await apiFetch(`/api/pozos/${window.POZO_ID}/general-setup/`);
    const s = data.general_setup;
    document.getElementById('chipMonedaSimbolo').textContent = s.moneda_simbolo;
    document.getElementById('chipMonedaDecimales').textContent = s.moneda_decimales;
    document.getElementById('inputTasaImpuesto').value = s.tasa_impuesto;
    document.getElementById('inputConTratamiento').checked = s.con_tratamiento_disposicion;
    document.getElementById('inputUsarApi5ta').checked = s.usar_api_5ta_edicion_hidraulica;

    const selAgua = document.getElementById('selectEcuacionAgua');
    const selAceite = document.getElementById('selectEcuacionAceite');
    selAgua.innerHTML = '';
    selAceite.innerHTML = '';
    data.ecuacion_solidos_choices.forEach(([valor, label]) => {
      selAgua.innerHTML += `<option value="${valor}" ${valor === s.ecuacion_solidos_base_agua ? 'selected' : ''}>${label}</option>`;
      selAceite.innerHTML += `<option value="${valor}" ${valor === s.ecuacion_solidos_base_aceite ? 'selected' : ''}>${label}</option>`;
    });
  }

  async function guardarGeneralSetup() {
    document.getElementById('errorGeneralSetup').textContent = '';
    const payload = {
      tasa_impuesto: parseFloat(document.getElementById('inputTasaImpuesto').value || '0'),
      con_tratamiento_disposicion: document.getElementById('inputConTratamiento').checked,
      usar_api_5ta_edicion_hidraulica: document.getElementById('inputUsarApi5ta').checked,
      ecuacion_solidos_base_agua: document.getElementById('selectEcuacionAgua').value,
      ecuacion_solidos_base_aceite: document.getElementById('selectEcuacionAceite').value,
    };
    try {
      await apiFetch(`/api/pozos/${window.POZO_ID}/general-setup/guardar/`, {
        method: 'POST', body: JSON.stringify(payload),
      });
      showToast('Configuración General guardada.', 'success');
    } catch (err) {
      document.getElementById('errorGeneralSetup').textContent = (err.data && err.data.error) || 'Error al guardar.';
    }
  }

  /* ---------- Modal: Warehouse Code Setup ---------- */

  function renderAlmacenes() {
    const tbody = document.getElementById('almacenesBody');
    tbody.innerHTML = '';
    state.almacenes.forEach((a, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><input type="text" class="a-codigo" value="${a.codigo || ''}"></td>
        <td><input type="text" class="a-nombre" value="${a.nombre || ''}"></td>
        <td><button type="button" class="btn-remove-row" data-idx="${idx}" title="Eliminar">&times;</button></td>
      `;
      tr.querySelector('.btn-remove-row').addEventListener('click', () => {
        state.almacenes.splice(idx, 1);
        renderAlmacenes();
      });
      tbody.appendChild(tr);
    });
  }

  async function cargarAlmacenes() {
    const data = await apiFetch(`/api/pozos/${window.POZO_ID}/almacenes/`);
    state.almacenes = data.almacenes;
    renderAlmacenes();
  }

  async function guardarAlmacenes() {
    document.getElementById('errorAlmacenes').textContent = '';
    const filas = [];
    document.querySelectorAll('#almacenesBody tr').forEach((tr) => {
      filas.push({
        codigo: tr.querySelector('.a-codigo').value,
        nombre: tr.querySelector('.a-nombre').value,
      });
    });
    try {
      await apiFetch(`/api/pozos/${window.POZO_ID}/almacenes/guardar/`, {
        method: 'POST', body: JSON.stringify({ almacenes: filas }),
      });
      showToast('Códigos de almacén guardados.', 'success');
      await cargarAlmacenes();
    } catch (err) {
      document.getElementById('errorAlmacenes').textContent = (err.data && err.data.error) || 'Error al guardar.';
    }
  }

  /* ---------- Modal: Time Distribution Setup ---------- */

  function tipoOptionsHtml(seleccionado) {
    return state.tipoDistribucionChoices.map(([valor, label]) => (
      `<option value="${valor}" ${valor === seleccionado ? 'selected' : ''}>${label}</option>`
    )).join('');
  }

  function renderDistribucion() {
    const tbody = document.getElementById('distribucionBody');
    tbody.innerHTML = '';
    state.distribucion.forEach((d, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><input type="number" class="d-numero" value="${d.numero}"></td>
        <td><input type="text" class="d-descripcion" value="${d.descripcion || ''}"></td>
        <td><select class="d-tipo">${tipoOptionsHtml(d.tipo)}</select></td>
        <td><button type="button" class="btn-remove-row" data-idx="${idx}" title="Eliminar">&times;</button></td>
      `;
      tr.querySelector('.btn-remove-row').addEventListener('click', () => {
        state.distribucion.splice(idx, 1);
        renderDistribucion();
      });
      tbody.appendChild(tr);
    });
  }

  async function cargarDistribucion() {
    const data = await apiFetch(`/api/pozos/${window.POZO_ID}/tipos-distribucion/`);
    state.distribucion = data.tipos_distribucion;
    state.tipoDistribucionChoices = data.tipo_choices;
    renderDistribucion();
  }

  async function guardarDistribucion() {
    document.getElementById('errorDistribucion').textContent = '';
    const filas = [];
    document.querySelectorAll('#distribucionBody tr').forEach((tr) => {
      filas.push({
        numero: parseInt(tr.querySelector('.d-numero').value, 10),
        descripcion: tr.querySelector('.d-descripcion').value,
        tipo: tr.querySelector('.d-tipo').value,
      });
    });
    try {
      await apiFetch(`/api/pozos/${window.POZO_ID}/tipos-distribucion/guardar/`, {
        method: 'POST', body: JSON.stringify({ tipos_distribucion: filas }),
      });
      showToast('Time Distribution Setup guardado.', 'success');
      await cargarDistribucion();
    } catch (err) {
      document.getElementById('errorDistribucion').textContent = (err.data && err.data.error) || 'Error al guardar.';
    }
  }

  /* ---------- Init ---------- */

  document.addEventListener('DOMContentLoaded', async () => {
    document.getElementById('btnGuardarGeneralSetup').addEventListener('click', guardarGeneralSetup);

    document.getElementById('btnAbrirAlmacenes').addEventListener('click', async () => {
      document.getElementById('modalAlmacenes').hidden = false;
      try { await cargarAlmacenes(); } catch (err) { showToast('No se pudieron cargar los almacenes.', 'error'); }
    });
    document.getElementById('btnCerrarAlmacenes').addEventListener('click', () => {
      document.getElementById('modalAlmacenes').hidden = true;
    });
    document.getElementById('btnAgregarAlmacen').addEventListener('click', () => {
      state.almacenes.push({ codigo: '', nombre: '' });
      renderAlmacenes();
    });
    document.getElementById('btnGuardarAlmacenes').addEventListener('click', guardarAlmacenes);

    document.getElementById('btnAbrirDistribucion').addEventListener('click', async () => {
      document.getElementById('modalDistribucion').hidden = false;
      try { await cargarDistribucion(); } catch (err) { showToast('No se pudo cargar la distribución de tiempo.', 'error'); }
    });
    document.getElementById('btnCerrarDistribucion').addEventListener('click', () => {
      document.getElementById('modalDistribucion').hidden = true;
    });
    document.getElementById('btnAgregarDistribucion').addEventListener('click', () => {
      const siguiente = state.distribucion.length
        ? Math.max(...state.distribucion.map((d) => d.numero)) + 1 : 1;
      state.distribucion.push({ numero: siguiente, descripcion: '', tipo: state.tipoDistribucionChoices[0][0] });
      renderDistribucion();
    });
    document.getElementById('btnGuardarDistribucion').addEventListener('click', guardarDistribucion);

    try {
      await cargarGeneralSetup();
    } catch (err) {
      showToast('No se pudo cargar la Configuración General.', 'error');
    }
  });
})();
