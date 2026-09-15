import json

from realize.cli import run
from realize.demos import run_demo


def test_demo_three_state(capsys):
    code = run(["demo", "three_state"])
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert out["ok"] is True
    assert out["cases"][0]["actual"] == "UNSAT"


def test_demo_max_formula(capsys):
    code = run(["demo", "max_formula"])
    out = json.loads(capsys.readouterr().out)
    assert code == 0, out
    assert out["ok"] is True


def test_demo_grid(capsys):
    code = run(["demo", "grid_recolor"])
    out = json.loads(capsys.readouterr().out)
    assert code == 0, out
    assert out["ok"] is True


def test_schema(capsys):
    code = run(["schema"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["properties"]["schema_version"]["const"] == "realize.v0"


def test_run_demo_helpers():
    for name in ("three_state", "max_formula", "grid_recolor"):
        result = run_demo(name)
        assert result["ok"] is True, name


def test_check_three_state_candidate(capsys):
    code = run(
        [
            "check",
            "demos/three_state/spec.json",
            "demos/three_state/candidate.json",
        ]
    )
    out = json.loads(capsys.readouterr().out)
    assert code == 3
    assert out["verdict"] == "UNSAT"
