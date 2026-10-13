from pathlib import Path
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import Contains
from simplibs.rules.testing import assert_rule_contract
from simplibs.path.rules import ParentNameIs


def test_parent_name_is_contract(subtests) -> None:
    """Verify the complete contract of the ParentNameIs rule."""
    assert_rule_contract(
        subtests,
        rule=ParentNameIs(Contains("src")),
        valid_values=["src/a.py", Path("/x/src/b.py"), "pkg_src/a", "a/src_old/b.txt"],
        invalid_values=["a.py", "other/a.py", "src/sub/a.py", "src", "", "a\0b", None, 5],
        expected_description="parent name: string containing 'src'",
        rule_factory=ParentNameIs,
        invalid_init_params=[(("nope",), {}), ((None,), {})],
        check_value=False,
        verbose=False,
    )


def test_parent_name_is_only_the_directly_containing_folder() -> None:
    rule = ParentNameIs(Contains("src"))
    assert rule.is_valid("src/pkg/a.py") is False
    assert rule.is_valid("x/src/a.py") is True


def test_parent_name_is_a_bare_name_has_an_empty_parent_name() -> None:
    assert ParentNameIs(lambda name: name == "").is_valid("a.py") is True


def test_parent_name_is_card_is_labelled_with_the_part(subtests) -> None:
    assert_exception_function(
        subtests,
        func=ParentNameIs(Contains("src")).validate,
        invalid_params=("other/a.py", Kwargs(value_name="source")),
        exception_type=ValidationError,
        error_name="CONTAINS_ERROR",
        label="source.parent name",
        value="other",
        verbose=False,
    )


def test_parent_name_is_non_path_card_has_its_own_error_name(subtests) -> None:
    assert_exception_function(
        subtests,
        func=ParentNameIs(Contains("src")).validate,
        invalid_params=(5,),
        exception_type=ValidationError,
        error_name="PARENT_NAME_IS_ERROR",
        value=5,
        verbose=False,
    )
