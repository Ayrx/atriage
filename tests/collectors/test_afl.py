from atriage.collectors import afl

import os.path


def test_parse_fuzzer_stats():
    samples_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../", "samples")
    r = afl.AFLCollector(None)
    with open(os.path.join(samples_dir, "fuzzer_stats")) as f:
        assert r._parse_fuzzer_stats(f) == "./harness @@"
