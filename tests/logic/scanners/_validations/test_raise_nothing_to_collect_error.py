from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.path.logic.scanners._validations import raise_nothing_to_collect_error


def test_raise_nothing_to_collect_error_contract(subtests) -> None:
    """Verify raise_nothing_to_collect_error produces a well-formed ParamError card."""

    def raising_wrapper():
        raise_nothing_to_collect_error()

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(),
        exception_type=ParamError,
        error_name="NOTHING_TO_COLLECT",
        label="collect_files, collect_dirs",
        expected="At least one of collect_files or collect_dirs set to True.",
        value="collect_files=False, collect_dirs=False",
        problem=(
            "Both collect_files and collect_dirs are False.",
            "Nothing could ever be collected, so the scan would be pointless.",
        ),
        how_to_fix=(
            "Set collect_files=True to collect files.",
            "Set collect_dirs=True to collect directories.",
        ),
        verbose=False,
    )
