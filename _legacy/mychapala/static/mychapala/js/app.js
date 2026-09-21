/**
 * ==============================================================================
 * APLICACIÓN JAVASCRIPT PRINCIPAL - PROYECTO CHAPALA
 * ==============================================================================
 * Controla:
 * 1. Navegación SPA fluida entre pestañas (General, Inventario, Uso).
 * 2. Módulo General: Actualización de metadatos, N° de Reporte, comentarios y costo acumulativo.
 * 3. Módulo Inventario: CRUD de productos, búsqueda en tiempo real y paginación.
 * 4. Módulo Uso: Selector de productos, precios variables, cálculo dinámico en tiempo real
 *    y sumatoria al costo final del reporte diario.
 * 5. Módulo de Historial: Consulta, selección y eliminación de reportes por su N° de identificación.
 * 6. Módulo de Impresión Oficial AOS: Planilla oficial con N° de reporte, desglose de costos y firmas.
 * ==============================================================================
 */

class ChapalaApp {
  constructor() {
    this.currentTab = 'inventario';
    this.currentCategory = 'quimico'; // 'quimico' | 'liquido' | 'wellsite'
    this.currentPrintCategory = 'quimico'; // 'quimico' | 'liquido' | 'wellsite'
    this.categoryCounts = { quimico: 0, liquido: 0, wellsite: 0 };
    this.allProducts = [];
    this.products = [];
    this.selectedIds = new Set();
    this.searchTerm = '';
    this.currentPage = 1;
    this.itemsPerPage = 10;
    this.editingProductId = null;
    this.pendingDeleteAction = null;
    this.dailyReport = null;
    this.usageList = [];
    this.selectedReportDate = ''; // Fecha activa del reporte (vacío = hoy)

    this.initElements();
    this.initEvents();
    this.initApp();
  }

  // ============================================================================
  // 1. INICIALIZACIÓN DE ELEMENTOS DOM
  // ============================================================================
  initElements() {
    // Pestañas y Navegación
    this.navButtons = document.querySelectorAll('.nav-item');
    this.tabPanels = {
      general: document.getElementById('tab-general'),
      inventario: document.getElementById('tab-inventario'),
      uso: document.getElementById('tab-uso'),
    };
    this.headerCurrentTab = document.getElementById('header-current-tab');
    this.headerDateDisplay = document.getElementById('header-date-display');
    this.badgeUsoCount = document.getElementById('badge-uso-count');
    this.btnQuickPrint = document.getElementById('btn-quick-print');
    this.btnOpenHistoryHeader = document.getElementById('btn-open-history-header');

    // Botones de Categoría de Inventario
    this.btnCatQuimico = document.getElementById('btn-cat-quimico');
    this.btnCatLiquido = document.getElementById('btn-cat-liquido');
    this.btnCatWellsite = document.getElementById('btn-cat-wellsite');
    this.badgeCountQuimico = document.getElementById('badge-count-quimico');
    this.badgeCountLiquido = document.getElementById('badge-count-liquido');
    this.badgeCountWellsite = document.getElementById('badge-count-wellsite');
    this.categoryTabButtons = document.querySelectorAll('.btn-category-tab');
    this.inventoryTableHead = document.getElementById('inventory-table-head');

    // Sección General
    this.genCostoTotal = document.getElementById('general-costo-total');
    this.genCodigoBadge = document.getElementById('general-codigo-badge');
    this.genFechaBadge = document.getElementById('general-fecha-badge');
    this.genTotalSalidas = document.getElementById('general-total-salidas');
    this.genCodigoReporte = document.getElementById('gen-codigo-reporte');
    this.genDepartamento = document.getElementById('gen-departamento');
    this.genEncargado = document.getElementById('gen-encargado');
    this.genElaboradoNombre = document.getElementById('gen-elaborado-nombre');
    this.genElaboradoCargo = document.getElementById('gen-elaborado-cargo');
    this.genRevisadoNombre = document.getElementById('gen-revisado-nombre');
    this.genRevisadoCargo = document.getElementById('gen-revisado-cargo');
    this.genObservaciones = document.getElementById('gen-observaciones');
    this.btnSaveGeneral = document.getElementById('btn-save-general');
    this.btnOpenHistoryGen = document.getElementById('btn-open-history-gen');

    // Sección Inventario
    this.inventorySearchInput = document.getElementById('inventory-search-input');
    this.btnClearSearch = document.getElementById('btn-clear-search');
    this.btnOpenCreateModal = document.getElementById('btn-open-create-modal');
    this.btnDeleteSelected = document.getElementById('btn-delete-selected');
    this.btnOpenPrintPreview = document.getElementById('btn-open-print-preview');
    this.btnOpenHistoryInv = document.getElementById('btn-open-history-inv');
    this.inventoryTableBody = document.getElementById('inventory-table-body');
    this.selectAllCheckbox = document.getElementById('select-all-products');
    this.paginationControls = document.getElementById('pagination-controls');
    this.paginationInfo = document.getElementById('pagination-info');
    this.statTotal = document.getElementById('stat-total');
    this.statLow = document.getElementById('stat-low');
    this.statOut = document.getElementById('stat-out');

    // Sección Uso (Combobox Integrado y Formulario)
    this.usoCostoTotalHeader = document.getElementById('uso-costo-total-header');
    this.formRegistroUso = document.getElementById('form-registro-uso');
    this.usoComboboxWrapper = document.getElementById('uso-combobox-wrapper');
    this.usoProductSearchInput = document.getElementById('uso-product-search-input');
    this.usoComboboxToggleBtn = document.getElementById('uso-combobox-toggle-btn');
    this.usoComboboxClearBtn = document.getElementById('uso-combobox-clear-btn');
    this.usoComboboxDropdown = document.getElementById('uso-combobox-dropdown');
    this.usoComboboxList = document.getElementById('uso-combobox-list');
    this.usoSelectProducto = document.getElementById('uso-select-producto');
    this.usoStockDisponibleHint = document.getElementById('uso-stock-disponible-hint');
    this.usoInputCantidad = document.getElementById('uso-input-cantidad');
    this.usoInputPrecio = document.getElementById('uso-input-precio');
    this.usoLiveSubtotal = document.getElementById('uso-live-subtotal');
    this.usoInputObservacion = document.getElementById('uso-input-observacion');
    this.usoTableBody = document.getElementById('uso-table-body');
    this.usoCounterBadge = document.getElementById('uso-counter-badge');
    this.usoGrandTotalAmount = document.getElementById('uso-grand-total-amount');

    // Modal Creación / Modificación de Productos
    this.productModal = document.getElementById('product-modal');
    this.productModalTitle = document.getElementById('product-modal-title');
    this.formProductCrud = document.getElementById('form-product-crud');
    this.modalProductId = document.getElementById('modal-product-id');
    this.modalCodigo = document.getElementById('modal-codigo');
    this.btnModalRegenSku = document.getElementById('btn-modal-regen-sku');
    this.modalDescripcion = document.getElementById('modal-descripcion');
    this.modalUnidad = document.getElementById('modal-unidad');
    this.modalLibraje = document.getElementById('modal-libraje');
    this.modalGravedad = document.getElementById('modal-gravedad');
    this.modalCantidad = document.getElementById('modal-cantidad');
    this.modalCategoria = document.getElementById('modal-categoria');
    this.modalPrecioUnitario = document.getElementById('modal-precio-unitario');
    this.btnModalSubmit = document.getElementById('btn-modal-submit');
    this.btnModalCancel = document.getElementById('btn-modal-cancel');
    this.btnCloseProductModal = document.getElementById('btn-close-product-modal');

    // Modal Confirmación
    this.confirmModal = document.getElementById('confirm-modal');
    this.confirmModalTitle = document.getElementById('confirm-modal-title');
    this.confirmModalMsg = document.getElementById('confirm-modal-msg');
    this.btnConfirmDelete = document.getElementById('btn-confirm-delete');
    this.btnCancelDelete = document.getElementById('btn-cancel-delete');
    this.btnCloseConfirmModal = document.getElementById('btn-close-confirm-modal');

    // Modal Historial de Reportes
    this.historyModal = document.getElementById('history-modal');
    this.historyTableBody = document.getElementById('history-table-body');
    this.btnCloseHistoryModal = document.getElementById('btn-close-history-modal');
    this.btnCancelHistory = document.getElementById('btn-cancel-history');

    // Modal Impresión Oficial y selector de formatos
    this.printPreviewModal = document.getElementById('print-preview-modal');
    this.printPreviewContent = document.getElementById('print-preview-content');
    this.btnClosePrintPreview = document.getElementById('btn-close-print-preview');
    this.btnExecutePrint = document.getElementById('btn-execute-print');
    this.printSheetContainer = document.getElementById('print-sheet-container');
    this.printCatButtons = document.querySelectorAll('.print-cat-btn');

    // Toast Container
    this.toastContainer = document.getElementById('toast-container');
  }

  // ============================================================================
  // 2. INICIALIZACIÓN DE EVENTOS
  // ============================================================================
  initEvents() {
    // Cambio de Pestañas
    this.navButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        this.switchTab(tab);
      });
    });

    // Barra de Búsqueda
    this.inventorySearchInput.addEventListener('input', (e) => {
      this.searchTerm = e.target.value.trim();
      this.btnClearSearch.style.display = this.searchTerm ? 'block' : 'none';
      this.currentPage = 1;
      this.fetchProducts();
    });

    this.btnClearSearch.addEventListener('click', () => {
      this.inventorySearchInput.value = '';
      this.searchTerm = '';
      this.btnClearSearch.style.display = 'none';
      this.currentPage = 1;
      this.fetchProducts();
    });

    // Checkbox Seleccionar Todos
    if (this.selectAllCheckbox) {
      this.selectAllCheckbox.addEventListener('change', (e) => {
        const isChecked = e.target.checked;
        if (isChecked) {
          this.products.forEach(p => this.selectedIds.add(p.id));
        } else {
          this.selectedIds.clear();
        }
        this.renderInventoryTable();
        this.updateDeleteButtonState();
      });
    }

    // Acciones de Botones Principales
    this.btnOpenCreateModal.addEventListener('click', () => this.openCreateProductModal());
    this.btnDeleteSelected.addEventListener('click', () => this.promptDeleteSelected());
    this.btnOpenPrintPreview.addEventListener('click', () => this.openPrintPreview());
    this.btnQuickPrint.addEventListener('click', () => this.openPrintPreview());
    this.btnSaveGeneral.addEventListener('click', () => this.saveGeneralReport());

    // Conmutador de Categorías en Inventario (Químico, Líquido, Wellsite)
    if (this.categoryTabButtons) {
      this.categoryTabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
          const cat = btn.dataset.cat;
          this.switchCategory(cat);
        });
      });
    }

    // Selector de Formato de Impresión por Categoría
    if (this.printCatButtons) {
      this.printCatButtons.forEach(btn => {
        btn.addEventListener('click', () => {
          this.printCatButtons.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          this.currentPrintCategory = btn.dataset.printCat;
          this.openPrintPreview();
        });
      });
    }

    // Cambio de categoría en modal regenera prefijo de código automático
    if (this.modalCategoria) {
      this.modalCategoria.addEventListener('change', () => {
        if (!this.editingProductId) {
          this.modalCodigo.value = this.generateRandomSku();
        }
      });
    }

    // Botones de Historial de Reportes
    if (this.btnOpenHistoryHeader) {
      this.btnOpenHistoryHeader.addEventListener('click', () => this.openHistoryModal());
    }
    if (this.btnOpenHistoryGen) {
      this.btnOpenHistoryGen.addEventListener('click', () => this.openHistoryModal());
    }
    if (this.btnOpenHistoryInv) {
      this.btnOpenHistoryInv.addEventListener('click', () => this.openHistoryModal());
    }

    // Generador automático de SKU en modal
    this.btnModalRegenSku.addEventListener('click', () => {
      this.modalCodigo.value = this.generateRandomSku();
    });

    // Guardar Producto (Form submit)
    this.formProductCrud.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleSaveProduct();
    });

    // Formulario de Uso: Combobox Interactivo (Búsqueda + Selección Fusión)
    if (this.usoProductSearchInput) {
      this.usoProductSearchInput.addEventListener('click', (e) => {
        e.stopPropagation();
        this.openComboboxDropdown();
      });

      this.usoProductSearchInput.addEventListener('focus', (e) => {
        e.stopPropagation();
        this.openComboboxDropdown();
      });

      this.usoProductSearchInput.addEventListener('input', (e) => {
        const query = e.target.value;
        if (this.usoComboboxClearBtn) {
          this.usoComboboxClearBtn.style.display = query.trim() ? 'flex' : 'none';
        }
        // Si el usuario escribe y cambia el texto, invalidar selección previa hasta que vuelva a elegir
        if (this.usoSelectProducto.value) {
          const selProd = this.products.find(p => p.id === parseInt(this.usoSelectProducto.value));
          if (!selProd || `${selProd.codigo} - ${selProd.descripcion}` !== query) {
            this.usoSelectProducto.value = '';
            this.onProductSelectionChange();
          }
        }
        this.openComboboxDropdown();
        this.renderComboboxList(query);
      });

      this.usoProductSearchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          this.closeComboboxDropdown();
        } else if (e.key === 'Enter') {
          // Si presiona enter en el input y hay opciones en el dropdown, seleccionar la primera
          const firstItem = this.usoComboboxList ? this.usoComboboxList.querySelector('.combobox-item') : null;
          if (firstItem && this.usoComboboxDropdown.style.display !== 'none') {
            e.preventDefault();
            const id = parseInt(firstItem.dataset.id);
            const p = this.products.find(prod => prod.id === id);
            if (p) {
              this.selectProductInCombobox(p);
            }
          }
        }
      });
    }

    if (this.usoComboboxToggleBtn) {
      this.usoComboboxToggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (this.usoComboboxDropdown.style.display === 'block') {
          this.closeComboboxDropdown();
        } else {
          this.openComboboxDropdown();
          this.usoProductSearchInput.focus();
        }
      });
    }

    if (this.usoComboboxClearBtn) {
      this.usoComboboxClearBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.clearComboboxSelection();
        this.usoProductSearchInput.focus();
      });
    }

    // Cerrar el combobox dropdown al hacer clic fuera
    document.addEventListener('click', (e) => {
      if (this.usoComboboxWrapper && !this.usoComboboxWrapper.contains(e.target)) {
        this.closeComboboxDropdown();
      }
    });

    this.usoInputCantidad.addEventListener('input', () => this.updateLiveCalculation());
    this.usoInputPrecio.addEventListener('input', () => this.updateLiveCalculation());

    this.formRegistroUso.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleSubmitUso();
    });

    // Botones de Modales
    this.btnModalCancel.addEventListener('click', () => this.closeProductModal());
    this.btnCloseProductModal.addEventListener('click', () => this.closeProductModal());
    this.btnCancelDelete.addEventListener('click', () => this.closeConfirmModal());
    this.btnCloseConfirmModal.addEventListener('click', () => this.closeConfirmModal());
    this.btnConfirmDelete.addEventListener('click', () => {
      if (typeof this.pendingDeleteAction === 'function') {
        this.pendingDeleteAction();
      }
      this.closeConfirmModal();
    });

    // Modal Historial
    if (this.btnCloseHistoryModal) {
      this.btnCloseHistoryModal.addEventListener('click', () => this.closeHistoryModal());
    }
    if (this.btnCancelHistory) {
      this.btnCancelHistory.addEventListener('click', () => this.closeHistoryModal());
    }

    // Modal Impresión
    this.btnClosePrintPreview.addEventListener('click', () => this.closePrintPreview());
    this.btnExecutePrint.addEventListener('click', () => {
      window.print();
    });

    // Tecla Escape para cerrar modales
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeProductModal();
        this.closeConfirmModal();
        this.closeHistoryModal();
        this.closePrintPreview();
      }
    });

    // Cerrar al hacer clic fuera del modal
    [this.productModal, this.confirmModal, this.historyModal, this.printPreviewModal].forEach(modal => {
      if (modal) {
        modal.addEventListener('click', (e) => {
          if (e.target === modal) {
            this.closeProductModal();
            this.closeConfirmModal();
            this.closeHistoryModal();
            this.closePrintPreview();
          }
        });
      }
    });
  }

  // ============================================================================
  // 3. INICIO DE LA APLICACIÓN Y CARGA DE DATOS
  // ============================================================================
  async initApp() {
    await this.fetchDailyReport();
    await this.fetchProducts();
    await this.fetchUsageData();
  }

  // Conmutador de Pestañas
  switchTab(tabName) {
    this.currentTab = tabName;
    
    this.navButtons.forEach(btn => {
      if (btn.dataset.tab === tabName) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    Object.keys(this.tabPanels).forEach(key => {
      if (key === tabName) {
        this.tabPanels[key].style.display = 'block';
      } else {
        this.tabPanels[key].style.display = 'none';
      }
    });

    const tabTitles = {
      general: 'General / Reportes',
      inventario: 'Inventario de Productos',
      uso: 'Uso y Cálculo de Costos'
    };
    this.headerCurrentTab.textContent = tabTitles[tabName] || tabName;

    if (tabName === 'uso') {
      this.closeComboboxDropdown();
      this.renderComboboxList(this.usoProductSearchInput ? this.usoProductSearchInput.value : '');
    } else if (tabName === 'general') {
      this.fetchDailyReport();
    }
  }

  // ============================================================================
  // 4. MÓDULO GENERAL (METADATOS Y REPORTES DIARIOS)
  // ============================================================================
  async fetchDailyReport() {
    try {
      const url = this.selectedReportDate ? `/api/reporte-diario/?fecha=${this.selectedReportDate}` : '/api/reporte-diario/';
      const response = await fetch(url);
      const data = await response.json();
      if (data.success) {
        this.dailyReport = data.reporte;
        this.renderGeneralData();
      }
    } catch (err) {
      console.error('Error al cargar reporte diario:', err);
    }
  }

  renderGeneralData() {
    if (!this.dailyReport) return;
    
    const codigo = this.dailyReport.codigo_reporte || `REP-${this.dailyReport.id}`;
    this.headerDateDisplay.textContent = `${codigo} | Fecha: ${this.dailyReport.fecha_formato}`;
    this.genCodigoBadge.textContent = codigo;
    this.genFechaBadge.textContent = `Fecha: ${this.dailyReport.fecha_formato}`;
    this.genCostoTotal.textContent = `$${this.dailyReport.costo_total.toFixed(2)}`;
    this.usoCostoTotalHeader.textContent = `$${this.dailyReport.costo_total.toFixed(2)}`;
    this.usoGrandTotalAmount.textContent = `$${this.dailyReport.costo_total.toFixed(2)}`;
    this.genTotalSalidas.textContent = `${this.dailyReport.total_items_usados} salidas`;

    this.genCodigoReporte.value = codigo;
    this.genDepartamento.value = this.dailyReport.departamento || 'ALMACÉN';
    this.genEncargado.value = this.dailyReport.encargado || 'LUIS BRICEÑO';
    this.genElaboradoNombre.value = this.dailyReport.elaborado_por_nombre || 'Lusneila Franceschi';
    this.genElaboradoCargo.value = this.dailyReport.elaborado_por_cargo || 'Administración';
    this.genRevisadoNombre.value = this.dailyReport.revisado_por_nombre || 'Luis Briceño';
    this.genRevisadoCargo.value = this.dailyReport.revisado_por_cargo || 'Encargado de Almacen';
    this.genObservaciones.value = this.dailyReport.observaciones || '';
  }

  async saveGeneralReport() {
    const payload = {
      codigo_reporte: this.genCodigoReporte.value.trim(),
      departamento: this.genDepartamento.value.trim(),
      encargado: this.genEncargado.value.trim(),
      elaborado_por_nombre: this.genElaboradoNombre.value.trim(),
      elaborado_por_cargo: this.genElaboradoCargo.value.trim(),
      revisado_por_nombre: this.genRevisadoNombre.value.trim(),
      revisado_por_cargo: this.genRevisadoCargo.value.trim(),
      observaciones: this.genObservaciones.value.trim(),
    };

    try {
      const url = this.selectedReportDate ? `/api/reporte-diario/?fecha=${this.selectedReportDate}` : '/api/reporte-diario/';
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (data.success) {
        this.dailyReport = data.reporte;
        this.renderGeneralData();
        this.showToast(`Reporte ${data.reporte.codigo_reporte} actualizado correctamente.`, 'success');
      } else {
        this.showToast(data.error || 'Error al actualizar el reporte.', 'error');
      }
    } catch (err) {
      console.error(err);
      this.showToast('Error de conexión con el servidor.', 'error');
    }
  }

  // ============================================================================
  // 5. MÓDULO HISTORIAL DE REPORTES ANTERIORES Y ELIMINACIÓN
  // ============================================================================
  async openHistoryModal() {
    this.historyTableBody.innerHTML = `
      <tr><td colspan="7" style="text-align: center; padding: 25px;">Cargando reportes anteriores...</td></tr>
    `;
    this.historyModal.classList.add('active');

    try {
      const response = await fetch('/api/reportes-historial/');
      const data = await response.json();

      if (data.success) {
        this.renderHistoryTable(data.reportes);
      } else {
        this.historyTableBody.innerHTML = `
          <tr><td colspan="7" style="text-align: center; padding: 25px; color: #dc2626;">Error al cargar historial.</td></tr>
        `;
      }
    } catch (e) {
      console.error(e);
      this.historyTableBody.innerHTML = `
        <tr><td colspan="7" style="text-align: center; padding: 25px; color: #dc2626;">Error de conexión.</td></tr>
      `;
    }
  }

  renderHistoryTable(reportes) {
    this.historyTableBody.innerHTML = '';

    if (!reportes || reportes.length === 0) {
      this.historyTableBody.innerHTML = `
        <tr><td colspan="7" style="text-align: center; padding: 25px; color: var(--text-muted);">No hay reportes registrados aún.</td></tr>
      `;
      return;
    }

    reportes.forEach(r => {
      const isCurrent = (this.selectedReportDate === r.fecha || (!this.selectedReportDate && r.fecha === this.dailyReport?.fecha));
      const tr = document.createElement('tr');
      if (isCurrent) tr.style.backgroundColor = '#e0f2fe';

      tr.innerHTML = `
        <td style="font-weight: 700; color: #0284c7;">${this.escapeHtml(r.codigo_reporte)}</td>
        <td style="font-weight: 600;">${this.escapeHtml(r.fecha_formato)} ${isCurrent ? '<span style="font-size:10px; background:#0284c7; color:#fff; padding:2px 6px; border-radius:4px; margin-left:4px;">Activo</span>' : ''}</td>
        <td>${this.escapeHtml(r.departamento)}</td>
        <td>${this.escapeHtml(r.encargado)}</td>
        <td style="text-align: right; font-weight: 600;">${r.total_items_usados}</td>
        <td style="text-align: right; font-weight: 700; color: #0284c7;">$${r.costo_total.toFixed(2)}</td>
        <td style="text-align: center;">
          <div style="display: flex; gap: 6px; justify-content: center;">
            <button class="btn btn-primary btn-sm btn-select-report" data-fecha="${r.fecha}">
              Cargar / Modificar
            </button>
            <button class="btn btn-danger btn-sm btn-delete-report" data-id="${r.id}" data-codigo="${r.codigo_reporte}">
              Eliminar
            </button>
          </div>
        </td>
      `;
      this.historyTableBody.appendChild(tr);
    });

    this.historyTableBody.querySelectorAll('.btn-select-report').forEach(btn => {
      btn.addEventListener('click', async () => {
        const fecha = btn.dataset.fecha;
        this.selectedReportDate = fecha;
        this.closeHistoryModal();
        await this.fetchDailyReport();
        await this.fetchUsageData();
        this.showToast(`Reporte ${this.dailyReport.codigo_reporte} (${this.dailyReport.fecha_formato}) cargado`, 'success');
      });
    });

    this.historyTableBody.querySelectorAll('.btn-delete-report').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.id;
        const codigo = btn.dataset.codigo;
        this.handleDeleteReport(id, codigo);
      });
    });
  }

  async handleDeleteReport(id, codigo) {
    if (!confirm(`¿Está seguro de que desea eliminar el reporte "${codigo}" de la base de datos?\n\nLas salidas registradas en este reporte se revertirán y se devolverá el stock al inventario.`)) {
      return;
    }

    try {
      const response = await fetch(`/api/reportes-historial/${id}/`, { method: 'DELETE' });
      const data = await response.json();
      if (data.success) {
        this.showToast(data.mensaje || `Reporte ${codigo} eliminado`, 'success');
        this.selectedReportDate = ''; // Vuelve a hoy
        await this.openHistoryModal();
        await this.fetchProducts();
        await this.fetchDailyReport();
        await this.fetchUsageData();
      } else {
        this.showToast(data.error || 'Error al eliminar reporte', 'error');
      }
    } catch (e) {
      console.error(e);
      this.showToast('Error al conectar con el servidor', 'error');
    }
  }

  closeHistoryModal() {
    this.historyModal.classList.remove('active');
  }

  // ============================================================================
  // 6. MÓDULO INVENTARIO (TABLA, CRUD, BÚSQUEDA Y CATEGORÍAS)
  // ============================================================================
  switchCategory(cat) {
    if (!['quimico', 'liquido', 'wellsite'].includes(cat)) return;
    this.currentCategory = cat;
    this.currentPage = 1;
    this.selectedIds.clear();

    if (this.categoryTabButtons) {
      this.categoryTabButtons.forEach(btn => {
        if (btn.dataset.cat === cat) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }

    this.filterAndRenderInventory();
  }

  async fetchProducts() {
    try {
      const response = await fetch('/api/productos/');
      const data = await response.json();

      if (data.success) {
        this.allProducts = data.productos;

        // Actualiza conteos de insignias por categoría
        this.categoryCounts.quimico = this.allProducts.filter(p => p.categoria === 'quimico').length;
        this.categoryCounts.liquido = this.allProducts.filter(p => p.categoria === 'liquido').length;
        this.categoryCounts.wellsite = this.allProducts.filter(p => p.categoria === 'wellsite').length;

        if (this.badgeCountQuimico) this.badgeCountQuimico.textContent = this.categoryCounts.quimico;
        if (this.badgeCountLiquido) this.badgeCountLiquido.textContent = this.categoryCounts.liquido;
        if (this.badgeCountWellsite) this.badgeCountWellsite.textContent = this.categoryCounts.wellsite;

        this.filterAndRenderInventory();
        this.populateProductSelect();
      }
    } catch (err) {
      console.error('Error al cargar productos:', err);
      this.inventoryTableBody.innerHTML = `
        <tr><td colspan="14" style="text-align:center; padding:30px; color:#dc2626;">Error al cargar el inventario desde el servidor.</td></tr>
      `;
    }
  }

  filterAndRenderInventory() {
    let list = this.allProducts.filter(p => p.categoria === this.currentCategory);

    if (this.searchTerm) {
      const q = this.searchTerm.toLowerCase();
      list = list.filter(p =>
        (p.codigo || '').toLowerCase().includes(q) ||
        (p.descripcion || '').toLowerCase().includes(q) ||
        (p.unidad || '').toLowerCase().includes(q) ||
        (p.libraje || '').toLowerCase().includes(q) ||
        (p.gravedad_especifica || '').toLowerCase().includes(q)
      );
    }

    this.products = list;

    const bajoStock = this.products.filter(p => p.cantidad <= 15 && p.cantidad > 0).length;
    const sinStock = this.products.filter(p => p.cantidad <= 0).length;

    this.statTotal.textContent = `Total Productos: ${this.products.length}`;
    this.statLow.textContent = `Bajo Stock (≤15): ${bajoStock}`;
    this.statOut.textContent = `Sin Stock: ${sinStock}`;

    this.renderInventoryTable();
  }

  renderInventoryTableHead() {
    if (!this.inventoryTableHead) return;

    if (this.currentCategory === 'wellsite') {
      this.inventoryTableHead.innerHTML = `
        <tr>
          <th style="width: 36px; text-align: center;">
            <input type="checkbox" id="select-all-products" class="custom-checkbox">
          </th>
          <th style="min-width: 170px;">Product</th>
          <th style="width: 110px;">Unit Size</th>
          <th style="width: 95px; text-align: right;">Unit Price</th>
          <th style="width: 80px; text-align: right;">Start Amt.</th>
          <th style="width: 80px; text-align: right;">Daily Used</th>
          <th style="width: 80px; text-align: right;">Cum Used</th>
          <th style="width: 80px; text-align: right;">Daily Rec'd</th>
          <th style="width: 80px; text-align: right;">Cum Rec'd</th>
          <th style="width: 80px; text-align: right;">Daily Return</th>
          <th style="width: 80px; text-align: right;">Cum. Return</th>
          <th style="width: 85px; text-align: right;">Final Stock</th>
          <th style="width: 95px; text-align: right;">Daily Cost</th>
          <th style="width: 80px; text-align: center;">Acciones</th>
        </tr>
      `;
    } else {
      this.inventoryTableHead.innerHTML = `
        <tr>
          <th style="width: 38px; text-align: center;">
            <input type="checkbox" id="select-all-products" class="custom-checkbox">
          </th>
          <th style="width: 110px;">Codigo</th>
          <th>Descripcion</th>
          <th style="width: 150px;">Unidad / Presentación</th>
          <th style="width: 100px;">Libraje</th>
          <th style="width: 100px;">Gravedad E</th>
          <th style="width: 100px; text-align: right;">Costo Base</th>
          <th style="width: 90px; text-align: right;">Cantidad</th>
          <th style="width: 105px; text-align: center;">Estado</th>
          <th style="width: 90px; text-align: center;">Acciones</th>
        </tr>
      `;
    }

    this.selectAllCheckbox = document.getElementById('select-all-products');
    if (this.selectAllCheckbox) {
      this.selectAllCheckbox.addEventListener('change', (e) => {
        const isChecked = e.target.checked;
        if (isChecked) {
          this.products.forEach(p => this.selectedIds.add(p.id));
        } else {
          this.selectedIds.clear();
        }
        this.renderInventoryTable();
        this.updateDeleteButtonState();
      });
    }
  }

  renderInventoryTable() {
    this.renderInventoryTableHead();

    const totalItems = this.products.length;
    const totalPages = Math.max(1, Math.ceil(totalItems / this.itemsPerPage));

    if (this.currentPage > totalPages) {
      this.currentPage = totalPages;
    }

    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const paginated = this.products.slice(startIndex, startIndex + this.itemsPerPage);

    this.inventoryTableBody.innerHTML = '';

    const colCount = this.currentCategory === 'wellsite' ? 14 : 10;

    if (paginated.length === 0) {
      this.inventoryTableBody.innerHTML = `
        <tr>
          <td colspan="${colCount}" style="text-align: center; padding: 40px; color: var(--text-muted);">
            <div style="font-size: 15px; font-weight: 600; margin-bottom: 6px;">No se encontraron productos en esta categoría</div>
            <div style="font-size: 13px;">No hay resultados para "${this.escapeHtml(this.searchTerm)}".</div>
          </td>
        </tr>
      `;
    } else {
      paginated.forEach(product => {
        const isSelected = this.selectedIds.has(product.id);
        const tr = document.createElement('tr');
        if (isSelected) tr.classList.add('row-selected');

        // Calcular salidas registradas hoy para este producto
        const dailyUsos = this.usageList.filter(u => u.producto_id === product.id);
        const dailyUsed = dailyUsos.reduce((sum, u) => sum + u.cantidad, 0);

        if (this.currentCategory === 'wellsite') {
          const cumUsed = product.cum_used + dailyUsed;
          const dailyCost = dailyUsed * (product.precio_unitario || 0);

          tr.innerHTML = `
            <td style="text-align: center;">
              <input type="checkbox" class="custom-checkbox row-product-checkbox" data-id="${product.id}" ${isSelected ? 'checked' : ''}>
            </td>
            <td style="font-weight: 700; color: #0f172a;">${this.escapeHtml(product.descripcion)}</td>
            <td>${this.escapeHtml(product.unidad)}</td>
            <td class="col-num" style="font-weight: 600;">$${(product.precio_unitario || 0).toFixed(2)}</td>
            <td class="col-num">${product.stock_inicial}</td>
            <td class="col-num" style="${dailyUsed > 0 ? 'font-weight: bold; color: #2563eb;' : ''}">${dailyUsed > 0 ? dailyUsed : '-'}</td>
            <td class="col-num">${cumUsed > 0 ? cumUsed : '-'}</td>
            <td class="col-num">${product.daily_received > 0 ? product.daily_received : '-'}</td>
            <td class="col-num">${product.cum_received > 0 ? product.cum_received : '-'}</td>
            <td class="col-num">${product.daily_return > 0 ? product.daily_return : '-'}</td>
            <td class="col-num">${product.cum_return > 0 ? product.cum_return : '-'}</td>
            <td class="col-num" style="font-weight: 700; color: #0f172a;">${product.cantidad}</td>
            <td class="col-num col-cost">${dailyCost > 0 ? `$${dailyCost.toFixed(2)}` : '-'}</td>
            <td style="text-align: center;">
              <div class="action-buttons-group">
                <button class="btn-table-action btn-edit-product" data-id="${product.id}" title="Editar producto">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                </button>
                <button class="btn-table-action btn-delete-row" data-id="${product.id}" title="Eliminar producto">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
              </div>
            </td>
          `;
        } else {
          // Químicos o Líquidos
          tr.innerHTML = `
            <td style="text-align: center;">
              <input type="checkbox" class="custom-checkbox row-product-checkbox" data-id="${product.id}" ${isSelected ? 'checked' : ''}>
            </td>
            <td class="col-sku">${this.escapeHtml(product.codigo)}</td>
            <td class="col-desc">${this.escapeHtml(product.descripcion)}</td>
            <td>${this.escapeHtml(product.unidad)}</td>
            <td>${this.escapeHtml(product.libraje || 'N/A')}</td>
            <td>${this.escapeHtml(product.gravedad_especifica || 'N/A')}</td>
            <td class="col-num" style="font-weight: 600; color: #166534;">$${(product.precio_unitario || 0).toFixed(2)}</td>
            <td class="col-num">${product.cantidad.toLocaleString('es-ES')}</td>
            <td style="text-align: center;">
              <span class="status-badge ${product.estado.badge_class}">${product.estado.label}</span>
            </td>
            <td style="text-align: center;">
              <div class="action-buttons-group">
                <button class="btn-table-action btn-edit-product" data-id="${product.id}" title="Editar producto">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                </button>
                <button class="btn-table-action btn-delete-row" data-id="${product.id}" title="Eliminar producto">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
              </div>
            </td>
          `;
        }
        this.inventoryTableBody.appendChild(tr);
      });
    }

    // Eventos de fila
    this.inventoryTableBody.querySelectorAll('.row-product-checkbox').forEach(cb => {
      cb.addEventListener('change', (e) => {
        const id = parseInt(e.target.dataset.id);
        if (e.target.checked) {
          this.selectedIds.add(id);
        } else {
          this.selectedIds.delete(id);
        }
        this.renderInventoryTable();
        this.updateDeleteButtonState();
      });
    });

    this.inventoryTableBody.querySelectorAll('.btn-edit-product').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = parseInt(btn.dataset.id);
        this.openEditProductModal(id);
      });
    });

    this.inventoryTableBody.querySelectorAll('.btn-delete-row').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = parseInt(btn.dataset.id);
        this.promptDeleteSingle(id);
      });
    });

    // Checkbox principal
    if (paginated.length > 0 && paginated.every(p => this.selectedIds.has(p.id))) {
      this.selectAllCheckbox.checked = true;
    } else {
      this.selectAllCheckbox.checked = false;
    }

    this.renderPagination(totalItems, totalPages);
    this.updateDeleteButtonState();
  }

  renderPagination(totalItems, totalPages) {
    this.paginationControls.innerHTML = '';

    const prevBtn = document.createElement('button');
    prevBtn.className = 'pagination-btn';
    prevBtn.textContent = 'Anterior';
    prevBtn.disabled = this.currentPage === 1;
    prevBtn.addEventListener('click', () => {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.renderInventoryTable();
      }
    });
    this.paginationControls.appendChild(prevBtn);

    for (let p = 1; p <= totalPages; p++) {
      if (p === 1 || p === totalPages || (p >= this.currentPage - 1 && p <= this.currentPage + 1)) {
        const pageBtn = document.createElement('button');
        pageBtn.className = `pagination-btn ${p === this.currentPage ? 'active' : ''}`;
        pageBtn.textContent = p;
        pageBtn.addEventListener('click', () => {
          this.currentPage = p;
          this.renderInventoryTable();
        });
        this.paginationControls.appendChild(pageBtn);
      } else if (p === this.currentPage - 2 || p === this.currentPage + 2) {
        const ellipsis = document.createElement('span');
        ellipsis.className = 'pagination-ellipsis';
        ellipsis.textContent = '...';
        ellipsis.style.padding = '6px';
        this.paginationControls.appendChild(ellipsis);
      }
    }

    const nextBtn = document.createElement('button');
    nextBtn.className = 'pagination-btn';
    nextBtn.textContent = 'Siguiente';
    nextBtn.disabled = this.currentPage >= totalPages;
    nextBtn.addEventListener('click', () => {
      if (this.currentPage < totalPages) {
        this.currentPage++;
        this.renderInventoryTable();
      }
    });
    this.paginationControls.appendChild(nextBtn);

    const startRange = totalItems === 0 ? 0 : (this.currentPage - 1) * this.itemsPerPage + 1;
    const endRange = Math.min(this.currentPage * this.itemsPerPage, totalItems);
    this.paginationInfo.textContent = `Mostrando ${startRange}-${endRange} de ${totalItems} productos`;
  }

  updateDeleteButtonState() {
    const count = this.selectedIds.size;
    if (count > 0) {
      this.btnDeleteSelected.disabled = false;
      this.btnDeleteSelected.textContent = `Eliminar (${count})`;
    } else {
      this.btnDeleteSelected.disabled = true;
      this.btnDeleteSelected.textContent = 'Eliminar';
    }
  }

  // Modales de Creación y Edición
  openCreateProductModal() {
    this.editingProductId = null;
    this.productModalTitle.textContent = 'Creacion de Productos';
    this.btnModalSubmit.textContent = 'Crear';
    this.formProductCrud.reset();
    this.modalProductId.value = '';
    this.modalCategoria.value = this.currentCategory;
    this.modalCodigo.value = this.generateRandomSku();
    this.modalCantidad.value = 0;
    this.modalPrecioUnitario.value = '0.00';
    this.modalLibraje.value = 'N/A';
    this.modalGravedad.value = 'N/A';
    this.productModal.classList.add('active');
  }

  openEditProductModal(id) {
    const product = (this.allProducts && this.allProducts.find(p => p.id === id)) || this.products.find(p => p.id === id);
    if (!product) return;

    this.editingProductId = id;
    this.productModalTitle.textContent = 'Modificar Producto';
    this.btnModalSubmit.textContent = 'Guardar';

    this.modalProductId.value = product.id;
    this.modalCodigo.value = product.codigo;
    this.modalDescripcion.value = product.descripcion;
    this.modalUnidad.value = product.unidad;
    this.modalLibraje.value = product.libraje || 'N/A';
    this.modalGravedad.value = product.gravedad_especifica || 'N/A';
    this.modalCantidad.value = product.cantidad;
    this.modalCategoria.value = product.categoria || 'quimico';
    this.modalPrecioUnitario.value = (product.precio_unitario || 0).toFixed(2);

    this.productModal.classList.add('active');
  }

  closeProductModal() {
    this.productModal.classList.remove('active');
    this.editingProductId = null;
  }

  async handleSaveProduct() {
    const codigo = this.modalCodigo.value.trim() || this.generateRandomSku();
    const descripcion = this.modalDescripcion.value.trim();
    const unidad = this.modalUnidad.value.trim();
    const libraje = this.modalLibraje.value.trim() || 'N/A';
    const gravedad = this.modalGravedad.value.trim() || 'N/A';
    const cantidad = parseInt(this.modalCantidad.value) || 0;
    const categoria = this.modalCategoria.value;
    const precio_unitario = parseFloat(this.modalPrecioUnitario.value) || 0;

    if (!descripcion) {
      this.showToast('La descripción del producto es obligatoria', 'error');
      return;
    }

    const payload = {
      codigo,
      descripcion,
      unidad,
      libraje,
      gravedad_especifica: gravedad,
      cantidad,
      categoria,
      precio_unitario
    };

    try {
      let url = '/api/productos/';
      let method = 'POST';

      if (this.editingProductId) {
        url = `/api/productos/${this.editingProductId}/`;
        method = 'PUT';
      }

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (data.success) {
        this.showToast(data.mensaje || 'Operación exitosa', 'success');
        this.closeProductModal();
        await this.fetchProducts();
      } else {
        this.showToast(data.error || 'Ocurrió un error al guardar', 'error');
      }
    } catch (err) {
      console.error(err);
      this.showToast('Error de conexión con el servidor', 'error');
    }
  }

  promptDeleteSingle(id) {
    const product = this.products.find(p => p.id === id);
    if (!product) return;

    this.confirmModalTitle.textContent = 'Confirmar Eliminación';
    this.confirmModalMsg.textContent = `¿Está seguro de que desea eliminar "${product.descripcion}" (${product.codigo}) del inventario?`;
    this.pendingDeleteAction = async () => {
      try {
        const response = await fetch(`/api/productos/${id}/`, { method: 'DELETE' });
        const data = await response.json();
        if (data.success) {
          this.selectedIds.delete(id);
          this.showToast(`Producto ${product.codigo} eliminado`, 'success');
          await this.fetchProducts();
        } else {
          this.showToast(data.error || 'Error al eliminar', 'error');
        }
      } catch (e) {
        this.showToast('Error al conectar con el servidor', 'error');
      }
    };
    this.confirmModal.classList.add('active');
  }

  promptDeleteSelected() {
    const count = this.selectedIds.size;
    if (count === 0) return;

    this.confirmModalTitle.textContent = 'Confirmar Eliminación Múltiple';
    this.confirmModalMsg.textContent = `¿Está seguro de que desea eliminar los ${count} productos seleccionados?`;
    this.pendingDeleteAction = async () => {
      for (const id of Array.from(this.selectedIds)) {
        await fetch(`/api/productos/${id}/`, { method: 'DELETE' });
      }
      this.selectedIds.clear();
      this.showToast(`${count} productos eliminados del inventario`, 'success');
      await this.fetchProducts();
    };
    this.confirmModal.classList.add('active');
  }

  closeConfirmModal() {
    this.confirmModal.classList.remove('active');
    this.pendingDeleteAction = null;
  }

  // ============================================================================
  // 7. MÓDULO USO (COMBOBOX FUSIONADO, CÁLCULO DE COSTO Y SUBTOTALES)
  // ============================================================================
  populateProductSelect(filterText = '') {
    this.renderComboboxList(filterText);
  }

  renderComboboxList(filterText = '') {
    if (!this.usoComboboxList) return;
    this.usoComboboxList.innerHTML = '';

    const filter = (filterText || '').trim().toLowerCase();
    const sourceProducts = (this.allProducts && this.allProducts.length > 0) ? this.allProducts : this.products;
    let filtered = sourceProducts;

    if (filter) {
      filtered = sourceProducts.filter(p => {
        const codigo = (p.codigo || '').toLowerCase();
        const desc = (p.descripcion || '').toLowerCase();
        const cat = (p.categoria || '').toLowerCase();
        return codigo.includes(filter) || desc.includes(filter) || cat.includes(filter);
      });
    }

    if (filtered.length === 0) {
      const li = document.createElement('li');
      li.className = 'combobox-empty';
      li.textContent = `No se encontraron productos con "${filterText}"`;
      this.usoComboboxList.appendChild(li);
      return;
    }

    const currentId = parseInt(this.usoSelectProducto.value) || null;

    filtered.forEach(p => {
      const li = document.createElement('li');
      li.className = `combobox-item ${p.id === currentId ? 'selected' : ''}`;
      li.dataset.id = p.id;
      const catBadge = p.categoria === 'liquido' ? '<span style="font-size:10px; background:#e0f2fe; color:#0369a1; padding:2px 5px; border-radius:3px; margin-left:6px;">💧 Líquido</span>' : (p.categoria === 'wellsite' ? '<span style="font-size:10px; background:#fef3c7; color:#92400e; padding:2px 5px; border-radius:3px; margin-left:6px;">🛢️ Wellsite</span>' : '<span style="font-size:10px; background:#ecfdf5; color:#047857; padding:2px 5px; border-radius:3px; margin-left:6px;">🧪 Químico</span>');
      li.innerHTML = `
        <div class="combobox-item-main">
          <span class="combobox-item-code">${this.escapeHtml(p.codigo)}</span>
          <span class="combobox-item-desc">${this.escapeHtml(p.descripcion)} ${catBadge}</span>
        </div>
        <div style="text-align: right;">
          <span class="combobox-item-stock">Stock: ${p.cantidad} ${this.escapeHtml(p.unidad)}</span>
          ${p.precio_unitario > 0 ? `<div style="font-size:11px; color:#166534; font-weight:600;">$${p.precio_unitario.toFixed(2)}</div>` : ''}
        </div>
      `;
      const selectAction = (e) => {
        if (e) {
          e.preventDefault();
          e.stopPropagation();
        }
        this.selectProductInCombobox(p);
      };
      li.addEventListener('mousedown', selectAction);
      li.addEventListener('click', selectAction);
      this.usoComboboxList.appendChild(li);
    });
  }

  openComboboxDropdown() {
    if (!this.usoComboboxDropdown) return;
    this.usoComboboxDropdown.style.display = 'block';
    if (this.usoComboboxToggleBtn) {
      this.usoComboboxToggleBtn.classList.add('open');
    }
    const currentId = parseInt(this.usoSelectProducto.value);
    const pool = (this.allProducts && this.allProducts.length > 0) ? this.allProducts : this.products;
    const currentProd = pool.find(p => p.id === currentId);
    if (!this.usoProductSearchInput || !this.usoProductSearchInput.value || (currentProd && this.usoProductSearchInput.value === `${currentProd.codigo} - ${currentProd.descripcion}`)) {
      this.renderComboboxList('');
    } else {
      this.renderComboboxList(this.usoProductSearchInput ? this.usoProductSearchInput.value : '');
    }
  }

  closeComboboxDropdown() {
    if (!this.usoComboboxDropdown) return;
    this.usoComboboxDropdown.style.display = 'none';
    if (this.usoComboboxToggleBtn) {
      this.usoComboboxToggleBtn.classList.remove('open');
    }
  }

  selectProductInCombobox(product) {
    if (!product) return;
    this.usoSelectProducto.value = product.id;
    this.usoProductSearchInput.value = `${product.codigo} - ${product.descripcion}`;
    if (this.usoComboboxClearBtn) {
      this.usoComboboxClearBtn.style.display = 'flex';
    }
    this.closeComboboxDropdown();
    this.onProductSelectionChange();
  }

  clearComboboxSelection() {
    this.usoSelectProducto.value = '';
    if (this.usoProductSearchInput) {
      this.usoProductSearchInput.value = '';
    }
    if (this.usoComboboxClearBtn) {
      this.usoComboboxClearBtn.style.display = 'none';
    }
    this.onProductSelectionChange();
    this.renderComboboxList('');
  }

  onProductSelectionChange() {
    const productId = parseInt(this.usoSelectProducto.value);
    const pool = (this.allProducts && this.allProducts.length > 0) ? this.allProducts : this.products;
    const product = pool.find(p => p.id === productId);

    if (product) {
      const stock = product.cantidad || 0;
      const unit = product.unidad || '';
      const catLabel = product.categoria === 'liquido' ? '💧 Líquido' : (product.categoria === 'wellsite' ? '🛢️ Wellsite' : '🧪 Químico');
      this.usoStockDisponibleHint.textContent = `[${catLabel}] Stock disponible: ${stock} ${unit}`;
      this.usoStockDisponibleHint.style.color = stock > 0 ? 'var(--text-muted)' : '#dc2626';

      // Auto-completar precio si el producto ya tiene un costo configurado
      if (product.precio_unitario && product.precio_unitario > 0) {
        this.usoInputPrecio.value = product.precio_unitario.toFixed(2);
      }
    } else {
      this.usoStockDisponibleHint.textContent = 'Stock disponible: -';
      this.usoStockDisponibleHint.style.color = 'var(--text-muted)';
    }
    this.updateLiveCalculation();
  }

  updateLiveCalculation() {
    const cantidad = parseFloat(this.usoInputCantidad.value) || 0;
    const precio = parseFloat(this.usoInputPrecio.value) || 0;
    const subtotal = cantidad * precio;

    this.usoLiveSubtotal.textContent = `$${subtotal.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }

  async fetchUsageData() {
    try {
      const url = this.selectedReportDate ? `/api/registro-uso/?fecha=${this.selectedReportDate}` : '/api/registro-uso/';
      const response = await fetch(url);
      const data = await response.json();
      if (data.success) {
        this.usageList = data.usos;
        this.badgeUsoCount.textContent = data.total_items;
        this.usoCounterBadge.textContent = `${data.total_items} registros`;
        this.usoGrandTotalAmount.textContent = `$${data.costo_total_acumulado.toFixed(2)}`;
        this.usoCostoTotalHeader.textContent = `$${data.costo_total_acumulado.toFixed(2)}`;
        this.genCostoTotal.textContent = `$${data.costo_total_acumulado.toFixed(2)}`;
        this.renderUsageTable();
      }
    } catch (e) {
      console.error('Error al cargar registros de uso:', e);
    }
  }

  renderUsageTable() {
    this.usoTableBody.innerHTML = '';

    if (this.usageList.length === 0) {
      this.usoTableBody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; padding: 30px; color: var(--text-muted);">
            No hay salidas de productos registradas para este reporte.
          </td>
        </tr>
      `;
      return;
    }

    this.usageList.forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="col-sku">${this.escapeHtml(item.producto_codigo)}</td>
        <td class="col-desc">${this.escapeHtml(item.producto_descripcion)}</td>
        <td style="text-align: right; font-weight: 600;">${item.cantidad} ${this.escapeHtml(item.producto_unidad)}</td>
        <td style="text-align: right;">$${item.precio_unitario.toFixed(2)}</td>
        <td style="text-align: right; font-weight: 700; color: var(--primary-navy);">$${item.costo_total.toFixed(2)}</td>
        <td style="font-size: 12px; color: var(--text-muted);">${this.escapeHtml(item.observacion || '-')}</td>
        <td style="text-align: center;">
          <button class="btn-table-action btn-delete-uso" data-id="${item.id}" title="Revertir y devolver al stock">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          </button>
        </td>
      `;
      this.usoTableBody.appendChild(tr);
    });

    this.usoTableBody.querySelectorAll('.btn-delete-uso').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = parseInt(btn.dataset.id);
        this.handleDeleteUso(id);
      });
    });
  }

  async handleSubmitUso() {
    const producto_id = this.usoSelectProducto.value;
    const cantidad = parseInt(this.usoInputCantidad.value) || 0;
    const precio_unitario = parseFloat(this.usoInputPrecio.value) || 0;
    const observacion = this.usoInputObservacion.value.trim();

    if (!producto_id) {
      this.showToast('Debe seleccionar un producto químico', 'error');
      return;
    }

    if (cantidad <= 0) {
      this.showToast('La cantidad debe ser mayor a 0', 'error');
      return;
    }

    const payload = {
      producto_id,
      cantidad,
      precio_unitario,
      observacion
    };

    try {
      const url = this.selectedReportDate ? `/api/registro-uso/?fecha=${this.selectedReportDate}` : '/api/registro-uso/';
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();

      if (data.success) {
        this.showToast(data.mensaje || 'Salida registrada correctamente', 'success');
        this.formRegistroUso.reset();
        this.clearComboboxSelection();
        this.usoLiveSubtotal.textContent = '$0.00';
        
        // Refresca catálogo y datos de uso
        await this.fetchProducts();
        await this.fetchUsageData();
        await this.fetchDailyReport();
      } else {
        this.showToast(data.error || 'Error al registrar uso', 'error');
      }
    } catch (e) {
      console.error(e);
      this.showToast('Error de conexión con el servidor', 'error');
    }
  }

  async handleDeleteUso(id) {
    if (!confirm('¿Desea revertir esta salida y restituir el producto al inventario?')) return;

    try {
      const response = await fetch(`/api/registro-uso/${id}/`, { method: 'DELETE' });
      const data = await response.json();
      if (data.success) {
        this.showToast(data.mensaje || 'Registro revertido', 'success');
        await this.fetchProducts();
        await this.fetchUsageData();
        await this.fetchDailyReport();
      } else {
        this.showToast(data.error || 'Error al revertir', 'error');
      }
    } catch (e) {
      this.showToast('Error de conexión', 'error');
    }
  }

  // ============================================================================
  // 8. MÓDULO DE IMPRESIÓN Y PLANILLA OFICIAL AOS (CON N° REPORTE Y COSTOS)
  // ============================================================================
  async openPrintPreview() {
    try {
      const url = this.selectedReportDate
        ? `/api/reporte-oficial/?fecha=${this.selectedReportDate}&categoria=${this.currentPrintCategory}`
        : `/api/reporte-oficial/?categoria=${this.currentPrintCategory}`;
      const response = await fetch(url);
      const data = await response.json();
      if (data.success) {
        let sheetHtml = '';
        if (this.currentPrintCategory === 'wellsite') {
          sheetHtml = this.buildWellsiteDailyReportSheetHtml(
            data.reporte,
            data.wellsite_filas || [],
            data.desglose_costos || [],
            data.total_wellsite_daily_cost || 0,
            data.total_wellsite_cum_cost || 0
          );
        } else {
          const isLiquid = (this.currentPrintCategory === 'liquido');
          sheetHtml = this.buildAosOfficialSheetHtml(
            data.reporte,
            data.filas || [],
            data.desglose_costos || [],
            data.costo_categoria !== undefined ? data.costo_categoria : data.costo_total_acumulado,
            isLiquid
          );
        }
        this.printPreviewContent.innerHTML = sheetHtml;
        this.printSheetContainer.innerHTML = sheetHtml;
        this.printPreviewModal.classList.add('active');
      }
    } catch (e) {
      console.error(e);
      this.showToast('Error al generar la vista previa del reporte oficial', 'error');
    }
  }

  closePrintPreview() {
    this.printPreviewModal.classList.remove('active');
  }

  buildAosOfficialSheetHtml(reporte, filas, desglose_costos = [], costo_total = 0, isLiquid = false) {
    let rowsHtml = '';
    filas.forEach(f => {
      const hasExcelMarker = (f.item === 35);
      rowsHtml += `
        <tr>
          <td class="td-item-num">${f.item}</td>
          <td class="td-desc">${this.escapeHtml(f.descripcion)}</td>
          <td class="td-pres">${this.escapeHtml(f.presentacion)}</td>
          <td class="td-num-red ${hasExcelMarker ? 'td-excel-marker' : ''}">${f.inicial}</td>
          <td class="td-num-black">${f.entrada > 0 ? f.entrada : 0}</td>
          <td class="td-num-black">${f.total_existente > 0 ? f.total_existente : ''}</td>
          <td class="td-num-black">${f.salida > 0 ? f.salida : 0}</td>
          <td class="td-num-red">${f.stock_final}</td>
        </tr>
      `;
    });

    // Desglose de costos de salidas
    let costosRows = '';
    if (desglose_costos && desglose_costos.length > 0) {
      desglose_costos.forEach(item => {
        costosRows += `
          <tr>
            <td style="font-weight: bold; text-align: center;">${this.escapeHtml(item.producto_codigo)}</td>
            <td>${this.escapeHtml(item.producto_descripcion)}</td>
            <td style="text-align: right;">${item.cantidad} ${this.escapeHtml(item.producto_unidad)}</td>
            <td style="text-align: right;">$${item.precio_unitario.toFixed(2)}</td>
            <td style="text-align: right; font-weight: bold;">$${item.costo_total.toFixed(2)}</td>
            <td style="font-size: 9px; color: #555;">${this.escapeHtml(item.observacion || '-')}</td>
          </tr>
        `;
      });
    } else {
      costosRows = `
        <tr>
          <td colspan="6" style="text-align: center; color: #777; padding: 6px;">No se registraron salidas de productos en este reporte.</td>
        </tr>
      `;
    }

    const codigoRep = reporte.codigo_reporte || `REP-${reporte.id}`;
    const reportTitle = isLiquid ? 'INVENTARIO DE PRODUCTOS LÍQUIDOS' : 'INVENTARIO DE PRODUCTOS QUÍMICOS';

    return `
      <div class="aos-official-sheet">
        <!-- Encabezado con Logotipo Vectorial Estilizado AOS -->
        <table class="aos-excel-grid">
          <tr class="aos-header-row">
            <td class="aos-logo-cell">
              <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <svg viewBox="0 0 260 85" width="220" height="70" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <linearGradient id="aosGradMain" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#0066cc"/>
                      <stop offset="50%" stop-color="#0044aa"/>
                      <stop offset="100%" stop-color="#002277"/>
                    </linearGradient>
                  </defs>
                  <text x="130" y="48" font-family="'Arial Black', Impact, sans-serif" font-weight="900" font-size="50" fill="url(#aosGradMain)" text-anchor="middle" letter-spacing="-2">AOS</text>
                  <path d="M 20 54 Q 130 36 240 40 Q 170 60 20 54 Z" fill="#e52424" opacity="0.95" />
                  <text x="130" y="67" font-family="Arial, Helvetica, sans-serif" font-weight="bold" font-size="10" fill="#002b66" text-anchor="middle" letter-spacing="1.2">ALL OIL SERVICES, C.A.</text>
                  <rect x="75" y="72" width="110" height="11" fill="#d32f2f" rx="1.5" />
                  <text x="130" y="81" font-family="Arial, Helvetica, sans-serif" font-weight="bold" font-size="8" fill="#ffffff" text-anchor="middle" letter-spacing="0.5">RIF: J-31267150-5</text>
                </svg>
              </div>
            </td>
            <td class="aos-title-cell">
              <div>${reportTitle}</div>
              <div style="font-size: 11px; font-weight: bold; color: #0044aa; margin-top: 4px;">N° REPORTE: ${this.escapeHtml(codigoRep)}</div>
            </td>
          </tr>
          <tr class="aos-meta-row">
            <td class="aos-meta-cell">DEPARTAMENTO: ${this.escapeHtml(reporte.departamento)}</td>
            <td class="aos-meta-cell">
              <div style="display: flex; justify-content: space-between;">
                <span>ENCARGADO: ${this.escapeHtml(reporte.encargado)}</span>
                <span>FECHA: ${this.escapeHtml(reporte.fecha_formato)}</span>
              </div>
            </td>
          </tr>
        </table>

        <!-- Tabla de Datos Físicos -->
        <table class="aos-table-data">
          <thead>
            <tr>
              <th rowspan="2" style="width: 30px;">ITEM</th>
              <th rowspan="2" style="width: 270px;">DESCRIPCION</th>
              <th rowspan="2" style="width: 140px;">PRESENTACION</th>
              <th colspan="2" style="width: 90px;">Cantidad</th>
              <th colspan="3" style="width: 140px;">INVENTARIO FISICO</th>
            </tr>
            <tr>
              <th style="width: 48px;">Inicial</th>
              <th style="width: 42px;">Entrada</th>
              <th style="width: 48px;">Total<br>Existente</th>
              <th style="width: 42px;">Total<br>Salida</th>
              <th style="width: 50px;">Stock<br>Final</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
        </table>

        <!-- Sección de Desglose de Costos de Salidas -->
        <div class="aos-costs-section">
          <div class="aos-costs-header">
            <span>DETALLE DE PRODUCTOS UTILIZADOS Y COSTO DE SALIDAS (REPORTE ${this.escapeHtml(codigoRep)})</span>
            <span>TOTAL: $${costo_total.toFixed(2)}</span>
          </div>
          <table class="aos-costs-table">
            <thead>
              <tr>
                <th style="width: 75px;">CÓDIGO</th>
                <th>PRODUCTO</th>
                <th style="width: 85px;">CANTIDAD</th>
                <th style="width: 95px;">PRECIO UNIT.</th>
                <th style="width: 105px;">SUBTOTAL ($)</th>
                <th>OBSERVACIÓN</th>
              </tr>
            </thead>
            <tbody>
              ${costosRows}
              <tr class="aos-costs-total-row">
                <td colspan="4" style="text-align: right; padding: 5px;">COSTO TOTAL DE SALIDAS:</td>
                <td style="text-align: right; padding: 5px; color: #166534; font-size: 11px;">$${costo_total.toFixed(2)}</td>
                <td></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Observaciones Generales -->
        <div class="aos-obs-box">
          OBSERVACIONES: ${this.escapeHtml(reporte.observaciones || '')}
        </div>

        <!-- Cuadro de Firmas Oficiales -->
        <table class="aos-signatures-grid">
          <tr>
            <td class="aos-sig-header" style="width: 50%;">REALIZADO POR:</td>
            <td class="aos-sig-header" style="width: 50%;">REVISADO POR:</td>
          </tr>
          <tr>
            <td>
              <div class="aos-sig-row"><strong>NOMBRE:</strong> ${this.escapeHtml(reporte.elaborado_por_nombre)}</div>
              <div class="aos-sig-row"><strong>CARGO:</strong> ${this.escapeHtml(reporte.elaborado_por_cargo)}</div>
              <div class="aos-sig-row"><strong>FECHA:</strong> ${this.escapeHtml(reporte.fecha_formato)}</div>
              <div class="aos-sig-row aos-sig-space"><strong>FIRMA:</strong></div>
            </td>
            <td>
              <div class="aos-sig-row"><strong>NOMBRE:</strong> ${this.escapeHtml(reporte.revisado_por_nombre)}</div>
              <div class="aos-sig-row"><strong>CARGO:</strong> ${this.escapeHtml(reporte.revisado_por_cargo)}</div>
              <div class="aos-sig-row"><strong>FECHA:</strong> ${this.escapeHtml(reporte.fecha_formato)}</div>
              <div class="aos-sig-row aos-sig-space"><strong>FIRMA:</strong></div>
            </td>
          </tr>
        </table>
      </div>
    `;
  }

  buildWellsiteDailyReportSheetHtml(reporte, wellsite_filas = [], desglose_costos = [], daily_cost = 0, cum_cost = 0) {
    let rowsHtml = '';
    wellsite_filas.forEach(f => {
      rowsHtml += `
        <tr>
          <td style="font-weight: bold;">${this.escapeHtml(f.product)}</td>
          <td style="text-align: center;">${this.escapeHtml(f.unit_size)}</td>
          <td class="text-right">${f.unit_price > 0 ? f.unit_price.toFixed(2) : ''}</td>
          <td class="text-right">${f.start_amt > 0 ? f.start_amt : ''}</td>
          <td class="text-right" style="${f.daily_used > 0 ? 'font-weight:bold; color:#0284c7;' : ''}">${f.daily_used > 0 ? f.daily_used : ''}</td>
          <td class="text-right">${f.cum_used > 0 ? f.cum_used : ''}</td>
          <td class="text-right">${f.daily_received > 0 ? f.daily_received : ''}</td>
          <td class="text-right">${f.cum_received > 0 ? f.cum_received : ''}</td>
          <td class="text-right">${f.daily_return > 0 ? f.daily_return : ''}</td>
          <td class="text-right">${f.cum_return > 0 ? f.cum_return : ''}</td>
          <td class="text-right" style="font-weight: bold;">${f.final_stock}</td>
          <td class="text-right ${f.daily_cost > 0 ? 'cost-highlight' : ''}">${f.daily_cost > 0 ? f.daily_cost.toFixed(2) : ''}</td>
        </tr>
      `;
    });

    const reportNo = reporte.reporte_no_wellsite || '16';
    const operator = reporte.operador || 'Cardon IV';
    const wellName = reporte.pozo || 'Perla-1X';
    const location = reporte.locacion || 'Offshore';

    return `
      <div class="wellsite-sheet">
        <!-- Encabezado Estilo M-I SWACO -->
        <div class="wellsite-header">
          <div class="wellsite-brand-row">
            <div style="font-family: Arial, Helvetica, sans-serif; font-size: 24px; font-weight: 900; letter-spacing: -1px; color: #000;">
              M<span style="color:#d97706;">i</span> SWACO
              <div style="height: 3px; background: linear-gradient(90deg, #d97706 0%, #b45309 60%, transparent 100%); margin-top: 2px;"></div>
            </div>
            <div class="wellsite-main-title">
              <h1>WELLSITE CHEMICAL INVENTORY</h1>
              <h2>Daily Report</h2>
            </div>
            <div style="width: 120px; text-align: right; font-size: 11px; color: #555;">
              A Schlumberger Co.
            </div>
          </div>

          <div class="wellsite-meta-grid">
            <div class="wellsite-meta-item">
              <span class="wellsite-meta-label">Operator:</span>
              <span>${this.escapeHtml(operator)}</span>
            </div>
            <div class="wellsite-meta-item">
              <span class="wellsite-meta-label">Date:</span>
              <span>${this.escapeHtml(reporte.fecha_formato)}</span>
            </div>
            <div class="wellsite-meta-item">
              <span class="wellsite-meta-label">Well Name:</span>
              <span>${this.escapeHtml(wellName)}</span>
            </div>
            <div class="wellsite-meta-item">
              <span class="wellsite-meta-label">Report No:</span>
              <span>${this.escapeHtml(reportNo)}</span>
            </div>
            <div class="wellsite-meta-item">
              <span class="wellsite-meta-label">Location:</span>
              <span>${this.escapeHtml(location)}</span>
            </div>
            <div class="wellsite-meta-item">
              <span class="wellsite-meta-label">Page:</span>
              <span>1</span>
            </div>
          </div>
        </div>

        <!-- Cost Summary Box -->
        <div class="wellsite-cost-summary">
          <div class="wellsite-cost-title">Cost Summary</div>
          <div class="wellsite-cost-row">
            <div class="wellsite-cost-cell">
              <span>Total Daily Cost:</span>
              <span class="amt">$${daily_cost.toFixed(2)}</span>
            </div>
            <div class="wellsite-cost-cell">
              <span>Total Daily Tax:</span>
              <span>$0.00</span>
            </div>
            <div class="wellsite-cost-cell">
              <span>Cumulative Cost:</span>
              <span class="amt">$${cum_cost.toFixed(2)}</span>
            </div>
          </div>
        </div>

        <!-- Tabla Wellsite -->
        <table class="wellsite-table">
          <thead>
            <tr>
              <th rowspan="2" style="width: 210px;">Product</th>
              <th rowspan="2" style="width: 85px;">Unit<br>Size</th>
              <th rowspan="2" style="width: 75px;">Unit<br>Price</th>
              <th rowspan="2" style="width: 65px;">Start<br>Amt.</th>
              <th rowspan="2" style="width: 65px;">Daily<br>Used</th>
              <th rowspan="2" style="width: 65px;">Cum<br>Used</th>
              <th rowspan="2" style="width: 65px;">Daily<br>Rec'd</th>
              <th rowspan="2" style="width: 65px;">Cum<br>Rec'd</th>
              <th rowspan="2" style="width: 65px;">Daily<br>Return</th>
              <th rowspan="2" style="width: 65px;">Cum.<br>Return</th>
              <th rowspan="2" style="width: 70px;">Final<br>Stock</th>
              <th rowspan="2" style="width: 80px;">Daily<br>Cost</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
        </table>
      </div>
    `;
  }

  // ============================================================================
  // 9. HELPERS Y UTILIDADES
  // ============================================================================
  generateRandomSku() {
    let prefix = 'AOS';
    const cat = (this.modalCategoria ? this.modalCategoria.value : this.currentCategory);
    if (cat === 'liquido') {
      prefix = 'AOS-LIQ';
    } else if (cat === 'wellsite') {
      prefix = 'WELL';
    }
    const pool = (this.allProducts && this.allProducts.length > 0) ? this.allProducts : this.products;
    const existingSkus = pool.map(p => p.codigo);
    let sku;
    let attempts = 0;
    do {
      const randomNum = Math.floor(1000 + Math.random() * 9000);
      sku = `${prefix}-${randomNum}`;
      attempts++;
    } while (existingSkus.includes(sku) && attempts < 1000);
    return sku;
  }

  showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span>${type === 'success' ? '✓' : '⚠️'}</span>
      <span>${this.escapeHtml(message)}</span>
    `;
    this.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.25s ease';
      setTimeout(() => toast.remove(), 250);
    }, 3200);
  }

  escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
  window.chapalaApp = new ChapalaApp();
});
