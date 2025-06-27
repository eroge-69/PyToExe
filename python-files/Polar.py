import tkinter as tk
from tkinter import ttk # For themed widgets

root = tk.Tk()
root.title("Polar Visual Menu")

# --- Style ---
style = ttk.Style()
style.theme_use('clam') # Or another theme you like. Experiment!
style.configure("TLabel", font=("Helvetica", 12)) # Adjust font as needed.
style.configure("TNotebook.Tab", padding=(10, 5), font=("Helvetica", 12)) # Tab appearance


# --- Notebook (Tabs) ---
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# --- Tab Creation ---
esp_tab = ttk.Frame(notebook)
hud_tab = ttk.Frame(notebook)
player_tab = ttk.Frame(notebook)

notebook.add(esp_tab, text="ESP")
notebook.add(hud_tab, text="HUD")
notebook.add(player_tab, text="PLAYER")


# --- Placeholder Widgets (Replace with your actual content) ---

# ESP Tab
ttk.Label(esp_tab, text="ESP Settings will go here").pack(pady=20)


# HUD Tab
ttk.Label(hud_tab, text="HUD Settings will go here").pack(pady=20)


# PLAYER Tab
ttk.Label(player_tab, text="PLAYER Settings will go here").pack(pady=20)


# --- Run the GUI ---
root.mainloop()

