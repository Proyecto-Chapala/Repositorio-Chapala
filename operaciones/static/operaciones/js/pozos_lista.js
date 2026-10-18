// Lista de pozos: filtro por texto y por estado, y fila completa como enlace.
document.addEventListener('DOMContentLoaded', () => {
  const filtroTexto = document.getElementById('filtroPozos');
  if (!filtroTexto) return;

  const filas = Array.from(document.querySelectorAll('#tablaPozos tr'));
  const botonesEstado = document.querySelectorAll('[data-estado]:not(tr)');
  const sinResultados = document.getElementById('pozosSinResultados');
  const contador = document.getElementById('pozosContador');
  let estadoElegido = '';

  const filtrar = () => {
    const palabras = filtroTexto.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let visibles = 0;
    filas.forEach((fila) => {
      const coincide = (!estadoElegido || fila.dataset.estado === estadoElegido)
        && palabras.every((palabra) => fila.dataset.texto.includes(palabra));
      fila.hidden = !coincide;
      if (coincide) visibles += 1;
    });
    sinResultados.hidden = visibles > 0;
    contador.textContent = `${visibles} de ${filas.length} pozos`;
  };

  filtroTexto.addEventListener('input', filtrar);
  botonesEstado.forEach((boton) => {
    boton.addEventListener('click', () => {
      estadoElegido = boton.dataset.estado;
      botonesEstado.forEach((otro) => otro.classList.toggle('is-active', otro === boton));
      filtrar();
    });
  });

  // Toda la fila abre el pozo (el enlace del nombre sigue sirviendo con teclado)
  filas.forEach((fila) => {
    fila.addEventListener('click', (evento) => {
      if (evento.target.closest('a')) return;
      fila.querySelector('a.enlace-fila').click();
    });
  });
});
