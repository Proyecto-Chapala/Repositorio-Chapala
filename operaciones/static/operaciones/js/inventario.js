/**
 * inventario.js - Lógica Exclusiva del Módulo de Inventario de Productos
 * - Gestión de lista de productos (Sólidos / Líquidos)
 * - Navegación (Inicio, <, >, Fin)
 * - Cálculo automático en vivo del estado (0-20 Bajo, 21-50 Medio, >50 Alto)
 * - Validación y control de botones Guardar/Cancelar
 * - Regla estricta de eliminación: Solo si cantidad == 0
 */

const Inventario = {
  productos: [],
  currentIndex: -1,
  currentCategoria: '', // '' (todos), 'SOLIDO', 'LIQUIDO'
  searchQuery: '',
  mode: 'VIEW', // 'VIEW', 'CREATE', 'EDIT'

  elements: {},

  init() {
    this.cacheElements();
    this.bindEvents();
    this.cargarProductos();
  },

  cacheElements() {
    this.elements = {
      tableBody: document.getElementById('tableBody'),
      searchInput: document.getElementById('searchInput'),
      badgeTodos: document.getElementById('badgeTodos'),
      badgeSolidos: document.getElementById('badgeSolidos'),
      badgeLiquidos: document.getElementById('badgeLiquidos'),
      countSolidos: document.getElementById('countSolidos'),
      countLiquidos: document.getElementById('countLiquidos'),
      countTotal: document.getElementById('countTotal'),

      // Botones CRUD izquierda
      btnNuevo: document.getElementById('btnNuevo'),
      btnModificar: document.getElementById('btnModificar'),
      btnEliminar: document.getElementById('btnEliminar'),

      // Navegación izquierda
      btnInicio: document.getElementById('btnInicio'),
      btnAnterior: document.getElementById('btnAnterior'),
      btnSiguiente: document.getElementById('btnSiguiente'),
      btnFin: document.getElementById('btnFin'),

      // Formulario
      productForm: document.getElementById('productForm'),
      formTitle: document.getElementById('formTitle'),
      formModeTag: document.getElementById('formModeTag'),

      inputCodigo: document.getElementById('inputCodigo'),
      inputDescripcion: document.getElementById('inputDescripcion'),
      inputUnidad: document.getElementById('inputUnidad'),
      inputLibraje: document.getElementById('inputLibraje'),
      inputGravedad: document.getElementById('inputGravedad'),
      inputCosto: document.getElementById('inputCosto'),
      inputCantidad: document.getElementById('inputCantidad'),
      selectCategoria: document.getElementById('selectCategoria'),
      badgeEstadoCalculado: document.getElementById('badgeEstadoCalculado'),
      inputObservacion: document.getElementById('inputObservacion'),

      // Botones Guardar / Cancelar
      actionsFooter: document.getElementById('actionsFooter'),
      btnGuardar: document.getElementById('btnGuardar'),
      btnCancelar: document.getElementById('btnCancelar'),
    };
  },

  bindEvents() {
    // Filtros de categoría
    this.elements.badgeTodos.addEventListener('click', () => this.filtrarCategoria(''));
    this.elements.badgeSolidos.addEventListener('click', () => this.filtrarCategoria('SOLIDO'));
    this.elements.badgeLiquidos.addEventListener('click', () => this.filtrarCategoria('LIQUIDO'));

    // Búsqueda en vivo
    let timeout = null;
    this.elements.searchInput.addEventListener('input', (e) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        this.searchQuery = e.target.value.trim();
        this.cargarProductos();
      }, 250);
    });

    // Botones CRUD
    this.elements.btnNuevo.addEventListener('click', () => this.iniciarCreacion());
    this.elements.btnModificar.addEventListener('click', () => this.iniciarModificacion());
    this.elements.btnEliminar.addEventListener('click', () => this.confirmarEliminacion());

    // Botones de Navegación
    this.elements.btnInicio.addEventListener('click', () => this.navegar(0));
    this.elements.btnAnterior.addEventListener('click', () => this.navegar(this.currentIndex - 1));
    this.elements.btnSiguiente.addEventListener('click', () => this.navegar(this.currentIndex + 1));
    this.elements.btnFin.addEventListener('click', () => this.navegar(this.productos.length - 1));

    // Submit del Formulario y Cancelar
    this.elements.productForm.addEventListener('submit', (e) => {
      e.preventDefault();
      this.guardarProducto();
    });
    this.elements.btnCancelar.addEventListener('click', () => this.cancelarEdicion());

    // CÁLCULO AUTOMÁTICO EN VIVO DEL ESTADO AL CAMBIAR CANTIDAD
    this.elements.inputCantidad.addEventListener('input', (e) => {
      const cantidad = parseFloat(e.target.value) || 0;
      this.actualizarBadgeEstado(cantidad);
    });
  },

  calcularEstadoPorCantidad(cantidad) {
    if (cantidad <= 20) return { key: 'BAJO', text: 'Stock Bajo', css: 'bajo' };
    if (cantidad <= 50) return { key: 'MEDIO', text: 'Stock Medio', css: 'medio' };
    return { key: 'ALTO', text: 'Stock Alto', css: 'alto' };
  },

  actualizarBadgeEstado(cantidad) {
    const estado = this.calcularEstadoPorCantidad(cantidad);
    const badge = this.elements.badgeEstadoCalculado;
    badge.className = `badge-status ${estado.css}`;
    badge.innerHTML = `
      <span style="display:inline-block; width:7px; height:7px; border-radius:50%; background:currentColor;"></span>
      ${estado.text}
    `;
  },

  filtrarCategoria(cat) {
    this.currentCategoria = cat;
    [this.elements.badgeTodos, this.elements.badgeSolidos, this.elements.badgeLiquidos].forEach(b => b.classList.remove('active'));

    if (cat === '') this.elements.badgeTodos.classList.add('active');
    if (cat === 'SOLIDO') this.elements.badgeSolidos.classList.add('active');
    if (cat === 'LIQUIDO') this.elements.badgeLiquidos.classList.add('active');

    this.cargarProductos();
  },

  async cargarProductos() {
    try {
      let url = `/api/productos/?`;
      if (this.currentCategoria) url += `categoria=${this.currentCategoria}&`;
      if (this.searchQuery) url += `search=${encodeURIComponent(this.searchQuery)}&`;

      const resp = await fetch(url);
      const data = await resp.json();

      if (data.success) {
        this.productos = data.productos;

        // Actualizar contadores
        this.elements.countTotal.textContent = data.totales.total;
        this.elements.countSolidos.textContent = data.totales.solidos;
        this.elements.countLiquidos.textContent = data.totales.liquidos;

        this.renderTabla();

        if (this.productos.length > 0) {
          if (this.currentIndex < 0 || this.currentIndex >= this.productos.length) {
            this.seleccionarFila(0);
          } else {
            this.seleccionarFila(this.currentIndex);
          }
        } else {
          this.currentIndex = -1;
          this.limpiarFormulario();
          this.actualizarEstadoUI();
        }
      } else {
        App.showToast(data.error || 'Error al cargar productos', 'error');
      }
    } catch (err) {
      console.error(err);
      App.showToast('Error de conexión con el servidor', 'error');
    }
  },

  renderTabla() {
    this.elements.tableBody.innerHTML = '';

    if (this.productos.length === 0) {
      this.elements.tableBody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; padding: 2.5rem; color: var(--color-text-muted);">
            No hay productos registrados. Presione <strong>Nuevo</strong> para agregar uno.
          </td>
        </tr>
      `;
      return;
    }

    this.productos.forEach((p, idx) => {
      const tr = document.createElement('tr');
      if (idx === this.currentIndex) tr.classList.add('selected');

      const estadoInfo = this.calcularEstadoPorCantidad(p.cantidad);

      tr.innerHTML = `
        <td><strong>${p.codigo}</strong></td>
        <td>${p.descripcion}</td>
        <td><span class="badge-cat">${p.categoria_display}</span></td>
        <td>${p.unidad}</td>
        <td style="text-align: right; font-weight: 700; color: var(--color-navy);">${p.cantidad.toFixed(2)}</td>
        <td style="text-align: right;">$${p.costo.toFixed(2)}</td>
        <td>
          <span class="badge-status ${estadoInfo.css}">
            <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:currentColor;"></span>
            ${estadoInfo.text}
          </span>
        </td>
      `;

      tr.addEventListener('click', () => {
        if (this.mode === 'CREATE' || this.mode === 'EDIT') {
          if (!confirm('¿Desea descartar los cambios en el formulario actual?')) return;
        }
        this.seleccionarFila(idx);
      });

      this.elements.tableBody.appendChild(tr);
    });
  },

  seleccionarFila(idx) {
    if (idx < 0 || idx >= this.productos.length) return;
    this.currentIndex = idx;
    this.mode = 'VIEW';

    const rows = this.elements.tableBody.querySelectorAll('tr');
    rows.forEach((r, i) => {
      r.classList.toggle('selected', i === idx);
    });

    const p = this.productos[idx];
    this.cargarEnFormulario(p);
    this.actualizarEstadoUI();
  },

  navegar(idx) {
    if (this.productos.length === 0) return;
    if (idx < 0) idx = 0;
    if (idx >= this.productos.length) idx = this.productos.length - 1;
    this.seleccionarFila(idx);
  },

  cargarEnFormulario(p) {
    this.elements.inputCodigo.value = p.codigo || '';
    this.elements.inputDescripcion.value = p.descripcion || '';
    this.elements.inputUnidad.value = p.unidad || '';
    this.elements.inputLibraje.value = p.libraje !== undefined ? p.libraje : 0;
    this.elements.inputGravedad.value = p.gravedad !== undefined ? p.gravedad : 1.0;
    this.elements.inputCosto.value = p.costo !== undefined ? p.costo : 0;
    this.elements.inputCantidad.value = p.cantidad !== undefined ? p.cantidad : 0;
    this.elements.selectCategoria.value = p.categoria || 'SOLIDO';
    this.elements.inputObservacion.value = p.observacion || '';

    this.actualizarBadgeEstado(p.cantidad || 0);
  },

  limpiarFormulario() {
    this.elements.inputCodigo.value = '';
    this.elements.inputDescripcion.value = '';
    this.elements.inputUnidad.value = '';
    this.elements.inputLibraje.value = '0.00';
    this.elements.inputGravedad.value = '1.0000';
    this.elements.inputCosto.value = '0.00';
    this.elements.inputCantidad.value = '0.00';
    this.elements.selectCategoria.value = this.currentCategoria || 'SOLIDO';
    this.elements.inputObservacion.value = '';

    this.actualizarBadgeEstado(0);
  },

  setFormDisabled(disabled) {
    const inputs = [
      this.elements.inputCodigo,
      this.elements.inputDescripcion,
      this.elements.inputUnidad,
      this.elements.inputLibraje,
      this.elements.inputGravedad,
      this.elements.inputCosto,
      this.elements.inputCantidad,
      this.elements.selectCategoria,
      this.elements.inputObservacion
    ];
    inputs.forEach(el => el.disabled = disabled);
  },

  actualizarEstadoUI() {
    const hasItems = this.productos.length > 0 && this.currentIndex >= 0;
    const currentProduct = hasItems ? this.productos[this.currentIndex] : null;

    if (this.mode === 'VIEW') {
      this.setFormDisabled(true);
      this.elements.actionsFooter.style.display = 'none';
      this.elements.formTitle.textContent = hasItems ? `Producto: ${currentProduct.codigo}` : 'Detalle de Producto';
      this.elements.formModeTag.textContent = 'Solo Lectura';
      this.elements.formModeTag.style.background = 'var(--color-btn-neutral)';
      this.elements.formModeTag.style.color = 'var(--color-text-secondary)';

      this.elements.btnNuevo.disabled = false;
      this.elements.btnModificar.disabled = !hasItems;

      // REGLA: Permitir borrar producto siempre y cuando no tenga cantidad disponible
      if (hasItems) {
        const cant = parseFloat(currentProduct.cantidad) || 0;
        this.elements.btnEliminar.disabled = (cant > 0);
        this.elements.btnEliminar.title = (cant > 0)
          ? `Bloqueado: el producto tiene ${cant} unidades en stock`
          : 'Eliminar producto (stock en 0)';
      } else {
        this.elements.btnEliminar.disabled = true;
      }

      this.elements.btnInicio.disabled = !hasItems || this.currentIndex === 0;
      this.elements.btnAnterior.disabled = !hasItems || this.currentIndex === 0;
      this.elements.btnSiguiente.disabled = !hasItems || this.currentIndex === this.productos.length - 1;
      this.elements.btnFin.disabled = !hasItems || this.currentIndex === this.productos.length - 1;

    } else if (this.mode === 'CREATE') {
      this.setFormDisabled(false);
      this.elements.actionsFooter.style.display = 'flex';
      this.elements.formTitle.textContent = 'Nuevo Producto';
      this.elements.formModeTag.textContent = 'Creando...';
      this.elements.formModeTag.style.background = 'rgba(255, 133, 0, 0.15)';
      this.elements.formModeTag.style.color = 'var(--color-orange)';

      this.elements.btnNuevo.disabled = true;
      this.elements.btnModificar.disabled = true;
      this.elements.btnEliminar.disabled = true;
      this.elements.btnInicio.disabled = true;
      this.elements.btnAnterior.disabled = true;
      this.elements.btnSiguiente.disabled = true;
      this.elements.btnFin.disabled = true;

    } else if (this.mode === 'EDIT') {
      this.setFormDisabled(false);
      this.elements.actionsFooter.style.display = 'flex';
      this.elements.formTitle.textContent = `Modificar: ${currentProduct.codigo}`;
      this.elements.formModeTag.textContent = 'Editando...';
      this.elements.formModeTag.style.background = 'rgba(20, 33, 61, 0.1)';
      this.elements.formModeTag.style.color = 'var(--color-navy)';

      this.elements.btnNuevo.disabled = true;
      this.elements.btnModificar.disabled = true;
      this.elements.btnEliminar.disabled = true;
      this.elements.btnInicio.disabled = true;
      this.elements.btnAnterior.disabled = true;
      this.elements.btnSiguiente.disabled = true;
      this.elements.btnFin.disabled = true;
    }
  },

  iniciarCreacion() {
    this.mode = 'CREATE';
    this.limpiarFormulario();
    this.actualizarEstadoUI();
    this.elements.inputCodigo.focus();
  },

  iniciarModificacion() {
    if (this.currentIndex < 0 || !this.productos[this.currentIndex]) return;
    this.mode = 'EDIT';
    this.actualizarEstadoUI();
    this.elements.inputDescripcion.focus();
  },

  cancelarEdicion() {
    this.mode = 'VIEW';
    if (this.productos.length > 0 && this.currentIndex >= 0) {
      this.cargarEnFormulario(this.productos[this.currentIndex]);
    } else {
      this.limpiarFormulario();
    }
    this.actualizarEstadoUI();
  },

  async guardarProducto() {
    const payload = {
      codigo: this.elements.inputCodigo.value.trim(),
      descripcion: this.elements.inputDescripcion.value.trim(),
      unidad: this.elements.inputUnidad.value.trim(),
      libraje: parseFloat(this.elements.inputLibraje.value) || 0,
      gravedad: parseFloat(this.elements.inputGravedad.value) || 1.0,
      costo: parseFloat(this.elements.inputCosto.value) || 0,
      cantidad: parseFloat(this.elements.inputCantidad.value) || 0,
      categoria: this.elements.selectCategoria.value,
      observacion: this.elements.inputObservacion.value.trim()
    };

    if (!payload.codigo) {
      App.showToast('El código del producto es obligatorio.', 'error');
      this.elements.inputCodigo.focus();
      return;
    }
    if (!payload.descripcion) {
      App.showToast('La descripción es obligatoria.', 'error');
      this.elements.inputDescripcion.focus();
      return;
    }
    if (!payload.unidad) {
      App.showToast('La unidad/presentación es obligatoria.', 'error');
      this.elements.inputUnidad.focus();
      return;
    }

    try {
      let url = '/api/productos/crear/';
      let method = 'POST';

      if (this.mode === 'EDIT') {
        const prodId = this.productos[this.currentIndex].id;
        url = `/api/productos/${prodId}/modificar/`;
        method = 'PUT';
      }

      const resp = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await resp.json();

      if (data.success) {
        App.showToast(data.mensaje || 'Producto guardado exitosamente', 'success');
        this.mode = 'VIEW';
        await this.cargarProductos();

        const savedCode = payload.codigo.toUpperCase();
        const foundIdx = this.productos.findIndex(p => p.codigo.toUpperCase() === savedCode);
        if (foundIdx >= 0) {
          this.seleccionarFila(foundIdx);
        }
      } else {
        App.showToast(data.error || 'Error al guardar el producto', 'error');
      }
    } catch (err) {
      console.error(err);
      App.showToast('Error de red al intentar guardar', 'error');
    }
  },

  async confirmarEliminacion() {
    if (this.currentIndex < 0 || !this.productos[this.currentIndex]) return;
    const prod = this.productos[this.currentIndex];

    if (prod.cantidad > 0) {
      App.showToast(`No se puede eliminar: el producto tiene ${prod.cantidad} unidades en stock disponible.`, 'error');
      return;
    }

    if (!confirm(`¿Desea eliminar permanentemente el producto "${prod.codigo} - ${prod.descripcion}"?`)) {
      return;
    }

    try {
      const resp = await fetch(`/api/productos/${prod.id}/eliminar/`, {
        method: 'DELETE'
      });
      const data = await resp.json();

      if (data.success) {
        App.showToast(data.mensaje || 'Producto eliminado', 'success');
        this.currentIndex = Math.max(0, this.currentIndex - 1);
        await this.cargarProductos();
      } else {
        App.showToast(data.error || 'No se pudo eliminar el producto', 'error');
      }
    } catch (err) {
      console.error(err);
      App.showToast('Error de red al intentar eliminar el producto', 'error');
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  Inventario.init();
});
