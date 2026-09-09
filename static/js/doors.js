// Transición "puertas de tren", compartida entre el login y las páginas
// internas. Dura 5 segundos en total: 2.5s cerrando (en el login, al
// enviar el formulario) + 2.5s abriendo (en la página de llegada, sea el
// dashboard si el login fue válido o el propio login de nuevo si hubo
// error). Como son dos cargas de página reales separadas por un POST al
// servidor, se usa sessionStorage para "avisarle" a la página siguiente
// que debe empezar con las puertas cerradas y abrirlas.
(function () {
  var FASE_MS = 2500; // 2.5s cerrar + 2.5s abrir = 5s
  var FLAG = 'wms_doors_transition';

  document.addEventListener('DOMContentLoaded', function () {
    var doorLeft = document.getElementById('doorLeft');
    var doorRight = document.getElementById('doorRight');
    var doorLabel = document.getElementById('doorLabel');
    if (!doorLeft || !doorRight) return;

    // Si venimos de un submit de login, esta pagina arranca "detras
    // de puertas cerradas" y las abre apenas carga.
    if (sessionStorage.getItem(FLAG)) {
      sessionStorage.removeItem(FLAG);
      doorLeft.classList.add('shut');
      doorRight.classList.add('shut');
      requestAnimationFrame(function () {
        doorLeft.classList.add('animate');
        doorRight.classList.add('animate');
        requestAnimationFrame(function () {
          doorLeft.classList.remove('shut');
          doorRight.classList.remove('shut');
        });
      });
      setTimeout(function () {
        doorLeft.classList.remove('animate');
        doorRight.classList.remove('animate');
      }, FASE_MS + 100);
    }

    var form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      doorLeft.classList.add('animate');
      doorRight.classList.add('animate');
      requestAnimationFrame(function () {
        doorLeft.classList.add('shut');
        doorRight.classList.add('shut');
      });
      if (doorLabel) {
        setTimeout(function () { doorLabel.classList.add('show'); }, 300);
      }
      sessionStorage.setItem(FLAG, '1');
      // Se espera a que la puerta termine de cerrar para recien enviar
      // el formulario de verdad hacia Django.
      setTimeout(function () {
        HTMLFormElement.prototype.submit.call(form);
      }, FASE_MS);
    });
  });
})();
