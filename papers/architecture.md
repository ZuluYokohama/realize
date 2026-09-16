# Formalizing intent into substance — what this repository is

The manuscript *Formalizing Intent into Substance: The Information-Geometric Value and Configurational Term Synthesis Architecture for Auditable Artificial Intelligence* describes a full stack:

1. Compile intent into a typed specification that separates **hard constraints** from **preferences**.
2. Prove representation adequacy (fibres do not collapse distinct requirements).
3. Search with a value-conformal geometry.
4. Ground concepts in observation (persistent homology, knowledge-graph coherence, schematism).
5. Compose typed operator series and emit one of four verdicts.

`realize` is **not** that whole stack. It is the **evidence channel and finite kernel** of it: an independent checker that cannot be talked into a yes.

Read [NONCLAIMS.md](../NONCLAIMS.md) first.

## Preference vs evidence

The manuscript’s firewall is the product:

- **Preference** may order search. In v0 it is recorded on the spec and ignored by the verdict.
- **Evidence** is `realize check`. A nicer wish does not flip `COUNTEREXAMPLE` to `PASS`.
- Agents may propose (`realize synthesize`). They may not certify.

That is why the public demos are overclaims, not “can a model pick max(a, b).”

## Layer map

| Layer in the manuscript | In `realize` v0 | Where |
|---|---|---|
| Intent / value spec: goal, hard `R`/`K`, preferences, budget, unresolved | Yes, as JSON `realize.v0` | `schema/realize.v0.json` |
| Provenance of clauses | Digest of the spec, not a full `τ` log | `spec_digest` |
| Natural-language compiler | No. Unrecognized phrases are `UNKNOWN` | `formula` family |
| Fibre compatibility / empty intersection | Yes | `three_state`, hidden `fourbit` |
| Obstruction-guided hitting set (weighted, dual certificates) | Obstruction is detected; the hitting-set solver is not shipped | `UNSAT` on obstructed encoder |
| Conformal value metric `g_v = e^{-βv} g_0` | No | papers only |
| Persistent homology on the unwarped base metric | No | papers only |
| Robust persistence transfer (`τ + 2ε`) | No | papers only |
| Knowledge-graph Laplacian, `Φ`, antinomy load | No | papers only |
| Schematism bridge / “transcendental error” | No | papers only |
| Typed term series, Hoare-style guards | Finite typed grid + guarded integer series | `grid_recolor`, hidden series fixtures |
| SMT / Z3 / MCTS proposer | No proposer. Checker only | CLI `synthesize` is bounded enumeration |
| Four verdicts: PASS / COUNTEREXAMPLE / UNSAT / UNKNOWN | Yes. Required. | checker, CLI exits 0/2/3/4 |
| Quotient safety games, constrained gradient flows | No | papers only |
| ASTAC drilling telemetry | No | papers only; operator data stays out |
| ARC-style grid recolor | Yes, 3×3 finite kernel | `grid_recolor` |
| Geometric LNNs / symplectic cache | No | papers only |

## Public demos as kernel instances

| Demo | Manuscript object | Verdict the page shows |
|---|---|---|
| Every pair / three_state | Fibre intersection empty; pairwise nonempty | Nothing here works (`UNSAT`) |
| Recolor and keep every color | Contradictory `R` and `K` (histogram) | Nothing here works (`UNSAT`) |
| Unknown formula | Unresolved intent `U`; no invented `R` | Can’t tell (`UNKNOWN`) |
| Affine-only toolbox | Empty `Sol_B` at the declared grammar | Nothing here works (`UNSAT`) |

The easy “always take the bigger number” plate is a **control**: a hold is possible. It is not the product.

## What would be a lie

- Shipping this package as “auditable AI” for wellbore control, ARC-AGI, or neural ODEs.
- Computing topology under the value-warped metric (the manuscript forbids that; the package does not compute topology at all).
- Treating `Φ` or a Laplacian gap as consciousness or as a substitute for `realize check`.
- Letting a model grade its own term series.

## What v1 could add without breaking the firewall

In order, and only as **checked** objects with the same four verdicts:

1. Weighted hitting-set certificates for encoder obstructions (still finite).
2. An optional SMT extra that returns witnesses the **checker** re-verifies — never a self-graded PASS.
3. Persistence / schematism as an **untrusted adapter** that can only produce `UNKNOWN` or a candidate, never a verdict.

Geometry remains out of the stdlib kernel.
