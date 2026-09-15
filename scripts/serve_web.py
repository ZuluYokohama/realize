#!/usr/bin/env python3
"""Local static server for web/. Threaded so the preview poller cannot stall it."""

from __future__ import annotations

import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "web"


def main() -> None:
    os.chdir(ROOT)
    httpd = ThreadingHTTPServer(("0.0.0.0", 8080), SimpleHTTPRequestHandler)
    print(f"serving {ROOT} on 0.0.0.0:8080", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
