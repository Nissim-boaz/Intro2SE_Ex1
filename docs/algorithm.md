# Projection Algorithm – Technical Specification

**Project:** Plane Projection of a 3D Volume (Ex1)  
**Authors:** Nissim Boaz, Bnaya Amitay | **Version:** 1.0

---

## 1. Overview & Data Flow

The algorithm extracts a 2D cross-section $E$ from a 3D volume $M$ ($sx \times sy \times sz$) along a plane defined by 3 points (isosceles triangle) or 4 points (isosceles trapezoid).

```
NRRD Volume M ────┐
                  ├─► [Validator] ─► [Vectorized Projector] ─► 2D Slice E ─► [Video Writer]
CSV Plane Definition ──┘
```

- **Tolerance:** $\varepsilon = 0.001$.
- **Sampling:** Nearest-neighbor, out-of-bounds voxels yield 0.
- **Output Matrix Size:** $\text{rows} = \max(1, \text{round}(D_{ab}))$, $\text{cols} = \max(1, \text{round}(D_{bc}))$.

---

## 2. Mathematical Formulation

### 2.1 Triangle Geometry (3 Points: $a, b, c$)
- **Leg length:** $D_{ab} = \|b - a\| \approx \|c - a\|$
- **Base length:** $D_{bc} = \|c - b\|$
- **Leg unit vectors:** $v_{ab} = \frac{b - a}{D_{ab}}$, $v_{ac} = \frac{c - a}{D_{ab}}$

### 2.2 Trapezoid Geometry (4 Points: $a_1, a_2, b, c$)
- **Leg length:** $D_{ab} = \|b - a_1\| \approx \|c - a_2\|$
- **Base length:** $D_{bc} = \|c - b\|$, with constraint $\|a_2 - a_1\| \le D_{bc} + \varepsilon$
- **Leg unit vectors:** $v_{ab} = \frac{b - a_1}{D_{ab}}$, $v_{ac} = \frac{c - a_2}{D_{ab}}$

### 2.3 Row-by-Row Scanning
For scanline row $y \in [0, \text{rows}-1]$:
1. **Advance leg walkers:**
   - Triangle: $a_1(y) = a + y \cdot v_{ab}$, $a_2(y) = a + y \cdot v_{ac}$
   - Trapezoid: $a_1(y) = a_1 + y \cdot v_{ab}$, $a_2(y) = a_2 + y \cdot v_{ac}$
2. **Row width:** $d_{12} = \|a_2(y) - a_1(y)\|$
3. **Apex boundary condition ($d_{12} = 0$):**  
   Occurs at $y=0$ in triangles. Evaluated as a single point at center column $x = \text{round}(D_{bc} / 2)$ to eliminate division by zero.
4. **Row step vector:** $dp = \frac{a_2(y) - a_1(y)}{d_{12}}$
5. **Voxel sampling:** For step $x_1 \in [0, \text{round}(d_{12})]$:
   $$\text{Sample position: } p(x_1) = a_1(y) + x_1 \cdot dp$$
   $$\text{Canvas column: } x = \text{round}\left(\frac{D_{bc}}{2} - \frac{d_{12}}{2} + x_1\right)$$

---

## 3. High-Performance Vectorization

To achieve $> 100$ FPS without per-voxel Python overhead, row sampling is fully vectorized:

```python
# Fully vectorized row evaluation (src/projector.py)
t = np.arange(0, round(d12) + 1)                 # Steps along current row
points = a1_curr + np.outer(t, dp)                # (N, 3) sample coordinates in 3D

# Nearest-neighbor voxel indices with bounds clipping
ix = np.clip(np.round(points[:, 0]).astype(int), 0, sx - 1)
iy = np.clip(np.round(points[:, 1]).astype(int), 0, sy - 1)
iz = np.clip(np.round(points[:, 2]).astype(int), 0, sz - 1)

# Single contiguous 1D memory lookup into flattened volume
flat_idx = ix * (sy * sz) + iy * sz + iz
values = M.ravel()[flat_idx]

# Mask out voxels strictly outside volume boundaries
in_bounds = (
    (points[:, 0] >= -0.5) & (points[:, 0] < sx - 0.5) &
    (points[:, 1] >= -0.5) & (points[:, 1] < sy - 0.5) &
    (points[:, 2] >= -0.5) & (points[:, 2] < sz - 0.5)
)
values[~in_bounds] = 0

# Assign batch to row in output canvas E
x_indices = np.clip(np.round(Dbc / 2.0 - d12 / 2.0 + t).astype(int), 0, cols - 1)
E[y, x_indices] = values
```

### Measured Throughput
| Dataset | Resolution | Slices | Measured FPS | Requirement |
| :--- | :--- | :--- | :--- | :--- |
| **MRHead (official)** | $256 \times 256 \times 130$ | 4 | **103+ FPS** | $\ge 30$ FPS (target $\ge 100$) |
| **Head Demo** | $256 \times 256 \times 130$ | 315 | **231+ FPS** | Target exceeded by $2.3\times$ |

---

## 4. Geometric Validation Rules

Every input row is verified before projection:

| Check | Condition | Error Category |
| :--- | :--- | :--- |
| **Degeneracy** | Edge lengths $\le \varepsilon$ or $\|\vec{v}_1 \times \vec{v}_2\| < \varepsilon$ | `Collinear Points (Degenerate)` / `Zero-Length Side` |
| **Triangle Isosceles** | $|\|b - a\| - \|c - a\|| \ge \varepsilon$ | `Triangle Not Isosceles` |
| **Trapezoid Isosceles**| $|\|b - a_1\| - \|c - a_2\|| \ge \varepsilon$ | `Trapezoid Not Isosceles` |
| **Base Ordering** | $\|a_2 - a_1\| > \|c - b\| + \varepsilon$ | `Top Wider Than Bottom` |
| **Coplanarity (4 pts)** | $|\hat{n}_{a_1,b,c} \cdot (a_2 - a_1)| \ge \varepsilon$ | `Points Not Coplanar` |
| **Parser Integrity** | Field count $\notin \{9, 10, 12, 13\}$ or declared count mismatch | `Point Count Mismatch` / `Wrong Number of Values` |

---

## 5. Error Slide Generation & Consecutive Grouping

- Invalid planes do not abort execution; an annotated error slide is rendered to the video canvas for 1.5 seconds (45 frames at 30 FPS).
- **Consecutive Error Grouping:** Contiguous rows sharing the identical error category are collapsed into a single slide displaying the full index range (e.g., `Planes: 1-25: Triangle Not Isosceles`), preventing redundant video clutter.
