/* ============================================================
   well_header.js — Well Header Information (2 pestañas)
   ============================================================ */

(function () {
  'use strict';

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

  function val(id) {
    const el = document.getElementById(id);
    return el ? el.value : '';
  }

  function num(id) {
    const v = val(id);
    return v === '' ? null : parseFloat(v);
  }

  function intVal(id) {
    const v = val(id);
    return v === '' ? null : parseInt(v, 10);
  }

  function setVal(id, valor) {
    const el = document.getElementById(id);
    if (el) el.value = (valor === null || valor === undefined) ? '' : valor;
  }

  // --------- Tabs ---------
  function initTabs() {
    document.querySelectorAll('.tab-nav-item').forEach((btn) => {
      btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        document.querySelectorAll('.tab-nav-item').forEach((b) => b.classList.toggle('is-active', b === btn));
        document.querySelectorAll('.tab-panel').forEach((panel) => {
          panel.hidden = panel.dataset.tab !== tab;
        });
      });
    });
  }

  // --------- Offshore toggle ---------
  function initOffshoreToggle() {
    const checkbox = document.getElementById('inputEsOffshore');
    const wrap = document.getElementById('offshoreFieldsWrap');
    checkbox.addEventListener('change', () => {
      wrap.hidden = !checkbox.checked;
    });
  }

  // --------- Cargar datos ---------
  async function cargarDatos() {
    const data = await apiFetch(`/api/pozos/${window.POZO_ID}/well-header/`);
    const w = data.well_header;

    document.getElementById('inputEsOffshore').checked = !!w.es_offshore;
    document.getElementById('offshoreFieldsWrap').hidden = !w.es_offshore;
    setVal('inputAirGap', w.air_gap_ft);
    setVal('inputWaterDepth', w.water_depth_ft);
    setVal('inputSeaFloorTemp', w.sea_floor_temp_f);

    setVal('inputOperador', w.operador);
    setVal('inputFieldArea', w.field_area);
    setVal('inputDescripcion', w.descripcion);
    setVal('inputUbicacion', w.ubicacion);
    setVal('inputAlmacen', w.almacen);
    setVal('inputContratista', w.contratista);
    setVal('inputRigName', w.nombre_taladro);
    setVal('inputProjectEngineer', w.ingeniero_proyecto);
    setVal('inputEngineer1', w.ingeniero_miswaco_1);
    setVal('inputEngineer2', w.ingeniero_miswaco_2);
    setVal('inputSpudDate', w.spud_date);
    setVal('inputTdDate', w.td_date);
    setVal('inputTdDays', w.td_days);
    setVal('inputReEntryDepth', w.re_entry_depth_ft);
    setVal('inputLatNs', w.latitud_ns_indicador);
    setVal('inputLonEw', w.longitud_ew_indicador);

    setVal('inputSurfaceTemp', w.surface_temp_f);
    setVal('inputTempGradient', w.temp_gradient_f_100ft);

    setVal('inputTotalDepth', w.total_depth_ft);
    setVal('inputTotalDays', w.total_days);
    setVal('inputMaxTemp', w.maximum_temperature_f);
    setVal('inputTvd', w.tvd_ft);
    setVal('inputEndDate', w.end_date);
    setVal('inputTotalCost', w.total_cost);
    setVal('inputHorizDisplacement', w.horiz_displacement_ft);

    document.getElementById('inputComentarios').value = w.comentarios || '';
    setVal('inputLogit', w.numero_control_logit);

    setVal('inputPrimaryMudCodigo', w.primary_mud_type_codigo);
    setVal('inputPrimaryMudDesc', w.primary_mud_type_descripcion);
    setVal('inputWellTypeCodigo', w.well_type_codigo);
    setVal('inputWellTypeDesc', w.well_type_descripcion);
    setVal('inputContractCodigo', w.contract_type_codigo);
    setVal('inputContractDesc', w.contract_type_descripcion);
    setVal('inputCompletionCodigo', w.completion_fluid_type_codigo);
    setVal('inputCompletionDesc', w.completion_fluid_type_descripcion);
  }

  // --------- Guardar Tab 1 ---------
  async function guardarTab1() {
    document.getElementById('errorTab1').textContent = '';
    const payload = {
      es_offshore: document.getElementById('inputEsOffshore').checked,
      air_gap_ft: num('inputAirGap'),
      water_depth_ft: num('inputWaterDepth'),
      sea_floor_temp_f: num('inputSeaFloorTemp'),
      operador: val('inputOperador'),
      field_area: val('inputFieldArea'),
      descripcion: val('inputDescripcion'),
      ubicacion: val('inputUbicacion'),
      almacen: val('inputAlmacen'),
      contratista: val('inputContratista'),
      nombre_taladro: val('inputRigName'),
      ingeniero_proyecto: val('inputProjectEngineer'),
      ingeniero_miswaco_1: val('inputEngineer1'),
      ingeniero_miswaco_2: val('inputEngineer2'),
      spud_date: val('inputSpudDate') || null,
      td_date: val('inputTdDate') || null,
      td_days: intVal('inputTdDays'),
      re_entry_depth_ft: num('inputReEntryDepth'),
      latitud_ns_indicador: val('inputLatNs'),
      longitud_ew_indicador: val('inputLonEw'),
      surface_temp_f: num('inputSurfaceTemp'),
      temp_gradient_f_100ft: num('inputTempGradient'),
      total_depth_ft: num('inputTotalDepth'),
      total_days: intVal('inputTotalDays'),
      maximum_temperature_f: num('inputMaxTemp'),
      tvd_ft: num('inputTvd'),
      end_date: val('inputEndDate') || null,
      total_cost: num('inputTotalCost'),
      horiz_displacement_ft: num('inputHorizDisplacement'),
      comentarios: document.getElementById('inputComentarios').value,
      numero_control_logit: val('inputLogit'),
    };

    try {
      await apiFetch(`/api/pozos/${window.POZO_ID}/well-header/guardar/`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      showToast('Well Information guardada.', 'success');
    } catch (err) {
      document.getElementById('errorTab1').textContent = err.data.error || 'Error al guardar.';
    }
  }

  // --------- Guardar Tab 2 ---------
  async function guardarTab2() {
    document.getElementById('errorTab2').textContent = '';
    const payload = {
      primary_mud_type_codigo: val('inputPrimaryMudCodigo'),
      primary_mud_type_descripcion: val('inputPrimaryMudDesc'),
      well_type_codigo: val('inputWellTypeCodigo'),
      well_type_descripcion: val('inputWellTypeDesc'),
      contract_type_codigo: val('inputContractCodigo'),
      contract_type_descripcion: val('inputContractDesc'),
      completion_fluid_type_codigo: val('inputCompletionCodigo'),
      completion_fluid_type_descripcion: val('inputCompletionDesc'),
    };

    try {
      await apiFetch(`/api/pozos/${window.POZO_ID}/marketing-codes/guardar/`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      showToast('Marketing Codes guardado.', 'success');
    } catch (err) {
      document.getElementById('errorTab2').textContent = err.data.error || 'Error al guardar.';
    }
  }

  document.addEventListener('DOMContentLoaded', async () => {
    initTabs();
    initOffshoreToggle();
    document.getElementById('btnGuardarTab1').addEventListener('click', guardarTab1);
    document.getElementById('btnGuardarTab2').addEventListener('click', guardarTab2);
    try {
      await cargarDatos();
    } catch (err) {
      showToast('No se pudo cargar Well Header Information.', 'error');
    }
  });
})();
