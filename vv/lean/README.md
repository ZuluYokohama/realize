# vv/lean — independent corroboration

Four files. Each re-states the finite facts of one domain in Lean 4, derives from them what verdict
the checker has to report for the specs that ship in that domain, and proves both with
kernel-checked `decide`.

| File | Domain | Facts it settles | Verdicts it derives |
|---|---|---|---|
| `Formula.lean` | `formula.bounded_coeff_template` | the template has 625 members; each phrase is realized by exactly one tuple; the affine sub-template is empty for `larger` | `max_formula`, `formula_affine_only`, `formula_unrecognized_phrase` |
| `Encoder.lean` | `encoder.finite_case_table` | the collapsing encoder's one fibre is obstructed while every pair still meets; the separating encoder is adequate and its decoder is sound; `{0,1,2}` is the one inclusion-minimal obstruction | `three_state`, `encoder_separating`, `encoder_zero_budget` |
| `Series.lean` | `term_series.guarded_integer_sequence` | 121 and 31 syntactic series; ten reach 7 and none in under three steps; the even repertoire and the above-cap target are both empty | `series_seven`, `series_even_repertoire`, `series_target_nine`, `series_zero_budget` |
| `Grid.lean` | `term_series.typed_grid` | `Extract` then `Render2` meets `R`; the empty series does not; the histogram of the input and of the goal differ; 2 of the 31 terms realize `R` | `grid_recolor`, `grid_preserve_histogram`, `grid_zero_budget` |

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
lines reporting what it settled, and `scripts/vv.py` answers the same questions from Python and
compares. A disagreement fails the run, and so does a fact that stops being reported.

The 51 facts come in two bands:

- **the parts** (29, named `formula.*`, `encoder.*`, `series.*`, `grid.*`) — quantities found inside
  a search. Python answers these in `python_facts()`, recomputing from kernel internals. This is the
  band that bites when a frozen count in `tests/test_counts.py` is edited to match a drifting
  kernel; the Python suite cannot catch that, because the suite is the thing that was edited.
- **the effect** (22, named `verdict.*`) — the verdict, optimality and reason the checker has to
  report for a spec file that ships, as `VERDICT/optimality/reason`. Lean works it out from the
  branch order in `realize.checker`, applied to numbers it computed itself. Python answers it in
  `effect_facts()` by running `check_search` on the real spec file and reading the certificate.

The second band is the one that catches a kernel whose parts are each right and whose verdict is
assembled from them wrongly — a mis-ordered branch, a wrong verdict constant, an exhaustive result
reported as unresolved. `vv/domains.json` records outcome and exit status, so a fault that keeps
both and changes only the reason is invisible to it.

Facts are derived, not written down: `series.witness` asks Lean to enumerate and take the shortest
valid series rather than restating a known answer, and `Grid.lean` walks all 31 terms the grammar
can name rather than assuming the two that work. The two sides have to agree about the enumeration
as well as the result.

Every spec that ships is covered: `tests/test_vv.py` fails when a file lands in `vv/specs/` or
`demos/` that no Lean file derives a verdict for.

## Run

```bash
lean Formula.lean          # one file; it checks on exit 0 with only its `fact` lines
                           # on stdout. Any other output is a failure.
python3 ../../scripts/vv.py --lean
```

Toolchain is pinned in `lean-toolchain`. Install with
[elan](https://github.com/leanprover/elan); the whole set checks in about seven seconds.

## What this is not

Lean does not verify the Python kernel, the CLI, the CI, or the papers' mathematics, and **a Lean
file cannot mint a verdict** — nothing here sits on the path that produces a certificate. Deriving
what a verdict *has to be* is not issuing one.

Lean also does not read the spec files. Each spec is transcribed into Lean by hand — `budget 10000`,
`cap 8`, `target 7` — so the comparison catches an edit to one side and not a matching edit to both.

If Lean and Python disagree, the V&V job goes red and one of them is wrong. The job does not say
which. See [../../NONCLAIMS.md](../../NONCLAIMS.md) §10.
