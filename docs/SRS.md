# Software Requirements Specification (SRS)

**Project:** Plane Projection of a 3D Volume  
**Course:** Introduction to Software Engineering (OOP/OOD), Ariel University – Ex1  
**Authors:** Nissim Boaz, Bnaya Amitay  
**Version:** 1.0  

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements of a software system that extracts a 2D cross-section (plane projection) from a 3D volumetric data set and produces a video of several such cross-sections. It is the reference for design, implementation, testing, and acceptance.

### 1.2 Scope
The system reads a 3D volume in NRRD format and a CSV file of planes. For each plane it computes a 2D image, and writes all images as consecutive frames of an MP4 video. Invalid planes are detected, classified, and represented as informative error slides; consecutive identical errors are collapsed into a single grouped slide. The system exposes two interfaces: a CLI (`Ex0.py`) and an optional desktop GUI (`gui.py`).

### 1.3 Definitions and Abbreviations
| Term | Meaning |
|------|---------|
| Volume (M) | 3D matrix of size `sx × sy × sz`; entry `M[x][y][z]` is an unsigned integer of 8, 16, or 32 bits |
| Voxel | A single entry of the volume |
| Plane (p) | A flat surface defined by 3 or 4 points (see 3.2) |
| Projection / slice | The 2D image obtained by sampling the volume along a plane |
| NRRD | Nearly Raw Raster Data, a file format for N-dimensional raster data |
| EPS | Numeric tolerance, `0.001` |
| FPS | Frames per second (number of planes processed per second) |
| `Dab`, `Dbc` | `dist(a,b)` (= `dist(a,c)`) and `dist(b,c)` |
| Error slide | A video frame that describes a skipped invalid plane instead of showing a projection |

### 1.4 References
- Assignment document: *Ex1 – Algorithm: Implementing a plane projection of 3D volume* (Ariel University)
- NRRD format specification: https://teem.sourceforge.net/nrrd/format.html
- 3D Slicer: https://www.slicer.org/ (source of MRHead sample data)

---

## 2. Overall Description

### 2.1 Product Perspective
A stand-alone command-line application, independent of other systems. It is inspired by the slice views of 3D Slicer, but supports slices at arbitrary orientation. An optional desktop GUI (`gui.py`) wraps the same pipeline with a file-picker interface.

### 2.2 Product Functions (Summary)
1. Load a 3D volume from an NRRD file.
2. Load a list of planes from a CSV file.
3. Validate each plane and classify any errors (11 categories).
4. Compute the 2D projection of each valid plane using a vectorized flat-index algorithm.
5. Write all projections to an MP4 video, in CSV order, at 30 FPS.
6. Insert informative error slides for invalid planes; group consecutive identical errors into a single slide.

### 2.3 Users
- Students and the course staff running the demo.
- Developers extending the code (the design must be modular and readable).

### 2.4 Operating Environment
- Python 3.10+.
- Desktop OS (macOS, Windows, or Linux), no GPU required.
- Libraries: `numpy`, `pynrrd`, `opencv-python`.

### 2.5 Constraints
- Sizes satisfy `1 ≤ sx, sy, sz < 2^10`.
- Voxel type: unsigned integer of 8, 16, or 32 bits (also accepts signed `int16` from real NRRD files).
- Performance: 30+ FPS is mandatory on a 500³ byte volume; 100+ FPS is the target.
- Run command format: `python Ex0.py file.nrrd file.csv file.mp4`.
- Code quality (design, readability, structure) is graded above raw implementation.

### 2.6 Assumptions and Dependencies
- Plane coordinates are given in **voxel index space** (not physical units such as mm).
- Voxel spacing is treated as uniform (1 × 1 × 1). Anisotropic spacing in the NRRD header is not corrected.
- The volume fits in memory.
- The required libraries are installed (`requirements.txt`).

---

## 3. Specific Requirements

### 3.1 Functional Requirements

#### 3.1.1 Command line (CLI)
| ID | Requirement |
|----|-------------|
| FR-1 | The program shall accept exactly three arguments: NRRD path, CSV path, output MP4 path. |
| FR-2 | If the number of arguments is wrong, the program shall print a usage message and exit with a non-zero code. |
| FR-3 | The program shall not overwrite the input files. If the output file exists, it shall be overwritten and a warning printed. |

#### 3.1.2 Volume loading
| ID | Requirement |
|----|-------------|
| FR-4 | The system shall read a 3D NRRD file and expose it as a C-contiguous 3D array `M[x][y][z]` with sizes `sx, sy, sz`. |
| FR-5 | The system shall support unsigned integer voxels of 8, 16, and 32 bits (and signed `int16` as produced by real MRI scanners). |
| FR-6 | The system shall reject files that are not 3D, have sizes outside `[1, 1023]`, or have an unsupported data type, with a clear error message. |
| FR-7 | The system shall report the volume size and data type after loading (for logging). |

#### 3.1.3 Plane input (CSV)
| ID | Requirement |
|----|-------------|
| FR-8 | Each CSV row shall define one plane: 3 points (9 numbers) or 4 points (12 numbers), each point as `x,y,z`. |
| FR-9 | The point order shall be `a, b, c` for 3 points and `a1, a2, b, c` for 4 points. |
| FR-10 | Coordinates may be real numbers. An optional header row and empty lines shall be ignored. |
| FR-11 | The output frame order shall equal the CSV row order. |
| FR-12 | A row that declares N points but provides fewer coordinates shall be detected as a `Point Count Mismatch` error. |

#### 3.1.4 Plane validation
| ID | Requirement |
|----|-------------|
| FR-13 | For 3 points, the system shall check `abs(dist(a,b) - dist(a,c)) < EPS`. |
| FR-14 | For 4 points, the system shall check: `abs(dist(a1,b) - dist(a2,c)) < EPS`, `dist(a1,a2) <= dist(b,c)`, and coplanarity (within EPS). |
| FR-15 | The system shall reject degenerate planes (collinear points, zero-length sides). |
| FR-16 | An invalid row shall be reported with its row number and classified reason (one of 11 categories). The system shall skip it and continue. |

#### 3.1.5 Projection algorithm
| ID | Requirement |
|----|-------------|
| FR-17 | The system shall compute `Dab`, `Dbc`, and the unit vectors `v(a,b)`, `v(a,c)`. |
| FR-18 | The system shall allocate an output matrix `E` of size `Dab × Dbc` (rounded to integers, at least 1×1). |
| FR-19 | For `y = 0 … Dab-1`, the system shall advance `a1` by `v(a,b)` and `a2` by `v(a,c)`, compute `d12 = dist(a1,a2)` and `dp = (a2 - a1) / d12`. |
| FR-20 | For `x1 = 0 … d12`, the system shall sample `M` at point `p` and write the value to `E[x][y]` with `x = Dbc/2 - d12/2 + x1`. |
| FR-21 | Sampling shall use nearest-neighbor: the voxel index is the rounded coordinate. |
| FR-22 | A point `p` outside the volume shall yield the value 0. |
| FR-23 | The same algorithm shall support the trapezoid (4-point) input, with `a1` and `a2` as the two starting points. |
| FR-24 | When `d12 = 0` (the apex row), the system shall write a single sample and avoid division by zero. |
| FR-25 | The inner sampling loop shall be fully vectorized using NumPy flat-index batch lookups, eliminating per-sample Python loops. |

#### 3.1.6 Video output
| ID | Requirement |
|----|-------------|
| FR-26 | The system shall write an MP4 file at 30 FPS with one frame per valid plane and one error slide per invalid plane (or error group), in CSV order. |
| FR-27 | All frames in a video shall have the same size. Smaller images shall be padded with zeros (black) to the maximal width and height among all planes. |
| FR-28 | Voxel values shall be mapped to 8-bit grayscale for display, by linear scaling from `[min(M), max(M)]` to `[0, 255]`. |
| FR-29 | Each error slide shall display the plane number (or range, e.g. `Planes: 1–25`) and a human-readable error category. It shall be shown for 1.5 seconds (45 frames at 30 FPS). |
| FR-30 | Consecutive CSV rows with the **same** error category shall be collapsed into a **single** error slide displaying the full range (e.g. `Planes: 1–25`). |
| FR-31 | The system shall print a summary at the end: planes read, planes written, planes skipped, total time, processing FPS. |

### 3.2 Plane Definition (Formal)
- **3 points** `(a, b, c)`: isosceles triangle with apex `a`, `abs(dist(a,b) - dist(a,c)) < EPS`.
- **4 points** `(a1, a2, b, c)`: isosceles trapezoid, with `abs(dist(a1,b) - dist(a2,c)) < EPS`, `dist(a1,a2) <= dist(b,c)`, and `a1→b`, `a2→c` on the same plane.
- `EPS = 0.001`.

### 3.3 Non-Functional Requirements

#### Performance
| ID | Requirement |
|----|-------------|
| NFR-1 | On a 500³ byte volume, the system shall process at least 30 planes per second (mandatory). |
| NFR-2 | The target is at least 100 planes per second on the same volume. |
| NFR-3 | The volume shall be loaded once and kept in memory as a C-contiguous flat array. The inner loop shall be fully vectorized with NumPy; no per-sample Python object allocation. |
| NFR-4 | Performance shall be measured for the projection stage separately from video encoding, and reported. |

#### Robustness and reliability
| ID | Requirement |
|----|-------------|
| NFR-5 | The system shall not crash on any input; every failure ends with a clear message. |
| NFR-6 | Results shall be deterministic: the same input gives the same output. |

#### Maintainability and design quality
| ID | Requirement |
|----|-------------|
| NFR-7 | The code shall be split into separate modules/classes with a single responsibility (volume loader, plane, projector, video writer, CSV parser, CLI, GUI). |
| NFR-8 | The projection logic shall be independent of file formats and of the CLI, so it can be unit-tested. |
| NFR-9 | Public functions and classes shall be documented with NumPy-style docstrings; names shall be meaningful; constants (e.g. `EPS`) shall be defined once. |
| NFR-10 | Work shall be committed frequently, using branches and Pull Requests. |

#### Portability and usability
| ID | Requirement |
|----|-------------|
| NFR-11 | The system shall run on macOS, Windows, and Linux. |
| NFR-12 | Installation shall require only `pip install -r requirements.txt`. |

### 3.4 Error Handling
| Situation | Behavior |
|-----------|----------|
| Wrong number of arguments | Usage message, exit code ≠ 0 |
| NRRD file missing / unreadable / not 3D | Error message, exit code ≠ 0 |
| CSV file missing / empty | Error message, exit code ≠ 0 |
| CSV row with a wrong number of values or non-numeric text | Row skipped, error slide inserted in video |
| CSV row with declared N points but fewer coordinates | Row skipped, `Point Count Mismatch` error slide inserted |
| Plane fails validation (3.2) | Row skipped, error slide inserted with classified reason |
| Consecutive rows with the same error | Single grouped error slide (e.g. `Planes: 1–25`) |
| All planes invalid | Error message, no video written, exit code ≠ 0 |
| Plane partly or fully outside the volume | Valid; outside samples are 0 |
| Output path not writable | Error message, exit code ≠ 0 |

### 3.5 Interface Requirements
- **User interface:** command line (`Ex0.py`) or optional desktop GUI (`gui.py`).
- **Input files:** NRRD (volume), CSV (planes).
- **Output file:** MP4 (video, 30 FPS).
- **CSV example** (one 3-point plane, one 4-point plane):
  ```
  10,10,10, 200,20,10, 20,200,10
  10,10,50, 30,10,50, 250,200,50, 20,220,50
  ```

---

## 4. Data Requirements
- **Dataset:** at least the 3D Slicer *MRHead* sample volume, plus synthetic volumes for testing (e.g. a volume where `M[x][y][z]` encodes the coordinates, so every slice has a known expected result).
- **Test planes:** axis-aligned planes (X, Y, Z sections), tilted planes, planes partly outside the volume, and invalid planes.
- **Demo dataset:** `data/head_demo.csv` — a 15-second showcase with 315 valid planes across three sweeps and 3 deliberately introduced errors.
- Data files are stored under `data/`.

---

## 5. Acceptance Criteria
1. The demo command runs on the MRHead volume and produces a playable MP4 with one frame per valid plane and one error slide (or grouped slide) per invalid row.
2. Axis-aligned planes produce images identical to the corresponding slices of the volume.
3. Invalid planes are reported, classified, and skipped; the program does not crash.
4. Consecutive identical errors are grouped into a single slide showing the range.
5. Measured speed is ≥ 30 FPS (target ≥ 100 FPS) on a 500³ volume.
6. All 38 automated tests pass.
7. The README, SRS, algorithm, and testing documents exist and are consistent with the code.

---

## 6. Traceability (Requirements → Verification)
| Requirements | Verified by |
|--------------|-------------|
| FR-1 – FR-3 | CLI tests (arguments, overwrite) |
| FR-4 – FR-7 | Loader tests (valid/invalid NRRD, 8/16/32 bit, int16) |
| FR-8 – FR-12 | CSV parser tests (format, BOM, header, count-mismatch) |
| FR-13 – FR-16 | Plane validation unit tests |
| FR-17 – FR-25 | Projection unit tests (known slices, out-of-bounds, apex row, vectorized) |
| FR-26 – FR-31 | Video writer tests (frame count, padding, normalization, error grouping) |
| NFR-1 – NFR-4 | Benchmark on MRHead and 500³ synthetic volume |
| NFR-5 – NFR-6 | Invalid-input and repeated-run tests |
| NFR-7 – NFR-12 | Code review, fresh install on a clean machine |

---

## 7. Open Issues (resolved)

| Issue | Resolution |
|-------|-----------|
| Frame size for planes of different sizes (FR-27) | Pad all frames to the maximum width × height; smaller frames are zero-padded. |
| Value mapping for 16/32-bit data (FR-28) | Linear scaling from `[min(M), max(M)]` to `[0, 255]`. |
| Sampling method | Nearest-neighbor (fast, sufficient for assignment requirements). |
| Voxel spacing | Treated as uniform 1×1×1; physical NRRD spacing not applied. |
| Script name | Confirmed as `Ex0.py` per assignment instructions. |
| Rounding of `x` index | Round to nearest integer, clamp to `[0, cols-1]`. |
