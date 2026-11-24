/* ============================================================
   recap.js — Control de modales para Cerrar y Reabrir pozo
   ============================================================ */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    // Modal Cerrar
    const modalCerrar = document.getElementById('modalCerrarPozo');
    const btnAbrirCerrar = document.getElementById('btnAbrirModalCerrar');
    const btnCerrarModalCerrar = document.getElementById('btnCerrarModalCerrar');
    const btnCancelarCerrar = document.getElementById('btnCancelarCerrar');

    if (btnAbrirCerrar && modalCerrar) {
      btnAbrirCerrar.addEventListener('click', () => {
        modalCerrar.hidden = false;
      });
    }

    const cerrarModalCerrar = () => {
      if (modalCerrar) modalCerrar.hidden = true;
    };

    if (btnCerrarModalCerrar) btnCerrarModalCerrar.addEventListener('click', cerrarModalCerrar);
    if (btnCancelarCerrar) btnCancelarCerrar.addEventListener('click', cerrarModalCerrar);
    if (modalCerrar) {
      modalCerrar.addEventListener('click', (ev) => {
        if (ev.target === modalCerrar) cerrarModalCerrar();
      });
    }

    // Modal Reabrir
    const modalReabrir = document.getElementById('modalReabrirPozo');
    const btnAbrirReabrir = document.getElementById('btnAbrirModalReabrir');
    const btnCerrarModalReabrir = document.getElementById('btnCerrarModalReabrir');
    const btnCancelarReabrir = document.getElementById('btnCancelarReabrir');

    if (btnAbrirReabrir && modalReabrir) {
      btnAbrirReabrir.addEventListener('click', () => {
        modalReabrir.hidden = false;
      });
    }

    const cerrarModalReabrir = () => {
      if (modalReabrir) modalReabrir.hidden = true;
    };

    if (btnCerrarModalReabrir) btnCerrarModalReabrir.addEventListener('click', cerrarModalReabrir);
    if (btnCancelarReabrir) btnCancelarReabrir.addEventListener('click', cerrarModalReabrir);
    if (modalReabrir) {
      modalReabrir.addEventListener('click', (ev) => {
        if (ev.target === modalReabrir) cerrarModalReabrir();
      });
    }
  });
})();

