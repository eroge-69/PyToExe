import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import hashlib
from datetime import datetime

class ValidierungsViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Validierungsviewer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5f5")

        self.filename = None
        self.filepath = None
        self.data = None
        self.check_vars = {}
        self.kuerzel_var = tk.StringVar()
        self.step_status = {}
        self.testziel_erreicht = tk.BooleanVar()

        control_frame = tk.Frame(root, bg="#f5f5f5")
        control_frame.pack(pady=10, fill="x")

        tk.Button(control_frame, text="JSON-Datei laden", command=self.load_json, bg="#4caf50", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        self.file_label = tk.Label(control_frame, text="Keine Datei geladen", fg="gray", bg="#f5f5f5", font=("Arial", 10, "italic"))
        self.file_label.pack(side="left", padx=10)
        self.save_button = tk.Button(control_frame, text="Validierung speichern", command=self.save_validated, state="disabled", bg="#2196f3", fg="white", font=("Arial", 10, "bold"))
        self.save_button.pack(side="right", padx=10)

        form_frame = tk.Frame(root, bg="#f5f5f5")
        form_frame.pack(fill="x", padx=20)
        tk.Label(form_frame, text="Kuerzel:*", bg="#f5f5f5", font=("Arial", 10)).pack(side="left")
        tk.Entry(form_frame, textvariable=self.kuerzel_var, width=20).pack(side="left", padx=10)

        self.meta_frame = tk.LabelFrame(root, text="\ud83d\udccb Testziel und Beschreibung", padx=10, pady=5, bg="#ffffff")
        self.meta_frame.pack(fill="x", padx=20, pady=10)
        self.description_label = tk.Label(self.meta_frame, text="", font=("Arial", 10), wraplength=1000, justify="left", bg="#ffffff")
        self.description_label.pack(anchor="w")
        tk.Checkbutton(self.meta_frame, text="Testziel wurde mit den Testschritten erreicht", variable=self.testziel_erreicht, bg="#ffffff").pack(anchor="w", pady=5)

        self.content_frame = tk.Frame(root, bg="#f5f5f5")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.step_listbox = tk.Listbox(self.content_frame, width=40, font=("Arial", 10))
        self.step_listbox.pack(side="left", fill="y", padx=(0, 10))
        self.step_listbox.bind("<<ListboxSelect>>", self.select_step)

        self.detail_canvas = tk.Canvas(self.content_frame, bg="#ffffff", bd=2, relief="ridge")
        self.detail_frame = tk.Frame(self.detail_canvas, bg="#ffffff")
        self.scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=self.detail_canvas.yview)
        self.detail_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.detail_canvas.create_window((0, 0), window=self.detail_frame, anchor="nw")
        self.detail_frame.bind("<Configure>", lambda e: self.detail_canvas.configure(scrollregion=self.detail_canvas.bbox("all")))
        self.detail_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def load_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON-Dateien", "*.json")])
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            json_raw = f.read()

        try:
            loaded_data = json.loads(json_raw)
        except json.JSONDecodeError:
            messagebox.showerror("Fehler", "Ungueltige JSON-Datei.")
            return

        stored_hash = loaded_data.get("DateiHash", "")
        loaded_data["DateiHash"] = ""
        recomputed_raw = json.dumps(loaded_data, separators=(",", ":"), ensure_ascii=False)
        recomputed_hash = hashlib.sha256(recomputed_raw.encode("utf-8")).hexdigest()

        if stored_hash != recomputed_hash:
            messagebox.showwarning("Warnung", "Datei wurde veraendert (Hash stimmt nicht)!")
        else:
            messagebox.showinfo("OK", "Datei-Integritaet bestaetigt.")

        loaded_data["DateiHash"] = stored_hash
        self.data = loaded_data
        self.filename = os.path.basename(path)
        self.filepath = os.path.dirname(path)
        self.file_label.config(text=self.filename)

        beschreibung = self.data.get("Beschreibung", "")
        meta = self.data.get("EditorMetadaten", {}).get("BetriebsstellenMapping", [{}])[0]
        anlage = meta.get("Anlage", "Unbekannt")
        name = meta.get("Name", "")
        self.description_label.config(text=f"{beschreibung}\nAnlage: {anlage}\nBetriebsstelle: {name}")

        self.steps = {s['ID']: s for s in self.data['Testschritte']}
        self.step_status = {sid: False for sid in self.steps}
        self.check_vars.clear()
        self.step_listbox.delete(0, tk.END)

        for sid, step in self.steps.items():
            action_name = step['Aktion']['Beschreibung']
            self.step_listbox.insert(tk.END, f"{sid}: {action_name}")

        validierung = self.data.get("Validierung", {})
        self.testziel_erreicht.set(validierung.get("TestzielErreicht", False))
        status_data = validierung.get("Status", {})
        for key, value in status_data.items():
            self.check_vars[key] = tk.BooleanVar(value=value)

        for sid in self.steps:
            self.set_step_status(sid)

    def select_step(self, event):
        selection = self.step_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        step_id = list(self.steps.keys())[index]
        step = self.steps[step_id]

        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        action = step['Aktion']
        tk.Label(self.detail_frame, text=f"Aktion: {action['Beschreibung']}", font=("Arial", 12, "bold"), bg="#ffffff", anchor="w", justify="left", wraplength=900).pack(anchor="w", padx=10, pady=5)
        tk.Label(self.detail_frame, text=f"Typ: {action['Handlung']}\nElement: {action['Elementbezeichner']}", bg="#ffffff", justify="left").pack(anchor="w", padx=20)
        a_var = self.check_vars.setdefault(f"A_{step_id}", tk.BooleanVar())
        tk.Checkbutton(self.detail_frame, text="OK", variable=a_var, bg="#ffffff", command=lambda: self.set_step_status(step_id)).pack(anchor="w", padx=30, pady=5)

        for reaction in step.get("Reaktionen", []):
            r_frame = tk.Frame(self.detail_frame, bg="#eef7ff", padx=5, pady=5, bd=1, relief="solid")
            r_frame.pack(fill="x", padx=30, pady=5)
            tk.Label(r_frame, text=f"Reaktion {reaction['ID']}: {reaction['Beschreibung']}", font=("Arial", 10, "bold"), bg="#eef7ff", anchor="w", justify="left", wraplength=850).pack(anchor="w")
            details = (
                f"Typ: {reaction['Reaktion']}\n"
                f"Element: {reaction['Elementbezeichner']}\n"
                f"Betriebsstelle: {reaction['Betriebsstelle']}\n"
                f"Timeout: {reaction.get('TimeoutMsec', 0)} ms"
            )
            tk.Label(r_frame, text=details, bg="#eef7ff", justify="left").pack(anchor="w")
            if reaction.get("Parameter"):
                param_text = json.dumps(reaction['Parameter'], ensure_ascii=False, indent=2)
                tk.Label(r_frame, text=f"Parameter:\n{param_text}", bg="#eef7ff", justify="left", font=("Courier", 9)).pack(anchor="w")
            r_var = self.check_vars.setdefault(reaction['ID'], tk.BooleanVar())
            tk.Checkbutton(r_frame, text="OK", variable=r_var, bg="#eef7ff", command=lambda sid=step_id: self.set_step_status(sid)).pack(anchor="w", pady=2)

        self.save_button.config(state="normal")

    def set_step_status(self, step_id):
        a_ok = self.check_vars.get(f"A_{step_id}", tk.BooleanVar()).get()
        all_r_ok = all(self.check_vars.get(r['ID'], tk.BooleanVar()).get() for r in self.steps[step_id].get("Reaktionen", []))
        self.step_status[step_id] = a_ok and all_r_ok
        self.update_step_background(step_id)

    def update_step_background(self, step_id):
        index = list(self.steps.keys()).index(step_id)
        color = "#c8e6c9" if self.step_status[step_id] else "#ffcdd2"
        self.step_listbox.itemconfig(index, {'bg': color})

    def save_validated(self):
        kürzel = self.kürzel_var.get().strip()
        if not kürzel:
            messagebox.showerror("Fehler", "Bitte ein Kürzel eingeben.")
            return

        erfolgreich = all(self.step_status.values()) and self.testziel_erreicht.get()
        status_data = {k: v.get() for k, v in self.check_vars.items()}

        validated_data = self.data.copy()
        validated_data["Validierung"] = {
            "Kürzel": kürzel,
            "Datum": datetime.now().strftime("%Y-%m-%d"),
            "Uhrzeit": datetime.now().strftime("%H:%M:%S"),
            "Status": status_data,
            "Erfolgreich": erfolgreich,
            "TestzielErreicht": self.testziel_erreicht.get()
        }

        validated_data["DateiHash"] = ""
        raw_json = json.dumps(validated_data, separators=(",", ":"), ensure_ascii=False)
        hash_value = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
        validated_data["DateiHash"] = hash_value

        base_name = os.path.splitext(self.filename)[0]
        status_prefix = "validiert" if erfolgreich else "nicht_validiert"
        save_name = f"{base_name}_{status_prefix}_{kürzel}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_path = os.path.join(self.filepath, save_name)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(validated_data, f, indent=2, ensure_ascii=False)

        messagebox.showinfo("Gespeichert", f"Validierung {'erfolgreich' if erfolgreich else 'NICHT erfolgreich'} gespeichert als:\n{save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ValidierungsViewer(root)
    root.mainloop()
