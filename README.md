# Plane Projection of 3D Volume (Ex1)

> **Course:** Introduction to Software Engineering (OOP / OOD), Ariel University  
> **Authors:** Nissim Boaz & Bnaya Amitay  
> **Repository:** https://github.com/Nissim-boaz/Intro2SE_Ex1

---

## 1. Problem & Scope
> *"Problem statement: Given 3D raster data matrix (M), and a plane (p). Compute the 2D matrix (image) of the projection of p in V"*  
> *"Implementation Requirements: ... Given a matrix of size 500^3 bytes, a runtime of at least 100 fps is expected; +30 FPS is a must"*

This system extracts 2D planar cross-sections from a 3D NRRD volume ($M$) along arbitrary orientations. A plane is defined in index space by:
- **3 Points $(a, b, c)$:** Isosceles triangle ($|dist(a,b) - dist(a,c)| < 0.001$).
- **4 Points $(a1, a2, b, c)$:** Isosceles trapezoid ($|dist(a1,b) - dist(a2,c)| < 0.001$ and $dist(a1,a2) \le dist(b,c)$).

Points outside the volume boundaries sample $0$ (black).

---

## 2. Documentation Links
- **SRS:** [docs/SRS.md](docs/SRS.md) — System requirements & specifications.
- **Algorithm Design:** [docs/algorithm.md](docs/algorithm.md) — Detailed pseudocode & vectorization design.
- **Testing Strategy:** [docs/testing.md](docs/testing.md) — Test plan for unit tests, ground-truth verification & benchmarks.

---

## 3. Dataset
> *"Data: In this assignment, we will use NRRD format and data from the 3D Slicer open-source project."*

- `data/sample_volume.nrrd` — Synthetic 3D spherical volume ($100^3$, uint8).
- `data/professor_planes.csv` — Official assignment planes containing valid & invalid cases.
- `data/50_planes.csv` — 50 validated axial & oblique planes (triangles & trapezoids).
- Real MRI data (e.g. `MRHead.nrrd`) can be placed in `data/`.

---

## 4. How to Run (Demo CLI & GUI)
> *"Create a demo 'main' allowing you to run the script in the following format: `python Ex0.py file.nrrd file.csv file.mp4`"*

### Setup
```bash
pip install -r requirements.txt
```

### CLI Command (Required Demo)
```bash
python Ex0.py <file.nrrd> <file.csv> <file.mp4>
```
*Example:*
```bash
python Ex0.py data/sample_volume.nrrd data/professor_planes.csv output.mp4
```

### Desktop GUI (Windows / macOS / Linux)
```bash
python gui.py
```

---

## 5. Experimental Results
> *"Perform an experiment and write down a short description of the results, including the mp4 output file."*

### Benchmark: $500^3$ Volume (50 Planes)
| Metric | Requirement | Measured | Status |
| :--- | :--- | :--- | :--- |
| **Projection Speed** | $\ge 30$ FPS | **79.4 FPS** | ✅ **PASS** |
| **Slice Latency** | $< 33.3$ ms | **12.6 ms** | ✅ **PASS** |
| **Unit Tests** | All modules | **34 / 34 passed** | ✅ **PASS** |

### Video Output (`output.mp4`)
- Each plane is displayed for 3.0 seconds at a smooth 30 FPS rate.
- **On-Screen Overlays:** Valid frames display active plane/row indices (`Plane 1 (Row 2)`).
- **Error Handling:** Invalid CSV rows (e.g. non-isosceles) are detected gracefully; the video shows an explanatory notice slide before continuing to the next frame.
