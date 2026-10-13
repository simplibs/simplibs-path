from pathlib import Path
import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import NotFoundError
from simplibs.path.logic.scanners._validations import raise_collect_paths_not_found_error


@pytest.mark.parametrize("path", [Path("missing/dir"), Path("another")])
def test_raise_collect_paths_not_found_error_contract(subtests, path) -> None:
    """Verify raise_collect_paths_not_found_error produces a well-formed NotFoundError card."""

    def raising_wrapper(target_path):
        raise_collect_paths_not_found_error(target_path)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(path,),
        exception_type=NotFoundError,
        error_name="COLLECT_PATHS_ROOT_NOT_FOUND",
        label=f"root directory '{path}'",
        expected="An existing directory path to use as the root for path collection.",
        value=str(path),
        problem=(
            f"Cannot scan directory tree at '{path}'.",
            "The specified root directory does not exist on disk.",
        ),
        how_to_fix=(
            f"Verify that the path '{path}' exists before collecting paths from it.",
            "Ensure parent directories are correctly spelled and accessible.",
        ),
        verbose=False,
    )
