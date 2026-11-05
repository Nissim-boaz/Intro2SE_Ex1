# Software Requirements Specification (SRS)

**Course:** Introduction to Software Engineering (Ex1)  
**Authors:** Nissim Boaz, Bnaya Amitay

---

## 1. System Scope & Interfaces
The system extracts 2D cross-sections from a 3D volumetric dataset (NRRD) based on geometric plane definitions (CSV) and renders them as an MP4 video (30 FPS).
- **CLI:** `python Ex0.py file.nrrd file.csv file.mp4`
- **GUI:** `python gui.py` (file-picker desktop interface)

## 2. Inputs & Outputs
- **Volume ($M$):** 3D NRRD array ($sx, sy, sz < 1024$), supporting `uint8`, `uint16`, `uint32`, and `int16`. Uniform $1\times1\times1$ voxel grid.
- **Planes (CSV):** Coordinates in voxel index space. Rows define either 3 points ($a, b, c$) or 4 points ($a_1, a_2, b, c$). Optional header and leading count column (10/13 values) supported.
- **Output (MP4):** 30 FPS video, padded to maximum slice size, auto-contrast scaled to 8-bit $[0, 255]$.

## 3. Geometric Plane Definitions ($\varepsilon = 0.001$)
- **Triangle (3 points: $a, b, c$):** Isosceles triangle with apex $a$ and base $b-c$. Valid if $|\|b - a\| - \|c - a\|| < \varepsilon$, side lengths $> \varepsilon$, and points are not collinear.
- **Trapezoid (4 points: $a_1, a_2, b, c$):** Isosceles trapezoid with legs $a_1-b, a_2-c$ and bases $a_1-a_2, b-c$. Valid if $|\|b - a_1\| - \|c - a_2\|| < \varepsilon$, $\|a_2 - a_1\| \le \|c - b\| + \varepsilon$, all 4 points are coplanar, and side lengths $> \varepsilon$.

## 4. Key Functional & Non-Functional Requirements
- **Projection:** Row-by-row scanning from apex/top to base using nearest-neighbor sampling. Voxels outside volume boundaries yield 0 (black).
- **Error Handling:** Invalid rows (non-isosceles, non-coplanar, degenerate, count mismatch) are skipped without crashing. Each invalid plane inserts a labeled error slide (1.5 s). Consecutive rows with identical errors are grouped into a single range slide (e.g., `Planes: 1-25`).
- **Performance:** $\ge 30$ FPS mandatory, $\ge 100$ FPS target on $500^3$ volumes.
