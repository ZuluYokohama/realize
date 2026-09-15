"""Bounded enumerator. Returns candidates only. Never a verdict."""

from __future__ import annotations

from typing import Any

from realize.digest import sha256_hex
from realize.formula import (
    PHRASES,
    all_coeffs,
    coeff_str,
    identities_hold,
    phrase_of,
    probe_counterexample,
)
from realize.kernel import adequate
from realize.spec import load_spec
from realize.verdicts import SCHEMA_VERSION, AdapterError


def _candidate(spec: dict, term: dict, extra: dict | None = None) -> dict:
    doc = {
        "schema_version": SCHEMA_VERSION,
        "spec_id": spec["id"],
        "spec_digest": sha256_hex(spec),
        "term": term,
    }
    if extra:
        doc.update(extra)
    return doc


def synthesize(spec: Any) -> list[dict]:
    return synthesize_with_coverage(spec)["candidates"]


def synthesize_with_coverage(spec: Any) -> dict:
    spec = load_spec(spec)
    budget = spec["bound"].get("budget", None)
    if budget is None:
        raise AdapterError("bound.budget is required for synthesize")
    if budget == 0:
        return {"candidates": [], "exhausted": False, "reason": "zero_budget"}
    family = spec["problem_family"]
    if family == "formula":
        return _syn_formula(spec, budget)
    if family == "encoder":
        return _syn_encoder(spec, budget)
    if family == "term_series":
        g = spec["library"]["grammar"]
        if g == "guarded_integer_sequence":
            return _syn_series(spec, budget)
        if g == "typed_grid":
            return _syn_grid(spec, budget)
        raise AdapterError(f"unknown grammar: {g}")
    raise AdapterError(f"unknown problem_family: {family}")


def _syn_formula(spec: dict, budget: int) -> dict:
    phrase = phrase_of(spec)
    affine = bool(spec["bound"].get("affine_only"))
    universe = all_coeffs(affine_only=affine)
    candidates = []
    examined = 0
    exhausted = True
    if phrase is None or phrase not in PHRASES:
        return {
            "candidates": [],
            "exhausted": True,
            "reason": "unrecognized_phrase",
            "phrase": phrase,
        }
    for c in universe:
        if examined >= budget:
            exhausted = False
            break
        examined += 1
        if probe_counterexample(c, phrase) is not None:
            continue
        if identities_hold(c, phrase):
            candidates.append(_candidate(spec, {"kind": "formula", "coeffs": coeff_str(c)}))
    return {
        "candidates": candidates,
        "exhausted": exhausted,
        "examined": examined,
        "universe": len(universe),
    }


def _syn_encoder(spec: dict, budget: int) -> dict:
    X = spec["context"]["X"]
    Xn = [tuple(x) if isinstance(x, list) else x for x in X]
    R = spec["specification"]["R"]
    candidates = []
    examined = 0
    exhausted = True
    for enc in spec["library"]["encoders"]:
        if examined >= budget:
            exhausted = False
            break
        examined += 1
        ok, info = adequate(R, enc, Xn)
        if ok:
            candidates.append(
                _candidate(
                    spec,
                    {
                        "kind": "case_table",
                        "encoder_id": enc.get("id"),
                        "table": info["decoder"],
                    },
                )
            )
    return {"candidates": candidates, "exhausted": exhausted, "examined": examined}


def _syn_series(spec: dict, budget: int) -> dict:
    from realize.series import classify

    ctx = spec["context"]
    ids = [p["id"] if isinstance(p, dict) else str(p) for p in spec["library"]["primitives"]]
    target = spec["specification"]["R"].get("target", ctx.get("Y_target"))
    horizon = spec["bound"].get("horizon", spec["bound"].get("max_term_size"))
    result = classify(ids, ctx["q0"], ctx["cap"], int(target), int(horizon), budget=budget)
    candidates = [
        _candidate(spec, {"kind": "sequence", "ops": ops}) for ops in result["valid"]
    ]
    return {
        "candidates": candidates,
        "exhausted": result["exhausted"],
        "examined": result["examined"],
        "n_valid": result["n_valid"],
    }


def _syn_grid(spec: dict, budget: int) -> dict:
    from itertools import product as iproduct

    from realize.compose import eval_ops, satisfies_K, satisfies_R

    x = spec["context"]["X"]
    K = spec["specification"]["K"]
    ids = [p["id"] if isinstance(p, dict) else str(p) for p in spec["library"]["primitives"]]
    max_size = spec["bound"].get("max_term_size", 4)
    examined = 0
    exhausted = True
    candidates = []
    for k in range(int(max_size) + 1):
        seqs = [()] if k == 0 else iproduct(ids, repeat=k)
        for seq in seqs:
            if examined >= budget:
                exhausted = False
                break
            examined += 1
            ev = eval_ops(list(seq), x)
            if ev["ok"] and satisfies_R(x, ev["Y"]) and satisfies_K(x, ev["Y"], K):
                candidates.append(
                    _candidate(spec, {"kind": "sequence", "ops": list(seq)})
                )
        if not exhausted:
            break
    return {"candidates": candidates, "exhausted": exhausted, "examined": examined}
