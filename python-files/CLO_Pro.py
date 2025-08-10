#!/usr/bin/env python3
import os
import math
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Optional

# Third-party
try:
    import pandas as pd
except Exception as e:
    raise SystemExit("Requires pandas. Install: pip install pandas openpyxl xlsxwriter pillow") from e

# Optional (for circular images)
try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_OK = True
except Exception:
    PIL_OK = False

APP_TITLE = "CLO Mark Distributor (Pro v5.1)"
WINDOW_MIN = (1140, 760)

# -------- Defaults (ALL ZERO by request) --------
DEFAULT_CAPS_ZERO = {
    "Midterm":     [0, 0, 0, 0],
    "Project":     [0, 0, 0, 0],
    "Final":       [0, 0, 0, 0],
    "Assignments": [0, 0, 0, 0],
    "Quizzes":     [0, 0, 0, 0],
    "Viva":        [0, 0, 0, 0],
}
ASSESS_ORDER = ["Midterm", "Project", "Final", "Assignments", "Quizzes", "Viva"]
TOTAL_HEADERS = {
    "Midterm": "Midterm Exam",
    "Project": "Project",
    "Final": "Final Term Exam",
    "Assignments": "Assignments",
    "Quizzes": "Quizzes",
    "Viva": "Viva",
}
WEIGHT_HEADERS = {title: f"{title} (Weightage)" for title in ASSESS_ORDER}

# ---------------- Helper logic ----------------
def scale_weightage(series, weightage: float, total: float) -> List[float]:
    vals = pd.to_numeric(series, errors="coerce").fillna(0.0).astype(float).tolist()
    if weightage <= 0 or total <= 0:
        return [0.0 for _ in vals]
    factor = total / weightage
    return [round(v * factor, 2) for v in vals]

def allocate_exact_target(target: float, caps: List[float]) -> List[float]:
    """Allocate exactly `target` across CLOs within caps; no negatives."""
    target = max(0.0, float(target or 0.0))
    caps = [max(0.0, float(c) if c is not None else 0.0) for c in caps]
    if target <= 0 or all(c <= 0 for c in caps):
        return [0.0] * len(caps)

    # Proportional seed
    weights = [random.random() for _ in caps]
    wsum = sum(weights) or 1.0
    alloc = [min(round((w / wsum) * target, 2), caps[i]) for i, w in enumerate(weights)]

    # Fill deficit
    deficit = round(target - sum(alloc), 2)
    if deficit > 0:
        order = list(range(len(caps)))
        random.shuffle(order)
        for i in order:
            if deficit <= 0: break
            room = round(caps[i] - alloc[i], 2)
            if room <= 0: continue
            add = round(min(room, deficit), 2)
            if add > 0:
                alloc[i] = round(alloc[i] + add, 2)
                deficit = round(deficit - add, 2)

    # Trim excess (rounding)
    excess = round(sum(alloc) - target, 2)
    if excess > 0:
        order = list(range(len(caps)))
        random.shuffle(order)
        for i in order:
            if excess <= 0: break
            take = round(min(alloc[i], excess), 2)
            if take > 0:
                alloc[i] = round(alloc[i] - take, 2)
                excess = round(excess - take, 2)

    return [max(0.0, min(alloc[i], caps[i])) for i in range(len(caps))]

def load_circular_image(path: str, size: int = 60):
    """Load an image, center-crop to square, resize, and apply circular mask."""
    if not (PIL_OK and path and os.path.exists(path)):
        return None
    img = Image.open(path).convert("RGBA")
    # center-crop to square
    w, h = img.size
    m = min(w, h)
    left = (w - m) // 2
    top = (h - m) // 2
    img = img.crop((left, top, left + m, top + m)).resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    img.putalpha(mask)
    return ImageTk.PhotoImage(img)

# Optional gender icon loader (custom PNGs)
def load_gender_icon(path, size=56):
    if not PIL_OK:
        return None
    try:
        img = Image.open(path).convert("RGBA")
        # center-crop to square if needed
        w, h = img.size
        m = min(w, h)
        left = (w - m) // 2
        top = (h - m) // 2
        img = img.crop((left, top, left + m, top + m)).resize((size, size), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

# ---------------- Start Dialog ----------------
class StartDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Welcome")
        self.geometry("380x220")
        self.resizable(False, False)
        self.configure(bg="#2B90D9")
        self.attributes("-topmost", True)

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) // 2
        y = (self.winfo_screenheight() - self.winfo_reqheight()) // 2
        self.geometry(f"+{x}+{y}")

        # Content
        box = tk.Frame(self, bg="#2B90D9")
        box.pack(expand=True, fill="both", padx=14, pady=14)

        tk.Label(box, text="Let’s set up your profile", bg="#2B90D9", fg="white",
                 font=("Segoe UI", 14, "bold")).pack(pady=(2,10))

        frm = tk.Frame(box, bg="#2B90D9")
        frm.pack(pady=4, fill="x")

        tk.Label(frm, text="Your Name:", bg="#2B90D9", fg="white").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.name_var = tk.StringVar(value="")
        tk.Entry(frm, textvariable=self.name_var).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        tk.Label(frm, text="Gender:", bg="#2B90D9", fg="white").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self.gender_var = tk.StringVar(value="male")
        tk.Radiobutton(frm, text="Male", variable=self.gender_var, value="male", bg="#2B90D9", fg="white", selectcolor="#2B90D9").grid(row=1, column=1, sticky="w", padx=6)
        tk.Radiobutton(frm, text="Female", variable=self.gender_var, value="female", bg="#2B90D9", fg="white", selectcolor="#2B90D9").grid(row=1, column=1, sticky="e", padx=6)

        tk.Button(box, text="Start", bg="#27AE60", fg="white", width=12, command=self._ok).pack(pady=(14,2))

        # Modal
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._ok)

    def _ok(self):
        self.result = {
            "name": (self.name_var.get() or "User").strip(),
            "gender": self.gender_var.get()
        }
        self.grab_release()
        self.destroy()

# ---------------- UI Components ----------------
class AssessmentRow(ttk.Frame):
    def __init__(self, master, title: str, default_caps: List[float] = None):
        super().__init__(master)
        self.title = title
        default_caps = default_caps or [0, 0, 0, 0]

        self.enabled_var = tk.BooleanVar(value=True)
        self.column_var = tk.StringVar(value="— None —")
        self.weightage_var = tk.StringVar(value="0")
        self.totalmarks_var = tk.StringVar(value="0")
        self.caps_vars = [tk.StringVar(value=str(default_caps[i])) for i in range(4)]

        self.enable_chk = ttk.Checkbutton(self, text=title, variable=self.enabled_var)
        self.enable_chk.grid(row=0, column=0, padx=(4,6), pady=6, sticky="w")

        ttk.Label(self, text="Column (weightage):", style="Muted.TLabel").grid(row=0, column=1, padx=(4,2), pady=6, sticky="e")
        self.combo = ttk.Combobox(self, textvariable=self.column_var, state="readonly", width=28, values=["— None —"], style="Combo.TCombobox")
        self.combo.grid(row=0, column=2, padx=2, pady=6, sticky="w")

        ttk.Label(self, text="Weightage:", style="Muted.TLabel").grid(row=0, column=3, padx=(8,2), pady=6, sticky="e")
        ttk.Entry(self, textvariable=self.weightage_var, width=8, style="Entry.TEntry", justify="center").grid(row=0, column=4, padx=2, pady=6, sticky="w")

        ttk.Label(self, text="Total Marks:", style="Muted.TLabel").grid(row=0, column=5, padx=(8,2), pady=6, sticky="e")
        ttk.Entry(self, textvariable=self.totalmarks_var, width=8, style="Entry.TEntry", justify="center").grid(row=0, column=6, padx=2, pady=6, sticky="w")

        capsf = ttk.Frame(self, style="Caps.TFrame"); capsf.grid(row=0, column=7, padx=(12,4), pady=6, sticky="w")
        ttk.Label(capsf, text="Caps CLO1..4:", style="Muted.TLabel").grid(row=0, column=0, padx=(0,8))
        for i, var in enumerate(self.caps_vars, start=1):
            ttk.Entry(capsf, textvariable=var, width=6, justify="center", style="Caps.TEntry").grid(row=0, column=i, padx=2)

        self.grid_columnconfigure(2, weight=1)

    def set_columns(self, columns: List[str]):
        vals = ["— None —"] + list(columns)
        self.combo.configure(values=vals)
        if self.column_var.get() not in vals:
            self.column_var.set("— None —")

    def get_config(self) -> Dict:
        def as_float(s):
            try:
                v = float(str(s).strip()); return max(0.0, v)
            except: return 0.0
        caps = [as_float(v.get()) for v in self.caps_vars]
        weightage = as_float(self.weightage_var.get())
        totalmarks = as_float(self.totalmarks_var.get())
        col = self.column_var.get();  col = None if col == "— None —" else col
        return {
            "enabled": self.enabled_var.get(),
            "title": self.title,
            "column": col,
            "weightage": weightage,
            "totalmarks": totalmarks,
            "caps": caps
        }

# ---------------- Data Viewer ----------------
class DataViewer(tk.Toplevel):
    def __init__(self, master, title="CLO Distributor — Data Viewer"):
        super().__init__(master)
        self.title(title)
        self.geometry("1220x660")
        self.minsize(900, 500)
        self.configure(bg="#8E44AD")

        head = tk.Frame(self, bg="#8E44AD"); head.pack(fill="x")
        tk.Label(head, text=title, bg="#8E44AD", fg="white", font=("Segoe UI", 14, "bold")).pack(side="left", padx=12, pady=10)

        toggle = ttk.Frame(self); toggle.pack(fill="x", padx=12, pady=(6,0))
        ttk.Label(toggle, text="View:", style="Header.TLabel").pack(side="left", padx=6)
        self.mode = tk.StringVar(value="raw")
        ttk.Radiobutton(toggle, text="Raw Sheet", variable=self.mode, value="raw", command=self._refresh).pack(side="left", padx=6)
        ttk.Radiobutton(toggle, text="Calculated + CLO", variable=self.mode, value="calc", command=self._refresh).pack(side="left", padx=6)

        frame = ttk.Frame(self, style="Card.TFrame"); frame.pack(fill="both", expand=True, padx=12, pady=8)
        self.tree = ttk.Treeview(frame, show="headings", style="Fancy.Treeview")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        self._raw_df = None
        self._calc_df = None

    def set_data(self, raw_df: Optional[pd.DataFrame], calc_df: Optional[pd.DataFrame]):
        self._raw_df = raw_df
        self._calc_df = calc_df
        self._refresh()

    def _refresh(self):
        df = self._raw_df if self.mode.get() == "raw" else self._calc_df
        self.tree.delete(*self.tree.get_children())
        if df is None or df.empty:
            self.tree["columns"] = []
            return
        cols = [str(c) for c in df.columns]
        self.tree["columns"] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=max(110, int(10 * (len(str(c))+4))))
        max_rows = min(len(df), 1500)
        for i in range(max_rows):
            vals = df.iloc[i].tolist()
            display = [("" if (isinstance(v, float) and math.isnan(v)) else v) for v in vals]
            self.tree.insert("", "end", values=display)

# ---------------- Main App ----------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.minsize(*WINDOW_MIN)
        self._setup_theme()

        self.user_name = "User"
        self.user_gender = "male"

        self.file_path: Optional[str] = None
        self.df: Optional[pd.DataFrame] = None
        self.calc_df: Optional[pd.DataFrame] = None
        self.viewer: Optional[DataViewer] = None
        self._dev_photo = None
        self._gender_icon_img = None

        header = tk.Frame(self, bg="#2B90D9"); header.pack(fill="x")

        tk.Label(header, text=APP_TITLE, bg="#2B90D9", fg="white",
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=14, pady=10)

        right = tk.Frame(header, bg="#2B90D9"); right.pack(side="right", padx=12, pady=6)
        self.icon_canvas = tk.Canvas(right, width=56, height=56, bg="#2B90D9", highlightthickness=0)
        self.icon_canvas.grid(row=0, column=0, padx=(0,8))
        self.greet_var = tk.StringVar(value="Hi, User")
        tk.Label(right, textvariable=self.greet_var, bg="#2B90D9", fg="white",
                 font=("Segoe UI", 11, "bold")).grid(row=0, column=1, sticky="w")

        top = ttk.Frame(self, style="Card.TFrame"); top.pack(fill="x", padx=12, pady=10)
        ttk.Label(top, text="Input Excel:", style="Header.TLabel").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.file_label_var = tk.StringVar(value="No file selected")
        ttk.Label(top, textvariable=self.file_label_var, style="Value.TLabel").grid(row=0, column=1, padx=8, pady=8, sticky="w")

        ttk.Button(top, text="Choose File", command=self.choose_file, style="Primary.TButton").grid(row=0, column=2, padx=6, pady=8)
        ttk.Button(top, text="Auto-Detect Columns", command=self.autodetect_columns, style="Info.TButton").grid(row=0, column=3, padx=6, pady=8)
        ttk.Button(top, text="Open Data Viewer", command=self.open_viewer, style="Accent.TButton").grid(row=0, column=4, padx=6, pady=8)

        ttk.Label(top, text="Output file:", style="Header.TLabel").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.output_path_var = tk.StringVar(value="")
        ttk.Entry(top, textvariable=self.output_path_var, width=54, style="Entry.TEntry").grid(row=1, column=1, padx=8, pady=8, sticky="w")
        ttk.Button(top, text="Save As…", command=self.choose_output, style="Accent.TButton").grid(row=1, column=2, padx=6, pady=8)

        mapf = ttk.LabelFrame(self, text="ID / Name Mapping", style="Group.TLabelframe")
        mapf.pack(fill="x", padx=12, pady=8)
        self.id_var = tk.StringVar(value="— None —")
        self.name_var = tk.StringVar(value="— None —")
        ttk.Label(mapf, text="ID Column:", style="Muted.TLabel").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.id_combo = ttk.Combobox(mapf, textvariable=self.id_var, state="readonly", width=30, values=["— None —"], style="Combo.TCombobox")
        self.id_combo.grid(row=0, column=1, padx=6, pady=6, sticky="w")
        ttk.Label(mapf, text="Name Column:", style="Muted.TLabel").grid(row=0, column=2, padx=6, pady=6, sticky="e")
        self.name_combo = ttk.Combobox(mapf, textvariable=self.name_var, state="readonly", width=30, values=["— None —"], style="Combo.TCombobox")
        self.name_combo.grid(row=0, column=3, padx=6, pady=6, sticky="w")

        rows = ttk.LabelFrame(self, text="Assessments (weightage column + Weightage & Total; edit caps)", style="Group.TLabelframe")
        rows.pack(fill="x", padx=12, pady=8)
        self.assessment_rows: Dict[str, AssessmentRow] = {}
        for r, title in enumerate(ASSESS_ORDER):
            ar = AssessmentRow(rows, title=title, default_caps=DEFAULT_CAPS_ZERO.get(title))
            ar.grid(row=r, column=0, sticky="ew", padx=6, pady=2)
            self.assessment_rows[title] = ar
        rows.grid_columnconfigure(0, weight=1)

        bottom = ttk.Frame(self, style="Card.TFrame"); bottom.pack(fill="x", padx=12, pady=10)
        self.seed_var = tk.StringVar(value="")
        ttk.Label(bottom, text="Random Seed (optional):", style="Muted.TLabel").pack(side="left", padx=(6,4))
        ttk.Entry(bottom, textvariable=self.seed_var, width=14, style="Entry.TEntry").pack(side="left", padx=(0,10))

        self.target_mode = tk.StringVar(value="total")
        ttk.Label(bottom, text="CLO target:", style="Muted.TLabel").pack(side="left", padx=(10,4))
        ttk.Radiobutton(bottom, text="obtained weightage", variable=self.target_mode, value="weightage").pack(side="left", padx=4)
        ttk.Radiobutton(bottom, text="obtained total marks", variable=self.target_mode, value="total").pack(side="left", padx=4)

        ttk.Button(bottom, text="Calculate", command=self.calculate_totals, style="Success.TButton").pack(side="right", padx=6)
        ttk.Button(bottom, text="Distribute CLOs", command=self.distribute_clos, style="Run.TButton").pack(side="right", padx=6)
        ttk.Button(bottom, text="Reload File", command=self.reload_file, style="Warning.TButton").pack(side="right", padx=6)
        ttk.Button(bottom, text="Save Results", command=self.save_results, style="Accent.TButton").pack(side="right", padx=6)

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(self, textvariable=self.status_var, anchor="w", style="Status.TLabel").pack(fill="x", padx=12, pady=(0,6))

        FOOTER_PHOTO_SIZE = 35  # adjust as needed
        
        footer = tk.Frame(self, bg="#F7F9FB", height=70)  # set fixed height
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)  # prevent shrinking to fit contents
        
        # Center content inside footer
        footer_content = tk.Frame(footer, bg="#F7F9FB")
        footer_content.pack(expand=True)
        
        # Developer details text (center)
        details = tk.Label(
            footer_content,
            text="Developed by Ehtisham Ashraf  |  Contact: 03228411435  |  Dept: Software Engineering, UMT  |  Student ID: F2023065032",
            bg="#F7F9FB", fg="#333",
            font=("Segoe UI", 9, "bold"),
            anchor="center",
            justify="center"
        )
        details.pack(side="left", padx=10)
        
        # Developer photo on right
        dev_holder = tk.Frame(footer_content, bg="#F7F9FB")
        dev_holder.pack(side="right", padx=10)
        
        self._dev_photo = load_circular_image("./shami.jpg", size=FOOTER_PHOTO_SIZE)
        if self._dev_photo is None:
            can = tk.Canvas(dev_holder, width=FOOTER_PHOTO_SIZE, height=FOOTER_PHOTO_SIZE, bg="#F7F9FB", highlightthickness=0)
            can.create_oval(2, 2, FOOTER_PHOTO_SIZE-2, FOOTER_PHOTO_SIZE-2, fill="#8E44AD", outline="")
            can.create_text(FOOTER_PHOTO_SIZE//2, FOOTER_PHOTO_SIZE//2+1, text="EA", fill="white", font=("Segoe UI", 11, "bold"))
            can.pack()
        else:
            tk.Label(dev_holder, image=self._dev_photo, bg="#F7F9FB").pack()


        self.after(200, self._run_start_dialog)

    def _setup_theme(self):
        style = ttk.Style(self)
        try: style.theme_use("clam")
        except: pass
        primary = "#2B90D9"; accent="#8E44AD"; info="#16A085"; success="#27AE60"; warning="#D35400"; runbtn="#E74C3C"
        style.configure("Card.TFrame", background="#F7F9FB")
        style.configure("Group.TLabelframe", background="#F7F9FB")
        style.configure("Group.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("Muted.TLabel", foreground="#555")
        style.configure("Value.TLabel", foreground="#333")
        style.configure("Status.TLabel", background="#F0F3F7", padding=6)
        style.configure("Entry.TEntry", fieldbackground="white")
        style.configure("Caps.TEntry", fieldbackground="#FFF8E6")
        style.configure("Combo.TCombobox", fieldbackground="white")
        style.configure("Fancy.Treeview.Heading", background=primary, foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Fancy.Treeview", rowheight=22)
        def btn(name,bg,fg="white"):
            style.configure(name, background=bg, foreground=fg, padding=(10,6), relief="flat")
            style.map(name, background=[("active", bg)], foreground=[("disabled","#ddd")])
        btn("Primary.TButton", primary); btn("Accent.TButton", accent); btn("Info.TButton", info)
        btn("Success.TButton", success); btn("Warning.TButton", warning); btn("Run.TButton", runbtn)
        style.configure("Caps.TFrame", background="#FFF8E6", padding=4, relief="flat")

    def _draw_gender_icon(self):
        self.icon_canvas.delete("all")
        color = "#3498DB" if self.user_gender == "male" else "#E91E63"
        symbol = "♂" if self.user_gender == "male" else "♀"
        self.icon_canvas.create_oval(2,2,54,54, fill=color, outline="")
        self.icon_canvas.create_text(28,30, text=symbol, fill="white", font=("Segoe UI", 16, "bold"))

    def _run_start_dialog(self):
        dlg = StartDialog(self)
        self.wait_window(dlg)
        if hasattr(dlg, "result"):
            self.user_name = dlg.result["name"] or "User"
            self.user_gender = dlg.result["gender"] or "male"
        else:
            self.user_name = "User"
            self.user_gender = "male"

        self.greet_var.set(f"Hi, {self.user_name}")

        icon_path = "male_icon.png" if self.user_gender.lower() == "male" else "female_icon.png"
        icon_img = load_gender_icon(icon_path, size=56)
        if icon_img:
            self._gender_icon_img = icon_img
            self.icon_canvas.delete("all")
            self.icon_canvas.create_image(28, 28, image=self._gender_icon_img)
        else:
            self._draw_gender_icon()

    def _safe_float_series(self, series) -> List[float]:
        return pd.to_numeric(series, errors="coerce").fillna(0.0).astype(float).tolist()

    def _update_combos(self, cols: List[str]):
        for combo in (self.id_combo, self.name_combo):
            combo.configure(values=["— None —"] + cols)
        self.id_var.set("— None —"); self.name_var.set("— None —")
        for ar in self.assessment_rows.values():
            ar.set_columns(cols)

    def choose_file(self):
        path = filedialog.askopenfilename(title="Select Excel file",
                                          filetypes=[("Excel files","*.xlsx *.xls"), ("All files","*.*")])
        if path:
            self.file_path = path
            self.file_label_var.set(os.path.basename(path))
            self.reload_file()

    def reload_file(self):
        if not self.file_path:
            messagebox.showwarning("No file", "Choose an Excel file first."); return
        try:
            df = pd.read_excel(self.file_path, header=0)
        except Exception as e:
            messagebox.showerror("Read Error", f"Could not read Excel:\n{e}"); return
        self.df = df; self.calc_df = None
        self.status_var.set(f"Loaded {len(df)} rows, {len(df.columns)} columns. Map columns → Calculate.")
        self._update_combos(list(map(str, df.columns)))
        if self.viewer is None or not self.viewer.winfo_exists():
            self.open_viewer()
        self.viewer.mode.set("raw")
        self.viewer.set_data(self.df, self.calc_df)

    def choose_output(self):
        path = filedialog.asksaveasfilename(title="Save Results As", defaultextension=".xlsx",
                                            filetypes=[("Excel Workbook","*.xlsx")])
        if path: self.output_path_var.set(path)

    def autodetect_columns(self):
        if self.df is None:
            messagebox.showwarning("No file", "Load an Excel file first."); return
        cols = [str(c) for c in self.df.columns]
        def find(*keys):
            keys = [k.lower() for k in keys]
            for c in cols:
                s = str(c).strip().lower().replace("_"," ").replace("-"," ")
                if any(k in s for k in keys): return c
            return "— None —"
        self.id_var.set(find("student i","student id","id","roll","reg","registration"))
        self.name_var.set(find("name","student name","full name"))
        mapping = {
            "Midterm": ("mid","mid-term","midterm","mid term","total 25"),
            "Final": ("final","final term","final exam","total 35"),
            "Project": ("project",),
            "Assignments": ("assignment","assignments","assi"),
            "Quizzes": ("quiz","quizzes","qz"),
            "Viva": ("viva","oral"),
        }
        for title, keys in mapping.items():
            self.assessment_rows[title].column_var.set(find(*keys))
        self.status_var.set("Auto-detected columns. Review, set Weightage & Total, then Calculate.")
        if self.viewer: self.viewer.set_data(self.df, self.calc_df)

    def calculate_totals(self):
        if self.df is None:
            messagebox.showwarning("No data", "Load an Excel file first."); return
        seed_text = self.seed_var.get().strip()
        if seed_text:
            try: random.seed(int(seed_text))
            except: random.seed(seed_text)
        df = self.df.copy()
        id_col = self.id_var.get(); name_col = self.name_var.get()
        out = pd.DataFrame()
        out["ID"] = df[id_col].astype(str) if id_col != "— None —" and id_col in df.columns else ""
        out["Name"] = df[name_col].astype(str) if name_col != "— None —" and name_col in df.columns else ""

        for title in ASSESS_ORDER:
            cfg = self.assessment_rows[title].get_config()
            if not cfg["enabled"]:
                continue
            col, W, T = cfg["column"], cfg["weightage"], cfg["totalmarks"]
            w_header = WEIGHT_HEADERS[title]
            t_header = TOTAL_HEADERS[title]
            if col is not None and col in df.columns:
                out[w_header] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float).round(2)
                out[t_header] = scale_weightage(df[col], W, T)
            else:
                out[w_header] = [0.0]*len(df)
                out[t_header] = [0.0]*len(df)

        self.calc_df = out
        self.status_var.set("Calculated totals. Choose CLO target and click 'Distribute CLOs'.")
        if self.viewer: self.viewer.set_data(self.df, self.calc_df)

    def distribute_clos(self):
        if self.calc_df is None:
            messagebox.showwarning("Not calculated", "Click 'Calculate' first."); return
        out = self.calc_df.copy()
        use_weightage = (self.target_mode.get() == "weightage")

        for title in ASSESS_ORDER:
            cfg = self.assessment_rows[title].get_config()
            if not cfg["enabled"]:
                continue
            caps = cfg["caps"]
            w_header = WEIGHT_HEADERS[title]
            t_header = TOTAL_HEADERS[title]
            basis_col = w_header if use_weightage else t_header
            if basis_col not in out.columns:
                continue
            targets = pd.to_numeric(out[basis_col], errors="coerce").fillna(0.0).astype(float).tolist()

            clo_cols = [f"{title} CLO{i}" for i in range(1,5)]
            for c in clo_cols:
                out[c] = 0.0

            for idx, target in enumerate(targets):
                target_capped = min(float(target), float(sum(caps)))
                alloc = allocate_exact_target(target_capped, caps)
                for j in range(4):
                    out.at[idx, clo_cols[j]] = alloc[j]

        self.calc_df = out
        basis_txt = "obtained weightage" if use_weightage else "obtained total marks"
        self.status_var.set(f"CLOs distributed using '{basis_txt}'.")
        if self.viewer: self.viewer.set_data(self.df, self.calc_df)

    def save_results(self):
        if self.calc_df is None:
            messagebox.showwarning("Nothing to save", "Calculate (and Distribute CLOs) first."); return
        out_path = self.output_path_var.get().strip()
        if not out_path:
            self.choose_output(); out_path = self.output_path_var.get().strip()
            if not out_path:
                messagebox.showwarning("No output", "Choose an output file name."); return
        try:
            with pd.ExcelWriter(out_path, engine="openpyxl") as xw:
                self.calc_df.to_excel(xw, index=False, sheet_name="Calculated + CLO")
        except ModuleNotFoundError:
            with pd.ExcelWriter(out_path, engine="xlsxwriter") as xw:
                self.calc_df.to_excel(xw, index=False, sheet_name="Calculated + CLO")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save:\n{e}"); return
        messagebox.showinfo("Success", f"Saved:\n{out_path}")
        self.status_var.set(f"Saved to: {out_path}")

    def open_viewer(self):
        if self.viewer is None or not self.viewer.winfo_exists():
            self.viewer = DataViewer(self, title="CLO Distributor — Data Viewer")
        self.viewer.mode.set("raw")
        self.viewer.set_data(self.df, self.calc_df)
        self.viewer.lift()

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
