# Plane Projection of a 3D Volume

Ex1 – Introduction to Software Engineering, Ariel University

Extracts an arbitrary 2D cross-section from a 3D NRRD volume (e.g. MRI) and writes one video frame per plane.

## Problem
Given a 3D matrix `M` (`sx × sy × sz`, 8/16/32-bit unsigned, each size < 1024) and a plane `p`, compute the 2D image of `p` inside `M`, at any orientation (not only the X/Y/Z axes).

A plane is given by 3 points `(a, b, c)` (isosceles triangle) or 4 points `(a1, a2, b, c)` (isosceles trapezoid), with `EPS = 0.001`.

## Usage
```bash
pip install -r requirements.txt
python Ex0.py file.nrrd file.csv file.mp4
```
- `file.nrrd` – 3D volume
- `file.csv` – one plane per row (3 or 4 points, `x,y,z` each)
- `file.mp4` – output video, one frame per row

Performance target: 30+ FPS required, 100+ FPS on a 500³ volume.

## Docs
- [SRS](docs/SRS.md) – requirements specification
- [Algorithm](docs/algorithm.md) – detailed design
- [Testing](docs/testing.md) – testing strategy

## Structure
`src/` code · `tests/` tests · `data/` NRRD files · `docs/` documents

## Results
_To be added after the experiment._

## Team
[@Nissim-boaz](https://github.com/Nissim-boaz) · [@bnayaamitay](https://github.com/bnayaamitay)

Work on branches, merge to `main` via Pull Request.

## License
Apache-2.0
