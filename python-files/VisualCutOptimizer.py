#!/usr/bin/env python3
# Visual Cut Optimizer — classic layout + Beginning Waste + amount/size input
# Runs with Python 3 standard library only.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass
from typing import List, Tuple
import csv

def parse_len_str(s: str) -> float:
    """Parse a length field.
    If the string contains a dot with EXACTLY three digits after it (e.g., '1.975'),
    and removing the dot yields a number > 999, interpret it as thousands-style -> 1975.
    Otherwise, parse normally as float. Examples:
      '1.975' -> 1975.0;  '2.4' -> 2.4;  '0.850' -> 0.85;  '12.345' -> 12345.0
    Kerf values are not parsed with this function.
    """
    s = s.strip()
    if '.' in s:
        try:
            pre, post = s.split('.', 1)
            if pre.isdigit() and post.isdigit() and len(post) == 3:
                candidate = int(pre + post)
                if candidate > 999:
                    return float(candidate)
        except Exception:
            pass
    return float(s)

@dataclass
class Piece:
    length: float
    label: str
    id: int

@dataclass
class Plank:
    segments: List[Piece]  # in order placed
    used: float            # includes beginning_waste + kerfs + pieces
    waste: float           # trailing waste (excludes beginning_waste)

class CutOptimizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Visual Cut Optimizer")
        self.geometry("1000x700")
        self.minsize(900, 600)

        ttk.Style(self).theme_use("clam")

        # state
        self._next_piece_id = 1
        self.last_planks: List[Plank] = []
        self.last_units = "mm"
        self.last_plank_length = 0.0
        self.last_kerf = 0.0
        self.last_beginning_waste = 0.0

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Plank length:").grid(row=0, column=0, sticky="w")
        self.plank_length_var = tk.StringVar(value="2400")
        ttk.Entry(top, textvariable=self.plank_length_var, width=12).grid(row=0, column=1, padx=(5, 15))

        ttk.Label(top, text="Saw kerf per cut:").grid(row=0, column=2, sticky="w")
        self.kerf_var = tk.StringVar(value="3")
        ttk.Entry(top, textvariable=self.kerf_var, width=8).grid(row=0, column=3, padx=(5, 15))

        ttk.Label(top, text="Beginning waste at start:").grid(row=0, column=4, sticky="w")
        self.beginning_waste_var = tk.StringVar(value="0")
        ttk.Entry(top, textvariable=self.beginning_waste_var, width=8).grid(row=0, column=5, padx=(5, 15))

        ttk.Label(top, text="Units:").grid(row=0, column=6, sticky="w")
        self.units_var = tk.StringVar(value="mm")
        ttk.Entry(top, textvariable=self.units_var, width=8).grid(row=0, column=7, padx=(5, 0))

        ttk.Label(top, text="Enter cutting list below (one per line: length[, qty][, label]  or  qty/length)").grid(row=1, column=0, columnspan=8, sticky="w", pady=(8,0))

        self.input_text = tk.Text(self, height=8, wrap="none", font=("Consolas", 11))
        self.input_text.pack(side=tk.TOP, fill=tk.X, padx=10)
        self.input_text.insert("1.0",
"""Examples:
800, 2, shelves
1200, 1, top
300, 4
600
# OR amount/size lines:
5/800
3/600
""")

        btns = ttk.Frame(self, padding=(10, 8))
        btns.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(btns, text="Calculate layout", command=self.calculate).pack(side=tk.LEFT)
        ttk.Button(btns, text="Clear results", command=self.clear_results).pack(side=tk.LEFT, padx=8)
        ttk.Button(btns, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=8)

        body = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        left = ttk.Frame(body)
        body.add(left, weight=1)

        cols = ("Plank #", "Pieces", "Used", "Waste")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, stretch=True, anchor="center")
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.summary_var = tk.StringVar(value="")
        ttk.Label(left, textvariable=self.summary_var, padding=(0,6)).pack(side=tk.TOP, anchor="w")

        right = ttk.Frame(body)
        body.add(right, weight=2)

        self.canvas = tk.Canvas(right, bg="#fafafa")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self._redraw_canvas())

    # ---------- parsing ----------
    def parse_input(self) -> Tuple[float, float, float, str, List[Piece]]:
        try:
            plank_length = parse_len_str(self.plank_length_var.get())
            if plank_length <= 0: raise ValueError
        except Exception:
            raise ValueError("Plank length must be a number > 0.")

        try:
            kerf = float(self.kerf_var.get())
            if kerf < 0: raise ValueError
        except Exception:
            raise ValueError("Saw kerf must be a non-negative number.")

        try:
            beginning_waste = parse_len_str(self.beginning_waste_var.get())
            if beginning_waste < 0: raise ValueError
        except Exception:
            raise ValueError("Beginning waste must be a non-negative number.")

        units = (self.units_var.get() or "").strip() or "units"

        raw = self.input_text.get("1.0", "end").strip()
        if not raw:
            raise ValueError("Please enter at least one line in the cutting list.")

        pieces: List[Piece] = []
        self._next_piece_id = 1

        for line in raw.splitlines():
            s = line.strip()
            if not s or s.lower().startswith("example") or s.startswith("#"):
                continue

            # amount/size format like "5/2000"
            if ("/" in s) and ("," not in s):
                try:
                    amt_str, size_str = s.split("/", 1)
                    qty = int(float(amt_str.strip()))
                    length = parse_len_str(size_str)
                    if qty <= 0 or length <= 0:
                        raise ValueError
                    for _ in range(qty):
                        pieces.append(Piece(length=length, label=f"{length:g}", id=self._next_piece_id))
                        self._next_piece_id += 1
                    continue
                except Exception:
                    raise ValueError(f"Invalid amount/size format on line: '{line}'")

            # CSV-ish formats
            parts = [p.strip() for p in s.split(",")]
            if len(parts) == 0 or parts[0] == "":
                continue
            try:
                length = parse_len_str(parts[0])
                if length <= 0: raise ValueError
            except Exception:
                raise ValueError(f"Invalid length on line: '{line}'")

            qty = 1
            label = parts[0]
            if len(parts) >= 2 and parts[1] != "":
                # if numeric -> quantity, else label
                try:
                    qty = int(float(parts[1]))
                    if qty <= 0: raise ValueError
                except Exception:
                    qty = 1
                    label = f"{parts[0]} {parts[1]}"
            if len(parts) >= 3 and parts[2] != "":
                label = parts[2]

            for _ in range(qty):
                pieces.append(Piece(length=length, label=label, id=self._next_piece_id))
                self._next_piece_id += 1

        if not pieces:
            raise ValueError("No valid pieces parsed from the cutting list.")

        return plank_length, kerf, beginning_waste, units, pieces

    # ---------- optimization ----------
    def optimize(self, plank_length: float, kerf: float, beginning_waste: float, pieces: List[Piece]) -> List[Plank]:
        # First-Fit Decreasing
        available_length = max(0.0, plank_length - beginning_waste)
        pieces_sorted = sorted(pieces, key=lambda p: p.length, reverse=True)
        planks: List[Plank] = []

        for piece in pieces_sorted:
            placed = False
            for plank in planks:
                # compute used *after* the initial waste for this plank
                length_used_by_pieces = sum(p.length for p in plank.segments)
                kerfs_in_plank = max(0, len(plank.segments) - 1) * kerf
                if length_used_by_pieces + kerfs_in_plank + (kerf if plank.segments else 0.0) + piece.length <= available_length + 1e-9:
                    if plank.segments:
                        plank.used += kerf
                    plank.segments.append(piece)
                    plank.used += piece.length
                    placed = True
                    break
            if not placed:
                # start a new plank: used starts at beginning_waste + first piece
                new_used = beginning_waste + piece.length
                planks.append(Plank(segments=[piece], used=new_used, waste=0.0))

        # finalize wastes
        for plank in planks:
            trailing = max(0.0, plank_length - plank.used)
            plank.waste = trailing

        return planks

    # ---------- actions ----------
    def calculate(self):
        try:
            plank_length, kerf, beginning_waste, units, pieces = self.parse_input()
        except Exception as e:
            messagebox.showerror("Input error", str(e))
            return

        planks = self.optimize(plank_length, kerf, beginning_waste, pieces)

        self.last_planks = planks
        self.last_units = units
        self.last_plank_length = plank_length
        self.last_kerf = kerf
        self.last_beginning_waste = beginning_waste

        # table
        for row in self.tree.get_children():
            self.tree.delete(row)

        total_used = 0.0
        total_trailing_waste = 0.0
        total_beginning_waste = beginning_waste * len(planks)

        for i, plank in enumerate(planks, start=1):
            piece_labels = " | ".join(f"{p.length:g}" for p in plank.segments)
            self.tree.insert("", "end", values=(i, piece_labels, f"{plank.used:g}", f"{plank.waste:g}"))
            total_used += plank.used
            total_trailing_waste += plank.waste

        self.summary_var.set(
            f"Planks needed: {len(planks)}    "
            f"Total used (incl. beginning waste): {total_used:g} {self.last_units}    "
            f"Beginning waste total: {total_beginning_waste:g} {self.last_units}    "
            f"Trailing waste total: {total_trailing_waste:g} {self.last_units}"
        )

        self._redraw_canvas()

    def clear_results(self):
        self.last_planks = []
        self.summary_var.set("")
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.canvas.delete("all")

    def export_csv(self):
        if not self.last_planks:
            messagebox.showinfo("Export CSV", "No results to export. Please calculate first.")
            return
        path = filedialog.asksaveasfilename(
            title="Export CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="cut_layout.csv"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Settings"])
                writer.writerow(["Plank length", self.last_plank_length, self.last_units])
                writer.writerow(["Kerf per cut", self.last_kerf, self.last_units])
                writer.writerow(["Beginning waste", self.last_beginning_waste, self.last_units])
                writer.writerow([])
                writer.writerow(["Plank #", "Segment index", "Piece length", "Kerf before?", "Cumulative used (incl. beginning waste)"])
                for i, plank in enumerate(self.last_planks, start=1):
                    cum = self.last_beginning_waste
                    for j, piece in enumerate(plank.segments, start=1):
                        kerf_before = "no" if j == 1 else "yes"
                        if j > 1:
                            cum += self.last_kerf
                        cum += piece.length
                        writer.writerow([i, j, f"{piece.length:g}", kerf_before, f"{cum:g}"])
                    writer.writerow([i, "", "", "", f"Trailing waste: {plank.waste:g} {self.last_units}"])
                writer.writerow([])
                total_used = sum(p.used for p in self.last_planks)
                total_trailing_waste = sum(p.waste for p in self.last_planks)
                writer.writerow(["Summary"])
                writer.writerow(["Planks", len(self.last_planks)])
                writer.writerow(["Total used (incl. beginning waste)", f"{total_used:g} {self.last_units}"])
                writer.writerow(["Beginning waste total", f"{self.last_beginning_waste * len(self.last_planks):g} {self.last_units}"])
                writer.writerow(["Trailing waste total", f"{total_trailing_waste:g} {self.last_units}"])
        except Exception as e:
            messagebox.showerror("Export error", str(e))
            return
        messagebox.showinfo("Export CSV", f"Saved to:\n{path}")

    # ---------- drawing ----------
    def _redraw_canvas(self):
        c = self.canvas
        c.delete("all")
        planks = self.last_planks
        if not planks:
            c.create_text(10, 10, text="Layout preview will appear here after you calculate.", anchor="nw", fill="#444")
            return

        width = c.winfo_width()
        height = c.winfo_height()
        margin = 40
        plank_gap = 26
        bar_height = 20

        usable_w = max(50, width - 2 * margin)
        if self.last_plank_length <= 0:
            return
        scale = usable_w / self.last_plank_length

        y = margin
        font = ("Arial", 10)

        for idx, plank in enumerate(planks, start=1):
            c.create_text(10, y + bar_height/2, text=f"Plank {idx}", anchor="w", font=font, fill="#333")

            x0 = margin
            x1 = margin + self.last_plank_length * scale
            bar_y0 = y
            bar_y1 = y + bar_height

            # outline
            c.create_rectangle(x0, bar_y0, x1, bar_y1, outline="#666")

            cursor = x0

            # beginning waste block
            if self.last_beginning_waste > 0:
                bw = self.last_beginning_waste * scale
                c.create_rectangle(cursor, bar_y0, cursor + bw, bar_y1, fill="#ffd9a3", outline="#e6b36a")  # orange
                c.create_text(cursor + bw/2, (bar_y0 + bar_y1)/2, text=f"waste {self.last_beginning_waste:g}", font=("Arial", 9))
                cursor += bw

            # pieces
            for j, piece in enumerate(plank.segments, start=1):
                if j > 1 and self.last_kerf > 0:
                    kerf_w = self.last_kerf * scale
                    c.create_rectangle(cursor, bar_y0, cursor + kerf_w, bar_y1, fill="#e0e0e0", outline="")  # grey kerf
                    cursor += kerf_w
                w = piece.length * scale
                c.create_rectangle(cursor, bar_y0, cursor + w, bar_y1, fill="#a7c7e7", outline="#5588cc")  # blue piece
                c.create_text(cursor + w/2, (bar_y0 + bar_y1)/2, text=f"{piece.length:g}", font=("Arial", 9))
                cursor += w

            # trailing waste
            if cursor < x1:
                c.create_rectangle(cursor, bar_y0, x1, bar_y1, fill="#ffd9a3", outline="#e6b36a")
                waste_len = (x1 - cursor) / scale
                c.create_text((cursor + x1)/2, (bar_y0 + bar_y1)/2, text=f"waste {waste_len:g}", font=("Arial", 9))

            y += bar_height + plank_gap
            if y + bar_height + plank_gap > height - margin:
                c.create_text(width - margin, height - margin/2, text="(Resize window to see more planks)", anchor="e", fill="#777", font=("Arial", 9))
                break

def main():
    app = CutOptimizerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
