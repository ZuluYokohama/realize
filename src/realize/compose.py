"""Typed grid composition. IGVF–CTS §7.1. Encoded as term_series / typed_grid."""

from __future__ import annotations

from itertools import product
from typing import Any

Grid = list[list[int]]
Mask = list[list[int]]


def shape(g: Grid) -> tuple[int, int]:
    return len(g), len(g[0]) if g else 0


def support(g: Grid) -> set[tuple[int, int]]:
    return {(i, j) for i, row in enumerate(g) for j, v in enumerate(row) if v != 0}


def extract(x: Grid) -> Mask:
    return [[1 if v != 0 else 0 for v in row] for row in x]


def render2(b: Mask) -> Grid:
    return [[2 if v else 0 for v in row] for row in b]


def histogram(g: Grid) -> dict[int, int]:
    h: dict[int, int] = {}
    for row in g:
        for v in row:
            h[v] = h.get(v, 0) + 1
    return h


def goal_y(x: Grid) -> Grid:
    return [[0 if v == 0 else 2 for v in row] for row in x]


def type_of_prefix(ops: list[str]) -> tuple[str, str] | None:
    """Return (in, out) or None if ill-typed."""
    cur_in, cur_out = "Grid", "Grid"
    first = True
    table = {"Extract": ("Grid", "Mask"), "Render2": ("Mask", "Grid")}
    if not ops:
        return "Grid", "Grid"
    for op in ops:
        if op not in table:
            return None
        pin, pout = table[op]
        if first:
            cur_in, cur_out = pin, pout
            first = False
            continue
        if pin != cur_out:
            return None
        cur_out = pout
    return cur_in, cur_out


def eval_ops(ops: list[str], x: Grid) -> dict[str, Any]:
    ty = type_of_prefix(ops)
    if ty is None:
        return {"ok": False, "reason": "ill_typed"}
    if ty != ("Grid", "Grid"):
        return {"ok": False, "reason": "wrong_type", "type": list(ty)}
    val: Any = x
    for op in ops:
        if op == "Extract":
            val = extract(val)
        elif op == "Render2":
            val = render2(val)
        else:
            return {"ok": False, "reason": "unknown_op", "op": op}
    return {"ok": True, "Y": val}


def satisfies_R(x: Grid, y: Grid) -> bool:
    return y == goal_y(x) and support(y) == support(x)


def satisfies_K(x: Grid, y: Grid, K) -> bool:
    if K is None:
        return True
    if isinstance(K, dict) and K.get("preserve_histogram"):
        return histogram(x) == histogram(y)
    return True


def all_3x3_masks() -> list[Mask]:
    cells = list(product([0, 1], repeat=9))
    out = []
    for bits in cells:
        g = [list(bits[0:3]), list(bits[3:6]), list(bits[6:9])]
        out.append(g)
    return out
