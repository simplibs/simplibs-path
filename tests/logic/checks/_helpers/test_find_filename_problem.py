import os
import pytest
from simplibs.path.logic.checks._helpers import find_filename_problem


@pytest.mark.parametrize(
    "name",
    ["report.txt", "my file (1).txt", ".bashrc", "archive.tar.gz", "ěščř.txt", "a" * 255, "x", "CONSOLE.txt"],
)
def test_find_filename_problem_accepts_valid_names(name) -> None:
    """Ordinary names — including dotfiles, spaces and non-ASCII letters — are fine."""
    assert find_filename_problem(name) is None


@pytest.mark.parametrize(
    "name, fragment",
    [
        ("", "empty"),
        ("   ", "empty"),
        (".", "reserved directory"),
        ("..", "reserved directory"),
        ("a/b", "separator"),
        ("a\0b", "null byte"),
        ("a\\b", "separator"),
        ("a:b", "forbids"),
        ("a?b", "forbids"),
        ("a*b", "forbids"),
        ('a"b', "forbids"),
        ("a<b", "forbids"),
        ("a>b", "forbids"),
        ("a|b", "forbids"),
        ("a\x01b", "control character"),
        ("name.", "dot or a space"),
        ("name ", "dot or a space"),
        ("con", "reserved Windows"),
        ("CON.txt", "reserved Windows"),
        ("nul.log", "reserved Windows"),
        ("Com1", "reserved Windows"),
        ("lpt9.txt", "reserved Windows"),
        ("a" * 256, "longer"),
        ("é" * 128, "longer"),
    ],
)
def test_find_filename_problem_reports_the_reason(name, fragment) -> None:
    """Every invalid name gets a text naming what is wrong with it."""
    problem = find_filename_problem(name)
    assert problem is not None
    assert fragment in problem


@pytest.mark.parametrize("name", ["", ".", "..", "a/b", "a\0b"])
def test_find_filename_problem_universal_rules_ignore_portable_flag(name) -> None:
    """Rules that hold everywhere apply even when portable=False."""
    assert find_filename_problem(name, portable=False) is not None


def test_find_filename_problem_non_portable_accepts_ordinary_names() -> None:
    """The relaxed mode still accepts normal names."""
    assert find_filename_problem("report.txt", portable=False) is None


@pytest.mark.skipif(os.name == "nt", reason="POSIX-only behavior")
@pytest.mark.parametrize("name", ["a:b", "con", "name.", "a?b"])
def test_find_filename_problem_non_portable_allows_windows_only_problems_on_posix(name) -> None:
    """On POSIX, names that only Windows rejects pass in non-portable mode."""
    assert find_filename_problem(name, portable=False) is None


@pytest.mark.skipif(os.name != "nt", reason="Windows-only behavior")
@pytest.mark.parametrize("name", ["a:b", "con", "name.", "a?b"])
def test_find_filename_problem_non_portable_still_rejects_windows_problems_on_windows(name) -> None:
    """On Windows, the Windows rules apply even in non-portable mode."""
    assert find_filename_problem(name, portable=False) is not None
