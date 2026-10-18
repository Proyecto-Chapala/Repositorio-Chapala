/**
 * app.js - Funcionalidad Global y Shell de la Aplicación
 * - Control de colapso de barra lateral (Sidebar)
 * - Sistema centralizado de notificaciones (Toast)
 */

window.App = {
  init() {
    this.initSidebar();
    this.initPanelReportes();
  },

  initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('toggleSidebarBtn');

    if (sidebar && toggleBtn) {
      // Cargar preferencia guardada en localStorage
      const isCollapsed = localStorage.getItem('chapala_sidebar_collapsed') === 'true';
      if (isCollapsed) {
        sidebar.classList.add('collapsed');
      }

      toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        localStorage.setItem('chapala_sidebar_collapsed', sidebar.classList.contains('collapsed'));
      });
    }
  },

  // Panel "Reportes": lista de pozos con buscador, se abre desde la barra lateral
  initPanelReportes() {
    const boton = document.getElementById('btnPanelReportes');
    const panel = document.getElementById('panelReportes');
    if (!boton || !panel) return;

    const buscador = document.getElementById('buscarPozoReportes');
    const filas = panel.querySelectorAll('li[data-nombre]');
    const sinResultados = document.getElementById('sinResultadosReportes');

    const abrir = () => {
      panel.hidden = false;
      boton.setAttribute('aria-expanded', 'true');
      buscador.focus();
    };
    const cerrar = () => {
      panel.hidden = true;
      boton.setAttribute('aria-expanded', 'false');
    };
    const filtrar = () => {
      const texto = buscador.value.trim().toLowerCase();
      let visibles = 0;
      filas.forEach((fila) => {
        const coincide = fila.dataset.nombre.includes(texto);
        fila.hidden = !coincide;
        if (coincide) visibles += 1;
      });
      sinResultados.hidden = visibles > 0 || filas.length === 0;
    };

    boton.addEventListener('click', () => (panel.hidden ? abrir() : cerrar()));
    document.getElementById('btnCerrarPanelReportes').addEventListener('click', () => {
      cerrar();
      boton.focus();
    });
    buscador.addEventListener('input', filtrar);
    // Flecha abajo pasa a la lista; Enter abre el primer pozo que coincide
    buscador.addEventListener('keydown', (evento) => {
      if (evento.key !== 'ArrowDown' && evento.key !== 'Enter') return;
      const primero = panel.querySelector('li[data-nombre]:not([hidden]) a');
      if (!primero) return;
      evento.preventDefault();
      if (evento.key === 'Enter') primero.click();
      else primero.focus();
    });
    panel.addEventListener('keydown', (evento) => {
      if (evento.key !== 'Escape') return;
      cerrar();
      boton.focus();
    });
    document.addEventListener('click', (evento) => {
      if (!panel.hidden && !panel.contains(evento.target) && !boton.contains(evento.target)) cerrar();
    });
  },

  showToast(mensaje, tipo = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.innerHTML = `
      <span style="font-size:1.1rem;">${tipo === 'success' ? '✓' : '⚠'}</span>
      <span>${mensaje}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(8px)';
      toast.style.transition = 'all 0.25s ease';
      setTimeout(() => toast.remove(), 250);
    }, 4000);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
