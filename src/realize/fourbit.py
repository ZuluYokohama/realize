"""Four-bit encoder library. VCOS §8.2. Hidden fixture, not a public demo."""

from __future__ import annotations

from itertools import product

X = list(product([0, 1], repeat=4))  # (x1, x2, x3, x4)


def parity(x: tuple[int, int, int, int]) -> int:
    return x[0] ^ x[1] ^ x[2] ^ x[3]


def encoders() -> list[dict]:
    return [
        {"id": "constant", "fn": lambda x: 0},
        {"id": "parity", "fn": lambda x: parity(x)},
        {"id": "first_bit", "fn": lambda x: x[0]},
        {"id": "hamming", "fn": lambda x: sum(x)},
        {"id": "parity_first", "fn": lambda x: (parity(x), x[0])},
        {"id": "identity", "fn": lambda x: x},
    ]


def task_A(x):
    return (parity(x), x[0])


def task_B(x):
    return x


def R_of(task) -> dict:
    return {x: [task(x)] for x in X}


def code_cardinalities() -> dict[str, int]:
    from realize.kernel import fibres

    out = {}
    for enc in encoders():
        out[enc["id"]] = len(fibres(enc, list(X)))
    return out
