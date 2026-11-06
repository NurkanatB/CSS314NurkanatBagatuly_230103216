import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from benchmarks.models import alpha_max, amdahl_speedup, gustafson_speedup
from benchmarks.weak_scale_bench.workload import count_hits, estimate_pi, pi_tolerance


def test_task06_values():
    assert gustafson_speedup(1024, 0.04) == pytest.approx(983.08)
    assert gustafson_speedup(16384, 0.04) == pytest.approx(16384 - 0.04 * 16383)


def test_task07_alpha_max():
    a = alpha_max(8192, 7500)
    assert a == pytest.approx(692 / 8191)
    assert gustafson_speedup(8192, a) == pytest.approx(7500)


def test_task08():
    assert amdahl_speedup(128, 0.08) == pytest.approx(1 / (0.08 + 0.92 / 128))
    assert gustafson_speedup(128, 0.08) == pytest.approx(117.84)


def test_task09():
    assert gustafson_speedup(512, 0.08) == pytest.approx(512 - 0.08 * 511)
    assert gustafson_speedup(2048, 0.08) == pytest.approx(2048 - 0.08 * 2047)


def test_monte_carlo_workload_deterministic_and_valid():
    assert count_hits(10_000, 1) == count_hits(10_000, 1)
    n = 2_000_000
    assert abs(estimate_pi(count_hits(n, 3), n) - 3.14159265) < pi_tolerance(n)
    with pytest.raises(ValueError):
        count_hits(-1, 0)
