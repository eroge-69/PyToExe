import os
import sys
import time
import uuid
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

APP_DIR = os.path.join(os.path.expanduser("~"), "Documents", "ToDoTimer")
DB_PATH = os.path.join(APP_DIR, "tasks.json")

def ensure_app_dir():
    os.makedirs(APP_DIR, exist_ok=True)

def fmt_hhmmss(seconds: int) -> str:
    if seconds < 0:
        seconds = 0
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def dt_str(dt: datetime | None) -> str:
    return dt.strftime("%H:%M") if dt else ""

@dataclass
class Segment:
    start: datetime
    end: datetime | None = None

    def to_json(self):
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat() if self.end else None
        }

    @staticmethod
    def from_json(d: dict) -> "Segment":
        def parse_dt(x):
            try:
                return datetime.fromisoformat(x) if x else None
            except Exception:
                return None
        return Segment(start=parse_dt(d.get("start")) or datetime.now(),
                       end=parse_dt(d.get("end")))

@dataclass
class TaskItem:
    id: str
    title: str
    # kept for backward-compat but no longer used for display; elapsed is computed from segments
    elapsed_seconds: int = 0
    is_running: bool = False
    start_time: datetime | None = None
    end_time: datetime | None = None
    completed: bool = False
    created: datetime = field(default_factory=datetime.now)
    segments: list[Segment] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.completed:
            return "Done"
        return "Running" if self.is_running else ("Paused" if self.start_time else "New")

    def total_seconds(self) -> int:
        total = 0
        for seg in self.segments:
            end = seg.end or datetime.now()
            total += max(0, int((end - seg.start).total_seconds()))
        return total

    @property
    def elapsed(self) -> str:
        return fmt_hhmmss(self.total_seconds())

    @property
    def start(self) -> str:
        return dt_str(self.start_time)

    @property
    def end(self) -> str:
        return dt_str(self.end_time)

    @property
    def total_min(self) -> str:
        return f"{self.total_seconds()/60:.1f}"

    def to_json(self):
        d = asdict(self)
        # convert datetimes
        for k in ("start_time", "end_time", "created"):
            v = d[k]
            d[k] = v.isoformat() if isinstance(v, datetime) else None
        # convert segments
        d["segments"] = [seg.to_json() for seg in self.segments]
        return d

    @staticmethod
    def from_json(d: dict) -> "TaskItem":
        def parse_dt(x):
            try:
                return datetime.fromisoformat(x) if x else None
            except Exception:
                return None
        segs_json = d.get("segments")
        start_time = parse_dt(d.get("start_time"))
        end_time = parse_dt(d.get("end_time"))
        # migrate older records without segments into a single segment if they had times
        segments = [Segment(start=start_time, end=end_time)] if (segs_json is None and start_time) else []
        if isinstance(segs_json, list):
            segments = [Segment.from_json(s) for s in segs_json]

        return TaskItem(
            id=d.get("id", str(uuid.uuid4())),
            title=d.get("title", ""),
            elapsed_seconds=int(d.get("elapsed_seconds", 0)),
            is_running=bool(d.get("is_running", False)),
            start_time=start_time,
            end_time=end_time,
            completed=bool(d.get("completed", False)),
            created=parse_dt(d.get("created")) or datetime.now(),
            segments=segments
        )

class ToDoApp:
    FLASH_MS = 600  # flash cadence for running rows

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("To-Do Timers (Tkinter)")
        self.root.geometry("1080x620")
        self.flash_state = False  # toggles to animate running rows

        self.tasks: list[TaskItem] = []
        ensure_app_dir()
        self.load_tasks()

        self.build_ui()
        self.apply_dark_theme()
        self.refresh_tree()
        self.tick()          # UI refresh loop (1s)
        self.flash_loop()    # flash loop (~600ms)

    # ---------- Persistence ----------
    def save_tasks(self):
        try:
            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump([t.to_json() for t in self.tasks], f, indent=2)
        except Exception as e:
            messagebox.showwarning("Save Error", str(e))

    def load_tasks(self):
        self.tasks.clear()
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for row in data or []:
                    self.tasks.append(TaskItem.from_json(row))
            except Exception as e:
                messagebox.showwarning("Load Error", f"Starting fresh.\n\n{e}")

    # ---------- UI ----------
    def build_ui(self):
        self.style = ttk.Style()
        try:
            self.root.call("ttk::style", "theme", "use", "clam")
        except Exception:
            pass

        # Root uses grid so center area expands
        self.root.grid_rowconfigure(1, weight=1)   # tree
        self.root.grid_columnconfigure(0, weight=1)

        # Top panel (inputs + actions)
        self.top = ttk.Frame(self.root, padding=10)
        self.top.grid(row=0, column=0, sticky="ew")
        for col in range(10):
            self.top.grid_columnconfigure(col, weight=0)
        self.top.grid_columnconfigure(1, weight=1)

        self.title_var = tk.StringVar()

        ttk.Label(self.top, text="Title").grid(row=0, column=0, sticky="w", padx=(0,6), pady=(0,8))
        self.title_entry = ttk.Entry(self.top, textvariable=self.title_var)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=(0,8))
        self.title_entry.focus_set()
        # ENTER adds/saves task
        self.title_entry.bind("<Return>", lambda e: (self.add_btn.invoke(), "break"))
        self.title_entry.bind("<KP_Enter>", lambda e: (self.add_btn.invoke(), "break"))

        # Actions row
        actions = ttk.Frame(self.top)
        actions.grid(row=1, column=0, columnspan=2, sticky="ew")
        for i in range(7):
            actions.grid_columnconfigure(i, weight=1, uniform="actions")

        self.add_btn = ttk.Button(actions, text="Add Task", command=self.add_task, style="Accent.TButton")
        self.add_btn.grid(row=0, column=0, sticky="ew", padx=(0,8))

        ttk.Button(actions, text="Edit", command=self.edit_task).grid(row=0, column=1, sticky="ew", padx=(0,8))
        ttk.Button(actions, text="Delete", command=self.delete_task).grid(row=0, column=2, sticky="ew", padx=(0,8))
        ttk.Button(actions, text="Start All", command=self.start_all).grid(row=0, column=3, sticky="ew", padx=(0,8))
        ttk.Button(actions, text="Pause All", command=self.pause_all).grid(row=0, column=4, sticky="ew", padx=(0,8))
        ttk.Button(actions, text="Mark Done", command=self.mark_done, style="Success.TButton").grid(row=0, column=5, sticky="ew", padx=(0,8))
        ttk.Button(actions, text="Reopen", command=self.reopen_task, style="Warning.TButton").grid(row=0, column=6, sticky="ew")

        # Tree (list)
        cols = ("title","status","elapsed","start","end","total")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=18, style="Dark.Treeview", selectmode="extended")
        self.tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(6,10))

        col_specs = [
            ("title","Title",240,tk.W, True),
            ("status","Status",90,tk.CENTER, False),
            ("elapsed","Elapsed",100,tk.CENTER, False),
            ("start","Time Started",160,tk.CENTER, True),
            ("end","Time Ended",160,tk.CENTER, True),
            ("total","Total (min)",120,tk.CENTER, False),
        ]
        for c, text, w, anchor, stretch in col_specs:
            self.tree.heading(c, text=text, anchor=(tk.CENTER if c != "title" else tk.W))
            self.tree.column(c, width=w, anchor=anchor, stretch=stretch)

        # Scrollbar
        vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        vsb.grid(row=1, column=1, sticky="ns", pady=(6,10))
        self.root.grid_columnconfigure(1, weight=0)
        self.tree.configure(yscrollcommand=vsb.set)

        # Bottom controls
        bottom = ttk.Frame(self.root, padding=10)
        bottom.grid(row=2, column=0, sticky="ew")
        for i in range(3):
            bottom.grid_columnconfigure(i, weight=1, uniform="bottom")

        ttk.Button(bottom, text="Start / Pause", command=self.start_pause).grid(row=0, column=0, sticky="ew", padx=6)
        ttk.Button(bottom, text="Reset Timer", command=self.reset_timer).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(bottom, text="Save All", command=self.save_tasks).grid(row=0, column=2, sticky="ew", padx=6)

        # Selection handling
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", lambda e: self.start_pause())

        # Tree tags (colors set in theme)
        self.tree.tag_configure("running_a")
        self.tree.tag_configure("running_b")
        self.tree.tag_configure("oddrow")
        self.tree.tag_configure("evenrow")
        self.tree.tag_configure("done")
        self.tree.tag_configure("selrow")
        self.tree.tag_configure("segment")  # sub-line rows

    # ---------- Dark Theme ----------
    def apply_dark_theme(self):
        BG = "#0F1115"
        PANEL = "#131720"
        ENTRY = "#1A2030"
        FG = "#FFFFFF"
        SUBTLE = "#AAB2C0"
        ACCENT = "#3B82F6"
        ACCENT_HI = "#60A5FA"
        SUCCESS = "#10B981"
        SUCCESS_HI = "#34D399"
        WARNING = "#F59E0B"
        WARNING_HI = "#FBBF24"
        ROW = "#0F1115"
        ROW_ALT = "#0D0F14"
        BORDER = "#232838"

        RUN_A_BG = "#FDE68A"  # soft yellow
        RUN_B_BG = "#FEF08A"  # softer yellow
        RUN_FG = "#111111"
        DONE_BG = "#064E3B"
        DONE_FG = "#D1FAE5"

        self.root.configure(bg=BG)

        # frames/labels
        self.style.configure("TFrame", background=BG)
        self.style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))

        # buttons
        self.style.configure("TButton",
                             background=PANEL,
                             foreground=FG,
                             bordercolor=BORDER,
                             focusthickness=3,
                             focuscolor=ACCENT,
                             padding=(14,10),
                             font=("Segoe UI Semibold", 10))
        self.style.map("TButton",
                       background=[("active", "#182132")],
                       foreground=[("disabled", "#6B7280")])

        self.style.configure("Accent.TButton",
                             background=ACCENT,
                             foreground="#FFFFFF",
                             bordercolor=ACCENT)
        self.style.map("Accent.TButton",
                       background=[("active", ACCENT_HI)])

        self.style.configure("Success.TButton",
                             background=SUCCESS,
                             foreground="#FFFFFF",
                             bordercolor=SUCCESS)
        self.style.map("Success.TButton",
                       background=[("active", SUCCESS_HI)])

        self.style.configure("Warning.TButton",
                             background=WARNING,
                             foreground="#111111",
                             bordercolor=WARNING)
        self.style.map("Warning.TButton",
                       background=[("active", WARNING_HI)])

        # entries
        self.style.configure("TEntry",
                             fieldbackground=ENTRY,
                             foreground=FG,
                             insertcolor=FG,
                             bordercolor=BORDER,
                             padding=(10,8),
                             font=("Segoe UI", 10))

        # tree
        self.style.configure("Dark.Treeview",
                             background=ROW,
                             fieldbackground=ROW,
                             foreground=FG,
                             bordercolor=BORDER,
                             rowheight=26)
        self.style.map("Dark.Treeview", background=[], foreground=[])
        self.style.configure("Treeview.Heading",
                             background=PANEL,
                             foreground=FG,
                             bordercolor=BORDER,
                             font=("Segoe UI Semibold", 10))

        # row tags
        self.tree.tag_configure("oddrow", background=ROW)
        self.tree.tag_configure("evenrow", background=ROW_ALT)
        self.tree.tag_configure("running_a", background=RUN_A_BG, foreground=RUN_FG)
        self.tree.tag_configure("running_b", background=RUN_B_BG, foreground=RUN_FG)
        self.tree.tag_configure("done", background=DONE_BG, foreground=DONE_FG)
        try:
            self.tree.tag_configure("selrow", foreground=ACCENT, font=("Segoe UI Semibold", 10, "underline"))
        except Exception:
            self.tree.tag_configure("selrow", foreground=ACCENT)
        # segment rows (slightly dim text)
        self.tree.tag_configure("segment", foreground=SUBTLE)

        # scrollbars
        try:
            self.style.configure("Vertical.TScrollbar", background=PANEL, troughcolor=BG, arrowcolor=SUBTLE, bordercolor=BORDER)
            self.style.configure("Horizontal.TScrollbar", background=PANEL, troughcolor=BG, arrowcolor=SUBTLE, bordercolor=BORDER)
        except Exception:
            pass

    # ---------- Data/Tree ----------
    def refresh_tree(self):
        sel_ids = set(self.tree.selection())
        self.tree.delete(*self.tree.get_children())

        for idx, t in enumerate(self.tasks):
            tags = []
            tags.append("evenrow" if idx % 2 == 0 else "oddrow")
            if t.completed:
                tags.append("done")
            elif t.is_running:
                tags.append("running_a" if self.flash_state else "running_b")
            if t.id in sel_ids:
                tags.append("selrow")

            # insert parent task row
            self.tree.insert("", tk.END, iid=t.id, values=(
                t.title, t.status, t.elapsed, t.start, t.end, t.total_min
            ), tags=tuple(tags))
            # ensure children are visible
            self.tree.item(t.id, open=True)

            # insert segment sub-rows
            for i, seg in enumerate(t.segments):
                seg_id = f"{t.id}:{i}"
                self.tree.insert(t.id, tk.END, iid=seg_id, values=(
                    f"↳ Run {i+1}", "", "", dt_str(seg.start), dt_str(seg.end), ""
                ), tags=("segment",))

        # restore selection
        if sel_ids:
            existing = [iid for iid in sel_ids if self.tree.exists(iid)]
            if existing:
                self.tree.selection_set(existing)

    def on_tree_select(self, _evt=None):
        # Clear selrow on all
        for iid in self.tree.get_children(""):
            # include children
            stack = [iid]
            stack.extend(self.tree.get_children(iid))
            for x in stack:
                tags = [tg for tg in self.tree.item(x, "tags") if tg != "selrow"]
                self.tree.item(x, tags=tuple(tags))
        # Add selrow to current selection (parent or child)
        for iid in self.tree.selection():
            tags = list(self.tree.item(iid, "tags"))
            if "selrow" not in tags:
                tags.append("selrow")
            self.tree.item(iid, tags=tuple(tags))

    def _normalize_selection_to_task_id(self) -> str | None:
        sel = self.tree.selection()
        if not sel:
            return None
        iid = sel[0]
        # child rows use "taskid:index"
        return iid.split(":")[0]

    def get_selected_task(self) -> TaskItem | None:
        task_id = self._normalize_selection_to_task_id()
        if not task_id:
            return None
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None

    def get_selected_task_id(self) -> str | None:
        return self._normalize_selection_to_task_id()

    # ---------- Actions ----------
    def add_task(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showinfo("Add Task", "Please enter a task title.")
            return
        t = TaskItem(id=str(uuid.uuid4()), title=title)
        self.tasks.append(t)
        self.title_var.set("")
        self.refresh_tree()
        self.save_tasks()

    def edit_task(self):
        t = self.get_selected_task()
        if not t:
            messagebox.showinfo("Edit", "Select a task to edit.")
            return
        self.title_var.set(t.title)

        def commit():
            title = self.title_var.get().strip()
            if not title:
                messagebox.showinfo("Edit", "Please enter a task title.")
                return
            t.title = title
            self.title_var.set("")
            self.add_btn.configure(text="Add Task", command=self.add_task)
            self.refresh_tree()
            self.save_tasks()

        self.add_btn.configure(text="Save Changes", command=commit)

    def delete_task(self):
        t = self.get_selected_task()
        if not t:
            messagebox.showinfo("Delete", "Select a task to delete.")
            return
        if messagebox.askyesno("Delete", f"Delete: {t.title}?"):
            self.tasks = [x for x in self.tasks if x.id != t.id]
            self.refresh_tree()
            self.save_tasks()

    def start_pause(self):
        t = self.get_selected_task()
        if not t:
            messagebox.showinfo("Start/Pause", "Select a task to start/pause.")
            return
        if t.completed:
            messagebox.showinfo("Start/Pause", "This task is marked Done. Reopen it to continue.")
            return

        now = datetime.now()
        if not t.is_running:
            # START: open a new segment
            if not t.start_time:
                t.start_time = now
            t.end_time = None
            t.is_running = True
            t.segments.append(Segment(start=now))
        else:
            # PAUSE: close the last open segment
            t.is_running = False
            t.end_time = now
            if t.segments and t.segments[-1].end is None:
                t.segments[-1].end = now

        self.refresh_tree()
        self.save_tasks()

    def reset_timer(self):
        t = self.get_selected_task()
        if not t:
            messagebox.showinfo("Reset", "Select a task to reset.")
            return
        if t.completed and not messagebox.askyesno("Reset", "This task is marked Done. Reset anyway?"):
            return
        t.elapsed_seconds = 0  # legacy field
        t.is_running = False
        t.start_time = None
        t.end_time = None
        t.completed = False
        t.segments.clear()
        self.refresh_tree()
        self.save_tasks()

    def start_all(self):
        now = datetime.now()
        for t in self.tasks:
            if not t.completed and not t.is_running:
                if not t.start_time:
                    t.start_time = now
                t.end_time = None
                t.is_running = True
                t.segments.append(Segment(start=now))
        self.refresh_tree(); self.save_tasks()

    def pause_all(self):
        now = datetime.now()
        for t in self.tasks:
            if t.is_running:
                t.is_running = False
                t.end_time = now
                if t.segments and t.segments[-1].end is None:
                    t.segments[-1].end = now
        self.refresh_tree(); self.save_tasks()

    def mark_done(self):
        t = self.get_selected_task()
        if not t:
            messagebox.showinfo("Mark Done", "Select a task to mark as done.")
            return
        now = datetime.now()
        if t.is_running:
            # close the active segment
            t.is_running = False
            if t.segments and t.segments[-1].end is None:
                t.segments[-1].end = now
        if not t.end_time:
            t.end_time = now
        t.completed = True
        self.refresh_tree()
        self.save_tasks()

    def reopen_task(self):
        t = self.get_selected_task()
        if not t:
            messagebox.showinfo("Reopen", "Select a task to reopen.")
            return
        if not t.completed:
            messagebox.showinfo("Reopen", "This task is not marked Done.")
            return
        t.completed = False
        t.is_running = False
        self.refresh_tree()
        self.save_tasks()

    # ---------- Timer & Flash Loops ----------
    def tick(self):
        # Repaint every second if any task is running so elapsed updates live
        if any(t.is_running for t in self.tasks):
            self.refresh_tree()
        self.root.after(1000, self.tick)

    def flash_loop(self):
        # Toggle flash state and repaint tags for RUNNING tasks only
        self.flash_state = not self.flash_state
        for t in self.tasks:
            item = t.id
            if not self.tree.exists(item):
                continue
            tags = [tg for tg in self.tree.item(item, "tags") if tg not in ("running_a", "running_b")]
            if t.is_running and not t.completed:
                tags.append("running_a" if self.flash_state else "running_b")
            self.tree.item(item, tags=tuple(tags))
        self.root.after(self.FLASH_MS, self.flash_loop)

def main():
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
