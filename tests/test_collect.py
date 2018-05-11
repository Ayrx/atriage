from atriage.db import AtriageDB, get_crash_statistics

import pytest

import sqlite3

import os


sample_db = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "samples", "atriage.db")

sample_path = os.path.dirname(sample_db)

r = AtriageDB(sample_db)


def test_get_crash_statistics():
    res, total = get_crash_statistics(r)

    assert res[0] == (0, "2")
    assert res[1] == (1, "+1")
    assert total == 3


def test_make_relative_path():
    assert r._make_relative_path("testfile") == os.path.join(
        sample_path, "testfile")


def test_all_crashes_property():
    assert r.all_crashes == set([
        (1, os.path.join(sample_path, "test_case_1")),
        (2, os.path.join(sample_path, "test_case_2")),
        (3, os.path.join(sample_path, "test_case_3"))
    ])


def test_new_crashes_property():
    assert r.new_crashes == set([
        (3, os.path.join(sample_path, "test_case_3"))
    ])


def test_raw_crashes_property():
    assert r.raw_crashes == [
        set([os.path.join(sample_path, "test_case_1"),
             os.path.join(sample_path, "test_case_2")]),
        set([os.path.join(sample_path, "test_case_3")])
    ]


def test_get_result_set_negative_index():
    with pytest.raises(IndexError):
        r.get_result_set(-2)


def test_get_result_set_invalid():
    with pytest.raises(IndexError):
        r.get_result_set(2)


def test_get_result_set_latest():
    r.get_result_set(-1) == set([
        (3, os.path.join(sample_path, "test_case_3"))
    ])


def test_get_result_set():
    r.get_result_set(0) == set([(1, os.path.join(sample_path, "test_case_1")),
                                (2, os.path.join(sample_path, "test_case_2"))])
    r.get_result_set(1) == set([(3, os.path.join(sample_path, "test_case_3"))])
