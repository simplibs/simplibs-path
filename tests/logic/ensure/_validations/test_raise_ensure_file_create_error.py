from pathlib import Path
import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import AccessError
from simplibs.path.logic.ensure._validations import raise_ensure_file_create_error


@pytest.mark.parametrize("path", [Path("readonly/file.txt"), Path("locked.log")])
def test_raise_ensure_file_create_error_contract(subtests, path) -> None:
    """Verify raise_ensure_file_create_error produces a well-formed AccessError card."""
    caught_exc = PermissionError("Permission denied")

    def raising_wrapper(target_path):
        raise_ensure_file_create_error(target_path, caught_exc)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(path,),
        exception_type=AccessError,
        error_name="FILE_CREATION_FAILED",
        label=f"file '{path}'",
        expected="A writable directory location where a new file can be created.",
        value=str(path),
        problem=(
            f"Failed to create file at '{path}'.",
        ),
        how_to_fix=(
            f"Check write permissions for directory '{path.parent}'.",
            "Verify that the storage device is accessible and not read-only.",
        ),
        verbose=False,
    )