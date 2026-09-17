/* ============================================================
   casing_intervals.js — Well Casing Intervals (Cost)
   ============================================================ */

(function () {
  'use strict';

  const state = {
    intervalos: [],
    tipoChoices: [],
    editandoId: null,
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

  function fmt(v) {
    return (v === null || v === undefined || v === '') ? '—' : v;
  }

  function renderTabla() {
    const tbody = document.getElementById('intervalosBody');
    tbody.innerHTML = '';
    document.getElementById('emptyHint').hidden = state.intervalos.length > 0;

    state.intervalos.forEach((i) => {
      const tr = document.createElement('tr');
      tr.style.cursor = 'pointer';
      tr.innerHTML = `
        <td>${i.numero_intervalo}</td>
        <td>${i.tipo_display || '—'}</td>
        <td>${fmt(i.casing_od_in)}</td>
        <td>${fmt(i.casing_id_in)}</td>
        <td>${fmt(i.profundidad_ft)}</td>
        <td>${fmt(i.tvd_ft)}</td>
        <td>${fmt(i.top_of_liner_ft)}</td>
        <td>${fmt(i.hole_size_in)}</td>
        <td>${fmt(i.maximum_angle)}</td>
        <td>${fmt(i.maximum_density_lb_gal)}</td>
        <td>${fmt(i.frac_grad_lb_gal)}</td>
        <td>${i.fluid_type_code_1 || '—'}</td>
        <td>${i.fluid_type_code_2 || '—'}</td>
        <td>${fmt(i.interval_cost)}</td>
        <td><button type="button" class="btn-remove-row" data-id="${i.id}" title="Eliminar">&times;</button></td>
      `;
      tr.addEventListener('click', (ev) => {
        if (ev.target.closest('.btn-remove-row')) return;
        abrirDetalle(i);
      });
      tr.querySelector('.btn-remove-row').addEventListener('click', (ev) => {
        ev.stopPropagation();
        eliminarIntervalo(i.id, i.numero_intervalo);
      });
      tbody.appendChild(tr);
    });
  }

  function renderTipoOptions() {
    const select = document.getElementById('dTipo');
    select.innerHTML = '<option value="">—</option>';
    state.tipoChoices.forEach(([valor, label]) => {
      const opt = document.createElement('option');
      opt.value = valor;
      opt.textContent = label;
      select.appendChild(opt);
    });
  }

  function limpiarDetalle() {
    ['dInterval', 'dCasingOd', 'dCasingId', 'dHoleSize', 'dDepth', 'dTvd', 'dTopLiner',
      'dMaxDensity', 'dMaxBht', 'dMaxAngle', 'dIntervalDays', 'dPlannedDays',
      'dPlannedLength', 'dIntervalCost', 'dPlannedCost', 'dFracGrad', 'dFluid1', 'dFluid2']
      .forEach((id) => { document.getElementById(id).value = ''; });
    document.getElementById('dTipo').value = '';
    document.getElementById('dObservaciones').value = '';
    document.getElementById('dComentariosRecap').value = '';
    document.getElementById('charCount').textContent = '0';
    document.getElementById('errorDetalle').textContent = '';
  }

  function abrirDetalle(intervalo) {
    limpiarDetalle();
    state.editandoId = intervalo ? intervalo.id : null;
    document.getElementById('detailTitle').textContent = intervalo
      ? `Intervalo ${intervalo.numero_intervalo}` : 'Nuevo Intervalo';
    document.getElementById('btnEliminarIntervalo').hidden = !intervalo;

    if (intervalo) {
      document.getElementById('dInterval').value = intervalo.numero_intervalo;
      document.getElementById('dTipo').value = intervalo.tipo || '';
      document.getElementById('dCasingOd').value = intervalo.casing_od_in ?? '';
      document.getElementById('dCasingId').value = intervalo.casing_id_in ?? '';
      document.getElementById('dHoleSize').value = intervalo.hole_size_in ?? '';
      document.getElementById('dDepth').value = intervalo.profundidad_ft ?? '';
      document.getElementById('dTvd').value = intervalo.tvd_ft ?? '';
      document.getElementById('dTopLiner').value = intervalo.top_of_liner_ft ?? '';
      document.getElementById('dMaxDensity').value = intervalo.maximum_density_lb_gal ?? '';
      document.getElementById('dMaxBht').value = intervalo.max_bht_f ?? '';
      document.getElementById('dMaxAngle').value = intervalo.maximum_angle ?? '';
      document.getElementById('dIntervalDays').value = intervalo.interval_days ?? '';
      document.getElementById('dPlannedDays').value = intervalo.planned_days ?? '';
      document.getElementById('dPlannedLength').value = intervalo.planned_length_ft ?? '';
      document.getElementById('dIntervalCost').value = intervalo.interval_cost ?? '';
      document.getElementById('dPlannedCost').value = intervalo.planned_cost ?? '';
      document.getElementById('dFracGrad').value = intervalo.frac_grad_lb_gal ?? '';
      document.getElementById('dFluid1').value = intervalo.fluid_type_code_1 || '';
      document.getElementById('dFluid2').value = intervalo.fluid_type_code_2 || '';
      document.getElementById('dObservaciones').value = intervalo.observaciones_recomendaciones || '';
      document.getElementById('dComentariosRecap').value = intervalo.comentarios_recap || '';
      document.getElementById('charCount').textContent = String((intervalo.comentarios_recap || '').length);
    } else {
      const siguiente = state.intervalos.length
        ? Math.max(...state.intervalos.map((i) => i.numero_intervalo)) + 1 : 1;
      document.getElementById('dInterval').value = siguiente;
    }

    document.getElementById('detailPanel').hidden = false;
    document.getElementById('detailPanel').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function cerrarDetalle() {
    document.getElementById('detailPanel').hidden = true;
    state.editandoId = null;
  }

  function numOrNull(id) {
    const v = document.getElementById(id).value;
    return v === '' ? null : parseFloat(v);
  }

  function intOrNull(id) {
    const v = document.getElementById(id).value;
    return v === '' ? null : parseInt(v, 10);
  }

  async function guardarIntervalo() {
    document.getElementById('errorDetalle').textContent = '';
    const payload = {
      numero_intervalo: intOrNull('dInterval'),
      tipo: document.getElementById('dTipo').value,
      casing_od_in: numOrNull('dCasingOd'),
      casing_id_in: numOrNull('dCasingId'),
      hole_size_in: numOrNull('dHoleSize'),
      profundidad_ft: numOrNull('dDepth'),
      tvd_ft: numOrNull('dTvd'),
      top_of_liner_ft: numOrNull('dTopLiner'),
      maximum_density_lb_gal: numOrNull('dMaxDensity'),
      max_bht_f: numOrNull('dMaxBht'),
      maximum_angle: numOrNull('dMaxAngle'),
      interval_days: intOrNull('dIntervalDays'),
      planned_days: intOrNull('dPlannedDays'),
      planned_length_ft: numOrNull('dPlannedLength'),
      interval_cost: numOrNull('dIntervalCost'),
      planned_cost: numOrNull('dPlannedCost'),
      frac_grad_lb_gal: numOrNull('dFracGrad'),
      fluid_type_code_1: document.getElementById('dFluid1').value,
      fluid_type_code_2: document.getElementById('dFluid2').value,
      observaciones_recomendaciones: document.getElementById('dObservaciones').value,
      comentarios_recap: document.getElementById('dComentariosRecap').value,
    };

    const url = state.editandoId
      ? `/api/pozos/${window.POZO_ID}/casing-intervals/${state.editandoId}/`
      : `/api/pozos/${window.POZO_ID}/casing-intervals/crear/`;

    try {
      await apiFetch(url, { method: 'POST', body: JSON.stringify(payload) });
      showToast('Intervalo guardado.', 'success');
      cerrarDetalle();
      await cargarIntervalos();
    } catch (err) {
      document.getElementById('errorDetalle').textContent = err.data.error || 'Error al guardar.';
    }
  }

  async function eliminarIntervalo(id, numero) {
    if (!window.confirm(`¿Eliminar el intervalo ${numero}?`)) return;
    try {
      await apiFetch(`/api/pozos/${window.POZO_ID}/casing-intervals/${id}/eliminar/`, { method: 'POST' });
      showToast('Intervalo eliminado.', 'success');
      if (state.editandoId === id) cerrarDetalle();
      await cargarIntervalos();
    } catch (err) {
      showToast(err.data.error || 'No se pudo eliminar.', 'error');
    }
  }

  async function cargarIntervalos() {
    const data = await apiFetch(`/api/pozos/${window.POZO_ID}/casing-intervals/`);
    state.intervalos = data.intervalos;
    state.tipoChoices = data.tipo_choices;
    renderTipoOptions();
    renderTabla();
  }

  document.addEventListener('DOMContentLoaded', async () => {
    document.getElementById('btnNuevoIntervalo').addEventListener('click', () => abrirDetalle(null));
    document.getElementById('btnCerrarDetalle').addEventListener('click', cerrarDetalle);
    document.getElementById('btnGuardarIntervalo').addEventListener('click', guardarIntervalo);
    document.getElementById('btnEliminarIntervalo').addEventListener('click', () => {
      if (state.editandoId) {
        const i = state.intervalos.find((x) => x.id === state.editandoId);
        eliminarIntervalo(state.editandoId, i ? i.numero_intervalo : '');
      }
    });
    document.getElementById('dComentariosRecap').addEventListener('input', (ev) => {
      document.getElementById('charCount').textContent = String(ev.target.value.length);
    });

    try {
      await cargarIntervalos();
    } catch (err) {
      showToast('No se pudieron cargar los intervalos.', 'error');
    }
  });
})();
