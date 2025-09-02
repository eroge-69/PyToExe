# -*- coding: utf-8 -*-
APP_NAME = "DSAS - Delimited File Sorter & Spliter"
APP_VERSION = "1.0.0"  # change as you like
import os
import sys
import time
import heapq
import csv
import tempfile
from dataclasses import dataclass, replace
from typing import List, Tuple, Optional, IO

# GUI (optional if running CLI)
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except Exception:
    tk = None
    ttk = None
    filedialog = None
    messagebox = None

# XLSX support (optional)
try:
    from openpyxl import Workbook
except Exception:
    Workbook = None


# -------------------- Options --------------------
@dataclass
class Options:
    input_path: str
    output_dir: str
    sort_cols_1based: List[int]          # dynamic sort columns (1-based)
    split_col_1based: int = 2            # dynamic split column (1-based)
    delimiter: str = "|"
    expected_cols: int = 30
    part_size: int = 100_000             # rows per output part
    has_header: bool = True
    # memory / chunking
    auto_memory: bool = True
    max_ram_mb: int = 512
    # encoding
    auto_encoding: bool = True
    encoding: Optional[str] = None
    # output
    use_temp_output: bool = True         # write to temp subfolder, then finalize
    output_format: str = "txt"           # "txt", "csv", or "xlsx"
    filename_prefix: str = ""            # prefix in output filenames ONLY (before group value)


# -------------------- THEME HELPERS --------------------
def apply_theme(root, mode="Dark"):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    palettes = {
        "Dark": {
            "bg":        "#000047",
            "surface":   "#151a30",
            "fg":        "#e5e7eb",
            "muted":     "#9ca3af",
            "entry":     "#0f172a",
            "button":    "#1f2937",
            "button_fg": "#e5e7eb",
            "button_hi": "#374151",
            "accent":    "#4f46e5",
            "trough":    "#0f172a",
        },
        "Light": {
            "bg":        "#ADD8E6",
            "surface":   "#EAF4FF", 
            "fg":        "#111827",
            "muted":     "#6b7280",
            "entry":     "#ffffff",
            "button":    "#e5e7eb",
            "button_fg": "#111827",
            "button_hi": "#d1d5db",
            "accent":    "#2563eb",
            "trough":    "#CFE8FF", 
        },
    }
    pal = palettes.get(mode, palettes["Dark"])

    root.configure(bg=pal["bg"])
    # FONT FIX: strings, not tuples
    try:
        root.option_add("*Font", ("Segoe UI", 10))
        root.option_add("*TButton.Font", ("Segoe UI", 10))
        root.option_add("*Treeview.Font", ("Segoe UI", 10))
        root.option_add("*TNotebook.Tab.Font", ("Segoe UI", 10))
    except Exception:
        pass

    style.configure("TFrame", background=pal["surface"])
    style.configure("TLabelframe", background=pal["surface"])
    style.configure("TLabelframe.Label", background=pal["surface"], foreground=pal["fg"])
    style.configure("TLabel", background=pal["surface"], foreground=pal["fg"])
    style.configure("Heading.TLabel", background=pal["surface"], foreground=pal["fg"], font=("Segoe UI Semibold", 12))
    style.configure("TEntry", fieldbackground=pal["entry"], foreground=pal["fg"], background=pal["entry"])
    style.configure("TCombobox", fieldbackground=pal["entry"], foreground=pal["fg"], background=pal["entry"])
    style.configure("TSpinbox", fieldbackground=pal["entry"], foreground=pal["fg"], background=pal["entry"])
    style.configure("TCheckbutton", background=pal["surface"], foreground=pal["fg"])
    style.configure("TButton", background=pal["button"], foreground=pal["button_fg"], borderwidth=1)
    style.map("TButton",
              background=[("active", pal["button_hi"])],
              relief=[("pressed", "sunken"), ("!pressed", "raised")])
    style.configure("Horizontal.TProgressbar", troughcolor=pal["trough"], background=pal["accent"])


# -------------------- Utilities --------------------
def sanitize_filename(name: str, replacement: str = "_") -> str:
    bad = '<>:"/\\|?*'
    out = "".join((c if c not in bad and 31 < ord(c) < 127 else replacement) for c in name)
    return out.strip() or "blank"


def split_columns(line: str, delimiter: str, expected_cols: int) -> List[str]:
    parts = line.rstrip("\n\r").split(delimiter, maxsplit=expected_cols - 1)
    if len(parts) < expected_cols:
        parts += [""] * (expected_cols - len(parts))
    return parts


def make_key(cols: List[str], sort_cols_1based: List[int]):
    return tuple(cols[i - 1] if 1 <= i <= len(cols) else "" for i in sort_cols_1based)


def detect_free_ram_mb() -> Optional[int]:
    try:
        if os.name == "nt":
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                return int(stat.ullAvailPhys // (1024 * 1024))
        else:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        kb = int(line.split()[1])
                        return kb // 1024
    except Exception:
        pass
    return None


def choose_max_ram_mb(auto: bool, manual_mb: int) -> int:
    if not auto:
        return manual_mb
    free = detect_free_ram_mb()
    if not free:
        return manual_mb
    use = int(free * 0.50)
    return max(256, min(4096, use))


def detect_encoding(path: str) -> str:
    try:
        with open(path, "rb") as fb:
            raw = fb.read(65536)
        if raw.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        if raw.startswith(b"\xff\xfe\x00\x00"):
            return "utf-32-le"
        if raw.startswith(b"\x00\x00\xfe\xff"):
            return "utf-32-be"
        if raw.startswith(b"\xff\xfe"):
            return "utf-16-le"
        if raw.startswith(b"\xfe\xff"):
            return "utf-16-be"
        for enc in ("utf-8", "cp1252", "latin-1"):
            try:
                raw.decode(enc)
                return enc
            except Exception:
                continue
    except Exception:
        pass
    return "utf-8"


def estimate_chunk_target_bytes(max_ram_mb: int) -> int:
    return int(max_ram_mb * 1024 * 1024 * 0.60)


def chunk_sort_write(lines: List[str], tmp_dir: str, delimiter: str, expected_cols: int,
                     sort_cols_1based: List[int], chunk_idx: int) -> str:
    keyed = []
    for ln in lines:
        cols = split_columns(ln, delimiter, expected_cols)
        keyed.append((make_key(cols, sort_cols_1based), ln))
    keyed.sort(key=lambda x: x[0])
    out_path = os.path.join(tmp_dir, f"chunk_{chunk_idx:06d}.tmp")
    with open(out_path, "w", encoding="utf-8", newline="", errors="replace") as f:
        for _, ln in keyed:
            f.write(ln)
    return out_path


# -------------------- Sorting pipeline --------------------
def external_sort_to_tempfiles(opts: Options, progress_cb=None) -> Tuple[List[str], Optional[str], int, str]:
    enc = detect_encoding(opts.input_path) if opts.auto_encoding else (opts.encoding or "utf-8")

    chunk_files: List[str] = []
    total_rows = 0
    header_line: Optional[str] = None
    chunk_idx = 0

    target_bytes = estimate_chunk_target_bytes(choose_max_ram_mb(opts.auto_memory, opts.max_ram_mb))
    cur_chunk: List[str] = []
    cur_bytes = 0

    fsize = os.path.getsize(opts.input_path)
    processed_bytes = 0

    with open(opts.input_path, "r", encoding=enc, errors="replace", newline="") as f:
        if opts.has_header:
            header_line = f.readline()
            processed_bytes += len(header_line.encode("utf-8", errors="ignore"))

        for ln in f:
            total_rows += 1
            cur_chunk.append(ln)
            b = len(ln.encode("utf-8", errors="ignore"))
            cur_bytes += b
            processed_bytes += b

            if cur_bytes >= target_bytes:
                out_path = chunk_sort_write(
                    cur_chunk, tempfile.gettempdir(), opts.delimiter,
                    opts.expected_cols, opts.sort_cols_1based, chunk_idx
                )
                chunk_files.append(out_path)
                chunk_idx += 1
                cur_chunk = []
                cur_bytes = 0

                if progress_cb:
                    progress_cb(processed_bytes, fsize, phase="chunking")

        if cur_chunk:
            out_path = chunk_sort_write(
                cur_chunk, tempfile.gettempdir(), opts.delimiter,
                opts.expected_cols, opts.sort_cols_1based, chunk_idx
            )
            chunk_files.append(out_path)

    return chunk_files, header_line, total_rows, enc


def merge_and_split(chunk_files: List[str], header_line: Optional[str], total_rows: int,
                    opts: Options, progress_cb=None) -> None:
    fps: List[IO[str]] = [open(p, "r", encoding="utf-8", errors="replace", newline="") for p in chunk_files]
    try:
        heap = []
        seq = 0

        def push(fp_index: int):
            nonlocal seq
            ln = fps[fp_index].readline()
            if ln:
                cols = split_columns(ln, opts.delimiter, opts.expected_cols)
                key = make_key(cols, opts.sort_cols_1based)
                heapq.heappush(heap, (key, seq, ln, fp_index, cols))
                seq += 1

        for i in range(len(fps)):
            push(i)

        if not os.path.isdir(opts.output_dir):
            os.makedirs(opts.output_dir, exist_ok=True)

        fmt = opts.output_format.lower()
        if fmt not in ("txt", "csv", "xlsx"):
            raise ValueError("output_format must be 'txt', 'csv' or 'xlsx'")
        if fmt == "xlsx" and Workbook is None:
            raise RuntimeError(
                "openpyxl is not installed. Install it on the build machine (pip install openpyxl) "
                "before creating the EXE, or choose TXT/CSV output."
            )

        # Ensure we group contiguously by the split column by sorting with it first if needed
        split_idx_1based = max(1, opts.split_col_1based)
        if opts.sort_cols_1based[0] != split_idx_1based:
            effective_sort = [split_idx_1based] + [c for c in opts.sort_cols_1based if c != split_idx_1based]
        else:
            effective_sort = opts.sort_cols_1based

        # If the effective sort differs, we must re-evaluate keys during merge
        # Rebuild the heap using the effective sort order
        for fp in fps:
            fp.seek(0)
        heap.clear()
        seq = 0

        def push_eff(fp_index: int):
            nonlocal seq
            ln = fps[fp_index].readline()
            if ln:
                cols = split_columns(ln, opts.delimiter, opts.expected_cols)
                key = make_key(cols, effective_sort)
                heapq.heappush(heap, (key, seq, ln, fp_index, cols))
                seq += 1

        for i in range(len(fps)):
            push_eff(i)

        split_idx0 = split_idx_1based - 1

        current_group = None
        part_count = 0
        rows_in_part = 0

        out_fp: Optional[IO[str]] = None
        csv_writer = None
        wb = None
        ws = None
        current_path = None
        ext = fmt

        header_cols = split_columns(header_line, opts.delimiter, opts.expected_cols) if (header_line and opts.has_header) else None

        def write_header():
            nonlocal out_fp, csv_writer, ws
            if not header_cols:
                return
            if fmt == "txt":
                out_fp.write(header_line)
            elif fmt == "csv":
                csv_writer.writerow(header_cols)
            else:
                ws.append(header_cols)

        def close_current():
            nonlocal out_fp, wb, ws, current_path, csv_writer
            if fmt in ("txt", "csv"):
                if out_fp:
                    out_fp.close()
                out_fp = None
                csv_writer = None
            else:
                if wb and current_path:
                    wb.save(current_path)
                wb, ws, current_path = None, None, None

        def open_new_part(group_value: str):
            nonlocal out_fp, wb, ws, current_path, csv_writer, part_count, rows_in_part
            close_current()
            part_count += 1
            rows_in_part = 0
            safe_group = sanitize_filename(group_value)
            safe_prefix = sanitize_filename(opts.filename_prefix) if opts.filename_prefix else ""
            name_core = f"{safe_prefix}{safe_group}" if safe_prefix else safe_group
            out_name = f"{name_core}_part{part_count:03d}.{ext}"
            current_path = os.path.join(opts.output_dir, out_name)

            if fmt == "txt":
                out_fp = open(current_path, "w", encoding="utf-8", newline="")
                write_header()
            elif fmt == "csv":
                out_fp = open(current_path, "w", encoding="utf-8", newline="")
                csv_writer = csv.writer(out_fp, lineterminator="\n")
                write_header()
            else:
                wb = Workbook(write_only=True)
                ws = wb.create_sheet("Sheet1")
                write_header()

        processed_rows = 0

        while heap:
            _, _, ln, fp_index, cols = heapq.heappop(heap)
            push_eff(fp_index)

            group_value = cols[split_idx0] if split_idx0 < len(cols) else ""

            if group_value != current_group:
                current_group = group_value
                part_count = 0
                open_new_part(current_group)

            if rows_in_part >= opts.part_size:
                open_new_part(current_group)

            if fmt == "txt":
                if out_fp is None:
                    open_new_part(current_group)
                out_fp.write(ln)
            elif fmt == "csv":
                if csv_writer is None:
                    open_new_part(current_group)
                csv_writer.writerow(cols)
            else:
                if ws is None:
                    open_new_part(current_group)
                ws.append(cols)

            rows_in_part += 1
            processed_rows += 1

            if progress_cb and processed_rows % 50000 == 0:
                progress_cb(processed_rows, total_rows, phase="merging")

        close_current()

    finally:
        for fp in fps:
            try:
                fp.close()
            except Exception:
                pass
        for p in chunk_files:
            try:
                os.remove(p)
            except Exception:
                pass


def finalize_from_temp(temp_dir: str, final_dir: str):
    for name in os.listdir(temp_dir):
        src = os.path.join(temp_dir, name)
        dst = os.path.join(final_dir, name)
        if os.path.isfile(src):
            os.replace(src, dst)
    try:
        os.rmdir(temp_dir)
    except OSError:
        pass


def run_engine(opts: Options, gui_progress=None):
    start = time.time()

    if not os.path.isdir(opts.output_dir):
        os.makedirs(opts.output_dir, exist_ok=True)

    using_temp = bool(opts.use_temp_output)
    if using_temp:
        stamp = time.strftime("%Y%m%d_%H%M%S")
        temp_out = os.path.join(opts.output_dir, f".partial_{stamp}_{os.getpid()}")
        os.makedirs(temp_out, exist_ok=True)
        work_opts = replace(opts, output_dir=temp_out)
    else:
        work_opts = opts

    chunk_files, header_line, total_rows, detected_enc = external_sort_to_tempfiles(work_opts, progress_cb=gui_progress)
    merge_and_split(chunk_files, header_line, total_rows, work_opts, progress_cb=gui_progress)

    if using_temp:
        finalize_from_temp(work_opts.output_dir, opts.output_dir)

    end = time.time()
    return end - start, total_rows, detected_enc

def show_about(parent):
    # Minimal, no extra files needed
    from tkinter import messagebox
    try:
        tk_version = parent.tk.call("info", "patchlevel")
    except Exception:
        tk_version = "unknown"
    lines = [
        f"{APP_NAME}",
        f"Version {APP_VERSION}",
        "",
        "sort & split for large delimited files.",
        "TXT / CSV / XLSX • Drag-and-drop sort • Safe and Fast",
        "By Sourabh Mishra",
        f"Python: {sys.version.split()[0]}",
        f"Tk: {tk_version}",
    ]
    messagebox.showinfo("About", "\n".join(lines), parent=parent)

# -------------------- GUI --------------------
def build_gui():
    if tk is None:
        print("Tkinter not available. Use CLI:\n"
              "python sort_and_split_psv_gui.py --in <input.txt> --out <output_dir> --sort-cols 2,3 --split-col 2")
        return

    root = tk.Tk()
    root.title("DSAS - Delimited File Sort & Split")
    
    # Menu bar with Help -> About
    menubar = tk.Menu(root)
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="About...", command=lambda: show_about(root))
    menubar.add_cascade(label="Help", menu=help_menu)
    root.config(menu=menubar)    

    # THEME
    theme_var = tk.StringVar(value="Light")
    apply_theme(root, mode=theme_var.get())

    in_path = tk.StringVar()
    out_dir = tk.StringVar()
    has_header = tk.BooleanVar(value=True)

    # memory
    auto_mem = tk.BooleanVar(value=True)
    ram_mb = tk.IntVar(value=512)

    # encoding
    auto_enc = tk.BooleanVar(value=True)
    enc_val = tk.StringVar(value="utf-8")

    # output
    use_temp = tk.BooleanVar(value=True)
    fmt = tk.StringVar(value="txt")  # "txt", "csv", "xlsx"
    filename_prefix = tk.StringVar(value="")
    split_size = tk.IntVar(value=100_000)

    # input separator
    sep_choice = tk.StringVar(value="|")
    sep_custom = tk.StringVar(value="")

    # dynamic split column
    split_col = tk.IntVar(value=2)            # 1-based

    # expected columns (user-adjustable)
    expected_cols = tk.IntVar(value=30)
    detected_cols_label = tk.StringVar(value="Detected: -")

    frm = ttk.Frame(root, padding=12)
    frm.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1); root.rowconfigure(0, weight=1)

    # Row 0: Theme
    ttk.Label(frm, text="Theme:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
    theme_combo = ttk.Combobox(frm, textvariable=theme_var, values=["Dark", "Light"], state="readonly", width=10)
    theme_combo.grid(row=0, column=1, sticky="w", padx=6, pady=4)
    theme_combo.bind("<<ComboboxSelected>>", lambda *_: apply_theme(root, mode=theme_var.get()))
    ttk.Label(frm, text="Utility To Sort and Split Delimited Files - Pocket Version", style="Heading.TLabel").grid(row=0, column=2, columnspan=2, sticky="e", padx=6)

    # Row 1: Input
    ttk.Label(frm, text="Input file:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
    ttk.Entry(frm, textvariable=in_path, width=60).grid(row=1, column=1, columnspan=2, sticky="we", padx=6, pady=4)
    ttk.Button(frm, text="Browse...", command=lambda: in_path.set(filedialog.askopenfilename(
        title="Select input file", filetypes=[("Text files", "*.txt *.psv *.csv"), ("All files", "*.*")]
    ) or in_path.get())).grid(row=1, column=3, padx=6, pady=4)

    # Row 2: Output
    ttk.Label(frm, text="Output folder:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
    ttk.Entry(frm, textvariable=out_dir, width=60).grid(row=2, column=1, columnspan=2, sticky="we", padx=6, pady=4)
    ttk.Button(frm, text="Browse...", command=lambda: out_dir.set(filedialog.askdirectory(
        title="Select output folder"
    ) or out_dir.get())).grid(row=2, column=3, padx=6, pady=4)

    # Row 3: Header + Temp
    ttk.Checkbutton(frm, text="File has header row", variable=has_header).grid(row=3, column=0, sticky="w", padx=6, pady=4)
    ttk.Checkbutton(frm, text="Write to temp folder then finalize (safer)", variable=use_temp).grid(row=3, column=1, sticky="w", padx=6, pady=4)

    # Row 4: Memory
    ttk.Checkbutton(frm, text="Auto memory (chunk size)", variable=auto_mem).grid(row=4, column=0, sticky="w", padx=6, pady=4)
    ttk.Label(frm, text="Target RAM (MB):").grid(row=4, column=1, sticky="e", padx=6, pady=4)
    mem_spin = ttk.Spinbox(frm, from_=128, to=8192, textvariable=ram_mb, width=10, increment=64)
    mem_spin.grid(row=4, column=2, sticky="w", padx=6, pady=4)

    # Row 5: Encoding
    ttk.Checkbutton(frm, text="Auto encoding", variable=auto_enc).grid(row=5, column=0, sticky="w", padx=6, pady=4)
    ttk.Label(frm, text="Encoding (manual):").grid(row=5, column=1, sticky="e", padx=6, pady=4)
    enc_combo = ttk.Combobox(frm, textvariable=enc_val,
                             values=["utf-8", "utf-8-sig", "cp1252", "latin-1", "utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"],
                             state="readonly", width=14)
    enc_combo.grid(row=5, column=2, sticky="w", padx=6, pady=4)

    def toggle_auto_mem(*_):
        mem_spin.config(state=("disabled" if auto_mem.get() else "normal"))
    def toggle_auto_enc(*_):
        enc_combo.config(state=("disabled" if auto_enc.get() else "readonly"))
    toggle_auto_mem(); toggle_auto_enc()
    auto_mem.trace_add("write", toggle_auto_mem)
    auto_enc.trace_add("write", toggle_auto_enc)

    # Row 6: Output format + filename prefix
    ttk.Label(frm, text="Output format:").grid(row=6, column=0, sticky="w", padx=6, pady=4)
    fmt_combo = ttk.Combobox(frm, textvariable=fmt, values=["txt", "csv", "xlsx"], state="readonly", width=10)
    fmt_combo.grid(row=6, column=1, sticky="w", padx=6, pady=4)
    ttk.Label(frm, text="Filename prefix:").grid(row=6, column=2, sticky="e", padx=6, pady=4)
    ttk.Entry(frm, textvariable=filename_prefix, width=20).grid(row=6, column=3, sticky="w", padx=6, pady=4)

    # Row 7: Rows per part + expected cols
    ttk.Label(frm, text="Rows per part:").grid(row=7, column=0, sticky="w", padx=6, pady=4)
    ttk.Spinbox(frm, from_=10_000, to=10_000_000, increment=10_000, textvariable=split_size, width=14).grid(row=7, column=1, sticky="w", padx=6, pady=4)
    ttk.Label(frm, text="Expected columns:").grid(row=7, column=2, sticky="e", padx=6, pady=4)
    ttk.Spinbox(frm, from_=1, to=500, textvariable=expected_cols, width=10).grid(row=7, column=3, sticky="w", padx=6, pady=4)

    # Row 8: Input separator
    ttk.Label(frm, text="Input separator:").grid(row=8, column=0, sticky="w", padx=6, pady=4)
    sep_combo = ttk.Combobox(frm, textvariable=sep_choice, values=["|", ",", "\\t", ";", "custom"], state="readonly", width=10)
    sep_combo.grid(row=8, column=1, sticky="w", padx=6, pady=4)
    sep_entry = ttk.Entry(frm, textvariable=sep_custom, width=10, state="disabled")
    sep_entry.grid(row=8, column=2, sticky="w", padx=6, pady=4)
    def on_sep_change(*_):
        sep_entry.config(state=("normal" if sep_choice.get() == "custom" else "disabled"))
    sep_combo.bind("<<ComboboxSelected>>", on_sep_change)

    # Row 9 & 10: Drag & Drop Sort UI + Split column
    ttk.Label(frm, text="Split by column (1-based):").grid(row=9, column=0, sticky="w", padx=6, pady=4)
    ttk.Spinbox(frm, from_=1, to=500, textvariable=split_col, width=10).grid(row=9, column=1, sticky="w", padx=6, pady=4)

    ttk.Label(frm, text="Available columns").grid(row=9, column=2, sticky="w", padx=6, pady=4)
    ttk.Label(frm, text="Sort order (drag to reorder)").grid(row=9, column=3, sticky="w", padx=6, pady=4)

    lb_available = tk.Listbox(frm, height=8, exportselection=False)
    lb_sort = tk.Listbox(frm, height=8, exportselection=False)
    lb_available.grid(row=10, column=2, sticky="we", padx=6, pady=4)
    lb_sort.grid(row=10, column=3, sticky="we", padx=6, pady=4)

    btns = ttk.Frame(frm); btns.grid(row=11, column=2, columnspan=2, sticky="w", padx=6, pady=2)
    add_btn = ttk.Button(btns, text="Add ->")
    rem_btn = ttk.Button(btns, text="<- Remove")
    up_btn  = ttk.Button(btns, text="Up")
    dn_btn  = ttk.Button(btns, text="Down")
    add_btn.pack(side="left", padx=4); rem_btn.pack(side="left", padx=4)
    up_btn.pack(side="left", padx=12); dn_btn.pack(side="left", padx=4)

    def populate_available(headers=None):
        lb_available.delete(0, "end")
        n = expected_cols.get()
        if headers:
            for i, name in enumerate(headers, start=1):
                shown = f"{i}: {name.strip()[:60]}" if name else f"{i}"
                lb_available.insert("end", shown)
        else:
            for i in range(1, n + 1):
                lb_available.insert("end", str(i))

    def add_selected(_ev=None):
        for i in lb_available.curselection():
            item = lb_available.get(i)
            if item not in lb_sort.get(0, "end"):
                lb_sort.insert("end", item)

    def remove_selected(_ev=None):
        sel = list(lb_sort.curselection())
        sel.reverse()
        for i in sel:
            lb_sort.delete(i)

    add_btn.configure(command=add_selected)
    rem_btn.configure(command=remove_selected)
    lb_available.bind("<Double-Button-1>", add_selected)
    lb_sort.bind("<Double-Button-1>", remove_selected)

    def move_up():
        sel = lb_sort.curselection()
        if not sel: return
        i = sel[0]
        if i == 0: return
        item = lb_sort.get(i)
        lb_sort.delete(i)
        lb_sort.insert(i - 1, item)
        lb_sort.selection_set(i - 1)

    def move_down():
        sel = lb_sort.curselection()
        if not sel: return
        i = sel[0]
        if i == lb_sort.size() - 1: return
        item = lb_sort.get(i)
        lb_sort.delete(i)
        lb_sort.insert(i + 1, item)
        lb_sort.selection_set(i + 1)

    up_btn.configure(command=move_up)
    dn_btn.configure(command=move_down)

    # Drag & drop within the Sort list
    _drag = {"start": None}
    def on_press(event):
        _drag["start"] = lb_sort.nearest(event.y)
    def on_motion(event):
        i = lb_sort.nearest(event.y)
        if _drag["start"] is None or i == _drag["start"]:
            return
        item = lb_sort.get(_drag["start"])
        lb_sort.delete(_drag["start"])
        lb_sort.insert(i, item)
        lb_sort.selection_clear(0, "end")
        lb_sort.selection_set(i)
        _drag["start"] = i
    def on_release(_event):
        _drag["start"] = None
    lb_sort.bind("<ButtonPress-1>", on_press)
    lb_sort.bind("<B1-Motion>", on_motion)
    lb_sort.bind("<ButtonRelease-1>", on_release)

    def get_sort_order_indices():
        result = []
        for item in lb_sort.get(0, "end"):
            idx = item.split(":", 1)[0].strip()  # "5: Header" or "5"
            if idx.isdigit():
                result.append(int(idx))
        return result

    # initial fill (numbers until user detects headers)
    populate_available()

    # Row 12: Detect columns preview
    ttk.Label(frm, textvariable=detected_cols_label).grid(row=12, column=0, columnspan=4, sticky="w", padx=6, pady=4)

    def map_separator(choice: str, custom_val: str) -> str:
        if choice == "\\t":
            return "\t"
        if choice == "custom":
            return custom_val or "|"
        return choice

    def detect_columns_preview_and_update_lists():
        p = in_path.get().strip()
        if not p:
            detected_cols_label.set("Detected: (no file selected)")
            return
        delim = map_separator(sep_choice.get(), sep_custom.get())
        enc = detect_encoding(p) if auto_enc.get() else (enc_val.get() or "utf-8")
        try:
            with open(p, "r", encoding=enc, errors="replace") as f:
                first = f.readline()
            cols = first.rstrip("\r\n").split(delim) if first else []
            count = len(cols)
            # keep user value if higher; otherwise raise to detected count
            expected_cols.set(max(expected_cols.get(), count))
            # preview
            preview = []
            for i, name in enumerate(cols[:12], start=1):
                short = name if len(name) <= 30 else name[:27] + "..."
                label = short if has_header.get() else "value"
                preview.append(f"{i}: {label}")
            suffix = " (header)" if has_header.get() else " (from first row)"
            detected_cols_label.set(f"Detected: {count} columns{suffix} | " + " | ".join(preview))
            # update Available with headers if we have a header
            populate_available(headers=cols if has_header.get() else None)
        except Exception as e:
            detected_cols_label.set(f"Detect error: {e}")

    ttk.Button(frm, text="Detect columns from file",
               command=detect_columns_preview_and_update_lists
               ).grid(row=12, column=3, sticky="e", padx=6, pady=4)

    # Row 13+: Progress/Status
    ttk.Separator(frm).grid(row=13, column=0, columnspan=4, sticky="we", pady=10)
    progress = ttk.Progressbar(frm, orient="horizontal", mode="determinate", length=480)
    progress.grid(row=14, column=0, columnspan=4, sticky="we", padx=6, pady=6)
    eta_lbl = ttk.Label(frm, text="ETA: --:--:--"); eta_lbl.grid(row=15, column=0, columnspan=4, sticky="w", padx=6, pady=4)
    status_lbl = ttk.Label(frm, text="Status: Idle"); status_lbl.grid(row=16, column=0, columnspan=4, sticky="w", padx=6, pady=4)

    btn_frame = ttk.Frame(frm); btn_frame.grid(row=17, column=0, columnspan=4, sticky="e", pady=(8, 0))
    start_btn = ttk.Button(btn_frame, text="Start"); start_btn.pack(side="right", padx=6)
    ttk.Button(btn_frame, text="Quit", command=root.destroy).pack(side="right", padx=6)
    

    def update_eta(done, total, phase):
        if not hasattr(update_eta, "start_time") or getattr(update_eta, "phase", None) != phase:
            update_eta.start_time = time.time()
            update_eta.phase = phase
        elapsed = max(time.time() - update_eta.start_time, 1e-6)
        rate = done / elapsed if elapsed > 0 else 0.0
        remain = (total - done) / rate if rate > 0 else 0.0
        h = int(remain) // 3600; m = (int(remain) % 3600) // 60; s = int(remain) % 60
        eta_lbl.config(text=f"ETA ({phase}): {h:02d}:{m:02d}:{s:02d}")

    def gui_progress_cb(done, total, phase):
        progress["maximum"] = 1000
        percent = 0 if total == 0 else int(1000 * done / total)
        progress["value"] = percent
        update_eta(done, total, phase)
        status_lbl.config(text=f"Status: {phase} {done}/{total}")
        root.update_idletasks()

    def on_start():
        inp = in_path.get().strip(); outp = out_dir.get().strip()
        if not inp:
            messagebox.showerror("Input required", "Please choose an input file."); return
        if not outp:
            messagebox.showerror("Output required", "Please choose an output folder."); return

        cols_list = get_sort_order_indices()
        if not cols_list:
            messagebox.showerror("Sort order", "Please add at least one column to the Sort order list."); return
        if split_size.get() <= 0:
            messagebox.showerror("Split size", "Rows per part must be > 0."); return
        if split_col.get() <= 0:
            messagebox.showerror("Split column", "Split-by column must be >= 1."); return

        # Resolve input separator
        delim = map_separator(sep_choice.get(), sep_custom.get())

        # IMPORTANT: ensure split column is primary in sort to keep groups contiguous
        split_primary = split_col.get()
        if cols_list[0] != split_primary:
            cols_list = [split_primary] + [c for c in cols_list if c != split_primary]

        start_btn.config(state="disabled")
        status_lbl.config(text="Status: chunking..."); root.update_idletasks()

        opts = Options(
            input_path=inp,
            output_dir=outp,
            sort_cols_1based=cols_list,
            split_col_1based=split_primary,
            has_header=has_header.get(),
            auto_memory=auto_mem.get(),
            max_ram_mb=ram_mb.get(),
            auto_encoding=auto_enc.get(),
            encoding=enc_val.get(),
            part_size=split_size.get(),
            use_temp_output=use_temp.get(),
            output_format=fmt.get(),
            filename_prefix=filename_prefix.get(),
            delimiter=delim,
            expected_cols=expected_cols.get(),
        )
        try:
            total_secs, total_rows, used_enc = run_engine(opts, gui_progress=gui_progress_cb)
            messagebox.showinfo("Done",
                                f"Completed.\nRows processed: {total_rows}\nTime: {total_secs:.1f}s\nEncoding: {used_enc}")
            status_lbl.config(text="Status: Done"); progress["value"] = progress["maximum"]
            eta_lbl.config(text="ETA: 00:00:00")
        except Exception as e:
            messagebox.showerror("Error", str(e)); status_lbl.config(text="Status: Error")
        finally:
            start_btn.config(state="normal")

    start_btn.config(command=on_start)
    root.mainloop()


# -------------------- CLI (optional) --------------------
def main_cli(argv: List[str]):
    import argparse
    ap = argparse.ArgumentParser(description="External sort & split for delimited files")
    ap.add_argument("--in", dest="inp", required=False, help="Input file (.txt/.psv/.csv)")
    ap.add_argument("--out", dest="out", required=False, help="Output folder")
    ap.add_argument("--sort-cols", dest="cols", default="2",
                    help="Comma-separated 1-based sort columns, e.g. 2,3,5")
    ap.add_argument("--split-col", type=int, default=2, help="1-based column to split by")
    ap.add_argument("--in-sep", default="|", help="Input separator (single char) or 'tab'")
    ap.add_argument("--expected-cols", type=int, default=30, help="Expected total columns (pad if short)")
    ap.add_argument("--no-header", action="store_true", help="Input has no header row")

    ap.add_argument("--auto-mem", action="store_true", help="Auto memory (chunk size)")
    ap.add_argument("--ram-mb", type=int, default=512, help="Target RAM for chunking (MB) if not auto")

    ap.add_argument("--auto-encoding", action="store_true", help="Auto encoding")
    ap.add_argument("--encoding", default="utf-8", help="Encoding to read if not auto")

    ap.add_argument("--no-temp", action="store_true", help="Write directly to output folder (no temp finalize)")
    ap.add_argument("--format", choices=["txt", "csv", "xlsx"], default="txt", help="Output format")

    ap.add_argument("--filename-prefix", default="", help="Prefix before group value in output filenames")
    ap.add_argument("--split-size", type=int, default=100_000, help="Rows per output part")

    args = ap.parse_args(argv)

    if args.inp and args.out:
        # Parse sort columns
        sort_cols = []
        for part in args.cols.split(","):
            part = part.strip()
            if part:
                if not part.isdigit():
                    print(f"Invalid sort column: {part}")
                    return
                sort_cols.append(int(part))
        if not sort_cols:
            sort_cols = [2]

        # ensure split column comes first
        if sort_cols[0] != args.split_col:
            sort_cols = [args.split_col] + [c for c in sort_cols if c != args.split_col]

        sep = "\t" if args.in_sep.lower() == "tab" else args.in_sep
        opts = Options(
            input_path=args.inp,
            output_dir=args.out,
            sort_cols_1based=sort_cols,
            split_col_1based=max(1, args.split_col),
            has_header=not args.no_header,
            auto_memory=bool(args.auto_mem),
            max_ram_mb=args.ram_mb,
            auto_encoding=bool(args.auto_encoding),
            encoding=args.encoding,
            use_temp_output=not args.no_temp,
            output_format=args.format,
            filename_prefix=args.filename_prefix,
            part_size=max(1, args.split_size),
            delimiter=sep,
            expected_cols=max(1, args.expected_cols),
        )
        total_secs, total_rows, used_enc = run_engine(opts)
        print(f"Done. Rows={total_rows}, Time={total_secs:.1f}s, Encoding={used_enc}")
    else:
        build_gui()


if __name__ == "__main__":
    main_cli(sys.argv[1:])
