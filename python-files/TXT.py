#!/usr/bin/env python3
# save_txt.pyw
# Save Txt - Classic Green Terminal-style Text/Script Manager
# Large feature-rich single-file Tkinter app (~450+ lines)
# Author: Generated for user request
# IMPORTANT: This is a SAFE utility for managing .txt scripts. No injection, no cheating.

import os
import sys
import json
import time
import threading
import tkinter as tk
from tkinter import (
    filedialog,
    messagebox,
    simpledialog,
    scrolledtext,
)
from datetime import datetime

# ---------------- CONFIG ----------------
APP_TITLE = "Save Txt"
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".save_txt_config.json")
DEFAULT_SCRIPTS_FOLDER = os.path.join(os.path.expanduser("~"), "SaveTxt_Scripts")
WINDOW_WIDTH = 980
WINDOW_HEIGHT = 620
AUTOSAVE_INTERVAL_SEC = 30  # autosave editor to temp file
CLIP_POLL_MS = 1500  # clipboard polling interval
# color theme - green on black (classic)
BG = "#07110a"
PANEL_BG = "#07110a"
TEXT_BG = "#001100"
ACCENT = "#65ff65"
DIM = "#2b5b2b"
STATUS_BG = "#051007"
# ----------------------------------------

# ---------- Config helpers ----------
def load_config():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    # default config
    return {
        "scripts_dir": DEFAULT_SCRIPTS_FOLDER,
        "last_file": "",
        "win_x": None,
        "win_y": None,
        "win_w": WINDOW_WIDTH,
        "win_h": WINDOW_HEIGHT,
        "autosave": True,
        "autosave_interval": AUTOSAVE_INTERVAL_SEC,
        "last_clipboard": "",
        "sort_by": "name",  # or 'mtime'
    }

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

# ---------- Utilities ----------
def ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass

def timestamped_name(prefix="script", ext=".txt"):
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"

def is_text_file(fn):
    return fn.lower().endswith(".txt")

def read_text_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None

def write_text_file(path, content):
    try:
        ensure_dir(os.path.dirname(path) or ".")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False

# ---------- Main App Class ----------
class SaveTxtApp:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        self.scripts_dir = self.config.get("scripts_dir", DEFAULT_SCRIPTS_FOLDER)
        ensure_dir(self.scripts_dir)

        # window
        self.root.title(APP_TITLE)
        w = self.config.get("win_w", WINDOW_WIDTH)
        h = self.config.get("win_h", WINDOW_HEIGHT)
        x = self.config.get("win_x")
        y = self.config.get("win_y")
        if x is not None and y is not None:
            self.root.geometry(f"{w}x{h}+{x}+{y}")
        else:
            self.root.geometry(f"{w}x{h}")
        self.root.configure(bg=BG)
        self.root.minsize(700, 420)

        # state
        self.current_relpath = None
        self.clip_last = self.config.get("last_clipboard", "")
        self._stop_threads = False
        self._dirty = False

        # build UI
        self._build_topbar()
        self._build_main_area()
        self._build_statusbar()
        self._bind_shortcuts()

        # init
        self.reload_file_list()
        self._start_autosave_thread()
        self._start_clip_poll()

        # restore last file if exists
        last = self.config.get("last_file", "")
        if last:
            full = os.path.join(self.scripts_dir, last)
            if os.path.exists(full):
                self._load_file_by_relpath(last)

        # graceful close hook
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- UI building ----------
    def _build_topbar(self):
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=8, pady=6)

        # Title (fixed top-left)
        title = tk.Label(top, text=APP_TITLE, fg=ACCENT, bg=BG, font=("Consolas", 18, "bold"))
        title.pack(side="left", anchor="w")

        # small description / subtitle
        subtitle = tk.Label(top, text="Classic green terminal style text manager", fg=DIM, bg=BG, font=("Consolas", 9))
        subtitle.pack(side="left", anchor="w", padx=(8,0))

        # right-side controls
        controls = tk.Frame(top, bg=BG)
        controls.pack(side="right", anchor="e")

        self.btn_folder = tk.Button(controls, text="📁 Folder", fg=ACCENT, bg=BG, relief="flat", command=self.choose_folder)
        self.btn_folder.pack(side="right", padx=6)

        self.btn_refresh = tk.Button(controls, text="↻ Refresh", fg=ACCENT, bg=BG, relief="flat", command=self.reload_file_list)
        self.btn_refresh.pack(side="right", padx=6)

        self.btn_save = tk.Button(controls, text="Save", fg=ACCENT, bg=BG, relief="flat", command=self.save_dialog)
        self.btn_save.pack(side="right", padx=6)

        self.btn_new = tk.Button(controls, text="New", fg=ACCENT, bg=BG, relief="flat", command=self.new_file_dialog)
        self.btn_new.pack(side="right", padx=6)

    def _build_main_area(self):
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=8, pady=(0,8))

        # left column: file list and small controls
        left = tk.Frame(main, width=260, bg=PANEL_BG)
        left.pack(side="left", fill="y", padx=(0,8), pady=4)
        left.pack_propagate(False)

        lbl = tk.Label(left, text="Saved files", fg=ACCENT, bg=PANEL_BG, font=("Consolas", 12, "bold"))
        lbl.pack(anchor="nw", padx=6, pady=(6,2))

        self.listbox = tk.Listbox(left, bg=TEXT_BG, fg=ACCENT, selectbackground=DIM, font=("Consolas", 10), activestyle="none")
        self.listbox.pack(fill="both", expand=True, padx=6, pady=(0,6))
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_selected())
        self.listbox.bind("<<ListboxSelect>>", lambda e: self._on_list_select())

        # left buttons row
        left_btns = tk.Frame(left, bg=PANEL_BG)
        left_btns.pack(fill="x", padx=6, pady=(0,6))

        tk.Button(left_btns, text="Open Folder", fg=ACCENT, bg=BG, relief="flat", command=self.open_scripts_folder).pack(side="left")
        tk.Button(left_btns, text="Delete", fg=ACCENT, bg=BG, relief="flat", command=self.delete_selected).pack(side="left", padx=6)
        tk.Button(left_btns, text="Rename", fg=ACCENT, bg=BG, relief="flat", command=self.rename_selected).pack(side="left")

        # search box
        search_frame = tk.Frame(left, bg=PANEL_BG)
        search_frame.pack(fill="x", padx=6, pady=(0,6))
        tk.Label(search_frame, text="Search:", fg=DIM, bg=PANEL_BG, font=("Consolas",9)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.reload_file_list())
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg=TEXT_BG, fg=ACCENT, insertbackground=ACCENT, font=("Consolas",10))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(4,0))

        # right column: editor and tools
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # editor toolbar
        ed_top = tk.Frame(right, bg=BG)
        ed_top.pack(fill="x")

        lbl_ed = tk.Label(ed_top, text="Editor / Paste", fg=ACCENT, bg=BG, font=("Consolas", 12, "bold"))
        lbl_ed.pack(side="left", padx=6, pady=4)

        # editor action buttons
        ed_actions = tk.Frame(ed_top, bg=BG)
        ed_actions.pack(side="right", padx=6)
        tk.Button(ed_actions, text="Paste Clip", fg=ACCENT, bg=BG, relief="flat", command=self.paste_clipboard).pack(side="left", padx=4)
        tk.Button(ed_actions, text="Copy All", fg=ACCENT, bg=BG, relief="flat", command=self.copy_all).pack(side="left", padx=4)
        tk.Button(ed_actions, text="Clear", fg=ACCENT, bg=BG, relief="flat", command=self.clear_editor).pack(side="left", padx=4)
        tk.Button(ed_actions, text="Stats", fg=ACCENT, bg=BG, relief="flat", command=self.show_stats).pack(side="left", padx=4)

        # editor frame with line numbers
        editor_frame = tk.Frame(right, bg=BG)
        editor_frame.pack(fill="both", expand=True, padx=6, pady=(0,6))

        self.linenumbers = tk.Text(editor_frame, width=4, padx=4, pady=4, bg="#001600", fg=ACCENT, font=("Consolas", 10), state="disabled", relief="flat")
        self.linenumbers.pack(side="left", fill="y")

        self.editor = scrolledtext.ScrolledText(editor_frame, wrap="none", font=("Consolas", 11), bg=TEXT_BG, fg=ACCENT, insertbackground=ACCENT)
        self.editor.pack(side="left", fill="both", expand=True)
        self.editor.bind("<<Modified>>", self._on_editor_modified)
        # keep line numbers updated with scroll
        self.editor.vbar = self.editor.vbar if hasattr(self.editor,'vbar') else None

        # small footer controls inside editor area
        footer_frame = tk.Frame(right, bg=BG)
        footer_frame.pack(fill="x")
        tk.Button(footer_frame, text="Export", fg=ACCENT, bg=BG, relief="flat", command=self.export_selected).pack(side="left", padx=6, pady=4)
        tk.Button(footer_frame, text="Import", fg=ACCENT, bg=BG, relief="flat", command=self.import_file).pack(side="left", padx=6)
        tk.Button(footer_frame, text="Recent", fg=ACCENT, bg=BG, relief="flat", command=self.show_recent).pack(side="left", padx=6)
        tk.Button(footer_frame, text="Settings", fg=ACCENT, bg=BG, relief="flat", command=self.show_settings).pack(side="right", padx=6)

    def _build_statusbar(self):
        self.statusbar = tk.Frame(self.root, bg=STATUS_BG)
        self.statusbar.pack(fill="x", side="bottom")
        self.status_label = tk.Label(self.statusbar, text=f"Folder: {self.scripts_dir}", anchor="w", bg=STATUS_BG, fg=ACCENT, font=("Consolas", 10))
        self.status_label.pack(side="left", padx=8)
        self.info_label = tk.Label(self.statusbar, text="Ready", anchor="e", bg=STATUS_BG, fg=DIM, font=("Consolas", 10))
        self.info_label.pack(side="right", padx=8)

    # ---------- file list & management ----------
    def reload_file_list(self):
        try:
            self.listbox.delete(0, "end")
            files = []
            for base, dirs, filenames in os.walk(self.scripts_dir):
                for fn in filenames:
                    if is_text_file(fn):
                        full = os.path.join(base, fn)
                        rel = os.path.relpath(full, self.scripts_dir)
                        if self.search_var.get().strip().lower() in rel.lower():
                            files.append((rel, os.path.getmtime(full)))
            sort_by = self.config.get("sort_by", "name")
            if sort_by == "mtime":
                files.sort(key=lambda x: x[1], reverse=True)
            else:
                files.sort(key=lambda x: x[0].lower())
            for rel, _ in files:
                self.listbox.insert("end", rel)
            self._update_status(f"Loaded {len(files)} files.")
        except Exception as e:
            self._update_status("Failed to list files.")

    def open_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        rel = self.listbox.get(sel[0])
        self._load_file_by_relpath(rel)

    def _load_file_by_relpath(self, rel):
        full = os.path.join(self.scripts_dir, rel)
        content = read_text_file(full)
        if content is None:
            messagebox.showerror("Error", f"Failed to read {rel}")
            return
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", content)
        self.current_relpath = rel
        self._dirty = False
        self.editor.edit_reset()
        self._update_line_numbers()
        self._update_status(f"Loaded: {rel}")
        # remember last file
        self.config["last_file"] = rel
        save_config(self.config)

    def delete_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Delete", "No file selected.")
            return
        rel = self.listbox.get(sel[0])
        full = os.path.join(self.scripts_dir, rel)
        if not messagebox.askyesno("Delete", f"Delete file:\n{rel}?"):
            return
        try:
            os.remove(full)
            # remove empty parent folders up to scripts_dir
            parent = os.path.dirname(full)
            while parent and os.path.isdir(parent) and os.path.abspath(parent) != os.path.abspath(self.scripts_dir):
                try:
                    if not os.listdir(parent):
                        os.rmdir(parent)
                        parent = os.path.dirname(parent)
                    else:
                        break
                except Exception:
                    break
            self.reload_file_list()
            self._update_status(f"Deleted: {rel}")
            # clear editor if it was the same file
            if self.current_relpath == rel:
                self.current_relpath = None
                self.editor.delete("1.0", "end")
        except Exception:
            messagebox.showerror("Delete", "Failed to delete file.")
            self._update_status("Delete failed.")

    def rename_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Rename", "No file selected.")
            return
        rel = self.listbox.get(sel[0])
        new = simpledialog.askstring("Rename", "Enter new name (without extension):", initialvalue=os.path.splitext(os.path.basename(rel))[0])
        if not new:
            return
        # preserve subfolder if present
        parent = os.path.dirname(rel)
        new_rel = os.path.join(parent, new + ".txt") if parent else new + ".txt"
        src = os.path.join(self.scripts_dir, rel)
        dst = os.path.join(self.scripts_dir, new_rel)
        try:
            ensure_dir(os.path.dirname(dst))
            os.replace(src, dst)
            self.reload_file_list()
            self._update_status(f"Renamed to: {new_rel}")
            if self.current_relpath == rel:
                self.current_relpath = new_rel
        except Exception:
            messagebox.showerror("Rename", "Failed to rename file.")
            self._update_status("Rename failed.")

    # ---------- editor handlers ----------
    def _on_editor_modified(self, event=None):
        # set dirty flag and update line numbers
        if self.editor.edit_modified():
            self._dirty = True
            self._update_line_numbers()
            self._update_status("Modified")
            self.editor.edit_modified(False)

    def _update_line_numbers(self):
        # compute line count and update left gutter
        text = self.editor.get("1.0", "end-1c")
        lines = text.splitlines()
        ln_str = "\n".join(str(i+1) for i in range(len(lines) or 1))
        self.linenumbers.config(state="normal")
        self.linenumbers.delete("1.0", "end")
        self.linenumbers.insert("1.0", ln_str)
        self.linenumbers.config(state="disabled")

    def clear_editor(self):
        if not self.editor.get("1.0", "end").strip():
            return
        if messagebox.askyesno("Clear", "Clear editor contents?"):
            self.editor.delete("1.0", "end")
            self.current_relpath = None
            self._dirty = False
            self._update_line_numbers()
            self._update_status("Editor cleared.")

    def copy_all(self):
        content = self.editor.get("1.0", "end")
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self._update_status("Editor copied to clipboard.")

    def paste_clipboard(self):
        try:
            content = self.root.clipboard_get()
        except Exception:
            content = ""
        if content:
            self.editor.insert("insert", content)
            self._update_line_numbers()
            self._update_status("Pasted clipboard.")
        else:
            self._update_status("Clipboard empty or unavailable.")

    def show_stats(self):
        txt = self.editor.get("1.0", "end-1c")
        chars = len(txt)
        words = len(txt.split())
        lines = len(txt.splitlines() or [""])
        messagebox.showinfo("Editor Stats", f"Lines: {lines}\nWords: {words}\nCharacters: {chars}")

    # ---------- save / new / export / import ----------
    def save_dialog(self):
        # If editing an existing file, ask to overwrite or save as new
        if self.current_relpath:
            if messagebox.askyesno("Save", f"Overwrite existing file?\n{self.current_relpath}"):
                self._save_to_relpath(self.current_relpath)
                return
        # otherwise Save As flow
        folder = simpledialog.askstring("Save", "Enter subfolder name (leave empty for root):")
        if folder is None:
            return
        folder = folder.strip()
        if folder and ("/" in folder or "\\" in folder):
            messagebox.showwarning("Invalid", "Folder name must not contain slashes.")
            return
        filename = simpledialog.askstring("Save", "Enter file name (without extension):")
        if filename is None:
            return
        filename = filename.strip()
        if not filename:
            messagebox.showwarning("Invalid", "File name cannot be empty.")
            return
        if folder:
            rel = os.path.join(folder, filename + ".txt")
        else:
            rel = filename + ".txt"
        full = os.path.join(self.scripts_dir, rel)
        if os.path.exists(full) and not messagebox.askyesno("Overwrite", f"{rel} exists. Overwrite?"):
            return
        ok = write_text_file(full, self.editor.get("1.0", "end"))
        if ok:
            self.current_relpath = rel
            self.reload_file_list()
            self._update_status(f"Saved: {rel}")
            messagebox.showinfo("Saved", f"Saved as:\n{full}")
            self.config["last_file"] = rel
            save_config(self.config)
            self._dirty = False
        else:
            messagebox.showerror("Save", "Failed to save file.")
            self._update_status("Save failed.")

    def new_file_dialog(self):
        name = simpledialog.askstring("New File", "Enter new file name (without extension):")
        if not name:
            return
        rel = name.strip() + ".txt"
        full = os.path.join(self.scripts_dir, rel)
        if os.path.exists(full):
            messagebox.showwarning("New File", "File already exists.")
            return
        ok = write_text_file(full, "")
        if ok:
            self.reload_file_list()
            self._load_file_by_relpath(rel)
            self._update_status(f"Created: {rel}")
        else:
            messagebox.showerror("New File", "Failed to create file.")

    def _save_to_relpath(self, rel):
        full = os.path.join(self.scripts_dir, rel)
        ok = write_text_file(full, self.editor.get("1.0", "end"))
        if ok:
            self._update_status(f"Saved: {rel}")
            self._dirty = False
            self.config["last_file"] = rel
            save_config(self.config)
        else:
            messagebox.showerror("Save", "Failed to save file.")
            self._update_status("Save failed.")

    def export_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Export", "No file selected.")
            return
        rel = self.listbox.get(sel[0])
        src = os.path.join(self.scripts_dir, rel)
        target = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=os.path.basename(rel))
        if not target:
            return
        try:
            with open(src, "rb") as fsrc, open(target, "wb") as fdst:
                fdst.write(fsrc.read())
            self._update_status(f"Exported to: {target}")
            messagebox.showinfo("Export", f"Exported to:\n{target}")
        except Exception:
            messagebox.showerror("Export", "Export failed.")
            self._update_status("Export failed.")

    def import_file(self):
        chosen = filedialog.askopenfilename(filetypes=[("Text files","*.txt"),("All files","*.*")])
        if not chosen:
            return
        name = os.path.basename(chosen)
        dest = os.path.join(self.scripts_dir, name)
        if os.path.exists(dest) and not messagebox.askyesno("Import", f"{name} exists. Overwrite?"):
            return
        try:
            with open(chosen, "rb") as fsrc, open(dest, "wb") as fdst:
                fdst.write(fsrc.read())
            self.reload_file_list()
            self._update_status(f"Imported: {name}")
        except Exception:
            messagebox.showerror("Import", "Import failed.")
            self._update_status("Import failed.")

    def show_recent(self):
        # list recent files by modification time
        try:
            files = []
            for base, dirs, filenames in os.walk(self.scripts_dir):
                for fn in filenames:
                    if is_text_file(fn):
                        full = os.path.join(base, fn)
                        rel = os.path.relpath(full, self.scripts_dir)
                        files.append((rel, os.path.getmtime(full)))
            files.sort(key=lambda x: x[1], reverse=True)
            top = files[:20]
            items = "\n".join(f[0] for f in top)
            if not items:
                items = "(no files)"
            messagebox.showinfo("Recent files", items)
        except Exception:
            messagebox.showerror("Recent", "Failed to get recent files.")

    # ---------- settings & misc ----------
    def choose_folder(self):
        chosen = filedialog.askdirectory(initialdir=self.scripts_dir, title="Choose scripts folder")
        if chosen:
            self.scripts_dir = chosen
            ensure_dir(self.scripts_dir)
            self.config["scripts_dir"] = self.scripts_dir
            save_config(self.config)
            self.reload_file_list()
            self._update_status(f"Main folder: {self.scripts_dir}")

    def open_scripts_folder(self):
        try:
            if sys.platform.startswith("win"):
                os.startfile(self.scripts_dir)
            elif sys.platform.startswith("darwin"):
                os.system(f'open "{self.scripts_dir}"')
            else:
                os.system(f'xdg-open "{self.scripts_dir}"')
            self._update_status("Opened main folder in file manager.")
        except Exception:
            messagebox.showinfo("Folder", f"Folder path:\n{self.scripts_dir}")

    def show_settings(self):
        # simple settings dialog
        dlg = tk.Toplevel(self.root)
        dlg.title("Settings")
        dlg.geometry("380x220")
        dlg.configure(bg=BG)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text="Autosave (sec):", fg=ACCENT, bg=BG).pack(anchor="w", padx=12, pady=(12,0))
        autosave_var = tk.IntVar(value=self.config.get("autosave_interval", AUTOSAVE_INTERVAL_SEC))
        tk.Entry(dlg, textvariable=autosave_var).pack(fill="x", padx=12)

        tk.Label(dlg, text="Sort files by:", fg=ACCENT, bg=BG).pack(anchor="w", padx=12, pady=(12,0))
        sort_var = tk.StringVar(value=self.config.get("sort_by", "name"))
        tk.Radiobutton(dlg, text="Name", variable=sort_var, value="name", bg=BG, fg=ACCENT, selectcolor=BG).pack(anchor="w", padx=18)
        tk.Radiobutton(dlg, text="Modified time (newest first)", variable=sort_var, value="mtime", bg=BG, fg=ACCENT, selectcolor=BG).pack(anchor="w", padx=18)

        def apply_settings():
            try:
                val = int(autosave_var.get())
                self.config["autosave_interval"] = max(5, val)
                self.config["sort_by"] = sort_var.get()
                save_config(self.config)
                self._update_status("Settings saved.")
                dlg.destroy()
                self.reload_file_list()
            except Exception:
                messagebox.showwarning("Settings", "Invalid autosave interval.")

        tk.Button(dlg, text="Apply", command=apply_settings, fg=ACCENT, bg=BG).pack(pady=12)

    # ---------- autosave & clipboard threads ----------
    def _start_autosave_thread(self):
        def autosave_loop():
            while not self._stop_threads:
                try:
                    if self.config.get("autosave", True):
                        interval = int(self.config.get("autosave_interval", AUTOSAVE_INTERVAL_SEC))
                        time.sleep(max(5, interval))
                        # save temp file
                        txt = self.editor.get("1.0", "end")
                        if txt.strip():
                            tmp = os.path.join(self.scripts_dir, ".autosave_tmp.txt")
                            write_text_file(tmp, txt)
                            # update status in main thread
                            self.root.after(0, lambda: self._update_status("Autosaved editor (temp)"))
                    else:
                        time.sleep(5)
                except Exception:
                    time.sleep(5)
        t = threading.Thread(target=autosave_loop, daemon=True)
        t.start()

    def _start_clip_poll(self):
        def poll():
            while not self._stop_threads:
                try:
                    clip = None
                    try:
                        clip = self.root.clipboard_get()
                    except Exception:
                        clip = None
                    if clip and clip != self.clip_last:
                        # ignore tiny whitespace
                        if clip.strip():
                            self.clip_last = clip
                            self.config["last_clipboard"] = clip
                            save_config(self.config)
                            # save into new file
                            name = timestamped_name("clip", ".txt")
                            full = os.path.join(self.scripts_dir, name)
                            write_text_file(full, clip)
                            self.root.after(0, self.reload_file_list)
                            self.root.after(0, lambda: self._update_status(f"Clipboard auto-saved: {name}"))
                    time.sleep(CLIP_POLL_MS/1000.0)
                except Exception:
                    time.sleep(1)
        t = threading.Thread(target=poll, daemon=True)
        t.start()

    # ---------- helpers ----------
    def _update_status(self, text, timeout=6):
        self.info_label.config(text=text)
        # restore folder path after timeout
        def restore():
            time.sleep(timeout)
            if not self._stop_threads:
                try:
                    self.info_label.config(text="Ready")
                except Exception:
                    pass
        threading.Thread(target=restore, daemon=True).start()

    def _bind_shortcuts(self):
        # common shortcuts
        self.root.bind("<Control-s>", lambda e: self.save_dialog())
        self.root.bind("<Control-n>", lambda e: self.new_file_dialog())
        self.root.bind("<Control-o>", lambda e: self.open_scripts_folder())
        self.root.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.root.bind("<Control-q>", lambda e: self.on_close())

    def _on_list_select(self):
        # update status with selected filename
        sel = self.listbox.curselection()
        if sel:
            rel = self.listbox.get(sel[0])
            self._update_status(f"Selected: {rel}", timeout=2)

    # ---------- on close ----------
    def on_close(self):
        if self._dirty:
            if not messagebox.askyesno("Exit", "You have unsaved changes. Exit anyway?"):
                return
        # save window geometry
        try:
            geom = self.root.geometry()
            # format "WxH+X+Y"
            parts = geom.split('+')
            wh = parts[0].split('x')
            self.config["win_w"] = int(wh[0])
            self.config["win_h"] = int(wh[1])
            if len(parts) >= 3:
                self.config["win_x"] = int(parts[1])
                self.config["win_y"] = int(parts[2])
        except Exception:
            pass
        save_config(self.config)
        self._stop_threads = True
        # small delay to let threads end
        self.root.after(150, self.root.destroy)

# ---------- run ----------
def main():
    ensure_dir(DEFAULT_SCRIPTS_FOLDER)
    cfg = load_config()
    ensure_dir(cfg.get("scripts_dir", DEFAULT_SCRIPTS_FOLDER))
    root = tk.Tk()
    app = SaveTxtApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()