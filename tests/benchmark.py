"""
benchmark.py
Performance benchmark: measures projection FPS on a synthetic 500^3 volume.

Run:
    python tests/benchmark.py
"""

import sys
import os
import time
import numpy as np

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.plane import Plane
from src.projector import project

TARGET_FPS  = 100   # desired target
MINIMUM_FPS = 30    # mandatory minimum
N_PLANES    = 50    # number of planes to project
VOL_SIZE    = 500   # volume edge length


def make_volume(size):
    """Synthetic uint8 volume of shape (size, size, size)."""
    print(f"Building {size}^3 synthetic volume ... ", end="", flush=True)
    x = np.arange(size, dtype=np.uint32).reshape(size, 1, 1)
    y = np.arange(size, dtype=np.uint32).reshape(1, size, 1)
    z = np.arange(size, dtype=np.uint32).reshape(1, 1, size)
    vol = ((x + y + z) % 256).astype(np.uint8)
    print("done.")
    return np.ascontiguousarray(vol)


def make_planes(n, size):
    """Generate n axis-aligned Z-slices evenly distributed across the volume."""
    planes = []
    s = float(size - 1)
    for k in np.linspace(0, size - 1, n, dtype=int):
        a = np.array([0.0,  0.0,  float(k)])
        b = np.array([s,    0.0,  float(k)])
        c = np.array([0.0,  s,    float(k)])
        planes.append(Plane([a, b, c]))
    return planes


def run():
    M = make_volume(VOL_SIZE)
    planes = make_planes(N_PLANES, VOL_SIZE)

    print(f"Projecting {N_PLANES} planes on {VOL_SIZE}^3 volume ...")
    t0 = time.perf_counter()
    for plane in planes:
        project(M, plane)
    elapsed = time.perf_counter() - t0

    fps = N_PLANES / elapsed

    print(f"\n-- Benchmark Results -------------------")
    print(f"  Planes projected : {N_PLANES}")
    print(f"  Total time       : {elapsed:.3f} s")
    print(f"  FPS              : {fps:.1f}")
    print(f"  Mandatory (>={MINIMUM_FPS}) : {'[PASS]' if fps >= MINIMUM_FPS else '[FAIL]'}")
    print(f"  Target    (>={TARGET_FPS}) : {'[PASS]' if fps >= TARGET_FPS  else '[FAIL]'}")
    print(f"----------------------------------------")

    return fps


if __name__ == "__main__":
    fps = run()
    sys.exit(0 if fps >= MINIMUM_FPS else 1)
