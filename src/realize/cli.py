"""CLI: check is the product. synthesize never emits a verdict."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from realize.checker import check
from realize.demos import DEMO_NAMES, run_demo
from realize.spec import load_spec
from realize.verdicts import EXIT, AdapterError, Verdict


def _dump(obj: Any) -> None:
    sys.stdout.write(json.dumps(obj, indent=2, sort_keys=True))
    sys.stdout.write("\n")


def _schema_text() -> str:
    try:
        from importlib.resources import files

        return files("realize").joinpath("data", "realize.v0.json").read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, OSError):
        here = Path(__file__).resolve().parent
        for p in (
            here / "data" / "realize.v0.json",
            here.parents[1] / "schema" / "realize.v0.json",
            here.parents[2] / "schema" / "realize.v0.json",
        ):
            if p.is_file():
                return p.read_text(encoding="utf-8")
    raise AdapterError("realize.v0 schema file is not installed")


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="realize",
        description="Independent checker for value-conditioned operator synthesis.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", help="check a candidate against a trusted spec")
    p_check.add_argument("spec")
    p_check.add_argument("candidate")

    p_syn = sub.add_parser("synthesize", help="emit candidates only; no verdict")
    p_syn.add_argument("spec")

    p_demo = sub.add_parser("demo", help="reproduce a bundled paper demo")
    p_demo.add_argument("name", choices=DEMO_NAMES)

    p_ex = sub.add_parser("explain", help="print a certificate witness as prose")
    p_ex.add_argument("certificate")

    sub.add_parser("schema", help="print realize.v0 JSON schema")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "schema":
            text = _schema_text()
            sys.stdout.write(text)
            if not text.endswith("\n"):
                sys.stdout.write("\n")
            return 0
        if args.cmd == "explain":
            cert = json.loads(Path(args.certificate).read_text(encoding="utf-8"))
            sys.stderr.write(_explain(cert))
            sys.stderr.write("\n")
            _dump(cert)
            return 0
        if args.cmd == "check":
            cert = check(args.spec, args.candidate)
            _dump(cert)
            return EXIT[Verdict(cert["verdict"])]
        if args.cmd == "synthesize":
            from realize.synthesize import synthesize_with_coverage

            spec = load_spec(args.spec)
            cov = synthesize_with_coverage(spec)
            for c in cov["candidates"]:
                if "verdict" in c:
                    raise AdapterError("internal error: synthesize emitted a verdict")
            _dump({"candidates": cov["candidates"], "exhausted": cov.get("exhausted")})
            return 0
        if args.cmd == "demo":
            result = run_demo(args.name)
            _dump(result)
            return 0 if result.get("ok") else 1
        parser.error("unknown command")
        return 1
    except AdapterError as exc:
        sys.stderr.write(f"adapter: {exc}\n")
        return EXIT["adapter"]
    except Exception as exc:  # noqa: BLE001 — fail closed, never a forged PASS
        sys.stderr.write(f"adapter: {exc}\n")
        return EXIT["adapter"]


def _explain(cert: dict) -> str:
    v = cert.get("verdict")
    w = cert.get("witness", {})
    sid = cert.get("spec_id")
    return f"{sid}: {v}. witness={json.dumps(w, sort_keys=True)}"


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(run(argv))


if __name__ == "__main__":
    main()
