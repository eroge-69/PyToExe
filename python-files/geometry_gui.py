# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import math

# Formula mappings for shapes
SHAPE_FORMULAS = {
    "Square": {
        "Area (side)": lambda a: a**2,
        "Area (diagonal)": lambda d: 0.5 * d**2,
        "Area (perimeter)": lambda p: (p**2) / 16,
        "Perimeter": lambda a: 4 * a,
        "Diagonal": lambda a: a * math.sqrt(2),
    },
    "Rectangle": {
        "Area (length � width)": lambda l, w: l * w,
        "Area (diagonal & angle)": lambda d, theta: 0.5 * d**2 * math.sin(math.radians(theta)),
        "Perimeter": lambda l, w: 2 * (l + w),
        "Diagonal": lambda l, w: math.sqrt(l**2 + w**2),
    },
    "Circle": {
        "Area (radius)": lambda r: math.pi * r**2,
        "Area (diameter)": lambda d: (math.pi * d**2) / 4,
        "Area (circumference)": lambda c: (c**2) / (4 * math.pi),
        "Circumference (radius)": lambda r: 2 * math.pi * r,
        "Circumference (diameter)": lambda d: math.pi * d,
    },
    "Triangle": {
        "Area (base � height)": lambda b, h: 0.5 * b * h,
        "Area (Heron)": lambda a, b, c: math.sqrt(
            ((a + b + c) / 2) * (((a + b + c) / 2 - a) *
                                ((a + b + c) / 2 - b) *
                                ((a + b + c) / 2 - c)),
        ),
        "Area (2 sides & angle)": lambda a, b, angle: 0.5 * a * b * math.sin(math.radians(angle)),
        "Perimeter": lambda a, b, c: a + b + c,
    },
    "Trapezoid": {
        "Area (2 bases & height)": lambda a, b, h: 0.5 * (a + b) * h,
        "Area (midsegment & height)": lambda m, h: m * h,
        "Perimeter": lambda a, b, c, d: a + b + c + d,
    },
    "Octagon": {
        "Area (side)": lambda a: 2 * (1 + math.sqrt(2)) * a**2,
        "Area (apothem & perimeter)": lambda p, a: 0.5 * p * a,
        "Perimeter": lambda a: 8 * a,
    },
    "Ellipse": {
        "Area": lambda a, b: math.pi * a * b,
        "Approx. Perimeter": lambda a, b: math.pi * (3 * (a + b) - math.sqrt((3*a + b)*(a + 3*b))),
    }
}

class GeometryCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Geometry Shape Calculator")
        self.geometry("480x400")
        self.resizable(False, False)

        self.shape_var = tk.StringVar()
        self.formula_var = tk.StringVar()

        # Shape selector
        ttk.Label(self, text="Select Shape:", font=("Arial", 12)).pack(pady=10)
        self.shape_menu = ttk.Combobox(self, textvariable=self.shape_var, values=list(SHAPE_FORMULAS.keys()), state="readonly")
        self.shape_menu.pack()
        self.shape_menu.bind("<<ComboboxSelected>>", self.update_formulas)

        # Formula selector
        ttk.Label(self, text="Select Formula:", font=("Arial", 12)).pack(pady=10)
        self.formula_menu = ttk.Combobox(self, textvariable=self.formula_var, state="readonly")
        self.formula_menu.pack()
        self.formula_menu.bind("<<ComboboxSelected>>", self.show_input_fields)

        # Frame for input fields
        self.inputs_frame = tk.Frame(self)
        self.inputs_frame.pack(pady=10)

        # Calculate button
        self.calc_btn = ttk.Button(self, text="Calculate", command=self.calculate)
        self.calc_btn.pack(pady=10)

        # Result
        self.result_label = ttk.Label(self, text="", font=("Arial", 12), foreground="blue")
        self.result_label.pack(pady=5)

    def update_formulas(self, event):
        shape = self.shape_var.get()
        if shape in SHAPE_FORMULAS:
            self.formula_menu["values"] = list(SHAPE_FORMULAS[shape].keys())
            self.formula_menu.set("")
            self.clear_inputs()

    def show_input_fields(self, event):
        self.clear_inputs()
        shape = self.shape_var.get()
        formula = self.formula_var.get()
        if shape and formula:
            func = SHAPE_FORMULAS[shape][formula]
            arg_count = func.__code__.co_argcount
            self.entries = []
            for i in range(arg_count):
                label = tk.Label(self.inputs_frame, text=f"Input {i+1}:")
                label.grid(row=i, column=0, sticky="w", padx=5, pady=5)
                entry = ttk.Entry(self.inputs_frame)
                entry.grid(row=i, column=1, padx=5, pady=5)
                self.entries.append(entry)

    def clear_inputs(self):
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()

    def calculate(self):
        shape = self.shape_var.get()
        formula = self.formula_var.get()
        if not shape or not formula:
            messagebox.showerror("Error", "Select shape and formula.")
            return

        func = SHAPE_FORMULAS[shape][formula]
        try:
            args = [float(entry.get()) for entry in self.entries]
            result = func(*args)
            self.result_label.config(text=f"Result: {round(result, 4)}")
        except Exception as e:
            messagebox.showerror("Calculation Error", str(e))

if __name__ == "__main__":
    app = GeometryCalculatorApp()
    app.mainloop()
