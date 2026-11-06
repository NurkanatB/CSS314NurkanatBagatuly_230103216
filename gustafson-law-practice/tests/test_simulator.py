import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from benchmarks import simulator
from benchmarks.fit_gustafson import fit_alpha
from benchmarks.models import amdahl_speedup, gustafson_speedup


def test_gustafson_p1_is_one():
    assert gustafson_speedup(1, 0.3) == pytest.approx(1.0)


def test_amdahl_limit():
    assert amdahl_speedup(1e12, 0.05) == pytest.approx(20.0, rel=1e-6)


def test_forms_equivalent():
    p = np.array([2, 16, 1024])
    assert np.allclose(gustafson_speedup(p, 0.1), 1 + 0.9 * (p - 1))


def test_invalid_inputs():
    with pytest.raises(ValueError):
        gustafson_speedup(4, 1.5)
    with pytest.raises(ValueError):
        amdahl_speedup(0, 0.1)
    with pytest.raises(ValueError):
        simulator.validate_alphas([0.5])
    with pytest.raises(ValueError):
        simulator.processor_counts(100000)


def test_simulate_shape_and_cli(tmp_path):
    df = simulator.simulate([0.04, 0.1], 64)
    assert set(df["alpha"]) == {0.04, 0.1} and df["P"].max() == 64
    rc = simulator.main(["--alpha", "0.04", "--max-processors", "32", "--csv", str(tmp_path / "o.csv"),
                         "--plot-dir", str(tmp_path)])
    assert rc == 0 and (tmp_path / "o.csv").exists() and (tmp_path / "efficiency_comparison.pdf").exists()
    assert simulator.main(["--alpha", "0.9", "--no-plots", "--csv", str(tmp_path / "x.csv")]) == 2


def test_fit_recovers_alpha_exactly():
    p = np.array([1, 2, 4, 8, 16], dtype=float)
    fit = fit_alpha(p, gustafson_speedup(p, 0.07))
    assert fit["alpha"] == pytest.approx(0.07)
