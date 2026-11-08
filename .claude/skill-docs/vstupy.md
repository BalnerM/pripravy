# Čtení vstupů (přednáška)

Vše z PDF ukládej do scratchpadu MIMO repo. Repo je veřejné.

## Případ A: jen čistá prezentace
- `pdftotext -layout soubor.pdf out.txt` je základ obsahu.
- Strany, kde text vzorců nebo schémat nedává smysl, vykresli (`pdftoppm -r 120 -f N -l N -png`) a prohlédni jako obrázek.

## Případ B: čistá prezentace + PDF s poznámkami
1. Text i obsah slidů vezmi z čisté verze (jako případ A).
2. Vykresli obě PDF (`pdftoppm -r 120 -png`) a ověř, že mají stejný počet stran a stejné rozměry.
   Pokud ne, přejdi na případ C.
3. Najdi strany s rukopisem porovnáním obrázků, např.:
   `uv run --with pillow python` a pro každou dvojici stran `ImageChops.difference(a, b).getbbox()`;
   strany s `None` (beze změny) přeskoč. U malého rozdílu zvaž práh, aby šum z exportu nebyl brán jako poznámka.
4. Rukopis čti jen ze stran, kde rozdíl je.

## Případ C: jen PDF s poznámkami (nebo nesouhlasí strany)
- Text slidů z `pdftotext`, poznámky čti ze všech stran jako obrázky.

## Přepis poznámek
Poznámky přepiš po slidech, s uvedením prvku slidu, ke kterému poznámka patří (vzorec, šipka, nadpis);
nejisté čtení označ `[?]`, nehádej. Přepis ulož do scratchpadu mimo repo.

Má-li rukopis víc než ~10 stran, deleguj čtení obrázků subagentovi, ať se obrázky nedostanou do hlavního kontextu:
subagent zapíše přepis do scratchpadu a do hlavního kontextu vrátí jen krátké shrnutí a seznam `[?]` s čísly slidů.
Hlavní agent pak čte jen přepis a konkrétní slidy tam, kde je to potřeba. U menšího rozsahu čti přímo.
