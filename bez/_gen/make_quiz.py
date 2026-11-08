"""Vygeneruje bez/index.html (procvičovací ABC test MPC-BEZ) z markdownu s otázkami.

Použití:  python bez/_gen/make_quiz.py ["cesta/k/Otázky KT - správné odpovědi.md"]
Výchozí cesta: ../bezpecnost/ vedle repozitáře (soubor do veřejného repa nepatří, data se jen vloží do stránky).
Spouští se ručně; GitHub Actions ho nespouští (není v */_build/).
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DEFAULT_MD = REPO.parent / "bezpecnost" / "Otázky KT - správné odpovědi.md"
OUT = HERE.parent / "index.html"

# Krátké vysvětlení u otázek, jejichž odpověď v přednáškách není doslova (zobrazí se po odpovědi).
NOTES = {
    1: "Poznámka: odpojení při poruše zajistí, aby dotykové napětí na neživých částech nezůstalo nebezpečné (přednáška 5).",
    7: "Poznámka: doplňující pospojování se použije, když v části instalace nelze splnit podmínky automatického odpojení (přednáška 5). S ochranou základní nesouvisí.",
    9: "Poznámka: přednáška uvádí zkráceně „EZ s pohyblivým přívodem musí být při přemísťování odpojena“; výjimka pro zařízení upravená pro přemísťování pod napětím je z NV 101/2005.",
    23: "Poznámka: v přednáškách není; podle ČSN 33 2000 smí být PE holý, musí však být veden společně s fázovými (krajními) vodiči.",
    30: "Poznámka: přednáška 1 uvádí zákaz PPN za deště, bouřky a špatné viditelnosti; ze tří možností vyhovuje jen tato.",
    31: "Poznámka: osoba znalá pro samostatnou činnost (§ 6 NV 194/2022) vykonává činnosti na EZ i v jejich blízkosti samostatně (přednáška 1).",
    34: "Poznámka: osoba znalá pracuje na EZ i v jejich blízkosti samostatně, osoba poučená jen s dohledem (přednáška 1).",
    60: "Poznámka: kryt chránící jen před nahodilým dotykem znamená pořád práci v blízkosti napětí (přednáška 1, osoba poučená). Za práci bez napětí se považuje práce za krytem chránícím před úmyslným dotykem.",
    62: "Poznámka: podle NV 101/2005 zaměstnavatel stanoví termíny, lhůty a rozsah kontrol a revizí na základě hodnocení rizik (přednáška 7).",
}


def parse(md_text):
    body = md_text.split("\n---\n")[0]
    blocks = re.split(r"^## Otázka (\d+)\s*$", body, flags=re.M)
    out = []
    for num, block in zip(blocks[1::2], blocks[2::2]):
        lines = [l for l in block.strip().splitlines() if l.strip()]
        q, opts = lines[0].strip(), lines[1:]
        assert int(num) == len(out) + 1, f"číslování otázek nesedí u {num}"
        assert len(opts) == 3, f"otázka {num}: {len(opts)} možností"
        texts, correct = [], []
        for k, l in enumerate(opts):
            m = re.match(r"^- \[( |x)\] (.+)$", l)
            assert m, f"otázka {num}: špatný řádek možnosti: {l!r}"
            texts.append(m.group(2).strip())
            if m.group(1) == "x":
                correct.append(k)
        assert len(correct) == 1, f"otázka {num}: {len(correct)} správných odpovědí"
        item = {"q": q, "o": texts, "c": correct[0]}
        if int(num) in NOTES:
            item["n"] = NOTES[int(num)]
        out.append(item)
    return out


def main():
    md = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MD
    data = parse(md.read_text(encoding="utf-8"))
    assert len(data) == 62, f"čekáno 62 otázek, nalezeno {len(data)}"
    tpl = (HERE / "quiz_template.html").read_text(encoding="utf-8")
    js = json.dumps(data, ensure_ascii=False, indent=0).replace("</", "<\\/")
    assert tpl.count("/*__DATA__*/") == 1
    OUT.write_text(tpl.replace("/*__DATA__*/", js), encoding="utf-8", newline="\n")
    first = sum(1 for d in data if d["c"] == 0)
    print(f"OK: {len(data)} otázek -> {OUT} (správná první: {first}, poznámek: {sum('n' in d for d in data)})")


if __name__ == "__main__":
    main()
