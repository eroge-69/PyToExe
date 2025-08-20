# pdf_to_svg_gui.py
# GUI PDF→SVG converter (one SVG per page) using PyMuPDF
# Build to .exe with PyInstaller:
#   pyinstaller --noconsole --onefile --name "PDF_to_SVG_Converter" pdf_to_svg_gui.py

import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

import fitz  # PyMuPDF

APP_TITLE = "PDF → SVG Converter (PyMuPDF)"

def safe_stem(name: str) -> str:
    bad = '<>:"/\\|?*'
    clean = "".join("_" if c in bad else c for c in name)
    clean = clean.strip().rstrip(".")
    return clean or "file"

def unique_path(path: Path) -> Path:
    """
    If path exists, append _1, _2, ... before suffix until unique.
    E.g., name.svg -> name_1.svg, name_2.svg, ...
    """
    if not path.exists():
        return path
    base = path.stem
    suffix = path.suffix
    parent = path.parent
    n = 1
    while True:
        cand = parent / f"{base}_{n}{suffix}"
        if not cand.exists():
            return cand
        n += 1

class ConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.minsize(680, 460)

        # State
        self.selected_files = []
        self.output_dir = None
        self.use_source_var = tk.BooleanVar(value=True)
        self.zoom_var = tk.DoubleVar(value=1.25)
        self.conflict_mode = None  # "overwrite" | "keep_both" | None (no conflicts)

        # UI
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 8}

        frm_top = ttk.Frame(self)
        frm_top.pack(fill="x", **pad)

        btn_select = ttk.Button(frm_top, text="Select PDF(s)…", command=self.select_pdfs)
        btn_select.pack(side="left")

        self.lbl_files = ttk.Label(frm_top, text="No files selected")
        self.lbl_files.pack(side="left", padx=10)

        frm_opts = ttk.LabelFrame(self, text="Output options")
        frm_opts.pack(fill="x", **pad)

        chk_source = ttk.Checkbutton(
            frm_opts,
            text="Save next to each PDF (default)",
            variable=self.use_source_var,
            command=self._toggle_output_dir_state
        )
        chk_source.grid(row=0, column=0, sticky="w", padx=10, pady=6, columnspan=3)

        ttk.Label(frm_opts, text="Or choose a single output folder:").grid(row=1, column=0, sticky="w", padx=10)
        self.txt_out = ttk.Entry(frm_opts, width=60)
        self.txt_out.grid(row=1, column=1, sticky="we", padx=6)
        btn_browse_out = ttk.Button(frm_opts, text="Browse…", command=self.choose_output_dir)
        btn_browse_out.grid(row=1, column=2, padx=6)
        frm_opts.columnconfigure(1, weight=1)

        ttk.Label(frm_opts, text="Detail (zoom):").grid(row=2, column=0, sticky="w", padx=10, pady=(6,10))
        spn_zoom = ttk.Spinbox(frm_opts, from_=0.5, to=3.0, increment=0.05, textvariable=self.zoom_var, width=6)
        spn_zoom.grid(row=2, column=1, sticky="w", padx=6, pady=(6,10))
        ttk.Label(frm_opts, text="(1.0–1.5 typical; higher if strokes look thin)").grid(row=2, column=2, sticky="w", padx=6, pady=(6,10))

        frm_run = ttk.Frame(self)
        frm_run.pack(fill="x", **pad)

        self.btn_convert = ttk.Button(frm_run, text="Start Conversion", command=self.start_conversion, state="disabled")
        self.btn_convert.pack(side="left")

        self.progress = ttk.Progressbar(frm_run, mode="indeterminate")
        self.progress.pack(side="left", fill="x", expand=True, padx=10)

        frm_log = ttk.LabelFrame(self, text="Log")
        frm_log.pack(fill="both", expand=True, **pad)

        self.txt_log = tk.Text(frm_log, height=12, wrap="word")
        self.txt_log.pack(fill="both", expand=True, padx=8, pady=8)

        self._toggle_output_dir_state()

    def log(self, msg: str):
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")
        self.update_idletasks()

    def select_pdfs(self):
        files = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not files:
            return
        self.selected_files = list(files)
        # Default single-output dir to the first file's folder (still overridden by checkbox)
        first_dir = str(Path(self.selected_files[0]).parent)
        self.output_dir = first_dir
        self.txt_out.delete(0, "end")
        self.txt_out.insert(0, first_dir)
        self.lbl_files.config(text=f"{len(self.selected_files)} file(s) selected")
        self.btn_convert.config(state="normal")

    def choose_output_dir(self):
        d = filedialog.askdirectory(title="Choose output folder")
        if not d:
            return
        self.output_dir = d
        self.txt_out.delete(0, "end")
        self.txt_out.insert(0, d)

    def _toggle_output_dir_state(self):
        use_source = self.use_source_var.get()
        state = "disabled" if use_source else "normal"
        self.txt_out.config(state=state)
        for child in self.txt_out.master.winfo_children():
            if isinstance(child, ttk.Button) and child.cget("text").startswith("Browse"):
                child.config(state=state)

    # ---------- Conflict preflight ----------
    def _planned_outputs(self):
        """
        Return a list of (pdf_path, out_dir, planned_svg_path_strings) for preflight.
        """
        tasks = []
        use_source = self.use_source_var.get()
        base_out = Path(self.output_dir) if self.output_dir else None

        for f in self.selected_files:
            pdf_path = Path(f)
            out_dir = pdf_path.parent if use_source else base_out
            base = safe_stem(pdf_path.stem)
            # We don't know page count without opening, so open to enumerate pages
            try:
                with fitz.open(pdf_path) as doc:
                    planned = []
                    for i, _ in enumerate(doc, start=1):
                        out_name = f"{base}_p{i:03}.svg"
                        planned.append(str((out_dir / out_name).resolve()))
                    tasks.append((pdf_path, out_dir, planned))
            except Exception:
                # If cannot open, skip; worker will also report error later
                tasks.append((pdf_path, out_dir, []))
        return tasks

    def _check_conflicts(self):
        """
        Checks filesystem for existing files matching planned outputs.
        Returns (total_conflicts, by_folder_counts: dict[str,int])
        """
        tasks = self._planned_outputs()
        by_folder = {}
        total = 0
        for _, out_dir, planned in tasks:
            cnt = 0
            for p in planned:
                if Path(p).exists():
                    cnt += 1
            if cnt:
                by_folder[str(out_dir)] = by_folder.get(str(out_dir), 0) + cnt
                total += cnt
        return total, by_folder

    def start_conversion(self):
        if not self.selected_files:
            messagebox.showwarning(APP_TITLE, "Please select at least one PDF.")
            return

        if not self.use_source_var.get():
            out_txt = self.txt_out.get().strip()
            if not out_txt:
                messagebox.showwarning(APP_TITLE, "Please choose an output folder or enable 'Save next to each PDF'.")
                return
            self.output_dir = out_txt

        try:
            z = float(self.zoom_var.get())
            if z <= 0:
                raise ValueError
        except Exception:
            messagebox.showwarning(APP_TITLE, "Zoom must be a positive number (e.g., 1.25).")
            return

        # Preflight conflict check
        total_conflicts, by_folder = self._check_conflicts()
        self.conflict_mode = None
        if total_conflicts > 0:
            details = "\n".join([f"  {folder}\n    {count} file(s) with same name"
                                 for folder, count in by_folder.items()])
            prompt = (
                f"{total_conflicts} SVG file(s) with the same name already exist in the destination.\n\n"
                "Choose:\n"
                "  Yes → OVERWRITE existing files\n"
                "  No  → KEEP BOTH (append _1, _2, … to new files)\n"
                "  Cancel → Abort\n\n"
                f"Details:\n{details}"
            )
            ans = messagebox.askyesnocancel(APP_TITLE, prompt, default="no")
            if ans is None:
                # Cancel
                self.log("Conversion cancelled by user.")
                return
            elif ans is True:
                self.conflict_mode = "overwrite"
            else:
                self.conflict_mode = "keep_both"
        else:
            self.conflict_mode = None  # no conflicts, normal write

        self.btn_convert.config(state="disabled")
        self.progress.start(12)
        self.log("Starting conversion…")

        t = threading.Thread(target=self._convert_worker, daemon=True)
        t.start()

    def _convert_worker(self):
        total_pages = 0
        failures = 0
        use_source = self.use_source_var.get()
        zoom = float(self.zoom_var.get())
        mode = self.conflict_mode  # None | "overwrite" | "keep_both"

        for f in self.selected_files:
            pdf_path = Path(f)
            out_dir = pdf_path.parent if use_source else Path(self.output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            base = safe_stem(pdf_path.stem)

            self.log(f"\nProcessing: {pdf_path.name}")
            try:
                doc = fitz.open(pdf_path)
            except Exception as e:
                self.log(f"  ERROR: Cannot open PDF → {e}")
                failures += 1
                continue

            if doc.is_encrypted:
                try:
                    doc.authenticate("")
                except Exception:
                    self.log("  ERROR: Encrypted PDF without password; skipping.")
                    failures += 1
                    doc.close()
                    continue

            mat = fitz.Matrix(zoom, zoom)
            exported = 0

            for i, page in enumerate(doc, start=1):
                try:
                    svg = page.get_svg_image(matrix=mat)
                    out_name = f"{base}_p{i:03}.svg"
                    target = out_dir / out_name

                    if mode == "keep_both":
                        target = unique_path(target)
                    # if mode == "overwrite" → write directly
                    # if mode is None (no conflicts found) → write directly

                    target.write_text(svg, encoding="utf-8")
                    exported += 1
                except Exception as e:
                    self.log(f"  ERROR on page {i}: {e}")

            doc.close()
            self.log(f"  Exported {exported} page(s) → {out_dir}")
            total_pages += exported

        self.progress.stop()
        self.btn_convert.config(state="normal")
        summary = f"\nDone. Total SVG pages exported: {total_pages}"
        if failures:
            summary += f" | Files failed: {failures}"
        self.log(summary)
        messagebox.showinfo(APP_TITLE, summary)

def main():
    app = ConverterApp()
    app.mainloop()

if __name__ == "__main__":
    main()
