from pathlib import Path
import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import AccessError
from simplibs.path.logic.scanners._validations import raise_collect_paths_root_unreadable_error


@pytest.mark.parametrize(
    "path, caught_exc",
    [
        (Path("/root/secure"), PermissionError("Permission denied")),
        (Path("protected_dir"), OSError("Input/output error")),
    ],
)
def test_raise_collect_paths_root_unreadable_error_contract(subtests, path, caught_exc) -> None:
    """Verify raise_collect_paths_root_unreadable_error produces a well-formed AccessError card."""

    def raising_wrapper(target_path, exc):
        raise_collect_paths_root_unreadable_error(target_path, exc)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(path, caught_exc),
        exception_type=AccessError,
        error_name="COLLECT_PATHS_ROOT_UNREADABLE",
        label=f"root directory '{path}'",
        expected="A root directory the current user is allowed to read.",
        value=str(path),
        problem=(
            f"Cannot list the entries of '{path}'.",
            f"OS reported: {caught_exc}",
        ),
        how_to_fix=(
            f"Check read and execute permissions of '{path}'.",
            "Scan a directory you have access to, or run with sufficient permissions.",
        ),
        verbose=False,
    )