---
name: kapitola-doladit
description: Doplní existující kapitolu skript podle přednášky a ručních poznámek (nejdřív návrh změn, po schválení doplnění). Použij, když kapitola už existuje a má se jen zlepšit. Režim „rovnou“ vynechá návrh.
disable-model-invocation: true
---

# Doladění existující kapitoly

Vstup od uživatele: soubor kapitoly, cesty k PDF (čistá prezentace a/nebo PDF s poznámkami), konkrétní přání, případně slovo „rovnou“.
Argumenty: $ARGUMENTS

1. `git status`: pokud jsou v dotčených souborech necommitnuté změny, upozorni uživatele.
2. Přečti `.claude/skill-docs/vstupy.md` a načti vstupy. Jsou-li poznámky, přečti i `.claude/skill-docs/poznamky.md`.
3. Přečti stávající kapitolu (a u `ALT` i její `obsah_en/` verzi).
4. **Výchozí režim: předlož NÁVRH změn, zatím nic neupravuj.** Max. ~10 položek seřazených podle přínosu, každá jednou větou:
   a) co chybí nebo je zkreslené oproti slidům/poznámkám (u každé poznámky uveď stav podle poznamky.md),
   b) kde pomůže vysvětlení, příklad nebo intuice (a v jakém boxu),
   c) kde pomůže graf (co přesně zobrazit, z jakých dat).
   Počkej na schválení.
5. **Režim „rovnou“** (uživatel napsal „rovnou“ nebo „bez návrhu“): návrh vynech a změny rovnou zapracuj.
   Poznámky ale roztřiď podle poznamky.md a přebírej jen potvrzené.
6. Zapracuj změny jako DOPLNĚNÍ: zachovej stávající text, styl, strukturu a všechna `id`. Nepřepisuj, co je v pořádku.
   Nic nepřidávej nad rámec přednášky, pokud o to uživatel výslovně nepožádal. Do boxů `intuice` a `zkouska`
   přebírej ověřené formulace z poznámek téměř doslova (přeložené, je-li kapitola česky).
7. U `ALT` uprav `obsah/` i `obsah_en/` se stejnými id. Nové grafy do `make_figures.py` (cs i en), pod každý box `odnes`.
8. Ověření podle AGENTS.md. Pak shrnutí: nejdřív nezapracované poznámky a důvod, potom co bylo přidáno / upraveno / odstraněno.
9. Zapiš do `RUNS.md`. Nic necommituj ani nepushuj.
