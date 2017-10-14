from atriage.collect import Results, get_crash_statistics

import pytest


r = Results([
    set(["test_case_1", "test_case_2"]),
    set(["test_case_3"])
])


def test_get_crash_statistics():
    res, total = get_crash_statistics(r)

    assert res[0] == (0, "2")
    assert res[1] == (1, "+1")
    assert total == 3


def test_all_crashes_property():
    assert r.all_crashes == set(["test_case_1", "test_case_2", "test_case_3"])


def test_new_crashes_property():
    assert r.new_crashes == set(["test_case_3"])


def test_raw_crashes_property():
    assert r.raw_crashes == [
        set(["test_case_1", "test_case_2"]),
        set(["test_case_3"])
    ]


def test_get_result_set_negative_index():
    with pytest.raises(IndexError):
        r.get_result_set(-2)


def test_get_result_set_invalid():
    with pytest.raises(IndexError):
        r.get_result_set(2)


def test_get_result_set_empty():
    r_empty = Results([])
    with pytest.raises(IndexError):
        r_empty.get_result_set(-1)


def test_get_result_set_latest():
    r.get_result_set(-1) == set(["test_case_3"])


def test_get_result_set():
    r.get_result_set(0) == set(["test_case_1", "test_case_2"])
    r.get_result_set(1) == set(["test_case_3"])
