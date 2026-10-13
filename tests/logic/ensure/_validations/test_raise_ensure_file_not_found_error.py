from pathlib import Path
import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import NotFoundError
from simplibs.path.logic.ensure._validations import raise_ensure_file_not_found_error


@pytest.mark.parametrize("path", [Path("missing.txt"), Path("config.json")])
def test_raise_ensure_file_not_found_error_contract(subtests, path) -> None:
    """Verify raise_ensure_file_not_found_error produces a well-formed NotFoundError card."""

    def raising_wrapper(target_path):
        raise_ensure_file_not_found_error(target_path)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(path,),
        exception_type=NotFoundError,
        error_name="FILE_NOT_FOUND",
        label=f"file '{path}'",
        expected="An existing file path, or call ensure_file with create=True.",
        value=str(path),
        problem=(
            f"Required file '{path}' does not exist on disk.",
            "Automatic creation was disabled because `create=False` was passed.",
        ),
        how_to_fix=(
            f"Ensure the file exists at '{path}' before invoking ensure_file.",
            "Set `create=True` if you want ensure_file to create missing files automatically.",
        ),
        verbose=False,
    )