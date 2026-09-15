import pytest

from realize.digest import sha256_hex
from realize.spec import load_spec
from realize.verdicts import AdapterError


def _base():
    return {
        "schema_version": "realize.v0",
        "id": "t",
        "problem_family": "encoder",
        "context": {"semantics": "finite_relation", "X": [0], "Y": [0]},
        "specification": {
            "R": {"0": [0]},
            "K": None,
            "preferences": [],
            "evidence_mode": "exhaustive_finite",
            "provenance": [],
        },
        "library": {
            "encoders": [{"id": "id", "map": {"0": 0}}],
            "primitives": [{"id": "case_table"}],
            "grammar": "finite_case_table",
        },
        "bound": {"budget": 10},
    }


def test_key_order_does_not_change_digest():
    a = load_spec(_base())
    b = load_spec(dict(reversed(list(_base().items()))))
    assert sha256_hex(a) == sha256_hex(b)


def test_float_rejected():
    spec = _base()
    spec["specification"]["R"] = {"0": [0.5]}
    with pytest.raises(AdapterError, match="float"):
        load_spec(spec)
