
import tkinter as tk
from tkinter import messagebox
import math

# Konstantne dimenzije cisterne
RADIUS = 0.5  # metara
LENGTH = 1.146  # metara
TOTAL_VOLUME_L = 1800  # litara

class CisternaApp:
    def __init__(self, root):
        self.root = root
        root.title("Cisterna")

        tk.Label(root, text="Unesi visinu tečnosti (u cm):").pack(pady=10)
        self.entry = tk.Entry(root)
        self.entry.pack()

        tk.Button(root, text="Izračunaj", command=self.calculate_fill).pack(pady=10)

        self.result_label = tk.Label(root, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)

        self.canvas = tk.Canvas(root, width=200, height=200, bg="white")
        self.canvas.pack(pady=10)
        self.draw_cisterna(0)

    def draw_cisterna(self, fill_ratio):
        self.canvas.delete("all")
        self.canvas.create_oval(20, 20, 180, 180, outline="black", width=2)
        if fill_ratio > 0:
            h = 160 * fill_ratio
            y0 = 180 - h
            self.canvas.create_rectangle(20, y0, 180, 180, fill="lightblue", outline="")

    def calculate_fill(self):
        try:
            h_cm = float(self.entry.get())
            h = h_cm / 100
            if h < 0 or h > 2 * RADIUS:
                messagebox.showerror("Greška", "Unesite visinu između 0 i 100 cm.")
                self.draw_cisterna(0)
                return

            theta = 2 * math.acos((RADIUS - h) / RADIUS)
            segment_area = (RADIUS**2 / 2) * (theta - math.sin(theta))
            volume_m3 = segment_area * LENGTH
            volume_liters = volume_m3 * 1000
            percent_full = volume_liters / TOTAL_VOLUME_L

            self.result_label.config(
                text=f"Zapremina: {volume_liters:.1f} L\nPopunjenost: {percent_full * 100:.1f}%"
            )
            self.draw_cisterna(percent_full)
        except:
            messagebox.showerror("Greška", "Unesite broj.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CisternaApp(root)
    root.mainloop()
