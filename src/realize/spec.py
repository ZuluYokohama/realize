"""Fail-closed loader for realize.v0 specs and candidates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from realize.digest import canonical_obj, sha256_hex
from realize.verdicts import (
    BOUND_KEYS,
    CONTEXT_KEYS,
    EVIDENCE_MODE,
    GRAMMARS,
    LIBRARY_KEYS,
    PROBLEM_FAMILIES,
    SCHEMA_VERSION,
    SEMANTICS,
    SPEC_KEYS,
    TOP_LEVEL_KEYS,
    AdapterError,
)


def _as_dict(src: Any) -> dict:
    if isinstance(src, dict):
        return json.loads(json.dumps(canonical_obj(src)))
    if isinstance(src, (str, Path)):
        path = Path(src)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise AdapterError(f"cannot read {path}: {exc}") from exc
        try:
            obj = json.loads(text)
        except json.JSONDecodeError as exc:
            raise AdapterError(f"malformed JSON in {path}: {exc}") from exc
        if not isinstance(obj, dict):
            raise AdapterError("document must be a JSON object")
        return json.loads(json.dumps(canonical_obj(obj)))
    raise AdapterError("document must be a dict or a filesystem path")


def _require_keys(obj: dict, required: set[str], label: str) -> None:
    missing = required - set(obj)
    if missing:
        raise AdapterError(f"{label} missing fields: {sorted(missing)}")


def _forbid_unknown(obj: dict, allowed: set[str], label: str) -> None:
    unknown = set(obj) - allowed
    if unknown:
        raise AdapterError(f"{label} unknown fields: {sorted(unknown)}")


def normalize_spec(spec: dict) -> dict:
    """Return canonical JSON-ready copy used for digests."""
    return json.loads(json.dumps(canonical_obj(spec)))


def load_spec(src: Any) -> dict:
    spec = _as_dict(src)
    _forbid_unknown(spec, TOP_LEVEL_KEYS, "spec")
    _require_keys(
        spec,
        {"schema_version", "id", "problem_family", "context", "specification", "library", "bound"},
        "spec",
    )
    if spec["schema_version"] != SCHEMA_VERSION:
        raise AdapterError(f"unsupported schema_version: {spec['schema_version']!r}")
    if not isinstance(spec["id"], str) or not spec["id"]:
        raise AdapterError("id must be a nonempty string")
    family = spec["problem_family"]
    if family not in PROBLEM_FAMILIES:
        raise AdapterError(f"unknown problem_family: {family!r}")
    context = spec["context"]
    if not isinstance(context, dict):
        raise AdapterError("context must be an object")
    _forbid_unknown(context, CONTEXT_KEYS, "context")
    if "semantics" not in context:
        raise AdapterError("context.semantics is required")
    expected = SEMANTICS[family]
    if context["semantics"] != expected:
        raise AdapterError(
            f"context.semantics {context['semantics']!r} does not match family {family} ({expected})"
        )
    specification = spec["specification"]
    if not isinstance(specification, dict):
        raise AdapterError("specification must be an object")
    _forbid_unknown(specification, SPEC_KEYS, "specification")
    _require_keys(specification, set(SPEC_KEYS), "specification")
    if specification["evidence_mode"] != EVIDENCE_MODE:
        raise AdapterError(
            f"unsupported evidence_mode: {specification['evidence_mode']!r}"
        )
    if not isinstance(specification["preferences"], list):
        raise AdapterError("preferences must be a list")
    if not isinstance(specification["provenance"], list):
        raise AdapterError("provenance must be a list")
    library = spec["library"]
    if not isinstance(library, dict):
        raise AdapterError("library must be an object")
    _forbid_unknown(library, LIBRARY_KEYS, "library")
    _require_keys(library, set(LIBRARY_KEYS), "library")
    if library["grammar"] not in GRAMMARS:
        raise AdapterError(f"unknown grammar: {library['grammar']!r}")
    if not isinstance(library["encoders"], list) or not isinstance(library["primitives"], list):
        raise AdapterError("library.encoders and library.primitives must be lists")
    bound = spec["bound"]
    if not isinstance(bound, dict):
        raise AdapterError("bound must be an object")
    _forbid_unknown(bound, BOUND_KEYS, "bound")
    return spec


def load_candidate(src: Any) -> dict:
    cand = _as_dict(src)
    required = {"schema_version", "spec_id", "spec_digest", "term"}
    missing = required - set(cand)
    if missing:
        raise AdapterError(f"candidate missing fields: {sorted(missing)}")
    if cand["schema_version"] != SCHEMA_VERSION:
        raise AdapterError(f"unsupported schema_version: {cand['schema_version']!r}")
    if "verdict" in cand:
        raise AdapterError("candidate must not contain a verdict field")
    if not isinstance(cand["spec_id"], str) or not cand["spec_id"]:
        raise AdapterError("spec_id must be a nonempty string")
    if not isinstance(cand["spec_digest"], str) or not cand["spec_digest"].startswith("sha256:"):
        raise AdapterError("spec_digest must be a sha256: hex string")
    if not isinstance(cand["term"], dict):
        raise AdapterError("term must be an object")
    return cand


def spec_digest(spec: dict) -> str:
    return sha256_hex(load_spec(spec) if "schema_version" in spec else spec)
