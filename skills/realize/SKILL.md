---
name: realize
description: Independent checker for value-conditioned operator synthesis. Load when a constructed operation, encoder, or spec must be believed. Four verdicts. You may propose; you may not certify.
---

# realize

You are the **preference channel**. `realize check` is the **evidence channel**. Generation, planning, and verification are not the same module.

Loop:

1. Write `spec.json` (`realize.v0`). Hard constraints and preferences stay distinct.
2. Optionally `realize synthesize spec.json` — candidates only, never a `verdict`.
3. Always `realize check spec.json candidate.json` before claiming anything. Paste stdout.
4. On `COUNTEREXAMPLE`: keep the witness; do not retry-until-PASS.
5. On `UNSAT`: revise the spec or the grammar; do not invent a compromise that violates `R`/`K`.
6. On `UNKNOWN`: halt. Do not relabel. Do not ask another model to be more confident.
7. On `PASS`: the certificate is the claim. Nothing else is.

The seven-phase IGVF–CTS harness (conformal search, schematism, `Φ`, SMT, ASTAC) is specified in `papers/agent-harness.md`. This package implements phases 1, 2, and 7 as a finite kernel. You must not pretend the rest is running.

Read `NONCLAIMS.md` before claiming anything.

## When to load

The user or the agent has a constructed operation, encoder, formula, or term series that must be believed relative to a written spec.

## Hard rules

1. You may propose. You may not certify.
2. Before claiming a candidate works, call `realize check` (CLI or MCP). Paste the certificate.
3. Do not call another model to grade the answer. That does not discharge the checker.
4. Do not substitute tests you wrote for `realize check`.
5. `UNKNOWN` is a legal outcome. Do not retry-until-PASS, relabel it `UNSAT`, or ask a model to be more confident.
6. Spec and candidate stay separate files. Do not merge them so the digest can be gamed.
7. Preferences in the spec are not a reason to override a `COUNTEREXAMPLE`.

## CLI

```
realize check <spec.json> <candidate.json>
realize synthesize <spec.json>     # candidates only; no verdict
realize demo {max_formula|grid_recolor|three_state}
realize explain <certificate.json>
realize schema
```

Stdout is JSON. Human text is on stderr.

| Exit | Meaning |
|---|---|
| 0 | PASS |
| 1 | adapter reject (bad JSON, digest mismatch, unknown semantics) |
| 2 | COUNTEREXAMPLE |
| 3 | UNSAT |
| 4 | UNKNOWN |

`synthesize` exits 0 on a well-formed spec and **must not** contain a `verdict` field.

There is no `realize solve`.

## MCP

Tools: `realize_check`, `realize_synthesize`, `realize_explain`, `realize_demo`.

`realize_synthesize` returns candidates and the instruction: call `realize_check` before claiming success.

## Verdicts

- **PASS** — this candidate meets `R` and `K` on the declared domain at this evidence mode.
- **COUNTEREXAMPLE** — this candidate is false. Not a claim about the rest of the class.
- **UNSAT** — the declared finite class is empty, or a fibre obstruction kills the encoder. Scoped, never “no operator exists.”
- **UNKNOWN** — zero budget, incomplete coverage, unrecognized phrase, interrupted check.

## Spec / candidate

Trusted spec is `realize.v0`. Candidate carries `spec_id` and `spec_digest`. Digest mismatch is an adapter error, not a `COUNTEREXAMPLE`.
