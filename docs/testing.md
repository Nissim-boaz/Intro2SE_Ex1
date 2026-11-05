# Testing Strategy & Results

**Course:** Introduction to Software Engineering (Ex1)  
**Authors:** Nissim Boaz, Bnaya Amitay

---

## 1. Testing Strategy
Testing is implemented with **pytest** across three layers: unit tests for isolated modules, end-to-end integration tests for the CLI pipeline, and performance benchmarks.

Run all tests:
```bash
pytest tests/
```

## 2. Test Suites Summary (38 Tests, 100% Pass)

| Module / Suite | Tests | Scope & Key Scenarios | Status |
| :--- | :---: | :--- | :--- |
| **Volume Loader** (`test_volume_loader.py`) | 7 | `uint8`/`uint16`/`uint32`/`int16` loading, rejection of 2D/float dtypes, C-contiguous layout. | ✅ PASS |
| **Plane Geometry** (`test_plane.py`) | 8 | Isosceles check, trapezoid base inequality, 4-point coplanarity, collinear/degenerate rejection. | ✅ PASS |
| **CSV Parser** (`test_csv_parser.py`) | 8 | 9/12 coordinates, 10/13 values with count column, BOM, empty rows, count mismatch detection. | ✅ PASS |
| **Projector** (`test_projector.py`) | 6 | Synthetic volume verification, apex row ($d_{12}=0$), out-of-bounds voxels (=0), trapezoid projection. | ✅ PASS |
| **Video Writer** (`test_video_writer.py`) | 9 | Canvas padding, 8-bit normalization, error slides, consecutive error grouping (`Planes: N-M`). | ✅ PASS |
| **Total Unit Tests** | **38** | **All pass in < 0.5s** | ✅ **PASS** |

## 3. Integration & Performance Verification
- **CLI Execution:** `python Ex0.py data/MRHead_1.nrrd data/professor_planes.csv out.mp4` successfully creates an MP4 with valid slices and error slides.
- **Performance:** Measured **103+ FPS** on MRHead and **231+ FPS** on `head_demo.csv`, exceeding the mandatory 30 FPS threshold and the 100 FPS target.
