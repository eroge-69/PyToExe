# impact_app.py
import os
import sys
import math
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

IMG_NAME = "istockphoto-881016858-612x612.jpg"

def resource_path(filename):
    if getattr(sys, "_MEIPASS", None):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)

class ImpactApp:
    def __init__(self, root):
        self.root = root
        root.title("Impact Calculator - Aléatoire")
        self.frame_left = tk.Frame(root)
        self.frame_left.pack(side=tk.LEFT, padx=10, pady=10)
        self.frame_right = tk.Frame(root)
        self.frame_right.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        img_path = resource_path(IMG_NAME)
        if not os.path.exists(img_path):
            messagebox.showerror("Erreur", f"Image introuvable : {img_path}\nPlace '{IMG_NAME}' dans le dossier du script.")
            root.destroy()
            return

        self.pil_img = Image.open(img_path).convert("RGBA")
        self.img_w, self.img_h = self.pil_img.size
        self.photo = ImageTk.PhotoImage(self.pil_img)

        self.canvas = tk.Canvas(self.frame_left, width=self.img_w, height=self.img_h, bg='white', highlightthickness=1)
        self.canvas.pack()
        self.canvas_image_id = self.canvas.create_image(0,0, anchor="nw", image=self.photo)

        self.click_point = None
        self.impact_point = None
        self.click_marker = None
        self.impact_marker = None
        self.line_id = None

        tk.Label(self.frame_right, text="Distance impact (1 = proche, 10 = éloigné)", wraplength=220).pack(pady=(6,0))
        self.scale = tk.Scale(self.frame_right, from_=1, to=10, orient=tk.HORIZONTAL, length=220)
        self.scale.set(5)
        self.scale.pack()

        # Optionnel : bouton pour forcer recoloration aléatoire (recalculate)
        tk.Button(self.frame_right, text="Reset", command=self.reset, bg="#f700c6", fg="white").pack(pady=8, fill=tk.X)

        self.info_label = tk.Label(self.frame_right, text="Clique sur la silhouette (face ou dos). L'impact final est légèrement aléatoire.", wraplength=220, justify=tk.LEFT)
        self.info_label.pack(pady=(8,0))

        self.coord_label = tk.Label(self.frame_right, text="")
        self.coord_label.pack(pady=(6,0))

        self.canvas.bind("<Button-1>", self.on_click)
        self.scale.bind("<ButtonRelease-1>", lambda e: self.recompute_if_needed())

    def is_pixel_on_body(self, x, y):
        ix = int(round(x))
        iy = int(round(y))
        if ix < 0 or iy < 0 or ix >= self.img_w or iy >= self.img_h:
            return False
        r, g, b, a = self.pil_img.getpixel((ix, iy))
        brightness = (r + g + b) / 3
        return (a > 20) and (brightness < 250)

    def reset(self):
        self.click_point = None
        self.impact_point = None
        for item in (self.click_marker, self.impact_marker, self.line_id):
            if item:
                try:
                    self.canvas.delete(item)
                except:
                    pass
        self.click_marker = None
        self.impact_marker = None
        self.line_id = None
        self.coord_label.config(text="")

    def on_click(self, event):
        x = event.x
        y = event.y
        if not self.is_pixel_on_body(x, y):
            messagebox.showinfo("Hors silhouette", "Clique en dehors du corps — clique sur la silhouette (partie face ou dos).")
            return
        self.click_point = (x, y)
        self.impact_point = self.compute_impact_random(x, y, self.scale.get())
        self.draw_markers()
        self.coord_label.config(text=f"Clic: ({int(x)},{int(y)})  — Impact: ({int(self.impact_point[0])},{int(self.impact_point[1])})")

    def recompute_if_needed(self):
        if not self.click_point:
            return
        x,y = self.click_point
        self.impact_point = self.compute_impact_random(x, y, self.scale.get())
        self.draw_markers()
        self.coord_label.config(text=f"Clic: ({int(x)},{int(y)})  — Impact: ({int(self.impact_point[0])},{int(self.impact_point[1])})")

    def draw_markers(self):
        if self.click_marker:
            self.canvas.delete(self.click_marker)
        if self.impact_marker:
            self.canvas.delete(self.impact_marker)
        if self.line_id:
            self.canvas.delete(self.line_id)

        x1, y1 = self.click_point
        x2, y2 = self.impact_point
        self.line_id = self.canvas.create_line(x1, y1, x2, y2, fill="lime", width=3)
        r = 6
        self.click_marker = self.canvas.create_oval(x1-r, y1-r, x1+r, y1+r, fill="red", outline="white", width=2)
        self.impact_marker = self.canvas.create_oval(x2-r, y2-r, x2+r, y2+r, fill="green", outline="white", width=2)

    def compute_impact_random(self, clickX, clickY, sliderValue):
        """
        Version aléatoire :
        - mélange les angles à chaque appel
        - ajoute un jitter sur la distance (±20%)
        - tente d'abord la distance souhaitée, puis la réduit progressivement
        """
        minDist = 6
        maxDist = min(self.img_w, self.img_h) * 0.33
        desiredDist_base = minDist + (sliderValue - 1) * (maxDist - minDist) / 9.0

        angleSteps = 72   # plus de precision angulaire
        distSteps = 40

        # préparer une liste d'angles et la mélanger pour l'aléa
        angles = [(i / angleSteps) * math.tau for i in range(angleSteps)]
        random.shuffle(angles)

        for ds in range(distSteps + 1):
            factor = 1.0 - (ds / distSteps)
            # ajouter un petit jitter multiplicatif à la distance (0.8 -> 1.2)
            jitter = random.uniform(0.8, 1.2)
            dist = desiredDist_base * factor * jitter

            # pour chaque angle (dans un ordre aléatoire), tester si point sur silhouette
            for theta in angles:
                # ajouter un petit jitter angulaire afin que deux appels successifs puissent différer légèrement
                theta_jitter = theta + random.uniform(-0.07, 0.07)  # ~ ±4°
                cx = clickX + math.cos(theta_jitter) * dist
                cy = clickY + math.sin(theta_jitter) * dist
                if 0 <= cx < self.img_w and 0 <= cy < self.img_h and self.is_pixel_on_body(cx, cy):
                    return (cx, cy)

        # fallback : retourner le point de clic si aucun point valide
        return (clickX, clickY)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImpactApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
