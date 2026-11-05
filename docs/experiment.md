# Experiment Results & Performance Benchmark

**Project:** Plane Projection of a 3D Volume (Ex1)  
**Authors:** Nissim Boaz, Bnaya Amitay | **Date:** November 2026

---

## 1. Setup & Execution

- **Volume Dataset:** `data/MRHead_1.nrrd` ($256 \times 256 \times 130$ voxels, datatype `int16`).
- **Official Dataset:** `data/professor_planes.csv` (4 plane definitions).
- **Showcase Dataset:** `data/head_demo.csv` (318 rows: 315 valid planes + 3 deliberate boundary errors; 15-second showcase video).

```bash
# Official benchmark
python Ex0.py data/MRHead_1.nrrd data/professor_planes.csv experiment_output.mp4

# 15-second demo video
python Ex0.py data/MRHead_1.nrrd data/head_demo.csv demo.mp4
```

---

## 2. Quantitative Results & Requirements Compliance

| Metric | Requirement | Measured Result | Status |
| :--- | :--- | :--- | :--- |
| **Official Benchmark Throughput** | $\ge 30$ FPS (mandatory), $\ge 100$ FPS (target) | **103+ FPS** | ✅ **PASS** |
| **Demo Dataset Throughput** | Real-time interactive ($> 100$ FPS) | **231+ FPS** | ✅ **PASS** |
| **Official Valid Planes** | Extract correct cross-sections | **2 planes** (Planes 2, 3) | ✅ **PASS** |
| **Official Invalid Planes** | Detect, classify, and skip without crash | **2 planes** (Planes 4, 5) | ✅ **PASS** |
| **Showcase Video Duration** | Visual representation of volume sweeps | **~15 seconds** @ 30 FPS | ✅ **PASS** |
| **Error Slide Grouping** | Consecutive identical errors collapsed | Aggregated into unified range notices | ✅ **PASS** |

---

## 3. Key Observations & Verification

1. **Projection Fidelity Across Sweeps:**
   - *Axial sweep (Planes 1–105):* Continuous cranial cross-sections highlighting outer skull contour, brain matter, and ventricles.
   - *Oblique sweep (Planes 107–226):* Angled slices capturing internal asymmetry.
   - *Coronal sweep (Planes 228–317):* Trapezoidal sections displaying bilateral hemisphere symmetry.
2. **Robust Boundary Error Handling:**  
   The 3 deliberately corrupted rows in `head_demo.csv` were caught and classified cleanly:
   - Row 106: `Triangle Not Isosceles` $\to$ pause slide rendered; pipeline continued.
   - Row 227: `Points Not Coplanar` $\to$ pause slide rendered; pipeline continued.
   - Row 318: `Point Count Mismatch` $\to$ pause slide rendered; video finalized cleanly.
3. **Consecutive Error Grouping:**  
   Consecutive rows sharing identical error types are automatically collapsed into a single explanatory slide (held for 1.5 s), avoiding video bloat.
4. **Vectorization Efficiency:**  
   Replacing voxel-by-voxel Python loops with contiguous flat memory lookups (`M.ravel()[flat_idx]`) reduced projection time to $< 4.3 \text{ ms}$ per slice, exceeding the course target by over $2\times$.
