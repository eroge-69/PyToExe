import tkinter as tk
import subprocess
import sys

# Function to run DisplaySwitch.exe with arguments
def switch_display(mode):
    try:
        subprocess.run(["DisplaySwitch.exe", mode], check=True)
        sys.exit(0)  # Close after switching
    except Exception as e:
        print(f"Error: {e}")

# App window
app = tk.Tk()
app.title("Screen Manager")
app.geometry("400x250")
app.configure(bg="#1e1e1e")   # dark background
app.resizable(False, False)

# Title
label = tk.Label(app, text="Projection Options", font=("Segoe UI", 14, "bold"),
                 fg="white", bg="#1e1e1e")
label.pack(pady=15)

# Grid container
frame = tk.Frame(app, bg="#1e1e1e")
frame.pack(expand=True)

btn_style = {
    "font": ("Segoe UI", 11, "bold"),
    "fg": "white",
    "bg": "#2d2d2d",
    "activebackground": "#3d3d3d",
    "activeforeground": "white",
    "width": 18,
    "height": 3,
    "relief": "flat",
    "bd": 0
}

# Buttons in 2×2 grid
btn1 = tk.Button(frame, text="PC Screen Only",
                 command=lambda: switch_display("/internal"), **btn_style)
btn2 = tk.Button(frame, text="Duplicate",
                 command=lambda: switch_display("/clone"), **btn_style)
btn3 = tk.Button(frame, text="Extend",
                 command=lambda: switch_display("/extend"), **btn_style)
btn4 = tk.Button(frame, text="Second Screen Only",
                 command=lambda: switch_display("/external"), **btn_style)

btn1.grid(row=0, column=0, padx=10, pady=10)
btn2.grid(row=0, column=1, padx=10, pady=10)
btn3.grid(row=1, column=0, padx=10, pady=10)
btn4.grid(row=1, column=1, padx=10, pady=10)

app.mainloop()
