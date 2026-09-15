"""Guarded integer term series. VCOS §8.3."""

from __future__ import annotations

from collections.abc import Callable
from itertools import product


def primitives_from_ids(ids: list[str]) -> dict[str, Callable[[int], int]]:
    table = {
        "add1": lambda q: q + 1,
        "add3": lambda q: q + 3,
        "double": lambda q: 2 * q,
        "add2": lambda q: q + 2,
    }
    out = {}
    for i in ids:
        if i not in table:
            raise KeyError(f"unknown primitive {i!r}")
        out[i] = table[i]
    return out


def syntactic_count(n_prims: int, horizon: int) -> int:
    return sum(n_prims**k for k in range(horizon + 1))


def enumerate_sequences(prim_ids: list[str], horizon: int, budget: int | None = None):
    """Yield sequences including empty, shortest first. Budget counts yielded sequences."""
    used = 0
    for k in range(horizon + 1):
        if k == 0:
            seqs = [()]
        else:
            seqs = product(prim_ids, repeat=k)
        for seq in seqs:
            if budget is not None and used >= budget:
                return
            used += 1
            yield tuple(seq)


def apply_partial(op: Callable[[int], int], q: int, cap: int) -> int | None:
    r = op(q)
    if 0 <= r <= cap:
        return r
    return None


def trace(seq, q0: int, cap: int, prims: dict[str, Callable[[int], int]]) -> dict:
    q = q0
    states = [q]
    for name in seq:
        nxt = apply_partial(prims[name], q, cap)
        if nxt is None:
            return {
                "ok": False,
                "reason": "partial_precondition",
                "states": states,
                "failed_op": name,
            }
        q = nxt
        states.append(q)
        if not (0 <= q <= cap):
            return {"ok": False, "reason": "invariant", "states": states}
    return {"ok": True, "states": states, "final": q}


def reachable(prim_ids: list[str], q0: int, cap: int, steps: int) -> set[int]:
    prims = primitives_from_ids(prim_ids)
    layer = {q0}
    for _ in range(steps):
        nxt: set[int] = set()
        for q in layer:
            for fn in prims.values():
                r = apply_partial(fn, q, cap)
                if r is not None:
                    nxt.add(r)
        layer = nxt
    return layer


def classify(
    prim_ids: list[str],
    q0: int,
    cap: int,
    target: int,
    horizon: int,
    budget: int | None = None,
) -> dict:
    prims = primitives_from_ids(prim_ids)
    valid = []
    examined = 0
    exhausted = True
    for seq in enumerate_sequences(prim_ids, horizon, budget=budget):
        examined += 1
        tr = trace(seq, q0, cap, prims)
        if tr["ok"] and tr["final"] == target:
            valid.append(list(seq))
    expected = syntactic_count(len(prim_ids), horizon)
    if budget is not None and examined < expected:
        exhausted = False
    lengths = [len(s) for s in valid]
    min_len = min(lengths) if lengths else None
    min_seqs = [s for s in valid if len(s) == min_len] if min_len is not None else []
    return {
        "examined": examined,
        "expected_syntactic": expected,
        "exhausted": exhausted,
        "valid": valid,
        "n_valid": len(valid),
        "min_len": min_len,
        "min_seqs": min_seqs,
    }
