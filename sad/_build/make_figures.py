"""Generuje obrázky do <zkratka>/figures/.

Spuštění (z kořene repozitáře pripravy):  uv run python <zkratka>/_build/make_figures.py
Schémata zapojení kreslí knihovna schemdraw, grafy (přenosové charakteristiky, průběhy) matplotlib.
Grafy dodržují paletu a pravidla skillu dataviz: pevné pořadí barev C1 → C2 → C3, tvar značky jako druhé
rozlišení, popisky osa/jednotky, žádná dvojí osa y. Všechny křivky jsou spočítané z přenosových funkcí.
"""
from pathlib import Path
from contextlib import contextmanager
import logging
import sys
import warnings

import numpy as np
from scipy import signal
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import schemdraw
import schemdraw.elements as elm

warnings.filterwarnings("ignore")
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
sys.stdout.reconfigure(encoding="utf-8")

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
    "font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 10, "mathtext.fontset": "dejavusans",
    "text.color": INK, "axes.labelcolor": INK2, "axes.edgecolor": AXIS,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 11,
    "axes.titleweight": "semibold", "axes.titlecolor": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "lines.linewidth": 2,
})
RNG = np.random.default_rng(7)
schemdraw.use("matplotlib")


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", dpi=150)
    plt.close(fig)
    print("ok", name)


@contextmanager
def schema(name, unit=2.6):
    """Schéma zapojení: stejný styl pro všechna schémata (tenká černá čára, světlé pozadí)."""
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=unit, fontsize=13, color=INK, lw=1.6, bgcolor=SURF, margin=0.35)
        yield d
        d.save(str(OUT / f"{name}.png"), dpi=150)
    plt.close("all")
    print("ok", name)


def svorka(d, xy, text, loc="left"):
    """Otevřená svorka (vstup / výstup) s popiskem."""
    elm.Dot(open=True).at(xy).label(text, loc=loc)


# ---- přenosové funkce (H = U_výst / U_vst, s = jω) ----
def h_dp(f, fc):
    return 1 / (1 + 1j * f / fc)


def h_hp(f, fc):
    return (1j * f / fc) / (1 + 1j * f / fc)


def db(h):
    return 20 * np.log10(np.abs(h))


def faze(h):
    return np.degrees(np.angle(h))


def log_osa(ax, label="frekvence f [Hz]"):
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    ax.set_xlabel(label)


def cz(v, nd=2):
    return f"{v:.{nd}f}".replace(".", ",")


# =====================================================================  kapitola 1: obvody, dělič napětí
def fig01_ohm():
    with schema("fig01_ohm") as d:
        elm.SourceV().up().label("$U$")
        elm.Line().right(d.unit * 0.6)
        r = elm.Resistor().down().label("$R$", loc="bottom")
        elm.CurrentLabelInline(direction="in", ofst=0.9).at(r).label("$I$", loc="top")
        elm.Line().left(d.unit * 0.6)


def fig01_kirchhoff():
    with schema("fig01_kirchhoff") as d:
        u = d.unit
        elm.SourceV().up().label("$U_1$ = 12 V")
        elm.Line().right(u * 0.5)
        r1 = elm.Resistor().right().label("$R_1$ = 1 kΩ")
        elm.CurrentLabelInline(direction="in", ofst=0.7).at(r1).label("$I_1$", loc="bottom")
        elm.Line().right(u * 0.5)
        a = elm.Dot().label("A", loc="top")
        elm.Line().right(u * 0.5)
        r2 = elm.Resistor().right().label("$R_2$ = 2 kΩ")
        elm.CurrentLabelInline(direction="out", ofst=0.7).at(r2).label("$I_2$", loc="bottom")
        elm.Line().right(u * 0.5)
        elm.SourceV().down().reverse().label("$U_2$ = 6 V", loc="bottom")
        elm.Line().left(u * 2)
        b = elm.Dot().label("B", loc="bottom")
        elm.Line().left(u * 2)
        r3 = elm.Resistor().at(a.center).down().label("$R_3$ = 2 kΩ", loc="bottom")
        elm.CurrentLabelInline(direction="in", ofst=0.7).at(r3).label("$I_3$", loc="top")
        elm.Label().at((u * 1.0, u * 0.45)).label("↻ smyčka 1", fontsize=12, color=C1)
        elm.Label().at((u * 3.25, u * 0.3)).label("↺ smyčka 2", fontsize=12, color=C2)


def fig01_delic():
    with schema("fig01_delic") as d:
        # nezatížený
        svorka(d, (0, 0), "$U_1$")
        elm.Line().right(d.unit * 0.4)
        r1 = elm.Resistor().down().label("$R_1$", loc="bottom")
        elm.Dot()
        r2 = elm.Resistor().down().label("$R_2$", loc="bottom")
        g = elm.Dot()
        elm.Line().at(r2.start).right(d.unit * 0.8)
        o = elm.Dot(open=True)
        elm.Line().at(g.center).right(d.unit * 0.8)
        elm.Dot(open=True)
        elm.Line().at(g.center).left(d.unit * 0.4)
        elm.Dot(open=True)
        elm.Gap().at(o.center).down(d.unit).label(["+", "$U_2$", "–"], loc="bottom")
        elm.CurrentLabelInline(direction="in", ofst=0.9).at(r1).label("$I$", loc="top")
        elm.Label().at((d.unit * 0.6, d.unit * 0.4)).label("nezatížený", fontsize=12, color=C1)
        # zatížený
        x0 = d.unit * 2.6
        svorka(d, (x0, 0), "$U_1$")
        elm.Line().right(d.unit * 0.4)
        elm.Resistor().down().label("$R_1$", loc="bottom")
        n = elm.Dot()
        r2b = elm.Resistor().down().label("$R_2$", loc="bottom")
        gb = elm.Dot()
        elm.Line().at(n.center).right(d.unit * 1.0)
        nz = elm.Dot()
        rz = elm.Resistor().down().label("$R_\\mathrm{z}$", loc="bottom", color=C2).color(C2)
        elm.Line().left(d.unit * 1.0)
        elm.Line().at(gb.center).left(d.unit * 0.4)
        elm.Dot(open=True)
        elm.Line().at(nz.center).right(d.unit * 0.5)
        ob = elm.Dot(open=True)
        elm.Line().at(rz.end).right(d.unit * 0.5)
        elm.Dot(open=True)
        elm.Gap().at(ob.center).down(d.unit).label(["+", "$U_{2\\mathrm{z}}$", "–"], loc="bottom")
        elm.Label().at((x0 + d.unit * 0.8, d.unit * 0.4)).label("zatížený (zátěž $R_\\mathrm{z}$)", fontsize=12, color=C2)


def fig01_zatizeni():
    U, R1, R2 = 10.0, 10e3, 10e3
    rz = np.logspace(2, 7, 400)
    rp = R2 * rz / (R2 + rz)
    u2 = U * rp / (R1 + rp)
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.axhline(U * R2 / (R1 + R2), color=MUTED, ls="--", lw=1.4)
    ax.text(1.3e2, 5.15, "nezatížený dělič: 5 V", color=INK2, fontsize=9.5)
    ax.plot(rz, u2, color=C1, label="napětí na zátěži $U_{2\\mathrm{z}}$")
    for rzi, ofs in [(1e3, (12, -4)), (10e3, (12, -6)), (100e3, (8, -18)), (1e6, (0, -18))]:
        rp = R2 * rzi / (R2 + rzi)
        v = U * rp / (R1 + rp)
        ax.plot(rzi, v, "o", color=C1, mec=SURF, ms=7)
        lab = f"{rzi / 1e3:g} kΩ" if rzi < 1e6 else "1 MΩ"
        ax.annotate(f"$R_z$ = {lab}: {cz(v)} V", (rzi, v), xytext=ofs, textcoords="offset points",
                    fontsize=9, color=INK2)
    log_osa(ax, "odpor zátěže $R_\\mathrm{z}$ [Ω] (log. osa)")
    ax.set_xticks([1e2, 1e3, 1e4, 1e5, 1e6, 1e7])
    ax.set_xticklabels(["100", "1 k", "10 k", "100 k", "1 M", "10 M"])
    ax.set_ylabel("$U_{2\\mathrm{z}}$ [V]")
    ax.set_ylim(0, 5.8)
    ax.set_title("Dělič 10 kΩ / 10 kΩ z 10 V: čím menší zátěž, tím víc napětí „spadne“", loc="left")
    save(fig, "fig01_zatizeni")


# =====================================================================  kapitola 2: filtry
def fig02_xc():
    f = np.logspace(0, 5, 400)
    C, R = 100e-9, 10e3
    xc = 1 / (2 * np.pi * f * C)
    fc = 1 / (2 * np.pi * R * C)
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.plot(f, xc, color=C1, label="kondenzátor $X_C = 1/(2\\pi f C)$, C = 100 nF")
    ax.plot(f, np.full_like(f, R), color=C2, ls="--", label="rezistor R = 10 kΩ (nezávisí na f)")
    ax.plot(fc, R, "o", color=INK, ms=7, mec=SURF)
    ax.annotate(f"$X_C = R$ při $f_c$ ≈ {fc:.0f} Hz", (fc, R), xytext=(14, 18), textcoords="offset points",
                fontsize=9.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
    ax.set_yscale("log")
    log_osa(ax)
    ax.set_ylabel("odpor / reaktance [Ω]")
    ax.text(1.5, 3e2, "nízké f: kondenzátor ≈ rozpojený obvod", fontsize=9, color=INK2)
    ax.text(1.2e3, 3e5, "vysoké f: kondenzátor ≈ zkrat", fontsize=9, color=INK2)
    ax.legend(loc="lower left", fontsize=9)
    ax.set_title("Reaktance kondenzátoru klesá s frekvencí", loc="left")
    save(fig, "fig02_xc")


def _rc_clanek(d, x0, prvni, druhy, nazev, barva):
    """Dvojbran: podélný prvek (prvni) a příčný prvek (druhy) – dělič napětí."""
    svorka(d, (x0, 0), "$U_\\mathrm{vst}$")
    a = prvni().right().at((x0, 0))
    n = elm.Dot()
    elm.Line().right(d.unit * 0.6)
    o = elm.Dot(open=True)
    b = druhy().at(n.center).down()
    g = elm.Dot()
    elm.Line().right(d.unit * 0.6)
    elm.Dot(open=True)
    elm.Line().at(g.center).left(d.unit)
    elm.Dot(open=True)
    elm.Gap().at(o.center).down(d.unit).label(["+", "$U_\\mathrm{výst}$", "–"], loc="bottom")
    elm.Label().at((x0 + d.unit * 0.8, d.unit * 0.75)).label(nazev, fontsize=12.5, color=barva)
    return a, b


def fig02_dp_hp():
    with schema("fig02_dp_hp") as d:
        _rc_clanek(d, 0, lambda: elm.Resistor().label("$R$"), lambda: elm.Capacitor().label("$C$", loc="bottom"),
                   "dolní propust (RC)", C1)
        _rc_clanek(d, d.unit * 3.2, lambda: elm.Capacitor().label("$C$"),
                   lambda: elm.Resistor().label("$R$", loc="bottom"), "horní propust (CR)", C2)


def _bode(name, h, fc, typ, barva, title):
    f = np.logspace(np.log10(fc) - 2, np.log10(fc) + 2, 600)
    H = h(f, fc)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.6, 5.4), sharex=True, gridspec_kw=dict(height_ratios=[1.5, 1]))
    if typ == "dp":
        asym = np.where(f < fc, 0, -20 * np.log10(f / fc))
        fa = np.where(f < fc / 10, 0, np.where(f > fc * 10, -90, -45 * (1 + np.log10(f / fc))))
    else:
        asym = np.where(f > fc, 0, 20 * np.log10(f / fc))
        fa = np.where(f < fc / 10, 90, np.where(f > fc * 10, 0, 45 * (1 - np.log10(f / fc))))
    a1.plot(f, asym, color=MUTED, ls="--", lw=1.4, label="asymptoty (náčrt rukou)")
    a1.plot(f, db(H), color=barva, label="skutečná charakteristika")
    a1.plot(fc, -3.01, "o", color=INK, ms=6, mec=SURF)
    a1.annotate("−3 dB v $f_c$", (fc, -3.01), xytext=(12, -16),
                textcoords="offset points", fontsize=9.5)
    a1.axvline(fc, color=AXIS, lw=1, ls=":")
    slope = "−20 dB/dekádu" if typ == "dp" else "+20 dB/dekádu"
    xs = fc * 10 if typ == "dp" else fc / 10
    a1.annotate(slope, (xs, -20), xytext=(10, 4) if typ == "dp" else (-95, 4), textcoords="offset points",
                fontsize=9.5, color=INK2)
    a1.set_ylabel("modul |H| [dB]")
    a1.set_ylim(-45, 5)
    a1.legend(loc="lower left" if typ == "dp" else "lower right", fontsize=9)
    a1.set_title(title, loc="left")
    a2.plot(f, fa, color=MUTED, ls="--", lw=1.4)
    a2.plot(f, faze(H), color=barva)
    a2.plot(fc, -45 if typ == "dp" else 45, "o", color=INK, ms=6, mec=SURF)
    a2.axvline(fc, color=AXIS, lw=1, ls=":")
    a2.set_ylabel("fáze φ [°]")
    a2.set_yticks([-90, -45, 0] if typ == "dp" else [0, 45, 90])
    log_osa(a2, f"frekvence f [Hz] (log. osa), $f_c$ = {fc:g} Hz")
    save(fig, name)


def fig02_bode_dp():
    _bode("fig02_bode_dp", h_dp, 100, "dp", C1, "Dolní propust: propouští nízké frekvence")


def fig02_bode_hp():
    _bode("fig02_bode_hp", h_hp, 100, "hp", C2, "Horní propust: propouští vysoké frekvence")


def fig02_postup():
    fc = 100
    f = np.logspace(0, 4, 400)
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.3), sharey=True)
    for k, ax in enumerate(axs):
        ax.set_xscale("log")
        ax.set_xticks([1, 10, 100, 1000, 10000])
        ax.set_xticklabels(["1", "10", "100", "1 k", "10 k"])
        ax.set_xlabel("f [Hz]")
        ax.set_ylim(-45, 6)
        ax.axvline(fc, color=AXIS, lw=1, ls=":")
    axs[0].set_ylabel("|H| [dB]")
    axs[0].set_title("1) spočítej a vyznač $f_c$", loc="left")
    axs[0].annotate("$f_c$ = 100 Hz", (fc, 0), xytext=(6, -30), textcoords="offset points", fontsize=9.5)
    axs[1].set_title("2) asymptoty: 0 dB a −20 dB/dek", loc="left")
    asym = np.where(f < fc, 0, -20 * np.log10(f / fc))
    axs[1].plot(f, asym, color=MUTED, ls="--", lw=1.6)
    for x, y in [(1000, -20), (10000, -40)]:
        axs[1].plot(x, y, "s", color=INK2, ms=5)
    axs[1].text(1.3, -33, "o dekádu dál → o 20 dB níž", fontsize=9, color=INK2)
    axs[2].set_title("3) zaobli: v $f_c$ o 3 dB pod zlomem", loc="left")
    axs[2].plot(f, asym, color=MUTED, ls="--", lw=1.4)
    axs[2].plot(f, db(h_dp(f, fc)), color=C1)
    axs[2].plot(fc, -3, "o", color=INK, ms=6, mec=SURF)
    axs[2].annotate("−3 dB", (fc, -3), xytext=(-40, -18), textcoords="offset points", fontsize=9.5)
    save(fig, "fig02_postup")


def fig02_typy():
    f = np.logspace(-1, 4, 500)
    fig, axs = plt.subplots(2, 2, figsize=(8.6, 5.0), sharex=True, sharey=True)
    hpp = h_hp(f, 10) * h_dp(f, 1000)
    hpz = h_dp(f, 10) + h_hp(f, 1000)
    data = [("dolní propust", h_dp(f, 100), [100]), ("horní propust", h_hp(f, 100), [100]),
            ("pásmová propust", hpp, [10, 1000]), ("pásmová zádrž", hpz, [10, 1000])]
    for ax, (t, H, fcs) in zip(axs.flat, data):
        ax.plot(f, db(H), color=C1)
        for x in fcs:
            ax.axvline(x, color=AXIS, lw=1, ls=":")
        ax.set_title(t, loc="left")
        ax.set_xscale("log")
        ax.set_ylim(-40, 5)
    for ax in axs[1]:
        ax.set_xticks([0.1, 1, 10, 100, 1000, 10000])
        ax.set_xticklabels(["0,1", "1", "10", "100", "1 k", "10 k"])
        ax.set_xlabel("f [Hz]")
    for ax in axs[:, 0]:
        ax.set_ylabel("|H| [dB]")
    axs[0, 0].annotate("propustné\npásmo", (3, -12), fontsize=9, color=INK2)
    axs[0, 0].annotate("nepropustné\npásmo", (1500, -12), fontsize=9, color=INK2)
    save(fig, "fig02_typy")


def fig02_pp_schema():
    with schema("fig02_pp_schema") as d:
        svorka(d, (0, 0), "$U_\\mathrm{vst}$")
        elm.Capacitor().right().label("$C_1$")
        n1 = elm.Dot()
        elm.Resistor().right().label("$R_2$")
        n2 = elm.Dot()
        elm.Line().right(d.unit * 0.6)
        o = elm.Dot(open=True)
        elm.Resistor().at(n1.center).down().label("$R_1$", loc="bottom")
        g1 = elm.Dot()
        elm.Capacitor().at(n2.center).down().label("$C_2$", loc="bottom")
        g2 = elm.Dot()
        elm.Line().right(d.unit * 0.6)
        elm.Dot(open=True)
        elm.Line().at(g1.center).tox(g2.center)
        elm.Line().at(g1.center).left(d.unit)
        elm.Dot(open=True)
        elm.Gap().at(o.center).down(d.unit).label(["+", "$U_\\mathrm{výst}$", "–"], loc="bottom")
        elm.Label().at((d.unit * 0.55, d.unit * 0.75)).label("HP ($f_d$)", fontsize=12, color=C2)
        elm.Label().at((d.unit * 1.55, d.unit * 0.75)).label("DP ($f_h$)", fontsize=12, color=C1)


def fig02_bode_pp():
    f = np.logspace(-2, 4, 600)
    R1, C1_, R2, C2_ = 318.3e3, 1e-6, 10.61e3, 100e-9
    fd, fh = 1 / (2 * np.pi * R1 * C1_), 1 / (2 * np.pi * R2 * C2_)
    ideal = h_hp(f, fd) * h_dp(f, fh)
    # pasivní kaskáda bez oddělení: druhý článek zatěžuje první
    w = 2j * np.pi * f
    zc1, zc2 = 1 / (w * C1_), 1 / (w * C2_)
    zlp = R2 + zc2
    zp = R1 * zlp / (R1 + zlp)
    pas = zp / (zp + zc1) * zc2 / (R2 + zc2)
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.plot(f, db(ideal), color=C1, label="HP → sledovač → DP (články se neovlivňují)")
    ax.plot(f, db(pas), color=C2, ls="--", label="HP → DP přímo (druhý článek zatěžuje první)")
    for x, t, ofs in [(fd, "$f_d$", (7, -16)), (fh, "$f_h$", (-82, -16))]:
        ax.axvline(x, color=AXIS, lw=1, ls=":")
        ax.plot(x, -3.01, "o", color=INK, ms=6, mec=SURF)
        ax.annotate(f"{t} = {x:.3g} Hz".replace(".", ","), (x, -3), xytext=ofs, textcoords="offset points",
                    fontsize=9.5)
    ax.annotate("", xy=(fd, -14), xytext=(fh, -14), arrowprops=dict(arrowstyle="<->", color=INK2, lw=1.2))
    ax.text(np.sqrt(fd * fh), -17.5, "šířka pásma B = $f_h - f_d$", ha="center", fontsize=9.5, color=INK2)
    log_osa(ax, "frekvence f [Hz] (log. osa)")
    ax.set_xticks([0.01, 0.1, 1, 10, 100, 1000, 10000])
    ax.set_xticklabels(["0,01", "0,1", "1", "10", "100", "1 k", "10 k"])
    ax.set_ylabel("|H| [dB]")
    ax.set_ylim(-40, 6)
    ax.legend(loc="lower center", fontsize=9)
    ax.set_title("Pásmová propust pro EKG: 0,5–150 Hz", loc="left")
    save(fig, "fig02_bode_pp")


def fig02_pz_schema():
    with schema("fig02_pz_schema") as d:
        u = d.unit
        svorka(d, (0, 0), "$U_\\mathrm{vst}$")
        elm.Line().right(u * 0.4)
        a = elm.Dot()
        # horní T: R – R, příčně 2C
        elm.Line().up(u * 0.9)
        elm.Resistor().right().label("$R$")
        t1 = elm.Dot()
        elm.Resistor().right().label("$R$")
        elm.Line().down(u * 0.9)
        b = elm.Dot()
        elm.Line().right(u * 0.4)
        o = elm.Dot(open=True)
        elm.Capacitor().at(t1.center).down(u * 0.7).label("$2C$", loc="bottom")
        elm.Ground()
        # dolní T: C – C, příčně R/2
        elm.Line().at(a.center).down(u * 0.9)
        elm.Capacitor().right().label("$C$", loc="bottom")
        t2 = elm.Dot()
        elm.Capacitor().right().label("$C$", loc="bottom")
        elm.Line().up(u * 0.9)
        elm.Resistor().at(t2.center).down(u * 0.8).label("$R/2$", loc="bottom")
        elm.Ground()
        elm.Gap().at(o.center).down(u * 0.7).label(["", "$U_\\mathrm{výst}$", ""], loc="bottom")
        elm.Label().at((u * 0.5, u * 1.35)).label("dvojitý T-článek", fontsize=12, color=C1)


def h_twin_t(f, f0):
    s = 1j * f / f0
    return (s ** 2 + 1) / (s ** 2 + 4 * s + 1)


def fig02_bode_pz():
    f = np.logspace(0, 4, 2000)
    H = h_twin_t(f, 50)
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.plot(f, db(H), color=C1, label="dvojitý T-článek, $f_0$ = 50 Hz")
    ax.axvline(50, color=AXIS, lw=1, ls=":")
    ax.annotate("50 Hz: síťový brum\nje téměř úplně potlačen", (50, -38), xytext=(14, 0), textcoords="offset points",
                fontsize=9.5, color=INK2)
    lo, hi = 50 * (np.sqrt(5) - 2), 50 * (np.sqrt(5) + 2)
    for x in (lo, hi):
        ax.plot(x, -3.01, "o", color=INK, ms=6, mec=SURF)
    ax.annotate(f"−3 dB: {cz(lo, 1)} Hz", (lo, -3), xytext=(-110, -14), textcoords="offset points", fontsize=9)
    ax.annotate(f"−3 dB: {cz(hi, 0)} Hz", (hi, -3), xytext=(8, -14), textcoords="offset points", fontsize=9)
    log_osa(ax, "frekvence f [Hz] (log. osa)")
    ax.set_xticks([1, 10, 50, 100, 1000, 10000])
    ax.set_xticklabels(["1", "10", "50", "100", "1 k", "10 k"])
    ax.set_ylabel("|H| [dB]")
    ax.set_ylim(-45, 4)
    ax.legend(loc="lower right", fontsize=9)
    ax.set_title("Pásmová zádrž (notch) na 50 Hz", loc="left")
    save(fig, "fig02_bode_pz")


# =====================================================================  kapitola 3: operační zesilovače
def fig03_oz_symbol():
    with schema("fig03_oz_symbol") as d:
        op = elm.Opamp(leads=True)
        elm.Line().at(op.in1).left(d.unit * 0.3)
        elm.Dot(open=True).label("$U_-$ (invertující)", loc="left")
        elm.Line().at(op.in2).left(d.unit * 0.3)
        elm.Dot(open=True).label("$U_+$ (neinvertující)", loc="left")
        elm.Line().at(op.out).right(d.unit * 0.3)
        elm.Dot(open=True).label("$U_\\mathrm{výst} = A_0\\,(U_+ - U_-)$", loc="right")


def fig03_oz_char():
    A0, usat = 1e5, 13.0
    ud = np.linspace(-300e-6, 300e-6, 801)
    uo = np.clip(A0 * ud, -usat, usat)
    fig, ax = plt.subplots(figsize=(7.6, 3.5))
    ax.plot(ud * 1e6, uo, color=C1)
    ax.axvspan(-usat / A0 * 1e6, usat / A0 * 1e6, color=C1, alpha=0.08, lw=0)
    ax.text(-290, 4, "podbarvená lineární oblast:\njen ±130 µV", fontsize=9.5, color=INK2)
    ax.text(150, 10.5, "saturace +13 V", fontsize=9.5, color=INK2)
    ax.text(-290, -12, "saturace −13 V", fontsize=9.5, color=INK2)
    ax.set_xlabel("rozdílové napětí $U_d = U_+ - U_-$ [µV]")
    ax.set_ylabel("$U_\\mathrm{výst}$ [V]")
    ax.set_title("OZ bez zpětné vazby ($A_0 = 10^5$, napájení ±15 V)", loc="left")
    save(fig, "fig03_oz_char")


def _vstup_zem(d, op):
    elm.Line().at(op.in2).down(d.unit * 0.3)
    elm.Ground(lead=False)


def fig03_inv():
    with schema("fig03_inv") as d:
        op = elm.Opamp(leads=True)
        _vstup_zem(d, op)
        elm.Line().at(op.in1).left(d.unit * 0.25)
        n = elm.Dot()
        elm.Resistor().left().label("$R_1$", loc="bottom")
        elm.Dot(open=True).label("$U_\\mathrm{vst}$", loc="left")
        elm.Line().at(n.center).up(d.unit * 0.6)
        elm.Resistor().tox(op.out).label("$R_2$")
        elm.Line().toy(op.out).dot()
        elm.Line().at(op.out).right(d.unit * 0.35)
        elm.Dot(open=True).label("$U_\\mathrm{výst}$", loc="right")
        elm.Label().at((op.in1[0] - d.unit * 0.15, op.in1[1] - 0.15)).label("0 V", loc="bottom", fontsize=10,
                                                                             color=C2)


def fig03_neinv():
    with schema("fig03_neinv") as d:
        op = elm.Opamp(leads=True, flip=True).right()  # flip: neinvertující vstup (in2) nahoře, invertující (in1) dole
        elm.Line().at(op.in2).left(d.unit * 0.5)
        elm.Dot(open=True).label("$U_\\mathrm{vst}$", loc="left")
        elm.Line().at(op.in1).left(d.unit * 0.25)
        elm.Line().down(d.unit * 0.6)
        m = elm.Dot()
        elm.Resistor().right().tox(op.out).label("$R_2$", loc="bottom")
        elm.Line().up().toy(op.out).dot()
        elm.Line().at(m.center).left(d.unit * 0.3)
        elm.Resistor().down().label("$R_1$", loc="bottom")
        elm.Ground()
        elm.Line().at(op.out).right(d.unit * 0.35)
        elm.Dot(open=True).label("$U_\\mathrm{výst}$", loc="right")


def fig03_dif():
    with schema("fig03_dif") as d:
        op = elm.Opamp(leads=True)
        elm.Line().at(op.in1).left(d.unit * 0.25)
        n = elm.Dot()
        elm.Resistor().left().label("$R_1$", loc="bottom")
        elm.Dot(open=True).label("$U_1$", loc="left")
        elm.Line().at(n.center).up(d.unit * 0.6)
        elm.Resistor().tox(op.out).label("$R_2$")
        elm.Line().toy(op.out).dot()
        elm.Line().at(op.in2).left(d.unit * 0.25)
        p = elm.Dot()
        elm.Resistor().left().label("$R_3$", loc="bottom")
        elm.Dot(open=True).label("$U_2$", loc="left")
        elm.Resistor().at(p.center).down().label("$R_4$", loc="bottom")
        elm.Ground()
        elm.Line().at(op.out).right(d.unit * 0.35)
        elm.Dot(open=True).label("$U_\\mathrm{výst}$", loc="right")


def fig03_pristrojovy():
    # rozměry OZ v schemdraw (leads=True): vstupy ±0,625 od středu, tělo ±1,25, výstup 3,4 vpravo od vstupů
    with schema("fig03_pristrojovy", unit=2.4) as d:
        u = d.unit
        op1 = elm.Opamp(leads=True, flip=True).right().anchor("in2").at((0, 0))  # + nahoře, − dole
        elm.Line().at(op1.in2).left(0.8)
        elm.Dot(open=True).label("$U_1$", loc="left")
        elm.Line().at(op1.in1).down(1.2)
        p = elm.Dot()
        elm.Resistor().right().tox(op1.out).label("$R$", loc="bottom")
        elm.Line().up().toy(op1.out).dot()
        elm.Resistor().at(p.center).down().label("$R_G$", loc="top", color=C2).color(C2)
        q = elm.Dot()
        op2 = elm.Opamp(leads=True).right().anchor("in1").at((q.center[0], q.center[1] - 1.2))  # − nahoře
        elm.Line().at(q.center).down().toy(op2.in1)
        elm.Resistor().at(q.center).right().tox(op2.out).label("$R$")
        elm.Line().down().toy(op2.out).dot()
        elm.Line().at(op2.in2).left(0.8)
        elm.Dot(open=True).label("$U_2$", loc="left")
        # rozdílový stupeň
        ymid = (op1.out[1] + op2.out[1]) / 2
        op3 = elm.Opamp(leads=True).right().anchor("center").at((op1.out[0] + 5.2, ymid))
        elm.Line().at(op1.out).dot().right(0.7)
        elm.Line().down().toy(op3.in1)
        elm.Resistor().right().tox(op3.in1[0] - 0.5).label("$R_1$")
        n3 = elm.Dot()
        elm.Line().right().tox(op3.in1)
        elm.Line().at(n3.center).up(1.2)
        elm.Resistor().right().tox(op3.out).label("$R_2$")
        elm.Line().down().toy(op3.out).dot()
        elm.Line().at(op2.out).dot().right(0.7)
        elm.Line().up().toy(op3.in2)
        elm.Resistor().right().tox(op3.in2[0] - 0.5).label("$R_1$", loc="bottom")
        m3 = elm.Dot()
        elm.Line().right().tox(op3.in2)
        elm.Resistor().at(m3.center).down().label("$R_2$", loc="top")
        elm.Ground()
        elm.Line().at(op3.out).right(0.6)
        elm.Dot(open=True).label("$U_\\mathrm{výst}$", loc="right")
        elm.Label().at((op1.center[0], op1.center[1] + 1.9)).label("1. stupeň: dva neinvertující zesilovače",
                                                                   fontsize=11, color=C1)
        elm.Label().at((op3.center[0], op3.center[1] + 3.1)).label("2. stupeň: rozdílový zesilovač",
                                                                   fontsize=11, color=C1)


def fig03_cmrr():
    fs = 2000
    t = np.arange(0, 1.6, 1 / fs)
    ekg = np.zeros_like(t)
    for t0 in [0.25, 1.05]:          # dva „tepy“: vlna P, komplex QRS, vlna T (zjednodušeně Gaussovy pulzy)
        for dt, a, w in [(-0.18, 0.12, 0.025), (-0.03, -0.1, 0.008), (0, 1.0, 0.01), (0.03, -0.25, 0.01),
                         (0.25, 0.3, 0.04)]:
            ekg += a * np.exp(-0.5 * ((t - t0 - dt) / w) ** 2)
    ekg *= 1e-3                      # 1 mV
    rusení = 0.5 * np.sin(2 * np.pi * 50 * t)   # souhlasné rušení 0,5 V, 50 Hz
    u_plus = rusení + ekg / 2
    u_minus = rusení - ekg / 2
    Ad = 1000
    out_ok = Ad * (u_plus - u_minus) + (Ad / 10 ** (100 / 20)) * rusení     # CMRR 100 dB
    out_bad = Ad * (u_plus - u_minus) + (Ad / 10 ** (60 / 20)) * rusení     # CMRR 60 dB
    fig, axs = plt.subplots(3, 1, figsize=(7.6, 6.4), sharex=True)
    axs[0].plot(t, u_plus, color=C1, lw=0.9, label="$U_+$")
    axs[0].plot(t, u_minus, color=C2, lw=0.9, ls="--", label="$U_-$")
    axs[0].set_ylim(-0.7, 0.95)
    axs[0].set_ylabel("vstupy [V]")
    axs[0].set_title("Na vstupech: EKG (1 mV) se ztrácí v rušení 50 Hz (0,5 V)", loc="left")
    axs[0].legend(loc="upper right", ncol=2, fontsize=9)
    axs[1].plot(t, out_bad, color=C2, lw=1.2)
    axs[1].set_ylabel("výstup [V]")
    axs[1].set_title("Výstup, $A_d$ = 1000, CMRR = 60 dB: brum ±0,5 V zůstává", loc="left")
    axs[2].plot(t, out_ok, color=C1, lw=1.2)
    axs[2].set_ylabel("výstup [V]")
    axs[2].set_title("Výstup, $A_d$ = 1000, CMRR = 100 dB: brum jen ±5 mV", loc="left")
    axs[2].set_xlabel("čas t [s]")
    for ax in axs[1:]:
        ax.set_ylim(-0.7, 1.3)
    for ax in axs:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    save(fig, "fig03_cmrr")


# =====================================================================  kapitola 4: sledovač, integrátor, derivátor
def fig04_sledovac():
    with schema("fig04_sledovac") as d:
        op = elm.Opamp(leads=True, flip=True).right()  # + (in2) nahoře, − (in1) dole
        elm.Line().at(op.in2).left(d.unit * 0.5)
        elm.Dot(open=True).label("$U_\\mathrm{vst}$", loc="left")
        elm.Line().at(op.in1).left(d.unit * 0.25)
        elm.Line().down(d.unit * 0.5)
        elm.Line().right().tox(op.out)
        elm.Line().up().toy(op.out).dot()
        elm.Line().at(op.out).right(d.unit * 0.35)
        elm.Dot(open=True).label("$U_\\mathrm{výst} = U_\\mathrm{vst}$", loc="right")


def fig04_sledovac_delic():
    with schema("fig04_sledovac_delic") as d:
        u = d.unit
        svorka(d, (0, 0), "$U_1$ = 10 V")
        elm.Line().right(u * 0.3)
        elm.Resistor().down().label("$R_1$ = 10 kΩ", loc="top")
        n = elm.Dot()
        elm.Resistor().down().label("$R_2$ = 10 kΩ", loc="top")
        elm.Ground()
        op = elm.Opamp(leads=True, flip=True).right().anchor("in2").at((n.center[0] + u * 1.0, n.center[1]))
        elm.Line().at(n.center).right().tox(op.in2)
        elm.Line().at(op.in1).left(u * 0.2)
        elm.Line().down(u * 0.4)
        elm.Line().right().tox(op.out)
        elm.Line().up().toy(op.out).dot()
        elm.Line().at(op.out).right(u * 0.5)
        z = elm.Dot()
        elm.Resistor().down().label("$R_\\mathrm{z}$ = 1 kΩ", loc="bottom", color=C2).color(C2)
        elm.Ground()
        elm.Label().at((z.center[0], z.center[1] + 0.45)).label("5 V", fontsize=11, color=C1)
        elm.Label().at((n.center[0] - 0.35, n.center[1] + 0.45)).label("5 V", fontsize=11, color=C1)


def _oz_inv_rc(name, vstup, zpetna, lbl_v, lbl_z):
    with schema(name) as d:
        op = elm.Opamp(leads=True)
        _vstup_zem(d, op)
        elm.Line().at(op.in1).left(d.unit * 0.25)
        n = elm.Dot()
        vstup().left().label(lbl_v, loc="bottom")
        elm.Dot(open=True).label("$U_\\mathrm{vst}$", loc="left")
        elm.Line().at(n.center).up(d.unit * 0.6)
        zpetna().tox(op.out).label(lbl_z)
        elm.Line().toy(op.out).dot()
        elm.Line().at(op.out).right(d.unit * 0.35)
        elm.Dot(open=True).label("$U_\\mathrm{výst}$", loc="right")


def fig04_integrator():
    _oz_inv_rc("fig04_integrator", elm.Resistor, elm.Capacitor, "$R$", "$C$")


def fig04_derivator():
    _oz_inv_rc("fig04_derivator", elm.Capacitor, elm.Resistor, "$C$", "$R$")


def fig04_prubehy():
    t = np.linspace(0, 40e-3, 4001)
    RC = 10e-3
    T = 20e-3
    sq = np.where((t % T) < T / 2, 1.0, -1.0)
    integ = -np.cumsum(sq) * (t[1] - t[0]) / RC
    integ -= (integ.max() + integ.min()) / 2
    tri = 2 * np.abs(2 * ((t / T) % 1) - 1) - 1          # trojúhelník ±1 V, perioda 20 ms
    tri = -tri
    RCd = 1e-3
    der = -RCd * np.gradient(tri, t)
    fig, axs = plt.subplots(2, 2, figsize=(9.2, 4.6), sharex=True)
    ms = t * 1e3
    axs[0, 0].plot(ms, sq, color=C1)
    axs[0, 0].set_title("Integrátor – vstup: obdélník ±1 V", loc="left")
    axs[1, 0].plot(ms, integ, color=C2)
    axs[1, 0].set_title("výstup: trojúhelník (RC = 10 ms)", loc="left")
    axs[0, 1].plot(ms, tri, color=C1)
    axs[0, 1].set_title("Derivátor – vstup: trojúhelník ±1 V", loc="left")
    axs[1, 1].plot(ms, der, color=C2)
    axs[1, 1].set_title("výstup: obdélník (RC = 1 ms)", loc="left")
    for ax in axs[:, 0]:
        ax.set_ylabel("U [V]")
    for ax in axs[1]:
        ax.set_xlabel("čas t [ms]")
    for ax in axs.flat:
        ax.set_ylim(-1.4, 1.4)
    save(fig, "fig04_prubehy")


# =====================================================================  přednáška 1: úvod, signál
def fig11_signaly():
    t = np.linspace(0, 1, 801)
    x = lambda tt: 0.6 + 0.35 * np.sin(2 * np.pi * 1.1 * tt + 0.3) - 0.25 * tt ** 2   # libovolný hladký průběh
    n = np.linspace(0, 1, 13)
    q = 0.2                                                                       # krok kvantování
    fig, axs = plt.subplots(2, 2, figsize=(8.8, 5.2), sharex=True, sharey=True)
    a, b, c, dd = axs.flat
    a.plot(t, x(t), color=C1)
    a.set_title("a) analogový $x(t)$", loc="left")
    b.vlines(n, 0, x(n), color=C1, lw=1.4)
    b.plot(n, x(n), "o", color=C1, mec=SURF, ms=6)
    b.plot(t, x(t), color=MUTED, ls=":", lw=1.2)
    b.set_title("b) diskrétní v čase $x(n)$", loc="left")
    c.plot(t, q * np.round(x(t) / q), color=C2, drawstyle="steps-post")
    c.set_title("c) víceúrovňový, spojitý v čase $x_q(t)$", loc="left")
    xq = q * np.round(x(n) / q)
    dd.vlines(n, 0, xq, color=C2, lw=1.4)
    dd.plot(n, xq, "s", color=C2, mec=SURF, ms=6)
    dd.plot(t, x(t), color=MUTED, ls=":", lw=1.2)
    dd.set_title("d) číslicový (vzorkovaný a kvantovaný) $x_q(n)$", loc="left")
    for ax in (c, dd):
        for lv in np.arange(0, 1.01, q):
            ax.axhline(lv, color=AXIS, ls="--", lw=0.8, zorder=0)
    for ax in axs.flat:
        ax.set_ylim(0, 1.0)
        ax.set_yticks([])
        ax.set_xticks([])
    a.set_ylabel("amplituda spojitá")
    c.set_ylabel("amplituda kvantovaná")
    c.set_xlabel("čas spojitý")
    dd.set_xlabel("čas diskrétní (vzorky)")
    save(fig, "fig11_signaly")


def fig11_zdroj():
    i = np.linspace(0, 1.2e-3, 200)
    Ue = 1.0
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.plot(i * 1e3, np.full_like(i, Ue), color=MUTED, ls="--", lw=1.6, label="ideální zdroj ($R_i = 0$)")
    ax.plot(i * 1e3, Ue - 50 * i, color=C1, label="tvrdý zdroj ($R_i$ = 50 Ω)")
    ax.plot(i[i <= 1e-3] * 1e3, Ue - 1e3 * i[i <= 1e-3], color=C2, label="měkký zdroj ($R_i$ = 1 kΩ)")
    ax.plot(1.0, 0, "o", color=C2, mec=SURF, ms=7)
    ax.annotate("zkratový proud\n$I_z = U_e / R_i$ = 1 mA", (1.0, 0), xytext=(1.03, 0.25), fontsize=9.5,
                color=INK2, ha="left", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xlabel("odebíraný proud $I$ [mA]")
    ax.set_ylabel("svorkové napětí $U$ [V]")
    ax.set_ylim(0, 1.15)
    ax.set_xlim(0, 1.2)
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 0.18))
    ax.set_title("Zatěžovací charakteristika zdroje $U = U_e - R_i I$ ($U_e$ = 1 V)", loc="left")
    for f in (ax.xaxis, ax.yaxis):
        f.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    save(fig, "fig11_zdroj")


def fig11_iu():
    with schema("fig11_iu") as d:
        op = elm.Opamp(leads=True)
        _vstup_zem(d, op)
        elm.Line().at(op.in1).left(d.unit * 0.25)
        n = elm.Dot()
        w = elm.Line().left(d.unit * 1.0)
        elm.Dot(open=True).label("vstup proudu", loc="left")
        elm.CurrentLabelInline(direction="out", ofst=0.3).at(w).label("$i_1$", loc="top")
        elm.Line().at(n.center).up(d.unit * 0.6)
        elm.Resistor().tox(op.out).label("$R$")
        elm.Line().toy(op.out).dot()
        elm.Line().at(op.out).right(d.unit * 0.35)
        elm.Dot(open=True).label("$U_2 = -i_1 R$", loc="right")
        elm.Label().at((n.center[0] - 0.55, n.center[1] - 0.45)).label("$U_1$ = 0", fontsize=11, color=C2)


def _shunt(d, x0, high):
    """Snímací rezistor nad zátěží (high-side) nebo pod ní (low-side) a rozdílové měření úbytku."""
    u = d.unit
    elm.Line().at((x0, 0)).up(0.01)
    elm.Label().at((x0, 0.25)).label("$V_\\mathrm{SUPPLY}$", fontsize=12)
    prvky = [("$R_\\mathrm{SENSE}$", elm.Resistor, C2), ("zátěž", elm.Resistor, INK)]
    if not high:
        prvky.reverse()
    uzly = [(x0, 0)]
    for lbl, el, col in prvky:
        e = el().at(uzly[-1]).down().label(lbl, loc="top", color=col).color(col)
        uzly.append(e.end)
    elm.Ground().at(uzly[-1])
    rs = 0 if high else 1                                   # index horního konce snímacího rezistoru
    op = elm.Opamp(leads=True, flip=True).right().anchor("in2").at((x0 + u * 0.9, uzly[rs][1] - 0.3))
    elm.Line().at(uzly[rs]).right(u * 0.35).dot()
    elm.Line().toy(op.in2)
    elm.Line().tox(op.in2)
    elm.Line().at(uzly[rs + 1]).right(u * 0.2)
    elm.Line().toy(op.in1)
    elm.Line().tox(op.in1)
    elm.Dot().at(uzly[rs + 1])
    elm.Line().at(op.out).right(u * 0.3)
    elm.Dot(open=True).label("výstup", loc="right")
    elm.Label().at((x0 + u * 1.4, 0.75)).label("High-Side" if high else "Low-Side", fontsize=13,
                                               color=C1 if high else C3)


def fig11_shunt():
    with schema("fig11_shunt", unit=2.2) as d:
        _shunt(d, 0, True)
        _shunt(d, d.unit * 4.6, False)


def fig11_trafo():
    with schema("fig11_trafo", unit=2.4) as d:
        u = d.unit
        t = elm.Transformer(t1=5, t2=5, core=True)
        w = elm.Line().at(t.p1).left(u * 0.8)
        elm.CurrentLabelInline(direction="out", ofst=0.0).at(w).label("$I_P$", loc="top")
        elm.SourceSin().down().toy(t.p2).label("$V_P$", loc="bottom")
        elm.Line().tox(t.p2)
        w2 = elm.Line().at(t.s1).right(u * 0.8)
        elm.CurrentLabelInline(direction="in", ofst=0.0).at(w2).label("$I_S$", loc="top")
        elm.Resistor().down().toy(t.s2).label("$R_B$", loc="bottom")
        elm.Line().tox(t.s2)
        xm = (t.p1[0] + t.s1[0]) / 2
        elm.Label().at((xm, t.p1[1] + 0.55)).label("$N_P : N_S$", fontsize=13)
        elm.Label().at((t.s1[0] + u * 0.45, (t.s1[1] + t.s2[1]) / 2)).label("$V_S$", fontsize=13)
        elm.Label().at((xm, t.s2[1] - 0.9)).label(
            "$\\frac{V_P}{V_S} = \\frac{I_S}{I_P} = \\frac{N_P}{N_S}$", fontsize=18, color=C1)


def fig11_fu_schema():
    with schema("fig11_fu_schema", unit=2.0) as d:
        u = d.unit
        a = elm.Opamp(leads=True, flip=True).right().label("OZA", loc="center", ofst=(-0.35, 0), fontsize=11)
        elm.Line().at(a.in2).left(u * 0.3)
        elm.Dot(open=True).label("$u_1$", loc="left")
        elm.Line().at(a.in1).left(u * 0.15)
        elm.Ground(lead=False)
        elm.Resistor().at(a.out).right().label("$R_1$")
        elm.Capacitor().right().label("$C_1$")
        n = elm.Dot()
        elm.Diode().at(n.center).down().label("$D_1$", loc="bottom")
        elm.Ground()
        elm.Line().at(n.center).up(u * 0.5)
        elm.Diode().right(u * 0.9).reverse().label("$D_2$")
        m = elm.Dot()
        b = elm.Opamp(leads=True).right().anchor("in1").at((m.center[0] + u * 0.25, m.center[1])).label(
            "OZB", loc="center", ofst=(-0.35, 0), fontsize=11)
        elm.Line().at(m.center).tox(b.in1)
        elm.Line().at(b.in2).down(u * 0.15)
        elm.Ground(lead=False)
        elm.Line().at(m.center).up(u * 0.55)
        k = elm.Dot()
        elm.Capacitor().right().tox(b.out).label("$C_A$")
        q = elm.Dot()
        elm.Line().at(k.center).up(u * 0.6)
        elm.Resistor().right().tox(b.out).label("$R_A$")
        elm.Line().down().toy(q.center)
        elm.Line().at(q.center).toy(b.out).dot()
        elm.Line().at(b.out).right(u * 0.3)
        elm.Dot(open=True).label("$u_0$", loc="right")


def fig11_fu_prubeh():
    Us, C1f, RA, CA = 13.0, 1e-9, 100e3, 1e-6
    tau = RA * CA
    dU = 2 * C1f * Us / CA                                   # skok napětí na C_A po jedné pumpě (Q1 / C_A)
    fig = plt.figure(figsize=(8.6, 6.0))
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 1, 1.7])
    a1 = fig.add_subplot(gs[0])
    a2 = fig.add_subplot(gs[1], sharex=a1)
    a3 = fig.add_subplot(gs[2])
    t = np.linspace(0, 3e-3, 3001)
    u1 = np.sin(2 * np.pi * 1e3 * t)
    a1.plot(t * 1e3, u1, color=C1)
    a1.set_ylabel("$u_1$ [V]")
    a1.set_title("Vstup $u_1$ (sinus 1 kHz) a výstup komparátoru OZA (obdélník ±$U_\\mathrm{SAT}$)", loc="left")
    a2.plot(t * 1e3, np.where(u1 >= 0, Us, -Us), color=C2)
    a2.set_ylabel("OZA [V]")
    a2.set_xlabel("čas t [ms]")
    a2.set_yticks([-13, 0, 13])
    plt.setp(a1.get_xticklabels(), visible=False)
    for f, col, mk in [(1e3, C1, "o"), (500, C3, "^")]:
        T = 1 / f
        tt, uu, v = [], [], 0.0
        for k in range(int(0.6 / T)):
            s = np.linspace(0, T, 20, endpoint=False)
            tt.append(k * T + s)
            uu.append(v * np.exp(-s / tau))
            v = v * np.exp(-T / tau) + dU                    # na konci periody vybití + načerpaný náboj
        tt, uu = np.concatenate(tt), np.concatenate(uu)
        a3.plot(tt * 1e3, uu, color=col, lw=1.6, label=f"f = {f:g} Hz")
        ust = 2 * Us * C1f * RA * f
        a3.axhline(ust, color=col, ls="--", lw=1.0)
        a3.annotate(f"$u_0 = 2U_\\mathrm{{SAT}}C_1R_Af$ = {cz(ust, 1)} V", (600, ust), xytext=(-4, 5),
                    textcoords="offset points", ha="right", fontsize=9.5, color=INK2)
    a3.set_xlabel("čas t [ms]")
    a3.set_ylabel("$u_0$ [V]")
    a3.set_ylim(0, 3.1)
    a3.set_xlim(0, 600)
    a3.legend(loc="lower right")
    a3.set_title("Výstup $u_0$ se ustálí na hodnotě úměrné frekvenci ($R_AC_A$ = 100 ms)", loc="left")
    a3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    save(fig, "fig11_fu_prubeh")


def fig11_rx():
    with schema("fig11_rx") as d:
        op = elm.Opamp(leads=True)
        _vstup_zem(d, op)
        elm.Line().at(op.in1).left(d.unit * 0.25)
        n = elm.Dot()
        w = elm.Line().left(d.unit * 0.6)
        elm.CurrentLabelInline(direction="out", ofst=0.0).at(w).label("$I_N$", loc="top")
        elm.Resistor().left().label("$R_N$", loc="bottom")
        elm.Dot(open=True).label("$U_\\mathrm{REF}$", loc="left")
        elm.Line().at(n.center).up(d.unit * 0.6)
        elm.Resistor().tox(op.out).label("$R_X$", color=C2).color(C2)
        elm.Line().toy(op.out).dot()
        elm.Line().at(op.out).right(d.unit * 0.35)
        elm.Dot(open=True).label("$U_X$", loc="right")


def fig11_mustek():
    with schema("fig11_mustek", unit=3.0) as d:
        u = d.unit
        s = u / np.sqrt(2)                                   # vodorovný i svislý průmět šikmého rezistoru
        A = (0, 0)
        D = elm.Resistor().at(A).theta(-135).end
        C = elm.ResistorVar().at(D).theta(-45).end
        B = elm.Resistor().at(A).theta(-45).end
        elm.Resistor().at(B).theta(-135).color(C2)
        for xy, lbl, col in [((-s / 2 - 0.55, -s / 2 + 0.4), "$R_1$", INK), ((s / 2 + 0.55, -s / 2 + 0.4), "$R_3$", INK),
                             ((-s / 2 - 1.05, -1.5 * s - 0.4), "$R_2$ (trimr)", INK),
                             ((s / 2 + 0.55, -1.5 * s - 0.4), "$R_X$", C2)]:
            elm.Label().at(xy).label(lbl, fontsize=14, color=col)
        for p, lbl, ofs in [(A, "A", (0.35, 0.2)), (B, "B", (0.35, 0)), (C, "C", (0.35, -0.2)), (D, "D", (-0.35, 0.25))]:
            elm.Dot().at(p)
            elm.Label().at((p[0] + ofs[0], p[1] + ofs[1])).label(lbl, fontsize=14)
        elm.Line().at(D).right(s * 0.5)
        elm.MeterV().right().tox((B[0] - s * 0.5, D[1]))
        elm.Line().tox(B)
        elm.Label().at((0, D[1] + 0.75)).label("$V_G$", fontsize=13)
        elm.Line().at(A).up(u * 0.25)
        elm.Line().left(s + u * 0.45)
        elm.Battery().down().toy(C[1] - u * 0.25).reverse()
        elm.Line().tox(C)
        elm.Line().toy(C)
        elm.Label().at((-s - u * 0.45 - 0.5, D[1])).label("$U$", fontsize=14)


# =====================================================================  přednáška 2: úprava signálu
def fig12_beta():
    ib = np.linspace(0, 27.5, 100)                               # µA
    beta = 384                                                   # z trojúhelníku na slidu: 3,84 mA / 10 µA
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.plot(ib, beta * ib * 1e-3, color=C1)
    ax.plot([10, 20, 20], [3.84, 3.84, 7.68], color=C2, lw=1.4)
    ax.plot([10, 20], [3.84, 7.68], "o", color=C2, mec=SURF, ms=6)
    ax.text(15, 3.2, "$\\Delta i_B$ = 10 µA", ha="center", fontsize=9.5, color=INK2)
    ax.text(20.6, 5.6, "$\\Delta i_C$ = 3,84 mA", fontsize=9.5, color=INK2)
    ax.text(1, 8.6, "$\\beta = \\Delta i_C / \\Delta i_B$ = 3,84 mA / 10 µA = 384", fontsize=10.5, color=C1)
    ax.set_xlabel("proud bází $i_B$ [µA]")
    ax.set_ylabel("proud kolektorem $i_C$ [mA]")
    ax.set_xlim(0, 27.5)
    ax.set_ylim(0, 10.5)
    ax.set_title("Proud kolektorem je β-násobkem proudu bází (podle slidu)", loc="left")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    save(fig, "fig12_beta")


def _stupen(name, q, r1, c1, c2, rc=None, r2=None, re=None, zv=False, sc=False, lc=None, fet=False):
    """Tranzistorový stupeň jako na slidech: napájení nahoře, 0 V dole, vstup přes C1 do báze (gate),
    výstup přes C2 z kolektoru (drainu), u SC / SD z emitoru (source)."""
    with schema(name, unit=1.9) as d:
        u = d.unit
        if fet:
            t = elm.NFet(bulk=True).reverse().anchor("gate").at((0, 0)).label(q, loc="right", ofst=(0.1, 0))
            hor, dol, vst = t.drain, t.source, "gate"
        else:
            t = elm.BjtNpn(circle=True).anchor("base").at((0, 0)).label(q, loc="right")
            hor, dol, vst = t.collector, t.emitter, "base"
        xt = hor[0]
        ytop = hor[1] + u * (1.75 if lc else 1.35)
        ybot = dol[1] - u * 1.25
        xb, xl, xo = (-u * 1.15, -u * 2.75, xt + u * 1.6) if lc else (-u * 0.75, -u * 2.35, xt + u * 1.6)
        # horní větev (kolektor / drain)
        if sc:
            elm.Line().at(hor).toy(ytop)
            nc = None
        else:
            nc = elm.Line().at(hor).up(u * 0.3).dot().end
            if lc:
                a = elm.Line().at(nc).up(u * 0.15).end
                elm.Line().at(a).left(u * 0.35)
                elm.Capacitor().up(u * 0.85).label(lc[0], loc="top")
                elm.Line().right(u * 0.35)
                elm.Line().at(a).right(u * 0.35)
                elm.Inductor2(loops=3).up(u * 0.85).label(lc[1], loc="bottom")
                elm.Line().left(u * 0.35)
                elm.Line().at((xt, a[1] + u * 0.85)).toy(ytop)
            else:
                elm.Resistor().at(nc).up().toy(ytop).label(rc, loc="bottom")
        # dolní větev (emitor / source)
        if re:
            ne = elm.Line().at(dol).down(u * 0.15).dot().end if sc else dol
            elm.Resistor().at(ne).down().toy(ybot).label(re, loc="bottom")
        else:
            ne = dol
            elm.Line().at(dol).toy(ybot)
        # báze / gate a předpětí
        nb = elm.Line().at(getattr(t, vst)).tox(xb).dot().end
        if zv:
            elm.Line().at(nb).toy(nc[1])
            elm.Resistor().right().tox(nc).label(r1)
        else:
            elm.Resistor().at(nb).up().toy(ytop).label(r1, loc="top")
        if r2:
            elm.Resistor().at(nb).down().toy(ybot).label(r2, loc="bottom")
        elm.Capacitor(polar=not fet).at(nb).left().tox(xl + u * 0.35).reverse().label(c1, loc="bottom")
        elm.Line().tox(xl)
        svorka(d, (xl, 0), "$V_\\mathrm{IN}$")
        # výstup
        nout = ne if sc else nc
        elm.Capacitor(polar=True).at(nout).right().tox(xo - u * 0.35).label(c2, loc="bottom")
        elm.Line().tox(xo)
        svorka(d, (xo, nout[1]), "$V_\\mathrm{OUT}$", loc="right")
        # napájecí a zemní vodič
        elm.Line().at((xl, ytop)).tox(xt)
        elm.Line().at((xl, ybot)).tox(xo)
        svorka(d, (xl, ytop), "$V_\\mathrm{DD}$ 15 V" if fet else "$V_\\mathrm{CC}$ 15 V")
        svorka(d, (xl, ybot), "0 V")
        svorka(d, (xo, ybot), "", loc="right")


def fig12_se():
    _stupen("fig12_se", "Q1 BC548", "$R_1$ 4M7", "$C_1$ 820n", "$C_2$ 1µ", rc="$R_2$ 7k5")


def fig12_se_zv():
    _stupen("fig12_se_zv", "Q1 BC548", "$R_1$ 2M2", "$C_1$ 820n", "$C_2$ 1µ", rc="$R_2$ 7k5", zv=True)


def fig12_se_delic():
    _stupen("fig12_se_delic", "Q1 BC548", "$R_1$ 240k", "$C_1$ 330n", "$C_2$ 1µ", rc="$R_3$ 7k5",
            r2="$R_2$ 33k", re="$R_4$ 1k")


def fig12_sc():
    _stupen("fig12_sc", "Q1 BC548", "$R_1$ 130k", "$C_1$ 120n", "$C_2$ 1µ", r2="$R_2$ 160k", re="$R_3$ 7k5",
            sc=True)


def fig12_selektivni():
    _stupen("fig12_selektivni", "Q1 2N2222", "$R_1$ 240k", "$C_1$ 330n", "$C_2$ 1µ", r2="$R_2$ 33k",
            re="$R_4$ 1k", lc=("$C_3$ 820p", "$L_1$ 3m3"))


def fig12_mosfet_ss():
    _stupen("fig12_mosfet_ss", "Q1 ZVN3306A", "$R_1$ 910k", "$C_1$ 33n", "$C_2$ 220µ", rc="$R_3$ 36R",
            r2="$R_2$ 330k", fet=True)


def fig12_mosfet_sd():
    _stupen("fig12_mosfet_sd", "Q1 ZVN3306A", "$R_1$ 910k", "$C_1$ 33n", "$C_2$ 220µ", r2="$R_2$ 330k",
            re="$R_3$ 36R", sc=True, fet=True)


def _ic_bias(beta):
    """Klidový proud kolektoru tří zapojení SE ze slidů v závislosti na β (U_BE = 0,7 V)."""
    vcc, ube = 15.0, 0.7
    ic_r1 = beta * (vcc - ube) / 4.7e6                                 # R1 4M7 z napájení do báze
    k = 7.5e3 * (beta + 1) / 2.2e6                                     # R1 2M2 z kolektoru do báze
    ic_zv = beta * ((vcc + k * ube) / (1 + k) - ube) / 2.2e6
    uth, rth = vcc * 33 / 273, 240e3 * 33e3 / 273e3                    # dělič 240k/33k (Théveninův zdroj), R4 1k
    ic_del = beta * (uth - ube) / (rth + (beta + 1) * 1e3)
    return ic_r1, ic_zv, ic_del


def fig12_stabilita():
    b = np.linspace(100, 800, 200)
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    for y, col, mk, lbl in zip(_ic_bias(b), CAT, MARK, ["$R_1$ z napájení do báze (slide 6)",
                                                        "$R_1$ z kolektoru do báze (slide 8)",
                                                        "dělič $R_1$–$R_2$ a $R_4$ v emitoru (slide 9)"]):
        y = np.minimum(y, 2e-3)
        ax.plot(b, y * 1e3, color=col, label=lbl)
        bb = np.array([200, 400, 600])
        ax.plot(bb, np.interp(bb, b, y) * 1e3, mk, color=col, mec=SURF, ms=7)
    ax.axhline(2.0, color=MUTED, ls="--", lw=1.0)
    ax.text(790, 2.04, "saturace: celé napájení na rezistoru 7k5 v kolektoru", fontsize=9, color=INK2,
            va="bottom", ha="right")
    ax.set_xlabel("proudový zesilovací činitel β")
    ax.set_ylabel("klidový proud $I_C$ [mA]")
    ax.set_ylim(0, 2.35)
    ax.set_xlim(100, 800)
    ax.legend(loc="lower right")
    ax.set_title("Jak se pracovní bod mění s β (různé kusy tranzistoru, teplota)", loc="left")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    save(fig, "fig12_stabilita")


def fig12_darlington():
    with schema("fig12_darlington", unit=2.0) as d:
        u = d.unit
        t1 = elm.BjtNpn(circle=True).anchor("base").at((0, 0)).label("$T_1$", loc="right")
        t2 = elm.BjtNpn(circle=True).anchor("base").at((t1.emitter[0] + u * 0.35, t1.emitter[1] - u * 0.45)).label(
            "$T_2$", loc="right")
        elm.Line().at(t1.emitter).toy(t2.base)
        elm.Line().tox(t2.base)
        ytop = t1.collector[1] + u * 0.5
        elm.Line().at(t1.collector).toy(ytop).dot()
        elm.Line().at(t2.collector).toy(ytop)
        elm.Line().tox(t1.collector)
        elm.Line().at((t2.collector[0], ytop)).up(u * 0.3)
        elm.Dot(open=True).label("C", loc="top")
        elm.Line().at(t1.base).left(u * 0.5)
        elm.Dot(open=True).label("B", loc="left")
        elm.Line().at(t2.emitter).down(u * 0.4)
        elm.Dot(open=True).label("E", loc="bottom")
        elm.Label().at((t1.emitter[0] - 0.75, (t1.emitter[1] + t2.base[1]) / 2)).label(
            "$i_{E1} = i_{B2}$", fontsize=11, color=C2)
        elm.Label().at((t2.collector[0] + u * 1.5, t1.base[1] - 0.2)).label(
            "$\\beta \\approx \\beta_1 \\cdot \\beta_2$", fontsize=16, color=C1)


def fig12_rozdilovy():
    with schema("fig12_rozdilovy", unit=2.0) as d:
        u = d.unit
        q1 = elm.BjtNpn(circle=True).anchor("base").at((0, 0))
        q2 = elm.BjtNpn(circle=True).reverse().anchor("base").at((q1.emitter[0] * 2 + u * 0.9, 0))
        elm.Label().at((q1.emitter[0] - 0.9, q1.emitter[1] - 0.6)).label("Q1 BC548", fontsize=11)
        elm.Label().at((q2.emitter[0] + 0.9, q2.emitter[1] - 0.6)).label("Q2 BC548", fontsize=11)
        ytop = q1.collector[1] + u * 1.3
        elm.Resistor().at(q1.collector).up().toy(ytop).label("$R_1$ 75k", loc="top")
        n2 = elm.Line().at(q2.collector).up(u * 0.3).dot().end
        elm.Resistor().at(n2).up().toy(ytop).label("$R_2$ 75k", loc="bottom")
        elm.Line().at(n2).right(u * 1.1)
        elm.Dot(open=True).label("$V_\\mathrm{OUT}$", loc="right")
        xm = (q1.emitter[0] + q2.emitter[0]) / 2
        ye = q1.emitter[1] - u * 0.35
        elm.Line().at(q1.emitter).toy(ye)
        elm.Line().tox(q2.emitter)
        elm.Line().toy(q2.emitter)
        elm.Dot().at((xm, ye))
        elm.Resistor().at((xm, ye)).down().label("$R_3$ 75k", loc="bottom")
        elm.Dot(open=True).label("$V_\\mathrm{EE}$ −15 V", loc="bottom")
        elm.Line().at((q1.collector[0] - u * 0.9, ytop)).tox(q2.collector)
        elm.Dot(open=True).at((q1.collector[0] - u * 0.9, ytop)).label("+15 V", loc="left")
        elm.Line().at(q1.base).left(u * 0.4)
        elm.Dot(open=True).label("$V_\\mathrm{in+}$", loc="left")
        elm.Line().at(q2.base).right(u * 0.4)
        elm.Dot(open=True).label("$V_\\mathrm{in-}$", loc="right")


def fig12_rozdilovy_prubeh():
    t = np.linspace(0, 2.9, 1000)
    vp = 120 * np.sin(2 * np.pi * t)                             # mV, jako na slidu: 1 Hz, posun o čtvrt periody
    vm = -120 * np.cos(2 * np.pi * t)
    vo = 5 * (vp - vm)                                           # zesílení 5 odpovídá amplitudám na slidu
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.plot(t, vo, color=C1, label="$V_\\mathrm{OUT}$ = 5 · ($V_\\mathrm{in+} - V_\\mathrm{in-}$)")
    ax.plot(t, vp, color=C2, lw=1.6, label="$V_\\mathrm{in+}$")
    ax.plot(t, vm, color=C3, lw=1.6, ls="--", label="$V_\\mathrm{in-}$")
    ax.set_xlabel("čas t [s]")
    ax.set_ylabel("napětí (střídavá složka) [mV]")
    ax.set_ylim(-950, 1300)
    ax.set_xlim(0, 2.9)
    ax.legend(loc="upper left", ncol=3)
    ax.set_title("Výstup sleduje rozdíl vstupů, ne vstupy samotné (podle grafu na slidu)", loc="left")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    save(fig, "fig12_rozdilovy_prubeh")


def fig12_mosfet_char():
    v = np.linspace(1.5, 3.6, 300)
    k = 50 / 0.9 ** 2                                            # mA/V², aby 2,7 V → 50 mA jako na slidu
    i = np.where(v > 1.8, k * (v - 1.8) ** 2, 0)
    fig, ax = plt.subplots(figsize=(7.6, 3.5))
    ax.plot(v, i, color=C1)
    ax.axvline(1.8, color=C2, ls="--", lw=1.2)
    ax.text(1.84, 165, "prahové napětí\n$V_\\mathrm{th}$ = 1,8 V", fontsize=9.5, color=C2)
    ax.text(1.52, 12, "pod prahem\nnevede", fontsize=9.5, color=INK2)
    ax.set_xlabel("napětí gate–source $V_\\mathrm{GS}$ [V]")
    ax.set_ylabel("proud drainem $i_D$ [mA]")
    ax.set_xlim(1.5, 3.6)
    ax.set_ylim(0, 210)
    ax.set_title("Převodní charakteristika n-kanálového MOSFETu (práh podle slidu)", loc="left")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    save(fig, "fig12_mosfet_char")


def fig12_spinace():
    with schema("fig12_spinace", unit=2.0) as d:
        u = d.unit
        elm.Dot(open=True).at((0, 0)).label("$V_\\mathrm{IN}$", loc="left")
        elm.Resistor().right().label("$R_1$ 22k")
        n = elm.Dot().center
        elm.Line().at(n).right(u * 0.9)
        elm.Dot(open=True).label("$V_\\mathrm{OUT}$", loc="right")
        f = elm.NFet(bulk=True).theta(0).reverse().anchor("drain").at(n)
        elm.Label().at((f.drain[0] + 1.2, f.gate[1] - 0.15)).label("ZVN4210", fontsize=11)
        elm.Line().at(f.bulk).toy(f.source)                     # substrát spojený se source (jako na slidu)
        elm.Line().at(f.gate).left(u * 0.4)
        elm.Dot(open=True).label("control", loc="left")
        elm.Line().at(f.source).down(u * 0.2)
        elm.Ground(lead=False)
        elm.Label().at((u * 0.6, 1.5)).label("a) spínač k zemi", fontsize=12, color=C1)
        x0 = u * 4.3
        g = elm.NFet(bulk=True).theta(0).reverse().anchor("drain").at((x0, 0))
        elm.Line().at(g.drain).up(u * 0.3)
        elm.Dot(open=True).label("$V_\\mathrm{IN}$ / $V_\\mathrm{OUT}$", loc="right")
        elm.Line().at(g.source).down(u * 0.3)
        elm.Dot(open=True).label("$V_\\mathrm{OUT}$ / $V_\\mathrm{IN}$", loc="right")
        elm.Line().at(g.gate).left(u * 0.4)
        elm.Dot(open=True).label("control", loc="left")
        elm.Line().at(g.bulk).right(u * 0.35)
        elm.Ground()
        elm.Label().at((x0, 1.5)).label("b) sériový spínač", fontsize=12, color=C3)


def fig12_slew():
    t = np.linspace(0, 40, 8000)                                 # µs
    f, up, sr = 50e-3, 10.0, 1.0                                 # 50 kHz (v 1/µs), amplituda 10 V, SR 1 V/µs
    want = up * np.sin(2 * np.pi * f * t)
    out = np.zeros_like(t)
    dt = t[1] - t[0]
    for k in range(1, len(t)):
        out[k] = out[k - 1] + np.clip(want[k] - out[k - 1], -sr * dt, sr * dt)
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.plot(t, want, color=MUTED, ls="--", lw=1.6, label="požadovaný výstup (sinus 50 kHz, 10 V)")
    ax.plot(t, out, color=C1, label="skutečný výstup OZ se SR = 1 V/µs")
    ax.set_xlabel("čas t [µs]")
    ax.set_ylabel("výstupní napětí [V]")
    ax.set_ylim(-11, 16)
    ax.set_xlim(0, 40)
    ax.legend(loc="upper left", ncol=2)
    ax.set_title("Omezená rychlost přeběhu: výstup nestíhá, ze sinusu je trojúhelník", loc="left")
    save(fig, "fig12_slew")


def fig12_zisk_f():
    f = np.logspace(-0.3, 6.5, 600)
    a0, fp = 2e5, 5.0                                            # zisk při DC a zlom (jednopólový model, 1 MHz)
    a = a0 / np.sqrt(1 + (f / fp) ** 2)
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.plot(f, 20 * np.log10(a), color=C1)
    g3 = 20 * np.log10(a0) - 3.0103
    ax.axhline(20 * np.log10(a0), color=MUTED, ls=":", lw=1.0)
    ax.plot(fp, g3, "o", color=C2, mec=SURF, ms=7)
    ax.annotate("−3 dB (polovina výkonu)\nšířka pásma $f_M$ = 5 Hz", (fp, g3), xytext=(30, 90), fontsize=9.5,
                color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.plot(1e6, 0, "s", color=C3, mec=SURF, ms=7)
    ax.annotate("jednotkový zisk (0 dB)\ntranzitní frekvence 1 MHz", (1e6, 0), xytext=(1.5e3, 6), fontsize=9.5,
                color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.text(300, 55, "pokles 20 dB na dekádu:\nzisk · frekvence = konst.", fontsize=9.5, color=INK2)
    log_osa(ax)
    ax.set_xticks([1, 10, 100, 1e3, 1e4, 1e5, 1e6])
    ax.set_xticklabels(["1", "10", "100", "1 k", "10 k", "100 k", "1 M"])
    ax.set_ylabel("zisk bez zpětné vazby [dB]")
    ax.set_ylim(-10, 115)
    ax.set_title("Zisk OZ s frekvencí klesá ($A_0 = 2 \\cdot 10^5$, jednoduchý model)", loc="left")
    save(fig, "fig12_zisk_f")


def fig12_komparator():
    with schema("fig12_komparator") as d:
        op = elm.Opamp(leads=True)
        elm.Line().at(op.in1).left(d.unit * 0.4)
        elm.Dot(open=True).label("$V_1$", loc="left")
        elm.Line().at(op.in2).left(d.unit * 0.4)
        elm.Dot(open=True).label("$V_2$", loc="left")
        elm.Line().at(op.out).right(d.unit * 0.35)
        elm.Dot(open=True).label("$V_\\mathrm{OUT}$", loc="right")
        elm.Label().at((op.out[0] - 0.4, op.out[1] - 1.3)).label("bez zpětné vazby", fontsize=11, color=C2)


# =====================================================================  přednáška 3: napájení a reference
def fig13_teplota():
    """Teplotní drift s nelineární složkou: u 100 ppm/°C ji velikost driftu skryje, u 5 ppm/°C ne (ilustrační model)."""
    t = np.linspace(-50, 125, 300)
    b = -0.02                                                    # zakřivení [ppm/°C²], stejné pro obě reference
    fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.7), sharex=True)
    for ax, a, barva, zn in ((axs[0], 100, C1, "o"), (axs[1], 5, C2, "s")):
        prim = a * (t - 25)
        skut = prim + b * (t - 25) ** 2
        ax.plot(t, prim, color=MUTED, ls="--", lw=1.4, label="přímka (jen lineární drift)")
        ax.plot(t, skut, color=barva, label="skutečná odchylka")
        ax.plot([25], [0], zn, color=barva, mec=SURF, ms=7)
        ax.set_title(f"reference {a} ppm/°C", loc="left")
        ax.set_xlabel("teplota [°C]")
        ax.legend(loc="upper left", fontsize=9)
    axs[0].set_ylabel("odchylka napětí od hodnoty při 25 °C [ppm]")
    axs[1].text(35, -380, "křivka se od přímky\nviditelně odchyluje", fontsize=9.5, color=INK2)
    axs[0].text(10, -6500, "křivka a přímka\nskoro splývají", fontsize=9.5, color=INK2)
    save(fig, "fig13_teplota")


def fig13_dlouhodoba():
    """Dlouhodobá stabilita 200 ppm/√kHr: drift roste s odmocninou času (čísla ze slidu)."""
    roky = np.linspace(0, 10, 400)
    drift = 200 * np.sqrt(8.766 * roky)
    fig, ax = plt.subplots(figsize=(7.6, 3.7))
    ax.plot(roky, 592.15 * roky, color=MUTED, ls="--", lw=1.4, label="kdyby drift rostl lineárně (10 × 592 ppm)")
    ax.plot(roky, drift, color=C1, label="skutečný drift 200 ppm/√kHr")
    ax.plot([1, 10], [200 * np.sqrt(8.766), 200 * np.sqrt(87.66)], "o", color=C1, mec=SURF, ms=7)
    ax.annotate("1 rok: 592 ppm", (1, 592), xytext=(1.6, 1500), fontsize=9.5, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("10 let: ≈ 1873 ppm (na slidu 1875)", (10, 1873), xytext=(4.6, 3300), fontsize=9.5, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xlabel("doba provozu [roky]")
    ax.set_ylabel("drift napětí reference [ppm]")
    ax.set_xlim(0, 10.3)
    ax.set_ylim(0, 6200)
    ax.legend(loc="upper left")
    ax.set_title("Stárnutí reference: za 10 let jen asi 3,2× víc než za rok, ne 10×", loc="left")
    save(fig, "fig13_dlouhodoba")


def fig13_zener_va():
    """VA charakteristika Zenerovy diody (ilustrační model, U_Z = 5,1 V)."""
    u = np.linspace(-6.4, 1.0, 800)
    uz, rz, a = 5.1, 15.0, 0.08
    i_f = 1e-12 * (np.exp(u / 0.029) - 1)                    # propustný směr (Shockley)
    i_r = -(a / rz) * np.log1p(np.exp((-u - uz) / a))         # průraz v závěrném směru, sklon 1/r_z
    i = (i_f + i_r) * 1e3
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.axhline(0, color=AXIS, lw=0.9)
    ax.axvline(0, color=AXIS, lw=0.9)
    ax.plot(u, np.where(np.abs(i) < 45, i, np.nan), color=C1)
    m = (i < -5) & (i > -40)
    ax.plot(u[m], i[m], color=C2, lw=4.5, alpha=0.45, solid_capstyle="round")
    ax.annotate("pracovní oblast stabilizátoru:\nproud se mění hodně, napětí málo", (-5.55, -22), xytext=(-4.6, -36),
                fontsize=9.5, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("Zenerovo napětí $U_Z$ ≈ 5,1 V\n(závěrný směr)", (-5.1, -1), xytext=(-4.4, 14), fontsize=9.5,
                color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("propustný směr ≈ 0,7 V", (0.7, 20), xytext=(-2.6, 32), fontsize=9.5, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xlabel("napětí na diodě U [V]")
    ax.set_ylabel("proud diodou I [mA]")
    ax.set_ylim(-45, 45)
    ax.set_title("Zenerova dioda: v závěrném směru drží napětí $U_Z$", loc="left")
    save(fig, "fig13_zener_va")


def fig13_zd_stab():
    """Stabilizátor s referenční ZD a neinvertujícím OZ (slide „Stabilizace napětí se Zenerovou diodou“)."""
    with schema("fig13_zd_stab", unit=2.2) as d:
        u = d.unit
        op = elm.Opamp(leads=True, flip=True).right()          # + (in2) nahoře, − (in1) dole
        yb = op.in1[1] - u * 1.75                               # zem
        # neinvertující vstup: filtr R3C1 a Zenerova dioda
        elm.Line().at(op.in2).left(u * 0.9)
        p = elm.Dot()
        elm.Capacitor().down().toy(yb).label("$C_1$", loc="top")
        elm.Ground(lead=False)
        elm.Resistor().at(p.center).left().label("$R_3$")
        z = elm.Dot()
        elm.Zener().down().toy(yb).reverse().label("$U_{ZD}$", loc="top")
        elm.Ground(lead=False)
        elm.Resistor().at(z.center).up(u * 0.9).label("$R_D$", loc="bottom")
        elm.Dot(open=True).label("$U_{CC} > 0$", loc="top")
        # zpětná vazba R2 ∥ C2, R1 do země
        elm.Line().at(op.in1).left(u * 0.2)
        elm.Line().down(u * 0.6)
        m = elm.Dot()
        elm.Resistor().right().tox(op.out).label("$R_2$")
        elm.Line().up().toy(op.out).dot()
        elm.Line().at(m.center).down(u * 0.5)
        elm.Capacitor().right().tox(op.out).label("$C_2$", loc="bottom")
        elm.Line().up(u * 0.5)
        elm.Line().at(m.center).left(u * 0.25)
        elm.Resistor().down().toy(yb).label("$R_1$", loc="top")
        elm.Ground(lead=False)
        elm.Line().at(op.out).right(u * 0.35)
        elm.Dot(open=True).label("$U_0 = (1 + R_2/R_1)\\,U_{ZD}$", loc="right")


def fig13_zd_alt():
    """Alternativní zapojení: ZD napájená ze stabilizovaného výstupu, D1 jako ochrana (slidy 14–15)."""
    with schema("fig13_zd_alt", unit=2.2) as d:
        u = d.unit
        op = elm.Opamp(leads=True, flip=True).right()          # + (in2) nahoře, − (in1) dole
        ytop = op.in2[1] + u * 1.0
        yb = op.in1[1] - u * 1.75
        xo = op.out[0] + u * 0.45
        # výstup → horní vodič → R3 → + vstup → D1 → ZD → zem
        elm.Line().at(op.out).right(u * 0.45)
        o = elm.Dot()
        elm.Line().right(u * 0.35)
        elm.Dot(open=True).label("$U_0$", loc="right")
        elm.Line().at(o.center).toy(ytop)
        xz = op.in2[0] - u * 0.75
        elm.Line().tox(xz)
        elm.Resistor().down().toy(op.in2[1]).label("$R_3$", loc="top")
        p = elm.Dot()
        elm.Line().at(op.in2).tox(xz)
        elm.Diode().at(p.center).down(u * 0.7).label("$D_1$", loc="bottom", color=C2).color(C2)
        elm.Zener().down().toy(yb).reverse().label("ZD", loc="bottom")
        elm.Ground(lead=False)
        # − vstup ← dělič R2 / R1 z výstupu (vpravo)
        elm.Resistor().at(o.center).down().toy(op.in1[1] - u * 0.6).label("$R_2$", loc="bottom")
        m = elm.Dot()
        elm.Resistor().down().toy(yb).label("$R_1$", loc="bottom")
        elm.Ground(lead=False)
        elm.Line().at(op.in1).left(u * 0.25)
        elm.Line().down().toy(m.center[1])
        elm.Line().right().tox(m.center)
        elm.Label().at(((xz + o.center[0]) / 2, ytop + 0.35)).label("napájení ZD ze stabilizovaného výstupu",
                                                                  fontsize=10, color=C1)


def fig13_posileni():
    """Stabilizátor s proudovým zesílením: emitorový sledovač za OZ (slide „… s proudovým zesílením“)."""
    with schema("fig13_posileni", unit=2.0) as d:
        u = d.unit
        op = elm.Opamp(leads=True, flip=True).right()          # + (in2) nahoře, − (in1) dole
        t = elm.BjtNpn(circle=True).anchor("base").at((op.out[0] + u * 0.3, op.out[1])).label("$T$", loc="right")
        elm.Line().at(op.out).tox(t.base)
        ytop = op.in2[1] + u * 1.2
        yb = op.in1[1] - u * 2.4
        elm.Line().at(t.collector).toy(ytop)
        elm.Dot(open=True).label("$U_{CC}^+$", loc="top")
        e = elm.Line().at(t.emitter).down(u * 0.3).dot().end
        elm.Resistor().at(e).down().label("$R_2$", loc="bottom")
        m = elm.Dot()
        elm.Resistor().down().toy(yb).label("$R_1$", loc="bottom")
        elm.Ground(lead=False)
        elm.Line().at(op.in1).left(u * 0.25)
        elm.Line().down().toy(m.center[1])
        elm.Line().right().tox(m.center)
        elm.Line().at(e).right(u * 0.9)
        z = elm.Dot()
        elm.Resistor().down().toy(yb).label("$R_Z$ (zátěž)", loc="bottom")
        elm.Ground(lead=False)
        elm.Line().at(z.center).right(u * 0.3)
        elm.Dot(open=True).label("$U_0$", loc="right")
        # reference: R_D z napájení a ZD
        elm.Line().at(op.in2).left(u * 0.7)
        p = elm.Dot()
        elm.Zener().down().toy(yb).reverse().label("$U_{ZD}$", loc="top")
        elm.Ground(lead=False)
        elm.Resistor().at(p.center).up(u * 0.9).label("$R_D$", loc="bottom")
        elm.Dot(open=True).label("$U_{CC}^+$", loc="top")
        elm.Label().at((t.emitter[0] + 0.9, t.emitter[1] + 1.6)).label("emitorový\nsledovač", fontsize=10,
                                                                        color=C1, halign="left")


def fig13_omezeni():
    """Stabilizátor s Darlingtonem a proudovým omezením tranzistorem T3 (slidy „… s proudovým omezením“)."""
    with schema("fig13_omezeni", unit=2.0) as d:
        u = d.unit
        op = elm.Opamp(leads=True, flip=True).right()          # + (in2) nahoře, − (in1) dole
        elm.Line().at(op.in2).left(u * 0.4)
        elm.Dot(open=True).label("$U_\\mathrm{REF} > 0$", loc="left")
        o = elm.Line().at(op.out).right(u * 0.3).dot().end
        t1 = elm.BjtNpn(circle=True).right().anchor("base").at((o[0] + u * 0.3, o[1])).label("$T_1$", loc="right")
        elm.Line().at(o).tox(t1.base)
        t2 = elm.BjtNpn(circle=True).right().anchor("base").at(
            (t1.emitter[0] + u * 0.35, t1.emitter[1] - u * 0.45)).label("$T_2$", loc="right")
        elm.Line().at(t1.emitter).toy(t2.base)
        elm.Line().tox(t2.base)
        ytop = t1.collector[1] + u * 0.45
        elm.Line().at(t1.collector).toy(ytop).dot()
        elm.Line().at(t2.collector).toy(ytop)
        elm.Line().tox(t1.collector)
        elm.Line().at((t2.collector[0], ytop)).right(u * 0.3)
        elm.Dot(open=True).label("$+U_N$", loc="right")
        # snímací rezistor R_I mezi emitorem T2 (A) a výstupem (B)
        a = elm.Line().at(t2.emitter).down(u * 0.25).dot().end
        elm.Line().at(a).right(u * 0.3)
        elm.Resistor().right(u * 1.1).label("$R_I$", loc="bottom", color=C2).color(C2)
        b = elm.Dot().center
        elm.Line().at(b).right(u * 1.1)
        z = elm.Dot()
        elm.Line().right(u * 0.3)
        elm.Dot(open=True).label("$U_0$", loc="right")
        yb = a[1] - u * 2.9
        elm.Resistor().at(z.center).down().toy(yb).label("$R_Z$ (zátěž)", loc="bottom")
        elm.Ground(lead=False)
        b2 = elm.Line().at(b).down(u * 0.95).dot().end
        elm.Resistor().at(b2).down(u * 0.95).label("$R_2$", loc="bottom")
        m = elm.Dot()
        elm.Resistor().down().toy(yb).label("$R_1$", loc="bottom")
        elm.Ground(lead=False)
        # T3: báze na A, emitor na B, kolektor do báze T1
        t3 = elm.BjtNpn(circle=True).right().reverse().anchor("collector").at((o[0], a[1] - u * 0.35)).label(
            "$T_3$", loc="left", color=C2)
        t3.color(C2)
        elm.Line().at(o).toy(t3.collector)
        elm.Line().at(t3.base).tox(a).color(C2)
        elm.Line().toy(a).color(C2)
        elm.Line().at(t3.emitter).toy(b2).color(C2)
        elm.Line().tox(b2).color(C2)
        # zpětná vazba z děliče na − vstup
        elm.Line().at(op.in1).left(u * 0.25)
        elm.Line().down().toy(m.center[1])
        elm.Line().right().tox(m.center)
        elm.Label().at(((a[0] + b[0]) / 2 + u * 0.15, a[1] + 0.55)).label("$U_{R_I} \\approx 0{,}5$ V", fontsize=11, color=C2)


def fig13_omezeni_va():
    """Výstupní charakteristika stabilizátoru s omezením proudu a s foldbackem (ilustrační hodnoty 10 V, 1 A)."""
    io = np.linspace(0, 1.0, 300)
    uo = 10 - 0.25 * np.exp((io - 1.0) / 0.02)                 # měkké koleno těsně před I_omax
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.plot(np.r_[io, 1.0, 1.0], np.r_[uo, 9.75, 0], color=C1, label="omezení proudu: zkratový proud = $I_{omax}$")
    ax.plot([0, 1.0, 0.3], [10.08, 10.08, 0], color=C2, ls="--", label="foldback: při zkratu proud klesne")
    ax.plot([1.0], [0], "o", color=C1, mec=SURF, ms=7)
    ax.plot([0.3], [0], "s", color=C2, mec=SURF, ms=7)
    ax.annotate("zkrat: 1 A", (1.0, 0), xytext=(0.78, 2.2), fontsize=9.5, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("zkrat: 0,3 A", (0.3, 0), xytext=(0.06, 2.2), fontsize=9.5, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.text(0.03, 8.6, "stabilizace: $U_0$ drží 10 V", fontsize=9.5, color=INK2)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: cz(v, 1)))
    ax.set_xlabel("výstupní proud $I_o$ [A]")
    ax.set_ylabel("výstupní napětí $U_o$ [V]")
    ax.set_xlim(0, 1.15)
    ax.set_ylim(0, 13.5)
    ax.legend(loc="upper left", ncol=1, fontsize=9)
    ax.set_title("Výstupní charakteristika zdroje s omezením proudu", loc="left")
    save(fig, "fig13_omezeni_va")


def fig13_vlecny():
    """Vlečný zdroj, zjednodušeno: kladná větev = neinvertující zesilovač reference 3,3 V, záporná = invertor −1."""
    with schema("fig13_vlecny", unit=2.0) as d:
        u = d.unit
        op = elm.Opamp(leads=True, flip=True).right().label("OZ1", loc="center", ofst=(-0.3, 0), fontsize=10)
        yb = op.in1[1] - u * 1.8
        # reference: R z +U_N a ZD 3V3
        elm.Line().at(op.in2).left(u * 1.0)
        p = elm.Dot()
        elm.Zener().down().toy(yb).reverse().label("$D_2$\n3V3", loc="top")
        elm.Ground(lead=False)
        elm.Resistor().at(p.center).up(u * 0.85).label("$R$", loc="bottom")
        elm.Dot(open=True).label("$+U_N$", loc="top")
        # zpětná vazba Ra / Rb
        elm.Line().at(op.in1).left(u * 0.2)
        elm.Line().down(u * 0.7)
        m = elm.Dot()
        elm.ResistorVar().right().tox(op.out).label("$R_a$", loc="bottom")
        elm.Line().up().toy(op.out).dot()
        elm.Line().at(m.center).left(u * 0.25)
        elm.Resistor().down().toy(yb).label("$R_b$", loc="top")
        elm.Ground(lead=False)
        # výstup U_o1 a invertor OZ2
        o1 = elm.Line().at(op.out).right(u * 0.5).dot().end
        elm.Line().at(o1).up(u * 0.6)
        elm.Dot(open=True).label("$U_{o1} = 3{,}3\\,(1 + R_a/R_b)$", loc="top")
        elm.Resistor().at(o1).right().label("330 k", loc="bottom")
        n = elm.Dot()
        op2 = elm.Opamp(leads=True).right().anchor("in1").at((n.center[0] + u * 0.35, n.center[1])).label(
            "OZ2", loc="center", ofst=(-0.3, 0), fontsize=10)
        elm.Line().at(n.center).tox(op2.in1)
        elm.Line().at(op2.in2).down(u * 0.3)
        elm.Ground(lead=False)
        elm.Line().at(n.center).up(u * 0.6)
        elm.Resistor().right().tox(op2.out).label("330 k")
        elm.Line().down().toy(op2.out).dot()
        elm.Line().at(op2.out).right(u * 0.35)
        elm.Dot(open=True).label("$U_{o2} = -U_{o1}$", loc="right")
        elm.Label().at((n.center[0], n.center[1] - 0.55)).label("0 V", fontsize=11, color=C2)


def fig13_proudovy():
    """Zdroj konstantního proudu: OZ + Darlington, proud nastaví U_REF a R1 (slide „Zdroje (konstantního) proudu“)."""
    with schema("fig13_proudovy", unit=2.0) as d:
        u = d.unit
        op = elm.Opamp(leads=True, flip=True).right()          # + (in2) nahoře, − (in1) dole
        elm.Line().at(op.in2).left(u * 0.4)
        elm.Dot(open=True).label("$U_\\mathrm{REF}$", loc="left")
        t1 = elm.BjtNpn(circle=True).right().anchor("base").at((op.out[0] + u * 0.4, op.out[1])).label(
            "$T_1$", loc="right")
        elm.Line().at(op.out).tox(t1.base)
        t2 = elm.BjtNpn(circle=True).right().anchor("base").at((t1.emitter[0] + u * 0.35, t1.emitter[1] - u * 0.45)).label(
            "$T_2$", loc="right")
        elm.Line().at(t1.emitter).toy(t2.base)
        elm.Line().tox(t2.base)
        yc = t1.collector[1] + u * 0.35
        elm.Line().at(t1.collector).toy(yc).dot()
        elm.Line().at(t2.collector).toy(yc)
        c = elm.Line().tox(t1.collector).end
        elm.Dot().at((t2.collector[0], yc)).label("C", loc="right")
        elm.Resistor().at((t2.collector[0], yc)).up(u * 0.9).label("zátěž", loc="top", color=C2).color(C2)
        elm.Dot(open=True).label("$+U_N$", loc="top")
        elm.Label().at((t2.collector[0] + 0.8, yc + 0.45)).label("$I_o$ ↓", fontsize=12, color=C2, halign="left")
        e = elm.Line().at(t2.emitter).down(u * 0.3).dot().end
        yb = e[1] - u * 1.2
        elm.Resistor().at(e).down().toy(yb).label("$R_1$", loc="bottom")
        elm.Ground(lead=False)
        elm.Label().at((e[0] - 0.75, e[1] - u * 0.5)).label("$U_1 = U_\\mathrm{REF}$", fontsize=11, color=C1,
                                                             halign="right")
        elm.Line().at(op.in1).left(u * 0.25)
        elm.Line().down().toy(e[1])
        elm.Line().right().tox(e)


# =====================================================================  přednáška 4: aplikace OZ (zapojení)
def _vystup(d, op, text, delka=0.35):
    elm.Line().at(op.out).right(d.unit * delka)
    elm.Dot(open=True).label(text, loc="right")


def fig14_nulovani():
    """Millerův integrátor s nulovacím obvodem: tranzistor T1 paralelně ke C (slide „… s nulovacím obvodem“)."""
    with schema("fig14_nulovani") as d:
        u = d.unit
        op = elm.Opamp(leads=True)
        _vstup_zem(d, op)
        elm.Line().at(op.in1).left(u * 0.25)
        n = elm.Dot()
        elm.Resistor().left().label("$R_1$", loc="bottom")
        elm.Dot(open=True).label("$U_i$", loc="left")
        elm.Line().at(n.center).up(u * 0.6)
        m = elm.Dot()
        elm.Capacitor().right().tox(op.out).label("$C$")
        k = elm.Dot()
        elm.Line().down().toy(op.out).dot()
        elm.Line().at(m.center).up(u * 0.55)
        elm.Switch(action="close").right().tox(op.out).label("$T_1$ (spínač, řízen $U_G$)", color=C2).color(C2)
        elm.Line().down().toy(k.center)
        _vystup(d, op, "$U_o$")


def _int_rc(name, minus):
    """Neinvertující (minus = None → R na zem) a diferenční (minus = popisek vstupu) integrátor."""
    with schema(name) as d:
        u = d.unit
        op = elm.Opamp(leads=True)                               # − (in1) nahoře, + (in2) dole
        elm.Line().at(op.in1).left(u * 0.25)
        n = elm.Dot()
        elm.Resistor().left().label("$R$")
        if minus:
            elm.Dot(open=True).label(minus, loc="left")
        else:
            elm.Line().down(u * 0.25)
            elm.Ground(lead=False)
        elm.Line().at(n.center).up(u * 0.6)
        elm.Capacitor().right().tox(op.out).label("$C$")
        elm.Line().down().toy(op.out).dot()
        elm.Line().at(op.in2).left(u * 0.25)
        p = elm.Dot()
        elm.Resistor().left().label("$R$", loc="bottom")
        elm.Dot(open=True).label("$u_2$" if minus else "$u_i$", loc="left")
        elm.Capacitor().at(p.center).down().label("$C$", loc="bottom")
        elm.Ground()
        _vystup(d, op, "$u_o$")


def fig14_neinv_int():
    _int_rc("fig14_neinv_int", None)


def fig14_dif_int():
    _int_rc("fig14_dif_int", "$u_1$")


def fig14_der_osetreny():
    """Derivátor ošetřený proti nestabilitě: R1 v sérii s C, C1 paralelně k R (slide „Ošetření nestability…“)."""
    with schema("fig14_der_osetreny", unit=2.3) as d:
        u = d.unit
        op = elm.Opamp(leads=True)
        elm.Resistor().at(op.in2).down().label("$R$", loc="bottom")
        elm.Ground()
        elm.Line().at(op.in1).left(u * 0.25)
        n = elm.Dot()
        elm.Resistor().left().label("$R_1$", loc="bottom", color=C2).color(C2)
        elm.Capacitor().left().label("$C$", loc="bottom")
        elm.Dot(open=True).label("$u_i$", loc="left")
        elm.Line().at(n.center).up(u * 0.55)
        m = elm.Dot()
        elm.Resistor().right().tox(op.out).label("$R$")
        k = elm.Dot()
        elm.Line().down().toy(op.out).dot()
        elm.Line().at(m.center).up(u * 0.55)
        elm.Capacitor().right().tox(op.out).label("$C_1$", color=C2).color(C2)
        elm.Line().down().toy(k.center)
        _vystup(d, op, "$u_o$")


def fig14_jednocestny():
    """Jednocestný usměrňovač: dioda uvnitř zpětné vazby sledovače (slide „Jednocestný usměrňovač“)."""
    with schema("fig14_jednocestny") as d:
        u = d.unit
        op = elm.Opamp(leads=True)                               # − nahoře, + dole
        elm.Line().at(op.in2).left(u * 0.3)
        elm.Dot(open=True).label("$u_i$", loc="left")
        elm.Line().at(op.out).right(u * 0.15)
        elm.Diode().right().label("$D$").label("$U_D$", loc="bottom", fontsize=11)
        o = elm.Dot()
        elm.Line().right(u * 0.4)
        elm.Dot(open=True).label("$u_o$", loc="right")
        elm.Resistor().at(o.center).down().label("$R_L$", loc="bottom")
        elm.Ground()
        elm.Line().at(op.in1).left(u * 0.25)
        elm.Line().up(u * 0.6)
        elm.Line().right().tox(o.center)
        elm.Line().down().toy(o.center)
        elm.Label().at((op.out[0] + 0.1, op.out[1] + 0.45)).label("$u_1$", fontsize=12)


def fig14_usm_a():
    """Jednocestný usměrňovač – invertující varianta s D1 a D2 (slide „… různá řešení“, vlevo)."""
    with schema("fig14_usm_a") as d:
        u = d.unit
        op = elm.Opamp(leads=True)
        _vstup_zem(d, op)
        elm.Line().at(op.in1).left(u * 0.25)
        n = elm.Dot()
        elm.Resistor().left().label("$R_1$", loc="bottom")
        elm.Dot(open=True).label("vstup", loc="left")
        xk = op.out[0] + u * 0.3
        elm.Line().at(n.center).up(u * 0.6)
        m = elm.Dot()
        elm.Diode().right().tox(xk).label("$D_1$")
        j = elm.Dot()
        elm.Line().at(op.out).right().tox(xk)
        elm.Line().up().toy(j.center)
        elm.Line().at(m.center).up(u * 0.6)
        elm.Resistor().right().tox(xk).label("$R_2$")
        v = elm.Dot()
        elm.Diode().at(j.center).up().toy(v.center).label("$D_2$", loc="bottom")
        elm.Line().at(v.center).right(u * 0.35)
        elm.Dot(open=True).label("výstup", loc="right")


def fig14_usm_b():
    """Jednocestný usměrňovač se dvěma výstupy A a B (slide „… různá řešení“, vpravo)."""
    with schema("fig14_usm_b") as d:
        u = d.unit
        op = elm.Opamp(leads=True)
        _vstup_zem(d, op)
        elm.Line().at(op.in1).left(u * 0.3)
        n = elm.Dot()
        elm.Resistor().left().label("$R$", loc="bottom")
        elm.Dot(open=True).label("vstup", loc="left")
        xk = op.out[0] + u * 0.45
        ya = op.in1[1] + u * 0.75
        yb = op.in2[1] - u * 0.95
        elm.Line().at(n.center).up().toy(ya)
        elm.Resistor().right().tox(xk).label("$R_1$")
        a = elm.Dot()
        elm.Line().right(u * 0.35)
        elm.Dot(open=True).label("A", loc="right")
        elm.Line().at(n.center).down().toy(yb)
        elm.Resistor().right().tox(xk).label("$R_2$", loc="bottom")
        b = elm.Dot()
        elm.Line().right(u * 0.35)
        elm.Dot(open=True).label("B", loc="right")
        elm.Line().at(op.out).right().tox(xk)
        s = elm.Dot()
        elm.Diode().at(a.center).down().toy(s.center).label("$D_1$", loc="bottom")
        elm.Diode().at(s.center).down().toy(b.center).label("$D_2$", loc="bottom")


def fig14_dvoucestny():
    """Precizní dvoucestný usměrňovač se třemi OZ (slide „Precizní dvoucestný usměrňovač“)."""
    with schema("fig14_dvoucestny", unit=2.2) as d:
        u = d.unit
        op1 = elm.Opamp(leads=True).label("OZ1", loc="center", fontsize=11)
        elm.Line().at(op1.in2).left(u * 0.15)
        elm.Resistor().left().label("$R_s$", loc="bottom")
        elm.Dot(open=True).label("$u_i$", loc="left")
        ytop = op1.out[1] + u * 1.0
        elm.Line().at(op1.in1).left(u * 0.2)
        elm.Line().up().toy(ytop)
        elm.Line().right().tox(op1.out[0] + u * 0.3)
        p = elm.Dot()
        elm.Line().down().toy(op1.out)
        elm.Line().left().tox(op1.out)
        elm.Label().at((p.center[0], p.center[1] + 0.4)).label("$u_i$", fontsize=12)
        # OZ2 – invertor se dvěma R1, dioda D ve zpětné vazbě
        x2 = p.center[0] + u * 1.6
        op2 = elm.Opamp(leads=True).right().anchor("in1").at((x2, op1.out[1])).label("OZ2", loc="center", fontsize=11)
        elm.Line().at(op2.in2).down(u * 0.25)
        elm.Ground(lead=False)
        elm.Line().at(op2.out).right(u * 0.1)
        elm.Diode().right(u * 0.8).label("$D$", color=C2).color(C2)
        c = elm.Dot()
        xa = x2 - u * 0.3
        elm.Resistor().at(p.center).right().tox(xa).label("$R_1$")
        a = elm.Dot()
        elm.Line().down().toy(op2.in1)
        elm.Line().right().tox(op2.in1)
        elm.Resistor().at(a.center).right().tox(c.center).label("$R_1$")
        elm.Line().down().toy(c.center)
        # OZ3 – sledovač
        op3 = elm.Opamp(leads=True, flip=True).right().anchor("in2").at((c.center[0] + u * 0.6, c.center[1])) \
            .label("OZ3", loc="center", fontsize=11)
        elm.Line().at(c.center).right().tox(op3.in2)
        elm.Label().at((c.center[0] + u * 0.3, c.center[1] - 0.4)).label("$u_+$", fontsize=12)
        elm.Line().at(op3.in1).left(u * 0.2)
        elm.Line().down(u * 0.5)
        elm.Line().right().tox(op3.out)
        elm.Line().up().toy(op3.out).dot()
        _vystup(d, op3, "$u_o = |u_i|$")


def fig14_vrcholovy():
    """Vrcholový detektor: OZ1 + D nabíjí C, OZ2 sledovač, R_V se spínačem = obnovení nuly (slide „Vrcholový detektor“)."""
    with schema("fig14_vrcholovy", unit=2.3) as d:
        u = d.unit
        op1 = elm.Opamp(leads=True).label("OZ1", loc="center", fontsize=11)
        elm.Line().at(op1.in2).left(u * 0.3)
        elm.Dot(open=True).label("$u_i$", loc="left")
        elm.Line().at(op1.out).right(u * 0.1)
        elm.Diode().right(u * 0.7).label("$D$")
        k = elm.Dot()
        elm.Line().right(u * 0.45)
        k2 = elm.Dot()
        elm.Line().right(u * 0.7)
        k3 = elm.Dot()
        elm.Capacitor().at(k2.center).down(u * 0.8).label("$C$", loc="bottom").label("$u_C$", loc="top", fontsize=11)
        elm.Ground()
        elm.Resistor().at(k3.center).down(u * 0.6).label("$R_V$", loc="bottom").linestyle("--")
        elm.Switch().down(u * 0.6).label("obnovení\n„nuly“", loc="bottom", color=C2).color(C2)
        elm.Ground()
        elm.Line().at(op1.in1).left(u * 0.2)
        elm.Line().up(u * 0.6)
        elm.Line().right().tox(k.center)
        elm.Line().down().toy(k.center)
        op2 = elm.Opamp(leads=True).right().anchor("in2").at((k3.center[0] + u * 0.5, k3.center[1])) \
            .label("OZ2", loc="center", fontsize=11)
        elm.Line().at(k3.center).right().tox(op2.in2)
        elm.Line().at(op2.in1).left(u * 0.2)
        elm.Line().up(u * 0.6)
        elm.Line().right().tox(op2.out)
        elm.Line().down().toy(op2.out).dot()
        _vystup(d, op2, "$u_o$")


def fig14_int_prubeh():
    """Odezva Millerova integrátoru na skok ±0,5 V, RC = 10 ms, saturace ±12 V (slide „Časové průběhy…“)."""
    t = np.linspace(0, 0.4, 2001)
    RC, t0, usat = 10e-3, 0.05, 12.0
    fig, axs = plt.subplots(2, 2, figsize=(9.2, 4.8), sharex=True)
    for j, ui in enumerate([0.5, -0.5]):
        uin = np.where(t >= t0, ui, 0.0)
        uo = np.clip(-ui / RC * np.clip(t - t0, 0, None), -usat, usat)
        axs[0, j].plot(t * 1e3, uin, color=C1)
        axs[0, j].set_ylim(-0.8, 0.8)
        axs[0, j].set_title(f"vstup $u_i$ = {cz(ui, 1).replace('-', '−')} V" + (" (> 0)" if ui > 0 else " (< 0)"), loc="left")
        axs[1, j].axhspan(np.sign(-ui) * usat, np.sign(-ui) * 14, color=C2, alpha=0.12, lw=0)
        axs[1, j].plot(t * 1e3, uo, color=C2)
        axs[1, j].set_ylim(-14, 14)
        ts = (t0 + usat * RC / abs(ui)) * 1e3
        axs[1, j].annotate("saturace", (ts + 30, np.sign(-ui) * 12.9), fontsize=9.5, color=INK2, va="center")
        txt = "sklon $-u_i/RC$ = −50 V/s" if ui > 0 else "sklon $-u_i/RC$ = +50 V/s"
        axs[1, j].text(t0 * 1e3 + 125, -np.sign(-ui) * 6, txt, fontsize=9.5, color=INK2)
        axs[1, j].set_title("výstup $u_o$", loc="left")
        axs[1, j].set_xlabel("čas t [ms]")
    axs[0, 0].set_ylabel("$u_i$ [V]")
    axs[1, 0].set_ylabel("$u_o$ [V]")
    save(fig, "fig14_int_prubeh")


def fig14_nulovani_prubeh():
    """Integrátor jako analogová paměť a nulování tranzistorem T1 (vlastní ilustrace, RC = 10 ms)."""
    dt = 1e-5
    t = np.arange(0, 0.12, dt)
    RC = 10e-3
    ui = np.where((t >= 0.01) & (t < 0.03), -1.0, 0.0) + np.where((t >= 0.07) & (t < 0.09), -1.0, 0.0)
    reset = (t < 0.005) | ((t >= 0.05) & (t < 0.06))
    uo = np.zeros_like(t)
    for i in range(1, len(t)):
        uo[i] = 0.0 if reset[i] else uo[i - 1] - ui[i] / RC * dt
    fig, axs = plt.subplots(3, 1, figsize=(7.8, 5.2), sharex=True, gridspec_kw=dict(height_ratios=[1, 0.6, 1.4]))
    ms = t * 1e3
    axs[0].plot(ms, ui, color=C1)
    axs[0].set_ylabel("$u_i$ [V]")
    axs[0].set_ylim(-1.4, 0.4)
    axs[0].set_title("vstup: dva pulzy −1 V po 20 ms", loc="left")
    axs[1].step(ms, reset.astype(float), where="post", color=C3)
    axs[1].set_yticks([0, 1], ["vyp.", "sepnut"])
    axs[1].set_ylim(-0.3, 1.3)
    axs[1].set_title("tranzistor $T_1$ (nulování)", loc="left")
    axs[2].plot(ms, uo, color=C2)
    axs[2].set_ylabel("$u_o$ [V]")
    axs[2].set_ylim(-0.4, 2.6)
    axs[2].set_title("výstup integrátoru (RC = 10 ms)", loc="left")
    axs[2].text(33, 2.15, "vstup 0 → výstup drží 2 V\n(analogová paměť)", fontsize=9.5, color=INK2)
    axs[2].text(94, 0.6,"po vynulování\nnová integrace", fontsize=9.5, color=INK2)
    axs[2].set_xlabel("čas t [ms]")
    for ax in axs:
        for a, b in [(0, 5), (50, 60)]:
            ax.axvspan(a, b, color=C3, alpha=0.10, lw=0)
    save(fig, "fig14_nulovani_prubeh")


def fig14_der_bode():
    """Ošetřený derivátor: R = 100 kΩ, R1 = 1 kΩ, C = 1 µF, C1 = 10 nF (vlastní čísla, tvar podle slidu)."""
    R, R1, C, Cz = 100e3, 1e3, 1e-6, 10e-9            # Cz = C1 ze slidu (C1 je barva)
    w = np.logspace(1, 5, 600)

    def h(ww):
        s = 1j * ww
        return -(R / (1 + s * R * Cz)) / (R1 + 1 / (s * C))

    wk = 1 / (R1 * C)
    fig, ax = plt.subplots(figsize=(7.8, 3.9))
    ax.axvspan(wk / 10, wk * 10, color=C3, alpha=0.08, lw=0)
    ax.plot(w, 20 * np.log10(w * C * R), color=MUTED, lw=1.2, ls="--")
    ax.plot(w, 20 * np.log10(1 / (w * Cz * R1)), color=MUTED, lw=1.2, ls="--")
    ax.plot(w, np.full_like(w, 20 * np.log10(R / R1)), color=MUTED, lw=1.2, ls=":")
    ax.plot(w, db(h(w)), color=C1)
    ax.plot([wk], [db(h(wk))], "o", color=C1)
    ax.axvline(wk, color=INK2, lw=0.8, ls="--")
    ax.text(12, 22, "+20 dB/dek\n(+6 dB/okt)\n$\\omega CR$", fontsize=9.5, color=INK2)
    ax.text(2.2e4, 22, "−20 dB/dek\n(−6 dB/okt)\n$1/(\\omega C_1 R_1)$", fontsize=9.5, color=INK2)
    ax.annotate("$\\omega_K$ = 1000 rad/s: 34 dB (50×)", (wk, db(h(wk))), xytext=(1.25e3, 6), fontsize=9.5,
                color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.text(12, 42.5, "asymptota $R/R_1$ = 100 (40 dB)", fontsize=9.5, color=INK2)
    for x, txt in [(25, "DERIVACE"), (wk, "PROPUST"), (4e4, "INTEGRACE")]:
        ax.text(x, -14, txt, fontsize=9.5, color=INK2, ha="center", weight="semibold")
    ax.set_xscale("log")
    ax.set_xlim(10, 1e5)
    ax.set_ylim(-20, 50)
    ax.set_xlabel("úhlová frekvence ω [rad/s]")
    ax.set_ylabel("zisk |A| [dB]")
    ax.set_title("Derivačně-integrační zesilovač", loc="left")
    save(fig, "fig14_der_bode")


def fig14_der_trojuhelnik():
    """Derivátor (RC = 1 ms) a trojúhelník ±1 V s periodou 4 ms a 8 ms (tvar podle slidu, vlastní čísla)."""
    t = np.linspace(0, 12e-3, 6001)
    RC = 1e-3

    def tri(T):
        return 1 - 2 * np.abs(2 * ((t / T + 0.25) % 1) - 1)      # začíná v 0 a roste

    fig, axs = plt.subplots(2, 1, figsize=(7.8, 4.6), sharex=True)
    for T, c, ls, lab in [(4e-3, C1, "-", "rychlý (T = 4 ms)"), (8e-3, C2, "--", "pomalý (T = 8 ms)")]:
        x = tri(T)
        axs[0].plot(t * 1e3, x, color=c, ls=ls, label=lab)
        axs[1].plot(t * 1e3, -RC * np.gradient(x, t), color=c, ls=ls)
    axs[0].set_ylabel("$u_i$ [V]")
    axs[0].set_title("vstup: trojúhelník ±1 V", loc="left")
    axs[0].legend(loc="upper right", ncol=2, fontsize=9)
    axs[0].set_ylim(-1.3, 1.7)
    axs[1].set_ylabel("$u_o$ [V]")
    axs[1].set_ylim(-1.4, 1.4)
    axs[1].set_title("výstup derivátoru: obdélník ∓1 V, resp. ∓0,5 V", loc="left")
    axs[1].set_xlabel("čas t [ms]")
    save(fig, "fig14_der_trojuhelnik")


def fig14_usm_prubeh():
    """Diodový usměrňovač (U_D = 0,7 V) vs. precizní s OZ, sinus 1 V (vlastní ilustrace)."""
    t = np.linspace(0, 40e-3, 2001)
    ui = np.sin(2 * np.pi * 50 * t)
    fig, axs = plt.subplots(2, 1, figsize=(7.8, 4.8), sharex=True)
    for ax in axs:
        ax.plot(t * 1e3, ui, color=MUTED, lw=1.1, ls=":", label="vstup $u_i$ (1 V)")
    axs[0].plot(t * 1e3, np.maximum(ui, 0), color=C1, label="precizní s OZ")
    axs[0].plot(t * 1e3, np.maximum(ui - 0.7, 0), color=C2, ls="--", label="jen dioda (0,7 V)")
    axs[0].set_title("jednocestné usměrnění", loc="left")
    axs[1].plot(t * 1e3, np.abs(ui), color=C1, label="$|u_i|$ precizní dvoucestný")
    axs[1].set_title("dvoucestné usměrnění", loc="left")
    for ax in axs:
        ax.set_ylim(-1.2, 1.9)
        ax.set_ylabel("napětí [V]")
        ax.legend(loc="upper right", ncol=3, fontsize=9)
    axs[1].set_xlabel("čas t [ms]")
    save(fig, "fig14_usm_prubeh")


UT = 0.02585                                   # tepelné napětí při 27 °C [V]
IS_SI, IS_SCH = 1.2e-14, 6.3e-8                # saturační proudy: Si dioda (1 mA při 0,65 V), Schottky (1 mA při 0,25 V)


def _proud_diody_rl(u, n_diod=1, rl=1e3):
    """Proud obvodem n diod v sérii s R_L: řeší u = n·U_T·ln(1 + I/I_S) + I·R_L bisekcí (Shockley)."""
    u = np.maximum(u, 0)
    lo, hi = np.zeros_like(u), u / rl
    for _ in range(80):
        mid = (lo + hi) / 2
        f = n_diod * UT * np.log1p(mid / IS_SI) + mid * rl - u
        lo, hi = np.where(f < 0, mid, lo), np.where(f < 0, hi, mid)
    return lo


def fig14_dioda_va():
    """VA charakteristika křemíkové a Schottkyho diody (Shockleyho model) + prahový model 0,7 V."""
    u = np.linspace(-2.0, 1.6, 1800)
    fig, ax = plt.subplots(figsize=(7.8, 3.9))
    ax.axhline(0, color=AXIS, lw=0.9)
    ax.axvline(0, color=AXIS, lw=0.9)
    for i_s, barva, styl, popis in ((IS_SI, C1, "-", "křemíková dioda"), (IS_SCH, C2, "--", "Schottkyho dioda")):
        i = i_s * (np.exp(u / UT) - 1) * 1e3
        ax.plot(u, np.where(i < 32, i, np.nan), color=barva, ls=styl, label=popis)
    ax.plot([-2.0, 0.7, 0.7], [0, 0, 32], color=MUTED, lw=1.3, ls=":", label="prahový model (0,7 V)")
    ax.annotate("propustný směr:\nnad prahem proud\nprudce roste", (0.735, 16), xytext=(0.9, 12), ha="left",
                fontsize=9.5, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("závěrný směr: teče jen nepatrný\nzávěrný proud (nA, u Schottkyho µA)", (-1.2, 0), xytext=(-1.95, -10),
                fontsize=9.5, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xlabel("napětí na diodě U (anoda − katoda) [V]")
    ax.set_ylabel("proud diodou I [mA]")
    ax.set_xlim(-2.0, 1.6)
    ax.set_ylim(-14, 32)
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "fig14_dioda_va")


def fig14_usm_va():
    """Proud zátěží R_L = 1 kΩ v závislosti na u_i: dioda sama / s OZ, diodový můstek / precizní dvoucestný."""
    u = np.linspace(-2.0, 2.0, 1601)
    rl, a, ud = 1e3, 1e5, 0.7
    oz = np.maximum(0, (a * u - ud) / (a + 1)) / rl * 1e3          # jednocestný s OZ: u_o = (A·u_i − U_D)/(A + 1)
    fig, axs = plt.subplots(2, 1, figsize=(7.8, 5.6), sharex=True)
    axs[0].plot(u, oz, color=C1, label="dioda ve zpětné vazbě OZ")
    axs[0].plot(u, _proud_diody_rl(u) * 1e3, color=C2, ls="--", label="jen dioda")
    axs[0].axvspan(0, 0.65, color=C2, alpha=0.12, lw=0)
    axs[0].text(0.06, 1.55, "práh diody:\nproud skoro neteče", fontsize=9, color=INK2)
    axs[0].set_title("jednocestné usměrnění", loc="left")
    axs[1].plot(u, np.abs(u) / rl * 1e3, color=C1, label="precizní dvoucestný ($|u_i|$)")
    axs[1].plot(u, _proud_diody_rl(np.abs(u), n_diod=2) * 1e3, color=C2, ls="--", label="diodový můstek (2 diody)")
    axs[1].axvspan(-1.3, 1.3, color=C2, alpha=0.12, lw=0)
    axs[1].text(0, 1.55, "dvojnásobný práh ±1,3 V", fontsize=9, color=INK2, ha="center")
    axs[1].set_title("dvoucestné usměrnění", loc="left")
    for ax in axs:
        ax.axhline(0, color=AXIS, lw=0.9)
        ax.axvline(0, color=AXIS, lw=0.9)
        ax.set_ylim(-0.2, 2.3)
        ax.set_ylabel("proud zátěží $I_L$ [mA]")
        ax.legend(loc="upper left", fontsize=9)
    axs[1].set_xlabel("vstupní napětí $u_i$ [V]")
    save(fig, "fig14_usm_va")


def fig14_vrchol_prubeh():
    """Vrcholový detektor: u_C drží maximum, v čase 70 ms obnovení nuly (vlastní ilustrace, tvar podle slidu)."""
    dt = 1e-5
    t = np.arange(0, 0.1, dt)
    ui = 1.0 + 0.6 * np.sin(2 * np.pi * 25 * t - 1.2) + 1.2 * np.exp(-((t - 0.045) / 0.02) ** 2)
    reset = (t >= 0.07) & (t < 0.072)
    uc = np.zeros_like(t)
    for i in range(len(t)):
        uc[i] = 0.0 if reset[i] else max(uc[i - 1] if i else 0.0, ui[i])
    fig, ax = plt.subplots(figsize=(7.8, 3.7))
    ax.axvspan(70, 72, color=C3, alpha=0.18, lw=0)
    ax.plot(t * 1e3, ui, color=C1, ls="--", label="vstup $u_i$")
    ax.plot(t * 1e3, uc, color=C2, label="$u_C = u_o$ (paměť vrcholu)")
    ax.text(73.5, 2.0, "obnovení nuly\n(spínač sepnut)", fontsize=9.5, color=INK2)
    ax.set_xlabel("čas t [ms]")
    ax.set_ylabel("napětí [V]")
    ax.set_ylim(0, 3.6)
    ax.legend(loc="upper left", ncol=2, fontsize=9)
    save(fig, "fig14_vrchol_prubeh")


# =====================================================================  přednáška 5: aktivní filtry
VST, VYST = "$U_\\mathrm{vst}$", "$U_\\mathrm{výst}$"


def _sledovac_zv(d, op, hloubka=0.45):
    """Zpětná vazba sledovače: invertující vstup (dole, flip=True) přímo na výstup."""
    elm.Line().at(op.in1).left(d.unit * 0.25)
    elm.Line().down(d.unit * hloubka)
    elm.Line().right().tox(op.out)
    elm.Line().up().toy(op.out).dot()


def _rad1(name, hp, inv):
    """Filtr 1. řádu (slidy „Aktivní filtr – DP/HP 1. řádu“): neinvertující nebo invertující varianta."""
    with schema(name, unit=2.3) as d:
        u = d.unit
        if inv:
            op = elm.Opamp(leads=True)                           # − nahoře, + dole
            _vstup_zem(d, op)
            elm.Line().at(op.in1).left(u * 0.25)
            n = elm.Dot()
            if hp:
                elm.Resistor().left().label("$R_1$", loc="bottom")
                elm.Capacitor().left().label("$C_1$", loc="bottom")
            else:
                elm.Resistor().left().label("$R_1$", loc="bottom")
            elm.Dot(open=True).label(VST, loc="left")
            elm.Line().at(n.center).up(u * 0.5)
            m = elm.Dot()
            elm.Resistor().right().tox(op.out).label("$R_2$")
            k = elm.Dot()
            elm.Line().down().toy(op.out).dot()
            if not hp:
                elm.Line().at(m.center).up(u * 0.5)
                elm.Capacitor().right().tox(op.out).label("$C_1$")
                elm.Line().down().toy(k.center)
        else:
            op = elm.Opamp(leads=True, flip=True).right()        # + nahoře, − dole
            elm.Line().at(op.in2).left(u * 0.7)
            n = elm.Dot()
            if hp:
                elm.Capacitor().left().label("$C_1$")
                elm.Dot(open=True).label(VST, loc="left")
                elm.Resistor().at(n.center).down().label("$R_1$", loc="bottom")
            else:
                elm.Resistor().left().label("$R_1$")
                elm.Dot(open=True).label(VST, loc="left")
                elm.Capacitor().at(n.center).down().label("$C_1$", loc="bottom")
            elm.Ground()
            elm.Line().at(op.in1).left(u * 0.2)
            elm.Line().down(u * 0.45)
            m = elm.Dot()
            elm.Resistor().right().tox(op.out).label("$R_2$", loc="bottom")
            elm.Line().up().toy(op.out).dot()
            elm.Resistor().at(m.center).down().label("$R_3$", loc="bottom")
            elm.Ground()
        _vystup(d, op, VYST)


def fig15_dp1_neinv():
    _rad1("fig15_dp1_neinv", hp=False, inv=False)


def fig15_dp1_inv():
    _rad1("fig15_dp1_inv", hp=False, inv=True)


def fig15_hp1_neinv():
    _rad1("fig15_hp1_neinv", hp=True, inv=False)


def fig15_hp1_inv():
    _rad1("fig15_hp1_inv", hp=True, inv=True)


def _sallen_key(name, hp):
    """Sallen-Key 2. řádu se ziskem 1 (slidy „DP/HP typu Sallen-Key“, „Pásmová propust“: záměna R ↔ C)."""
    with schema(name, unit=2.3) as d:
        u = d.unit
        op = elm.Opamp(leads=True, flip=True).right()            # + nahoře, − dole
        elm.Line().at(op.in2).left(u * 0.6)
        p = elm.Dot()
        if hp:
            elm.Capacitor().left().label("$C$")
            a = elm.Dot()
            elm.Capacitor().left().label("$C$")
            elm.Dot(open=True).label(VST, loc="left")
            elm.Resistor().at(p.center).down().label("$R_1$", loc="bottom")
        else:
            elm.Resistor().left().label("$R_2$")
            a = elm.Dot()
            elm.Resistor().left().label("$R_1$")
            elm.Dot(open=True).label(VST, loc="left")
            elm.Capacitor().at(p.center).down().label("$C_1$", loc="bottom")
        elm.Ground()
        _sledovac_zv(d, op)
        elm.Line().at(a.center).up(u * 0.75)
        if hp:
            elm.Resistor().right().tox(op.out).label("$R_2$")
        else:
            elm.Capacitor().right().tox(op.out).label("$C_2$")
        elm.Line().down().toy(op.out)
        _vystup(d, op, VYST)


def fig15_sk_dp():
    _sallen_key("fig15_sk_dp", hp=False)


def fig15_sk_hp():
    _sallen_key("fig15_sk_hp", hp=True)


def _mfb(name, vstup, zem, k_minus, zv_dole, zv_nahore):
    """Struktura MFB (slidy „… typu MFB“): vstupní prvek → uzel a, z něj prvek na zem, prvek k invertujícímu
    vstupu a horní zpětná vazba na výstup; dolní zpětná vazba z invertujícího vstupu na výstup.
    Každý prvek je dvojice (třída prvku, popisek)."""
    with schema(name, unit=2.3) as d:
        u = d.unit
        op = elm.Opamp(leads=True)                               # − nahoře, + dole
        _vstup_zem(d, op)
        elm.Line().at(op.in1).left(u * 0.25)
        n = elm.Dot()
        k_minus[0]().left().label(k_minus[1], loc="bottom")
        a = elm.Dot()
        vstup[0]().left().label(vstup[1], loc="bottom")
        elm.Dot(open=True).label(VST, loc="left")
        zem[0]().at(a.center).down().label(zem[1], loc="bottom")
        elm.Ground()
        elm.Line().at(n.center).up(u * 0.5)
        zv_dole[0]().right().tox(op.out).label(zv_dole[1])
        k = elm.Dot()
        elm.Line().down().toy(op.out).dot()
        elm.Line().at(a.center).up(u * 1.05)
        zv_nahore[0]().right().tox(op.out).label(zv_nahore[1])
        elm.Line().down().toy(k.center)
        _vystup(d, op, VYST)


def fig15_mfb_dp():
    R, C = elm.Resistor, elm.Capacitor
    _mfb("fig15_mfb_dp", (R, "$R_1$"), (C, "$C_2$"), (R, "$R_3$"), (C, "$C_1$"), (R, "$R_2$"))


def fig15_mfb_hp():
    R, C = elm.Resistor, elm.Capacitor
    _mfb("fig15_mfb_hp", (C, "$C_1 = C$"), (R, "$R_2$"), (C, "$C_3 = C$"), (R, "$R_1$"), (C, "$C_2$"))


def fig15_mfb_pp():
    R, C = elm.Resistor, elm.Capacitor
    _mfb("fig15_mfb_pp", (R, "$R_1$"), (R, "$R_3$"), (C, "$C$"), (R, "$R_2$"), (C, "$C$"))


def fig15_twint():
    """Aktivní pásmová zádrž s dvojitým T-článkem (slide „Pásmová zádrž – dvojitý T článek“): R/2 vede na výstup."""
    with schema("fig15_twint", unit=2.2) as d:
        u = d.unit
        svorka(d, (0, 0), VST)
        elm.Line().right(u * 0.3)
        v = elm.Dot()
        elm.Resistor().right().label("$R$", loc="bottom")
        b = elm.Dot()
        elm.Resistor().right().label("$R$", loc="bottom")
        p = elm.Dot()
        elm.Capacitor().at(b.center).down().label("$2C$", loc="bottom")
        elm.Ground()
        elm.Line().at(v.center).up(u * 1.4)
        elm.Capacitor().right().label("$C$", loc="bottom")
        a = elm.Dot()
        elm.Capacitor().right().label("$C$", loc="bottom")
        elm.Line().down().toy(p.center)
        op = elm.Opamp(leads=True, flip=True).right().anchor("in2").at((p.center[0] + u * 0.5, p.center[1]))
        elm.Line().at(p.center).tox(op.in2)
        elm.Line().at(op.in1).left(u * 0.25)
        elm.Line().down(u * 0.5)
        m = elm.Dot()
        elm.Resistor().right().tox(op.out).label("$R_2$", loc="bottom")
        elm.Line().up().toy(op.out).dot()
        elm.Resistor().at(m.center).down().label("$R_1$", loc="bottom")
        elm.Ground()
        elm.Resistor().at(a.center).up(u * 0.7).label("$R/2$", loc="bottom", color=C2).color(C2)
        elm.Line().right().tox(op.out).color(C2)
        elm.Line().down().toy(op.out).color(C2)
        _vystup(d, op, VYST)


def fig15_wien():
    """Wienův-Robinsonův můstek (pasivní, slide „Pásmová zádrž – Wienův-Robinsonův můstek“ vpravo)."""
    with schema("fig15_wien", unit=2.0) as d:
        u = d.unit
        svorka(d, (0, 0), VST)
        elm.Line().right(u * 0.9)
        t1 = elm.Dot()
        elm.Line().right(u * 2.4)
        elm.Resistor().down(u * 1.2).label("$2R_1$")
        y = elm.Dot()
        elm.Resistor().down().label("$R_1$")
        elm.Ground()
        elm.Resistor().at(t1.center).down(u).label("$R$", loc="bottom")
        elm.Capacitor().down(u).label("$C$", loc="bottom")
        x = elm.Dot()
        elm.Resistor().down().label("$R$", loc="bottom")
        elm.Ground()
        elm.Line().at(x.center).left(u * 0.8)
        elm.Capacitor().down().label("$C$", loc="top")
        elm.Ground()
        xm = t1.center[0] + u * 1.2
        elm.Line().at(x.center).tox(xm)
        elm.Dot(open=True).label("$-$", loc="left")
        elm.Line().at(y.center).tox(xm)
        elm.Dot(open=True).label("$+$", loc="left")
        elm.Label().at((xm + u * 0.15, (x.center[1] + y.center[1]) / 2)).label(VYST, loc="right")


def fig15_kaskada_schema():
    """Kaskáda čtyř RC článků oddělených sledovači (slide „Příklad kaskády filtrů“)."""
    with schema("fig15_kaskada_schema", unit=1.9) as d:
        u = d.unit
        svorka(d, (0, 0), VST)
        bod = (0, 0)
        for i in range(4):
            elm.Resistor().at(bod).right().label("$R$")
            n = elm.Dot()
            elm.Capacitor().at(n.center).down().label("$C$", loc="bottom")
            elm.Ground()
            op = elm.Opamp(leads=True, flip=True).right().anchor("in2").at((n.center[0] + u * 0.4, n.center[1]))
            elm.Line().at(n.center).tox(op.in2)
            _sledovac_zv(d, op, 0.35)
            bod = elm.Line().at(op.out).right(u * 0.3).end
        elm.Dot(open=True).at(bod).label(VYST, loc="right")


def _h_ab(om, a1, b1, a0=1.0):
    s = 1j * om
    return a0 / (1 + a1 * s + b1 * s * s)


def fig15_idealni_realny():
    """Ideální a reálná DP (slidy „Charakteristika ideálního / reálného filtru“), reálná = Butterworth 4. řádu."""
    om = np.logspace(-1, 1, 800)
    real = -10 * np.log10(1 + om ** 8)
    w1 = (10 ** 4 - 1) ** (1 / 8)                       # kde reálná DP klesne na A2 = −40 dB
    fig, ax = plt.subplots(figsize=(7.8, 3.9))
    ax.axvspan(0.1, 1, color=C1, alpha=0.08, lw=0)
    ax.axvspan(1, w1, color=C2, alpha=0.10, lw=0)
    ax.axvspan(w1, 10, color=C3, alpha=0.08, lw=0)
    ax.plot([0.1, 1, 1, 10], [0, 0, -70, -70], color=INK2, lw=1.4, ls="--", label="ideální DP")
    ax.plot(om, real, color=C1, label="reálná DP (4. řád)")
    ax.axhline(-3.01, color=MUTED, lw=0.8, ls=":")
    ax.axhline(-40, color=MUTED, lw=0.8, ls=":")
    ax.plot([1, w1], [-3.01, -40], "o", color=C1, mec=SURF)
    ax.text(0.105, -4.5, "$A_1$ = −3 dB", fontsize=9.5, color=INK2, va="top")
    ax.text(0.105, -41.5, "$A_2$ = −40 dB", fontsize=9.5, color=INK2, va="top")
    for x, txt in [(0.3, "pásmo\npropustnosti"), (np.sqrt(w1), "přechodová\noblast"), (6.0, "pásmo\nútlumu")]:
        ax.text(x, -58, txt, fontsize=9.5, color=INK2, ha="center", weight="semibold")
    ax.set_xscale("log")
    ax.set_xticks([0.1, 1, w1, 10])
    ax.set_xticklabels(["0,1", "$\\omega_0$", "$\\omega_1$", "10"])
    ax.xaxis.set_minor_locator(mticker.NullLocator())
    ax.set_xlim(0.1, 10)
    ax.set_ylim(-72, 5)
    ax.set_xlabel("normovaná frekvence Ω = ω/ω₀ (log. osa)")
    ax.set_ylabel("|A| [dB]")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_title("Ideální a reálná dolní propust", loc="left")
    save(fig, "fig15_idealni_realny")


def fig15_strmost():
    """HP 1. řádu s f_M = 1,8 kHz: oktávy a dekády pod mezní frekvencí (příklad ze slidů „Řád filtru a strmost“)."""
    fM = 1800.0
    f = np.logspace(1, 5, 800)
    fig, ax = plt.subplots(figsize=(7.8, 4.0))
    ax.plot(f, np.minimum(0, 20 * np.log10(f / fM)), color=MUTED, lw=1.2, ls="--", label="asymptota")
    ax.plot(f, db(h_hp(f, fM)), color=C1, label="HP 1. řádu, $f_M$ = 1,8 kHz")
    body = [(1800, "o", C1, (12, -10)), (900, "s", C2, (10, -14)), (450, "s", C2, (8, -4)),
            (180, "^", C3, (8, -4)), (18, "^", C3, (8, -4))]
    for fx, mk, col, off in body:
        y = db(h_hp(fx, fM))
        ax.plot(fx, y, mk, color=col, ms=7, mec=SURF)
        ax.annotate(f"{cz(fx, 0)} Hz: {cz(y, 1)} dB".replace("-", "−"), (fx, y), xytext=off,
                    textcoords="offset points", fontsize=9, color=INK2)
    ax.text(25, -14, "oktáva (½ f): asi −6 dB\ndekáda (⅒ f): −20 dB", fontsize=9.5, color=INK2)
    log_osa(ax, "frekvence f [Hz] (log. osa)")
    ax.set_xticks([10, 100, 1000, 10000, 100000])
    ax.set_xticklabels(["10", "100", "1 k", "10 k", "100 k"])
    ax.set_xlim(10, 1e5)
    ax.set_ylim(-50, 5)
    ax.set_ylabel("|H| [dB]")
    ax.legend(loc="lower right", fontsize=9)
    ax.set_title("Strmost 6 dB/okt = 20 dB/dek (horní propust 1. řádu)", loc="left")
    save(fig, "fig15_strmost")


def fig15_sk_q():
    """DP 2. řádu s koeficienty z tabulky slidu „DP typu Sallen-Key“ (normovaná frekvence)."""
    om = np.logspace(-1, 1, 800)
    fig, ax = plt.subplots(figsize=(7.8, 3.9))
    for (nazev, a1, b1), col, mk in zip([("Bessel, Q = 0,58", 1.3617, 0.6180),
                                         ("Butterworth, Q = 0,71", 1.4142, 1.0),
                                         ("Čebyšev 3 dB, Q = 1,3", 1.065, 1.9305)], CAT, MARK):
        y = db(_h_ab(om, a1, b1))
        ax.plot(om, y, color=col, label=nazev, marker=mk, markevery=80, ms=5)
    ax.axhline(-3.01, color=MUTED, lw=0.8, ls=":")
    ax.axvline(1, color=MUTED, lw=0.8, ls=":")
    ax.text(0.105, -2.4, "−3 dB", fontsize=9, color=INK2)
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    ax.set_xlim(0.1, 10)
    ax.set_ylim(-45, 6)
    ax.set_xlabel("normovaná frekvence $\\Omega = f/f_c$ (log. osa)")
    ax.set_ylabel("|A| [dB]")
    ax.legend(loc="lower left", fontsize=9)
    ax.set_title("Dolní propust 2. řádu: stejné zapojení, jiné a₁, b₁", loc="left")
    save(fig, "fig15_sk_q")


def _mfb_pp(f, fm, Q, Am, C):
    R2 = Q / (np.pi * fm * C)
    R1 = R2 / (2 * Am)
    K = (2 * np.pi * fm * C) ** 2 * R2
    R3 = R1 / (K * R1 - 1)
    s = 1j * 2 * np.pi * f
    return -(s / (R1 * C)) / (s * s + 2 * s / (R2 * C) + (1 / R1 + 1 / R3) / (R2 * C * C))


def fig15_pp_mfb():
    """Pásmová propust MFB: f_m = 1 kHz, |A_m| = 2, C = 10 nF; Q = 5 a Q = 2 (vlastní čísla; R3 > 0 vyžaduje |A_m| < 2Q²)."""
    f = np.logspace(2, 4, 1200)
    fig, ax = plt.subplots(figsize=(7.8, 3.9))
    for Q, col, mk in [(5, C1, "o"), (2, C2, "s")]:
        ax.plot(f, db(_mfb_pp(f, 1000, Q, 2, 10e-9)), color=col, marker=mk, markevery=150, ms=5,
                label=f"Q = {Q}: B = {1000 // Q:.0f} Hz")
    pk = 20 * np.log10(2)
    ax.axhline(pk - 3.01, color=MUTED, lw=0.8, ls=":")
    for fx in (905.0, 1105.0):
        ax.plot(fx, pk - 3.01, "o", color=INK, ms=5, mec=SURF)
    ax.annotate("905 Hz a 1105 Hz:\n−3 dB pod vrcholem", (905, pk - 3.01), xytext=(-150, -30),
                textcoords="offset points", fontsize=9, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("vrchol $|A_m|$ = 2 (6,02 dB)\nna $f_m$ = 1 kHz", (1000, pk), xytext=(30, 2),
                textcoords="offset points", fontsize=9, color=INK2)
    log_osa(ax, "frekvence f [Hz] (log. osa)")
    ax.set_xticks([100, 1000, 10000])
    ax.set_xticklabels(["100", "1 k", "10 k"])
    ax.set_ylim(-30, 12)
    ax.set_ylabel("|A| [dB]")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("Pásmová propust MFB: Q určuje šířku pásma", loc="left")
    save(fig, "fig15_pp_mfb")


def fig15_pz_q():
    """Pásmová zádrž A(s) = (1 + s²)/(1 + s/Q + s²) na 50 Hz pro Q = 0,25; 1; 10 (jako graf na slidu)."""
    f = np.logspace(0, 4, 3000)
    fig, ax = plt.subplots(figsize=(7.8, 3.9))
    for Q, col, mk in [(0.25, C1, "o"), (1, C2, "s"), (10, C3, "^")]:
        s = 1j * f / 50
        ax.plot(f, db((1 + s * s) / (1 + s / Q + s * s)), color=col, marker=mk, markevery=300, ms=5,
                label=f"Q = {cz(Q, 2).rstrip('0').rstrip(',')}")
    ax.axhline(-3.01, color=MUTED, lw=0.8, ls=":")
    ax.text(1.1, -2.5, "−3 dB", fontsize=9, color=INK2)
    log_osa(ax, "frekvence f [Hz] (log. osa)")
    ax.set_xticks([1, 10, 50, 100, 1000, 10000])
    ax.set_xticklabels(["1", "10", "50", "100", "1 k", "10 k"])
    ax.set_ylim(-40, 3)
    ax.set_ylabel("|A| [dB]")
    ax.legend(loc="lower left", fontsize=9)
    ax.set_title("Pásmová zádrž na 50 Hz: čím větší Q, tím užší zářez", loc="left")
    save(fig, "fig15_pz_q")


def fig15_kaskada():
    """1. řád, kaskáda 4 RC článků (každý s mezní frekvencí 2,3 Ω) a Butterworth 4. řádu: amplituda a fáze."""
    om = np.logspace(-2, 2, 1200)
    k = 1 / np.sqrt(2 ** 0.25 - 1)
    b4, a4 = signal.butter(4, 1, analog=True)
    _, hb = signal.freqs(b4, a4, worN=om)
    krivky = [("1. řád (jeden RC článek)", 1 / (1 + 1j * om)),
              ("4 RC články za sebou", (1 / (1 + 1j * om / k)) ** 4),
              ("Butterworth 4. řádu", hb)]
    fig, axs = plt.subplots(2, 1, figsize=(7.8, 5.6), sharex=True)
    for (nazev, h), col, mk in zip(krivky, CAT, MARK):
        axs[0].plot(om, db(h), color=col, marker=mk, markevery=150, ms=5, label=nazev)
        axs[1].plot(om, np.degrees(np.unwrap(np.angle(h))), color=col, marker=mk, markevery=150, ms=5)
    axs[0].axhline(-3.01, color=MUTED, lw=0.8, ls=":")
    axs[0].set_ylim(-80, 5)
    axs[0].set_ylabel("|A| [dB]")
    axs[0].legend(loc="lower left", fontsize=9)
    axs[0].set_title("Kaskáda filtrů: 4 stejné články nejsou „ideální“ 4. řád", loc="left")
    axs[1].set_ylim(-370, 10)
    axs[1].set_yticks([0, -90, -180, -270, -360])
    axs[1].set_ylabel("fáze φ [°]")
    axs[1].set_xscale("log")
    axs[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    axs[1].set_xlabel("normovaná frekvence $\\Omega = f/f_c$ (log. osa)")
    save(fig, "fig15_kaskada")


def fig15_butterworth():
    """Butterworthova DP řádu 1, 2, 4 a 10 (slide „Butterworthova aproximace DP“)."""
    om = np.logspace(-1, 2, 1200)
    fig, ax = plt.subplots(figsize=(7.8, 3.9))
    barvy = [C1, C2, C3, INK2]
    for n, col, mk in zip([1, 2, 4, 10], barvy, ["o", "s", "^", "D"]):
        ax.plot(om, -10 * np.log10(1 + om ** (2 * n)), color=col, marker=mk, markevery=150, ms=5,
                label=f"{n}. řád")
    ax.axhline(-3.01, color=MUTED, lw=0.8, ls=":")
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    ax.set_xlim(0.1, 100)
    ax.set_ylim(-60, 5)
    ax.set_xlabel("normovaná frekvence $\\Omega = f/f_c$ (log. osa)")
    ax.set_ylabel("|A| [dB]")
    ax.legend(loc="lower left", fontsize=9)
    ax.set_title("Butterworth: plochý vršek, s řádem strmější pokles", loc="left")
    save(fig, "fig15_butterworth")


def fig15_aproximace():
    """Bessel, Butterworth a Čebyšev (zvlnění 3 dB), vše 4. řád s −3 dB v Ω = 1: amplituda, fáze, skupinové zpoždění."""
    om = np.logspace(-1, 1, 2000)
    filtry = [("Butterworth", signal.butter(4, 1, analog=True)),
              ("Čebyšev (zvlnění 3 dB)", signal.cheby1(4, 3, 1, analog=True)),
              ("Bessel", signal.bessel(4, 1, analog=True, norm="mag"))]
    fig, axs = plt.subplots(3, 1, figsize=(7.8, 7.6), sharex=True)
    for (nazev, (b, a)), col, mk in zip(filtry, CAT, MARK):
        _, h = signal.freqs(b, a, worN=om)
        faze = np.unwrap(np.angle(h))
        tg = -np.gradient(faze, om)
        kw = dict(color=col, marker=mk, markevery=250, ms=5)
        axs[0].plot(om, db(h), label=nazev, **kw)
        axs[1].plot(om, np.degrees(faze), **kw)
        axs[2].plot(om, tg, **kw)
    axs[0].axhline(-3.01, color=MUTED, lw=0.8, ls=":")
    axs[0].set_ylim(-60, 5)
    axs[0].set_ylabel("|A| [dB]")
    axs[0].legend(loc="lower left", fontsize=9)
    axs[0].set_title("Tři aproximace dolní propusti 4. řádu", loc="left")
    axs[1].set_ylim(-370, 10)
    axs[1].set_yticks([0, -90, -180, -270, -360])
    axs[1].set_ylabel("fáze φ [°]")
    axs[2].set_ylabel("skup. zpoždění $\\tau_g \\omega_c$")
    axs[2].set_ylim(0, 6)
    axs[2].set_xscale("log")
    axs[2].xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    axs[2].set_xlabel("normovaná frekvence $\\Omega = \\omega/\\omega_c$ (log. osa)")
    save(fig, "fig15_aproximace")


# =====================================================================  přednáška 6: omezovač, komparátor, Schmitt, flash ADC
def _omez_stupen(d, ox, y0, ref, popis_d, nazvy, horni, vst=None, alt=None):
    """Jeden stupeň omezovače (slide „Omezovač“): OZ1 s diodou D ve zpětné vazbě za sledovačem OZ2.
    horni=True: dioda vede z uzlu k výstupu OZ1 (omezení shora), jinak naopak (omezení zdola);
    vst = popisek vstupní svorky (None = navazuje na předchozí stupeň); alt = popisek čárkované druhé diody."""
    u = d.unit
    op1 = elm.Opamp(leads=True).right().at((ox, y0)).anchor("in2").label(nazvy[0], loc="center", fontsize=11)
    elm.Line().at(op1.in2).left(u * 0.35)
    elm.Dot(open=True).label(ref, loc="left")
    elm.Line().at(op1.in1).left(u * 0.2)
    n = elm.Dot()
    elm.Resistor().left(u * 0.9).label("$R_1$", loc="bottom")
    if vst:
        elm.Dot(open=True).label(vst, loc="left")
    xk = op1.out[0] + u * 0.9
    elm.Line().at(op1.out).right(u * 0.1)
    a = elm.Dot()
    dd = elm.Diode().right().tox(xk).label(popis_d)
    if horni:
        dd.reverse()
    k = elm.Dot()
    if alt:
        ya = op1.out[1] - u * 0.75
        elm.Line().at(a.center).down().toy(ya).color(MUTED)
        dd2 = elm.Diode().right().tox(xk).label(alt, loc="bottom").color(MUTED).linestyle("--")
        if not horni:
            dd2.reverse()
        elm.Line().up().toy(k.center).color(MUTED)
    yt = op1.in1[1] + u * 0.55
    elm.Line().at(n.center).up().toy(yt)
    elm.Line().right().tox(xk)
    elm.Line().down().toy(k.center)
    op2 = elm.Opamp(leads=True).right().at((xk + u * 0.5, k.center[1])).anchor("in2").label(nazvy[1], loc="center", fontsize=11)
    elm.Line().at(k.center).right().tox(op2.in2)
    elm.Line().at(op2.in1).left(u * 0.25)
    elm.Line().up(u * 0.45)
    elm.Line().right().tox(op2.out)
    elm.Line().down().toy(op2.out).dot()
    elm.Label().at((k.center[0] + 0.05, k.center[1] - 0.38)).label("$U_+$", fontsize=11)
    return op1, op2


def fig16_omezovac():
    """Precizní omezovač: D1 omezuje shora, místo ní D2 zdola (slide „Omezovač“)."""
    with schema("fig16_omezovac", unit=2.3) as d:
        op1, op2 = _omez_stupen(d, 0, 0, "$U_\\mathrm{REF}$", "$D_1$", ("OZ1", "OZ2"), True, vst="$u_i$", alt="$D_2$")
        elm.Line().at(op2.out).right(d.unit * 0.4)
        elm.Dot(open=True).label("$u_o$", loc="right")


def fig16_oboustranny():
    """Oboustranný omezovač: dva stupně za sebou (slide „Oboustranný omezovač“), druhý stupeň pod prvním."""
    with schema("fig16_oboustranny", unit=2.0) as d:
        u = d.unit
        op1, op2 = _omez_stupen(d, 0, 0, "$U_\\mathrm{REF1}$", "$D_1$", ("OZ1", "OZ2"), True, vst="$u_i$")
        p = op2.out
        y0 = -4.4
        ymid = -1.0
        xs = -1.1 * u
        elm.Line().at(p).down().toy(ymid)
        elm.Line().left().tox(xs)
        elm.Line().down().toy(y0 + 1.25).dot()
        op3, op4 = _omez_stupen(d, 0, y0, "$U_\\mathrm{REF2}$", "$D_2$", ("OZ3", "OZ4"), False)
        elm.Line().at(op4.out).right(u * 0.4)
        elm.Dot(open=True).label("$u_o$", loc="right")


def fig16_zener_omezovac():
    """Invertující zesilovač s antisériovými Zenerovými diodami a R2 ve zpětné vazbě (slide „… s vlastním referenčním napětím“)."""
    with schema("fig16_zener_omezovac", unit=2.3) as d:
        u = d.unit
        op = elm.Opamp(leads=True)
        _vstup_zem(d, op)
        elm.Line().at(op.in1).left(u * 0.2)
        n = elm.Dot()
        elm.Resistor().left(u * 0.9).label("$R_1$", loc="bottom")
        elm.Dot(open=True).label("$u_i$", loc="left")
        xb = op.out[0] + u * 0.35
        y1 = op.in1[1] + u * 0.6
        y2 = y1 + u * 0.7
        elm.Line().at(n.center).up().toy(y2)
        elm.Resistor().right().tox(xb).label("$R_2$")
        elm.Line().down().toy(y1)
        elm.Dot()
        elm.Line().down().toy(op.out[1])
        elm.Dot()
        elm.Line().at(op.out).right().tox(xb)
        elm.Line().at((xb, op.out[1])).right(u * 0.35)
        elm.Dot(open=True).label("$u_o$", loc="right")
        elm.Dot().at((n.center[0], y1))
        elm.Line().at((n.center[0], y1)).right(u * 0.2)
        elm.Zener().right(u * 0.75).label("$D_1$")
        elm.Zener().right(u * 0.75).reverse().label("$D_2$")
        elm.Line().tox(xb)


def _zd_mustek(d, cx, cy, r=1.5, popisy=True):
    """Zenerova dioda v diodovém můstku (X nahoře, Y dole; ZD vodorovně mezi L a R). Vrací body X a Y."""
    X, Y, L, R = (cx, cy + r), (cx, cy - r), (cx - r, cy), (cx + r, cy)
    for a, b in ((X, L), (Y, L), (R, X), (R, Y)):
        elm.Diode().endpoints(a, b)
    elm.Zener().endpoints(R, L)
    if popisy:
        h, o = r / 2, 0.62
        for t, sx, sy in (("$D_1$", -1, 1), ("$D_3$", 1, 1), ("$D_4$", -1, -1), ("$D_2$", 1, -1)):
            elm.Label().at((cx + sx * (h + o), cy + sy * (h + o))).label(t, fontsize=10)
        elm.Label().at((cx, cy - 0.7)).label("ZD", fontsize=10)
    return X, Y


def fig16_zd_mustek():
    """Oboustranný omezovač s jedinou Zenerovou diodou v můstku (slide „… s vlastním referenčním napětím“, 2.)."""
    with schema("fig16_zd_mustek", unit=2.2) as d:
        u = d.unit
        op = elm.Opamp(leads=True)
        _vstup_zem(d, op)
        elm.Line().at(op.in1).left(u * 0.2)
        n = elm.Dot()
        elm.Resistor().left(u * 0.9).label("$R_1$", loc="bottom")
        elm.Dot(open=True).label("$u_i$", loc="left")
        r = 1.5
        cx = op.out[0] + u * 0.8
        cy = op.out[1] + r + 0.55
        ytop = cy + r + 0.4
        xr = cx + r + u * 1.3
        X, Y = _zd_mustek(d, cx, cy, r)
        elm.Line().at(n.center).up().toy(ytop)
        elm.Line().right().tox(X[0])
        elm.Dot()
        elm.Line().at(X).up().toy(ytop)
        elm.Resistor().at((X[0], ytop)).right().tox(xr).label("$R_2$")
        elm.Line().down().toy(op.out[1])
        elm.Dot()
        elm.Line().right(u * 0.35)
        elm.Dot(open=True).label("$u_o$", loc="right")
        elm.Line().at(op.out).right().tox(cx)
        elm.Dot()
        elm.Line().right().tox(xr)
        elm.Line().at(Y).down().toy(op.out[1])


def fig16_komp_omezeni():
    """Komparátor s omezením výstupního napětí: rezistor a Zenerova dioda v můstku (slide „… s omezením výstupního napětí“)."""
    with schema("fig16_komp_omezeni", unit=2.2) as d:
        u = d.unit
        op = elm.Opamp(leads=True)
        elm.Line().at(op.in1).left(u * 0.4)
        elm.Dot(open=True).label("$u_i$", loc="left")
        elm.Line().at(op.in2).left(u * 0.4)
        elm.Dot(open=True).label("$U_\\mathrm{REF}$", loc="left")
        elm.Resistor().at(op.out).right(u * 0.9)
        j = elm.Dot()
        elm.Line().right(u * 0.4)
        elm.Dot(open=True).label("$u_o$", loc="right")
        r = 1.5
        cy = op.out[1] - 0.55 - r - 0.4
        X, Y = _zd_mustek(d, j.center[0], cy, r)
        elm.Line().at(j.center).down().toy(X[1])
        elm.Line().at(Y).down(0.4)
        elm.Ground()


def fig16_schmitt():
    """Schmittův klopný obvod s OZ: R1, R2 a UREF tvoří kladnou zpětnou vazbu (slide „Schmittův klopný obvod“)."""
    with schema("fig16_schmitt", unit=2.2) as d:
        u = d.unit
        op = elm.Opamp(leads=True)
        elm.Line().at(op.in1).left(u * 0.4)
        elm.Dot(open=True).label("$U_i$", loc="left")
        xj = op.out[0] + u * 0.5
        elm.Line().at(op.out).right().tox(xj)
        j = elm.Dot()
        elm.Line().right(u * 0.35)
        elm.Dot(open=True).label("$U_o$", loc="right")
        elm.Resistor().at(j.center).down(u * 1.1).label("$R_2$", loc="bottom")
        m = elm.Dot()
        elm.Resistor().down(u * 1.1).label("$R_1$", loc="bottom")
        elm.Dot(open=True).label("$U_\\mathrm{REF}$", loc="bottom")
        elm.Line().at(m.center).left().tox(op.in2[0] - u * 0.3)
        elm.Line().up().toy(op.in2[1])
        elm.Line().right().tox(op.in2[0])
        elm.Label().at((op.in2[0] - u * 0.45, op.in2[1] + 0.3)).label("$U_+$", fontsize=11)


def fig16_schmitt_zd():
    """Schmittův KO s Zenerovou diodou v můstku: stálé saturační napětí (slide „… s vyloučením změn saturačního napětí“)."""
    with schema("fig16_schmitt_zd", unit=2.2) as d:
        u = d.unit
        op = elm.Opamp(leads=True)
        elm.Line().at(op.in1).left(u * 0.4)
        elm.Dot(open=True).label("$U_i$", loc="left")
        elm.Resistor().at(op.out).right(u * 0.9)
        j = elm.Dot()
        elm.Line().right(u * 1.3)
        k = elm.Dot()
        elm.Line().right(u * 0.35)
        elm.Dot(open=True).label("$U_o$", loc="right")
        r = 1.5
        cy = op.out[1] - 0.55 - r - 0.4
        X, Y = _zd_mustek(d, j.center[0], cy, r)
        elm.Line().at(j.center).down().toy(X[1])
        elm.Line().at(Y).down(0.4)
        elm.Ground()
        yz = Y[1] - 3.2
        elm.Resistor().at(k.center).down().toy(yz + 1.5).label("$R_2$", loc="bottom")
        m = elm.Dot()
        elm.Resistor().down().toy(yz).label("$R_1$", loc="bottom")
        elm.Ground()
        elm.Line().at(m.center).left().tox(op.in2[0] - u * 0.3)
        elm.Line().up().toy(op.in2[1])
        elm.Line().right().tox(op.in2[0])
        elm.Label().at((op.in2[0] - u * 0.45, op.in2[1] + 0.3)).label("$U_+$", fontsize=11)


def fig16_selektor():
    """Amplitudový selektor: tři OZ s diodami na společném vodiči (slidy „K čemu slouží toto zapojení?“)."""
    with schema("fig16_selektor", unit=2.0) as d:
        xr = -0.7                                           # společný vodič
        p = 3.2
        ops = []
        for i in range(3):
            yc = -i * p
            op = elm.Opamp(leads=True).right().at((0, yc - 0.625)).anchor("in2").label(f"OZ{i + 1}", loc="center", fontsize=11)
            ops.append(op)
        ytop = ops[0].in1[1] + 0.8
        elm.Dot(open=True).at((xr, ytop + 0.5)).label("$U_\\mathrm{omax}$", loc="top")
        elm.Line().at((xr, ytop + 0.5)).down().toy(ops[2].in2[1] - 0.2)
        for i, op in enumerate(ops):
            elm.Line().at(op.in1).left().tox(xr)
            elm.Dot()
            elm.Line().at(op.in2).left().tox(-2.0)
            elm.Dot(open=True).label(f"$U_{{i{i + 1}}}$", loc="left")
            xk = op.out[0] + 0.5
            yd = op.in1[1] + 0.95
            elm.Dot().at((xr, yd))
            elm.Line().at((xr, yd)).right(0.3)
            elm.Diode().right().tox(xk - 0.4).reverse().label(f"$D_{i + 1}$")
            elm.Line().tox(xk)
            elm.Line().down().toy(op.out[1]).dot()
            elm.Line().at(op.out).right().tox(xk)
            elm.Line().at((xk, op.out[1])).right(0.4)
            elm.Dot(open=True).label(f"$U_{{o{i + 1}}}$", loc="right")
        yb = ops[2].in2[1] - 0.2
        elm.Line().at((xr, yb)).down(0.2)
        elm.Resistor().down().label("$R$", loc="bottom")
        elm.Ground()


def fig16_flash():
    """Paralelní (flash) ADC: 3 bity, VREF = 8 V, VIN = 3,8 V (slidy „Paralelní ADC“)."""
    with schema("fig16_flash", unit=2.0) as d:
        p = 2.6
        prahy = [6.5, 5.5, 4.5, 3.5, 2.5, 1.5, 0.5]
        vin = 3.8
        xl, xb, xc = 0.0, 2.2, 4.5
        ops, taps = [], []
        for k in range(7):
            op = elm.Opamp(leads=True).right().at((xc, -k * p - 0.625)).anchor("in2")
            ops.append(op)
            taps.append(op.in1[1])
        ytop = taps[0] + p
        # žebřík
        elm.Line().at((xl, ytop)).left(0.35)
        elm.Dot(open=True).label("$V_\\mathrm{REF}$ = 8 V", loc="left")
        zn = [ytop] + taps + [taps[6] - p]
        for j, (y1, y2) in enumerate(zip(zn[:-1], zn[1:])):
            elm.Resistor().at((xl, y1)).down().toy(y2)
            elm.Label().at((xl + 0.55, (y1 + y2) / 2)).label("3R/2" if j == 0 else ("R/2" if j == 7 else "R"), fontsize=10)
        elm.Ground()
        # sběrnice VIN
        yv = ytop + 0.9
        elm.Line().at((xl - 0.35, yv)).right().tox(xb)
        elm.Dot(open=True).at((xl - 0.35, yv)).label("$V_\\mathrm{IN}$ = 3,8 V", loc="left")
        elm.Line().at((xb, yv)).down().toy(ops[6].in2[1])
        for k, op in enumerate(ops):
            elm.Dot().at((xl, taps[k]))
            elm.Line().at((xl, taps[k])).right().tox(xc)
            elm.Label().at((xl + 0.95, taps[k] + 0.2)).label(f"{prahy[k]:.1f} V".replace(".", ","), fontsize=10)
            elm.Line().at(op.in2).left().tox(xb)
            elm.Dot().at((xb, op.in2[1]))
        # kodér
        xe = xc + 3.415 + 1.0
        ye1, ye2 = ops[0].out[1] + 0.9, ops[6].out[1] - 0.9
        for a, b in (((xe, ye1), (xe + 2.0, ye1)), ((xe + 2.0, ye1), (xe + 2.0, ye2)),
                     ((xe + 2.0, ye2), (xe, ye2)), ((xe, ye2), (xe, ye1))):
            elm.Line().at(a).to(b)
        elm.Label().at((xe + 1.0, (ye1 + ye2) / 2)).label("kodér\n(priority\nencoder)", fontsize=11)
        for k, op in enumerate(ops):
            zap = prahy[k] < vin
            col = C3 if zap else MUTED
            elm.Line().at(op.out).right().tox(xe).color(col)
            elm.Label().at((op.out[0] + 0.5, op.out[1] + 0.22)).label("1" if zap else "0", fontsize=11, color=col)
        ymid = (ye1 + ye2) / 2
        for j, (nm, val) in enumerate((("D2", "1"), ("D1", "0"), ("D0", "0"))):
            y = ymid + (1 - j) * 1.2
            elm.Line().at((xe + 2.0, y)).right(0.5)
            elm.Dot(open=True).label(f"{nm} = {val}", loc="right")


def _osy_nula(ax):
    """Osy procházející nulou (převodní charakteristiky)."""
    ax.axhline(0, color=AXIS, lw=1)
    ax.axvline(0, color=AXIS, lw=1)


def fig16_omezovac_char():
    """Převodní charakteristiky precizního omezovače: D1 omezuje shora, D2 zdola (slide „Omezovač“)."""
    ui = np.linspace(-5, 5, 400)
    fig, axs = plt.subplots(1, 2, figsize=(9.4, 4.3), sharey=True)
    for ax, ref, f, titul, pop in (
            (axs[0], (3, 1, -2), np.minimum, "zapojená $D_1$: omezení shora", "$U_\\mathrm{REF}$"),
            (axs[1], (-3, -1, 2), np.maximum, "zapojená $D_2$: omezení zdola", "$U_\\mathrm{REF}$")):
        _osy_nula(ax)
        ax.plot(ui, ui, color=MUTED, lw=1.2, ls="--", label="$u_o = u_i$")
        for i, r in enumerate(ref):
            ax.plot(ui, f(ui, r), color=CAT[i], lw=2.2, marker=MARK[i], markevery=(60 + 40 * i, 120), ms=6,
                    label=f"{pop} = {r} V".replace("-", "−"))
        ax.set_title(titul)
        ax.set_xlabel("vstupní napětí $u_i$ [V]")
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.legend(loc="lower right" if f is np.minimum else "upper left", fontsize=9)
    axs[0].set_ylabel("výstupní napětí $u_o$ [V]")
    save(fig, "fig16_omezovac_char")


def fig16_oboustranny_char():
    """Charakteristika oboustranného omezovače: symetrická a nesymetrická (slide „Oboustranný omezovač“)."""
    ui = np.linspace(-5, 5, 400)
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    _osy_nula(ax)
    ax.plot(ui, ui, color=MUTED, lw=1.2, ls="--", label="$u_o = u_i$")
    ax.plot(ui, np.clip(ui, -3, 3), color=C1, lw=2.4, marker=MARK[0], markevery=(40, 120), ms=6,
            label="$U_\\mathrm{REF1}$ = 3 V, $U_\\mathrm{REF2}$ = −3 V")
    ax.plot(ui, np.clip(ui, -1.5, 3), color=C2, lw=2.0, marker=MARK[1], markevery=(70, 120), ms=6,
            label="$U_\\mathrm{REF1}$ = 3 V, $U_\\mathrm{REF2}$ = −1,5 V")
    ax.set_xlabel("vstupní napětí $u_i$ [V]")
    ax.set_ylabel("výstupní napětí $u_o$ [V]")
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect("equal")
    ax.legend(loc="upper left", fontsize=8.5)
    save(fig, "fig16_oboustranny_char")


def fig16_zener_char():
    """Charakteristika omezovače se Zenerovými diodami: symetrická a nesymetrická (slide „… s vlastním referenčním napětím“)."""
    ui = np.linspace(-1.6, 1.6, 600)
    k = 10.0                                            # R2/R1
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    _osy_nula(ax)
    for i, (uz2, c, m, txt) in enumerate(((9.4, C1, "o", "$U_{Z2}$ = 9,4 V (symetrické)"),
                                          (4.4, C2, "s", "$U_{Z2}$ = 4,4 V (nesymetrické)"))):
        uo = np.clip(-k * ui, -(uz2 + 0.6), 9.4 + 0.6)
        ax.plot(ui, uo, color=c, lw=2.2, marker=m, markevery=(80 + 60 * i, 200), ms=6, label=txt)
    ax.set_xlabel("vstupní napětí $u_i$ [V]")
    ax.set_ylabel("výstupní napětí $u_o$ [V]")
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-12, 12)
    ax.set_yticks([-10, -5, 0, 5, 10])
    ax.set_yticklabels(["−10", "−5", "0", "5", "10"])
    ax.annotate("$+10$ V = $U_{Z1}$ + 0,6 V", (-1.55, 10), (-1.5, 11.0), fontsize=9, color=INK2, va="bottom")
    ax.annotate("sklon −$R_2/R_1$", (-0.45, 4.5), (0.15, 7.5), fontsize=9, color=INK2,
                arrowprops=dict(arrowstyle="->", color=MUTED))
    ax.legend(loc="lower left", fontsize=9)
    save(fig, "fig16_zener_char")


def fig16_komparator_char():
    """Převodní charakteristika komparátoru se skutečnou šířkou lineární oblasti ±U_sat/A_u (slide „Charakteristika komparátoru“)."""
    usat, au = 12.0, 1e5
    ud = np.linspace(-300, 300, 1201)                    # [µV]
    uo = np.clip(au * ud * 1e-6, -usat, usat)
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    _osy_nula(ax)
    hr = usat / au * 1e6
    ax.axvspan(-hr, hr, color=C2, alpha=0.18, lw=0)
    ax.plot(ud, uo, color=C1, lw=2.4)
    ax.set_xlabel("rozdíl vstupů $u_{i2} - u_{i1}$ [µV]")
    ax.set_ylabel("výstupní napětí $u_o$ [V]")
    ax.set_ylim(-15, 15)
    ax.set_xlim(-300, 300)
    ax.set_yticks([-12, -6, 0, 6, 12])
    ax.set_yticklabels(["−$U_\\mathrm{sat}$ = −12", "−6", "0", "6", "$+U_\\mathrm{sat}$ = 12"])
    ax.set_xticks([-hr, 0, hr])
    ax.set_xticklabels(["−$U_\\mathrm{sat}/A_u$\n= −120", "0", "$U_\\mathrm{sat}/A_u$\n= 120"])
    ax.text(0, -6.3, "oblast přeběhu", ha="center", fontsize=9, color=C2)
    save(fig, "fig16_komparator_char")


def _komp_sim(ui, hi, lo, usat=12.0):
    """Komparátor s hysterezí: výstup +usat, dokud vstup nepřekročí hi; zpět se překlopí až pod lo."""
    uo = np.empty_like(ui)
    stav = usat
    for i, v in enumerate(ui):
        if stav > 0 and v > hi:
            stav = -usat
        elif stav < 0 and v < lo:
            stav = usat
        uo[i] = stav
    return uo


def fig16_rusivy():
    """Komparátor s pomalým vstupem, s rušením a s hysterezí (slide „Charakteristika komparátoru“)."""
    t = np.linspace(0, 1, 2000)
    ramp = 0.9 * t
    sum_ = 0.045 * np.sin(2 * np.pi * 23 * t) + 0.03 * np.sin(2 * np.pi * 57 * t + 1.0)
    thr = 0.45
    scen = (("bez rušení", ramp, thr, thr), ("s rušením", ramp + sum_, thr, thr),
            ("s hysterezí", ramp + sum_, thr, thr - 0.12))
    fig, axs = plt.subplots(2, 3, figsize=(10.6, 5.0), sharex=True, gridspec_kw=dict(height_ratios=[1.15, 1]))
    for j, (titul, ui, hi, lo) in enumerate(scen):
        a, b = axs[0, j], axs[1, j]
        a.plot(t, ui, color=C1, lw=1.8, label="$u_{i1}$")
        a.axhline(hi, color=C2, lw=1.8, ls="--", label="$u_{i2}$")
        if lo != hi:
            a.axhline(lo, color=C2, lw=1.4, ls=":")
            a.annotate("", (0.07, hi), (0.07, lo), arrowprops=dict(arrowstyle="<->", color=INK2))
            a.text(0.1, (hi + lo) / 2, "hystereze", fontsize=9, color=INK2, va="center")
        a.set_title(titul)
        a.set_ylim(-0.05, 1.0)
        b.step(t, _komp_sim(ui, hi, lo), where="post", color=C3, lw=2)
        b.set_ylim(-16, 16)
        b.set_yticks([-12, 0, 12])
        b.set_yticklabels(["−12", "0", "12"])
        b.set_xlabel("čas $t$ (libovolné jednotky)")
        a.set_xticks([])
        b.set_xticks([])
    axs[0, 0].set_ylabel("vstupy [V]")
    axs[1, 0].set_ylabel("výstup $u_o$ [V]")
    axs[0, 0].legend(loc="upper left", fontsize=9)
    save(fig, "fig16_rusivy")


def fig16_komp_omezeni_prubeh():
    """Komparátor s omezením: výstup ±(U_ZD + 2U_D) pro dvě referenční napětí (slide „… s omezením výstupního napětí“)."""
    t = np.linspace(0, 1, 1600)
    ui = 2.0 * np.interp(t % 1, [0, 0.25, 0.75, 1], [0, 1, -1, 0])
    ul = 4.7 + 2 * 0.6
    u1, u2 = 1.0, -1.0
    fig, axs = plt.subplots(3, 1, figsize=(7.6, 6.2), sharex=True, gridspec_kw=dict(height_ratios=[1.1, 1, 1]))
    axs[0].plot(t, ui, color=C1, lw=2, label="$u_i$")
    axs[0].axhline(u1, color=C2, lw=1.6, ls="--", label="$U_\\mathrm{REF} = U_1$")
    axs[0].axhline(u2, color=C3, lw=1.6, ls=":", label="$U_\\mathrm{REF} = U_2$")
    axs[0].set_ylabel("$u_i$ [V]")
    axs[0].set_ylim(-2.6, 2.9)
    axs[0].legend(loc="upper right", fontsize=8.5, ncol=3)
    for ax, ref, c, txt in ((axs[1], u1, C2, "$U_\\mathrm{REF} = U_1$"), (axs[2], u2, C3, "$U_\\mathrm{REF} = U_2$")):
        ax.step(t, np.where(ui < ref, ul, -ul), where="post", color=c, lw=2)
        ax.set_ylabel("$u_o$ [V]")
        ax.set_ylim(-9, 9)
        ax.set_yticks([-ul, 0, ul])
        ax.set_yticklabels(["−5,9", "0", "5,9"])
        ax.text(0.99, 7.0, txt, ha="right", va="center", fontsize=9, color=INK2)
    axs[2].set_xlabel("čas $t$ (libovolné jednotky)")
    axs[2].set_xticks([])
    save(fig, "fig16_komp_omezeni_prubeh")


def fig16_schmitt_char():
    """Hysterezní smyčka Schmittova KO (UREF = 2 V, R1 = 1 kΩ, R2 = 9 kΩ, U_sat = ±12 V)."""
    usat, ur, r1, r2 = 12.0, 2.0, 1.0, 9.0
    ua = usat * r1 / (r1 + r2) + ur * r2 / (r1 + r2)
    ub = -usat * r1 / (r1 + r2) + ur * r2 / (r1 + r2)
    st = ur * r2 / (r1 + r2)
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    _osy_nula(ax)
    kw = dict(color=C1, lw=2.4)
    ax.plot([-1.5, ua], [usat, usat], **kw)
    ax.plot([ua, ua], [usat, -usat], **kw)
    ax.plot([ua + 2.4, ub], [-usat, -usat], **kw)
    ax.plot([ub, ub], [-usat, usat], **kw)
    for x0, y0, x1, y1 in ((-0.2, usat, 0.5, usat), (ua, 3, ua, -3), (ua + 1.0, -usat, ua - 0.6, -usat), (ub, -3, ub, 3)):
        ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="-|>", color=C1, lw=2.4, mutation_scale=16))
    ax.plot([ua, ub], [0, 0], "o", color=C2, ms=7)
    ax.plot([st], [0], "s", color=C3, ms=7)
    ax.annotate("", (ua, 6.5), (ub, 6.5), arrowprops=dict(arrowstyle="<->", color=INK2))
    ax.text((ua + ub) / 2, 7.2, "$U_H$", ha="center", fontsize=11, color=INK2)
    ax.text(ua + 0.12, 1.4, f"$U_{{+a}}$ = {ua:.1f} V".replace(".", ","), fontsize=10, color=C2)
    ax.text(ub - 0.1, -2.4, f"$U_{{+b}}$ = {ub:.1f} V".replace(".", ","), fontsize=10, color=C2, ha="right")
    ax.text(st, -9.0, "střed hystereze\n$U_\\mathrm{REF}\\,R_2/(R_1+R_2)$ = 1,8 V", fontsize=9, color=C3, ha="center")
    ax.set_xlim(-1.5, 6.2)
    ax.set_ylim(-15, 15)
    ax.set_xlabel("vstupní napětí $U_i$ [V]")
    ax.set_ylabel("výstupní napětí $U_o$ [V]")
    ax.set_yticks([-12, 0, 12])
    ax.set_yticklabels(["$U_\\mathrm{sat}^-$ = −12", "0", "$U_\\mathrm{sat}^+$ = 12"])
    save(fig, "fig16_schmitt_char")


def fig16_selektor_prubeh():
    """Výstup amplitudového selektoru = maximum ze vstupů (slide „Amplitudový selektor“)."""
    t = np.linspace(0, 1, 800)
    uis = [3.0 + 2.2 * np.sin(2 * np.pi * (t + f)) for f in (0.0, 0.33, 0.66)]
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    for i, y in enumerate(uis):
        ax.plot(t, y, color=CAT[i], lw=1.5, label=f"$U_{{i{i + 1}}}$")
    ax.plot(t, np.max(uis, axis=0), color=INK, lw=3.4, alpha=0.55, label="$U_\\mathrm{omax}$ (maximum)")
    ax.set_xlabel("čas $t$ (libovolné jednotky)")
    ax.set_ylabel("napětí [V]")
    ax.set_xticks([])
    ax.legend(loc="lower center", ncol=4, fontsize=9, bbox_to_anchor=(0.5, 1.0))
    save(fig, "fig16_selektor_prubeh")


def fig16_kvantovani():
    """Vzorkování a kvantování 3bitovým převodníkem, VREF = 8 V (slidy „Analogově-digitální převodník“)."""
    t = np.linspace(0, 1, 800)
    sig = lambda x: 4.0 + 3.2 * np.sin(2 * np.pi * x)
    ts = np.arange(0, 1.0001, 1 / 16)
    k = np.clip(np.round(sig(ts)), 0, 7)
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    for lv in range(8):
        ax.axhline(lv, color=GRID, lw=0.8)
        ax.text(1.015, lv, f"{lv:03b}", va="center", fontsize=9, color=MUTED)
    ax.plot(t, sig(t), color=C1, lw=1.8, label="analogový signál")
    ax.step(ts, k, where="post", color=C3, lw=2.2, label="kvantovaný signál (po vzorcích)")
    ax.plot(ts, sig(ts), "o", color=C2, ms=6, label="vzorky")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.6, 8)
    ax.set_xticks([])
    ax.set_xlabel("čas $t$ (libovolné jednotky); vzorky po $T_s$")
    ax.set_ylabel("napětí [V] (kvantizační krok 1 V)")
    ax.text(1.015, 8.0, "kód", fontsize=9, color=MUTED, va="center")
    ax.legend(loc="lower center", ncol=3, fontsize=9, bbox_to_anchor=(0.5, 1.0))
    save(fig, "fig16_kvantovani")


def fig16_adc_char():
    """Převodní charakteristika 3bitového flash ADC, VREF = 8 V (slide s příkladem VIN = 3,8 V)."""
    vin = np.linspace(0, 8, 1601)
    kod = np.clip(np.floor(vin + 0.5), 0, 7)
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.step(vin, kod, where="post", color=C1, lw=2.4)
    ax.plot([3.8], [4], "s", color=C2, ms=9, zorder=5)
    ax.annotate("$V_\\mathrm{IN}$ = 3,8 V → kód 4 = (100)$_2$", (3.8, 4), (4.9, 2.2), fontsize=9.5, color=C2,
                arrowprops=dict(arrowstyle="->", color=C2))
    ax.axvspan(3.5, 4.5, color=C2, alpha=0.12, lw=0)
    ax.set_xlim(0, 8)
    ax.set_ylim(-0.3, 7.6)
    ax.set_xticks(range(0, 9))
    ax.set_yticks(range(8))
    ax.set_xlabel("vstupní napětí $V_\\mathrm{IN}$ [V]")
    ax.set_ylabel("výstupní kód (desítkově)")
    ax.text(0.15, 6.6, "kvantizační krok = 1 V,\nprahy 0,5; 1,5; …; 6,5 V", fontsize=9, color=INK2, va="center")
    save(fig, "fig16_adc_char")


# =====================================================================  přednáška 7: A/D a D/A převodníky
KOD17 = "101100"                                                   # B5…B0 v příkladech DAC (D = 44)


def _box(d, x0, y0, w, h, text, fontsize=12):
    """Obdélníkový blok (čítač, registr) z čar, text uprostřed."""
    for a, b in (((x0, y0), (x0 + w, y0)), ((x0 + w, y0), (x0 + w, y0 - h)),
                 ((x0 + w, y0 - h), (x0, y0 - h)), ((x0, y0 - h), (x0, y0))):
        elm.Line().at(a).to(b)
    elm.Label().at((x0 + w / 2, y0 - h / 2)).label(text, fontsize=fontsize)


def fig17_dac_vahovy():
    """DAC s váhovými rezistory R, 2R … 32R a invertujícím sčítacím OZ (slide „DAC typu R – 2R – 4R …“)."""
    with schema("fig17_dac_vahovy", unit=2.0) as d:
        p, xs, xn = 1.25, 1.6, 6.2
        nazvy = ["R", "2R", "4R", "8R", "16R", "32R"]
        ytop, ybot = 0.0, -5 * p
        elm.Line().at((0, ytop + 0.9)).down().toy(ybot)
        elm.Dot(open=True).at((0, ytop + 0.9)).label("$U_\\mathrm{REF}$", loc="top")
        for k in range(6):
            y = -k * p
            bit = KOD17[k]
            col = C3 if bit == "1" else MUTED
            elm.Dot().at((0, y))
            elm.Line().at((0, y)).right(0.4)
            elm.Switch(nc=(bit == "1")).right().to((xs, y)).color(col)
            elm.Label().at((0.95, y + 0.55)).label(f"$B_{5 - k}$ = {bit}", fontsize=10, color=col)
            elm.Resistor().at((xs, y)).right().to((xn, y)).label(nazvy[k], fontsize=11)
            elm.Dot().at((xn, y))
        elm.Line().at((xn, ytop)).down().toy(ybot)
        elm.Label().at((-1.0, ytop)).label("MSB", fontsize=11, color=C2)
        elm.Label().at((-1.0, ybot)).label("LSB", fontsize=11, color=C2)
        ym = -2.5 * p
        op = elm.Opamp(leads=True).right().at((xn + 0.9, ym)).anchor("in1")
        elm.Line().at((xn, ym)).to(op.in1)
        elm.Dot().at((xn, ym))
        elm.Line().at(op.in2).left(0.4)
        elm.Ground()
        elm.Line().at((xn, ytop)).up(0.9)
        elm.Resistor().right().tox(op.out[0] + 0.5).label("$R_f$")
        elm.Line().down().toy(op.out[1])
        elm.Line().at(op.out).right(0.5).dot()
        elm.Line().right(0.6)
        elm.Dot(open=True).label("$U_o$", loc="right")
        elm.Label().at((xn + 0.5, ym + 0.35)).label("$\\Sigma I$", fontsize=11, color=C1)


def fig17_dac_r2r():
    """Příčková síť R–2R s přepínači mezi U_REF a zemí a invertujícím OZ (slide „DAC typu R – 2R“)."""
    with schema("fig17_dac_r2r", unit=2.0) as d:
        s, yl = 2.3, 0.0
        ysw, ybus = -3.2, -5.2
        xs = [1.6 + k * s for k in range(6)]                      # uzly B0 … B5
        elm.Line().at((0, yl)).down(0.4)
        elm.Ground()
        elm.Resistor().at((0, yl)).right().to((xs[0], yl)).label("2R", fontsize=11)
        xr = []
        for k, x in enumerate(xs):
            bit = KOD17[5 - k]
            col = C3 if bit == "1" else MUTED
            elm.Dot().at((x, yl))
            if k < 5:
                elm.Resistor().at((x, yl)).right().to((xs[k + 1], yl)).label("R", fontsize=11)
            elm.Resistor().at((x, yl)).down().to((x, ysw)).label("2R", loc="bottom", fontsize=11)
            # pravý kontakt = sběrnice U_REF, levý = zem; páka (kontakt b) míří podle bitu
            sw = elm.SwitchSpdt2(action=None)
            if bit == "0":
                sw = sw.flip()
            sw = sw.at((x, ysw)).down().anchor("a").color(col)
            k_ref, k_zem = (sw.b, sw.c) if bit == "1" else (sw.c, sw.b)
            elm.Line().at(k_ref).down().toy(ybus)
            elm.Dot().at((k_ref[0], ybus))
            xr.append(k_ref[0])
            elm.Line().at(k_zem).down(0.25)
            elm.Ground()
            elm.Label().at((x + 0.95, ysw - 0.15)).label(f"$B_{k}$ = {bit}", fontsize=10, color=col)
        elm.Line().at((xs[0] - 1.6, ybus)).right().tox(max(xr))
        elm.Dot(open=True).at((xs[0] - 1.6, ybus)).label("$U_\\mathrm{REF}$", loc="left")
        elm.Label().at((xs[0], ybus - 0.6)).label("LSB", fontsize=11, color=C2)
        elm.Label().at((xs[5], ybus - 0.6)).label("MSB", fontsize=11, color=C2)
        op = elm.Opamp(leads=True).right().at((xs[5] + 2.0, yl)).anchor("in1")
        elm.Line().at((xs[5], yl)).to(op.in1)
        elm.Line().at(op.in2).left(0.4)
        elm.Ground()
        elm.Line().at((xs[5] + 0.7, yl)).up(1.4)
        elm.Resistor().right().tox(op.out[0] + 0.5).label("$R_f$")
        elm.Line().down().toy(op.out[1])
        elm.Line().at(op.out).right(0.5).dot()
        elm.Line().right(0.6)
        elm.Dot(open=True).label("$U_o$", loc="right")
        elm.Dot().at((xs[5] + 0.7, yl))


def _integrator17(d, vybiti):
    """Integrátor P7: OZ s C ve zpětné vazbě a spínačem pro vybití C; vrací (OZ, uzel invertujícího vstupu)."""
    u = d.unit
    op = elm.Opamp(leads=True)                                   # − (in1) nahoře, + (in2) dole
    elm.Line().at(op.in2).left(0.4)
    elm.Ground()
    elm.Line().at(op.in1).left(u * 0.25)
    n = elm.Dot()
    elm.Line().at(n.center).up(u * 0.6)
    m = elm.Dot()
    elm.Capacitor().right().tox(op.out[0] + 0.4).label("$C$")
    k = elm.Dot()
    elm.Line().down().toy(op.out[1])
    elm.Line().left().tox(op.out[0])
    elm.Line().at(m.center).up(u * 0.5)
    elm.Switch().right().tox(op.out[0] + 0.4).label(vybiti, color=C2, fontsize=11).color(C2)
    elm.Line().down().toy(k.center).color(C2)
    return op, n


def fig17_single_slope():
    """Single slope ADC: integrátor −U_REF, komparátor s U_IN, hradlo AND s hodinami a čítač (slidy „Single Slope ADC“)."""
    import schemdraw.logic as logic
    with schema("fig17_single_slope", unit=2.0) as d:
        op1, n = _integrator17(d, "vybití C")
        elm.Resistor().at(n.center).left().label("$R$")
        elm.Dot(open=True).label("$-U_\\mathrm{REF}$", loc="left")
        xo = op1.out[0] + 0.4
        op2 = elm.Opamp(leads=True).right().at((xo + 1.0, op1.out[1])).anchor("in1")
        elm.Line().at(op1.out).to(op2.in1)
        elm.Dot().at((xo, op1.out[1]))
        elm.Line().at(op2.in2).left(1.0)
        elm.Dot(open=True).label("$U_\\mathrm{IN}$", loc="left")
        elm.Label().at((op1.out[0] - 1.4, op1.out[1] - 1.9)).label("integrátor", fontsize=11, color=INK2)
        elm.Label().at((op2.out[0] - 1.4, op2.out[1] - 1.9)).label("komparátor", fontsize=11, color=INK2)
        elm.Line().at(op2.out).right(0.6)
        g = logic.And().right().anchor("in2")
        elm.Line().at(g.in1).left(0.6)
        elm.Line().up(0.8)
        elm.Dot(open=True).label("CLK", loc="top")
        elm.Line().at(g.out).right(0.6)
        x0, y0 = g.out[0] + 0.6, g.out[1] + 1.2
        _box(d, x0, y0, 2.2, 2.4, "čítač\n(Counter)", fontsize=11)
        for j in range(4):
            y = y0 - 0.5 - j * 0.47
            elm.Line().at((x0 + 2.2, y)).right(0.6)
        elm.Label().at((x0 + 3.6, y0 - 1.2)).label("binární\nvýstup", fontsize=11)


def fig17_dual_slope():
    """Dual slope ADC: integrátor s přepínačem U_IN / −U_REF na vstupu a spínačem paralelně k C (slidy „Dual Slope ADC“)."""
    with schema("fig17_dual_slope", unit=2.0) as d:
        op, n = _integrator17(d, "vybití C")
        elm.Resistor().at(n.center).left().label("$R$")
        sw = elm.SwitchSpdt2(action=None).left().anchor("a")
        elm.Line().at(sw.b).left(0.5)
        elm.Dot(open=True).label("$U_\\mathrm{IN}$", loc="left")
        elm.Line().at(sw.c).left(0.5)
        elm.Dot(open=True).label("$-U_\\mathrm{REF}$", loc="left")
        elm.Line().at(op.out).right(0.9)
        elm.Dot(open=True).label("$U_o$", loc="right")
        elm.Label().at((sw.a[0] - 0.6, sw.a[1] - 1.5)).label("1. fáze: $U_\\mathrm{IN}$ po dobu $T_1$\n2. fáze: $-U_\\mathrm{REF}$ po dobu $T_2$",
                                                       fontsize=10, color=INK2)


def fig17_single_prubeh():
    """Single slope: rampy se stejnou strmostí U_REF/RC, doba převodu roste s U_IN; čítané impulzy (vlastní čísla)."""
    k, tclk, mezera = 2.0, 0.05, 0.2                          # V/ms (U_REF = 2 V, RC = 1 ms), T_CLK = 50 µs
    fig, axs = plt.subplots(2, 1, figsize=(8.4, 5.0), sharex=True, gridspec_kw=dict(height_ratios=[2.3, 1]))
    t0 = 0.0
    for v in (1.0, 0.5, 1.5):
        T = v / k
        tt = np.linspace(0, T, 50)
        axs[0].plot(t0 + tt, k * tt, color=C1)
        axs[0].plot([t0 + T, t0 + T], [v, 0], color=C1, lw=1.2, ls=":")
        axs[0].hlines(v, t0, t0 + T, color=C2, ls="--", lw=1.4)
        axs[0].plot([t0 + T], [v], "o", color=C2, ms=6)
        axs[0].text(t0 + 0.02, v + 0.09, f"$U_\\mathrm{{IN}}$ = {cz(v, 1)} V", fontsize=9.5, color=C2)
        axs[0].annotate("", (t0, -0.18), (t0 + T, -0.18), arrowprops=dict(arrowstyle="<->", color=INK2, lw=1))
        axs[0].text(t0 + T / 2, -0.38, f"T = {cz(T, 2)} ms", ha="center", fontsize=9.5, color=INK2)
        N = int(round(T / tclk))
        for j in range(N):
            axs[1].add_patch(plt.Rectangle((t0 + j * tclk, 0), tclk / 2, 1, color=C3, lw=0))
        axs[1].text(t0 + T / 2, 1.2, f"{N} impulzů", ha="center", fontsize=9.5, color=INK2)
        t0 += T + mezera
    axs[0].text(0.06, 1.75, "strmost $U_\\mathrm{REF}/RC$ = 2 V/ms (stejná pro všechny)", fontsize=9.5, color=C1)
    axs[0].set_ylim(-0.55, 2.0)
    axs[0].set_ylabel("výstup integrátoru [V]")
    axs[0].set_title("pila integrátoru a měřené napětí", loc="left")
    axs[1].set_ylim(0, 1.55)
    axs[1].set_yticks([])
    axs[1].set_title("impulzy hodin, které projdou hradlem AND (čítač je počítá)", loc="left")
    axs[1].set_xlabel("čas t [ms]   ($T_\\mathrm{CLK}$ = 50 µs)")
    axs[1].set_xlim(-0.03, t0)
    save(fig, "fig17_single_prubeh")


def fig17_dual_prubeh():
    """Dual slope: T1 pevné, T2 = T1·U_IN/U_REF; vlevo různé U_IN, vpravo různé RC (vlastní čísla)."""
    uref, T1 = 2.0, 10.0                                          # V, ms
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.2), sharey=True)
    pripady = (((1.5, 10.0), (0.75, 10.0)), ((1.5, 10.0), (1.5, 20.0)))
    titulky = ("různé $U_\\mathrm{IN}$, stejné RC = 10 ms", "stejné $U_\\mathrm{IN}$ = 1,5 V, různé RC")
    for ax, pp, tit in zip(axs, pripady, titulky):
        ax.axhline(0, color=AXIS, lw=1)
        ax.axvline(T1, color=MUTED, lw=1, ls=":")
        for j, ((uin, rc), c, mk) in enumerate(zip(pp, CAT, MARK)):
            v1 = -T1 * uin / rc
            T2 = -v1 * rc / uref
            ax.plot([0, T1, T1 + T2], [0, v1, 0], color=c, marker=mk, ms=6, markevery=[1, 2])
            pop = f"$U_\\mathrm{{IN}}$ = {cz(uin, 2)} V" if pp[0][1] == pp[1][1] else f"RC = {cz(rc, 0)} ms"
            ax.text(12.6, -1.2 - 0.2 * j, f"{pop}: $T_2$ = {cz(T2, 2)} ms", fontsize=9, color=c)
            ax.text(T1 - 0.3, v1, f"$V_1$ = {cz(v1, 2).replace('-', '−')} V", fontsize=9, color=c, ha="right", va="center")
        ax.text(T1 / 2, 0.15, "$T_1$ = 10 ms (pevné)", ha="center", fontsize=9.5, color=INK2)
        ax.set_title(tit, loc="left")
        ax.set_xlabel("čas t [ms]")
        ax.set_xlim(0, 24)
    axs[0].set_ylabel("výstup integrátoru [V]")
    axs[0].set_ylim(-1.8, 0.5)
    save(fig, "fig17_dual_prubeh")


def _signal17(t):
    return 8.0 + 4.0 * np.sin(2 * np.pi * t / 70) + 1.0 * np.sin(2 * np.pi * t / 23)


def fig17_counter_tracking():
    """Counter type (každý převod od nuly) vs. tracking type (krok ±1 LSB za takt): 4 bity, krok 1 V (vlastní signál)."""
    nt = 90
    t = np.arange(nt + 1)
    tj = np.linspace(0, nt, 900)
    cnt, lat_t, lat_v, v = [], [], [], 0
    for i in t:
        cnt.append(v)
        if v > _signal17(i):                                      # U_DAC > U_IN → konec převodu, zápis do registru
            lat_t.append(i)
            lat_v.append(v)
            v = 0
        else:
            v = min(v + 1, 15)
    trk, v = [], 0
    for i in t:
        trk.append(v)
        v = int(np.clip(v + (1 if _signal17(i) > v else -1), 0, 15))
    fig, axs = plt.subplots(2, 1, figsize=(8.6, 6.0), sharex=True)
    for ax, y, tit in ((axs[0], cnt, "counter type: každý převod začíná od nuly"),
                       (axs[1], trk, "tracking type: v každém taktu krok o 1 LSB nahoru nebo dolů")):
        ax.plot(tj, _signal17(tj), color=C1, lw=1.8, label="vstupní napětí $U_\\mathrm{IN}$")
        ax.step(t, y, where="post", color=C2, lw=1.6, label="$U_\\mathrm{DAC}$ (kód čítače)")
        ax.set_title(tit, loc="left")
        ax.set_ylabel("napětí [V] (1 krok = 1 V)")
        ax.set_ylim(-0.5, 15.5)
    axs[0].plot(lat_t, lat_v, "^", color=C3, ms=7, label="zapsaný výsledek (konec převodu)")
    axs[0].legend(loc="upper center", ncol=3, fontsize=8.5, bbox_to_anchor=(0.5, 1.32))
    i0 = next(i for i in t if trk[i] > _signal17(i))
    axs[1].axvspan(0, i0, color=C2, alpha=0.1, lw=0)
    axs[1].text(i0 / 2, 13.5, "náběh první\ndigitalizace", ha="center", fontsize=9.5, color=INK2)
    axs[1].set_xlabel("čas [takty hodin $T_\\mathrm{CLK}$]")
    save(fig, "fig17_counter_tracking")


def fig17_sar_prubeh():
    """SAR, 4 bity, U_REF = 16 V (krok 1 V), U_IN = 6,4 V: zkoušené kódy 1000, 0100, 0110, 0111 → 0110 (podle stromu ze slidu)."""
    uin, kod, pokusy, intervaly = 6.4, 0, [], []
    lo, hi = 0, 16
    for b in (3, 2, 1, 0):
        zk = kod | (1 << b)
        vys = uin >= zk
        pokusy.append((zk, vys))
        if vys:
            kod, lo = zk, zk
        else:
            hi = zk
        intervaly.append((lo, hi))
    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    for i, ((zk, vys), (a, b)) in enumerate(zip(pokusy, intervaly), start=1):
        ax.add_patch(plt.Rectangle((i - 0.38, a), 0.76, b - a, color=C1, alpha=0.12, lw=0))
        c, mk = (C3, "^") if vys else (C2, "v")
        ax.plot([i - 0.38, i + 0.38], [zk, zk], color=c, lw=2.4)
        ax.plot([i], [zk], mk, color=c, ms=8)
        ax.text(i, zk - 0.6 if vys else zk + 0.6, f"zkouším {zk:04b} = {zk} V", fontsize=9, color=c, ha="center",
                va="top" if vys else "bottom")
        ax.text(i, -1.3, "$U_\\mathrm{IN} > U_\\mathrm{DAC}$\nbit = 1" if vys else "$U_\\mathrm{IN} < U_\\mathrm{DAC}$\nbit = 0",
                ha="center", fontsize=8.5, color=c)
    ax.axhline(uin, color=C1, lw=1.6, ls="--")
    ax.text(0.45, uin + 0.3, "$U_\\mathrm{IN}$ = 6,4 V", color=C1, fontsize=9.5)
    ax.plot([4.65, 5.45], [6, 6], color=INK, lw=2.4)
    ax.text(5.05, 5.4, "výsledek\n0110 = 6 V", fontsize=10, color=INK, va="top", ha="center", weight="semibold")
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["takt 1\n(MSB)", "takt 2", "takt 3", "takt 4\n(LSB)"])
    ax.set_xlim(0.4, 5.6)
    ax.set_ylim(-2.4, 16.5)
    ax.set_yticks(range(0, 17, 2))
    ax.set_ylabel("napětí [V]")
    ax.set_title("modrý pruh = interval, ve kterém $U_\\mathrm{IN}$ po porovnání určitě leží", loc="left", fontsize=10)
    save(fig, "fig17_sar_prubeh")


def fig17_cas_konverze():
    """Nejdelší čas konverze podle počtu bitů: (2^n − 1)·T_CLK vs. n·T_CLK, T_CLK = 100 ns (slidy „Příklady času konverze“)."""
    n = np.arange(4, 17)
    tclk = 0.1                                                    # µs
    fig, ax = plt.subplots(figsize=(7.6, 4.3))
    ax.semilogy(n, (2.0 ** n - 1) * tclk, "o-", color=C1, label="counter, tracking, single slope: $(2^n - 1)\\,T_\\mathrm{CLK}$")
    ax.semilogy(n, n * tclk, "s-", color=C2, label="postupná aproximace: $n\\,T_\\mathrm{CLK}$")
    for nb, txt1, txt2 in ((12, "409,5 µs", "1,2 µs"), (16, "6,55 ms", "1,6 µs")):
        ax.annotate(txt1, (nb, (2 ** nb - 1) * tclk), (nb - 1.6, (2 ** nb - 1) * tclk * 2.2), fontsize=9.5, color=C1,
                    arrowprops=dict(arrowstyle="->", color=C1))
        ax.annotate(txt2, (nb, nb * tclk), (nb - 1.3, nb * tclk * 0.3), fontsize=9.5, color=C2,
                    arrowprops=dict(arrowstyle="->", color=C2))
    ax.set_xlabel("počet bitů n")
    ax.set_ylabel("nejdelší čas konverze [µs]")
    ax.set_xticks(n)
    ax.set_ylim(0.1, 3e4)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: cz(v, 1) if v < 1 else f"{v:.0f}"))
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("$T_\\mathrm{CLK}$ = 100 ns ($f_\\mathrm{CLK}$ = 10 MHz)", loc="left")
    save(fig, "fig17_cas_konverze")


# =====================================================================  přednáška P8: multiplexace signálů
def _jfet_kanal(d, x, y, vst, ovl, zv):
    """Jeden vstup analogového MPX (slide „MPX analogových signálů“): R1, JFET k zemi, sledovač. Vrací OZ."""
    u = d.unit
    svorka(d, (x, y), vst)
    elm.Resistor().at((x, y)).right(u * 0.9).label("$R_1$")
    n = elm.Dot()
    op = elm.Opamp(leads=True, flip=True).right().anchor("in2").at((n.center[0] + u * 1.0, y)).label(zv, ofst=(-0.2, 0.0))
    elm.Line().at(n.center).to(op.in2)
    ln = elm.Line().at(n.center).down(u * 0.2)
    # JFET s kanálem N jako na slidu: šipka gate míří do kanálu (schemdraw ji tak kreslí u JFetP)
    j = elm.JFetP().at(ln.end).anchor("drain").left().flip()           # drain nahoře, gate vlevo
    elm.Line().at(j.source).down(u * 0.1)
    elm.Ground()
    elm.Line().at(j.gate).left(u * 0.35)
    elm.Dot(open=True).label(ovl, loc="left")
    elm.Line().at(op.in1).left(u * 0.2)
    elm.Line().down(u * 0.45)
    elm.Line().right().tox(op.out[0] + u * 0.15)
    elm.Line().up().toy(op.out[1])
    return op


def fig18_mpx_analog():
    """Analogový MPX ze slidu: vstupy přes R1, JFET X_i k zemi (výchozí stav sepnut), sledovače OZ1…OZn, součtový OZs."""
    with schema("fig18_mpx_analog", unit=2.4) as d:
        u = d.unit
        op1 = _jfet_kanal(d, 0, 0, "$u_{i1}$", "$X_1$", "OZ1")
        opn = _jfet_kanal(d, 0, -u * 2.2, "$u_{in}$", "$X_n$", "OZn")
        xb = op1.out[0] + u * 1.6
        for op, nm in ((op1, "$u_1$"), (opn, "$u_n$")):
            elm.Line().at(op.out).right(u * 0.15).dot().label(nm, loc="bottom", fontsize=11)
            elm.Resistor().right().tox(xb).label("$R_2$")
            elm.Dot()
        elm.Line().at((xb, op1.out[1])).down().toy(opn.out[1])
        ym = (op1.out[1] + opn.out[1]) / 2
        elm.Line().at((xb - u * 1.0, ym)).right().tox(xb).linestyle("--").label("$u_k$", loc="top", fontsize=11)
        ops = elm.Opamp(leads=True).right().anchor("in1").at((xb + u * 0.9, ym)).label("OZs", ofst=(-0.2, 0.0))
        elm.Line().at((xb, ym)).to(ops.in1)
        elm.Dot().at((xb, ym))
        elm.Line().at(ops.in2).left(u * 0.25)
        elm.Ground()
        elm.Line().at((xb, op1.out[1])).right(u * 0.35)
        elm.Resistor().right().tox(ops.out[0] + u * 0.2).label("$R_3$")
        elm.Line().down().toy(ops.out[1])
        elm.Line().left().tox(ops.out[0])
        elm.Line().at((ops.out[0] + u * 0.2, ops.out[1])).right(u * 0.3)
        elm.Dot(open=True).label("$u_o$", loc="right")


def fig18_spinac_sp():
    """Sériově-paralelní spínač na vstupu kanálu k (slide): a v sérii se signálem, b z + vstupu na zem, oba řídí X_k."""
    with schema("fig18_spinac_sp", unit=2.4) as d:
        u = d.unit
        for x0, a_sep, nadpis in ((0, False, "kanál nevybrán: a rozepnut, b sepnut"),
                                  (u * 5.8, True, "kanál vybrán: a sepnut, b rozepnut")):
            col = C3 if a_sep else C2
            svorka(d, (x0, 0), "$u_{ik}$")
            elm.Resistor().at((x0, 0)).right(u * 0.8).label("$R_1$")
            elm.Switch(nc=a_sep).right(u * 0.7).label("a", color=col).color(col)
            n = elm.Dot()
            op = elm.Opamp(leads=True, flip=True).right().anchor("in2").at((n.center[0] + u * 0.9, 0)).label("OZk", ofst=(-0.2, 0.0))
            elm.Line().at(n.center).to(op.in2)
            elm.Switch(nc=not a_sep).at(n.center).down(u * 0.7).label("b", loc="bottom", color=col).color(col)
            elm.Ground()
            elm.Line().at(op.in1).left(u * 0.2)
            elm.Line().down(u * 0.45)
            elm.Line().right().tox(op.out[0] + u * 0.15)
            elm.Line().up().toy(op.out[1])
            elm.Line().at(op.out).right(u * 0.25)
            elm.Dot(open=True).label("$u_k$", loc="right")
            elm.Label().at((x0 + u * 1.9, u * 0.95)).label(nadpis, fontsize=11, color=col)
            elm.Label().at((x0 + u * 0.6, -u * 0.55)).label("$X_k$ řídí a i b", fontsize=10, color=MUTED)


def fig18_cas_frekvence():
    """Rozdělení roviny čas × frekvence: TDM (svislé pruhy, celé pásmo) vs. FDM (vodorovné pásy, celý čas) – slidy TDM a FDM."""
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.9), sharey=True)
    ax = axs[0]
    for i in range(9):
        k = i % 3
        ax.add_patch(plt.Rectangle((i, 0), 0.92, 3, color=CAT[k], alpha=0.8, lw=0))
        ax.text(i + 0.46, 1.5, f"{k + 1}", ha="center", va="center", color="white", fontsize=11, weight="semibold")
    ax.set_xlim(0, 9)
    ax.set_title("TDM: každý kanál má své časové okno", loc="left")
    ax = axs[1]
    for k in range(3):
        ax.add_patch(plt.Rectangle((0, k + 0.06), 9, 0.84, color=CAT[k], alpha=0.8, lw=0))
        ax.text(4.5, k + 0.48, f"kanál {k + 1}", ha="center", va="center", color="white", fontsize=11, weight="semibold")
    ax.set_xlim(0, 9)
    ax.set_title("FDM: každý kanál má své frekvenční pásmo", loc="left")
    for ax in axs:
        ax.set_ylim(0, 3)
        ax.set_xlabel("čas")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
    axs[0].set_ylabel("frekvence")
    save(fig, "fig18_cas_frekvence")


def _sig18(t):
    """Tři pomalé analogové signály (vlastní)."""
    return [np.sin(2 * np.pi * 0.9 * t) + 0.3 * np.sin(2 * np.pi * 2.3 * t),
            0.8 * np.cos(2 * np.pi * 0.45 * t) - 0.2,
            0.6 * np.sin(2 * np.pi * 1.6 * t + 1.0) + 0.3]


def fig18_tdm_prubeh():
    """TDM tří analogových signálů: rámec 0,3 s, každý kanál okno 0,1 s; výstup MUX a co z něj vybere DEMUX pro kanál 1."""
    t = np.linspace(0, 3, 3001)
    s = _sig18(t)
    okno = 0.1
    k = (np.floor(t / okno + 1e-9).astype(int)) % 3
    fig, axs = plt.subplots(3, 1, figsize=(8.6, 6.6), sharex=True)
    ax = axs[0]
    for i in range(3):
        ax.plot(t, s[i], color=CAT[i], lw=1.8, label=f"kanál {i + 1}")
    ax.legend(loc="upper right", ncol=3, fontsize=9)
    ax.set_ylabel("vstupy [V]")
    ax.set_title("tři analogové signály na vstupech MUX", loc="left")
    ax = axs[1]
    ax.plot(t, np.choose(k, s), color=MUTED, lw=0.6, zorder=0)
    for i in range(3):
        ax.plot(t, np.where(k == i, s[i], np.nan), color=CAT[i], lw=2.2)
    ax.set_ylabel("společný kanál [V]")
    ax.set_title("výstup MUX: kanály se střídají po 0,1 s (rámec 0,3 s)", loc="left")
    ax = axs[2]
    ax.plot(t, s[0], color=C1, lw=1, alpha=0.35, label="původní kanál 1")
    ax.plot(t, np.where(k == 0, s[0], np.nan), color=C1, lw=2.4, label="co DEMUX pustí na výstup 1")
    ax.legend(loc="upper right", fontsize=9, ncol=2)
    ax.set_ylabel("výstup 1 [V]")
    ax.set_xlabel("čas [s]")
    ax.set_title("DEMUX: kanál 1 jen ve svých oknech – spojitý signál je „rozsekaný“", loc="left")
    for ax in axs:
        ax.set_ylim(-1.6, 1.9)
    save(fig, "fig18_tdm_prubeh")


F18_NOSNE = [10.0, 13.3, 16.6]                                  # posun pásma (kHz): 10,3–13,4 / 13,6–16,7 / 16,9–20,0


def fig18_fdm_spektrum():
    """FDM podle slidu: tři hovorové signály 300–3400 Hz posunuté do pásma 10–20 kHz s ochrannými pásmy (posuny vlastní)."""
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.6), gridspec_kw=dict(width_ratios=[1, 2.3]))
    ax = axs[0]
    for i in range(3):
        ax.add_patch(plt.Rectangle((0.3, 2 - i + 0.1), 3.1, 0.75, color=CAT[i], alpha=0.85, lw=0))
        ax.text(3.6, 2 - i + 0.47, f"signál {i + 1}", va="center", fontsize=9.5, color=INK2)
    ax.set_xlim(0, 6.5)
    ax.set_ylim(0, 3)
    ax.set_xticks([0.3, 3.4])
    ax.set_xticklabels(["0,3", "3,4"])
    ax.set_title("vstupy: každý 300–3400 Hz", loc="left")
    ax = axs[1]
    for i, fn in enumerate(F18_NOSNE):
        ax.add_patch(plt.Rectangle((fn + 0.3, 0), 3.1, 1, color=CAT[i], alpha=0.85, lw=0))
        ax.text(fn + 1.85, 0.5, f"{i + 1}", ha="center", va="center", color="white", fontsize=12, weight="semibold")
    for g in (F18_NOSNE[1] + 0.15, F18_NOSNE[2] + 0.15):
        ax.annotate("ochranné\npásmo", (g, 1.0), (g, 1.45), ha="center", fontsize=9, color=INK2,
                    arrowprops=dict(arrowstyle="->", color=INK2))
    ax.set_xlim(0, 21)
    ax.set_ylim(0, 1.9)
    ax.set_xticks([0, 10, 20])
    ax.set_title("společný kanál: pásma vedle sebe v 10–20 kHz", loc="left")
    for ax in axs:
        ax.set_yticks([])
        ax.grid(False)
        ax.set_xlabel("frekvence [kHz]")
    save(fig, "fig18_fdm_spektrum")


def fig18_chyba_r1():
    """Chyba „nulového“ napětí u_o(0)/u_i ≅ R_X/R1 pro R_X = 100 Ω (slide): 10 kΩ → 1 %, 1 MΩ → 0,1 ‰."""
    r1 = np.logspace(3, 7, 200)
    rx = 100.0
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    ax.loglog(r1, rx / r1 * 100, color=C1, label="přibližně $R_{X_1}/R_1$ (slide)")
    ax.loglog(r1, rx / (r1 + rx) * 100, "--", color=C2, lw=1.4, label="přesně (dělič) $R_{X_1}/(R_1 + R_{X_1})$")
    for r, txt, off in ((1e4, "10 kΩ → 1 %", (1.8e4, 2.5)), (1e6, "1 MΩ → 0,01 % = 0,1 ‰", (1.5e6, 0.04))):
        ax.plot(r, rx / r * 100, "o", color=C1, ms=7)
        ax.annotate(txt, (r, rx / r * 100), off, fontsize=9.5, color=INK2, arrowprops=dict(arrowstyle="->", color=INK2))
    ax.set_xlabel("$R_1$ [Ω]")
    ax.set_ylabel("chyba [% $u_i$]")
    ax.set_title("$R_{X_1}$ = 100 Ω (sepnutý tranzistor nevybraného kanálu)", loc="left")
    ax.legend(loc="lower left", fontsize=9)
    save(fig, "fig18_chyba_r1")


# =====================================================================  přednáška P9: galvanické oddělení
def fig19_trafo():
    """Transformátorová vazba: zdroj a zátěž bez vodivého spojení, každá strana má vlastní zem (GND1 ≠ GND2)."""
    with schema("fig19_trafo", unit=2.4) as d:
        u = d.unit
        t = elm.Transformer(t1=5, t2=5, core=True)
        elm.Line().at(t.p1).left(u * 0.8)
        elm.SourceSin().down().toy(t.p2).label("$u_1$ (AC)", loc="bottom")
        elm.Line().tox(t.p2)
        elm.Ground().at(((t.p1[0] - u * 0.4), t.p2[1]))
        elm.Line().at(t.s1).right(u * 0.8)
        elm.Resistor().down().toy(t.s2).label("$R_Z$", loc="bottom")
        elm.Line().tox(t.s2)
        elm.GroundSignal().at(((t.s1[0] + u * 0.4), t.s2[1]))
        xm = (t.p1[0] + t.s1[0]) / 2
        elm.Line().at((xm, t.p1[1] + 0.9)).down(t.p1[1] - t.p2[1] + 2.4).linestyle("--").color(C2)
        elm.Label().at((xm, t.p1[1] + 1.55)).label("izolační bariéra\n(přenos magnetickým polem)", fontsize=11, color=C2)
        elm.Label().at((t.p1[0] - u * 0.4, t.p2[1] - 1.25)).label("GND1", fontsize=11, color=MUTED)
        elm.Label().at((t.s1[0] + u * 0.4, t.s2[1] - 1.25)).label("GND2", fontsize=11, color=MUTED)


def fig19_trafo_frekvence():
    """Ilustrační frekvenční závislost převodu transformátoru: DC neprojde, pracovní pásmo mezi f_d a f_h."""
    f = np.logspace(-0.5, 5.6, 600)
    fd, fh = 40.0, 20e3
    h = (1j * f / fd) / (1 + 1j * f / fd) / (1 + 1j * f / fh) ** 2
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    ax.axvspan(fd, fh * 0.64, color=C3, alpha=0.12, lw=0)
    ax.plot(f, db(h), color=C1)
    ax.axhline(-3, color=MUTED, lw=0.8, ls=":")
    ax.text(np.sqrt(fd * fh * 0.64), -8, "pracovní pásmo\n(převod přibližně stálý)", ha="center", va="top", fontsize=10, color=INK2)
    ax.annotate("k f → 0 (DC) převod klesá k nule:\nkonstantní proud neindukuje napětí", (1, db(h[np.argmin(abs(f - 1))])),
                (2.2, -42), fontsize=9.5, color=INK2, arrowprops=dict(arrowstyle="->", color=INK2))
    ax.annotate("vysoké frekvence: rozptyl\na kapacity vinutí", (2e5, db(h[np.argmin(abs(f - 2e5))])),
                (1.2e4, -44), fontsize=9.5, color=INK2, arrowprops=dict(arrowstyle="->", color=INK2))
    log_osa(ax)
    ax.set_ylim(-50, 5)
    ax.set_ylabel("převod [dB]")
    ax.set_title("transformátor přenáší jen v určitém pásmu frekvencí (ilustrační model)", loc="left")
    save(fig, "fig19_trafo_frekvence")


def fig19_kapacitni_prubeh():
    """Kapacitní vazba v DC/DC (podle slidu: driver ST1/ST2, f_OSC 100 kHz): protifázové obdélníky, za kondenzátory
    zbude jen střídavá složka, diodový můstek ji usměrní (ideální diody)."""
    t = np.linspace(0, 30, 3001)                                         # µs, perioda 10 µs = 100 kHz
    st1 = np.where((t % 10) < 5, 5.0, 0.0)
    st2 = 5.0 - st1
    rozdil = st1 - st2
    fig, axs = plt.subplots(2, 1, figsize=(8.4, 5.2), sharex=True)
    ax = axs[0]
    ax.plot(t, st1, color=C1, label="ST1")
    ax.plot(t, st2, "--", color=C2, label="ST2")
    ax.axhline(2.5, color=MUTED, lw=0.8, ls=":")
    ax.text(0.3, 2.75, "střední hodnota 2,5 V", fontsize=9, color=MUTED)
    ax.set_ylim(-0.8, 6.2)
    ax.set_ylabel("napětí [V]")
    ax.set_title("výstupy driveru: dva obdélníky 0–5 V v protifázi", loc="left")
    ax.legend(loc="upper right", ncol=2, fontsize=9)
    ax = axs[1]
    ax.plot(t, rozdil, color=C1, label="za kondenzátory (vstup můstku)")
    ax.plot(t, np.abs(rozdil) + 0.25, "--", color=C3, lw=2.4, label="po usměrnění můstkem (kresleno o 0,25 V výš)")
    ax.axhline(0, color=AXIS, lw=0.8)
    ax.set_ylim(-6.5, 7.5)
    ax.set_ylabel("napětí [V]")
    ax.set_xlabel("čas [µs]")
    ax.set_title("bariérou projde jen střídavá složka ±5 V, můstek z ní udělá opět stejnosměrné napětí", loc="left")
    ax.legend(loc="upper right", ncol=2, fontsize=9)
    save(fig, "fig19_kapacitni_prubeh")


def _opto(x):
    """Ilustrační nelineární převod optické vazby (normováno 0–1)."""
    return np.tanh(1.8 * x) / np.tanh(1.8)


def fig19_opto_nelinearita():
    """Nelinearita přímé optické vazby: analogový signál se zkreslí, digitální (0/1) projde."""
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.9), gridspec_kw=dict(width_ratios=[1, 1.6]))
    ax = axs[0]
    x = np.linspace(0, 1, 200)
    ax.plot(x, x, ":", color=MUTED, lw=1.2, label="lineární (ideál)")
    ax.plot(x, _opto(x), color=C1, label="skutečná vazba")
    ax.set_xlabel("proud LED $I_F$ (normovaný)")
    ax.set_ylabel("proud fotodetektoru (normovaný)")
    ax.set_title("a) převodní charakteristika", loc="left")
    ax.legend(loc="lower right", fontsize=9)
    ax = axs[1]
    t = np.linspace(0, 2, 800)
    sin_in = 0.5 + 0.45 * np.sin(2 * np.pi * t)
    dig_in = np.where((t % 1) < 0.5, 0.95, 0.05)
    ax.plot(t, sin_in, ":", color=C1, lw=1.3, label="analogový vstup")
    ax.plot(t, _opto(sin_in), color=C1, label="analogový výstup – zkreslený")
    ax.plot(t, dig_in - 1.25, ":", color=C2, lw=1.3, label="digitální vstup")
    ax.plot(t, _opto(dig_in) - 1.25, color=C2, label="digitální výstup – 0/1 poznám")
    ax.set_yticks([])
    ax.set_xlabel("čas (perioda = 1)")
    ax.set_title("b) co projde přímou optickou vazbou", loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=9)
    save(fig, "fig19_opto_nelinearita")


def fig19_lin_zesilovac():
    """Izolační zesilovač s linearizovanou vazbou (podle slidu, HCNR200): A1 + PD1 + LED vysílací část, PD2 + A2 přijímací."""
    with schema("fig19_lin_zesilovac", unit=2.2) as d:
        u = d.unit
        svorka(d, (0, 0), "$U_{IN}$")
        elm.Resistor().at((0, 0)).right(u * 0.9).label("$R_1$")
        n1 = elm.Dot()
        elm.Photodiode().at(n1.center).down(u * 0.8).reverse().label("PD1", loc="bottom")
        elm.Ground()
        a1 = elm.Opamp(leads=True, flip=True).right().anchor("in2").at((n1.center[0] + u * 0.7, 0)).label("A1", ofst=(-0.2, 0))
        elm.Line().at(n1.center).to(a1.in2)
        elm.Line().at(a1.in1).left(u * 0.15)
        elm.Line().down(u * 0.45)
        elm.Ground()
        elm.Line().at(a1.out).right(u * 0.35)
        led = elm.LED().down(u * 0.8).label("LED", loc="bottom")
        elm.Ground()
        x2 = a1.out[0] + u * 2.0
        n2 = elm.Dot().at((x2, 0))
        elm.Photodiode().at(n2.center).down(u * 0.8).reverse().label("PD2", loc="top")
        elm.GroundSignal()
        a2 = elm.Opamp(leads=True).right().anchor("in1").at((x2 + u * 0.7, 0)).label("A2", ofst=(-0.2, 0))
        elm.Line().at(n2.center).to(a2.in1)
        elm.Line().at(a2.in2).left(u * 0.15)
        elm.Line().down(u * 0.45)
        elm.GroundSignal()
        elm.Line().at(n2.center).up(u * 0.6)
        elm.Resistor().right().tox(a2.out[0] + u * 0.2).label("$R_2$")
        elm.Line().down().toy(a2.out[1])
        elm.Line().left().tox(a2.out[0])
        elm.Line().at((a2.out[0] + u * 0.2, a2.out[1])).right(u * 0.3)
        elm.Dot(open=True).label("$U_{OUT}$", loc="right")
        xb = (led.center[0] + x2) / 2 - u * 0.15
        elm.Line().at((xb, u * 1.2)).down(u * 2.6).linestyle("--").color(C2)
        elm.Label().at((xb, u * 1.4)).label("izolační bariéra", fontsize=11, color=C2)
        elm.Label().at((a1.center[0] - u * 0.5, u * 1.05)).label("vysílací část (GND1)", fontsize=11, color=C1)
        elm.Label().at((a2.center[0] - u * 0.3, u * 1.05)).label("přijímací část (GND2)", fontsize=11, color=C3)
        elm.Label().at((n1.center[0] - u * 0.55, -u * 1.25)).label("$I_{PD1} = K_1 I_F$", fontsize=11, color=C1)
        elm.Label().at((x2 - u * 0.15, -u * 1.25)).label("$I_{PD2} = K_2 I_F$", fontsize=11, color=C3)
        elm.Label().at((led.center[0] - u * 0.4, led.center[1] + u * 0.05)).label("$I_F$", fontsize=11, color=INK2)


def fig19_linearizace():
    """Linearizovaná vazba: A1 si sám najde (nelineární) proud LED, výstup je přímka (ilustrační, K2/K1 = 1, R2 = R1)."""
    u = np.linspace(0, 1, 200)
    i_f = np.arctanh(u * np.tanh(1.8)) / 1.8                             # inverze _opto: proud LED, aby I_PD1 ~ U_IN
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.8))
    ax = axs[0]
    ax.plot(u, u, ":", color=MUTED, lw=1.2, label="kdyby byla LED lineární")
    ax.plot(u, i_f, color=C2, label="proud LED, který nastaví A1")
    ax.set_xlabel("$U_{IN}$ (normované)")
    ax.set_ylabel("$I_F$ (normovaný)")
    ax.set_title("a) A1 „předkřiví“ proud LED", loc="left")
    ax.legend(loc="upper left", fontsize=9)
    ax = axs[1]
    ax.plot(u, _opto(u), "--", color=C2, label="přímá vazba ($I_F \\sim U_{IN}$)")
    ax.plot(u, u, color=C1, lw=2.4, label="linearizovaná vazba")
    ax.set_xlabel("$U_{IN}$ (normované)")
    ax.set_ylabel("$U_{OUT}$ (normované)")
    ax.set_title("b) výstup: přímka díky PD1 ve zpětné vazbě", loc="left")
    ax.legend(loc="lower right", fontsize=9)
    save(fig, "fig19_linearizace")


def fig19_pwm():
    """PWM bipolárního signálu (vlastní čísla): rozsah ±10 V, U_in = 0 → střída 50 %, U_MAX = 5 V; demodulace střední hodnotou."""
    T = 1.0
    t = np.linspace(0, 16, 16001)
    sig = lambda x: 7 * np.sin(2 * np.pi * x / 16) + 2.5 * np.sin(2 * np.pi * x / 5.3)
    k = np.floor(t / T)
    dc = 0.5 + sig(k * T) / 20
    pwm = np.where((t - k * T) < dc * T, 5.0, 0.0)
    stred = np.convolve(pwm, np.ones(1000) / 1000, mode="same")
    fig, axs = plt.subplots(3, 1, figsize=(8.6, 6.6), sharex=True)
    ax = axs[0]
    ax.plot(t, sig(t), color=C1)
    ax.plot(np.arange(16) * T, sig(np.arange(16) * T), "o", color=C1, ms=5, mfc=SURF)
    ax.axhline(0, color=AXIS, lw=0.8)
    ax.set_ylabel("$U_{in}$ [V]")
    ax.set_title("vstupní signál (vzorkuje se na začátku každé periody)", loc="left")
    ax = axs[1]
    ax.plot(t, pwm, color=C2, lw=1.4)
    ax.set_ylim(-0.6, 6.4)
    ax.set_ylabel("PWM [V]")
    ax.set_title("PWM: kladné napětí → střída nad 50 %, záporné → pod 50 %", loc="left")
    ax = axs[2]
    m = (t > 0.6) & (t < 15.4)
    ax.plot(t, sig(t), ":", color=C1, lw=1.3, label="původní $U_{in}$")
    ax.plot(t[m], (stred[m] - 2.5) * 4, color=C3, lw=2.2, label="z PWM: $(\\bar u - 2{,}5\\ \\mathrm{V})\\cdot 4$")
    ax.axhline(0, color=AXIS, lw=0.8)
    ax.set_ylabel("$U_{out}$ [V]")
    ax.set_xlabel("čas [periody PWM]")
    ax.set_title("demodulace: střední hodnota za periodu vrátí signál", loc="left")
    ax.legend(loc="lower left", fontsize=9, ncol=2)
    save(fig, "fig19_pwm")


def fig19_pwm_menic():
    """Obecný princip přenosu napětí pomocí PWM (slide): spínač řízený PWM, dioda, cívka (akumulace/filtr), zátěž."""
    with schema("fig19_pwm_menic", unit=2.4) as d:
        u = d.unit
        svorka(d, (0, 0), "$U_S$")
        elm.Line().at((0, 0)).right(u * 0.4)
        sw = elm.Switch().right(u * 0.8).label("spínač", loc="bottom")
        n = elm.Dot()
        elm.Inductor2(loops=3).right(u * 1.2).label("$L$")
        elm.Line().right(u * 0.5)
        r = elm.Resistor().down(u * 1.2).label("$R$ (zátěž)")
        elm.Line().left().tox(n.center[0])
        g = elm.Dot()
        elm.Ground()
        elm.Diode().at(n.center).down().toy(g.center).reverse().label("$D$", loc="top")
        xs = sw.center[0]
        elm.Line().at((xs, 0.3)).up(u * 0.5).linestyle("--")
        elm.Label().at((xs, 0.3 + u * 0.5 + 0.35)).label("řízení PWM", fontsize=12)
        elm.Label().at((r.center[0] + u * 0.45, r.center[1])).label("$U_O$", fontsize=13)


def fig19_pwm_zvlneni():
    """Výstup PWM měniče (RL podle slidu): velikost dává střída, zvlnění perioda vůči τ = L/R (U_S = 12 V)."""
    us, tau = 12.0, 1.0

    def sim(D, T, tmax):
        t = np.linspace(0, tmax, 40001)
        dt = t[1] - t[0]
        v = np.where((t % T) < D * T, us, 0.0)
        out = np.zeros_like(t)
        for i in range(1, len(t)):
            out[i] = out[i - 1] + dt / tau * (v[i - 1] - out[i - 1])
        return t, v, out

    fig, axs = plt.subplots(1, 2, figsize=(9.8, 3.9), sharey=True)
    ax = axs[0]
    for (T, c, ls, lab) in ((2.0, C2, "--", "T = 2τ: velké zvlnění"), (0.2, C1, "-", "T = 0,2τ: malé zvlnění")):
        t, v, o = sim(0.5, T, 8)
        ax.plot(t, o, ls, color=c, label=lab)
    ax.axhline(6, color=MUTED, lw=0.8, ls=":")
    ax.set_title("a) střída 50 %, dvě periody PWM", loc="left")
    ax.set_xlabel("čas [τ = L/R]")
    ax.set_ylabel("$U_O$ [V]")
    ax.legend(loc="lower right", fontsize=9)
    ax = axs[1]
    for D, c, mk in ((0.25, C1, "o"), (0.5, C2, "s"), (0.75, C3, "^")):
        t, v, o = sim(D, 0.2, 8)
        ax.plot(t, o, color=c, label=f"střída {int(D * 100)} % → {cz(D * us, 0)} V")
        ax.plot(t[-1], o[-1], mk, color=c, ms=6)
    ax.set_title("b) T = 0,2τ, tři různé střídy", loc="left")
    ax.set_xlabel("čas [τ = L/R]")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_ylim(0, 12.5)
    save(fig, "fig19_pwm_zvlneni")


ALL = [fig01_ohm, fig01_kirchhoff, fig01_delic, fig01_zatizeni,
       fig02_xc, fig02_dp_hp, fig02_bode_dp, fig02_bode_hp, fig02_postup, fig02_typy, fig02_pp_schema,
       fig02_bode_pp, fig02_pz_schema, fig02_bode_pz,
       fig03_oz_symbol, fig03_oz_char, fig03_inv, fig03_neinv, fig03_dif, fig03_pristrojovy, fig03_cmrr,
       fig04_sledovac, fig04_sledovac_delic, fig04_integrator, fig04_derivator, fig04_prubehy,
       fig11_signaly, fig11_zdroj, fig11_iu, fig11_shunt, fig11_trafo, fig11_fu_schema, fig11_fu_prubeh, fig11_rx,
       fig11_mustek,
       fig12_beta, fig12_se, fig12_se_zv, fig12_se_delic, fig12_stabilita, fig12_sc, fig12_darlington,
       fig12_rozdilovy, fig12_rozdilovy_prubeh, fig12_selektivni, fig12_mosfet_char, fig12_mosfet_ss,
       fig12_mosfet_sd, fig12_spinace, fig12_slew, fig12_zisk_f, fig12_komparator,
       fig13_teplota, fig13_dlouhodoba, fig13_zener_va, fig13_zd_stab, fig13_zd_alt, fig13_posileni, fig13_omezeni,
       fig13_omezeni_va, fig13_vlecny, fig13_proudovy,
       fig14_nulovani, fig14_neinv_int, fig14_dif_int, fig14_der_osetreny, fig14_jednocestny, fig14_usm_a,
       fig14_usm_b, fig14_dvoucestny, fig14_vrcholovy, fig14_int_prubeh, fig14_nulovani_prubeh, fig14_der_bode,
       fig14_der_trojuhelnik, fig14_usm_prubeh, fig14_dioda_va, fig14_usm_va, fig14_vrchol_prubeh,
       fig15_dp1_neinv, fig15_dp1_inv, fig15_hp1_neinv, fig15_hp1_inv, fig15_sk_dp, fig15_sk_hp, fig15_mfb_dp,
       fig15_mfb_hp, fig15_mfb_pp, fig15_twint, fig15_wien, fig15_kaskada_schema, fig15_idealni_realny,
       fig15_strmost, fig15_sk_q, fig15_pp_mfb, fig15_pz_q, fig15_kaskada, fig15_butterworth, fig15_aproximace,
       fig16_omezovac, fig16_oboustranny, fig16_zener_omezovac, fig16_zd_mustek, fig16_komp_omezeni, fig16_schmitt, fig16_schmitt_zd, fig16_selektor, fig16_flash, fig16_omezovac_char, fig16_oboustranny_char, fig16_zener_char, fig16_komparator_char, fig16_rusivy, fig16_komp_omezeni_prubeh, fig16_schmitt_char, fig16_selektor_prubeh, fig16_kvantovani, fig16_adc_char,
       fig17_dac_vahovy, fig17_dac_r2r, fig17_single_slope, fig17_dual_slope, fig17_single_prubeh, fig17_dual_prubeh,
       fig17_counter_tracking, fig17_sar_prubeh, fig17_cas_konverze,
       fig18_mpx_analog, fig18_spinac_sp, fig18_cas_frekvence, fig18_tdm_prubeh, fig18_fdm_spektrum, fig18_chyba_r1,
       fig19_trafo, fig19_trafo_frekvence, fig19_kapacitni_prubeh, fig19_opto_nelinearita, fig19_lin_zesilovac,
       fig19_linearizace, fig19_pwm, fig19_pwm_menic, fig19_pwm_zvlneni]

if __name__ == "__main__":
    vyber = sys.argv[1:]
    for f in ALL:
        if not vyber or any(v in f.__name__ for v in vyber):
            f()
