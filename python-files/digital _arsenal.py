#!/usr/bin/env python3
"""
Dark Themed Code Repository GUI
Author: Omar
"""

import os
import shutil
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ---------- Config ----------
app_name = "Digital arsenal"

REPO_DIR = "repo_files"
DB_PATH = "repo.db"
# ----------------------------

os.makedirs(REPO_DIR, exist_ok=True)

# Database
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_name TEXT NOT NULL,
    stored_name TEXT NOT NULL,
    extension TEXT,
    language TEXT,
    upload_time TEXT
)
""")
conn.commit()

def ext_to_lang(ext: str) -> str:
    mapping = {
        ".py": "Python", ".js": "JavaScript", ".java": "Java",
        ".c": "C", ".cpp": "C++", ".cs": "C#", ".rb": "Ruby",
        ".go": "Go", ".php": "PHP", ".html": "HTML", ".css": "CSS",
        ".sh": "Shell", ".rs": "Rust", ".ts": "TypeScript",
        ".json": "JSON", ".xml": "XML", ".sql": "SQL",
        ".md": "Markdown", ".txt": "Text"
    }
    return mapping.get(ext.lower(), "Unknown")

def store_file(fullpath: str) -> None:
    if not os.path.isfile(fullpath):
        raise FileNotFoundError(fullpath)
    original_name = os.path.basename(fullpath)
    name, ext = os.path.splitext(original_name)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    stored_name = f"{name}_{timestamp}{ext}"
    dest = os.path.join(REPO_DIR, stored_name)
    shutil.copy2(fullpath, dest)
    language = ext_to_lang(ext)
    upload_time = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO files (original_name, stored_name, extension, language, upload_time) VALUES (?, ?, ?, ?, ?)",
        (original_name, stored_name, ext, language, upload_time)
    )
    conn.commit()

def delete_entry(entry_id: int) -> None:
    cur.execute("SELECT stored_name FROM files WHERE id=?", (entry_id,))
    r = cur.fetchone()
    if not r:
        return
    stored_name = r[0]
    path = os.path.join(REPO_DIR, stored_name)
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print("Warning:", e)
    cur.execute("DELETE FROM files WHERE id=?", (entry_id,))
    conn.commit()

def list_files(filter_text: str = ""):
    q = "SELECT id, original_name, extension, language, upload_time FROM files"
    params = ()
    if filter_text:
        q += " WHERE original_name LIKE ? OR extension LIKE ? OR language LIKE ?"
        s = f"%{filter_text}%"
        params = (s, s, s)
    q += " ORDER BY upload_time DESC"
    cur.execute(q, params)
    return cur.fetchall()

def get_file_path_by_id(entry_id: int):
    cur.execute("SELECT stored_name, original_name FROM files WHERE id=?", (entry_id,))
    r = cur.fetchone()
    if not r:
        return None, None
    stored_name, original_name = r
    return os.path.join(REPO_DIR, stored_name), original_name

# ---------- GUI ----------
class RepoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Code Repository")
        self.geometry("900x550")
        self.configure(bg="black")
        self.style = ttk.Style(self)
        self.set_dark_theme()
        self.create_widgets()
        self.refresh_list()

    def set_dark_theme(self):
        self.style.theme_use("default")
        self.style.configure("Treeview",
                             background="black",
                             foreground="cyan",
                             fieldbackground="black",
                             rowheight=25)
        self.style.configure("Treeview.Heading",
                             background="black",
                             foreground="cyan")
        self.style.map("Treeview", background=[("selected", "cyan")], foreground=[("selected", "black")])
        self.style.configure("TButton", background="black", foreground="cyan", padding=6)
        self.style.map("TButton", background=[("active", "cyan")], foreground=[("active", "black")])
        self.style.configure("TLabel", background="black", foreground="cyan")
        self.style.configure("TEntry", fieldbackground="black", foreground="cyan")

    def create_widgets(self):
        # Top frame
        top = ttk.Frame(self, padding=8)
        top.pack(fill=tk.X)

        ttk.Button(top, text="Upload", command=self.upload_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Refresh", command=self.refresh_list).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Delete", command=self.delete_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="View", command=self.view_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Download", command=self.download_selected).pack(side=tk.LEFT, padx=4)

        ttk.Label(top, text="Search:").pack(side=tk.LEFT, padx=(20, 4))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<Return>", lambda e: self.refresh_list())

        # Treeview
        cols = ("id","name","ext","lang","time")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="File Name")
        self.tree.heading("ext", text="Ext")
        self.tree.heading("lang", text="Language")
        self.tree.heading("time", text="Upload Time (UTC)")
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("name", width=350)
        self.tree.column("ext", width=70, anchor=tk.CENTER)
        self.tree.column("lang", width=120, anchor=tk.CENTER)
        self.tree.column("time", width=260)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def upload_file(self):
        paths = filedialog.askopenfilenames(title="Select file(s) to upload")
        if not paths: return
        for p in paths:
            try:
                store_file(p)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload {p}: {e}")
        self.refresh_list()

    def refresh_list(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = list_files(self.search_var.get().strip())
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def selected_id(self):
        sel = self.tree.selection()
        if not sel: return None
        vals = self.tree.item(sel[0])["values"]
        return vals[0]

    def delete_selected(self):
        sid = self.selected_id()
        if not sid: return
        if not messagebox.askyesno("Confirm", "Delete this file permanently?"):
            return
        delete_entry(sid)
        self.refresh_list()

    def view_selected(self):
        sid = self.selected_id()
        if not sid: return
        path, original_name = get_file_path_by_id(sid)
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "File not found")
            return
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        vw = tk.Toplevel(self)
        vw.title(f"View: {original_name}")
        vw.geometry("800x600")
        txt = tk.Text(vw, wrap="none", bg="black", fg="cyan", insertbackground="cyan")
        txt.insert("1.0", content)
        txt.config(state="disabled")
        txt.pack(fill=tk.BOTH, expand=True)

    def download_selected(self):
        sid = self.selected_id()
        if not sid: return
        path, original_name = get_file_path_by_id(sid)
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "File not found")
            return
        dest = filedialog.asksaveasfilename(initialfile=original_name, title="Save file as")
        if not dest: return
        shutil.copy2(path, dest)
        messagebox.showinfo("Done", f"Saved to {dest}")

if __name__ == "__main__":
    app = RepoApp()
    app.mainloop()
