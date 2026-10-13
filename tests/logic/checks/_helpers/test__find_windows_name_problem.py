import pytest
from simplibs.path.logic.checks._helpers._find_windows_name_problem import _find_windows_name_problem


@pytest.mark.parametrize("name", ["report.txt", "CONSOLE", "console.txt", "a b", ".gitignore", "COM10"])
def test_find_windows_name_problem_accepts_fine_names(name) -> None:
    """Names that merely resemble reserved ones are fine."""
    assert _find_windows_name_problem(name) is None


@pytest.mark.parametrize(
    "name",
    ["a\\b", "a:b", "a?b", "a*b", 'a"b', "a<b", "a>b", "a|b", "a\x00b", "a\x1fb", "x.", "x ", "CON", "con.TXT", "aux.", "COM0", "LPT3.x"],
)
def test_find_windows_name_problem_reports_problems(name) -> None:
    """Names Windows rejects or alters are reported."""
    assert isinstance(_find_windows_name_problem(name), str)


def test_find_windows_name_problem_reserved_name_ignores_trailing_spaces_before_dot() -> None:
    """`nul .txt` still refers to the device on Windows."""
    assert "NUL" in _find_windows_name_problem("nul .txt")
