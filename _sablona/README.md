# Šablona nového předmětu

Kostra skript pro další předmět. Nesestavuje se ani nenasazuje (složky začínající `_` workflow přeskakuje).

## Použití
1. Zkopíruj celou složku `_sablona/` do `<zkratka>/` (malými písmeny, bez diakritiky, např. `ziz/`).
2. V `<zkratka>/_build/build.py` uprav blok **KONFIGURACE** (`LANG`, `SHORT`, `BRAND`, `BRAND_SUB`, `GLOSSARY`, `PAGES`).
3. Kapitoly piš do `<zkratka>/_build/obsah/` podle vzoru `01_ukazka.html` (ukázkovou kapitolu pak smaž z `PAGES`
   i ze složky); grafy do `<zkratka>/_build/make_figures.py`.
4. Z kořene repozitáře:
   ```
   uv run python <zkratka>/_build/make_figures.py
   python <zkratka>/_build/build.py
   python <zkratka>/_build/make_pdf.py        # volitelně, PDF jinak vytvoří GitHub Actions
   ```
5. Přidej kartu do kořenového `index.html` a řádek do tabulky v kořenovém `README.md`.

Podrobný postup a standard obsahu: `AGENTS.md` v kořeni repozitáře.

## Obsah
- `_build/build.py` – sestavení stránek, slovník z rámečků definic, stránka `skripta_vse.html`, kontroly
- `_build/make_pdf.py` – PDF každé stránky a celých skript (headless Chrome)
- `_build/make_figures.py` – grafy (paleta a pravidla jako ve VMM)
- `_build/obsah/` – zdrojové texty stránek (`index.html`, kapitoly; slovník se generuje)
- `assets/` – styl a skript (téma, navigace, vzorce KaTeX, tisk; v `app.js` jsou i interaktivní ukázky z VMM
  v objektu `DEMOS` – nové ukázky se přidávají tam a do stránky se vloží `<div data-demo="nazev"></div>`)
