"""Generuje obrázky do vmm/figures/.

Spuštění (z kořene repozitáře pripravy):  uv run python vmm/_build/make_figures.py
Všechna data jsou syntetická (pevný random seed) nebo dataset spotřeby proteinů z přednášky 6.
"""
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy import stats
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.datasets import make_blobs, make_moons, make_circles, make_swiss_roll
from sklearn.decomposition import PCA, KernelPCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
import logging
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

# ---- paleta (referenční paleta skillu dataviz, světlý povrch) ----
SURF = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
CAT = [C1, C2, C3]
MARK = ["o", "s", "^"]
SEQ = matplotlib.colors.LinearSegmentedColormap.from_list(
    "modra", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"])

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


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", dpi=150)
    plt.close(fig)
    print("ok", name)


def scatter_groups(ax, X, y, labels=None, s=22, alpha=0.85):
    for k in np.unique(y):
        m = y == k
        if k < 0:  # šum (DBSCAN)
            ax.scatter(X[m, 0], X[m, 1], s=s * 0.8, c=MUTED, marker="x", lw=1, label="šum")
            continue
        ax.scatter(X[m, 0], X[m, 1], s=s, c=CAT[k % 3], marker=MARK[k % 3], alpha=alpha,
                   edgecolors=SURF, linewidths=0.6,
                   label=labels[k] if labels else f"shluk {k + 1}")


def ellipse95(ax, X, color=INK2):
    mu = X.mean(0)
    S = np.cov(X.T)
    w, v = np.linalg.eigh(S)
    ang = np.degrees(np.arctan2(v[1, 1], v[0, 1]))
    c = np.sqrt(stats.chi2.ppf(0.95, 2))
    ax.add_patch(Ellipse(mu, 2 * c * np.sqrt(w[1]), 2 * c * np.sqrt(w[0]), angle=ang,
                         fill=False, ec=color, lw=1.5, ls="--"))


# =====================================================================  přednáška 2
def fig02_korelace():
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.3))
    for ax, r, txt in zip(axs, [0, -0.29, 0.56, 0.8],
                          ["nezávislé", "slabá záporná", "středně silná", "velmi silná"]):
        X = RNG.multivariate_normal([0, 0], [[1, r], [r, 1]], 300)
        ax.scatter(X[:, 0], X[:, 1], s=10, c=C1, alpha=0.6, edgecolors="none")
        ellipse95(ax, X)
        ax.set_title(f"{txt}: r = {np.corrcoef(X.T)[0, 1]:.2f}")
        ax.set_xlim(-4, 4); ax.set_ylim(-4, 4); ax.set_aspect("equal")
        ax.set_xlabel("x₁"); ax.set_ylabel("x₂")
    save(fig, "fig02_korelace")


def fig02_chi2():
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    n = 60
    X1 = RNG.multivariate_normal([0, 0], [[1, .6], [.6, 1]], n)
    X2 = X1.copy()
    X2[:, 0] = np.exp(X2[:, 0] * 0.8)  # zešikmení
    X2[:4] = [[6, -2], [5.5, 2.8], [-1, 3.3], [7, 0]]  # odlehlé hodnoty
    for ax, X, t in zip(axs, [X1, X2], ["data z normálního rozdělení",
                                         "šikmá proměnná + odlehlé hodnoty"]):
        mu, Si = X.mean(0), np.linalg.inv(np.cov(X.T))
        d2 = np.sort(np.einsum("ij,jk,ik->i", X - mu, Si, X - mu))
        q = stats.chi2.ppf((np.arange(1, n + 1) - 0.5) / n, 2)
        ax.plot([0, 14], [0, 14], color=AXIS, lw=1.5, zorder=1)
        ax.scatter(q, d2, s=22, c=C1 if X is X1 else C2, edgecolors=SURF, zorder=2)
        ax.set_title(t)
        ax.set_xlabel("teoretický kvantil χ²(2)")
        ax.set_ylabel("Mahalanobisova vzdálenost D² (seřazená)")
        ax.set_xlim(0, 14); ax.set_ylim(0, max(14, d2.max() + 1))
    save(fig, "fig02_chi2")


def fig02_hotelling():
    n = 30
    S = [[1, .95], [.95, 1]]
    for seed in range(200):  # hledá seed, kde jednotlivé t-testy nic neukážou (p > 0,2), jinak zůstane poslední pokus
        rng = np.random.default_rng(seed)
        A = rng.multivariate_normal([0, 0], S, n)
        B = rng.multivariate_normal([0.45, -0.45], S, n)
        pa = stats.ttest_ind(A[:, 0], B[:, 0]).pvalue
        pb = stats.ttest_ind(A[:, 1], B[:, 1]).pvalue
        if min(pa, pb) > 0.2: break
    d = A.mean(0) - B.mean(0)
    Sp = ((n - 1) * np.cov(A.T) + (n - 1) * np.cov(B.T)) / (2 * n - 2)
    T2 = n * n / (2 * n) * d @ np.linalg.inv(Sp) @ d
    p, N = 2, 2 * n
    F = (N - p - 1) / (p * (N - 2)) * T2
    pT = 1 - stats.f.cdf(F, p, N - p - 1)
    fig = plt.figure(figsize=(10, 4.2))
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1.4])
    for i, (col, pv) in enumerate([(0, pa), (1, pb)]):
        ax = fig.add_subplot(gs[i, 0:2])
        bins = np.linspace(-3.5, 3.5, 25)
        ax.hist(A[:, col], bins, color=C1, alpha=.6, label="skupina A")
        ax.hist(B[:, col], bins, color=C2, alpha=.6, label="skupina B")
        ax.set_title(f"jen proměnná x{col + 1}: t-test p = {pv:.2f}", fontsize=10)
        ax.set_yticks([])
        if i == 0:
            ax.legend(loc="upper left")
    ax = fig.add_subplot(gs[:, 2])
    scatter_groups(ax, np.vstack([A, B]), np.r_[np.zeros(n, int), np.ones(n, int)],
                   ["skupina A", "skupina B"])
    ax.set_title("obě proměnné najednou: Hotelling T² " + (f"p = {pT:.3f}" if pT >= 0.001 else "p < 0,001"), fontsize=10)
    ax.set_xlabel("x₁"); ax.set_ylabel("x₂"); ax.set_aspect("equal"); ax.legend(loc="upper left")
    save(fig, "fig02_hotelling")


def fig02_vyznamnost():
    n = 2000
    a = RNG.normal(0, 1, n)
    b = RNG.normal(0.2, 1, n)
    p = stats.ttest_ind(a, b).pvalue
    fig, ax = plt.subplots(figsize=(8, 3.4))
    bins = np.linspace(-4, 4, 50)
    ax.hist(a, bins, color=C1, alpha=.55, label="skupina A (n = 2000)")
    ax.hist(b, bins, color=C2, alpha=.55, label="skupina B (n = 2000)")
    ax.axvline(a.mean(), color=C1, lw=2); ax.axvline(b.mean(), color=C2, lw=2)
    ax.set_title(f"t-test: p = {p:.1e} → „statisticky významné“, ale skupiny se téměř úplně překrývají")
    ax.set_xlabel("měřená veličina"); ax.set_yticks([]); ax.legend(loc="upper left")
    save(fig, "fig02_vyznamnost")


# =====================================================================  přednáška 3
def fig03_skalovani():
    n = 60
    vek = RNG.uniform(20, 90, n)
    bmi = RNG.normal(26, 4, n)
    bmi[0], vek[0] = 94.75, 45  # chyba v datech (307 kg / 1.8 m²) jako v přednášce
    X = np.c_[vek, bmi]
    Z = (X - X.mean(0)) / X.std(0, ddof=1)
    N = (X - X.min(0)) / (X.max(0) - X.min(0))
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.6))
    for ax, D, t, xl in zip(axs, [X, Z, N],
                            ["původní data", "standardizace (z-skóre)", "normalizace min–max na 0–1"],
                            ["věk [roky]", "věk (z)", "věk (0–1)"]):
        ax.scatter(D[1:, 0], D[1:, 1], s=18, c=C1, edgecolors=SURF)
        ax.scatter(D[0, 0], D[0, 1], s=50, c=C2, marker="s", edgecolors=SURF, label="chybná hodnota BMI = 94,75")
        ax.set_title(t); ax.set_xlabel(xl); ax.set_ylabel(xl.replace("věk", "BMI").replace("[roky]", "[kg/m²]"))
    axs[0].legend(loc="upper right")
    axs[2].annotate("ostatní body jsou\nstlačené do úzkého pásu", xy=(0.5, 0.15), xytext=(0.35, 0.55),
                    arrowprops=dict(arrowstyle="->", color=INK2), color=INK2, fontsize=9)
    save(fig, "fig03_skalovani")


def fig03_log():
    x = RNG.lognormal(3, 0.8, 600)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.3))
    axs[0].hist(x, 40, color=C1, edgecolor=SURF)
    axs[0].set_title("původní: silně pravostranně zešikmená"); axs[0].set_xlabel("x (např. koncentrace, čas)")
    axs[1].hist(np.log(x), 40, color=C3, edgecolor=SURF)
    axs[1].set_title("po transformaci log(x): přibližně symetrická"); axs[1].set_xlabel("log(x)")
    for a in axs: a.set_yticks([])
    save(fig, "fig03_log")


# =====================================================================  přednáška 4
def fig04_korelace_tvary():
    n = 80
    x1 = RNG.normal(0, 1, n); y1 = 0.8 * x1 + RNG.normal(0, .5, n)
    x2 = RNG.uniform(-2, 2, n); y2 = x2 ** 2 + RNG.normal(0, .3, n)
    x3 = RNG.normal(0, 1, n); y3 = RNG.normal(0, 1, n); x3[0], y3[0] = 9, 9
    x4 = RNG.uniform(0, 4, n); y4 = np.exp(1.3 * x4) + RNG.normal(0, 3, n)
    fig, axs = plt.subplots(1, 4, figsize=(12.5, 3.3))
    for ax, x, y, t in zip(axs, [x1, x2, x3, x4], [y1, y2, y3, y4],
                           ["lineární vztah", "parabola (nelineární)", "jedna odlehlá hodnota",
                            "monotónní, ale nelineární"]):
        ax.scatter(x, y, s=16, c=C1, edgecolors=SURF)
        r = stats.pearsonr(x, y)[0]; rs = stats.spearmanr(x, y)[0]
        ax.set_title(f"{t}\nPearson r = {r:.2f} | Spearman = {rs:.2f}", fontsize=10)
    save(fig, "fig04_korelace_tvary")


def fig04_regrese():
    x = np.array([1, 2, 3, 4, 5, 6, 7.0])
    y = np.array([1.8, 2.1, 3.9, 3.6, 5.6, 5.2, 7.4])
    b, a = np.polyfit(x, y, 1)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
    xx = np.linspace(0.5, 7.5, 2)
    axs[0].plot(xx, a + b * xx, color=C1)
    for xi, yi in zip(x, y):
        axs[0].plot([xi, xi], [yi, a + b * xi], color=C2, lw=1.5)
    axs[0].set_title("obyčejná (OLS) regrese:\nchyby měříme svisle (jen v y)")
    Xc = np.c_[x, y] - [x.mean(), y.mean()]
    v = np.linalg.svd(Xc)[2][0]
    k = v[1] / v[0]; q = y.mean() - k * x.mean()
    axs[1].plot(xx, q + k * xx, color=C1)
    for xi, yi in zip(x, y):
        t = ((xi - x.mean()) * v[0] + (yi - y.mean()) * v[1])
        px, py = x.mean() + t * v[0], y.mean() + t * v[1]
        axs[1].plot([xi, px], [yi, py], color=C3, lw=1.5)
    axs[1].set_title("ortogonální regrese:\nchyby měříme kolmo k přímce (v x i y)")
    for ax in axs:
        ax.scatter(x, y, s=40, c=INK, zorder=3); ax.set_aspect("equal")
        ax.set_xlabel("x"); ax.set_ylabel("y")
    save(fig, "fig04_regrese")


def fig04_logit():
    x = np.r_[RNG.normal(30, 8, 40), RNG.normal(55, 8, 40)]
    y = np.r_[np.zeros(40), np.ones(40)]
    from sklearn.linear_model import LogisticRegression
    m = LogisticRegression().fit(x[:, None], y)
    xx = np.linspace(5, 85, 200)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.scatter(x, y + RNG.uniform(-.03, .03, 80), s=18, c=np.where(y, C2, C1), edgecolors=SURF)
    ax.plot(xx, m.predict_proba(xx[:, None])[:, 1], color=INK)
    ax.axhline(0.5, color=AXIS, ls="--", lw=1)
    ax.set_xlabel("vysvětlující proměnná x (např. věk)")
    ax.set_ylabel("P(y = 1 | x)")
    ax.set_title("logistická regrese: lineární kombinace „schovaná“ v esovité křivce → pravděpodobnost 0–1")
    save(fig, "fig04_logit")


def fig04_anova():
    n = 50
    sets = [((0, 2.2, 4.4), "znak odděluje všechny skupiny"),
            ((0, 0.3, 2.6), "znak odděluje jen skupinu R"),
            ((0, 0.15, 0.1), "znak neodděluje nic")]
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.4))
    for ax, (mus, t) in zip(axs, sets):
        g = [RNG.normal(m, 1, n) for m in mus]
        F, p = stats.f_oneway(*g)
        for i, gi in enumerate(g):
            ax.scatter(gi, i + RNG.uniform(-.18, .18, n), s=12, c=CAT[i], marker=MARK[i], alpha=.7,
                       edgecolors="none")
            ax.plot([gi.mean()] * 2, [i - .3, i + .3], color=INK, lw=2.5)
        ax.set_yticks([0, 1, 2], ["Sync", "L", "R"])
        ax.set_title(f"{t}\nANOVA: F = {F:.1f}, p = {p:.2g}", fontsize=10)
        ax.set_xlabel("hodnota znaku")
    save(fig, "fig04_anova")


# =====================================================================  přednáška 5
def fig05_vazby():
    Xb, _ = make_blobs(220, centers=[[0, 0], [4, 0], [2, 3.5]], cluster_std=[0.6, 1.2, 0.5],
                       random_state=3)
    Xm, _ = make_circles(300, factor=0.45, noise=0.05, random_state=3)
    fig, axs = plt.subplots(2, 4, figsize=(12.5, 6))
    for r, (X, k) in enumerate([(Xb, 3), (Xm, 2)]):
        X = StandardScaler().fit_transform(X)
        for c, (meth, nm) in enumerate([("single", "nejbližší soused\n(single)"),
                                        ("average", "průměrná vazba\n(average)"),
                                        ("complete", "nejvzdálenější soused\n(complete)"),
                                        ("ward", "Wardova metoda")]):
            lab = AgglomerativeClustering(k, linkage=meth).fit_predict(X)
            scatter_groups(axs[r, c], X, lab, s=14)
            axs[r, c].set_xticks([]); axs[r, c].set_yticks([])
            if r == 0: axs[r, c].set_title(nm, fontsize=10)
    save(fig, "fig05_vazby")


def fig05_dendrogram():
    X, _ = make_blobs(30, centers=[[0, 0], [5, 1], [2, 5]], cluster_std=0.8, random_state=11)
    Z = linkage(X, "ward")
    lab = fcluster(Z, 3, "maxclust") - 1
    order = []
    for leaf in dendrogram(Z, no_plot=True)["leaves"]:
        if lab[leaf] not in order: order.append(lab[leaf])
    lab = np.array([order.index(l) for l in lab])
    from scipy.cluster.hierarchy import set_link_color_palette
    set_link_color_palette(CAT)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={"width_ratios": [1, 1.6]})
    scatter_groups(axs[0], X, lab)
    for i, (a, b) in enumerate(X):
        axs[0].annotate(str(i), (a, b), xytext=(3, 3), textcoords="offset points", fontsize=7, color=INK2)
    axs[0].set_title("data a výsledné 3 shluky"); axs[0].set_aspect("equal")
    cut = (Z[-3, 2] + Z[-2, 2]) / 2
    dendrogram(Z, ax=axs[1], color_threshold=cut, above_threshold_color=MUTED,
               link_color_func=None)
    axs[1].axhline(cut, color=INK2, ls="--", lw=1.5)
    axs[1].text(axs[1].get_xlim()[0] + 5, cut + 0.3, "řez → 3 shluky", color=INK2, va="bottom")
    axs[1].set_title("dendrogram (Wardova metoda)"); axs[1].set_ylabel("vzdálenost při sloučení")
    axs[1].grid(axis="x", visible=False)
    save(fig, "fig05_dendrogram")


def fig05_pocet_k():
    X, _ = make_blobs(400, centers=[[0, 0], [6, 0], [3, 5]], cluster_std=1.0, random_state=5)
    ks = range(1, 9)
    wss, ch, sil = [], [], []
    for k in ks:
        km = KMeans(k, n_init=10, random_state=0).fit(X)
        wss.append(km.inertia_)
        if k > 1:
            ch.append(calinski_harabasz_score(X, km.labels_)); sil.append(silhouette_score(X, km.labels_))
    fig, axs = plt.subplots(1, 4, figsize=(13, 3.2))
    km3 = KMeans(3, n_init=10, random_state=0).fit(X)
    scatter_groups(axs[0], X, km3.labels_, s=10); axs[0].set_title("data (K = 3)")
    axs[1].plot(list(ks), wss, "-o", color=C1); axs[1].set_title("WSS – metoda lokte")
    axs[1].annotate("loket", (3, wss[2]), xytext=(5, wss[1]), arrowprops=dict(arrowstyle="->", color=INK2))
    axs[2].plot(list(ks)[1:], ch, "-o", color=C1); axs[2].set_title("Calinski–Harabasz (max)")
    axs[3].plot(list(ks)[1:], sil, "-o", color=C1); axs[3].set_title("průměrná silueta (max)")
    for a in axs[1:]: a.set_xlabel("počet shluků K")
    save(fig, "fig05_pocet_k")


def fig05_kmeans_dbscan():
    X, _ = make_moons(300, noise=0.07, random_state=2)
    X = np.vstack([X, RNG.uniform([-1.3, -0.8], [2.3, 1.3], (15, 2))])
    X = StandardScaler().fit_transform(X)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
    scatter_groups(axs[0], X, KMeans(2, n_init=10, random_state=0).fit_predict(X), s=14)
    axs[0].set_title("k-means (K = 2): řeže „napříč“ – hledá kulaté shluky")
    scatter_groups(axs[1], X, DBSCAN(eps=0.3, min_samples=6).fit_predict(X), s=14)
    axs[1].set_title("DBSCAN: sleduje hustotu, šum označí zvlášť")
    axs[1].legend(loc="lower left", fontsize=8)
    for a in axs: a.set_xticks([]); a.set_yticks([])
    save(fig, "fig05_kmeans_dbscan")


# =====================================================================  přednáška 6 (PCA)
PROT = pd.read_csv(Path(__file__).parent / "protein.csv", index_col=0)
CZ = {"Albania": "Albánie", "Austria": "Rakousko", "Belgium": "Belgie", "Bulgaria": "Bulharsko",
      "Czechoslovakia": "ČSSR", "Denmark": "Dánsko", "E Germany": "NDR", "Finland": "Finsko",
      "France": "Francie", "Greece": "Řecko", "Hungary": "Maďarsko", "Ireland": "Irsko",
      "Italy": "Itálie", "Netherlands": "Nizozemsko", "Norway": "Norsko", "Poland": "Polsko",
      "Portugal": "Portugalsko", "Romania": "Rumunsko", "Spain": "Španělsko", "Sweden": "Švédsko",
      "Switzerland": "Švýcarsko", "UK": "VB", "USSR": "SSSR", "W Germany": "SRN", "Yugoslavia": "Jugoslávie"}
VARCZ = ["červené maso", "bílé maso", "vejce", "mléko", "ryby", "obiloviny", "škrob. potr.",
         "ořechy", "ovoce+zel."]


def protein_pca():
    Z = StandardScaler().fit_transform(PROT.values)
    R = np.corrcoef(Z.T)
    w, V = np.linalg.eigh(R)
    i = w.argsort()[::-1]; w, V = w[i], V[:, i]
    # znaménka jako v přednášce (obiloviny kladně v PC1)
    if V[5, 0] < 0: V[:, 0] *= -1
    if V[4, 1] < 0: V[:, 1] *= -1
    return Z, w, V, Z @ V


def fig06_princip():
    X = RNG.multivariate_normal([0, 0], [[1, .8], [.8, 1]], 120)
    X = StandardScaler().fit_transform(X)
    p = PCA().fit(X)
    Y = p.transform(X)
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.6))
    ax = axs[0]
    ax.scatter(X[:, 0], X[:, 1], s=14, c=C1, alpha=.55, edgecolors="none")
    v1, v2 = p.components_
    for v, lam, nm, col in [(v1, p.explained_variance_[0], "PC1", C2), (v2, p.explained_variance_[1], "PC2", C3)]:
        ax.annotate("", xy=2 * np.sqrt(lam) * v, xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=2.5))
        ax.text(*(2.2 * np.sqrt(lam) * v), nm, color=col, fontweight="bold")
    ax.plot([-3.5 * v1[0], 3.5 * v1[0]], [-3.5 * v1[1], 3.5 * v1[1]], color=C2, lw=1, ls=":")
    for j in [3, 17, 40, 77, 101]:
        t = X[j] @ v1
        ax.plot([X[j, 0], t * v1[0]], [X[j, 1], t * v1[1]], color=INK2, lw=1)
        ax.scatter(*(t * v1), s=18, c=C2, zorder=3)
    ax.set_aspect("equal"); ax.set_xlim(-3.5, 3.5); ax.set_ylim(-3.5, 3.5)
    ax.set_xlabel("příznak 1 (standardizovaný)"); ax.set_ylabel("příznak 2 (standardizovaný)")
    ax.set_title("původní osy: nové navzájem kolmé osy PC1 a PC2\npodle největšího rozptylu")
    ax = axs[1]
    ax.scatter(Y[:, 0], Y[:, 1], s=14, c=C1, alpha=.55, edgecolors="none")
    ax.set_aspect("equal"); ax.set_xlim(-3.5, 3.5); ax.set_ylim(-3.5, 3.5)
    ev = p.explained_variance_ratio_ * 100
    ax.set_xlabel(f"PC1 ({ev[0]:.0f} % rozptylu)"); ax.set_ylabel(f"PC2 ({ev[1]:.0f} % rozptylu)")
    ax.set_title("stejná data v nových osách (komponentní skóre):\nmrak je „narovnaný“, PC1 a PC2 nekorelují")
    save(fig, "fig06_princip")


def fig06_scree():
    _, w, _, _ = protein_pca()
    k = np.arange(1, 10)
    cum = np.cumsum(w) / w.sum() * 100
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.7))
    axs[0].plot(k, w, "-o", color=C1)
    axs[0].axhline(1, color=C2, ls="--", lw=1.5)
    axs[0].text(9, 1.08, "Kaiserovo kritérium λ = 1", color=C2, ha="right")
    for i in range(3):
        axs[0].annotate(f"{w[i]:.2f}", (k[i], w[i]), xytext=(6, 4), textcoords="offset points", color=INK2)
    axs[0].set_title("scree plot (graf úpatí) – hledáme „zlom“")
    axs[0].set_xlabel("pořadí komponenty"); axs[0].set_ylabel("vlastní číslo λ (= rozptyl PC)")
    axs[1].bar(k, w / w.sum() * 100, color=C1, width=.6)
    axs[1].plot(k, cum, "-o", color=C2, label="kumulativně")
    axs[1].axhspan(75, 85, color=GRID, alpha=.6, lw=0)
    axs[1].text(9.3, 80, "obvyklý cíl 75–85 %", va="center", ha="right", color=INK2, fontsize=9)
    for i in range(4):
        axs[1].annotate(f"{cum[i]:.0f} %", (k[i], cum[i]), xytext=(-8, 8), textcoords="offset points",
                        color=INK2, fontsize=9)
    axs[1].set_title("vysvětlený rozptyl [%]"); axs[1].set_xlabel("pořadí komponenty"); axs[1].legend(loc="center right")
    save(fig, "fig06_scree")


def fig06_zateze():
    _, w, V, _ = protein_pca()
    L = V[:, :2] * np.sqrt(w[:2])  # korelace příznak–komponenta
    fig, ax = plt.subplots(figsize=(6, 6))
    t = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(t), np.sin(t), color=AXIS, lw=1)
    for (a, b), nm in zip(L, VARCZ):
        ax.annotate("", xy=(a, b), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.8))
        ax.text(a * 1.1, b * 1.1, nm, ha="center", va="center", fontsize=9, color=INK)
    ax.axhline(0, color=AXIS, lw=.8); ax.axvline(0, color=AXIS, lw=.8)
    ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.15, 1.15); ax.set_aspect("equal")
    ev = w / w.sum() * 100
    ax.set_xlabel(f"PC1 ({ev[0]:.0f} %)"); ax.set_ylabel(f"PC2 ({ev[1]:.0f} %)")
    ax.set_title("graf komponentních zátěží (korelace příznak–PC)")
    save(fig, "fig06_zateze")


def fig06_biplot():
    from adjustText import adjust_text
    _, w, V, Y = protein_pca()
    S = Y[:, :2] / np.sqrt(w[:2])
    lab = KMeans(3, n_init=20, random_state=1).fit_predict(S)
    # pořadí shluků podle PC1 (obiloviny vpravo)
    order = np.argsort([S[lab == k, 0].mean() for k in range(3)])
    lab = np.array([list(order).index(l) for l in lab])
    fig, ax = plt.subplots(figsize=(9, 7))
    names = ["hlavně maso, mléko, vejce", "hlavně ryby (Pyrenejský poloostrov)", "hlavně obiloviny, ořechy"]
    # shluk se střední hodnotou PC1 a vysokým PC2 = ryby
    hi = int(np.argmax([S[lab == k, 1].mean() for k in range(3)]))
    rest = [k for k in range(3) if k != hi]
    mapping = {rest[0]: 0, hi: 1, rest[1]: 2}
    lab = np.array([mapping[l] for l in lab])
    scatter_groups(ax, S, lab, names, s=40)
    L = V[:, :2] * np.sqrt(w[:2]) * 1.9
    for (a, b), nm in zip(L, VARCZ):
        ax.annotate("", xy=(a, b), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.2))
        ax.text(a * 1.07, b * 1.07 + (0.08 if nm == "vejce" else 0), nm, fontsize=9, color=INK,
                fontweight="semibold", ha="center", va="center")
    texts = [ax.text(a, b, CZ[c], fontsize=8.5, color=INK2) for (a, b), c in zip(S, PROT.index)]
    ax.set_xlim(-2.1, 2.2); ax.set_ylim(-1.7, 3.7)
    adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle="-", color=AXIS, lw=.5))
    ax.axhline(0, color=AXIS, lw=.8); ax.axvline(0, color=AXIS, lw=.8)
    ev = w / w.sum() * 100
    ax.set_xlabel(f"PC1 ({ev[0]:.0f} %)  →  více obilovin a ořechů, méně živočišných bílkovin")
    ax.set_ylabel(f"PC2 ({ev[1]:.0f} %)  →  více ryb, ovoce a zeleniny")
    ax.set_title("biplot: státy (body) + příznaky (šipky); barvy = k-means (K = 3) na PC1 a PC2")
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "fig06_biplot")


def fig06_limitace():
    n = 150
    A = RNG.multivariate_normal([0, 0.6], [[6, 0], [0, .08]], n)
    B = RNG.multivariate_normal([0, -0.6], [[6, 0], [0, .08]], n)
    X = np.vstack([A, B]); y = np.r_[np.zeros(n, int), np.ones(n, int)]
    p = PCA().fit(X); Y = p.transform(X)
    fig, axs = plt.subplots(1, 3, figsize=(12.5, 3.4))
    scatter_groups(axs[0], X, y, ["třída A", "třída B"], s=12)
    axs[0].set_title("dvě třídy: rozdíl je ve „slabém“ směru"); axs[0].set_aspect("equal")
    axs[0].legend(loc="upper right", fontsize=8)
    for ax, j in zip(axs[1:], [0, 1]):
        bins = np.linspace(Y[:, j].min(), Y[:, j].max(), 35)
        ax.hist(Y[y == 0, j], bins, color=C1, alpha=.6); ax.hist(Y[y == 1, j], bins, color=C2, alpha=.6)
        ax.set_yticks([])
        ax.set_title(f"projekce na PC{j + 1} ({p.explained_variance_ratio_[j] * 100:.0f} % rozptylu)")
    axs[1].set_xlabel("třídy splývají"); axs[2].set_xlabel("třídy jsou dokonale oddělené")
    save(fig, "fig06_limitace")


# =====================================================================  přednáška 7 (kernel PCA)
def fig07_limity():
    rng = np.random.default_rng(71)  # vlastní generátor: nemění data ostatních obrázků
    # multimodální: 3 shluky (jako slide 4)
    mm = np.vstack([rng.normal(c, .35, (25, 2)) for c in [(1, 3), (4, 4.6), (1.4, .8)]])
    ymm = np.repeat([0, 1, 2], 25)
    # tvar X: dva nekolmé směry (slide 5)
    t = rng.uniform(-2.2, 2.2, 30)
    xx = np.vstack([np.c_[t, -0.35 * t], np.c_[0.3 * t, -1.6 * t]]) + rng.normal(0, .08, (60, 2))
    yxx = np.repeat([0, 1], 30)
    # soustředné kruhy (slide 6)
    ci, yci = make_circles(120, factor=0.45, noise=0.05, random_state=3)
    ci = ci * 2
    fig, axs = plt.subplots(2, 3, figsize=(12.5, 6.2), gridspec_kw={"height_ratios": [3, 1.15]})
    for c, (X, y, tit, labs) in enumerate([
            (mm, ymm, "multimodální rozložení", ["shluk 1", "shluk 2", "shluk 3"]),
            (xx, yxx, "nekolmé „přirozené“ osy", ["směr 1", "směr 2"]),
            (ci, yci, "lineárně neseparabilní skupiny", ["vnější kruh", "vnitřní kruh"])]):
        p = PCA(2).fit(X); mu = X.mean(0); Z = p.transform(X)
        ax = axs[0, c]
        scatter_groups(ax, X, y, labs, s=22)
        r = np.abs(X - mu).max() * 1.15
        for k, nm in enumerate(["PC1", "PC2"]):
            v = p.components_[k]
            ax.plot(*np.c_[mu - r * v, mu + r * v], color=INK2, ls="--", lw=1.2)
            e = mu + r * v
            ax.text(*e, nm, color=INK2, fontsize=9, fontweight="semibold", ha="left", va="bottom")
        ax.set_aspect("equal"); ax.set_title(tit)
        ax.set_xlabel("příznak 1 (x₁)"); ax.set_ylabel("příznak 2 (x₂)")
        ax.legend(loc="lower right", fontsize=7.5)
        ax.set_xticks([]); ax.set_yticks([])
        b = axs[1, c]
        for k in np.unique(y):
            m = y == k
            for row in (0, 1):
                b.scatter(Z[m, row], np.full(m.sum(), 1 - row) + rng.uniform(-.12, .12, m.sum()),
                          s=14, c=CAT[k], marker=MARK[k], alpha=.8, edgecolors=SURF, linewidths=.5)
        b.set_yticks([1, 0], ["PC1", "PC2"]); b.set_ylim(-.5, 1.5); b.set_xticks([])
        b.set_xlabel("projekce na komponentu")
    save(fig, "fig07_limity")


def fig07_poly():
    rng = np.random.default_rng(72)
    P = rng.uniform(-2, 2, (900, 2))
    fns = [("polynom 1. řádu: přímka", lambda x1, x2: x2 - 0.5 * x1),
           ("polynom 2. řádu: kružnice / elipsa", lambda x1, x2: x1 ** 2 + x2 ** 2 - 1.4),
           ("polynom 3. řádu: kubická křivka", lambda x1, x2: x2 - (x1 ** 3 - 2 * x1) / 1.5)]
    g = np.linspace(-2, 2, 300); G1, G2 = np.meshgrid(g, g)
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (tit, f) in zip(axs, fns):
        v = f(P[:, 0], P[:, 1]); keep = np.abs(v) > 0.25
        X = P[keep][:110]; y = (v[keep][:110] > 0).astype(int)
        scatter_groups(ax, X, y, ["třída A", "třída B"], s=18)
        ax.contour(G1, G2, f(G1, G2), levels=[0], colors=INK, linestyles="--", linewidths=1.5)
        ax.set_title(tit, fontsize=10); ax.set_aspect("equal")
        ax.set_xlabel("x₁"); ax.set_ylabel("x₂"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_ylim(-2.05, 2.75)
        ax.legend(loc="upper left", fontsize=8, ncol=2)
    save(fig, "fig07_poly")


def fig07_kernel_1d():
    a = RNG.uniform(-1, 1, 14)
    b = np.r_[RNG.uniform(-3, -1.6, 7), RNG.uniform(1.6, 3, 7)]
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.6))
    axs[0].scatter(a, np.zeros_like(a), s=50, c=C1, marker="o", label="třída A", edgecolors=SURF)
    axs[0].scatter(b, np.zeros_like(b), s=50, c=C2, marker="s", label="třída B", edgecolors=SURF)
    axs[0].set_yticks([]); axs[0].set_ylim(-1, 1); axs[0].set_xlabel("x")
    axs[0].set_title("1D: žádný jeden práh třídy neoddělí"); axs[0].legend(loc="upper right")
    axs[1].scatter(a, a ** 2, s=50, c=C1, marker="o", edgecolors=SURF)
    axs[1].scatter(b, b ** 2, s=50, c=C2, marker="s", edgecolors=SURF)
    axs[1].axhline(1.7, color=INK, ls="--", lw=1.5)
    axs[1].text(-3, 1.95, "přímka (lineární hranice) už stačí", color=INK2, fontsize=9)
    axs[1].set_xlabel("x"); axs[1].set_ylabel("φ(x) = x²")
    axs[1].set_title("po zobrazení x → (x, x²) do 2D: lineárně separabilní")
    save(fig, "fig07_kernel_1d")


def fig07_kpca():
    X, y = make_circles(400, factor=0.35, noise=0.06, random_state=0)
    lin = PCA(2).fit_transform(X)
    kp = KernelPCA(2, kernel="rbf", gamma=5).fit_transform(X)
    fig, axs = plt.subplots(1, 4, figsize=(13.5, 3.4))
    scatter_groups(axs[0], X, y, ["vnější kruh", "vnitřní kruh"], s=10); axs[0].set_title("původní data")
    axs[0].legend(loc="upper right", fontsize=7)
    scatter_groups(axs[1], lin, y, s=10); axs[1].set_title("lineární PCA: jen otočení")
    scatter_groups(axs[2], kp, y, s=10); axs[2].set_title("kernel PCA (RBF, γ = 5)")
    bins = np.linspace(kp[:, 0].min(), kp[:, 0].max(), 30)
    axs[3].hist(kp[y == 0, 0], bins, color=C1, alpha=.6); axs[3].hist(kp[y == 1, 0], bins, color=C2, alpha=.6)
    axs[3].set_title("kernel PCA: stačí jen PC1"); axs[3].set_yticks([])
    for a in axs[:3]: a.set_aspect("equal"); a.set_xticks([]); a.set_yticks([])
    save(fig, "fig07_kpca")


def fig07_gamma():
    X, y = make_circles(400, factor=0.35, noise=0.06, random_state=0)
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.5))
    for ax, g, t in zip(axs, [0.1, 5, 300], ["γ malé (široké jádro) ≈ lineární PCA", "γ vhodné",
                                             "γ velké (úzké jádro) – „každý sám“"]):
        Y = KernelPCA(2, kernel="rbf", gamma=g).fit_transform(X)
        scatter_groups(ax, Y, y, s=10); ax.set_title(f"{t}", fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
    save(fig, "fig07_gamma")


# =====================================================================  přednáška 8 (SVD)
def fig08_svd():
    A = np.array([[2.0, 1.0], [0.5, 1.5]])
    U, s, Vt = np.linalg.svd(A)
    t = np.linspace(0, 2 * np.pi, 200)
    C = np.vstack([np.cos(t), np.sin(t)])
    e = np.eye(2)
    steps = [(np.eye(2), "1) jednotková kružnice x"),
             (Vt, "2) Vᵀx: otočení"),
             (np.diag(s) @ Vt, "3) ΣVᵀx: natažení podél os"),
             (U @ np.diag(s) @ Vt, "4) UΣVᵀx = Ax: druhé otočení")]
    fig, axs = plt.subplots(1, 4, figsize=(13, 3.5))
    for ax, (M, ttl) in zip(axs, steps):
        P = M @ C
        ax.fill(P[0], P[1], color=C1, alpha=.12); ax.plot(P[0], P[1], color=C1)
        for v, col in [(Vt.T[:, 0], C2), (Vt.T[:, 1], C3)]:
            q = M @ v
            ax.annotate("", xy=q, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=2))
        ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_aspect("equal"); ax.set_title(ttl, fontsize=10)
    axs[0].text(-2.9, -2.8, "šipky = pravé singulární vektory v₁, v₂", fontsize=8, color=INK2)
    axs[3].text(-2.9, -2.8, f"délky šipek = σ₁ = {s[0]:.2f}, σ₂ = {s[1]:.2f}", fontsize=8, color=INK2)
    save(fig, "fig08_svd")


# =====================================================================  přednáška 9 (FA)
def varimax(L, iters=100, tol=1e-8):
    """Klasická varimax rotace (Kaiser): hledá ortogonální T maximalizující rozptyl kvadrátů zátěží."""
    p, k = L.shape
    T = np.eye(k); d = 0
    for _ in range(iters):
        Lr = L @ T
        u, s, vt = np.linalg.svd(L.T @ (Lr ** 3 - Lr @ np.diag((Lr ** 2).sum(0)) / p))
        T = u @ vt
        if s.sum() < d * (1 + tol): break
        d = s.sum()
    return L @ T


def fig09_rotace():
    n = 300
    rng = np.random.default_rng(9)
    F = rng.normal(size=(n, 2))
    # struktura jako v přednášce: 3 příznaky „dlouhodobý trénink“, 3 „aktuální forma“, 4 smíšené
    G = np.array([[.8, .05], [.85, .1], [.8, .1],
                  [.65, .55], [.6, .45], [.05, .75], [.1, .85], [.1, .8],
                  [.7, .6], [.65, .5]])
    X = F @ G.T + rng.normal(0, .45, (n, 10))
    names = ["km/týden", "počet maratonů", "roky aktivní", "BMI", "věk",
             "rychlost", "zrychlení", "výkon", "spirometrie", "biochemie"]
    grp = [0, 0, 0, 2, 2, 1, 1, 1, 2, 2]
    R = np.corrcoef(X.T)
    w, V = np.linalg.eigh(R)
    i = w.argsort()[::-1][:2]
    L0 = V[:, i] * np.sqrt(w[i])  # odhad zátěží metodou PCA: Γ = V·√λ
    L0 = L0 * np.sign(L0.sum(0))
    if L0[0, 1] < 0: L0[:, 1] *= -1
    Lv = varimax(L0)
    Lv = Lv * np.sign(Lv.sum(0))
    if Lv[0, 0] < Lv[0, 1]: Lv = Lv[:, ::-1]
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 5.2))
    labels = ["km/týden, maratony, roky aktivní", "rychlost, zrychlení, výkon", "BMI, věk, spirometrie, biochemie"]
    for ax, L, t in zip(axs, [L0, Lv], ["před rotací: všechny příznaky mají vysokou zátěž na F1",
                                        "po rotaci varimax: osy faktorů míří ke skupinám příznaků"]):
        for (a, b), g in zip(L, grp):
            ax.annotate("", xy=(a, b), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=CAT[g], lw=1.6))
        for g in range(3):
            ax.plot([], [], color=CAT[g], label=labels[g])
        ax.legend(loc="lower left", fontsize=8)
        ax.axhline(0, color=AXIS, lw=.8); ax.axvline(0, color=AXIS, lw=.8)
        ax.set_xlim(-.7, 1.05); ax.set_ylim(-.7, 1.05); ax.set_aspect("equal")
        ax.set_xlabel("zátěž na faktor F1"); ax.set_ylabel("zátěž na faktor F2"); ax.set_title(t, fontsize=10)
    save(fig, "fig09_rotace")
    print(pd.DataFrame(np.c_[L0, Lv, (Lv ** 2).sum(1)], index=names,
                       columns=["F1", "F2", "F1 var", "F2 var", "komunalita"]).round(2))


# =====================================================================  přednáška 10 (t-SNE)
def fig10_gauss_t():
    d = np.linspace(0, 5, 300)
    g = np.exp(-d ** 2 / 2); tt = 1 / (1 + d ** 2)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.plot(d, g, color=C1, label="Gaussova křivka (vysoká dimenze, p)")
    ax.plot(d, tt, color=C2, label="Studentovo t, 1 st. volnosti (mapa 2D, q)")
    ax.fill_between(d, g, tt, where=tt > g, color=C2, alpha=.12)
    ax.text(2.6, 0.25, "„těžké chvosty“: i vzdálené body\nmají v mapě nenulovou podobnost\n→ mohou se odsunout dál (crowding)",
            color=INK2, fontsize=9)
    ax.set_xlabel("vzdálenost od bodu i"); ax.set_ylabel("podobnost (neškálovaná)"); ax.legend()
    save(fig, "fig10_gauss_t")


def fig10_perplexita():
    X, y = make_blobs(300, centers=[[0, 0], [5, 0], [30, 0]], cluster_std=[0.5, 2.5, 1.0], random_state=4)
    fig, axs = plt.subplots(1, 5, figsize=(14, 3.1))
    scatter_groups(axs[0], X, y, s=8); axs[0].set_title("původní 2D data")
    for ax, p in zip(axs[1:], [2, 5, 30, 100]):
        Y = TSNE(2, perplexity=p, random_state=0, init="pca").fit_transform(X)
        scatter_groups(ax, Y, y, s=8); ax.set_title(f"t-SNE, perplexita = {p}")
    for a in axs: a.set_xticks([]); a.set_yticks([])
    save(fig, "fig10_perplexita")


def swiss():
    X, t = make_swiss_roll(1000, noise=0.05, random_state=0)
    return X, t


def fig10_swiss():
    X, t = swiss()
    fig = plt.figure(figsize=(12, 3.8))
    ax = fig.add_subplot(1, 3, 1, projection="3d")
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=t, cmap=SEQ, s=5)
    ax.set_title("„švýcarská roláda“ (3D)"); ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    ax.view_init(10, -70); ax.set_facecolor(SURF)
    P = PCA(2).fit_transform(X)
    T = TSNE(2, perplexity=30, random_state=0, init="pca").fit_transform(X)
    for i, (Y, ttl) in enumerate([(P, "PCA: roláda se „promáčkne“ – vrstvy se překryjí"),
                                  (T, "t-SNE: lokální sousedství zachováno")]):
        a = fig.add_subplot(1, 3, i + 2)
        a.scatter(Y[:, 0], Y[:, 1], c=t, cmap=SEQ, s=5); a.set_title(ttl, fontsize=10)
        a.set_xticks([]); a.set_yticks([])
    save(fig, "fig10_swiss")


# =====================================================================  přednáška 11 (UMAP)
def hier_data():
    # 3 skupiny; skupiny A a B jsou si blízko, C je daleko (globální struktura)
    centers = np.zeros((3, 20)); centers[1, 0] = 6; centers[2, 0] = 30
    X, y = make_blobs(450, centers=centers, cluster_std=1.5, random_state=1)
    return X, y


def fig11_umap_params():
    import umap
    X, y = hier_data()
    fig, axs = plt.subplots(2, 3, figsize=(12, 7))
    for r, md in enumerate([0.0, 0.8]):
        for c, k in enumerate([3, 15, 100]):
            Y = umap.UMAP(n_neighbors=k, min_dist=md, random_state=0).fit_transform(X)
            scatter_groups(axs[r, c], Y, y, ["A", "B (blízko A)", "C (daleko)"], s=8)
            axs[r, c].set_title(f"n_neighbors = {k}, min_dist = {md}", fontsize=10)
            axs[r, c].set_xticks([]); axs[r, c].set_yticks([])
    axs[0, 0].legend(loc="best", fontsize=8)
    save(fig, "fig11_umap_params")


def fig11_srovnani():
    import umap
    X, y = hier_data()
    S, t = swiss()
    fig, axs = plt.subplots(2, 3, figsize=(12, 7.2))
    for c, (nm, f) in enumerate([("PCA", lambda Z: PCA(2).fit_transform(Z)),
                                 ("t-SNE (perplexita 30)", lambda Z: TSNE(2, perplexity=30, random_state=0, init="pca").fit_transform(Z)),
                                 ("UMAP (n_neighbors 15)", lambda Z: umap.UMAP(random_state=0).fit_transform(Z))]):
        Y = f(X)
        scatter_groups(axs[0, c], Y, y, ["A", "B (blízko A)", "C (daleko)"], s=8)
        axs[0, c].set_title(nm)
        Y2 = f(S)
        axs[1, c].scatter(Y2[:, 0], Y2[:, 1], c=t, cmap=SEQ, s=4)
        for a in axs[:, c]: a.set_xticks([]); a.set_yticks([])
    axs[0, 0].legend(fontsize=8, loc="best")
    axs[0, 0].set_ylabel("3 skupiny ve 20D", fontsize=10)
    axs[1, 0].set_ylabel("švýcarská roláda (3D)", fontsize=10)
    save(fig, "fig11_srovnani")


if __name__ == "__main__":
    for f in [fig02_korelace, fig02_chi2, fig02_hotelling, fig02_vyznamnost,
              fig03_skalovani, fig03_log,
              fig04_korelace_tvary, fig04_regrese, fig04_logit, fig04_anova,
              fig05_vazby, fig05_dendrogram, fig05_pocet_k, fig05_kmeans_dbscan,
              fig06_princip, fig06_scree, fig06_zateze, fig06_biplot, fig06_limitace,
              fig07_limity, fig07_poly, fig07_kernel_1d, fig07_kpca, fig07_gamma, fig08_svd, fig09_rotace,
              fig10_gauss_t, fig10_perplexita, fig10_swiss, fig11_umap_params, fig11_srovnani]:
        f()
    _, w, V, _ = protein_pca()
    print("vlastní čísla:", w.round(2), "% :", (w / w.sum() * 100).round(2))
    print(pd.DataFrame(V[:, :2], index=PROT.columns).round(3))
