/* ============================================================
   spud_date.js — Confirmación de la pantalla única Spud Date
   ============================================================ */

(function () {
  'use strict';

  function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
  }

  function showToast(mensaje, tipo) {
    const container = document.getElementById('toastContainer');
    if (!container) { window.alert(mensaje); return; }
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + (tipo || 'info');
    toast.textContent = mensaje;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  }

  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('btnConfirmarSpudDate');
    if (!btn) return; // Ya estaba completada (vista de solo lectura)

    btn.addEventListener('click', async () => {
      document.getElementById('errorFecha').textContent = '';
      document.getElementById('errorFluido').textContent = '';

      const fecha = document.getElementById('inputFechaPrimeraCaptura').value;
      const fluidoEl = document.querySelector('input[name="tipoFluido"]:checked');
      const conTratamiento = document.getElementById('inputConTratamiento').checked;
      const numeroLogit = document.getElementById('inputNumeroLogit').value.trim();

      if (!fecha) {
        document.getElementById('errorFecha').textContent = 'La fecha es obligatoria.';
        return;
      }
      if (!fluidoEl) {
        document.getElementById('errorFluido').textContent = 'Selecciona el tipo de fluido.';
        return;
      }

      try {
        const res = await fetch(`/operaciones/api/pozos/${window.POZO_ID}/spud-date/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({
            fecha_primera_captura: fecha,
            tipo_fluido_inicial: fluidoEl.value,
            con_tratamiento_disposicion: conTratamiento,
            numero_control_logit: numeroLogit,
          }),
        });
        const data = await res.json();
        if (!res.ok || !data.success) {
          showToast(data.error || 'No se pudo confirmar la fecha de inicio.', 'error');
          return;
        }
        showToast(data.mensaje, 'success');
        window.location.href = '/operaciones/';
      } catch (err) {
        showToast('Error de conexión al confirmar.', 'error');
      }
    });
  });
})();
