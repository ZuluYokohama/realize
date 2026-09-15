"""Bounded coefficient template over exact rationals. VCOS §8.1 / Table 2."""

from __future__ import annotations

from collections.abc import Iterable
from fractions import Fraction
from itertools import product

D: list[Fraction] = [
    Fraction(-1),
    Fraction(-1, 2),
    Fraction(0),
    Fraction(1, 2),
    Fraction(1),
]

PHRASES = frozenset({"larger", "smaller", "midpoint", "absdiff"})
PROBE = tuple(product(range(-2, 3), repeat=2))  # 25 points; generator prune only


def as_frac(v) -> Fraction:
    if isinstance(v, Fraction):
        return v
    if isinstance(v, int) and not isinstance(v, bool):
        return Fraction(v)
    if isinstance(v, str):
        return Fraction(v)
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return Fraction(v[0], v[1])
    raise TypeError(f"cannot parse Fraction from {v!r}")


def parse_coeffs(c) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    vals = [as_frac(x) for x in c]
    if len(vals) != 4:
        raise ValueError("coeffs must have length 4")
    return vals[0], vals[1], vals[2], vals[3]


def eval_formula(c, a, b) -> Fraction:
    c0, c1, c2, c3 = parse_coeffs(c)
    a = as_frac(a)
    b = as_frac(b)
    return c0 + c1 * a + c2 * b + c3 * abs(a - b)


def all_coeffs(*, affine_only: bool = False) -> list[tuple[Fraction, Fraction, Fraction, Fraction]]:
    if affine_only:
        return [(c0, c1, c2, Fraction(0)) for c0, c1, c2 in product(D, repeat=3)]
    return [tuple(c) for c in product(D, repeat=4)]  # type: ignore[misc]


def halfplane_affine(c, plane: str) -> tuple[Fraction, Fraction, Fraction]:
    c0, c1, c2, c3 = parse_coeffs(c)
    if plane == "a_ge_b":
        return c0, c1 + c3, c2 - c3
    if plane == "b_ge_a":
        return c0, c1 - c3, c2 + c3
    raise ValueError(plane)


def target_affine(phrase: str, plane: str) -> tuple[Fraction, Fraction, Fraction]:
    half = Fraction(1, 2)
    if phrase == "larger":
        return (Fraction(0), Fraction(1), Fraction(0)) if plane == "a_ge_b" else (
            Fraction(0),
            Fraction(0),
            Fraction(1),
        )
    if phrase == "smaller":
        return (Fraction(0), Fraction(0), Fraction(1)) if plane == "a_ge_b" else (
            Fraction(0),
            Fraction(1),
            Fraction(0),
        )
    if phrase == "midpoint":
        return Fraction(0), half, half
    if phrase == "absdiff":
        return (Fraction(0), Fraction(1), Fraction(-1)) if plane == "a_ge_b" else (
            Fraction(0),
            Fraction(-1),
            Fraction(1),
        )
    raise KeyError(phrase)


def identities_hold(c, phrase: str) -> bool:
    for plane in ("a_ge_b", "b_ge_a"):
        if halfplane_affine(c, plane) != target_affine(phrase, plane):
            return False
    return True


def identity_witness(c, phrase: str) -> dict:
    planes = {}
    ok = True
    for plane in ("a_ge_b", "b_ge_a"):
        got = halfplane_affine(c, plane)
        want = target_affine(phrase, plane)
        planes[plane] = {
            "got": [str(x) for x in got],
            "want": [str(x) for x in want],
            "match": got == want,
        }
        ok = ok and got == want
    return {"phrase": phrase, "identities": planes, "ok": ok}


def probe_counterexample(c, phrase: str) -> tuple[Fraction, Fraction, Fraction] | None:
    """Search a small grid for a violating input. Checker still uses identities for PASS."""
    for a, b in list(PROBE) + [(3, 1), (1, 3), (5, -2), (-2, 5)]:
        y = eval_formula(c, a, b)
        if not relation_holds(phrase, Fraction(a), Fraction(b), y):
            return Fraction(a), Fraction(b), y
    return None


def relation_holds(phrase: str, a: Fraction, b: Fraction, y: Fraction) -> bool:
    if phrase == "larger":
        return y >= a and y >= b and (y == a or y == b)
    if phrase == "smaller":
        return y <= a and y <= b and (y == a or y == b)
    if phrase == "midpoint":
        return 2 * y == a + b
    if phrase == "absdiff":
        return y >= 0 and y * y == (a - b) * (a - b)
    raise KeyError(phrase)


def valid_tuples(phrase: str, *, affine_only: bool = False) -> list:
    return [c for c in all_coeffs(affine_only=affine_only) if identities_hold(c, phrase)]


def phrase_of(spec: dict) -> str | None:
    R = spec["specification"]["R"]
    if isinstance(R, str):
        return R
    if isinstance(R, dict) and "phrase" in R:
        return R["phrase"]
    if isinstance(R, dict) and "id" in R:
        return R["id"]
    return None


def coeff_str(c: Iterable) -> list[str]:
    return [str(as_frac(x)) for x in c]
