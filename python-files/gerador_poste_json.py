
import json
import math
import os

def create_circle_polygon(lat, lon, radius_m, num_points=24):
    earth_radius = 6378137
    coords = []
    for i in range(num_points + 1):
        angle = 2 * math.pi * i / num_points
        dx = radius_m * math.cos(angle)
        dy = radius_m * math.sin(angle)

        dlon = (dx / (earth_radius * math.cos(math.radians(lat)))) * (180 / math.pi)
        dlat = (dy / earth_radius) * (180 / math.pi)

        coords.append([lon + dlon, lat + dlat])
    return coords

def main():
    print("=== Gerador de GeoJSON para poste cilíndrico ===")
    try:
        radius = float(input("Digite o raio do poste (em metros): "))
        height = float(input("Digite a altura do poste (em metros): "))
        lat = float(input("Digite a latitude: "))
        lon = float("Digite a longitude: "))
    except ValueError:
        print("Erro: entrada inválida.")
        return

    coords = create_circle_polygon(lat, lon, radius)

    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "height": height,
                    "radius": radius
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                }
            }
        ]
    }

    filename = f"poste_{int(height)}m_{int(radius*100)}cm.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Arquivo salvo: {filename}")

if __name__ == "__main__":
    main()
