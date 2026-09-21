/* ============================================================
   loss_setup.js — Configuración de Pérdidas (Loss Setup)
   ============================================================ */

(function () {
  'use strict';

  const state = {
    categorias: [],
    tipoChoices: [],
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

  function tipoOptionsHtml(seleccionado) {
    return state.tipoChoices.map(([valor, label]) => (
      `<option value="${valor}" ${valor === seleccionado ? 'selected' : ''}>${label}</option>`
    )).join('');
  }

  function renderTabla() {
    const tbody = document.getElementById('categoriasBody');
    tbody.innerHTML = '';
    state.categorias.forEach((c, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><input type="number" class="c-codigo" value="${c.codigo}"></td>
        <td><input type="text" class="c-descripcion" value="${c.descripcion || ''}"></td>
        <td>
          <select class="c-tipo">${tipoOptionsHtml(c.tipo)}</select>
        </td>
        <td><button type="button" class="btn-remove-row" data-idx="${idx}" title="Eliminar">&times;</button></td>
      `;
      tr.querySelector('.btn-remove-row').addEventListener('click', () => {
        state.categorias.splice(idx, 1);
        renderTabla();
      });
      tbody.appendChild(tr);
    });
  }

  function agregarFila() {
    const siguiente = state.categorias.length
      ? Math.max(...state.categorias.map((c) => c.codigo)) + 1 : 1;
    state.categorias.push({ codigo: siguiente, descripcion: '', tipo: state.tipoChoices[0][0] });
    renderTabla();
  }

  function leerFilas() {
    const filas = [];
    document.querySelectorAll('#categoriasBody tr').forEach((tr) => {
      filas.push({
        codigo: parseInt(tr.querySelector('.c-codigo').value, 10),
        descripcion: tr.querySelector('.c-descripcion').value,
        tipo: tr.querySelector('.c-tipo').value,
      });
    });
    return filas;
  }

  async function cargarCategorias() {
    const data = await apiFetch(`/api/pozos/${window.POZO_ID}/loss-setup/`);
    state.categorias = data.categorias;
    state.tipoChoices = data.tipo_choices;
    renderTabla();
  }

  async function guardarCategorias() {
    try {
      await apiFetch(`/api/pozos/${window.POZO_ID}/loss-setup/guardar/`, {
        method: 'POST',
        body: JSON.stringify({ categorias: leerFilas() }),
      });
      showToast('Categorías de pérdida guardadas.', 'success');
      await cargarCategorias();
    } catch (err) {
      showToast((err.data && err.data.error) || 'No se pudieron guardar las categorías.', 'error');
    }
  }

  document.addEventListener('DOMContentLoaded', async () => {
    document.getElementById('btnAgregarCategoria').addEventListener('click', agregarFila);
    document.getElementById('btnGuardarCategorias').addEventListener('click', guardarCategorias);

    try {
      await cargarCategorias();
    } catch (err) {
      showToast('No se pudieron cargar las categorías de pérdida.', 'error');
    }
  });
})();
