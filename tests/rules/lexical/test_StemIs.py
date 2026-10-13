from pathlib import Path
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import Contains
from simplibs.rules.testing import assert_rule_contract
from simplibs.path.rules import StemIs


def test_stem_is_contract(subtests) -> None:
    """Verify the complete contract of the StemIs rule."""
    assert_rule_contract(
        subtests,
        rule=StemIs(Contains("draft")),
        valid_values=["draft_1.txt", Path("dir/my_draft.md"), "draft", "a/draft.tar.gz"],
        invalid_values=["final.txt", "dir_draft/final.txt", "", "a\0b", None, 5],
        expected_description="stem: string containing 'draft'",
        rule_factory=StemIs,
        invalid_init_params=[(("nope",), {}), ((None,), {})],
        check_value=False,
        verbose=False,
    )


def test_stem_is_ignores_the_suffix() -> None:
    rule = StemIs(Contains("py"))
    assert rule.is_valid("a.py") is False       # the stem is just "a"
    assert rule.is_valid("py_tool.txt") is True


def test_stem_is_removes_only_the_last_suffix() -> None:
    assert StemIs(Contains("tar")).is_valid("archive.tar.gz") is True


def test_stem_is_card_is_labelled_with_the_stem(subtests) -> None:
    assert_exception_function(
        subtests,
        func=StemIs(Contains("draft")).validate,
        invalid_params=("final.txt", Kwargs(value_name="source")),
        exception_type=ValidationError,
        error_name="CONTAINS_ERROR",
        label="source.stem",
        value="final",
        verbose=False,
    )
