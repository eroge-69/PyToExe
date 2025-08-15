import json
    import os
    import sys
    import logging
    from datetime import datetime
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from pathlib import Path

    # Dependencies
    try:
        from nida import load_user
    except Exception as e:
        load_user = None

    APP_DIR = Path(__file__).resolve().parent.parent
    ASSETS_DIR = APP_DIR / "assets"
    EXPORTS_DIR = APP_DIR / "exports"
    LOGS_DIR = APP_DIR / "logs"

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Logging setup
    log_file = LOGS_DIR / "app.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger("NIDA_APP")

    # Load config
    CONFIG = {
        "app_name": "NIDA Desktop App",
        "log_level": "INFO",
        "save_folder": "exports",
        "github_repo": "Kalebu/Nida",
    }
    cfg_path = APP_DIR / "config.json"
    if cfg_path.exists():
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                CONFIG.update(json.load(f))
        except Exception as e:
            logger.warning("Failed to read config.json: %s", e)

    # Adjust log level from config
    try:
        logger.setLevel(getattr(logging, CONFIG.get("log_level", "INFO").upper(), logging.INFO))
    except Exception:
        pass

    class NidaApp(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title(CONFIG.get("app_name", "NIDA Desktop App"))
            self.geometry("900x600")
            self.minsize(800, 520)

            # Styles
            style = ttk.Style(self)
            try:
                self.call("tk", "scaling", 1.25)
            except Exception:
                pass
            style.configure("TButton", padding=6)
            style.configure("TLabel", padding=4)
            style.configure("Treeview", rowheight=26)

            self._build_ui()

        def _build_ui(self):
            container = ttk.Frame(self, padding=12)
            container.pack(fill="both", expand=True)

            # Top input frame
            top = ttk.Frame(container)
            top.pack(fill="x", pady=(0, 8))

            ttk.Label(top, text="National ID (NIN):").pack(side="left")
            self.nin_var = tk.StringVar()
            self.nin_entry = ttk.Entry(top, textvariable=self.nin_var, width=40)
            self.nin_entry.pack(side="left", padx=8)
            self.nin_entry.focus_set()

            self.fetch_btn = ttk.Button(top, text="Fetch", command=self.on_fetch)
            self.fetch_btn.pack(side="left")

            self.clear_btn = ttk.Button(top, text="Clear", command=self.clear_results)
            self.clear_btn.pack(side="left", padx=(8,0))

            # Treeview for results
            columns = ("key", "value")
            self.tree = ttk.Treeview(container, columns=columns, show="headings", selectmode="browse")
            self.tree.heading("key", text="Field")
            self.tree.heading("value", text="Value")
            self.tree.column("key", width=240, anchor="w")
            self.tree.column("value", width=600, anchor="w")
            self.tree.pack(fill="both", expand=True)

            # Bottom buttons
            bottom = ttk.Frame(container)
            bottom.pack(fill="x", pady=(8,0))

            self.save_json_btn = ttk.Button(bottom, text="Save as JSON", command=self.save_json, state="disabled")
            self.save_json_btn.pack(side="left")

            self.save_csv_btn = ttk.Button(bottom, text="Save as CSV", command=self.save_csv, state="disabled")
            self.save_csv_btn.pack(side="left", padx=(8,0))

            self.copy_btn = ttk.Button(bottom, text="Copy JSON to Clipboard", command=self.copy_json, state="disabled")
            self.copy_btn.pack(side="left", padx=(8,0))

            self.status_var = tk.StringVar(value="Ready")
            status = ttk.Label(bottom, textvariable=self.status_var, anchor="w")
            status.pack(side="right")

            # Data holder
            self.current_payload = None

        def set_status(self, text):
            self.status_var.set(text)
            self.update_idletasks()

        def clear_results(self):
            for i in self.tree.get_children():
                self.tree.delete(i)
            self.current_payload = None
            self.save_json_btn.config(state="disabled")
            self.save_csv_btn.config(state="disabled")
            self.copy_btn.config(state="disabled")
            self.set_status("Cleared")

        def on_fetch(self):
            nin = self.nin_var.get().strip()
            if not nin:
                messagebox.showwarning("Validation", "Weka NIN kwanza.")
                return

            if load_user is None:
                messagebox.showerror("Dependency Missing",
                    "Package 'nida' haijapatikana. Tafadhali kimbiza:

pip install -r requirements.txt")
                return

            self.set_status("Fetching...")
            self.fetch_btn.config(state="disabled")
            self.after(100, lambda: self._do_fetch(nin))

        def _do_fetch(self, nin):
            try:
                logger.info("Fetching data for NIN=%s", nin)
                payload = load_user(national_id=nin)
                if not payload:
                    messagebox.showinfo("No Data", "Hakuna taarifa zilizopatikana kwa NIN ulioweka.")
                    self.set_status("No data")
                    return
                # Normalize dict
                if hasattr(payload, "dict"):
                    payload = payload.dict()
                elif not isinstance(payload, dict):
                    # Try to coerce to dict
                    try:
                        import dataclasses as dc
                        if dc.is_dataclass(payload):
                            payload = dc.asdict(payload)
                        else:
                            payload = dict(payload)
                    except Exception:
                        payload = {"result": str(payload)}

                self.current_payload = payload
                self._render_payload(payload)
                self.set_status("Done")
                self.save_json_btn.config(state="normal")
                self.save_csv_btn.config(state="normal")
                self.copy_btn.config(state="normal")
            except Exception as e:
                logger.exception("Fetch failed")
                messagebox.showerror("Error", f"Imeshindwa kupata taarifa:\n{e}")
                self.set_status("Failed")
            finally:
                self.fetch_btn.config(state="normal")

        def _render_payload(self, payload: dict):
            # Clear existing
            for i in self.tree.get_children():
                self.tree.delete(i)

            def flatten(prefix, obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        yield from flatten(f"{prefix}.{k}" if prefix else str(k), v)
                elif isinstance(obj, list):
                    for idx, v in enumerate(obj):
                        yield from flatten(f"{prefix}[{idx}]", v)
                else:
                    yield (prefix, "" if obj is None else str(obj))

            for k, v in flatten("", payload):
                self.tree.insert("", "end", values=(k, v))

        def save_json(self):
            if not self.current_payload:
                return
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"NIDA_{ts}.json"
            path = filedialog.asksaveasfilename(defaultextension=".json", initialfile=default_name,
                                                filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
            if not path:
                return
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.current_payload, f, indent=2, ensure_ascii=False)
            self.set_status(f"Saved JSON: {os.path.basename(path)}")

        def save_csv(self):
            if not self.current_payload:
                return
            try:
                import pandas as pd
            except Exception:
                messagebox.showerror("Missing dependency", "Pandas haijasakinishwa. Kimbiza: pip install pandas")
                return
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"NIDA_{ts}.csv"
            path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=default_name,
                                                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
            if not path:
                return

            rows = []
            def flatten(prefix, obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        yield from flatten(f"{prefix}.{k}" if prefix else str(k), v)
                elif isinstance(obj, list):
                    for idx, v in enumerate(obj):
                        yield from flatten(f"{prefix}[{idx}]", v)
                else:
                    yield (prefix, "" if obj is None else str(obj))

            for k, v in flatten("", self.current_payload):
                rows.append({"field": k, "value": v})

            import pandas as pd
            df = pd.DataFrame(rows)
            df.to_csv(path, index=False)
            self.set_status(f"Saved CSV: {os.path.basename(path)}")

        def copy_json(self):
            if not self.current_payload:
                return
            try:
                data = json.dumps(self.current_payload, indent=2, ensure_ascii=False)
                self.clipboard_clear()
                self.clipboard_append(data)
                self.update()
                self.set_status("JSON copied to clipboard")
            except Exception as e:
                messagebox.showerror("Error", f"Imeshindikana kunakili: {e}")

    if __name__ == "__main__":
        app = NidaApp()
        app.mainloop()