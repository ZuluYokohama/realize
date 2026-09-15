"""Finite encoder kernel: fibres, adequacy, obstructions, case tables."""

from __future__ import annotations

from collections.abc import Hashable
from itertools import combinations
from typing import Any


def _as_key(x: Any) -> str:
    if isinstance(x, (list, tuple)):
        return "(" + ",".join(_as_key(v) for v in x) + ")"
    return str(x)


def lookup_R(R: dict, x: Any) -> set:
    """Acceptable outputs for input x. R keys may be str or native."""
    for key in (x, _as_key(x), str(x)):
        if key in R:
            return {_freeze(v) for v in R[key]}
    # JSON objects stringify tuple keys poorly; try list-as-json
    if isinstance(x, (list, tuple)):
        alt = list(x)
        if str(alt) in R:
            return {_freeze(v) for v in R[str(alt)]}
    raise KeyError(f"R has no entry for input {x!r}")


def _freeze(v: Any) -> Hashable:
    if isinstance(v, list):
        return tuple(_freeze(x) for x in v)
    return v


def encode_one(encoder: dict, x: Any) -> Hashable:
    if "map" in encoder:
        m = encoder["map"]
        for key in (x, _as_key(x), str(x)):
            if key in m:
                return _freeze(m[key])
        raise KeyError(f"encoder {encoder.get('id')!r} has no image for {x!r}")
    if "fn" in encoder:
        return _freeze(encoder["fn"](x))
    raise ValueError("encoder needs map or fn")


def fibres(encoder: dict, X: list) -> dict[Hashable, list]:
    groups: dict[Hashable, list] = {}
    for x in X:
        code = encode_one(encoder, x)
        groups.setdefault(code, []).append(x)
    return groups


def adequate(R: dict, encoder: dict, X: list) -> tuple[bool, dict]:
    grouped = fibres(encoder, X)
    decoder: dict[str, Any] = {}
    for code, xs in grouped.items():
        sets = [lookup_R(R, x) for x in xs]
        inter = set(sets[0])
        for s in sets[1:]:
            inter &= s
        if not inter:
            return False, {
                "obstruction_fibre": code if not isinstance(code, tuple) else list(code),
                "inputs": xs,
                "sets": [sorted(_unfreeze(v) for v in s) for s in sets],
            }
        pick = min(inter, key=lambda v: _sort_key(v))
        decoder[str(code)] = _unfreeze(pick)
    return True, {"decoder": decoder, "fibres": {str(k): v for k, v in grouped.items()}}


def _unfreeze(v: Any) -> Any:
    if isinstance(v, tuple):
        return [_unfreeze(x) for x in v]
    return v


def _sort_key(v: Any) -> Any:
    if isinstance(v, tuple):
        return tuple(_sort_key(x) for x in v)
    return v


def obstructions(R: dict, X: list, max_size: int | None = None) -> list[list]:
    """Inclusion-minimal B ⊆ X with empty ∩ A(x)."""
    A = {id(x): (x, lookup_R(R, x)) for x in X}
    items = [A[id(x)] for x in X]
    n = len(items)
    limit = n if max_size is None else min(max_size, n)
    found: list[list] = []
    found_sets: list[set[int]] = []
    for k in range(1, limit + 1):
        for combo in combinations(range(n), k):
            idxs = set(combo)
            if any(prev <= idxs for prev in found_sets):
                continue
            inter: set | None = None
            for i in combo:
                s = items[i][1]
                inter = set(s) if inter is None else inter & s
            if not inter:
                found.append([items[i][0] for i in combo])
                found_sets.append(idxs)
    return found


def eval_case_table(table: dict, encoder: dict, x: Any) -> Any:
    code = encode_one(encoder, x)
    for key in (code, str(code), _as_key(code)):
        if key in table:
            return table[key]
    raise KeyError(f"case table has no row for code {code!r}")
