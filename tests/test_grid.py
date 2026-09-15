from realize.checker import check, check_search
from realize.compose import all_3x3_masks, render2, support
from realize.demos import load_demo_spec
from realize.digest import sha256_hex
from realize.spec import load_spec
from realize.verdicts import SCHEMA_VERSION, Verdict


def test_recolor_pass():
    spec = load_demo_spec("grid_recolor")
    cand = {
        "schema_version": SCHEMA_VERSION,
        "spec_id": spec["id"],
        "spec_digest": sha256_hex(spec),
        "term": {"kind": "sequence", "ops": ["Extract", "Render2"]},
    }
    cert = check(spec, cand)
    assert cert["verdict"] == Verdict.PASS.value
    assert cert["witness"]["Y"] == [[0, 2, 0], [2, 2, 0], [0, 0, 2]]


def test_histogram_unsat():
    spec = load_demo_spec("grid_recolor")
    hist = load_spec(
        {
            **spec,
            "id": "igvf.grid_recolor.histogram",
            "specification": {**spec["specification"], "K": {"preserve_histogram": True}},
        }
    )
    cert = check_search(hist)
    assert cert["verdict"] == Verdict.UNSAT.value


def test_type_failures():
    spec = load_demo_spec("grid_recolor")
    digest = sha256_hex(spec)
    for ops in ([], ["Extract"], ["Render2"]):
        cand = {
            "schema_version": SCHEMA_VERSION,
            "spec_id": spec["id"],
            "spec_digest": digest,
            "term": {"kind": "sequence", "ops": ops},
        }
        cert = check(spec, cand)
        assert cert["verdict"] == Verdict.COUNTEREXAMPLE.value, ops


def test_512_masks_preserve_support():
    masks = all_3x3_masks()
    assert len(masks) == 512
    for b in masks:
        y = render2(b)
        assert support(y) == support(b)
