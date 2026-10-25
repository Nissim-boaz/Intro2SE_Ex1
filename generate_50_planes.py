import csv

def generate_50_planes():
    filename = "data/50_planes.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Number of Points (3 or 4)", "x1", "y1", "z1", "x2", "y2", "z2", "x3", "y3", "z3", "x4", "y4", "z4"])
        
        # 1. 25 Horizontal Slices (Triangles) scanning across Z from 5 to 245
        for i in range(25):
            z = 10 + i * 8
            # Apex at (100, 100, z), endpoints at (0, 200, z) and (200, 200, z)
            # dist(a,b) = sqrt(100^2 + 100^2) = 141.42
            # dist(a,c) = sqrt(100^2 + 100^2) = 141.42 -> Perfectly isosceles
            writer.writerow([3, 100, 100, z, 0, 200, z, 200, 200, z, "", "", ""])

        # 2. 25 Coronal/Sagittal Slices (Trapezoids) scanning across Y from 10 to 200
        for i in range(25):
            y = 10 + i * 8
            # Top: a1=(50, y, 0), a2=(150, y, 0) -> width = 100
            # Bottom: b=(0, y, 200), c=(200, y, 200) -> width = 200
            # Legs: dist(a1,b) = sqrt(50^2 + 200^2) = 206.155
            #       dist(a2,c) = sqrt(50^2 + 200^2) = 206.155 -> Perfectly isosceles trapezoid
            writer.writerow([4, 50, y, 0, 150, y, 0, 0, y, 200, 200, y, 200])

    print(f"Generated {filename} with 50 valid planes.")

if __name__ == "__main__":
    generate_50_planes()
