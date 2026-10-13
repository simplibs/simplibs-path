from pathlib import Path
import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import StateError
from simplibs.path.logic.ensure._validations import raise_ensure_file_not_a_file_error


@pytest.mark.parametrize("path", [Path("some_dir"), Path("sub/folder")])
def test_raise_ensure_file_not_a_file_error_contract(subtests, path) -> None:
    """Verify raise_ensure_file_not_a_file_error produces a well-formed StateError card."""

    def raising_wrapper(target_path):
        raise_ensure_file_not_a_file_error(target_path)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(path,),
        exception_type=StateError,
        error_name="PATH_IS_NOT_A_FILE",
        label=f"path '{path}'",
        expected="A regular file path or a non-existent path where a file can be created.",
        value=str(path),
        problem=(
            f"Expected file at '{path}', but an existing directory was found at this location.",
        ),
        how_to_fix=(
            "Provide a path pointing to a file rather than a directory.",
            f"Remove or rename the existing directory at '{path}' if a file is intended.",
        ),
        verbose=False,
    )