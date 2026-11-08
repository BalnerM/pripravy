"""Generuje pso/test/tabulky.html: statistické tabulky na 2 A4 (Φ, u, t, χ², F, Kolmogorov–Smirnov).

Spuštění: uv run python pso/test/_gen/make_tabulky.py  (pak make_pdfs.py tabulky.html)
"""
from pathlib import Path
from scipy import stats as st

OUT = Path(__file__).resolve().parent.parent / "tabulky.html"
INF = "∞"


def c(v, nd):
    return f"{v:.{nd}f}".replace(".", ",")


def auto(v):
    return c(v, 4 if v < 0.1 else 3 if v < 10 else 2 if v < 100 else 1)


def tab(head, rows, cls=""):
    h = "<tr>" + "".join(f"<th>{x}</th>" for x in head) + "</tr>"
    b = "\n".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    return f'<table class="{cls}">\n{h}\n{b}\n</table>'


def phi():
    rows = []
    for i in range(35):
        u = i / 10
        rows.append([c(u, 1)] + [c(st.norm.cdf(u + j / 100), 4)[1:] for j in range(10)])
    return tab(["u"] + [c(j / 100, 2) for j in range(10)], rows, "phi")


def quant_u():
    ps = [0.8, 0.85, 0.875, 0.9, 0.95, 0.975, 0.98, 0.99, 0.995, 0.999]
    return tab(["p"] + [c(p, 3).rstrip("0") for p in ps], [["u<sub>p</sub>"] + [c(st.norm.ppf(p), 4) for p in ps]])


NU = list(range(1, 31)) + [40, 50, 60, 80, 100, 120, 150, 200]


def t_tab():
    ps = [0.9, 0.95, 0.975, 0.99, 0.995]
    rows = [[n] + [c(st.t.ppf(p, n), 3) for p in ps] for n in NU]
    rows.append([INF] + [c(st.norm.ppf(p), 3) for p in ps])
    return tab(["ν"] + [c(p, 3).rstrip("0") for p in ps], rows)


def chi_tab():
    ps = [0.005, 0.01, 0.025, 0.05, 0.95, 0.975, 0.99, 0.995]
    rows = [[n] + [auto(st.chi2.ppf(p, n)) for p in ps] for n in NU[:-2]]
    return tab(["ν"] + [c(p, 3).rstrip("0") for p in ps], rows)


N1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 60, None]
N2 = list(range(1, 31)) + [40, 60, 120, None]


def f_tab(p):
    head = ["ν₂ ↓  ν₁ →"] + [INF if a is None else a for a in N1]
    rows = []
    for b in N2:
        r = [INF if b is None else b]
        for a in N1:
            aa = 1e7 if a is None else a
            bb = 1e7 if b is None else b
            r.append(auto(st.f.ppf(p, aa, bb)))
        rows.append(r)
    return tab(head, rows, "ft")


def ks_tab():
    rows = []
    for k in (1, 21):
        part = range(k, k + 20)
        rows.append(["<b>n</b>"] + [f"<b>{n}</b>" for n in part])
        rows.append(["α = 0,05"] + [c(st.kstwo.ppf(0.95, n), 3) for n in part])
        rows.append(["α = 0,01"] + [c(st.kstwo.ppf(0.99, n), 3) for n in part])
    b = "\n".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    return f'<table class="ks">\n{b}\n</table>'


HTML = """<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PSO statistické tabulky</title>
<style>
:root {{ --ink:#111a24; --mute:#55606d; --line:#c8d0d9; --c1d:#174f96; --th:#eef1f5; }}
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: #fff; color: var(--ink); -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font: 7.3pt/1.15 "Segoe UI", Arial, sans-serif; font-variant-numeric: tabular-nums; }}
.page {{ width: 210mm; height: 297mm; padding: 5mm 6mm 4mm; overflow: hidden; break-after: page; display: flex; flex-direction: column; gap: 2mm; }}
.page:last-child {{ break-after: auto; }}
.row {{ display: flex; gap: 4mm; align-items: flex-start; }}
.row > div {{ flex: 1; min-width: 0; }}
h1 {{ font-size: 10pt; margin: 0; color: var(--c1d); }}
h1 span {{ font-size: 7pt; font-weight: 500; color: var(--mute); margin-left: 2mm; }}
h2 {{ font-size: 7.8pt; margin: 0 0 .6mm; padding: .3mm 1.2mm; background: var(--c1d); color: #fff; border-radius: .6mm; }}
h2 span {{ font-weight: 400; }}
table {{ width: 100%; border-collapse: collapse; }}
td, th {{ padding: .05mm .5mm; text-align: right; border-bottom: .12mm solid #e3e7ec; white-space: nowrap; }}
th {{ background: var(--th); font-weight: 600; }}
td:first-child, th:first-child {{ text-align: left; font-weight: 600; background: var(--th); }}
tr:nth-child(5n+1) td {{ border-bottom: .2mm solid #9aa5b1; }}
.ks tr:nth-child(3n+1) td {{ background: var(--th); }}
.ks tr:nth-child(5n+1) td {{ border-bottom: .12mm solid #e3e7ec; }}
.ft td, .ft th {{ padding: .05mm .35mm; }}
p {{ margin: .4mm 0 0; color: var(--mute); }}
@media screen {{
  html {{ background: #dde2e8; }}
  .page {{ margin: 6mm auto; background: #fff; box-shadow: 0 1mm 4mm rgba(0,0,0,.2); }}
  @media (max-width: 800px) {{
    .page {{ width: auto; height: auto; margin: 0; padding: 12px; overflow: visible; box-shadow: none; }}
    .row {{ flex-direction: column; }}
    .row > div {{ width: 100%; overflow-x: auto; }}
  }}
}}
</style>
</head>
<body>
<div class="page">
<h1>PSO – statistické tabulky <span>kvantil x<sub>p</sub>: p(X &lt; x<sub>p</sub>) = p · oboustranně α → p = 1 − α/2 · jednostranně → p = 1 − α</span></h1>
<div class="row">
<div><h2>Φ(u) = p(U &lt; u), U ~ No(0, 1) <span>· Φ(−u) = 1 − Φ(u) · hodnoty bez „0“</span></h2>
{phi}
<p>Kvantily: u<sub>1−p</sub> = −u<sub>p</sub></p>
{qu}</div>
</div>
<div class="row">
<div><h2>Studentovo t(ν): t<sub>p</sub>(ν)</h2>
{t}</div>
<div style="flex:1.45"><h2>χ²(ν): χ²<sub>p</sub>(ν)</h2>
{chi}
<p>Pro ν &gt; 100: χ²<sub>p</sub>(ν) ≈ ½(u<sub>p</sub> + √(2ν − 1))².</p></div>
</div>
</div>
<div class="page">
<div class="row"><div><h2>F(ν₁, ν₂): F<sub>0,975</sub> <span>· oboustranný F-test s α = 0,05 · ν₁ = stupně volnosti čitatele (větší rozptyl)</span></h2>
{f975}</div></div>
<div class="row"><div><h2>F(ν₁, ν₂): F<sub>0,95</sub> <span>· jednostranný F-test s α = 0,05 · F<sub>α</sub>(ν₁, ν₂) = 1 / F<sub>1−α</sub>(ν₂, ν₁)</span></h2>
{f95}</div></div>
<div class="row"><div><h2>Kolmogorovův–Smirnovův test: D<sub>n</sub>(α) <span>· zamítám, když D = max|F<sub>n</sub> − F<sub>0</sub>| ≥ D<sub>n</sub>(α); n &gt; 40: D<sub>n</sub>(0,05) ≈ 1,36/√n, D<sub>n</sub>(0,01) ≈ 1,63/√n</span></h2>
{ks}</div></div>
</div>
</body>
</html>
"""


def main():
    OUT.write_text(HTML.format(phi=phi(), qu=quant_u(), t=t_tab(), chi=chi_tab(), f975=f_tab(0.975), f95=f_tab(0.95), ks=ks_tab()),
                   encoding="utf-8")
    print("zapsáno", OUT)


if __name__ == "__main__":
    main()
