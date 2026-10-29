/* MLR – skripta: navigace, téma, vzorce a interaktivní ukázky (bez knihoven). */
(function () {
  "use strict";

  // ---------- téma ----------
  const root = document.documentElement;
  const EN = root.lang === "en";
  const i18n = (cs, en) => EN ? en : cs; // text ukázek podle jazyka stránky
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
        tb.textContent = dark ? i18n("Světlý režim", "Light mode") : i18n("Tmavý režim", "Dark mode");
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
    // přepínač jazyka: obě verze mají stejná id, takže se zachová místo na stránce
    document.querySelectorAll("a.langbtn").forEach(a =>
      a.addEventListener("click", () => { a.href = a.href.split("#")[0] + location.hash; }));
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
  function dec(s) { return EN ? s : s.replace(".", ","); } // desetinná čárka jen v češtině
  function fmt(x, d) { return dec(x.toFixed(d === undefined ? 2 : d)); }
  function frame(el, title, desc) {
    el.classList.add("demo");
    el.innerHTML = `<div class="demo-t">${title}</div><div class="demo-d">${desc}</div>`;
  }
  function axes(svg, W, Hh, pad) {
    S("line", { x1: pad, y1: Hh / 2, x2: W - pad, y2: Hh / 2, class: "ax" }, svg);
    S("line", { x1: W / 2, y1: pad, x2: W / 2, y2: Hh - pad, class: "ax" }, svg);
  }

  const DEMOS = {};

  // ===== 2) PCA: otáčení osy =====
  DEMOS["pca-rotace"] = function (el) {
    frame(el, i18n("PCA jako hledání nejlepšího směru", "PCA as a search for the best direction"),
      i18n("Otáčej osou a sleduj, kolik rozptylu se na ni „promítne“. PCA dělá přesně tohle – hledá směr s největším rozptylem projekcí (to je PC1). Všimni si, že součet rozptylu podél osy a kolmo na ni je pořád stejný.",
        "Rotate the axis and watch how much variance is “projected” onto it. This is exactly what PCA does – it looks for the direction with the largest variance of the projections (that is PC1). Notice that the variance along the axis plus the variance perpendicular to it is always the same."));
    const W = 440, Hh = 400, sc = 60, cx = W / 2, cy = Hh / 2;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, class: "sq", role: "img", "aria-label": i18n("projekce bodů na otáčenou osu", "projection of points onto a rotating axis") }, el);
    const r = rng(5), N = 120, P = [];
    for (let i = 0; i < N; i++) { const z1 = gauss(r), z2 = gauss(r); P.push([1.5 * z1, 0.85 * (0.75 * z1 + 0.66 * z2)]); }
    const mx = P.reduce((s, p) => s + p[0], 0) / N, my = P.reduce((s, p) => s + p[1], 0) / N;
    P.forEach(p => { p[0] -= mx; p[1] -= my; });
    let a = 0, b = 0, c = 0;
    P.forEach(p => { a += p[0] * p[0]; b += p[0] * p[1]; c += p[1] * p[1]; });
    a /= N - 1; b /= N - 1; c /= N - 1;
    const total = a + c;
    const best = (0.5 * Math.atan2(2 * b, a - c) * 180 / Math.PI + 180) % 180;
    const ctr = H(`<div class="controls"><label>${i18n("úhel osy", "axis angle")}: <b class="av">0°</b><input type="range" min="0" max="179" step="1" value="0"></label><button class="primary">${i18n("Najdi PC1", "Find PC1")}</button><button class="perp">${i18n("Kolmý směr (PC2)", "Perpendicular direction (PC2)")}</button></div>`);
    el.appendChild(ctr);
    const out = H(`<div class="readout"></div>`); el.appendChild(out);
    const bar = H(`<svg viewBox="0 0 440 34" aria-hidden="true"></svg>`); el.appendChild(bar);
    const inp = ctr.querySelector("input"), av = ctr.querySelector(".av");
    function draw() {
      const th = +inp.value * Math.PI / 180, u = [Math.cos(th), Math.sin(th)];
      av.textContent = inp.value + "°";
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      axes(svg, W, Hh, 10);
      S("line", { x1: cx - u[0] * 400, y1: cy + u[1] * 400, x2: cx + u[0] * 400, y2: cy - u[1] * 400, style: "stroke:var(--c2);stroke-width:2" }, svg);
      let v = 0;
      P.forEach(p => {
        const t = p[0] * u[0] + p[1] * u[1]; v += t * t;
        S("line", { x1: cx + p[0] * sc, y1: cy - p[1] * sc, x2: cx + t * u[0] * sc, y2: cy - t * u[1] * sc, style: "stroke:var(--line-strong);stroke-width:.8" }, svg);
      });
      P.forEach(p => S("circle", { cx: cx + p[0] * sc, cy: cy - p[1] * sc, r: 3, style: "fill:var(--c1);opacity:.75" }, svg));
      P.forEach(p => {
        const t = p[0] * u[0] + p[1] * u[1];
        S("circle", { cx: cx + t * u[0] * sc, cy: cy - t * u[1] * sc, r: 2.2, style: "fill:var(--c2)" }, svg);
      });
      v /= N - 1;
      const pct = v / total * 100;
      out.innerHTML = i18n(`rozptyl projekcí na osu: <b>${fmt(v)}</b> (${fmt(pct, 0)} % celku) · kolmo na osu: <b>${fmt(total - v)}</b> · celkem vždy <b>${fmt(total)}</b>`,
        `variance of projections onto the axis: <b>${fmt(v)}</b> (${fmt(pct, 0)} % of total) · perpendicular to the axis: <b>${fmt(total - v)}</b> · total always <b>${fmt(total)}</b>`) +
        (Math.abs(((+inp.value - best + 270) % 180) - 90) < 1.5 ? i18n(" · <b>to je PC1!</b>", " · <b>this is PC1!</b>") : "");
      while (bar.firstChild) bar.removeChild(bar.firstChild);
      S("rect", { x: 0, y: 6, width: 440, height: 22, rx: 4, style: "fill:var(--surface-2)" }, bar);
      S("rect", { x: 0, y: 6, width: 440 * pct / 100, height: 22, rx: 4, style: "fill:var(--c2)" }, bar);
    }
    inp.addEventListener("input", draw);
    ctr.querySelector(".primary").addEventListener("click", () => { inp.value = Math.round(best); draw(); });
    ctr.querySelector(".perp").addEventListener("click", () => { inp.value = Math.round((best + 90) % 180); draw(); });
    draw();
  };

  // ===== 3) k-means krok za krokem =====
  DEMOS.kmeans = function (el) {
    frame(el, i18n("k-means krok za krokem", "k-means step by step"),
      i18n("Střídej kroky <b>1) přiřaď</b> a <b>2) přepočítej těžiště</b>. Zkus zvolit „špatné“ K nebo nová náhodná těžiště a sleduj, že výsledek závisí na startu a že WSS při každém kroku klesá.",
        "Alternate the steps <b>1) assign</b> and <b>2) recompute centroids</b>. Try a “wrong” K or new random centroids and see that the result depends on the start and that WSS goes down with every step."));
    const W = 440, Hh = 340, sc = 40, cx = W / 2, cy = Hh / 2;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": i18n("shlukování k-means", "k-means clustering") }, el);
    const ctr = H(`<div class="controls">
      <label>K <select class="k"><option>2</option><option selected>3</option><option>4</option></select></label>
      <button class="nd">${i18n("Nová data", "New data")}</button><button class="init">${i18n("Náhodná těžiště", "Random centroids")}</button>
      <button class="primary as">${i18n("1) Přiřaď body", "1) Assign points")}</button><button class="primary up">${i18n("2) Přepočítej těžiště", "2) Recompute centroids")}</button><button class="run">${i18n("Dokonči", "Finish")}</button></div>`);
    el.appendChild(ctr);
    const out = H(`<div class="readout"></div>`); el.appendChild(out);
    let seed = 3, X = [], C = [], lab = null, it = 0, phase = "init";
    function data() {
      const r = rng(seed++); X = [];
      const cs = [[-2.5 + r(), -1 + r()], [2 + r(), -1.5 + r()], [0 + r(), 2 + r()]];
      cs.forEach(c => { for (let i = 0; i < 35; i++) X.push([c[0] + 0.8 * gauss(r), c[1] + 0.8 * gauss(r)]); });
      init();
    }
    function init() {
      const K = +ctr.querySelector(".k").value, r = rng(seed * 97 + K);
      C = []; const used = new Set();
      while (C.length < K) { const i = Math.floor(r() * X.length); if (!used.has(i)) { used.add(i); C.push(X[i].slice()); } }
      lab = null; it = 0; phase = "assign"; draw(i18n("Těžiště umístěna náhodně do bodů. Teď krok 1.", "Centroids placed at random data points. Now step 1."));
    }
    function d2(p, q) { return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2; }
    function assign() {
      lab = X.map(p => { let b = 0; C.forEach((c, k) => { if (d2(p, c) < d2(p, C[b])) b = k; }); return b; });
      phase = "update"; draw(i18n("Každý bod přiřazen k nejbližšímu těžišti.", "Each point assigned to the nearest centroid."));
    }
    function update() {
      if (!lab) return assign();
      let moved = 0;
      C = C.map((c, k) => {
        const m = X.filter((p, i) => lab[i] === k);
        if (!m.length) return c;
        const n = [m.reduce((s, p) => s + p[0], 0) / m.length, m.reduce((s, p) => s + p[1], 0) / m.length];
        moved = Math.max(moved, Math.sqrt(d2(n, c))); return n;
      });
      it++; phase = "assign";
      draw(moved < 1e-6 ? i18n("Těžiště se už nepohnula → algoritmus zkonvergoval.", "The centroids did not move → the algorithm has converged.") :
        i18n(`Těžiště posunuta do průměru svých bodů (max. posun ${fmt(moved)}).`, `Centroids moved to the mean of their points (max. shift ${fmt(moved)}).`));
      return moved;
    }
    function run() { let g = 0; do { assign(); g++; } while (update() > 1e-6 && g < 50); }
    function wss() { return lab ? X.reduce((s, p, i) => s + d2(p, C[lab[i]]), 0) : NaN; }
    function draw(msg) {
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      axes(svg, W, Hh, 8);
      X.forEach((p, i) => {
        const x = cx + p[0] * sc, y = cy - p[1] * sc;
        if (lab) {
          S("line", { x1: x, y1: y, x2: cx + C[lab[i]][0] * sc, y2: cy - C[lab[i]][1] * sc, style: "stroke:var(--line);stroke-width:.8" }, svg);
        }
      });
      X.forEach((p, i) => {
        const x = cx + p[0] * sc, y = cy - p[1] * sc;
        if (lab) marker(svg, lab[i], x, y, 3.6, COL[lab[i]]);
        else S("circle", { cx: x, cy: y, r: 3.4, style: "fill:var(--muted);opacity:.7" }, svg);
      });
      C.forEach((c, k) => {
        const x = cx + c[0] * sc, y = cy - c[1] * sc;
        S("circle", { cx: x, cy: y, r: 10, style: `fill:var(--surface);stroke:${COL[k]};stroke-width:3` }, svg);
        S("path", { d: `M${x - 5},${y - 5}L${x + 5},${y + 5}M${x - 5},${y + 5}L${x + 5},${y - 5}`, style: "stroke:var(--ink);stroke-width:2" }, svg);
      });
      const w = wss();
      out.innerHTML = `${msg || ""}<br>${i18n("iterace", "iterations")}: <b>${it}</b> · ${i18n("WSS (součet čtverců vzdáleností k těžišti)", "WSS (sum of squared distances to the centroid)")}: <b>${isNaN(w) ? "–" : fmt(w, 1)}</b>`;
    }
    ctr.querySelector(".nd").onclick = data;
    ctr.querySelector(".init").onclick = init;
    ctr.querySelector(".k").onchange = init;
    ctr.querySelector(".as").onclick = assign;
    ctr.querySelector(".up").onclick = update;
    ctr.querySelector(".run").onclick = run;
    data();
  };

  // ===== 4) t-SNE: σ a perplexita =====
  DEMOS.perplexita = function (el) {
    frame(el, i18n("σ, podmíněné pravděpodobnosti a perplexita", "σ, conditional probabilities and perplexity"),
      i18n("Bod i je uprostřed. Gaussova křivka kolem něj určuje, s jakou pravděpodobností si i „vybere“ ostatní body za sousedy (sloupce). Šířku σ měň posuvníkem – perplexita ukazuje <b>efektivní počet sousedů</b>. t-SNE hledá σ pro každý bod zvlášť tak, aby perplexita byla rovna zadané hodnotě.",
        "Point i is in the middle. The Gaussian curve around it sets the probability with which i “picks” the other points as neighbours (bars). Change the width σ with the slider – perplexity shows the <b>effective number of neighbours</b>. t-SNE looks for σ separately for each point so that the perplexity equals the chosen value."));
    const W = 600, Hh = 230, x0 = 300, sc = 34, base = 180;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": i18n("podmíněné pravděpodobnosti sousedů", "conditional probabilities of neighbours") }, el);
    const pos = [-1.0, -0.6, -0.35, 0.3, 0.55, 0.9, 2.6, 3.4, 4.3, 5.6, 7.2, -3.0, -4.6, -6.5];
    const ctr = H(`<div class="controls"><label>σ = <b class="sv"></b><input type="range" min="-2.3" max="1.8" step="0.01" value="-0.3"></label>
      <label>${i18n("cílová perplexita", "target perplexity")} <select class="tp"><option>2</option><option selected>5</option><option>10</option></select></label><button class="primary">${i18n("Najdi σ (půlení intervalu)", "Find σ (bisection)")}</button></div>`);
    el.appendChild(ctr);
    const out = H(`<div class="readout"></div>`); el.appendChild(out);
    const inp = ctr.querySelector("input"), sv = ctr.querySelector(".sv");
    function probs(s) {
      const w = pos.map(d => Math.exp(-d * d / (2 * s * s))), z = w.reduce((a, b) => a + b, 0) || 1e-300;
      const p = w.map(x => x / z);
      const Hb = -p.reduce((a, q) => a + (q > 0 ? q * Math.log2(q) : 0), 0);
      return [p, Math.pow(2, Hb)];
    }
    function draw(extra) {
      const s = Math.exp(+inp.value); sv.textContent = fmt(s);
      const [p, perp] = probs(s);
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      S("line", { x1: 10, y1: base, x2: W - 10, y2: base, class: "ax" }, svg);
      let d = "";
      for (let x = -8.5; x <= 8.5; x += 0.05) {
        const y = base - 130 * Math.exp(-x * x / (2 * s * s));
        d += (d ? "L" : "M") + (x0 + x * sc).toFixed(1) + "," + y.toFixed(1);
      }
      S("path", { d: d, style: "fill:none;stroke:var(--c1);stroke-width:2;opacity:.6" }, svg);
      pos.forEach((x, j) => {
        const h = 140 * p[j];
        S("rect", { x: x0 + x * sc - 6, y: base - h, width: 12, height: h, rx: 2, style: "fill:var(--c2)" }, svg);
        S("circle", { cx: x0 + x * sc, cy: base + 12, r: 5, style: "fill:var(--c2)" }, svg);
      });
      S("circle", { cx: x0, cy: base + 12, r: 7, style: "fill:var(--ink)" }, svg);
      const t = S("text", { x: x0, y: base + 38, "text-anchor": "middle", style: "font-size:13px;fill:var(--ink)" }, svg); t.textContent = i18n("bod i", "point i");
      const t2 = S("text", { x: x0 - 1.5 * sc, y: 24, "text-anchor": "middle" }, svg); t2.textContent = i18n("hustá oblast", "dense region");
      const t3 = S("text", { x: x0 + 5 * sc, y: 24, "text-anchor": "middle" }, svg); t3.textContent = i18n("řídká oblast", "sparse region");
      out.innerHTML = i18n(`perplexita = 2<sup>H</sup> = <b>${fmt(perp, 1)}</b> (≈ počet „vlivných“ sousedů)`,
        `perplexity = 2<sup>H</sup> = <b>${fmt(perp, 1)}</b> (≈ number of “important” neighbours)`) + (extra ? " · " + extra : "");
    }
    ctr.querySelector(".primary").onclick = () => {
      const target = +ctr.querySelector(".tp").value;
      let lo = 0.01, hi = 50, s = 1, k = 0;
      for (; k < 60; k++) { s = (lo + hi) / 2; const pp = probs(s)[1]; if (Math.abs(pp - target) < 1e-3) break; if (pp > target) hi = s; else lo = s; }
      inp.value = Math.log(s); draw(i18n(`nalezeno za ${k + 1} kroků půlení intervalu`, `found in ${k + 1} bisection steps`));
    };
    inp.addEventListener("input", () => draw()); draw();
  };

  // ===== 5) UMAP: fuzzy graf sousedů =====
  DEMOS["umap-graf"] = function (el) {
    frame(el, i18n("UMAP – vážený graf k nejbližších sousedů", "UMAP – weighted graph of the k nearest neighbours"),
      i18n("Body leží na zašuměné křivce s různou hustotou. UMAP propojí každý bod s jeho k nejbližšími sousedy; síla (tloušťka) hrany klesá se vzdáleností, ale měřítko je <b>lokální</b> – v řídké oblasti se „natáhne“, takže graf zůstane spojený. Malé k → rozpadlý graf (jen detaily), velké k → hustý graf (globální tvar).",
        "The points lie on a noisy curve with changing density. UMAP connects each point with its k nearest neighbours; the strength (thickness) of an edge drops with distance, but the scale is <b>local</b> – in a sparse region it “stretches”, so the graph stays connected. Small k → broken graph (only details), large k → dense graph (global shape)."));
    const W = 600, Hh = 260;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": i18n("graf sousedů UMAP", "UMAP neighbour graph") }, el);
    const r = rng(8), P = [];
    for (let i = 0; i < 46; i++) {
      const u = r(); const x = 10 * (u < .55 ? 0.3 + 0.25 * r() : r());
      P.push([x, Math.sin(x * 0.9) + 0.18 * gauss(r)]);
    }
    const sx = x => 30 + x * 54, sy = y => 130 - y * 75;
    const ctr = H(`<div class="controls"><label>k = <b class="kv">5</b><input type="range" min="2" max="15" step="1" value="5"></label></div>`);
    el.appendChild(ctr);
    const out = H(`<div class="readout"></div>`); el.appendChild(out);
    const inp = ctr.querySelector("input"), kv = ctr.querySelector(".kv");
    const D = P.map(p => P.map(q => Math.hypot(p[0] - q[0], p[1] - q[1])));
    function draw() {
      const k = +inp.value; kv.textContent = k;
      const n = P.length, Wm = Array.from({ length: n }, () => new Float64Array(n));
      for (let i = 0; i < n; i++) {
        const nn = D[i].map((d, j) => [d, j]).filter(x => x[1] !== i).sort((a, b) => a[0] - b[0]).slice(0, k);
        const rho = nn[0][0], target = Math.log2(k);
        let lo = 1e-4, hi = 50, s = 1;
        for (let t = 0; t < 60; t++) {
          s = (lo + hi) / 2;
          const sum = nn.reduce((a, [d]) => a + Math.exp(-Math.max(0, d - rho) / s), 0);
          if (sum > target) hi = s; else lo = s;
        }
        nn.forEach(([d, j]) => { Wm[i][j] = Math.exp(-Math.max(0, d - rho) / s); });
      }
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      let edges = 0; const par = P.map((_, i) => i);
      const find = i => par[i] === i ? i : (par[i] = find(par[i]));
      for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
        const a = Wm[i][j], b = Wm[j][i], w = a + b - a * b;
        if (w > 0.001) {
          edges++; par[find(i)] = find(j);
          S("line", { x1: sx(P[i][0]), y1: sy(P[i][1]), x2: sx(P[j][0]), y2: sy(P[j][1]), style: `stroke:var(--c1);stroke-width:${0.6 + 3 * w};opacity:${0.15 + 0.75 * w}` }, svg);
        }
      }
      P.forEach(p => S("circle", { cx: sx(p[0]), cy: sy(p[1]), r: 4, style: "fill:var(--c2);stroke:var(--surface);stroke-width:1" }, svg));
      const comps = new Set(P.map((_, i) => find(i))).size;
      out.innerHTML = i18n(`hran v grafu: <b>${edges}</b> · počet oddělených částí grafu: <b>${comps}</b>`, `edges in the graph: <b>${edges}</b> · number of separate parts of the graph: <b>${comps}</b>`) +
        (comps > 1 ? i18n(" (graf je rozpadlý – v mapě vzniknou umělé „ostrůvky“)", " (the graph is broken – the map will show artificial “islands”)") : i18n(" (graf je souvislý)", " (the graph is connected)"));
    }
    inp.addEventListener("input", draw); draw();
  };

  // ===== 6) kernel: 1D → 2D =====
  DEMOS.kernel = function (el) {
    frame(el, i18n("jádrová transformace 1D → 2D", "kernel transformation 1D → 2D"),
      i18n("V 1D jsou modré body uprostřed a oranžové po stranách – žádný jediný práh je neoddělí. Po zobrazení x → (x, x²) „vyskočí“ oranžové body nahoru a stačí jediná přímka.",
        "In 1D the blue points are in the middle and the orange ones on the sides – no single threshold can separate them. After the mapping x → (x, x²) the orange points “jump” up and one straight line is enough."));
    const W = 520, Hh = 280, x0 = 260, sc = 70, base = 240;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": i18n("jádrová transformace", "kernel transformation") }, el);
    const r = rng(4), A = [], B = [];
    for (let i = 0; i < 10; i++) A.push(-1 + 2 * r());
    for (let i = 0; i < 6; i++) { B.push(-3.2 + 1.4 * r()); B.push(1.8 + 1.4 * r()); }
    const toTwo = i18n("Zobraz do 2D: x → (x, x²)", "Map to 2D: x → (x, x²)");
    const ctr = H(`<div class="controls"><button class="primary">${toTwo}</button></div>`);
    el.appendChild(ctr);
    let t = 0, target = 0, anim = null;
    function draw() {
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      S("line", { x1: 10, y1: base, x2: W - 10, y2: base, class: "ax" }, svg);
      const yk = 21 * t;
      if (t > 0.98) {
        S("line", { x1: 10, y1: base - 2.2 * yk, x2: W - 10, y2: base - 2.2 * yk, style: "stroke:var(--ink);stroke-width:1.5;stroke-dasharray:6 4" }, svg);
        const tx = S("text", { x: 14, y: base - 2.2 * yk - 8 }, svg); tx.textContent = i18n("lineární hranice", "linear boundary");
      }
      A.forEach(x => marker(svg, 0, x0 + x * sc * 0.75, base - x * x * yk, 6, "var(--c1)"));
      B.forEach(x => marker(svg, 1, x0 + x * sc * 0.75, base - x * x * yk, 6, "var(--c2)"));
    }
    ctr.querySelector("button").onclick = function () {
      target = target ? 0 : 1;
      this.textContent = target ? i18n("Zpět do 1D", "Back to 1D") : toTwo;
      cancelAnimationFrame(anim);
      const step = () => { t += (target - t) * 0.12; if (Math.abs(target - t) < 0.01) t = target; draw(); if (t !== target) anim = requestAnimationFrame(step); };
      step();
    };
    draw();
  };

  // ===================================================================== MLR
  function erf(x) { // Abramowitz–Stegun 7.1.26
    const s = x < 0 ? -1 : 1; x = Math.abs(x);
    const t = 1 / (1 + 0.3275911 * x);
    const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
    return s * y;
  }
  function Phi(x) { return 0.5 * (1 + erf(x / Math.SQRT2)); }
  function clear(svg) { while (svg.firstChild) svg.removeChild(svg.firstChild); }
  function label(svg, x, y, txt, extra) {
    const t = S("text", Object.assign({ x: x, y: y }, extra || {}), svg); t.textContent = txt; return t;
  }
  function solve(A, b) { // Gaussova eliminace s částečnou pivotací
    const n = b.length, M = A.map((r, i) => r.concat([b[i]]));
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      [M[c], M[p]] = [M[p], M[c]];
      const d = M[c][c] || 1e-300;
      for (let r = c + 1; r < n; r++) { const f = M[r][c] / d; for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; }
    }
    const x = new Array(n).fill(0);
    for (let r = n - 1; r >= 0; r--) { let s = M[r][n]; for (let k = r + 1; k < n; k++) s -= M[r][k] * x[k]; x[r] = s / (M[r][r] || 1e-300); }
    return x;
  }
  function moonsData(n, noise, seed) {
    const r = rng(seed), X = [], y = [];
    for (let i = 0; i < n; i++) {
      const c = i % 2, t = Math.PI * r();
      const p = c === 0 ? [Math.cos(t), Math.sin(t)] : [1 - Math.cos(t), 0.5 - Math.sin(t)];
      X.push([p[0] + noise * gauss(r), p[1] + noise * gauss(r)]); y.push(c);
    }
    return [X, y];
  }

  // ===== gradientní sestup: krok učení =====
  DEMOS["gd-eta"] = function (el) {
    frame(el, i18n("krok učení gradientního sestupu", "learning rate of gradient descent"),
      i18n("Funkce f = ½(x₁² + q·x₂²), start vlevo nahoře, 25 kroků. Posuň krok učení η a „protáhlost“ údolí q. Sestup konverguje jen pro η &lt; 2/L, kde L = max(1, q) je největší křivost.",
        "Function f = ½(x₁² + q·x₂²), start at the top left, 25 steps. Move the learning rate η and the “stretch” of the valley q. Descent converges only for η &lt; 2/L, where L = max(1, q) is the largest curvature."));
    const W = 520, Hh = 300, sx = W / 9.2, sy = Hh / 5.2, ox = W / 2, oy = Hh / 2;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": i18n("trajektorie gradientního sestupu", "gradient descent path") }, el);
    const ctr = H(`<div class="controls"><label>η = <b class="ev"></b><input class="eta" type="range" min="0.01" max="0.6" step="0.01" value="0.2"></label>
      <label>q = <b class="qv"></b><input class="q" type="range" min="1" max="10" step="0.5" value="5"></label></div>`);
    el.appendChild(ctr);
    const out = H(`<div class="readout"></div>`); el.appendChild(out);
    const ie = ctr.querySelector(".eta"), iq = ctr.querySelector(".q");
    function draw() {
      const eta = +ie.value, q = +iq.value; ctr.querySelector(".ev").textContent = fmt(eta); ctr.querySelector(".qv").textContent = fmt(q, 1);
      clear(svg);
      [0.5, 2, 4.5, 8, 12.5].forEach(c => S("ellipse", { cx: ox, cy: oy, rx: Math.sqrt(2 * c) * sx, ry: Math.sqrt(2 * c / q) * sy, style: "fill:none;stroke:var(--line-strong);stroke-width:1" }, svg));
      let x = [-4, 1.5], d = `M${ox + x[0] * sx},${oy - x[1] * sy}`, div = false;
      const pts = [x.slice()];
      for (let k = 0; k < 25; k++) {
        x = [x[0] - eta * x[0], x[1] - eta * q * x[1]];
        if (Math.abs(x[0]) > 1e6 || Math.abs(x[1]) > 1e6) { div = true; break; }
        pts.push(x.slice());
      }
      pts.forEach((p, i) => { const px = Math.max(-4.55, Math.min(4.55, p[0])), py = Math.max(-2.55, Math.min(2.55, p[1])); if (i) d += `L${ox + px * sx},${oy - py * sy}`; });
      S("path", { d: d, style: "fill:none;stroke:var(--c2);stroke-width:1.6" }, svg);
      pts.forEach(p => { const px = Math.max(-4.55, Math.min(4.55, p[0])), py = Math.max(-2.55, Math.min(2.55, p[1])); S("circle", { cx: ox + px * sx, cy: oy - py * sy, r: 2.6, style: "fill:var(--c2)" }, svg); });
      S("circle", { cx: ox, cy: oy, r: 5, style: "fill:var(--c1)" }, svg);
      const last = pts[pts.length - 1], f = 0.5 * (last[0] ** 2 + q * last[1] ** 2), L = Math.max(1, q);
      const a = Math.abs(1 - eta), b = Math.abs(1 - eta * q);
      out.innerHTML = i18n(`násobitel chyby za krok: osa x₁ |1 − η| = <b>${fmt(a)}</b>, osa x₂ |1 − ηq| = <b>${fmt(b)}</b> · hranice 2/L = <b>${fmt(2 / L)}</b><br>`,
        `error multiplier per step: axis x₁ |1 − η| = <b>${fmt(a)}</b>, axis x₂ |1 − ηq| = <b>${fmt(b)}</b> · limit 2/L = <b>${fmt(2 / L)}</b><br>`) +
        (div || b >= 1 ? i18n(`<b>diverguje</b> – ve strmém směru chyba každým krokem roste`, `<b>diverges</b> – in the steep direction the error grows with every step`) :
          `${i18n("f po 25 krocích", "f after 25 steps")} = <b>${f < 1e-3 ? dec(f.toExponential(1)) : fmt(f, 3)}</b> · ` +
          (b > 0.6 && eta * q > 1 ? i18n("kmitá ve strmém směru", "oscillates in the steep direction") : a > 0.9 ? i18n("plíží se v plochém směru", "crawls in the flat direction") : i18n("rychlá konvergence", "fast convergence")));
    }
    ie.addEventListener("input", draw); iq.addEventListener("input", draw); draw();
  };

  // ===== k-NN: počet sousedů =====
  DEMOS["knn-k"] = function (el) {
    frame(el, i18n("k nejbližších sousedů", "k nearest neighbours"),
      i18n("Barva pozadí = třída, kterou by k-NN přiřadil bodu v daném místě. Malé k obkresluje každý bod (přeučení), velké k vše vyhladí (podučení). Sleduj přesnost na trénovacích a na nových (testovacích) bodech.",
        "Background colour = the class k-NN would give to a point at that place. Small k traces every point (overfitting), large k smooths everything (underfitting). Watch the accuracy on the training points and on new (test) points."));
    const W = 480, Hh = 300;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": i18n("oblasti rozhodnutí k-NN", "k-NN decision regions") }, el);
    const ctr = H(`<div class="controls"><label>k = <b class="kv"></b><input type="range" min="1" max="61" step="2" value="1"></label><button class="nd">${i18n("Nová data", "New data")}</button></div>`);
    el.appendChild(ctr);
    const out = H(`<div class="readout"></div>`); el.appendChild(out);
    const inp = ctr.querySelector("input");
    let seed = 2, X, y, Xt, yt;
    const x0 = -1.6, x1 = 2.6, y0 = -1.4, y1 = 1.6, px = v => (v - x0) / (x1 - x0) * W, py = v => Hh - (v - y0) / (y1 - y0) * Hh;
    function data() { [X, y] = moonsData(100, 0.33, seed); [Xt, yt] = moonsData(400, 0.33, seed + 1000); seed++; draw(); }
    function pred(p, k, skipSelf) {
      const d = X.map((q, i) => [(q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2, y[i]]).sort((a, b) => a[0] - b[0]);
      let s = 0; for (let i = 0; i < k; i++) s += d[i][1];
      return s * 2 > k ? 1 : 0;
    }
    function draw() {
      const k = +inp.value; ctr.querySelector(".kv").textContent = k;
      clear(svg);
      const nx = 60, ny = 38, cw = W / nx, ch = Hh / ny;
      for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
        const p = [x0 + (i + 0.5) / nx * (x1 - x0), y1 - (j + 0.5) / ny * (y1 - y0)];
        S("rect", { x: i * cw, y: j * ch, width: cw + 0.5, height: ch + 0.5, style: `fill:color-mix(in srgb, ${COL[pred(p, k)]} 18%, var(--surface))`, "shape-rendering": "crispEdges" }, svg);
      }
      X.forEach((p, i) => marker(svg, y[i], px(p[0]), py(p[1]), 4, COL[y[i]]));
      const tr = X.reduce((s, p, i) => s + (pred(p, k) === y[i]), 0) / X.length;
      const te = Xt.reduce((s, p, i) => s + (pred(p, k) === yt[i]), 0) / Xt.length;
      out.innerHTML = i18n(`přesnost: trénovací <b>${fmt(tr)}</b> · testovací <b>${fmt(te)}</b>`, `accuracy: training <b>${fmt(tr)}</b> · test <b>${fmt(te)}</b>`) +
        (k === 1 ? i18n(" · k = 1: každý trénovací bod je svým vlastním sousedem → trénovací přesnost 1", " · k = 1: every training point is its own neighbour → training accuracy 1") :
          k > 40 ? i18n(" · velké k: hranice se blíží přímce", " · large k: the boundary gets close to a straight line") : "");
    }
    inp.addEventListener("input", draw); ctr.querySelector(".nd").onclick = data; data();
  };

  // ===== práh a ROC =====
  DEMOS["roc-prah"] = function (el) {
    frame(el, i18n("práh, matice záměn a ROC", "threshold, confusion matrix and ROC"),
      i18n("Skóre negativních (modře) a pozitivních (oranžově) vzorků jsou dvě gaussovky. Posuň práh t, vzdálenost tříd d a prevalenci. Počty jsou pro 1000 vzorků.",
        "The scores of negative (blue) and positive (orange) samples are two Gaussian curves. Move the threshold t, the class distance d and the prevalence. Counts are for 1000 samples."));
    const W = 600, Hh = 230;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": i18n("rozdělení skóre a ROC křivka", "score distributions and ROC curve") }, el);
    const ctr = H(`<div class="controls"><label>${i18n("práh", "threshold")} t = <b class="tv"></b><input class="t" type="range" min="-3" max="6" step="0.05" value="1.2"></label>
      <label>d = <b class="dv"></b><input class="d" type="range" min="0" max="4" step="0.1" value="1.8"></label>
      <label>prevalence <b class="pv"></b><input class="p" type="range" min="0.01" max="0.5" step="0.01" value="0.2"></label></div>`);
    el.appendChild(ctr);
    const out = H(`<div class="readout"></div>`); el.appendChild(out);
    const it = ctr.querySelector(".t"), id = ctr.querySelector(".d"), ip = ctr.querySelector(".p");
    const L = 360, sx = v => 10 + (v + 4) / 11 * (L - 20), base = 200;
    const rx = v => 400 + v * 180, ry = v => 210 - v * 180;
    function draw() {
      const t = +it.value, d = +id.value, prev = +ip.value;
      ctr.querySelector(".tv").textContent = fmt(t); ctr.querySelector(".dv").textContent = fmt(d, 1); ctr.querySelector(".pv").textContent = fmt(prev * 100, 0) + " %";
      clear(svg);
      S("line", { x1: 10, y1: base, x2: L - 10, y2: base, class: "ax" }, svg);
      [[0, "var(--c1)"], [d, "var(--c2)"]].forEach(([mu, c]) => {
        let p = "", fill = `M${sx(t)},${base}`;
        for (let v = -4; v <= 7; v += 0.05) {
          const yv = base - 160 * Math.exp(-((v - mu) ** 2) / 2);
          p += (p ? "L" : "M") + sx(v).toFixed(1) + "," + yv.toFixed(1);
          if (v >= t) fill += `L${sx(v).toFixed(1)},${yv.toFixed(1)}`;
        }
        fill += `L${sx(7)},${base}Z`;
        S("path", { d: fill, style: `fill:${c};opacity:.22` }, svg);
        S("path", { d: p, style: `fill:none;stroke:${c};stroke-width:2` }, svg);
      });
      S("line", { x1: sx(t), y1: 20, x2: sx(t), y2: base, style: "stroke:var(--ink);stroke-width:1.5;stroke-dasharray:5 4" }, svg);
      label(svg, sx(t) + 4, 30, i18n("práh", "threshold"));
      S("rect", { x: rx(0), y: ry(1), width: 180, height: 180, style: "fill:none;stroke:var(--line-strong)" }, svg);
      S("line", { x1: rx(0), y1: ry(0), x2: rx(1), y2: ry(1), style: "stroke:var(--line-strong);stroke-dasharray:4 4" }, svg);
      let p = "";
      for (let v = 7; v >= -5; v -= 0.05) { const f = 1 - Phi(v), tp = 1 - Phi(v - d); p += (p ? "L" : "M") + rx(f).toFixed(1) + "," + ry(tp).toFixed(1); }
      S("path", { d: p, style: "fill:none;stroke:var(--c1);stroke-width:2" }, svg);
      const fpr = 1 - Phi(t), tpr = 1 - Phi(t - d);
      S("circle", { cx: rx(fpr), cy: ry(tpr), r: 6, style: "fill:var(--c2);stroke:var(--surface);stroke-width:1.5" }, svg);
      label(svg, rx(0.5), 225, "FPR", { "text-anchor": "middle" }); label(svg, rx(0) - 6, ry(0.5), "TPR", { "text-anchor": "end" });
      const P = 1000 * prev, N = 1000 - P, TP = tpr * P, FN = P - TP, FP = fpr * N, TN = N - FP;
      const prec = TP + FP > 0 ? TP / (TP + FP) : 0, f1 = 2 * TP / (2 * TP + FP + FN), acc = (TP + TN) / 1000;
      out.innerHTML = `TP <b>${Math.round(TP)}</b> · FN <b>${Math.round(FN)}</b> · FP <b>${Math.round(FP)}</b> · TN <b>${Math.round(TN)}</b><br>
        ${i18n("senzitivita", "sensitivity")} (TPR) <b>${fmt(tpr)}</b> · ${i18n("specificita", "specificity")} <b>${fmt(1 - fpr)}</b> · precision <b>${fmt(prec)}</b> · F1 <b>${fmt(f1)}</b> · accuracy <b>${fmt(acc)}</b> · AUC <b>${fmt(Phi(d / Math.SQRT2))}</b>`;
    }
    [it, id, ip].forEach(i => i.addEventListener("input", draw)); draw();
  };

  // ===== polynomiální ridge regrese =====
  DEMOS["poly-ridge"] = function (el) {
    frame(el, i18n("stupeň polynomu a regularizace λ", "polynomial degree and regularization λ"),
      i18n("20 trénovacích bodů ze sinusovky se šumem (čárkovaně skutečná funkce). Zvyšuj stupeň a sleduj, kdy model začne kmitat; pak přidej regularizaci λ. MSE na testu se počítá na 200 nových bodech.",
        "20 training points from a noisy sine wave (dashed: the true function). Increase the degree and watch when the model starts to wiggle; then add regularization λ. Test MSE is computed on 200 new points."));
    const W = 520, Hh = 280;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": i18n("polynomiální regrese", "polynomial regression") }, el);
    const ctr = H(`<div class="controls"><label>${i18n("stupeň", "degree")} m = <b class="mv"></b><input class="m" type="range" min="1" max="15" step="1" value="3"></label>
      <label>λ = <b class="lv"></b><input class="l" type="range" min="-8" max="2" step="0.5" value="-8"></label><button class="nd">${i18n("Nová data", "New data")}</button></div>`);
    el.appendChild(ctr);
    const out = H(`<div class="readout"></div>`); el.appendChild(out);
    const im = ctr.querySelector(".m"), il = ctr.querySelector(".l");
    const f = x => Math.sin(2 * Math.PI * x);
    let seed = 5, X, Y, Xt, Yt;
    function data() {
      const r = rng(seed++); X = []; Y = []; Xt = []; Yt = [];
      for (let i = 0; i < 20; i++) { const x = r(); X.push(x); Y.push(f(x) + 0.3 * gauss(r)); }
      for (let i = 0; i < 200; i++) { const x = r(); Xt.push(x); Yt.push(f(x) + 0.3 * gauss(r)); }
      draw();
    }
    const feat = (x, m) => { const s = 2 * x - 1, v = [1]; for (let k = 1; k <= m; k++) v.push(v[k - 1] * s); return v; };
    const sx = x => 20 + x * (W - 40), sy = v => Hh / 2 - v * 80;
    function draw() {
      const m = +im.value, lam = Math.pow(10, +il.value);
      ctr.querySelector(".mv").textContent = m; ctr.querySelector(".lv").textContent = +il.value <= -8 ? "0" : lam < 0.01 ? dec(lam.toExponential(0)) : fmt(lam, lam < 1 ? 2 : 0);
      const reg = +il.value <= -8 ? 1e-10 : lam;
      const A = Array.from({ length: m + 1 }, () => new Array(m + 1).fill(0)), b = new Array(m + 1).fill(0);
      X.forEach((x, i) => { const v = feat(x, m); for (let a = 0; a <= m; a++) { b[a] += v[a] * Y[i]; for (let c = 0; c <= m; c++) A[a][c] += v[a] * v[c]; } });
      for (let a = 1; a <= m; a++) A[a][a] += reg;
      const w = solve(A, b), pr = x => feat(x, m).reduce((s, v, k) => s + v * w[k], 0);
      clear(svg);
      S("line", { x1: 10, y1: Hh / 2, x2: W - 10, y2: Hh / 2, class: "ax" }, svg);
      let d1 = "", d2 = "";
      for (let x = 0; x <= 1.0001; x += 0.005) {
        d1 += (d1 ? "L" : "M") + sx(x).toFixed(1) + "," + sy(f(x)).toFixed(1);
        d2 += (d2 ? "L" : "M") + sx(x).toFixed(1) + "," + Math.max(-20, Math.min(Hh + 20, sy(pr(x)))).toFixed(1);
      }
      S("path", { d: d1, style: "fill:none;stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:5 4" }, svg);
      S("path", { d: d2, style: "fill:none;stroke:var(--c2);stroke-width:2.2" }, svg);
      X.forEach((x, i) => S("circle", { cx: sx(x), cy: sy(Y[i]), r: 4, style: "fill:var(--c1);stroke:var(--surface);stroke-width:1" }, svg));
      const tr = X.reduce((s, x, i) => s + (pr(x) - Y[i]) ** 2, 0) / X.length, te = Xt.reduce((s, x, i) => s + (pr(x) - Yt[i]) ** 2, 0) / Xt.length;
      const wn = Math.sqrt(w.slice(1).reduce((s, v) => s + v * v, 0));
      out.innerHTML = `MSE ${i18n("trénink", "train")} <b>${fmt(tr, 3)}</b> · MSE test <b>${fmt(te, 3)}</b> · ${i18n("velikost koeficientů", "size of coefficients")} ‖w‖ = <b>${wn > 1e4 ? dec(wn.toExponential(1)) : fmt(wn, 1)}</b>` +
        (te > 2 * tr && te > 0.2 ? i18n(" · <b>přeučení</b>", " · <b>overfitting</b>") : tr > 0.2 ? i18n(" · <b>podučení</b>", " · <b>underfitting</b>") : "");
    }
    im.addEventListener("input", draw); il.addEventListener("input", draw); ctr.querySelector(".nd").onclick = data; data();
  };

  // ===== lineární soft-margin SVM: parametr C =====
  DEMOS["svm-c"] = function (el) {
    frame(el, i18n("soft-margin SVM a parametr C", "soft-margin SVM and the parameter C"),
      i18n("Lineární SVM řešené duálním souřadnicovým sestupem. Plná čára = hranice, čárkovaně okraje, kroužky = support vektory. Malé C = levná porušení, široký pás; velké C = drahá porušení, úzký pás.",
        "Linear SVM solved by dual coordinate descent. Solid line = boundary, dashed = margins, circles = support vectors. Small C = cheap violations, wide band; large C = expensive violations, narrow band."));
    const W = 420, Hh = 320, sc = 50, ox = W / 2, oy = Hh / 2;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, class: "sq", role: "img", "aria-label": i18n("lineární SVM", "linear SVM") }, el);
    const ctr = H(`<div class="controls"><label>C = <b class="cv"></b><input type="range" min="-2" max="2.5" step="0.1" value="0"></label><button class="nd">${i18n("Nová data", "New data")}</button></div>`);
    el.appendChild(ctr);
    const out = H(`<div class="readout"></div>`); el.appendChild(out);
    const inp = ctr.querySelector("input");
    let seed = 4, X, y;
    function data() {
      const r = rng(seed++); X = []; y = [];
      for (let i = 0; i < 40; i++) { const c = i % 2 ? 1 : -1; X.push([c * 0.9 + 0.95 * gauss(r), c * 0.8 + 0.95 * gauss(r)]); y.push(c); }
      draw();
    }
    function train(C) { // duální souřadnicový sestup (bias jako 3. složka)
      const n = X.length, Z = X.map(p => [p[0], p[1], 1]), a = new Array(n).fill(0), w = [0, 0, 0];
      for (let ep = 0; ep < 400; ep++) {
        let maxd = 0;
        for (let i = 0; i < n; i++) {
          const z = Z[i], G = y[i] * (w[0] * z[0] + w[1] * z[1] + w[2] * z[2]) - 1, Q = z[0] * z[0] + z[1] * z[1] + 1;
          const na = Math.min(Math.max(a[i] - G / Q, 0), C), dd = (na - a[i]) * y[i];
          if (dd) { w[0] += dd * z[0]; w[1] += dd * z[1]; w[2] += dd * z[2]; }
          maxd = Math.max(maxd, Math.abs(na - a[i])); a[i] = na;
        }
        if (maxd < 1e-6) break;
      }
      return [w, a];
    }
    function draw() {
      const C = Math.pow(10, +inp.value); ctr.querySelector(".cv").textContent = C < 1 ? fmt(C, 2) : fmt(C, C < 10 ? 1 : 0);
      const [w, a] = train(C);
      clear(svg); axes(svg, W, Hh, 8);
      const line = (off, ls) => {
        const P = [];
        if (Math.abs(w[1]) > 1e-9) [-5, 5].forEach(x => P.push([x, (off - w[2] - w[0] * x) / w[1]]));
        else [-4, 4].forEach(yy => P.push([(off - w[2]) / w[0], yy]));
        S("line", { x1: ox + P[0][0] * sc, y1: oy - P[0][1] * sc, x2: ox + P[1][0] * sc, y2: oy - P[1][1] * sc, style: `stroke:var(--ink-2);stroke-width:${ls ? 1.2 : 2};${ls ? "stroke-dasharray:5 4" : ""}` }, svg);
      };
      line(0, false); line(1, true); line(-1, true);
      let sv = 0, err = 0;
      X.forEach((p, i) => {
        const f = w[0] * p[0] + w[1] * p[1] + w[2];
        if (a[i] > 1e-6) { sv++; S("circle", { cx: ox + p[0] * sc, cy: oy - p[1] * sc, r: 9, style: "fill:none;stroke:var(--ink);stroke-width:1.2" }, svg); }
        if (y[i] * f <= 0) err++;
        marker(svg, y[i] > 0 ? 1 : 0, ox + p[0] * sc, oy - p[1] * sc, 4.2, COL[y[i] > 0 ? 1 : 0]);
      });
      const nw = Math.hypot(w[0], w[1]);
      out.innerHTML = i18n(`šířka pásu 2/‖w‖ = <b>${fmt(2 / nw)}</b> · support vektorů <b>${sv}</b> z 40 · chybně zařazených trénovacích bodů <b>${err}</b>`,
        `band width 2/‖w‖ = <b>${fmt(2 / nw)}</b> · support vectors <b>${sv}</b> of 40 · misclassified training points <b>${err}</b>`);
    }
    inp.addEventListener("input", draw); ctr.querySelector(".nd").onclick = data; data();
  };

  // ===== regresní strom a bagging =====
  DEMOS["strom-bagging"] = function (el) {
    frame(el, i18n("regresní strom, hloubka a bagging", "regression tree, depth and bagging"),
      i18n("45 trénovacích bodů, čárkovaně skutečná funkce. Hloubka a minimální velikost listu řídí jeden strom (šedě); bagging zprůměruje M stromů natrénovaných na bootstrap výběrech (oranžově). Klikni na „Nová data“ a sleduj, jak moc se mění jeden strom a jak málo průměr.",
        "45 training points, dashed: the true function. Depth and minimum leaf size control a single tree (grey); bagging averages M trees trained on bootstrap samples (orange). Click “New data” and watch how much a single tree changes and how little the average does."));
    const W = 540, Hh = 280;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": i18n("regresní strom a bagging", "regression tree and bagging") }, el);
    const ctr = H(`<div class="controls"><label>max_depth = <b class="dv"></b><input class="d" type="range" min="1" max="8" step="1" value="4"></label>
      <label>min_samples_leaf = <b class="lv"></b><input class="l" type="range" min="1" max="10" step="1" value="1"></label>
      <label>M = <b class="mv"></b><input class="m" type="range" min="1" max="100" step="1" value="30"></label><button class="nd">${i18n("Nová data", "New data")}</button></div>`);
    el.appendChild(ctr);
    const out = H(`<div class="readout"></div>`); el.appendChild(out);
    const idp = ctr.querySelector(".d"), il = ctr.querySelector(".l"), imm = ctr.querySelector(".m");
    const f = x => 1.2 * Math.sin(1.4 * x) + 0.25 * x;
    let seed = 12, X, Y, Xt, Yt;
    function data() {
      const r = rng(seed++); X = []; Y = []; Xt = []; Yt = [];
      for (let i = 0; i < 45; i++) { const x = 5 * r(); X.push(x); Y.push(f(x) + 0.5 * gauss(r)); }
      for (let i = 0; i < 400; i++) { const x = 5 * r(); Xt.push(x); Yt.push(f(x) + 0.5 * gauss(r)); }
      draw();
    }
    function grow(idx, depth, maxD, minLeaf) { // CART pro 1D: dělení minimalizující součet čtverců
      const ys = idx.map(i => Y[i]), mean = ys.reduce((a, b) => a + b, 0) / ys.length;
      if (depth >= maxD || idx.length < 2 * minLeaf) return { v: mean };
      const s = idx.slice().sort((a, b) => X[a] - X[b]);
      let best = null, sl = 0, sl2 = 0, tot = 0, tot2 = 0;
      s.forEach(i => { tot += Y[i]; tot2 += Y[i] * Y[i]; });
      for (let k = 0; k < s.length - 1; k++) {
        sl += Y[s[k]]; sl2 += Y[s[k]] ** 2;
        const nl = k + 1, nr = s.length - nl;
        if (nl < minLeaf || nr < minLeaf || X[s[k]] === X[s[k + 1]]) continue;
        const sse = sl2 - sl * sl / nl + (tot2 - sl2) - (tot - sl) ** 2 / nr;
        if (!best || sse < best.sse) best = { sse: sse, thr: (X[s[k]] + X[s[k + 1]]) / 2, k: k };
      }
      if (!best) return { v: mean };
      return { thr: best.thr, l: grow(s.slice(0, best.k + 1), depth + 1, maxD, minLeaf), r: grow(s.slice(best.k + 1), depth + 1, maxD, minLeaf) };
    }
    const pred = (t, x) => t.thr === undefined ? t.v : pred(x <= t.thr ? t.l : t.r, x);
    const sx = x => 20 + x / 5 * (W - 40), sy = v => 150 - v * 50;
    function path(fn, style) {
      let d = ""; for (let x = 0; x <= 5.0001; x += 0.02) d += (d ? "L" : "M") + sx(x).toFixed(1) + "," + sy(fn(x)).toFixed(1);
      S("path", { d: d, style: style }, svg);
    }
    function draw() {
      const D = +idp.value, mL = +il.value, M = +imm.value;
      ctr.querySelector(".dv").textContent = D; ctr.querySelector(".lv").textContent = mL; ctr.querySelector(".mv").textContent = M;
      const all = X.map((_, i) => i), single = grow(all, 0, D, mL);
      const r = rng(77), trees = [];
      for (let m = 0; m < M; m++) { const b = all.map(() => Math.floor(r() * X.length)); trees.push(grow(b, 0, D, mL)); }
      const bag = x => trees.reduce((s, t) => s + pred(t, x), 0) / trees.length;
      clear(svg);
      trees.slice(0, 12).forEach(t => path(x => pred(t, x), "fill:none;stroke:var(--c2);stroke-width:.8;opacity:.25"));
      path(f, "fill:none;stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:5 4");
      path(x => pred(single, x), "fill:none;stroke:var(--c4);stroke-width:1.8");
      path(bag, "fill:none;stroke:var(--c2);stroke-width:2.4");
      X.forEach((x, i) => S("circle", { cx: sx(x), cy: sy(Y[i]), r: 3.6, style: "fill:var(--c1);stroke:var(--surface);stroke-width:1" }, svg));
      const mse = g => Xt.reduce((s, x, i) => s + (g(x) - Yt[i]) ** 2, 0) / Xt.length;
      out.innerHTML = i18n(`MSE na testu: jeden strom <b>${fmt(mse(x => pred(single, x)), 3)}</b> · bagging M = ${M} <b>${fmt(mse(bag), 3)}</b> <span class="muted">(šum σ² = 0,25 je minimum, pod které se nedá dostat)</span>`,
        `test MSE: single tree <b>${fmt(mse(x => pred(single, x)), 3)}</b> · bagging M = ${M} <b>${fmt(mse(bag), 3)}</b> <span class="muted">(noise σ² = 0.25 is the minimum you cannot go below)</span>`);
    }
    [idp, il, imm].forEach(i => i.addEventListener("input", draw)); ctr.querySelector(".nd").onclick = data; data();
  };

  // ===== optimalizátory na Bealeově funkci =====
  DEMOS.optimizery = function (el) {
    frame(el, i18n("optimalizátory na Bealeově funkci", "optimizers on the Beale function"),
      i18n("Kliknutím do mapy zvolíš start, posuvníkem vynásobíš krok učení všech optimalizátorů. Výchozí kroky: SGD a momentum η = 10⁻⁵, RMSprop 0,03, Adam 0,2. Hvězda = minimum (3; 0,5). Zkus × 10 – kdo se rozbije první?",
        "Click into the map to choose the start; the slider multiplies the learning rate of all optimizers. Default rates: SGD and momentum η = 10⁻⁵, RMSprop 0.03, Adam 0.2. Star = minimum (3, 0.5). Try × 10 – who breaks first?"));
    const W = 500, Hh = 300, xa = -0.5, xb = 4.5, ya = -3.2, yb = 1.6;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": i18n("trajektorie optimalizátorů", "optimizer paths"), style: "cursor:crosshair" }, el);
    const ctr = H(`<div class="controls"><label>η × <b class="sv"></b><input type="range" min="-1" max="1" step="0.1" value="0"></label><label>${i18n("kroků", "steps")} <select class="st"><option>300</option><option>1000</option><option selected>3000</option></select></label></div>`);
    el.appendChild(ctr);
    const out = H(`<div class="readout"></div>`); el.appendChild(out);
    const inp = ctr.querySelector("input");
    const px = v => (v - xa) / (xb - xa) * W, py = v => Hh - (v - ya) / (yb - ya) * Hh;
    const beale = (x, y) => (1.5 - x + x * y) ** 2 + (2.25 - x + x * y * y) ** 2 + (2.625 - x + x * y ** 3) ** 2;
    const grad = (x, y) => {
      const a = 1.5 - x + x * y, b = 2.25 - x + x * y * y, c = 2.625 - x + x * y ** 3;
      return [2 * a * (y - 1) + 2 * b * (y * y - 1) + 2 * c * (y ** 3 - 1), 2 * a * x + 4 * b * x * y + 6 * c * x * y * y];
    };
    let start = [2.4, -2.8];
    const OPT = [["SGD", 1e-5, "var(--c4)"], ["momentum", 1e-5, "var(--c1)"], ["RMSprop", 0.03, "var(--c3)"], ["Adam", 0.2, "var(--c2)"]];
    function run(name, eta, steps) {
      let p = start.slice(), u = [0, 0], s = [0, 0], m = [0, 0], v = [0, 0]; const P = [p.slice()];
      for (let t = 1; t <= steps; t++) {
        const g = grad(p[0], p[1]);
        for (let k = 0; k < 2; k++) {
          if (name === "SGD") p[k] -= eta * g[k];
          else if (name === "momentum") { u[k] = 0.9 * u[k] + eta * g[k]; p[k] -= u[k]; }
          else if (name === "RMSprop") { s[k] = 0.9 * s[k] + 0.1 * g[k] * g[k]; p[k] -= eta * g[k] / (Math.sqrt(s[k]) + 1e-8); }
          else { m[k] = 0.9 * m[k] + 0.1 * g[k]; v[k] = 0.999 * v[k] + 0.001 * g[k] * g[k]; p[k] -= eta * (m[k] / (1 - 0.9 ** t)) / (Math.sqrt(v[k] / (1 - 0.999 ** t)) + 1e-8); }
        }
        if (!isFinite(p[0]) || !isFinite(p[1]) || Math.abs(p[0]) > 50 || Math.abs(p[1]) > 50) return [P, true];
        if (t % 5 === 0 || t < 50) P.push(p.slice());
      }
      P.push(p.slice()); return [P, false];
    }
    const nx = 50, ny = 30, cells = [];
    for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
      const x = xa + (i + 0.5) / nx * (xb - xa), y = yb - (j + 0.5) / ny * (yb - ya);
      cells.push([i, j, Math.log10(beale(x, y) + 1e-3)]);
    }
    function draw() {
      const mult = Math.pow(10, +inp.value), steps = +ctr.querySelector(".st").value;
      ctr.querySelector(".sv").textContent = fmt(mult, mult < 1 ? 2 : 1);
      clear(svg);
      const cw = W / nx, ch = Hh / ny;
      cells.forEach(([i, j, l]) => S("rect", { x: i * cw, y: j * ch, width: cw + .5, height: ch + .5, style: `fill:color-mix(in srgb, var(--c1) ${(Math.max(0, Math.min(5, l + 1)) / 5 * 35).toFixed(1)}%, var(--surface))`, "shape-rendering": "crispEdges" }, svg));
      const res = [];
      OPT.forEach(([name, eta, col]) => {
        const [P, div] = run(name, eta * mult, steps);
        let d = ""; P.forEach(p => { d += (d ? "L" : "M") + px(Math.max(xa, Math.min(xb, p[0]))).toFixed(1) + "," + py(Math.max(ya, Math.min(yb, p[1]))).toFixed(1); });
        S("path", { d: d, style: `fill:none;stroke:${col};stroke-width:2` }, svg);
        const last = P[P.length - 1];
        res.push(`${name}: <b>${div ? i18n("diverguje", "diverges") : fmt(Math.hypot(last[0] - 3, last[1] - 0.5), 3)}</b>`);
      });
      label(svg, px(3) + 8, py(0.5) - 8, "minimum", { style: "font-size:12px;fill:var(--ink)" });
      S("path", { d: `M${px(3)},${py(0.5) - 8}l2.4,5.6 6,.5-4.6,4 1.4,5.9-5.2-3.1-5.2,3.1 1.4-5.9-4.6-4 6-.5z`, style: "fill:var(--ink)" }, svg);
      S("circle", { cx: px(start[0]), cy: py(start[1]), r: 5, style: "fill:var(--surface);stroke:var(--ink);stroke-width:2" }, svg);
      out.innerHTML = i18n("vzdálenost od minima: ", "distance from the minimum: ") + res.join(" · ") +
        `<br><span class="muted">${i18n("šedá SGD · modrá momentum · zelená RMSprop · oranžová Adam", "grey SGD · blue momentum · green RMSprop · orange Adam")}</span>`;
    }
    svg.addEventListener("click", e => {
      const r = svg.getBoundingClientRect();
      start = [xa + (e.clientX - r.left) / r.width * (xb - xa), yb - (e.clientY - r.top) / r.height * (yb - ya)];
      draw();
    });
    inp.addEventListener("input", draw); ctr.querySelector(".st").addEventListener("change", draw); draw();
  };
})();
