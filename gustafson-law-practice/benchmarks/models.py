"""Closed-form scaling models shared by simulator, fitting script and tests."""
from __future__ import annotations

import numpy as np


def _check_fraction(value: float, name: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1], got {value}")


def _check_p(p) -> None:
    if np.any(np.asarray(p) < 1):
        raise ValueError("processor count P must be >= 1")


def gustafson_speedup(p, alpha: float):
    """Scaled speedup S_G(P) = P - alpha * (P - 1)."""
    _check_fraction(alpha, "alpha")
    _check_p(p)
    p = np.asarray(p, dtype=float)
    return p - alpha * (p - 1.0)


def gustafson_efficiency(p, alpha: float):
    """E_G(P) = S_G(P) / P."""
    return gustafson_speedup(p, alpha) / np.asarray(p, dtype=float)


def amdahl_speedup(p, s: float):
    """Fixed-size speedup S_A(P) = 1 / (s + (1 - s) / P)."""
    _check_fraction(s, "s")
    _check_p(p)
    p = np.asarray(p, dtype=float)
    return 1.0 / (s + (1.0 - s) / p)


def amdahl_efficiency(p, s: float):
    """E_A(P) = S_A(P) / P."""
    return amdahl_speedup(p, s) / np.asarray(p, dtype=float)


def alpha_max(p: float, required_speedup: float) -> float:
    """Largest alpha with S_G(P) >= required_speedup: (P - S) / (P - 1)."""
    if p <= 1:
        raise ValueError("P must be > 1")
    if not 1.0 <= required_speedup <= p:
        raise ValueError("required speedup must lie in [1, P]")
    return (p - required_speedup) / (p - 1.0)
