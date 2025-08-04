# occult_calculator_part1.py

import tkinter as tk
from tkinter import ttk
from fractions import Fraction
import math
import random
import statistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Initialize main window
root = tk.Tk()
root.title("Occult Calculator - Tabbed GUI")
root.geometry("900x700")

# Create tabbed notebook interface
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Define individual tab frames
tab_advanced = ttk.Frame(notebook)
tab_angles = ttk.Frame(notebook)
tab_math = ttk.Frame(notebook)

notebook.add(tab_advanced, text="Advanced Functions")
notebook.add(tab_angles, text="Angles (Degrees)")
notebook.add(tab_math, text="Math & Fractions")

# Create shared Matplotlib canvas
fig, ax = plt.subplots(figsize=(6, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill='x', pady=10)

# Shared UI builder
def setup_tab(tab, label_text):
    frame = ttk.Frame(tab)
    frame.pack(pady=10)
    ttk.Label(frame, text=label_text).grid(row=0, column=0, padx=5, sticky="w")
    combo = ttk.Combobox(frame, width=40)
    combo.grid(row=0, column=1, padx=5)
    input_entry = tk.Entry(tab, width=60)
    input_entry.pack(pady=5)
    output_var = tk.StringVar()
    ttk.Label(tab, textvariable=output_var, font=("Consolas", 12), foreground="blue").pack()
    return combo, input_entry, output_var

# Setup all tab components
adv_combo, adv_input, adv_output = setup_tab(tab_advanced, "Select Function:")
angle_combo, angle_input, angle_output = setup_tab(tab_angles, "Select Trig Function:")
math_combo, math_input, math_output = setup_tab(tab_math, "Select Math/Fraction Function:")
# occult_calculator_part2.py

# --- Advanced Math + Utility Functions ---
def approach(cur, target, delta): return target if abs(target - cur) <= delta else cur + delta * ((target - cur) > 0) - ((target - cur) < 0)
def approachAngle(cur, target, delta): return cur + clamp(normalizeAngle(target - cur), -delta, delta)
def clamp(x, a, b): return max(a, min(x, b))
def normalizeAngle(angle): return (angle + 180) % 360 - 180
def angleDifference(a, b): return normalizeAngle(b - a)
def remap(val, in_min, in_max, out_min, out_max): return out_min + (val - in_min) * (out_max - out_min) / (in_max - in_min)
def timeFraction(start, end, now): return clamp((now - start) / (end - start), 0, 1)
def lerp(a, b, t): return a + (b - a) * t
def lerpAngle(a, b, t): return a + normalizeAngle(b - a) * t
def sharedRandom(seed, a, b): return random.Random(seed).uniform(a, b)
def intToBin(n): return bin(int(n))[2:]
def binToInt(b): return int(str(b), 2)

# --- Angle-Based Functions (in degrees) ---
angle_functions = {
    "sin (deg)": lambda x: math.sin(math.radians(x)),
    "cos (deg)": lambda x: math.cos(math.radians(x)),
    "tan (deg)": lambda x: math.tan(math.radians(x)),
    "asin (deg)": lambda x: math.degrees(math.asin(x)),
    "acos (deg)": lambda x: math.degrees(math.acos(x)),
    "atan (deg)": lambda x: math.degrees(math.atan(x)),
    "atan2 (deg)": lambda y, x: math.degrees(math.atan2(y, x)),
}

# --- Basic Math + Fractions ---
math_frac_functions = {
    "Add": lambda x, y: x + y,
    "Subtract": lambda x, y: x - y,
    "Multiply": lambda x, y: x * y,
    "Divide": lambda x, y: x / y,
    "Median": lambda *args: statistics.median(args),
    "Mode": lambda *args: statistics.mode(args),
    "Fraction Add": lambda x, y: Fraction(x) + Fraction(y),
    "Fraction Subtract": lambda x, y: Fraction(x) - Fraction(y),
    "Fraction Multiply": lambda x, y: Fraction(x) * Fraction(y),
    "Fraction Divide": lambda x, y: Fraction(x) / Fraction(y),
}

# --- All Advanced Functions Mapped ---
advanced_functions = {
    "ceil": math.ceil, "floor": math.floor, "round": round, "trunc": math.trunc,
    "abs": abs, "exp": math.exp, "log": math.log, "log10": math.log10,
    "sqrt": math.sqrt, "factorial": math.factorial, "frexp": math.frexp,
    "ldexp": math.ldexp, "modf": math.modf, "fmod": math.fmod,
    "min": min, "max": max, "pow": math.pow,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan, "atan2": math.atan2,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "pi": lambda: math.pi, "huge": lambda: float('inf'),
    "rand": lambda: random.random(), "random": lambda: random.random(),
    "sign": lambda x: (x > 0) - (x < 0),
    "intToBin": intToBin, "binToInt": binToInt,
    "lerp": lerp, "lerpAngle": lerpAngle,
    "approach": approach, "approachAngle": approachAngle,
    "clamp": clamp, "normalizeAngle": normalizeAngle,
    "angleDifference": angleDifference,
    "remap": remap, "timeFraction": timeFraction,
    "sharedRandom": sharedRandom
}
# occult_calculator_part3.py

# --- Populate function dropdowns ---
adv_combo['values'] = sorted(advanced_functions.keys())
adv_combo.set("lerp")

angle_combo['values'] = sorted(angle_functions.keys())
angle_combo.set("sin (deg)")

math_combo['values'] = sorted(math_frac_functions.keys())
math_combo.set("Add")

# --- Matplotlib Visualizer for angles and values ---
def draw_result(value, title="Output", angle_args=None):
    ax.clear()
    if title in ("normalizeAngle", "angleDifference", "lerpAngle", "approachAngle") and angle_args:
        angle1 = math.radians(angle_args[0])
        angle2 = math.radians(angle_args[1])
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')
        circle = plt.Circle((0, 0), 1, color='lightgray', fill=False)
        ax.add_patch(circle)
        ax.arrow(0, 0, math.cos(angle1), math.sin(angle1), head_width=0.05, fc='blue', ec='blue')
        ax.arrow(0, 0, math.cos(angle2), math.sin(angle2), head_width=0.05, fc='red', ec='red')
        if isinstance(value, (int, float)):
            result_angle = math.radians(value)
            ax.arrow(0, 0, math.cos(result_angle), math.sin(result_angle), head_width=0.05, fc='green', ec='green')
            ax.set_title(f"{title}: {value:.2f}°")
    elif isinstance(value, (int, float)):
        ax.plot([0, 1], [0, value], marker='o')
        ax.set_title(f"{title}: {value}")
        ax.grid(True)
    else:
        ax.set_title("No visual")
    canvas.draw()
# occult_calculator_part4.py

# --- Unified calculate logic ---
def calculate(tab):
    try:
        if tab == "advanced":
            func = advanced_functions[adv_combo.get()]
            args = [float(Fraction(x.strip())) for x in adv_input.get().split(',') if x.strip()]
            result = func(*args)
            adv_output.set(f"Result: {result}")
            draw_result(result, adv_combo.get(), angle_args=args if adv_combo.get() in ("normalizeAngle", "angleDifference", "lerpAngle", "approachAngle") else None)
        elif tab == "angles":
            func = angle_functions[angle_combo.get()]
            args = [float(Fraction(x.strip())) for x in angle_input.get().split(',') if x.strip()]
            result = func(*args)
            angle_output.set(f"Result: {result}")
            draw_result(result, angle_combo.get())
        elif tab == "math":
            func = math_frac_functions[math_combo.get()]
            args = [Fraction(x.strip()) for x in math_input.get().split(',') if x.strip()]
            result = func(*args)
            math_output.set(f"Result: {result}")
            draw_result(float(result), math_combo.get())
    except Exception as e:
        if tab == "advanced":
            adv_output.set(f"Error: {e}")
        elif tab == "angles":
            angle_output.set(f"Error: {e}")
        elif tab == "math":
            math_output.set(f"Error: {e}")
        ax.clear()
        ax.set_title("Error")
        canvas.draw()

# --- Buttons for each tab ---
ttk.Button(tab_advanced, text="Calculate", command=lambda: calculate("advanced")).pack(pady=5)
ttk.Button(tab_angles, text="Calculate", command=lambda: calculate("angles")).pack(pady=5)
ttk.Button(tab_math, text="Calculate", command=lambda: calculate("math")).pack(pady=5)
# occult_calculator_part5.py

# --- Run the GUI ---
root.mainloop()

