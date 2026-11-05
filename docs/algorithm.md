# Projection Algorithm – Detailed Design

**Project:** Plane Projection of a 3D Volume  
**Authors:** Nissim Boaz, Bnaya Amitay  
**Version:** 1.0  

---

## 1. Overview

The algorithm receives a 3D volume `M` of size `sx × sy × sz` and a plane defined by 3 or 4 points. It outputs a 2D matrix `E` representing the cross-section of the volume along that plane.

### Input
| Parameter | Description |
|-----------|-------------|
| `M[x][y][z]` | 3D matrix, unsigned integer (8/16/32 bit), each dimension ∈ [1, 1023] |
| 3-point plane | Points `(a, b, c)` where `abs(dist(a,b) - dist(a,c)) < EPS` (isosceles triangle) |
| 4-point plane | Points `(a1, a2, b, c)` forming an isosceles trapezoid |

### Output
| Parameter | Description |
|-----------|-------------|
| `E[x][y]` | 2D matrix of sampled voxel values |

### Constants
| Name | Value | Purpose |
|------|-------|---------|
| `EPS` | 0.001 | Tolerance for distance comparisons |

---

## 2. Triangle Case (3 Points)

### 2.1 Geometry

The plane is defined by an isosceles triangle with apex `a` and base `b–c`:

```
        a  (apex)
       / \
      /   \
     /     \
    b ——————c  (base)

    dist(a,b) = dist(a,c) = Dab
    dist(b,c) = Dbc
```

The algorithm scans the triangle row by row from apex `a` toward the base `b–c`. Each row is a horizontal segment parallel to the base, growing wider as `y` increases.

### 2.2 Pseudocode

```
function project_triangle(M, a, b, c) -> E:
    Dab = dist(a, b)          # = dist(a, c), the equal sides
    Dbc = dist(b, c)          # the base length

    v_ab = (b - a) / Dab      # unit vector from a toward b
    v_ac = (c - a) / Dab      # unit vector from a toward c

    E = matrix of zeros, size: round(Dab) × round(Dbc)

    a1 = a                    # walker along a→b
    a2 = a                    # walker along a→c

    for y = 0 to round(Dab) - 1:
        a1 = a1 + v_ab        # step toward b
        a2 = a2 + v_ac        # step toward c

        d12 = dist(a1, a2)    # current row width
        if d12 == 0:
            # apex row: single sample
            E[round(Dbc/2)][y] = sample(M, a1)
            continue

        dp = (a2 - a1) / d12  # unit vector along the row

        p = a1                # sampling cursor
        for x1 = 0 to round(d12):
            v = sample(M, p)
            x = round(Dbc/2 - d12/2 + x1)
            E[x][y] = v
            p = p + dp

    return E
```

### 2.3 Scan Diagram

```
y=0    a1≈a2 (apex)            →  one sample at center
y=1      a1--a2                →  short row, centered
y=2     a1----a2               →  wider row
  ...
y=Dab  b----------c           →  full base width = Dbc
       |__________|
       x: centered in E
           width Dbc
```

---

## 3. Trapezoid Case (4 Points)

### 3.1 Geometry

The plane is defined by an isosceles trapezoid `(a1, a2, b, c)`:

```
    a1 ————— a2   (top, shorter side)
   /           \
  /             \
 b ————————————— c   (bottom, longer side)

 dist(a1, b) = dist(a2, c)   (equal legs)
 dist(a1, a2) <= dist(b, c)
```

### 3.2 Adaptation

The algorithm is identical to the triangle case, except:
- The two walkers start at `a1` and `a2` instead of both starting at `a`.
- `Dab = dist(a1, b)` (= `dist(a2, c)`), the leg length.
- `v_ab = (b - a1) / Dab`, `v_ac = (c - a2) / Dab`.
- The first row already has width `dist(a1, a2) > 0`.

---

## 4. Design Decisions

### 4.1 Sampling: Nearest-Neighbor

Each 3D point `p = (px, py, pz)` is sampled by rounding to the nearest integer index:

```
sample(M, p):
    ix, iy, iz = round(px), round(py), round(pz)
    if 0 <= ix < sx and 0 <= iy < sy and 0 <= iz < sz:
        return M[ix][iy][iz]
    else:
        return 0   # out-of-bounds → black
```

**Rationale:** Nearest-neighbor is the simplest and fastest method. Trilinear interpolation would give smoother results but is slower and not required by the assignment.

### 4.2 Output Size Rounding

`Dab` and `Dbc` are real numbers. The output matrix dimensions are rounded to the nearest integer, with a minimum of 1:

```
rows = max(1, round(Dab))
cols = max(1, round(Dbc))
```

### 4.3 Index `x` Rounding

The formula `x = Dbc/2 - d12/2 + x1` may produce a non-integer. We round to the nearest integer and clamp to `[0, cols-1]` to avoid out-of-bounds writes.

### 4.4 Apex Row (`d12 = 0`)

At `y = 0` in the triangle case, `a1 = a2 = a`, so `d12 = 0`. Division by zero is avoided by writing a single sample at the center column `x = round(Dbc/2)`.

### 4.5 Out-of-Bounds Points

Any point `p` outside the volume boundaries returns value `0` (black). This is consistent with the assignment: *"if p is NOT in M, v=0"*.

---

## 5. Performance Optimizations

### 5.1 Target

| Requirement | FPS |
|-------------|-----|
| Mandatory   | ≥ 30 |
| Target      | ≥ 100 |

On a 500³ byte volume.

### 5.2 Strategies

| Strategy | Description |
|----------|-------------|
| **Contiguous flat array** | Volume stored as a single C-contiguous `numpy.ndarray`; rows, columns, and slices map to a single 1D memory buffer for cache-friendly access |
| **Flat-index batch lookup** | Sample positions are converted to a single flat integer index `idx = ix*sy*sz + iy*sz + iz` and looked up in one vectorized call: `M.ravel()[idx]` |
| **Fully vectorized inner loop** | The Python `for x1` loop is eliminated entirely: all sample positions for a row are precomputed with `np.arange` + broadcasting, rounded, clipped, and indexed in one NumPy operation |
| **Avoid object allocation** | No per-sample Python object creation; output `E` is pre-allocated once per plane |

### 5.3 Vectorized Projection (Key Optimization)

Instead of looping sample-by-sample, each row is computed as:

```python
# For each row y:
t = np.arange(0, round(d12) + 1)          # [0, 1, ..., d12]
points = a1 + np.outer(t, dp)             # all sample positions, shape (n, 3)
ix = np.clip(np.round(points[:, 0]).astype(int), 0, sx-1)
iy = np.clip(np.round(points[:, 1]).astype(int), 0, sy-1)
iz = np.clip(np.round(points[:, 2]).astype(int), 0, sz-1)
flat_idx = ix * sy * sz + iy * sz + iz    # flat index into M.ravel()
values = M.ravel()[flat_idx]              # single batch lookup
# write values into E at the correct x offsets
```

This eliminates the innermost Python loop entirely and accesses memory in one contiguous batch.

### 5.4 Measured Performance

| Dataset | Volume Size | Measured FPS |
|---------|------------|-------------|
| MRHead  | 256×256×130 | **103+ FPS** |
| head_demo (315 planes) | 256×256×130 | **231+ FPS** |

Both results exceed the 100 FPS target.

---

## 6. Validation

### 6.1 Triangle Validation

```
abs(dist(a, b) - dist(a, c)) < EPS
dist(a, b) > EPS               # non-degenerate
points are not collinear
```

### 6.2 Trapezoid Validation

```
abs(dist(a1, b) - dist(a2, c)) < EPS
dist(a1, a2) <= dist(b, c)
a1→b and a2→c lie on the same plane (cross-product check)
dist(a1, b) > EPS              # non-degenerate
```

### 6.3 Coplanarity Check (4 Points)

```
n1 = cross(b - a1, c - a1)
n2 = cross(b - a2, c - a2)
n1_norm = n1 / |n1|
n2_norm = n2 / |n2|
coplanar = abs(|dot(n1_norm, n2_norm)| - 1) < EPS
```

---

## 7. Error Detection & Video Output

### 7.1 Error Categories

The CSV parser and plane validator detect **11 error categories**:

| Category | Trigger |
|----------|---------|
| `Triangle Not Isosceles` | `abs(dist(a,b) - dist(a,c)) >= EPS` |
| `Trapezoid Not Isosceles` | `abs(dist(a1,b) - dist(a2,c)) >= EPS` |
| `Top Wider Than Bottom` | `dist(a1,a2) > dist(b,c)` |
| `Points Not Coplanar` | Coplanarity check fails |
| `Degenerate Triangle` | Collinear points or zero-length sides |
| `Degenerate Trapezoid` | Collinear points or zero-length legs |
| `Point Count Mismatch` | Declared N points but fewer coordinates provided |
| `Wrong Number of Values` | Row has neither 9 nor 12 numeric fields |
| `Non-Numeric Values` | Fields cannot be parsed as floats |
| `Empty Row` | Row contains no data |
| `Unknown` | Catch-all for unexpected failures |

### 7.2 Consecutive Error Grouping

When the same error occurs on a contiguous range of CSV rows, the video writer collapses them into **a single error slide** (1.5 s duration) instead of one slide per row:

```
Planes: 1-25
Triangle Not Isosceles
```

This keeps the output video concise when systematic input errors span many consecutive rows.

---

## 8. Data Flow

```
NRRD file ──→ [Volume Loader] ──→ M (3D array, C-contiguous)
                                       │
CSV file  ──→ [CSV Parser] ──→ list of (Plane | Error)
                                       │
                              ┌────────┘
                              ▼
                    [Plane Validator]
                              │
                     valid planes only
                              │
                              ▼
                    [Projector] ──→ list of 2D images (E)
                              │
                              ▼
                    [Video Writer] ──→ MP4 file
                     (groups consecutive identical errors
                      into single annotated slides)
```

---

## 9. Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `volume_loader.py` | Read NRRD, validate dimensions and dtype, return C-contiguous `ndarray` |
| `plane.py` | Represent and validate a plane (3 or 4 points) |
| `projector.py` | Implement the vectorized flat-index projection algorithm, return 2D `ndarray` |
| `video_writer.py` | Collect frames and error info, normalize to 8-bit, group consecutive errors, write MP4 |
| `csv_parser.py` | Parse CSV rows into `Plane` objects; detect and classify 11 error categories |
| `Ex0.py` | CLI entry point, orchestrate the pipeline |
| `gui.py` | Optional desktop GUI wrapping the same pipeline |
