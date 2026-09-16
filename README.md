# realize

Don’t take the AI’s word for it. Modern models will agree to two easy jobs that cannot both hold, and they will write a formula for a job they do not know. realize is an independent check. The model may propose. It may not grade itself.

Independent checker for value-conditioned operator synthesis. Finite kernel. Four verdicts. Agents cannot grade themselves.

**Read [NONCLAIMS.md](NONCLAIMS.md) first.** This package does not compile arbitrary English, does not beat SemGuS, and does not let an agent grade itself. Public theatre (render-only, in-repo until GitHub Pages is enabled): [web/](https://github.com/ZuluYokohama/realize/tree/main/web).

## 30 seconds

```bash
pip install git+https://github.com/ZuluYokohama/realize.git
realize demo three_state
realize demo max_formula
realize demo grid_recolor
realize check demos/three_state/spec.json candidate.json
```

Not on PyPI yet. `pip install realize` will 404.

`three_state` is supposed to be `UNSAT`: three inputs share one code and their acceptable sets `{0,1} ∩ {1,2} ∩ {0,2}` are empty. Pairwise intersections are nonempty. That is the point.

## Four verdicts

| Verdict | Meaning | CLI exit |
|---|---|---|
| `PASS` | This candidate meets `R` and `K` at the declared scope | 0 |
| adapter reject | Bad JSON, digest mismatch, unknown semantics | 1 |
| `COUNTEREXAMPLE` | This candidate is false | 2 |
| `UNSAT` | The declared finite class is empty (scoped) | 3 |
| `UNKNOWN` | Budget, coverage, or evidence is insufficient | 4 |

Stdout is the certificate JSON. `realize synthesize` emits candidates only and never a `verdict`.

## What v0 does

- Independent checker: `realize.checker` does not import the generator.
- Three public demos: `max_formula` (VCOS Table 2), `grid_recolor` (IGVF–CTS §7.1), `three_state` (VCMS Ex. 4.3).
- Hidden fixtures that still have to pass: 2,625 coefficient candidates, 192 encoder–input cases, 121 and 31 term series, zero-budget `UNKNOWN`.
- Agent surfaces: CLI, optional MCP extra, [`skills/realize/SKILL.md`](skills/realize/SKILL.md).

## What v0 does not do

See [NONCLAIMS.md](NONCLAIMS.md). No LLM proposer, no geometry, no sheaves, no `realize solve`. The finite kernel of the IGVF–CTS / VCMS architecture is mapped in [papers/architecture.md](papers/architecture.md).

## Agent use

Load the skill. Propose if you must. Then:

```bash
realize check spec.json candidate.json
```

Paste the certificate. Do not call another model to grade the answer.

```toml
# GitHub Actions
- run: realize check spec.json candidate.json
```

Nonzero exit fails the job. `UNKNOWN` (exit 4) is not green unless you explicitly allow it.

MCP:

```bash
pip install 'realize[mcp]'
python -m realize.mcp_server
```

Tools: `realize_check`, `realize_synthesize`, `realize_explain`, `realize_demo`. No `realize_solve`.

## Install (dev)

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
```

Python ≥ 3.11. Core extra is stdlib-only.

## Papers

Citations in [papers/README.md](papers/README.md). Schema: [schema/realize.v0.json](schema/realize.v0.json).
