/**
 * app.js - Funcionalidad Global y Shell de la Aplicación
 * - Control de colapso de barra lateral (Sidebar)
 * - Sistema centralizado de notificaciones (Toast)
 */

window.App = {
  init() {
    this.initSidebar();
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
