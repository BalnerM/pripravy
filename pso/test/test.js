// Společný skript stránek přípravy na test PSO: vykreslení vzorců, rozbalení řešení, tisk.
(function () {
  function math() {
    if (window.renderMathInElement) {
      renderMathInElement(document.body, {
        delimiters: [{ left: "\\[", right: "\\]", display: true }, { left: "\\(", right: "\\)", display: false }],
        throwOnError: false
      });
    }
  }
  function setAll(open) {
    document.querySelectorAll("details.res").forEach(function (d) { d.open = open; });
  }
  window.addEventListener("DOMContentLoaded", function () {
    math();
    document.querySelectorAll("[data-open]").forEach(function (b) {
      b.addEventListener("click", function () { setAll(b.getAttribute("data-open") === "1"); });
    });
    document.querySelectorAll("[data-print]").forEach(function (b) {
      b.addEventListener("click", function () { setAll(true); window.print(); });
    });
  });
  window.addEventListener("beforeprint", function () { setAll(true); });
})();
