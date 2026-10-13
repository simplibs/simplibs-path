import os
import pytest
from simplibs.exception import ParamError
from simplibs.path.logic.scanners._helpers import build_ignore_matcher
from simplibs.path.logic.scanners.ignore_names import DEFAULT_IGNORE_NAMES


@pytest.mark.parametrize("collection", [{".git", "node_modules"}, (".git", "node_modules"), [".git", "node_modules"], frozenset({".git", "node_modules"})])
def test_matcher_accepts_any_collection_of_names(collection) -> None:
    matches = build_ignore_matcher(collection)
    assert matches(".git") is True
    assert matches("node_modules") is True
    assert matches("src") is False


@pytest.mark.parametrize("nothing", [None, set(), (), []])
def test_matcher_ignores_nothing_for_none_or_empty(nothing) -> None:
    matches = build_ignore_matcher(nothing)
    assert matches(".git") is False
    assert matches("anything") is False


def test_matcher_matches_whole_names_not_substrings() -> None:
    matches = build_ignore_matcher({"build"})
    assert matches("build") is True
    assert matches("rebuild") is False
    assert matches("build2") is False


def test_matcher_supports_glob_patterns() -> None:
    matches = build_ignore_matcher({"*.egg-info", ".coverage.*", "tmp_?", "[ab]file"})
    assert matches("pkg.egg-info") is True
    assert matches(".coverage.host.123") is True
    assert matches("tmp_1") is True
    assert matches("afile") is True
    assert matches("cfile") is False
    assert matches("pkg.egg") is False
    assert matches("tmp_12") is False


def test_matcher_mixes_exact_names_and_patterns() -> None:
    matches = build_ignore_matcher({".git", "*.egg-info"})
    assert matches(".git") is True
    assert matches("x.egg-info") is True
    assert matches("src") is False


@pytest.mark.skipif(os.name != "nt", reason="Case-insensitive on Windows only")
def test_matcher_is_case_insensitive_on_windows() -> None:
    matches = build_ignore_matcher({"Thumbs.db", "*.EGG-INFO"})
    assert matches("THUMBS.DB") is True
    assert matches("pkg.egg-info") is True


@pytest.mark.skipif(os.name == "nt", reason="Case-sensitive off Windows")
def test_matcher_is_case_sensitive_off_windows() -> None:
    matches = build_ignore_matcher({"Thumbs.db"})
    assert matches("Thumbs.db") is True
    assert matches("thumbs.db") is False


@pytest.mark.parametrize("bare_string", [".git", "node_modules", "x", ""])
def test_matcher_rejects_a_single_string(bare_string) -> None:
    """A bare string would be split into characters."""
    with pytest.raises(ParamError):
        build_ignore_matcher(bare_string)


def test_matcher_works_with_the_default_names() -> None:
    matches = build_ignore_matcher(DEFAULT_IGNORE_NAMES)
    for name in (".git", "__pycache__", "node_modules", ".venv", ".DS_Store", "foo.egg-info", ".coverage", ".env"):
        assert matches(name) is True
    for name in ("src", "build", "dist", "env", "README.md"):
        assert matches(name) is False


def test_matcher_does_not_change_the_given_collection() -> None:
    names = {".git", "*.egg-info"}
    build_ignore_matcher(names)
    assert names == {".git", "*.egg-info"}
