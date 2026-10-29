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

## Generované soubory
- `uv run python pso/_build/make_figures.py [název_funkce …]` – grafy do `figures/`
- `uv run python pso/_build/make_tables.py` – fragment `obsah/13_tabulky.html` (needituj ručně)
- `python pso/_build/build.py` – stránky a slovník
