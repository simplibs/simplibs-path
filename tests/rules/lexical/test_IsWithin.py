from pathlib import Path
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.path.rules import IsWithin


def test_is_within_contract(subtests, tmp_path) -> None:
    """Verify the complete contract of the IsWithin rule."""
    root = tmp_path / "root"
    root.mkdir()
    assert_rule_contract(
        subtests,
        rule=IsWithin(root),
        valid_values=[root / "a.txt", str(root / "sub" / "b.txt"), root, root / "missing" / "x"],
        invalid_values=[
            tmp_path / "other" / "a.txt",
            root / ".." / "escape.txt",
            tmp_path / "root2" / "a.txt",
            "", "   ", "a\0b", None, 5, b"x",
        ],
        expected_error_name="IS_WITHIN_ERROR",
        expected_description=f"path within {str(root)!r}",
        rule_factory=IsWithin,
        invalid_init_params=[
            ((5,), {}),
            ((None,), {}),
            (("",), {}),
            (("   ",), {}),
            (("a\0b",), {}),
            ((root,), {"resolve_symlinks": "yes"}),
            ((root,), {"allow_equal": 1}),
        ],
        verbose=False,
    )


def test_is_within_allow_equal_false_rejects_the_root_itself(tmp_path) -> None:
    rule = IsWithin(tmp_path, allow_equal=False)
    assert rule.is_valid(tmp_path) is False
    assert rule.is_valid(tmp_path / "a.txt") is True


def test_is_within_options_must_be_keyword_only(tmp_path) -> None:
    with pytest.raises(TypeError):
        IsWithin(tmp_path, False)


def test_is_within_stores_its_parameters(tmp_path) -> None:
    rule = IsWithin(tmp_path, resolve_symlinks=False, allow_equal=False)
    assert rule.root == tmp_path
    assert rule.resolve_symlinks is False
    assert rule.allow_equal is False


def test_is_within_resolves_symlinks_by_default(tmp_path) -> None:
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    try:
        (root / "escape").symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    assert IsWithin(root).is_valid(root / "escape" / "f.txt") is False
    assert IsWithin(root, resolve_symlinks=False).is_valid(root / "escape" / "f.txt") is True


def test_is_within_accepts_a_string_root(tmp_path) -> None:
    assert IsWithin(str(tmp_path)).is_valid(tmp_path / "a.txt") is True


def test_is_within_card(subtests, tmp_path) -> None:
    root = tmp_path / "root"
    outside = tmp_path / "other" / "a.txt"
    assert_exception_function(
        subtests,
        func=IsWithin(root).validate,
        invalid_params=(outside, Kwargs(value_name="target", context="step")),
        exception_type=ValidationError,
        error_name="IS_WITHIN_ERROR",
        label="target",
        context="step",
        value=outside,
        expected=f"a path inside {str(root)!r}",
        problem=f"Path {outside!r} is not inside {str(root)!r}.",
        how_to_fix=f"Provide a path located inside {str(root)!r}.",
        exception=ValueError,
        verbose=False,
    )


def test_is_within_card_for_a_non_path(subtests, tmp_path) -> None:
    assert_exception_function(
        subtests,
        func=IsWithin(tmp_path).validate,
        invalid_params=(5,),
        exception_type=ValidationError,
        error_name="IS_WITHIN_ERROR",
        value=5,
        problem="Value 5 of type 'int' is not a string or Path.",
        exception=TypeError,
        verbose=False,
    )
