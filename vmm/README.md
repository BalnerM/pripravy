# Příprava na zkoušku VMM

Studijní skripta k ústní zkoušce z přednášek 1–11 předmětu VMM (vícerozměrné metody).

- **Online:** https://balnerm.github.io/pripravy/vmm/
- **Lokálně:** otevři `index.html` v prohlížeči.

## Obsah
- `index.html` – mapa kurzu a rozcestník
- `01_uvod.html` … `11_umap.html` – jedna stránka na přednášku (definice, princip, postup, vzorce s vysvětlenými
  proměnnými, příklady, obrázky, shrnutí, take-home messages, otázky ke zkoušce s odpověďmi)
- `12_srovnani.html` – rozhodovací schéma, srovnávací tabulky, zaměňované pojmy, tahák vzorců
- `13_slovnik.html` – všechny definice pohromadě (generuje se automaticky z rámečků definic v kapitolách)
- `assets/` – styl a skript (téma, navigace, interaktivní ukázky)
- `figures/` – vygenerované grafy

## Jak skripta upravit
HTML stránky v této složce se **generují** – needituj je ručně, ale zdroje v `_build/`:
- texty kapitol: `_build/obsah/*.html` (jen obsah stránky, bez hlavičky a navigace)
- definice pojmů: rámeček `<div class="box definice" id="def-…"><div class="box-t">Definice: pojem</div><p>…</p><p class="jinak">…</p></div>`
  přímo v textu kapitoly; `build.py` z nich sestaví `_build/obsah/13_slovnik.html` (ten needituj)
- seznam stránek a šablona: `_build/build.py`
- grafy: `_build/make_figures.py` (data o proteinech z přednášky 6: `_build/protein.csv`)

**Úprava přímo na GitHubu:** otevři soubor v `vmm/_build/obsah/`, klikni na tužku, uprav a ulož (Commit changes).
GitHub Actions stránky znovu sestaví a asi za minutu je změna na webu.

**Úprava lokálně** (z kořene repozitáře `pripravy`):
```
python vmm/_build/build.py                                       # sestaví stránky a zkontroluje odkazy
uv run --project ../VMM python vmm/_build/make_figures.py        # přegeneruje obrázky (prostředí projektu VMM)
git add -A && git commit -m "popis změny" && git push
```
Vzorce vykresluje KaTeX z CDN (potřeba internet); offline zůstane vidět zdrojový zápis vzorců.
