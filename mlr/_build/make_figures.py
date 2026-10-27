"""Generuje obrázky do mlr/figures/.

Spuštění (z kořene repozitáře pripravy):  uv run python mlr/_build/make_figures.py
Anglické popisky pro anglickou verzi skript (do mlr/figures/en/):  uv run python mlr/_build/make_figures.py --lang en
Vybrané obrázky:  … make_figures.py [--lang en] fig04_poly fig06_rf
Data jsou syntetická s pevným random seedem (výsledek je reprodukovatelný) nebo standardní datasety ze scikit-learn
(wine, digits, diabetes, breast cancer). Grafy dodržují paletu a pravidla skillu dataviz:
pevné pořadí barev C1 → C2 → C3, tvar značky jako druhé rozlišení, popisky osa/jednotky, žádná dvojí osa y.
Většina obrázků ukazuje, co se stane, když změníme jeden hyperparametr (ostatní zůstávají stejné).
"""
from pathlib import Path
import logging
import sys
import warnings

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

warnings.filterwarnings("ignore")
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

ARGS = sys.argv[1:]
LANG = "cs"
if "--lang" in ARGS:
    i = ARGS.index("--lang")
    LANG = ARGS[i + 1]
    del ARGS[i:i + 2]

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures" if LANG == "cs" else ROOT / "figures" / LANG
OUT.mkdir(exist_ok=True)


def T(cs, en):
    """Popisek podle jazyka (česká verze → figures/, anglická → figures/en/)."""
    return cs if LANG == "cs" else en

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
# světlé výplně oblastí rozhodnutí (barva třídy smíchaná s povrchem)
REG = ListedColormap(["#d6e5f7", "#fbdccf"])

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 10,
    "text.color": INK, "axes.labelcolor": INK2, "axes.edgecolor": AXIS,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 11,
    "axes.titleweight": "semibold", "axes.titlecolor": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "lines.linewidth": 2,
    "axes.formatter.use_locale": False,
})


def rng(seed):
    return np.random.default_rng(seed)


def cz(x, d=2):
    """Číslo s desetinnou čárkou pro popisky (v angličtině s tečkou)."""
    s = f"{x:.{d}f}"
    return s.replace(".", ",") if LANG == "cs" else s


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", dpi=150)
    plt.close(fig)
    print("ok", name)


def scatter2(ax, X, y, s=22):
    for k in np.unique(y):
        m = y == k
        ax.scatter(X[m, 0], X[m, 1], s=s, c=CAT[int(k)], marker=MARK[int(k)], edgecolors=SURF, linewidths=0.6,
                   zorder=3)


def regions(ax, model, X, h=200, pad=0.5):
    x0, x1 = X[:, 0].min() - pad, X[:, 0].max() + pad
    y0, y1 = X[:, 1].min() - pad, X[:, 1].max() + pad
    xx, yy = np.meshgrid(np.linspace(x0, x1, h), np.linspace(y0, y1, h))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    ax.contourf(xx, yy, Z, levels=[-0.5, 0.5, 1.5], cmap=REG, zorder=0)
    ax.contour(xx, yy, Z, levels=[0.5], colors=[INK2], linewidths=1, zorder=1)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    return xx, yy


def moons(n, noise, seed):
    from sklearn.datasets import make_moons
    return make_moons(n_samples=n, noise=noise, random_state=seed)


# =====================================================================  přednáška 1
def fig01_gd_eta():
    """Gradientní sestup na f = ½(x1² + 5x2²) se čtyřmi kroky učení (jako na slidu 36)."""
    xs = np.linspace(-4.6, 4.6, 200); ys = np.linspace(-2.6, 2.6, 200)
    XX, YY = np.meshgrid(xs, ys); F = 0.5 * (XX ** 2 + 5 * YY ** 2)
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.3), sharey=True)
    labels = {0.05: T("plíží se", "crawls"), 0.2: T("dobře zvolený", "well chosen"),
              0.38: T("přestřeluje, ale konverguje", "overshoots but converges"), 0.45: T("diverguje", "diverges")}
    for ax, eta in zip(axs, [0.05, 0.2, 0.38, 0.45]):
        ax.contour(XX, YY, F, levels=[0.5, 2, 4.5, 8, 12.5], colors=[AXIS], linewidths=0.8)
        x = np.array([-4.0, 1.5]); path = [x.copy()]
        for _ in range(20):
            x = x - eta * np.array([1, 5]) * x
            path.append(x.copy())
        P = np.array(path)
        P = np.clip(P, -4.5, 4.5)
        ax.plot(P[:, 0], np.clip(P[:, 1], -2.5, 2.5), "-o", color=C2, ms=3, lw=1.2, zorder=3)
        ax.plot(0, 0, marker="*", ms=12, color=C1, zorder=4)
        fval = 0.5 * (x[0] ** 2 + 5 * x[1] ** 2)
        ax.set_title(f"η = {cz(eta)}: {labels[eta]}", fontsize=10)
        ax.text(0.04, 0.05, T("f po 20 krocích = ", "f after 20 steps = ") +
                (cz(fval) if fval < 1e3 else T("roste do ∞", "grows to ∞")),
                transform=ax.transAxes, fontsize=9, color=INK2, bbox=dict(fc=SURF, ec="none", pad=1.5), zorder=5)
        ax.set_xlabel("x₁"); ax.set_xlim(-4.6, 4.6); ax.set_ylim(-2.6, 2.6)
    axs[0].set_ylabel("x₂")
    save(fig, "fig01_gd_eta")


def fig01_knn_k():
    """k-NN: vliv počtu sousedů k na hranici rozhodnutí."""
    from sklearn.neighbors import KNeighborsClassifier
    X, y = moons(240, 0.35, 3)
    Xtr, ytr, Xte, yte = X[:120], y[:120], X[120:], y[120:]
    fig, axs = plt.subplots(1, 3, figsize=(11.5, 3.6), sharey=True)
    for ax, k in zip(axs, [1, 15, 101]):
        m = KNeighborsClassifier(n_neighbors=k).fit(Xtr, ytr)
        regions(ax, m, X)
        scatter2(ax, Xtr, ytr, s=18)
        ax.set_title(f"k = {k}: {T('trénink', 'train')} {cz(m.score(Xtr, ytr))}, test {cz(m.score(Xte, yte))}",
                     fontsize=10)
        ax.set_xlabel(T("příznak x₁", "feature x₁"))
    axs[0].set_ylabel(T("příznak x₂", "feature x₂"))
    save(fig, "fig01_knn_k")


# =====================================================================  přednáška 2
def fig02_roc():
    """Skóre dvou tříd, práh a ROC křivka se třemi pracovními body."""
    from scipy.stats import norm
    mu0, mu1 = 0.0, 1.8
    t_grid = np.linspace(-4, 6, 400)
    tpr = 1 - norm.cdf(t_grid, mu1, 1); fpr = 1 - norm.cdf(t_grid, mu0, 1)
    auc = norm.cdf((mu1 - mu0) / np.sqrt(2))
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [1.4, 1]})
    ax = axs[0]
    s = np.linspace(-4, 6, 400)
    ax.plot(s, norm.pdf(s, mu0, 1), color=C1, label=T("negativní (zdraví)", "negative (healthy)"))
    ax.plot(s, norm.pdf(s, mu1, 1), color=C2, label=T("pozitivní (nemocní)", "positive (sick)"))
    t = 1.2
    ax.fill_between(s[s >= t], norm.pdf(s[s >= t], mu0, 1), color=C1, alpha=0.25, lw=0)
    ax.fill_between(s[s >= t], norm.pdf(s[s >= t], mu1, 1), color=C2, alpha=0.25, lw=0)
    ax.axvline(t, color=INK, lw=1.2, ls="--")
    ax.text(t + 0.1, 0.49, T("práh t = 1,2: vše vpravo = „pozitivní“", "threshold t = 1.2: all to the right = “positive”"),
            fontsize=9, color=INK2, va="top")
    ax.set_ylim(0, 0.5)
    ax.text(2.7, 0.1, f"TPR = {cz(1 - norm.cdf(t, mu1, 1))}", color=INK, fontsize=9)
    ax.text(1.35, 0.03, f"FPR = {cz(1 - norm.cdf(t, mu0, 1))}", color=INK, fontsize=9)
    ax.set_xlabel(T("skóre klasifikátoru s(x)", "classifier score s(x)")); ax.set_ylabel(T("hustota", "density"))
    ax.set_title(T("Skóre obou tříd a jeden práh", "Scores of both classes and one threshold"))
    ax.legend(loc="upper left", fontsize=9)
    ax = axs[1]
    ax.plot(fpr, tpr, color=C1, label=f"model (AUC = {cz(auc)})")
    ax.plot([0, 1], [0, 1], color=MUTED, lw=1, ls="--",
            label=T("náhodný klasifikátor (AUC = 0,5)", "random classifier (AUC = 0.5)"))
    for tt, mk, txt in [(2.8, "o", T("vysoký práh", "high threshold")), (1.2, "s", f"t = {cz(1.2, 1)}"),
                        (-0.5, "^", T("nízký práh", "low threshold"))]:
        x_, y_ = 1 - norm.cdf(tt, mu0, 1), 1 - norm.cdf(tt, mu1, 1)
        ax.plot(x_, y_, marker=mk, color=C2, ms=8, mec=SURF, zorder=4)
        ax.annotate(txt, (x_, y_), xytext=(8, 4 if tt > 2 else -12), textcoords="offset points", fontsize=9, color=INK2)
    ax.set_xlabel(T("FPR = 1 − specificita", "FPR = 1 − specificity")); ax.set_ylabel(T("TPR = senzitivita", "TPR = sensitivity"))
    ax.set_title(T("ROC křivka: všechny prahy najednou", "ROC curve: all thresholds at once"))
    ax.legend(loc="lower right", fontsize=8.5)
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02); ax.set_aspect("equal")
    save(fig, "fig02_roc")


def fig02_kfold_var():
    """Hold-out vs. k-fold: jak moc kolísá odhad úspěšnosti podle náhodného rozdělení dat."""
    from sklearn.datasets import load_breast_cancer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
    X, y = load_breast_cancer(return_X_y=True)
    X, y = X[:200], y[:200]
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    hold, cv5, cv10 = [], [], []
    for s in range(60):
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=s, stratify=y)
        hold.append(model.fit(Xtr, ytr).score(Xte, yte))
        cv5.append(cross_val_score(model, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=s)).mean())
        cv10.append(cross_val_score(model, X, y, cv=StratifiedKFold(10, shuffle=True, random_state=s)).mean())
    fig, ax = plt.subplots(figsize=(8, 3.4))
    data = [hold, cv5, cv10]
    names = [T("hold-out\n(1 rozdělení 80/20)", "hold-out\n(1 split 80/20)"),
             T("5-fold CV\n(průměr 5 foldů)", "5-fold CV\n(mean of 5 folds)"),
             T("10-fold CV\n(průměr 10 foldů)", "10-fold CV\n(mean of 10 folds)")]
    for i, d in enumerate(data):
        jit = rng(i).uniform(-0.12, 0.12, len(d))
        ax.scatter(np.full(len(d), i) + jit, d, s=16, c=CAT[i], marker=MARK[i], edgecolors=SURF, linewidths=0.5)
        ax.text(i + 0.22, np.mean(d), f"{T('sm. odch.', 'std. dev.')} {cz(np.std(d), 3)}", fontsize=9, color=INK2,
                va="center")
    ax.set_xticks(range(3)); ax.set_xticklabels(names)
    ax.set_xlim(-0.5, 2.9)
    ax.set_ylabel(T("odhad accuracy", "accuracy estimate"))
    ax.set_title(T("Stejný model, 60 různých náhodných rozdělení dat (200 vzorků)",
                   "Same model, 60 different random splits of the data (200 samples)"))
    save(fig, "fig02_kfold_var")


# =====================================================================  přednáška 3
def fig03_hughes():
    """Hughesův jev: LDA, 20 trénovacích vzorků, prvních 10 příznaků informativních, ostatní šum."""
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    R = rng(3); D = 60; runs = 40
    acc = np.zeros((runs, D))
    for r in range(runs):
        shift = np.zeros(D); shift[:10] = 0.55
        def sample(n):
            y = np.arange(n) % 2
            X = R.normal(size=(n, D)) + np.outer(2 * y - 1, shift) / 2
            return X, y
        Xtr, ytr = sample(20); Xte, yte = sample(1000)
        for d in range(1, D + 1):
            m = LinearDiscriminantAnalysis(solver="lsqr", shrinkage=None)
            try:
                m.fit(Xtr[:, :d], ytr); acc[r, d - 1] = m.score(Xte[:, :d], yte)
            except Exception:
                acc[r, d - 1] = np.nan
    mean = np.nanmean(acc, 0); se = np.nanstd(acc, 0) / np.sqrt(runs)
    d = np.arange(1, D + 1); best = d[np.nanargmax(mean)]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.axvspan(0.5, 10.5, color=C3, alpha=0.12, lw=0)
    ax.text(3, mean.min() - 0.005, T("informativní\npříznaky", "informative\nfeatures"), fontsize=9, color=INK2,
            va="bottom")
    ax.annotate(T("d = n = 20: kovarianci\nuž nelze odhadnout", "d = n = 20: covariance\ncan no longer be estimated"),
                (19, mean[18]), xytext=(21, mean[18] - 0.03), fontsize=8.5, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED))
    ax.text(40, mean.max() - 0.02, T("přidáváme jen šum", "adding only noise"), fontsize=9, color=INK2)
    ax.fill_between(d, mean - se, mean + se, color=C1, alpha=0.2, lw=0)
    ax.plot(d, mean, color=C1)
    ax.axvline(best, color=C2, ls="--", lw=1.2)
    ax.text(best + 0.8, mean.max(), f"optimum d* = {best}", color=INK, fontsize=9)
    ax.set_xlabel(T("počet příznaků d (přidávány postupně)", "number of features d (added one by one)"))
    ax.set_ylabel(T("přesnost na testu", "test accuracy"))
    ax.set_title(T("Hughesův jev: LDA, 20 trénovacích vzorků, průměr 40 opakování",
                   "Hughes phenomenon: LDA, 20 training samples, mean of 40 runs"))
    save(fig, "fig03_hughes")


def fig03_pca_lda():
    """PCA vs. LDA na dvou protáhlých třídách vedle sebe."""
    R = rng(5); n = 120
    base = R.normal(size=(2 * n, 2)) * [2.6, 0.45]
    ang = np.deg2rad(35); Rm = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
    y = np.r_[np.zeros(n), np.ones(n)].astype(int)
    off = np.array([0, 1.0])
    X = base @ Rm.T + np.outer(2 * y - 1, Rm @ off) * 0.75
    Xc = X - X.mean(0)
    w_pca = np.linalg.eigh(np.cov(Xc.T))[1][:, -1]
    mu0, mu1 = X[y == 0].mean(0), X[y == 1].mean(0)
    Sw = np.cov(X[y == 0].T) + np.cov(X[y == 1].T)
    w_lda = np.linalg.solve(Sw, mu1 - mu0); w_lda /= np.linalg.norm(w_lda)
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.6), gridspec_kw={"width_ratios": [1.15, 1, 1]})
    ax = axs[0]
    scatter2(ax, X, y, s=14)
    for w, c, lab in [(w_pca, INK2, T("směr PCA", "PCA direction")), (w_lda, C3, T("směr LDA", "LDA direction"))]:
        ax.plot([-5 * w[0], 5 * w[0]], [-5 * w[1], 5 * w[1]], color=c, lw=2, label=lab)
    ax.set_aspect("equal"); ax.legend(fontsize=9, loc="upper left")
    ax.set_title(T("Data a dva směry projekce", "Data and two projection directions"))
    ax.set_xlabel("x₁"); ax.set_ylabel("x₂")
    for ax, w, ttl in [(axs[1], w_pca, T("Projekce na PCA: třídy se překrývají", "Projection on PCA: classes overlap")),
                       (axs[2], w_lda, T("Projekce na LDA: třídy oddělené", "Projection on LDA: classes separated"))]:
        z = Xc @ w
        bins = np.linspace(z.min(), z.max(), 30)
        for k in [0, 1]:
            ax.hist(z[y == k], bins=bins, color=CAT[k], alpha=0.6, label=f"{T('třída', 'class')} {k}")
        ax.set_title(ttl, fontsize=10); ax.set_xlabel(T("souřadnice z = wᵀx", "coordinate z = wᵀx")); ax.legend(fontsize=9)
    axs[1].set_ylabel(T("počet vzorků", "number of samples"))
    save(fig, "fig03_pca_lda")


def _digits(n=600):
    from sklearn.datasets import load_digits
    from sklearn.preprocessing import StandardScaler
    X, y = load_digits(return_X_y=True)
    idx = rng(0).permutation(len(y))[:n]
    return StandardScaler().fit_transform(X[idx]), y[idx]


def _embed_plot(ax, Z, y, title):
    cmap = plt.get_cmap("tab10")
    ax.scatter(Z[:, 0], Z[:, 1], c=[cmap(int(k)) for k in y], s=6, linewidths=0)
    ax.set_title(title, fontsize=10); ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)


def fig03_tsne_perp():
    from sklearn.manifold import TSNE
    X, y = _digits()
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.2))
    for ax, p in zip(axs, [2, 10, 30, 100]):
        Z = TSNE(perplexity=p, random_state=0, init="pca", learning_rate="auto").fit_transform(X)
        _embed_plot(ax, Z, y, f"perplexity = {p}")
    save(fig, "fig03_tsne_perp")


def fig03_umap_params():
    import umap
    X, y = _digits()
    fig, axs = plt.subplots(2, 3, figsize=(11, 6.6))
    for i, md in enumerate([0.0, 0.8]):
        for j, nn in enumerate([3, 15, 100]):
            Z = umap.UMAP(n_neighbors=nn, min_dist=md, random_state=0).fit_transform(X)
            _embed_plot(axs[i, j], Z, y, f"n_neighbors = {nn}, min_dist = {cz(md, 1)}")
    save(fig, "fig03_umap_params")


# =====================================================================  přednáška 4
def _poly_data(seed=1, n=40):
    R = rng(seed)
    x = np.sort(R.uniform(0, 5, n))
    y = 6 * np.cos(1.1 * x) - 1.6 * x + R.normal(0, 3, n)
    return x, y


def _poly_fit(x, y, deg, lam):
    """Polynomiální ridge regrese na x škálovaném do [−1, 1]; intercept se nepenalizuje."""
    s = (x - 2.5) / 2.5
    Phi = np.vander(s, deg + 1, increasing=True)
    P = np.eye(deg + 1) * lam; P[0, 0] = 0
    w = np.linalg.lstsq(Phi.T @ Phi + P, Phi.T @ y, rcond=None)[0]
    return lambda xn: np.vander((xn - 2.5) / 2.5, deg + 1, increasing=True) @ w


def fig04_poly():
    x, y = _poly_data()
    xt, yt = _poly_data(seed=11, n=400)
    xs = np.linspace(0, 5, 300)
    fig, axs = plt.subplots(2, 3, figsize=(12, 6.2), sharey=True)
    deg_ = T("stupeň", "degree")
    cfg = [(1, 0, f"{deg_} 1 (OLS)"), (3, 0, f"{deg_} 3 (OLS)"), (15, 0, f"{deg_} 15 (OLS)"),
           (15, 0, f"{deg_} 15, λ = 0"), (15, 0.1, f"{deg_} 15, λ = {cz(0.1, 1)}"), (15, 100, f"{deg_} 15, λ = 100")]
    for ax, (deg, lam, ttl) in zip(axs.ravel(), cfg):
        f = _poly_fit(x, y, deg, lam)
        tr = np.mean((f(x) - y) ** 2); te = np.mean((f(xt) - yt) ** 2)
        ax.scatter(x, y, s=16, c=C1, edgecolors=SURF, linewidths=0.5, zorder=3, label=T("trénovací data", "training data"))
        ax.plot(xs, np.clip(f(xs), -25, 20), color=C2, label="model")
        ax.set_ylim(-22, 16)
        ax.set_title(f"{ttl}\nMSE {T('trénink', 'train')} {cz(tr, 1)} · test {cz(te, 1)}", fontsize=10)
        ax.set_xlabel("x")
    axs[0, 0].set_ylabel("y"); axs[1, 0].set_ylabel("y"); axs[0, 0].legend(fontsize=8.5, loc="lower left")
    save(fig, "fig04_poly")


def fig04_ridge_lasso():
    from sklearn.datasets import load_diabetes
    from sklearn.linear_model import Ridge, Lasso
    from sklearn.preprocessing import StandardScaler
    X, y = load_diabetes(return_X_y=True)
    X = StandardScaler().fit_transform(X); y = y - y.mean()
    names = load_diabetes().feature_names
    lam_r = np.logspace(-2, 4.5, 60); lam_l = np.logspace(-1.5, 1.8, 60)
    Wr = np.array([Ridge(alpha=a).fit(X, y).coef_ for a in lam_r])
    Wl = np.array([Lasso(alpha=a, max_iter=20000).fit(X, y).coef_ for a in lam_l])
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 3.8), sharey=True)
    hi = np.argsort(-np.abs(Wr[0]))[:3]
    for ax, L, W, ttl in [(axs[0], lam_r, Wr, T("Ridge (L2): koeficienty se jen zmenšují", "Ridge (L2): coefficients only shrink")),
                          (axs[1], lam_l, Wl, T("LASSO (L1): koeficienty padají přesně na 0",
                                                "LASSO (L1): coefficients drop exactly to 0"))]:
        for j in range(W.shape[1]):
            k = list(hi).index(j) if j in hi else None
            ax.plot(L, W[:, j], color=CAT[k] if k is not None else AXIS, lw=2 if k is not None else 1.1,
                    label=T(f"příznak „{names[j]}“", f"feature “{names[j]}”") if k is not None else None)
        ax.set_xscale("log"); ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_xlabel(T("síla regularizace λ (log. osa)", "regularization strength λ (log axis)")); ax.set_title(ttl, fontsize=10)
    axs[0].set_ylabel(T("hodnota koeficientu wⱼ", "coefficient value wⱼ")); axs[0].legend(fontsize=8.5)
    nz = [(Wl[i] != 0).sum() for i in [0, 30, 59]]
    axs[1].text(0.97, 0.95, f"{T('nenulových koeficientů', 'non-zero coefficients')}:\n{nz[0]} → {nz[1]} → {nz[2]}",
                transform=axs[1].transAxes,
                ha="right", va="top", fontsize=9, color=INK2)
    save(fig, "fig04_ridge_lasso")


def fig04_losses():
    m = np.linspace(-2, 3, 400)
    fig, ax = plt.subplots(figsize=(9.5, 3.6))
    ax.plot(m, (m <= 0).astype(float), color=MUTED, lw=1.5, ls="--", label=T("0/1 chyba (to, co chceme)", "0/1 error (what we want)"))
    ax.plot(m, np.maximum(0, 1 - m), color=C1, label="hinge (SVM): max(0, 1 − yz)")
    ax.plot(m, np.log(1 + np.exp(-m)), color=C2, label=T("logistická", "logistic") + ": log(1 + e^(−yz))")
    ax.plot(m, np.maximum(0, -m), color=C3, label="perceptron: max(0, −yz)")
    ax.plot(m, (1 - m) ** 2, color=INK2, lw=1.2, ls=":", label="MSE: (1 − yz)²")
    ax.set_ylim(-0.1, 3.2); ax.axvline(0, color=AXIS, lw=0.8)
    ax.text(-1.95, 2.95, T("špatně zařazeno", "misclassified"), fontsize=9, color=INK2)
    ax.text(1.6, 2.95, T("správně zařazeno", "correctly classified"), fontsize=9, color=INK2)
    ax.set_xlabel(T("y · z  (skóre se znaménkem správné třídy)", "y · z  (score with the sign of the true class)"))
    ax.set_ylabel(T("ztráta L(y, z)", "loss L(y, z)"))
    ax.set_title(T("Ztrátové funkce lineární klasifikace", "Loss functions of linear classification")); ax.legend(fontsize=8.5, loc="upper left", bbox_to_anchor=(1.01, 1))
    save(fig, "fig04_losses")


def fig04_svm_c():
    from sklearn.svm import SVC
    R = rng(4); n = 25
    X = np.r_[R.normal([-1, -1], 0.9, (n, 2)), R.normal([1.2, 1.0], 0.9, (n, 2))]
    y = np.r_[np.zeros(n), np.ones(n)].astype(int)
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
    for ax, C in zip(axs, [0.01, 1, 100]):
        m = SVC(kernel="linear", C=C).fit(X, y)
        w = m.coef_[0]; b = m.intercept_[0]
        xx = np.linspace(-3.5, 3.5, 50)
        for off, ls in [(0, "-"), (1, "--"), (-1, "--")]:
            ax.plot(xx, -(w[0] * xx + b - off) / w[1], color=INK2, ls=ls, lw=1.4 if off == 0 else 1)
        ax.scatter(*m.support_vectors_.T, s=110, facecolors="none", edgecolors=INK, linewidths=1, zorder=4)
        scatter2(ax, X, y, s=20)
        ax.set_xlim(-3.5, 3.5); ax.set_ylim(-3.5, 3.5)
        ax.set_title(f"C = {cz(C) if C < 1 else C}: {T('šířka pásu', 'band width')} 2/‖w‖ = {cz(2 / np.linalg.norm(w))}, "
                     f"SV = {len(m.support_)}",
                     fontsize=10)
        ax.set_xlabel("x₁")
    axs[0].set_ylabel("x₂")
    save(fig, "fig04_svm_c")


def fig04_svm_rbf():
    from sklearn.svm import SVC
    X, y = moons(100, 0.35, 1)
    Xt, yt = moons(1000, 0.35, 2)
    fig, axs = plt.subplots(2, 3, figsize=(12, 7), sharey=True, sharex=True)
    rows = [[(1, 0.1), (1, 1), (1, 100)], [(0.05, 1), (1, 1), (10000, 1)]]
    for i, row in enumerate(rows):
        for j, (C, g) in enumerate(row):
            ax = axs[i, j]
            m = SVC(kernel="rbf", C=C, gamma=g).fit(X, y)
            regions(ax, m, X, h=180)
            scatter2(ax, X, y, s=14)
            ax.set_title(f"C = {cz(C) if C < 1 else C}, γ = {cz(g, 1) if g < 1 else g}\n"
                         f"SV = {len(m.support_)} · {T('trénink', 'train')} {cz(m.score(X, y))} · test {cz(m.score(Xt, yt))}",
                         fontsize=10)
    for ax in axs[1]:
        ax.set_xlabel("x₁")
    for ax in axs[:, 0]:
        ax.set_ylabel("x₂")
    save(fig, "fig04_svm_rbf")


# =====================================================================  přednáška 6
def fig06_terce():
    """Bias a rozptyl vizuálně (podle slidu 7, překresleno): terče a rozklad chyby podle složitosti."""
    from matplotlib.patches import Circle
    fig = plt.figure(figsize=(12, 5.2))
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 2.1], wspace=0.15, hspace=0.12)
    R = rng(6)
    lo, hi = T("nízký", "low"), T("vysoký", "high")
    var_ = T("rozptyl", "variance")
    cfg = [(0, 0, 0.0, 0.13, f"{lo} bias, {lo} {var_}"), (0, 1, 0.0, 0.42, f"{lo} bias, {hi} {var_}"),
           (1, 0, 0.62, 0.13, f"{hi} bias, {lo} {var_}"), (1, 1, 0.62, 0.42, f"{hi} bias, {hi} {var_}")]
    for r, c, bias, sd, ttl in cfg:
        ax = fig.add_subplot(gs[r, c])
        for rad, fc in [(1.0, SURF), (0.75, "#d6e5f7"), (0.42, SURF)]:
            ax.add_patch(Circle((0, 0), rad, facecolor=fc, edgecolor=INK2, lw=1.1))
        ax.add_patch(Circle((0, 0), 0.11, facecolor=C2, edgecolor="none", zorder=3))
        ang = np.deg2rad(135)
        P = np.array([bias * np.cos(ang), bias * np.sin(ang)]) + R.normal(0, sd, (16, 2))
        ax.scatter(P[:, 0], P[:, 1], s=14, c=C1, marker="o", edgecolors=SURF, linewidths=0.5, zorder=4)
        ax.set_xlim(-1.08, 1.08); ax.set_ylim(-1.08, 1.08); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(ttl, fontsize=9.5)
    ax = fig.add_subplot(gs[:, 2])
    c = np.linspace(0.05, 1, 300)
    bias2 = 0.9 * np.exp(-4.5 * c) + 0.04
    var = 0.03 + 0.9 * c ** 3.2
    noise = 0.12
    tot = bias2 + var + noise
    ax.plot(c, bias2, color=C2, label="bias²")
    ax.plot(c, var, color=C3, label=var_)
    ax.axhline(noise, color=MUTED, ls=":", lw=1.3, label=T("šum (neodstranitelný)", "noise (irreducible)"))
    ax.plot(c, tot, color=INK, lw=2.4, label=T("celková testová chyba", "total test error"))
    i = int(np.argmin(tot))
    ax.axvline(c[i], color=INK2, ls="--", lw=1)
    ax.plot(c[i], tot[i], "o", color=C3, ms=8, mec=SURF, zorder=5)
    ax.annotate(T("optimum\n(„sweet spot“)", "optimum\n(“sweet spot”)"), (c[i], tot[i]), xytext=(c[i] - 0.2, tot[i] - 0.14),
                fontsize=9.5, color=INK, arrowprops=dict(arrowstyle="->", color=INK2))
    ax.text(0.07, 1.08, T("podučení", "underfitting"), color=C2, fontsize=10, fontweight="semibold")
    ax.text(0.97, 1.08, T("přeučení", "overfitting"), color=C3, fontsize=10, fontweight="semibold", ha="right")
    ax.set_ylim(0, 1.15); ax.set_xlim(0.05, 1)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(T("složitost modelu →", "model complexity →")); ax.set_ylabel(T("chyba", "error"))
    ax.set_title(T("Rozklad testové chyby podle složitosti modelu", "Decomposition of test error by model complexity"))
    ax.legend(fontsize=9, loc="upper center", bbox_to_anchor=(0.52, 0.93))
    fig.savefig(OUT / "fig06_terce.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("ok fig06_terce")


def fig06_regimy():
    """Učicí křivky a dva režimy (podle slidu 8, překresleno, schematicky)."""
    from matplotlib.patches import Ellipse
    n = np.linspace(1, 100, 400)
    test = 0.30 + 2.2 / (n + 2.5) ** 0.95
    train = 0.30 - 0.30 * np.exp(-n / 22)
    eps = 0.25
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    ax.plot(n, test, color=C2, label=T("testovací chyba", "test error"))
    ax.plot(n, train, color=C1, label=T("trénovací chyba", "training error"))
    ax.axhline(eps, color=INK2, ls="--", lw=1.2)
    ax.text(99, eps - 0.035, T("přijatelná testová chyba ε", "acceptable test error ε"), ha="right", fontsize=9.5, color=INK2)
    ax.add_patch(Ellipse((9, 0.37), 15, 0.62, fill=False, ec=MUTED, lw=1.3))
    ax.text(3, 0.71, T("Režim 1:\nvysoký rozptyl", "Regime 1:\nhigh variance"), fontsize=9.5, color=INK, va="bottom")
    ax.add_patch(Ellipse((72, 0.33), 40, 0.14, fill=False, ec=MUTED, lw=1.3))
    ax.text(72, 0.415, T("Režim 2: vysoký bias\n(obě křivky splynuly nad ε)", "Regime 2: high bias\n(both curves meet above ε)"),
            fontsize=9.5, color=INK, ha="center")
    ax.annotate(T("velká mezera\n= rozptyl", "large gap\n= variance"), (12, 0.27), xytext=(22, 0.52), fontsize=9, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED))
    ax.set_ylim(0, 0.95); ax.set_xlim(0, 100)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(T("počet trénovacích vzorků n →", "number of training samples n →")); ax.set_ylabel(T("chyba", "error"))
    ax.set_title(T("Učicí křivky: ve kterém režimu jsem?", "Learning curves: which regime am I in?"))
    ax.legend(fontsize=9.5, loc="upper right")
    save(fig, "fig06_regimy")


def fig06_bias_variance():
    from sklearn.tree import DecisionTreeRegressor
    R = rng(8)
    f = lambda x: np.sin(2 * x) + 0.4 * x

    def sample(n):
        x = R.uniform(0, 5, n); return x[:, None], f(x) + R.normal(0, 0.45, n)
    Xte, yte = sample(3000)
    depths = range(1, 13)
    tr, te = [], []
    for d in depths:
        a, b = [], []
        for _ in range(30):
            X, y = sample(60)
            m = DecisionTreeRegressor(max_depth=d, random_state=0).fit(X, y)
            a.append(np.mean((m.predict(X) - y) ** 2)); b.append(np.mean((m.predict(Xte) - yte) ** 2))
        tr.append(np.mean(a)); te.append(np.mean(b))
    fig, axs = plt.subplots(1, 3, figsize=(12.5, 3.7))
    ax = axs[0]
    ax.plot(list(depths), tr, "-o", color=C1, ms=5, label=T("trénovací chyba", "training error"))
    ax.plot(list(depths), te, "-s", color=C2, ms=5, label=T("testovací chyba", "test error"))
    ax.axhline(0.45 ** 2, color=MUTED, ls=":", lw=1.2)
    ax.text(8.3, 0.45 ** 2 - 0.03, f"{T('šum', 'noise')} σ² = {cz(0.2)}", fontsize=9, color=INK2)
    best = list(depths)[int(np.argmin(te))]
    ax.axvline(best, color=INK2, ls="--", lw=1)
    ax.text(1.1, 0.01, T("podučení\n(vysoký bias)", "underfitting\n(high bias)"), fontsize=9, color=INK2, va="bottom")
    ax.text(8.3, 0.3, T("přeučení\n(vysoký rozptyl)", "overfitting\n(high variance)"), fontsize=9, color=INK2, va="center")
    ax.set_xlabel(T("složitost modelu (max_depth stromu)", "model complexity (tree max_depth)")); ax.set_ylabel("MSE")
    ax.legend(fontsize=8.5, loc="center", bbox_to_anchor=(0.5, 0.55))
    ax.set_title(T("Chyba vs. složitost (60 vzorků)", "Error vs. complexity (60 samples)"), fontsize=10)
    ns = np.unique(np.logspace(1.1, 3, 14).astype(int))
    for ax, d, ttl in [(axs[1], 8, T("Režim 1: vysoký rozptyl (strom hloubky 8)", "Regime 1: high variance (tree of depth 8)")),
                       (axs[2], 1, T("Režim 2: vysoký bias (pařez, hloubka 1)", "Regime 2: high bias (stump, depth 1)"))]:
        a, b = [], []
        for n in ns:
            aa, bb = [], []
            for _ in range(20):
                X, y = sample(n)
                m = DecisionTreeRegressor(max_depth=d, random_state=0).fit(X, y)
                aa.append(np.mean((m.predict(X) - y) ** 2)); bb.append(np.mean((m.predict(Xte) - yte) ** 2))
            a.append(np.mean(aa)); b.append(np.mean(bb))
        ax.plot(ns, a, "-o", color=C1, ms=4, label=T("trénovací chyba", "training error"))
        ax.plot(ns, b, "-s", color=C2, ms=4, label=T("testovací chyba", "test error"))
        ax.axhline(0.3, color=INK2, ls="--", lw=1)
        ax.text(ns[-1], 0.27, T("přijatelná chyba ε", "acceptable error ε"), fontsize=8.5, color=INK2, ha="right", va="top")
        ax.set_xscale("log"); ax.set_xlabel(T("počet trénovacích vzorků n", "number of training samples n"))
        ax.set_title(ttl, fontsize=10)
        ax.set_ylim(-0.02, 1.0); ax.legend(fontsize=8.5, loc="upper right")
    axs[1].set_ylabel("MSE")
    save(fig, "fig06_bias_variance")


def fig06_tree_depth():
    from sklearn.datasets import load_wine
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.model_selection import train_test_split
    data = load_wine()
    j = [list(data.feature_names).index("alcohol"), list(data.feature_names).index("flavanoids")]
    X, y = data.data[:, j], data.target
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=63, random_state=0, stratify=y)
    cm3 = ListedColormap(["#d6e5f7", "#fbdccf", "#d1efe4"])
    fig, axs = plt.subplots(1, 4, figsize=(13, 3.6), gridspec_kw={"width_ratios": [1, 1, 1, 1.15]})
    xx, yy = np.meshgrid(np.linspace(X[:, 0].min() - .3, X[:, 0].max() + .3, 250),
                         np.linspace(X[:, 1].min() - .3, X[:, 1].max() + .3, 250))
    for ax, d in zip(axs[:3], [1, 3, 10]):
        m = DecisionTreeClassifier(max_depth=d, random_state=0).fit(Xtr, ytr)
        Z = m.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        ax.contourf(xx, yy, Z, levels=[-.5, .5, 1.5, 2.5], cmap=cm3)
        for k in range(3):
            mm = ytr == k
            ax.scatter(Xtr[mm, 0], Xtr[mm, 1], s=16, c=CAT[k], marker=MARK[k], edgecolors=SURF, linewidths=.5)
        ax.set_title(f"max_depth = {d}: {m.get_n_leaves()} {T('listů', 'leaves')}\n"
                     f"{T('trénink', 'train')} {cz(m.score(Xtr, ytr))} · test {cz(m.score(Xte, yte))}", fontsize=10)
        ax.set_xlabel(T("alkohol [%]", "alcohol [%]"))
    axs[0].set_ylabel(T("flavonoidy", "flavanoids"))
    ds = range(1, 11)
    tr = [DecisionTreeClassifier(max_depth=d, random_state=0).fit(Xtr, ytr).score(Xtr, ytr) for d in ds]
    te = [DecisionTreeClassifier(max_depth=d, random_state=0).fit(Xtr, ytr).score(Xte, yte) for d in ds]
    ax = axs[3]
    ax.plot(list(ds), tr, "-o", color=C1, ms=5, label=T("trénink", "train")); ax.plot(list(ds), te, "-s", color=C2, ms=5, label="test")
    ax.set_xlabel("max_depth"); ax.set_ylabel("accuracy"); ax.legend(fontsize=9)
    ax.set_title(T("Přesnost vs. hloubka", "Accuracy vs. depth"), fontsize=10)
    save(fig, "fig06_tree_depth")


def fig06_impurity():
    p = np.linspace(1e-6, 1 - 1e-6, 400)
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    ax.plot(p, 1 - np.maximum(p, 1 - p), color=C1, label=T("chybovost 1 − max p", "error rate 1 − max p"))
    ax.plot(p, -(p * np.log2(p) + (1 - p) * np.log2(1 - p)), color=C2, label=T("entropie [bit]", "entropy [bit]"))
    ax.plot(p, 2 * p * (1 - p), color=C3, label="Gini 1 − Σp² = 2p(1 − p)")
    ax.plot([0.8], [0.32], "^", color=C3, ms=8, mec=SURF); ax.plot([0.8], [0.722], "s", color=C2, ms=7, mec=SURF)
    ax.plot([0.8], [0.2], "o", color=C1, ms=7, mec=SURF)
    ax.annotate(f"{T('list', 'leaf')} 4 : 1 (p = {cz(0.8, 1)})", (0.8, 0.722), xytext=(0.83, 0.88), fontsize=9, color=INK2)
    ax.set_xlabel(T("podíl třídy 1 v uzlu p", "share of class 1 in the node p")); ax.set_ylabel(T("nečistota uzlu", "node impurity"))
    ax.set_title(T("Míry nečistoty pro dvě třídy", "Impurity measures for two classes")); ax.legend(fontsize=8.5, loc="upper left")
    save(fig, "fig06_impurity")


def fig06_bagging():
    from sklearn.tree import DecisionTreeRegressor
    R = rng(12)
    f = lambda x: np.sin(1.4 * x) * 1.2 + 0.25 * x
    xs = np.linspace(0, 5, 300)[:, None]

    def sample(n=45):
        x = R.uniform(0, 5, n); return x[:, None], f(x) + R.normal(0, 0.5, n)

    def bag(X, y, M):
        P = np.zeros(len(xs))
        for _ in range(M):
            i = R.integers(0, len(y), len(y))
            P += DecisionTreeRegressor(max_depth=4).fit(X[i], y[i]).predict(xs)
        return P / M
    fig, axs = plt.subplots(1, 3, figsize=(12.5, 3.6), gridspec_kw={"width_ratios": [1, 1, 1.05]})
    single, bagged = [], []
    for _ in range(20):
        X, y = sample()
        single.append(DecisionTreeRegressor(max_depth=4).fit(X, y).predict(xs)); bagged.append(bag(X, y, 50))
    for ax, P, ttl in [(axs[0], single, T("1 strom (max_depth = 4), 20 trénovacích sad", "1 tree (max_depth = 4), 20 training sets")),
                       (axs[1], bagged, T("bagging M = 50, stejných 20 sad", "bagging M = 50, the same 20 sets"))]:
        for pr in P:
            ax.plot(xs[:, 0], pr, color=C1, lw=0.8, alpha=0.45)
        ax.plot(xs[:, 0], f(xs[:, 0]), color=INK, lw=1.6, label=T("skutečná funkce", "true function"))
        ax.plot(xs[:, 0], np.mean(P, 0), color=C2, lw=1.8, ls="--", label=T("průměr přes sady ≈ h̄", "mean over sets ≈ h̄"))
        ax.set_title(ttl, fontsize=10); ax.set_xlabel("x"); ax.set_ylim(-2.2, 3)
        v = np.mean(np.var(P, 0))
        ax.text(0.03, 0.04, f"{T('průměrný rozptyl predikce', 'mean prediction variance')} {cz(v, 3)}", transform=ax.transAxes,
                                           fontsize=9, color=INK2)
    axs[0].set_ylabel("y"); axs[0].legend(fontsize=8.5, loc="upper left")
    # rozptyl vs. M: teorie s korelací ρ
    Ms = np.arange(1, 101)
    s2 = 1.0
    ax = axs[2]
    for k, rho in enumerate([0.0, 0.36, 0.7]):
        ax.plot(Ms, rho * s2 + (1 - rho) * s2 / Ms, color=CAT[k], marker=MARK[k], markevery=12, ms=6,
                label=f"ρ = {cz(rho)}")
    ax.set_xlabel(T("počet stromů M", "number of trees M")); ax.set_ylabel(T("rozptyl průměru / σ²", "variance of the mean / σ²"))
    ax.set_title("Var = ρσ² + (1 − ρ)σ²/M", fontsize=10); ax.legend(fontsize=9)
    save(fig, "fig06_bagging")


def fig06_rf():
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    X, y = make_classification(n_samples=500, n_features=20, n_informative=6, n_redundant=4, flip_y=0.05,
                               random_state=3)
    trees = [10, 20, 40, 70, 100, 150, 200, 300]
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    for k, (mf, lab) in enumerate([(None, T("max_features = všech 20 (= bagging)", "max_features = all 20 (= bagging)")),
                                   ("sqrt", "max_features = √20 ≈ 4"), (1, "max_features = 1")]):
        err = []
        for t in trees:
            m = RandomForestClassifier(n_estimators=t, max_features=mf, oob_score=True, random_state=0, n_jobs=-1).fit(X, y)
            err.append(1 - m.oob_score_)
        ax.plot(trees, err, color=CAT[k], marker=MARK[k], ms=6, label=lab)
    ax.set_xlabel(T("počet stromů (n_estimators)", "number of trees (n_estimators)")); ax.set_ylabel(T("OOB chyba", "OOB error"))
    ax.set_title(T("Random forest: počet stromů a počet příznaků na split", "Random forest: number of trees and features per split"))
    ax.legend(fontsize=9)
    save(fig, "fig06_rf")


def fig06_adaboost():
    from sklearn.ensemble import AdaBoostClassifier
    from sklearn.tree import DecisionTreeClassifier
    X, y = moons(200, 0.25, 5)
    Xt, yt = moons(2000, 0.25, 6)
    fig, axs = plt.subplots(1, 4, figsize=(13, 3.5), sharey=True)
    for ax, M in zip(axs, [1, 3, 20, 300]):
        m = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), n_estimators=M, random_state=0).fit(X, y)
        regions(ax, m, X, h=200)
        scatter2(ax, X, y, s=12)
        ax.set_title(f"M = {M} {T('pařezů', 'stumps')}\n{T('trénink', 'train')} {cz(m.score(X, y))} · test {cz(m.score(Xt, yt))}",
                     fontsize=10)
        ax.set_xlabel("x₁")
    axs[0].set_ylabel("x₂")
    save(fig, "fig06_adaboost")


# příklad z přednášky (slidy 37–41): 10 bodů odečtených ze slidu, 3 pařezy; čísla ε, α a vah odpovídají slidům
ADA_X = np.array([[.11, .52], [.18, .29], [.37, .77], [.51, .85], [.66, .72],
                  [.35, .57], [.52, .50], [.31, .14], [.86, .81], [.83, .23]])
ADA_Y = np.array([1, 1, 1, 1, 1, -1, -1, -1, -1, -1])
ADA_STUMPS = [(0, 0.245, 1), (0, 0.74, 1), (1, 0.65, -1)]   # (příznak, práh, třída pro x ≤ práh)


def ada_stump(X, j, s, left):
    return np.where(X[:, j] <= s, left, -left)


def ada_run():
    """Vrátí seznam kol: (váhy před kolem, predikce pařezu, ε, α, váhy po kole)."""
    w = np.full(len(ADA_Y), 1 / len(ADA_Y))
    out = []
    for j, s, left in ADA_STUMPS:
        p = ada_stump(ADA_X, j, s, left)
        eps = w[p != ADA_Y].sum()
        a = 0.5 * np.log((1 - eps) / eps)
        w_new = w * np.exp(-a * ADA_Y * p)
        w_new /= w_new.sum()
        out.append((w, p, eps, a, w_new))
        w = w_new
    return out


def ada_points(ax, w, labels=True, wrong=None):
    """+1 = modrý křížek, −1 = oranžová čárka; plocha značky ∝ váha vzorku."""
    for k, (c, mk) in enumerate([(C1, "+"), (C2, "_")]):
        m = ADA_Y == (1 if k == 0 else -1)
        ax.scatter(ADA_X[m, 0], ADA_X[m, 1], s=2200 * w[m], c=c, marker=mk, linewidths=3, zorder=3)
    if wrong is not None:
        ax.scatter(ADA_X[wrong, 0], ADA_X[wrong, 1], s=650, facecolors="none", edgecolors=INK, linewidths=1.2, zorder=2)
    if labels:
        for (x, y), v in zip(ADA_X, w):
            ax.text(x + 0.075, y, cz(v), ha="left", va="center", fontsize=11, color=INK2, zorder=4,
                    bbox=dict(boxstyle="round,pad=0.12", fc=SURF, ec="none", alpha=0.85))


def ada_frame(ax, Z=None):
    if Z is not None:
        g = np.linspace(0, 1, 300)
        xx, yy = np.meshgrid(g, g)
        ax.contourf(xx, yy, (Z(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape) < 0).astype(float),
                    levels=[-0.5, 0.5, 1.5], cmap=REG, zorder=0)
        ax.contour(xx, yy, Z(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape), levels=[0], colors=[C3],
                   linewidths=1.6, zorder=1)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(True)


def fig06_ada_kola():
    runs = ada_run()
    sub, sup = "₁₂₃", "¹²³⁴"
    fig, axs = plt.subplots(2, 3, figsize=(11, 7.4))
    for m, (w, p, eps, a, w_new) in enumerate(runs):
        j, s, left = ADA_STUMPS[m]
        ax = axs[0, m]
        ada_frame(ax, lambda P, j=j, s=s, left=left: ada_stump(P, j, s, left).astype(float))
        ada_points(ax, w, wrong=np.where(p != ADA_Y)[0])
        ax.set_title(T(f"kolo {m + 1}: pařez h{sub[m]} na vahách w⁽{sup[m]}⁾\nε{sub[m]} = {cz(eps)} · α{sub[m]} = {cz(a)}",
                       f"round {m + 1}: stump h{sub[m]} on weights w⁽{sup[m]}⁾\nε{sub[m]} = {cz(eps)} · α{sub[m]} = {cz(a)}"),
                     fontsize=12.5)
        ax = axs[1, m]
        ada_frame(ax)
        ada_points(ax, w_new)
        ax.set_title(T(f"nové váhy w⁽{sup[m + 1]}⁾ po kole {m + 1}", f"new weights w⁽{sup[m + 1]}⁾ after round {m + 1}"),
                     fontsize=12.5)
    axs[0, 0].set_ylabel(T("pařez a chyby", "stump and errors"), fontsize=12)
    axs[1, 0].set_ylabel(T("převážení", "reweighting"), fontsize=12)
    save(fig, "fig06_ada_kola")


def fig06_ada_silny():
    runs = ada_run()
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.5))
    for m, ax in enumerate(axs[:3]):
        j, s, left = ADA_STUMPS[m]
        ada_frame(ax, lambda P, j=j, s=s, left=left: ada_stump(P, j, s, left).astype(float))
        ada_points(ax, np.full(10, 0.1), labels=False)
        ax.set_title(f"{'' if m == 0 else '+ '}{cz(runs[m][3])} · h{'₁₂₃'[m]}(x)", fontsize=14)
    H = lambda P: sum(r[3] * ada_stump(P, *st) for r, st in zip(runs, ADA_STUMPS))
    ada_frame(axs[3], H)
    ada_points(axs[3], np.full(10, 0.1), labels=False)
    axs[3].set_title("= H(x) = sign(…)", fontsize=14)
    save(fig, "fig06_ada_silny")


# =====================================================================  přednáška 7
def fig07_activations():
    z = np.linspace(-5, 5, 400)
    sig = 1 / (1 + np.exp(-z))
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.5))
    for ax, fs, ttl in [(axs[0], [sig, np.tanh(z), np.maximum(0, z)], T("Aktivační funkce f(z)", "Activation functions f(z)")),
                        (axs[1], [sig * (1 - sig), 1 - np.tanh(z) ** 2, (z > 0).astype(float)],
                         T("Jejich derivace f′(z)", "Their derivatives f′(z)"))]:
        for k, (fv, lab) in enumerate(zip(fs, [T("sigmoida", "sigmoid"), "tanh", "ReLU"])):
            ax.plot(z, fv, color=CAT[k], marker=MARK[k], markevery=50, ms=6, label=lab)
        ax.set_xlabel(T("vnitřní potenciál z", "inner potential z")); ax.set_title(ttl, fontsize=10); ax.legend(fontsize=9)
    axs[0].set_ylim(-1.2, 2.5)
    axs[1].text(2.2, 0.32, f"max σ′ = {cz(0.25)}", fontsize=9, color=INK2)
    save(fig, "fig07_activations")


def _beale(p):
    x, y = p
    return (1.5 - x + x * y) ** 2 + (2.25 - x + x * y ** 2) ** 2 + (2.625 - x + x * y ** 3) ** 2


def _beale_grad(p):
    x, y = p
    a, b, c = 1.5 - x + x * y, 2.25 - x + x * y ** 2, 2.625 - x + x * y ** 3
    return np.array([2 * a * (y - 1) + 2 * b * (y ** 2 - 1) + 2 * c * (y ** 3 - 1),
                     2 * a * x + 2 * b * 2 * x * y + 2 * c * 3 * x * y ** 2])


def run_opt(name, start, steps=3000):
    p = np.array(start, float); path = [p.copy()]
    u = np.zeros(2); s = np.zeros(2); m = np.zeros(2); v = np.zeros(2)
    for t in range(1, steps + 1):
        g = _beale_grad(p)
        if name == "SGD":
            p = p - 1e-5 * g
        elif name == "momentum":
            u = 0.9 * u + 1e-5 * g; p = p - u
        elif name == "RMSprop":
            s = 0.9 * s + 0.1 * g ** 2; p = p - 0.03 * g / (np.sqrt(s) + 1e-8)
        elif name == "Adam":
            m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g ** 2
            mh = m / (1 - 0.9 ** t); vh = v / (1 - 0.999 ** t)
            p = p - 0.2 * mh / (np.sqrt(vh) + 1e-8)
        path.append(p.copy())
    return np.array(path)


ETA = {"SGD": "10⁻⁵", "momentum": "10⁻⁵", "RMSprop": cz(0.03), "Adam": cz(0.2, 1)}


def fig07_optimizers():
    xs = np.linspace(-0.5, 4.5, 300); ys = np.linspace(-3.2, 1.6, 300)
    XX, YY = np.meshgrid(xs, ys); F = _beale([XX, YY])
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.contour(XX, YY, np.log10(F + 1e-3), levels=18, colors=[AXIS], linewidths=0.7)
    start = (2.4, -2.8)
    cols = [(MUTED, "o"), (C1, "s"), (C3, "^"), (C2, "D")]
    for (c, mk), name in zip(cols, ["SGD", "momentum", "RMSprop", "Adam"]):
        P = run_opt(name, start)
        d = np.linalg.norm(P[-1] - [3, 0.5])
        ax.plot(P[:, 0], P[:, 1], color=c, lw=1.6, marker=mk, markevery=300, ms=5,
                label=f"{name} (η = {ETA[name]}): {T('vzdálenost od min.', 'distance from min.')} {cz(d, 3)}")
    ax.plot(3, 0.5, marker="*", ms=14, color=INK); ax.plot(*start, marker="o", ms=7, color=INK, mfc=SURF)
    ax.text(3.05, 0.6, T("minimum (3; 0,5)", "minimum (3, 0.5)"), fontsize=9); ax.text(2.45, -2.95, "start", fontsize=9)
    ax.set_xlim(-0.5, 4.5); ax.set_ylim(-3.2, 1.6)
    ax.set_xlabel("θ₁"); ax.set_ylabel("θ₂")
    ax.set_title(T("Beale funkce, 3000 kroků ze stejného startu", "Beale function, 3000 steps from the same start"))
    ax.legend(fontsize=8.5, loc="upper left")
    save(fig, "fig07_optimizers")


def fig07_early_stopping():
    """Malá síť na malých datech: trénovací a validační ztráta během epoch, bez a s weight decay."""
    from sklearn.neural_network import MLPClassifier
    from sklearn.metrics import log_loss
    X, y = moons(80, 0.35, 21)
    Xv, yv = moons(1000, 0.35, 22)
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 3.6))
    for ax, alpha, ttl in [(axs[0], 1e-5, T("bez regularizace (λ ≈ 0)", "no regularization (λ ≈ 0)")),
                           (axs[1], 0.3, f"weight decay λ = {cz(0.3, 1)}")]:
        m = MLPClassifier(hidden_layer_sizes=(200, 200), alpha=alpha, learning_rate_init=0.005, random_state=0,
                          batch_size=16)
        tr, va = [], []
        for ep in range(500):
            m.partial_fit(X, y, classes=[0, 1])
            tr.append(log_loss(y, m.predict_proba(X))); va.append(log_loss(yv, m.predict_proba(Xv)))
        e = np.arange(1, 501)
        ax.plot(e, tr, color=C1, label=T("trénovací ztráta", "training loss"))
        ax.plot(e, va, color=C2, label=T("validační ztráta", "validation loss"))
        b = int(np.argmin(va))
        ax.axvline(b + 1, color=INK2, ls="--", lw=1)
        ax.text(b + 8, max(va) * 0.9, f"early stopping\n({T('epocha', 'epoch')} {b + 1})", fontsize=9, color=INK2, va="top")
        ax.set_xlabel(T("epocha", "epoch")); ax.set_ylabel(T("křížová entropie", "cross-entropy")); ax.set_title(ttl, fontsize=10)
        ax.set_ylim(0, max(1.0, min(max(va), 2.5))); ax.legend(fontsize=9, loc="upper right")
    save(fig, "fig07_early_stopping")


def fig07_alpha():
    from sklearn.neural_network import MLPClassifier
    X, y = moons(100, 0.35, 31)
    Xt, yt = moons(1000, 0.35, 32)
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.7), sharey=True)
    for ax, a in zip(axs, [1e-4, 0.1, 3]):
        m = MLPClassifier(hidden_layer_sizes=(100, 100), alpha=a, max_iter=4000, random_state=0).fit(X, y)
        regions(ax, m, X, h=180)
        scatter2(ax, X, y, s=14)
        ax.set_title(f"λ (alpha) = {a if a >= 1 else cz(a, 4) if a < 0.01 else cz(a, 1)}\n"
                     f"{T('trénink', 'train')} {cz(m.score(X, y))} · test {cz(m.score(Xt, yt))}", fontsize=10)
        ax.set_xlabel("x₁")
    axs[0].set_ylabel("x₂")
    save(fig, "fig07_alpha")


ALL = [fig01_gd_eta, fig01_knn_k, fig02_roc, fig02_kfold_var, fig03_hughes, fig03_pca_lda, fig03_tsne_perp,
       fig03_umap_params, fig04_poly, fig04_ridge_lasso, fig04_losses, fig04_svm_c, fig04_svm_rbf,
       fig06_terce, fig06_regimy, fig06_bias_variance, fig06_tree_depth, fig06_impurity, fig06_bagging, fig06_rf, fig06_adaboost,
       fig06_ada_kola, fig06_ada_silny,
       fig07_activations, fig07_optimizers, fig07_early_stopping, fig07_alpha]

if __name__ == "__main__":
    only = ARGS
    for f in ALL:
        if not only or f.__name__ in only:
            f()
