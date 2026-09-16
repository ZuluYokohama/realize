# Dual-channel agent harness

A coding agent can implement IGVF–CTS / VCMS as a **loop**, not as an unconstrained model. Generation, planning, and verification stay separate modules. This repository ships the verification module.

Read [NONCLAIMS.md](../NONCLAIMS.md) and [architecture.md](architecture.md) first. Load [`skills/realize/SKILL.md`](../skills/realize/SKILL.md) before claiming any candidate.

## Firewall

| Channel | Who | May do | Must not do |
|---|---|---|---|
| Preference | The agent, `realize synthesize`, any proposer | Compile a spec, enumerate or search candidates, order them | Emit a `verdict`, grade its own homework, flip a fail because the wish was nicer |
| Evidence | `realize check` only | Stamp PASS / COUNTEREXAMPLE / UNSAT / UNKNOWN | Import the generator |

There is no `realize solve`.

## Seven-phase loop vs v0

| Phase | Channel | In `realize` v0 |
|---|---|---|
| 1. Intent compilation → `Σ` | Normative | JSON spec (`R`, `K`, preferences, bound). Unrecognized English is `UNKNOWN`, not an invented `R`. |
| 2. Representation / fibre adequacy | Relational | Encoder fibres; `three_state` empty triple; hidden `fourbit`. Hitting-set *solver* is not shipped. |
| 3. Path search on `g_v` | Preference | Bounded enumeration only. No conformal metric, no MCTS. |
| 4. Schematism / persistence on `d_0` | Evidence | Not in the package. |
| 5. Coherence `Φ` | Evidence | Not in the package. |
| 6. SMT / quotient safety | Evidence | Not in the package. An external solver may propose a witness; it may not certify. |
| 7. Actuation or refutation | Execution | Four verdicts. CLI exits 0 / 2 / 3 / 4. Adapter reject is 1. |

Agent cycle in v0:

```
write spec.json          # hard constraints ≠ preferences
realize synthesize spec  # optional; candidates only
realize check spec cand  # required before any claim
```

| Verdict | Agent must |
|---|---|
| PASS | Paste the certificate. That is the only claim. |
| COUNTEREXAMPLE | Keep the witness. Do not retry-until-yes. Propose a different candidate or stop. |
| UNSAT | Revise the spec or the grammar. Do not invent a compromise that violates `R`/`K`. |
| UNKNOWN | Halt. Do not relabel as UNSAT. Do not ask a model to be more sure. |

## Falsifiable hypotheses — what this repo can already run

**H1 — Intent decoupling (supported in-kernel).** Conflicting hard constraints must not be “optimized away.”

- `realize demo three_state` → `UNSAT` (pairwise nonempty, triple empty).
- `realize demo grid_recolor` histogram plate → `UNSAT` (recolor and keep every color).
- Affine-only formula toolbox → `UNSAT`. Unrecognized phrase → `UNKNOWN`.

A 0% hard-constraint violation rate on these fixtures is the test. An unconstrained model that says “you’re covered” fails H1.

**H2 — Conformal search efficiency.** Not in v0. Would require an optional proposer extra. Safety still means: misaligned `v` may slow search or yield `UNKNOWN`; it must not mint a PASS.

**H3 — Schematism hallucination halt.** Not in v0. Persistence and `Φ` stay papers-only.

**H4 — Quotient invariance.** Not in v0.

## Environments

| Env | Manuscript | In v0 |
|---|---|---|
| A. Discrete relational (ARC-like) | Grid, histogram, fibres | `grid_recolor`, `three_state`, formula |
| B. Cyber-physical telemetry (ASTAC) | Stick-slip `H_1`, SMT kinematics | No. Operator data stays out. |
| C. Constrained continuous flow | Projection `K`, `ḣ = 0` | No. |

## Ablations this kernel can already distinguish

| Ablation | What happens here |
|---|---|
| Full architecture | Not claimed. |
| No conformal metric | v0 is this for search: enumeration on the discrete class, value ignored for the stamp. |
| No schematism | v0 has no schematism; do not read `Φ` into a PASS. |
| Pairwise-only fibre check | `three_state` is the counterexample: every pair works, the triple does not. |
| Unconstrained base model | The left column of the public rooms: fluent yes, no certificate. |

## What not to build into the pip package

MCTS on `g_v`, GUDHI, knowledge-graph `Φ`, Z3 as grader, ASTAC ingestion, “transcendental error” as a fifth verdict. Those may exist as **untrusted adapters** that output candidates or `UNKNOWN`. They never output PASS.
