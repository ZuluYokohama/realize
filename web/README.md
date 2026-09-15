# web/ — public face of realize

This directory is **not** the checker. It cannot mint `PASS`.

Landing plus three worked examples. Hash routes. Static HTML/CSS/JS. Art in `art/` is illustration, not evidence.

## Local

```
python3 scripts/serve_web.py
```

Then open the landing and **See a model get this wrong**.

## Fixtures

```
PYTHONPATH=src python3 scripts/export_web_fixtures.py
```

Do not hand-edit `web/fixtures/*.json` unless you are changing the exporter. The page displays whatever `verdict` the file carries.

## Paste

Paste certificate JSON from `realize check` stdout. Specs and candidates are refused.

## Pages

https://zuluyokohama.github.io/realize/ currently **404s** (Pages is not enabled). Until then: [tree/main/web](https://github.com/ZuluYokohama/realize/tree/main/web).

Settings → Pages → Deploy from a branch → `main` → `/web` → Save.

Asset URLs are relative (`./css/...`). `.nojekyll` is present.
