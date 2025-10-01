import os
import json
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox

CONFIG_PATH = Path.home() / ".folder_size_compare.json"

# ---------- Config ----------
def load_config():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except:
            return {}
    return {}

def save_config(cfg):
    try:
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
    except:
        pass

# ---------- Helpers ----------
def get_size(path):
    if not path or not os.path.exists(path):
        return 0
    if os.path.isfile(path):
        try:
            return os.path.getsize(path)
        except:
            return 0
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    return total

def format_size(size):
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

# ---------- App ----------
class FolderCompareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup Folder Compare")
        self.root.geometry("1200x650")
        self.root.configure(bg="#f3f3f3")  # Windows 11 light gray background
        self.root.minsize(900, 500)

        self.config = load_config()
        self.pairs = []
        self._build_ui()

        for pair in self.config.get("pairs", []):
            self._add_pair(pair[0], pair[1])

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")  # clam is clean, less 90s looking

        # General font
        default_font = ("Segoe UI Variable", 10)
        style.configure("Treeview", font=default_font, rowheight=28, background="white", fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI Variable", 10, "bold"), background="#f3f3f3", relief="flat")
        style.map("Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "white")])

        style.configure("TButton", font=("Segoe UI Variable", 10), padding=6, relief="flat", background="white")
        style.map("TButton",
                  background=[("active", "#e0e0e0")],
                  relief=[("pressed", "flat")])

        # --- top toolbar ---
        top = Frame(self.root, bg="#f3f3f3")
        top.pack(fill=X, padx=12, pady=10)

        ttk.Button(top, text="➕ Add Pair", command=lambda: self._add_pair("", "")).pack(side=LEFT, padx=6)
        ttk.Button(top, text="🔍 Compare", command=self._compare).pack(side=LEFT, padx=6)
        ttk.Button(top, text="🗑 Clear", command=self._clear_all).pack(side=LEFT, padx=6)

        self.pair_frame = Frame(self.root, bg="#f3f3f3")
        self.pair_frame.pack(fill=X, padx=12, pady=6)

        # --- Treeview ---
        self.tree = ttk.Treeview(
            self.root,
            columns=("path1", "size1", "path2", "size2", "diff", "status"),
            show="tree headings"
        )
        self.tree.pack(fill=BOTH, expand=True, padx=12, pady=12)

        self.tree.heading("#0", text="Name", anchor="w")
        self.tree.column("#0", width=260, anchor="w", stretch=True)

        cols = [
            ("path1", "Folder 1", 320),
            ("size1", "Size 1", 110),
            ("path2", "Folder 2", 320),
            ("size2", "Size 2", 110),
            ("diff", "Difference", 150),
            ("status", "Status", 120),
        ]
        for col_id, text, width in cols:
            self.tree.heading(col_id, text=text, anchor="w")
            self.tree.column(col_id, width=width, anchor="w", stretch=True)

        # Scrollbars
        vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.root, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)

        # Tags for row highlighting
        self.tree.tag_configure("NEW", background="#d9fdd3")      # Windows 11 green
        self.tree.tag_configure("MODIFIED", background="#fff4ce") # soft yellow
        self.tree.tag_configure("MISSING", background="#fde7e9")  # soft red

        self.tree.bind("<<TreeviewOpen>>", self._on_open)

    def _add_pair(self, f1, f2):
        var1, var2 = StringVar(value=f1), StringVar(value=f2)
        row = Frame(self.pair_frame, bg="#f3f3f3")
        row.pack(fill=X, pady=4)

        Entry(row, textvariable=var1, width=50, font=("Segoe UI Variable", 9)).pack(side=LEFT, expand=True, fill=X, padx=2)
        ttk.Button(row, text="Browse", command=lambda: self._browse(var1)).pack(side=LEFT, padx=2)
        Label(row, text=" ↔ ", bg="#f3f3f3", font=("Segoe UI Variable", 11)).pack(side=LEFT)
        Entry(row, textvariable=var2, width=50, font=("Segoe UI Variable", 9)).pack(side=LEFT, expand=True, fill=X, padx=2)
        ttk.Button(row, text="Browse", command=lambda: self._browse(var2)).pack(side=LEFT, padx=2)
        ttk.Button(row, text="Remove", command=lambda: self._remove_pair(row, var1, var2)).pack(side=LEFT, padx=6)

        self.pairs.append((var1, var2))

    def _remove_pair(self, row, var1, var2):
        row.destroy()
        try:
            self.pairs.remove((var1, var2))
        except ValueError:
            pass

    def _browse(self, var):
        p = filedialog.askdirectory()
        if p:
            var.set(p)

    def _clear_all(self):
        for r in self.pair_frame.winfo_children():
            r.destroy()
        self.pairs.clear()
        self.tree.delete(*self.tree.get_children())
        save_config({"pairs": []})

    def _compare(self):
        folder_pairs = [(v1.get(), v2.get()) for v1, v2 in self.pairs if v1.get() and v2.get()]
        if not folder_pairs:
            messagebox.showwarning("Need folders", "Please add at least one folder pair")
            return

        save_config({"pairs": folder_pairs})
        self.tree.delete(*self.tree.get_children())

        for i, (f1, f2) in enumerate(folder_pairs, start=1):
            size1 = get_size(f1)
            size2 = get_size(f2)
            diff = size2 - size1
            diff_text = f"{diff:+,} B ({format_size(abs(diff))})"

            parent_id = self.tree.insert(
                "", "end",
                text=f"Pair {i}",
                values=(f1, format_size(size1), f2, format_size(size2), diff_text, "")
            )
            self.tree.insert(parent_id, "end", text="Loading...")

    def _on_open(self, event):
        item_id = self.tree.focus()
        children = self.tree.get_children(item_id)
        if children and self.tree.item(children[0], "text") == "Loading...":
            self.tree.delete(children[0])
            vals = self.tree.item(item_id, "values")
            if vals and len(vals) >= 3:
                f1 = vals[0]
                f2 = vals[2]
                self._populate_children(item_id, f1, f2)

    def _populate_children(self, parent_id, f1, f2):
        try:
            entries1 = {n: os.path.join(f1, n) for n in os.listdir(f1)} if f1 and os.path.isdir(f1) else {}
        except Exception:
            entries1 = {}
        try:
            entries2 = {n: os.path.join(f2, n) for n in os.listdir(f2)} if f2 and os.path.isdir(f2) else {}
        except Exception:
            entries2 = {}

        all_names = sorted(set(entries1.keys()) | set(entries2.keys()))

        for name in all_names:
            path1 = entries1.get(name)
            path2 = entries2.get(name)

            size1 = size2 = 0
            mtime1 = mtime2 = 0
            status = ""

            if path1 and os.path.exists(path1):
                try:
                    size1 = os.path.getsize(path1) if os.path.isfile(path1) else get_size(path1)
                    mtime1 = os.path.getmtime(path1)
                except:
                    pass
            if path2 and os.path.exists(path2):
                try:
                    size2 = os.path.getsize(path2) if os.path.isfile(path2) else get_size(path2)
                    mtime2 = os.path.getmtime(path2)
                except:
                    pass

            if not path1 and path2:
                status = "NEW"
            elif path1 and path2:
                if size1 != size2 or int(mtime1) != int(mtime2):
                    status = "MODIFIED"
            elif path1 and not path2:
                status = "MISSING"

            if status:
                diff = size2 - size1
                diff_text = f"{diff:+,} B ({format_size(abs(diff))})"
                node_id = self.tree.insert(
                    parent_id, "end",
                    text=name,
                    values=(path1 or "-", format_size(size1),
                            path2 or "-", format_size(size2),
                            diff_text, status),
                    tags=(status,)
                )
                if (path1 and os.path.isdir(path1)) or (path2 and os.path.isdir(path2)):
                    self.tree.insert(node_id, "end", text="Loading...")

# ---------- Run ----------
if __name__ == "__main__":
    root = Tk()
    app = FolderCompareApp(root)
    root.mainloop()
