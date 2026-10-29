"""Generuje fragment _build/obsah/13_tabulky.html se statistickými tabulkami (Φ(u), kvantily u, t, χ², F).

Spuštění (z kořene repozitáře pripravy):  uv run python pso/_build/make_tables.py
Fragment je generovaný – needituj ho ručně, uprav tento skript. Hodnoty počítá scipy.
"""
from pathlib import Path

from scipy import stats

OUT = Path(__file__).resolve().parent / "obsah" / "13_tabulky.html"


def c(v, nd):
    return f"{v:.{nd}f}".replace(".", ",").replace("-", "−")


def sub(p):
    """Index kvantilu pro KaTeX: 0,975 → 0{,}975 (čárka bez mezery)."""
    return c(p, 3).rstrip("0").replace(",", "{,}")


def table(head, rows, cls="compact"):
    h = "<tr>" + "".join(f"<th>{x}</th>" for x in head) + "</tr>"
    body = "\n".join("<tr>" + "".join(f"<td>{x}</td>" if i else f"<th>{x}</th>" for i, x in enumerate(r)) + "</tr>"
                     for r in rows)
    return f'<div class="tablewrap"><table class="{cls}">\n{h}\n{body}\n</table></div>'


def phi_table():
    head = ["u"] + [f"0,0{k}" for k in range(10)]
    rows = []
    for i in range(0, 35):
        base = i / 10
        rows.append([c(base, 1)] + [c(stats.norm.cdf(base + k / 100), 4) for k in range(10)])
    return table(head, rows)


def quantile_u():
    ps = [0.8, 0.85, 0.875, 0.9, 0.95, 0.975, 0.98, 0.99, 0.995, 0.999]
    return table(["p"] + [c(p, 3).rstrip("0").rstrip(",") for p in ps],
                 [["\\(u_p\\)"] + [c(stats.norm.ppf(p), 3) for p in ps]])


def t_table():
    ps = [0.9, 0.95, 0.975, 0.99, 0.995]
    head = ["ν"] + [f"\\(t_{{{sub(p)}}}\\)" for p in ps]
    nus = list(range(1, 31)) + [40, 60, 120]
    rows = [[str(n)] + [c(stats.t.ppf(p, n), 3) for p in ps] for n in nus]
    rows.append(["∞"] + [c(stats.norm.ppf(p), 3) for p in ps])
    return table(head, rows)


def chi2_table():
    ps = [0.01, 0.025, 0.05, 0.95, 0.975, 0.99]
    head = ["ν"] + [f"\\(\\chi^2_{{{sub(p)}}}\\)" for p in ps]
    nus = list(range(1, 31)) + [40, 50, 60]
    rows = [[str(n)] + [c(stats.chi2.ppf(p, n), 3) for p in ps] for n in nus]
    return table(head, rows)


def f_table(p):
    n1s = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 20]
    n2s = list(range(1, 21)) + [22, 24, 26, 28, 30, 40, 60, 120]
    head = ["ν₂ \\ ν₁"] + [str(n) for n in n1s]
    rows = [[str(n2)] + [c(stats.f.ppf(p, n1, n2), 2) for n1 in n1s] for n2 in n2s]
    return table(head, rows)


def main():
    parts = [
        "<!-- GENEROVANÝ SOUBOR: needituj ručně, uprav _build/make_tables.py a spusť ho znovu. -->",
        "<h1>Statistické tabulky</h1>",
        '<p class="lead">Hodnoty potřebné k úlohám: Laplaceova funkce Φ(u), kvantily normovaného normálního '
        "rozdělení, Studentova t-rozdělení, rozdělení χ² a F. Spočítáno přesně (scipy); oproti tištěným tabulkám se "
        "může lišit poslední číslice zaokrouhlením.</p>",
        '<h2 id="phi">Laplaceova funkce Φ(u)</h2>',
        "<p>\\(\\Phi(u) = p(U &lt; u)\\) pro U ~ No(0, 1). Řádek = u na desetiny, sloupec = setiny. "
        "Pro záporné u použij \\(\\Phi(-u) = 1 - \\Phi(u)\\). Příklad: \\(\\Phi(1{,}67)\\) je v řádku 1,6 a sloupci "
        "0,07.</p>",
        phi_table(),
        '<h2 id="kvantily-u">Kvantily normovaného normálního rozdělení</h2>',
        "<p>\\(u_p\\) je číslo, pro které \\(\\Phi(u_p) = p\\). Pro malá p: \\(u_p = -u_{1-p}\\).</p>",
        quantile_u(),
        '<h2 id="t">Kvantily Studentova t-rozdělení</h2>',
        "<p>\\(t_p(\\nu)\\): plocha vlevo je p. Oboustranný test nebo interval s α = 0,05 → sloupec "
        "\\(t_{0{,}975}\\); jednostranný s α = 0,05 → \\(t_{0{,}95}\\). Poslední řádek (∞) jsou kvantily No(0, 1).</p>",
        t_table(),
        '<h2 id="chi2">Kvantily rozdělení χ²</h2>',
        "<p>\\(\\chi^2_p(\\nu)\\): plocha vlevo je p. Interval pro σ² se spolehlivostí 0,95 → sloupce "
        "\\(\\chi^2_{0{,}025}\\) a \\(\\chi^2_{0{,}975}\\).</p>",
        chi2_table(),
        '<h2 id="f975">Kvantily F-rozdělení (p = 0,975)</h2>',
        "<p>\\(F_{0{,}975}(\\nu_1, \\nu_2)\\) pro oboustranný F-test shody rozptylů s α = 0,05 (větší rozptyl v čitateli). ν₁ = stupně volnosti "
        "čitatele (sloupec), ν₂ = jmenovatele (řádek).</p>",
        f_table(0.975),
        '<h2 id="f95">Kvantily F-rozdělení (p = 0,95)</h2>',
        "<p>\\(F_{0{,}95}(\\nu_1, \\nu_2)\\) pro jednostranný test s α = 0,05 (např. analýza rozptylu).</p>",
        f_table(0.95),
    ]
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print("ok", OUT.name)


if __name__ == "__main__":
    main()
