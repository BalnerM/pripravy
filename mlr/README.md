# Příprava na zkoušku MLR

Studijní skripta k přednáškám 1–7 předmětu MPA-MLR (strojové učení, FEKT VUT, podzim 2026). Navíc oproti
běžnému standardu: u každého modelu rámeček **Parametry** – co který hyperparametr znamená a co se stane,
když ho zvětším / zmenším; vše pohromadě na stránce `08_parametry.html`.

- **Online:** https://balnerm.github.io/pripravy/mlr/
- **Lokálně:** otevři `index.html` v prohlížeči.
- **Zdroj:** přednášky T. Vičara a J. Chmelíka (https://tomasvicar.github.io/MLR-public/lectures.html);
  slidy se do repozitáře nekopírují. Přednášky 8–12 se doplní po zveřejnění.

## Obsah
- `index.html` – mapa kurzu a rozcestník
- `01_uvod.html` … `07_neuronove_site.html` – jedna stránka na přednášku (definice, princip, postup, vzorce
  s vysvětlenými proměnnými, příklady s přepočítanými čísly, obrázky, parametry modelů, shrnutí, take-home
  messages, otázky ke zkoušce s odpověďmi)
- `08_parametry.html` – tahák: hyperparametry všech modelů, srovnání modelů, metriky, chytáky
- `99_slovnik.html` – všechny definice pohromadě (generuje se z rámečků definic v kapitolách)
- `skripta_vse.html` – všechny stránky za sebou (podklad pro PDF celých skript, generuje se)
- `pdf/` – PDF každé stránky a `skripta_vse.pdf` (vytváří `_build/make_pdf.py` v GitHub Actions, v gitu nejsou)
- `assets/` – styl (včetně rámečku `box parametry`) a skript s interaktivními ukázkami (`DEMOS` v `app.js`:
  krok učení, k-NN, k-means, práh a ROC, PCA, perplexita, UMAP graf, jádro, polynomiální ridge, SVM,
  regresní strom + bagging, optimalizátory)
- `figures/` – grafy z `_build/make_figures.py` (syntetická data s pevným seedem a datasety ze scikit-learn)

## Anglická verze
Na `https://balnerm.github.io/pripravy/mlr/en/`; tlačítko **EN / CZ** v horní liště přepne na totéž místo ve
druhém jazyce. Zdroje jsou v `_build/obsah_en/` (stejné názvy souborů a stejná id jako v `obsah/` – `build.py`
to kontroluje), grafy s anglickými popisky v `figures/en/` (`make_figures.py --lang en`), texty interaktivních
ukázek v `assets/app.js` (funkce `i18n`). Při úpravě české kapitoly je potřeba upravit i anglickou.

## Jak skripta upravit
HTML stránky v této složce se **generují** – edituj zdroje v `_build/obsah/*.html` a seznam stránek
v `_build/build.py`. Z kořene repozitáře `pripravy`:
```
uv run python mlr/_build/make_figures.py      # přegeneruje obrázky (jen vybrané: … make_figures.py fig04_poly)
uv run python mlr/_build/make_figures.py --lang en   # totéž s anglickými popisky do figures/en/
python mlr/_build/build.py                     # sestaví stránky a zkontroluje odkazy, obrázky, sekce
python mlr/_build/make_pdf.py                  # volitelně PDF lokálně
```
