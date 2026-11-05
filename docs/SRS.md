# Software Requirements Specification (SRS)

**Project:** Plane Projection of a 3D Volume (Ex1)  
**Course:** Introduction to Software Engineering, Ariel University  
**Authors:** Nissim Boaz, Bnaya Amitay | **Version:** 1.0

---

## 1. System Overview

Extracts 2D planar cross-sections from 3D volumetric datasets (NRRD format) based on arbitrary geometric plane definitions (CSV), and renders the sequence as an MP4 video at 30 FPS. Invalid planes are identified, classified into standardized error categories, and displayed as informative video slides (with consecutive identical errors grouped).

- **Interfaces:** CLI (`Ex0.py`) and Desktop GUI (`gui.py`).
- **Core Dependencies:** Python 3.8+, `numpy`, `pynrrd`, `opencv-python`.

```
[NRRD Volume] + [CSV Planes] ──> [Validation & Projection] ──> [MP4 Video (30 FPS)]
```

---

## 2. System Specifications & Constraints

| Parameter | Specification | Constraint / Rule |
| :--- | :--- | :--- |
| **Volume Dimensions** | $sx, sy, sz \in [1, 1023]$ | 3D array, C-contiguous in memory |
| **Voxel Types** | `uint8`, `uint16`, `uint32`, `int16` | Linear contrast scaling to 8-bit $[0, 255]$ |
| **Coordinate Space** | Voxel index space (uniform $1\times1\times1$) | Nearest-neighbor sampling; out-of-bounds = $0$ |
| **Plane Geometries** | Triangle (3 pts) or Trapezoid (4 pts) | Numeric tolerance $\varepsilon = 0.001$ |
| **Performance** | Throughput $\ge 30$ FPS (mandatory) | Target $\ge 100$ FPS on $500^3$ volume |
| **Execution Format** | `python Ex0.py file.nrrd file.csv file.mp4` | Overwrites existing output with warning |

---

## 3. Plane Geometry Specifications

- **Isosceles Triangle (3 points: $a, b, c$):**  
  Apex $a$, legs $a \to b$ and $a \to c$.  
  Condition: $|\|b - a\| - \|c - a\|| < \varepsilon$, side lengths $> \varepsilon$, non-collinear.
- **Isosceles Trapezoid (4 points: $a_1, a_2, b, c$):**  
  Top base $a_1 \to a_2$, bottom base $b \to c$, legs $a_1 \to b$ and $a_2 \to c$.  
  Conditions: $|\|b - a_1\| - \|c - a_2\|| < \varepsilon$, $\|a_2 - a_1\| \le \|c - b\| + \varepsilon$, coplanar ($|\hat{n}_{a_1,b,c} \cdot (a_2 - a_1)| < \varepsilon$), leg lengths $> \varepsilon$.

---

## 4. Functional Requirements

### 4.1 CLI & Volume Loading
| ID | Requirement | Verification |
| :--- | :--- | :--- |
| **FR-1** | Accept CLI arguments: `file.nrrd file.csv file.mp4`. Print usage and exit non-zero if invalid. | `test_cli` |
| **FR-2** | Load 3D NRRD as C-contiguous NumPy array. Support `uint8`, `uint16`, `uint32`, `int16`. | `test_volume_loader.py` |
| **FR-3** | Reject non-3D datasets, dimensions outside $[1, 1023]$, or unsupported dtypes with descriptive errors. | `test_volume_loader.py` |

### 4.2 CSV Parsing & Plane Validation
| ID | Requirement | Verification |
| :--- | :--- | :--- |
| **FR-4** | Parse CSV rows with 9 coordinates (3 pts), 12 coordinates (4 pts), or leading count column (10/13 values). | `test_csv_parser.py` |
| **FR-5** | Handle UTF-8 BOM, ignore whitespace, empty lines, and non-numeric headers silently. | `test_csv_parser.py` |
| **FR-6** | Validate geometric rules (isosceles triangle/trapezoid, coplanarity, degenerate cases). | `test_plane.py` |
| **FR-7** | Classify invalid rows into one of 11 distinct error categories; skip invalid rows without crashing. | `test_plane.py`, `test_csv_parser.py` |

### 4.3 Projection Algorithm
| ID | Requirement | Verification |
| :--- | :--- | :--- |
| **FR-8** | Scan plane row-by-row along leg vectors $v_{ab}, v_{ac}$ from apex/top to base. Output size: $\text{round}(D_{ab}) \times \text{round}(D_{bc})$. | `test_projector.py` |
| **FR-9** | Fully vectorized row sampling via NumPy flat-indexing (`M.ravel()[flat_idx]`). No per-voxel Python loop. | `test_projector.py` |
| **FR-10** | Nearest-neighbor sampling: round coordinates to nearest voxel index. Out-of-bounds voxels yield 0. | `test_projector.py` |
| **FR-11** | Apex row handling ($d_{12} = 0$): sample single centered voxel without division-by-zero errors. | `test_projector.py` |

### 4.4 Video Generation & Error Slides
| ID | Requirement | Verification |
| :--- | :--- | :--- |
| **FR-12** | Render valid slices in CSV sequence to MP4 at 30 FPS. Canvas padded with zeros to max slice size. | `test_video_writer.py` |
| **FR-13** | Auto-level contrast to 8-bit $[0, 255]$ with subtle edge enhancement and discrete top-left plane index label. | `test_video_writer.py` |
| **FR-14** | Display centered informative error slides for invalid planes (held for 1.5s / 45 frames). | `test_video_writer.py` |
| **FR-15** | Group consecutive identical errors into a single unified slide displaying index range (e.g., `Planes: 1-25`). | `test_video_writer.py` |
| **FR-16** | Print summary metrics upon completion: valid/skipped planes, elapsed time, projection FPS. | `Ex0.py` |

---

## 5. Non-Functional Requirements

- **Performance (NFR-1):** $\ge 30$ FPS mandatory, $\ge 100$ FPS target on $500^3$ volumes. Inner sampling loop vectorized with zero heap allocation per voxel.
- **Robustness (NFR-2):** Zero crashes on corrupt inputs, out-of-bounds slices, or degenerate geometry. Deterministic output across repeated runs.
- **Architecture (NFR-3):** Modular single-responsibility design (`volume_loader`, `csv_parser`, `plane`, `projector`, `video_writer`, `Ex0`).
- **Cross-Platform (NFR-4):** Identical behavior across macOS, Linux, and Windows.

---

## 6. Error Handling Matrix

| Fault Condition | System Response | Video Output |
| :--- | :--- | :--- |
| Missing / invalid CLI arguments | Print usage, exit code 1 | None |
| NRRD corrupt / non-3D / invalid dtype | Print error, exit code 1 | None |
| All CSV rows invalid | Print error, exit code 1 | None |
| Coordinate count mismatch | Row skipped with warning | Error slide (`Point Count Mismatch`) |
| Triangle not isosceles | Row skipped with warning | Error slide (`Triangle Not Isosceles`) |
| Trapezoid not isosceles / inverted base | Row skipped with warning | Error slide (`Trapezoid Not Isosceles` / `Top Wider Than Bottom`) |
| 4 points not coplanar | Row skipped with warning | Error slide (`Points Not Coplanar`) |
| Collinear points / zero-length edge | Row skipped with warning | Error slide (`Collinear Points` / `Zero-Length Side`) |
| Contiguous identical errors | Aggregated | Unified slide (e.g. `Planes: 4-10: Triangle Not Isosceles`) |
| Plane voxels outside volume | Valid execution | Sampled as 0 (black background) |

---

## 7. Acceptance Criteria

1. CLI runs cleanly: `python Ex0.py data/MRHead_1.nrrd data/professor_planes.csv out.mp4`.
2. Valid planes generate correct, contrast-enhanced 2D cross-sections; invalid planes produce classified error slides.
3. Performance reaches $\ge 30$ FPS (mandatory) and $\ge 100$ FPS (target).
4. All 38 automated unit and integration tests pass without errors.
