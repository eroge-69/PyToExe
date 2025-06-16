import math
import tkinter as tk
from tkinter import ttk, messagebox

units_table = [
    ("mm", "χιλιοστόμετρο", "χιλιοστά", "millimeter", "millimeters", 0.001),
    ("cm", "εκατοστόμετρο", "εκατοστά", "centimeter", "centimeters", 0.01),
    ("dm", "δεκατόμετρο", "δεκατόμετρα", "decimeter", "decimeters", 0.1),
    ("m", "μέτρο", "μέτρα", "meter", "meters", 1),
    ("km", "χιλιόμετρο", "χιλιόμετρα", "kilometer", "kilometers", 1000),
]
unit_dict = {u[0]: u for u in units_table}
unit_to_m = {u[0]: u[5] for u in units_table}

# --- Υπολογιστικές συναρτήσεις για κάθε σχήμα ---
def area_circle(r): return math.pi * r ** 2
def perimeter_circle(r): return 2 * math.pi * r

def area_square(a): return a ** 2
def perimeter_square(a): return 4 * a

def area_rectangle(a, b): return a * b
def perimeter_rectangle(a, b): return 2 * (a + b)

def area_triangle(a, h): return 0.5 * a * h
def perimeter_triangle(a, b, c): return a + b + c

def area_parallelogram(a, h): return a * h
def perimeter_parallelogram(a, b): return 2 * (a + b)

# --- GUI Functions ---
def show_shape_window(shape, calc_type):
    win = tk.Toplevel(root)
    win.title(f"{calc_type} - {shape}")
    win.configure(bg="#f0f4f8")

    # Πίνακας μονάδων
    table_frame = ttk.LabelFrame(win, text="Πίνακας Μονάδων", padding=8)
    table_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="ew")
    headers = ["Συντομ.", "Ελληνικά", "Πληθ.", "English", "Plural"]
    for col, h in enumerate(headers):
        ttk.Label(table_frame, text=h, font=("Segoe UI", 9, "bold")).grid(row=0, column=col, padx=3, pady=1)
    for row, u in enumerate(units_table, start=1):
        for col, val in enumerate(u[:5]):
            ttk.Label(table_frame, text=val, font=("Segoe UI", 9)).grid(row=row, column=col, padx=3, pady=1)

    # Ορισμός πεδίων εισόδου ανά σχήμα
    params = []
    if shape == "Κύκλος":
        params = ["Ακτίνα"]
    elif shape == "Τετράγωνο":
        params = ["Πλευρά"]
    elif shape == "Ορθογώνιο":
        params = ["Πλευρά α", "Πλευρά β"]
    elif shape == "Τρίγωνο":
        params = ["Βάση", "Ύψος"] if calc_type == "Εμβαδόν" else ["Πλευρά α", "Πλευρά β", "Πλευρά γ"]
    elif shape == "Παραλληλόγραμμο":
        params = ["Βάση", "Ύψος"] if calc_type == "Εμβαδόν" else ["Βάση", "Πλευρά"]

    entries = {}
    for i, p in enumerate(params):
        ttk.Label(win, text=p + ":").grid(row=i+1, column=0, sticky="w", pady=3)
        e = ttk.Entry(win)
        e.grid(row=i+1, column=1, pady=3)
        entries[p] = e

    # Επιλογή μονάδας
    ttk.Label(win, text="Μονάδα:").grid(row=1, column=2, sticky="w")
    combo_unit = ttk.Combobox(win, values=[u[0] for u in units_table], width=5)
    combo_unit.grid(row=2, column=2, sticky="w")
    combo_unit.set("cm")

    # Υπολογισμός
    def calculate():
        try:
            unit = combo_unit.get()
            if unit not in unit_dict:
                messagebox.showerror("Σφάλμα", "Επιλέξτε έγκυρη μονάδα!")
                return
            # Λήψη τιμών και μετατροπή σε μέτρα
            vals = []
            for p in params:
                v = float(entries[p].get())
                v_m = v * unit_to_m[unit]
                vals.append(v_m)
            # Υπολογισμός
            if shape == "Κύκλος":
                result = area_circle(vals[0]) if calc_type == "Εμβαδόν" else perimeter_circle(vals[0])
            elif shape == "Τετράγωνο":
                result = area_square(vals[0]) if calc_type == "Εμβαδόν" else perimeter_square(vals[0])
            elif shape == "Ορθογώνιο":
                result = area_rectangle(vals[0], vals[1]) if calc_type == "Εμβαδόν" else perimeter_rectangle(vals[0], vals[1])
            elif shape == "Τρίγωνο":
                if calc_type == "Εμβαδόν":
                    result = area_triangle(vals[0], vals[1])
                else:
                    result = perimeter_triangle(vals[0], vals[1], vals[2])
            elif shape == "Παραλληλόγραμμο":
                if calc_type == "Εμβαδόν":
                    result = area_parallelogram(vals[0], vals[1])
                else:
                    result = perimeter_parallelogram(vals[0], vals[1])
            else:
                result = "N/A"
            label_result.config(text=f"{calc_type} (σε m): {result:.4f} m{'²' if calc_type == 'Εμβαδόν' else ''}")
            btn_convert.config(state="normal")
            win.result_value = result
        except Exception:
            messagebox.showerror("Σφάλμα", "Δώσε έγκυρους αριθμούς!")

    btn = ttk.Button(win, text="Υπολογισμός", command=calculate)
    btn.grid(row=len(params)+2, column=0, columnspan=2, pady=10)

    label_result = ttk.Label(win, text=f"{calc_type}: ")
    label_result.grid(row=len(params)+3, column=0, columnspan=3, pady=5)

    # Επιλογή μετατροπής μονάδας
    ttk.Label(win, text="Μετατροπή σε:").grid(row=len(params)+4, column=0, sticky="w")
    combo_convert = ttk.Combobox(win, values=[u[0] for u in units_table], width=5)
    combo_convert.grid(row=len(params)+4, column=1, sticky="w")
    combo_convert.set("cm")
    btn_convert = ttk.Button(win, text="Μετατροπή", state="disabled")
    btn_convert.grid(row=len(params)+4, column=2, sticky="w")

    def convert_area():
        try:
            to_unit = combo_convert.get()
            if to_unit not in unit_dict:
                messagebox.showerror("Σφάλμα", "Επιλέξτε έγκυρη μονάδα!")
                return
            result = getattr(win, "result_value", None)
            if result is None:
                messagebox.showerror("Σφάλμα", "Υπολόγισε πρώτα το αποτέλεσμα!")
                return
            # Αν είναι εμβαδόν, μετατροπή από m² στη νέα μονάδα
            if calc_type == "Εμβαδόν":
                factor = (1 / unit_to_m[to_unit]) ** 2
                converted = result * factor
                label_result.config(text=f"{calc_type}: {converted:.4f} {to_unit}²")
            else:
                factor = 1 / unit_to_m[to_unit]
                converted = result * factor
                label_result.config(text=f"{calc_type}: {converted:.4f} {to_unit}")
        except Exception:
            messagebox.showerror("Σφάλμα", "Σφάλμα μετατροπής!")

    btn_convert.config(command=convert_area)

# --- Lobby Window ---
root = tk.Tk()
root.title("Γεωμετρικός Υπολογιστής")
root.geometry("430x420")
root.configure(bg="#f0f4f8")

style = ttk.Style()
style.configure("TFrame", background="#f0f4f8")
style.configure("TLabel", background="#f0f4f8", font=("Segoe UI", 12))
style.configure("TButton", font=("Segoe UI", 12))

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True)

ttk.Label(main_frame, text="Διάλεξε τι θέλεις να υπολογίσεις:", font=("Segoe UI", 13, "bold")).pack(pady=10)

calc_type = tk.StringVar(value="Εμβαδόν")
ttk.Radiobutton(main_frame, text="Εμβαδόν", variable=calc_type, value="Εμβαδόν").pack(anchor="w")
ttk.Radiobutton(main_frame, text="Περίμετρος", variable=calc_type, value="Περίμετρος").pack(anchor="w")

ttk.Label(main_frame, text="Σχήμα:", font=("Segoe UI", 12, "bold")).pack(pady=(15, 5))

shapes = ["Κύκλος", "Τετράγωνο", "Ορθογώνιο", "Τρίγωνο", "Παραλληλόγραμμο"]

for s in shapes:
    ttk.Button(main_frame, text=s, width=20, command=lambda sh=s: show_shape_window(sh, calc_type.get())).pack(pady=2)

root.mainloop()