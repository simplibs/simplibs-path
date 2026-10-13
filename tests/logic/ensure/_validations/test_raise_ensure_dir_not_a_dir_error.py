from pathlib import Path
import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import StateError
from simplibs.path.logic.ensure._validations import raise_ensure_dir_not_a_dir_error


@pytest.mark.parametrize("path", [Path("file.txt"), Path("document.pdf")])
def test_raise_ensure_dir_not_a_dir_error_contract(subtests, path) -> None:
    """Verify raise_ensure_dir_not_a_dir_error produces a well-formed StateError card."""

    def raising_wrapper(target_path):
        raise_ensure_dir_not_a_dir_error(target_path)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(path,),
        exception_type=StateError,
        error_name="PATH_IS_NOT_A_DIRECTORY",
        label=f"path '{path}'",
        expected="A directory path or a non-existent path where a directory can be created.",
        value=str(path),
        problem=(
            f"Expected directory at '{path}', but an existing file was found at this location.",
        ),
        how_to_fix=(
            "Provide a path to a directory or a location that does not yet exist.",
            f"Remove or rename the existing file at '{path}' if it should be replaced by a directory.",
        ),
        verbose=False,
    )