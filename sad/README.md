# SAD – Měření a zpracování biosignálů (příprava na půlsemestrální test)

Web: https://balnerm.github.io/pripravy/sad/

Kapitoly: 1 Ohmův zákon, Kirchhoffovy zákony, dělič napětí · 2 RC filtry (DP, HP, PP, PZ, Bodeho graf) ·
3 operační zesilovače a CMRR · 4 sledovač, integrátor, derivátor · ★ tahák · slovník.
Obsah vychází ze standardní elektrotechniky (podklady z přednášek nebyly k dispozici).

## Úpravy
Z kořene repozitáře:
```
uv run python sad/_build/make_figures.py      # schémata (schemdraw) a grafy do sad/figures/
python sad/_build/build.py                    # stránky z sad/_build/obsah/
python sad/_build/make_pdf.py                 # volitelně, PDF jinak vytvoří GitHub Actions
```
`make_figures.py` přijme i část názvu obrázku (`… make_figures.py bode pristrojovy`) a vygeneruje jen ty.

## Obsah složky
- `_build/build.py` – sestavení stránek, slovník z rámečků definic, `skripta_vse.html`, kontroly
- `_build/make_figures.py` – schémata zapojení (schemdraw) a přenosové charakteristiky / průběhy (matplotlib)
- `_build/make_pdf.py` – PDF každé stránky a celých skript (headless Chrome)
- `_build/obsah/` – zdrojové texty stránek
- `assets/` – styl a skript (téma, navigace, vzorce KaTeX, tisk)
