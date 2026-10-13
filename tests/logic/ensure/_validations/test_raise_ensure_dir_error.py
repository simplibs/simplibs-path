from pathlib import Path
import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import AccessError
from simplibs.path.logic.ensure._validations import raise_ensure_dir_error


@pytest.mark.parametrize("path", [Path("restricted/dir"), Path("system/path")])
def test_raise_ensure_dir_error_contract(subtests, path) -> None:
    """Verify raise_ensure_dir_error produces a well-formed AccessError card."""

    caught_exc = ValueError("Permission denied")

    def raising_wrapper(target_path):
        raise_ensure_dir_error(target_path, caught_exc)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(path,),
        exception_type=AccessError,
        error_name="DIRECTORY_CREATION_FAILED",
        label=f"directory '{path}'",
        expected="A writable parent filesystem location where directory can be created.",
        value=str(path),
        problem=(
            f"Failed to guarantee directory at '{path}'.",
        ),
        how_to_fix=(
            f"Check write permissions for parent directory '{path.parent}'.",
            "Verify that the storage device is mounted and has sufficient free space.",
        ),
        verbose=False,
    )