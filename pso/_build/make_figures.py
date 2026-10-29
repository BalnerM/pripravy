"""Generuje obrázky do pso/figures/.

Spuštění (z kořene repozitáře pripravy):  uv run python pso/_build/make_figures.py
Rozdělení a čísla odpovídají úlohám ze sad cvičení (S1/9, S2/1, S3, S4/4 …); simulace mají pevný random seed.
Grafy dodržují paletu a pravidla skillu dataviz: pevné pořadí barev C1 → C2 → C3, tvar značky jako druhé
rozlišení, popisky os, žádná dvojí osa y. Desetinná čárka na osách (česká skripta).
"""
from pathlib import Path
import logging
import warnings

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats

warnings.filterwarnings("ignore")
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

# ---- paleta (referenční paleta skillu dataviz, světlý povrch; obrázky se v tmavém režimu zobrazují na světlé kartě) ----
SURF = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
CAT = [C1, C2, C3]
MARK = ["o", "s", "^"]

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 10,
    "text.color": INK, "axes.labelcolor": INK2, "axes.edgecolor": AXIS,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 11,
    "axes.titleweight": "semibold", "axes.titlecolor": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "lines.linewidth": 2,
})
RNG = np.random.default_rng(7)
COMMA = mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−"))


def cz(*axs):
    for ax in axs:
        ax.xaxis.set_major_formatter(COMMA)
        ax.yaxis.set_major_formatter(COMMA)


def num(v, nd=3):
    return f"{v:.{nd}f}".replace(".", ",")


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", dpi=150)
    plt.close(fig)
    print("ok", name)


def bars(ax, x, y, color=C1, width=0.62, label=None, gap=2):
    """Tenké sloupce s mezerou (pravděpodobnostní funkce diskrétní veličiny)."""
    ax.bar(x, y, width=width, color=color, edgecolor=SURF, linewidth=gap, label=label, zorder=3)


# =====================================================================  kapitola 1
def fig01_kostky():
    fig, ax = plt.subplots(figsize=(4.6, 4.3))
    ax.grid(False)
    for i in range(1, 7):
        for j in range(1, 7):
            s = i + j
            fc = {4: C1, 5: C2}.get(s, SURF)
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=fc, edgecolor=AXIS, linewidth=1,
                                       alpha=0.85 if s in (4, 5) else 1))
            ax.text(j, i, str(s), ha="center", va="center", fontsize=11,
                    color="#ffffff" if s in (4, 5) else INK2, fontweight="semibold" if s in (4, 5) else "normal")
    ax.set_xlim(0.5, 6.5); ax.set_ylim(6.5, 0.5); ax.set_aspect("equal")
    ax.set_xticks(range(1, 7)); ax.set_yticks(range(1, 7))
    ax.set_xlabel("druhá kostka"); ax.set_ylabel("první kostka")
    ax.set_title("36 stejně pravděpodobných dvojic: součet 4 (3×), součet 5 (4×)", fontsize=10)
    save(fig, "fig01_kostky")


def fig01_geom():
    fig, ax = plt.subplots(figsize=(5.2, 5.5))
    x = np.linspace(0.001, 1, 800)
    lo, hi = 0.1, 0.9
    # oblast x + y < 1 a xy < 0,09
    top = np.minimum(1 - x, 0.09 / x)
    top = np.clip(top, 0, 1)
    ax.fill_between(x, 0, top, color=C1, alpha=0.30, linewidth=0, label="hledaná oblast A (plocha ≈ 0,298)")
    xm = np.linspace(lo, hi, 400)
    ax.fill_between(xm, 0.09 / xm, 1 - xm, color=C2, alpha=0.30, linewidth=0, label="odečtený kus mezi křivkami (≈ 0,202)")
    ax.plot(x, 1 - x, color=INK2, lw=1.6)
    xx = np.linspace(0.09, 1, 400)
    ax.plot(xx, 0.09 / xx, color=INK2, lw=1.6, ls="--")
    ax.text(0.62, 0.42, "x + y = 1", color=INK2, fontsize=9.5, rotation=-40)
    ax.text(0.55, 0.11, "xy = 0,09", color=INK2, fontsize=9.5)
    for p in (lo, hi):
        ax.plot(p, 1 - p, "o", color=INK, ms=5, zorder=5)
    ax.annotate("průsečík x = 0,1", (0.1, 0.9), xytext=(0.15, 0.86), fontsize=9, color=INK2)
    ax.annotate("průsečík x = 0,9", (0.9, 0.1), xytext=(0.66, 0.24), fontsize=9, color=INK2)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect("equal")
    ax.set_xlabel("první číslo x"); ax.set_ylabel("druhé číslo y")
    ax.legend(loc="upper center", fontsize=8.5, bbox_to_anchor=(0.5, -0.13))
    cz(ax)
    save(fig, "fig01_geom")


def fig01_kvadraticka():
    """Analogie k HW1/4: x² + 2px + q = 0 má reálné kořeny, když q ≤ p² (čtverec |p| ≤ 1, |q| ≤ 1)."""
    fig, ax = plt.subplots(figsize=(4.8, 4.6))
    pp = np.linspace(-1, 1, 400)
    ax.fill_between(pp, -1, pp ** 2, color=C1, alpha=0.3, linewidth=0, label="q ≤ p²: kořeny reálné (plocha 8/3)")
    ax.fill_between(pp, pp ** 2, 1, color=C2, alpha=0.18, linewidth=0, label="q > p²: kořeny komplexní")
    ax.plot(pp, pp ** 2, color=INK2, lw=1.6)
    ax.text(0.05, 0.08, "q = p²", fontsize=9.5, color=INK2)
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_aspect("equal")
    ax.set_xlabel("koeficient p"); ax.set_ylabel("koeficient q")
    ax.legend(loc="upper center", fontsize=8.5, bbox_to_anchor=(0.5, -0.14))
    cz(ax)
    save(fig, "fig01_kvadraticka")


# =====================================================================  kapitola 3
def fig03_pmf_cdf():
    xi = np.array([1, 2, 3, 4]); pi = np.array([0.4, 0.3, 0.2, 0.1])
    fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.3))
    bars(a, xi, pi)
    for x_, p_ in zip(xi, pi):
        a.text(x_, p_ + 0.012, num(p_, 1), ha="center", fontsize=9.5, color=INK2)
    a.set_xticks(xi); a.set_ylim(0, 0.48)
    a.set_xlabel("počet tahů x"); a.set_ylabel("p(X = x)"); a.set_title("pravděpodobnostní funkce")
    F = np.concatenate([[0], np.cumsum(pi)])
    edges = [-0.5, 1, 2, 3, 4, 5.5]
    for k in range(5):
        b.plot([edges[k], edges[k + 1]], [F[k], F[k]], color=C1, lw=2.2, solid_capstyle="butt")
    for k, x_ in enumerate(xi):
        b.plot(x_, F[k], "o", color=C1, ms=7, zorder=4)                       # F(x) = p(X < x): hodnota vlevo
        b.plot(x_, F[k + 1], "o", mfc=SURF, mec=C1, mew=1.6, ms=7, zorder=4)  # skok nahoru až za bodem
        b.text(x_ + 0.08, (F[k] + F[k + 1]) / 2, f"skok {num(pi[k], 1)}", fontsize=8.5, color=INK2, va="center")
    b.set_xticks(xi); b.set_ylim(-0.05, 1.08); b.set_xlim(-0.5, 5.5)
    b.set_xlabel("x"); b.set_ylabel("F(x) = p(X < x)"); b.set_title("distribuční funkce (spojitá zleva)")
    cz(a, b)
    save(fig, "fig03_pmf_cdf")


def fig03_ex_dx():
    xi = np.arange(7); pi = np.array([0.4, 0.35, 0.15, 0.05, 0.03, 0.01, 0.01])
    ex = xi @ pi; sd = np.sqrt(xi ** 2 @ pi - ex ** 2)
    fig, ax = plt.subplots(figsize=(7, 3.2))
    bars(ax, xi, pi)
    ax.axvline(ex, color=C2, lw=2, zorder=4)
    ax.text(ex + 0.08, 0.41, f"EX = {num(ex, 2)}", color=INK, fontsize=9.5)
    ax.annotate("", xy=(ex + sd, 0.30), xytext=(ex - sd, 0.30), arrowprops=dict(arrowstyle="<->", color=INK2, lw=1.3))
    ax.text(ex + sd + 0.1, 0.295, f"±σ = ±{num(sd, 2)}", color=INK2, fontsize=9)
    ax.set_xticks(xi); ax.set_ylim(0, 0.45)
    ax.set_xlabel("počet dní přípravy x"); ax.set_ylabel("p(X = x)")
    ax.set_title("Střední hodnota = těžiště sloupců, σ = typická vzdálenost od těžiště", fontsize=10)
    cz(ax)
    save(fig, "fig03_ex_dx")


# =====================================================================  kapitola 4
def fig04_rozdeleni():
    fig, axs = plt.subplots(2, 2, figsize=(9.4, 5.8))
    k = np.arange(7)
    bars(axs[0, 0], k, stats.binom.pmf(k, 6, 0.85)); axs[0, 0].set_title("binomické Bi(6; 0,85): kolik úspěchů z 6")
    axs[0, 0].set_xticks(k)
    k = np.arange(1, 21)
    bars(axs[0, 1], k, (5 / 6) ** (k - 1) / 6, width=0.7); axs[0, 1].set_title("geometrické: na kolikátý hod padne šestka")
    axs[0, 1].set_xticks([1, 5, 10, 15, 20])
    k = np.arange(11)
    bars(axs[1, 0], k, stats.hypergeom.pmf(k, 100, 20, 10)); axs[1, 0].set_title("hypergeometrické H(100, 20, 10): zmetky ve výběru")
    axs[1, 0].set_xticks(k)
    k = np.arange(21)
    bars(axs[1, 1], k, stats.poisson.pmf(k, 8), width=0.7); axs[1, 1].set_title("Poissonovo Po(8): počet požadavků za hodinu")
    axs[1, 1].set_xticks([0, 4, 8, 12, 16, 20])
    for ax in axs.flat:
        ax.set_xlabel("hodnota k"); ax.set_ylabel("p(X = k)")
    cz(*axs.flat)
    save(fig, "fig04_rozdeleni")


def fig04_bi_po():
    k = np.arange(0, 21)
    fig, ax = plt.subplots(figsize=(7.4, 3.3))
    ax.vlines(k - 0.12, 0, stats.binom.pmf(k, 800, 0.01), color=C1, lw=2)
    ax.plot(k - 0.12, stats.binom.pmf(k, 800, 0.01), "o", color=C1, ms=6, label="binomické Bi(800; 0,01) – přesně")
    ax.vlines(k + 0.12, 0, stats.poisson.pmf(k, 8), color=C2, lw=2)
    ax.plot(k + 0.12, stats.poisson.pmf(k, 8), "s", color=C2, ms=6, label="Poissonovo Po(λ = np = 8) – aproximace")
    ax.set_xlabel("počet počítačů, které poslaly požadavek"); ax.set_ylabel("pravděpodobnost")
    ax.set_xticks(range(0, 21, 2)); ax.legend(fontsize=9)
    cz(ax)
    save(fig, "fig04_bi_po")


# =====================================================================  kapitola 5
def fig05_hustota():
    a = 2 / 9
    x = np.linspace(-0.6, 3.6, 600)
    f = np.where((x >= 0) & (x <= 3), a * (3 * x - x * x), 0)
    F = np.where(x < 0, 0, np.where(x > 3, 1, x ** 2 / 3 - 2 * x ** 3 / 27))
    fig, (p, q) = plt.subplots(1, 2, figsize=(9.2, 3.3))
    p.plot(x, f, color=C1)
    m = (x >= 1) & (x <= 2)
    p.fill_between(x[m], 0, f[m], color=C1, alpha=0.3, linewidth=0)
    p.text(1.5, 0.12, "plocha = p(1 < X < 2)\n= 13/27 ≈ 0,481", ha="center", fontsize=9, color=INK,
           bbox=dict(boxstyle="round,pad=0.3", fc=SURF, ec=AXIS, lw=0.8), zorder=5)
    p.axvline(1.5, color=C2, lw=1.6, ls="--"); p.text(1.55, 0.53, "EX = 1,5", fontsize=9, color=INK2)
    p.set_ylim(0, 0.6); p.set_xlabel("x"); p.set_ylabel("f(x)"); p.set_title("hustota f(x) = (2/9)(3x − x²)")
    q.plot(x, F, color=C1)
    for xv in (1, 2):
        Fv = xv ** 2 / 3 - 2 * xv ** 3 / 27
        q.plot([xv, xv], [0, Fv], color=MUTED, lw=1, ls=":"); q.plot(xv, Fv, "o", color=C1, ms=6)
    q.annotate("", xy=(2.25, 20 / 27), xytext=(2.25, 7 / 27), arrowprops=dict(arrowstyle="<->", color=C2, lw=1.4))
    q.text(2.33, 0.48, "F(2) − F(1)\n= 13/27", fontsize=9, color=INK2)
    q.set_ylim(-0.03, 1.08); q.set_xlabel("x"); q.set_ylabel("F(x)"); q.set_title("distribuční funkce F(x) = ∫ f")
    cz(p, q)
    save(fig, "fig05_hustota")


def fig05_laplace():
    x = np.linspace(-4, 4, 600)
    fig, (p, q) = plt.subplots(1, 2, figsize=(9.2, 3.2))
    for i, lam in enumerate((1, 2)):
        p.plot(x, lam / 2 * np.exp(-lam * np.abs(x)), color=CAT[i], label=f"λ = {lam}")
        F = np.where(x <= 0, 0.5 * np.exp(lam * x), 1 - 0.5 * np.exp(-lam * x))
        q.plot(x, F, color=CAT[i], label=f"λ = {lam}")
    p.set_title("hustota f(x) = (λ/2)·e^(−λ|x|)"); p.set_xlabel("x"); p.set_ylabel("f(x)")
    q.set_title("distribuční funkce F(x)"); q.set_xlabel("x"); q.set_ylabel("F(x)")
    p.text(1.0, 0.75, "λ = 2", color=INK, fontsize=9); p.text(1.6, 0.17, "λ = 1", color=INK, fontsize=9)
    p.legend(fontsize=9, loc="upper left"); q.legend(fontsize=9, loc="upper left")
    cz(p, q)
    save(fig, "fig05_laplace")


# =====================================================================  kapitola 6
def _std_normal(ax, lo, hi, txt, color=C1):
    x = np.linspace(-3.6, 3.6, 700); y = stats.norm.pdf(x)
    ax.plot(x, y, color=INK2, lw=1.6)
    m = (x >= lo) & (x <= hi)
    ax.fill_between(x[m], 0, y[m], color=color, alpha=0.35, linewidth=0)
    ax.set_ylim(0, 0.46); ax.set_yticks([]); ax.set_xlabel("u")
    ax.set_title(txt, fontsize=10)


def fig06_plochy():
    fig, axs = plt.subplots(1, 3, figsize=(10, 2.9))
    _std_normal(axs[0], -9, 1.67, "p(U < 1,67) = Φ(1,67) ≈ 0,953")
    _std_normal(axs[1], 0.35, 9, "p(U > 0,35) = 1 − Φ(0,35) ≈ 0,363")
    _std_normal(axs[2], -1.5, 0.5, "p(−1,5 < U < 0,5) = Φ(0,5) − Φ(−1,5)")
    for ax, v in zip(axs, (1.67, 0.35, None)):
        if v is not None:
            ax.axvline(v, color=C1, lw=1.2)
    axs[2].axvline(-1.5, color=C1, lw=1.2); axs[2].axvline(0.5, color=C1, lw=1.2)
    cz(*axs)
    save(fig, "fig06_plochy")


def fig06_symetrie():
    fig, ax = plt.subplots(figsize=(7, 3))
    x = np.linspace(-3.6, 3.6, 700); y = stats.norm.pdf(x)
    ax.plot(x, y, color=INK2, lw=1.6)
    ax.fill_between(x[x <= -1], 0, y[x <= -1], color=C1, alpha=0.4, linewidth=0, label="Φ(−u): plocha vlevo od −u")
    ax.fill_between(x[x >= 1], 0, y[x >= 1], color=C2, alpha=0.4, linewidth=0, label="1 − Φ(u): plocha vpravo od u")
    ax.set_xticks([-3, -2, -1, 0, 1, 2, 3]); ax.set_xticklabels(["−3", "−2", "−u", "0", "u", "2", "3"])
    ax.set_yticks([]); ax.set_ylim(0, 0.46); ax.set_xlabel("u")
    ax.set_title("Symetrie: obě plochy jsou stejné, proto Φ(−u) = 1 − Φ(u)", fontsize=10)
    ax.legend(fontsize=9, loc="upper right")
    save(fig, "fig06_symetrie")


def fig06_kvantily():
    fig, axs = plt.subplots(1, 2, figsize=(9.4, 3))
    u = stats.norm.ppf(0.95)
    _std_normal(axs[0], u, 9, "jednostranně: p(U > u) = 0,05  →  u = 1,645", color=C2)
    axs[0].axvline(u, color=C2, lw=1.2); axs[0].text(u + 0.1, 0.3, "u₀,₉₅ ≈ 1,645", fontsize=9, color=INK2)
    _std_normal(axs[1], -u, u, "oboustranně: p(−u < U < u) = 0,9  →  u = 1,645")
    for v in (-u, u):
        axs[1].axvline(v, color=C1, lw=1.2)
    axs[1].text(0, 0.15, "0,9", ha="center", fontsize=10, color=INK)
    axs[1].text(-3.3, 0.05, "0,05", fontsize=9, color=INK2); axs[1].text(2.5, 0.05, "0,05", fontsize=9, color=INK2)
    cz(*axs)
    save(fig, "fig06_kvantily")


def fig06_sigma():
    fig, ax = plt.subplots(figsize=(7.4, 3.1))
    x = np.linspace(-4, 4, 800); y = stats.norm.pdf(x)
    ax.plot(x, y, color=INK2, lw=1.6)
    for k, (c, a) in zip((3, 2, 1), ((C1, 0.12), (C1, 0.22), (C1, 0.36))):
        m = np.abs(x) <= k
        ax.fill_between(x[m], 0, y[m], color=c, alpha=a, linewidth=0)
    for k, pct, h in ((1, "68,3 %", 0.27), (2, "95,4 %", 0.17), (3, "99,7 %", 0.07)):
        ax.annotate("", xy=(k, h), xytext=(-k, h), arrowprops=dict(arrowstyle="<->", color=INK, lw=1))
        ax.text(0, h + 0.012, pct, ha="center", fontsize=9, color=INK)
    ax.set_xticks([-3, -2, -1, 0, 1, 2, 3])
    ax.set_xticklabels(["μ−3σ", "μ−2σ", "μ−σ", "μ", "μ+σ", "μ+2σ", "μ+3σ"])
    ax.set_yticks([]); ax.set_ylim(0, 0.44)
    ax.set_title("Kolik hodnot leží do 1σ, 2σ a 3σ od střední hodnoty", fontsize=10)
    save(fig, "fig06_sigma")


# =====================================================================  kapitola 7
def fig07_moivre():
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.3))
    for ax, n in zip(axs, (10, 400)):
        p = 0.515; mu = n * p; sd = np.sqrt(n * p * (1 - p))
        k = np.arange(0, n + 1)
        m = np.abs(k - mu) <= 4.2 * sd
        bars(ax, k[m], stats.binom.pmf(k[m], n, p), width=0.8 if n == 10 else 1.0, label="binomické (přesně)", gap=2 if n == 10 else 0.3)
        x = np.linspace(k[m].min() - 1, k[m].max() + 1, 500)
        ax.plot(x, stats.norm.pdf(x, mu, sd), color=C2, lw=2, label="normální No(np, √(np(1−p)))")
        ax.set_title(f"n = {n}: np(1−p) = {num(n * p * (1 - p), 1)}" + (" < 9 → hrubé" if n == 10 else " > 9 → sedí"))
        ax.set_xlabel("počet chlapců"); ax.set_ylabel("pravděpodobnost")
    axs[0].legend(fontsize=8.5, loc="upper left")
    cz(*axs)
    save(fig, "fig07_moivre")


def fig07_clt():
    """Součet n hodů kostkou: z rovnoměrného rozdělení se rychle stane zvonovitá křivka."""
    fig, axs = plt.subplots(1, 3, figsize=(10, 2.9))
    one = np.ones(6) / 6
    dist = one.copy()
    for ax, n in zip(axs, (1, 2, 5)):
        dist = one.copy()
        for _ in range(n - 1):
            dist = np.convolve(dist, one)
        s = np.arange(n, 6 * n + 1)
        bars(ax, s, dist, width=0.8)
        if n > 1:
            mu, sd = 3.5 * n, np.sqrt(n * 35 / 12)
            x = np.linspace(s.min(), s.max(), 300)
            ax.plot(x, stats.norm.pdf(x, mu, sd), color=C2, lw=2)
        ax.set_title(f"součet {n} {'kostky' if n == 1 else 'kostek'}"); ax.set_xlabel("součet"); ax.set_yticks([])
    cz(*axs)
    save(fig, "fig07_clt")


# =====================================================================  kapitola 8
def fig08_oblast():
    fig, axs = plt.subplots(1, 2, figsize=(9, 4))
    g = np.linspace(0, 1, 200); X, Y = np.meshgrid(g, g)
    for ax in axs:
        im = ax.imshow(4 * X * (1 - Y), origin="lower", extent=(0, 1, 0, 1), cmap="Blues", vmin=0, vmax=5, alpha=0.9)
        ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_aspect("equal"); ax.grid(False)
    axs[0].add_patch(plt.Rectangle((0.5, 0.5), 0.25, 0.5, fill=False, edgecolor=C2, lw=2.4))
    axs[0].text(0.52, 0.42, "½ < x < ¾, y > ½", color=INK, fontsize=9)
    axs[0].set_title("(b) obdélník: meze jsou čísla")
    axs[1].fill_between([0, 1], [0, 0], [0, 1], facecolor="none", edgecolor=C2, hatch="///", linewidth=0)
    axs[1].plot([0, 1], [0, 1], color=C2, lw=2)
    axs[1].text(0.55, 0.2, "y ≤ x", color=INK, fontsize=10)
    axs[1].annotate("", xy=(0.7, 0.7), xytext=(0.7, 0.0), arrowprops=dict(arrowstyle="->", color=INK, lw=1.3))
    axs[1].text(0.72, 0.33, "pro dané x:\ny od 0 do x", fontsize=8.5, color=INK)
    axs[1].set_title("(d) trojúhelník: vnitřní mez závisí na x")
    cz(*axs)
    fig.colorbar(im, ax=axs, shrink=0.8, label="hustota f(x, y) = 4x(1 − y)")
    fig.savefig(OUT / "fig08_oblast.png", dpi=150, bbox_inches="tight"); plt.close(fig); print("ok fig08_oblast")


# =====================================================================  kapitola 9
def fig09_t():
    x = np.linspace(-4.5, 4.5, 600)
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    ax.plot(x, stats.norm.pdf(x), color=INK2, lw=1.6, ls="--", label="normované normální No(0, 1)")
    ax.plot(x, stats.t.pdf(x, 2), color=C1, label="t s ν = 2")
    ax.plot(x, stats.t.pdf(x, 9), color=C2, label="t s ν = 9")
    ax.set_xlabel("t"); ax.set_ylabel("hustota"); ax.legend(fontsize=9)
    ax.set_title("t-rozdělení má těžší konce; s rostoucím ν se blíží normálnímu", fontsize=10)
    cz(ax)
    save(fig, "fig09_t")


def fig09_intervaly():
    rng = np.random.default_rng(11)
    mu, sd, n, m = 10, 4, 10, 25
    t = stats.t.ppf(0.975, n - 1)
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    miss = 0
    for i in range(m):
        s = rng.normal(mu, sd, n); c, h = s.mean(), t * s.std(ddof=1) / np.sqrt(n)
        ok = c - h <= mu <= c + h
        miss += not ok
        col, mk = (C1, "o") if ok else (C2, "s")
        ax.plot([c - h, c + h], [i, i], color=col, lw=2)
        ax.plot(c, i, mk, color=col, ms=6)
    ax.axvline(mu, color=INK, lw=1.4)
    ax.text(mu + 0.15, m - 0.2, "skutečné μ = 10", fontsize=9, color=INK)
    ax.plot([], [], "o-", color=C1, label="interval μ pokryl")
    ax.plot([], [], "s-", color=C2, label="interval μ minul")
    ax.set_yticks([]); ax.set_xlabel("hodnota"); ax.set_ylabel(f"{m} různých výběrů (n = {n})")
    ax.legend(fontsize=9, loc="lower right")
    ax.set_title(f"95% intervaly z {m} výběrů: minulo jich {miss} (čekáme ≈ 5 %)", fontsize=10)
    cz(ax)
    save(fig, "fig09_intervaly")


def fig09_chi2():
    nu = 8
    x = np.linspace(0, 26, 600); y = stats.chi2.pdf(x, nu)
    lo, hi = stats.chi2.ppf(0.025, nu), stats.chi2.ppf(0.975, nu)
    fig, ax = plt.subplots(figsize=(7.4, 3.1))
    ax.plot(x, y, color=C1)
    ax.fill_between(x[x <= lo], 0, y[x <= lo], color=C2, alpha=0.4, linewidth=0)
    ax.fill_between(x[x >= hi], 0, y[x >= hi], color=C2, alpha=0.4, linewidth=0)
    ax.text(lo, 0.02, f"  χ²₀,₀₂₅ = {num(lo, 2)}", fontsize=9, color=INK)
    ax.text(hi, 0.02, f"  χ²₀,₉₇₅ = {num(hi, 2)}", fontsize=9, color=INK)
    ax.text(8, 0.06, "0,95", fontsize=10, ha="center", color=INK)
    ax.set_xlabel("x"); ax.set_ylabel("hustota")
    ax.set_title("χ² s ν = 8: nesymetrické, proto dva různé kvantily", fontsize=10)
    cz(ax)
    save(fig, "fig09_chi2")


# =====================================================================  kapitola 10
def fig10_obor():
    """Úloha S7/5 (maso): levostranný test H1: μ < 100, kritický obor t < −t_0,95(9)."""
    nu = 9; tk = stats.t.ppf(0.95, nu); tobs = -5.65
    x = np.linspace(-6.5, 4.5, 700); y = stats.t.pdf(x, nu)
    fig, ax = plt.subplots(figsize=(7.8, 3.2))
    ax.plot(x, y, color=INK2, lw=1.6)
    ax.fill_between(x[x <= -tk], 0, y[x <= -tk], color=C2, alpha=0.45, linewidth=0, label="kritický obor (plocha α = 0,05)")
    ax.fill_between(x[x > -tk], 0, y[x > -tk], color=C1, alpha=0.18, linewidth=0, label="H₀ nezamítáme")
    ax.axvline(-tk, color=C2, lw=1.2)
    ax.text(-tk + 0.1, 0.3, f"$-t_k$ = −{num(tk, 3)}", fontsize=9, color=INK2)
    ax.plot(tobs, 0.012, "v", color=INK, ms=9)
    ax.text(tobs, 0.05, "naměřené\nt = −5,65", ha="center", fontsize=9, color=INK)
    ax.set_xlabel("hodnota testového kritéria t"); ax.set_yticks([]); ax.set_ylim(0, 0.44)
    ax.legend(fontsize=9, loc="upper right")
    ax.set_title("Levostranný t-test, α = 0,05, ν = 9 (úloha s masem)", fontsize=10)
    cz(ax)
    save(fig, "fig10_obor")


def fig10_chyby():
    x = np.linspace(-4, 7, 700)
    fig, ax = plt.subplots(figsize=(7.8, 3.1))
    c = stats.norm.ppf(0.95)
    y0, y1 = stats.norm.pdf(x), stats.norm.pdf(x, 2.5)
    ax.plot(x, y0, color=C1, label="rozdělení kritéria, když platí H₀")
    ax.plot(x, y1, color=C2, ls="--", label="rozdělení kritéria, když platí H₁")
    ax.fill_between(x[x >= c], 0, y0[x >= c], color=C1, alpha=0.35, linewidth=0)
    ax.fill_between(x[x < c], 0, y1[x < c], color=C2, alpha=0.25, linewidth=0)
    ax.axvline(c, color=INK, lw=1.2)
    ax.text(c + 0.1, 0.42, "kritická hodnota", fontsize=9, color=INK)
    ax.text(2.0, 0.025, "α", fontsize=12, color=INK)
    ax.text(1.0, 0.1, "β", fontsize=12, color=INK)
    ax.set_yticks([]); ax.set_ylim(0, 0.48); ax.set_xlabel("hodnota testového kritéria")
    ax.legend(fontsize=8.5, loc="upper left")
    ax.set_title("α = chyba 1. druhu (zamítnu platnou H₀), β = chyba 2. druhu (nezamítnu neplatnou H₀)", fontsize=9.5)
    cz(ax)
    save(fig, "fig10_chyby")


FIGS = [fig01_kostky, fig01_geom, fig01_kvadraticka, fig03_pmf_cdf, fig03_ex_dx, fig04_rozdeleni, fig04_bi_po, fig05_hustota,
        fig05_laplace, fig06_plochy, fig06_symetrie, fig06_kvantily, fig06_sigma, fig07_moivre, fig07_clt,
        fig08_oblast, fig09_t, fig09_intervaly, fig09_chi2, fig10_obor, fig10_chyby]

if __name__ == "__main__":
    import sys
    only = sys.argv[1:]
    for f in FIGS:
        if not only or f.__name__ in only:
            f()
