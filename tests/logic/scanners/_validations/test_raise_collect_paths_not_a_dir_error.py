from pathlib import Path
import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import StateError
from simplibs.path.logic.scanners._validations import raise_collect_paths_not_a_dir_error


@pytest.mark.parametrize("path", [Path("notes.txt"), Path("some/file.py")])
def test_raise_collect_paths_not_a_dir_error_contract(subtests, path) -> None:
    """Verify raise_collect_paths_not_a_dir_error produces a well-formed StateError card."""

    def raising_wrapper(target_path):
        raise_collect_paths_not_a_dir_error(target_path)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(path,),
        exception_type=StateError,
        error_name="COLLECT_PATHS_NOT_A_DIRECTORY",
        label=f"root directory '{path}'",
        expected="A path pointing to an existing directory that can be scanned.",
        value=str(path),
        problem=(
            f"Cannot collect paths from '{path}'.",
            "Expected a root directory, but an existing regular file was found at this location.",
        ),
        how_to_fix=(
            "Provide a path to a directory instead of a regular file.",
            f"Check if '{path}' was mistakenly passed instead of its parent directory.",
        ),
        verbose=False,
    )
