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
    # By explicit path: the repo has both `scripts/vv.py` and a `vv/` data directory,
    # and `import vv` would be free to pick the wrong one.
    spec = importlib.util.spec_from_file_location("realize_vv", ROOT / "scripts" / "vv.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vv = _load_runner()
CONFIG = json.loads((ROOT / "vv" / "domains.json").read_text(encoding="utf-8"))
DOMAINS = CONFIG["domains"]
IDS = [d["id"] for d in DOMAINS]


def test_config_version_is_supported():
    assert CONFIG["schema_version"] == vv.CONFIG_VERSION


def test_every_declared_domain_is_covered():
    """A grammar added to realize.verdicts must arrive with a domain that exercises it."""
    result = vv.run_coverage(DOMAINS)
    unmet = [f"{o['objective']}: {o['detail']}" for o in result["objectives"] if not o["met"]]
    assert not unmet, unmet


@pytest.mark.parametrize("domain", DOMAINS, ids=IDS)
def test_domain_meets_its_objectives(domain):
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
