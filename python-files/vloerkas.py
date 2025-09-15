import os
import pandas as pd
import cadquery as cq
from cadquery import Color

BOARD_THICKNESS = 16  # mm
CONFIG_FILE = "config.txt"

# ---------- Safe input ----------
def safe_input(prompt, min_value=0, default=None):
    while True:
        try:
            if default is not None:
                raw = input(f"{prompt} [default={default}]: ").strip()
            else:
                raw = input(f"{prompt}: ").strip()
            if raw == "" and default is not None:
                return default
            value = int(raw)
            if value < min_value:
                print(f"⚠️ Value must be at least {min_value}.")
                continue
            return value
        except ValueError:
            print("⚠️ Invalid number. Enter an integer.")

# ---------- Config handling ----------
def load_config():
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    config[k] = int(v) if v.isdigit() else v
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        for k, v in config.items():
            f.write(f"{k}={v}\n")

# ---------- User inputs ----------
def get_user_inputs():
    config = load_config()
    def ci(key, prompt, minv=1):
        default = config.get(key)
        value = safe_input(prompt, min_value=minv, default=default)
        config[key] = value
        return value

    cabinet_width = ci("cabinet_width", "Cabinet width (mm)")
    cabinet_depth = ci("cabinet_depth", "Cabinet depth (mm)")
    total_height = ci("total_height", "Total height incl. countertop (mm)")
    plinth_height = ci("plinth_height", "Plinth height (mm)")
    plinth_inset = ci("plinth_inset", "Plinth inset (mm)")
    countertop_thickness = ci("countertop_thickness", "Countertop thickness (mm)")
    countertop_overhang = ci("countertop_overhang", "Countertop overhang (mm)")
    shelves = ci("shelves", "Number of shelves", minv=0)
    edging_tolerance = ci("edging", "Edging tolerance (mm)", minv=0)

    countertop_type = input(f"Countertop type [{config.get('countertop_type','Postform')}]: ") or config.get('countertop_type','Postform')
    internal_color = input(f"Internal color [{config.get('internal_color','white')}]: ") or config.get('internal_color','white')
    external_color = input(f"External color [{config.get('external_color','gray')}]: ") or config.get('external_color','gray')

    config.update({
        "countertop_type": countertop_type,
        "internal_color": internal_color,
        "external_color": external_color
    })
    save_config(config)

    return (cabinet_width, cabinet_depth, total_height, plinth_height, plinth_inset,
            shelves, countertop_thickness, countertop_overhang, countertop_type,
            internal_color, external_color, edging_tolerance)

# ---------- Drawer inputs ----------
def get_drawer_inputs(remaining_height, num_doors, door_width, edging):
    drawers = []
    wants_drawer = input("Do you want drawers above doors? (y/n) [n]: ").strip().lower() or "n"
    if wants_drawer != "y" or remaining_height <= 0:
        return drawers

    num_vertical = safe_input("Number of drawers vertically above each door", min_value=1)
    num_horizontal = safe_input("Number of horizontal drawers per door", min_value=1)

    for door_index in range(num_doors):
        horizontal_drawer_width = door_width  # width matches door (no extra subtraction)
        vertical_drawer_height = remaining_height / num_vertical - edging*2  # top/bottom edging
        print(f"Door {door_index+1} drawer width: {horizontal_drawer_width:.1f} mm, height: {vertical_drawer_height:.1f} mm")
        for v in range(num_vertical):
            for h in range(num_horizontal):
                drawers.append({
                    "width": horizontal_drawer_width,
                    "height": vertical_drawer_height,
                    "color": None,
                    "name": f"Drawer D{door_index+1}V{v+1}H{h+1}"
                })
    return drawers

# ---------- Excel export ----------
def save_excel(parts, filename, parameters):
    df = pd.DataFrame(parts, columns=[
        "No","Description","Color","W (mm)","H (mm)","Thickness (mm)","L edging","W edging","Notes"
    ])
    df["Area (m2)"] = df["W (mm)"]*df["H (mm)"]/1_000_000
    df_sorted = df.sort_values(by="Color").reset_index(drop=True)

    BOARD_AREA = 1.22*2.44
    summary = df_sorted.groupby("Color")["Area (m2)"].sum().reset_index()
    summary["Required boards (1220x2440)"] = (summary["Area (m2)"]/BOARD_AREA).apply(lambda x:int(x)+1)

    with pd.ExcelWriter(filename) as writer:
        df_sorted.to_excel(writer, index=False, sheet_name="Cutting List")
        summary.to_excel(writer, index=False, sheet_name="Summary")

        # Save user parameters
        param_items = list(parameters.items())
        param_df = pd.DataFrame(param_items, columns=["Parameter", "Value"])
        param_df.to_excel(writer, index=False, sheet_name="Parameters")

    print(f"✅ Excel saved: {filename}")

# ---------- STEP export ----------
def export_step(parts, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    color_map = {"white": Color(1,1,1),"gray":Color(0.5,0.5,0.5)}
    for part in parts:
        desc = part[1]
        W = float(part[3])
        H = float(part[4])
        D = BOARD_THICKNESS
        if W<=0 or H<=0:
            continue
        cq_color = color_map.get(part[2].lower(), Color(0.8,0.8,0.8))
        panel = cq.Workplane("XY").box(W,H,D)
        cq.exporters.export(panel, os.path.join(folder,f"{desc}.step"))
    print(f"✅ STEP parts exported to {folder}")

# ---------- Preview doors/drawers ----------
def preview_parts(parts):
    print("\n📐 Preview of doors and drawers:")
    print(f"{'Name':25} {'Width':>8} mm {'Height':>8} mm")
    print("-"*50)
    for p in parts:
        if "Door" in p[1] or "Drawer" in p[1]:
            print(f"{p[1]:25} {float(p[3]):8.1f} {float(p[4]):8.1f}")
    print("-"*50)

# ---------- Main ----------
def vloerkas():
    (cabinet_width, cabinet_depth, total_height, plinth_height, plinth_inset,
     shelves, countertop_thickness, countertop_overhang, countertop_type,
     internal_color, external_color, edging_tolerance) = get_user_inputs()

    inside_width = cabinet_width - 2*BOARD_THICKNESS
    shelf_depth = cabinet_depth - 5
    carcass_height = total_height - plinth_height - countertop_thickness

    # Door calculation
    num_doors = 1 if cabinet_width <= 500 else 2
    door_width_total = cabinet_width / num_doors
    door_width = door_width_total - edging_tolerance*2

    # user-visible door height (used to compute remaining height)
    door_height = safe_input(f"Set door height (mm) up to carcass height {carcass_height}", min_value=1, default=carcass_height)

    # door panel (cut) height subtracts edging on top+bottom
    door_panel_height = door_height - edging_tolerance*2
    if door_panel_height < 0:
        print("⚠️ Warning: door_panel_height <= 0 after edging subtraction. Setting to 0.")
        door_panel_height = 0

    # drawers use remaining visible height above door (user-entered door_height)
    remaining_height_for_drawers = carcass_height - door_height

    # Drawer calculation
    drawers = get_drawer_inputs(remaining_height_for_drawers, num_doors, door_width, edging_tolerance)

    # ---------- Generate parts ----------
    parts = []
    part_no = 1

    if not drawers:
        parts.append([part_no,"Top panel",internal_color,inside_width,cabinet_depth,BOARD_THICKNESS,internal_color,internal_color,"Covered by countertop"])
        part_no+=1

    parts.append([part_no,"Bottom panel",internal_color,inside_width,cabinet_depth,BOARD_THICKNESS,internal_color,internal_color,"On floor"])
    part_no+=1

    for i in range(shelves):
        parts.append([part_no,f"Shelf {i+1}",internal_color,inside_width,shelf_depth,BOARD_THICKNESS,external_color,external_color,"Edged front only"])
        part_no+=1

    # Use door_panel_height for the part (cut) size, but cutters know the user-entered door_height is the visible size
    if door_panel_height > 0:
        for i in range(num_doors):
            parts.append([part_no,f"Door {i+1}",external_color,door_width,door_panel_height,BOARD_THICKNESS,external_color,external_color,"Edged all around"])
            part_no+=1

    for d in drawers:
        parts.append([part_no,d["name"],external_color,d["width"],d["height"],BOARD_THICKNESS,external_color,external_color,"Edged all around"])
        part_no+=1

    # Plinth
    front_back_width = cabinet_width - 2*plinth_inset
    side_depth = cabinet_depth - 2*plinth_inset - BOARD_THICKNESS*2
    parts.append([part_no,"Plinth front",external_color,front_back_width,plinth_height,BOARD_THICKNESS,external_color,internal_color,"Edged short sides only"])
    part_no+=1
    parts.append([part_no,"Plinth back",external_color,front_back_width,plinth_height,BOARD_THICKNESS,external_color,internal_color,"Edged short sides only"])
    part_no+=1
    parts.append([part_no,"Plinth left",external_color,side_depth,plinth_height,BOARD_THICKNESS,external_color,internal_color,"Edged short sides only"])
    part_no+=1
    parts.append([part_no,"Plinth right",external_color,side_depth,plinth_height,BOARD_THICKNESS,external_color,internal_color,"Edged short sides only"])
    part_no+=1

    # Mounting strips (internal board, external edging)
    strip_width = cabinet_width - 2*BOARD_THICKNESS
    strip_height = 100
    parts.append([part_no,"Mounting strip front",internal_color,strip_width,strip_height,BOARD_THICKNESS,external_color,internal_color,"On wall, short sides edged"])
    part_no+=1
    parts.append([part_no,"Mounting strip back",internal_color,strip_width,strip_height,BOARD_THICKNESS,external_color,internal_color,"On wall, short sides edged"])
    part_no+=1

    # Countertop
    parts.append([part_no,"Countertop",external_color,cabinet_width+countertop_overhang,cabinet_depth+countertop_overhang,countertop_thickness,internal_color,internal_color,f"{countertop_type}, no edging"])
    part_no+=1

    # Preview doors/drawers
    preview_parts(parts)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    params = {
        "cabinet_width": cabinet_width,
        "cabinet_depth": cabinet_depth,
        "total_height": total_height,
        "plinth_height": plinth_height,
        "plinth_inset": plinth_inset,
        "shelves": shelves,
        "countertop_thickness": countertop_thickness,
        "countertop_overhang": countertop_overhang,
        "countertop_type": countertop_type,
        "internal_color": internal_color,
        "external_color": external_color,
        "edging_tolerance": edging_tolerance,
        "door_height_visible": door_height,
        "door_panel_height_cut": door_panel_height,
        "num_doors": num_doors
    }
    save_excel(parts, os.path.join(BASE_DIR, "vloerkas_cutting_list.xlsx"), params)
    export_step(parts, os.path.join(BASE_DIR, "panels_step"))

if __name__ == "__main__":
    vloerkas()
