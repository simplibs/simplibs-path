from pathlib import Path
import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.path.logic.transformers._validations import raise_path_has_no_name_error


@pytest.mark.parametrize(
    "path",
    [
        Path("/"),
        Path("."),
        Path(".."),
        Path(""),
    ],
)
def test_raise_path_has_no_name_error_contract(subtests, path) -> None:
    """Verify raise_path_has_no_name_error produces a well-formed ParamError card."""

    def raising_wrapper(target_path):
        raise_path_has_no_name_error(target_path)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(path,),
        exception_type=ParamError,
        error_name="PATH_HAS_NO_NAME",
        label=f"path '{path}'",
        expected="A path ending with a file or directory name, e.g. 'dir/report.txt'.",
        value=str(path),
        problem=(
            f"Path '{path}' has no final name component.",
            "It is empty, the current directory ('.'), '..', or a filesystem root.",
        ),
        how_to_fix=(
            "Provide a path that ends with a file or directory name.",
            "Normalize the path with `normalize_path` first if it is '.' or '..'.",
        ),
        verbose=False,
    )