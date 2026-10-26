"""Vytvoří PDF ke každé stránce skript a jedno PDF celých skript (headless Chrome) do složky pdf/.

Spuštění (z kořene repozitáře pripravy, po build.py):  python vmm/_build/make_pdf.py
Prohlížeč se hledá v proměnné CHROME, v PATH (google-chrome, chromium…) a ve standardních cestách Windows.
Stránka se otevře s parametrem ?pdf, takže app.js přepne světlý režim a rozbalí odpovědi na otázky.
"""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import ALL, SITES  # noqa: E402


def find_chrome():
    candidates = [os.environ.get("CHROME")]
    candidates += [shutil.which(n) for n in ("google-chrome", "google-chrome-stable", "chromium",
                                             "chromium-browser", "chrome")]
    candidates += [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                   r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
    for c in candidates:
        if c and Path(c).exists():
            return c
    sys.exit("Nenalezen Chrome/Chromium – nastav cestu v proměnné prostředí CHROME.")


def main():
    chrome = find_chrome()
    errors = []
    count = 0
    with tempfile.TemporaryDirectory() as profile:
        for site in SITES:  # každá jazyková verze má vlastní složku pdf/ (en/pdf/ …)
            root, out = site["out"], site["out"] / "pdf"
            out.mkdir(exist_ok=True)
            for name in [s for s, *_ in site["pages"] if s != "index"] + [ALL]:
                dst = out / f"{name}.pdf"
                dst.unlink(missing_ok=True)
                cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                       f"--user-data-dir={profile}", "--virtual-time-budget=20000",
                       f"--print-to-pdf={dst}", (root / f"{name}.html").as_uri() + "?pdf=1"]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
                rel = dst.relative_to(SITES[0]["out"]).as_posix()
                if not dst.exists() or dst.stat().st_size < 20_000:
                    errors.append(rel)
                    continue
                count += 1
                print(f"  {rel}: {dst.stat().st_size // 1024} kB")
    if errors:
        sys.exit(f"PDF se nepodařilo vytvořit: {', '.join(errors)}")
    print(f"PDF hotová: {count} souborů")


if __name__ == "__main__":
    main()
