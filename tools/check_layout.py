"""Kontrola vykreslených skript v prohlížeči: přetékání, rozbité obrázky, chybné vzorce, husté odstavce.

Spuštění (z kořene repozitáře pripravy):
    uv run python tools/check_layout.py                    # všechny předměty, lokální soubory
    uv run python tools/check_layout.py --only vmm,mlr     # jen vybrané předměty
    uv run python tools/check_layout.py --base https://balnerm.github.io/pripravy/   # živý web

Používá nainstalovaný Chrome (Playwright, channel="chrome") – nic se nestahuje. Otázky <details> se před
měřením rozbalí. Stránky se kontrolují při šířce 1280 a 500 px. Nenulový exit kód = něco k opravě.
"""
from pathlib import Path
import argparse
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
WIDTHS = [1280, 500]

# Vrací seznam problémů na stránce; stejná heuristika „hustého odstavce“ jako v build.py.
PROBE = r"""() => {
  const out = [];
  const snip = el => (el.innerText || el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 90);
  const where = el => {
    let e = el;
    while (e) {
      let p = e;
      while (p) { if (p.matches && p.matches("h2[id], h3[id], .box[id]")) return "#" + p.id; p = p.previousElementSibling; }
      e = e.parentElement;
    }
    return "";
  };
  const add = (kind, el, extra) => out.push({kind, at: where(el), text: (extra ? extra + " | " : "") + snip(el)});
  const W = window.innerWidth;
  if (document.documentElement.scrollWidth > W + 1)
    out.push({kind: "stránka", at: "", text: `vodorovný scroll celé stránky (${document.documentElement.scrollWidth} > ${W} px)`});
  document.querySelectorAll("img").forEach(img => {
    if (!img.complete || img.naturalWidth === 0) add("obrázek", img, "nenačtený " + img.getAttribute("src"));
  });
  document.querySelectorAll(".katex-error").forEach(el => add("vzorec", el, "chyba KaTeX"));
  // zbylý nevykreslený TeX v textu
  document.querySelectorAll("main p, main li, main td").forEach(el => {
    const t = el.innerText || "";
    if (/\\\(|\\\[/.test(t)) add("vzorec", el, "nevykreslený TeX");
  });
  // široká tabulka / schéma smí mít na úzkém displeji vlastní posuvník (záměr); vzorec nikdy
  document.querySelectorAll("main .katex-display, main table, main .tablewrap, main pre, main figure, main .box, main .schema").forEach(el => {
    if (el.scrollWidth <= el.clientWidth + 1) return;
    const box = el.matches(".tablewrap, .schema") || (el.matches("table") && el.closest(".tablewrap"));
    if (box && el.matches("table")) return;            // hlásí se jednou jako .tablewrap
    add(box && W < 800 ? "posuvník" : "přetéká", el, `${el.className || el.tagName.toLowerCase()} ${el.scrollWidth}>${el.clientWidth}px`);
  });
  const inline = [...document.querySelectorAll("main .katex")].filter(k => !k.closest(".katex-display"));
  inline.forEach(k => {
    const box = k.closest("p, li, td, th, figcaption, .box-t, summary, h1, h2, h3");
    if (!box) return;
    const r = k.getBoundingClientRect(), b = box.getBoundingClientRect();
    if (r.width > 0 && r.right > b.right + 2) add("přetéká", box, `vzorec v textu ${Math.round(r.width)} px`);
  });
  // husté odstavce: hodně vzorců v textu za sebou místo kroků pod sebou
  document.querySelectorAll("main p, main li").forEach(el => {
    if (el.closest(".katex")) return;
    const ks = [...el.querySelectorAll(".katex")].filter(k => !k.closest(".katex-display") && k.closest("p, li") === el);
    if (!ks.length) return;
    const tex = ks.map(k => (k.querySelector("annotation") || {}).textContent || "");
    const eqs = tex.reduce((s, t) => s + (t.match(/=|\\approx|\\Rightarrow|\\lt|\\gt|\\le|\\ge/g) || []).length, 0);
    const big = tex.filter(t => t.length >= 20 || /\\frac|\\sum|\\sqrt|\\begin|\\int|\\prod|\\max|\\min|\\left/.test(t)).length;
    const longest = Math.max(...tex.map(t => t.length));
    const total = tex.reduce((s, t) => s + t.length, 0);
    if ((big >= 3 && eqs >= 3) || longest >= 75 || total >= 170)
      add("hustý", el, `${ks.length} vzorců, ${eqs}× „=“, nejdelší ${longest} zn.`);
  });
  return out;
}"""


def pages(subjects):
    for subj in subjects:
        d = ROOT / subj
        for f in sorted(d.glob("*.html")) + sorted((d / "en").glob("*.html")):
            if f.name != "skripta_vse.html":
                yield f.relative_to(ROOT).as_posix()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="zkratky předmětů oddělené čárkou (výchozí: všechny)")
    ap.add_argument("--base", help="URL webu místo lokálních souborů, např. https://balnerm.github.io/pripravy/")
    ap.add_argument("--pages", default="", help="jen stránky, jejichž cesta obsahuje některý z textů (oddělené čárkou)")
    ap.add_argument("--widths", default=",".join(map(str, WIDTHS)))
    ap.add_argument("--skip", default="posuvník",
                    help="druhy problémů, které nehlásit (výchozí: posuvník = záměrně posuvná tabulka/schéma na mobilu)")
    a = ap.parse_args()
    subjects = a.only.split(",") if a.only else sorted(
        p.parent.name for p in ROOT.glob("*/_build/build.py") if not p.parent.parent.name.startswith("_"))
    skip = set(filter(None, a.skip.split(",")))
    widths = [int(w) for w in a.widths.split(",")]
    problems = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome")
        for w in widths:
            page = browser.new_page(viewport={"width": w, "height": 900})
            for rel in pages(subjects):
                if a.pages and not any(x in rel for x in a.pages.split(",")):
                    continue
                url = (a.base.rstrip("/") + "/" + rel) if a.base else (ROOT / rel).as_uri()
                resp = page.goto(url, wait_until="networkidle")
                if a.base and (resp is None or resp.status >= 400):
                    print(f"{rel} @{w}: HTTP {resp.status if resp else '?'}")
                    problems += 1
                    continue
                page.evaluate("""async () => {
                  document.querySelectorAll("details").forEach(d => d.open = true);
                  const imgs = [...document.querySelectorAll("img")];
                  imgs.forEach(i => i.loading = "eager");
                  await Promise.all(imgs.map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
                }""")
                page.wait_for_timeout(150)
                for p in page.evaluate(PROBE):
                    if p["kind"] in skip:
                        continue
                    problems += 1
                    print(f"{rel} @{w} {p['at']}: [{p['kind']}] {p['text']}")
            page.close()
        browser.close()
    print(f"\nproblémů: {problems}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
