from realize.cert import make_certificate
from realize.spec import load_spec
from realize.verdicts import Verdict


def test_certificate_has_no_generator_field():
    spec = load_spec(
        {
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
            "library": {
                "encoders": [],
                "primitives": [],
                "grammar": "bounded_coeff_template",
            },
            "bound": {"budget": 1},
        }
    )
    cert = make_certificate(spec=spec, verdict=Verdict.UNKNOWN, witness={"reason": "t"})
    blob = str(cert)
    assert "generator" not in blob
    assert cert["checker"]["name"] == "realize.checker"
    assert "synthesize" not in cert
