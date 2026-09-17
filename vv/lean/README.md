# vv/lean — independent corroboration

Four files. Each re-states the finite facts of one domain in Lean 4 and proves them with
kernel-checked `decide`.

| File | Domain | What it settles |
|---|---|---|
| `Formula.lean` | `formula.bounded_coeff_template` | the template has 625 members; each phrase is realized by exactly one tuple; the affine sub-template is empty for `larger` |
| `Encoder.lean` | `encoder.finite_case_table` | the collapsing encoder's one fibre is obstructed while every pair still meets; the separating encoder is adequate and its decoder is sound |
| `Series.lean` | `term_series.guarded_integer_sequence` | 121 and 31 syntactic series; ten reach 7 and none in under three steps; the even repertoire and the above-cap target are both empty |
| `Grid.lean` | `term_series.typed_grid` | `Extract` then `Render2` meets `R`; the empty series does not; the histogram of the input and of the goal differ |

## Ground rules

Core Lean only. No Mathlib, no `lake`, no network at check time.

**No `native_decide`, no `sorry`, no new `axiom`, no `@[implemented_by]` or `@[extern]`.**
`scripts/vv.py` greps for all of these and refuses the file before `lean` is invoked, because a
file that may assume things corroborates nothing. Lean also warns rather than fails on `sorry`, so
the runner treats any warning as a failure too.

Rationals are carried as halves — every coefficient in `D = {-1, -1/2, 0, 1/2, 1}` is a whole number
of halves, so `h` stands for the value `h/2`. That keeps the arithmetic exact with no rational type.

## Reported facts

Proving something in Lean corroborates nothing on its own — two implementations drift apart quite
happily when nobody compares them. So each file ends with `#eval IO.println "fact <name>=<value>"`
lines reporting the quantities it settled. `scripts/vv.py` recomputes all 29 from the Python kernel
and compares them. A disagreement fails the run, and so does a fact that stops being reported.

This is the check that bites when a frozen count in `tests/test_counts.py` is edited to match a
drifting kernel. The Python suite cannot catch that, because the suite is the thing that was edited.

Facts are derived, not written down: `series.witness` asks Lean to enumerate and take the shortest
valid series rather than restating a known answer, so the two sides have to agree about the
enumeration as well as the result.

## Run

```bash
lean Formula.lean          # one file; exit 0 and no output means it checks
python3 ../../scripts/vv.py --lean
```

Toolchain is pinned in `lean-toolchain`. Install with
[elan](https://github.com/leanprover/elan); the whole set checks in about seven seconds.

## What this is not

Lean does not verify the Python kernel, the CLI, the CI, or the papers' mathematics, and **a Lean
file cannot mint a verdict**. If Lean and Python disagree, the V&V job goes red and one of them is
wrong. The job does not say which. See [../../NONCLAIMS.md](../../NONCLAIMS.md) §10.
