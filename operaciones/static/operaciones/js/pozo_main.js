/* ============================================================
   pozo_main.js — Pantalla principal del pozo (eliminar, cerrar y reabrir)
   ============================================================ */

(function () {
  'use strict';

  function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
  }

  // --- Eliminar pozo ---
  function abrirModalEliminar() {
    document.getElementById('inputConfirmarPozo').value = '';
    document.getElementById('errorEliminarPozo').textContent = '';
    document.getElementById('btnConfirmarEliminarPozo').disabled = true;
    document.getElementById('modalEliminarPozo').hidden = false;
    document.getElementById('inputConfirmarPozo').focus();
  }

  function cerrarModalEliminar() {
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

  // --- Cerrar pozo ---
  function abrirModalCerrar() {
    const m = document.getElementById('modalCerrarPozoMain');
    if (m) m.hidden = false;
  }

  function cerrarModalCerrar() {
    const m = document.getElementById('modalCerrarPozoMain');
    if (m) m.hidden = true;
  }

  async function confirmarCerrarPozo() {
    const btn = document.getElementById('btnConfirmarCerrarMain');
    if (btn) btn.disabled = true;
    try {
      const res = await fetch(`/api/pozos/${window.POZO_ID}/cerrar/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      });
      const data = await res.json();
      if (res.ok && data.success) {
        window.location.reload();
      } else {
        alert(data.error || 'No se pudo cerrar el pozo.');
        if (btn) btn.disabled = false;
      }
    } catch (e) {
      alert('Error de conexión al cerrar el pozo.');
      if (btn) btn.disabled = false;
    }
  }

  // --- Reabrir pozo ---
  function abrirModalReabrir() {
    const m = document.getElementById('modalReabrirPozoMain');
    if (m) m.hidden = false;
  }

  function cerrarModalReabrir() {
    const m = document.getElementById('modalReabrirPozoMain');
    if (m) m.hidden = true;
  }

  async function confirmarReabrirPozo() {
    const btn = document.getElementById('btnConfirmarReabrirMain');
    if (btn) btn.disabled = true;
    try {
      const res = await fetch(`/api/pozos/${window.POZO_ID}/reabrir/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      });
      const data = await res.json();
      if (res.ok && data.success) {
        window.location.reload();
      } else {
        alert(data.error || 'No se pudo reabrir el pozo.');
        if (btn) btn.disabled = false;
      }
    } catch (e) {
      alert('Error de conexión al reabrir el pozo.');
      if (btn) btn.disabled = false;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    // Eliminar
    const btnEliminar = document.getElementById('btnEliminarPozo');
    if (btnEliminar) {
      btnEliminar.addEventListener('click', abrirModalEliminar);
      document.getElementById('btnCerrarEliminarPozo')?.addEventListener('click', cerrarModalEliminar);
      document.getElementById('modalEliminarPozo')?.addEventListener('click', (ev) => {
        if (ev.target.id === 'modalEliminarPozo') cerrarModalEliminar();
      });
      document.getElementById('inputConfirmarPozo')?.addEventListener('input', (ev) => {
        document.getElementById('btnConfirmarEliminarPozo').disabled = ev.target.value.trim() !== window.POZO_NOMBRE;
      });
      document.getElementById('btnConfirmarEliminarPozo')?.addEventListener('click', eliminarPozo);
    }

    // Cerrar
    const btnCerrar = document.getElementById('btnCerrarPozoMain');
    if (btnCerrar) {
      btnCerrar.addEventListener('click', abrirModalCerrar);
      document.getElementById('btnCerrarModalCerrarMain')?.addEventListener('click', cerrarModalCerrar);
      document.getElementById('btnCancelarCerrarMain')?.addEventListener('click', cerrarModalCerrar);
      document.getElementById('modalCerrarPozoMain')?.addEventListener('click', (ev) => {
        if (ev.target.id === 'modalCerrarPozoMain') cerrarModalCerrar();
      });
      document.getElementById('btnConfirmarCerrarMain')?.addEventListener('click', confirmarCerrarPozo);
    }

    // Reabrir
    const btnReabrir = document.getElementById('btnReabrirPozoMain');
    if (btnReabrir) {
      btnReabrir.addEventListener('click', abrirModalReabrir);
      document.getElementById('btnCerrarModalReabrirMain')?.addEventListener('click', cerrarModalReabrir);
      document.getElementById('btnCancelarReabrirMain')?.addEventListener('click', cerrarModalReabrir);
      document.getElementById('modalReabrirPozoMain')?.addEventListener('click', (ev) => {
        if (ev.target.id === 'modalReabrirPozoMain') cerrarModalReabrir();
      });
      document.getElementById('btnConfirmarReabrirMain')?.addEventListener('click', confirmarReabrirPozo);
    }
  });
})();
