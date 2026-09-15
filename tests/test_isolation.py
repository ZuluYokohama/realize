import re
from pathlib import Path

import realize.checker as checker


def test_checker_does_not_import_synthesize():
    src = Path(checker.__file__).read_text(encoding="utf-8")
    assert not re.search(
        r"^\s*(from|import)\s+realize\.synthesize", src, re.MULTILINE
    )
    assert "from realize import synthesize" not in src
    assert "realize.synthesize" not in checker.__dict__.get("__all__", ())
