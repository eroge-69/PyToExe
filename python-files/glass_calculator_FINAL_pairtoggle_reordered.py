#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glass Size Calculator - FINAL (with Pair toggle)
Features:
  • Units: in/mm (inch input accepts fractions; inch output rounds to nearest 1/16")
  • Door Types: Narrow / Medium / Wide / Custom (presets for stiles/rails)
  • Door Config: Single / Double (Pair)
  • Pair leaf mode (only visible for Double):
      - Equal (auto): classic split
      - Unequal (specify): input left/right leaf net openings; auto-update Opening Width
  • Narrow Pair Specials:
      - Auto-check "Narrow special" when Door=Narrow & Config=Double
      - Equal (auto) + Narrow special: total stiles across width = L + R + 2-1/8 + 2
      - Unequal (specify) + Narrow: larger leaf uses center stile = 2.0", smaller uses 2-1/8"
  • Glass Thickness option (per-direction total deduction): 1/4"→7/16", 1"→1/2"
  • Hinge (width only): None / Butt −3/16" / ROTON −7/16"
  • Frame: width deduct = 2×frame; height deduct = 1×frame (2" / 1-3/4")
  • Saddle (height only): 4" −3/4" ; 5-1/2" high −7/8"

Robustness:
  • Top-level exception hook shows a message box with details and writes error_log.txt next to script
"""
import tkinter as tk
from tkinter import ttk, messagebox
import math, re, sys, traceback, os

APP_TITLE = "Glass Size Calculator (Final)"
VERSION = "2.7.0"

# ---------- Error hook ----------
def _excepthook(exc_type, exc, tb):
    try:
        msg = "".join(traceback.format_exception(exc_type, exc, tb))
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_log.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(msg)
        try:
            messagebox.showerror("Application Error", f"An unexpected error occurred.\nA log was saved to:\n{path}\n\n{exc}")
        except Exception:
            pass
    finally:
        sys.__excepthook__(exc_type, exc, tb)
sys.excepthook = _excepthook

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
        main = ttk.Notebook(self)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        self.calc_frame = ttk.Frame(main)
        main.add(self.calc_frame, text="Calculator")

        self.build_calc_tab(self.calc_frame)

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
        ttk.Label(input_frame, text="Door Type").grid(row=1, column=2, sticky="e", padx=6, pady=6)
        self.door_var = tk.StringVar(value='Medium Stile Door')
        door_combo = ttk.Combobox(
            input_frame,
            textvariable=self.door_var,
            state="readonly",
            values=['Narrow Stile Door', 'Medium Stile Door', 'Wide Stile Door', 'Custom'],
            width=28
        )
        door_combo.grid(row=1, column=3, sticky="w", padx=6, pady=6)
        door_combo.bind("<<ComboboxSelected>>", self.apply_preset)

        # Door configuration
        ttk.Label(input_frame, text="Door Config").grid(row=4, column=0, sticky="w", padx=6, pady=6)
        self.config_var = tk.StringVar(value='Single Door')
        cfg_combo = ttk.Combobox(input_frame, textvariable=self.config_var, state="readonly",
                                 values=['Single Door', 'Double Door (Pair)'], width=28)
        cfg_combo.grid(row=4, column=1, sticky="w", padx=6, pady=6)
        cfg_combo.bind("<<ComboboxSelected>>", lambda e: (self._auto_check_narrow_special(), self._toggle_pair_controls(), self.update_results()))
        self.config_var.trace_add("write", lambda *a: (self._auto_check_narrow_special(), self._toggle_pair_controls(), self.update_results()))

        # Center allowance
        ttk.Label(input_frame, text="Center allowance (Pair)").grid(row=4, column=2, sticky="e", padx=6, pady=6)
        self.center_var = tk.StringVar(value="0")
        ttk.Entry(input_frame, textvariable=self.center_var, width=14).grid(row=4, column=3, sticky="w", padx=6, pady=6)

        # Narrow pair special checkbox (auto-checked when Door=Narrow & Config=Double)
        self.narrow_special_var = tk.BooleanVar(value=False)
        self.narrow_chk = ttk.Checkbutton(input_frame, text='Narrow double: center stile 2" (3×2-1/8", 1×2")',
                                          variable=self.narrow_special_var, command=self.update_results)
        self.narrow_chk.grid(row=5, column=0, columnspan=4, sticky="w", padx=6, pady=(0,6))

        # Pair leaf mode & manual leaf openings (for Double Door Unequal)
        self.lbl_pair_mode = ttk.Label(input_frame, text="Pair leaf mode")
        self.pair_mode_var = tk.StringVar(value='Equal (auto)')
        self.pair_mode_combo = ttk.Combobox(input_frame, textvariable=self.pair_mode_var, state="readonly",
                                            values=['Equal (auto)', 'Unequal (specify)'], width=28)
        self.pair_mode_combo.grid(row=6, column=1, sticky="w", padx=6, pady=6)
        self.lbl_pair_mode.grid(row=6, column=0, sticky="w", padx=6, pady=6)
        self.pair_mode_combo.bind("<<ComboboxSelected>>", lambda e: (self._toggle_unequal_fields(), self.update_results()))

        self.lbl_leaf_left = ttk.Label(input_frame, text="Left leaf opening (Unequal)")
        self.leaf_left_open_var = tk.StringVar()
        self.ent_leaf_left = ttk.Entry(input_frame, textvariable=self.leaf_left_open_var, width=14)

        self.lbl_leaf_right = ttk.Label(input_frame, text="Right leaf opening (Unequal)")
        self.leaf_right_open_var = tk.StringVar()
        self.ent_leaf_right = ttk.Entry(input_frame, textvariable=self.leaf_right_open_var, width=14)

        # Place (toggle will show/hide as needed)
        self.lbl_leaf_left.grid(row=6, column=2, sticky="e", padx=6, pady=6)
        self.ent_leaf_left.grid(row=6, column=3, sticky="w", padx=6, pady=6)
        self.lbl_leaf_right.grid(row=7, column=2, sticky="e", padx=6, pady=6)
        self.ent_leaf_right.grid(row=7, column=3, sticky="w", padx=6, pady=6)

        # Trace leaf inputs to re-calc Opening Width when Unequal
        self.leaf_left_open_var.trace_add('write', lambda *a: self._recalc_opening_from_leafs())
        self.leaf_right_open_var.trace_add('write', lambda *a: self._recalc_opening_from_leafs())

        # Glass Thickness (per-direction total)
        ttk.Label(input_frame, text="Glass Thickness").grid(row=3, column=0, sticky="w", padx=6, pady=6)
        self.glass_var = tk.StringVar(value='1/4" (7/16" total/dir)')
        glass_combo = ttk.Combobox(input_frame, textvariable=self.glass_var, state="readonly",
                                   values=['1/4" (7/16" total/dir)', '1" (1/2" total/dir)'], width=28)
        glass_combo.grid(row=3, column=1, sticky="w", padx=6, pady=6)
        glass_combo.bind("<<ComboboxSelected>>", lambda e: self.update_results())

        # Hinge (width only)
        ttk.Label(input_frame, text="Hinge Type").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        self.hinge_var = tk.StringVar(value='Butt hinge (−3/16")')
        hinge_combo = ttk.Combobox(input_frame, textvariable=self.hinge_var, state="readonly",
                                   values=['None', 'Butt hinge (−3/16")', 'ROTON hinge (−7/16")'], width=28)
        hinge_combo.grid(row=2, column=1, sticky="w", padx=6, pady=6)
        hinge_combo.bind("<<ComboboxSelected>>", lambda e: self.update_results())

        # Frame option
        ttk.Label(input_frame, text="Frame").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.frame_var = tk.StringVar(value='None')
        frame_combo = ttk.Combobox(input_frame, textvariable=self.frame_var, state="readonly",
                                   values=['None', '2" frame', '1 3/4" frame'], width=28)
        frame_combo.grid(row=1, column=1, sticky="w", padx=6, pady=6)
        frame_combo.bind("<<ComboboxSelected>>", lambda e: self.update_results())

        # Saddle option (height only)
        ttk.Label(input_frame, text="Saddle").grid(row=2, column=2, sticky="e", padx=6, pady=6)
        self.saddle_var = tk.StringVar(value='None')
        saddle_combo = ttk.Combobox(input_frame, textvariable=self.saddle_var, state="readonly",
                                    values=['None', '4" saddle (−3/4")', '5 1/2" high saddle (−7/8")'], width=28)
        saddle_combo.grid(row=2, column=3, sticky="w", padx=6, pady=6)
        saddle_combo.bind("<<ComboboxSelected>>", lambda e: self.update_results())

        # Opening size
        ttk.Label(input_frame, text="Opening Width (W)").grid(row=8, column=0, sticky="w", padx=6, pady=6)
        self.open_w_var = tk.StringVar(value="72")
        ttk.Entry(input_frame, textvariable=self.open_w_var, width=14).grid(row=8, column=1, sticky="w", padx=6, pady=6)
        ttk.Label(input_frame, text="Opening Height (H)").grid(row=8, column=2, sticky="e", padx=6, pady=6)
        self.open_h_var = tk.StringVar(value="84")
        ttk.Entry(input_frame, textvariable=self.open_h_var, width=14).grid(row=8, column=3, sticky="w", padx=6, pady=6)

        # Custom rails
        rails = ttk.LabelFrame(input_frame, text="Rails / Stiles (custom, per leaf piece)")
        rails.grid(row=9, column=0, columnspan=4, sticky="nsew", padx=6, pady=6)
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
                'Equal + Narrow special：总宽先扣 Frame_W、Center、四根竖料（L、R、2-1/8、2），再平分；每扇扣 Hinge & GlassExtra。\n'
                'Unequal（仅 Double 时显示）：填左右净开口；会自动回填 Opening Width = 左 + 右 + Frame_W + Center。高度计算一致。')
        ttk.Label(input_frame, text=hint, foreground="gray").grid(row=10, column=0, columnspan=4, sticky="w", padx=6, pady=(0,6))

        # Buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=11, column=0, columnspan=4, sticky="w", padx=6, pady=6)
        ttk.Button(btn_frame, text="Apply Door Defaults", command=self.apply_preset).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Calculate", command=self.update_results).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Reset", command=self.reset_inputs).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="About", command=self.show_about).pack(side="left", padx=4)

        # Results
        self.result_text = tk.Text(output_frame, height=34, width=90, wrap="word")
        self.result_text.pack(fill="both", expand=True, padx=6, pady=6)

        self.apply_preset()
        self._auto_check_narrow_special()
        self._toggle_pair_controls()
        self._toggle_unequal_fields()
        self.update_results()

    # --- option helpers ---
    def _auto_check_narrow_special(self, *args):
        try:
            if self.door_var.get() == "Narrow Stile Door" and "Double Door" in self.config_var.get():
                self.narrow_special_var.set(True)
            else:
                self.narrow_special_var.set(False)
        except Exception:
            pass

    def _toggle_pair_controls(self):
        """Show Pair leaf mode row only when Door Config = Double; also sync unequal fields visibility."""
        try:
            is_double = self.config_var.get().startswith("Double")
            if is_double:
                self.lbl_pair_mode.grid(row=6, column=0, sticky="w", padx=6, pady=6)
                self.pair_mode_combo.grid(row=6, column=1, sticky="w", padx=6, pady=6)
                self._toggle_unequal_fields()
            else:
                self.lbl_pair_mode.grid_remove()
                self.pair_mode_combo.grid_remove()
                self.lbl_leaf_left.grid_remove()
                self.ent_leaf_left.grid_remove()
                self.lbl_leaf_right.grid_remove()
                self.ent_leaf_right.grid_remove()
        except Exception:
            pass

    def _toggle_unequal_fields(self):
        mode = self.pair_mode_var.get()
        if not self.config_var.get().startswith("Double"):
            # Always hide if not Double
            self.lbl_leaf_left.grid_remove()
            self.ent_leaf_left.grid_remove()
            self.lbl_leaf_right.grid_remove()
            self.ent_leaf_right.grid_remove()
            return
        if mode.startswith("Unequal"):
            self.lbl_leaf_left.grid(row=6, column=2, sticky="e", padx=6, pady=6)
            self.ent_leaf_left.grid(row=6, column=3, sticky="w", padx=6, pady=6)
            self.lbl_leaf_right.grid(row=7, column=2, sticky="e", padx=6, pady=6)
            self.ent_leaf_right.grid(row=7, column=3, sticky="w", padx=6, pady=6)
        else:
            self.lbl_leaf_left.grid_remove()
            self.ent_leaf_left.grid_remove()
            self.lbl_leaf_right.grid_remove()
            self.ent_leaf_right.grid_remove()

    def _recalc_opening_from_leafs(self):
        try:
            if not (self.config_var.get().startswith("Double") and self.pair_mode_var.get().startswith("Unequal")):
                return
            unit = self.unit_var.get()
            left_txt = self.leaf_left_open_var.get().strip()
            right_txt = self.leaf_right_open_var.get().strip()
            if not left_txt or not right_txt:
                return
            left_open = parse_value_by_unit(left_txt, unit, "Left leaf opening")
            right_open = parse_value_by_unit(right_txt, unit, "Right leaf opening")
            frame_w_ded, _ = self._frame_deductions(unit)
            center = parse_value_by_unit(self.center_var.get(), unit, "Center allowance")
            open_w = left_open + right_open + frame_w_ded + center
            if unit == "in":
                self.open_w_var.set(inch_fraction_string(open_w).replace('"',''))
            else:
                self.open_w_var.set(f"{open_w:.1f}")
            self.update_results()
        except Exception:
            pass

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
            L_in, R_in, T_in, B_in = 3.5, 3.125, 3.5, 5.0  # corrected top/bottom if needed
            # If prior code expected Medium top=3-1/8", bottom=5": swap as you need
            L_in, R_in, T_in, B_in = 3.5, 3.5, 3.125, 5.0
        else:
            return
        if unit == "in":
            self.left_var.set(f"{L_in:.5f}"); self.right_var.set(f"{R_in:.5f}")
            self.top_var.set(f"{T_in:.5f}");  self.bottom_var.set(f"{B_in:.5f}")
        else:
            self.left_var.set(f"{in_to_mm(L_in):.3f}"); self.right_var.set(f"{in_to_mm(R_in):.3f}")
            self.top_var.set(f"{in_to_mm(T_in):.3f}");  self.bottom_var.set(f"{in_to_mm(B_in):.3f}")
        self._auto_check_narrow_special()
        self._toggle_pair_controls()
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
            # Unequal mode first (early return)
            if self.pair_mode_var.get().startswith("Unequal"):
                effective_w_total = ow - frame_w_ded - center_allow
                def _parse_leaf(txt, name):
                    txt = (txt or "").strip()
                    if not txt: return None
                    try: return parse_value_by_unit(txt, unit, name)
                    except Exception: return None
                left_open = _parse_leaf(self.leaf_left_open_var.get(), "Left leaf opening")
                right_open = _parse_leaf(self.leaf_right_open_var.get(), "Right leaf opening")

                if left_open is None and right_open is None:
                    left_open = right_open = effective_w_total / 2.0
                elif left_open is None:
                    left_open = max(effective_w_total - right_open, 0)
                elif right_open is None:
                    right_open = max(effective_w_total - left_open, 0)

                total_in = left_open + right_open
                if total_in > 0 and abs(total_in - effective_w_total) > (0.0001 if unit == "in" else 0.01):
                    scale = effective_w_total / total_in
                    left_open *= scale; right_open *= scale

                if self.door_var.get().startswith("Narrow"):
                    left_is_larger = left_open >= right_open
                    if unit == "mm":
                        center_left = in_to_mm(2.0 if left_is_larger else 2.125)
                        center_right = in_to_mm(2.0 if not left_is_larger else 2.125)
                    else:
                        center_left = 2.0 if left_is_larger else 2.125
                        center_right = 2.0 if not left_is_larger else 2.125
                    gw_left = left_open - (Ls + center_left) - hinge_allow - glass_extra_total
                    gw_right = right_open - (Rs + center_right) - hinge_allow - glass_extra_total
                else:
                    gw_left = left_open - (Ls + Rs) - hinge_allow - glass_extra_total
                    gw_right = right_open - (Ls + Rs) - hinge_allow - glass_extra_total

                gh_left = gh_right = oh - (Tr + Br) - glass_extra_total - frame_h_ded - saddle_h_ded

                if gw_left <= 0 or gw_right <= 0 or gh_left <= 0:
                    self.result_text.insert("end", "⚠️ Pair (Unequal) 结果为非正值，请检查输入（扇宽、门料、活页、Glass、Frame、Saddle、Center）。\n")

                if unit == "mm":
                    self.print_results_pair_unequal_mm_first(ow, oh, left_open, right_open, Ls, Rs, Tr, Br,
                                                             hinge_allow, glass_extra_total, frame_w_ded, frame_h_ded, saddle_h_ded, center_allow,
                                                             gw_left, gh_left, gw_right, gh_right)
                else:
                    self.print_results_pair_unequal_in_first(ow, oh, left_open, right_open, Ls, Rs, Tr, Br,
                                                             hinge_allow, glass_extra_total, frame_w_ded, frame_h_ded, saddle_h_ded, center_allow,
                                                             gw_left, gh_left, gw_right, gh_right)
                return

            # Equal mode
            narrow_special_active = (self.door_var.get().startswith("Narrow") and self.narrow_special_var.get())
            if narrow_special_active:
                if unit == "mm":
                    total_stiles_ded = Ls + Rs + in_to_mm(2.125 + 2.0)
                else:
                    total_stiles_ded = Ls + Rs + (2.125 + 2.0)
                effective_w_total = ow - frame_w_ded - center_allow - total_stiles_ded
                leaf_open_w = effective_w_total / 2.0
                gw_leaf = leaf_open_w - hinge_allow - glass_extra_total
                gh_leaf = oh - (Tr + Br) - glass_extra_total - frame_h_ded - saddle_h_ded
            else:
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

    def print_results_pair_unequal_in_first(self, ow, oh, left_open, right_open, Ls, Rs, Tr, Br,
                                            hinge_allow, glass_extra_total, frame_w_ded, frame_h_ded, saddle_h_ded, center_allow,
                                            gw_left_in, gh_left_in, gw_right_in, gh_right_in):
        self.result_text.insert("end", f"[Double Door (Pair) — Unequal]\n")
        self.result_text.insert("end", f"Opening (in):  W {inch_fraction_string(ow)}  |  H {inch_fraction_string(oh)}  |  Center {inch_fraction_string(center_allow)}\n")
        self.result_text.insert("end", f"Leaf openings (in): Left {inch_fraction_string(left_open)} | Right {inch_fraction_string(right_open)}\n")
        self.result_text.insert("end", f"Rails inputs (in): L {inch_fraction_string(Ls)}, R {inch_fraction_string(Rs)}, T {inch_fraction_string(Tr)}, B {inch_fraction_string(Br)}\n")
        self.result_text.insert("end", f"Glass extra/dir: {inch_fraction_string(glass_extra_total)}   |  Hinge/leaf (W): {inch_fraction_string(hinge_allow)}\n")
        self.result_text.insert("end", f"Frame (total):  W deduct {inch_fraction_string(frame_w_ded)},  H deduct {inch_fraction_string(frame_h_ded)}   |  Saddle (H): {inch_fraction_string(saddle_h_ded)}\n")
        self.result_text.insert("end", "—\n")
        self.result_text.insert("end", f"Left leaf CUT SIZE (in):  W {inch_fraction_string(gw_left_in)}  |  H {inch_fraction_string(gh_left_in)}\n")
        self.result_text.insert("end", f"Right leaf CUT SIZE (in): W {inch_fraction_string(gw_right_in)} |  H {inch_fraction_string(gh_right_in)}\n")
        self.result_text.insert("end", f"Left leaf CUT SIZE (mm):  W {in_to_mm(gw_left_in):.1f} mm  |  H {in_to_mm(gh_left_in):.1f} mm\n")
        self.result_text.insert("end", f"Right leaf CUT SIZE (mm): W {in_to_mm(gw_right_in):.1f} mm |  H {in_to_mm(gh_right_in):.1f} mm\n")

    def print_results_pair_unequal_mm_first(self, ow, oh, left_open, right_open, Ls, Rs, Tr, Br,
                                            hinge_allow, glass_extra_total, frame_w_ded, frame_h_ded, saddle_h_ded, center_allow,
                                            gw_left_mm, gh_left_mm, gw_right_mm, gh_right_mm):
        self.result_text.insert("end", f"[Double Door (Pair) — Unequal]\n")
        self.result_text.insert("end", f"Opening (mm):  W {ow:.1f} mm  |  H {oh:.1f} mm  |  Center {center_allow:.1f} mm\n")
        self.result_text.insert("end", f"Leaf openings (mm): Left {left_open:.1f} | Right {right_open:.1f}\n")
        self.result_text.insert("end", f"Rails inputs (mm): L {Ls:.1f}, R {Rs:.1f}, T {Tr:.1f}, B {Br:.1f}\n")
        self.result_text.insert("end", f"Glass extra/dir: {glass_extra_total:.1f}   |  Hinge/leaf (W): {hinge_allow:.1f}\n")
        self.result_text.insert("end", f"Frame (total):  W deduct {frame_w_ded:.1f},  H deduct {frame_h_ded:.1f}   |  Saddle (H): {saddle_h_ded:.1f}\n")
        self.result_text.insert("end", "—\n")
        self.result_text.insert("end", f"Left leaf CUT SIZE (mm):  W {gw_left_mm:.1f} mm  |  H {gh_left_mm:.1f} mm  ({inch_fraction_string(mm_to_in(gw_left_mm))} × {inch_fraction_string(mm_to_in(gh_left_mm))})\n")
        self.result_text.insert("end", f"Right leaf CUT SIZE (mm): W {gw_right_mm:.1f} mm |  H {gh_right_mm:.1f} mm ({inch_fraction_string(mm_to_in(gw_right_mm))} × {inch_fraction_string(mm_to_in(gh_right_mm))})\n")

    def reset_inputs(self):
        self.unit_var.set("in")
        self.door_var.set('Medium Stile Door')
        self.config_var.set('Single Door')
        self.center_var.set("0")
        self.narrow_special_var.set(False)
        self.pair_mode_var.set('Equal (auto)')
        self.leaf_left_open_var.set("")
        self.leaf_right_open_var.set("")
        self.glass_var.set('1/4" (7/16" total/dir)')
        self.hinge_var.set('Butt hinge (−3/16")')
        self.frame_var.set('None')
        self.saddle_var.set('None')
        self.open_w_var.set("72")
        self.open_h_var.set("84")
        self.apply_preset()
        self._auto_check_narrow_special()
        self._toggle_pair_controls()
        self._toggle_unequal_fields()
        self.update_results()

    def show_about(self):
        messagebox.showinfo(
            "About",
            f"{APP_TITLE} v{VERSION}\n\n"
            "Double (Pair):\n"
            "  • Equal + Narrow special: total deduct stiles = L + R + 2-1/8 + 2 (across width), then /2; per leaf deduct Hinge + GlassExtra.\n"
            "  • Unequal: enter leaf net openings; Narrow: larger leaf uses center stile 2.0\", smaller uses 2-1/8\".\n"
            "Height per leaf: Opening_H − Top − Bottom − GlassExtra − Frame_H − Saddle.\n\n"
            "Door presets: Narrow (2-1/8,2-1/8,4), Medium (3-1/2,3-1/8,5), Wide (5,5,7-1/2)."
        )

if __name__ == "__main__":
    try:
        app = GlassCalculatorApp()
        app.mainloop()
    except Exception as e:
        _excepthook(type(e), e, e.__traceback__)
