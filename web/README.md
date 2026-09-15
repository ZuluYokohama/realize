# web/ — public face of realize

This directory is **not** the checker. It cannot mint `PASS`.

A landing page and three worked examples, in plain language, with still-life art. Hash routes. Static HTML/CSS/JS. GitHub Pages source: branch `main`, folder `/web`.

Art in `art/` is generated still-life (inspection bench, keys, paper half-planes, tiles, tags). It is illustration, not evidence.

## Local

```
python3 scripts/serve_web.py
```

Open the site, then Examples → Three keys.

## Fixtures

```
PYTHONPATH=src python3 scripts/export_web_fixtures.py
```


## Local

Serve this folder (any static server). Open `/` then `#/studio/three_state`.

```
python3 -m http.server 8080 --bind 0.0.0.0 --directory web
```

## Fixtures

Certificates are exported from the Python kernel:

```
PYTHONPATH=src python3 scripts/export_web_fixtures.py
```

Do not hand-edit `web/fixtures/*.json` unless you are changing the exporter. The page displays whatever `verdict` the file carries.

## Paste

Paste **certificate** JSON from `realize check` stdout. Specs and candidates are refused with copy to run the kernel locally.

## Pages

Intended URL: https://zuluyokohama.github.io/realize/

Enable once in the GitHub UI (the token used to push cannot call the Pages API):

Settings → Pages → Deploy from a branch → `main` → `/web` → Save.

Asset URLs are relative (`./css/...`) so project Pages works. `.nojekyll` is present.
