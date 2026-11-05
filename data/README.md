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

### Other `.nrrd` files (`biscuit_cake`, `croissant`, `onion`, `swiss_roll`)
- **Source:** Provided by the project authors for additional testing.
- **Usage:** Supplementary test volumes for visual validation of the projection pipeline.

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
- **Source:** Official assignment sample sheet.
- **Content:** 50 geometrically validated planes (25 triangles scanning along the Z-axis, 25 trapezoids scanning along the Y-axis).
- **Usage:** Used for multi-frame video generation and automated performance evaluation.

---

## 3. AI-Generated CSV Datasets

The following CSV files were **generated using AI** (specifically prompted to produce geometrically valid plane definitions over the corresponding NRRD volumes). They are provided as convenient test and demonstration inputs:

| File | Description |
|------|-------------|
| `head_demo.csv` | 318-row showcase for `MRHead_1.nrrd`: 105 axial + 120 oblique + 90 coronal planes, plus 3 deliberate errors — produces a ~15-second output video. |
| `head.csv` | Alias/copy of `head_demo.csv`. |
| `biscuit_cake.csv` | Plane sweep over the `biscuit_cake.nrrd` volume. |
| `croissant.csv` | Plane sweep over the `croissant.nrrd` volume. |
| `onion.csv` | Plane sweep over the `onion.nrrd` volume. |
| `swiss_roll.csv` | Plane sweep over the `swiss_roll.nrrd` volume. |
| `edge_cases.csv` | Intentional edge cases: collinear points, degenerate planes, count mismatches, and coplanarity failures. |
| `lecturer_example.csv` | Replication of the example planes used in the lecturer's project walkthrough. |
