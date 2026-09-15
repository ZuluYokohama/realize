"""Independent checker. Must not import the generator."""

from __future__ import annotations

from typing import Any

from realize.cert import make_certificate
from realize.compose import (
    eval_ops,
    goal_y,
    histogram,
    satisfies_K,
    satisfies_R,
)
from realize.digest import sha256_hex
from realize.formula import (
    PHRASES,
    all_coeffs,
    coeff_str,
    identities_hold,
    identity_witness,
    phrase_of,
    probe_counterexample,
)
from realize.kernel import adequate, encode_one, eval_case_table, lookup_R, obstructions
from realize.series import classify, primitives_from_ids, trace
from realize.spec import load_candidate, load_spec
from realize.verdicts import AdapterError, Optimality, Verdict


def check(spec: Any, candidate: Any | None = None) -> dict:
    spec = load_spec(spec)
    if candidate is None:
        return check_search(spec)
    cand = load_candidate(candidate)
    if cand["spec_id"] != spec["id"]:
        raise AdapterError("spec_id does not match spec.id")
    if cand["spec_digest"] != sha256_hex(spec):
        raise AdapterError("spec_digest mismatch")
    family = spec["problem_family"]
    if family == "formula":
        return _check_formula_candidate(spec, cand)
    if family == "encoder":
        return _check_encoder_candidate(spec, cand)
    if family == "term_series":
        grammar = spec["library"]["grammar"]
        if grammar == "typed_grid":
            return _check_grid_candidate(spec, cand)
        if grammar == "guarded_integer_sequence":
            return _check_series_candidate(spec, cand)
        raise AdapterError(f"unknown grammar for term_series: {grammar}")
    raise AdapterError(f"unknown problem_family: {family}")


def check_search(spec: Any) -> dict:
    spec = load_spec(spec)
    budget = spec["bound"].get("budget", None)
    if budget is None:
        raise AdapterError("bound.budget is required for search checking")
    if budget == 0:
        return make_certificate(
            spec=spec,
            verdict=Verdict.UNKNOWN,
            witness={"reason": "zero_budget"},
            optimality=Optimality.UNRESOLVED,
        )
    family = spec["problem_family"]
    if family == "formula":
        return _search_formula(spec)
    if family == "encoder":
        return _search_encoder(spec)
    if family == "term_series":
        grammar = spec["library"]["grammar"]
        if grammar == "typed_grid":
            return _search_grid(spec)
        if grammar == "guarded_integer_sequence":
            return _search_series(spec)
        raise AdapterError(f"unknown grammar for term_series: {grammar}")
    raise AdapterError(f"unknown problem_family: {family}")


def _search_formula(spec: dict) -> dict:
    phrase = phrase_of(spec)
    if phrase is None or phrase not in PHRASES:
        return make_certificate(
            spec=spec,
            verdict=Verdict.UNKNOWN,
            witness={"reason": "unrecognized_phrase", "phrase": phrase},
            optimality=Optimality.UNRESOLVED,
        )
    affine = bool(spec["bound"].get("affine_only"))
    universe = all_coeffs(affine_only=affine)
    budget = spec["bound"]["budget"]
    examined = 0
    valid = []
    exhausted = True
    for c in universe:
        if examined >= budget:
            exhausted = False
            break
        examined += 1
        if identities_hold(c, phrase):
            valid.append(c)
    if not exhausted:
        return make_certificate(
            spec=spec,
            verdict=Verdict.UNKNOWN,
            witness={
                "reason": "incomplete_coverage",
                "examined": examined,
                "universe": len(universe),
                "n_valid_so_far": len(valid),
            },
            optimality=Optimality.UNRESOLVED,
        )
    if not valid:
        return make_certificate(
            spec=spec,
            verdict=Verdict.UNSAT,
            witness={
                "reason": "empty_template",
                "universe": len(universe),
                "examined": examined,
                "affine_only": affine,
                "phrase": phrase,
            },
            optimality=Optimality.PROVED,
        )
    # Exhaustive nonempty: class has realizations; PASS requires a candidate.
    return make_certificate(
        spec=spec,
        verdict=Verdict.UNKNOWN,
        witness={
            "reason": "realizations_exist_supply_a_candidate",
            "n_valid": len(valid),
            "universe": len(universe),
            "example": coeff_str(valid[0]),
        },
        optimality=Optimality.PROVED,
    )


def _check_formula_candidate(spec: dict, cand: dict) -> dict:
    phrase = phrase_of(spec)
    if phrase is None or phrase not in PHRASES:
        return make_certificate(
            spec=spec,
            candidate=cand,
            verdict=Verdict.UNKNOWN,
            witness={"reason": "unrecognized_phrase", "phrase": phrase},
            optimality=Optimality.UNRESOLVED,
        )
    term = cand["term"]
    if term.get("kind") not in (None, "formula") and "coeffs" not in term:
        raise AdapterError("formula term must contain coeffs")
    coeffs = term.get("coeffs")
    if coeffs is None:
        raise AdapterError("formula term.coeffs is required")
    if spec["bound"].get("affine_only"):
        from realize.formula import as_frac

        if as_frac(coeffs[3]) != 0:
            return make_certificate(
                spec=spec,
                candidate=cand,
                verdict=Verdict.COUNTEREXAMPLE,
                witness={"reason": "c3_not_allowed_in_affine_template", "coeffs": coeffs},
            )
    ident = identity_witness(coeffs, phrase)
    if ident["ok"]:
        return make_certificate(
            spec=spec,
            candidate=cand,
            verdict=Verdict.PASS,
            witness=ident,
            optimality=Optimality.NOT_REQUESTED,
        )
    cex = probe_counterexample(coeffs, phrase)
    witness: dict[str, Any] = {"identities": ident, "reason": "identity_failure"}
    if cex is not None:
        a, b, y = cex
        witness["input"] = [str(a), str(b)]
        witness["got"] = str(y)
    return make_certificate(
        spec=spec,
        candidate=cand,
        verdict=Verdict.COUNTEREXAMPLE,
        witness=witness,
    )


def _encoder_by_id(spec: dict, encoder_id: str) -> dict:
    for e in spec["library"]["encoders"]:
        if e.get("id") == encoder_id:
            return e
    raise AdapterError(f"unknown encoder_id: {encoder_id!r}")


def _domain_X(spec: dict) -> list:
    if "X" not in spec["context"]:
        raise AdapterError("context.X is required for encoder problems")
    X = spec["context"]["X"]
    out = []
    for x in X:
        if isinstance(x, list):
            out.append(tuple(x))
        else:
            out.append(x)
    return out


def _search_encoder(spec: dict) -> dict:
    X = _domain_X(spec)
    R = spec["specification"]["R"]
    budget = spec["bound"]["budget"]
    if budget < 1:
        return make_certificate(
            spec=spec,
            verdict=Verdict.UNKNOWN,
            witness={"reason": "zero_budget"},
            optimality=Optimality.UNRESOLVED,
        )
    adequate_ids = []
    for i, enc in enumerate(spec["library"]["encoders"]):
        if i >= budget:
            return make_certificate(
                spec=spec,
                verdict=Verdict.UNKNOWN,
                witness={"reason": "incomplete_coverage", "examined_encoders": i},
                optimality=Optimality.UNRESOLVED,
            )
        ok, _info = adequate(R, enc, X)
        if ok:
            adequate_ids.append(enc.get("id"))
    if not adequate_ids:
        obs = obstructions(R, X, max_size=len(spec["context"].get("Y", X)))
        return make_certificate(
            spec=spec,
            verdict=Verdict.UNSAT,
            witness={
                "reason": "no_adequate_encoder",
                "obstructions": obs,
            },
            optimality=Optimality.PROVED,
        )
    return make_certificate(
        spec=spec,
        verdict=Verdict.UNKNOWN,
        witness={
            "reason": "realizations_exist_supply_a_candidate",
            "adequate_encoders": adequate_ids,
        },
        optimality=Optimality.PROVED,
    )


def _check_encoder_candidate(spec: dict, cand: dict) -> dict:
    X = _domain_X(spec)
    R = spec["specification"]["R"]
    term = cand["term"]
    encoder_id = term.get("encoder_id") or cand.get("encoder_id")
    if not encoder_id:
        raise AdapterError("encoder candidate needs term.encoder_id")
    enc = _encoder_by_id(spec, encoder_id)
    ok, info = adequate(R, enc, X)
    if not ok:
        return make_certificate(
            spec=spec,
            candidate=cand,
            verdict=Verdict.UNSAT,
            witness={"reason": "encoder_inadequate", **info},
            scope={
                "problem_family": "encoder",
                "encoder_family": [encoder_id],
                "grammar": spec["library"]["grammar"],
                "bound": spec["bound"],
                "evidence_mode": spec["specification"]["evidence_mode"],
            },
        )
    table = term.get("table") or info["decoder"]
    for x in X:
        try:
            y = eval_case_table(table, enc, x)
        except KeyError as exc:
            raise AdapterError(str(exc)) from exc
        allowed = lookup_R(R, x)
        y_key = y if not isinstance(y, list) else tuple(y)
        if y_key not in allowed and y not in allowed:
            return make_certificate(
                spec=spec,
                candidate=cand,
                verdict=Verdict.COUNTEREXAMPLE,
                witness={
                    "input": x if not isinstance(x, tuple) else list(x),
                    "got": y,
                    "allowed": [_unf(a) for a in allowed],
                    "code": encode_one(enc, x)
                    if not isinstance(encode_one(enc, x), tuple)
                    else list(encode_one(enc, x)),
                },
            )
    return make_certificate(
        spec=spec,
        candidate=cand,
        verdict=Verdict.PASS,
        witness={"decoder": table, "encoder_id": encoder_id},
    )


def _unf(a):
    if isinstance(a, tuple):
        return list(a)
    return a


def _prim_ids(spec: dict) -> list[str]:
    return [p["id"] if isinstance(p, dict) else str(p) for p in spec["library"]["primitives"]]


def _search_series(spec: dict) -> dict:
    ctx = spec["context"]
    q0 = ctx["q0"]
    cap = ctx["cap"]
    target = spec["specification"]["R"].get("target", ctx.get("Y_target"))
    if target is None:
        raise AdapterError("series spec needs specification.R.target")
    if target > cap or target < 0:
        return make_certificate(
            spec=spec,
            verdict=Verdict.UNSAT,
            witness={
                "reason": "target_outside_invariant",
                "target": target,
                "cap": cap,
            },
            optimality=Optimality.PROVED,
        )
    horizon = spec["bound"].get("horizon", spec["bound"].get("max_term_size"))
    if horizon is None:
        raise AdapterError("bound.horizon is required")
    budget = spec["bound"]["budget"]
    ids = _prim_ids(spec)
    result = classify(ids, q0, cap, int(target), int(horizon), budget=budget)
    if not result["exhausted"]:
        return make_certificate(
            spec=spec,
            verdict=Verdict.UNKNOWN,
            witness={"reason": "incomplete_coverage", **{k: result[k] for k in ("examined", "n_valid")}},
            optimality=Optimality.UNRESOLVED,
        )
    if result["n_valid"] == 0:
        return make_certificate(
            spec=spec,
            verdict=Verdict.UNSAT,
            witness={"reason": "no_valid_sequence", **result},
            optimality=Optimality.PROVED,
        )
    return make_certificate(
        spec=spec,
        verdict=Verdict.UNKNOWN,
        witness={
            "reason": "realizations_exist_supply_a_candidate",
            "n_valid": result["n_valid"],
            "min_len": result["min_len"],
            "example": result["min_seqs"][0] if result["min_seqs"] else None,
            "examined": result["examined"],
        },
        optimality=Optimality.PROVED,
    )


def _check_series_candidate(spec: dict, cand: dict) -> dict:
    ctx = spec["context"]
    q0 = ctx["q0"]
    cap = ctx["cap"]
    target = spec["specification"]["R"].get("target", ctx.get("Y_target"))
    ids = _prim_ids(spec)
    prims = primitives_from_ids(ids)
    ops = cand["term"].get("ops")
    if ops is None:
        raise AdapterError("series term.ops is required")
    for op in ops:
        if op not in prims:
            raise AdapterError(f"unknown op {op!r}")
    tr = trace(ops, q0, cap, prims)
    if not tr["ok"]:
        return make_certificate(
            spec=spec,
            candidate=cand,
            verdict=Verdict.COUNTEREXAMPLE,
            witness=tr,
        )
    if tr["final"] != target:
        return make_certificate(
            spec=spec,
            candidate=cand,
            verdict=Verdict.COUNTEREXAMPLE,
            witness={"input": q0, "got": tr["final"], "expected": target, "states": tr["states"]},
        )
    return make_certificate(
        spec=spec,
        candidate=cand,
        verdict=Verdict.PASS,
        witness={"states": tr["states"], "ops": ops},
    )


def _grid_X(spec: dict) -> list[list[int]]:
    X = spec["context"].get("X")
    if X is None:
        raise AdapterError("grid spec needs context.X")
    return X


def _search_grid(spec: dict) -> dict:
    x = _grid_X(spec)
    K = spec["specification"]["K"]
    if K and isinstance(K, dict) and K.get("preserve_histogram"):
        y = goal_y(x)
        if histogram(x) != histogram(y):
            return make_certificate(
                spec=spec,
                verdict=Verdict.UNSAT,
                witness={
                    "reason": "histogram_contradicts_R",
                    "input_histogram": {str(k): v for k, v in histogram(x).items()},
                    "R_histogram": {str(k): v for k, v in histogram(y).items()},
                },
                optimality=Optimality.PROVED,
            )
    max_size = spec["bound"].get("max_term_size", spec["bound"].get("horizon", 4))
    budget = spec["bound"]["budget"]
    ids = _prim_ids(spec)
    from itertools import product as iproduct

    examined = 0
    valid = []
    exhausted = True
    for k in range(int(max_size) + 1):
        seqs = [()] if k == 0 else iproduct(ids, repeat=k)
        for seq in seqs:
            if examined >= budget:
                exhausted = False
                break
            examined += 1
            ev = eval_ops(list(seq), x)
            if not ev["ok"]:
                continue
            y = ev["Y"]
            if satisfies_R(x, y) and satisfies_K(x, y, K):
                valid.append(list(seq))
        if not exhausted:
            break
    if not exhausted:
        return make_certificate(
            spec=spec,
            verdict=Verdict.UNKNOWN,
            witness={"reason": "incomplete_coverage", "examined": examined, "n_valid": len(valid)},
            optimality=Optimality.UNRESOLVED,
        )
    if not valid:
        return make_certificate(
            spec=spec,
            verdict=Verdict.UNSAT,
            witness={"reason": "no_typed_realization", "examined": examined},
            optimality=Optimality.PROVED,
        )
    return make_certificate(
        spec=spec,
        verdict=Verdict.UNKNOWN,
        witness={
            "reason": "realizations_exist_supply_a_candidate",
            "n_valid": len(valid),
            "example": valid[0],
        },
        optimality=Optimality.PROVED,
    )


def _check_grid_candidate(spec: dict, cand: dict) -> dict:
    x = _grid_X(spec)
    K = spec["specification"]["K"]
    ops = cand["term"].get("ops")
    if ops is None:
        raise AdapterError("grid term.ops is required")
    ev = eval_ops(ops, x)
    if not ev["ok"]:
        return make_certificate(
            spec=spec,
            candidate=cand,
            verdict=Verdict.COUNTEREXAMPLE,
            witness=ev,
        )
    y = ev["Y"]
    if not satisfies_R(x, y):
        return make_certificate(
            spec=spec,
            candidate=cand,
            verdict=Verdict.COUNTEREXAMPLE,
            witness={"input": x, "got": y, "expected": goal_y(x)},
        )
    if not satisfies_K(x, y, K):
        return make_certificate(
            spec=spec,
            candidate=cand,
            verdict=Verdict.COUNTEREXAMPLE,
            witness={"reason": "K_failed", "K": K, "got": y},
        )
    return make_certificate(
        spec=spec,
        candidate=cand,
        verdict=Verdict.PASS,
        witness={"Y": y, "ops": ops},
    )
