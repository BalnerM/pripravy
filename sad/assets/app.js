/* VMM – skripta: navigace, téma, vzorce a interaktivní ukázky (bez knihoven). */
(function () {
  "use strict";

  // ---------- téma ----------
  const root = document.documentElement;
  function getStored() { try { return localStorage.getItem("vmm-theme"); } catch (e) { return null; } }
  function setStored(v) { try { localStorage.setItem("vmm-theme", v); } catch (e) { /* bez úložiště */ } }
  const stored = getStored();
  if (stored === "light" || stored === "dark") root.setAttribute("data-theme", stored);

  // ---------- velikost písma a postranní panel (klíče sdílené mezi předměty; základ nastavuje skript v <head>) ----------
  const FS_STEPS = [0.85, 1, 1.15, 1.3, 1.5];
  function setKey(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* bez úložiště */ } }
  function fsIndex() {
    const f = parseFloat(root.style.getPropertyValue("--fs")) || 1;
    let best = 1;
    FS_STEPS.forEach((s, i) => { if (Math.abs(s - f) < Math.abs(FS_STEPS[best] - f)) best = i; });
    return best;
  }

  // ---------- tisk / PDF ----------
  // ?pdf (generování PDF skriptem make_pdf.py) i ruční tisk: světlý režim, rozbalené odpovědi, načtené obrázky
  let themeBeforePrint = null;
  function preparePrint() {
    themeBeforePrint = root.getAttribute("data-theme");
    root.setAttribute("data-theme", "light");
    document.querySelectorAll("details.q").forEach(d => { d.open = true; });
    document.querySelectorAll('img[loading="lazy"]').forEach(img => { img.loading = "eager"; });
  }
  window.addEventListener("beforeprint", preparePrint);
  window.addEventListener("afterprint", () => {
    if (themeBeforePrint) root.setAttribute("data-theme", themeBeforePrint);
    else root.removeAttribute("data-theme");
  });
  if (/[?&]pdf\b/.test(location.search)) {
    root.setAttribute("data-theme", "light");
    root.style.setProperty("--fs", "1");   // PDF z Actions má vždy výchozí velikost
    document.addEventListener("DOMContentLoaded", preparePrint);
  }

  document.addEventListener("DOMContentLoaded", function () {
    const tb = document.getElementById("themeBtn");
    if (tb) {
      const label = () => {
        const dark = root.getAttribute("data-theme") === "dark" ||
          (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
        const en = root.lang === "en";
        tb.textContent = dark ? (en ? "Light mode" : "Světlý režim") : (en ? "Dark mode" : "Tmavý režim");
        return dark;
      };
      label();
      tb.addEventListener("click", function () {
        const dark = label();
        const next = dark ? "light" : "dark";
        root.setAttribute("data-theme", next);
        setStored(next);
        label();
      });
    }
    const fsDown = document.getElementById("fsDown"), fsUp = document.getElementById("fsUp"),
          fsVal = document.getElementById("fsVal"), pdfBtn = document.getElementById("pdfBtn");
    function applyFs(i) {
      i = Math.max(0, Math.min(FS_STEPS.length - 1, i));
      const v = FS_STEPS[i];
      root.style.setProperty("--fs", v);
      setKey("vmm-fs", v);
      if (fsVal) fsVal.textContent = Math.round(v * 100) + " %";
      if (fsDown) fsDown.disabled = i === 0;
      if (fsUp) fsUp.disabled = i === FS_STEPS.length - 1;
      if (pdfBtn) pdfBtn.title = v === 1 ? pdfBtn.dataset.dl : pdfBtn.dataset.print;
    }
    if (fsDown) {
      applyFs(fsIndex());
      fsDown.addEventListener("click", () => applyFs(fsIndex() - 1));
      fsUp.addEventListener("click", () => applyFs(fsIndex() + 1));
      fsVal.addEventListener("click", () => applyFs(1));
    }
    // jiná než výchozí velikost: tlačítko PDF otevře tisk stránky (hotová PDF mají jen výchozí velikost)
    if (pdfBtn) pdfBtn.addEventListener("click", e => {
      if (FS_STEPS[fsIndex()] !== 1) { e.preventDefault(); window.print(); }
    });
    const sb = document.getElementById("sideBtn");
    if (sb) {
      const syncSide = () => {
        const hidden = root.classList.contains("side-hidden");
        sb.setAttribute("aria-pressed", hidden ? "true" : "false");
        sb.title = hidden ? sb.dataset.show : sb.dataset.hide;
      };
      syncSide();
      sb.addEventListener("click", () => {
        root.classList.toggle("side-hidden");
        setKey("vmm-side", root.classList.contains("side-hidden") ? "0" : "1");
        syncSide();
      });
    }
    const mb = document.getElementById("menuBtn");
    if (mb) mb.addEventListener("click", () => document.body.classList.toggle("menu-open"));
    document.querySelectorAll(".sidebar a").forEach(a =>
      a.addEventListener("click", () => document.body.classList.remove("menu-open")));

    // zvýraznění aktuální sekce v obsahu
    const tocLinks = Array.from(document.querySelectorAll(".toc a"));
    if (tocLinks.length && "IntersectionObserver" in window) {
      const map = new Map(tocLinks.map(a => [a.getAttribute("href").slice(1), a]));
      const obs = new IntersectionObserver(entries => {
        entries.forEach(e => {
          if (e.isIntersecting) {
            tocLinks.forEach(a => a.classList.remove("here"));
            const a = map.get(e.target.id);
            if (a) a.classList.add("here");
          }
        });
      }, { rootMargin: "-20% 0px -70% 0px" });
      document.querySelectorAll("main h2[id]").forEach(h => obs.observe(h));
    }

    // rozbalit / sbalit všechny odpovědi
    document.querySelectorAll("[data-qall]").forEach(btn => {
      btn.addEventListener("click", () => {
        const open = btn.getAttribute("data-qall") === "open";
        document.querySelectorAll("details.q").forEach(d => { d.open = open; });
      });
    });

    // vzorce (KaTeX z CDN; bez internetu zůstane čitelný TeX)
    if (window.renderMathInElement) {
      renderMathInElement(document.body, {
        delimiters: [{ left: "\\[", right: "\\]", display: true }, { left: "\\(", right: "\\)", display: false }],
        throwOnError: false
      });
    }

    document.querySelectorAll("[data-demo]").forEach(el => {
      const f = DEMOS[el.getAttribute("data-demo")];
      if (f) f(el);
    });
  });

  // ---------- pomocné funkce ----------
  const NS = "http://www.w3.org/2000/svg";
  function S(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function H(html) { const d = document.createElement("div"); d.innerHTML = html.trim(); return d.firstChild; }
  function rng(seed) { // mulberry32
    let a = seed >>> 0;
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function gauss(r) { let u = 0, v = 0; while (u === 0) u = r(); v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  const COL = ["var(--c1)", "var(--c2)", "var(--c3)", "var(--c4)"];
  function marker(g, shape, x, y, size, color) {
    const st = `fill:${color};stroke:var(--surface);stroke-width:1`;
    if (shape === 0) return S("circle", { cx: x, cy: y, r: size, style: st }, g);
    if (shape === 1) return S("rect", { x: x - size, y: y - size, width: 2 * size, height: 2 * size, style: st }, g);
    if (shape === 2) return S("path", { d: `M${x},${y - size * 1.25}L${x + size * 1.15},${y + size * .8}L${x - size * 1.15},${y + size * .8}Z`, style: st }, g);
    return S("path", { d: `M${x},${y - size * 1.3}L${x + size * 1.1},${y}L${x},${y + size * 1.3}L${x - size * 1.1},${y}Z`, style: st }, g);
  }
  function fmt(x, d) { return x.toFixed(d === undefined ? 2 : d).replace(".", ","); }
  function frame(el, title, desc) {
    el.classList.add("demo");
    el.innerHTML = `<div class="demo-t">${title}</div><div class="demo-d">${desc}</div>`;
  }
  function axes(svg, W, Hh, pad) {
    S("line", { x1: pad, y1: Hh / 2, x2: W - pad, y2: Hh / 2, class: "ax" }, svg);
    S("line", { x1: W / 2, y1: pad, x2: W / 2, y2: Hh - pad, class: "ax" }, svg);
  }

  const DEMOS = {};
  // Interaktivní ukázky: DEMOS.nazev = function (el) {...}, v obsahu <div data-demo="nazev"></div> (vzor: vmm/assets/app.js)
})();
