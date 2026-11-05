# Experiment Results & Analysis

**Course:** Introduction to Software Engineering (Ex1)  
**Authors:** Nissim Boaz, Bnaya Amitay

---

## 1. Setup & Execution
- **Volume:** `data/MRHead_1.nrrd` ($256 \times 256 \times 130$, `int16` MRI scan).
- **Datasets:**
  - Official: `data/professor_planes.csv` (4 planes).
  - 15s Showcase: `data/head_demo.csv` (318 rows: 315 valid planes across axial, oblique, coronal sweeps + 3 deliberate boundary errors).

```bash
# Official benchmark
python Ex0.py data/MRHead_1.nrrd data/professor_planes.csv experiment_output.mp4

# 15-second demo video
python Ex0.py data/MRHead_1.nrrd data/head_demo.csv demo.mp4
```

## 2. Results & Performance

| Benchmark | Slices | Measured Speed | Target | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Official Experiment** | 4 (2 valid, 2 invalid) | **103+ FPS** | $\ge 30$ FPS (target 100) | ✅ PASS |
| **Demo Showcase** | 318 (315 valid, 3 errors) | **231+ FPS** | Interactive (> 100 FPS) | ✅ PASS |

## 3. Key Observations
1. **Fidelity:** Axial sweeps show clear brain anatomy (ventricles, skull boundary), oblique sweeps reveal asymmetric internal tissue, and coronal sweeps demonstrate bilateral symmetry.
2. **Error Detection:** All 3 deliberate boundary errors (non-isosceles, non-coplanar, count mismatch) were caught, printed, and rendered as explanatory error slides without crashing.
3. **Consecutive Grouping:** Contiguous rows with identical errors are automatically grouped into a single range slide (e.g., `Planes: 1-25`), keeping the video concise and legible.
