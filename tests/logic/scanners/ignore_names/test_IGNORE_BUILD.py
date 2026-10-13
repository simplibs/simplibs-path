from simplibs.path.logic.scanners.ignore_names import IGNORE_BUILD


def test_ignore_build_contains_unmistakable_artifacts() -> None:
    for name in ("__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", ".nox", "htmlcov", ".coverage"):
        assert name in IGNORE_BUILD


def test_ignore_build_contains_glob_patterns() -> None:
    assert "*.egg-info" in IGNORE_BUILD
    assert ".coverage.*" in IGNORE_BUILD


def test_ignore_build_no_longer_hides_ambiguous_output_folders() -> None:
    """`build`, `dist`, `site`, `_build` moved to IGNORE_GENERIC."""
    for name in ("build", "dist", "site", "_build"):
        assert name not in IGNORE_BUILD


def test_ignore_build_is_immutable() -> None:
    assert isinstance(IGNORE_BUILD, frozenset)
