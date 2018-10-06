# flake8: noqa
from atriage.asan import feed_crashes

import pytest


def test_command_without_index():
    with pytest.raises(IndexError):
        feed_crashes(None, "command", None, None)
