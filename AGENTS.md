# Pracovní pravidla (pro AI agenty i lidi)

Repozitář `pripravy` = studijní skripta k ústním i písemným zkouškám, jeden web pro všechny předměty.

- Web: https://balnerm.github.io/pripravy/ (rozcestník), předmět na `https://balnerm.github.io/pripravy/<zkratka>/`
- GitHub: https://github.com/BalnerM/pripravy (**veřejný** repozitář, účet `BalnerM`, `gh` je přihlášený)
- Lokálně: `OneDrive/Plocha/MPAD-BIO/pripravy/` (vedle složek jednotlivých předmětů, např. `../VMM`, `../ZIZ`)

## Struktura

```
index.html                    rozcestník: úvodní stránka ukazuje předměty, po rozkliknutí (#zkratka) jejich materiály;
                              data v poli PREDMETY na začátku skriptu
README.md                     přehled předmětů a návod pro uživatele
AGENTS.md / CLAUDE.md         tato pravidla
pyproject.toml, uv.lock       Python prostředí pro grafy (uv); dev skupina: playwright pro tools/check_layout.py
tools/check_layout.py         kontrola vykreslených stránek v Chromu: přetékání, rozbité obrázky, chyby KaTeX, husté odstavce
.github/workflows/pages.yml   při pushi do main: všechny */_build/build.py → */_build/make_pdf.py → GitHub Pages
_sablona/                     kostra nového předmětu (nesestavuje se, nenasazuje se)
vmm/                          hotová skripta VMM – referenční příklad kvality a stylu
<zkratka>/                    další předměty se stejnou strukturou jako _sablona/
```

Složka předmětu: `_build/build.py` (konfigurace + engine), `_build/make_figures.py`, `_build/make_pdf.py`,
`_build/obsah/*.html` (zdrojové texty stránek), `assets/` (styl, skript), `figures/` (PNG z make_figures),
vygenerované `*.html` a `skripta_vse.html`; `pdf/` vzniká až v GitHub Actions (v gitu není).

## Pravidla

- **Komunikace s uživatelem česky.** **Jazyk skript** podle přání uživatele: výchozí čeština, na požádání angličtina
  (`LANG = "en"` v konfiguraci `build.py`; rámečky pak „Definition: …“ a texty v anglických nadpisech boxů).
  **Obě verze najednou** (přepínač CZ/EN v liště): `ALT` v konfiguraci `build.py`, překlady v `_build/obsah_en/`
  se stejnými soubory a id (build to kontroluje), grafy `make_figures.py --lang en` do `figures/en/`, texty ukázek
  přes `i18n(cs, en)` v `app.js` – vzorem je `mlr/`. Angličtina jednoduchá, odborné pojmy zachovat.
- **Python jen přes uv:** `uv run python …`, nové balíčky `uv add …`; žádné `pip install`. `build.py` a `make_pdf.py`
  potřebují jen standardní knihovnu (spouští se i obyčejným `python`).
- **Repo je veřejné:** nikdy do něj nekopíruj ani necommituj slidy / PDF přednášek, skeny, zadání, osobní soubory
  ani nic z okolních složek (v `MPAD-BIO/` leží např. `github-recovery-codes.txt`). Přednášky se jen čtou z jejich
  složky (zpřístupnit přes `/add-dir` nebo `claude --add-dir`). Data převzatá z přednášky pro grafy případně vhodné grafy ano.
- **Generované soubory needituj ručně:** `<zkratka>/*.html` a stránku slovníku vytváří `build.py` – edituj
  `_build/obsah/*.html` (slovník se skládá z rámečků definic v kapitolách).
- Commit a push dělej, až když uživatel o zveřejnění požádá nebo to schválil v plánu; zprávy commitů česky.
- Před „hotovo“: `python <zkratka>/_build/build.py` musí projít (kontroluje obrázky, odkazy, kotvy, duplicitní id,
  povinné sekce a formát definic) **bez řádků „UPOZORNĚNÍ“** (husté odstavce se vzorci, dlouhé řádky vzorců),
  `uv run python tools/check_layout.py --only <zkratka>` musí skončit „problémů: 0“ a výsledek ověř vizuálně
  (viz Ověření). Pak záznam do `RUNS.md`.

## Standard obsahu skript (co uživatel požaduje)

Skripta slouží k **pochopení** a k tomu, aby uživatel uměl látku **vysvětlit vlastními slovy u zkoušky**.
Kód za grafy uživatel znát nepotřebuje. Vzorem je `vmm/` – před psaním si projdi aspoň `vmm/_build/obsah/03_predzpracovani.html`.

Každá kapitola (= jedna přednáška) obsahuje:

1. `<h1>` a `<p class="lead">` – o čem kapitola je a proč na tom záleží.
2. Pro každý pojem **rámeček Definice** – přesná definiční věta + pod čarou „Jinými slovy“ (praktický význam):
   `<div class="box definice" id="def-xyz"><div class="box-t">Definice: pojem</div><p>…</p><p class="jinak">…</p></div>`
   (přesně tento tvar, jinak se nepřevezme do slovníku; uvnitř žádné další `<div>`). Definice nevynechávej –
   uživatel výslovně chce definice **i** intuitivní vysvětlení, ne jen jedno z nich.
3. Rámečky podle potřeby (třídy `box …`): `intuice` (princip bez vzorců), `postup` (kroky algoritmu),
   `vzorec` (vzorec + `<table class="vars">` s vysvětlením **každé** proměnné), `priklad` (konkrétní čísla, ideálně
   z přednášky; **každé číslo přepočítej skriptem**), `pozor` (častá past / chyták), `zkouska` („Jak to říct u
   zkoušky“), `kostka` (shrnutí tématu jednou větou), `odnes` (pod každým obrázkem: „Co si z obrázku odnést“).
4. Obrázky: `<figure><div class="paper"><img src="figures/….png" alt="…" loading="lazy"></div><figcaption>…</figcaption></figure>`,
   schémata postupů jako inline SVG s třídami z `assets/style.css` (`node`, `fl1–fl3`, `ln`, `t2` – viz VMM).
5. Na konci povinně: `<section class="souhrn" id="shrnuti">` se shrnutím a `<div class="takehome">` (take-home
   messages), pak `<h2 id="otazky">` s 5–8 otázkami ke zkoušce jako `<details class="q">` s modelovou odpovědí.
6. Vzorce v KaTeX: `\( … \)` v textu, `\[ … \]` samostatně. **Přehlednost má přednost před úsporou místa** – platí
   pro příklady, definice, výklad i modelové odpovědi:
   - v textu jen krátké výrazy (symbol, `\(\lambda = 1\)`, zadané hodnoty); zlomek, suma, matice, řetěz víc „=“ nebo
     celá definiční rovnice patří do samostatného `\[ … \]` (v rámečku definice uvnitř jeho `<p>`, formát rámečku zůstane);
   - výpočet v příkladu **po krocích pod sebou**: jeden `\[ … \]` nebo řádek `aligned` na krok, mezi kroky krátký
     text („Dosadíme:“, „1. …“), nikdy řetěz `⇒` přes celý odstavec; výčet vlastností / kroků jako `<ul>`/`<ol>`;
   - **jeden řádek vzorce ≈ jeden vztah**: na mobilu (500 px) má vzorec jen ~420 px, takže víc vzorců vedle sebe
     (`,\qquad`) dej do `aligned` pod sebe; dlouhou rovnici zalom za `=` (`&=` na dalším řádku);
   - `aligned[t]` KaTeX neumí (vypíše „[t]“) – popisek dej do vlastního řádku `&\text{…}: \\`;
   - široká tabulka s mnoha sloupci: `<table class="compact">`; delší vzorec v buňce tabulky jako `\[ … \]`.
   Špatně: `<p>\(X^\top X = …\), \(X^\top y = …\) ⇒ \(\tilde w = …\), tedy \(\hat y = …\).</p>` –
   dobře: `<p>1. Součiny:</p> \[ X^\top X = …,\qquad X^\top y = … \] <p>2. Řešení:</p> \[ \tilde w = … \]`.
   Jazyk výkladu jednoduchý, bez zbytečně složitých formulací; definice ale přesné. Věrnost přednáškám: stejné
   příklady, terminologie a čísla jako na slidech (u nejasností se podívej na stránku PDF jako obrázek).
   Navíc obvykle: srovnávací stránka / tahák (`★`), slovník (generuje se), interaktivní ukázky (volitelné, `DEMOS` v `app.js`).

Grafy (`_build/make_figures.py`): paleta C1 `#2a78d6`, C2 `#eb6834`, C3 `#1baf7a` v pevném pořadí, tvar značky
jako druhé rozlišení, popsané osy, žádná dvojí osa y, pevný random seed; řiď se skillem `dataviz`, je-li k dispozici.
Elektrická schémata (R, C, OZ…) kresli knihovnou `schemdraw` v `make_figures.py` – vzorem je `sad/`.

## Postup: nová skripta k předmětu

1. Ujasni si s uživatelem: složku s přednáškami, zkratku (`ziz`), jazyk (cs/en), rozsah (které přednášky) a doplňky
   (otázky s odpověďmi, srovnávací tabulky, interaktivní ukázky). Pokud agent nemá k přednáškám přístup, požádej
   uživatele o `/add-dir "../<složka>"`.
2. Vytáhni text slidů do scratchpadu: `pdftotext -layout soubor.pdf out.txt` (Poppler z MiKTeX je v PATH);
   obrázkové slidy si prohlédni přímo (čtení PDF po stránkách).
3. `cp -r _sablona <zkratka>`; v `<zkratka>/_build/build.py` uprav KONFIGURACI (`LANG`, `SHORT`, `BRAND`,
   `BRAND_SUB`, `GLOSSARY`, `PAGES`); smaž ukázkovou kapitolu `01_ukazka` (z `PAGES` i `obsah/`) a ukázkový graf.
4. Napiš `obsah/index.html` (mapa kurzu, jak skripta používat, karty kapitol) a kapitoly podle standardu výše.
5. Grafy: `uv run python <zkratka>/_build/make_figures.py`.
6. Sestavení: `python <zkratka>/_build/build.py`; PDF lokálně (volitelně): `python <zkratka>/_build/make_pdf.py`.
7. Přidej předmět (objekt s `id` = malá zkratka, `materialy` s odkazy) do pole `PREDMETY` v kořenovém `index.html`
   a řádek do tabulky v `README.md`. Další materiál k předmětu = další objekt v jeho `materialy`.
8. Ověř (níže), zapiš do `RUNS.md`, a po souhlasu uživatele `git add -A`, `git commit`, `git push`;
   pak `gh run watch` a zkontroluj web a PDF (`curl -sI https://balnerm.github.io/pripravy/<zkratka>/`).

## Ověření

- `build.py` bez chyb a bez upozornění; čísla v příkladech přepočítaná.
- `uv run python tools/check_layout.py --only <zkratka>` (lokální soubory, šířky 1280 a 500 px, cs i en, otázky
  rozbalené): hlásí přetékající vzorce / tabulky / boxy, vodorovný scroll stránky, nenačtené obrázky, chyby KaTeX
  a husté odstavce. Po nasazení totéž s `--base https://balnerm.github.io/pripravy/` na živém webu. Široká
  tabulka nebo SVG schéma s vlastním posuvníkem na 500 px je záměr (`posuvník`, výchozí se nehlásí), na 1280 px ne.
  Jednu stránku zkontroluješ přes `--pages 04_lin`. Na hromadnou kontrolu je tento skript efektivnější než MCP
  Playwright (proběhne celý najednou, vrátí krátký seznam); MCP/prohlížeč jen na interaktivní ladění ukázek.
- Screenshoty headless Chrome (`chrome --headless=new --screenshot --window-size=1280,8000 --virtual-time-budget=6000`,
  vlastní `--user-data-dir`): světlý i tmavý režim (kopie stránky s `data-theme` + `<base href>`), úzká šířka (~500 px),
  vykreslené vzorce, obrázky, žádné přetékání.
- PDF: `pdftoppm -r 60 -png` několika stran – A4, rozbalené odpovědi, vzorce.

## Po každém úkolu

Přidej řádek do `RUNS.md` (datum, model, co bylo zadáno, jak se to ověřilo – včetně selhání).
