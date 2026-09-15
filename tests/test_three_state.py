from realize.checker import check_search
from realize.demos import load_demo_spec
from realize.kernel import adequate, obstructions
from realize.verdicts import Verdict


def test_collapse_all_unsat():
    spec = load_demo_spec("three_state")
    enc = spec["library"]["encoders"][0]
    X = spec["context"]["X"]
    ok, info = adequate(spec["specification"]["R"], enc, X)
    assert ok is False
    assert set(info["inputs"]) == {0, 1, 2}


def test_pairwise_would_pass_but_adequate_fails():
    A = {0: {0, 1}, 1: {1, 2}, 2: {0, 2}}
    assert A[0] & A[1] and A[1] & A[2] and A[0] & A[2]
    assert not (A[0] & A[1] & A[2])


def test_minimal_obstruction_is_all_three():
    spec = load_demo_spec("three_state")
    B = obstructions(spec["specification"]["R"], spec["context"]["X"])
    sets = [set(b) for b in B]
    assert {0, 1, 2} in sets
    assert not any(len(s) < 3 for s in sets)


def test_identity_encoder_pass():
    R = {"0": [0, 1], "1": [1, 2], "2": [0, 2]}
    enc = {"id": "identity", "map": {"0": 0, "1": 1, "2": 2}}
    ok, info = adequate(R, enc, [0, 1, 2])
    assert ok is True
    assert info["decoder"]


def test_search_unsat():
    spec = load_demo_spec("three_state")
    cert = check_search(spec)
    assert cert["verdict"] == Verdict.UNSAT.value
