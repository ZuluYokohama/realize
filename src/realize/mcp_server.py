"""MCP adapter. Untrusted caller. No realize_solve tool."""

from __future__ import annotations

from realize.checker import check
from realize.cli import _explain
from realize.demos import DEMO_NAMES, run_demo
from realize.spec import load_spec
from realize.verdicts import AdapterError

TOOL_NAMES = (
    "realize_check",
    "realize_synthesize",
    "realize_explain",
    "realize_demo",
)

SYNTHESIZE_DESCRIPTION = (
    "Propose candidates for a realize.v0 spec. Returns candidates only. "
    "Call realize_check before claiming success."
)


def tool_names() -> tuple[str, ...]:
    return TOOL_NAMES


def realize_check(spec: dict, candidate: dict) -> dict:
    return check(spec, candidate)


def realize_synthesize(spec: dict) -> dict:
    from realize.synthesize import synthesize_with_coverage

    cov = synthesize_with_coverage(load_spec(spec))
    return {
        "candidates": cov["candidates"],
        "exhausted": cov.get("exhausted"),
        "instruction": "call realize_check before claiming success",
    }


def realize_explain(certificate: dict) -> dict:
    return {"prose": _explain(certificate), "certificate": certificate}


def realize_demo(name: str) -> dict:
    if name not in DEMO_NAMES:
        raise AdapterError(f"unknown demo {name}")
    return run_demo(name)


def main() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise SystemExit("pip install 'realize[mcp]'") from exc

    mcp = FastMCP("realize")

    @mcp.tool(name="realize_check")
    def _check(spec: dict, candidate: dict) -> dict:
        return realize_check(spec, candidate)

    @mcp.tool(name="realize_synthesize", description=SYNTHESIZE_DESCRIPTION)
    def _syn(spec: dict) -> dict:
        return realize_synthesize(spec)

    @mcp.tool(name="realize_explain")
    def _exp(certificate: dict) -> dict:
        return realize_explain(certificate)

    @mcp.tool(name="realize_demo")
    def _demo(name: str) -> dict:
        return realize_demo(name)

    mcp.run()


if __name__ == "__main__":
    main()
