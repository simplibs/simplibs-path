from pathlib import Path
import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.path.logic.transformers._validations import raise_path_not_within_root_error


@pytest.mark.parametrize(
    "path, root",
    [
        (Path("other/file.txt"), Path("project/src")),
        (Path("a"), Path("b/c")),
    ],
)
def test_raise_path_not_within_root_error_contract(subtests, path, root) -> None:
    """Verify raise_path_not_within_root_error produces a well-formed ParamError card."""

    def raising_wrapper(target_path, target_root):
        raise_path_not_within_root_error(target_path, target_root)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(path, root),
        exception_type=ParamError,
        error_name="PATH_NOT_WITHIN_ROOT",
        label=f"path '{path}'",
        expected=f"A path located inside '{root}'.",
        value=str(path),
        problem=(
            f"Path '{path}' is not located inside the root directory '{root}'.",
            "The path cannot be expressed relative to this root.",
        ),
        how_to_fix=(
            f"Provide a path that starts with '{root}'.",
            "Check that both paths are absolute, or both are relative to the same base.",
            "Normalize both paths with `normalize_path` before comparing them.",
        ),
        verbose=False,
    )
