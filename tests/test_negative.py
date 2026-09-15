import copy

import pytest

from realize.checker import check, check_search
from realize.demos import load_demo_spec
from realize.digest import sha256_hex
from realize.spec import load_spec
from realize.verdicts import SCHEMA_VERSION, AdapterError, Verdict


def test_corrupted_coefficients_counterexample():
    spec = load_demo_spec("max_formula")
    cand = {
        "schema_version": SCHEMA_VERSION,
        "spec_id": spec["id"],
        "spec_digest": sha256_hex(spec),
        "term": {"kind": "formula", "coeffs": ["1", "1", "1", "1"]},
    }
    cert = check(spec, cand)
    assert cert["verdict"] == Verdict.COUNTEREXAMPLE.value


def test_digest_mismatch():
    spec = load_demo_spec("max_formula")
    cand = {
        "schema_version": SCHEMA_VERSION,
        "spec_id": spec["id"],
        "spec_digest": "sha256:" + "ab" * 32,
        "term": {"kind": "formula", "coeffs": ["0", "1/2", "1/2", "1/2"]},
    }
    with pytest.raises(AdapterError, match="digest"):
        check(spec, cand)


def test_preference_flip_same_verdict():
    spec = load_demo_spec("three_state")
    a = check_search(spec)
    flipped = copy.deepcopy(spec)
    flipped["specification"]["preferences"] = ["anything"]
    flipped = load_spec(flipped)
    # preferences are not in the digest-relevant acceptance; they ARE in the spec digest.
    # Verdict of search must still be UNSAT.
    b = check_search(flipped)
    assert a["verdict"] == b["verdict"] == Verdict.UNSAT.value


def test_zero_budget_unknown():
    spec = load_demo_spec("three_state")
    spec = copy.deepcopy(spec)
    spec["bound"]["budget"] = 0
    spec = load_spec(spec)
    cert = check_search(spec)
    assert cert["verdict"] == Verdict.UNKNOWN.value
    assert cert["witness"]["reason"] == "zero_budget"


def test_incomplete_coverage_not_unsat():
    spec = load_demo_spec("max_formula")
    spec = copy.deepcopy(spec)
    spec["bound"]["budget"] = 3
    spec = load_spec(spec)
    cert = check_search(spec)
    assert cert["verdict"] == Verdict.UNKNOWN.value
    assert cert["witness"]["reason"] == "incomplete_coverage"


def test_malformed_series_trace_unknown_op():
    spec = {
        "schema_version": "realize.v0",
        "id": "series.bad",
        "problem_family": "term_series",
        "context": {"semantics": "finite_integer", "q0": 0, "cap": 8, "Y_target": 7},
        "specification": {
            "R": {"target": 7},
            "K": None,
            "preferences": [],
            "evidence_mode": "exhaustive_finite",
            "provenance": [],
        },
        "library": {
            "encoders": [],
            "primitives": [{"id": "add1"}],
            "grammar": "guarded_integer_sequence",
        },
        "bound": {"budget": 10, "horizon": 4},
    }
    spec = load_spec(spec)
    cand = {
        "schema_version": SCHEMA_VERSION,
        "spec_id": spec["id"],
        "spec_digest": sha256_hex(spec),
        "term": {"kind": "sequence", "ops": ["not_a_primitive"]},
    }
    with pytest.raises(AdapterError):
        check(spec, cand)
