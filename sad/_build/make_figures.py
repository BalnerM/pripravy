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


ALL = [fig01_ohm, fig01_kirchhoff, fig01_delic, fig01_zatizeni,
       fig02_xc, fig02_dp_hp, fig02_bode_dp, fig02_bode_hp, fig02_postup, fig02_typy, fig02_pp_schema,
       fig02_bode_pp, fig02_pz_schema, fig02_bode_pz,
       fig03_oz_symbol, fig03_oz_char, fig03_inv, fig03_neinv, fig03_dif, fig03_pristrojovy, fig03_cmrr,
       fig04_sledovac, fig04_sledovac_delic, fig04_integrator, fig04_derivator, fig04_prubehy,
       fig11_signaly, fig11_zdroj, fig11_iu, fig11_shunt, fig11_trafo, fig11_fu_schema, fig11_fu_prubeh, fig11_rx,
       fig11_mustek]

if __name__ == "__main__":
    vyber = sys.argv[1:]
    for f in ALL:
        if not vyber or any(v in f.__name__ for v in vyber):
            f()
