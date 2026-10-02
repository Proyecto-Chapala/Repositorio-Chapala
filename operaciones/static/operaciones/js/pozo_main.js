/* ============================================================
   pozo_main.js — Pantalla principal del pozo (eliminar pozo)
   ============================================================ */

(function () {
  'use strict';

  function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
  }

  function abrirModal() {
    document.getElementById('inputConfirmarPozo').value = '';
    document.getElementById('errorEliminarPozo').textContent = '';
    document.getElementById('btnConfirmarEliminarPozo').disabled = true;
    document.getElementById('modalEliminarPozo').hidden = false;
    document.getElementById('inputConfirmarPozo').focus();
  }

  function cerrarModal() {
    document.getElementById('modalEliminarPozo').hidden = true;
  }

  async function eliminarPozo() {
    const boton = document.getElementById('btnConfirmarEliminarPozo');
    const error = document.getElementById('errorEliminarPozo');
    boton.disabled = true;
    error.textContent = '';
    try {
      const res = await fetch(`/api/pozos/${window.POZO_ID}/eliminar/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ confirmar: document.getElementById('inputConfirmarPozo').value.trim() }),
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        error.textContent = data.error || 'No se pudo eliminar el pozo.';
        boton.disabled = false;
        return;
      }
      window.location.href = window.URL_POZOS;
    } catch (e) {
      error.textContent = 'Error de conexión al eliminar el pozo.';
      boton.disabled = false;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('btnEliminarPozo');
    if (!btn) return;
    btn.addEventListener('click', abrirModal);
    document.getElementById('btnCerrarEliminarPozo').addEventListener('click', cerrarModal);
    document.getElementById('modalEliminarPozo').addEventListener('click', (ev) => {
      if (ev.target.id === 'modalEliminarPozo') cerrarModal();
    });
    document.getElementById('inputConfirmarPozo').addEventListener('input', (ev) => {
      document.getElementById('btnConfirmarEliminarPozo').disabled = ev.target.value.trim() !== window.POZO_NOMBRE;
    });
    document.getElementById('btnConfirmarEliminarPozo').addEventListener('click', eliminarPozo);
  });
})();
