#!/usr/bin/env python3
"""
pnp_calc_ext.py – rozšířená pomůcka pro výpočet a vykreslení
požárně nebezpečného prostoru (PNP) podle ČSN 73 0802, tab. F.2 (zjednodušená).

Novinky oproti původní verzi
----------------------------
* **DXF export** – generuje soubor vhodný pro AutoCAD/BricsCAD/Archicad …
* **Batch režim** – načte víc případů z CSV, každý zvlášť vykreslí a exportuje.
* **Více kritických hustot toku** – umí paralelně ověřit např. 18,5 kW/m² i 15 kW/m².
* **Jednoduché přepnutí na PNG/DXF** – volby `--png`, `--dxf`.
* **Připraveno pro kompilaci PyInstallerem** na samostatné EXE.

Použití
-------
Single run (PNG + DXF, dvě q<sub>crit</sub>):
```
python pnp_calc_ext.py -A 18 -O 2.4 -w 6 --qcrit 18.5,15 --png --dxf
```
Batch run z CSV → složka `vysledky`:
```
python pnp_calc_ext.py --csv vstupy.csv --qcrit 18.5,15 --png --dxf --outdir vysledky
```

Příklad CSV (`vstupy.csv`):
```
label,area_wall,area_open,width,km,kv
Fasada_A,18,2.4,6,1,1
Fasada_B,72,6.8,12,0.9,1.1
```

EXE build (Windows):
```
pip install pyinstaller
pyinstaller --onefile pnp_calc_ext.py
```

Poznámka: Výpočet pro jiné q<sub>crit</sub> než 18,5 kW/m² je proveden
prostým přepočtem vzdálenosti podle vztahu  d ~ √(18,5 / q<sub>crit</sub>).
Pro oficiální posouzení doporučuji ověřit platnost postupu vůči aktuální
normě / metodice PBŘ.
"""

import argparse
import csv
import math
import os
from typing import List, Dict

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import ezdxf

# Základní kritická hustota toku, pro kterou platí tabulka F.2 (ČSN 73 0802)
BASE_QCRIT = 18.5  # kW m⁻²

# Tabulka F.2 – hranice Ae [m²] → d [m]
TABLE = [
    (0.2, 0.5), (0.5, 0.8), (1.0, 1.2), (2.0, 1.8),
    (4.0, 2.6), (6.0, 3.1), (8.0, 3.6)  # >10 → 4,5 m
]

def d_from_ae(ae: float) -> float:
    """Vrátí odstupovou vzdálenost d pro dané Ae podle tabulky F.2."""
    for limit, dist in TABLE:
        if ae <= limit:
            return dist
    return 4.5

def scale_d(d_base: float, qcrit: float) -> float:
    """Přepočet d na jinou kritickou hustotu toku (≈ d ~ √(q_base / q))."""
    return d_base * math.sqrt(BASE_QCRIT / qcrit)

def draw_png(width: float, height: float, d: float, title: str, outpath: str) -> None:
    """Vykreslí stěnu + PNP do PNG."""
    fig, ax = plt.subplots()
    ax.add_patch(Rectangle((0, 0), width, height, fill=False, linewidth=2))
    ax.add_patch(Rectangle((width, 0), d, height, color="red", alpha=0.25))
    ax.add_patch(Circle((width, 0), d, color="red", alpha=0.25))
    ax.add_patch(Circle((width, height), d, color="red", alpha=0.25))

    ax.set_aspect("equal")
    ax.set_xlim(-0.5, width + d + 0.5)
    ax.set_ylim(-0.5, height + d + 0.5)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title(title)

    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close(fig)

def export_dxf(width: float, height: float, d: float, outpath: str) -> None:
    """Vytvoří jednoduchý DXF s obrysem stěny a PNP."""
    doc = ezdxf.new()
    msp = doc.modelspace()

    # stěna (obdélník)
    msp.add_lwpolyline([(0, 0), (width, 0), (width, height), (0, height), (0, 0)])

    # PNP – pruh a půlválce
    msp.add_lwpolyline([(width, 0), (width + d, 0), (width + d, height), (width, height), (width, 0)])
    msp.add_arc((width, 0), d, 270, 90)       # dolní půlkruh
    msp.add_arc((width, height), d, 90, 270)  # horní půlkruh

    doc.saveas(outpath)

def draw_and_export(params: Dict[str, float], qcrit_list: List[float], outdir: str) -> None:
    label = params.get("label", "case")
    A_wall = float(params["area_wall"])
    A_open = float(params["area_open"])
    width = float(params.get("width", 6))
    km = float(params.get("km", 1))
    kv = float(params.get("kv", 1))

    Ae = A_open * km * kv
    d_base = d_from_ae(Ae)
    height = A_wall / width

    for qcrit in qcrit_list:
        d = scale_d(d_base, qcrit)
        tag = f"q{str(qcrit).replace('.', 'p')}"  # např. q15 nebo q18p5
        title = f"PNP – d = {d:.2f} m   (Aₑ = {Ae:.2f} m², q_crit = {qcrit} kW/m²)"

        if params.get("png"):
            png_path = os.path.join(outdir, f"{label}_{tag}.png")
            draw_png(width, height, d, title, png_path)
        if params.get("dxf"):
            dxf_path = os.path.join(outdir, f"{label}_{tag}.dxf")
            export_dxf(width, height, d, dxf_path)

    print(f"✓ {label}: hotovo pro q_crit = {', '.join(map(str, qcrit_list))}")

def read_csv(csv_path: str):
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            yield row

def parse_args():
    p = argparse.ArgumentParser(description="Výpočet PNP s DXF a batch podporou")
    p.add_argument("-A", "--area_wall", type=float, help="plocha stěny [m²]")
    p.add_argument("-O", "--area_open", type=float, help="plocha otvorů [m²]")
    p.add_argument("-w", "--width", type=float, default=6, help="šířka pruhu stěny [m]")
    p.add_argument("--km", type=float, default=1, help="koeficient k_m")
    p.add_argument("--kv", type=float, default=1, help="koeficient k_v")
    p.add_argument("--qcrit", default="18.5", help="seznam q_crit oddělený čárkami")
    p.add_argument("--png", action="store_true", help="export do PNG")
    p.add_argument("--dxf", action="store_true", help="export do DXF")
    p.add_argument("--csv", help="cesta k CSV souboru s více případy")
    p.add_argument("--outdir", default="outputs", help="výstupní složka")
    return p.parse_args()

def main():
    args = parse_args()
    qcrit_list = [float(v) for v in args.qcrit.split(",")]
    os.makedirs(args.outdir, exist_ok=True)

    if args.csv:  # batch režim
        for row in read_csv(args.csv):
            row.setdefault("png", args.png)
            row.setdefault("dxf", args.dxf)
            draw_and_export(row, qcrit_list, args.outdir)
    else:  # single run
        if args.area_wall is None or args.area_open is None:
            raise SystemExit("Musíte zadat -A a -O nebo --csv.")
        params = {
            "label": "single",
            "area_wall": args.area_wall,
            "area_open": args.area_open,
            "width": args.width,
            "km": args.km,
            "kv": args.kv,
            "png": args.png,
            "dxf": args.dxf,
        }
        draw_and_export(params, qcrit_list, args.outdir)

if __name__ == "__main__":
    main()
