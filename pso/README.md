# PSO – Pravděpodobnost a statistika (MPA-PSO)

Česká skripta k předmětu vyučovanému anglicky. Anglické termíny jsou v nadpisu každé definice
(`<span class="en">…</span>`, přecházejí i do slovníku) a v boxu `slovicka` na konci kapitoly.

**Kapitoly nejsou podle přednášek, ale podle typů úloh** ze sad cvičení (`tasks/`). Teorie je ze skript
předmětu (Bastinec, *Probability, Statistics and Operational research*), značení stejné: \(p(A)\), \(EX\), \(DX\),
\(F(x) = p(X < x)\), Bi(n, p), Po(λ), No(μ, σ), Φ(u), test v krocích K1–K5.

## Stavební prvky navíc oproti šabloně
- `<div class="box uloha" id="u-sN-k">` – úloha k ze sady N: zadání česky (parafráze, ne kopie PDF), řádek
  `<p class="meta">` s anglickými klíčovými slovy (`<span class="kw">`) a výsledkem, pod tím
  `<details class="reseni"><summary>Řešení krok po kroku</summary><div>…</div></details>`.
- Domácí úkoly (HW) se **neřeší** (bodované, web je veřejný): místo nich `box priklad` s id `pr-…`
  „Podobná úloha jako HWx/y“ s jinými čísly a celým postupem.
- `box postup` s nadpisem „Jak poznat a jak postupovat: …“ u každého typu úlohy.
- `box slovicka` – tabulka CZ ↔ EN a fráze ze zadání, před `#shrnuti`.

## Přidání nové sady úloh
1. Vytáhni text zadání (`pdftotext -layout`) do scratchpadu; výsledky přepočítej skriptem.
2. Každou úlohu zařaď do kapitoly podle typu jako `box uloha` s id `u-sN-k`; nový typ úlohy = nová sekce
   (nebo nová kapitola do `PAGES` v `_build/build.py` + karta v `obsah/index.html`).
3. Doplň řádky do `obsah/12_ulohy.html` (přehled) a případně do rozpoznávače v `obsah/11_jak_poznat.html`.
4. Nový HW: analogická úloha do kapitoly + řádek do tabulky `#hw` v `12_ulohy.html`.
5. Aktualizuj popis „sady 1–N“ v kořenovém `index.html`.

## Příprava na semestrální test (`test/`)
Samostatné stránky mimo `build.py` (Actions je jen nasadí): `index.html` (14 typů úloh ze sad 1–8 a HW: poznáš
podle, postup, kalkulačka, pozor, vzory, příklady k procvičení; sada 8 vyřešená celá), `cvicny_test.html`,
`kalkulacka.html` (Casio fx-991CE X), `tahak.html` (2 A4 s postupy), `tahak_vzorce.html` (2 A4 jen vzorce),
`tabulky.html` (2 A4). Společný styl `test.css` + `test.js`, taháky `tahak.css`.
- `PYTHONIOENCODING=utf-8 uv run python pso/test/_gen/make_tabulky.py` – vygeneruje `tabulky.html` (scipy)
- `uv run python pso/test/_gen/make_pdfs.py [soubor.html …]` – PDF (Playwright) taháků, tabulek a kalkulačky
  + kontrola, že tahák nepřetéká z A4; PDF se commitují
- Kontrola webu: `uv run python tools/check_layout.py --only pso --pages test/`
- Taháky/tabulky editovat přes Edit, ne heredoc v Bashi (zkracuje `\\` v `aligned`).

## Generované soubory
- `uv run python pso/_build/make_figures.py [název_funkce …]` – grafy do `figures/`
- `uv run python pso/_build/make_tables.py` – fragment `obsah/13_tabulky.html` (needituj ručně)
- `python pso/_build/build.py` – stránky a slovník
