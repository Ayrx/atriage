from atriage.collect import Results, get_crash_statistics


def test_get_crash_statistics():
    r = Results([
        set(["test_case_1", "test_case_2"]),
        set(["test_case_3"])
    ])
    res, total = get_crash_statistics(r)

    assert res[0] == (0, "2")
    assert res[1] == (1, "+1")
    assert total == 3


def test_all_crashes_property():
    r = Results([
        set(["test_case_1", "test_case_2"]),
        set(["test_case_3"])
    ])

    assert r.all_crashes == set(["test_case_1", "test_case_2", "test_case_3"])


def test_new_crashes_property():
    r = Results([
        set(["test_case_1", "test_case_2"]),
        set(["test_case_3"])
    ])

    assert r.new_crashes == set(["test_case_3"])


def test_raw_crashes_property():
    r = Results([
        set(["test_case_1", "test_case_2"]),
        set(["test_case_3"])
    ])

    assert r.raw_crashes == [
        set(["test_case_1", "test_case_2"]),
        set(["test_case_3"])
    ]
