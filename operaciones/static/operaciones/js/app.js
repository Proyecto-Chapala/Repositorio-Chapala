/**
 * app.js - Funcionalidad Global y Shell de la Aplicación
 * - Control de colapso de barra lateral (Sidebar)
 * - Buscador global (Ctrl+K)
 * - Sistema centralizado de notificaciones (Toast)
 */

window.App = {
  init() {
    this.initSidebar();
    this.initBuscador();
    this.initSelectorPozo();
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

  // Buscador global (Ctrl+K): pozos, sus reportes y las pantallas del pozo abierto.
  // Cada palabra escrita debe aparecer en el texto del resultado ("reportes prueba").
  initBuscador() {
    const velo = document.getElementById('buscadorGlobal');
    if (!velo) return;

    const entrada = document.getElementById('buscadorTexto');
    const lista = document.getElementById('buscadorResultados');
    const vacio = document.getElementById('buscadorVacio');
    const filas = Array.from(lista.querySelectorAll('li[data-texto]'));
    const MAXIMO_POR_GRUPO = 6;
    const TITULOS = { reportes: 'Reportes', pozos: 'Pozos', pantallas: 'Configuración del pozo' };
    let enlacesVisibles = [];
    let seleccionado = 0;
    let focoAnterior = null;

    // Un título por grupo, antes de su primer resultado
    const titulos = {};
    Object.keys(TITULOS).forEach((grupo) => {
      const primera = filas.find((fila) => fila.dataset.grupo === grupo);
      if (!primera) return;
      const titulo = document.createElement('li');
      titulo.className = 'buscador-grupo';
      titulo.textContent = TITULOS[grupo];
      lista.insertBefore(titulo, primera);
      titulos[grupo] = titulo;
    });

    const marcar = () => {
      lista.querySelectorAll('.seleccionado').forEach((enlace) => enlace.classList.remove('seleccionado'));
      const actual = enlacesVisibles[seleccionado];
      if (!actual) return;
      actual.classList.add('seleccionado');
      actual.scrollIntoView({ block: 'nearest' });
    };

    const filtrar = () => {
      const palabras = entrada.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      const porGrupo = {};
      filas.forEach((fila) => {
        const grupo = fila.dataset.grupo;
        const coincide = palabras.every((palabra) => fila.dataset.texto.includes(palabra));
        porGrupo[grupo] = (porGrupo[grupo] || 0) + (coincide ? 1 : 0);
        fila.hidden = !coincide || porGrupo[grupo] > MAXIMO_POR_GRUPO;
      });
      Object.entries(titulos).forEach(([grupo, titulo]) => { titulo.hidden = !porGrupo[grupo]; });
      enlacesVisibles = filas.filter((fila) => !fila.hidden).map((fila) => fila.querySelector('a'));
      vacio.hidden = enlacesVisibles.length > 0;
      seleccionado = 0;
      marcar();
    };

    const abrir = (texto = '') => {
      focoAnterior = document.activeElement;
      velo.hidden = false;
      entrada.value = texto;
      filtrar();
      entrada.focus();
    };
    const cerrar = () => {
      velo.hidden = true;
      if (focoAnterior) focoAnterior.focus();
    };

    entrada.addEventListener('input', filtrar);
    entrada.addEventListener('keydown', (evento) => {
      if (evento.key === 'ArrowDown' || evento.key === 'ArrowUp') {
        evento.preventDefault();
        const paso = evento.key === 'ArrowDown' ? 1 : -1;
        seleccionado = Math.min(Math.max(seleccionado + paso, 0), enlacesVisibles.length - 1);
        marcar();
      } else if (evento.key === 'Enter' && enlacesVisibles[seleccionado]) {
        evento.preventDefault();
        enlacesVisibles[seleccionado].click();
      }
    });
    velo.addEventListener('keydown', (evento) => { if (evento.key === 'Escape') cerrar(); });
    velo.addEventListener('click', (evento) => { if (evento.target === velo) cerrar(); });

    document.addEventListener('keydown', (evento) => {
      if ((evento.ctrlKey || evento.metaKey) && evento.key.toLowerCase() === 'k') {
        evento.preventDefault();
        if (velo.hidden) abrir(); else cerrar();
      }
    });
    document.getElementById('btnBuscarGlobal').addEventListener('click', () => abrir());
    document.querySelectorAll('[data-abrir-buscador]').forEach((boton) => {
      boton.addEventListener('click', () => abrir(boton.dataset.abrirBuscador));
    });
  },

  // Selector de pozo de la barra superior: lista con buscador; cada pozo abre la misma pantalla.
  initSelectorPozo() {
    const boton = document.getElementById('selectorPozoBoton');
    const menu = document.getElementById('selectorPozoMenu');
    if (!boton || !menu) return;

    const entrada = document.getElementById('selectorPozoTexto');
    const filas = Array.from(menu.querySelectorAll('li[data-texto]'));
    const vacio = document.getElementById('selectorPozoVacio');

    const abrir = () => {
      menu.hidden = false;
      boton.setAttribute('aria-expanded', 'true');
      entrada.value = '';
      filtrar();
      entrada.focus();
    };
    const cerrar = () => {
      menu.hidden = true;
      boton.setAttribute('aria-expanded', 'false');
    };
    const filtrar = () => {
      const texto = entrada.value.trim().toLowerCase();
      let visibles = 0;
      filas.forEach((fila) => {
        fila.hidden = !fila.dataset.texto.includes(texto);
        if (!fila.hidden) visibles += 1;
      });
      vacio.hidden = visibles > 0;
    };

    boton.addEventListener('click', () => (menu.hidden ? abrir() : cerrar()));
    entrada.addEventListener('input', filtrar);
    entrada.addEventListener('keydown', (evento) => {
      const primero = menu.querySelector('li[data-texto]:not([hidden]) a');
      if (evento.key === 'Enter' && primero) {
        evento.preventDefault();
        primero.click();
      } else if (evento.key === 'ArrowDown' && primero) {
        evento.preventDefault();
        primero.focus();
      }
    });
    menu.addEventListener('keydown', (evento) => {
      if (evento.key !== 'Escape') return;
      cerrar();
      boton.focus();
    });
    document.addEventListener('click', (evento) => {
      if (!menu.hidden && !menu.contains(evento.target) && !boton.contains(evento.target)) cerrar();
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
