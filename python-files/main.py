# -*- coding: utf-8 -*-



import os
import re
import json
import tkinter as tk
from tkinter import ttk, messagebox

APP_TITLE = "Template CopieR"
CONFIG_FILE = "templates.json"

def ensure_default_templates(path: str):
    """Crée un fichier JSON d'exemple si absent."""
    if os.path.exists(path):
        return
    sample = {
        "TEST": [
            {
                "title": "un test",
                "text": "Ceci est un test"
            },
            {
                "title": "un test2",
                "text": "Bonjour"
            }
        ],
        "TEST2": [
            {
                "title": "Tessst",
                "text": "Bonjour, Test"
            },
            {
                "title": "Demande de test ",
                "text": "Bonjour l'équipe, c'est un test"
            }
        ]
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)

def load_templates(path: str):
    ensure_default_templates(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # data attendu: {category: [ {title: str, text: str}, ... ], ...}
    if not isinstance(data, dict):
        raise ValueError("Le fichier JSON doit contenir un objet racine ({}).")
    # normalisation minimum
    norm = {}
    for cat, items in data.items():
        if not isinstance(items, list):
            continue
        out = []
        for it in items:
            title = str(it.get("title", "(Sans titre)"))
            text = str(it.get("text", ""))
            out.append({"title": title, "text": text})
        if out:
            norm[str(cat)] = out
    return norm

def extract_placeholders(text: str):
    # {nom} alphanum + underscore
    return sorted(set(re.findall(r"\{([A-Za-z0-9_]+)\}", text)))

class PlaceholderDialog(tk.Toplevel):
    def __init__(self, parent, placeholders):
        super().__init__(parent)
        self.title("Remplir les variables")
        self.resizable(False, False)
        self.values = {}
        self.grab_set()

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        self.entries = {}
        for i, ph in enumerate(placeholders):
            ttk.Label(frm, text=ph + " :").grid(row=i, column=0, sticky="e", padx=(0,8), pady=4)
            e = ttk.Entry(frm, width=32)
            e.grid(row=i, column=1, sticky="w", pady=4)
            self.entries[ph] = e

        btns = ttk.Frame(frm)
        btns.grid(row=len(placeholders), column=0, columnspan=2, pady=(10,0))
        ttk.Button(btns, text="OK", command=self.on_ok).pack(side="left", padx=5)
        ttk.Button(btns, text="Annuler", command=self.on_cancel).pack(side="left", padx=5)

        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())

    def on_ok(self):
        for k, entry in self.entries.items():
            self.values[k] = entry.get()
        self.destroy()

    def on_cancel(self):
        self.values = None
        self.destroy()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x540")
        self.minsize(760, 480)

        self.config_path = os.path.abspath(CONFIG_FILE)
        try:
            self.data = load_templates(self.config_path)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger {CONFIG_FILE}:\n{e}")
            self.data = {}
        self.filtered = dict(self.data)

        self._build_ui()
        self.populate_categories()

    def _build_ui(self):
        self.columnconfigure(0, weight=0)  # sidebar
        self.columnconfigure(1, weight=1)  # main
        self.rowconfigure(0, weight=1)

        # Sidebar catégories
        sidebar = ttk.Frame(self, padding=10)
        sidebar.grid(row=0, column=0, sticky="ns")
        ttk.Label(sidebar, text="Catégories", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.category_list = tk.Listbox(sidebar, height=20, exportselection=False)
        self.category_list.pack(fill="y", expand=True, pady=(6,8))
        self.category_list.bind("<<ListboxSelect>>", lambda e: self.on_category_changed())

        ttk.Button(sidebar, text="Ouvrir templates.json", command=self.open_config).pack(fill="x", pady=4)
        ttk.Button(sidebar, text="Recharger", command=self.reload_config).pack(fill="x")

        # Zone principale
        main = ttk.Frame(self, padding=10)
        main.grid(row=0, column=1, sticky="nsew")
        main.rowconfigure(3, weight=1)
        main.columnconfigure(0, weight=1)

        # Recherche
        search_row = ttk.Frame(main)
        search_row.grid(row=0, column=0, sticky="ew", pady=(0,8))
        ttk.Label(search_row, text="Recherche:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_row, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(6,6))
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filter())
        ttk.Button(search_row, text="Effacer", command=self.clear_search).pack(side="left")

        # Liste des modèles
        ttk.Label(main, text="Modèles", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w")
        self.template_list = tk.Listbox(main, height=12, exportselection=False)
        self.template_list.grid(row=2, column=0, sticky="nsew", pady=(6,8))
        self.template_list.bind("<Double-Button-1>", lambda e: self.copy_selected())

        # Aperçu
        preview_frame = ttk.Frame(main)
        preview_frame.grid(row=3, column=0, sticky="nsew")
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        self.preview = tk.Text(preview_frame, wrap="word", height=8)
        self.preview.grid(row=0, column=0, sticky="nsew")
        self.preview.configure(state="disabled")

        # Actions
        action_row = ttk.Frame(main)
        action_row.grid(row=4, column=0, sticky="ew", pady=(8,0))
        self.status_var = tk.StringVar(value="Prêt.")
        ttk.Button(action_row, text="Copier", command=self.copy_selected).pack(side="left")
        ttk.Button(action_row, text="Copier + Fermer", command=self.copy_and_quit).pack(side="left", padx=(8,0))
        ttk.Label(action_row, textvariable=self.status_var).pack(side="right")

        # Bindings pratiques
        self.template_list.bind("<<ListboxSelect>>", lambda e: self.update_preview())
        self.bind("<Control-c>", lambda e: self.copy_selected())
        self.bind("<Return>", lambda e: self.copy_selected())

    def open_config(self):
        # Ouvre le JSON dans l'éditeur par défaut (Bloc-notes sur Windows)
        path = self.config_path
        if not os.path.exists(path):
            messagebox.showerror("Erreur", f"Fichier introuvable: {path}")
            return
        try:
            os.startfile(path)  # Windows only
        except Exception:
            messagebox.showinfo("Info", f"Veuillez ouvrir manuellement: {path}")

    def reload_config(self):
        try:
            self.data = load_templates(self.config_path)
            self.apply_filter()
            self.status_var.set("Config rechargée.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de recharger: {e}")

    def populate_categories(self):
        self.category_list.delete(0, tk.END)
        for cat in self.data.keys():
            self.category_list.insert(tk.END, cat)
        if self.data:
            self.category_list.select_set(0)
        self.populate_templates()

    def get_selected_category(self):
        try:
            idx = self.category_list.curselection()
            if not idx:
                return None
            return self.category_list.get(idx[0])
        except Exception:
            return None

    def populate_templates(self):
        self.template_list.delete(0, tk.END)
        cat = self.get_selected_category()
        items = []
        if cat and cat in self.filtered:
            items = self.filtered.get(cat, [])
        for it in items:
            self.template_list.insert(tk.END, it.get("title", "(Sans titre)"))
        if items:
            self.template_list.select_set(0)
        self.update_preview()

    def on_category_changed(self):
        self.populate_templates()

    def clear_search(self):
        self.search_var.set("")
        self.apply_filter()

    def apply_filter(self):
        q = self.search_var.get().strip().lower()
        if not q:
            self.filtered = dict(self.data)
        else:
            filt = {}
            for cat, lst in self.data.items():
                keep = []
                for it in lst:
                    title = (it.get("title","") or "").lower()
                    text = (it.get("text","") or "").lower()
                    if q in title or q in text:
                        keep.append(it)
                if keep:
                    filt[cat] = keep
            self.filtered = filt
        current_cat = self.get_selected_category()
        self.populate_categories()
        if current_cat in self.filtered.keys():
            for i, c in enumerate(self.filtered.keys()):
                if c == current_cat:
                    self.category_list.select_clear(0, tk.END)
                    self.category_list.select_set(i)
                    break
        self.populate_templates()

    def get_current_item(self):
        cat = self.get_selected_category()
        if not cat:
            return None
        idxs = self.template_list.curselection()
        if not idxs:
            return None
        idx = idxs[0]
        items = self.filtered.get(cat, [])
        if 0 <= idx < len(items):
            return items[idx]
        return None

    def update_preview(self):
        item = self.get_current_item()
        text = item.get("text","") if item else ""
        self.preview.configure(state="normal")
        self.preview.delete("1.0", tk.END)
        self.preview.insert("1.0", text)
        self.preview.configure(state="disabled")

    def fill_placeholders(self, text: str):
        placeholders = extract_placeholders(text)
        if not placeholders:
            return text
        dlg = PlaceholderDialog(self, placeholders)
        self.wait_window(dlg)
        if dlg.values is None:
            return None  # annulé
        for k, v in dlg.values.items():
            text = text.replace("{%s}" % k, v)
        return text

    def copy_to_clipboard(self, text: str):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()  # s'assurer que le presse-papiers est rempli
            self.status_var.set("Copié dans le presse-papiers.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de copier: {e}")

    def copy_selected(self):
        item = self.get_current_item()
        if not item:
            return
        text = item.get("text","")
        filled = self.fill_placeholders(text)
        if filled is None:
            self.status_var.set("Copie annulée.")
            return
        self.copy_to_clipboard(filled)

    def copy_and_quit(self):
        self.copy_selected()
        self.after(100, self.quit)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
