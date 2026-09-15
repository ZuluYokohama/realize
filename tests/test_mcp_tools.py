from realize.mcp_server import SYNTHESIZE_DESCRIPTION, tool_names


def test_no_solve_tool():
    names = tool_names()
    assert "realize_solve" not in names
    assert "realize_grade_text" not in names
    assert names == (
        "realize_check",
        "realize_synthesize",
        "realize_explain",
        "realize_demo",
    )
    assert "call realize_check before claiming success" in SYNTHESIZE_DESCRIPTION.lower()
