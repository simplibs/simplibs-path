from pathlib import Path
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.exception import ValidationError
from simplibs.rules.predicates.strings import Contains
from simplibs.rules.testing import assert_rule_contract
from simplibs.path.rules import AnyParentNameIs


def test_any_parent_name_is_contract(subtests) -> None:
    """Verify the complete contract of the AnyParentNameIs rule."""
    assert_rule_contract(
        subtests,
        rule=AnyParentNameIs(Contains("src")),
        valid_values=["src/a.py", Path("/x/src/b.py"), "pkg_src/a", "src/sub/a.py", "x/src/y/z.py"],
        invalid_values=["a.py", "other/a.py", "x/pkg/a.py", "src", "", "a\0b", None, 5],
        expected_description="any parent name: string containing 'src'",
        rule_factory=AnyParentNameIs,
        invalid_init_params=[(("nope",), {}), ((None,), {})],
        check_value=False,
        verbose=False,
    )


def test_any_parent_name_is_every_level_counts() -> None:
    rule = AnyParentNameIs(Contains("src"))
    assert rule.is_valid("src/pkg/a.py") is True        # the top folder
    assert rule.is_valid("x/src/pkg/a.py") is True      # a folder in the middle
    assert rule.is_valid("x/pkg/src/a.py") is True      # the folder directly containing the file
    assert rule.is_valid("x/pkg/a.py") is False


def test_any_parent_name_is_does_not_judge_the_name_of_the_path_itself() -> None:
    rule = AnyParentNameIs(Contains("src"))
    assert rule.is_valid("x/src_file.py") is False
    assert rule.is_valid("x/src") is False


def test_any_parent_name_is_a_bare_name_has_no_folder_above_it() -> None:
    """Unlike `ParentNameIs`, which sees an empty name, there is nothing to judge here."""
    assert AnyParentNameIs(lambda name: True).is_valid("a.py") is False


def test_any_parent_name_is_folders_are_tried_nearest_first() -> None:
    seen: list[str] = []
    AnyParentNameIs(lambda name: seen.append(name) or False).is_valid("a/b/c/f.py")
    assert seen == ["c", "b", "a"]


def test_any_parent_name_is_root_and_double_dot_are_not_names() -> None:
    seen: list[str] = []
    rule = AnyParentNameIs(lambda name: seen.append(name) or False)
    rule.is_valid("../x/f.py")
    rule.is_valid(Path("/a/b/f.py"))
    assert seen == ["x", "b", "a"]


def test_any_parent_name_is_a_plain_callable_is_accepted() -> None:
    assert AnyParentNameIs(lambda name: name == "tests").is_valid("p/tests/deep/a.py") is True


def test_any_parent_name_is_card_is_labelled_with_the_value_name(subtests) -> None:
    assert_exception_function(
        subtests,
        func=AnyParentNameIs(Contains("src")).validate,
        invalid_params=("other/a.py", Kwargs(value_name="source")),
        exception_type=ValidationError,
        error_name="ANY_PARENT_NAME_IS_ERROR",
        label="source",
        value="other/a.py",
        verbose=False,
    )


def test_any_parent_name_is_card_of_a_path_without_a_folder(subtests) -> None:
    assert_exception_function(
        subtests,
        func=AnyParentNameIs(Contains("src")).validate,
        invalid_params=("a.py",),
        exception_type=ValidationError,
        error_name="ANY_PARENT_NAME_IS_ERROR",
        value="a.py",
        verbose=False,
    )


def test_any_parent_name_is_non_path_card_has_its_own_error_name(subtests) -> None:
    assert_exception_function(
        subtests,
        func=AnyParentNameIs(Contains("src")).validate,
        invalid_params=(5,),
        exception_type=ValidationError,
        error_name="ANY_PARENT_NAME_IS_ERROR",
        value=5,
        verbose=False,
    )