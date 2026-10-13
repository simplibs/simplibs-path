from pathlib import Path
import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import AccessError
from simplibs.path.logic.transformers._validations import raise_normalize_path_error


@pytest.mark.parametrize(
    "path, caught_exc",
    [
        ("~/some/dir", OSError("device not ready")),
        (Path("loop/a"), RuntimeError("Symlink loop from 'loop/a'")),
        ("bad\0path", ValueError("embedded null byte")),
    ],
)
def test_raise_normalize_path_error_contract(subtests, path, caught_exc) -> None:
    """Verify raise_normalize_path_error produces a well-formed AccessError card."""

    def raising_wrapper(target_path, exc):
        raise_normalize_path_error(target_path, exc)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(path, caught_exc),
        exception_type=AccessError,
        error_name="PATH_NORMALIZATION_FAILED",
        label=f"path '{path}'",
        expected="A valid path string or Path instance that can be resolved on this system.",
        value=str(path),
        problem=(
            f"Could not resolve or normalize path '{path}'.",
            # f"System error details: {caught_exc}",
        ),
        how_to_fix=(
            "Check for recursive or circular symlinks on the path.",
            "Ensure the path contains no null bytes or characters invalid for the operating system.",
            "Ensure the path format is valid for the operating system.",
        ),
        verbose=False,
    )
