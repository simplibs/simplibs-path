import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.path.logic.scanners._validations import raise_ignore_names_not_names_error


@pytest.mark.parametrize("value", [".git", "node_modules", "x"])
def test_raise_ignore_names_not_names_error_contract(subtests, value) -> None:
    """Verify raise_ignore_names_not_names_error produces a well-formed ParamError card."""

    def raising_wrapper(target_value):
        raise_ignore_names_not_names_error(target_value)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(value,),
        exception_type=ParamError,
        error_name="IGNORE_NAMES_NOT_A_COLLECTION",
        label="ignore_names",
        expected="A collection of entry names, e.g. a tuple, list, set or frozenset of strings.",
        value=value,
        problem=(
            f"A single string {value!r} was passed instead of a collection of names.",
            "A string is iterable, so it would be silently split into single characters.",
        ),
        how_to_fix=(
            f"Wrap the name in a collection: ignore_names=({value!r},).",
            "Extend the defaults with a union: DEFAULT_IGNORE_NAMES | {'my_dir'}.",
        ),
        verbose=False,
    )
