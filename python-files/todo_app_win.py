import json
import csv
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, filedialog, ttk

APP_TITLE = "ToDo Lite"

def _data_file_path():
    # If user explicitly wants portable mode (same folder of script/exe)
    if os.getenv("TODO_PORTABLE") == "1":
        base = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
        return base / "tasks.json"
    # Default: per-user app data (always writable)
    appdata = os.getenv("APPDATA") or str(Path.home())
    base = Path(appdata) / "ToDoLite"
    base.mkdir(parents=True, exist_ok=True)
    return base / "tasks.json"

DATA_FILE = _data_file_path()

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.tasks = []
        self.filter_var = tk.StringVar(value="All")

        self._build_ui()
        self._load_tasks()
        self._render_list()

    # ---------------- UI ----------------
    def _build_ui(self):
        self.root.geometry("520x460")
        self.root.minsize(480, 420)

        # Top frame: entry + add
        top = tk.Frame(self.root, padx=8, pady=8)
        top.pack(fill="x")

        self.entry = tk.Entry(top, font=("Segoe UI", 11))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.entry.bind("<Return>", lambda e: self.add_task())
        self.entry.focus_set()

        add_btn = tk.Button(top, text="Aggiungi", command=self.add_task, width=10)
        add_btn.pack(side="left")

        # Filter
        filter_frame = tk.Frame(self.root, padx=8)
        filter_frame.pack(fill="x")
        tk.Label(filter_frame, text="Filtro:").pack(side="left")
        filter_box = ttk.Combobox(filter_frame, state="readonly",
                                  values=["All", "Active", "Completed"],
                                  textvariable=self.filter_var, width=12)
        filter_box.pack(side="left", padx=(6, 0))
        filter_box.bind("<<ComboboxSelected>>", lambda e: self._render_list())

        # Listbox + scrollbar
        mid = tk.Frame(self.root, padx=8, pady=8)
        mid.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(mid, font=("Consolas", 11), activestyle="dotbox",
                                  selectmode="browse")
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<Double-Button-1>", lambda e: self.toggle_selected())
        self.listbox.bind("<space>", lambda e: self.toggle_selected())
        self.listbox.bind("<Delete>", lambda e: self.delete_selected())

        scrollbar = tk.Scrollbar(mid, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Bottom bar: buttons
        bottom = tk.Frame(self.root, padx=8, pady=8)
        bottom.pack(fill="x")

        tk.Button(bottom, text="Modifica", command=self.edit_selected, width=10).pack(side="left")
        tk.Button(bottom, text="Completa", command=self.toggle_selected, width=10).pack(side="left", padx=(6, 0))
        tk.Button(bottom, text="Elimina", command=self.delete_selected, width=10).pack(side="left", padx=(6, 0))

        tk.Button(bottom, text="Pulisci completati", command=self.clear_completed).pack(side="right")
        tk.Button(bottom, text="Esporta CSV", command=self.export_csv).pack(side="right", padx=(0, 6))

        # Status bar
        self.status = tk.StringVar(value="0 attività")
        status_bar = tk.Label(self.root, textvariable=self.status, anchor="w", bd=1, relief="sunken")
        status_bar.pack(side="bottom", fill="x")

    # -------------- Data I/O --------------
    def _load_tasks(self):
        try:
            if DATA_FILE.exists():
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            else:
                self.tasks = []
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile leggere {DATA_FILE}.\\n{e}")
            self.tasks = []

    def _save_tasks(self):
        try:
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare {DATA_FILE}.\\n{e}")

    # -------------- Render --------------
    def _render_list(self):
        self.listbox.delete(0, tk.END)
        flt = self.filter_var.get()

        for t in self.tasks:
            if flt == "Active" and t["done"]:
                continue
            if flt == "Completed" and not t["done"]:
                continue
            prefix = "[x]" if t["done"] else "[ ]"
            self.listbox.insert(tk.END, f"{prefix} {t['text']}")
        self._update_status()

    def _update_status(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t["done"])
        active = total - done
        self.status.set(f"{total} attività • {active} attive • {done} completate")

    def _selected_index_in_model(self):
        sel = self.listbox.curselection()
        if not sel:
            return None

        visible_to_model = []
        flt = self.filter_var.get()
        for i, t in enumerate(self.tasks):
            if flt == "Active" and t["done"]:
                continue
            if flt == "Completed" and not t["done"]:
                continue
            visible_to_model.append(i)

        idx_visible = sel[0]
        if 0 <= idx_visible < len(visible_to_model):
            return visible_to_model[idx_visible]
        return None

    # -------------- Actions --------------
    def add_task(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.tasks.append({"text": text, "done": False})
        self.entry.delete(0, tk.END)
        self._save_tasks()
        self._render_list()

    def edit_selected(self):
        idx = self._selected_index_in_model()
        if idx is None:
            messagebox.showinfo("Nessuna selezione", "Seleziona una voce da modificare.")
            return
        current = self.tasks[idx]["text"]
        new_text = simpledialog.askstring("Modifica attività", "Testo:", initialvalue=current)
        if new_text is None:
            return
        new_text = new_text.strip()
        if new_text == "":
            return
        self.tasks[idx]["text"] = new_text
        self._save_tasks()
        self._render_list()

    def toggle_selected(self):
        idx = self._selected_index_in_model()
        if idx is None:
            return
        self.tasks[idx]["done"] = not self.tasks[idx]["done"]
        self._save_tasks()
        self._render_list()

    def delete_selected(self):
        idx = self._selected_index_in_model()
        if idx is None:
            return
        del self.tasks[idx]
        self._save_tasks()
        self._render_list()

    def clear_completed(self):
        self.tasks = [t for t in self.tasks if not t["done"]]
        self._save_tasks()
        self._render_list()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["text", "done"])
                for t in self.tasks:
                    writer.writerow([t["text"], "1" if t["done"] else "0"])
            messagebox.showinfo("Esportazione", "CSV salvato correttamente.")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile esportare CSV.\\n{e}")

def main():
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
