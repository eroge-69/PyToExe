import tkinter as tk
from tkinter import filedialog, messagebox

def generate_gcode():
    try:
        # Panel dimensions
        panel_width = float(entry_panel_width.get())
        panel_height = float(entry_panel_height.get())

        # Square dimensions
        square_width = float(entry_square_width.get())
        square_height = float(entry_square_height.get())

        # Panel count
        num_cols = int(entry_cols.get())
        num_rows = int(entry_rows.get())

        # Spacing
        gap_x = float(entry_gapx.get())
        gap_y = float(entry_gapy.get())

        # Z movements
        plunge = float(entry_plunge.get())
        lift = float(entry_lift.get())

        # Feedrate
        feedrate = int(entry_feedrate.get())

        # Servo angles
        servo_y = int(entry_servo_y.get())
        servo_x = int(entry_servo_x.get())

        # Machine limits
        max_x = float(entry_maxx.get())
        max_y = float(entry_maxy.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values.")
        return

    gcode = []
    gcode.append("G21 ; Set units to mm")
    gcode.append("G90 ; Absolute positioning")
    gcode.append("G92 X0 Y0 Z0 ; Set current position as zero")

    panel_count = 0

    for row in range(num_rows):
        for col in range(num_cols):
            start_x = col * (panel_width + gap_x)
            start_y = row * (panel_height + gap_y)

            if start_x + panel_width > max_x or start_y + panel_height > max_y:
                messagebox.showwarning(
                    "Warning", 
                    f"Panel R{row+1}C{col+1} exceeds limits and may not fit!"
                )

            panel_count += 1
            gcode.append(f"\n; --- Panel R{row+1}C{col+1} (# {panel_count}) at X{start_x} Y{start_y} ---")

            # Servo for vertical cuts (Y direction)
            gcode.append("M400")
            gcode.append(f"M280 P0 S{servo_y} ; Servo for Y cuts")
            gcode.append("G4 P500 ; wait for servo")
            gcode.append("M400")
            
            x = start_x
            while x <= start_x + panel_width - square_width:
                gcode.append(f"G0 Z{lift} F{feedrate}")
                gcode.append("M400")
                gcode.append(f"G0 X{x:.2f} Y{start_y:.2f} F{feedrate}")
                gcode.append("M400")
                gcode.append(f"G1 Z{plunge} F{feedrate}")
                gcode.append("M400")
                gcode.append(f"G1 Y{start_y+panel_height:.2f} F{feedrate}")
                gcode.append("M400")
                gcode.append(f"G0 Z{lift} F{feedrate}")
                gcode.append("M400")
                x += square_width

            # Servo for horizontal cuts (X direction)
            gcode.append("M400")
            gcode.append(f"M280 P0 S{servo_x} ; Servo for X cuts")
            gcode.append("G4 P500 ; wait for servo")
            gcode.append("M400")
            
            y = start_y
            while y <= start_y + panel_height - square_height:
                gcode.append(f"G0 Z{lift} F{feedrate}")
                gcode.append("M400")
                gcode.append(f"G0 X{start_x:.2f} Y{y:.2f} F{feedrate}")
                gcode.append("M400")
                gcode.append(f"G1 Z{plunge} F{feedrate}")
                gcode.append("M400")
                gcode.append(f"G1 X{start_x+panel_width:.2f} F{feedrate}")
                gcode.append("M400")
                gcode.append(f"G0 Z{lift} F{feedrate}")
                gcode.append("M400")
                y += square_height

    gcode.append("\n; --- Return to home ---")
    gcode.append(f"G0 Z{lift} F{feedrate}")
    gcode.append("M400")
    gcode.append("G0 X0 Y0 F1800")
    gcode.append("M400")

    # Save file
    filepath = filedialog.asksaveasfilename(defaultextension=".gcode",
                                            filetypes=[("G-code files", "*.gcode")])
    if filepath:
        with open(filepath, "w") as f:
            f.write("\n".join(gcode))
        messagebox.showinfo("Success", f"G-code saved to {filepath}")

# GUI setup
root = tk.Tk()
root.title("Panel Grid G-code Generator")
root.geometry("450x560")
root.configure(bg="#f4f4f4")

frame = tk.Frame(root, bg="#f4f4f4")
frame.pack(pady=10)

fields = [
    ("Panel Width (mm)", "panel_width"),
    ("Panel Height (mm)", "panel_height"),
    ("Square Width (mm)", "square_width"),
    ("Square Height (mm)", "square_height"),
    ("Number of Columns", "cols"),
    ("Number of Rows", "rows"),
    ("Gap X (mm)", "gapx"),
    ("Gap Y (mm)", "gapy"),
    ("Plunge Depth (Z down)", "plunge"),
    ("Lift Height (Z up)", "lift"),
    ("Feedrate (F)", "feedrate"),
    ("Servo Angle Y cuts", "servo_y"),
    ("Servo Angle X cuts", "servo_x"),
    ("Max X (mm)", "maxx"),
    ("Max Y (mm)", "maxy"),
]

entries = {}
for i, (label, var) in enumerate(fields):
    tk.Label(frame, text=label, anchor="w", bg="#f4f4f4", font=("Arial", 10, "bold")).grid(row=i, column=0, padx=10, pady=5, sticky="w")
    e = tk.Entry(frame, width=15, font=("Arial", 10))
    e.grid(row=i, column=1, padx=10, pady=5)
    entries[var] = e

entry_panel_width = entries["panel_width"]
entry_panel_height = entries["panel_height"]
entry_square_width = entries["square_width"]
entry_square_height = entries["square_height"]
entry_cols = entries["cols"]
entry_rows = entries["rows"]
entry_gapx = entries["gapx"]
entry_gapy = entries["gapy"]
entry_plunge = entries["plunge"]
entry_lift = entries["lift"]
entry_feedrate = entries["feedrate"]
entry_servo_y = entries["servo_y"]
entry_servo_x = entries["servo_x"]
entry_maxx = entries["maxx"]
entry_maxy = entries["maxy"]

tk.Button(root, text="Generate G-code", command=generate_gcode,
          bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
          padx=20, pady=10).pack(pady=15)

root.mainloop()
