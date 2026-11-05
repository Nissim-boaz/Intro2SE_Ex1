


# Ex1: Plane Projection of a 3D Volume

**Course:** Introduction to Software Engineering (OOP/OOD), Ariel University  
**Authors:** Nissim Boaz & Bnaya Amitay  

---

## Problem Definition
> *"Given 3D raster data matrix (M), and a plane (p). Compute the 2D matrix (image) of the projection of p in V"*  
> *"Given a 3D matrix (M) of size sx\*sy\*sz byte values (the entry M[x][y][z] is an unsigned integer value of 8, 16, 32 bits), where 1<=sx,sy,sz<2^10 and 0<=x<sx, 0<=y<sy, 0<=z<sz."*

The goal is to extract arbitrary 2D cross-sections (projections) from a 3D volumetric matrix $M$ along any plane $p$.

The plane $p$ is defined by:
- **3 Points $(a, b, c)$:** An isosceles triangle where $|dist(a,b) - dist(a,c)| < 0.001$.
- **4 Points $(a1, a2, b, c)$:** An isosceles trapezoid where $|dist(a1,b) - dist(a2,c)| < 0.001$, $dist(a1,a2) \le dist(b,c)$, and all four points are coplanar.

Points outside the volume boundaries sample a value of $0$.

---

## Project Scope
- **Input:** 3D volume in NRRD format, and a CSV file specifying slicing planes (each row defining 3 or 4 points).
- **Processing:** Efficient vectorized sampling of voxel values along the plane in index space.
- **Output:** An MP4 video file compiling all computed 2D projection frames in CSV row order.
- **Performance:** Optimized runtime achieving over 103 FPS on the MRHead volume (256×256×130), and over 231 FPS on the demo dataset.
- **Robustness:** Automatic detection and skipping of invalid planes with informative error slides in the output video. Consecutive identical errors are grouped into a single slide (e.g., `Planes: 1–25`) to keep the video concise.

---

## Usage

```bash
pip install -r requirements.txt
python Ex0.py file.nrrd file.csv file.mp4
```

*Optional Desktop GUI:*
```bash
python gui.py
```

---

<p align="center">
  <video src="https://github.com/user-attachments/assets/5b04c373-2602-41fb-b3bd-a82f5170110c" width="600" autoplay loop muted playsinline controls></video>
  <br>
  <i>Demo: 3D volume plane projection in action</i>
</p>

---

## Documentation
- [Software Requirements Specification (SRS)](docs/SRS.md)
- [Algorithm Detailed Design](docs/algorithm.md)
- [Testing Strategy](docs/testing.md)
- [Experiment Results](docs/experiment.md)
