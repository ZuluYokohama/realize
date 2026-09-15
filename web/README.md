# web/ — verdict theatre

Renderer only. This directory is **not** the checker. It cannot mint `PASS`.

Public face of [`realize`](https://github.com/ZuluYokohama/realize): landing + certificate studio. Hash routes, static HTML/CSS/JS + SVG. GitHub Pages source: branch `main`, folder `/web`.

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
