# vv/ — the verification & validation matrix

This directory is **not** the checker. It cannot mint `PASS`.

It declares what every domain must be observed to do, and holds the specs and candidates that make
each domain reachable from the command line. The prose is in [../VV.md](../VV.md).

```
domains.json    the matrix: four domains, their cases, their expected outcomes
specs/          specs the demos do not already ship
candidates/     candidates bound by digest to those specs
lean/           independent corroboration of the same finite facts
```

## Run

```bash
python3 ../scripts/vv.py            # from here, or scripts/vv.py from the repo root
```

## Adding a domain

A domain is a `problem_family` paired with a `grammar`. Add one when the kernel learns a new
grammar — `grammar_coverage` will fail until you do.

1. Add the grammar to `GRAMMARS` in `src/realize/verdicts.py` and to `schema/realize.v0.json`.
2. Add a domain entry to `domains.json` with cases reaching all five outcomes: `PASS`,
   `COUNTEREXAMPLE`, `UNSAT`, `UNKNOWN`, adapter reject. `outcome_coverage` will fail until you do.
3. Write the specs under `specs/` with `provenance` for every clause that constrains. A
   source names where the clause came from — a paper, a section. This repository's own
   documents are not origins; a clause that genuinely has none says so with
   `"unsourced": true` and explains why.
4. Write the candidates under `candidates/`, each carrying the spec's digest.
5. Add a Lean file under `lean/` re-stating that domain's finite facts.

## Editing a spec

A candidate is bound to its spec by `spec_digest`. Editing a spec therefore breaks its candidates,
and `realize check` will refuse them with `adapter: spec_digest mismatch`. That is the binding
working, not a bug.

There is deliberately no `--restamp` flag. Re-author the candidate with the new digest, on purpose:

```bash
PYTHONPATH=src python3 -c "import json,sys; from realize.spec import load_spec; \
  from realize.digest import sha256_hex; print(sha256_hex(load_spec(sys.argv[1])))" vv/specs/your.spec.json
```
