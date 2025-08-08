
import json, os, sys, tkinter as tk
from tkinter import ttk, messagebox, filedialog
import difflib

APP_TITLE = "Offline German–Persian–English Dictionary"
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

def load_data(path=DATA_FILE):
    if not os.path.exists(path):
        return {"entries": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data, path=DATA_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def normalize(s):
    return s.strip().lower()

class DictApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x600")
        self.minsize(800, 500)

        self.data = load_data()
        self.entries = self.data.get("entries", [])

        # UI
        self.search_var = tk.StringVar()
        self.search_lang = tk.StringVar(value="german")
        self.create_widgets()
        self.populate_list(self.entries)

    def create_widgets(self):
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Search:").pack(side=tk.LEFT)
        e = ttk.Entry(top, textvariable=self.search_var, width=40)
        e.pack(side=tk.LEFT, padx=6)
        e.bind("<Return>", lambda *_: self.do_search())

        ttk.Label(top, text="in").pack(side=tk.LEFT, padx=(8,2))
        lang_cb = ttk.Combobox(top, textvariable=self.search_lang, values=["german","persian","english"], width=10, state="readonly")
        lang_cb.pack(side=tk.LEFT)

        ttk.Button(top, text="Find", command=self.do_search).pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="Clear", command=self.clear_search).pack(side=tk.LEFT)

        ttk.Button(top, text="Add / Edit", command=self.add_edit_entry).pack(side=tk.RIGHT, padx=6)
        ttk.Button(top, text="Export CSV", command=self.export_csv).pack(side=tk.RIGHT)
        ttk.Button(top, text="Import CSV", command=self.import_csv).pack(side=tk.RIGHT, padx=(0,6))

        main = ttk.Frame(self, padding=8)
        main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # List of results
        self.tree = ttk.Treeview(main, columns=("german","persian","english"), show="headings", selectmode="browse")
        self.tree.heading("german", text="German")
        self.tree.heading("persian", text="Persian (FA)")
        self.tree.heading("english", text="English")
        self.tree.column("german", width=240, anchor="w")
        self.tree.column("persian", width=260, anchor="w")
        self.tree.column("english", width=240, anchor="w")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Details
        right = ttk.Frame(main, padding=8)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.detail = tk.Text(right, height=20, width=40, wrap="word")
        self.detail.pack(fill=tk.BOTH, expand=True)

        # Status
        self.status = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status, anchor="w").pack(side=tk.BOTTOM, fill=tk.X)

    def populate_list(self, items):
        self.tree.delete(*self.tree.get_children())
        for idx, e in enumerate(items):
            self.tree.insert("", "end", iid=str(idx), values=(e.get("german",""), e.get("persian",""), e.get("english","")))
        self.status.set(f"{len(items)} entries")

    def do_search(self):
        q = normalize(self.search_var.get())
        lang = self.search_lang.get()
        if not q:
            self.populate_list(self.entries)
            return

        # exact, prefix, then fuzzy
        exact = []
        prefix = []
        rest = []
        for e in self.entries:
            val = normalize(e.get(lang, ""))
            if not val:
                continue
            if val == q:
                exact.append(e)
            elif val.startswith(q):
                prefix.append(e)
            else:
                rest.append(e)

        # fuzzy on remaining
        candidates = [e for e in rest if e.get(lang)]
        keys = [e.get(lang, "") for e in candidates]
        # get close matches indices
        close = difflib.get_close_matches(self.search_var.get(), keys, n=50, cutoff=0.6)
        fuzzy = [candidates[keys.index(c)] for c in close]

        results = exact + prefix + fuzzy
        self.populate_list(results)

    def clear_search(self):
        self.search_var.set("")
        self.populate_list(self.entries)

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel: return
        idx = int(sel[0])
        # Tree indices reflect current filtered list; reconstruct from displayed values
        vals = self.tree.item(sel[0], "values")
        # find the matching entry by german+persian pair
        match = None
        for e in self.entries:
            if e.get("german","") == vals[0] and e.get("persian","") == vals[1]:
                match = e
                break
        if not match:
            # fallback by german only
            for e in self.entries:
                if e.get("german","") == vals[0]:
                    match = e; break
        if not match:
            self.detail.delete("1.0", tk.END)
            self.detail.insert(tk.END, "No details.")
            return
        self.show_details(match)

    def show_details(self, e):
        self.detail.delete("1.0", tk.END)
        lines = []
        lines.append(f"German: {e.get('german','')}")
        if e.get("ipa"):
            lines.append(f"IPA: {e['ipa']}")
        if e.get("persian"):
            lines.append(f"Persian: {e['persian']}")
        if e.get("english"):
            lines.append(f"English: {e['english']}")
        if e.get("notes"):
            lines.append(f"Notes: {e['notes']}")
        self.detail.insert(tk.END, "\n".join(lines))

    def add_edit_entry(self):
        # Simple dialog to add or edit selected entry
        sel = self.tree.selection()
        current = None
        if sel:
            vals = self.tree.item(sel[0], "values")
            for e in self.entries:
                if e.get("german","") == vals[0] and e.get("persian","") == vals[1]:
                    current = e; break

        dialog = tk.Toplevel(self)
        dialog.title("Add / Edit Entry")
        dialog.geometry("420x340")
        dialog.transient(self)
        dialog.grab_set()

        fields = {}
        def row(label, key, default=""):
            frm = ttk.Frame(dialog, padding=4); frm.pack(fill="x")
            ttk.Label(frm, text=label, width=12).pack(side="left")
            var = tk.StringVar(value=(current.get(key,"") if current else default))
            ent = ttk.Entry(frm, textvariable=var)
            ent.pack(side="left", fill="x", expand=True)
            fields[key] = var
        row("German", "german")
        row("IPA", "ipa")
        row("Persian", "persian")
        row("English", "english")
        # Notes
        frm = ttk.Frame(dialog, padding=4); frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Notes", width=12).pack(side="left", anchor="n")
        notes = tk.Text(frm, height=6, width=30, wrap="word")
        notes.pack(side="left", fill="both", expand=True)
        if current and current.get("notes"):
            notes.insert("1.0", current["notes"])

        btns = ttk.Frame(dialog, padding=4); btns.pack(fill="x")
        def save_and_close():
            e = {
                "german": fields["german"].get().strip(),
                "ipa": fields["ipa"].get().strip(),
                "persian": fields["persian"].get().strip(),
                "english": fields["english"].get().strip(),
                "notes": notes.get("1.0", "end-1c").strip(),
            }
            if not e["german"]:
                messagebox.showerror("Error", "German field is required.")
                return
            # Update existing or append
            found = False
            for idx, ex in enumerate(self.entries):
                if ex.get("german","").lower() == e["german"].lower():
                    self.entries[idx] = e
                    found = True
                    break
            if not found:
                self.entries.append(e)
            self.data["entries"] = self.entries
            save_data(self.data)
            self.populate_list(self.entries)
            dialog.destroy()
        ttk.Button(btns, text="Save", command=save_and_close).pack(side="right")
        ttk.Button(btns, text="Cancel", command=dialog.destroy).pack(side="right", padx=6)

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not path: return
        import csv
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["german","ipa","persian","english","notes"])
            for e in self.entries:
                w.writerow([e.get(k,"") for k in ["german","ipa","persian","english","notes"]])
        messagebox.showinfo("Export", "CSV exported.")

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV","*.csv")])
        if not path: return
        import csv
        new_entries = []
        with open(path, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                new_entries.append({
                    "german": row.get("german",""),
                    "ipa": row.get("ipa",""),
                    "persian": row.get("persian",""),
                    "english": row.get("english",""),
                    "notes": row.get("notes",""),
                })
        # Merge by german (case-insensitive)
        merged = {e["german"].lower(): e for e in self.entries if e.get("german")}
        for e in new_entries:
            if e.get("german"):
                merged[e["german"].lower()] = e
        self.entries = list(merged.values())
        self.data["entries"] = self.entries
        save_data(self.data)
        self.populate_list(self.entries)
        messagebox.showinfo("Import", f"Imported {len(new_entries)} entries.")

if __name__ == "__main__":
    app = DictApp()
    app.mainloop()
