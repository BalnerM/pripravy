"""PDF k tisku pro přípravu na test PSO (pso/test/): taháky, tabulky a návod ke kalkulačce.

Spuštění: uv run python pso/test/_gen/make_pdfs.py [název.html …]
Používá Playwright (dev skupina v pyproject.toml). PDF se commitují (Actions je negenerují).
Kontroluje, že obsah taháků a tabulek nepřetéká z A4 stránek (.cols / .page) a že KaTeX nehlásí chybu.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent.parent
DEFAULT = ["tahak.html", "tahak_vzorce.html", "tabulky.html", "kalkulacka.html"]

CHECK = """() => {
  const out = [];
  document.querySelectorAll('.page').forEach((p, i) => {
    const c = p.querySelector('.cols') || p;
    if (c.scrollWidth > c.clientWidth + 2) out.push(`strana ${i + 1}: obsah přetéká do další kolony (${c.scrollWidth} > ${c.clientWidth})`);
    if (p.scrollHeight > p.clientHeight + 2) out.push(`strana ${i + 1}: obsah přetéká dolů`);
  });
  document.querySelectorAll('.katex-error').forEach(e => out.push('KaTeX: ' + e.textContent.slice(0, 80)));
  return out;
}"""


def main(names):
    sys.stdout.reconfigure(encoding="utf-8")
    ok = True
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page()
        for n in names:
            src = HERE / n
            pg.goto(src.as_uri(), wait_until="networkidle")
            pg.wait_for_function("() => !document.querySelector('script[src*=katex]') || document.querySelector('.katex')", timeout=20000)
            pg.evaluate("document.fonts.ready")
            pg.emulate_media(media="print")
            problems = pg.evaluate(CHECK)
            out = src.with_suffix(".pdf")
            pg.pdf(path=str(out), prefer_css_page_size=True, print_background=True)
            print(f"{n} → {out.name}" + ("" if not problems else "  PROBLÉMY: " + "; ".join(problems)))
            ok = ok and not problems
        br.close()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or DEFAULT))
