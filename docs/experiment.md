# Experiment Results & Analysis

**Project:** Plane Projection of a 3D Volume (Ex1)  
**Authors:** Nissim Boaz & Bnaya Amitay  
**Date:** November 2026  

---

## 1. Experiment Setup

The experiment was performed according to Section 8 of the assignment instructions:

- **Volume Data:** Real MRI head scan (`data/MRHead_1.nrrd`), dimensions: $256 \times 256 \times 130$ voxels, datatype `int16`.
- **Official Planes:** The official CSV file provided by the instructor (`data/professor_planes.csv`), containing 4 plane definitions.
- **Demo Dataset:** A purpose-built showcase CSV (`data/head_demo.csv`), containing 315 valid planes across three sweeps and 3 deliberately introduced errors — producing a 15-second output video.

Commands executed:

```bash
# Official experiment
python Ex0.py data/MRHead_1.nrrd data/professor_planes.csv experiment_output.mp4

# 15-second demo
python Ex0.py data/MRHead_1.nrrd data/head_demo.csv demo.mp4
```

---

## 2. Quantitative Results & Performance

### 2.1 Official Experiment (`professor_planes.csv`)

| Metric | Target | Measured Result | Status |
| :--- | :--- | :--- | :--- |
| **Projection Speed** | $\ge 30$ FPS (mandatory), $100$ FPS (target) | **103+ FPS** | ✅ **PASS** |
| **Total Projection Time** | Real-time | **< 0.02 seconds** | ✅ **PASS** |
| **Valid Planes Processed** | Total valid rows | **2 planes** (Row 2, Row 3) | ✅ **PASS** |
| **Invalid Planes Detected** | Reported and skipped | **2 planes** (Row 4, Row 5) | ✅ **PASS** |
| **Video Output** | 1 frame per valid plane + error slides | **MP4 produced** | ✅ **PASS** |

### 2.2 Demo Experiment (`head_demo.csv`)

| Metric | Value |
| :--- | :--- |
| **Total CSV rows** | 318 |
| **Valid planes** | 315 (105 axial + 120 oblique + 90 coronal) |
| **Error rows** | 3 (one per sweep boundary) |
| **Projection Speed** | **231+ FPS** |
| **Video Duration** | **~15 seconds** @ 30 FPS |
| **Error slides** | 3 single-frame grouped slides (1.5 s each) |

---

## 3. Observations & Findings

### 3.1 Accuracy of Plane Projections

- **Axial sweep (Planes 1–105):** Cross-sections through the top-to-bottom axis of the MRI head show progressive anatomical detail — skull outer contour, brain tissue, ventricles.
- **Oblique sweep (Planes 107–226):** Rotational slices passing through the brain at varying angles produce distinct triangular cross-sections highlighting asymmetric structures.
- **Coronal sweep (Planes 228–317):** Trapezoidal cuts along the coronal axis reveal bilateral symmetry of the brain hemispheres.

### 3.2 Robust Error Handling

Three deliberately invalid rows were inserted at the boundaries of each sweep:

| Plane | Error Type | Behavior |
|-------|-----------|---------|
| Row 106 | Triangle Not Isosceles | Error slide displayed, processing continues |
| Row 227 | Points Not Coplanar | Error slide displayed, processing continues |
| Row 318 | Point Count Mismatch | Error slide displayed, video finalizes normally |

The system correctly identified each geometric or structural violation, printed a clear warning with the row number, and inserted a labeled error slide — without crashing or interrupting the pipeline.

### 3.3 Consecutive Error Grouping

When a systematic input error produces the same error category on many consecutive rows, the video writer collapses them into a single slide (e.g. `Planes: 1–25`) rather than flooding the video with individual error frames. This feature keeps the output concise and viewer-friendly.

### 3.4 High-Performance Vectorization

The NumPy flat-index vectorized coordinate mapping achieved:
- **103+ FPS** on the official 4-plane experiment (MRHead, `256×256×130`).
- **231+ FPS** on the 315-plane demo dataset.

Both results comfortably exceed the mandatory 30 FPS threshold and the 100 FPS target. The key optimization is computing all sample positions for each scanline row in a single NumPy batch (`M.ravel()[flat_idx]`), eliminating the innermost Python loop entirely.

---

## 4. Summary

The implemented system meets all functional, error-handling, and performance requirements:

| Requirement | Result |
|-------------|--------|
| ≥ 30 FPS mandatory | ✅ 103+ FPS measured |
| ≥ 100 FPS target | ✅ 103+ FPS (official), 231+ FPS (demo) |
| Invalid planes detected & skipped | ✅ All 3 deliberate errors caught |
| Consecutive errors grouped | ✅ Single slide per contiguous error group |
| 15-second showcase video | ✅ `head_demo.csv` → ~15 s MP4 |
| All 38 unit tests pass | ✅ `38 passed` |
