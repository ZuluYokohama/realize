"""Certificate constructor. Generator name is not a trusted field."""

from __future__ import annotations

from typing import Any

from realize import __version__
from realize.digest import sha256_hex
from realize.spec import load_spec
from realize.verdicts import Optimality, Verdict


def make_certificate(
    *,
    spec: dict,
    verdict: Verdict,
    witness: dict,
    candidate: dict | None = None,
    scope: dict | None = None,
    optimality: Optimality = Optimality.NOT_REQUESTED,
) -> dict:
    spec = load_spec(spec)
    encoder_ids = [
        e.get("id") for e in spec["library"]["encoders"] if isinstance(e, dict) and "id" in e
    ]
    resolved_scope = scope or {
        "problem_family": spec["problem_family"],
        "encoder_family": encoder_ids,
        "grammar": spec["library"]["grammar"],
        "bound": spec["bound"],
        "evidence_mode": spec["specification"]["evidence_mode"],
    }
    cert: dict[str, Any] = {
        "schema_version": spec["schema_version"],
        "spec_id": spec["id"],
        "spec_digest": sha256_hex(spec),
        "verdict": verdict.value if isinstance(verdict, Verdict) else verdict,
        "scope": resolved_scope,
        "witness": witness,
        "optimality": optimality.value if isinstance(optimality, Optimality) else optimality,
        "checker": {"name": "realize.checker", "version": __version__},
    }
    if candidate is not None:
        cert["candidate_digest"] = sha256_hex(candidate)
    return cert
