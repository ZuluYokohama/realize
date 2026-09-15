from fractions import Fraction

from realize.checker import check, check_search
from realize.digest import sha256_hex
from realize.formula import all_coeffs, identities_hold, valid_tuples
from realize.spec import load_spec
from realize.verdicts import SCHEMA_VERSION, Verdict


def test_universe_sizes():
    assert len(all_coeffs()) == 625
    assert len(all_coeffs(affine_only=True)) == 125
    assert 4 * len(all_coeffs()) + len(all_coeffs(affine_only=True)) == 2625


def test_table2_one_valid_each():
    for phrase in ("larger", "smaller", "midpoint", "absdiff"):
        v = valid_tuples(phrase)
        assert len(v) == 1, phrase
    assert valid_tuples("larger", affine_only=True) == []


def test_larger_coeffs():
    c = valid_tuples("larger")[0]
    assert c == (Fraction(0), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2))


def _spec(phrase, affine=False):
    return load_spec(
        {
            "schema_version": "realize.v0",
            "id": f"formula.{phrase}",
            "problem_family": "formula",
            "context": {"semantics": "exact_rational"},
            "specification": {
                "R": {"phrase": phrase},
                "K": None,
                "preferences": [],
                "evidence_mode": "exhaustive_finite",
                "provenance": [],
            },
            "library": {
                "encoders": [],
                "primitives": [],
                "grammar": "bounded_coeff_template",
            },
            "bound": {"budget": 10000, "affine_only": affine},
        }
    )


def test_checker_uses_identities_not_probe_label():
    spec = _spec("larger")
    # (0,1,0,0) is `a`, matches larger on a>=b including many probe points but fails b>a.
    cand = {
        "schema_version": SCHEMA_VERSION,
        "spec_id": spec["id"],
        "spec_digest": sha256_hex(spec),
        "term": {"kind": "formula", "coeffs": ["0", "1", "0", "0"]},
    }
    cert = check(spec, cand)
    assert cert["verdict"] == Verdict.COUNTEREXAMPLE.value
    assert identities_hold(["0", "1", "0", "0"], "larger") is False


def test_unrecognized_phrase_unknown():
    spec = _spec("larger")
    spec = load_spec(
        {**spec, "id": "formula.unknown", "specification": {**spec["specification"], "R": {"phrase": "xyz"}}}
    )
    cert = check_search(spec)
    assert cert["verdict"] == Verdict.UNKNOWN.value


def test_affine_unsat():
    spec = _spec("larger", affine=True)
    cert = check_search(spec)
    assert cert["verdict"] == Verdict.UNSAT.value
    assert cert["witness"]["universe"] == 125
