from realize.checker import check, check_search
from realize.digest import sha256_hex
from realize.series import classify, reachable, syntactic_count
from realize.spec import load_spec
from realize.verdicts import SCHEMA_VERSION, Verdict

P = ["add1", "add3", "double"]
EVEN = ["add2", "double"]


def _spec(target, prims, budget=10000, cap=8, horizon=4):
    return load_spec(
        {
            "schema_version": "realize.v0",
            "id": f"series.{target}.{'-'.join(prims)}",
            "problem_family": "term_series",
            "context": {"semantics": "finite_integer", "q0": 0, "cap": cap, "Y_target": target},
            "specification": {
                "R": {"target": target},
                "K": {"invariant": "in_S"},
                "preferences": ["min_length"],
                "evidence_mode": "exhaustive_finite",
                "provenance": [],
            },
            "library": {
                "encoders": [],
                "primitives": [{"id": p} for p in prims],
                "grammar": "guarded_integer_sequence",
            },
            "bound": {"budget": budget, "horizon": horizon, "max_term_size": horizon},
        }
    )


def test_syntactic_121():
    assert syntactic_count(3, 4) == 121
    result = classify(P, 0, 8, 7, 4)
    assert result["examined"] == 121
    assert result["n_valid"] == 10
    assert result["min_len"] == 3
    assert ["add3", "double", "add1"] in result["min_seqs"]


def test_min_length_independent():
    assert 7 not in reachable(P, 0, 8, 1)
    assert 7 not in reachable(P, 0, 8, 2)
    r1 = reachable(P, 0, 8, 1)
    r2 = reachable(P, 0, 8, 2)
    assert r1 == {0, 1, 3}
    assert r2 == {0, 1, 2, 3, 4, 6}


def test_target_9_unsat():
    spec = _spec(9, P)
    cert = check_search(spec)
    assert cert["verdict"] == Verdict.UNSAT.value
    assert cert["witness"]["reason"] == "target_outside_invariant"


def test_even_repertoire_31_unsat():
    assert syntactic_count(2, 4) == 31
    result = classify(EVEN, 0, 8, 7, 4)
    assert result["examined"] == 31
    assert result["n_valid"] == 0
    spec = _spec(7, EVEN)
    cert = check_search(spec)
    assert cert["verdict"] == Verdict.UNSAT.value


def test_witness_sequence_pass():
    spec = _spec(7, P)
    cand = {
        "schema_version": SCHEMA_VERSION,
        "spec_id": spec["id"],
        "spec_digest": sha256_hex(spec),
        "term": {"kind": "sequence", "ops": ["add3", "double", "add1"]},
    }
    cert = check(spec, cand)
    assert cert["verdict"] == Verdict.PASS.value
    assert cert["witness"]["states"] == [0, 3, 6, 7]
