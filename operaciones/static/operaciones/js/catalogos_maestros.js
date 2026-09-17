// Catálogos Maestros (Equipos, Mallas, Propiedades de Equipo, Parámetros de Benchmark)
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // ---------- Estado ----------
    let tabActiva = 'equipos';
    let equipos = [];
    let mallas = [];
    let propiedades = [];
    let benchmarks = [];
    let equipoSeleccionadoId = null;
    let mallaSeleccionadaId = null;
    let propiedadSeleccionadaId = null;
    let benchmarkSeleccionadoId = null;

    const TIPO_EQUIPO_LABELS = {
        CENTRIFUGA: 'Centrífuga',
        LIMPIADOR_LODO: 'Limpiador de Lodo (Mud Cleaner)',
        ZARANDA: 'Zaranda (Shale Shaker)',
        SISTEMA_VACIO: 'Sistema de Vacío',
        CONTENEDOR_RECORTES: 'Contenedor de Recortes',
        OTROS: 'Otros',
    };

    // ---------- Elementos: Tabs ----------
    const tabButtons = {
        equipos: document.getElementById('tabEquipos'),
        mallas: document.getElementById('tabMallas'),
        propiedades: document.getElementById('tabPropiedades'),
        benchmark: document.getElementById('tabBenchmark'),
    };
    const panels = {
        equipos: document.getElementById('panelEquipos'),
        mallas: document.getElementById('panelMallas'),
        propiedades: document.getElementById('panelPropiedades'),
        benchmark: document.getElementById('panelBenchmark'),
    };
    const searchInput = document.getElementById('searchInput');

    // ---------- Elementos: Equipos ----------
    const tablaEquiposBody = document.getElementById('tablaEquiposBody');
    const statsEquipos = document.getElementById('statsEquipos');
    const btnNuevoEquipo = document.getElementById('btnNuevoEquipo');
    const btnEliminarEquipo = document.getElementById('btnEliminarEquipo');
    const formTituloEquipo = document.getElementById('formTituloEquipo');
    const formModoEquipo = document.getElementById('formModoEquipo');
    const inputEquipoCodigo = document.getElementById('inputEquipoCodigo');
    const inputEquipoNombre = document.getElementById('inputEquipoNombre');
    const inputEquipoTipo = document.getElementById('inputEquipoTipo');
    const errorEquipo = document.getElementById('errorEquipo');
    const btnCancelarEquipo = document.getElementById('btnCancelarEquipo');
    const btnGuardarEquipo = document.getElementById('btnGuardarEquipo');

    // ---------- Elementos: Mallas ----------
    const tablaMallasBody = document.getElementById('tablaMallasBody');
    const statsMallas = document.getElementById('statsMallas');
    const btnNuevaMalla = document.getElementById('btnNuevaMalla');
    const btnEliminarMalla = document.getElementById('btnEliminarMalla');
    const formTituloMalla = document.getElementById('formTituloMalla');
    const formModoMalla = document.getElementById('formModoMalla');
    const inputMallaCodigo = document.getElementById('inputMallaCodigo');
    const inputMallaDescripcion = document.getElementById('inputMallaDescripcion');
    const inputMallaMesh = document.getElementById('inputMallaMesh');
    const errorMalla = document.getElementById('errorMalla');
    const btnCancelarMalla = document.getElementById('btnCancelarMalla');
    const btnGuardarMalla = document.getElementById('btnGuardarMalla');

    // ---------- Elementos: Propiedades de Equipo ----------
    const tablaPropiedadesBody = document.getElementById('tablaPropiedadesBody');
    const statsPropiedades = document.getElementById('statsPropiedades');
    const btnNuevaPropiedad = document.getElementById('btnNuevaPropiedad');
    const btnEliminarPropiedad = document.getElementById('btnEliminarPropiedad');
    const formTituloPropiedad = document.getElementById('formTituloPropiedad');
    const formModoPropiedad = document.getElementById('formModoPropiedad');
    const inputPropiedadTipo = document.getElementById('inputPropiedadTipo');
    const inputPropiedadDescripcion = document.getElementById('inputPropiedadDescripcion');
    const inputPropiedadUnidad = document.getElementById('inputPropiedadUnidad');
    const inputPropiedadOrden = document.getElementById('inputPropiedadOrden');
    const errorPropiedad = document.getElementById('errorPropiedad');
    const btnCancelarPropiedad = document.getElementById('btnCancelarPropiedad');
    const btnGuardarPropiedad = document.getElementById('btnGuardarPropiedad');

    // ---------- Elementos: Parámetros de Benchmark ----------
    const tablaBenchmarkBody = document.getElementById('tablaBenchmarkBody');
    const statsBenchmark = document.getElementById('statsBenchmark');
    const btnNuevoBenchmark = document.getElementById('btnNuevoBenchmark');
    const btnEliminarBenchmark = document.getElementById('btnEliminarBenchmark');
    const formTituloBenchmark = document.getElementById('formTituloBenchmark');
    const formModoBenchmark = document.getElementById('formModoBenchmark');
    const inputBenchmarkGrupo = document.getElementById('inputBenchmarkGrupo');
    const inputBenchmarkDescripcion = document.getElementById('inputBenchmarkDescripcion');
    const inputBenchmarkUnidad = document.getElementById('inputBenchmarkUnidad');
    const inputBenchmarkFluido = document.getElementById('inputBenchmarkFluido');
    const inputBenchmarkTipoDato = document.getElementById('inputBenchmarkTipoDato');
    const errorBenchmark = document.getElementById('errorBenchmark');
    const btnCancelarBenchmark = document.getElementById('btnCancelarBenchmark');
    const btnGuardarBenchmark = document.getElementById('btnGuardarBenchmark');

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
        opts.headers = Object.assign({
            'X-CSRFToken': getCookie('csrftoken'),
        }, opts.headers || {});
        const resp = await fetch(url, opts);
        let data = null;
        try {
            data = await resp.json();
        } catch (e) {
            data = null;
        }
        if (!resp.ok) {
            throw { data, status: resp.status };
        }
        return data;
    }

    function showToast(mensaje, tipo) {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = 'toast toast-' + (tipo || 'info');
        toast.textContent = mensaje;
        container.appendChild(toast);
        setTimeout(() => {
            toast.remove();
        }, 3500);
    }

    function escapeHtml(str) {
        if (str === null || str === undefined) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // ---------- Tabs ----------
    const searchPlaceholders = {
        equipos: 'Buscar por código o nombre...',
        mallas: 'Buscar por código o descripción...',
        propiedades: 'Buscar por descripción...',
        benchmark: 'Buscar por descripción...',
    };

    function activarTab(tab) {
        tabActiva = tab;
        Object.keys(tabButtons).forEach(function (key) {
            tabButtons[key].classList.toggle('active', key === tab);
            panels[key].hidden = (key !== tab);
        });
        searchInput.placeholder = searchPlaceholders[tab];
        searchInput.value = '';
    }

    tabButtons.equipos.addEventListener('click', () => activarTab('equipos'));
    tabButtons.mallas.addEventListener('click', () => activarTab('mallas'));
    tabButtons.propiedades.addEventListener('click', () => activarTab('propiedades'));
    tabButtons.benchmark.addEventListener('click', () => activarTab('benchmark'));

    // ---------- Carga de datos ----------
    async function cargarEquipos(search) {
        try {
            const url = '/api/equipos/' + (search ? ('?search=' + encodeURIComponent(search)) : '');
            const data = await apiFetch(url);
            equipos = (data && data.equipos) || [];
            renderEquipos();
        } catch (err) {
            showToast('Error al cargar el catálogo de equipos.', 'error');
        }
    }

    async function cargarMallas(search) {
        try {
            const url = '/api/mallas/' + (search ? ('?search=' + encodeURIComponent(search)) : '');
            const data = await apiFetch(url);
            mallas = (data && data.mallas) || [];
            renderMallas();
        } catch (err) {
            showToast('Error al cargar el catálogo de mallas.', 'error');
        }
    }

    async function cargarPropiedades(search) {
        try {
            const url = '/api/propiedades-equipo/' + (search ? ('?search=' + encodeURIComponent(search)) : '');
            const data = await apiFetch(url);
            propiedades = (data && data.propiedades) || [];
            renderPropiedades();
        } catch (err) {
            showToast('Error al cargar las propiedades de equipo.', 'error');
        }
    }

    async function cargarBenchmarks(search) {
        try {
            const url = '/api/parametros-benchmark/' + (search ? ('?search=' + encodeURIComponent(search)) : '');
            const data = await apiFetch(url);
            benchmarks = (data && data.parametros) || [];
            renderBenchmarks();
        } catch (err) {
            showToast('Error al cargar los parámetros de benchmark.', 'error');
        }
    }

    // ---------- Render ----------
    function renderEquipos() {
        tablaEquiposBody.innerHTML = '';
        statsEquipos.textContent = equipos.length + (equipos.length === 1 ? ' equipo' : ' equipos');
        equipos.forEach(function (eq) {
            const tr = document.createElement('tr');
            tr.dataset.id = eq.id;
            if (eq.id === equipoSeleccionadoId) tr.classList.add('selected');
            tr.innerHTML = '<td>' + escapeHtml(eq.codigo) + '</td><td>' + escapeHtml(eq.nombre) + '</td><td>' + escapeHtml(eq.tipo_equipo_display) + '</td>';
            tr.addEventListener('click', function () {
                seleccionarEquipo(eq.id);
            });
            tablaEquiposBody.appendChild(tr);
        });
    }

    function renderMallas() {
        tablaMallasBody.innerHTML = '';
        statsMallas.textContent = mallas.length + (mallas.length === 1 ? ' malla' : ' mallas');
        mallas.forEach(function (m) {
            const tr = document.createElement('tr');
            tr.dataset.id = m.id;
            if (m.id === mallaSeleccionadaId) tr.classList.add('selected');
            tr.innerHTML = '<td>' + escapeHtml(m.codigo) + '</td><td>' + escapeHtml(m.descripcion) + '</td><td>' + escapeHtml(String(m.mesh_size)) + '</td>';
            tr.addEventListener('click', function () {
                seleccionarMalla(m.id);
            });
            tablaMallasBody.appendChild(tr);
        });
    }

    function renderPropiedades() {
        tablaPropiedadesBody.innerHTML = '';
        statsPropiedades.textContent = propiedades.length + (propiedades.length === 1 ? ' propiedad' : ' propiedades');
        propiedades.forEach(function (p) {
            const tr = document.createElement('tr');
            tr.dataset.id = p.id;
            if (p.id === propiedadSeleccionadaId) tr.classList.add('selected');
            tr.innerHTML = '<td>' + escapeHtml(p.tipo_equipo_display) + '</td><td>' + escapeHtml(p.descripcion) + '</td><td>' + escapeHtml(p.unidad) + '</td><td>' + escapeHtml(String(p.orden)) + '</td>';
            tr.addEventListener('click', function () {
                seleccionarPropiedad(p.id);
            });
            tablaPropiedadesBody.appendChild(tr);
        });
    }

    function renderBenchmarks() {
        tablaBenchmarkBody.innerHTML = '';
        statsBenchmark.textContent = benchmarks.length + (benchmarks.length === 1 ? ' parámetro' : ' parámetros');
        benchmarks.forEach(function (b) {
            const tr = document.createElement('tr');
            tr.dataset.id = b.id;
            if (b.id === benchmarkSeleccionadoId) tr.classList.add('selected');
            tr.innerHTML = '<td>' + escapeHtml(b.grupo) + '</td><td>' + escapeHtml(b.descripcion) + '</td><td>' + escapeHtml(b.unidad) + '</td><td>' + escapeHtml(b.tipo_fluido_display) + '</td><td>' + escapeHtml(b.tipo_dato_display) + '</td>';
            tr.addEventListener('click', function () {
                seleccionarBenchmark(b.id);
            });
            tablaBenchmarkBody.appendChild(tr);
        });
    }

    // ---------- Selección ----------
    function seleccionarEquipo(id) {
        equipoSeleccionadoId = id;
        const eq = equipos.find(function (e) { return e.id === id; });
        if (!eq) return;
        inputEquipoCodigo.value = eq.codigo;
        inputEquipoNombre.value = eq.nombre;
        inputEquipoTipo.value = eq.tipo_equipo;
        formTituloEquipo.textContent = eq.nombre;
        formModoEquipo.textContent = 'Editando';
        errorEquipo.textContent = '';
        btnEliminarEquipo.disabled = false;
        renderEquipos();
    }

    function seleccionarMalla(id) {
        mallaSeleccionadaId = id;
        const m = mallas.find(function (x) { return x.id === id; });
        if (!m) return;
        inputMallaCodigo.value = m.codigo;
        inputMallaDescripcion.value = m.descripcion;
        inputMallaMesh.value = m.mesh_size;
        formTituloMalla.textContent = m.descripcion;
        formModoMalla.textContent = 'Editando';
        errorMalla.textContent = '';
        btnEliminarMalla.disabled = false;
        renderMallas();
    }

    function seleccionarPropiedad(id) {
        propiedadSeleccionadaId = id;
        const p = propiedades.find(function (x) { return x.id === id; });
        if (!p) return;
        inputPropiedadTipo.value = p.tipo_equipo;
        inputPropiedadDescripcion.value = p.descripcion;
        inputPropiedadUnidad.value = p.unidad;
        inputPropiedadOrden.value = p.orden;
        formTituloPropiedad.textContent = p.descripcion;
        formModoPropiedad.textContent = 'Editando';
        errorPropiedad.textContent = '';
        btnEliminarPropiedad.disabled = false;
        renderPropiedades();
    }

    function seleccionarBenchmark(id) {
        benchmarkSeleccionadoId = id;
        const b = benchmarks.find(function (x) { return x.id === id; });
        if (!b) return;
        inputBenchmarkGrupo.value = b.grupo;
        inputBenchmarkDescripcion.value = b.descripcion;
        inputBenchmarkUnidad.value = b.unidad;
        inputBenchmarkFluido.value = b.tipo_fluido;
        inputBenchmarkTipoDato.value = b.tipo_dato;
        formTituloBenchmark.textContent = b.descripcion;
        formModoBenchmark.textContent = 'Editando';
        errorBenchmark.textContent = '';
        btnEliminarBenchmark.disabled = false;
        renderBenchmarks();
    }

    function limpiarFormEquipo() {
        equipoSeleccionadoId = null;
        inputEquipoCodigo.value = '';
        inputEquipoNombre.value = '';
        inputEquipoTipo.value = 'CENTRIFUGA';
        formTituloEquipo.textContent = 'Nuevo Equipo';
        formModoEquipo.textContent = 'Creando';
        errorEquipo.textContent = '';
        btnEliminarEquipo.disabled = true;
        renderEquipos();
    }

    function limpiarFormMalla() {
        mallaSeleccionadaId = null;
        inputMallaCodigo.value = '';
        inputMallaDescripcion.value = '';
        inputMallaMesh.value = '';
        formTituloMalla.textContent = 'Nueva Malla';
        formModoMalla.textContent = 'Creando';
        errorMalla.textContent = '';
        btnEliminarMalla.disabled = true;
        renderMallas();
    }

    function limpiarFormPropiedad() {
        propiedadSeleccionadaId = null;
        inputPropiedadTipo.value = 'CENTRIFUGA';
        inputPropiedadDescripcion.value = '';
        inputPropiedadUnidad.value = '';
        inputPropiedadOrden.value = '';
        formTituloPropiedad.textContent = 'Nueva Propiedad';
        formModoPropiedad.textContent = 'Creando';
        errorPropiedad.textContent = '';
        btnEliminarPropiedad.disabled = true;
        renderPropiedades();
    }

    function limpiarFormBenchmark() {
        benchmarkSeleccionadoId = null;
        inputBenchmarkGrupo.value = '';
        inputBenchmarkDescripcion.value = '';
        inputBenchmarkUnidad.value = '';
        inputBenchmarkFluido.value = 'NA';
        inputBenchmarkTipoDato.value = 'MIN_MAX';
        formTituloBenchmark.textContent = 'Nuevo Parámetro';
        formModoBenchmark.textContent = 'Creando';
        errorBenchmark.textContent = '';
        btnEliminarBenchmark.disabled = true;
        renderBenchmarks();
    }

    // ---------- CRUD Equipos ----------
    btnNuevoEquipo.addEventListener('click', limpiarFormEquipo);
    btnCancelarEquipo.addEventListener('click', limpiarFormEquipo);

    btnGuardarEquipo.addEventListener('click', async function () {
        const codigo = inputEquipoCodigo.value.trim();
        const nombre = inputEquipoNombre.value.trim();
        const tipoEquipo = inputEquipoTipo.value;
        errorEquipo.textContent = '';

        if (!codigo || !nombre) {
            errorEquipo.textContent = 'El código y el nombre son obligatorios.';
            return;
        }

        const payload = { codigo: codigo, nombre: nombre, tipo_equipo: tipoEquipo };
        const esEdicion = equipoSeleccionadoId !== null;
        const url = esEdicion
            ? '/api/equipos/' + equipoSeleccionadoId + '/modificar/'
            : '/api/equipos/crear/';

        try {
            await apiFetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            showToast(esEdicion ? 'Equipo actualizado correctamente.' : 'Equipo creado correctamente.', 'success');
            limpiarFormEquipo();
            await cargarEquipos(searchInput.value.trim());
        } catch (err) {
            const msg = (err.data && err.data.error) || 'No se pudo guardar el equipo.';
            errorEquipo.textContent = msg;
        }
    });

    btnEliminarEquipo.addEventListener('click', async function () {
        if (equipoSeleccionadoId === null) return;
        if (!confirm('¿Eliminar este equipo del catálogo maestro?')) return;
        try {
            await apiFetch('/api/equipos/' + equipoSeleccionadoId + '/eliminar/', { method: 'POST' });
            showToast('Equipo eliminado correctamente.', 'success');
            limpiarFormEquipo();
            await cargarEquipos(searchInput.value.trim());
        } catch (err) {
            const msg = (err.data && err.data.error) || 'No se pudo eliminar el equipo.';
            showToast(msg, 'error');
        }
    });

    // ---------- CRUD Mallas ----------
    btnNuevaMalla.addEventListener('click', limpiarFormMalla);
    btnCancelarMalla.addEventListener('click', limpiarFormMalla);

    btnGuardarMalla.addEventListener('click', async function () {
        const codigo = inputMallaCodigo.value.trim();
        const descripcion = inputMallaDescripcion.value.trim();
        const meshSize = inputMallaMesh.value.trim();
        errorMalla.textContent = '';

        if (!codigo || !descripcion || !meshSize) {
            errorMalla.textContent = 'El código, la descripción y el tamaño de malla son obligatorios.';
            return;
        }

        const payload = { codigo: codigo, descripcion: descripcion, mesh_size: parseInt(meshSize, 10) };
        const esEdicion = mallaSeleccionadaId !== null;
        const url = esEdicion
            ? '/api/mallas/' + mallaSeleccionadaId + '/modificar/'
            : '/api/mallas/crear/';

        try {
            await apiFetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            showToast(esEdicion ? 'Malla actualizada correctamente.' : 'Malla creada correctamente.', 'success');
            limpiarFormMalla();
            await cargarMallas(searchInput.value.trim());
        } catch (err) {
            const msg = (err.data && err.data.error) || 'No se pudo guardar la malla.';
            errorMalla.textContent = msg;
        }
    });

    btnEliminarMalla.addEventListener('click', async function () {
        if (mallaSeleccionadaId === null) return;
        if (!confirm('¿Eliminar esta malla del catálogo maestro?')) return;
        try {
            await apiFetch('/api/mallas/' + mallaSeleccionadaId + '/eliminar/', { method: 'POST' });
            showToast('Malla eliminada correctamente.', 'success');
            limpiarFormMalla();
            await cargarMallas(searchInput.value.trim());
        } catch (err) {
            const msg = (err.data && err.data.error) || 'No se pudo eliminar la malla.';
            showToast(msg, 'error');
        }
    });

    // ---------- CRUD Propiedades de Equipo ----------
    btnNuevaPropiedad.addEventListener('click', limpiarFormPropiedad);
    btnCancelarPropiedad.addEventListener('click', limpiarFormPropiedad);

    btnGuardarPropiedad.addEventListener('click', async function () {
        const tipoEquipo = inputPropiedadTipo.value;
        const descripcion = inputPropiedadDescripcion.value.trim();
        const unidad = inputPropiedadUnidad.value.trim();
        const orden = inputPropiedadOrden.value.trim() || '1';
        errorPropiedad.textContent = '';

        if (!descripcion) {
            errorPropiedad.textContent = 'La descripción de la propiedad es obligatoria.';
            return;
        }

        const payload = { tipo_equipo: tipoEquipo, descripcion: descripcion, unidad: unidad, orden: parseInt(orden, 10) };
        const esEdicion = propiedadSeleccionadaId !== null;
        const url = esEdicion
            ? '/api/propiedades-equipo/' + propiedadSeleccionadaId + '/modificar/'
            : '/api/propiedades-equipo/crear/';

        try {
            await apiFetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            showToast(esEdicion ? 'Propiedad actualizada correctamente.' : 'Propiedad creada correctamente.', 'success');
            limpiarFormPropiedad();
            await cargarPropiedades(searchInput.value.trim());
        } catch (err) {
            const msg = (err.data && err.data.error) || 'No se pudo guardar la propiedad.';
            errorPropiedad.textContent = msg;
        }
    });

    btnEliminarPropiedad.addEventListener('click', async function () {
        if (propiedadSeleccionadaId === null) return;
        if (!confirm('¿Eliminar esta propiedad del catálogo maestro?')) return;
        try {
            await apiFetch('/api/propiedades-equipo/' + propiedadSeleccionadaId + '/eliminar/', { method: 'POST' });
            showToast('Propiedad eliminada correctamente.', 'success');
            limpiarFormPropiedad();
            await cargarPropiedades(searchInput.value.trim());
        } catch (err) {
            const msg = (err.data && err.data.error) || 'No se pudo eliminar la propiedad.';
            showToast(msg, 'error');
        }
    });

    // ---------- CRUD Parámetros de Benchmark ----------
    btnNuevoBenchmark.addEventListener('click', limpiarFormBenchmark);
    btnCancelarBenchmark.addEventListener('click', limpiarFormBenchmark);

    btnGuardarBenchmark.addEventListener('click', async function () {
        const grupo = inputBenchmarkGrupo.value.trim();
        const descripcion = inputBenchmarkDescripcion.value.trim();
        const unidad = inputBenchmarkUnidad.value.trim();
        const tipoFluido = inputBenchmarkFluido.value;
        const tipoDato = inputBenchmarkTipoDato.value;
        errorBenchmark.textContent = '';

        if (!grupo || !descripcion) {
            errorBenchmark.textContent = 'El grupo y la descripción son obligatorios.';
            return;
        }

        const payload = {
            grupo: grupo, descripcion: descripcion, unidad: unidad,
            tipo_fluido: tipoFluido, tipo_dato: tipoDato,
        };
        const esEdicion = benchmarkSeleccionadoId !== null;
        const url = esEdicion
            ? '/api/parametros-benchmark/' + benchmarkSeleccionadoId + '/modificar/'
            : '/api/parametros-benchmark/crear/';

        try {
            await apiFetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            showToast(esEdicion ? 'Parámetro actualizado correctamente.' : 'Parámetro creado correctamente.', 'success');
            limpiarFormBenchmark();
            await cargarBenchmarks(searchInput.value.trim());
        } catch (err) {
            const msg = (err.data && err.data.error) || 'No se pudo guardar el parámetro.';
            errorBenchmark.textContent = msg;
        }
    });

    btnEliminarBenchmark.addEventListener('click', async function () {
        if (benchmarkSeleccionadoId === null) return;
        if (!confirm('¿Eliminar este parámetro del catálogo maestro?')) return;
        try {
            await apiFetch('/api/parametros-benchmark/' + benchmarkSeleccionadoId + '/eliminar/', { method: 'POST' });
            showToast('Parámetro eliminado correctamente.', 'success');
            limpiarFormBenchmark();
            await cargarBenchmarks(searchInput.value.trim());
        } catch (err) {
            const msg = (err.data && err.data.error) || 'No se pudo eliminar el parámetro.';
            showToast(msg, 'error');
        }
    });

    // ---------- Búsqueda (debounced) ----------
    let searchTimeout = null;
    searchInput.addEventListener('input', function () {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(function () {
            const term = searchInput.value.trim();
            if (tabActiva === 'equipos') {
                cargarEquipos(term);
            } else if (tabActiva === 'mallas') {
                cargarMallas(term);
            } else if (tabActiva === 'propiedades') {
                cargarPropiedades(term);
            } else {
                cargarBenchmarks(term);
            }
        }, 250);
    });

    // ---------- Carga inicial ----------
    cargarEquipos('');
    cargarMallas('');
    cargarPropiedades('');
    cargarBenchmarks('');
});
