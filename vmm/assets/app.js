/* VMM – skripta: navigace, téma, vzorce a interaktivní ukázky (bez knihoven). */
(function () {
  "use strict";

  // ---------- téma ----------
  const root = document.documentElement;
  function getStored() { try { return localStorage.getItem("vmm-theme"); } catch (e) { return null; } }
  function setStored(v) { try { localStorage.setItem("vmm-theme", v); } catch (e) { /* bez úložiště */ } }
  const stored = getStored();
  if (stored === "light" || stored === "dark") root.setAttribute("data-theme", stored);

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
    document.addEventListener("DOMContentLoaded", preparePrint);
  }

  document.addEventListener("DOMContentLoaded", function () {
    const tb = document.getElementById("themeBtn");
    if (tb) {
      const label = () => {
        const dark = root.getAttribute("data-theme") === "dark" ||
          (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
        tb.textContent = dark ? "Světlý režim" : "Tmavý režim";
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

  // ===== 1) korelace a Mahalanobisova vzdálenost =====
  DEMOS.korelace = function (el) {
    frame(el, "korelace a Mahalanobisova vzdálenost",
      "Posuň korelaci ρ. Body A a B mají od středu <b>stejnou eukleidovskou</b> vzdálenost, ale jejich Mahalanobisova vzdálenost se liší podle toho, jestli leží „po směru“ mraku, nebo „proti“ němu.");
    const W = 420, Hh = 420, sc = 56, cx = W / 2, cy = Hh / 2;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, class: "sq", role: "img", "aria-label": "bodový graf korelovaných dat" }, el);
    const r = rng(11), N = 260, Z = [];
    for (let i = 0; i < N; i++) Z.push([gauss(r), gauss(r)]);
    const ctr = H(`<div class="controls"><label>ρ = <b class="rv">0,70</b><input type="range" min="-0.95" max="0.95" step="0.05" value="0.7"></label></div>`);
    el.appendChild(ctr);
    const out = H(`<div class="readout"></div>`); el.appendChild(out);
    el.appendChild(H(`<div class="note">Elipsa = oblast, kam padá 95 % bodů (D² ≤ 5,99 = 95% kvantil χ² se 2 st. v.). Bod mimo elipsu je „vícerozměrně odlehlý“, i když v každé proměnné zvlášť vypadá normálně.</div>`));
    const inp = ctr.querySelector("input"), rv = ctr.querySelector(".rv");
    const A = [1.5, 1.5], B = [1.5, -1.5];
    function draw() {
      const rho = +inp.value; rv.textContent = fmt(rho);
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      for (let k = -3; k <= 3; k++) {
        S("line", { x1: cx + k * sc, y1: 14, x2: cx + k * sc, y2: Hh - 14, class: "grid" }, svg);
        S("line", { x1: 14, y1: cy + k * sc, x2: W - 14, y2: cy + k * sc, class: "grid" }, svg);
      }
      axes(svg, W, Hh, 14);
      const s = Math.sqrt(1 - rho * rho);
      let sxy = 0, sxx = 0, syy = 0;
      const pts = Z.map(z => [z[0], rho * z[0] + s * z[1]]);
      pts.forEach(p => { sxy += p[0] * p[1]; sxx += p[0] * p[0]; syy += p[1] * p[1]; });
      pts.forEach(p => S("circle", { cx: cx + p[0] * sc, cy: cy - p[1] * sc, r: 2.6, style: "fill:var(--c1);opacity:.45" }, svg));
      const c = Math.sqrt(5.991);
      S("ellipse", {
        cx: cx, cy: cy, rx: c * Math.sqrt(1 + rho) * sc, ry: c * Math.sqrt(1 - rho) * sc,
        transform: `rotate(-45 ${cx} ${cy})`, style: "fill:none;stroke:var(--ink-2);stroke-width:1.5;stroke-dasharray:5 4"
      }, svg);
      const dA = Math.sqrt(4.5 / (1 + rho)), dB = Math.sqrt(4.5 / (1 - rho));
      [[A, "A", dA, 0], [B, "B", dB, 1]].forEach(([p, nm, d, sh]) => {
        S("line", { x1: cx, y1: cy, x2: cx + p[0] * sc, y2: cy - p[1] * sc, style: "stroke:var(--ink-2);stroke-width:1" }, svg);
        marker(svg, sh, cx + p[0] * sc, cy - p[1] * sc, 7, "var(--c2)");
        const t = S("text", { x: cx + p[0] * sc + 10, y: cy - p[1] * sc + 4, style: "font-size:14px;font-weight:600;fill:var(--ink)" }, svg);
        t.textContent = nm;
      });
      const rr = sxy / Math.sqrt(sxx * syy);
      out.innerHTML = `výběrová korelace r = <b>${fmt(rr)}</b> · eukleidovská vzdálenost A i B = <b>2,12</b><br>
        Mahalanobis: A = <b>${fmt(dA)}</b> ${dA * dA <= 5.991 ? "(uvnitř elipsy)" : "(mimo elipsu)"} · B = <b>${fmt(dB)}</b> ${dB * dB <= 5.991 ? "(uvnitř elipsy)" : "(mimo elipsu → odlehlý)"}`;
    }
    inp.addEventListener("input", draw); draw();
  };

  // ===== 2) PCA: otáčení osy =====
  DEMOS["pca-rotace"] = function (el) {
    frame(el, "PCA jako hledání nejlepšího směru",
      "Otáčej osou a sleduj, kolik rozptylu se na ni „promítne“. PCA dělá přesně tohle – hledá směr s největším rozptylem projekcí (to je PC1). Všimni si, že součet rozptylu podél osy a kolmo na ni je pořád stejný.");
    const W = 440, Hh = 400, sc = 60, cx = W / 2, cy = Hh / 2;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, class: "sq", role: "img", "aria-label": "projekce bodů na otáčenou osu" }, el);
    const r = rng(5), N = 120, P = [];
    for (let i = 0; i < N; i++) { const z1 = gauss(r), z2 = gauss(r); P.push([1.5 * z1, 0.85 * (0.75 * z1 + 0.66 * z2)]); }
    const mx = P.reduce((s, p) => s + p[0], 0) / N, my = P.reduce((s, p) => s + p[1], 0) / N;
    P.forEach(p => { p[0] -= mx; p[1] -= my; });
    let a = 0, b = 0, c = 0;
    P.forEach(p => { a += p[0] * p[0]; b += p[0] * p[1]; c += p[1] * p[1]; });
    a /= N - 1; b /= N - 1; c /= N - 1;
    const total = a + c;
    const best = (0.5 * Math.atan2(2 * b, a - c) * 180 / Math.PI + 180) % 180;
    const ctr = H(`<div class="controls"><label>úhel osy: <b class="av">0°</b><input type="range" min="0" max="179" step="1" value="0"></label><button class="primary">Najdi PC1</button><button class="perp">Kolmý směr (PC2)</button></div>`);
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
      out.innerHTML = `rozptyl projekcí na osu: <b>${fmt(v)}</b> (${fmt(pct, 0)} % celku) · kolmo na osu: <b>${fmt(total - v)}</b> · celkem vždy <b>${fmt(total)}</b>` +
        (Math.abs(((+inp.value - best + 270) % 180) - 90) < 1.5 ? " · <b>to je PC1!</b>" : "");
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
    frame(el, "k-means krok za krokem",
      "Střídej kroky <b>1) přiřaď</b> a <b>2) přepočítej těžiště</b>. Zkus zvolit „špatné“ K nebo nová náhodná těžiště a sleduj, že výsledek závisí na startu a že WSS při každém kroku klesá.");
    const W = 440, Hh = 340, sc = 40, cx = W / 2, cy = Hh / 2;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": "shlukování k-means" }, el);
    const ctr = H(`<div class="controls">
      <label>K <select class="k"><option>2</option><option selected>3</option><option>4</option></select></label>
      <button class="nd">Nová data</button><button class="init">Náhodná těžiště</button>
      <button class="primary as">1) Přiřaď body</button><button class="primary up">2) Přepočítej těžiště</button><button class="run">Dokonči</button></div>`);
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
      lab = null; it = 0; phase = "assign"; draw("Těžiště umístěna náhodně do bodů. Teď krok 1.");
    }
    function d2(p, q) { return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2; }
    function assign() {
      lab = X.map(p => { let b = 0; C.forEach((c, k) => { if (d2(p, c) < d2(p, C[b])) b = k; }); return b; });
      phase = "update"; draw("Každý bod přiřazen k nejbližšímu těžišti.");
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
      draw(moved < 1e-6 ? "Těžiště se už nepohnula → algoritmus zkonvergoval." : `Těžiště posunuta do průměru svých bodů (max. posun ${fmt(moved)}).`);
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
      out.innerHTML = `${msg || ""}<br>iterace: <b>${it}</b> · WSS (součet čtverců vzdáleností k těžišti): <b>${isNaN(w) ? "–" : fmt(w, 1)}</b>`;
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
    frame(el, "σ, podmíněné pravděpodobnosti a perplexita",
      "Bod i je uprostřed. Gaussova křivka kolem něj určuje, s jakou pravděpodobností si i „vybere“ ostatní body za sousedy (sloupce). Šířku σ měň posuvníkem – perplexita ukazuje <b>efektivní počet sousedů</b>. t-SNE hledá σ pro každý bod zvlášť tak, aby perplexita byla rovna zadané hodnotě.");
    const W = 600, Hh = 230, x0 = 300, sc = 34, base = 180;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": "podmíněné pravděpodobnosti sousedů" }, el);
    const pos = [-1.0, -0.6, -0.35, 0.3, 0.55, 0.9, 2.6, 3.4, 4.3, 5.6, 7.2, -3.0, -4.6, -6.5];
    const ctr = H(`<div class="controls"><label>σ = <b class="sv"></b><input type="range" min="-2.3" max="1.8" step="0.01" value="-0.3"></label>
      <label>cílová perplexita <select class="tp"><option>2</option><option selected>5</option><option>10</option></select></label><button class="primary">Najdi σ (půlení intervalu)</button></div>`);
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
      const t = S("text", { x: x0, y: base + 38, "text-anchor": "middle", style: "font-size:13px;fill:var(--ink)" }, svg); t.textContent = "bod i";
      const t2 = S("text", { x: x0 - 1.5 * sc, y: 24, "text-anchor": "middle" }, svg); t2.textContent = "hustá oblast";
      const t3 = S("text", { x: x0 + 5 * sc, y: 24, "text-anchor": "middle" }, svg); t3.textContent = "řídká oblast";
      out.innerHTML = `perplexita = 2<sup>H</sup> = <b>${fmt(perp, 1)}</b> (≈ počet „vlivných“ sousedů)` + (extra ? " · " + extra : "");
    }
    ctr.querySelector(".primary").onclick = () => {
      const target = +ctr.querySelector(".tp").value;
      let lo = 0.01, hi = 50, s = 1, k = 0;
      for (; k < 60; k++) { s = (lo + hi) / 2; const pp = probs(s)[1]; if (Math.abs(pp - target) < 1e-3) break; if (pp > target) hi = s; else lo = s; }
      inp.value = Math.log(s); draw(`nalezeno za ${k + 1} kroků půlení intervalu`);
    };
    inp.addEventListener("input", () => draw()); draw();
  };

  // ===== 5) UMAP: fuzzy graf sousedů =====
  DEMOS["umap-graf"] = function (el) {
    frame(el, "UMAP – vážený graf k nejbližších sousedů",
      "Body leží na zašuměné křivce s různou hustotou. UMAP propojí každý bod s jeho k nejbližšími sousedy; síla (tloušťka) hrany klesá se vzdáleností, ale měřítko je <b>lokální</b> – v řídké oblasti se „natáhne“, takže graf zůstane spojený. Malé k → rozpadlý graf (jen detaily), velké k → hustý graf (globální tvar).");
    const W = 600, Hh = 260;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": "graf sousedů UMAP" }, el);
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
      out.innerHTML = `hran v grafu: <b>${edges}</b> · počet oddělených částí grafu: <b>${comps}</b>` + (comps > 1 ? " (graf je rozpadlý – v mapě vzniknou umělé „ostrůvky“)" : " (graf je souvislý)");
    }
    inp.addEventListener("input", draw); draw();
  };

  // ===== 6) kernel: 1D → 2D =====
  DEMOS.kernel = function (el) {
    frame(el, "jádrová transformace 1D → 2D",
      "V 1D jsou modré body uprostřed a oranžové po stranách – žádný jediný práh je neoddělí. Po zobrazení x → (x, x²) „vyskočí“ oranžové body nahoru a stačí jediná přímka.");
    const W = 520, Hh = 280, x0 = 260, sc = 70, base = 240;
    const svg = S("svg", { viewBox: `0 0 ${W} ${Hh}`, role: "img", "aria-label": "jádrová transformace" }, el);
    const r = rng(4), A = [], B = [];
    for (let i = 0; i < 10; i++) A.push(-1 + 2 * r());
    for (let i = 0; i < 6; i++) { B.push(-3.2 + 1.4 * r()); B.push(1.8 + 1.4 * r()); }
    const ctr = H(`<div class="controls"><button class="primary">Zobraz do 2D: x → (x, x²)</button></div>`);
    el.appendChild(ctr);
    let t = 0, target = 0, anim = null;
    function draw() {
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      S("line", { x1: 10, y1: base, x2: W - 10, y2: base, class: "ax" }, svg);
      const yk = 21 * t;
      if (t > 0.98) {
        S("line", { x1: 10, y1: base - 2.2 * yk, x2: W - 10, y2: base - 2.2 * yk, style: "stroke:var(--ink);stroke-width:1.5;stroke-dasharray:6 4" }, svg);
        const tx = S("text", { x: 14, y: base - 2.2 * yk - 8 }, svg); tx.textContent = "lineární hranice";
      }
      A.forEach(x => marker(svg, 0, x0 + x * sc * 0.75, base - x * x * yk, 6, "var(--c1)"));
      B.forEach(x => marker(svg, 1, x0 + x * sc * 0.75, base - x * x * yk, 6, "var(--c2)"));
    }
    ctr.querySelector("button").onclick = function () {
      target = target ? 0 : 1;
      this.textContent = target ? "Zpět do 1D" : "Zobraz do 2D: x → (x, x²)";
      cancelAnimationFrame(anim);
      const step = () => { t += (target - t) * 0.12; if (Math.abs(target - t) < 0.01) t = target; draw(); if (t !== target) anim = requestAnimationFrame(step); };
      step();
    };
    draw();
  };
})();
