# Dataset Description

This directory contains the volumetric NRRD data and plane CSV files used for testing and demonstrations.

---

## 1. Volumetric Data (`.nrrd`)

### `MRHead_1.nrrd`
- **Source:** 3D Slicer Sample Data ([3D Slicer Project](https://www.slicer.org/))
- **Content:** Real human head MRI scan.
- **Dimensions:** $256 \times 256 \times 130$ voxels ($sx = 256, sy = 256, sz = 130$).
- **Data Type:** `int16` (signed 16-bit integer, values range from 0 to 279).
- **Voxel Spacing:** Treated as uniform $1 \times 1 \times 1$ in index space.
- **Usage:** Primary dataset for running the official demo and evaluating projection quality on anatomical structures.

---

## 2. Planes Datasets (`.csv`)

### `professor_planes.csv`
- **Source:** Official assignment sample sheet.
- **Content:** 4 plane definitions demonstrating both valid planes and error-handling cases:
  - **Row 2:** Valid 3-point isosceles triangle.
  - **Row 3:** Valid 4-point isosceles trapezoid.
  - **Row 4:** Invalid triangle (deliberately non-isosceles, skipped with warning).
  - **Row 5:** Invalid trapezoid (deliberately unequal leg lengths, skipped with warning).

### `50_planes.csv`
- **Content:** 50 geometrically validated planes (25 triangles scanning along the Z-axis, 25 trapezoids scanning along the Y-axis).
- **Usage:** Used for multi-frame video generation and automated performance evaluation.
