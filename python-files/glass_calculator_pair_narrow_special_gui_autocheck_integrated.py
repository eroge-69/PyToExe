#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glass Size Calculator - Desktop (Tkinter)

What's new (v2.4.0):
  • Narrow Stile Double Door "special center" option:
      - For double doors with Narrow Stile selected, enable checkbox:
        "Narrow double: center stile 2\" (3×2-1/8\", 1×2\")"
      - In this mode, total opening width deducts stiles as:
        outer_left (use Left input) + outer_right (use Right input) + 2.125" + 2.0"
        then subtract Frame_W_Ded and Center, divide by 2, and finally deduct hinge + glass extra.
      - Height calculation unchanged.

Existing features kept:
  • Door Type presets (Narrow / Medium / Wide)
  • Door Config (Single / Double with Center)
  • Custom rails (L/R/T/B), Glass Thickness (per-direction total), Hinge (width only),
    Frame (W×2, H×1), Saddle (H only), fractional inch inputs, inch display as 1/16" fraction
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv, math, re

APP_TITLE = "Glass Size Calculator (Pair Narrow Special + Presets + Options)"
VERSION = "2.4.0"

# ---------- Unit helpers ----------
def in_to_mm(inches: float) -> float: return inches * 25.4
def mm_to_in(mm: float) -> float: return mm / 25.4

def inch_fraction_string(value_in_inches: float, denom: int = 16) -> str:
    """Format inches as a mixed fraction rounded to nearest 1/denom inch."""
    sign = "-" if value_in_inches < 0 else ""
    x = abs(value_in_inches)
    whole = int(math.floor(x))
    frac = x - whole
    num = int(round(frac * denom))
    if num >= denom:
        whole += 1
        num = 0
    if num == 0:
        return f'{sign}{whole}"'
    g = math.gcd(num, denom)
    n = num // g
    d = denom // g
    return f'{sign}{n}/{d}"' if whole == 0 else f'{sign}{whole} {n}/{d}"'

# ---------- Parsing helpers ----------
_fraction_re = re.compile(r'^\s*([+-])?\s*(?:(\d+)\s+)?(\d+)\s*/\s*(\d+)\s*"?\s*$')
_int_or_float_re = re.compile(r'^\s*([+-])?\s*(\d+(?:\.\d+)?)\s*"?\s*$')

def parse_inch_value(s: str) -> float:
    """Parse inches input: integer/decimal, fraction, or mixed number (optionally with \")."""
    if s is None:
        raise ValueError("Empty input")
    txt = s.strip().replace("″", '"').replace("”", '"').replace("in", "").replace("IN", "").replace("In", "")
    if not txt:
        raise ValueError("Empty input")

    m = _fraction_re.match(txt)
    if m:
        sign, whole, num, den = m.groups()
        whole_val = int(whole) if whole else 0
        num = int(num); den = int(den)
        if den == 0:
            raise ValueError("Denominator cannot be 0")
        val = whole_val + num / den
        if sign == "-":
            val = -val
        return float(val)

    m2 = _int_or_float_re.match(txt)
    if m2:
        sign, val = m2.groups()
        x = float(val)
        if sign == "-":
            x = -x
        return x

    parts = txt.split()
    if len(parts) == 2:
        try:
            whole = float(parts[0])
            frac = parse_inch_value(parts[1])
            return whole + frac if whole >= 0 else whole - frac
        except Exception:
            pass

    raise ValueError(f"Invalid inch value: {s}")

def parse_value_by_unit(s: str, unit: str, name: str) -> float:
    if unit == "in":
        try:
            return parse_inch_value(s)
        except ValueError as e:
            raise ValueError(f"{name}: {e}")
    else:
        try:
            return float(s)
        except ValueError:
            raise ValueError(f"{name} must be a number (mm)")

# ---------- App ----------
class GlassCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE}  v{VERSION}")
        self.geometry("1280x900")
        self.resizable(True, True)
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.calc_frame = ttk.Frame(notebook)
        self.batch_frame = ttk.Frame(notebook)
        notebook.add(self.calc_frame, text="Calculator")
        notebook.add(self.batch_frame, text="Batch (CSV)")

        self.build_calc_tab(self.calc_frame)
        self.build_batch_tab(self.batch_frame)

    # ---------------- Calculator Tab ----------------
    def build_calc_tab(self, parent):
        input_frame = ttk.LabelFrame(parent, text="Inputs (Door Opening & Rails)")
        input_frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        output_frame = ttk.LabelFrame(parent, text="Results (Glass Cut Size)")
        output_frame.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        # Units
        ttk.Label(input_frame, text="Units").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.unit_var = tk.StringVar(value="in")
        unit_combo = ttk.Combobox(input_frame, textvariable=self.unit_var, state="readonly",
                                  values=["in", "mm"], width=8)
        unit_combo.grid(row=0, column=1, sticky="w", padx=6, pady=6)
        unit_combo.bind("<<ComboboxSelected>>", lambda e: self.update_results())

        # Door Type presets
        ttk.Label(input_frame, text="Door Type").grid(row=0, column=2, sticky="e", padx=6, pady=6)
        self.door_var = tk.StringVar(value='Medium Stile Door')
        door_combo = ttk.Combobox(
            input_frame,
            textvariable=self.door_var,
            state="readonly",
            values=['Narrow Stile Door', 'Medium Stile Door', 'Wide Stile Door', 'Custom'],
            width=28
        )
        door_combo.grid(row=0, column=3, sticky="w", padx=6, pady=6)
        door_combo.bind("<<ComboboxSelected>>", self.apply_preset)

        # Door configuration
        ttk.Label(input_frame, text="Door Config").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.config_var = tk.StringVar(value='Single Door')

        # --- Auto-check Narrow Stile Double Door special center stile ---
        def _auto_check_narrow_special(*args):
            try:
                if self.door_var.get() == "Narrow Stile Door" and "Double Door" in self.config_var.get():
                    self.narrow_special_var.set(True)
                else:
                    self.narrow_special_var.set(False)
            except Exception:
                pass

        self.door_var.trace_add('write', _auto_check_narrow_special)
        self.config_var.trace_add('write', _auto_check_narrow_special)
        # Initial trigger
        _auto_check_narrow_special()

        cfg_combo = ttk.Combobox(input_frame, textvariable=self.config_var, state="readonly",
                                 values=['Single Door', 'Double Door (Pair)'], width=28)
        cfg_combo.grid(row=1, column=1, sticky="w", padx=6, pady=6)
        cfg_combo.bind("<<ComboboxSelected>>", lambda e: self.update_results())

        # Center allowance
        ttk.Label(input_frame, text="Center allowance (Pair)").grid(row=1, column=2, sticky="e", padx=6, pady=6)
        self.center_var = tk.StringVar(value="0")
        ttk.Entry(input_frame, textvariable=self.center_var, width=14).grid(row=1, column=3, sticky="w", padx=6, pady=6)

        # Narrow pair special checkbox
        self.narrow_special_var = tk.BooleanVar(value=False)
        self.narrow_chk = ttk.Checkbutton(input_frame, text='Narrow double: center stile 2" (3×2-1/8", 1×2")',
                                          variable=self.narrow_special_var, command=self.update_results)
        self.narrow_chk.grid(row=2, column=0, columnspan=4, sticky="w", padx=6, pady=(0,6))

        # Glass Thickness (per-direction total)
        ttk.Label(input_frame, text="Glass Thickness").grid(row=3, column=0, sticky="w", padx=6, pady=6)
        self.glass_var = tk.StringVar(value='1/4" (7/16" total/dir)')
        glass_combo = ttk.Combobox(input_frame, textvariable=self.glass_var, state="readonly",
                                   values=['1/4" (7/16" total/dir)', '1" (1/2" total/dir)'], width=28)
        glass_combo.grid(row=3, column=1, sticky="w", padx=6, pady=6)
        glass_combo.bind("<<ComboboxSelected>>", lambda e: self.update_results())

        # Hinge (width only)
        ttk.Label(input_frame, text="Hinge Type").grid(row=3, column=2, sticky="e", padx=6, pady=6)
        self.hinge_var = tk.StringVar(value='Butt hinge (−3/16")')
        hinge_combo = ttk.Combobox(input_frame, textvariable=self.hinge_var, state="readonly",
                                   values=['None', 'Butt hinge (−3/16")', 'ROTON hinge (−7/16")'], width=28)
        hinge_combo.grid(row=3, column=3, sticky="w", padx=6, pady=6)
        hinge_combo.bind("<<ComboboxSelected>>", lambda e: self.update_results())

        # Frame option
        ttk.Label(input_frame, text="Frame").grid(row=4, column=0, sticky="w", padx=6, pady=6)
        self.frame_var = tk.StringVar(value='None')
        frame_combo = ttk.Combobox(input_frame, textvariable=self.frame_var, state="readonly",
                                   values=['None', '2" frame', '1 3/4" frame'], width=28)
        frame_combo.grid(row=4, column=1, sticky="w", padx=6, pady=6)
        frame_combo.bind("<<ComboboxSelected>>", lambda e: self.update_results())

        # Saddle option (height only)
        ttk.Label(input_frame, text="Saddle").grid(row=4, column=2, sticky="e", padx=6, pady=6)
        self.saddle_var = tk.StringVar(value='None')
        saddle_combo = ttk.Combobox(input_frame, textvariable=self.saddle_var, state="readonly",
                                    values=['None', '4" saddle (−3/4")', '5 1/2" high saddle (−7/8")'], width=28)
        saddle_combo.grid(row=4, column=3, sticky="w", padx=6, pady=6)
        saddle_combo.bind("<<ComboboxSelected>>", lambda e: self.update_results())

        # Opening size
        ttk.Label(input_frame, text="Opening Width (W)").grid(row=5, column=0, sticky="w", padx=6, pady=6)
        self.open_w_var = tk.StringVar(value="72")
        ttk.Entry(input_frame, textvariable=self.open_w_var, width=14).grid(row=5, column=1, sticky="w", padx=6, pady=6)
        ttk.Label(input_frame, text="Opening Height (H)").grid(row=5, column=2, sticky="e", padx=6, pady=6)
        self.open_h_var = tk.StringVar(value="84")
        ttk.Entry(input_frame, textvariable=self.open_h_var, width=14).grid(row=5, column=3, sticky="w", padx=6, pady=6)

        # Custom rails
        rails = ttk.LabelFrame(input_frame, text="Rails / Stiles (custom, per leaf piece)")
        rails.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=6, pady=6)
        for i in range(4):
            rails.columnconfigure(i, weight=1)
        ttk.Label(rails, text="Left stile").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        ttk.Label(rails, text="Right stile").grid(row=0, column=1, sticky="w", padx=6, pady=6)
        ttk.Label(rails, text="Top rail").grid(row=0, column=2, sticky="w", padx=6, pady=6)
        ttk.Label(rails, text="Bottom rail").grid(row=0, column=3, sticky="w", padx=6, pady=6)
        self.left_var = tk.StringVar(); self.right_var = tk.StringVar(); self.top_var = tk.StringVar(); self.bottom_var = tk.StringVar()
        ttk.Entry(rails, textvariable=self.left_var, width=14).grid(row=1, column=0, sticky="w", padx=6, pady=6)
        ttk.Entry(rails, textvariable=self.right_var, width=14).grid(row=1, column=1, sticky="w", padx=6, pady=6)
        ttk.Entry(rails, textvariable=self.top_var, width=14).grid(row=1, column=2, sticky="w", padx=6, pady=6)
        ttk.Entry(rails, textvariable=self.bottom_var, width=14).grid(row=1, column=3, sticky="w", padx=6, pady=6)

        # Hint
        hint = ('Tip（英寸模式）：输入支持分数；毫米模式请输入数字（允许小数）。\n'
                'Double + Narrow + Special 时：总宽先扣 Frame_W、Center、四根竖料（L、R、2-1/8、2），再平分，\n'
                '每扇再扣 Hinge 与 Glass Extra。高度计算不变。')
        ttk.Label(input_frame, text=hint, foreground="gray").grid(row=7, column=0, columnspan=4, sticky="w", padx=6, pady=(0,6))

        # Buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=8, column=0, columnspan=4, sticky="w", padx=6, pady=6)
        ttk.Button(btn_frame, text="Apply Door Defaults", command=self.apply_preset).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Calculate", command=self.update_results).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Reset", command=self.reset_inputs).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="About", command=self.show_about).pack(side="left", padx=4)

        # Results
        self.result_text = tk.Text(output_frame, height=34, width=90, wrap="word")
        self.result_text.pack(fill="both", expand=True, padx=6, pady=6)

        self.apply_preset()
        self.update_results()

    # --- option helpers ---
    def _glass_extra_total(self, unit: str) -> float:
        choice = self.glass_var.get()
        val_in = 7.0/16.0 if choice.startswith('1/4') else 1.0/2.0
        return val_in if unit == "in" else in_to_mm(val_in)

    def _hinge_allowance(self, unit: str) -> float:
        choice = self.hinge_var.get()
        if choice.startswith('Butt'):
            v_in = 3.0/16.0
        elif choice.startswith('ROTON'):
            v_in = 7.0/16.0
        else:
            v_in = 0.0
        return v_in if unit == "in" else in_to_mm(v_in)

    def _frame_deductions(self, unit: str):
        choice = self.frame_var.get()
        if choice.startswith('2"'):
            size_in = 2.0
        elif choice.startswith('1 3/4'):
            size_in = 1.75
        else:
            size_in = 0.0
        w_ded_in = 2.0 * size_in
        h_ded_in = 1.0 * size_in
        return (w_ded_in, h_ded_in) if unit == "in" else (in_to_mm(w_ded_in), in_to_mm(h_ded_in))

    def _saddle_deduction(self, unit: str) -> float:
        choice = self.saddle_var.get()
        if choice.startswith('4"'):
            v_in = 3.0/4.0
        elif choice.startswith('5 1/2"'):
            v_in = 7.0/8.0
        else:
            v_in = 0.0
        return v_in if unit == "in" else in_to_mm(v_in)

    # --- apply door type defaults ---
    def apply_preset(self, event=None):
        unit = self.unit_var.get()
        door = self.door_var.get()
        if door.startswith('Narrow'):
            L_in, R_in, T_in, B_in = 2.125, 2.125, 2.125, 4.0
        elif door.startswith('Wide'):
            L_in, R_in, T_in, B_in = 5.0, 5.0, 5.0, 7.5
        elif door.startswith('Medium'):
            L_in, R_in, T_in, B_in = 3.5, 3.5, 3.125, 5.0
        else:
            return
        if unit == "in":
            self.left_var.set(f"{L_in:.5f}"); self.right_var.set(f"{R_in:.5f}")
            self.top_var.set(f"{T_in:.5f}");  self.bottom_var.set(f"{B_in:.5f}")
        else:
            self.left_var.set(f"{in_to_mm(L_in):.3f}"); self.right_var.set(f"{in_to_mm(R_in):.3f}")
            self.top_var.set(f"{in_to_mm(T_in):.3f}");  self.bottom_var.set(f"{in_to_mm(B_in):.3f}")
        self.update_results()

    def parse_value(self, var, name):
        unit = self.unit_var.get()
        return parse_value_by_unit(var.get(), unit, name)

    # --- core compute ---
    def update_results(self):
        self.result_text.delete("1.0", "end")
        unit = self.unit_var.get()
        try:
            ow = self.parse_value(self.open_w_var, "Opening Width")
            oh = self.parse_value(self.open_h_var, "Opening Height")
            Ls = self.parse_value(self.left_var, "Left stile")
            Rs = self.parse_value(self.right_var, "Right stile")
            Tr = self.parse_value(self.top_var, "Top rail")
            Br = self.parse_value(self.bottom_var, "Bottom rail")
            center_allow = self.parse_value(self.center_var, "Center allowance")
        except ValueError as e:
            self.result_text.insert("end", f"⚠️ {e}\n")
            return

        glass_extra_total = self._glass_extra_total(unit)       # applies to W & H
        hinge_allow = self._hinge_allowance(unit)               # width only
        frame_w_ded, frame_h_ded = self._frame_deductions(unit)# W: 2×frame; H: 1×frame
        saddle_h_ded = self._saddle_deduction(unit)             # height only

        config = self.config_var.get()

        if config.startswith("Double"):
            narrow_special_active = (self.door_var.get().startswith("Narrow") and self.narrow_special_var.get())
            if narrow_special_active:
                # Sum all stiles across total width: outer L (input) + outer R (input) + center pair (2.125 + 2.0) inches
                if unit == "mm":
                    outer_L = Ls; outer_R = Rs
                    center_pair = in_to_mm(2.125 + 2.0)
                else:
                    outer_L = Ls; outer_R = Rs
                    center_pair = 2.125 + 2.0
                total_stiles_ded = outer_L + outer_R + center_pair
                effective_w_total = ow - frame_w_ded - center_allow - total_stiles_ded
                leaf_open_w = effective_w_total / 2.0
                gw_leaf = leaf_open_w - hinge_allow - glass_extra_total
                gh_leaf = oh - (Tr + Br) - glass_extra_total - frame_h_ded - saddle_h_ded
            else:
                # Standard pair logic
                effective_w_total = ow - frame_w_ded - center_allow
                leaf_open_w = effective_w_total / 2.0
                gw_leaf = leaf_open_w - (Ls + Rs) - hinge_allow - glass_extra_total
                gh_leaf = oh - (Tr + Br) - glass_extra_total - frame_h_ded - saddle_h_ded

            if gw_leaf <= 0 or gh_leaf <= 0:
                self.result_text.insert("end", "⚠️ Pair 结果为非正值，请检查输入（门料、活页、Glass、Frame、Saddle、Center 是否过大）。\n")
            if unit == "mm":
                gw_in = mm_to_in(gw_leaf); gh_in = mm_to_in(gh_leaf)
                self.print_results_pair_mm_first(ow, oh, Ls, Rs, Tr, Br, hinge_allow, glass_extra_total, frame_w_ded, frame_h_ded, saddle_h_ded, center_allow, self.narrow_special_var.get(), gw_leaf, gh_leaf, gw_in, gh_in)
            else:
                gw_mm = in_to_mm(gw_leaf); gh_mm = in_to_mm(gh_leaf)
                self.print_results_pair_in_first(ow, oh, Ls, Rs, Tr, Br, hinge_allow, glass_extra_total, frame_w_ded, frame_h_ded, saddle_h_ded, center_allow, self.narrow_special_var.get(), gw_leaf, gh_leaf, gw_mm, gh_mm)
        else:
            # Single
            gw = ow - (Ls + Rs) - hinge_allow - glass_extra_total - frame_w_ded
            gh = oh - (Tr + Br) - glass_extra_total - frame_h_ded - saddle_h_ded
            if gw <= 0 or gh <= 0:
                self.result_text.insert("end", "⚠️ 结果为非正值，请检查输入（门料、活页、Glass、Frame、Saddle 是否过大）。\n")
            if unit == "mm":
                gw_in = mm_to_in(gw); gh_in = mm_to_in(gh)
                self.print_results_mm_first(ow, oh, Ls, Rs, Tr, Br, hinge_allow, glass_extra_total, frame_w_ded, frame_h_ded, saddle_h_ded, gw, gh, gw_in, gh_in)
            else:
                gw_mm = in_to_mm(gw); gh_mm = in_to_mm(gh)
                self.print_results_in_first(ow, oh, Ls, Rs, Tr, Br, hinge_allow, glass_extra_total, frame_w_ded, frame_h_ded, saddle_h_ded, gw, gh, gw_mm, gh_mm)

    # --- output helpers ---
    def print_results_in_first(self, ow, oh, Ls, Rs, Tr, Br, hinge_allow, glass_extra_total, frame_w_ded, frame_h_ded, saddle_h_ded, gw_in, gh_in, gw_mm, gh_mm):
        self.result_text.insert("end", f"[Single Door]\n")
        self.result_text.insert("end", f"Opening (in):  W {inch_fraction_string(ow)}  |  H {inch_fraction_string(oh)}\n")
        self.result_text.insert("end", f"Rails (in):    L {inch_fraction_string(Ls)}, R {inch_fraction_string(Rs)}, T {inch_fraction_string(Tr)}, B {inch_fraction_string(Br)}\n")
        self.result_text.insert("end", f"Glass extra/dir: {inch_fraction_string(glass_extra_total)}   |  Hinge (W only): {inch_fraction_string(hinge_allow)}\n")
        self.result_text.insert("end", f"Frame:  W deduct {inch_fraction_string(frame_w_ded)},  H deduct {inch_fraction_string(frame_h_ded)}   |  Saddle (H only): {inch_fraction_string(saddle_h_ded)}\n")
        self.result_text.insert("end", "—\n")
        self.result_text.insert("end", f"Glass CUT SIZE (in):  W {inch_fraction_string(gw_in)}\n")
        self.result_text.insert("end", f"Glass CUT SIZE (in):  H {inch_fraction_string(gh_in)}\n")
        self.result_text.insert("end", f"Glass CUT SIZE (mm):  W {gw_mm:.1f} mm  |  H {gh_mm:.1f} mm\n")

    def print_results_mm_first(self, ow, oh, Ls, Rs, Tr, Br, hinge_allow, glass_extra_total, frame_w_ded, frame_h_ded, saddle_h_ded, gw_mm, gh_mm, gw_in, gh_in):
        self.result_text.insert("end", f"[Single Door]\n")
        self.result_text.insert("end", f"Opening (mm):  W {ow:.1f} mm  |  H {oh:.1f} mm\n")
        self.result_text.insert("end", f"Rails (mm):    L {Ls:.1f}, R {Rs:.1f}, T {Tr:.1f}, B {Br:.1f}\n")
        self.result_text.insert("end", f"Glass extra/dir: {glass_extra_total:.1f}   |  Hinge (W only): {hinge_allow:.1f}\n")
        self.result_text.insert("end", f"Frame:  W deduct {frame_w_ded:.1f},  H deduct {frame_h_ded:.1f}   |  Saddle (H only): {saddle_h_ded:.1f}\n")
        self.result_text.insert("end", "—\n")
        self.result_text.insert("end", f"Glass CUT SIZE (mm):  W {gw_mm:.1f} mm  |  H {gh_mm:.1f} mm\n")
        self.result_text.insert("end", f"Glass CUT SIZE (in):  W {inch_fraction_string(gw_in)}  |  H {inch_fraction_string(gh_in)}\n")

    def print_results_pair_in_first(self, ow, oh, Ls, Rs, Tr, Br, hinge_allow, glass_extra_total, frame_w_ded, frame_h_ded, saddle_h_ded, center_allow, narrow_special, gw_leaf_in, gh_leaf_in, gw_leaf_mm, gh_leaf_mm):
        tag = "Double Door (Pair)"
        if narrow_special: tag += " — Narrow center special"
        self.result_text.insert("end", f"[{tag}]\n")
        self.result_text.insert("end", f"Opening (in):  W {inch_fraction_string(ow)}  |  H {inch_fraction_string(oh)}  |  Center {inch_fraction_string(center_allow)}\n")
        self.result_text.insert("end", f"Rails/leaf (in): L {inch_fraction_string(Ls)}, R {inch_fraction_string(Rs)}, T {inch_fraction_string(Tr)}, B {inch_fraction_string(Br)}\n")
        if narrow_special:
            self.result_text.insert("end", f"Special: center stile 2\" & 2-1/8\" (total), outer stiles use L/R inputs\n")
        self.result_text.insert("end", f"Glass extra/dir: {inch_fraction_string(glass_extra_total)}   |  Hinge/leaf (W): {inch_fraction_string(hinge_allow)}\n")
        self.result_text.insert("end", f"Frame (total):  W deduct {inch_fraction_string(frame_w_ded)},  H deduct {inch_fraction_string(frame_h_ded)}   |  Saddle (H): {inch_fraction_string(saddle_h_ded)}\n")
        self.result_text.insert("end", "—\n")
        self.result_text.insert("end", f"Glass CUT SIZE per leaf (in):  W {inch_fraction_string(gw_leaf_in)}  |  H {inch_fraction_string(gh_leaf_in)}   (×2 pieces)\n")
        self.result_text.insert("end", f"Glass CUT SIZE per leaf (mm):  W {gw_leaf_mm:.1f} mm  |  H {gh_leaf_mm:.1f} mm\n")

    def print_results_pair_mm_first(self, ow, oh, Ls, Rs, Tr, Br, hinge_allow, glass_extra_total, frame_w_ded, frame_h_ded, saddle_h_ded, center_allow, narrow_special, gw_leaf_mm, gh_leaf_mm, gw_leaf_in, gh_leaf_in):
        tag = "Double Door (Pair)"
        if narrow_special: tag += " — Narrow center special"
        self.result_text.insert("end", f"[{tag}]\n")
        self.result_text.insert("end", f"Opening (mm):  W {ow:.1f} mm  |  H {oh:.1f} mm  |  Center {center_allow:.1f} mm\n")
        self.result_text.insert("end", f"Rails/leaf (mm): L {Ls:.1f}, R {Rs:.1f}, T {Tr:.1f}, B {Br:.1f}\n")
        if narrow_special:
            self.result_text.insert("end", f"Special: center stile 2\" & 2-1/8\" (total), outer stiles use L/R inputs\n")
        self.result_text.insert("end", f"Glass extra/dir: {glass_extra_total:.1f}   |  Hinge/leaf (W): {hinge_allow:.1f}\n")
        self.result_text.insert("end", f"Frame (total):  W deduct {frame_w_ded:.1f},  H deduct {frame_h_ded:.1f}   |  Saddle (H): {saddle_h_ded:.1f}\n")
        self.result_text.insert("end", "—\n")
        self.result_text.insert("end", f"Glass CUT SIZE per leaf (mm):  W {gw_leaf_mm:.1f} mm  |  H {gh_leaf_mm:.1f} mm   (×2 pieces)\n")
        self.result_text.insert("end", f"Glass CUT SIZE per leaf (in):  W {inch_fraction_string(gw_leaf_in)}  |  H {inch_fraction_string(gh_leaf_in)}\n")

    def reset_inputs(self):
        self.unit_var.set("in")
        self.door_var.set('Medium Stile Door')
        self.config_var.set('Single Door')
        self.center_var.set("0")
        self.narrow_special_var.set(False)
        self.glass_var.set('1/4" (7/16" total/dir)')
        self.hinge_var.set('Butt hinge (−3/16")')
        self.frame_var.set('None')
        self.saddle_var.set('None')
        self.open_w_var.set("72")
        self.open_h_var.set("84")
        self.apply_preset()
        self.update_results()

    def show_about(self):
        messagebox.showinfo(
            "About",
            f"{APP_TITLE} v{VERSION}\n\n"
            "Double (Pair) Narrow Special:\n"
            "  • Total W deducts outer stiles L/R + center pair (2-1/8\" & 2\") + Frame_W_Ded + Center, then /2.\n"
            "  • Per leaf deduct: Hinge + GlassExtraTotal only (no L/R again).\n"
            "  • Height per leaf same as single.\n\n"
            "Door Type presets:\n"
            "  • Narrow: L/R = 2-1/8\", Top = 2-1/8\", Bottom = 4\"\n"
            "  • Medium: L/R = 3-1/2\", Top = 3-1/8\", Bottom = 5\"\n"
            "  • Wide:   L/R = 5\",     Top = 5\",     Bottom = 7-1/2\"\n\n"
            "Other options: Glass thickness (1/4→7/16, 1→1/2), Hinge (W only), Frame (W×2,H×1), Saddle (H only).\n"
            "Inputs: inch supports fractions; display: inch as nearest 1/16\" fraction; mm 1-decimal."
        )

    # ---------------- Batch Tab ----------------
    def build_batch_tab(self, parent):
        info = tk.Label(parent, text=(
            "CSV headers:\n"
            "opening_width,opening_height,unit,left_stile,right_stile,top_rail,bottom_rail,glass_thickness,hinge_type,frame,saddle,door_type,door_config,center,narrow_special\n"
            "• unit = in：英寸可分数；door_type: narrow|medium|wide|custom；door_config: single|double；center: 分数；narrow_special: true/false\n"
            "• unit = mm：数值小数；door_config: single|double；center: 数值；narrow_special: true/false"
        ), justify="left")
        info.pack(anchor="w", padx=8, pady=8)

        btns = ttk.Frame(parent)
        btns.pack(anchor="w", padx=8, pady=8)
        ttk.Button(btns, text="Import CSV & Compute → Export CSV", command=self.process_csv).pack(side="left", padx=4)

        self.batch_status = tk.Label(parent, text="", fg="gray")
        self.batch_status.pack(anchor="w", padx=8, pady=8)

    def _parse_door_csv_defaults(self, door: str):
        d = (door or "").strip().lower()
        if d.startswith("narrow"): return 2.125, 2.125, 2.125, 4.0
        if d.startswith("wide"):   return 5.0, 5.0, 5.0, 7.5
        if d.startswith("medium"): return 3.5, 3.5, 3.125, 5.0
        return None

    def _parse_glass_thickness_csv(self, val: str, unit: str) -> float:
        txt = (val or "").strip().lower().replace('"','')
        if unit == "in":
            if txt in ("1/4", "0.25", ".25"): v_in = 7.0/16.0
            elif txt in ("1", "1.0"):         v_in = 1.0/2.0
            else: raise ValueError("glass_thickness must be 1/4 or 1 (in)")
            return v_in
        else:
            if txt in ("7/16", "0.4375", ".4375"): return in_to_mm(7.0/16.0)
            elif txt in ("1/2", "0.5", ".5"):      return in_to_mm(1.0/2.0)
            else: raise ValueError("glass_thickness must be 7/16 or 1/2 (mm)")

    def _parse_hinge_csv(self, val: str, unit: str) -> float:
        txt = (val or "").strip().lower()
        if txt in ("none", "", "0"): v_in = 0.0
        elif txt in ("butt", "butt hinge", "b"): v_in = 3.0/16.0
        elif txt in ("roton", "roton hinge", "r"): v_in = 7.0/16.0
        else: raise ValueError("hinge_type must be none/butt/roton")
        return v_in if unit == "in" else in_to_mm(v_in)

    def _parse_frame_csv(self, val: str, unit: str):
        txt = (val or "").strip().lower()
        if txt in ("none", "", "0"): size_in = 0.0
        elif txt in ("2", "2.0", '2"'): size_in = 2.0
        elif txt in ("1-3/4", "1.75", "1 3/4"): size_in = 1.75
        else: raise ValueError("frame must be none|2|1-3/4")
        w_ded_in = 2.0 * size_in
        h_ded_in = 1.0 * size_in
        return (w_ded_in, h_ded_in) if unit == "in" else (in_to_mm(w_ded_in), in_to_mm(h_ded_in))

    def _parse_saddle_csv(self, val: str, unit: str) -> float:
        txt = (val or "").strip().lower()
        if txt in ("none", "", "0"): v_in = 0.0
        elif txt in ("4", '4"'):     v_in = 3.0/4.0
        elif txt in ("5-1/2", "5.5", '5 1/2'): v_in = 7.0/8.0
        else: raise ValueError("saddle must be none|4|5-1/2")
        return v_in if unit == "in" else in_to_mm(v_in)

    def process_csv(self):
        in_path = filedialog.askopenfilename(
            title="Select input CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not in_path:
            return

        rows = []
        try:
            with open(in_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                required = ["opening_width","opening_height","unit","left_stile","right_stile","top_rail","bottom_rail","glass_thickness","hinge_type","frame","saddle","door_type","door_config","center","narrow_special"]
                for r in required:
                    if r not in reader.fieldnames:
                        raise ValueError(f"Missing required column: {r}")
                for row in reader:
                    rows.append(row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV:\n{e}")
            return

        out_rows = []
        for row in rows:
            try:
                unit = row["unit"].strip().lower()
                door_defaults = self._parse_door_csv_defaults(row.get("door_type",""))
                def get_val(cell, fallback_in=None):
                    v = (cell or "").strip()
                    if v == "" and fallback_in is not None:
                        return fallback_in if unit == "in" else in_to_mm(fallback_in)
                    return parse_inch_value(v) if unit == "in" else float(v)

                if unit == "in":
                    ow = parse_inch_value(row["opening_width"]); oh = parse_inch_value(row["opening_height"])
                    Ls = get_val(row["left_stile"], door_defaults[0] if door_defaults else None)
                    Rs = get_val(row["right_stile"], door_defaults[1] if door_defaults else None)
                    Tr = get_val(row["top_rail"],   door_defaults[2] if door_defaults else None)
                    Br = get_val(row["bottom_rail"],door_defaults[3] if door_defaults else None)
                    glass_extra_total = self._parse_glass_thickness_csv(row["glass_thickness"], "in")
                    hinge_allow = self._parse_hinge_csv(row["hinge_type"], "in")
                    frame_w_ded, frame_h_ded = self._parse_frame_csv(row["frame"], "in")
                    saddle_h_ded = self._parse_saddle_csv(row["saddle"], "in")
                    center_allow = get_val(row.get("center","0"), None)
                else:
                    ow = float(row["opening_width"]); oh = float(row["opening_height"])
                    Ls = get_val(row["left_stile"], door_defaults[0] if door_defaults else None)
                    Rs = get_val(row["right_stile"], door_defaults[1] if door_defaults else None)
                    Tr = get_val(row["top_rail"],   door_defaults[2] if door_defaults else None)
                    Br = get_val(row["bottom_rail"],door_defaults[3] if door_defaults else None)
                    glass_extra_total = self._parse_glass_thickness_csv(row["glass_thickness"], "mm")
                    hinge_allow = self._parse_hinge_csv(row["hinge_type"], "mm")
                    frame_w_ded, frame_h_ded = self._parse_frame_csv(row["frame"], "mm")
                    saddle_h_ded = self._parse_saddle_csv(row["saddle"], "mm")
                    center_allow = get_val(row.get("center","0"), None)

                narrow_special = (row.get("narrow_special","false").strip().lower() in ("1","true","yes","y"))
                door_cfg = (row.get("door_config","single") or "single").strip().lower()

                if door_cfg.startswith("double"):
                    if narrow_special and (row.get("door_type","").lower().startswith("narrow")):
                        center_pair = (2.125 + 2.0) if unit == "in" else in_to_mm(2.125 + 2.0)
                        total_stiles_ded = Ls + Rs + center_pair
                        effective_w_total = ow - frame_w_ded - center_allow - total_stiles_ded
                        leaf_open_w = effective_w_total / 2.0
                        gw = leaf_open_w - hinge_allow - glass_extra_total
                    else:
                        effective_w_total = ow - frame_w_ded - center_allow
                        leaf_open_w = effective_w_total / 2.0
                        gw = leaf_open_w - (Ls + Rs) - hinge_allow - glass_extra_total
                    gh = oh - (Tr + Br) - glass_extra_total - frame_h_ded - saddle_h_ded

                    if unit == "in":
                        out_rows.append({
                            **{k: row.get(k,"") for k in ["opening_width","opening_height","unit","glass_thickness","hinge_type","frame","saddle","door_type","door_config","center","narrow_special"]},
                            "left_stile": inch_fraction_string(Ls),
                            "right_stile": inch_fraction_string(Rs),
                            "top_rail": inch_fraction_string(Tr),
                            "bottom_rail": inch_fraction_string(Br),
                            "leaf_glass_width_in": inch_fraction_string(gw),
                            "leaf_glass_height_in": inch_fraction_string(gh),
                            "leaf_glass_width_mm": f"{in_to_mm(gw):.1f}",
                            "leaf_glass_height_mm": f"{in_to_mm(gh):.1f}",
                            "pieces": "2"
                        })
                    else:
                        out_rows.append({
                            **{k: row.get(k,"") for k in ["opening_width","opening_height","unit","glass_thickness","hinge_type","frame","saddle","door_type","door_config","center","narrow_special"]},
                            "left_stile": f"{Ls:.1f}",
                            "right_stile": f"{Rs:.1f}",
                            "top_rail": f"{Tr:.1f}",
                            "bottom_rail": f"{Br:.1f}",
                            "leaf_glass_width_mm": f"{gw:.1f}",
                            "leaf_glass_height_mm": f"{gh:.1f}",
                            "leaf_glass_width_in": inch_fraction_string(mm_to_in(gw)),
                            "leaf_glass_height_in": inch_fraction_string(mm_to_in(gh)),
                            "pieces": "2"
                        })
                else:
                    gw = ow - (Ls + Rs) - hinge_allow - glass_extra_total - frame_w_ded
                    gh = oh - (Tr + Br) - glass_extra_total - frame_h_ded - saddle_h_ded
                    if unit == "in":
                        out_rows.append({
                            **{k: row.get(k,"") for k in ["opening_width","opening_height","unit","glass_thickness","hinge_type","frame","saddle","door_type","door_config","center","narrow_special"]},
                            "left_stile": inch_fraction_string(Ls),
                            "right_stile": inch_fraction_string(Rs),
                            "top_rail": inch_fraction_string(Tr),
                            "bottom_rail": inch_fraction_string(Br),
                            "glass_width_in": inch_fraction_string(gw),
                            "glass_height_in": inch_fraction_string(gh),
                            "glass_width_mm": f"{in_to_mm(gw):.1f}",
                            "glass_height_mm": f"{in_to_mm(gh):.1f}",
                            "pieces": "1"
                        })
                    else:
                        out_rows.append({
                            **{k: row.get(k,"") for k in ["opening_width","opening_height","unit","glass_thickness","hinge_type","frame","saddle","door_type","door_config","center","narrow_special"]},
                            "left_stile": f"{Ls:.1f}",
                            "right_stile": f"{Rs:.1f}",
                            "top_rail": f"{Tr:.1f}",
                            "bottom_rail": f"{Br:.1f}",
                            "glass_width_mm": f"{gw:.1f}",
                            "glass_height_mm": f"{gh:.1f}",
                            "glass_width_in": inch_fraction_string(mm_to_in(gw)),
                            "glass_height_in": inch_fraction_string(mm_to_in(gh)),
                            "pieces": "1"
                        })
            except Exception as e:
                row_out = {"error": f"Row failed: {e}"}
                row_out.update(row)
                out_rows.append(row_out)

        out_path = filedialog.asksaveasfilename(
            title="Save output CSV as",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="glass_cut_sizes.csv"
        )
        if not out_path:
            return

        try:
            if out_rows:
                fieldnames = list(out_rows[0].keys())
            else:
                fieldnames = ["opening_width","opening_height","unit","left_stile","right_stile","top_rail","bottom_rail","glass_thickness","hinge_type","frame","saddle","door_type","door_config","center","narrow_special","glass_width_in","glass_height_in","glass_width_mm","glass_height_mm","leaf_glass_width_in","leaf_glass_height_in","leaf_glass_width_mm","leaf_glass_height_mm","pieces"]
            with open(out_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in out_rows:
                    writer.writerow(r)
            self.batch_status.config(text=f"Exported: {out_path}")
            messagebox.showinfo("Done", f"Exported results to:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write CSV:\n{e}")

if __name__ == "__main__":
    app = GlassCalculatorApp()
    app.mainloop()
