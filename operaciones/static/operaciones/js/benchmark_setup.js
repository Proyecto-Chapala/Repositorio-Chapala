// Configuración de Benchmark (Benchmark Setup)
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    const POZO_ID = window.POZO_ID;

    // ---------- Helpers ----------
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async function apiFetch(url, options = {}) {
        const opts = Object.assign({}, options);
        opts.headers = Object.assign({ 'X-CSRFToken': getCookie('csrftoken') }, opts.headers || {});
        const resp = await fetch(url, opts);
        let data = null;
        try { data = await resp.json(); } catch (e) { data = null; }
        if (!resp.ok) { throw { data, status: resp.status }; }
        return data;
    }

    function showToast(mensaje, tipo) {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = 'toast toast-' + (tipo || 'info');
        toast.textContent = mensaje;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 3500);
    }

    function escapeHtml(str) {
        if (str === null || str === undefined) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function debounce(fn, ms) {
        let t;
        return (...args) => {
            clearTimeout(t);
            t = setTimeout(() => fn(...args), ms);
        };
    }

    // ---------- Tabs ----------
    function initTabs() {
        document.querySelectorAll('.tab-nav-item').forEach((btn) => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-nav-item').forEach((b) => b.classList.remove('is-active'));
                document.querySelectorAll('.tab-panel').forEach((p) => { p.hidden = true; });
                btn.classList.add('is-active');
                document.querySelector(`.tab-panel[data-tab="${btn.dataset.tab}"]`).hidden = false;
                if (btn.dataset.tab === 'targets') {
                    cargarTargets();
                }
            });
        });
    }

    // ---------- Pestaña 1: Definiciones ----------
    const parametrosBody = document.getElementById('parametrosBody');
    const buscarParametro = document.getElementById('buscarParametro');
    const filtroGrupo = document.getElementById('filtroGrupo');
    const btnGuardarDefiniciones = document.getElementById('btnGuardarDefiniciones');

    let gruposCargados = false;

    async function cargarDefiniciones() {
        const search = buscarParametro.value.trim();
        const grupo = filtroGrupo.value;
        const url = '/api/pozos/' + POZO_ID + '/benchmark-setup/definiciones/'
            + '?search=' + encodeURIComponent(search) + '&grupo=' + encodeURIComponent(grupo);
        try {
            const data = await apiFetch(url);
            if (!gruposCargados) {
                (data.grupos || []).forEach(function (g) {
                    const opt = document.createElement('option');
                    opt.value = g;
                    opt.textContent = g;
                    filtroGrupo.appendChild(opt);
                });
                gruposCargados = true;
            }
            parametrosBody.innerHTML = '';
            (data.parametros || []).forEach(function (p) {
                const tr = document.createElement('tr');
                tr.innerHTML =
                    '<td><input type="checkbox" class="parametro-checkbox" data-id="' + p.id + '"' +
                    (p.seleccionado ? ' checked' : '') + '></td>' +
                    '<td>' + escapeHtml(p.grupo) + '</td>' +
                    '<td>' + escapeHtml(p.descripcion) + '</td>' +
                    '<td>' + escapeHtml(p.unidad) + '</td>' +
                    '<td>' + escapeHtml(p.tipo_fluido_display) + '</td>';
                parametrosBody.appendChild(tr);
            });
        } catch (err) {
            showToast('Error al cargar los parámetros de benchmark.', 'error');
        }
    }

    // Nota: los checkboxes marcados se preservan en memoria aunque se filtre,
    // usando un set separado de ids seleccionados.
    const seleccionadosSet = new Set();

    async function cargarDefinicionesConSeleccion() {
        await cargarDefiniciones();
        parametrosBody.querySelectorAll('.parametro-checkbox').forEach(function (cb) {
            const id = parseInt(cb.dataset.id, 10);
            if (cb.checked) seleccionadosSet.add(id);
            cb.addEventListener('change', function () {
                if (cb.checked) seleccionadosSet.add(id);
                else seleccionadosSet.delete(id);
            });
        });
    }

    buscarParametro.addEventListener('input', debounce(cargarDefinicionesConSeleccion, 250));
    filtroGrupo.addEventListener('change', cargarDefinicionesConSeleccion);

    btnGuardarDefiniciones.addEventListener('click', async function () {
        try {
            await apiFetch('/api/pozos/' + POZO_ID + '/benchmark-setup/definiciones/guardar/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ parametro_ids: Array.from(seleccionadosSet) }),
            });
            showToast('Definiciones de Benchmark guardadas.', 'success');
        } catch (err) {
            const msg = (err.data && err.data.error) || 'No se pudo guardar.';
            showToast(msg, 'error');
        }
    });

    // ---------- Pestaña 2: Target Entry ----------
    const targetsThead = document.getElementById('targetsThead');
    const targetsBody = document.getElementById('targetsBody');
    const targetsTableWrap = document.getElementById('targetsTableWrap');
    const sinParametrosAviso = document.getElementById('sinParametrosAviso');
    const btnGuardarTargets = document.getElementById('btnGuardarTargets');

    const MIN_MAX_LABELS = { VALOR: 'Valor', MIN: 'Mínimo', MAX: 'Máximo' };

    async function cargarTargets() {
        try {
            const data = await apiFetch('/api/pozos/' + POZO_ID + '/benchmark-setup/targets/');
            const parametros = data.parametros || [];
            const intervalos = data.intervalos || [];
            const targets = data.targets || {};

            if (!parametros.length) {
                sinParametrosAviso.style.display = 'block';
                targetsTableWrap.style.display = 'none';
                return;
            }
            sinParametrosAviso.style.display = 'none';
            targetsTableWrap.style.display = '';

            // Header
            let headerHtml = '<tr><th>Parámetro</th><th style="width:90px;">Unidad</th><th style="width:60px;">Tipo</th>'
                + '<th style="width:120px;">Whole Well</th>';
            intervalos.forEach(function (iv) {
                headerHtml += '<th style="width:120px;">Intervalo ' + iv.numero_intervalo + '</th>';
            });
            headerHtml += '</tr>';
            targetsThead.innerHTML = headerHtml;

            // Body
            targetsBody.innerHTML = '';
            parametros.forEach(function (p) {
                const minMaxRows = p.tipo_dato === 'MIN_MAX' ? ['MIN', 'MAX'] : ['VALOR'];
                minMaxRows.forEach(function (minMax, idx) {
                    const tr = document.createElement('tr');
                    let rowHtml = '';
                    if (idx === 0) {
                        rowHtml += '<td rowspan="' + minMaxRows.length + '">' + escapeHtml(p.descripcion) + '</td>';
                        rowHtml += '<td rowspan="' + minMaxRows.length + '">' + escapeHtml(p.unidad) + '</td>';
                    }
                    rowHtml += '<td>' + MIN_MAX_LABELS[minMax] + '</td>';

                    const claveWhole = p.id + ':whole:' + minMax;
                    rowHtml += '<td><input type="text" class="form-input target-input" style="padding:6px 8px;" '
                        + 'data-parametro-id="' + p.id + '" data-intervalo-id="" data-min-max="' + minMax + '" '
                        + 'value="' + escapeHtml(targets[claveWhole] || '') + '"></td>';

                    intervalos.forEach(function (iv) {
                        const clave = p.id + ':' + iv.id + ':' + minMax;
                        rowHtml += '<td><input type="text" class="form-input target-input" style="padding:6px 8px;" '
                            + 'data-parametro-id="' + p.id + '" data-intervalo-id="' + iv.id + '" data-min-max="' + minMax + '" '
                            + 'value="' + escapeHtml(targets[clave] || '') + '"></td>';
                    });

                    tr.innerHTML = rowHtml;
                    targetsBody.appendChild(tr);
                });
            });
        } catch (err) {
            showToast('Error al cargar la entrada de objetivos.', 'error');
        }
    }

    btnGuardarTargets.addEventListener('click', async function () {
        const filas = [];
        document.querySelectorAll('.target-input').forEach(function (input) {
            const valor = input.value.trim();
            if (!valor) return;
            filas.push({
                parametro_id: parseInt(input.dataset.parametroId, 10),
                intervalo_id: input.dataset.intervaloId ? parseInt(input.dataset.intervaloId, 10) : null,
                min_max: input.dataset.minMax,
                valor: valor,
            });
        });

        try {
            await apiFetch('/api/pozos/' + POZO_ID + '/benchmark-setup/targets/guardar/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ targets: filas }),
            });
            showToast('Objetivos de Benchmark guardados.', 'success');
        } catch (err) {
            const msg = (err.data && err.data.error) || 'No se pudo guardar.';
            showToast(msg, 'error');
        }
    });

    // ---------- Init ----------
    initTabs();
    cargarDefinicionesConSeleccion();
});
