import ezdxf
import csv
import math

# Inserisci il tuo file DXF qui
input_file = "disegno.dxf"
output_file = "punti.csv"

# Carica il DXF
doc = ezdxf.readfile(input_file)
msp = doc.modelspace()

punti = []

for e in msp:
    if e.dxftype() == "LINE":
        punti.append((e.dxf.start.x, e.dxf.start.y))
        punti.append((e.dxf.end.x, e.dxf.end.y))
    elif e.dxftype() == "POINT":
        punti.append((e.dxf.location.x, e.dxf.location.y))
    elif e.dxftype() == "LWPOLYLINE":
        for x, y, *_ in e.get_points():
            punti.append((x, y))
    elif e.dxftype() == "CIRCLE":
        cx, cy, r = e.dxf.center.x, e.dxf.center.y, e.dxf.radius
        for i in range(0, 360, 10):
            ang = math.radians(i)
            punti.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))

# Salva su CSV
with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["X", "Y"])
    writer.writerows(punti)

print(f"Coordinate salvate in {output_file}")
