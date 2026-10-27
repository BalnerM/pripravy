"""Sestaví HTML stránky skript z fragmentů v _build/obsah/ a zkontroluje odkazy.

Spuštění (z kořene repozitáře pripravy):  python <zkratka>/_build/build.py
Stačí standardní knihovna Pythonu – stejný příkaz spouští i GitHub Actions při nasazení na Pages.
Pro nový předmět se mění jen KONFIGURACE (nahoře), engine pod ní je společný.
"""

# =====================================================================================================================
# KONFIGURACE PŘEDMĚTU  (po zkopírování _sablona/ do <zkratka>/ uprav tento blok)
# =====================================================================================================================
LANG = "cs"                                   # jazyk skript: "cs" nebo "en" (texty rozhraní, <html lang>)
SHORT = "XYZ"                                 # zkratka předmětu (titulky stránek)
BRAND = "XYZ – příprava na zkoušku"           # název v horní liště a tiskové hlavičce (en: "XYZ – exam notes")
BRAND_SUB = "název předmětu, principy a postupy"
GLOSSARY = "99_slovnik"                       # stránka slovníku generovaná z rámečků definic (None = bez slovníku)

# (soubor fragmentu bez .html, číslo přednášky / značka, název, krátký popis)
# Stránky s číselným „číslem“ jsou kapitoly přednášek – musí mít definice, #shrnuti, take-home a #otazky.
PAGES = [
    ("index", "", "Mapa kurzu", "Jak skripta používat a jak spolu témata souvisí."),
    ("01_ukazka", "1", "Ukázková kapitola", "Vzor všech typů rámečků a povinných sekcí."),
    ("99_slovnik", "Aa", "Slovník pojmů (definice)", "Všechny definice ze skript na jednom místě."),
]

# Druhá jazyková verze (volitelné, None = skripta jen v jednom jazyce). Fragmenty jsou v _build/obsah_<jazyk>/
# se stejnými názvy souborů a stejnými id, stránky se sestaví do <zkratka>/<jazyk>/ a na každé stránce je tlačítko,
# které přepne na totéž místo ve druhém jazyce. Obrázky se berou z figures/<jazyk>/. Vzor: mlr/_build/build.py
#   ALT = dict(LANG="en", BRAND="XYZ – exam notes", BRAND_SUB="…", PAGES=[(stejné soubory, přeložené názvy)])
ALT = None


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
        gl_link="výklad v kapitole {num} →",
        lang_label="CZ", lang_title="Česká verze"),
    "en": dict(
        menu="☰ Contents", menu_aria="Contents", nav_aria="Navigation", back="All study notes", theme="Dark mode",
        chapters="Chapters", on_page="On this page", prev="← previous", next="next →", lecture="Lecture",
        pdf_page="Download this page as PDF", pdf_all="All notes in one PDF",
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
    for s in sites:
        s["t"] = TEXTS[s["lang"]]
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
{alternate}<script>try{{var t=localStorage.getItem("vmm-theme");if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
<link rel="stylesheet" href="{katex}/katex.min.css">
<link rel="stylesheet" href="{up}assets/style.css">
<script defer src="{katex}/katex.min.js"></script>
<script defer src="{katex}/contrib/auto-render.min.js"></script>
<script defer src="{up}assets/app.js"></script>
</head>
<body>
<header class="topbar">
  <button class="iconbtn" id="menuBtn" aria-label="{t[menu_aria]}">{t[menu]}</button>
  <a class="brand" href="index.html">{brand}<small>{brand_sub}</small></a>
  <span class="spacer"></span>
  <a class="iconbtn back" href="{up}../index.html#{short}" title="{t[back]}">←<span> {t[back]}</span></a>
  {langbtn}
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
                           up=s["up"], short=SHORT.lower(), langbtn=langbtn, alternate=alternate, **kw)


def chrome(s, slug, page_title):
    """Tlačítko PDF a tisková hlavička; úvodní stránka odkazuje na PDF celých skript."""
    T = s["t"]
    if slug in ("index", ALL):
        pdf, tip = ALL, T["pdf_all"]
    else:
        pdf, tip = slug, T["pdf_page"]
    pdfbtn = f'<a class="iconbtn" href="pdf/{pdf}.pdf" download title="{tip}">PDF</a>'
    printhead = f'<p class="printhead">{s["brand"]} · {html.escape(page_title)} · {s["site"]}{slug}.html</p>'
    return pdfbtn, printhead


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
        kicker = f'<p class="kicker">{T["lecture"]} {num}</p>' if num.isdigit() else ""
        parts.append(f'<section class="kapitola" id="{p}">\n{kicker}\n{body}\n</section>')
    page_title = f'{T["all_title"]} – {SHORT}'
    pdfbtn, printhead = chrome(s, ALL, page_title)
    return render(s, ALL, title=page_title, desc=html.escape(f'{SHORT}: {T["all_desc"]}'), nav=nav, toc="",
                  pdfbtn=pdfbtn, printhead=printhead, kicker="", body="\n".join(parts), pager="")


def build_site(s):
    """Sestaví stránky jedné jazykové verze; vrací {slug: html} a počet definic ve slovníku."""
    T, pages = s["t"], s["pages"]
    s["out"].mkdir(exist_ok=True)
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
        kicker = f'<p class="kicker">{T["lecture"]} {num}</p>' if num.isdigit() else ""
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
    tag = f'{s["lang"]}/' if s["up"] else ""
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


def build():
    errors = []
    results = [(s, *build_site(s)) for s in SITES]
    for s, built, n_defs in results:
        check_site(s, built, errors)
        where = f" [{s['lang']}/]" if s["up"] else ""
        print(f"sestaveno stránek{where}: {len(built)} (včetně {ALL}.html), definic ve slovníku: {n_defs}")
    if errors:
        print("CHYBY:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("kontrola odkazů, obrázků a povinných sekcí: OK")


if __name__ == "__main__":
    build()
