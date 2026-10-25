# Plane Projection of a 3D Volume

**Course:** Introduction to Software Engineering (OOP / OOD), Ariel University – Ex1  
**Team:** [@Nissim-boaz](https://github.com/Nissim-boaz) · [@bnayaamitay](https://github.com/bnayaamitay)  
**License:** Apache-2.0

Extracts an arbitrary 2D cross-section from a 3D volumetric raster (e.g. medical MRI in NRRD format) along any plane and compiles consecutive slices into an MP4 video.

---

## 🎯 Problem Statement

Given a 3D volume matrix $M$ of size $sx \times sy \times sz$ (where $1 \le sx, sy, sz < 1024$ with 8, 16, or 32-bit unsigned/signed voxels) and an arbitrary slicing plane $p$, compute the 2D projection matrix $E$ in real time.

The plane $p$ is defined by:
- **3 Points $(a, b, c)$:** Isosceles triangle with apex $a$ where $|dist(a,b) - dist(a,c)| < 0.001$.
- **4 Points $(a1, a2, b, c)$:** Coplanar isosceles trapezoid where $|dist(a1,b) - dist(a2,c)| < 0.001$ and $dist(a1,a2) \le dist(b,c)$.

The implementation must maintain high runtime performance: **at least 30 FPS is mandatory** on a $500^3$ volume, with a target of 100+ FPS.

---

## 🚀 Getting Started

### 1. Installation
Clone the repository and install dependencies in a virtual environment:

```bash
# Clone
git clone https://github.com/Nissim-boaz/Intro2SE_Ex1.git
cd Intro2SE_Ex1

# Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Graphical User Interface (GUI)
A cross-platform desktop UI (works on Windows, macOS, and Linux) allows selecting files via dialogs and displays live progress:

```bash
python gui.py
```

### 3. Command Line Interface (CLI)
As specified in the assignment requirements:

```bash
python Ex0.py <file.nrrd> <file.csv> <file.mp4>
```

**Example:**
```bash
python Ex0.py data/sample_volume.nrrd data/professor_planes.csv output.mp4
```

---

## 💡 Key Features & Robustness

- **Optimized Projection (NumPy Vectorization):** The inner sampling loops avoid per-sample allocations and use vectorized batch-indexing to achieve high frame rates.
- **On-Screen Annotations:** Each frame features a discreet banner displaying the active plane index and source CSV row number (e.g. `Plane 1 (Row 2)`).
- **Graceful Error Handling:** Invalid plane rows (e.g. non-isosceles or malformed) are detected without crashing; the video presents an informative notice slide explaining the skip reason before proceeding.
- **Configurable Frame Duration:** Each plane slice is presented for 3 seconds at a smooth 30 FPS playback rate.
- **Cross-Platform Compatibility:** Full support for Windows Excel UTF-8 BOM, CRLF line endings, and case/path standards.

---

## 📊 Experimental Results & Benchmark

### Performance Benchmark ($500^3$ Synthetic Volume, 50 Planes)
| Metric | Requirement | Result | Status |
| :--- | :--- | :--- | :--- |
| **Minimum FPS** | $\ge 30$ FPS | **79.4 FPS** | ✅ PASS |
| **Target FPS** | $\ge 100$ FPS | **79.4 FPS** | Sub-target (Python) |
| **Average Slice Time**| $< 33.3$ ms | **12.6 ms** | ✅ PASS |

*(Tested on Apple Silicon M-series. A pure C/C++ or compiled Java backend can exceed 300 FPS).*

### Test Suite
The project includes a comprehensive test suite covering all modules:
```bash
pytest tests/ -v
```
**Result:** `34 passed in 0.18s` (100% test coverage for Volume Loader, Plane geometry validation, CSV parsing, Projector, and Video Writer).

---

## 📂 Project Structure

```text
Intro2SE_Ex1/
├── Ex0.py                 # CLI entry point (required format)
├── gui.py                 # Cross-platform Desktop GUI
├── requirements.txt       # Dependencies (numpy, pynrrd, opencv-python, pytest)
├── src/
│   ├── volume_loader.py   # NRRD 3D volume reader & validator
│   ├── plane.py           # Triangle & trapezoid geometric validation
│   ├── projector.py       # Core projection algorithm (vectorized)
│   ├── csv_parser.py      # Robust CSV reader with status reporting
│   └── video_writer.py    # Video encoding with overlays & error slides
├── data/
│   ├── 50_planes.csv      # Test dataset with 50 valid planes
│   └── professor_planes.csv # Assignment sample planes
├── docs/
│   ├── SRS.md             # Software Requirements Specification
│   ├── algorithm.md       # Detailed algorithm design & pseudo-code
│   └── testing.md         # Testing strategy & verification
└── tests/                 # Unit tests & benchmark suite
```

---

## 📖 Documentation
- [SRS Specification](docs/SRS.md)
- [Algorithm Detailed Design](docs/algorithm.md)
- [Testing Strategy](docs/testing.md)
