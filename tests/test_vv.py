"""The V&V matrix under pytest. Do not relax an objective to make this green.

The Lean corroboration is deliberately not run here: it needs a toolchain that
`pip install -e ".[dev]"` does not provide. CI runs it as its own job.
"""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_runner():
    """Import `scripts/vv.py` by path.

    The repo has both `scripts/vv.py` and a `vv/` data directory, so a plain
    `import vv` would be free to pick the wrong one.
    """
    spec = importlib.util.spec_from_file_location("realize_vv", ROOT / "scripts" / "vv.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vv = _load_runner()
provenance_gaps = vv.provenance_gaps
CONFIG = json.loads((ROOT / "vv" / "domains.json").read_text(encoding="utf-8"))
DOMAINS = CONFIG["domains"]
IDS = [d["id"] for d in DOMAINS]


def test_config_version_is_supported():
    """The matrix must declare a config version this runner accepts."""
    assert CONFIG["schema_version"] == vv.CONFIG_VERSION


def test_every_declared_domain_is_covered():
    """A grammar added to realize.verdicts must arrive with a domain that exercises it."""
    result = vv.run_coverage(DOMAINS)
    unmet = [f"{o['objective']}: {o['detail']}" for o in result["objectives"] if not o["met"]]
    assert not unmet, unmet


@pytest.mark.parametrize("domain", DOMAINS, ids=IDS)
def test_domain_meets_its_objectives(domain):
    """Every per-case objective and every per-domain property, for one domain."""
    result = vv.run_domain(domain)
    unmet = []
    for case in result["cases"]:
        unmet += [
            f"{case['id']}: {o['objective']}: {o['detail']}"
            for o in case["objectives"]
            if not o["met"]
        ]
    unmet += [f"{p['objective']}: {p['detail']}" for p in result["properties"] if not p["met"]]
    assert not unmet, unmet


@pytest.mark.parametrize("domain", DOMAINS, ids=IDS)
def test_domain_reaches_all_four_verdicts_and_the_adapter(domain):
    """Four verdicts plus adapter reject, in every domain. No domain gets a pass on one."""
    reached = {c["expect"]["outcome"] for c in domain["cases"]}
    assert reached >= vv.OUTCOMES, sorted(vv.OUTCOMES - reached)


def _spec(provenance, *, k=None):
    return {"R": {"phrase": "larger"}, "K": k, "provenance": provenance}


def test_provenance_accepts_a_named_origin():
    assert provenance_gaps("s", _spec([{"clause": "R", "source": "VCOS §8.1 Table 2"}])) == []


def test_provenance_rejects_a_repo_document_as_an_origin():
    """The gate exists because a citation that does not cite still looks like one.

    Four specs in the first version of this matrix cited NONCLAIMS.md — which explains
    why a zero budget yields UNKNOWN — as the source of the relation in R. A reviewer
    caught it; the gate could not. Now it can.
    """
    gaps = provenance_gaps("s", _spec([{"clause": "R", "source": "NONCLAIMS.md §2"}]))
    assert len(gaps) == 1
    assert "NONCLAIMS.md" in gaps[0]


def test_provenance_rejects_a_blank_source():
    assert provenance_gaps("s", _spec([{"clause": "R", "source": "   "}])) != []
    assert provenance_gaps("s", _spec([{"clause": "R"}])) != []


def test_provenance_rejects_a_constraining_clause_that_cites_nothing():
    gaps = provenance_gaps("s", _spec([{"clause": "R", "source": "VCOS §8.1"}], k={"inv": "x"}))
    assert any("K constrains but cites nothing" in g for g in gaps)


def test_provenance_allows_a_declared_absence_of_origin():
    """`unsourced` is a bypass. It is meant to be one, and meant to be visible."""
    entry = {"clause": "R", "unsourced": True, "source": "deliberately outside the declared set"}
    assert provenance_gaps("s", _spec([entry])) == []


def test_shipped_specs_carry_no_provenance_gaps():
    for path in sorted((ROOT / "vv" / "specs").glob("*.json")) + sorted(
        (ROOT / "demos").glob("*/spec.json")
    ):
        spec = json.loads(path.read_text(encoding="utf-8"))
        assert provenance_gaps(path.name, spec["specification"]) == []
