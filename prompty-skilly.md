# Prompty pro skilly `/kapitola-doladit` a `/kapitola-nova`

Ukázkové prompty pro všechny varianty. Cesty a názvy uprav podle sebe.

## Příprava (jednou za relaci)

```
cd ".../MPAD-BIO/pripravy"
claude --add-dir "../MLR"
```

Relace už běží? Použij `/add-dir ../MLR`.
Ověř, že po napsání `/` vidíš `/kapitola-nova` a `/kapitola-doladit`.

## Základní pravidla promptování

1. **Vždy napiš typ vstupu**: slovo `čistá` (bez poznámek) nebo `s poznámkami`. Podle názvu souboru to agent nepozná.
2. **Doladění = výchozí návrh změn**, slovo `rovnou` návrh vynechá.
3. **Nová kapitola = vždy rovnou**, bez návrhu. Diff proto projdi celý.
4. **Přání piš konkrétně** (co přesně zobrazit, kde chceš víc intuice), ne obecně „zlepši to“.
5. Mezi kapitolami dělej `/clear`.
6. Nic se necommituje samo. Commit a push řekneš až ty po kontrole diffu.

---

## A) Doladění existující kapitoly

### A1) Jen čistá prezentace (bez poznámek), s návrhem

```
/kapitola-doladit mlr/_build/obsah/05_neuron.html
čistá: ../MLR/prednasky/05.pdf
Přání: graf sigmoidy a její derivace, víc intuice k násobení derivací při backpropagation.
```

### A2) Jen PDF s poznámkami, s návrhem

```
/kapitola-doladit mlr/_build/obsah/05_neuron.html
s poznámkami: ../MLR/prednasky/05_poznamky.pdf
Přání: využij moje poznámky na slidech 8-12, doplň graf aktivačních funkcí.
```

### A3) Čistá i s poznámkami (úspornější čtení rukopisu), s návrhem

```
/kapitola-doladit mlr/_build/obsah/05_neuron.html
čistá: ../MLR/prednasky/05_clean.pdf
s poznámkami: ../MLR/prednasky/05_poznamky.pdf
Přání: doplň intuici k chybové funkci a graf průběhu učení.
```

### A4) Rovnou, bez návrhu

Přidej slovo `rovnou`. Funguje u všech tří vstupů výše.

```
/kapitola-doladit mlr/_build/obsah/05_neuron.html
s poznámkami: ../MLR/prednasky/05_poznamky.pdf
Rovnou.
Přání: doplň, co chybí oproti přednášce, a graf sigmoidy.
```

Agent i tak roztřídí poznámky a do kapitoly vezme jen potvrzené. Ostatní vypíše na začátku shrnutí.

### A5) Doladění bez konkrétního přání (agent navrhne sám)

```
/kapitola-doladit mlr/_build/obsah/05_neuron.html
čistá: ../MLR/prednasky/05.pdf
Bez konkrétního přání. Navrhni, co chybí nebo je nejasné oproti přednášce.
```

---

## B) Nová kapitola od nuly

Agent píše rovnou, návrh se nedělá.

### B1) Z čisté prezentace

```
/kapitola-nova mlr, kapitola 8
čistá: ../MLR/prednasky/08.pdf
```

### B2) Z PDF s poznámkami

```
/kapitola-nova mlr, kapitola 8
s poznámkami: ../MLR/prednasky/08_poznamky.pdf
Přání: u regularizace dej důraz na moje poznámky, do boxu "Jak to říct u zkoušky" použij moje formulace.
```

### B3) Z čisté i s poznámkami

```
/kapitola-nova mlr, kapitola 8
čistá: ../MLR/prednasky/08_clean.pdf
s poznámkami: ../MLR/prednasky/08_poznamky.pdf
```

### B4) S dodatečnými požadavky

```
/kapitola-nova vmm, kapitola 6
čistá: ../VMM/prednasky/06.pdf
Přání: aspoň jeden interaktivní graf, srovnávací tabulka metod na konci, 8 otázek ke zkoušce.
```

---

## C) Reakce po návrhu změn (u doladění)

Agent předloží očíslovaný seznam. Odpovědi:

```
Zapracuj 1, 2, 4, 6 a 7. Bez 3 a 5.
```

```
Zapracuj vše kromě 3. U bodu 5 to uprav tak, že graf bude jen pro sigmoidu, ne pro tanh.
```

```
Zapracuj vše.
```

### Rozhodnutí o poznámkách, které agent nezapracoval

Agent je vypíše na začátku shrnutí (nepotvrzené, rozporné, `[?]`).

```
Poznámka ze slidu 10 "feeded forwardly" je "feed-forward". Zapracuj ji. Ostatní nepotvrzené nech být.
```

```
Poznámky 2 a 4 jsou specifické pro náš kurz, vezmi je jako platné a zapracuj je.
```

---

## D) Po dokončení

Nejdřív zkontroluj `git diff` a vzhled stránky. Pokud je to v pořádku:

```
Commitni a pushni. Zpráva commitu česky.
```

Pokud něco nesedí a chceš začít znovu:

```
git restore .
```

(Vrací jen necommitnuté změny. Nové soubory, které agent vytvořil, smaž ručně nebo `git clean -n` pro náhled.)

Pokud je výsledek skoro dobrý, jen s výhradami:

```
Vrať změnu u [konkrétní místo], zbytek nech. U grafu změň [co přesně].
```

---

## Co dělat, když něco nefunguje

| Problém | Řešení |
|---|---|
| Skill se nenabízí po napsání `/` | Spusť Claude Code z kořene `pripravy`, restartuj relaci, zkontroluj `.claude/skills/` |
| Agent neví, kde je PDF | `/add-dir ../MLR` a zadej cestu relativně od kořene repa |
| Návrh obsahuje spoustu zbytečností | Vyškrtni položky a zpřesni příště "Přání". Případně uprav `.claude/skills/kapitola-doladit/SKILL.md` |
| Špatně rozpoznané strany s rukopisem (případ A3) | Uprav práh rozdílu v `.claude/skill-docs/vstupy.md` nebo dej jen verzi s poznámkami |
| Rukopis čtený špatně | V přepisu hledej `[?]`, případně řekni, jak to má být, a agent to opraví |
| Změnilo se `id` nebo se rozbil slovník | `git restore` a zopakuj. Pravidlo o stabilních `id` je v `AGENTS.md` |

## Vzorový průběh jedné kapitoly

1. `/clear`
2. `/kapitola-doladit …` (s návrhem)
3. Projít návrh a odpovědět, co zapracovat
4. Projít shrnutí agenta: nejdřív nezapracované poznámky, pak změny
5. Zkontrolovat `git diff` a vzhled stránky
6. "Commitni a pushni."
7. Další kapitola, znovu od bodu 1
