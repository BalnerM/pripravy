"""Sestaví HTML stránky skript z fragmentů v _build/obsah/ a zkontroluje odkazy.

Spuštění (z kořene repozitáře pripravy):  python <zkratka>/_build/build.py
Stačí standardní knihovna Pythonu – stejný příkaz spouští i GitHub Actions při nasazení na Pages.
Pro nový předmět se mění jen KONFIGURACE (nahoře), engine pod ní je společný.
"""

# =====================================================================================================================
# KONFIGURACE PŘEDMĚTU  (po zkopírování _sablona/ do <zkratka>/ uprav tento blok)
# =====================================================================================================================
LANG = "cs"                                   # jazyk skript: "cs" nebo "en" (texty rozhraní, <html lang>)
SHORT = "MLR"                                 # zkratka předmětu (titulky stránek)
BRAND = "MLR – příprava na zkoušku"           # název v horní liště a tiskové hlavičce (en: "XYZ – exam notes")
BRAND_SUB = "strojové učení: principy, modely a jejich parametry"
GLOSSARY = "99_slovnik"                       # stránka slovníku generovaná z rámečků definic (None = bez slovníku)

# (soubor fragmentu bez .html, číslo přednášky / značka, název, krátký popis)
# Stránky s číselným „číslem“ jsou kapitoly přednášek – musí mít definice, #shrnuti, take-home a #otazky.
PAGES = [
    ("index", "", "Mapa kurzu", "Jak skripta používat a jak spolu témata souvisí."),
    ("01_uvod", "1", "Úvod, větve ML a optimalizace",
     "AI, ML a DL, učení s učitelem i bez něj, optimalizace a gradientní sestup, k-NN a k-means."),
    ("02_hodnoceni", "2", "Hodnocení modelů a předzpracování",
     "Trénovací, validační a testovací data, metriky, ROC a AUC, nevyvážené třídy, křížová validace, předzpracování."),
    ("03_redukce", "3", "Výběr příznaků a redukce dimenze",
     "Prokletí dimenzionality, filtry, wrappery, PCA, LDA, t-SNE, UMAP a jádrový trik."),
    ("04_linearni", "4", "Lineární modely, jádra a SVM",
     "Lineární a polynomiální regrese, ridge a LASSO, jádra, logistická regrese, perceptron a SVM."),
    ("05_vibecoding", "5", "Vibecoding: práce s AI agentem",
     "Jazykový model, agent a nástroje, kontext, kontrola výsledků a bezpečnost."),
    ("06_stromy", "6", "Rozhodovací stromy a ensemble methods",
     "Bias, rozptyl a šum, CART, bagging, random forest a AdaBoost."),
    ("07_neuronove_site", "7", "Umělé neuronové sítě",
     "Neuron, aktivační funkce, backpropagation, optimalizátory, ztrátové funkce a regularizace."),
    ("08_parametry", "★", "Tahák: parametry a srovnání modelů",
     "Všechny hyperparametry na jednom místě: co znamenají a co se stane, když je zvětším nebo zmenším."),
    ("99_slovnik", "Aa", "Slovník pojmů (definice)", "Všechny definice ze skript na jednom místě."),
]

# Druhá jazyková verze (volitelné, None = skripta jen v jednom jazyce). Fragmenty jsou v _build/obsah_<jazyk>/
# se stejnými názvy souborů a stejnými id, stránky se sestaví do <zkratka>/<jazyk>/ a na každé stránce je tlačítko,
# které přepne na totéž místo ve druhém jazyce. Obrázky se berou z figures/<jazyk>/ (make_figures.py --lang <jazyk>).
ALT = dict(
    LANG="en",
    BRAND="MLR – exam notes",
    BRAND_SUB="machine learning: principles, models and their parameters",
    PAGES=[
        ("index", "", "Course map", "How to use the notes and how the topics fit together."),
        ("01_uvod", "1", "Introduction, branches of ML and optimization",
         "AI, ML and DL, supervised and unsupervised learning, optimization and gradient descent, k-NN and k-means."),
        ("02_hodnoceni", "2", "Model evaluation and preprocessing",
         "Training, validation and test data, metrics, ROC and AUC, imbalanced classes, cross-validation, "
         "preprocessing."),
        ("03_redukce", "3", "Feature selection and dimensionality reduction",
         "Curse of dimensionality, filters, wrappers, PCA, LDA, t-SNE, UMAP and the kernel trick."),
        ("04_linearni", "4", "Linear models, kernels and SVM",
         "Linear and polynomial regression, ridge and LASSO, kernels, logistic regression, perceptron and SVM."),
        ("05_vibecoding", "5", "Vibecoding: working with an AI agent",
         "Language model, agent and tools, context, checking results and security."),
        ("06_stromy", "6", "Decision trees and ensembles",
         "Bias, variance and noise, CART, bagging, random forest and AdaBoost."),
        ("07_neuronove_site", "7", "Artificial neural networks",
         "Neuron, activation functions, backpropagation, optimizers, loss functions and regularization."),
        ("08_parametry", "★", "Cheat sheet: parameters and model comparison",
         "All hyperparameters in one place: what they mean and what happens when I increase or decrease them."),
        ("99_slovnik", "Aa", "Glossary (definitions)", "All definitions from the notes in one place."),
    ],
)

# Další samostatná skripta téhož předmětu ve vlastní podsložce (sdílí assets/ a figures/, mají vlastní slovník,
# skripta_vse.html a pdf/). Fragmenty v _build/obsah_<DIR>/, jazyková verze v _build/obsah_<DIR>_<jazyk>/
# (výstup <DIR>/<jazyk>/). KICKER = štítek nad nadpisem kapitoly místo „Přednáška“.
#   test1/  příprava na Practical test 1 (computing): kapitoly podle typů úloh z ukázek A a B a z cvičení 1–6,
#           zadání úloh anglicky jako v testu, řešené ukázky, cvičné testy, tahák.
EDITIONS = [dict(
    DIR="test1", BRAND="MLR – průběžný test 1", BRAND_SUB="typové úlohy: výpočty na papíře a čtení kódu",
    KICKER="Typ úloh",
    PAGES=[
        ("index", "", "Jak se připravit", "Formát testu, mapa typů úloh a plán přípravy."),
        ("01_numpy", "1", "Čtení kódu v NumPy", "Tvary polí, axis, @ a *, masky, argmax, column_stack, rng.choice."),
        ("02_knn", "2", "Vzdálenosti, k-NN a gradientní sestup", "Nejbližší soused ručně, hlasování, krok sestupu."),
        ("03_metriky", "3", "Matice záměn a metriky", "TP, FN, FP, TN, accuracy, recall, precision, F1, MSE a MAE."),
        ("04_predzpracovani", "4", "Předzpracování a únik dat", "Standardizace, fit jen na trénovacích datech, red flags."),
        ("05_vyber_priznaku", "5", "Výběr příznaků a PCA", "Korelace, entropie a MI ručně, dopředný výběr, PCA."),
        ("06_linearni_regrese", "6", "Lineární regrese ručně", "Matice X, normální rovnice, inverze 2×2, predikce."),
        ("07_polynom_ridge", "7", "Polynomy, přeučení, ridge a jádra",
         "Polynomiální příznaky, under/overfitting, ridge, lasso, duální tvar a jádra."),
        ("08_stromy_ansambly", "8", "Stromy, bagging a SVM", "Strom na papíře, Gini, bootstrap, hlasování, C a gamma."),
        ("09_agenti", "9", "AI agenti: skill a subagent", "Pojmy z 5. přednášky a cvičení jednou větou."),
        ("10_ukazky", "✎", "Ukázky A a B s řešením", "Oba ukázkové testy vyřešené tak, jak je napsat do testu."),
        ("11_cvicne_testy", "✎", "Cvičné testy C–F", "Čtyři nové testy ve stejném formátu, s řešením."),
        ("12_tahak", "★", "Tahák", "Vzorce, idiomy kódu a pasti na jedné stránce."),
        ("99_slovnik", "Aa", "Slovník pojmů (definice)", "Všechny definice z těchto skript na jednom místě."),
    ],
    ALT=dict(
        LANG="en", BRAND="MLR – practical test 1", BRAND_SUB="task types: paper calculations and reading code",
        KICKER="Task type",
        PAGES=[
            ("index", "", "How to prepare", "Test format, map of task types and a study plan."),
            ("01_numpy", "1", "Reading NumPy code", "Shapes, axis, @ and *, masks, argmax, column_stack, rng.choice."),
            ("02_knn", "2", "Distances, k-NN and gradient descent", "Nearest neighbour by hand, voting, one descent step."),
            ("03_metriky", "3", "Confusion matrix and metrics", "TP, FN, FP, TN, accuracy, recall, precision, F1, MSE, MAE."),
            ("04_predzpracovani", "4", "Preprocessing and data leakage", "Standardization, fit on training data only, red flags."),
            ("05_vyber_priznaku", "5", "Feature selection and PCA", "Correlation, entropy and MI by hand, forward selection, PCA."),
            ("06_linearni_regrese", "6", "Linear regression by hand", "Matrix X, normal equation, 2×2 inverse, prediction."),
            ("07_polynom_ridge", "7", "Polynomials, overfitting, ridge and kernels",
             "Polynomial features, under/overfitting, ridge, lasso, dual form and kernels."),
            ("08_stromy_ansambly", "8", "Trees, bagging and SVM", "Tree on paper, Gini, bootstrap, voting, C and gamma."),
            ("09_agenti", "9", "AI agents: skill and subagent", "Terms from lecture and lab 5 in one sentence."),
            ("10_ukazky", "✎", "Samples A and B solved", "Both sample tests solved the way you would write them."),
            ("11_cvicne_testy", "✎", "Practice tests C–F", "Four new tests in the same format, with solutions."),
            ("12_tahak", "★", "Cheat sheet", "Formulas, code idioms and traps on one page."),
            ("99_slovnik", "Aa", "Glossary (definitions)", "All definitions from these notes in one place."),
        ],
    ),
)]


# =====================================================================================================================
# Níže je společný „engine“ – stejný pro všechny předměty, obvykle se nemění.
# =====================================================================================================================
from pathlib import Path
import hashlib
import html
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent          # složka předmětu (např. vmm/)
SRC = Path(__file__).resolve().parent / "obsah"         # fragmenty stránek
SITE = f"https://balnerm.github.io/pripravy/{ROOT.name}/"
KATEX = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist"
ASSET_V = hashlib.md5(b"".join((ROOT / "assets" / f).read_bytes() for f in ("style.css", "app.js"))).hexdigest()[:8]  # změna souboru = nová adresa (obejde cache prohlížeče)
ALL = "skripta_vse"  # stránka se všemi kapitolami za sebou (podklad pro jedno PDF celých skript)

TEXTS = {
    "cs": dict(
        menu="☰ Obsah", menu_aria="Obsah", nav_aria="Navigace", back="Všechny přípravy", theme="Tmavý režim",
        chapters="Kapitoly", on_page="Na této stránce", prev="← předchozí", next="další →", lecture="Přednáška",
        pdf_page="Stáhnout tuto stránku jako PDF", pdf_all="Celá skripta v jednom PDF",
        pdf_print="Vytisknout / uložit jako PDF s nastavenou velikostí písma",
        fs_down="Zmenšit písmo", fs_up="Zvětšit písmo", fs_reset="Původní velikost písma",
        side_label="◧ Panel", side_hide="Skrýt postranní panel", side_show="Zobrazit postranní panel",
        all_title="Celá skripta", all_desc="Všechny kapitoly na jedné stránce (tisková verze).",
        gl_title="Slovník pojmů",
        gl_lead="Všechny definice ze skript na jednom místě, seřazené podle kapitol. Hodí se na rychlé opakování: "
                "zakryj text, řekni definici nahlas a pak si ji zkontroluj. Odkaz „výklad“ vede k místu, kde je pojem "
                "vysvětlen podrobně.",
        gl_link="výklad v kapitole {num} →",
        lang_label="CZ", lang_title="Česká verze"),
    "en": dict(
        menu="☰ Contents", menu_aria="Contents", nav_aria="Navigation", back="All study notes", theme="Dark mode",
        chapters="Chapters", on_page="On this page", prev="← previous", next="next →", lecture="Lecture",
        pdf_page="Download this page as PDF", pdf_all="All notes in one PDF",
        pdf_print="Print / save as PDF with the chosen font size",
        fs_down="Smaller text", fs_up="Larger text", fs_reset="Default text size",
        side_label="◧ Sidebar", side_hide="Hide the sidebar", side_show="Show the sidebar",
        all_title="All notes", all_desc="All chapters on one page (print version).",
        gl_title="Glossary",
        gl_lead="All definitions from the notes in one place, ordered by chapter. Good for quick revision: cover the "
                "text, say the definition out loud, then check it. The link leads to the detailed explanation.",
        gl_link="explained in chapter {num} →",
        lang_label="EN", lang_title="English version"),
}

# Rámeček definice ve fragmentu (do slovníku se převezme automaticky):
#   <div class="box definice" id="def-xyz"><div class="box-t">Definice: pojem</div><p>…</p><p class="jinak">…</p></div>
#   (v angličtině „Definition: term“)
DEF_RE = re.compile(r'<div class="box definice" id="(def-[^"]+)"><div class="box-t">(?:Definice|Definition): (.*?)</div>'
                    r'(.*?)</div>', flags=re.S)


def make_sites():
    """Hlavní verze skript a případně druhá jazyková verze (v podsložce <jazyk>/, sdílí assets/ a figures/)."""
    main = dict(lang=LANG, brand=BRAND, brand_sub=BRAND_SUB, pages=PAGES, src=SRC, out=ROOT, up="",
                fig="figures/", site=SITE)
    sites = [main]
    if ALT:
        lang = ALT["LANG"]
        sites.append(dict(lang=lang, brand=ALT["BRAND"], brand_sub=ALT["BRAND_SUB"], pages=ALT["PAGES"],
                          src=SRC.parent / f"obsah_{lang}", out=ROOT / lang, up="../", fig=f"../figures/{lang}/",
                          site=f"{SITE}{lang}/"))
        main["other"], sites[1]["other"] = sites[1], main
        main["switch"], sites[1]["switch"] = f"{lang}/", "../"
    for e in EDITIONS:
        # samostatná skripta v podsložce <DIR>/, případně s vlastní jazykovou verzí v <DIR>/<jazyk>/
        d = e["DIR"]
        ed = dict(lang=LANG, brand=e["BRAND"], brand_sub=e["BRAND_SUB"], pages=e["PAGES"],
                  src=SRC.parent / f"obsah_{d}", out=ROOT / d, up="../", fig="../figures/",
                  site=f"{SITE}{d}/", tag=f"{d}/", kicker=e.get("KICKER"))
        sites.append(ed)
        a = e.get("ALT")
        if a:
            lang = a["LANG"]
            alt = dict(lang=lang, brand=a["BRAND"], brand_sub=a["BRAND_SUB"], pages=a["PAGES"],
                       src=SRC.parent / f"obsah_{d}_{lang}", out=ROOT / d / lang, up="../../",
                       fig=f"../../figures/{lang}/", site=f"{SITE}{d}/{lang}/", tag=f"{d}/{lang}/",
                       kicker=a.get("KICKER"))
            sites.append(alt)
            ed["other"], alt["other"] = alt, ed
            ed["switch"], alt["switch"] = f"{lang}/", "../"
    for s in sites:
        s["t"] = TEXTS[s["lang"]]
        s.setdefault("tag", f'{s["lang"]}/' if s["up"] else "")
    return sites


SITES = make_sites()


def make_glossary(s):
    """Z rámečků definic ve fragmentech poskládá stránku GLOSSARY (její fragment se generuje, needituje se ručně)."""
    if not GLOSSARY:
        return 0
    T = s["t"]
    parts = [f'<h1>{T["gl_title"]}</h1>', f'<p class="lead">{T["gl_lead"]}</p>']
    count = 0
    for slug, num, title, _ in s["pages"]:
        if not num.isdigit():
            continue
        body = (s["src"] / f"{slug}.html").read_text(encoding="utf-8")
        defs = DEF_RE.findall(body)
        if not defs:
            continue
        parts.append(f'<h2 id="k{num}" class="slovnik-kap">{num} · {title}</h2>')
        for anchor, term, inner in defs:
            count += 1
            parts.append(f'<div class="box definice" id="s-{anchor[4:]}"><div class="box-t">{term}</div>{inner}'
                         f'<p class="slovnik-odkaz"><a href="{slug}.html#{anchor}">{T["gl_link"].format(num=num)}'
                         f'</a></p></div>')
    (s["src"] / f"{GLOSSARY}.html").write_text("\n".join(parts) + "\n", encoding="utf-8")
    return count


TEMPLATE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{alternate}<script>try{{var t=localStorage.getItem("vmm-theme");if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t);var f=parseFloat(localStorage.getItem("vmm-fs"));if(f>=.8&&f<=1.6)document.documentElement.style.setProperty("--fs",f);if(localStorage.getItem("vmm-side")==="0")document.documentElement.classList.add("side-hidden")}}catch(e){{}}</script>
<link rel="stylesheet" href="{katex}/katex.min.css">
<link rel="stylesheet" href="{up}assets/style.css?v={av}">
<script defer src="{katex}/katex.min.js"></script>
<script defer src="{katex}/contrib/auto-render.min.js"></script>
<script defer src="{up}assets/app.js?v={av}"></script>
</head>
<body>
<header class="topbar">
  <button class="iconbtn" id="menuBtn" aria-label="{t[menu_aria]}">{t[menu]}</button>
  <button class="iconbtn" id="sideBtn" type="button" aria-pressed="false" data-hide="{t[side_hide]}" data-show="{t[side_show]}" title="{t[side_hide]}">{t[side_label]}</button>
  <a class="brand" href="index.html">{brand}<small>{brand_sub}</small></a>
  <span class="spacer"></span>
  <a class="iconbtn back" href="{up}../index.html#{short}" title="{t[back]}">←<span> {t[back]}</span></a>
  {langbtn}
  <span class="fsgroup">
    <button class="iconbtn" id="fsDown" type="button" title="{t[fs_down]}" aria-label="{t[fs_down]}">A−</button>
    <button class="iconbtn" id="fsVal" type="button" title="{t[fs_reset]}">100 %</button>
    <button class="iconbtn" id="fsUp" type="button" title="{t[fs_up]}" aria-label="{t[fs_up]}">A+</button>
  </span>
  {pdfbtn}
  <button class="iconbtn" id="themeBtn" type="button">{t[theme]}</button>
</header>
<div class="layout">
<nav class="sidebar" aria-label="{t[nav_aria]}">
  <h4>{t[chapters]}</h4>
  <ol>
{nav}
  </ol>
{toc}
</nav>
<main>
{printhead}
{kicker}
{body}
{pager}
</main>
</div>
</body>
</html>
"""


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def render(s, slug, **kw):
    langbtn = alternate = ""
    if "other" in s:
        o = s["other"]
        href = f'{s["switch"]}{slug}.html'
        langbtn = (f'<a class="iconbtn langbtn" href="{href}" hreflang="{o["lang"]}" lang="{o["lang"]}" '
                   f'title="{o["t"]["lang_title"]}">{o["t"]["lang_label"]}</a>')
        alternate = f'<link rel="alternate" hreflang="{o["lang"]}" href="{href}">\n'
    return TEMPLATE.format(lang=s["lang"], t=s["t"], katex=KATEX, brand=s["brand"], brand_sub=s["brand_sub"],
                           up=s["up"], short=SHORT.lower(), av=ASSET_V, langbtn=langbtn, alternate=alternate, **kw)


def chrome(s, slug, page_title):
    """Tlačítko PDF a tisková hlavička; úvodní stránka odkazuje na PDF celých skript."""
    T = s["t"]
    if slug in ("index", ALL):
        pdf, tip = ALL, T["pdf_all"]
    else:
        pdf, tip = slug, T["pdf_page"]
    pdfbtn = (f'<a class="iconbtn" id="pdfBtn" href="pdf/{pdf}.pdf" download title="{tip}" data-dl="{tip}" '
              f'data-print="{T["pdf_print"]}">PDF</a>')
    printhead = f'<p class="printhead">{s["brand"]} · {html.escape(page_title)} · {s["site"]}{slug}.html</p>'
    return pdfbtn, printhead


def kicker_html(s, num):
    """Štítek nad nadpisem kapitoly („Přednáška 3“; samostatná skripta mohou mít vlastní, např. „Kapitola 3“)."""
    if not num.isdigit():
        return ""
    return f'<p class="kicker">{s.get("kicker") or s["t"]["lecture"]} {num}</p>'


def make_all(s, bodies, nav):
    """Všechny stránky za sebou na jedné stránce: id dostanou předponu kapitoly, odkazy mezi stránkami se
    přepíšou na kotvy, aby fungovaly i uvnitř jednoho PDF."""
    T = s["t"]
    slugs = [x for x, *_ in s["pages"]]

    def pref(x):
        return "k" + (x[:2] if x[:2].isdigit() else "00")

    link_re = re.compile(r'href="(' + "|".join(map(re.escape, slugs)) + r')\.html(?:#([^"]*))?"')
    parts = []
    for slug, num, title, _ in s["pages"]:
        p = pref(slug)
        body = bodies[slug]
        body = re.sub(r'(?<![\w-])id="', f'id="{p}-', body)
        body = body.replace('href="#', f'href="#{p}-').replace("url(#", f"url(#{p}-")
        body = link_re.sub(lambda m: f'href="#{pref(m.group(1))}' + (f'-{m.group(2)}' if m.group(2) else "") + '"',
                           body)
        kicker = kicker_html(s, num)
        parts.append(f'<section class="kapitola" id="{p}">\n{kicker}\n{body}\n</section>')
    page_title = f'{T["all_title"]} – {SHORT}'
    pdfbtn, printhead = chrome(s, ALL, page_title)
    return render(s, ALL, title=page_title, desc=html.escape(f'{SHORT}: {T["all_desc"]}'), nav=nav, toc="",
                  pdfbtn=pdfbtn, printhead=printhead, kicker="", body="\n".join(parts), pager="")


def build_site(s):
    """Sestaví stránky jedné jazykové verze; vrací {slug: html} a počet definic ve slovníku."""
    T, pages = s["t"], s["pages"]
    s["out"].mkdir(parents=True, exist_ok=True)
    built = {}
    bodies = {}
    n_defs = make_glossary(s)
    for i, (slug, num, title, desc) in enumerate(pages):
        src = s["src"] / f"{slug}.html"
        if not src.exists():
            print("chybí fragment:", src)
            continue
        body = src.read_text(encoding="utf-8")
        if s["fig"] != "figures/":
            body = body.replace('src="figures/', f'src="{s["fig"]}')
        bodies[slug] = body
        nav = "\n".join(
            f'    <li><a href="{x}.html"{" class=\"active\"" if x == slug else ""}>'
            f'<span class="n">{n}</span><span>{t}</span></a></li>'
            for x, n, t, _ in pages)
        h2 = re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', body, flags=re.S)
        toc = ""
        if h2 and slug != "index":
            toc = f'  <h4>{T["on_page"]}</h4>\n  <ul class="toc">\n' + "\n".join(
                f'    <li><a href="#{a}">{html.escape(strip_tags(t))}</a></li>' for a, t in h2) + "\n  </ul>"
        prev = pages[i - 1] if i > 0 else None
        nxt = pages[i + 1] if i + 1 < len(pages) else None
        pager = '<nav class="pager">'
        if prev:
            pager += f'<a class="prev" href="{prev[0]}.html"><small>{T["prev"]}</small>{prev[2]}</a>'
        if nxt:
            pager += f'<a class="next" href="{nxt[0]}.html"><small>{T["next"]}</small>{nxt[2]}</a>'
        pager += "</nav>"
        kicker = kicker_html(s, num)
        page_title = f"{title} – {SHORT}" if slug != "index" else s["brand"]
        pdfbtn, printhead = chrome(s, slug, page_title)
        out = render(s, slug, title=page_title, desc=html.escape(desc), nav=nav, toc=toc, pdfbtn=pdfbtn,
                     printhead=printhead, kicker=kicker, body=body, pager=pager)
        (s["out"] / f"{slug}.html").write_text(out, encoding="utf-8")
        built[slug] = out

    nav = "\n".join(f'    <li><a href="{x}.html"><span class="n">{n}</span><span>{t}</span></a></li>'
                    for x, n, t, _ in pages)
    built[ALL] = make_all(s, bodies, nav)
    (s["out"] / f"{ALL}.html").write_text(built[ALL], encoding="utf-8")
    return built, n_defs


def check_site(s, built, errors):
    """Obrázky, odkazy a kotvy, povinné sekce kapitol, formát definic a duplicitní id."""
    lectures = {x for x, n, *_ in s["pages"] if n.isdigit()}
    tag = s["tag"]
    ids = {x: set(re.findall(r'id="([^"]+)"', h)) for x, h in built.items()}
    for slug, h in built.items():
        for src in re.findall(r'<img[^>]+src="([^"]+)"', h):
            if not (s["out"] / src).exists():
                errors.append(f"{tag}{slug}: chybí obrázek {src}")
        for href in re.findall(r'href="([^"#:]*\.html)?(#[^"]*)?"', h):
            f, frag = href
            target = f[:-5] if f else slug
            if f and not (s["out"] / f).exists():
                errors.append(f"{tag}{slug}: odkaz na neexistující {f}")
            elif frag and frag[1:] and target in ids and frag[1:] not in ids[target]:
                errors.append(f"{tag}{slug}: kotva {f}{frag} neexistuje")
        lecture = slug in lectures
        for a in ["shrnuti", "otazky"]:
            if lecture and a not in ids[slug]:
                errors.append(f"{tag}{slug}: chybí sekce #{a}")
        if lecture and "takehome" not in h:
            errors.append(f"{tag}{slug}: chybí take-home messages")
        if lecture and 'class="box definice"' not in h:
            errors.append(f"{tag}{slug}: kapitola nemá žádnou definici")
        if lecture and h.count('class="box definice"') != len(DEF_RE.findall(h)):
            errors.append(f"{tag}{slug}: rámeček definice v nečekaném formátu (nepřevezme se do slovníku)")
        dup = [x for x in re.findall(r'id="([^"]+)"', h) if re.findall(rf'id="{re.escape(x)}"', h).__len__() > 1]
        if dup:
            errors.append(f"{tag}{slug}: duplicitní id {sorted(set(dup))}")
    if "other" in s:
        # obě jazykové verze mají stejné stránky a stejná id, aby přepínač jazyka vedl na totéž místo
        o = s["other"]
        if [x for x, *_ in s["pages"]] != [x for x, *_ in o["pages"]]:
            errors.append(f"{tag}: jiný seznam stránek než ve verzi {o['lang']}")
        for slug, h in built.items():
            other = o["out"] / f"{slug}.html"
            if other.exists():
                missing = ids[slug] - set(re.findall(r'id="([^"]+)"', other.read_text(encoding="utf-8")))
                if missing:
                    errors.append(f"{tag}{slug}: id chybí ve verzi {o['lang']}: {sorted(missing)[:8]}")


DISPLAY_RE = re.compile(r"\\\[(.*?)\\\]", re.S)
INLINE_RE = re.compile(r"\\\((.*?)\\\)", re.S)
REL_RE = re.compile(r"=|\\approx|\\Rightarrow|\\lt|\\gt|\\le|\\ge")
BIG_RE = re.compile(r"\\frac|\\sum|\\sqrt|\\begin|\\int|\\prod|\\max|\\min|\\left")
MATRIX_RE = re.compile(r"\\begin\{[a-z]*matrix\}.*?\\end\{[a-z]*matrix\}", re.S)

def check_math_layout(src, skip=()):
    """Upozornění na nepřehledné vzorce ve zdrojových fragmentech (stejná heuristika jako tools/check_layout.py):
    odstavec s mnoha vzorci za sebou (výpočet má jít po krocích pod sebou) a příliš dlouhý řádek
    samostatného vzorce (víc vzorců za sebou v jednom bloku – rozdělit na řádky / aligned)."""
    warnings = []
    for f in sorted(src.glob("*.html")):
        if f.stem in skip:
            continue
        text = f.read_text(encoding="utf-8")
        line = lambda pos: text.count("\n", 0, pos) + 1
        for m in re.finditer(r"<(p|li)\b[^>]*>(.*?)</\1>", text, re.S):
            maths = INLINE_RE.findall(DISPLAY_RE.sub("", m.group(2)))
            if not maths:
                continue
            # krátké dosazení („R = 1 kΩ“) nevadí; vadí řetěz delších vzorců nebo jeden dlouhý vzorec v textu
            rel = sum(len(REL_RE.findall(x)) for x in maths)
            big = sum(1 for x in maths if len(x) >= 20 or BIG_RE.search(x))
            longest, total = max(map(len, maths)), sum(map(len, maths))
            if (big >= 3 and rel >= 3) or longest >= 75 or total >= 170:
                warnings.append(f"{f.name}:{line(m.start())}: hustý odstavec ({len(maths)} vzorců v textu, "
                                f"{rel}× vztah, nejdelší {longest} zn.) – výpočet rozepiš po krocích pod sebou")
        for m in DISPLAY_RE.finditer(text):
            # přibližná délka řádku: formátovací příkazy (mathbf, frac, text…), závorky a mezery se nepočítají
            rows = re.split(r"\\\\", MATRIX_RE.sub("M", m.group(1)))
            wide = max(len(re.sub(r"[{}\s^_&]|\\[,;!]", "", re.sub(r"\\(mathbf|boldsymbol|text|operatorname|tilde|hat|"
                                                                     r"bar|left|right|big|Big|t?frac|textstyle)\b", "", r)))
                                                                     for r in rows)
            if wide > 90:
                warnings.append(f"{f.name}:{line(m.start())}: dlouhý řádek vzorce (~{wide} zn.) – rozděl na víc řádků")
    return warnings

def build():
    errors = []
    results = [(s, *build_site(s)) for s in SITES]
    for s, built, n_defs in results:
        check_site(s, built, errors)
        where = f" [{s['tag']}]" if s["tag"] else ""
        print(f"sestaveno stránek{where}: {len(built)} (včetně {ALL}.html), definic ve slovníku: {n_defs}")
    if errors:
        print("CHYBY:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("kontrola odkazů, obrázků a povinných sekcí: OK")
    for s in SITES:
        for w in check_math_layout(s["src"], skip={GLOSSARY}):
            print(f"UPOZORNĚNÍ{' [' + s['tag'] + ']' if s['tag'] else ''}: {w}")


if __name__ == "__main__":
    build()
