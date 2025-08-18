import tkinter as tk
from tkinter import ttk

# --- Fenêtre principale ---
root = tk.Tk()
root.title("Vape Demo - Fake UI")
root.geometry("800x500")
root.configure(bg="#1e1e1e")

# --- Style sombre ---
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 11))
style.configure("TButton", background="#2d2d2d", foreground="white", font=("Segoe UI", 10), padding=6)
style.map("TButton", background=[("active", "#3c3c3c")])

# --- Colonnes ---
frame_left = tk.Frame(root, bg="#252526", width=200, height=500)
frame_left.pack(side="left", fill="y")

frame_right = tk.Frame(root, bg="#1e1e1e")
frame_right.pack(side="right", fill="both", expand=True)

# --- Modules fake ---
modules = ["Reach", "Velocity", "Aim Assist", "Scaffold", "ESP", "AutoClicker"]

tk.Label(frame_left, text="Modules", bg="#252526", fg="white", font=("Segoe UI", 12, "bold")).pack(pady=10)

for mod in modules:
    ttk.Button(frame_left, text=mod).pack(pady=5, fill="x", padx=10)

# --- Partie droite ---
title = tk.Label(frame_right, text="Fake Vape Config", font=("Segoe UI", 14, "bold"))
title.pack(pady=20)

desc = tk.Label(frame_right, text="Ceci est une démo de design inspiré de Vape.\nIl n'y a AUCUN cheat actif.", font=("Segoe UI", 11))
desc.pack(pady=10)

btn_demo = ttk.Button(frame_right, text="Inject (Fake)", command=lambda: print("Injection fictive..."))
btn_demo.pack(pady=20)

root.mainloop()
