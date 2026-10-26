# Přípravy na zkoušky

Studijní materiály k jednotlivým předmětům, zveřejněné přes GitHub Pages:
**https://balnerm.github.io/pripravy/**

| Složka | Předmět | Web |
|---|---|---|
| `vmm/` | Vícerozměrné metody (VMM) | https://balnerm.github.io/pripravy/vmm/ |

## Jak to funguje
- `index.html` v kořeni je rozcestník (píše se ručně).
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

## Přidání dalšího předmětu
1. Vytvoř složku (např. `ziz/`) s `index.html` – nejjednodušeji zkopíruj strukturu `vmm/` včetně `_build/`.
2. Přidej kartu do kořenového `index.html` a řádek do tabulky výše.
3. Commit a push – workflow sestaví a nasadí i novou složku.
