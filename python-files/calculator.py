import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import math
import re
from sympy import symbols, sympify, simplify, factor
import time
import json
import os


# --- Global Variables ---
variables = {v: 0 for v in "BCDEFGXYZ"}
constants = {
    "P": 3.14159265,       # Pi
    "O": 9.80665,         # Gravity
    "K": 2.718281828,     # Euler's number
    "C": 299792458,        # Speed of light
    "L": 6.02214076e23,   # Avogadro's number
    "J": 6.62607015e-34   # Planck's constant
}
constant_explanations = {
    "P": "Pi — ratio of a circle's circumference to its diameter",
    "O": "Gravity — acceleration due to gravity on Earth (m/s²)",
    "K": "Euler's number — base of natural logarithms",
    "C": "Speed of light — in vacuum (m/s)",
    "L": "Avogadro's number — particles per mole",
    "J": "Planck's constant — quantum of electromagnetic action (J·s)"
}
angle_mode = "degrees"
fraction_mode = "decimal"
ans = None
P = 3.14159
history = []
child_windows = []
themes = {
    "Black": {"bg": "#000000", "fg": "#ffffff"},
    "Grey": {"bg": "#353535", "fg": "#ffffff"},
    "White": {"bg": "#ffffff", "fg": "#000000"},
    "Navy": {"bg": "#001f3f", "fg": "#ffffff"},
    "Olive": {"bg": "#222b13", "fg": "#ffffff"},
}
p = 3.14159265  # constant value, not editable
def calculate():
    global ans
    try:
        original_expr = entry.get()

        expr = original_expr.replace("^", "**")
        expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
        expr = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expr)

        # Replace constants
        for const, val in constants.items():
            expr = re.sub(rf'\b{const}\b', str(val), expr)

        # Replace A with ans
        expr = re.sub(r'\bA\b', str(ans if ans is not None else 0), expr)

        # Replace variables
        for var, val in variables.items():
            expr = re.sub(rf'\b{var}\b', str(val), expr)

        x = symbols('x')
        result = eval(expr, {"__builtins__": None}, {
            **vars(math),
            "x": x,
            "ans": ans
        })

        ans = result
        entry.delete(0, tk.END)
        entry.insert(0, str(result))
        history.append(f"{original_expr} = {result}")

    except Exception:
        entry.delete(0, tk.END)
        entry.insert(0, "Error")
        ans = None




def clear():
    entry.delete(0, tk.END)

def delete_last():
    entry.delete(len(entry.get()) - 1, tk.END)

def click(event):
    entry.insert(tk.END, event.widget["text"])
def open_constants_panel():
    const_win = tk.Toplevel(root)
    child_windows.append(const_win)
    const_win.title("Constants")
    const_win.geometry("300x575")
    const_win.resizable(False, False)
    const_win.protocol("WM_DELETE_WINDOW", lambda w=const_win: (child_windows.remove(w), w.destroy()))

    tk.Label(const_win, text="Physical & Mathematical Constants", font=("Arial", 14)).pack(pady=10)

    grid = tk.Frame(const_win)
    grid.pack(fill="both", expand=True, padx=10, pady=10)

    for name, value in constants.items():
        row = tk.Frame(grid)
        row.pack(fill="x", pady=5)

        tk.Label(row, text=f"{name} = {value}", font=("Arial", 12), width=20, anchor="w").pack(side="top", anchor="w")
        tk.Label(row, text=constant_explanations.get(name, ""), font=("Arial", 10), fg="gray", wraplength=450, justify="left").pack(side="top", anchor="w")

        def make_recaller(n=name):
            return lambda: entry.insert(tk.END, n)

        tk.Button(row, text="Recall", font=("Arial", 10), command=make_recaller()).pack(side="right", padx=5)

def open_variable_panel():
    var_win = tk.Toplevel(root)
    child_windows.append(var_win)
    var_win.title("Variables")
    var_win.geometry("220x350")
    var_win.resizable(False, False)
    var_win.protocol("WM_DELETE_WINDOW", lambda w=var_win: (child_windows.remove(w), w.destroy()))

    tk.Label(var_win, text="Variable Manager", font=("Arial", 14)).pack(pady=10)

    grid = tk.Frame(var_win)
    grid.pack(fill="both", expand=True, padx=10, pady=10)

    for i, var in enumerate(variables):
        row = tk.Frame(grid)
        row.pack(fill="x", pady=2)

        val_label = tk.Label(row, text=f"{var} = {variables[var]}", font=("Arial", 12), width=10)
        val_label.pack(side="left")

        def make_setter(v=var, label=val_label):
            return lambda: (
                variables.__setitem__(v, ans if ans is not None else 0),
                label.config(text=f"{v} = {variables[v]}")
            )

        def make_recaller(v=var):
            return lambda: entry.insert(tk.END, v)

        tk.Button(row, text="Set", font=("Arial", 10), command=make_setter()).pack(side="left", padx=5)
        tk.Button(row, text="Recall", font=("Arial", 10), command=make_recaller()).pack(side="left", padx=5)


def open_simplify_window():
    simplify_win = tk.Toplevel(root)
    child_windows.append(simplify_win)
    simplify_win.title("Simplify Expression")
    simplify_win.geometry("400x200")
    simplify_win.resizable(False, False)
    simplify_win.protocol("WM_DELETE_WINDOW", lambda w=simplify_win: (child_windows.remove(w), w.destroy()))

    tk.Label(simplify_win, text="Enter expression:", font=("Arial", 12)).pack(pady=5)
    expr_entry = tk.Entry(simplify_win, font=("Arial", 12))
    expr_entry.pack(fill="x", padx=10)

    result_label = tk.Label(simplify_win, text="", font=("Arial", 12), fg="blue")
    result_label.pack(pady=10)

    def simplify_expr():
        try:
            x = symbols('x')
            expr = sympify(expr_entry.get(), locals={'x': x})
            simplified = simplify(expr)
            result_label.config(text=f"Simplified: {simplified}", fg="blue")
        except Exception:
            result_label.config(text="Error: Invalid expression", fg="red")

    tk.Button(simplify_win, text="Simplify", font=("Arial", 12), command=simplify_expr).pack(pady=5)

    # Instructional note
    tk.Label(simplify_win, text="Please write expressions like: e.g. 3*x + 2*x", font=("Arial", 10), fg="gray").pack(pady=5)

def open_factor_window():
    factor_win = tk.Toplevel(root)
    child_windows.append(factor_win)
    factor_win.title("Factor Expression")
    factor_win.geometry("400x200")
    factor_win.resizable(False, False)
    factor_win.protocol("WM_DELETE_WINDOW", lambda w=factor_win: (child_windows.remove(w), w.destroy()))

    tk.Label(factor_win, text="Enter polynomial:", font=("Arial", 12)).pack(pady=5)
    poly_entry = tk.Entry(factor_win, font=("Arial", 12))
    poly_entry.pack(fill="x", padx=10)

    result_label = tk.Label(factor_win, text="", font=("Arial", 12), fg="blue")
    result_label.pack(pady=10)

    def factor_expr():
        try:
            x = symbols('x')
            expr = sympify(poly_entry.get(), locals={'x': x})
            factored = factor(expr)
            result_label.config(text=f"Factored: {factored}", fg="blue")
        except Exception:
            result_label.config(text="Error: Invalid polynomial", fg="red")

    tk.Button(factor_win, text="Factor", font=("Arial", 12), command=factor_expr).pack(pady=5)

def open_graph_window():
    graph_win = tk.Toplevel(root)
    child_windows.append(graph_win)
    graph_win.title("Graph Any Equation")
    graph_win.geometry("500x550")
    graph_win.resizable(False, False)

    tk.Label(graph_win, text="Enter equation in y = f(x) form:", font=("Arial", 12)).pack(pady=5)
    eq_entry = tk.Entry(graph_win, font=("Arial", 12))
    eq_entry.pack(fill="x", padx=10)

    result_label = tk.Label(graph_win, text="", font=("Arial", 11), fg="red")
    result_label.pack()

    def plot_graph():
        try:
            raw = eq_entry.get().strip()
            if not raw.startswith("y="):
                raise ValueError("Equation must start with 'y='")

            expr_str = raw[2:].replace("^", "**")
            expr_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr_str)
            expr_str = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr_str)
            expr_str = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expr_str)

            x = symbols('x')
            expr = sympify(expr_str, locals={'x': x})
            f = lambda val: eval(str(expr), {"x": val, "math": math, "sin": math.sin, "cos": math.cos,
                                             "tan": math.tan, "log": math.log, "exp": math.exp,
                                             "sqrt": math.sqrt, "abs": abs})

            x_vals = np.linspace(-100, 100, 1000)
            y_vals = []
            for val in x_vals:
                try:
                    y = f(val)
                    y_vals.append(y)
                except:
                    y_vals.append(np.nan)

            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.set_aspect('auto')  # Auto scaling

            ax.plot(x_vals, y_vals, label=f"y = {expr_str}", color="blue")
            ax.axhline(0, color='black', linewidth=3)
            ax.axvline(0, color='black', linewidth=3)
            ax.set_title("Graph of y = f(x)")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.grid(True)
            ax.legend()

            canvas = FigureCanvasTkAgg(fig, master=graph_win)
            canvas.draw()
            canvas.get_tk_widget().pack()

            toolbar = NavigationToolbar2Tk(canvas, graph_win)
            toolbar.update()
            toolbar.pan()

            btn_frame = tk.Frame(graph_win)
            btn_frame.pack(pady=5)

            def refresh_view():
                ax.set_xlim(-100, 100)
                ax.set_ylim(-100, 100)
                canvas.draw()

            def recenter_view():
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                x_range = xlim[1] - xlim[0]
                y_range = ylim[1] - ylim[0]
                ax.set_xlim(-x_range / 2, x_range / 2)
                ax.set_ylim(-y_range / 2, y_range / 2)
                canvas.draw()

            tk.Button(btn_frame, text="Refresh View", font=("Arial", 10), command=refresh_view).pack(side="left", padx=10)
            tk.Button(btn_frame, text="Recenter", font=("Arial", 10), command=recenter_view).pack(side="left", padx=10)

            result_label.config(text="")

        except Exception as e:
            result_label.config(text=f"Error: {str(e)}")

    tk.Button(graph_win, text="Plot", font=("Arial", 12), command=plot_graph).pack(pady=10)

def open_simultaneous_solver():
    sim_win = tk.Toplevel(root)
    child_windows.append(sim_win)
    sim_win.title("Simultaneous Solver")
    sim_win.geometry("400x300")
    sim_win.resizable(False, False)

    tk.Label(sim_win, text="Enter two equations:", font=("Arial", 12)).pack(pady=5)
    eq1_entry = tk.Entry(sim_win, font=("Arial", 12))
    eq1_entry.pack(fill="x", padx=10)
    eq2_entry = tk.Entry(sim_win, font=("Arial", 12))
    eq2_entry.pack(fill="x", padx=10)

    result_label = tk.Label(sim_win, text="", font=("Arial", 12), fg="blue")
    result_label.pack(pady=10)

    def solve_system():
        try:
            x, y = symbols('x y')
            eq1 = sympify(eq1_entry.get(), locals={'x': x, 'y': y})
            eq2 = sympify(eq2_entry.get(), locals={'x': x, 'y': y})
            from sympy import solve
            sol = solve([eq1, eq2], (x, y))
            result_label.config(text=f"Solution: x = {sol[x]}, y = {sol[y]}", fg="blue")
        except Exception:
            result_label.config(text="Error: Invalid system", fg="red")

    tk.Button(sim_win, text="Solve", font=("Arial", 12), command=solve_system).pack(pady=5)
def open_table_to_equation():
    table_win = tk.Toplevel(root)
    child_windows.append(table_win)
    table_win.title("Table to Equation")
    table_win.geometry("400x400")
    table_win.resizable(False, False)

    tk.Label(table_win, text="Enter x values (comma-separated):", font=("Arial", 12)).pack(pady=5)
    x_entry = tk.Entry(table_win, font=("Arial", 12))
    x_entry.pack(fill="x", padx=10)

    tk.Label(table_win, text="Enter y values (comma-separated):", font=("Arial", 12)).pack(pady=5)
    y_entry = tk.Entry(table_win, font=("Arial", 12))
    y_entry.pack(fill="x", padx=10)

    result_label = tk.Label(table_win, text="", font=("Arial", 12), fg="blue")
    result_label.pack(pady=10)

    def compute_equation():
        try:
            x_vals = list(map(float, x_entry.get().split(",")))
            y_vals = list(map(float, y_entry.get().split(",")))
            if len(x_vals) != len(y_vals) or len(x_vals) < 2:
                raise ValueError("Mismatched or insufficient data")

            m = (y_vals[-1] - y_vals[0]) / (x_vals[-1] - x_vals[0])
            b = y_vals[0] - m * x_vals[0]
            result_label.config(text=f"Equation: y = {round(m, 3)}x + {round(b, 3)}", fg="blue")
        except Exception:
            result_label.config(text="Error: Invalid input", fg="red")

    tk.Button(table_win, text="Find Equation", font=("Arial", 12), command=compute_equation).pack(pady=10)

def open_scientific_panel():
    sci_win = tk.Toplevel(root)
    child_windows.append(sci_win)
    sci_win.title("Scientific Functions")
    sci_win.geometry("300x300")
    sci_win.resizable(False, False)
    sci_win.protocol("WM_DELETE_WINDOW", lambda w=sci_win: (child_windows.remove(w), w.destroy()))

    grid = tk.Frame(sci_win)
    grid.pack(expand=True, fill="both", padx=10, pady=10)

    functions = [
        ("sin", "sin("), ("cos", "cos("), ("tan", "tan("),
        ("asin", "asin("), ("acos", "acos("), ("atan", "atan("),
        ("log", "log("), ("log10", "log10("), ("x^y", "^")
    ]

    for i, (label, insert_text) in enumerate(functions):
        if label == "x^y":
            btn = tk.Button(grid, text=label, font=("Arial", 12), command=lambda: entry.insert(tk.END, '^'))
        else:
            btn = tk.Button(grid, text=label, font=("Arial", 12), command=lambda t=insert_text: entry.insert(tk.END, t))
        btn.grid(row=i // 3, column=i % 3, sticky="nsew", padx=2, pady=2)

    for i in range(3): grid.columnconfigure(i, weight=1)
    for i in range(3): grid.rowconfigure(i, weight=1)

def apply_theme(name):
    theme = themes.get(name, themes["White"])
    bg, fg = theme["bg"], theme["fg"]

    root.config(bg=bg)
    entry.config(bg=bg, fg=fg, insertbackground=fg)

    def apply_to_children(widget):
        for child in widget.winfo_children():
            try:
                child.config(bg=bg, fg=fg)
                if isinstance(child, tk.Entry):
                    child.config(insertbackground=fg)
                elif isinstance(child, tk.Text):
                    child.config(insertbackground=fg)
            except:
                pass
            apply_to_children(child)

    apply_to_children(root)
    for win in child_windows:
        try:
            win.config(bg=bg)
            apply_to_children(win)
        except:
            pass


def open_theme_panel():
    theme_win = tk.Toplevel(root)
    child_windows.append(theme_win)
    theme_win.title("Theme Selector")
    theme_win.geometry("300x300")
    theme_win.resizable(False, False)
    theme_win.protocol("WM_DELETE_WINDOW", lambda w=theme_win: (child_windows.remove(w), w.destroy()))

    label = tk.Label(theme_win, text="Choose a Theme", font=("Arial", 14))
    label.pack(pady=10)

    for name in themes:
        btn = tk.Button(theme_win, text=name, font=("Arial", 12),
                        command=lambda n=name: apply_theme(n))
        btn.pack(fill="x", padx=20, pady=5)

def open_history_window():
    hist_win = tk.Toplevel(root)
    child_windows.append(hist_win)
    hist_win.title("History")
    hist_win.geometry("400x300")
    hist_win.resizable(False, False)
    hist_win.protocol("WM_DELETE_WINDOW", lambda w=hist_win: (child_windows.remove(w), w.destroy()))

    listbox = tk.Listbox(hist_win, font=("Arial", 12))
    listbox.pack(expand=True, fill="both", padx=10, pady=10)

    for item in history:
        listbox.insert(tk.END, item)

    def recall():
        selected = listbox.curselection()
        if selected:
            expr = history[selected[0]].split(" = ")[0]
            entry.delete(0, tk.END)
            entry.insert(0, expr)

    tk.Button(hist_win, text="sync", font=("Arial", 12), command=recall).pack(pady=5)

def open_ratio_panel():
    ratio_win = tk.Toplevel(root)
    child_windows.append(ratio_win)
    ratio_win.title("Ratio Tools")
    ratio_win.geometry("300x250")
    ratio_win.resizable(False, False)
    ratio_win.protocol("WM_DELETE_WINDOW", lambda w=ratio_win: (child_windows.remove(w), w.destroy()))

    tk.Label(ratio_win, text="Choose a Ratio Tool", font=("Arial", 14)).pack(pady=10)

    tk.Button(ratio_win, text="Simplify Ratio", font=("Arial", 12), command=open_ratio_simplifier).pack(fill="x", padx=20, pady=5)
    tk.Button(ratio_win, text="Combine Ratios", font=("Arial", 12), command=open_ratio_combiner).pack(fill="x", padx=20, pady=5)
    tk.Button(ratio_win, text="Solve Ratio", font=("Arial", 12), command=open_ratio_solver).pack(fill="x", padx=20, pady=5)
def open_ratio_panel():
    ratio_win = tk.Toplevel(root)
    child_windows.append(ratio_win)
    ratio_win.title("Ratio Tools")
    ratio_win.geometry("300x250")
    ratio_win.resizable(False, False)
    ratio_win.protocol("WM_DELETE_WINDOW", lambda w=ratio_win: (child_windows.remove(w), w.destroy()))

    tk.Label(ratio_win, text="Choose a Ratio Tool", font=("Arial", 14)).pack(pady=10)

    tk.Button(ratio_win, text="Simplify Ratio", font=("Arial", 12), command=open_ratio_simplifier).pack(fill="x", padx=20, pady=5)
    tk.Button(ratio_win, text="Combine Ratios", font=("Arial", 12), command=open_ratio_combiner).pack(fill="x", padx=20, pady=5)
    tk.Button(ratio_win, text="Solve Ratio", font=("Arial", 12), command=open_ratio_solver).pack(fill="x", padx=20, pady=5)

def open_ratio_simplifier():
    win = tk.Toplevel(root)
    child_windows.append(win)
    win.title("Simplify Ratio")
    win.geometry("300x200")
    win.resizable(False, False)
    win.protocol("WM_DELETE_WINDOW", lambda w=win: (child_windows.remove(w), w.destroy()))

    tk.Label(win, text="Enter ratio (a:b):", font=("Arial", 12)).pack(pady=5)
    entry = tk.Entry(win, font=("Arial", 12))
    entry.pack(fill="x", padx=10)

    result = tk.Label(win, text="", font=("Arial", 12), fg="blue")
    result.pack(pady=10)

    def simplify_ratio():
        try:
            a, b = map(int, entry.get().split(":"))
            from math import gcd
            g = gcd(a, b)
            result.config(text=f"Simplified: {a//g}:{b//g}", fg="blue")
        except:
            result.config(text="Error: Invalid input", fg="red")

    tk.Button(win, text="Simplify", font=("Arial", 12), command=simplify_ratio).pack(pady=5)

def open_ratio_combiner():
    win = tk.Toplevel(root)
    child_windows.append(win)
    win.title("Combine Ratios")
    win.geometry("350x250")
    win.resizable(False, False)
    win.protocol("WM_DELETE_WINDOW", lambda w=win: (child_windows.remove(w), w.destroy()))

    tk.Label(win, text="Enter a:b (e.g. 10:12):", font=("Arial", 12)).pack(pady=5)
    ab_entry = tk.Entry(win, font=("Arial", 12))
    ab_entry.pack(fill="x", padx=10)

    tk.Label(win, text="Enter b:c (e.g. 1:2):", font=("Arial", 12)).pack(pady=5)
    bc_entry = tk.Entry(win, font=("Arial", 12))
    bc_entry.pack(fill="x", padx=10)

    result = tk.Label(win, text="", font=("Arial", 12), fg="blue")
    result.pack(pady=10)

    def combine_ratios():
        try:
            a, b1 = map(int, ab_entry.get().split(":"))
            b2, c = map(int, bc_entry.get().split(":"))
            lcm = np.lcm(b1, b2)
            a_scaled = a * (lcm // b1)
            b_scaled = lcm
            c_scaled = c * (lcm // b2)
            result.config(text=f"Combined: a:b:c = {a_scaled}:{b_scaled}:{c_scaled}", fg="blue")
        except:
            result.config(text="Error: Invalid input", fg="red")

    tk.Button(win, text="Combine", font=("Arial", 12), command=combine_ratios).pack(pady=5)

def open_data_stats_panel():
    stats_win = tk.Toplevel(root)
    child_windows.append(stats_win)
    stats_win.title("Data Stats")
    stats_win.geometry("400x400")
    stats_win.resizable(False, False)
    stats_win.protocol("WM_DELETE_WINDOW", lambda w=stats_win: (child_windows.remove(w), w.destroy()))

    tk.Label(stats_win, text="Enter numbers (comma-separated):", font=("Arial", 12)).pack(pady=5)
    entry = tk.Entry(stats_win, font=("Arial", 12))
    entry.pack(fill="x", padx=10)

    result_label = tk.Label(stats_win, text="", font=("Arial", 12), fg="blue", justify="left")
    result_label.pack(pady=10)

    def compute_stats():
        try:
            data = list(map(float, entry.get().split(",")))
            if len(data) < 2:
                raise ValueError("Need at least 2 values")

            import statistics as stats

            mean = round(stats.mean(data), 3)
            median = round(stats.median(data), 3)
            try:
                mode = round(stats.mode(data), 3)
            except:
                mode = "No unique mode"
            range_val = round(max(data) - min(data), 3)
            variance = round(stats.variance(data), 3)
            stdev = round(stats.stdev(data), 3)

            result_text = (
                f"Mean: {mean}\n"
                f"Median: {median}\n"
                f"Mode: {mode}\n"
                f"Range: {range_val}\n"
                f"Variance: {variance}\n"
                f"Standard Deviation: {stdev}"
            )
            result_label.config(text=result_text, fg="blue")
        except:
            result_label.config(text="Error: Invalid input", fg="red")

    tk.Button(stats_win, text="Compute", font=("Arial", 12), command=compute_stats).pack(pady=5)

def open_shape_calculator():
    shape_win = tk.Toplevel(root)
    child_windows.append(shape_win)
    shape_win.title("Shape Calculator")
    shape_win.geometry("450x450")
    shape_win.resizable(True, True)
    shape_win.protocol("WM_DELETE_WINDOW", lambda w=shape_win: (child_windows.remove(w), w.destroy()))

    tk.Label(shape_win, text="Choose a shape:", font=("Arial", 14)).pack(pady=10)

    shape_var = tk.StringVar(value="Circle")
    shapes = ["Circle", "Square", "Rectangle", "Triangle", "Trapezium"]
    shape_menu = ttk.Combobox(shape_win, textvariable=shape_var, values=shapes, font=("Arial", 12), state="readonly")
    shape_menu.pack(fill="x", padx=20)

    input_frame = tk.Frame(shape_win)
    input_frame.pack(fill="both", expand=True, padx=10, pady=10)

    result_label = tk.Label(shape_win, text="", font=("Arial", 12), fg="blue", justify="left")
    result_label.pack(pady=10)

    entries = {}

    def update_inputs(*args):
        for widget in input_frame.winfo_children():
            widget.destroy()
        entries.clear()

        shape = shape_var.get()
        fields = {
            "Circle": ["Radius"],
            "Square": ["Side"],
            "Rectangle": ["Length", "Width"],
            "Triangle": ["Base", "Height", "Side A", "Side B", "Side C"],
            "Trapezium": ["Base A", "Base B", "Height", "Side A", "Side B"]
        }[shape]


        for field in fields:
            tk.Label(input_frame, text=field + ":", font=("Arial", 12)).pack()
            ent = tk.Entry(input_frame, font=("Arial", 12))
            ent.pack(fill="x")
            entries[field] = ent

    shape_var.trace_add("write", update_inputs)
    update_inputs()

    def compute_shape():
        try:
            vals = {k: float(e.get()) for k, e in entries.items()}
            shape = shape_var.get()

            if shape == "Circle":
                r = vals["Radius"]
                area = round(math.pi * r**2, 3)
                perimeter = round(2 * math.pi * r, 3)

            elif shape == "Square":
                s = vals["Side"]
                area = round(s**2, 3)
                perimeter = round(4 * s, 3)

            elif shape == "Rectangle":
                l, w = vals["Length"], vals["Width"]
                area = round(l * w, 3)
                perimeter = round(2 * (l + w), 3)

            elif shape == "Triangle":
                b, h = vals["Base"], vals["Height"]
                a, c = vals["Side A"], vals["Side C"]
                area = round(0.5 * b * h, 3)
                perimeter = round(b + a + c, 3)

            elif shape == "Trapezium":
                a, b = vals["Base A"], vals["Base B"]
                h = vals["Height"]
                sa, sb = vals["Side A"], vals["Side B"]
                area = round(0.5 * (a + b) * h, 3)
                perimeter = round(a + b + sa + sb, 3)

            result_label.config(text=f"Area: {area}\nPerimeter: {perimeter}", fg="blue")

        except Exception:
            result_label.config(text="Error: Invalid input", fg="red")

    tk.Button(shape_win, text="Compute", font=("Arial", 12), command=compute_shape).pack(pady=5)

def open_ratio_solver():
    win = tk.Toplevel(root)
    child_windows.append(win)
    win.title("Solve Ratio")
    win.geometry("400x300")
    win.resizable(False, False)
    win.protocol("WM_DELETE_WINDOW", lambda w=win: (child_windows.remove(w), w.destroy()))

    tk.Label(win, text="Total value to split:", font=("Arial", 12)).pack(pady=5)
    total_entry = tk.Entry(win, font=("Arial", 12))
    total_entry.pack(fill="x", padx=10)

    tk.Label(win, text="Enter ratio (e.g. 10:2:8):", font=("Arial", 12)).pack(pady=5)
    ratio_entry = tk.Entry(win, font=("Arial", 12))
    ratio_entry.pack(fill="x", padx=10)

    result = tk.Label(win, text="", font=("Arial", 12), fg="blue")
    result.pack(pady=10)

    def solve_ratio():
        try:
            total = float(total_entry.get())
            parts = list(map(float, ratio_entry.get().split(":")))
            total_parts = sum(parts)
            shares = [round(total * p / total_parts, 2) for p in parts]
            result.config(text="Shares: " + ", ".join(f"Part {i+1} = {s}" for i, s in enumerate(shares)), fg="blue")
        except:
            result.config(text="Error: Invalid input", fg="red")

    tk.Button(win, text="Solve", font=("Arial", 12), command=solve_ratio).pack(pady=5)

def open_shape_calculator():
    shape_win = tk.Toplevel(root)
    child_windows.append(shape_win)
    shape_win.title("Shape Calculator")
    shape_win.geometry("600x600")
    shape_win.resizable(False, False)
    shape_win.protocol("WM_DELETE_WINDOW", lambda w=shape_win: (child_windows.remove(w), w.destroy()))

    tk.Label(shape_win, text="Choose a shape:", font=("Arial", 14)).pack(pady=10)

    shape_var = tk.StringVar(value="Circle")
    shapes = ["Circle", "Square", "Rectangle", "Triangle", "Trapezium"]
    shape_menu = ttk.Combobox(shape_win, textvariable=shape_var, values=shapes, font=("Arial", 12), state="readonly")
    shape_menu.pack(fill="x", padx=20)

    input_frame = tk.Frame(shape_win)
    input_frame.pack(fill="both", expand=True, padx=10, pady=10)

    result_label = tk.Label(shape_win, text="", font=("Arial", 12), fg="blue", justify="left")
    result_label.pack(pady=10)

    # Matplotlib canvas
    fig = Figure(figsize=(4.5, 3.5), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=shape_win)
    canvas.get_tk_widget().pack()

    entries = {}

    def update_inputs(*args):
        for widget in input_frame.winfo_children():
            widget.destroy()
        entries.clear()

        shape = shape_var.get()
        fields = {
            "Circle": ["Radius"],
            "Square": ["Side"],
            "Rectangle": ["Length", "Width"],
            "Triangle": ["Base", "Height", "Side A", "Side C"],
            "Trapezium": ["Base A", "Base B", "Height", "Side A", "Side B"]
        }[shape]

        for field in fields:
            tk.Label(input_frame, text=field + ":", font=("Arial", 12)).pack()
            ent = tk.Entry(input_frame, font=("Arial", 12))
            ent.pack(fill="x")
            entries[field] = ent

    shape_var.trace_add("write", update_inputs)
    update_inputs()

    def compute_shape():
        try:
            vals = {k: float(e.get()) for k, e in entries.items()}
            shape = shape_var.get()
            ax.clear()

            if shape == "Circle":
                r = vals["Radius"]
                area = round(math.pi * r**2, 3)
                perimeter = round(2 * math.pi * r, 3)
                circle = plt.Circle((0, 0), r, fill=False, color="blue")
                ax.add_patch(circle)
                ax.text(0, r + 0.5, f"r = {r}", ha="center", fontsize=10)
                ax.set_xlim(-r*1.5, r*1.5)
                ax.set_ylim(-r*1.5, r*1.5)

            elif shape == "Square":
                s = vals["Side"]
                area = round(s**2, 3)
                perimeter = round(4 * s, 3)
                ax.plot([0, s, s, 0, 0], [0, 0, s, s, 0], color="green")
                ax.text(s/2, -0.5, f"{s}", ha="center", fontsize=10)
                ax.text(-0.5, s/2, f"{s}", va="center", fontsize=10)
                ax.set_xlim(-1, s + 1)
                ax.set_ylim(-1, s + 1)

            elif shape == "Rectangle":
                l, w = vals["Length"], vals["Width"]
                area = round(l * w, 3)
                perimeter = round(2 * (l + w), 3)
                ax.plot([0, l, l, 0, 0], [0, 0, w, w, 0], color="purple")
                ax.text(l/2, -0.5, f"L = {l}", ha="center", fontsize=10)
                ax.text(-0.5, w/2, f"W = {w}", va="center", fontsize=10)
                ax.set_xlim(-1, l + 1)
                ax.set_ylim(-1, w + 1)

            elif shape == "Triangle":
                b, h = vals["Base"], vals["Height"]
                a, c = vals["Side A"], vals["Side C"]
                area = round(0.5 * b * h, 3)
                perimeter = round(b + a + c, 3)
                ax.plot([0, b, b/2, 0], [0, 0, h, 0], color="orange")
                ax.text(b/2, -0.5, f"Base = {b}", ha="center", fontsize=10)
                ax.text(b + 0.5, h/2, f"Side C = {c}", fontsize=10)
                ax.text(-0.5, h/2, f"Side A = {a}", fontsize=10)
                ax.set_xlim(-1, b + 1)
                ax.set_ylim(-1, h + 1)

            elif shape == "Trapezium":
                a, b = vals["Base A"], vals["Base B"]
                h = vals["Height"]
                sa, sb = vals["Side A"], vals["Side B"]
                area = round(0.5 * (a + b) * h, 3)
                perimeter = round(a + b + sa + sb, 3)
                ax.plot([0, a, b, 0, 0], [0, 0, h, h, 0], color="brown")
                ax.text(a/2, -0.5, f"Base A = {a}", ha="center", fontsize=10)
                ax.text(b/2, h + 0.5, f"Base B = {b}", ha="center", fontsize=10)
                ax.text(-0.5, h/2, f"Side A = {sa}", va="center", fontsize=10)
                ax.text(a + 0.5, h/2, f"Side B = {sb}", va="center", fontsize=10)
                ax.set_xlim(-1, max(a, b) + 2)
                ax.set_ylim(-1, h + 2)

            ax.set_aspect('equal')
            ax.axis('off')
            canvas.draw()

            result_label.config(text=f"Area: {area}\nPerimeter: {perimeter}", fg="blue")

        except Exception:
            result_label.config(text="Error: Invalid input", fg="red")
            ax.clear()
            canvas.draw()

    tk.Button(shape_win, text="Compute", font=("Arial", 12), command=compute_shape).pack(pady=5)


def open_options_panel():
    screen = tk.Toplevel(root)
    child_windows.append(screen)
    screen.title("Options Panel")
    screen.geometry("450x450")
    screen.resizable(False, False)
    screen.protocol("WM_DELETE_WINDOW", lambda w=screen: (child_windows.remove(w), w.destroy()))

    grid = tk.Frame(screen)
    grid.pack(expand=True, fill="both", padx=10, pady=10)

    options = [
        ("Variables", open_variable_panel),
        ("Constants", open_constants_panel),
        ("History", open_history_window),
        ("Scientific", open_scientific_panel),
        ("Themes", open_theme_panel),
        ("Simultaneous", open_simultaneous_solver),
        ("Graph Line", open_graph_window),
        ("Table to Equation", open_table_to_equation),
        ("Simplify", open_simplify_window),
        ("Factor", open_factor_window),
        ("Ratio Tools", open_ratio_panel),
        ("Data Stats", open_data_stats_panel),
        ("Shape Calculator", open_shape_calculator),

         ]

    for i, (label, command) in enumerate(options):
        btn = tk.Button(grid, text=label, font=("Arial", 12), command=command)
        btn.grid(row=i // 3, column=i % 3, sticky="nsew", padx=2, pady=2)

    angle_btn = tk.Button(grid, text=f"Angle Mode: {angle_mode.capitalize()}", font=("Arial", 12),
                          command=lambda: toggle_angle_mode(angle_btn))
    angle_btn.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=2, pady=2)

    frac_btn = tk.Button(grid, text=f"Fraction Mode: {fraction_mode.capitalize()}", font=("Arial", 12),
                         command=lambda: toggle_fraction_mode(frac_btn))
    frac_btn.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=2, pady=2)

    for i in range(3): grid.columnconfigure(i, weight=1)
    for i in range(6): grid.rowconfigure(i, weight=1)
def toggle_angle_mode(button):
    global angle_mode
    angle_mode = "degrees" if angle_mode == "radians" else "radians"
    button.config(text=f"Angle Mode: {angle_mode.capitalize()}")

def toggle_fraction_mode(button):
    global fraction_mode
    fraction_mode = "mixed" if fraction_mode == "decimal" else "decimal"
    button.config(text=f"Fraction Mode: {fraction_mode.capitalize()}")

root = tk.Tk()
root.title("calculator - T_Bailey")
root.geometry("400x600")
root.resizable(False, False)

entry = tk.Entry(root, font=("Arial", 20), justify="right")
entry.pack(fill="both", padx=10, pady=10)

main_frame = tk.Frame(root)
main_frame.pack(side="left", expand=True, fill="both")

button_frame = tk.Frame(main_frame)
button_frame.pack(expand=True, fill="both")

buttons = [
    ['AC', 'ANS', 'Options', 'DEL'],
    ['(', ')', 'x²', 'x³'],
    ['7', '8', '9', '+'],
    ['4', '5', '6', '-'],
    ['1', '2', '3', '/'],
    ['0', '.', 'EXE', '*']
]

for r, row in enumerate(buttons):
    for c, char in enumerate(row):
        btn = tk.Button(button_frame, text=char, font=("Arial", 18), relief="ridge")
        btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
        if char == 'AC':
            btn.config(command=clear)
        elif char == 'EXE':
            btn.config(command=calculate)
        elif char == 'ANS':
            btn.config(command=lambda: entry.insert(tk.END, "A"))
        elif char == 'Options':
            btn.config(command=open_options_panel)
        elif char == 'DEL':
            btn.config(command=delete_last)
        elif char == 'x²':
            btn.config(command=lambda: entry.insert(tk.END, '**2'))
        elif char == 'x³':
            btn.config(command=lambda: entry.insert(tk.END, '**3'))
        else:
            btn.bind("<Button-1>", click)

for i in range(4):
    button_frame.columnconfigure(i, weight=1)
for i in range(len(buttons)):
    button_frame.rowconfigure(i, weight=1)

def handle_keypress(event):
    key = event.keysym
    if key in '0123456789':
        entry.insert(tk.END, key)
    elif key == 'period':
        entry.insert(tk.END, '.')
    elif key in ['plus', 'KP_Add']:
        entry.insert(tk.END, '+')
    elif key in ['minus', 'KP_Subtract']:
        entry.insert(tk.END, '-')
    elif key in ['asterisk', 'KP_Multiply']:
        entry.insert(tk.END, '*')
    elif key in ['slash', 'KP_Divide']:
        entry.insert(tk.END, '/')
    elif key in ['Return', 'KP_Enter']:
        calculate()
    elif key == 'Escape':
        clear()
    elif key == 'BackSpace':
        delete_last()

def sync_child_windows(event):
    state = root.state()
    for win in child_windows:
        try:
            win.state(state)
        except:
            pass

root.bind("<Key>", handle_keypress)
root.bind("<Unmap>", sync_child_windows)
root.bind("<Map>", sync_child_windows)
root.bind("<Configure>", sync_child_windows)

root.mainloop()
