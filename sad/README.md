# SAD – Měření a zpracování biosignálů

Dvoje samostatná skripta:

- **Půlsemestrální test** – https://balnerm.github.io/pripravy/sad/ – jen základy: 1 Ohmův zákon, Kirchhoffovy
  zákony, dělič napětí · 2 RC filtry (DP, HP, PP, PZ, Bodeho graf) · 3 operační zesilovače a CMRR · 4 sledovač,
  integrátor, derivátor · ★ tahák · slovník. Fragmenty v `_build/obsah/`, obsah vychází ze standardní elektrotechniky.
- **Závěrečná zkouška** – https://balnerm.github.io/pripravy/sad/zkouska/ – přednášky P1–P7 (další přibývají),
  ★ tahák, slovník. Fragmenty v `_build/obsah_zkouska/`. Látka základů je vložená do přednášek jako
  „Připomenutí ze základů“ (`<div class="zaklad">`) v místě, kde je poprvé potřeba, aby se skripta dala číst
  jako celek; definice ze základů mají stejná id jako v testu (`def-delic`, `def-invertujici` …).
  Nastavení verze je `EDITIONS` v `_build/build.py`.

## Úpravy
Z kořene repozitáře:
```
uv run python sad/_build/make_figures.py      # schémata (schemdraw) a grafy do sad/figures/
python sad/_build/build.py                    # stránky z sad/_build/obsah/ a obsah_zkouska/ (→ sad/zkouska/)
python sad/_build/make_pdf.py                 # volitelně, PDF jinak vytvoří GitHub Actions
```
`make_figures.py` přijme i část názvu obrázku (`… make_figures.py bode pristrojovy`) a vygeneruje jen ty.

## Obsah složky
- `_build/build.py` – sestavení stránek, slovník z rámečků definic, `skripta_vse.html`, kontroly
- `_build/make_figures.py` – schémata zapojení (schemdraw) a přenosové charakteristiky / průběhy (matplotlib)
- `_build/make_pdf.py` – PDF každé stránky a celých skript (headless Chrome)
- `_build/obsah/` – zdrojové texty stránek k testu, `_build/obsah_zkouska/` – ke zkoušce
- `zkouska/` – vygenerovaná skripta ke zkoušce (sdílí `assets/` a `figures/`)
- `assets/` – styl a skript (téma, navigace, vzorce KaTeX, tisk)
