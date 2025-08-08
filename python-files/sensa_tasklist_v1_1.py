#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sensa Hotel Marketing Task List v1.1
Upgrades from v1.0:
- Drag & drop reorder (within & across sections)
- Bulk add (paste multiple lines)
- Archive done (hide/show)
- Due date per item (+ overdue/soon colors)
- Priority chips (P1/P2/P3/None)
- Progress bar per section
- Hotkeys: Enter=new below, Ctrl+D duplicate, Delete=delete checked
- Undo/Redo (Ctrl+Z/Ctrl+Y)
- Compact/Comfortable view toggle
- Dark/Light themes
No external dependencies (pure Tkinter).
"""

import json
import os
import sys
import datetime as dt
import calendar
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_NAME = "Sensa Hotel Marketing Task List v1.1"
MAX_ITEMS = 10

# --- Themes ---
LIGHT = {
    "bg": "#F7F7F7", "fg": "#111111", "panel": "#FFFFFF",
    "accent": "#1E88E5", "entry_bg": "#FFFFFF", "entry_fg": "#111111",
    "disabled": "#9AA0A6", "check_fg": "#111111", "button_bg": "#EEEEEE",
    "button_fg": "#111111", "border": "#DDDDDD",
    "p1": "#E53935", "p2": "#FB8C00", "p3": "#1E88E5",
    "soon": "#FDD835", "overdue": "#E53935", "ok": "#43A047"
}
DARK = {
    "bg": "#0F1419", "fg": "#E8EAED", "panel": "#161B22",
    "accent": "#4EA1F3", "entry_bg": "#1E232A", "entry_fg": "#F1F3F5",
    "disabled": "#5F6A76", "check_fg": "#E8EAED", "button_bg": "#232A32",
    "button_fg": "#E8EAED", "border": "#2D333B",
    "p1": "#EF5350", "p2": "#FFA726", "p3": "#64B5F6",
    "soon": "#FBC02D", "overdue": "#EF5350", "ok": "#66BB6A"
}


def today():
    return dt.date.today()


def parse_date(s):
    try:
        y, m, d = map(int, s.split("-"))
        return dt.date(y, m, d)
    except Exception:
        return None


class History:
    def __init__(self, capacity=100):
        self.stack = []
        self.redo_stack = []
        self.capacity = capacity

    def push(self, state):
        self.stack.append(json.dumps(state))
        if len(self.stack) > self.capacity:
            self.stack.pop(0)
        self.redo_stack.clear()

    def undo(self, current_state):
        if not self.stack:
            return None
        self.redo_stack.append(json.dumps(current_state))
        return json.loads(self.stack.pop())

    def redo(self):
        if not self.redo_stack:
            return None
        s = self.redo_stack.pop()
        self.stack.append(s)
        return json.loads(s)


class CalendarPopup(tk.Toplevel):
    def __init__(self, master, initial=None, on_pick=None, theme=LIGHT):
        super().__init__(master)
        self.title("Pick date")
        self.transient(master)
        self.resizable(False, False)
        self.on_pick = on_pick
        self.theme = theme
        self.configure(bg=theme["panel"])
        d = initial or today()
        self.year = d.year
        self.month = d.month
        self._build()

    def _build(self):
        self.header = ttk.Frame(self)
        self.header.pack(fill="x", padx=8, pady=8)
        prev = ttk.Button(self.header, text="◀", width=3, command=self._prev_month, style="Task.TButton")
        nextb = ttk.Button(self.header, text="▶", width=3, command=self._next_month, style="Task.TButton")
        self.lbl = ttk.Label(self.header, text="", style="Task.TLabel")
        prev.pack(side="left"); nextb.pack(side="right"); self.lbl.pack(side="top", pady=4)
        self.gridf = ttk.Frame(self)
        self.gridf.pack(padx=8, pady=8)

        self._render()

    def _render(self):
        for w in self.gridf.winfo_children():
            w.destroy()
        self.lbl.config(text=f"{calendar.month_name[self.month]} {self.year}")
        days = ["Mo","Tu","We","Th","Fr","Sa","Su"]
        for i, d in enumerate(days):
            ttk.Label(self.gridf, text=d, style="Task.TLabel").grid(row=0, column=i, padx=2, pady=2)
        cal = calendar.Calendar(firstweekday=0)
        row = 1
        for week in cal.monthdatescalendar(self.year, self.month):
            col = 0
            for day in week:
                txt = str(day.day)
                btn = ttk.Button(self.gridf, text=txt, width=3, style="Task.TButton",
                                 command=lambda day=day: self._pick(day))
                if day.month != self.month:
                    btn.state(["disabled"])
                btn.grid(row=row, column=col, padx=2, pady=2)
                col += 1
            row += 1

    def _prev_month(self):
        if self.month == 1:
            self.month, self.year = 12, self.year - 1
        else:
            self.month -= 1
        self._render()

    def _next_month(self):
        if self.month == 12:
            self.month, self.year = 1, self.year + 1
        else:
            self.month += 1
        self._render()

    def _pick(self, day):
        if callable(self.on_pick):
            self.on_pick(day)
        self.destroy()


class ItemRow(ttk.Frame):
    def __init__(self, master, app, section_idx, data=None, density="comfortable"):
        super().__init__(master, style="Row.TFrame")
        self.app = app
        self.section_idx = section_idx
        self.data = data or {"text":"", "done":False, "due":"", "prio":0}
        self._dragging = False
        self._build(density)

    # UI
    def _build(self, density):
        pad = (2, 2) if density == "compact" else (4, 4)
        ipx = 3 if density == "compact" else 6

        self.drag = ttk.Label(self, text="≡", width=2, style="Drag.TLabel")
        self.chk_var = tk.BooleanVar(value=self.data.get("done", False))
        self.chk = ttk.Checkbutton(self, variable=self.chk_var, style="Task.TCheckbutton", command=self._on_toggle)

        self.txt_var = tk.StringVar(value=self.data.get("text", ""))
        self.entry = ttk.Entry(self, textvariable=self.txt_var, style="Task.TEntry")
        self.entry.bind("<Return>", self._add_below)
        self.entry.bind("<Control-d>", self._dup_current)

        # Priority chip
        self.prio = int(self.data.get("prio", 0))
        self.prio_btn = ttk.Button(self, width=3, text=self._prio_label(), style="Chip.TButton", command=self._cycle_prio)

        # Due date
        self.due_var = tk.StringVar(value=self.data.get("due", ""))
        self.due_entry = ttk.Entry(self, width=10, textvariable=self.due_var, style="Task.TEntry")
        self.due_btn = ttk.Button(self, text="…", width=2, style="Task.TButton", command=self._open_calendar)

        # Layout
        self.drag.grid(row=0, column=0, padx=(0,4), pady=pad)
        self.chk.grid(row=0, column=1, padx=(0,4), pady=pad)
        self.entry.grid(row=0, column=2, sticky="ew", pady=pad, ipady=ipx)
        self.prio_btn.grid(row=0, column=3, padx=4, pady=pad)
        self.due_entry.grid(row=0, column=4, padx=(6,2), pady=pad)
        self.due_btn.grid(row=0, column=5, padx=(0,0), pady=pad)
        self.columnconfigure(2, weight=1)

        # Drag bindings
        for w in (self, self.drag):
            w.bind("<Button-1>", self._start_drag)
            w.bind("<B1-Motion>", self._do_drag)
            w.bind("<ButtonRelease-1>", self._end_drag)

        # Visual state
        self._update_due_colors()

    def _prio_label(self):
        return {0:"—",1:"P1",2:"P2",3:"P3"}.get(self.prio, "—")

    # Actions
    def _on_toggle(self):
        self.data["done"] = self.chk_var.get()
        self.app.on_board_changed()

    def _cycle_prio(self):
        self.prio = (self.prio + 1) % 4
        self.data["prio"] = self.prio
        self.prio_btn.config(text=self._prio_label())
        self.app.on_board_changed()
        self.app.refresh_styles()

    def _open_calendar(self):
        base = parse_date(self.due_var.get()) or today()
        CalendarPopup(self, initial=base, on_pick=self._set_due, theme=self.app.palette)

    def _set_due(self, d):
        self.due_var.set(d.strftime("%Y-%m-%d"))
        self.data["due"] = self.due_var.get()
        self._update_due_colors()
        self.app.on_board_changed()

    def _update_due_colors(self):
        dstr = self.due_var.get().strip()
        color = None
        if dstr:
            d = parse_date(dstr)
            if d:
                if d < today():
                    color = self.app.palette["overdue"]
                elif (d - today()).days <= 2:
                    color = self.app.palette["soon"]
                else:
                    color = self.app.palette["ok"]
        if color:
            self.due_entry.configure(foreground=color)
        else:
            self.due_entry.configure(foreground=self.app.palette["entry_fg"])

    def _add_below(self, e=None):
        self.app.add_item_below(self.section_idx, self)
        return "break"

    def _dup_current(self, e=None):
        self.app.duplicate_item(self.section_idx, self)
        return "break"

    # Drag & drop (simple implementation)
    def _start_drag(self, e):
        self._dragging = True
        self.lift()
        self.start_y = e.y_root
        self.start_section = self.section_idx
        self.app.begin_drag(self)

    def _do_drag(self, e):
        if not self._dragging: return
        self.app.update_drag(self, e.x_root, e.y_root)

    def _end_drag(self, e):
        if not self._dragging: return
        self._dragging = False
        self.app.end_drag(self, e.x_root, e.y_root)

    # Data exchange
    def get_data(self):
        self.data["text"] = self.txt_var.get()
        self.data["done"] = self.chk_var.get()
        self.data["due"] = self.due_var.get().strip()
        self.data["prio"] = self.prio
        return dict(self.data)


class Section(ttk.Frame):
    def __init__(self, master, app, index, title="Section", items=None):
        super().__init__(master, style="Panel.TFrame")
        self.app = app
        self.index = index
        self.items = []
        self.archived_hidden = False

        self.title_var = tk.StringVar(value=title)
        self.title_entry = ttk.Entry(self, textvariable=self.title_var, style="Title.TEntry")
        self.title_entry.grid(row=0, column=0, columnspan=6, sticky="ew", pady=(0,6))
        self.columnconfigure(0, weight=1)

        self.items_frame = ttk.Frame(self, style="Panel.TFrame")
        self.items_frame.grid(row=1, column=0, columnspan=6, sticky="nsew")
        self.rowconfigure(1, weight=1)

        # Controls
        self.add_btn = ttk.Button(self, text="Add Item", command=self.add_item, style="Task.TButton")
        self.bulk_btn = ttk.Button(self, text="Bulk Add", command=self.bulk_add, style="Task.TButton")
        self.del_btn = ttk.Button(self, text="Delete Checked", command=self.delete_checked, style="Task.TButton")
        self.arch_btn = ttk.Button(self, text="Archive Done", command=self.toggle_archive, style="Task.TButton")
        self.count_lbl = ttk.Label(self, text="", style="Task.TLabel")
        self.progress = ttk.Progressbar(self, mode="determinate")

        self.add_btn.grid(row=2, column=0, sticky="w", pady=(6,0))
        self.bulk_btn.grid(row=2, column=1, sticky="w", padx=(6,0), pady=(6,0))
        self.del_btn.grid(row=2, column=2, sticky="w", padx=(6,0), pady=(6,0))
        self.arch_btn.grid(row=2, column=3, sticky="w", padx=(6,0), pady=(6,0))
        self.count_lbl.grid(row=2, column=4, sticky="e", pady=(6,0))
        self.progress.grid(row=2, column=5, sticky="ew", padx=(6,0), pady=(6,0))
        self.columnconfigure(5, weight=1)

        for it in (items or [])[:MAX_ITEMS]:
            self._add_item_internal(it)

        self._update_count_progress()
        self._update_add_state()

    def _add_item_internal(self, data=None, pos=None):
        if len([i for i in self.items]) >= MAX_ITEMS:
            return None
        row = ItemRow(self.items_frame, app=self.app, section_idx=self.index, data=data or {}, density=self.app.density)
        if pos is None or pos >= len(self.items):
            row.grid(row=len(self.items), column=0, sticky="ew", pady=2)
            self.items.append(row)
        else:
            self.items.insert(pos, row)
            self._regrid_items()
        self.items_frame.columnconfigure(0, weight=1)
        self._update_count_progress()
        self._update_add_state()
        return row

    def _regrid_items(self):
        r = 0
        for row in self.items:
            # hide archived done
            if self.archived_hidden and row.get_data().get("done"):
                row.grid_remove()
            else:
                row.grid(row=r, column=0, sticky="ew", pady=2)
                r += 1

    def add_item(self):
        if len(self.items) >= MAX_ITEMS:
            messagebox.showinfo(APP_NAME, f"Max {MAX_ITEMS} items reached for this section.")
            return
        self._add_item_internal({})
        self.app.on_board_changed()

    def add_item_below(self, after_row):
        idx = self.items.index(after_row) + 1
        if len(self.items) >= MAX_ITEMS:
            return None
        r = self._add_item_internal({}, pos=idx)
        self.app.on_board_changed()
        return r

    def duplicate_item(self, row):
        if len(self.items) >= MAX_ITEMS: return
        data = row.get_data()
        idx = self.items.index(row) + 1
        self._add_item_internal(data, pos=idx)
        self.app.on_board_changed()

    def delete_checked(self):
        keep = []
        for row in self.items:
            if not row.get_data().get("done"):
                keep.append(row)
            else:
                row.destroy()
        self.items = keep
        self._regrid_items()
        self._update_count_progress()
        self._update_add_state()
        self.app.on_board_changed()

    def toggle_archive(self):
        self.archived_hidden = not self.archived_hidden
        self.arch_btn.config(text="Show Archived" if self.archived_hidden else "Archive Done")
        self._regrid_items()

    def bulk_add(self):
        win = tk.Toplevel(self)
        win.title("Bulk Add")
        win.geometry("420x300")
        ttk.Label(win, text="Paste one task per line:", style="Task.TLabel").pack(anchor="w", padx=8, pady=6)
        txt = tk.Text(win, height=10)
        txt.pack(fill="both", expand=True, padx=8, pady=6)
        def do_add():
            lines = [l.strip() for l in txt.get("1.0","end").splitlines() if l.strip()]
            added = 0
            for line in lines:
                if len(self.items) >= MAX_ITEMS: break
                self._add_item_internal({"text": line, "done": False})
                added += 1
            self.app.on_board_changed()
            messagebox.showinfo(APP_NAME, f"Added {added} items.")
            win.destroy()
        ttk.Button(win, text="Add", command=do_add, style="Task.TButton").pack(pady=8)

    def get_data(self):
        return {"title": self.title_var.get(), "items": [r.get_data() for r in self.items]}

    def load_from(self, data):
        self.title_var.set(data.get("title", f"Section {self.index+1}"))
        for r in self.items:
            r.destroy()
        self.items.clear()
        for it in data.get("items", [])[:MAX_ITEMS]:
            self._add_item_internal(it)
        self._update_count_progress()
        self._update_add_state()

    def _update_count_progress(self):
        total = len(self.items)
        checked = sum(1 for r in self.items if r.get_data().get("done"))
        self.count_lbl.config(text=f"{checked}/{total} done")
        self.progress.config(maximum=max(total, 1), value=checked)

    def _update_add_state(self):
        state = "disabled" if len(self.items) >= MAX_ITEMS else "!disabled"
        self.add_btn.state([state] if state == "disabled" else [])

    def set_density(self, density):
        for r in self.items:
            r.destroy()
        backup = [i.get_data() for i in self.items]
        self.items.clear()
        for it in backup:
            self._add_item_internal(it)


class TaskListApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME + " – (unsaved)")
        self.geometry("1200x760")
        self.minsize(980, 560)

        self._file_path = None
        self.palette = LIGHT
        self.density = "comfortable"
        self.history = History()

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self._apply_theme(self.palette)

        self._build_menu()

        self.container = ttk.Frame(self, padding=12, style="Bg.TFrame")
        self.container.pack(fill="both", expand=True)

        self.sections = []
        grid = ((0,0,"Section 1"), (0,1,"Section 2"), (1,0,"Section 3"), (1,1,"Section 4"))
        for i in range(2):
            self.container.columnconfigure(i, weight=1, uniform="c")
            self.container.rowconfigure(i, weight=1, uniform="r")

        for r, c, title in grid:
            f = ttk.Frame(self.container, padding=10, style="Panel.TFrame")
            f.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
            s = Section(f, app=self, index=len(self.sections), title=title, items=[])
            s.pack(fill="both", expand=True)
            self.sections.append(s)

        # Hotkeys
        self.bind_all("<Control-s>", lambda e: self.save())
        self.bind_all("<Control-o>", lambda e: self.open())
        self.bind_all("<Control-n>", lambda e: self.new())
        self.bind_all("<Delete>", lambda e: self.delete_checked())
        self.bind_all("<Control-d>", lambda e: self.duplicate_focused())
        self.bind_all("<Control-z>", lambda e: self.undo())
        self.bind_all("<Control-y>", lambda e: self.redo())

        self.drag_placeholder = None  # a visual placeholder during drag

        self.snapshot_to_history()

    # --- Theme & Style ---
    def _apply_theme(self, pal):
        self.configure(bg=pal["bg"])
        s = self.style
        s.configure("Bg.TFrame", background=pal["bg"])
        s.configure("Panel.TFrame", background=pal["panel"], borderwidth=1, relief="solid")
        s.configure("Row.TFrame", background=pal["panel"])
        s.configure("Task.TLabel", background=pal["panel"], foreground=pal["fg"])
        s.configure("Drag.TLabel", background=pal["panel"], foreground=pal["fg"])
        for name in ("Task.TEntry", "Title.TEntry"):
            s.configure(name, fieldbackground=pal["entry_bg"], foreground=pal["entry_fg"])
        s.configure("Task.TButton", background=pal["button_bg"], foreground=pal["button_fg"])
        s.map("Task.TButton",
              foreground=[("disabled", pal["disabled"]), ("active", pal["fg"])],
              background=[("disabled", pal["button_bg"]), ("active", pal["accent"])])

        self.option_add("*Entry*insertBackground", pal["fg"])
        self.option_add("*Entry*selectBackground", pal["accent"])
        self.option_add("*Entry*selectForeground", pal["panel"])

    def set_theme(self, name):
        self.palette = LIGHT if name == "light" else DARK
        self._apply_theme(self.palette)
        self.refresh_styles()

    def refresh_styles(self):
        # Repaint priority colors by configuring button foregrounds
        for sec in self.sections:
            for r in sec.items:
                # colorize priority chip text
                col = {1:self.palette["p1"], 2:self.palette["p2"], 3:self.palette["p3"]}.get(r.prio, self.palette["fg"])
                r.prio_btn.configure(foreground=col)
                r._update_due_colors()

    # --- Menu / Commands ---
    def _build_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New\tCtrl+N", command=self.new)
        file_menu.add_command(label="Open...\tCtrl+O", command=self.open)
        file_menu.add_command(label="Save\tCtrl+S", command=self.save)
        file_menu.add_command(label="Save As...", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Light Theme", command=lambda: self.set_theme("light"))
        view_menu.add_command(label="Dark Theme", command=lambda: self.set_theme("dark"))
        view_menu.add_separator()
        view_menu.add_command(label="Compact Density", command=lambda: self.set_density("compact"))
        view_menu.add_command(label="Comfortable Density", command=lambda: self.set_density("comfortable"))

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo\tCtrl+Z", command=self.undo)
        edit_menu.add_command(label="Redo\tCtrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete Checked\tDel", command=self.delete_checked)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        menubar.add_cascade(label="View", menu=view_menu)
        self.config(menu=menubar)

    def set_density(self, density):
        self.density = density
        # Recreate rows per section to apply padding changes
        state = self._collect_data()
        self._load_data(state)

    # --- Board changes & history ---
    def on_board_changed(self):
        self.refresh_counts()
        self.snapshot_to_history()

    def refresh_counts(self):
        for s in self.sections:
            s._update_count_progress()

    def snapshot_to_history(self):
        self.history.push(self._collect_data())
        self._update_title_dirty(False)

    def undo(self):
        prev = self.history.undo(self._collect_data())
        if prev is not None:
            self._load_data(prev)
            self._update_title_dirty(False)

    def redo(self):
        nxt = self.history.redo()
        if nxt is not None:
            self._load_data(nxt)
            self._update_title_dirty(False)

    def _update_title_dirty(self, dirty=True):
        base = os.path.basename(self._file_path) if self._file_path else "(unsaved)"
        mark = "● " if dirty else ""
        self.title(f"{mark}{APP_NAME} – {base}")

    # --- File I/O ---
    def new(self):
        if not self._confirm_discard_changes(): return
        for i, s in enumerate(self.sections, start=1):
            s.load_from({"title": f"Section {i}", "items": []})
        self._file_path = None
        self.snapshot_to_history()

    def open(self):
        if not self._confirm_discard_changes(): return
        path = filedialog.askopenfilename(
            title=f"{APP_NAME} - Open",
            filetypes=[("Task Board JSON", "*.json"), ("All files", "*.*")],
        )
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Failed to open file.\n\n{e}")
            return
        self._load_data(data)
        self._file_path = path
        self.snapshot_to_history()

    def save(self, *args):
        if not self._file_path: return self.save_as()
        data = self._collect_data()
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self._update_title_dirty(False)
            messagebox.showinfo(APP_NAME, f"Saved:\n{self._file_path}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Failed to save file.\n\n{e}")

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Task Board JSON", "*.json"), ("All files", "*.*")],
            title=f"{APP_NAME} - Save As"
        )
        if not path: return
        self._file_path = path
        self.save()

    def _confirm_discard_changes(self):
        return messagebox.askyesno(APP_NAME, "Discard current board and continue?")

    # --- Data plumbing ---
    def _collect_data(self):
        return {"sections":[s.get_data() for s in self.sections]}

    def _load_data(self, data):
        secs = data.get("sections", [])
        for idx, s in enumerate(self.sections):
            payload = secs[idx] if idx < len(secs) else {"title": f"Section {idx+1}", "items":[]}
            s.load_from(payload)
        self.refresh_styles()
        self.refresh_counts()

    # --- Hotkey helpers ---
    def delete_checked(self):
        for s in self.sections:
            s.delete_checked()
        self.on_board_changed()

    def find_focused_row(self):
        w = self.focus_get()
        for si, s in enumerate(self.sections):
            for r in s.items:
                if w is r.entry or w is r.prio_btn or w is r.due_entry:
                    return si, r
        return None, None

    def duplicate_focused(self):
        si, r = self.find_focused_row()
        if r is not None:
            self.sections[si].duplicate_item(r)

    def add_item_below(self, section_idx, row_widget):
        r = self.sections[section_idx].add_item_below(row_widget)
        if r: r.entry.focus_set()

    def duplicate_item(self, section_idx, row_widget):
        self.sections[section_idx].duplicate_item(row_widget)

    # --- Drag & Drop ---
    def begin_drag(self, row: ItemRow):
        # Create a placeholder frame to show drop location
        self._make_placeholder(row)

    def update_drag(self, row: ItemRow, x_root, y_root):
        target_section = None
        target_index = None
        # Determine which section and index we're over
        for s in self.sections:
            absx = s.items_frame.winfo_rootx()
            absy = s.items_frame.winfo_rooty()
            w = s.items_frame.winfo_width()
            h = s.items_frame.winfo_height()
            if absx <= x_root <= absx + w and absy <= y_root <= absy + h:
                target_section = s
                # Find position
                y_local = y_root - absy
                idx = 0
                for idx, r in enumerate(s.items):
                    ry = r.winfo_y()
                    rh = r.winfo_height()
                    if y_local < ry + rh/2:
                        target_index = idx
                        break
                else:
                    target_index = len(s.items)
                break

        if target_section is None:
            self._place_placeholder(None, None)
        else:
            self._place_placeholder(target_section, target_index)

    def end_drag(self, row: ItemRow, x_root, y_root):
        dest = self.drag_placeholder
        self._remove_placeholder_visual_only()
        if not dest or dest["section"] is None:
            return
        src_sec = self.sections[row.section_idx]
        dst_sec = dest["section"]
        # Remove from src
        if row in src_sec.items:
            src_idx = src_sec.items.index(row)
            src_sec.items.pop(src_idx)
            row.grid_forget()
        # Insert into dst
        if len(dst_sec.items) >= MAX_ITEMS:
            # give row back to start location
            src_sec.items.insert(src_idx, row)
            src_sec._regrid_items()
            return
        insert_at = min(dest["index"], len(dst_sec.items))
        dst_sec.items.insert(insert_at, row)
        row.section_idx = dst_sec.index
        dst_sec._regrid_items()
        src_sec._regrid_items()
        self.on_board_changed()
        self.drag_placeholder = None

    def _make_placeholder(self, row):
        self.drag_placeholder = {"section": None, "index": None}
        # a simple visual cue via section regrid method; no floating ghost for simplicity

    def _place_placeholder(self, section, index):
        self.drag_placeholder["section"] = section
        self.drag_placeholder["index"] = max(0, index) if index is not None else None

    def _remove_placeholder_visual_only(self):
        # nothing to remove visually in this simplified approach
        pass


def main():
    app = TaskListApp()
    app.mainloop()


if __name__ == "__main__":
    main()
