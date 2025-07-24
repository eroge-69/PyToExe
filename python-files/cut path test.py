import ezdxf
import math
from shapely.geometry import Point
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from collections import Counter

# --- Helper functions ---
def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def arc_length(arc):
    angle = abs(arc.dxf.end_angle - arc.dxf.start_angle)
    return math.radians(angle) * arc.dxf.radius

def lwpolyline_length(poly):
    points = list(poly.get_points())
    if poly.closed:
        points.append(points[0])
    return sum(distance(points[i], points[i + 1]) for i in range(len(points) - 1))

def center_of_entity(entity):
    if entity.dxftype() == 'LINE':
        return ((entity.dxf.start[0] + entity.dxf.end[0]) / 2,
                (entity.dxf.start[1] + entity.dxf.end[1]) / 2)
    elif entity.dxftype() == 'CIRCLE':
        return (entity.dxf.center[0], entity.dxf.center[1])
    elif entity.dxftype() == 'ARC':
        angle = math.radians((entity.dxf.start_angle + entity.dxf.end_angle) / 2)
        cx, cy = entity.dxf.center[0], entity.dxf.center[1]
        return (cx + entity.dxf.radius * math.cos(angle),
                cy + entity.dxf.radius * math.sin(angle))
    elif entity.dxftype() == 'LWPOLYLINE':
        points = list(entity.get_points())
        if not points:
            return (0, 0)
        x_coords, y_coords = zip(*[(pt[0], pt[1]) for pt in points])
        return (sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords))
    return (0, 0)

def is_solid_line(entity, doc):
    ent_linetype = entity.dxf.get('linetype', 'BYLAYER').upper()

    if ent_linetype == 'CONTINUOUS':
        return True

    if ent_linetype == 'BYLAYER':
        layer_name = entity.dxf.layer
        layer = doc.layers.get(layer_name)
        if layer:
            layer_linetype = layer.dxf.linetype.upper()
            return layer_linetype == 'CONTINUOUS'
        else:
            # If no layer found, assume not solid
            return False
    # Any other linetype considered non-solid
    return False

# --- Main Function ---
def load_dxf_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("DXF files", "*.dxf")])
    if not file_path:
        print("No file selected.")
        return

    try:
        doc = ezdxf.readfile(file_path)
    except Exception as e:
        print(f"❌ Failed to read DXF file: {e}")
        return

    msp = doc.modelspace()

    # --- Show entity types summary ---
    print("\n📋 Entity Types in File:")
    type_counts = Counter(e.dxftype() for e in msp)
    for t, c in type_counts.items():
        print(f"  {t}: {c}")

    cut_length = 0.0
    centers = []

    valid_types = {'LINE', 'CIRCLE', 'ARC', 'LWPOLYLINE'}
    for e in msp:
        if e.dxftype() not in valid_types:
            continue

        if not is_solid_line(e, doc):
            continue

        try:
            if e.dxftype() == 'LINE':
                cut_length += distance(e.dxf.start, e.dxf.end)
                centers.append(center_of_entity(e))
            elif e.dxftype() == 'CIRCLE':
                cut_length += 2 * math.pi * e.dxf.radius
                centers.append(center_of_entity(e))
            elif e.dxftype() == 'ARC':
                cut_length += arc_length(e)
                centers.append(center_of_entity(e))
            elif e.dxftype() == 'LWPOLYLINE':
                cut_length += lwpolyline_length(e)
                centers.append(center_of_entity(e))
        except Exception as err:
            print(f"⚠️ Error processing {e.dxftype()}: {err}")

    if not centers:
        print("\n⚠️ No valid solid line entities found for perimeter/travel calculation.")
        return

    # --- Compute travel distance between cuts ---
    visited = []
    total_travel = 0.0
    current = centers[0]
    remaining = centers[1:]
    visited.append(current)

    while remaining:
        next_pt = min(remaining, key=lambda p: distance(current, p))
        total_travel += distance(current, next_pt)
        current = next_pt
        visited.append(current)
        remaining.remove(next_pt)

    # --- Print results ---
    print(f"\n✅ Total Cut Perimeter (solid lines only): {cut_length:.2f} units")
    print(f"📏 Travel Distance Between Cuts: {total_travel:.2f} units")

    # --- Optional plot ---
    if visited:
        xs, ys = zip(*visited)
        plt.figure(figsize=(8, 6))
        plt.plot(xs, ys, '-o', label='Travel Path')
        plt.title('Tool Travel Path')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.legend()
        plt.axis('equal')
        plt.grid(True)
        plt.show()

# --- Run Program ---
if __name__ == "__main__":
    load_dxf_file()
