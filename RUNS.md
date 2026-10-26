# RUNS – záznam běhů AI agenta

Každý záznam: datum, model, co bylo zadáno, jak se výsledek ověřil. (Starší historie skript VMM je v `../VMM/RUNS.md`.)

| Datum | Model | Co bylo zadáno | Jak se to ověřilo |
|---|---|---|---|
| 2026-10-26 | Opus 5.5 (`claude-opus-5-5`) | Připravit repo tak, aby agent spuštěný v `pripravy` uměl udělat skripta k dalšímu předmětu (i v angličtině): `AGENTS.md`/`CLAUDE.md`, šablona `_sablona/`, obecný `build.py` s konfigurací a jazykem, vlastní uv prostředí. | `vmm`: nový `build.py` dává shodné HTML (jediný rozdíl: popis stránky `skripta_vse`); `uv run python vmm/_build/make_figures.py` v novém prostředí – 29 obrázků, vizuálně beze změny. `_sablona`: grafy, `build.py` i `make_pdf.py` projdou; anglická zkušební kopie (`LANG = "en"`) – texty rozhraní anglicky, screenshot OK. Workflow přeskakuje `_*`. |
