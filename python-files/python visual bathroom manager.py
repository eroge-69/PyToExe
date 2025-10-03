# -*- coding: utf-8 -*-
"""
Seating Chart Tracker — Background Image + Bathroom/Loaner/Pencil

Controls:
- Left-click seat: Bathroom
- Right-click seat: Loaner
- Shift + Right-click seat: Pencil
- Edit Layout: shows Rename/Add/Delete/Save buttons, drag seats, arrow keys nudge,
  -/= width, ,/. height.

Storage layout (aligned to your project):
./charts/
    Period_1.json
    Period_2.json
    chart1.png
    chart2.png
    images/
        Period_1/  (optional fallback location for images)
        Period_2/
./events.db  (SQLite, auto-created / migrated to include 'pencil')
"""

import os
import re
import json
import csv
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox

# Optional Pillow for JPEGs; PNG/GIF work with Tk alone
try:
    from PIL import Image, ImageTk
    PIL_OK = True
except Exception:
    PIL_OK = False

APP_TITLE = "Seating Chart Tracker (B=LClick · L=RClick · P=Shift+RClick)"
DB_PATH = Path("./events.db")

# ---- Folders ----
CHARTS_DIR = Path("./charts")
IMAGE_DIR = CHARTS_DIR / "images"
CHARTS_DIR.mkdir(exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# ---- Events ----
EVENT_BATHROOM = "bathroom"
EVENT_LOANER = "loaner"
EVENT_PENCIL = "pencil"

# Default periods (names should match your JSON chart_id like "Period 2")
DEFAULT_CLASSES = ["Period 1", "Period 2", "Period 3", "Period 4", "Period 5", "Period 6"]

# Seat default size (used only when adding new seats)
DEFAULT_SEAT_W = 90
DEFAULT_SEAT_H = 50


def iso_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def week_start(d: datetime) -> datetime:
    return d - timedelta(days=d.weekday())  # Monday


# ---------- Data Store ----------

class DataStore:
    def __init__(self, db_path: Path):
        self.db_path = str(db_path)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    chart_key TEXT NOT NULL,
                    chart_id TEXT NOT NULL,
                    seat_id TEXT NOT NULL,
                    student_name TEXT NOT NULL,
                    event_type TEXT NOT NULL CHECK (event_type IN ('bathroom','loaner'))
                )
                """
            )
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_chart ON events(chart_key, seat_id)")
            conn.commit()
        self._ensure_pencil_event_allowed()

    def _ensure_pencil_event_allowed(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            row = c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='events'").fetchone()
            ddl = row[0] if row else ""
            if "pencil" in ddl:
                return
            c.executescript(
                """
                PRAGMA foreign_keys=off;
                BEGIN TRANSACTION;
                CREATE TABLE events_new(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    chart_key TEXT NOT NULL,
                    chart_id TEXT NOT NULL,
                    seat_id TEXT NOT NULL,
                    student_name TEXT NOT NULL,
                    event_type TEXT NOT NULL CHECK (event_type IN ('bathroom','loaner','pencil'))
                );
                INSERT INTO events_new(id, ts, chart_key, chart_id, seat_id, student_name, event_type)
                SELECT id, ts, chart_key, chart_id, seat_id, student_name,
                       CASE WHEN event_type IN ('bathroom','loaner') THEN event_type ELSE 'loaner' END
                FROM events;
                DROP TABLE events;
                ALTER TABLE events_new RENAME TO events;
                CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
                CREATE INDEX IF NOT EXISTS idx_events_chart ON events(chart_key, seat_id);
                COMMIT;
                PRAGMA foreign_keys=on;
                """
            )

    def insert_event(self, ts: str, chart_key: str, chart_id: str,
                     seat_id: str, student_name: str, event_type: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO events(ts, chart_key, chart_id, seat_id, student_name, event_type) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (ts, chart_key, chart_id, seat_id, student_name, event_type),
            )
            conn.commit()
            return c.lastrowid

    def delete_event(self, event_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM events WHERE id=?", (event_id,))
            conn.commit()

    def fetch_week_counts(self, chart_key: str, start: datetime, end: datetime
                          ) -> Dict[Tuple[str, str], Dict[str, int]]:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            rows = c.execute(
                """
                SELECT seat_id, student_name, event_type, COUNT(*)
                FROM events
                WHERE chart_key=? AND ts >= ? AND ts < ?
                GROUP BY seat_id, student_name, event_type
                """,
                (chart_key, start.isoformat(), end.isoformat()),
            ).fetchall()

        counts: Dict[Tuple[str, str], Dict[str, int]] = {}
        for seat_id, name, e_type, n in rows:
            key = (seat_id, name)
            if key not in counts:
                counts[key] = {EVENT_BATHROOM: 0, EVENT_LOANER: 0, EVENT_PENCIL: 0}
            if e_type in counts[key]:
                counts[key][e_type] = n
        return counts

    def export_csv(self, out_path: Path, chart_key: str):
        with sqlite3.connect(self.db_path) as conn, out_path.open("w", newline="", encoding="utf-8") as f:
            c = conn.cursor()
            writer = csv.writer(f)
            writer.writerow(["id", "ts", "chart_key", "chart_id", "seat_id", "student_name", "event_type"])
            for row in c.execute(
                "SELECT id, ts, chart_key, chart_id, seat_id, student_name, event_type "
                "FROM events WHERE chart_key=? ORDER BY ts ASC",
                (chart_key,),
            ):
                writer.writerow(row)


# ---------- Domain Models ----------

class Seat:
    def __init__(self, seat_id: str, name: str, x: int, y: int, w: int, h: int):
        self.seat_id = seat_id  # e.g., "A1"
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def to_json(self) -> dict:
        # Preserve your schema: use "id"
        return {"id": self.seat_id, "name": self.name, "x": self.x, "y": self.y, "w": self.w, "h": self.h}

    @staticmethod
    def from_json(d: dict) -> "Seat":
        # Accept either "id" or "seat_id" (but save back as "id")
        sid = d.get("id", d.get("seat_id", ""))
        return Seat(sid, d.get("name", ""), int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"]))


class Chart:
    def __init__(self, key: str):
        self.key = key              # e.g., "Period 2"
        self.chart_id = key         # from JSON "chart_id" if present
        self.background: Optional[Path] = None  # from JSON "image"
        self.seats: List[Seat] = []

    def _candidate_paths(self) -> List[Path]:
        # try both "Period 2.json" and "Period_2.json"
        return [
            CHARTS_DIR / f"{self.key}.json",
            CHARTS_DIR / f"{self.key.replace(' ', '_')}.json",
        ]

    def load(self):
        path = next((p for p in self._candidate_paths() if p.exists()), None)
        if path is None:
            messagebox.showwarning(
                "Layout not found",
                f"No chart JSON for '{self.key}'. Expected:\n"
                f"- {CHARTS_DIR / (self.key + '.json')}\n"
                f"- {CHARTS_DIR / (self.key.replace(' ', '_') + '.json')}\n"
                "Use Edit Layout → Save Layout to create one."
            )
            self.seats = []
            self.background = None
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.chart_id = data.get("chart_id", self.key)
            img = data.get("image", "")
            self.background = self._resolve_bg(img)
            self.seats = [Seat.from_json(s) for s in data.get("seats", [])]
        except Exception as e:
            messagebox.showerror("Layout read error", f"Failed to load:\n{path}\n\n{e}")
            self.seats = []
            self.background = None

    def save(self):
        # Save with your schema (chart_id + image + seats[id,...])
        # Prefer underscore filename for stability
        fname = f"{self.key.replace(' ', '_')}.json"
        path = CHARTS_DIR / fname
        image_name = self.background.name if isinstance(self.background, Path) else (self.background or "")
        data = {"chart_id": self.chart_id, "image": image_name, "seats": [s.to_json() for s in self.seats]}
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _resolve_bg(self, image_name: str) -> Optional[Path]:
        """
        Resolve the background image for the chart. Priority:
        1) charts/<image_name>
        2) charts/images/<Period_key>/<image_name>
        3) charts/images/<image_name>
        """
        if not image_name:
            return None
        candidates = [
            CHARTS_DIR / image_name,
            IMAGE_DIR / self.key.replace(" ", "_") / image_name,
            IMAGE_DIR / image_name,
        ]
        for p in candidates:
            if p.exists():
                return p
        # not found; keep the provided name for saving but no path
        return None


# ---------- App ----------

class SeatingTrackerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.ds = DataStore(DB_PATH)

        self.chart_key_var = tk.StringVar(value=DEFAULT_CLASSES[0])
        self.chart = Chart(self.chart_key_var.get())
        self.chart.load()

        self.edit_mode = False
        self.add_mode = False
        self.dragging = None
        self.selected_seat: Optional[Seat] = None
        self.undo_stack: List[Tuple[str, dict]] = []

        self._bg_photo = None  # keep reference to background image

        self._build_ui()
        self._bind_canvas()
        self.refresh_all()

    # ---- UI ----
    def _build_ui(self):
        self.main = ttk.Frame(self.root)
        self.main.pack(fill=tk.BOTH, expand=True)

        self.topbar = ttk.Frame(self.main)
        self.topbar.pack(fill=tk.X, padx=6, pady=6)

        ttk.Label(self.topbar, text="Class:").pack(side=tk.LEFT)
        self.class_combo = ttk.Combobox(self.topbar, values=DEFAULT_CLASSES,
                                        textvariable=self.chart_key_var, state="readonly", width=18)
        self.class_combo.pack(side=tk.LEFT, padx=(4, 10))
        self.class_combo.bind("<<ComboboxSelected>>", self.on_change_class)

        self.btn_undo = ttk.Button(self.topbar, text="Undo Last", command=self.on_undo)
        self.btn_undo.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_export = ttk.Button(self.topbar, text="Export CSV", command=self.on_export)
        self.btn_export.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_edit = ttk.Button(self.topbar, text="Edit Layout", command=self.toggle_edit_mode)
        self.btn_edit.pack(side=tk.LEFT, padx=(0, 8))

        try:
            self.btn_open = ttk.Button(self.topbar, text="Open Charts Folder",
                                       command=lambda: os.startfile(str(CHARTS_DIR)))
            self.btn_open.pack(side=tk.LEFT, padx=(0, 8))
        except Exception:
            pass

        # Edit-only toolbar
        self.editbar = ttk.Frame(self.main)
        self.btn_rename = ttk.Button(self.editbar, text="Rename Seat", command=self.on_rename_seat)
        self.btn_add = ttk.Button(self.editbar, text="Add Seat", command=self.on_add_seat_click)
        self.btn_delete = ttk.Button(self.editbar, text="Delete Seat", command=self.on_delete_seat)
        self.btn_save_layout = ttk.Button(self.editbar, text="Save Layout", command=self.on_save_layout)
        self.btn_templates = ttk.Button(self.editbar, text="Create Templates", command=self.on_create_templates)
        for i, b in enumerate([self.btn_rename, self.btn_add, self.btn_delete, self.btn_save_layout, self.btn_templates]):
            b.grid(row=0, column=i, padx=6, pady=6)

        # Body: canvas + sidebar
        self.body = ttk.Frame(self.main)
        self.body.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.body, bg="#ffffff")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 3), pady=(0, 6))

        self.sidebar = ttk.Frame(self.body, width=320)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(3, 6), pady=(0, 6))

        self.tree = ttk.Treeview(
            self.sidebar,
            columns=("seat", "name", "bathroom", "loaner", "pencil", "flag"),
            show="headings", height=20
        )
        self.tree.heading("seat", text="Seat")
        self.tree.heading("name", text="Name")
        self.tree.heading("bathroom", text="Bathrm")
        self.tree.heading("loaner", text="Loaner")
        self.tree.heading("pencil", text="Pencil")
        self.tree.heading("flag", text=">=3 Loaners")
        self.tree.column("seat", width=70, anchor=tk.CENTER)
        self.tree.column("name", width=150)
        self.tree.column("bathroom", width=70, anchor=tk.CENTER)
        self.tree.column("loaner", width=70, anchor=tk.CENTER)
        self.tree.column("pencil", width=70, anchor=tk.CENTER)
        self.tree.column("flag", width=95, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(
            value="Left-click: Bathroom · Right-click: Loaner · Shift+Right-click: Pencil"
        )
        self.status = ttk.Label(self.main, textvariable=self.status_var, anchor="w")
        self.status.pack(fill=tk.X, padx=6, pady=(0, 6))

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

    def _bind_canvas(self):
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        self.root.bind("<Key>", self.on_key)

    # ---- Drawing ----
    def refresh_all(self):
        self.draw_chart()
        self.refresh_weekly_counts()

    def draw_chart(self):
        self.canvas.delete("all")

        # Draw background image if available
        self._bg_photo = None
        if self.chart.background is not None and self.chart.background.exists():
            try:
                if PIL_OK:
                    im = Image.open(self.chart.background)
                    self._bg_photo = ImageTk.PhotoImage(im)
                else:
                    self._bg_photo = tk.PhotoImage(file=str(self.chart.background))  # PNG/GIF
                self.canvas.create_image(0, 0, image=self._bg_photo, anchor="nw")
                # Set canvas size to background size
                w = self._bg_photo.width()
                h = self._bg_photo.height()
                self.canvas.config(width=w, height=h, scrollregion=(0, 0, w, h))
            except Exception as e:
                messagebox.showwarning("Background image", f"Could not load background:\n{self.chart.background}\n\n{e}")
        else:
            # No background; leave white canvas
            pass

        for seat in self.chart.seats:
            self._draw_seat(seat)

    def _draw_seat(self, seat: Seat):
        x1, y1 = seat.x, seat.y
        x2, y2 = x1 + seat.w, y1 + seat.h

        box_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#fffef6", outline="#333333", width=2)
        name_id = self.canvas.create_text(
            (x1 + x2) // 2, y1 + 14, text=seat.name or "(empty)", font=("Segoe UI", 10, "bold")
        )
        count_id = self.canvas.create_text(
            (x1 + x2) // 2, y2 - 12, text="B:0 L:0 P:0", font=("Segoe UI", 9)
        )
        self.canvas.tag_bind(box_id, "<Enter>", lambda e, b=box_id: self.canvas.itemconfigure(b, fill="#eef6ff"))
        self.canvas.tag_bind(box_id, "<Leave>", lambda e, b=box_id: self.canvas.itemconfigure(b, fill="#fffef6"))

        for item_id in (box_id, name_id, count_id):
            self.canvas.addtag_withtag(f"seat:{seat.seat_id}", item_id)

        seat._box_id = box_id
        seat._name_id = name_id
        seat._count_id = count_id

    def refresh_seat_counts_on_canvas(self, by_seat: Dict[str, Dict[str, int]]):
        for seat in self.chart.seats:
            b = by_seat.get(seat.seat_id, {}).get(EVENT_BATHROOM, 0)
            l = by_seat.get(seat.seat_id, {}).get(EVENT_LOANER, 0)
            p = by_seat.get(seat.seat_id, {}).get(EVENT_PENCIL, 0)
            if hasattr(seat, "_count_id"):
                self.canvas.itemconfigure(seat._count_id, text=f"B:{b} L:{l} P:{p}")

    # ---- Counts / Sidebar ----
    def refresh_weekly_counts(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        start = week_start(datetime.now())
        end = start + timedelta(days=7)
        counts = self.ds.fetch_week_counts(self.chart.key, start, end)

        by_seat: Dict[str, Dict[str, int]] = {
            s.seat_id: {EVENT_BATHROOM: 0, EVENT_LOANER: 0, EVENT_PENCIL: 0} for s in self.chart.seats
        }
        for (seat_id, _name), d in counts.items():
            if seat_id in by_seat:
                for k, v in d.items():
                    by_seat[seat_id][k] = v

        self.refresh_seat_counts_on_canvas(by_seat)

        for s in sorted(self.chart.seats, key=self._natural_seat_key):
            b = by_seat[s.seat_id][EVENT_BATHROOM]
            l = by_seat[s.seat_id][EVENT_LOANER]
            p = by_seat[s.seat_id][EVENT_PENCIL]
            flag = "Yes" if l >= 3 else ""
            self.tree.insert("", tk.END, values=(s.seat_id, s.name, b, l, p, flag))

    @staticmethod
    def _natural_seat_key(seat: Seat):
        # Sort like A1, A2, B1...  Split letters/numbers
        m = re.match(r"([A-Za-z]+)(\d+)$", seat.seat_id)
        if m:
            return (m.group(1).upper(), int(m.group(2)))
        return (seat.seat_id, 0)

    # ---- Helpers ----
    def find_seat_at(self, x: int, y: int) -> Optional[Seat]:
        for s in reversed(self.chart.seats):
            if s.x <= x <= s.x + s.w and s.y <= y <= s.y + s.h:
                return s
        return None

    def select_seat(self, seat: Optional[Seat]):
        if hasattr(self, "selected_seat") and self.selected_seat and hasattr(self.selected_seat, "_box_id"):
            self.canvas.itemconfigure(self.selected_seat._box_id, outline="#333333", width=2)
        self.selected_seat = seat
        if seat and hasattr(seat, "_box_id"):
            self.canvas.itemconfigure(seat._box_id, outline="#0066ff", width=3)

    # ---- Mouse/Key ----
    def on_left_click(self, evt):
        seat = self.find_seat_at(evt.x, evt.y)
        if self.edit_mode:
            self.select_seat(seat)
            if seat:
                self.dragging = (seat, evt.x - seat.x, evt.y - seat.y)
            return
        if seat:
            self.record_event(seat, EVENT_BATHROOM)

    def on_right_click(self, evt):
        if self.edit_mode:
            return
        seat = self.find_seat_at(evt.x, evt.y)
        if seat:
            if evt.state & 0x0001:   # Shift
                self.record_event(seat, EVENT_PENCIL)
            else:
                self.record_event(seat, EVENT_LOANER)

    def on_drag(self, evt):
        if not self.edit_mode or not self.dragging:
            return
        seat, dx, dy = self.dragging
        seat.x = max(0, evt.x - dx)
        seat.y = max(0, evt.y - dy)
        self.canvas.coords(seat._box_id, seat.x, seat.y, seat.x + seat.w, seat.y + seat.h)
        self.canvas.coords(seat._name_id, seat.x + seat.w // 2, seat.y + 14)
        self.canvas.coords(seat._count_id, seat.x + seat.w // 2, seat.y + seat.h - 12)

    def on_drag_end(self, evt):
        if not self.edit_mode:
            return
        if self.dragging:
            seat, _, _ = self.dragging
            self.dragging = None
            self.undo_stack.append(("move_seat", {"seat_id": seat.seat_id, "x": seat.x, "y": seat.y}))

    def on_key(self, evt):
        if not self.edit_mode or not self.selected_seat:
            return
        s = self.selected_seat
        step = 2
        if evt.keysym == "Left":
            s.x = max(0, s.x - step)
        elif evt.keysym == "Right":
            s.x += step
        elif evt.keysym == "Up":
            s.y = max(0, s.y - step)
        elif evt.keysym == "Down":
            s.y += step
        elif evt.char == "-":
            s.w = max(30, s.w - 2)
        elif evt.char == "=":
            s.w += 2
        elif evt.char == ",":
            s.h = max(24, s.h - 2)
        elif evt.char == ".":
            s.h += 2
        else:
            return
        self.canvas.coords(s._box_id, s.x, s.y, s.x + s.w, s.y + s.h)
        self.canvas.coords(s._name_id, s.x + s.w // 2, s.y + 14)
        self.canvas.coords(s._count_id, s.x + s.w // 2, s.y + s.h - 12)

    # ---- Commands ----
    def record_event(self, seat: Seat, event_type: str):
        ts = iso_now()
        event_id = self.ds.insert_event(
            ts=ts, chart_key=self.chart.key, chart_id=self.chart.chart_id,
            seat_id=seat.seat_id, student_name=seat.name, event_type=event_type
        )
        self.undo_stack.append(("insert_event", {"event_id": event_id}))
        self.refresh_weekly_counts()

    def on_undo(self):
        if not self.undo_stack:
            self._ok("Nothing to undo.")
            return
        action, payload = self.undo_stack.pop()
        if action == "insert_event":
            try:
                self.ds.delete_event(payload["event_id"])
            except Exception as e:
                self._err(f"Undo failed: {e}")
        elif action == "delete_seat":
            s = Seat.from_json(payload["seat"])
            self.chart.seats.append(s)
            self.draw_chart()
        elif action == "add_seat":
            sid = payload["seat_id"]
            self.chart.seats = [s for s in self.chart.seats if s.seat_id != sid]
            self.draw_chart()
        elif action == "rename_seat":
            sid = payload["seat_id"]; old_name = payload["old_name"]
            for s in self.chart.seats:
                if s.seat_id == sid:
                    s.name = old_name
                    break
            self.draw_chart()
        elif action == "move_seat":
            pass
        self.refresh_weekly_counts()

    def on_export(self):
        out = filedialog.asksaveasfilename(
            title="Export CSV", defaultextension=".csv", filetypes=[("CSV", "*.csv")],
            initialfile=f"{self.chart.key.replace(' ', '_')}_events.csv",
        )
        if not out:
            return
        try:
            self.ds.export_csv(Path(out), self.chart.key)
            self._ok(f"Exported to:\n{out}")
        except Exception as e:
            self._err(f"Export failed:\n{e}")

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.add_mode = False
        self.btn_add.config(text="Add Seat")
        self.btn_edit.config(text=("Exit Edit" if self.edit_mode else "Edit Layout"))
        if self.edit_mode:
            self.editbar.pack(fill=tk.X, padx=6, pady=(0, 6))
            self.status_var.set("Edit mode: click to select/drag; arrows move; -/= width, ,/. height; Save when done.")
        else:
            try:
                self.editbar.pack_forget()
            except Exception:
                pass
            self.status_var.set("Left-click: Bathroom · Right-click: Loaner · Shift+Right-click: Pencil")
            self.select_seat(None)

    def on_rename_seat(self):
        s = self.selected_seat or (self.chart.seats[0] if self.chart.seats else None)
        if not s:
            self._ok("Select a seat first.")
            return
        new_name = simpledialog.askstring("Rename Seat", f"Enter name for {s.seat_id}:", initialvalue=s.name)
        if new_name is None:
            return
        old_name = s.name
        s.name = new_name.strip()
        self.undo_stack.append(("rename_seat", {"seat_id": s.seat_id, "old_name": old_name}))
        self.draw_chart()
        self.refresh_weekly_counts()

    def on_add_seat_click(self):
        self.add_mode = not self.add_mode
        self.btn_add.config(text=("Click to Place…" if self.add_mode else "Add Seat"))
        if self.add_mode:
            self.status_var.set("Click on the background to place the new seat.")
            self.canvas.bind("<Button-1>", self._place_new_seat_once, add="+")
        else:
            self.canvas.unbind("<Button-1>")

    def _place_new_seat_once(self, evt):
        if not self.add_mode or not self.edit_mode:
            return
        # generate new id like 'Z99' if you need; here just numeric increment if possible
        base = "N"
        next_idx = 1 + sum(1 for s in self.chart.seats if s.seat_id.startswith(base))
        sid = f"{base}{next_idx}"
        new_seat = Seat(sid, "(empty)",
                        max(2, evt.x - DEFAULT_SEAT_W // 2),
                        max(2, evt.y - DEFAULT_SEAT_H // 2),
                        DEFAULT_SEAT_W, DEFAULT_SEAT_H)
        self.chart.seats.append(new_seat)
        self.undo_stack.append(("add_seat", {"seat_id": new_seat.seat_id}))
        self.draw_chart()
        self.refresh_weekly_counts()
        self.add_mode = False
        self.btn_add.config(text="Add Seat")
        self.canvas.unbind("<Button-1>")
        self.status_var.set("Seat added. Drag to position, then Save Layout when done.")

    def on_delete_seat(self):
        s = self.selected_seat
        if not s:
            self._ok("Select a seat to delete.")
            return
        if not messagebox.askyesno("Delete Seat", f"Delete {s.seat_id} ({s.name})?"):
            return
        payload = {"seat": s.to_json()}
        self.chart.seats = [z for z in self.chart.seats if z.seat_id != s.seat_id]
        self.undo_stack.append(("delete_seat", payload))
        self.draw_chart()
        self.refresh_weekly_counts()

    def on_save_layout(self):
        try:
            self.chart.save()
            self._ok(f"Layout saved to {CHARTS_DIR}")
        except Exception as e:
            self._err(f"Save failed:\n{e}")

    def on_create_templates(self):
        out_dir = CHARTS_DIR / "templates"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{self.chart.key.replace(' ', '_')}_TEMPLATE.json"
        try:
            data = {
                "chart_id": self.chart.chart_id,
                "image": (self.chart.background.name if isinstance(self.chart.background, Path) else (self.chart.background or "")),
                "seats": [s.to_json() for s in self.chart.seats],
            }
            out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            self._ok(f"Template written to:\n{out_path}")
        except Exception as e:
            self._err(f"Template write failed:\n{e}")

    def on_change_class(self, _evt=None):
        self.chart = Chart(self.chart_key_var.get())
        self.chart.load()
        self.select_seat(None)
        self.draw_chart()
        self.refresh_weekly_counts()

    # ---- UI helpers ----
    def _ok(self, msg: str):
        messagebox.showinfo("Info", msg)

    def _err(self, msg: str):
        messagebox.showerror("Error", msg)


def main():
    root = tk.Tk()
    root.geometry("1150x760")
    app = SeatingTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
