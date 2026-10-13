import pytest
from simplibs.path.logic.transformers._helpers import is_valid_suffix


@pytest.mark.parametrize("suffix", ["", ".py", ".txt", ".tar.gz", ".v2", ".PY", ".a b", ".é"])
def test_is_valid_suffix_accepts_suffix_shapes(suffix) -> None:
    assert is_valid_suffix(suffix) is True


@pytest.mark.parametrize("suffix", [".", "py", "txt", "/x", ".a/b", ".a\\b", ".a\0b", " .py", "a.py"])
def test_is_valid_suffix_rejects_everything_else(suffix) -> None:
    assert is_valid_suffix(suffix) is False
