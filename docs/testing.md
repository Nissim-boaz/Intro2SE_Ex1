# Testing Strategy & Verification Report

**Project:** Plane Projection of a 3D Volume (Ex1)  
**Authors:** Nissim Boaz, Bnaya Amitay | **Version:** 1.0

---

## 1. Testing Framework & Strategy

Automated test execution via **pytest**, structured into three verification tiers:

```
[Unit Tests: 38 isolated tests] ──► [Integration Tests: CLI & GUI pipeline] ──► [Benchmark: 500³ & MRHead]
```

- **Command:** `pytest tests/`
- **Current Status:** **38 passed in ~1.4s (100% pass rate)**

---

## 2. Unit Test Suites

### 2.1 Volume Loader (`tests/test_volume_loader.py` – 7 tests)
| Test ID | Scenario | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **VL-1 – VL-3** | Valid `uint8`, `uint16`, `uint32` NRRD files | Loaded correctly with matching shape and dtype | ✅ PASS |
| **VL-4** | Non-3D volume (2D image) | Rejects with descriptive dimension error | ✅ PASS |
| **VL-5** | Missing file path | FileNotFoundError captured gracefully | ✅ PASS |
| **VL-6** | Unsupported datatype (float32) | Rejects with explicit dtype error | ✅ PASS |
| **VL-7** | Memory layout verification | Asserts C-contiguous layout in memory | ✅ PASS |

### 2.2 Plane Geometry (`tests/test_plane.py` – 8 tests)
| Test ID | Scenario | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **PV-1** | Valid isosceles triangle | Initialized successfully | ✅ PASS |
| **PV-2** | Non-isosceles triangle ($|D_{ab} - D_{ac}| \ge \varepsilon$) | Rejects with `Triangle Not Isosceles` | ✅ PASS |
| **PV-3** | Collinear points | Rejects with `Collinear Points (Degenerate)` | ✅ PASS |
| **PV-4** | Zero-length edge | Rejects with `Zero-Length Side (Degenerate)` | ✅ PASS |
| **PV-5** | Valid isosceles trapezoid | Initialized successfully | ✅ PASS |
| **PV-6** | Trapezoid with $d_{\text{top}} > d_{\text{bottom}}$ | Rejects with `Top Wider Than Bottom` | ✅ PASS |
| **PV-7** | Non-coplanar 4 points | Rejects with `Points Not Coplanar` | ✅ PASS |

### 2.3 CSV Parser (`tests/test_csv_parser.py` – 8 tests)
| Test ID | Scenario | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **CSV-1 – CSV-2** | 9-value (3 pts) and 12-value (4 pts) rows | Parsed into corresponding Plane objects | ✅ PASS |
| **CSV-3 – CSV-4** | Corrupt field counts or non-numeric cells | Skipped; recorded with descriptive error | ✅ PASS |
| **CSV-5** | UTF-8 BOM, whitespace, empty rows, headers | Handled transparently without error | ✅ PASS |
| **CSV-6** | File with only invalid rows | Returns clean error list without crashing | ✅ PASS |
| **CSV-7** | Declared count exceeds provided coordinates | Rejects with `Point Count Mismatch` | ✅ PASS |

### 2.4 Projector (`tests/test_projector.py` – 6 tests)
| Test ID | Scenario | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **PR-4** | Plane completely inside volume | Output canvas populated without zero-padding | ✅ PASS |
| **PR-5** | Plane partially outside volume boundaries | In-bounds voxels sampled; outside voxels set to 0 | ✅ PASS |
| **PR-6** | Plane completely outside volume | Returns all-zero canvas | ✅ PASS |
| **PR-7** | Triangle apex row ($d_{12} = 0$) | Evaluates single centered sample; no division-by-zero | ✅ PASS |
| **PR-8** | Trapezoid projection | Correct cross-section matched to synthetic volume | ✅ PASS |
| **PR-9** | Output dimensions | Conforms to $\text{round}(D_{ab}) \times \text{round}(D_{bc})$ | ✅ PASS |

### 2.5 Video Writer (`tests/test_video_writer.py` – 9 tests)
| Test ID | Scenario | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **VW-1** | Write $N$ valid frames | Produces valid MP4 with exact frame count | ✅ PASS |
| **VW-2** | Variable slice dimensions | Uniform canvas padding to maximum slice size | ✅ PASS |
| **VW-3** | Higher bit-depth normalization | Dynamically scaled to 8-bit $[0, 255]$ range | ✅ PASS |
| **VW-4** | Non-writable output path | Clean error report; zero crash | ✅ PASS |
| **VW-5** | Single invalid plane | Inserts explanatory pause slide (1.5 s) | ✅ PASS |
| **VW-6 – VW-7** | Error labeling (single vs range) | Formats `Plane: N` vs `Planes: N-M` | ✅ PASS |
| **VW-8** | Non-consecutive different errors | Rendered as separate distinct slides | ✅ PASS |

---

## 3. Integration & Performance Tests

| ID | Description | Command | Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **IT-1** | End-to-end CLI official run | `python Ex0.py data/MRHead_1.nrrd data/professor_planes.csv out.mp4` | Video rendered, errors reported | ✅ PASS |
| **IT-2** | 315-slice showcase demo | `python Ex0.py data/MRHead_1.nrrd data/head_demo.csv demo.mp4` | 15s MP4, 3 error slides grouped | ✅ PASS |
| **PERF-1** | Mandatory throughput | Minimum 30 FPS on $500^3$ volume | **103+ FPS** on MRHead ($3.4\times$ requirement) | ✅ PASS |
| **PERF-2** | Target throughput | Minimum 100 FPS on $500^3$ volume | **231+ FPS** on demo dataset ($2.3\times$ target) | ✅ PASS |

---

## 4. Verification Summary

All 38 automated unit tests pass, and end-to-end CLI integration satisfies all mandatory and target performance constraints.
