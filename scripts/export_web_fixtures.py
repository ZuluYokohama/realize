#!/usr/bin/env python3
"""Dev-only: dump demo certificates into web/fixtures. Not part of the pip package."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from realize import __version__
    from realize.demos import load_demo_spec, run_demo
except ModuleNotFoundError:  # a bare checkout, before `pip install -e ".[dev]"`
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from realize import __version__
    from realize.demos import load_demo_spec, run_demo

ROOT = Path(__file__).resolve().parents[1]

OUT = ROOT / "web" / "fixtures"


def write(name: str, obj: dict) -> None:
    """Write one fixture, sorted and newline-terminated so reruns produce no diff."""
    path = OUT / name
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    """Dump every demo certificate the pages display, plus a manifest naming them."""
    OUT.mkdir(parents=True, exist_ok=True)
    files: list[str] = []

    three = run_demo("three_state")
    write("three_state.certificate.json", three["cases"][0]["certificate"])
    files.append("three_state.certificate.json")

    formula = run_demo("max_formula")
    phrase_map = {
        "larger": "max_formula.larger.json",
        "smaller": "max_formula.smaller.json",
        "midpoint": "max_formula.midpoint.json",
        "absdiff": "max_formula.absdiff.json",
        "larger_affine": "max_formula.affine_unsat.json",
        "unrecognized": "max_formula.unknown.json",
    }
    for case, cert in zip(formula["cases"], formula["certificates"], strict=True):
        fname = phrase_map[case["phrase"]]
        write(fname, cert)
        files.append(fname)

    grid = run_demo("grid_recolor")
    gmap = {
        "recolor": "grid_recolor.pass.json",
        "histogram": "grid_recolor.histogram_unsat.json",
        "empty_series": "grid_recolor.empty_counterexample.json",
    }
    for case in grid["cases"]:
        fname = gmap[case["label"]]
        write(fname, case["certificate"])
        files.append(fname)

    spec = load_demo_spec("grid_recolor")
    write("grid_recolor.context.json", {"X": spec["context"]["X"]})
    files.append("grid_recolor.context.json")

    write(
        "manifest.json",
        {
            "generated_by": "scripts/export_web_fixtures.py",
            "realize_version": __version__,
            "files": files,
        },
    )


if __name__ == "__main__":
    main()
