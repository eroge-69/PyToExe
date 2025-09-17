#!/usr/bin/env python3
"""
roulette.py

Ruleta de 30 casillas (colores automáticos alternados) con panel de configuración.
Guarda/lee la configuración desde config.json.

Cómo usar:
    python roulette.py

Requisitos:
    - Python 3.8+
    - Tkinter (suele venir con Python en Windows/Mac/Linux)

Para convertir en .exe:
    pip install pyinstaller
    pyinstaller --onefile --windowed roulette.py
    (el EXE quedará en dist/roulette.exe)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, math, random, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(HERE, "config.json")
NUM_SLICES = 30

# Default labels
DEFAULT_LABELS = [f"Casilla {i+1}" for i in range(NUM_SLICES)]

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            labels = data.get("labels", DEFAULT_LABELS)
            if len(labels) != NUM_SLICES:
                labels = DEFAULT_LABELS
            return labels
        except Exception:
            return DEFAULT_LABELS
    else:
        return DEFAULT_LABELS

def save_config(labels):
    data = {"labels": labels}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hsv_to_rgb(h, s, v):
    # h in [0,1], s in [0,1], v in [0,1] -> returns hex color
    i = int(h*6)
    f = (h*6) - i
    p = v * (1 - s)
    q = v * (1 - f*s)
    t = v * (1 - (1-f)*s)
    i = i % 6
    if i == 0: r,g,b = v,t,p
    if i == 1: r,g,b = q,v,p
    if i == 2: r,g,b = p,v,t
    if i == 3: r,g,b = p,q,v
    if i == 4: r,g,b = t,p,v
    if i == 5: r,g,b = v,p,q
    return '#{0:02x}{1:02x}{2:02x}'.format(int(r*255), int(g*255), int(b*255))

class WheelApp:
    def __init__(self, master):
        self.master = master
        master.title("Ruleta - 30 casillas")
        master.resizable(False, False)

        # Load labels
        self.labels = load_config()

        # Canvas for wheel
        self.canvas_size = 700
        self.canvas = tk.Canvas(master, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Control frame
        ctrl = ttk.Frame(master)
        ctrl.grid(row=1, column=0, sticky="w", padx=10, pady=(0,10))

        self.spin_button = ttk.Button(ctrl, text="Girar", command=self.start_spin)
        self.spin_button.pack(side="left", padx=(0,8))

        self.config_button = ttk.Button(ctrl, text="Configurar etiquetas", command=self.open_config)
        self.config_button.pack(side="left", padx=(0,8))

        self.reset_button = ttk.Button(ctrl, text="Reset etiquetas por defecto", command=self.reset_defaults)
        self.reset_button.pack(side="left")

        # Info label
        self.info_var = tk.StringVar(value="")
        self.info_label = ttk.Label(master, textvariable=self.info_var)
        self.info_label.grid(row=1, column=1, sticky="e", padx=10)

        # Wheel state
        self.center = self.canvas_size // 2
        self.radius = int(self.canvas_size * 0.42)
        self.angle = 0.0  # current rotation angle in degrees
        self.angular_velocity = 0.0
        self.is_spinning = False

        # Precompute slice colors (alternating hues)
        self.slice_colors = self.compute_colors()

        # Draw initial wheel
        self.redraw_wheel()

    def compute_colors(self):
        colors = []
        # use hues around the circle; alternate saturations/values for contrast
        for i in range(NUM_SLICES):
            h = i / NUM_SLICES
            s = 0.75 if (i % 2 == 0) else 0.55
            v = 0.95
            colors.append(hsv_to_rgb(h, s, v))
        return colors

    def redraw_wheel(self):
        self.canvas.delete("all")
        cx, cy = self.center, self.center
        start_angle = self.angle
        wedge = 360.0 / NUM_SLICES
        for i in range(NUM_SLICES):
            a0 = start_angle + i * wedge
            a1 = a0 + wedge
            # Create arc polygon for smoother text placement
            x0 = cx + self.radius * math.cos(math.radians(a0))
            y0 = cy + self.radius * math.sin(math.radians(a0))
            x1 = cx + self.radius * math.cos(math.radians(a1))
            y1 = cy + self.radius * math.sin(math.radians(a1))
            # Draw slice
            self.canvas.create_arc(cx-self.radius, cy-self.radius, cx+self.radius, cy+self.radius,
                                   start=-a0, extent=-wedge, fill=self.slice_colors[i], outline="black")
            # Text position (mid-angle)
            mid = a0 + wedge/2
            tx = cx + (self.radius*0.62) * math.cos(math.radians(mid))
            ty = cy + (self.radius*0.62) * math.sin(math.radians(mid))
            label = self.labels[i] if i < len(self.labels) else f"#{i+1}"
            # rotate text by computing angle relative to horizontal
            angle_text = mid
            # Transform for readability: keep text upright
            if angle_text > 90 and angle_text < 270:
                angle_text += 180
            # Create text (tkinter doesn't support rotated text natively; so we draw without rotation)
            self.canvas.create_text(tx, ty, text=label, font=("Arial", 10, "bold"), width=120)
        # Draw center circle
        self.canvas.create_oval(cx-40, cy-40, cx+40, cy+40, fill="white", outline="black")
        self.canvas.create_text(cx, cy, text="GIRAR", font=("Arial", 12, "bold"))
        # Draw fixed pointer at top
        pointer_height = 20
        self.canvas.create_polygon(cx, cy - self.radius - pointer_height,
                                   cx-12, cy - self.radius + 6,
                                   cx+12, cy - self.radius + 6, fill="red")

    def start_spin(self):
        if self.is_spinning:
            return
        self.is_spinning = True
        # Randomize initial angular velocity (degrees per update)
        self.angular_velocity = random.uniform(15, 40)
        # Random direction
        if random.choice([True, False]):
            self.angular_velocity *= -1
        self.spin_button.config(state="disabled")
        self.info_var.set("")
        self.after_spin()

    def after_spin(self):
        # Simple physics: apply friction until slow, animate
        if not self.is_spinning:
            return
        # update angle
        self.angle = (self.angle + self.angular_velocity) % 360
        # friction (damp)
        self.angular_velocity *= 0.985
        # if angular velocity small, decelerate faster
        if abs(self.angular_velocity) < 0.5:
            self.angular_velocity *= 0.92
        self.redraw_wheel()
        # stop condition
        if abs(self.angular_velocity) < 0.05:
            self.is_spinning = False
            self.spin_button.config(state="normal")
            winner = self.compute_winner()
            self.info_var.set(f"Resultado: {winner}")
            messagebox.showinfo("Resultado", f"Ha salido: {winner}")
            return
        # schedule next frame (approx 30-60 FPS)
        self.master.after(16, self.after_spin)

    def compute_winner(self):
        # The pointer is at angle 90 deg (top), convert wheel angle to slice index
        # Each slice covers wedge degrees starting from angle self.angle
        # We compute which slice crosses the top (angle = 90)
        top_angle = 90
        # Angle on wheel corresponding to top in wheel coordinates:
        relative = (top_angle - self.angle) % 360
        wedge = 360.0 / NUM_SLICES
        idx = int(relative // wedge) % NUM_SLICES
        return self.labels[idx]

    def open_config(self):
        ConfigWindow(self)

    def reset_defaults(self):
        if messagebox.askyesno("Reset", "¿Restablecer etiquetas a valores por defecto?"):
            self.labels = DEFAULT_LABELS.copy()
            save_config(self.labels)
            self.redraw_wheel()
            messagebox.showinfo("Reset", "Etiquetas restablecidas y guardadas.")

class ConfigWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.master)
        self.app = app
        self.title("Configurar etiquetas")
        self.geometry("560x520")
        self.resizable(False, False)

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollable canvas for many entries
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.inner = ttk.Frame(canvas)

        self.inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0,0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Entries for each label
        self.entries = []
        for i in range(NUM_SLICES):
            row = ttk.Frame(self.inner)
            row.pack(fill="x", pady=2)
            lbl = ttk.Label(row, text=f"{i+1:02d}", width=4)
            lbl.pack(side="left")
            var = tk.StringVar(value=self.app.labels[i] if i < len(self.app.labels) else "")
            ent = ttk.Entry(row, textvariable=var, width=56)
            ent.pack(side="left", padx=(4,8))
            self.entries.append(var)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=8)
        save_btn = ttk.Button(btn_frame, text="Guardar", command=self.on_save)
        save_btn.pack(side="right", padx=6)
        cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=self.destroy)
        cancel_btn.pack(side="right")

    def on_save(self):
        labels = [v.get().strip() or f"Casilla {i+1}" for i,v in enumerate(self.entries)]
        self.app.labels = labels
        save_config(labels)
        self.app.redraw_wheel()
        messagebox.showinfo("Guardado", "Etiquetas guardadas en config.json")
        self.destroy()

def main():
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    app = WheelApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
