# Non-claims

`realize` is a finite, fail-closed checker. It is not a theory of everything and it is not an agent that grades itself.

Read this before the README examples.

1. **Not a universal natural-language compiler.** Unrecognized formula phrases return `UNKNOWN`. The package does not invent a formal `R` from English.
2. **`UNKNOWN` is required.** There is no total exact solver for the unrestricted class of partial computable operations (VCOS Proposition 6.4). Zero budget, incomplete coverage, and interrupted checks are `UNKNOWN`, not `UNSAT`.
3. **Value does not rewrite evidence.** Preferences and proposal order never flip a fail to a pass. Changing only `≺` does not change `Sol`.
4. **Geometry, topology, Φ, sheaves, IsoZ, schematism, persistent homology, SMT, ASTAC, geometric LNNs, Dressing Field Method, holonomy, and lattice gauge theory are not in this package.** Their presence in the papers does not put them in this package. Their presence elsewhere would not imply consciousness. Their absence here is deliberate.
5. **Counts are coverage, not benchmark superiority.** 2,625 coefficient candidates, 192 encoder–input cases, 121 and 31 series, and the regression suite are reconstruction counts. They are not accuracy percentages and they are not a claim of beating SemGuS, cvc5, or DreamCoder.
6. **A proof in a model is not an observation of the world.** A `PASS` certificate is scoped to the declared finite context, grammar, bound, and evidence mode.
7. **Checker independence reduces one self-confirmation path.** Separate generator and checker implementations do not certify the Python runtime, the papers’ mathematics, or that a formal `R` matches anyone’s linguistic intention.
8. **`UNSAT` is scoped.** It means the declared finite class is empty (or the encoder fibre is obstructed). It never means “no operator exists.”
9. **Agents may propose. They may not certify.** Calling another model to judge an answer does not discharge `realize check`.
10. **Lean corroboration is not a verdict.** The files in `vv/lean/` re-state finite facts, and derive from them what verdict the checker has to report for each spec that ships; both are checked in Lean's kernel. Agreement means two implementations, written by different means, reached the same answer about the same small finite object. It does not verify the Python code, the CLI, the CI, or the papers' mathematics, and a Lean file cannot mint `PASS` — nothing in `vv/lean/` sits on the path that produces a certificate. Lean does not read the spec files either: each is transcribed into Lean by hand, so the comparison catches an edit to one side and not a matching edit to both. Disagreement means one of the two is wrong and does not say which.
11. **A green V&V run is not validation.** `scripts/vv.py` checks that each declared domain does what it says it does (verification). Whether a formal `R` matches anyone's intention is a separate question this repository does not answer. See [VV.md](VV.md).

If a README sentence appears to contradict this file, this file wins.
