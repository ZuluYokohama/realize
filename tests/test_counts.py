"""Paper coverage counts. Do not change the expected numbers to make tests green."""

from realize.formula import all_coeffs, valid_tuples
from realize.fourbit import X, encoders
from realize.series import classify, syntactic_count


def test_paper_counts_frozen():
    assert len(all_coeffs()) == 625
    assert len(all_coeffs(affine_only=True)) == 125
    assert 4 * 625 + 125 == 2625
    assert all(len(valid_tuples(p)) == 1 for p in ("larger", "smaller", "midpoint", "absdiff"))
    assert valid_tuples("larger", affine_only=True) == []
    assert syntactic_count(3, 4) == 121
    assert syntactic_count(2, 4) == 31
    r = classify(["add1", "add3", "double"], 0, 8, 7, 4)
    assert r["n_valid"] == 10
    assert r["min_len"] == 3
    assert len(list(X)) == 16
    assert len(encoders()) == 6
    assert 6 * 16 * 2 == 192
