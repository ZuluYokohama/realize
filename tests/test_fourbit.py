from realize.fourbit import R_of, X, code_cardinalities, encoders, task_A, task_B
from realize.kernel import adequate


def test_192_and_adequacy():
    cards = code_cardinalities()
    assert cards == {
        "constant": 1,
        "parity": 2,
        "first_bit": 2,
        "hamming": 5,
        "parity_first": 4,
        "identity": 16,
    }
    visits = 0
    adequate_A = []
    adequate_B = []
    RA, RB = R_of(task_A), R_of(task_B)
    for enc in encoders():
        for task_name, R, bucket in (("A", RA, adequate_A), ("B", RB, adequate_B)):
            for x in X:
                visits += 1
                enc["fn"](x)  # encoder–input evaluation
            ok, _ = adequate(R, enc, list(X))
            if ok:
                bucket.append(enc["id"])
    assert visits == 192
    assert set(adequate_A) == {"parity_first", "identity"}
    assert adequate_B == ["identity"]


def test_four_state_lower_bound():
    outputs = {task_A(x) for x in X}
    assert len(outputs) == 4
    cards = code_cardinalities()
    assert cards["parity_first"] == 4
