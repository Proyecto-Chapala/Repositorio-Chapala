/* ============================================================
   pozos.js — Wizard de Nuevo Pozo (4 pasos)
   Sigue el mismo patrón que inventario.js: fetch + JSON, sin
   frameworks. Guarda el mismo Pozo (BORRADOR) paso a paso.
   ============================================================ */

(function () {
  'use strict';

  // --------- Catálogos que reflejan las choices del modelo Pozo ---------
  const UNIT_PRESETS = [
    { value: 'STANDARD_OILFIELD', label: 'Standard Oilfield', hint: 'ft · bbl · psi · lb/gal' },
    { value: 'STANDARD_1', label: 'Standard 1 (lb/ft³)', hint: '' },
    { value: 'STANDARD_2', label: 'Standard 2 (m)', hint: '' },
    { value: 'STANDARD_3', label: 'Standard 3 (m, m/min)', hint: '' },
    { value: 'SI_METRIC', label: 'SI Métrico', hint: '' },
    { value: 'METRIC_1', label: 'Métrico 1', hint: '' },
    { value: 'METRIC_2', label: 'Métrico 2', hint: '' },
    { value: 'METRIC_3', label: 'Métrico 3', hint: '' },
    { value: 'METRIC_4', label: 'Métrico 4', hint: '' },
    { value: 'METRIC_5', label: 'Métrico 5', hint: '' },
    { value: 'CUSTOM', label: 'Personalizado', hint: 'Elegir unidad por propiedad' },
  ];

  const PROPIEDADES_UNIDAD = [
    ['PROFUNDIDAD', 'Profundidad', ['ft', 'm']],
    ['HOYO_TUBERIA', 'Hoyo/Tubería', ['in', 'mm']],
    ['VOLUMEN', 'Volumen', ['bbl', 'm3', 'L']],
    ['CAUDAL', 'Caudal', ['gal/min', 'bbl/min', 'L/min', 'm3/min']],
    ['BOQUILLA_BROCA', 'Boquilla de Broca', ['1/32"', 'mm']],
    ['VELOCIDAD', 'Velocidad', ['ft/min', 'm/min', 'm/s']],
    ['PRESION', 'Presión', ['psi', 'kPa', 'bar']],
    ['FACTOR_K', 'Factor K', ['lb-s^n/100ft2', 'Pa-s^n']],
    ['PESO_FLUIDO', 'Peso de Fluido', ['lb/gal', 'kg/m3', 'sg']],
    ['VISCOSIDAD_PLASTICA', 'Viscosidad Plástica', ['cP', 'mPa-s']],
    ['PUNTO_CEDENCIA_GELES', 'Punto de Cedencia y Geles', ['lb/100ft2', 'Pa']],
    ['VELOCIDAD_CHORRO', 'Velocidad de Chorro', ['ft/s', 'm/s']],
    ['CONCENTRACION_PRODUCTO', 'Concentración de Producto', ['lb/bbl', 'kg/m3']],
    ['FUERZA', 'Fuerza', ['lbf', 'N']],
    ['TEMPERATURA', 'Temperatura', ['F', 'C']],
    ['ESPESOR_TORTA', 'Espesor de Revoque', ['1/32"', 'mm']],
  ];

  // --------- Estado del wizard ---------
  const state = {
    pozoId: window.POZO_ID_INICIAL || null,
    pasoActual: 1,
    sistemaUnidades: 'STANDARD_OILFIELD',
    categoriaPerdidaTipo: 'MI',
    lossRowCount: 0,
  };

  // --------- Helpers ---------
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

  // --------- Stepper visual ---------
  function renderStepper() {
    document.querySelectorAll('.stepper-item').forEach((el) => {
      const n = parseInt(el.dataset.step, 10);
      el.classList.toggle('is-active', n === state.pasoActual);
      el.classList.toggle('is-complete', n < state.pasoActual);
    });
    document.getElementById('wizardFooterHint').textContent = `Paso ${state.pasoActual} de 4`;
  }

  function goToStep(n) {
    document.querySelectorAll('.wizard-step').forEach((el) => {
      el.hidden = parseInt(el.dataset.step, 10) !== n;
    });
    state.pasoActual = n;
    renderStepper();

    document.getElementById('btnAtras').hidden = n === 1;
    document.getElementById('btnContinuar').hidden = n === 4;
    document.getElementById('btnCrearPozo').hidden = n !== 4;

    if (n === 4) renderResumen();
    document.getElementById('wizardBody').scrollTop = 0;
  }

  // --------- Paso 1: Datos Básicos ---------
  async function cargarPlantillas() {
    const data = await apiFetch('/api/pozos/plantillas/');
    const select = document.getElementById('selectPlantilla');
    data.pozos.forEach((p) => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.nombre;
      select.appendChild(opt);
    });
  }

  function initPaso1() {
    const toggle = document.getElementById('toggleUsarPlantilla');
    const wrap = document.getElementById('templateSelectWrap');
    toggle.addEventListener('click', () => {
      const activo = toggle.getAttribute('aria-checked') === 'true';
      toggle.setAttribute('aria-checked', String(!activo));
      wrap.hidden = activo;
    });
    return cargarPlantillas().catch(() => showToast('No se pudieron cargar los pozos plantilla.', 'error'));
  }

  async function guardarPaso1() {
    const nombre = document.getElementById('inputNombrePozo').value.trim();
    document.getElementById('errorNombrePozo').textContent = '';
    const usaPlantilla = document.getElementById('toggleUsarPlantilla').getAttribute('aria-checked') === 'true';
    const plantillaId = usaPlantilla ? (document.getElementById('selectPlantilla').value || null) : null;

    const url = state.pozoId
      ? `/api/pozos/${state.pozoId}/paso1/`
      : '/api/pozos/paso1/';

    try {
      const data = await apiFetch(url, {
        method: 'POST',
        body: JSON.stringify({ nombre, pozo_plantilla_id: plantillaId }),
      });
      state.pozoId = data.pozo.id;
      history.replaceState(null, '', `/pozos/${state.pozoId}/continuar/`);
      if (data.pozo.sistema_unidades) {
        state.sistemaUnidades = data.pozo.sistema_unidades;
        aplicarPresetSeleccionado();
      }
      goToStep(2);
    } catch (err) {
      document.getElementById('errorNombrePozo').textContent = err.data.error || 'Error al guardar.';
      throw err;
    }
  }

  // --------- Paso 2: Unidades ---------
  function renderUnitPresets() {
    const grid = document.getElementById('unitPresetGrid');
    grid.innerHTML = '';
    UNIT_PRESETS.forEach((preset) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'unit-preset-card';
      btn.dataset.value = preset.value;
      btn.innerHTML = `<div class="unit-preset-card-title">${preset.label}</div>` +
        (preset.hint ? `<div class="field-hint">${preset.hint}</div>` : '');
      btn.addEventListener('click', () => {
        state.sistemaUnidades = preset.value;
        aplicarPresetSeleccionado();
      });
      grid.appendChild(btn);
    });
    aplicarPresetSeleccionado();
  }

  function aplicarPresetSeleccionado() {
    document.querySelectorAll('.unit-preset-card').forEach((card) => {
      card.classList.toggle('is-selected', card.dataset.value === state.sistemaUnidades);
    });
    document.getElementById('customUnitsPanel').hidden = state.sistemaUnidades !== 'CUSTOM';
  }

  function renderCustomUnitsGrid() {
    const grid = document.getElementById('customUnitsGrid');
    grid.innerHTML = '';
    PROPIEDADES_UNIDAD.forEach(([clave, label, opciones]) => {
      const wrap = document.createElement('div');
      wrap.className = 'custom-unit-field';
      const optionsHtml = opciones.map((u) => `<option value="${u}">${u}</option>`).join('');
      wrap.innerHTML = `
        <label for="unit_${clave}">${label}</label>
        <select id="unit_${clave}" class="form-select" data-propiedad="${clave}">${optionsHtml}</select>
      `;
      grid.appendChild(wrap);
    });
  }

  function initPaso2() {
    renderUnitPresets();
    renderCustomUnitsGrid();
  }

  async function guardarPaso2() {
    document.getElementById('errorSistemaUnidades').textContent = '';
    const payload = { sistema_unidades: state.sistemaUnidades };

    if (state.sistemaUnidades === 'CUSTOM') {
      payload.unidades_personalizadas = Array.from(
        document.querySelectorAll('#customUnitsGrid select')
      ).map((sel) => ({ propiedad: sel.dataset.propiedad, unidad: sel.value }));
    }

    try {
      await apiFetch(`/api/pozos/${state.pozoId}/paso2/`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      goToStep(3);
    } catch (err) {
      document.getElementById('errorSistemaUnidades').textContent = err.data.error || 'Error al guardar.';
      throw err;
    }
  }

  // --------- Paso 3: Financiero ---------
  function agregarFilaCategoria(fila) {
    fila = fila || { codigo: '', descripcion: '', tipo: 'SUPERFICIE' };
    state.lossRowCount += 1;
    const tr = document.createElement('tr');
    tr.dataset.rowId = state.lossRowCount;
    tr.innerHTML = `
      <td><input type="number" class="loss-codigo" value="${fila.codigo}"></td>
      <td><input type="text" class="loss-descripcion" value="${fila.descripcion}"></td>
      <td>
        <select class="form-select loss-tipo">
          <option value="SUPERFICIE" ${fila.tipo === 'SUPERFICIE' ? 'selected' : ''}>Superficie</option>
          <option value="SUBSUELO" ${fila.tipo === 'SUBSUELO' ? 'selected' : ''}>Subsuelo</option>
        </select>
      </td>
      <td><button type="button" class="btn-remove-row" aria-label="Eliminar fila">&times;</button></td>
    `;
    tr.querySelector('.btn-remove-row').addEventListener('click', () => tr.remove());
    document.getElementById('lossCategoriesBody').appendChild(tr);
  }

  function initPaso3() {
    const select = document.getElementById('selectCategoriaPerdida');
    const panel = document.getElementById('lossCategoriesPanel');
    select.addEventListener('change', () => {
      state.categoriaPerdidaTipo = select.value;
      panel.hidden = select.value !== 'CUSTOM';
    });
    document.getElementById('btnAgregarCategoria').addEventListener('click', () => agregarFilaCategoria());
  }

  async function guardarPaso3() {
    const payload = {
      moneda_simbolo: document.getElementById('inputMonedaSimbolo').value.trim() || 'USD',
      moneda_decimales: parseInt(document.getElementById('inputMonedaDecimales').value, 10) || 0,
      tasa_impuesto: parseFloat(document.getElementById('inputTasaImpuesto').value) || 0,
      ecuacion_solidos_base_agua: document.getElementById('selectEcuacionAgua').value,
      ecuacion_solidos_base_aceite: document.getElementById('selectEcuacionAceite').value,
      categoria_perdida_tipo: document.getElementById('selectCategoriaPerdida').value,
    };

    if (payload.categoria_perdida_tipo === 'CUSTOM') {
      payload.categorias_perdida = Array.from(document.querySelectorAll('#lossCategoriesBody tr')).map((tr) => ({
        codigo: parseInt(tr.querySelector('.loss-codigo').value, 10) || 0,
        descripcion: tr.querySelector('.loss-descripcion').value.trim(),
        tipo: tr.querySelector('.loss-tipo').value,
      }));
    }

    try {
      await apiFetch(`/api/pozos/${state.pozoId}/paso3/`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      goToStep(4);
    } catch (err) {
      showToast(err.data.error || 'Error al guardar el paso 3.', 'error');
      throw err;
    }
  }

  // --------- Paso 4: Resumen y Confirmación ---------
  function pintarDl(elId, pares) {
    const dl = document.getElementById(elId);
    dl.innerHTML = pares.map(([label, valor]) => `<dt>${label}</dt><dd>${valor}</dd>`).join('');
  }

  async function renderResumen() {
    const data = await apiFetch(`/api/pozos/${state.pozoId}/`);
    const p = data.pozo;

    pintarDl('resumenBasicos', [
      ['Nombre', p.nombre],
      ['Plantilla usada', p.pozo_plantilla_nombre || 'Ninguna'],
    ]);

    pintarDl('resumenUnidades', [
      ['Sistema', p.sistema_unidades_display],
      ['Propiedades personalizadas', p.unidades_personalizadas.length || '—'],
    ]);

    pintarDl('resumenFinanciero', [
      ['Moneda', `${p.moneda_simbolo} (${p.moneda_decimales} decimales)`],
      ['Tasa de impuesto', `${p.tasa_impuesto}%`],
      ['Ecuación sólidos (agua)', p.ecuacion_solidos_base_agua],
      ['Ecuación sólidos (aceite)', p.ecuacion_solidos_base_aceite],
      ['Categorías de pérdida', p.categoria_perdida_tipo],
    ]);
  }

  async function confirmarPozo() {
    try {
      const data = await apiFetch(`/api/pozos/${state.pozoId}/confirmar/`, { method: 'POST' });
      showToast(data.mensaje, 'success');
      window.location.href = `/pozos/${state.pozoId}/spud-date/`;
    } catch (err) {
      showToast(err.data.error || 'No se pudo crear el pozo.', 'error');
    }
  }

  // --------- Navegación general ---------
  function initNavegacion() {
    document.getElementById('btnAtras').addEventListener('click', () => goToStep(state.pasoActual - 1));

    document.getElementById('btnContinuar').addEventListener('click', async () => {
      try {
        if (state.pasoActual === 1) await guardarPaso1();
        else if (state.pasoActual === 2) await guardarPaso2();
        else if (state.pasoActual === 3) await guardarPaso3();
      } catch (err) {
        // El error ya se mostró en el paso correspondiente.
      }
    });

    document.getElementById('btnCrearPozo').addEventListener('click', confirmarPozo);
  }

  // --------- Repoblar un borrador existente (retomar wizard) ---------
  async function cargarBorrador() {
    const data = await apiFetch(`/api/pozos/${state.pozoId}/`);
    const p = data.pozo;

    if (p.estado === 'ACTIVO') {
      showToast('Este pozo ya fue creado; no se puede continuar el wizard.', 'error');
      window.location.href = '/';
      return;
    }

    // Paso 1
    document.getElementById('inputNombrePozo').value = p.nombre || '';
    if (p.pozo_plantilla_id) {
      const toggle = document.getElementById('toggleUsarPlantilla');
      toggle.setAttribute('aria-checked', 'true');
      document.getElementById('templateSelectWrap').hidden = false;
      document.getElementById('selectPlantilla').value = String(p.pozo_plantilla_id);
    }

    // Paso 2
    state.sistemaUnidades = p.sistema_unidades;
    aplicarPresetSeleccionado();
    if (p.sistema_unidades === 'CUSTOM') {
      p.unidades_personalizadas.forEach((u) => {
        const sel = document.querySelector(`#customUnitsGrid select[data-propiedad="${u.propiedad}"]`);
        if (sel) sel.value = u.unidad;
      });
    }

    // Paso 3
    document.getElementById('inputMonedaSimbolo').value = p.moneda_simbolo || 'USD';
    document.getElementById('inputMonedaDecimales').value = p.moneda_decimales;
    document.getElementById('inputTasaImpuesto').value = p.tasa_impuesto;
    document.getElementById('selectEcuacionAgua').value = p.ecuacion_solidos_base_agua;
    document.getElementById('selectEcuacionAceite').value = p.ecuacion_solidos_base_aceite;
    document.getElementById('selectCategoriaPerdida').value = p.categoria_perdida_tipo;
    state.categoriaPerdidaTipo = p.categoria_perdida_tipo;
    if (p.categoria_perdida_tipo === 'CUSTOM') {
      document.getElementById('lossCategoriesPanel').hidden = false;
      document.getElementById('lossCategoriesBody').innerHTML = '';
      p.categorias_perdida.forEach((c) => agregarFilaCategoria(c));
    }

    // Reanudar justo en el paso donde se quedó (paso_wizard_actual apunta
    // al siguiente paso a completar; se limita a 1-4 por seguridad).
    const destino = Math.min(Math.max(p.paso_wizard_actual || 1, 1), 4);
    goToStep(destino);
  }

  // --------- Init ---------
  document.addEventListener('DOMContentLoaded', async () => {
    const plantillasListas = initPaso1();
    initPaso2();
    initPaso3();
    initNavegacion();

    await plantillasListas;

    if (state.pozoId) {
      try {
        await cargarBorrador();
      } catch (err) {
        showToast('No se pudo cargar el pozo en curso.', 'error');
        goToStep(1);
      }
    } else {
      goToStep(1);
    }
  });
})();
