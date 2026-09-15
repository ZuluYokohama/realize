"""Canonical JSON digest. Floats are forbidden in trusted documents."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from typing import Any

from realize.verdicts import AdapterError


def _canon(obj: Any) -> Any:
    if isinstance(obj, bool) or obj is None:
        return obj
    if isinstance(obj, float):
        raise AdapterError("float is not allowed in trusted realize.v0 documents")
    if isinstance(obj, Fraction):
        return f"{obj.numerator}/{obj.denominator}"
    if isinstance(obj, dict):
        return {str(k): _canon(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_canon(v) for v in obj]
    if isinstance(obj, int):
        return obj
    if isinstance(obj, str):
        return obj
    raise AdapterError(f"unsupported type in trusted document: {type(obj).__name__}")


def canonical_obj(obj: Any) -> Any:
    return _canon(obj)


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(
        _canon(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_hex(obj: Any) -> str:
    digest = hashlib.sha256(canonical_bytes(obj)).hexdigest()
    return f"sha256:{digest}"
