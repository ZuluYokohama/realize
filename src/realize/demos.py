"""Bundled paper demos. Exit ok only if expected verdicts match."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from realize.checker import check, check_search
from realize.digest import sha256_hex
from realize.formula import valid_tuples
from realize.spec import load_spec
from realize.verdicts import SCHEMA_VERSION, AdapterError, Verdict

DEMO_NAMES = ("max_formula", "grid_recolor", "three_state")


def _data_dir() -> Path:
    here = Path(__file__).resolve().parent
    packaged = here / "data"
    if (packaged / "demos").is_dir():
        return packaged / "demos"
    repo = here.parents[1] / "demos"
    if repo.is_dir():
        return repo
    raise AdapterError("demo fixtures are not installed")


def load_demo_spec(name: str) -> dict:
    path = _data_dir() / name / "spec.json"
    if not path.is_file():
        # packaged layout: data/demos/<name>.json
        alt = Path(__file__).resolve().parent / "data" / "demos" / f"{name}.json"
        if alt.is_file():
            return load_spec(alt)
        raise AdapterError(f"demo spec not found: {name}")
    return load_spec(path)


def _expect(actual: dict, verdict: str) -> dict:
    return {
        "expected": verdict,
        "actual": actual["verdict"],
        "match": actual["verdict"] == verdict,
        "certificate": actual,
    }


def run_demo(name: str) -> dict:
    if name == "three_state":
        return _demo_three_state()
    if name == "max_formula":
        return _demo_max_formula()
    if name == "grid_recolor":
        return _demo_grid_recolor()
    raise AdapterError(f"unknown demo {name}")


def _demo_three_state() -> dict:
    spec = load_demo_spec("three_state")
    cert = check_search(spec)
    row = _expect(cert, Verdict.UNSAT.value)
    return {"name": "three_state", "ok": row["match"], "cases": [row]}


def _formula_spec(phrase: str, *, affine_only: bool = False) -> dict:
    base = load_demo_spec("max_formula")
    spec = copy.deepcopy(base)
    spec["id"] = f"vcos.table2.{phrase}" + (".affine" if affine_only else "")
    spec["specification"]["R"] = {"phrase": phrase}
    spec["bound"]["affine_only"] = affine_only
    spec["bound"]["budget"] = 10_000
    return load_spec(spec)


def _demo_max_formula() -> dict:
    cases = []
    expected_ops = {
        "larger": ["0", "1/2", "1/2", "1/2"],
        "smaller": ["0", "1/2", "1/2", "-1/2"],
        "midpoint": ["0", "1/2", "1/2", "0"],
        "absdiff": ["0", "0", "0", "1"],
    }
    for phrase, coeffs in expected_ops.items():
        spec = _formula_spec(phrase)
        cand = {
            "schema_version": SCHEMA_VERSION,
            "spec_id": spec["id"],
            "spec_digest": sha256_hex(spec),
            "term": {"kind": "formula", "coeffs": coeffs},
        }
        cert = check(spec, cand)
        row = _expect(cert, Verdict.PASS.value)
        row["phrase"] = phrase
        row["n_valid"] = len(valid_tuples(phrase))
        cases.append(row)
    spec_aff = _formula_spec("larger", affine_only=True)
    cert_aff = check_search(spec_aff)
    row = _expect(cert_aff, Verdict.UNSAT.value)
    row["phrase"] = "larger_affine"
    row["n_valid"] = len(valid_tuples("larger", affine_only=True))
    cases.append(row)
    # unrecognized phrase
    spec_u = _formula_spec("larger")
    spec_u = copy.deepcopy(spec_u)
    spec_u["specification"]["R"] = {"phrase": "not_a_declared_phrase"}
    spec_u["id"] = "vcos.table2.unknown"
    spec_u = load_spec(spec_u)
    cert_u = check_search(spec_u)
    row_u = _expect(cert_u, Verdict.UNKNOWN.value)
    row_u["phrase"] = "unrecognized"
    cases.append(row_u)
    ok = all(c["match"] for c in cases) and all(
        c.get("n_valid") in (1, None, 0) for c in cases if "n_valid" in c
    )
    # four phrases have 1 valid; affine 0
    ok = (
        cases[0]["n_valid"] == 1
        and cases[1]["n_valid"] == 1
        and cases[2]["n_valid"] == 1
        and cases[3]["n_valid"] == 1
        and cases[4]["n_valid"] == 0
        and all(c["match"] for c in cases)
    )
    return {
        "name": "max_formula",
        "ok": ok,
        "universe": 625,
        "affine_universe": 125,
        "cases": [{k: v for k, v in c.items() if k != "certificate"} | {"verdict": c["actual"]} for c in cases],
        "certificates": [c["certificate"] for c in cases],
    }


def _demo_grid_recolor() -> dict:
    spec = load_demo_spec("grid_recolor")
    cand = {
        "schema_version": SCHEMA_VERSION,
        "spec_id": spec["id"],
        "spec_digest": sha256_hex(spec),
        "term": {"kind": "sequence", "ops": ["Extract", "Render2"]},
    }
    pass_cert = check(spec, cand)
    hist = copy.deepcopy(spec)
    hist["id"] = "igvf.grid_recolor.histogram"
    hist["specification"]["K"] = {"preserve_histogram": True}
    hist = load_spec(hist)
    unsat = check_search(hist)
    empty = {
        "schema_version": SCHEMA_VERSION,
        "spec_id": spec["id"],
        "spec_digest": sha256_hex(spec),
        "term": {"kind": "sequence", "ops": []},
    }
    empty_cert = check(spec, empty)
    cases = [
        _expect(pass_cert, Verdict.PASS.value) | {"label": "recolor"},
        _expect(unsat, Verdict.UNSAT.value) | {"label": "histogram"},
        _expect(empty_cert, Verdict.COUNTEREXAMPLE.value) | {"label": "empty_series"},
    ]
    return {
        "name": "grid_recolor",
        "ok": all(c["match"] for c in cases),
        "cases": cases,
    }


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
