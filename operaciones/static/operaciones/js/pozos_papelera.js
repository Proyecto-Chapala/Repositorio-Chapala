/* ============================================================
   pozos_papelera.js — Papelera de pozos (restaurar)
   ============================================================ */

(function () {
  'use strict';

  function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
  }

  async function restaurarPozo(boton) {
    const error = document.getElementById('errorPapelera');
    boton.disabled = true;
    error.textContent = '';
    try {
      const res = await fetch(`/api/pozos/${boton.dataset.pozoId}/restaurar/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        error.textContent = data.error || 'No se pudo restaurar el pozo.';
        boton.disabled = false;
        return;
      }
      window.location.reload();
    } catch (e) {
      error.textContent = 'Error de conexión al restaurar el pozo.';
      boton.disabled = false;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.btn-restaurar-pozo').forEach((boton) => {
      boton.addEventListener('click', () => restaurarPozo(boton));
    });
  });
})();
