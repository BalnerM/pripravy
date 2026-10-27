# Přípravy na zkoušky

Studijní materiály k jednotlivým předmětům, zveřejněné přes GitHub Pages:
**https://balnerm.github.io/pripravy/**

| Složka | Předmět | Web |
|---|---|---|
| `vmm/` | Vícerozměrné metody (VMM) | https://balnerm.github.io/pripravy/vmm/ |
| `mlr/` | Strojové učení (MPA-MLR), přednášky 1–7; i anglicky | https://balnerm.github.io/pripravy/mlr/ (EN: …/mlr/en/) |

## Jak to funguje
- `index.html` v kořeni je rozcestník: úvodní stránka ukazuje předměty, po rozkliknutí se objeví materiály
  k předmětu (skripta, další materiály). Obsah je v poli `PREDMETY` na začátku skriptu v `index.html`.
- Každý předmět má svou složku; stránky se generují skriptem `<předmět>/_build/build.py` ze zdrojů
  v `<předmět>/_build/obsah/` (podrobnosti v `vmm/README.md`).
- Po každém pushi do větve `main` workflow `.github/workflows/pages.yml` spustí všechny `*/_build/build.py`
  a `*/_build/make_pdf.py` (PDF ke každé stránce + celá skripta, tlačítko **PDF** na webu) a nasadí web.
  Průběh je vidět v záložce **Actions**.

## Úpravy a verze
- **Na GitHubu:** otevři zdrojový soubor (např. `vmm/_build/obsah/03_predzpracovani.html`), tužka → uprav →
  *Commit changes*. Web se sám přestaví (cca 1 minuta).
- **Lokálně:** uprav zdroje, spusť `python vmm/_build/build.py`, pak `git add -A`, `git commit -m "…"`, `git push`.
  Před lokální úpravou nejdřív `git pull` (kdyby se mezitím něco změnilo na GitHubu).
- **Historie verzí:** u každého souboru tlačítko *History* na GitHubu, lokálně `git log`;
  starou verzi lze zobrazit nebo vrátit (`git revert <commit>`).

## Skripta k dalšímu předmětu (s pomocí Claude Code)
Agent spuštěný v této složce má všechny potřebné informace v `AGENTS.md` (postup, standard obsahu, pravidla)
a vychází ze šablony `_sablona/`. Stačí mu zpřístupnit složku s přednáškami:
```
cd "…/MPAD-BIO/pripravy"
claude --add-dir "../ZIZ"
> Udělej skripta k předmětu ZIZ podle AGENTS.md, přednášky jsou v ../ZIZ/prednasky.
```
(Ve spuštěné relaci jde složka přidat i příkazem `/add-dir ../ZIZ`.) Skripta mohou být česky i anglicky –
stačí to agentovi říct („…v angličtině“). Přednášky se jen čtou, do veřejného repozitáře se nekopírují.

Ručně: zkopíruj `_sablona/` do `<zkratka>/`, uprav konfiguraci v `<zkratka>/_build/build.py`, piš kapitoly
do `<zkratka>/_build/obsah/`, přidej předmět do pole `PREDMETY` v kořenovém `index.html` a řádek do tabulky výše, commit a push
(podrobně v `_sablona/README.md`). Grafy: `uv run python <zkratka>/_build/make_figures.py` (prostředí repa,
po klonu `uv sync`).
