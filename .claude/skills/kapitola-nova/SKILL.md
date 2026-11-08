---
name: kapitola-nova
description: Napíše celou kapitolu skript od nuly z jedné přednášky (čistá prezentace, PDF s ručními poznámkami, nebo obojí). Použij, když kapitola ještě neexistuje.
disable-model-invocation: true
---

# Nová kapitola z přednášky

Vstup od uživatele: předmět (zkratka), číslo/název kapitoly, cesty k PDF (čistá prezentace a/nebo PDF s poznámkami), případná přání.
Argumenty: $ARGUMENTS

1. Přečti `.claude/skill-docs/vstupy.md` a načti vstupy podle toho, co uživatel dal.
2. Pokud jsou ve vstupu ruční poznámky, přečti i `.claude/skill-docs/poznamky.md` a poznámky roztřiď.
3. Prohlédni vzor kvality: `vmm/_build/obsah/03_predzpracovani.html` a u dvojjazyčného předmětu `mlr/`.
4. Napiš kapitolu rovnou, bez mezikroku s návrhem, podle „Standardu obsahu skript“ v AGENTS.md:
   - věrnost přednášce: stejné příklady, terminologie, čísla, značení; každé číslo v příkladu přepočítej skriptem,
   - z poznámek přebírej jen potvrzené (viz poznamky.md); do boxů `intuice` a `zkouska` jejich formulace téměř doslova,
   - grafy přidej do `make_figures.py` (cs i en, má-li předmět `ALT`), pod každý box `odnes`,
   - nové stránky zapiš do `PAGES` v `build.py`; u `ALT` vytvoř stejné soubory a id v `obsah_en/`.
5. Ověření podle AGENTS.md (`build.py` bez UPOZORNĚNÍ, `check_layout.py --only <zkratka>`).
6. Závěrečné shrnutí uživateli, v tomto pořadí:
   a) poznámky, které NEBYLY zapracovány (nepotvrzené, rozporné, důležitá `[?]`) a proč,
   b) co bylo vytvořeno (stránky, grafy),
   c) co se nepodařilo ověřit.
7. Zapiš do `RUNS.md`. Nic necommituj ani nepushuj, uživatel nejdřív projde diff a výsledek.
