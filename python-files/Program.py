import tkinter as tk
from tkinter import ttk

# Conversions
SQFT_PER_SQ_METER = 10.7639
SQFT_PER_GAJ = 9.0
SQFT_PER_MARLA = 272.25  # common Punjab/Haryana marla

def validate_entry(entry):
    """Return True if entry is empty or valid positive number; highlight only invalid."""
    txt = entry.get().strip()
    if txt == "":
        entry.config(bg="white")
        return True
    try:
        v = float(txt)
        if v > 0:
            entry.config(bg="white")
            return True
        else:
            entry.config(bg="misty rose")
            return False
    except Exception:
        entry.config(bg="misty rose")
        return False

def calculate_total(*args):
    total_sqft = 0.0
    for lbl, le, be in room_rows:
        # validate but do not treat empty as error
        valid_l = validate_entry(le)
        valid_b = validate_entry(be)
        ltxt = le.get().strip()
        btxt = be.get().strip()
        if not ltxt or not btxt:
            # incomplete row -> skip area for now
            continue
        if not (valid_l and valid_b):
            # invalid numeric -> skip adding to total
            continue
        l = float(ltxt)
        b = float(btxt)
        unit = unit_var.get()
        # Interpret length & breadth input units (Feet or Meters)
        if unit == "Feet":
            area_sqft = l * b
        else:  # Meters
            area_sqft = l * b * SQFT_PER_SQ_METER
        total_sqft += area_sqft

    total_sq_m = total_sqft / SQFT_PER_SQ_METER
    total_gaj = total_sqft / SQFT_PER_GAJ
    total_marla = total_sqft / SQFT_PER_MARLA

    result_label.config(
        text=(
            f"Total Area:\n"
            f"{total_sqft:.2f} sq ft\n"
            f"{total_sq_m:.2f} sq m\n"
            f"{total_gaj:.2f} gaj\n"
            f"{total_marla:.2f} marla"
        )
    )

def add_room():
    idx = len(room_rows) + 1
    lbl = tk.Label(root, text=f"Room {idx}")
    le = tk.Entry(root, width=12)
    be = tk.Entry(root, width=12)

    row = idx + 1
    lbl.grid(row=row, column=0, padx=6, pady=4, sticky="w")
    le.grid(row=row, column=1, padx=6, pady=4)
    be.grid(row=row, column=2, padx=6, pady=4)

    # Bind validation + recalc on each change
    le_var = le
    be_var = be
    le.bind("<KeyRelease>", lambda e: (validate_entry(le_var), calculate_total()))
    be.bind("<KeyRelease>", lambda e: (validate_entry(be_var), calculate_total()))

    room_rows.append((lbl, le, be))
    calculate_total()

def remove_room():
    if not room_rows:
        return
    lbl, le, be = room_rows.pop()
    lbl.destroy()
    le.destroy()
    be.destroy()
    # renumber remaining room labels
    for i, (lbl2, _, _) in enumerate(room_rows, start=1):
        lbl2.config(text=f"Room {i}")
    calculate_total()

# --- GUI ---
root = tk.Tk()
root.title("House Area Calculator (Feet / Meters)")

# Headers
tk.Label(root, text="Room").grid(row=1, column=0, padx=6, pady=6)
tk.Label(root, text="Length").grid(row=1, column=1, padx=6, pady=6)
tk.Label(root, text="Breadth").grid(row=1, column=2, padx=6, pady=6)

# Controls
btn_frame = tk.Frame(root)
btn_frame.grid(row=0, column=0, columnspan=3, sticky="w", padx=6, pady=6)

add_btn = tk.Button(btn_frame, text="Add Room", command=add_room)
add_btn.pack(side="left", padx=(0,8))

remove_btn = tk.Button(btn_frame, text="Remove Room", command=remove_room)
remove_btn.pack(side="left", padx=(0,8))

tk.Label(btn_frame, text="Input unit:").pack(side="left")
unit_var = tk.StringVar(value="Feet")
unit_menu = ttk.Combobox(btn_frame, textvariable=unit_var, values=["Feet", "Meters"], state="readonly", width=8)
unit_menu.pack(side="left", padx=(4,8))
unit_menu.bind("<<ComboboxSelected>>", calculate_total)

# Result label
result_label = tk.Label(root, text="Total Area:\n0.00 sq ft\n0.00 sq m\n0.00 gaj\n0.00 marla", justify="left", font=("Arial", 11, "bold"))
result_label.grid(row=0, column=3, rowspan=3, padx=10, pady=6, sticky="n")

room_rows = []
# start with one row
add_room()

# Make window a bit larger and center (optional)
root.geometry("700x300")
root.mainloop()
