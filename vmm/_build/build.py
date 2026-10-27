"""Sestaví HTML stránky skript z fragmentů v _build/obsah/ a zkontroluje odkazy.

Spuštění (z kořene repozitáře pripravy):  python vmm/_build/build.py
Stačí standardní knihovna Pythonu – stejný příkaz spouští i GitHub Actions při nasazení na Pages.
Pro nový předmět se mění jen KONFIGURACE (nahoře), engine pod ní je společný (viz _sablona/).
"""

# =====================================================================================================================
# KONFIGURACE PŘEDMĚTU
# =====================================================================================================================
LANG = "cs"                                   # jazyk skript: "cs" nebo "en" (texty rozhraní, <html lang>)
SHORT = "VMM"                                 # zkratka předmětu (titulky stránek)
BRAND = "VMM – příprava na zkoušku"           # název v horní liště a tiskové hlavičce
BRAND_SUB = "vícerozměrné metody, principy a postupy"
GLOSSARY = "13_slovnik"                       # stránka slovníku generovaná z rámečků definic (None = bez slovníku)

# (soubor fragmentu bez .html, číslo přednášky / značka, název, krátký popis)
# Stránky s číselným „číslem“ jsou kapitoly přednášek – musí mít definice, #shrnuti, take-home a #otazky.
PAGES = [
    ("index", "", "Mapa kurzu", "Jak skripta používat a jak spolu témata souvisí."),
    ("01_uvod", "1", "Úvod do analýzy vícerozměrných dat",
     "Zdrojová matice, typy dat, proč více proměnných najednou a jak se metody dělí."),
    ("02_vicerozmerne_rozdeleni", "2", "Vícerozměrné rozdělení a testy",
     "Střední vektor, kovarianční matice, normalita, Mahalanobis, χ² diagram, Hotellingův T²."),
    ("03_predzpracovani", "3", "Předzpracování dat",
     "Kódování kategorií, chybějící hodnoty, standardizace a normalizace, transformace."),
    ("04_vztahy", "4", "Vztahy mezi proměnnými",
     "Vizualizace, regrese, korelace, multikolinearita (VIF), ANOVA a Tukey HSD."),
    ("05_shlukova_analyza", "5", "Shluková analýza",
     "Vzdálenosti, hierarchické shlukování, k-means, DBSCAN, počet shluků, validace."),
    ("06_pca", "6", "Analýza hlavních komponent (PCA)",
     "Princip, vlastní čísla a vektory, počet komponent, zátěže, skóre, biplot."),
    ("07_kernel_pca", "7", "Kernel PCA",
     "Limity lineární PCA, jádrový trik, polynomiální a RBF jádro."),
    ("08_maticove_rozklady", "8", "Maticové rozklady: ED a SVD",
     "Spektrální a singulární rozklad, jejich vztah a proč se v praxi používá SVD."),
    ("09_faktorova_analyza", "9", "Faktorová analýza",
     "Skryté faktory, komunalita, odhad zátěží, rotace (varimax, oblimin), PCA vs. FA."),
    ("10_tsne", "10", "t-SNE",
     "Varietní učení, podobnosti jako pravděpodobnosti, perplexita, KL divergence, úskalí."),
    ("11_umap", "11", "UMAP",
     "Topologický přístup, graf sousedů, hyperparametry, srovnání s t-SNE."),
    ("12_srovnani", "★", "Srovnání metod a tahák",
     "Kdy použít kterou metodu, srovnávací tabulky, rozhodovací schéma."),
    ("13_slovnik", "Aa", "Slovník pojmů (definice)",
     "Všechny definice ze skript na jednom místě, seřazené podle kapitol."),
]


# =====================================================================================================================
# Níže je společný „engine“ – stejný pro všechny předměty, obvykle se nemění.
# =====================================================================================================================
from pathlib import Path
import html
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent          # složka předmětu (např. vmm/)
SRC = Path(__file__).resolve().parent / "obsah"         # fragmenty stránek
SITE = f"https://balnerm.github.io/pripravy/{ROOT.name}/"
KATEX = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist"
ALL = "skripta_vse"  # stránka se všemi kapitolami za sebou (podklad pro jedno PDF celých skript)

TEXTS = {
    "cs": dict(
        menu="☰ Obsah", menu_aria="Obsah", nav_aria="Navigace", back="Všechny přípravy", theme="Tmavý režim",
        chapters="Kapitoly", on_page="Na této stránce", prev="← předchozí", next="další →", lecture="Přednáška",
        pdf_page="Stáhnout tuto stránku jako PDF", pdf_all="Celá skripta v jednom PDF",
        all_title="Celá skripta", all_desc="Všechny kapitoly na jedné stránce (tisková verze).",
        gl_title="Slovník pojmů",
        gl_lead="Všechny definice ze skript na jednom místě, seřazené podle kapitol. Hodí se na rychlé opakování: "
                "zakryj text, řekni definici nahlas a pak si ji zkontroluj. Odkaz „výklad“ vede k místu, kde je pojem "
                "vysvětlen podrobně.",
        gl_link="výklad v kapitole {num} →"),
    "en": dict(
        menu="☰ Contents", menu_aria="Contents", nav_aria="Navigation", back="All study notes", theme="Dark mode",
        chapters="Chapters", on_page="On this page", prev="← previous", next="next →", lecture="Lecture",
        pdf_page="Download this page as PDF", pdf_all="All notes in one PDF",
        all_title="All notes", all_desc="All chapters on one page (print version).",
        gl_title="Glossary",
        gl_lead="All definitions from the notes in one place, ordered by chapter. Good for quick revision: cover the "
                "text, say the definition out loud, then check it. The link leads to the detailed explanation.",
        gl_link="explained in chapter {num} →"),
}
T = TEXTS[LANG]

# Rámeček definice ve fragmentu (do slovníku se převezme automaticky):
#   <div class="box definice" id="def-xyz"><div class="box-t">Definice: pojem</div><p>…</p><p class="jinak">…</p></div>
#   (v angličtině „Definition: term“)
DEF_RE = re.compile(r'<div class="box definice" id="(def-[^"]+)"><div class="box-t">(?:Definice|Definition): (.*?)</div>'
                    r'(.*?)</div>', flags=re.S)


def make_glossary():
    """Z rámečků definic ve fragmentech poskládá stránku GLOSSARY (její fragment se generuje, needituje se ručně)."""
    if not GLOSSARY:
        return 0
    parts = [f'<h1>{T["gl_title"]}</h1>', f'<p class="lead">{T["gl_lead"]}</p>']
    count = 0
    for slug, num, title, _ in PAGES:
        if not num.isdigit():
            continue
        body = (SRC / f"{slug}.html").read_text(encoding="utf-8")
        defs = DEF_RE.findall(body)
        if not defs:
            continue
        parts.append(f'<h2 id="k{num}" class="slovnik-kap">{num} · {title}</h2>')
        for anchor, term, inner in defs:
            count += 1
            parts.append(f'<div class="box definice" id="s-{anchor[4:]}"><div class="box-t">{term}</div>{inner}'
                         f'<p class="slovnik-odkaz"><a href="{slug}.html#{anchor}">{T["gl_link"].format(num=num)}'
                         f'</a></p></div>')
    (SRC / f"{GLOSSARY}.html").write_text("\n".join(parts) + "\n", encoding="utf-8")
    return count


TEMPLATE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<script>try{{var t=localStorage.getItem("vmm-theme");if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
<link rel="stylesheet" href="{katex}/katex.min.css">
<link rel="stylesheet" href="assets/style.css">
<script defer src="{katex}/katex.min.js"></script>
<script defer src="{katex}/contrib/auto-render.min.js"></script>
<script defer src="assets/app.js"></script>
</head>
<body>
<header class="topbar">
  <button class="iconbtn" id="menuBtn" aria-label="{t[menu_aria]}">{t[menu]}</button>
  <a class="brand" href="index.html">{brand}<small>{brand_sub}</small></a>
  <span class="spacer"></span>
  <a class="iconbtn back" href="../index.html#{short}" title="{t[back]}">←<span> {t[back]}</span></a>
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


def render(**kw):
    return TEMPLATE.format(lang=LANG, t=T, katex=KATEX, brand=BRAND, brand_sub=BRAND_SUB, short=SHORT.lower(), **kw)


def chrome(slug, page_title):
    """Tlačítko PDF a tisková hlavička; úvodní stránka odkazuje na PDF celých skript."""
    if slug in ("index", ALL):
        pdf, tip = ALL, T["pdf_all"]
    else:
        pdf, tip = slug, T["pdf_page"]
    pdfbtn = f'<a class="iconbtn" href="pdf/{pdf}.pdf" download title="{tip}">PDF</a>'
    printhead = f'<p class="printhead">{BRAND} · {html.escape(page_title)} · {SITE}{slug}.html</p>'
    return pdfbtn, printhead


def make_all(bodies, nav):
    """Všechny stránky za sebou na jedné stránce: id dostanou předponu kapitoly, odkazy mezi stránkami se
    přepíšou na kotvy, aby fungovaly i uvnitř jednoho PDF."""
    slugs = [s for s, *_ in PAGES]

    def pref(s):
        return "k" + (s[:2] if s[:2].isdigit() else "00")

    link_re = re.compile(r'href="(' + "|".join(map(re.escape, slugs)) + r')\.html(?:#([^"]*))?"')
    parts = []
    for slug, num, title, _ in PAGES:
        p = pref(slug)
        body = bodies[slug]
        body = re.sub(r'(?<![\w-])id="', f'id="{p}-', body)
        body = body.replace('href="#', f'href="#{p}-').replace("url(#", f"url(#{p}-")
        body = link_re.sub(lambda m: f'href="#{pref(m.group(1))}' + (f'-{m.group(2)}' if m.group(2) else "") + '"',
                           body)
        kicker = f'<p class="kicker">{T["lecture"]} {num}</p>' if num.isdigit() else ""
        parts.append(f'<section class="kapitola" id="{p}">\n{kicker}\n{body}\n</section>')
    page_title = f'{T["all_title"]} – {SHORT}'
    pdfbtn, printhead = chrome(ALL, page_title)
    return render(title=page_title, desc=html.escape(f'{SHORT}: {T["all_desc"]}'), nav=nav, toc="", pdfbtn=pdfbtn,
                  printhead=printhead, kicker="", body="\n".join(parts), pager="")


def build():
    errors = []
    built = {}
    bodies = {}
    n_defs = make_glossary()
    for i, (slug, num, title, desc) in enumerate(PAGES):
        src = SRC / f"{slug}.html"
        if not src.exists():
            print("chybí fragment:", src.name)
            continue
        body = src.read_text(encoding="utf-8")
        bodies[slug] = body
        nav = "\n".join(
            f'    <li><a href="{s}.html"{" class=\"active\"" if s == slug else ""}>'
            f'<span class="n">{n}</span><span>{t}</span></a></li>'
            for s, n, t, _ in PAGES)
        h2 = re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', body, flags=re.S)
        toc = ""
        if h2 and slug != "index":
            toc = f'  <h4>{T["on_page"]}</h4>\n  <ul class="toc">\n' + "\n".join(
                f'    <li><a href="#{a}">{html.escape(strip_tags(t))}</a></li>' for a, t in h2) + "\n  </ul>"
        prev = PAGES[i - 1] if i > 0 else None
        nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
        pager = '<nav class="pager">'
        if prev:
            pager += f'<a class="prev" href="{prev[0]}.html"><small>{T["prev"]}</small>{prev[2]}</a>'
        if nxt:
            pager += f'<a class="next" href="{nxt[0]}.html"><small>{T["next"]}</small>{nxt[2]}</a>'
        pager += "</nav>"
        kicker = f'<p class="kicker">{T["lecture"]} {num}</p>' if num.isdigit() else ""
        page_title = f"{title} – {SHORT}" if slug != "index" else BRAND
        pdfbtn, printhead = chrome(slug, page_title)
        out = render(title=page_title, desc=html.escape(desc), nav=nav, toc=toc, pdfbtn=pdfbtn,
                     printhead=printhead, kicker=kicker, body=body, pager=pager)
        (ROOT / f"{slug}.html").write_text(out, encoding="utf-8")
        built[slug] = out

    nav = "\n".join(f'    <li><a href="{s}.html"><span class="n">{n}</span><span>{t}</span></a></li>'
                    for s, n, t, _ in PAGES)
    built[ALL] = make_all(bodies, nav)
    (ROOT / f"{ALL}.html").write_text(built[ALL], encoding="utf-8")

    # ---- kontroly ----
    lectures = {s for s, n, *_ in PAGES if n.isdigit()}
    ids = {s: set(re.findall(r'id="([^"]+)"', h)) for s, h in built.items()}
    for slug, h in built.items():
        for src in re.findall(r'<img[^>]+src="([^"]+)"', h):
            if not (ROOT / src).exists():
                errors.append(f"{slug}: chybí obrázek {src}")
        for href in re.findall(r'href="([^"#:]*\.html)?(#[^"]*)?"', h):
            f, frag = href
            target = f[:-5] if f else slug
            if f and not (ROOT / f).exists():
                errors.append(f"{slug}: odkaz na neexistující {f}")
            elif frag and frag[1:] and target in ids and frag[1:] not in ids[target]:
                errors.append(f"{slug}: kotva {f}{frag} neexistuje")
        lecture = slug in lectures
        for a in ["shrnuti", "otazky"]:
            if lecture and a not in ids[slug]:
                errors.append(f"{slug}: chybí sekce #{a}")
        if lecture and "takehome" not in h:
            errors.append(f"{slug}: chybí take-home messages")
        if lecture and 'class="box definice"' not in h:
            errors.append(f"{slug}: kapitola nemá žádnou definici")
        if lecture and h.count('class="box definice"') != len(DEF_RE.findall(h)):
            errors.append(f"{slug}: rámeček definice v nečekaném formátu (nepřevezme se do slovníku)")
        dup = [x for x in re.findall(r'id="([^"]+)"', h) if re.findall(rf'id="{re.escape(x)}"', h).__len__() > 1]
        if dup:
            errors.append(f"{slug}: duplicitní id {sorted(set(dup))}")
    print(f"sestaveno stránek: {len(built)} (včetně {ALL}.html), definic ve slovníku: {n_defs}")
    if errors:
        print("CHYBY:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("kontrola odkazů, obrázků a povinných sekcí: OK")


if __name__ == "__main__":
    build()
