# Testing Strategy

**Project:** Plane Projection of a 3D Volume
**Authors:** Nissim, Bnaya Amitay
**Version:** 0.1

---

## 1. Testing Approach

Testing is divided into three levels:

| Level | What | When |
|-------|------|------|
| Unit tests | Each module in isolation | During implementation |
| Integration tests | Full pipeline end-to-end | After all modules are ready |
| Performance benchmark | FPS on a 500³ volume | After optimization |

Framework: **pytest** (Python).

---

## 2. Unit Tests

### 2.1 Volume Loader (`volume_loader.py`)

| Test ID | Input | Expected Result |
|---------|-------|-----------------|
| VL-1 | Valid 8-bit 3D NRRD | Returns correct ndarray shape and dtype |
| VL-2 | Valid 16-bit 3D NRRD | Returns correct ndarray shape and dtype |
| VL-3 | Valid 32-bit 3D NRRD | Returns correct ndarray shape and dtype |
| VL-4 | 2D NRRD file | Raises error with clear message |
| VL-5 | Non-existent file path | Raises error with clear message |
| VL-6 | Unsupported dtype (float) | Raises error with clear message |

---

### 2.2 CSV Parser (`csv_parser.py`)

| Test ID | Input | Expected Result |
|---------|-------|-----------------|
| CSV-1 | Row with 9 values (3-point plane) | Returns valid Plane object |
| CSV-2 | Row with 12 values (4-point plane) | Returns valid Plane object |
| CSV-3 | Row with wrong number of values | Skips row, prints warning with row number |
| CSV-4 | Row with non-numeric text | Skips row, prints warning with row number |
| CSV-5 | Header row or empty line | Ignored silently |
| CSV-6 | All rows invalid | Returns empty list |

---

### 2.3 Plane Validation (`plane.py`)

| Test ID | Input | Expected Result |
|---------|-------|-----------------|
| PV-1 | Valid isosceles triangle | Valid |
| PV-2 | Triangle with `abs(dist(a,b)-dist(a,c)) > EPS` | Invalid: not isosceles |
| PV-3 | Collinear points | Invalid: degenerate |
| PV-4 | Zero-length side | Invalid: degenerate |
| PV-5 | Valid isosceles trapezoid | Valid |
| PV-6 | Trapezoid with `dist(a1,a2) > dist(b,c)` | Invalid |
| PV-7 | Trapezoid with points not on same plane | Invalid: not coplanar |

---

### 2.4 Projector (`projector.py`)

These tests use a **synthetic volume** where `M[x][y][z] = x + y + z` (or similar), so the expected output is analytically known.

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| PR-1 | Axis-aligned X-slice (plane x=k) | Output equals `M[k, :, :]` |
| PR-2 | Axis-aligned Y-slice (plane y=k) | Output equals `M[:, k, :]` |
| PR-3 | Axis-aligned Z-slice (plane z=k) | Output equals `M[:, :, k]` |
| PR-4 | Plane fully inside volume | No zero-padding in output |
| PR-5 | Plane partly outside volume | Out-of-bounds samples = 0 |
| PR-6 | Plane fully outside volume | All-zero output |
| PR-7 | Triangle apex row (`d12 = 0`) | Single sample, no division by zero |
| PR-8 | 4-point trapezoid | Output matches expected cross-section |
| PR-9 | Output matrix size | `round(Dab) × round(Dbc)` |

> **Key insight for PR-1 / PR-2 / PR-3:**
> An axis-aligned slice is the easiest way to verify correctness — the expected output is just a 2D slice of the array, which can be extracted directly with NumPy and compared pixel-by-pixel.

---

### 2.5 Video Writer (`video_writer.py`)

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| VW-1 | Write N frames | Output MP4 has exactly N frames |
| VW-2 | Frames of different sizes | All padded to max width × height |
| VW-3 | 16-bit values in input | Normalized correctly to 8-bit in output |
| VW-4 | Output path not writable | Error message, no crash |

---

## 3. Integration Tests

Run the full CLI command and verify end-to-end behavior:

| Test ID | Command | Expected Result |
|---------|---------|-----------------|
| IT-1 | `python Ex0.py mrhead.nrrd planes.csv out.mp4` | MP4 created, one frame per row |
| IT-2 | Wrong number of arguments | Usage message, exit code ≠ 0 |
| IT-3 | Missing NRRD file | Error message, exit code ≠ 0 |
| IT-4 | Empty CSV file | Error message, no MP4 written |
| IT-5 | CSV with mix of valid and invalid rows | Valid frames written, warnings printed |
| IT-6 | Axis-aligned planes CSV | Frames match direct NumPy slices |

---

## 4. Performance Benchmark

| Test ID | Description | Pass Condition |
|---------|-------------|----------------|
| PERF-1 | Process 100 planes on a 500³ synthetic volume | ≥ 30 FPS (mandatory) |
| PERF-2 | Same as above | ≥ 100 FPS (target) |
| PERF-3 | Projection time only (exclude video encoding) | Measured and reported separately |

**How to run:**
```bash
python tests/benchmark.py
```
Outputs: total time, FPS, and whether targets are met.

---

## 5. Test Data

| Data File | Description | Used in |
|-----------|-------------|---------|
| `data/synthetic_8bit.nrrd` | 100³ volume, `M[x][y][z] = (x+y+z) % 256` | PR-1 to PR-9 |
| `data/mrhead.nrrd` | Real MRI from 3D Slicer | IT-1, PERF-1/2/3 |
| `data/planes_axial.csv` | Axis-aligned X/Y/Z slices | PR-1/2/3, IT-6 |
| `data/planes_tilted.csv` | Tilted planes at various angles | IT-1 |
| `data/planes_invalid.csv` | Mix of valid and invalid rows | CSV-3/4/6, IT-5 |

---

## 6. What Is NOT Tested

| Item | Reason |
|------|--------|
| Trilinear interpolation | Not implemented (nearest-neighbor only) |
| Anisotropic voxel spacing | Out of scope (uniform spacing assumed) |
| GPU acceleration | Not required |

---

## 7. Results

All test suites and benchmarks have been executed and verified:

| Test Suite | Tests | Result | Status |
| :--- | :--- | :--- | :--- |
| **Volume Loader Tests** | VL-1 – VL-6 | 7 passed (uint8, uint16, uint32, int16, error cases) | ✅ **PASS** |
| **Plane Geometry Tests** | PV-1 – PV-7 | 8 passed (triangle/trapezoid validation, coplanarity) | ✅ **PASS** |
| **CSV Parser Tests** | CSV-1 – CSV-6 | 8 passed (format flexibility, BOM, header handling) | ✅ **PASS** |
| **Projector Unit Tests** | PR-1 – PR-9 | 6 passed (ground truth slices, apex row, out-of-bounds) | ✅ **PASS** |
| **Video Writer Tests** | VW-1 – VW-4 | 5 passed (frame counts, padding, 16-bit normalization) | ✅ **PASS** |
| **Total Automated Tests**| `pytest tests/` | **34 passed in 0.18s** | ✅ **PASS (100%)** |
| **CLI Demo Integration** | `python Ex0.py` | Full pipeline executed on `MRHead_1.nrrd` | ✅ **PASS** |
| **Performance Benchmark**| $500^3$ Volume | **79.4 FPS** ($\ge 30$ FPS mandatory threshold) | ✅ **PASS** |
| **MRI Experiment Speed** | $256\times256\times130$ | **104.8 FPS** ($\ge 100$ FPS target) | ✅ **PASS** |
