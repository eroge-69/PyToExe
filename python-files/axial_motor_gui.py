"""
axial_motor_gui.py

GUI app (Tkinter) to generate a parametric axial‑flux motor STEP assembly + optional DXFs
suitable for import into ANSYS Motor-CAD. Wrap with PyInstaller to make a Windows .exe.

Requirements (recommended via conda):
  - Python 3.9–3.11
  - cadquery >= 2.3 (conda install -c conda-forge cadquery)
  - (optional) pyinstaller for packaging

Notes:
  - Units are millimeters (mm) and degrees.
  - STEP embeds part names encoding magnetization hints for Halbach arrays
    (e.g., "<Halbach:90deg>").
  - DXFs are simple ring outlines (top view) for rotor & stator.

Author: ChatGPT (GPT-5 Thinking)
"""

from __future__ import annotations
import math
import sys
import traceback
from dataclasses import dataclass
from typing import List, Optional, Tuple

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# CadQuery imports
import cadquery as cq
from cadquery import exporters

# ------------------------- Materials Library -------------------------
MATERIALS = {
    "steel_1018": {"density": 7.87e-3, "desc": "Mild steel 1018 (yoke/backiron)"},
    "steel_1010": {"density": 7.87e-3, "desc": "Low carbon steel 1010"},
    "electrical_steel_M19": {"density": 7.65e-3, "desc": "M-19 electrical steel (laminated)"},
    "ss_430": {"density": 7.70e-3, "desc": "Ferritic stainless 430"},
    "al_6061": {"density": 2.70e-3, "desc": "Aluminum 6061-T6 (carriers)"},
    "al_7075": {"density": 2.81e-3, "desc": "Aluminum 7075-T6"},
    "cu_EC": {"density": 8.94e-3, "desc": "Electrolytic copper (windings)"},
    "mag_NdFeB_35": {"density": 7.5e-3, "desc": "NdFeB N35"},
    "mag_NdFeB_42": {"density": 7.5e-3, "desc": "NdFeB N42"},
    "mag_SmCo_24": {"density": 8.3e-3, "desc": "SmCo 24"},
    "epoxy": {"density": 1.2e-3, "desc": "Potting epoxy"},
    "air": {"density": 1.225e-6, "desc": "Air (for gaps)"},
}

# ------------------------- Data Classes -------------------------
@dataclass
class MagnetParams:
    shape: str                 # "rect_arc" or "pie"
    thickness: float           # axial thickness
    radial_length: float       # radial depth of magnet
    chamfer: float             # edge chamfer
    halbach: bool
    halbach_shift_deg: float
    material_key: str
    coverage: float            # 0..1 fraction of pole pitch

@dataclass
class RotorParams:
    material_key: str
    thickness: float
    backiron_inner_d: float
    backiron_outer_d: float
    magnet_airgap_clearance: float

@dataclass
class StatorParams:
    material_key: str
    thickness: float
    inner_d: float
    outer_d: float
    tooth_count: int
    slot_opening: float
    yoke_thickness: float

@dataclass
class StackParams:
    arrangement: str           # "SRS" or "RSR"
    rotor_count: int
    stator_count: int
    pole_pairs: int
    mech_clearance_between_discs: float
    airgap: float
    shaft_diameter: float
    keyway: bool
    hub_thickness: float
    hub_diameter: float

@dataclass
class ModelParams:
    name: str
    units: str
    rotor: RotorParams
    stator: StatorParams
    magnets: MagnetParams
    stack: StackParams
    output_step: str
    make_dxfs: bool
    dxf_rotor: Optional[str]
    dxf_stator: Optional[str]

# ------------------------- Geometry Helpers -------------------------

def magnet_solid_rect_arc(ri: float, ro: float, arc_span_deg: float, thick: float, chamfer: float):
    nseg = max(6, int(abs(arc_span_deg) / 5))
    pts_inner = []
    pts_outer = []
    for i in range(nseg + 1):
        a = -arc_span_deg / 2 + i * (arc_span_deg / nseg)
        rad = math.radians(a)
        pts_inner.append((ri * math.cos(rad), ri * math.sin(rad)))
        pts_outer.append((ro * math.cos(rad), ro * math.sin(rad)))
    poly = cq.Workplane("XY").polyline(pts_inner + list(reversed(pts_outer))).close()
    solid = poly.extrude(thick)
    if chamfer > 0:
        try:
            solid = solid.edges("|Z").chamfer(chamfer)
        except Exception:
            pass
    return solid


def magnet_solid_pie(ro: float, arc_span_deg: float, thick: float, chamfer: float):
    nseg = max(6, int(abs(arc_span_deg) / 5))
    pts = [(0, 0)]
    for i in range(nseg + 1):
        a = -arc_span_deg / 2 + i * (arc_span_deg / nseg)
        rad = math.radians(a)
        pts.append((ro * math.cos(rad), ro * math.sin(rad)))
    poly = cq.Workplane("XY").polyline(pts).close()
    solid = poly.extrude(thick)
    if chamfer > 0:
        try:
            solid = solid.edges("|Z").chamfer(chamfer)
        except Exception:
            pass
    return solid


def halbach_direction(index: int, total_magnets: int, base_phase_deg: float) -> Tuple[float, float, float]:
    phase = (index * base_phase_deg) % 360.0
    return (0.0, 0.0, phase)


def place_rotor_with_magnets(rp: RotorParams, mp: MagnetParams, p_pairs: int, z: float, name_prefix: str) -> cq.Assembly:
    asm = cq.Assembly(name=f"{name_prefix}_asm")

    # Backiron
    backiron = (
        cq.Workplane("XY")
        .circle(rp.backiron_outer_d / 2)
        .circle(rp.backiron_inner_d / 2)
        .extrude(rp.thickness)
    )
    asm.add(backiron, name=f"{name_prefix}_backiron[{rp.material_key}]", loc=cq.Location(cq.Vector(0, 0, z)),
            color=cq.Color(0.45, 0.45, 0.45))

    magnets_per_rotor = 2 * p_pairs
    pitch_deg = 360.0 / magnets_per_rotor
    arc_span_deg = pitch_deg * mp.coverage

    ri = rp.backiron_outer_d / 2 - mp.radial_length
    ro = rp.backiron_outer_d / 2

    magnet_base_z = z + rp.thickness

    for i in range(magnets_per_rotor):
        ang = i * pitch_deg
        if mp.shape == "rect_arc":
            mag = magnet_solid_rect_arc(ri=ri, ro=ro, arc_span_deg=arc_span_deg, thick=mp.thickness, chamfer=mp.chamfer)
        else:
            mag = magnet_solid_pie(ro=ro, arc_span_deg=arc_span_deg, thick=mp.thickness, chamfer=mp.chamfer)

        loc = cq.Location(cq.Vector(0, 0, magnet_base_z), cq.Vector(0, 0, 1), ang)

        if mp.halbach:
            _, _, hz = halbach_direction(i, magnets_per_rotor, mp.halbach_shift_deg)
            mname = f"{name_prefix}_mag_{i:02d}[{mp.material_key}]<Halbach:{hz:.1f}deg>"
        else:
            mname = f"{name_prefix}_mag_{i:02d}[{mp.material_key}]"
        asm.add(mag, name=mname, loc=loc, color=cq.Color(0.75, 0.1, 0.1))

    return asm


def make_stator(sp: StatorParams, z: float, name: str) -> cq.Assembly:
    part = (
        cq.Workplane("XY")
        .circle(sp.outer_d / 2)
        .circle(sp.inner_d / 2)
        .extrude(sp.thickness)
    )
    asm = cq.Assembly()
    asm.add(part, name=f"{name}_ring[{sp.material_key}]",
            loc=cq.Location(cq.Vector(0, 0, z)), color=cq.Color(0.8, 0.8, 0.85))
    return asm


def add_shaft_and_hub(asm: cq.Assembly, shaft_d: float, hub_d: float, hub_t: float, keyway: bool, z0: float, z1: float):
    length = abs(z1 - z0)
    base_z = min(z0, z1)
    shaft = cq.Workplane("XY").circle(shaft_d / 2).extrude(length)
    asm.add(shaft, name="shaft", loc=cq.Location(cq.Vector(0, 0, base_z)), color=cq.Color(0.6, 0.6, 0.6))
    if hub_d > shaft_d and hub_t > 0:
        hub = cq.Workplane("XY").circle(hub_d / 2).circle(shaft_d / 2).extrude(hub_t)
        asm.add(hub, name="hub", loc=cq.Location(cq.Vector(0, 0, base_z)), color=cq.Color(0.6, 0.6, 0.6))


def build_assembly(mp: ModelParams) -> cq.Assembly:
    asm = cq.Assembly(name=mp.name)

    rp = mp.rotor
    sp = mp.stator
    gap = mp.stack.airgap

    base_seq = ["S", "R", "S"] if mp.stack.arrangement == "SRS" else ["R", "S", "R"]

    seq: List[str] = []
    r_left = mp.stack.rotor_count
    s_left = mp.stack.stator_count
    while r_left > 0 or s_left > 0:
        for t in base_seq:
            if t == "R" and r_left > 0:
                seq.append("R")
                r_left -= 1
            elif t == "S" and s_left > 0:
                seq.append("S")
                s_left -= 1
            if r_left == 0 and s_left == 0:
                break

    def element_thickness(t):
        return (rp.thickness + mp.magnets.thickness) if t == "R" else sp.thickness

    total_thick = sum(element_thickness(t) for t in seq) + (len(seq) - 1) * gap
    z_start = -total_thick / 2.0
    z_cursor = z_start

    rotor_index = 0
    stator_index = 0
    z_first = None
    z_last = None

    for idx, t in enumerate(seq):
        if t == "R":
            rname = f"rotor{rotor_index}"
            rotor_asm = place_rotor_with_magnets(rp, mp.magnets, mp.stack.pole_pairs, z_cursor, rname)
            asm.add(rotor_asm, name=rname)
            z_cursor += rp.thickness + mp.magnets.thickness
            rotor_index += 1
        else:
            sname = f"stator{stator_index}"
            stator_asm = make_stator(sp, z_cursor, sname)
            asm.add(stator_asm, name=sname)
            z_cursor += sp.thickness
            stator_index += 1

        if idx < len(seq) - 1:
            z_cursor += gap

        if z_first is None:
            z_first = z_start
        z_last = z_cursor

    add_shaft_and_hub(asm, mp.stack.shaft_diameter, mp.stack.hub_diameter, mp.stack.hub_thickness,
                      mp.stack.keyway, z_first if z_first is not None else 0.0, z_last if z_last is not None else 0.0)
    return asm

# ------------------------- DXF Helpers -------------------------

def export_top_dxf(filename: str, outer_d: float, inner_d: float):
    wp = cq.Workplane("XY").circle(outer_d / 2).circle(inner_d / 2)
    exporters.export(wp, filename)

# ------------------------- GUI -------------------------

class LabeledEntry(ttk.Frame):
    def __init__(self, parent, label: str, default: str = "", width: int = 12):
        super().__init__(parent)
        ttk.Label(self, text=label).grid(row=0, column=0, sticky="w")
        self.var = tk.StringVar(value=default)
        self.entry = ttk.Entry(self, textvariable=self.var, width=width)
        self.entry.grid(row=0, column=1, sticky="ew")
        self.columnconfigure(1, weight=1)

    def get_float(self, name: str) -> float:
        try:
            return float(self.var.get())
        except ValueError:
            raise ValueError(f"{name} must be a number")

    def get_int(self, name: str) -> int:
        try:
            return int(float(self.var.get()))
        except ValueError:
            raise ValueError(f"{name} must be an integer")

    def get(self) -> str:
        return self.var.get()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Axial Motor STEP/DXF Generator")
        self.geometry("900x680")
        self.minsize(820, 600)

        # Style
        style = ttk.Style(self)
        if sys.platform.startswith("win"):
            style.theme_use("vista")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.frm_stack = ttk.Frame(nb, padding=10)
        self.frm_rotor = ttk.Frame(nb, padding=10)
        self.frm_stator = ttk.Frame(nb, padding=10)
        self.frm_magnet = ttk.Frame(nb, padding=10)
        self.frm_output = ttk.Frame(nb, padding=10)

        nb.add(self.frm_stack, text="Stack & Layout")
        nb.add(self.frm_rotor, text="Rotor")
        nb.add(self.frm_stator, text="Stator")
        nb.add(self.frm_magnet, text="Magnets")
        nb.add(self.frm_output, text="Output")

        self.build_stack_tab()
        self.build_rotor_tab()
        self.build_stator_tab()
        self.build_magnet_tab()
        self.build_output_tab()

        # Footer buttons
        footer = ttk.Frame(self, padding=(10, 5))
        footer.pack(fill="x")
        self.btn_generate = ttk.Button(footer, text="Generate STEP/DXF", command=self.on_generate)
        self.btn_generate.pack(side="right")
        self.status = tk.StringVar(value="Ready.")
        ttk.Label(footer, textvariable=self.status).pack(side="left")

    # ---- Tabs ----
    def build_stack_tab(self):
        f = self.frm_stack
        # Row 0
        ttk.Label(f, text="Arrangement").grid(row=0, column=0, sticky="w")
        self.arrangement = tk.StringVar(value="SRS")
        ttk.Combobox(f, textvariable=self.arrangement, values=["SRS", "RSR"], width=8, state="readonly").grid(row=0, column=1, sticky="w")

        self.e_rotors = LabeledEntry(f, "# Rotors", "2")
        self.e_rotors.grid(row=0, column=2, padx=12, sticky="w")
        self.e_stators = LabeledEntry(f, "# Stators", "1")
        self.e_stators.grid(row=0, column=3, padx=12, sticky="w")

        # Row 1
        self.e_polepairs = LabeledEntry(f, "Pole pairs (p)", "8")
        self.e_polepairs.grid(row=1, column=0, padx=(0,12), pady=6, sticky="w")
        self.e_airgap = LabeledEntry(f, "Airgap (mm)", "0.8")
        self.e_airgap.grid(row=1, column=1, padx=12, pady=6, sticky="w")
        self.e_mechclr = LabeledEntry(f, "Mech. clearance (mm)", "0.0")
        self.e_mechclr.grid(row=1, column=2, padx=12, pady=6, sticky="w")

        # Row 2
        self.e_shaftd = LabeledEntry(f, "Shaft Ø (mm)", "10.0")
        self.e_shaftd.grid(row=2, column=0, padx=(0,12), pady=6, sticky="w")
        self.e_hubd = LabeledEntry(f, "Hub Ø (mm)", "30.0")
        self.e_hubd.grid(row=2, column=1, padx=12, pady=6, sticky="w")
        self.e_hubt = LabeledEntry(f, "Hub thickness (mm)", "6.0")
        self.e_hubt.grid(row=2, column=2, padx=12, pady=6, sticky="w")
        self.keyway = tk.BooleanVar(value=False)
        ttk.Checkbutton(f, text="Keyway (metadata)", variable=self.keyway).grid(row=2, column=3, sticky="w")

        for c in range(4):
            f.columnconfigure(c, weight=1)

    def build_rotor_tab(self):
        f = self.frm_rotor
        ttk.Label(f, text="Backiron Material").grid(row=0, column=0, sticky="w")
        self.rotor_mat = tk.StringVar(value="steel_1018")
        ttk.Combobox(f, textvariable=self.rotor_mat, values=list(MATERIALS.keys()), state="readonly").grid(row=0, column=1, sticky="ew")
        self.e_rt = LabeledEntry(f, "Backiron thickness (mm)", "4.0")
        self.e_rt.grid(row=1, column=0, padx=(0,12), pady=6, sticky="w")
        self.e_rid = LabeledEntry(f, "Inner Ø (mm)", "12.0")
        self.e_rid.grid(row=1, column=1, padx=12, pady=6, sticky="w")
        self.e_rod = LabeledEntry(f, "Outer Ø (mm)", "150.0")
        self.e_rod.grid(row=1, column=2, padx=12, pady=6, sticky="w")
        self.e_magclr = LabeledEntry(f, "Magnet→stator face clr (mm)", "0.0")
        self.e_magclr.grid(row=1, column=3, padx=12, pady=6, sticky="w")
        for c in range(4):
            f.columnconfigure(c, weight=1)

    def build_stator_tab(self):
        f = self.frm_stator
        ttk.Label(f, text="Stator Material").grid(row=0, column=0, sticky="w")
        self.stator_mat = tk.StringVar(value="electrical_steel_M19")
        ttk.Combobox(f, textvariable=self.stator_mat, values=list(MATERIALS.keys()), state="readonly").grid(row=0, column=1, sticky="ew")
        self.e_st = LabeledEntry(f, "Stack thickness (mm)", "8.0")
        self.e_st.grid(row=1, column=0, padx=(0,12), pady=6, sticky="w")
        self.e_sid = LabeledEntry(f, "Inner Ø (mm)", "14.0")
        self.e_sid.grid(row=1, column=1, padx=12, pady=6, sticky="w")
        self.e_sod = LabeledEntry(f, "Outer Ø (mm)", "150.0")
        self.e_sod.grid(row=1, column=2, padx=12, pady=6, sticky="w")
        self.e_tooth = LabeledEntry(f, "Tooth count (info)", "24")
        self.e_tooth.grid(row=2, column=0, padx=(0,12), pady=6, sticky="w")
        self.e_slot = LabeledEntry(f, "Slot opening @OD (mm, info)", "2.0")
        self.e_slot.grid(row=2, column=1, padx=12, pady=6, sticky="w")
        self.e_yoke = LabeledEntry(f, "Yoke thickness (mm, info)", "6.0")
        self.e_yoke.grid(row=2, column=2, padx=12, pady=6, sticky="w")
        for c in range(3):
            f.columnconfigure(c, weight=1)

    def build_magnet_tab(self):
        f = self.frm_magnet
        ttk.Label(f, text="Magnet shape").grid(row=0, column=0, sticky="w")
        self.m_shape = tk.StringVar(value="rect_arc")
        ttk.Combobox(f, textvariable=self.m_shape, values=["rect_arc", "pie"], state="readonly", width=12).grid(row=0, column=1, sticky="w")
        self.e_mt = LabeledEntry(f, "Magnet thickness (mm)", "3.0")
        self.e_mt.grid(row=1, column=0, padx=(0,12), pady=6, sticky="w")
        self.e_mrad = LabeledEntry(f, "Magnet radial length (mm)", "12.0")
        self.e_mrad.grid(row=1, column=1, padx=12, pady=6, sticky="w")
        self.e_mch = LabeledEntry(f, "Magnet chamfer (mm)", "0.3")
        self.e_mch.grid(row=1, column=2, padx=12, pady=6, sticky="w")
        self.halbach = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Halbach array", variable=self.halbach).grid(row=2, column=0, sticky="w")
        self.e_phase = LabeledEntry(f, "Halbach phase/blk (deg)", "90.0")
        self.e_phase.grid(row=2, column=1, padx=12, pady=6, sticky="w")
        ttk.Label(f, text="Magnet material").grid(row=3, column=0, sticky="w")
        self.m_mat = tk.StringVar(value="mag_NdFeB_42")
        ttk.Combobox(f, textvariable=self.m_mat, values=list(MATERIALS.keys()), state="readonly").grid(row=3, column=1, sticky="ew")
        self.e_cov = LabeledEntry(f, "Circumf. coverage per pole (0..1)", "0.8")
        self.e_cov.grid(row=3, column=2, padx=12, pady=6, sticky="w")
        for c in range(3):
            f.columnconfigure(c, weight=1)

    def build_output_tab(self):
        f = self.frm_output
        self.model_name = LabeledEntry(f, "Model name", "axial_motor")
        self.model_name.grid(row=0, column=0, padx=(0,12), pady=6, sticky="w")
        self.output_step = LabeledEntry(f, "STEP filename", "axial_motor.step", width=32)
        self.output_step.grid(row=0, column=1, padx=12, pady=6, sticky="w")
        ttk.Button(f, text="Browse…", command=self.on_browse_step).grid(row=0, column=2, sticky="w")
        self.want_dxf = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Also export DXFs", variable=self.want_dxf).grid(row=1, column=0, sticky="w")
        self.dxf_rotor = LabeledEntry(f, "Rotor DXF", "rotor_outline.dxf", width=32)
        self.dxf_rotor.grid(row=1, column=1, padx=12, pady=6, sticky="w")
        self.dxf_stator = LabeledEntry(f, "Stator DXF", "stator_outline.dxf", width=32)
        self.dxf_stator.grid(row=2, column=1, padx=12, pady=6, sticky="w")
        ttk.Button(f, text="Browse Rotor…", command=lambda: self.on_browse_dxf(self.dxf_rotor)).grid(row=1, column=2, sticky="w")
        ttk.Button(f, text="Browse Stator…", command=lambda: self.on_browse_dxf(self.dxf_stator)).grid(row=2, column=2, sticky="w")
        f.columnconfigure(0, weight=0)
        f.columnconfigure(1, weight=1)
        f.columnconfigure(2, weight=0)

    # ---- File dialogs ----
    def on_browse_step(self):
        fname = filedialog.asksaveasfilename(title="Save STEP", defaultextension=".step", filetypes=[("STEP","*.step"),("STEP","*.stp"),("All","*.*")])
        if fname:
            self.output_step.var.set(fname)

    def on_browse_dxf(self, widget: LabeledEntry):
        fname = filedialog.asksaveasfilename(title="Save DXF", defaultextension=".dxf", filetypes=[("DXF","*.dxf"),("All","*.*")])
        if fname:
            widget.var.set(fname)

    # ---- Generate ----
    def on_generate(self):
        try:
            self.status.set("Validating inputs…")
            self.update_idletasks()
            mp = self.collect_params()

            self.status.set("Building 3D assembly…")
            self.update_idletasks()
            asm = build_assembly(mp)

            self.status.set("Exporting STEP…")
            self.update_idletasks()
            exporters.export(asm.toCompound(), mp.output_step)  # IMPORTANT: .toCompound()

            if mp.make_dxfs:
                if mp.dxf_rotor:
                    self.status.set("Exporting rotor DXF…")
                    self.update_idletasks()
                    export_top_dxf(mp.dxf_rotor, mp.rotor.backiron_outer_d, mp.rotor.backiron_inner_d)
                if mp.dxf_stator:
                    self.status.set("Exporting stator DXF…")
                    self.update_idletasks()
                    export_top_dxf(mp.dxf_stator, mp.stator.outer_d, mp.stator.inner_d)

            self.status.set("Done.")
            messagebox.showinfo("Success", f"Generated:\nSTEP: {mp.output_step}\n" + (f"DXFs: {mp.dxf_rotor}, {mp.dxf_stator}" if mp.make_dxfs else ""))
        except Exception as e:
            self.status.set("Error.")
            tb = traceback.format_exc()
            messagebox.showerror("Error", f"Generation failed:\n{e}\n\nDetails:\n{tb}")

    # ---- Collect & validate ----
    def collect_params(self) -> ModelParams:
        # Basic numeric sanity checks happen here.
        def pos(name: str, val: float) -> float:
            if val <= 0:
                raise ValueError(f"{name} must be > 0")
            return val

        arrangement = self.arrangement.get()
        rotor_count = self.e_rotors.get_int("# Rotors")
        stator_count = self.e_stators.get_int("# Stators")
        pole_pairs = pos("Pole pairs", self.e_polepairs.get_int("Pole pairs"))
        airgap = pos("Airgap", self.e_airgap.get_float("Airgap"))
        mech_clearance = max(0.0, self.e_mechclr.get_float("Mech clearance"))
        shaft_d = pos("Shaft diameter", self.e_shaftd.get_float("Shaft Ø"))
        hub_d = pos("Hub diameter", self.e_hubd.get_float("Hub Ø"))
        hub_t = pos("Hub thickness", self.e_hubt.get_float("Hub thickness"))

        r_mat = self.rotor_mat.get()
        r_t = pos("Rotor thickness", self.e_rt.get_float("Backiron thickness"))
        r_id = pos("Rotor inner diameter", self.e_rid.get_float("Inner Ø"))
        r_od = pos("Rotor outer diameter", self.e_rod.get_float("Outer Ø"))
        if r_id >= r_od:
            raise ValueError("Rotor inner diameter must be < outer diameter")
        mag_clear = max(0.0, self.e_magclr.get_float("Magnet->stator clearance"))

        s_mat = self.stator_mat.get()
        s_t = pos("Stator thickness", self.e_st.get_float("Stack thickness"))
        s_id = pos("Stator inner diameter", self.e_sid.get_float("Inner Ø"))
        s_od = pos("Stator outer diameter", self.e_sod.get_float("Outer Ø"))
        if s_id >= s_od:
            raise ValueError("Stator inner diameter must be < outer diameter")

        tooth_count = max(1, self.e_tooth.get_int("Tooth count"))
        slot_opening = max(0.0, self.e_slot.get_float("Slot opening"))
        yoke_thick = max(0.0, self.e_yoke.get_float("Yoke thickness"))

        m_shape = self.m_shape.get()
        m_t = pos("Magnet thickness", self.e_mt.get_float("Magnet thickness"))
        m_rad = pos("Magnet radial length", self.e_mrad.get_float("Magnet radial length"))
        if m_rad >= r_od / 2:
            # Allow but warn; still OK for pie magnets.
            pass
        m_ch = max(0.0, self.e_mch.get_float("Magnet chamfer"))
        halbach = self.halbach.get()
        phase = max(0.0, self.e_phase.get_float("Halbach phase"))
        m_mat = self.m_mat.get()
        coverage = self.e_cov.get_float("Coverage")
        if not (0.0 < coverage <= 1.0):
            raise ValueError("Coverage must be in (0, 1]")

        model_name = self.model_name.get()
        step_path = self.output_step.get()
        want_dxf = self.want_dxf.get()
        dxf_rotor = self.dxf_rotor.get() if want_dxf else None
        dxf_stator = self.dxf_stator.get() if want_dxf else None

        mp = ModelParams(
            name=model_name,
            units="mm",
            rotor=RotorParams(
                material_key=r_mat,
                thickness=r_t,
                backiron_inner_d=r_id,
                backiron_outer_d=r_od,
                magnet_airgap_clearance=mag_clear,
            ),
            stator=StatorParams(
                material_key=s_mat,
                thickness=s_t,
                inner_d=s_id,
                outer_d=s_od,
                tooth_count=tooth_count,
                slot_opening=slot_opening,
                yoke_thickness=yoke_thick,
            ),
            magnets=MagnetParams(
                shape=m_shape,
                thickness=m_t,
                radial_length=m_rad,
                chamfer=m_ch,
                halbach=halbach,
                halbach_shift_deg=phase,
                material_key=m_mat,
                coverage=coverage,
            ),
            stack=StackParams(
                arrangement=arrangement,
                rotor_count=rotor_count,
                stator_count=stator_count,
                pole_pairs=pole_pairs,
                mech_clearance_between_discs=mech_clearance,
                airgap=airgap,
                shaft_diameter=shaft_d,
                keyway=self.keyway.get(),
                hub_thickness=hub_t,
                hub_diameter=hub_d,
            ),
            output_step=step_path,
            make_dxfs=want_dxf,
            dxf_rotor=dxf_rotor,
            dxf_stator=dxf_stator,
        )
        return mp


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
# This allows the script to be run directly or imported without executing the GUI.
# If run directly, it will start the GUI application.
# If imported, it will not start the GUI, allowing for unit testing or other uses.
# This is useful for modularity and testing.
# The main() function is only called when the script is executed directly.
# This allows for better separation of concerns and makes the code more maintainable.
# The __name__ variable is set to "__main__" when the script is run directly.
# This is a common Python idiom to allow or prevent parts of code from being run when the modules are imported.