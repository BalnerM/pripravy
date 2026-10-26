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
from build import ALL, PAGES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pdf"


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
    OUT.mkdir(exist_ok=True)
    names = [s for s, *_ in PAGES if s != "index"] + [ALL]
    errors = []
    with tempfile.TemporaryDirectory() as profile:
        for name in names:
            dst = OUT / f"{name}.pdf"
            dst.unlink(missing_ok=True)
            cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                   f"--user-data-dir={profile}", "--virtual-time-budget=20000",
                   f"--print-to-pdf={dst}", (ROOT / f"{name}.html").as_uri() + "?pdf=1"]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
            if not dst.exists() or dst.stat().st_size < 20_000:
                errors.append(name)
                continue
            print(f"  {dst.name}: {dst.stat().st_size // 1024} kB")
    if errors:
        sys.exit(f"PDF se nepodařilo vytvořit: {', '.join(errors)}")
    print(f"PDF hotová: {len(names)} souborů v {OUT.name}/")


if __name__ == "__main__":
    main()
