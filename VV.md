# Verification & validation

This file says what the repository now runs across every domain it declares, and — more
carefully — what that still does not establish.

Read [NONCLAIMS.md](NONCLAIMS.md) first. Nothing here adds a claim that file denies.

## Two questions wearing one abbreviation

V&V is one abbreviation for two questions that are easy to run together (IEEE 1012, DO-178C):

| | Academic name | The question | Said with the simplest words |
|---|---|---|---|
| **V₁** | Verification | Did we build the thing right? | Someone said what this thing must do. This thing does that. |
| **V₂** | Validation | Did we build the right thing? | Someone wanted something. The words say the same as what this someone wanted. |

`realize check` is **verification**, and always was. A certificate says: at this declared finite
scope, under these bounds, this candidate does what `R` and `K` say.

**Validation is the harder one, and this package cannot discharge it.** NONCLAIMS §7 already says
so: separating the generator from the checker does not certify "that a formal `R` matches anyone's
linguistic intention." No amount of green CI closes that gap. What *can* be configured is the
discipline that makes the gap visible instead of invisible — every clause that constrains must say
where it came from, and every certificate must carry the boundary its claim is good inside. That is
what the `provenance` and `scope_completeness` objectives below do. They are not validation. They
are the bookkeeping that keeps someone from mistaking verification for it.

## The vocabulary, in the simplest words

| Academic concept | Where it lives here | Said simply |
|---|---|---|
| Verification (IEEE 1012) | `realize check` | the thing does what the words say |
| Validation (IEEE 1012) | not dischargeable; only provenance and scope | the words say what someone wanted |
| The oracle problem | the spec is the oracle; the model is not | something else has to say what is true, and it cannot be the one that made the thing |
| Separation of duties | `tests/test_isolation.py`; `synthesize_emits_no_verdict` | the one who makes a thing is not the one who says it is good |
| N-version / dissimilar redundancy (DO-178C) | [`vv/lean/`](vv/lean/) | two different ones do the same work apart; then you see if they say the same |
| Soundness | `PASS` is scoped, never global | when it says yes, it is true |
| Refusal of completeness | `UNKNOWN` is required (NONCLAIMS §2) | when it cannot know, it says so |
| Falsification (Popper) | `COUNTEREXAMPLE` | one thing is enough to show it is not true |
| Bounded / scoped model checking | `evidence_mode: exhaustive_finite` plus `bound` | it looked at all of a small part, not at everything |
| Trusted computing base | Lean kernel `decide` only; no `native_decide` | how much you must believe before you can believe the rest |
| Provenance / audit trail | `specification.provenance` | someone can see where these words came from |
| Tamper evidence | `spec_digest` binding | if someone changes the words, you can see it |

## Domains

A domain is a `problem_family` paired with a `grammar` — the axis the kernel already dispatches on.
Four are declared in [`vv/domains.json`](vv/domains.json):

| Domain | Semantics | Source |
|---|---|---|
| `formula.bounded_coeff_template` | `exact_rational` | VCOS §8.1 / Table 2 |
| `encoder.finite_case_table` | `finite_relation` | VCMS Example 4.3 |
| `term_series.typed_grid` | `finite_integer` | IGVF–CTS §7.1 |
| `term_series.guarded_integer_sequence` | `finite_integer` | VCOS §8.3 |

The last one was declared in `schema/realize.v0.json` and dispatched in `realize/checker.py`, and
until now shipped no spec at all — the CLI never ran it. [`vv/specs/series_seven.spec.json`](vv/specs/series_seven.spec.json)
and its siblings close that.

Coverage is structural, not a habit: `grammar_coverage` reads `GRAMMARS` out of
`realize.verdicts` and fails if any declared grammar has no domain. Adding a grammar to the kernel
now breaks CI until a domain arrives with it. Same for `problem_family` and `semantics`.

## Objectives

Per case:

| Objective | What has to hold |
|---|---|
| `outcome` | The observed verdict (or adapter reject) is the declared one. |
| `exit_table` | The exit code the matrix declares matches `realize.verdicts.EXIT`. |
| `exit_observed` | The process actually exited with that code. |
| `determinism` | Two runs of the same case agree byte for byte. |
| `scope_completeness` | The certificate carries its digest, scope, witness, and checker name. |

Per domain:

| Objective | What has to hold |
|---|---|
| `declared_semantics` | Matrix, kernel table, and every referenced spec agree on family / grammar / semantics. |
| `outcome_coverage` | The domain is seen reaching `PASS`, `COUNTEREXAMPLE`, `UNSAT`, `UNKNOWN`, and adapter reject. All five. |
| `tamper_evidence` | Change `bound.budget` by one, and the candidate bound to that spec is refused rather than judged. |
| `synthesize_emits_no_verdict` | `realize synthesize` returns candidates and no `verdict`, anywhere in the payload. |
| `provenance` | Every non-null `R` and `K` clause names an origin, or declares with `unsourced` that it has none. |

### What `provenance` can and cannot decide

Three things about a citation are decidable, and the objective checks all three: that a clause
which constrains is cited at all, that the citation is not blank, and that it does not point at
one of this repository's own documents. `NONCLAIMS.md`, `README.md` and `VV.md` explain what the
package does and refuses to claim; none of them is ever where a clause came from.

That third rule is not hypothetical. Four specs in the first version of this matrix cited
`NONCLAIMS.md §2` — the section explaining why a zero budget yields `UNKNOWN` — as the source of
the relation in `R`. The gate passed them, because a citation that does not cite still looks like
a citation. A reviewer caught it; the gate could not. It can now, and
`tests/test_vv.py` keeps that specific failure caught.

**What stays undecidable: whether a source names anything real.** `VCOS §8.1 Table 2` and `asdf`
are the same shape, and nothing in a finite checker tells them apart. A clause with no origin
declares that with `"unsourced": true` *and* a `source` giving the reason, and the gate takes
the author's word for it — so that marker is a bypass, deliberately a visible one. The reason is
required precisely because an unexplained bypass is one nobody can audit. Counting the `unsourced` clauses in `vv/specs/` is
a minute's work for a person; noticing a plausible-looking citation that names nothing is not.

This is V₂ reaching into a V₁ check, and it does not close. What the objective changed is where
the gap sits: it used to hide inside citations that looked fine, and now it sits in a marker you
can grep for. Countable is the most a finite checker can make it.

### What the objective names mean

An objective is named for **what it reads**, not for the property someone might hope it
establishes. `synthesize_emits_no_verdict` says a payload carried no `verdict` key; it does not
say an agent refrained from grading itself, which is what NONCLAIMS §9 forbids and what no check
here can see. `tamper_evidence` says one named field was changed and the bound candidate was
refused; the general property comes from the digest, not from the test.

This is not pedantry about naming. A report line reading `[ok] no_self_grading` is read as
"self-grading has been ruled out," and that is a claim this harness cannot make. In a repository
whose product is refusing to overclaim, the harness is the last place that should start.

`outcome_coverage` is the one worth reading twice. Every domain must be *observed* reaching all four
verdicts and the adapter reject — not merely be capable of it in principle. A domain that can only
be shown passing is a domain nobody has watched fail.

## Running it

```bash
python3 scripts/vv.py                                   # every domain
python3 scripts/vv.py --domain encoder.finite_case_table # one domain
python3 scripts/vv.py --report vv-report.json            # full observations as JSON
python3 scripts/vv.py --lean                             # add Lean, skip it if absent
python3 scripts/vv.py --lean-required                    # add Lean, fail if absent
pytest tests/test_vv.py                                  # the same matrix under pytest
```

The runner exits `0` when every objective is met and `1` when one is not. That is deliberately
**not** the verdict scale — `0/1/2/3/4` belongs to `realize`, and a harness must not look like it is
issuing verdicts. `scripts/vv.py` is dev-only and is not part of the pip package. It cannot mint a
`PASS`; it only writes down what `realize` already decided.

## Lean

[`vv/lean/`](vv/lean/) re-states the finite facts of each domain in Lean 4 and proves them with
kernel-checked `decide`: core Lean only, no Mathlib, no `native_decide`, no `sorry`, no new axioms.
The runner refuses a file that reaches for any of those before `lean` is even invoked, because a
file that may assume things corroborates nothing.

Proving things in a second language is not yet a cross-check, though: two implementations can drift
apart happily if nobody puts their answers side by side. So each Lean file also *reports* what it
settled, and `scripts/vv.py` answers the same questions from Python and compares. A disagreement
fails the run; so does a fact that quietly stops being reported.

### Two bands: the parts, and the effect

The questions come in two kinds, and the second one is the point.

| Band | Facts | Lean reports | Python reports | What only this band sees |
|---|---|---|---|---|
| parts | 29 | what a search contains — 625 template members, ten series reaching 7, the obstructed fibre | the same, recomputed from kernel internals | a kernel that counts wrong |
| effect | 22 | the verdict the checker **has to** give a spec that ships, worked out from the branch order the checker uses | the verdict `check_search` **did** give that same spec file | a kernel whose parts are each right and whose verdict is assembled from them wrongly |

The effect band is what makes this a check on the repository rather than on its arithmetic. Python
answers it by running the real entry point on the real spec file and reading the certificate: the
verdict, how settled it is, and why.

Two injected faults show the difference. Move the histogram pre-check in `_search_grid` to after the
enumeration: `grid_preserve_histogram` still reports `UNSAT`, still exits 3, so the domain matrix
passes, the whole Python suite passes, and all 29 part-facts agree — only the effect band sees it
change reason from `histogram_contradicts_R` to `no_typed_realization`. Report an exhaustive `UNSAT`
as `unresolved` instead of `proved` and the same thing happens again.

Coverage of that band is structural, not a list someone remembers to extend: `tests/test_vv.py`
fails when a spec lands in `vv/specs/` or `demos/` that no Lean file derives a verdict for.

What agreement buys: two implementations written in different languages, by different means, reached
the same answer about the same small finite object. NONCLAIMS §7 says checker independence "reduces
one self-confirmation path." This reduces a second one — and it is the one that catches a frozen
count edited to match a drifting kernel, which the Python suite alone cannot catch, because the
suite is what would have been edited.

What it does not buy: Lean does not verify the Python kernel, the CLI, the CI, or the papers'
mathematics, and **a Lean file cannot mint a verdict** — nothing in `vv/lean/` sits on the path that
produces a certificate. Lean does not read the spec files either: each one is transcribed into Lean
by hand, so the comparison catches an edit to one side and not a matching edit to both. If Lean and
Python disagree, the V&V job goes red and one of them is wrong — the job does not say which.

## What this does not establish

1. That `R` means what anyone intended. That is V₂, and it stays open. NONCLAIMS §7. The
   `provenance` objective checks the *form* of a citation, never that it names something real —
   see above.
2. That a `PASS` says anything outside the declared finite scope. NONCLAIMS §6.
3. That the counts are a benchmark result. They are coverage. NONCLAIMS §5.
4. That the Python runtime, the OS, or GitHub Actions are correct.
5. That the domains here are the only ones that matter — only that every grammar the kernel
   *declares* is exercised. A grammar nobody wrote down is still a grammar nobody checks.
