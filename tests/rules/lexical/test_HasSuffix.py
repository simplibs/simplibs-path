from pathlib import Path
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.path.rules import HasSuffix


def test_has_suffix_contract(subtests) -> None:
    """Verify the complete contract of the HasSuffix rule."""
    assert_rule_contract(
        subtests,
        rule=HasSuffix(".py", ".md"),
        valid_values=["a.py", Path("x/b.MD"), "dir/c.py", "readme.md", "pkg.py"],
        invalid_values=["a.txt", "a.pyc", ".py", "noext", "a.py.bak", "", "   ", "a\0.py", None, 5, b"a.py", []],
        expected_error_name="HAS_SUFFIX_ERROR",
        expected_description="suffix one of '.py', '.md'",
        rule_factory=HasSuffix,
        invalid_init_params=[
            ((), {}),                          # no suffix at all
            (("py",), {}),                     # missing leading dot
            ((".",), {}),                      # a lone dot
            (("/x",), {}),                     # path separator
            ((5,), {}),                        # not a string
            ((None,), {}),
            ((".py",), {"ignore_case": "yes"}),  # not a bool
        ],
        verbose=False,
    )


def test_has_suffix_single_suffix_description() -> None:
    assert HasSuffix(".py").describe() == "suffix '.py'"


def test_has_suffix_case_sensitive_description() -> None:
    assert HasSuffix(".py", ignore_case=False).describe() == "suffix '.py' (case-sensitive)"
    assert HasSuffix(".py", ".md", ignore_case=False).describe() == "suffix one of '.py', '.md' (case-sensitive)"


@pytest.mark.parametrize("name, expected", [("A.PY", True), ("a.Py", True), ("a.py", True)])
def test_has_suffix_ignores_case_by_default(name, expected) -> None:
    assert HasSuffix(".py").is_valid(name) is expected


def test_has_suffix_can_be_case_sensitive() -> None:
    rule = HasSuffix(".py", ignore_case=False)
    assert rule.is_valid("a.py") is True
    assert rule.is_valid("a.PY") is False


def test_has_suffix_supports_compound_suffixes() -> None:
    rule = HasSuffix(".tar.gz")
    assert rule.is_valid("archive.tar.gz") is True
    assert rule.is_valid("archive.gz") is False
    assert rule.is_valid("archive.tar") is False


def test_has_suffix_empty_suffix_means_no_suffix() -> None:
    rule = HasSuffix("")
    assert rule.is_valid("Makefile") is True
    assert rule.is_valid(".bashrc") is True
    assert rule.is_valid("a.txt") is False


def test_has_suffix_empty_suffix_can_be_combined_with_others() -> None:
    rule = HasSuffix("", ".md")
    assert rule.is_valid("Makefile") is True
    assert rule.is_valid("a.md") is True
    assert rule.is_valid("a.py") is False


def test_has_suffix_a_name_that_is_only_the_suffix_does_not_match() -> None:
    """`.py` as a whole name is a hidden file without an extension."""
    assert HasSuffix(".py").is_valid(".py") is False


def test_has_suffix_looks_at_the_name_not_the_directories() -> None:
    assert HasSuffix(".py").is_valid("dir.py/readme.txt") is False


def test_has_suffix_is_lexical_a_directory_name_matches_too(tmp_path) -> None:
    (tmp_path / "pkg.py").mkdir()
    assert HasSuffix(".py").is_valid(tmp_path / "pkg.py") is True


def test_has_suffix_stores_the_given_suffixes() -> None:
    rule = HasSuffix(".py", ".md")
    assert rule.suffixes == (".py", ".md")
    assert rule.ignore_case is True


def test_has_suffix_ignore_case_must_be_keyword_only() -> None:
    with pytest.raises(ParamError):
        HasSuffix(".py", True)


def test_has_suffix_card_for_a_path_without_the_suffix(subtests) -> None:
    rule = HasSuffix(".py", ".md")
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("notes.txt", Kwargs(value_name="source", context="step")),
        exception_type=ValidationError,
        error_name="HAS_SUFFIX_ERROR",
        label="source",
        context="step",
        value="notes.txt",
        expected="a path with suffix one of '.py', '.md'",
        problem="Path 'notes.txt' does not have suffix one of '.py', '.md'.",
        how_to_fix="Provide a path with suffix one of '.py', '.md'.",
        exception=ValueError,
        verbose=False,
    )


def test_has_suffix_card_for_a_non_path(subtests) -> None:
    assert_exception_function(
        subtests,
        func=HasSuffix(".py").validate,
        invalid_params=(5, Kwargs(value_name="source")),
        exception_type=ValidationError,
        error_name="HAS_SUFFIX_ERROR",
        label="source",
        value=5,
        expected="a path with suffix '.py'",
        problem="Value 5 of type 'int' is not a string or Path.",
        how_to_fix="Provide a path as a str or a Path object.",
        exception=TypeError,
        verbose=False,
    )
