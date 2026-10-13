from pathlib import Path
import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import OperationError
from simplibs.path.logic.transformers._validations import raise_unique_path_exhausted_error


@pytest.mark.parametrize(
    "path, attempts",
    [
        (Path("out/report.txt"), 1000),
        (Path("data"), 5),
    ],
)
def test_raise_unique_path_exhausted_error_contract(subtests, path, attempts) -> None:
    """Verify raise_unique_path_exhausted_error produces a well-formed OperationError card."""

    def raising_wrapper(target_path, target_attempts):
        raise_unique_path_exhausted_error(target_path, target_attempts)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(path, attempts),
        exception_type=OperationError,
        error_name="UNIQUE_PATH_EXHAUSTED",
        label=f"path '{path}'",
        expected="A path with at least one free numbered variant within the attempt limit.",
        value=str(path),
        problem=(
            f"Could not find a free name for '{path}' after {attempts} attempts.",
            "Every numbered candidate already exists.",
        ),
        how_to_fix=(
            "Clean up the existing numbered variants of this path.",
            "Use a different base name or target directory.",
            "Raise `max_attempts` if that many variants are really needed.",
        ),
        verbose=False,
    )
