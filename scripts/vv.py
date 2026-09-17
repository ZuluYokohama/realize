#!/usr/bin/env python3
"""Dev-only verification & validation runner. Not part of the pip package.

This script cannot mint a verdict. It observes what `realize` already decides and
reports whether each declared domain was observed to behave as `vv/domains.json`
says it must. Its own exit status is 0 (every objective met) or 1 (something was
not met) — deliberately not the verdict exit codes, which belong to `realize`.

Read VV.md before changing what counts as met.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from realize import __version__  # noqa: E402
from realize.checker import check_search  # noqa: E402
from realize.digest import canonical_bytes  # noqa: E402
from realize.spec import load_spec  # noqa: E402
from realize.verdicts import (  # noqa: E402
    EXIT,
    GRAMMARS,
    PROBLEM_FAMILIES,
    SEMANTICS,
    Verdict,
)

CONFIG_VERSION = "realize.vv.v0"

# A Lean file that may assume things, or that hands checking to the compiler instead
# of the kernel, corroborates nothing. These are refused before `lean` is even run.
LEAN_FORBIDDEN = (
    (re.compile(r"\bsorry\b"), "sorry"),
    (re.compile(r"\bnative_decide\b"), "native_decide, which trusts the compiler, not the kernel"),
    (re.compile(r"^\s*axiom\b", re.MULTILINE), "a new axiom"),
    (re.compile(r"@\[(implemented_by|extern)"), "a compiler override"),
)
ADAPTER = "adapter"
OUTCOMES = frozenset({v.value for v in Verdict} | {ADAPTER})
PROVENANCE_CLAUSES = ("R", "K")


# ---------------------------------------------------------------- primitives


def expected_exit(outcome: str) -> int:
    """The exit status the documented table assigns to this outcome."""
    return EXIT[ADAPTER] if outcome == ADAPTER else EXIT[Verdict(outcome)]


def run_cli(spec: Path, candidate: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "realize", "check", str(spec), str(candidate)],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin", "HOME": str(ROOT)},
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def observe(case: dict) -> dict:
    """Run one case and report what came back. No expectation is applied here."""
    spec = ROOT / case["spec"]
    if case["entry"] == "cli":
        code, out, err = run_cli(spec, ROOT / case["candidate"])
        if code == EXIT[ADAPTER]:
            return {"outcome": ADAPTER, "exit": code, "certificate": None, "stderr": err.strip()}
        try:
            cert = json.loads(out)
        except json.JSONDecodeError:
            return {"outcome": None, "exit": code, "certificate": None, "stderr": err.strip()}
        return {"outcome": cert.get("verdict"), "exit": code, "certificate": cert, "stderr": ""}
    cert = check_search(spec)
    verdict = cert["verdict"]
    return {"outcome": verdict, "exit": expected_exit(verdict), "certificate": cert, "stderr": ""}


def fail(objective: str, detail: str) -> dict:
    return {"objective": objective, "met": False, "detail": detail}


def meet(objective: str, detail: str = "") -> dict:
    return {"objective": objective, "met": True, "detail": detail}


# ---------------------------------------------------------------- objectives


def case_objectives(case: dict, seen: dict) -> list[dict]:
    """Did this case do what the matrix says, through the interface it names?"""
    want = case["expect"]
    got = seen["outcome"]
    out = []
    if got != want["outcome"]:
        detail = f"expected {want['outcome']}, observed {got}"
        if got == ADAPTER and seen.get("stderr"):
            detail += f" ({seen['stderr']})"
        out.append(fail("outcome", detail))
    else:
        out.append(meet("outcome", want["outcome"]))
    if want["exit"] != expected_exit(want["outcome"]):
        out.append(
            fail(
                "exit_table",
                f"matrix says exit {want['exit']} for {want['outcome']}, "
                f"realize.verdicts.EXIT says {expected_exit(want['outcome'])}",
            )
        )
    else:
        out.append(meet("exit_table", f"{want['outcome']} -> {want['exit']}"))
    if seen["exit"] != want["exit"]:
        out.append(fail("exit_observed", f"expected exit {want['exit']}, observed {seen['exit']}"))
    else:
        out.append(meet("exit_observed", str(want["exit"])))
    return out


def objective_determinism(case: dict, first: dict) -> dict:
    again = observe(case)
    if first["certificate"] is None and again["certificate"] is None:
        same = first["outcome"] == again["outcome"] and first["exit"] == again["exit"]
    else:
        same = canonical_bytes(first["certificate"]) == canonical_bytes(again["certificate"])
    if not same:
        return fail("determinism", "two runs of the same case did not agree")
    return meet("determinism", "two runs agree byte for byte")


def objective_scope(case: dict, seen: dict) -> dict:
    """A certificate must carry the boundary its claim is good inside."""
    cert = seen["certificate"]
    if cert is None:
        return meet("scope_completeness", "adapter reject carries no certificate, by design")
    missing = [k for k in ("spec_digest", "scope", "witness", "checker") if k not in cert]
    scope = cert.get("scope") or {}
    missing += [
        f"scope.{k}"
        for k in ("problem_family", "grammar", "bound", "evidence_mode")
        if k not in scope
    ]
    if missing:
        return fail("scope_completeness", f"certificate is missing {sorted(missing)}")
    if cert.get("checker", {}).get("name") != "realize.checker":
        return fail("scope_completeness", "certificate does not name realize.checker")
    return meet("scope_completeness", "digest, scope, witness and checker all present")


def objective_tamper(domain: dict) -> dict:
    """One changed field in the spec must cost the candidate its binding."""
    passing = next(
        (c for c in domain["cases"] if c["entry"] == "cli" and c["expect"]["outcome"] == "PASS"),
        None,
    )
    if passing is None:
        return fail("tamper_evidence", "domain declares no CLI PASS case to tamper with")
    spec = json.loads((ROOT / passing["spec"]).read_text(encoding="utf-8"))
    spec["bound"]["budget"] = int(spec["bound"]["budget"]) - 1
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(spec, fh)
        tampered = Path(fh.name)
    try:
        code, _out, _err = run_cli(tampered, ROOT / passing["candidate"])
    finally:
        tampered.unlink(missing_ok=True)
    if code != EXIT[ADAPTER]:
        return fail(
            "tamper_evidence",
            f"budget changed by one and the candidate still scored exit {code}",
        )
    return meet("tamper_evidence", "a one-field spec edit turns PASS into an adapter reject")


def objective_no_self_grading(domain: dict) -> dict:
    """The proposer channel must never hand back something that reads as a verdict."""
    case = next((c for c in domain["cases"] if c["expect"]["outcome"] == "PASS"), None)
    if case is None:
        return fail("no_self_grading", "domain declares no PASS case to synthesize from")
    proc = subprocess.run(
        [sys.executable, "-m", "realize", "synthesize", case["spec"]],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin", "HOME": str(ROOT)},
        check=False,
    )
    if proc.returncode != 0:
        return fail("no_self_grading", f"synthesize exited {proc.returncode}: {proc.stderr.strip()}")
    payload = json.loads(proc.stdout)
    if "verdict" in payload:
        return fail("no_self_grading", "synthesize output carries a top-level verdict")
    graded = [c for c in payload.get("candidates", []) if "verdict" in c]
    if graded:
        return fail("no_self_grading", f"{len(graded)} synthesized candidates carry a verdict")
    return meet(
        "no_self_grading",
        f"{len(payload.get('candidates', []))} candidates, none carrying a verdict",
    )


def objective_provenance(domain: dict) -> dict:
    """Validation gate: a clause that constrains must say where it came from."""
    gaps = []
    for path in sorted({c["spec"] for c in domain["cases"]}):
        spec = load_spec(ROOT / path)
        cited = {p.get("clause") for p in spec["specification"]["provenance"] if isinstance(p, dict)}
        for clause in PROVENANCE_CLAUSES:
            if spec["specification"][clause] is not None and clause not in cited:
                gaps.append(f"{path}:{clause}")
    if gaps:
        return fail("provenance", f"clauses constrain but cite no source: {gaps}")
    return meet("provenance", "every non-null R and K clause cites a source")


def objective_declared_semantics(domain: dict) -> dict:
    """The matrix, the kernel's table, and every referenced spec must agree."""
    family, declared = domain["problem_family"], domain["semantics"]
    if SEMANTICS.get(family) != declared:
        return fail(
            "declared_semantics",
            f"matrix says {family} is {declared}, realize.verdicts.SEMANTICS says "
            f"{SEMANTICS.get(family)}",
        )
    for path in sorted({c["spec"] for c in domain["cases"]}):
        spec = load_spec(ROOT / path)
        if spec["problem_family"] != family:
            return fail("declared_semantics", f"{path} is not family {family}")
        if spec["library"]["grammar"] != domain["grammar"]:
            return fail("declared_semantics", f"{path} is not grammar {domain['grammar']}")
        if spec["context"]["semantics"] != declared:
            return fail("declared_semantics", f"{path} is not semantics {declared}")
    return meet("declared_semantics", f"{family} / {domain['grammar']} / {declared}")


def objective_outcome_coverage(domain: dict) -> dict:
    """Every domain must be seen reaching every outcome the kernel can return."""
    reached = {c["expect"]["outcome"] for c in domain["cases"]}
    missing = sorted(OUTCOMES - reached)
    if missing:
        return fail("outcome_coverage", f"domain never reaches {missing}")
    return meet("outcome_coverage", f"reaches all {len(OUTCOMES)} outcomes")


# ---------------------------------------------------------------- the sweep


def run_domain(domain: dict) -> dict:
    cases = []
    for case in domain["cases"]:
        seen = observe(case)
        objectives = case_objectives(case, seen)
        objectives.append(objective_determinism(case, seen))
        objectives.append(objective_scope(case, seen))
        cases.append(
            {
                "id": case["id"],
                "entry": case["entry"],
                "spec": case["spec"],
                "candidate": case.get("candidate"),
                "expected": case["expect"],
                "observed": {"outcome": seen["outcome"], "exit": seen["exit"]},
                "why": case.get("why", ""),
                "objectives": objectives,
                "ok": all(o["met"] for o in objectives),
            }
        )
    properties = [
        objective_declared_semantics(domain),
        objective_outcome_coverage(domain),
        objective_tamper(domain),
        objective_no_self_grading(domain),
        objective_provenance(domain),
    ]
    return {
        "id": domain["id"],
        "problem_family": domain["problem_family"],
        "grammar": domain["grammar"],
        "semantics": domain["semantics"],
        "source": domain.get("source", ""),
        "cases": cases,
        "properties": properties,
        "ok": all(c["ok"] for c in cases) and all(p["met"] for p in properties),
    }


def run_coverage(domains: list[dict]) -> dict:
    """Nothing the kernel declares may go unexercised."""
    families = {d["problem_family"] for d in domains}
    grammars = {d["grammar"] for d in domains}
    semantics = {d["semantics"] for d in domains}
    objectives = []
    for label, declared, covered in (
        ("problem_family", set(PROBLEM_FAMILIES), families),
        ("grammar", set(GRAMMARS), grammars),
        ("semantics", set(SEMANTICS.values()), semantics),
    ):
        missing = sorted(declared - covered)
        if missing:
            objectives.append(
                fail(
                    f"{label}_coverage",
                    f"declared in realize.verdicts but no domain covers {missing}",
                )
            )
        else:
            objectives.append(meet(f"{label}_coverage", f"{len(covered)} of {len(declared)}"))
    stray = sorted(grammars - set(GRAMMARS)) + sorted(families - set(PROBLEM_FAMILIES))
    if stray:
        objectives.append(fail("no_stray_domains", f"matrix declares unknown {stray}"))
    else:
        objectives.append(meet("no_stray_domains", "every domain names a known family and grammar"))
    return {
        "problem_families": sorted(families),
        "grammars": sorted(grammars),
        "semantics": sorted(semantics),
        "objectives": objectives,
        "ok": all(o["met"] for o in objectives),
    }


# ---------------------------------------------------------------- lean layer


def python_facts() -> dict[str, str]:
    """The same finite questions, answered by the Python kernel.

    Lean answers them in `vv/lean/`. The two are compared in `run_lean`; a proof
    nobody compares to anything corroborates nothing.
    """
    from realize.compose import eval_ops, goal_y
    from realize.formula import all_coeffs, valid_tuples
    from realize.kernel import adequate, fibres, lookup_R
    from realize.series import classify, syntactic_count

    def halves(tuples) -> str:
        return ";".join(",".join(str(int(2 * v)) for v in c) for c in tuples)

    def joined(values) -> str:
        return ",".join(str(v) for v in values)

    out: dict[str, str] = {
        "formula.template_card": str(len(all_coeffs())),
        "formula.affine_card": str(len(all_coeffs(affine_only=True))),
        "formula.affine_larger_count": str(len(valid_tuples("larger", affine_only=True))),
    }
    for phrase in ("larger", "smaller", "midpoint", "absdiff"):
        solutions = valid_tuples(phrase)
        out[f"formula.{phrase}_count"] = str(len(solutions))
        out[f"formula.{phrase}_solution"] = halves(solutions)

    odd = ["add1", "add3", "double"]
    even = ["add2", "double"]
    seven = classify(odd, 0, 8, 7, 4)
    out["series.syntactic_121"] = str(syntactic_count(3, 4))
    out["series.syntactic_31"] = str(syntactic_count(2, 4))
    out["series.seven_valid"] = str(seven["n_valid"])
    out["series.seven_min_len"] = str(seven["min_len"])
    out["series.witness"] = joined(seven["min_seqs"][0]) if seven["min_seqs"] else ""
    out["series.even_valid"] = str(classify(even, 0, 8, 7, 4)["n_valid"])
    out["series.nine_valid"] = str(classify(odd, 0, 8, 9, 4)["n_valid"])

    R = {"0": [0, 1], "1": [1, 2], "2": [0, 2]}
    dom = [0, 1, 2]
    collapse = {"id": "collapse_all", "map": {"0": "z", "1": "z", "2": "z"}}
    separate = {"id": "separate_all", "map": {"0": "a", "1": "b", "2": "c"}}
    out["encoder.collapse_adequate"] = str(adequate(R, collapse, dom)[0]).lower()
    out["encoder.separate_adequate"] = str(adequate(R, separate, dom)[0]).lower()
    out["encoder.collapse_fibre"] = joined(fibres(collapse, dom)["z"])
    triple = lookup_R(R, 0) & lookup_R(R, 1) & lookup_R(R, 2)
    out["encoder.obstruction"] = joined(sorted(triple))
    for a, b in ((0, 1), (1, 2), (0, 2)):
        out[f"encoder.pair_{a}{b}"] = joined(sorted(lookup_R(R, a) & lookup_R(R, b)))

    grid = [[0, 3, 0], [4, 4, 0], [0, 0, 5]]
    recolored = eval_ops(["Extract", "Render2"], grid)
    out["grid.recolor_meets_R"] = str(recolored["Y"] == goal_y(grid)).lower()
    out["grid.empty_series_meets_R"] = str(grid == goal_y(grid)).lower()

    def hist(g) -> str:
        flat = [v for row in g for v in row]
        return joined(flat.count(v) for v in range(10))

    out["grid.hist_input"] = hist(grid)
    out["grid.hist_goal"] = hist(goal_y(grid))
    return out


def compare_facts(reported: dict[str, str]) -> dict:
    """Two implementations, one set of questions. Every fact must be compared."""
    expected = python_facts()
    disagreements = [
        {"fact": k, "lean": reported.get(k), "python": v}
        for k, v in sorted(expected.items())
        if reported.get(k) != v
    ]
    unclaimed = sorted(set(reported) - set(expected))
    if unclaimed:
        disagreements += [
            {"fact": k, "lean": reported[k], "python": None} for k in unclaimed
        ]
    return {
        "ok": not disagreements,
        "compared": len(expected),
        "disagreements": disagreements,
    }


def run_lean(require: bool) -> dict:
    """Optional independent corroboration. Lean agrees or disagrees; it never grades."""
    lean_dir = ROOT / "vv" / "lean"
    files = sorted(lean_dir.glob("*.lean"))
    binary = None
    for candidate in (Path.home() / ".elan" / "bin" / "lean", Path("/usr/local/bin/lean")):
        if candidate.is_file():
            binary = str(candidate)
            break
    if binary is None:
        from shutil import which

        binary = which("lean")
    if binary is None or not files:
        detail = "lean is not installed" if binary is None else "no .lean files found"
        return {
            "status": "unavailable" if require else "skipped",
            "ok": not require,
            "detail": detail,
            "files": [],
        }
    results = []
    for path in files:
        source = path.read_text(encoding="utf-8")
        banned = [why for pattern, why in LEAN_FORBIDDEN if pattern.search(source)]
        if banned:
            results.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "ok": False,
                    "exit": None,
                    "output": f"refused before checking: file uses {', '.join(banned)}",
                }
            )
            continue
        proc = subprocess.run(
            [binary, str(path)], capture_output=True, text=True, cwd=lean_dir, check=False
        )
        output = (proc.stdout + proc.stderr).strip()
        noise = [ln for ln in output.splitlines() if not ln.startswith("fact ")]
        # Lean warns on `sorry` but still exits 0, so a clean exit is not enough.
        clean = proc.returncode == 0 and not noise
        results.append(
            {
                "file": str(path.relative_to(ROOT)),
                "ok": clean,
                "exit": proc.returncode,
                "output": output[:2000],
            }
        )
    reported: dict[str, str] = {}
    for row in results:
        for match in re.finditer(r"^fact ([\w.]+)=(.*)$", row["output"], re.MULTILINE):
            reported[match.group(1)] = match.group(2)
    cross = compare_facts(reported)
    return {
        "status": "checked",
        "ok": all(r["ok"] for r in results) and cross["ok"],
        "detail": "Lean corroborates the finite facts. It does not certify the Python kernel.",
        "files": results,
        "cross_check": cross,
    }


# ---------------------------------------------------------------- reporting


def render(report: dict) -> str:
    lines = []
    cov = report["coverage"]
    lines.append("coverage")
    for obj in cov["objectives"]:
        lines.append(f"  [{'ok' if obj['met'] else 'XX'}] {obj['objective']}: {obj['detail']}")
    for domain in report["domains"]:
        lines.append("")
        lines.append(f"{domain['id']}  ({domain['source']})")
        for case in domain["cases"]:
            mark = "ok" if case["ok"] else "XX"
            observed = f"{case['observed']['outcome']}/{case['observed']['exit']}"
            lines.append(f"  [{mark}] {case['id']:<32} {case['entry']:<8} {observed}")
            for obj in case["objectives"]:
                if not obj["met"]:
                    lines.append(f"       -> {obj['objective']}: {obj['detail']}")
        for prop in domain["properties"]:
            mark = "ok" if prop["met"] else "XX"
            lines.append(f"  [{mark}] {prop['objective']:<32} {prop['detail']}")
    lean = report.get("lean")
    if lean:
        lines.append("")
        lines.append(f"lean  ({lean['status']}): {lean['detail']}")
        for row in lean["files"]:
            lines.append(f"  [{'ok' if row['ok'] else 'XX'}] {row['file']}")
            if not row["ok"]:
                lines.append(f"       -> {row['output'][:500]}")
        cross = lean.get("cross_check")
        if cross:
            mark = "ok" if cross["ok"] else "XX"
            lines.append(
                f"  [{mark}] {'cross_check':<32} "
                f"{cross['compared']} facts compared against the Python kernel"
            )
            for row in cross["disagreements"]:
                lines.append(
                    f"       -> {row['fact']}: lean {row['lean']!r} vs python {row['python']!r}"
                )
    lines.append("")
    lines.append("V&V objectives met" if report["ok"] else "V&V objectives NOT met")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vv",
        description="Run the realize verification & validation matrix across declared domains.",
    )
    parser.add_argument("--config", default=str(ROOT / "vv" / "domains.json"))
    parser.add_argument("--domain", action="append", default=None, help="run only these domain ids")
    parser.add_argument("--report", default=None, help="write the full report JSON here")
    parser.add_argument("--lean", action="store_true", help="also run the Lean corroboration")
    parser.add_argument(
        "--lean-required",
        action="store_true",
        help="fail instead of skipping when Lean is not installed",
    )
    args = parser.parse_args(argv)

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    if config.get("schema_version") != CONFIG_VERSION:
        sys.stderr.write(f"vv: unsupported config version {config.get('schema_version')!r}\n")
        return 1
    domains = config["domains"]
    if args.domain:
        domains = [d for d in domains if d["id"] in set(args.domain)]
        if not domains:
            sys.stderr.write(f"vv: no domain matches {args.domain}\n")
            return 1

    coverage = run_coverage(config["domains"])
    results = [run_domain(d) for d in domains]
    lean: dict[str, Any] | None = None
    if args.lean or args.lean_required:
        lean = run_lean(require=args.lean_required)

    report = {
        "schema_version": CONFIG_VERSION,
        "generated_by": "scripts/vv.py",
        "realize_version": __version__,
        "note": "This report records observations. It is not a certificate and it is not a verdict.",
        "coverage": coverage,
        "domains": results,
        "lean": lean,
        "ok": coverage["ok"] and all(d["ok"] for d in results) and (lean is None or lean["ok"]),
    }
    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sys.stderr.write(render(report) + "\n")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
