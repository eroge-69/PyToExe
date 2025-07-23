from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import ezdxf
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union, polygonize
import tempfile
import os

app = FastAPI()

def get_polygons_from_layer(msp, layer_name):
    polygons = []
    for e in msp.query('LWPOLYLINE[layer=="{}"]'.format(layer_name)):
        points = [(p[0], p[1]) for p in e.get_points()]
        if len(points) >= 3:
            polygons.append(Polygon(points))
    return polygons

@app.post("/process_dxf/")
async def process_dxf(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as temp:
        temp.write(await file.read())
        temp_path = temp.name

    doc = ezdxf.readfile(temp_path)
    msp = doc.modelspace()

    polygons_arch = get_polygons_from_layer(msp, "Αρχικά Πολύγωνα")
    polygons_base = get_polygons_from_layer(msp, "Βασικό Πολύγωνο")
    polygons_final = get_polygons_from_layer(msp, "Τελικό Πολύγωνο")

    if not polygons_arch or not polygons_base or not polygons_final:
        return JSONResponse({"error": "Ένα ή περισσότερα layers δεν βρέθηκαν ή είναι άδεια."})

    results = []
    counter = 1

    for idx, poly in enumerate(polygons_arch, 1):
        intersections = poly.intersection(polygons_final[0])
        if not intersections.is_empty:
            if intersections.geom_type == 'Polygon':
                intersections = [intersections]
            for part in intersections:
                area = part.area
                coords = list(part.exterior.coords)
                results.append({
                    "A/A": counter,
                    "Κορυφές": [f"{c[0]:.2f},{c[1]:.2f}" for c in coords],
                    "Εμβαδό": f"{area:.2f} τ.μ.",
                    "Από ΚΑΕΚ": f"Αρχ-{idx}",
                    "Σε ΚΑΕΚ": "Τ-1",
                    "Παρατήρηση": "Διεκδικούμενο"
                })
                counter += 1

    for idx, poly in enumerate(polygons_base, 1):
        diff = poly.difference(polygons_final[0])
        if not diff.is_empty:
            if diff.geom_type == 'Polygon':
                diff = [diff]
            for part in diff:
                area = part.area
                coords = list(part.exterior.coords)
                results.append({
                    "A/A": counter,
                    "Κορυφές": [f"{c[0]:.2f},{c[1]:.2f}" for c in coords],
                    "Εμβαδό": f"{area:.2f} τ.μ.",
                    "Από ΚΑΕΚ": f"Β-1",
                    "Σε ΚΑΕΚ": f"ΝΕΟ ΚΑΕΚ-{idx}",
                    "Παρατήρηση": "Αφαιρούμενο"
                })
                counter += 1

    output_json = os.path.join(tempfile.gettempdir(), "geometric_changes.json")
    with open(output_json, "w", encoding="utf-8") as f:
        import json
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Αν θέλεις να δημιουργεί και νέο DXF αρχείο για εξαγωγή:
    output_dxf = os.path.join(tempfile.gettempdir(), "output.dxf")
    new_doc = ezdxf.new()
    new_msp = new_doc.modelspace()

    for r in results:
        pts = [tuple(map(float, p.split(','))) for p in r["Κορυφές"]]
        new_msp.add_lwpolyline(pts, close=True)

    new_doc.saveas(output_dxf)

    return {
        "message": "Επεξεργασία Ολοκληρώθηκε",
        "download_json": f"/download_json/",
        "download_dxf": f"/download_dxf/"
    }

@app.get("/download_json/")
def download_json():
    file_path = os.path.join(tempfile.gettempdir(), "geometric_changes.json")
    return FileResponse(file_path, media_type='application/json', filename="geometric_changes.json")

@app.get("/download_dxf/")
def download_dxf():
    file_path = os.path.join(tempfile.gettempdir(), "output.dxf")
    return FileResponse(file_path, media_type='application/dxf', filename="output.dxf")

