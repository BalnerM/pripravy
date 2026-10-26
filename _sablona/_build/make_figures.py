"""Generuje obrázky do <zkratka>/figures/.

Spuštění (z kořene repozitáře pripravy):  uv run python <zkratka>/_build/make_figures.py
Data jsou syntetická s pevným random seedem (výsledek je reprodukovatelný), nebo převzatá z přednášky
(ulož je vedle skriptu jako CSV a uveď zdroj). Grafy dodržují paletu a pravidla skillu dataviz:
pevné pořadí barev C1 → C2 → C3, tvar značky jako druhé rozlišení, popisky osa/jednotky, žádná dvojí osa y.
"""
from pathlib import Path
import logging
import warnings

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

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


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", dpi=150)
    plt.close(fig)
    print("ok", name)


# =====================================================================  přednáška 1 (ukázka – nahraď vlastními grafy)
def fig01_ukazka():
    x = RNG.normal(0, 1, 120)
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, (k, rho, ttl) in zip(axs, [(0, 0.1, "slabý vztah (r ≈ 0,1)"), (1, 0.85, "silný vztah (r ≈ 0,85)")]):
        y = rho * x + np.sqrt(1 - rho ** 2) * RNG.normal(0, 1, x.size)
        ax.scatter(x, y, s=18, c=CAT[k], marker=MARK[k], edgecolors=SURF, linewidths=0.6)
        ax.set_title(ttl); ax.set_xlabel("proměnná x"); ax.set_ylabel("proměnná y")
    save(fig, "fig01_ukazka")


if __name__ == "__main__":
    for f in [fig01_ukazka]:
        f()
