// Configuración de Propiedades de Equipo (Equipment Properties Setup)
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    const POZO_ID = window.POZO_ID;

    const avisoSinEquipo = document.getElementById('avisoSinEquipo');
    const tiposEquipoContainer = document.getElementById('tiposEquipoContainer');
    const cardCentrifuga = document.getElementById('cardCentrifuga');
    const selectUnidadFlowRate = document.getElementById('selectUnidadFlowRate');
    const selectUnidadMass = document.getElementById('selectUnidadMass');
    const footerGuardar = document.getElementById('footerGuardar');
    const btnGuardarPropiedades = document.getElementById('btnGuardarPropiedades');
    const tplTipoEquipoCard = document.getElementById('tplTipoEquipoCard');
    const tplFilaExtra = document.getElementById('tplFilaExtra');

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

    // ---------- Render ----------
    function renderTipoEquipoCard(tipo) {
        const fragment = tplTipoEquipoCard.content.cloneNode(true);
        const card = fragment.querySelector('.tipo-equipo-card');
        card.dataset.tipoEquipo = tipo.tipo_equipo;
        card.querySelector('.tipo-equipo-nombre').textContent = tipo.tipo_equipo_display;

        const propiedadesBody = card.querySelector('.propiedades-body');
        tipo.propiedades.forEach(function (p) {
            const tr = document.createElement('tr');
            tr.innerHTML =
                '<td><input type="checkbox" class="propiedad-checkbox" data-propiedad-id="' + p.id + '"' +
                (p.seleccionada ? ' checked' : '') + '></td>' +
                '<td>' + escapeHtml(p.descripcion) + '</td>' +
                '<td>' + escapeHtml(p.unidad) + '</td>';
            propiedadesBody.appendChild(tr);
        });

        const extrasBody = card.querySelector('.extras-body');
        tipo.extras.forEach(function (extra) {
            agregarFilaExtra(extrasBody, extra.descripcion, extra.unidad);
        });

        card.querySelector('.btn-agregar-extra').addEventListener('click', function () {
            agregarFilaExtra(extrasBody, '', '');
        });

        tiposEquipoContainer.appendChild(card);
    }

    function agregarFilaExtra(tbody, descripcion, unidad) {
        const fragment = tplFilaExtra.content.cloneNode(true);
        const tr = fragment.querySelector('tr');
        tr.querySelector('.extra-descripcion').value = descripcion || '';
        tr.querySelector('.extra-unidad').value = unidad || '';
        tr.querySelector('.btn-remove-row').addEventListener('click', function () {
            tr.remove();
        });
        tbody.appendChild(tr);
    }

    // ---------- Carga inicial ----------
    async function cargar() {
        try {
            const data = await apiFetch('/api/pozos/' + POZO_ID + '/equipment-properties-setup/');
            if (!data.success) {
                showToast('Error al cargar la configuración.', 'error');
                return;
            }
            if (data.sin_equipo_activo) {
                avisoSinEquipo.hidden = false;
                footerGuardar.hidden = true;
                return;
            }
            tiposEquipoContainer.innerHTML = '';
            data.tipos.forEach(renderTipoEquipoCard);

            if (data.centrifuga_config) {
                cardCentrifuga.hidden = false;
                selectUnidadFlowRate.value = data.centrifuga_config.unidad_flow_rate;
                selectUnidadMass.value = data.centrifuga_config.unidad_mass;
            }
            footerGuardar.hidden = false;
        } catch (err) {
            showToast('Error al cargar la configuración de propiedades de equipo.', 'error');
        }
    }

    // ---------- Guardar ----------
    btnGuardarPropiedades.addEventListener('click', async function () {
        const propiedadesSeleccionadas = [];
        const extras = [];

        document.querySelectorAll('.tipo-equipo-card').forEach(function (card) {
            const tipoEquipo = card.dataset.tipoEquipo;
            card.querySelectorAll('.propiedad-checkbox:checked').forEach(function (cb) {
                propiedadesSeleccionadas.push({
                    tipo_equipo: tipoEquipo,
                    propiedad_id: parseInt(cb.dataset.propiedadId, 10),
                });
            });
            card.querySelectorAll('.extras-body tr').forEach(function (tr) {
                const descripcion = tr.querySelector('.extra-descripcion').value.trim();
                const unidad = tr.querySelector('.extra-unidad').value.trim();
                if (descripcion) {
                    extras.push({ tipo_equipo: tipoEquipo, descripcion: descripcion, unidad: unidad });
                }
            });
        });

        const payload = { propiedades_seleccionadas: propiedadesSeleccionadas, extras: extras };
        if (!cardCentrifuga.hidden) {
            payload.centrifuga_config = {
                unidad_flow_rate: selectUnidadFlowRate.value,
                unidad_mass: selectUnidadMass.value,
            };
        }

        try {
            await apiFetch('/api/pozos/' + POZO_ID + '/equipment-properties-setup/guardar/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            showToast('Configuración de Propiedades de Equipo guardada.', 'success');
            await cargar();
        } catch (err) {
            const msg = (err.data && err.data.error) || 'No se pudo guardar la configuración.';
            showToast(msg, 'error');
        }
    });

    cargar();
});
