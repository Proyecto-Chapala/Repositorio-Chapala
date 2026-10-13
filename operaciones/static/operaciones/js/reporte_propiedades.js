/* ============================================================
   reporte_propiedades.js — Reporte de propiedades (reportito)
   Guarda el comentario y descarga el Excel (guardando antes el comentario).
   ============================================================ */

(function () {
  'use strict';

  const urls = document.body.dataset;
  const comentario = document.getElementById('rpComentario');
  const estado = document.getElementById('rpEstado');

  function getCookie(nombre) {
    const m = document.cookie.match('(^|;)\\s*' + nombre + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
  }

  function ajustarAltura() {
    comentario.style.height = 'auto';
    comentario.style.height = comentario.scrollHeight + 'px';
  }

  async function guardarComentario() {
    try {
      const res = await fetch(urls.urlComentario, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ comentario: comentario.value }),
      });
      const data = await res.json();
      estado.textContent = data.ok ? 'Comentario guardado.' : (data.error || 'No se pudo guardar el comentario.');
      return data.ok;
    } catch (e) {
      estado.textContent = 'Error de conexión: el comentario no se guardó.';
      return false;
    }
  }

  comentario.addEventListener('input', () => {
    ajustarAltura();
    estado.textContent = 'Comentario sin guardar.';
  });
  document.getElementById('rpGuardar').addEventListener('click', guardarComentario);
  document.getElementById('rpExcel').addEventListener('click', async () => {
    if (await guardarComentario()) window.location.href = urls.urlExcel;
  });
  ajustarAltura();
})();
