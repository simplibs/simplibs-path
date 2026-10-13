import pytest
from simplibs.rules import IsTyping
from simplibs.path.annotations import RecursionDepth


@pytest.mark.parametrize(
    "value",
    [True, False, 0, 1, 42, 100],
)
def test_recursion_depth_accepts_valid_values(value) -> None:
    """Booleans and non-negative integers are valid recursion depths."""
    assert IsTyping(RecursionDepth).is_valid(value)


@pytest.mark.parametrize(
    "value",
    [-1, -42, 3.5, "True", "0", None, [1], {"depth": 1}],
)
def test_recursion_depth_rejects_invalid_values(value) -> None:
    """Negative integers, floats, strings, and other types are rejected."""
    assert not IsTyping(RecursionDepth).is_valid(value)