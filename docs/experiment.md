# Experiment Results & Analysis

**Project:** Plane Projection of a 3D Volume (Ex1)  
**Authors:** Nissim Boaz & Bnaya Amitay  
**Date:** October 2026  

---

## 1. Experiment Setup
The experiment was performed according to Section 8 of the assignment instructions:
- **Volume Data:** Real MRI head scan (`data/MRHead_1.nrrd`), dimensions: $256 \times 256 \times 130$ voxels, datatype `int16`.
- **Planes Input:** The official CSV file provided by the instructor (`data/professor_planes.csv`), containing 4 plane definitions.
- **Output Video:** `experiment_output.mp4`.

Command executed:
```bash
python Ex0.py data/MRHead_1.nrrd data/professor_planes.csv experiment_output.mp4
```

---

## 2. Quantitative Results & Performance

| Metric | Target | Measured Result | Status |
| :--- | :--- | :--- | :--- |
| **Projection Speed** | $\ge 30$ FPS (mandatory), $100$ FPS (target) | **104.8 FPS** | ✅ **PASS** |
| **Total Projection Time** | Real-time | **0.019 seconds** | ✅ **PASS** |
| **Valid Planes Processed**| Total valid rows | **2 planes** (Row 2, Row 3) | ✅ **PASS** |
| **Invalid Planes Detected**| Reported and skipped | **2 planes** (Row 4, Row 5) | ✅ **PASS** |
| **Video Playback** | 3.0 seconds per slice @ 30 FPS | **12.0 seconds total** (360 frames) | ✅ **PASS** |

---

## 3. Observations & Findings

1. **Accuracy of Plane Projections:**
   - **Plane 1 (Row 2):** An oblique triangular slice passing through the brain structures, showing clear anatomical cross-sections.
   - **Plane 2 (Row 3):** An axial trapezoidal cross-section showing symmetrical brain tissue slice.
2. **Robust Error Handling:**
   - Rows 4 and 5 in the instructor's CSV file deliberately contained non-isosceles configurations (side lengths differing by over 20 and 100 units).
   - The system correctly identified the geometric violations, printed clear warnings with the row numbers, and generated explicit on-screen notice slides in the output video (`INVALID PLANE - SKIPPED`) rather than crashing.
3. **High-Performance Vectorization:**
   - The NumPy vectorized coordinate mapping and batch indexing achieved **104.8 FPS**, well exceeding the 30 FPS threshold required by the assignment.

