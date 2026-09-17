/* ============================================================
   pits.js — Pit Information (Fosas + Pit Type Setup)
   ============================================================ */

(function () {
  'use strict';

  let fosaRowCount = 0;
  let tipoRowCount = 0;

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

  // --------- Fosas ---------
  function agregarFilaFosa(fosa) {
    fosa = fosa || { numero: '', descripcion: '', capacidad: '' };
    fosaRowCount += 1;
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="number" class="fosa-numero" value="${fosa.numero}"></td>
      <td><input type="text" class="fosa-descripcion" value="${fosa.descripcion}"></td>
      <td><input type="number" step="0.01" class="fosa-capacidad" value="${fosa.capacidad}"></td>
      <td><button type="button" class="btn-remove-row" aria-label="Eliminar fila">&times;</button></td>
    `;
    tr.querySelector('.btn-remove-row').addEventListener('click', () => tr.remove());
    document.getElementById('fosasBody').appendChild(tr);
  }

  async function guardarFosas() {
    const filas = Array.from(document.querySelectorAll('#fosasBody tr')).map((tr) => ({
      numero: parseInt(tr.querySelector('.fosa-numero').value, 10) || 0,
      descripcion: tr.querySelector('.fosa-descripcion').value.trim(),
      capacidad: parseFloat(tr.querySelector('.fosa-capacidad').value) || 0,
    }));

    try {
      await apiFetch(`/api/pozos/${window.POZO_ID}/pits/guardar/`, {
        method: 'POST',
        body: JSON.stringify({ fosas: filas }),
      });
      showToast('Fosas guardadas.', 'success');
    } catch (err) {
      showToast(err.data.error || 'Error al guardar las fosas.', 'error');
    }
  }

  // --------- Tipos de Fosa ---------
  function agregarFilaTipo(tipo) {
    tipo = tipo || { codigo: '', descripcion: '' };
    tipoRowCount += 1;
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="number" class="tipo-codigo" value="${tipo.codigo}"></td>
      <td><input type="text" class="tipo-descripcion" value="${tipo.descripcion}"></td>
      <td><button type="button" class="btn-remove-row" aria-label="Eliminar fila">&times;</button></td>
    `;
    tr.querySelector('.btn-remove-row').addEventListener('click', () => tr.remove());
    document.getElementById('tiposFosaBody').appendChild(tr);
  }

  async function guardarTipos() {
    const filas = Array.from(document.querySelectorAll('#tiposFosaBody tr')).map((tr) => ({
      codigo: parseInt(tr.querySelector('.tipo-codigo').value, 10) || 0,
      descripcion: tr.querySelector('.tipo-descripcion').value.trim(),
    }));

    try {
      await apiFetch(`/api/pozos/${window.POZO_ID}/pit-types/guardar/`, {
        method: 'POST',
        body: JSON.stringify({ tipos_fosa: filas }),
      });
      showToast('Pit Type Setup guardado.', 'success');
    } catch (err) {
      showToast(err.data.error || 'Error al guardar los tipos de fosa.', 'error');
    }
  }

  async function cargarDatos() {
    const data = await apiFetch(`/api/pozos/${window.POZO_ID}/pits/`);
    document.getElementById('fosasBody').innerHTML = '';
    document.getElementById('tiposFosaBody').innerHTML = '';
    data.fosas.forEach((f) => agregarFilaFosa(f));
    data.tipos_fosa.forEach((t) => agregarFilaTipo(t));
  }

  document.addEventListener('DOMContentLoaded', async () => {
    document.getElementById('btnAgregarFosa').addEventListener('click', () => agregarFilaFosa());
    document.getElementById('btnAgregarTipo').addEventListener('click', () => agregarFilaTipo());
    document.getElementById('btnGuardarFosas').addEventListener('click', guardarFosas);
    document.getElementById('btnGuardarTipos').addEventListener('click', guardarTipos);

    try {
      await cargarDatos();
    } catch (err) {
      showToast('No se pudo cargar Pit Information.', 'error');
    }
  });
})();
