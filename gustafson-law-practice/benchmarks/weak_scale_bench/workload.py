"""Monte Carlo estimation of pi: constant work per worker."""
from __future__ import annotations

import numpy as np

CHUNK = 1_000_000


def count_hits(samples: int, seed: int) -> int:
    """Count random points in the unit square that fall inside the quarter circle.

    Uses an independent PCG64 stream from ``SeedSequence(seed)``. Chunked to bound memory.
    """
    if samples < 0:
        raise ValueError("samples must be non-negative")
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    hits, remaining = 0, samples
    while remaining > 0:
        n = min(CHUNK, remaining)
        xy = rng.random((n, 2))
        hits += int(np.count_nonzero(xy[:, 0] ** 2 + xy[:, 1] ** 2 <= 1.0))
        remaining -= n
    return hits


def estimate_pi(total_hits: int, total_samples: int) -> float:
    return 4.0 * total_hits / total_samples


def pi_tolerance(total_samples: int, sigmas: float = 5.0) -> float:
    """Statistical tolerance: sigmas * standard error of the pi estimator."""
    p = np.pi / 4.0
    return sigmas * 4.0 * float(np.sqrt(p * (1 - p) / total_samples))
