# Relational certificates (finite kernel)

This is not a dressing-field solver and not a lattice gauge engine. It is the **certificate pattern** a relational program needs and `realize` already runs: the checker does not import the generator; the stamp does not depend on the proposer; `UNKNOWN` is not green.

The physical rhyme is: **no privileged situated viewpoint.** The computational rhyme is: **no privileged proposer.** Same shape, different substrate.

Literature this note is written against (not implemented here):

- J. François, L. Ravera, *Geometric relational framework for general-relativistic gauge field theories*, [arXiv:2407.04043](https://arxiv.org/abs/2407.04043)
- L. Ravera, *Lecture Notes on Symmetry Reduction via the Dressing Field Method*, [arXiv:2603.29505](https://arxiv.org/abs/2603.29505)
- J. François, L. Ravera, *Invariant Path-Integral Quantization and Anomaly Cancellation*, [arXiv:2604.21004](https://arxiv.org/abs/2604.21004) — “amenable to lattice implementations”

A lattice implementation of that path integral still needs an independent stamp. That stamp is what this package is.

## What v0 already is, in that language

`three_state` is the finite **every context consistent, no global section**:

- Three contexts. Every pair has a nonempty overlap.
- The triple overlap is empty.
- Pairwise yes is not a global assignment. The stamp is `UNSAT`, not a fluent compromise.

That is the discrete cousin of the continuous-selection fact (VCMS Extensions §7): nonempty fibres pointwise do not give a global continuous operator (square-root on the circle). Gauge/diffeomorphism dressings live on the continuous side. This kernel stays discrete.

`UNKNOWN` is the other relational duty: do not invent a formula for a job you have not written.

## Certificate protocol (C1–C3) — pattern, not shipped physics

| Id | Claim | Finite meaning | `realize` today |
|---|---|---|---|
| **C1** invariance | The dressed observable does not depend on the gauge / chart | Same candidate, two writings, same value on the declared domain | Not a dressing family. Ordinary `PASS` is scoped invariance of a candidate against `R`/`K` only. |
| **C2** covariance under change of tree | Changing the reference/tree rewrites the dressing, not the physics | Two trees, one spec; certificates agree or the adapter rejects | Not shipped. |
| **C3** adequacy | The representation does not collapse distinct relational facts | Fibre intersection nonempty; pairwise nonempty is not enough | **Shipped.** `three_state` is the C3 counterexample. Hidden `fourbit` too. |

Preferences, gauge choices, and proposer order may **search**. They may not rewrite C1–C3.

## Lattice DFM adapter (not in v0)

A later `problem_family` (name TBD), still fail-closed, still four verdicts:

| Spec | Candidate | Stamp |
|---|---|---|
| Finite graph, compact group, configuration | Dressing field + dressed observable | C1 |
| Choice of spanning tree / reference | Same dressing on another tree | C2 |
| Encoder of contexts | Fibre check | C3 |

Public finite plates, if that family is added:

1. U(1) on a lattice, tree dressing as the Lorenz-gauge analogue — C1/C2.
2. Matter dressing at a root (Abelian Higgs without SSB) — relational observable, not a vev.
3. `three_state` recast as C3 — every context, no global section.

Until that adapter exists, `realize check` does not compute a holonomy, does not extract a dressing field, and does not certify section-independence of a dressed observable.

See [architecture.md](architecture.md), [agent-harness.md](agent-harness.md), [NONCLAIMS.md](../NONCLAIMS.md).
