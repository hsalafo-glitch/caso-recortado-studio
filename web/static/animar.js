// Aparición suave de las secciones al bajar por la página. Sin esto (o con «reducir movimiento») todo se ve igual, sin animar.
(function () {
  if (!("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  document.documentElement.classList.add("js");
  var sel = ".titulo-sec,.creador,.galeria figure,.tarjeta,.incluye div,.plan,.faq details,.cierre,.lista-wrap > *";
  var els = document.querySelectorAll(sel);
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("visto"); io.unobserve(e.target); } });
  }, { rootMargin: "0px 0px -8% 0px" });
  els.forEach(function (el) {
    var hermanos = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
    el.style.setProperty("--d", Math.min(hermanos, 6) * 0.06 + "s");   // en cascada dentro de cada fila
    el.classList.add("revelar");
    io.observe(el);
  });
})();
