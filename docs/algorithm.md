# Projection Algorithm

**Course:** Introduction to Software Engineering (Ex1)  
**Authors:** Nissim Boaz, Bnaya Amitay

---

## 1. Geometric Model & Walkers ($\varepsilon = 0.001$)
The algorithm projects a 2D slice $E$ of size $\text{round}(D_{ab}) \times \text{round}(D_{bc})$ from volume $M$:

- **Triangle (3 pts: $a, b, c$):** Apex $a$, base $b-c$. Leg length $D_{ab} = \|b - a\|$, base length $D_{bc} = \|c - b\|$. Unit vectors: $v_{ab} = (b - a)/D_{ab}$, $v_{ac} = (c - a)/D_{ab}$.
- **Trapezoid (4 pts: $a_1, a_2, b, c$):** Top $a_1-a_2$, base $b-c$. Leg length $D_{ab} = \|b - a_1\|$, base length $D_{bc} = \|c - b\|$. Unit vectors: $v_{ab} = (b - a_1)/D_{ab}$, $v_{ac} = (c - a_2)/D_{ab}$.

## 2. Row Scanning & Sampling
For each row $y \in [0, \text{round}(D_{ab}) - 1]$:
1. **Advance walkers:** $a_1(y) = a_1 + y \cdot v_{ab}$, $a_2(y) = a_2 + y \cdot v_{ac}$.
2. **Row width:** $d_{12} = \|a_2(y) - a_1(y)\|$.
   - *Apex row ($d_{12} = 0$):* Sample single point at center column $x = \text{round}(D_{bc} / 2)$ to prevent division by zero.
3. **Step vector:** $dp = (a_2(y) - a_1(y)) / d_{12}$.
4. **Voxel sampling ($x_1 \in [0, \text{round}(d_{12})]$):**
   - 3D coordinates: $p = a_1(y) + x_1 \cdot dp$.
   - Output canvas position: $x = \text{round}(D_{bc}/2 - d_{12}/2 + x_1)$.
   - Nearest-neighbor: round coordinates to integer indices $(ix, iy, iz)$. If in volume bounds, take $M[ix, iy, iz]$; otherwise $0$.

## 3. Vectorized Flat-Index Optimization
To exceed 100 FPS, inner loops are eliminated using NumPy vectorization:
- All sample points for an entire row are computed simultaneously via `points = a1_curr + np.outer(np.arange(d12 + 1), dp)`.
- 3D coordinates are converted to 1D flat memory offsets: `flat_idx = ix * (sy * sz) + iy * sz + iz`.
- Voxel intensities are extracted in a single memory lookup: `M.ravel()[flat_idx]`.

## 4. Plane Validation
A row is valid only if:
1. Edge lengths $> \varepsilon$ and points are not collinear ($\|\vec{u} \times \vec{v}\| \ge \varepsilon$).
2. Triangle: $|\|b - a\| - \|c - a\|| < \varepsilon$.
3. Trapezoid: $|\|b - a_1\| - \|c - a_2\|| < \varepsilon$, $\|a_2 - a_1\| \le \|c - b\| + \varepsilon$, and coplanar ($|\hat{n} \cdot (a_2 - a_1)| < \varepsilon$).
