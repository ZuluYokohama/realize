"""Four verdicts and adapter errors. No fifth outcome."""

from enum import Enum

SCHEMA_VERSION = "realize.v0"

class Verdict(str, Enum):
    PASS = "PASS"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"
    UNSAT = "UNSAT"
    UNKNOWN = "UNKNOWN"


class AdapterError(Exception):
    """Malformed spec/candidate. CLI exit 1. Not a verdict."""


class Optimality(str, Enum):
    PROVED = "proved"
    UNRESOLVED = "unresolved"
    NOT_REQUESTED = "not_requested"


PROBLEM_FAMILIES = frozenset({"formula", "encoder", "term_series"})

SEMANTICS = {
    "formula": "exact_rational",
    "encoder": "finite_relation",
    "term_series": "finite_integer",
}

EVIDENCE_MODE = "exhaustive_finite"

GRAMMARS = frozenset(
    {
        "bounded_coeff_template",
        "finite_case_table",
        "guarded_integer_sequence",
        "typed_grid",
    }
)

TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "id",
        "problem_family",
        "context",
        "specification",
        "library",
        "bound",
    }
)

CONTEXT_KEYS = frozenset(
    {
        "semantics",
        "X",
        "Y",
        "q0",
        "cap",
        "alphabet",
        "height",
        "width",
        "types",
        "Y_target",
    }
)

SPEC_KEYS = frozenset({"R", "K", "preferences", "evidence_mode", "provenance"})

LIBRARY_KEYS = frozenset({"encoders", "primitives", "grammar"})

BOUND_KEYS = frozenset(
    {"budget", "max_term_size", "horizon", "affine_only", "max_length"}
)

EXIT = {
    Verdict.PASS: 0,
    "adapter": 1,
    Verdict.COUNTEREXAMPLE: 2,
    Verdict.UNSAT: 3,
    Verdict.UNKNOWN: 4,
}
