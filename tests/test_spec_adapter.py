import pytest

from realize.spec import load_candidate, load_spec
from realize.verdicts import AdapterError


def _ok():
    return {
        "schema_version": "realize.v0",
        "id": "t",
        "problem_family": "formula",
        "context": {"semantics": "exact_rational"},
        "specification": {
            "R": {"phrase": "larger"},
            "K": None,
            "preferences": [],
            "evidence_mode": "exhaustive_finite",
            "provenance": [],
        },
        "library": {"encoders": [], "primitives": [], "grammar": "bounded_coeff_template"},
        "bound": {"budget": 1, "affine_only": False},
    }


def test_unknown_family():
    s = _ok()
    s["problem_family"] = "geometry"
    with pytest.raises(AdapterError, match="problem_family"):
        load_spec(s)


def test_semantics_mismatch():
    s = _ok()
    s["context"]["semantics"] = "finite_relation"
    with pytest.raises(AdapterError, match="semantics"):
        load_spec(s)


def test_candidate_with_verdict_rejected():
    with pytest.raises(AdapterError, match="verdict"):
        load_candidate(
            {
                "schema_version": "realize.v0",
                "spec_id": "t",
                "spec_digest": "sha256:" + "0" * 64,
                "term": {"coeffs": ["0", "0", "0", "0"]},
                "verdict": "PASS",
            }
        )


def test_target_nine_with_cap_eight_loads():
    spec = {
        "schema_version": "realize.v0",
        "id": "vcos.reach9",
        "problem_family": "term_series",
        "context": {"semantics": "finite_integer", "q0": 0, "cap": 8, "Y_target": 9},
        "specification": {
            "R": {"target": 9},
            "K": {"invariant": "in_S"},
            "preferences": [],
            "evidence_mode": "exhaustive_finite",
            "provenance": [],
        },
        "library": {
            "encoders": [],
            "primitives": [{"id": "add1"}],
            "grammar": "guarded_integer_sequence",
        },
        "bound": {"budget": 100, "horizon": 4},
    }
    loaded = load_spec(spec)
    assert loaded["specification"]["R"]["target"] == 9
