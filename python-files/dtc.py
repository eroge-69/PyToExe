# AutotechTuning – Denso DTC Eliminator
# © 2025 AutotechTuning. All rights reserved.

from tkinter import *
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import csv

# Core known DTC system filters
EGR_CODES = {"P0400", "P0401", "P0402", "P0403", "P0404", "P0405", "P0406"}
DPF_CODES = {"P2002", "P242F", "P244A", "P2463", "P2459", "P2458"}
NOX_CODES = {"P2200", "P2201", "P2202", "P2203", "P229F", "P229E"}
SCR_CODES = {"P20EE", "P204F", "P2084", "P207F", "P20BD"}

# Sample DTC descriptions (partial, will expand with full DB)
DTC_DESCRIPTIONS = {
    "P2463": "DPF soot accumulation too high",
    "P2002": "DPF efficiency below threshold",
    "P0401": "EGR insufficient flow",
    "P2201": "NOx sensor circuit range/performance",
    "P20EE": "SCR NOx catalyst efficiency below threshold",
    "P204F": "Reductant system performance",
    "P0101": "MAF circuit range/performance",
    "P0420": "Catalyst system efficiency below threshold (Bank 1)",
    "P0299": "Turbocharger underboost",
}

def decode_dtc(code):
    if code >= 0xC000: return f'U{code & 0x3FFF:04d}'
    if code >= 0x8000: return f'B{code & 0x3FFF:04d}'
    if code >= 0x4000: return f'C{code & 0x3FFF:04d}'
    return f'P{code:04d}'

def get_description(dtc):
    return DTC_DESCRIPTIONS.get(dtc, "Unknown")

def is_valid_dtc_block(data, offset):
    try:
        block = data[offset:offset+12]
        if len(block) < 12: return False
        dtc = int.from_bytes(block[0:2], 'little')
        dup = int.from_bytes(block[2:4], 'little')
        if dtc != dup: return False
        if not (0x0001 < dtc < 0xFFFF): return False
        if block[4] == 0x00: return False
        if block[5] not in range(0x10, 0xF0): return False
        if block[10] not in [0x00, 0x01]: return False
        if block[11] not in [0x00, 0x01]: return False
        return True
    except:
        return False

def find_dtc_blocks(data):
    dtcs = []
    for i in range(0, len(data) - 16, 2):
        if is_valid_dtc_block(data, i):
            code = int.from_bytes(data[i:i+2], 'little')
            dtc = decode_dtc(code)
            dtcs.append({
                "offset": i,
                "code": code,
                "dtc": dtc,
                "desc": get_description(dtc),
                "enabled": IntVar(value=0)
            })
    return dtcs

def patch_dtc_blocks(data, entries):
    patched = bytearray(data)
    for entry in entries:
        if entry["enabled"].get() == 0:  # OFF = disable
            for i in range(12):
                patched[entry["offset"] + i] = 0x00
    return patched

def write_log_and_csv(base, entries):
    log_path = f"{base}_patched_log.txt"
    csv_path = f"{base}_dtc_map.csv"
    with open(log_path, "w") as log_file:
        for e in entries:
            if e["enabled"].get() == 0:
                log_file.write(f"Disabled {e['dtc']} at 0x{e['offset']:06X} - {e['desc']}\n")
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["Map Name", "Start Offset", "Size", "Description", "Group"])
        for e in entries:
            if e["enabled"].get() == 0:
                writer.writerow([
                    f"DTC_{e['dtc']}",
                    f"{e['offset']}",
                    "12",
                    f"{e['dtc']} - {e['desc']}",
                    "DTC_Block"
                ])
    return log_path, csv_path

def create_gui():
    root = TkinterDnD.Tk()
    root.title("AutotechTuning – Denso DTC Eliminator (Emissions Filter Enabled)")

    # Emissions Filter Toggles
    filter_frame = Frame(root)
    filter_frame.pack(pady=5)

    show_egr = IntVar(value=1)
    show_dpf = IntVar(value=1)
    show_nox = IntVar(value=1)
    show_scr = IntVar(value=1)

    Checkbutton(filter_frame, text="EGR", variable=show_egr).pack(side="left")
    Checkbutton(filter_frame, text="DPF", variable=show_dpf).pack(side="left")
    Checkbutton(filter_frame, text="NOx", variable=show_nox).pack(side="left")
    Checkbutton(filter_frame, text="SCR", variable=show_scr).pack(side="left")

    Label(root, text="➡️ Drag and drop your .bin file below").pack(pady=5)

    canvas = Canvas(root, borderwidth=0, width=700, height=400)
    frame = Frame(canvas)
    vsb = Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((4, 4), window=frame, anchor="nw")
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    all_dtc_entries = []
    binary_data = None
    file_path = ""

    def passes_emissions_filter(code):
        return (
            (show_egr.get() and code in EGR_CODES) or
            (show_dpf.get() and code in DPF_CODES) or
            (show_nox.get() and code in NOX_CODES) or
            (show_scr.get() and code in SCR_CODES)
        )

    def refresh_gui():
        for widget in frame.winfo_children():
            widget.destroy()
        for entry in all_dtc_entries:
            if passes_emissions_filter(entry["dtc"]):
                cb = Checkbutton(frame,
                    text=f"{entry['dtc']} – {entry['desc']} @ 0x{entry['offset']:06X}",
                    variable=entry["enabled"])
                cb.pack(anchor="w")

    def process_file(event):
        nonlocal all_dtc_entries, binary_data, file_path
        path = event.data.strip('{}')
        if not path.lower().endswith(".bin"):
            messagebox.showerror("Invalid file", "Please drop a .bin file")
            return
        with open(path, "rb") as f:
            binary_data = f.read()
        file_path = path
        all_dtc_entries = find_dtc_blocks(binary_data)
        refresh_gui()
        messagebox.showinfo("Scan complete", f"Found {len(all_dtc_entries)} DTCs")

    def patch_selected():
        if not all_dtc_entries or not binary_data:
            messagebox.showerror("Error", "No binary or DTCs loaded.")
            return
        patched = patch_dtc_blocks(binary_data, all_dtc_entries)
        base = os.path.splitext(file_path)[0] + "_patched"
        with open(base + ".bin", "wb") as f:
            f.write(patched)
        log, csv = write_log_and_csv(base, all_dtc_entries)
        messagebox.showinfo("Done", f"Saved:\n{base}.bin\n{log}\n{csv}")

    def enable_all():
        for e in all_dtc_entries:
            if passes_emissions_filter(e["dtc"]):
                e["enabled"].set(1)

    def disable_all():
        for e in all_dtc_entries:
            if passes_emissions_filter(e["dtc"]):
                e["enabled"].set(0)

    Button(root, text="✅ Patch Selected DTCs", command=patch_selected).pack(pady=5)
    Button(root, text="🔄 Enable All Visible", command=enable_all).pack(pady=2)
    Button(root, text="❌ Disable All Visible", command=disable_all).pack(pady=2)

    canvas.drop_target_register(DND_FILES)
    canvas.dnd_bind("<<Drop>>", process_file)

    # Auto-refresh on filter toggle
    Checkbutton(filter_frame, text="Refresh View", command=refresh_gui).pack(side="left", padx=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()