from simplibs.path.logic.checks._helpers.constants import MAX_NAME_LENGTH


def test_max_name_length_is_255() -> None:
    assert MAX_NAME_LENGTH == 255
