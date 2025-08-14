
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd, math, datetime
import matplotlib.pyplot as plt

CP_WATER = 4.186  # kJ/kg-K
DENSITY_WATER = 1000  # kg/m3

# Default catalog (sample) - replace with company's actual catalog CSV
DEFAULT_CATALOG = [
    {"type": "open", "model": "CT-60",  "nom_kw": 600,  "min_flow": 100, "max_flow": 220, "fan_kw": 5.5, "footprint": "1.4x1.4", "height_m": 2.2, "notes": ""},
    {"type": "open", "model": "CT-90",  "nom_kw": 900,  "min_flow": 150, "max_flow": 320, "fan_kw": 7.5, "footprint": "1.6x1.6", "height_m": 2.4, "notes": ""},
    {"type": "open", "model": "CT-120", "nom_kw": 1200, "min_flow": 200, "max_flow": 420, "fan_kw": 11,  "footprint": "1.8x1.8", "height_m": 2.6, "notes": ""},
    {"type": "closed","model": "FC-60", "nom_kw": 520,  "min_flow": 90,  "max_flow": 200, "fan_kw": 7.5, "footprint": "1.6x1.6", "height_m": 2.6, "notes": "coil"},
    {"type": "closed","model": "FC-90", "nom_kw": 800,  "min_flow": 140, "max_flow": 300, "fan_kw": 11,  "footprint": "1.8x1.8", "height_m": 2.8, "notes": "coil"}
]

def estimate_env_correction(approach, wbt, mode):
    # same simple env correction as previous versions (for catalog reference conversion)
    REF_APPROACH = 5.0
    REF_WBT = 24.0
    if approach <= 0.1:
        approach = 0.1
    fa = (REF_APPROACH / approach)
    fw = 1.0 - 0.01 * (wbt - REF_WBT)
    fw = max(0.75, min(1.10, fw))
    fa = max(0.60, min(1.50, fa))
    mode_factor = 0.95 if mode == "closed" else 1.0
    return fa * fw * mode_factor

def select_model(catalog, mode, q_kw_required_corr, vdot_m3h):
    candidates = []
    for item in catalog:
        if item.get("type") != mode:
            continue
        cap = float(item.get("nom_kw", 0.0))
        min_flow = float(item.get("min_flow", 0.0))
        max_flow = float(item.get("max_flow", 1e9))
        if cap >= q_kw_required_corr and (min_flow <= vdot_m3h <= max_flow):
            candidates.append(item)
    if not candidates:
        for item in catalog:
            if item.get("type") != mode:
                continue
            cap = float(item.get("nom_kw", 0.0))
            if cap >= q_kw_required_corr:
                candidates.append(item)
    if not candidates:
        return None
    candidates.sort(key=lambda x: float(x.get("nom_kw", 0.0)))
    return candidates[0]

def load_catalog_from_csv(path):
    import csv
    out = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for k in ["nom_kw","min_flow","max_flow","fan_kw","height_m"]:
                if k in row and row[k] != "":
                    try:
                        row[k] = float(row[k])
                    except:
                        pass
            out.append(row)
    return out

class App:
    def __init__(self, root):
        self.root = root
        root.title("Cooling Tower Selector - v3 (Project Form + Water Balance)")
        root.geometry("980x720")
        self.catalog = DEFAULT_CATALOG.copy()
        self.last_results = None

        main = ttk.Frame(root, padding=10); main.pack(fill=tk.BOTH, expand=True)

        # Project info frame
        proj = ttk.LabelFrame(main, text="اطلاعات پروژه (Project)"); proj.pack(fill=tk.X, pady=6)
        self.project_title = self._add_row(proj, "1. عنوان پروژه:")
        self.buyer_name = self._add_row(proj, "2. نام خریدار:")
        self.sales_pos = self._add_row(proj, "3. شماره موقعیت فروش:")
        self.install_addr = self._add_row(proj, "4. آدرس محل نصب:")

        # Operational inputs
        inp = ttk.LabelFrame(main, text="شرایط عملکردی (عملیات)"); inp.pack(fill=tk.X, pady=6)
        self.flow_entry = self._add_row(inp, "5. ظرفیت آب در گردش کل (m³/h):", "200")
        self.tin_entry = self._add_row(inp, "6. دمای آب گرم ورودی Tin (°C):", "35")
        self.tout_entry = self._add_row(inp, "7. دمای آب سرد خروجی Tout (°C):", "29")
        self.wbt_entry = self._add_row(inp, "8. دمای مرطوب محیط WBT (°C):", "24")
        self.coc_entry = self._add_row(inp, "9. ضریب COC (Cycles of Concentration):", "3")

        # Catalog controls and actions
        cat_frame = ttk.Frame(main); cat_frame.pack(fill=tk.X, pady=6)
        ttk.Button(cat_frame, text="لود کاتالوگ CSV...", command=self.load_catalog).pack(side=tk.RIGHT, padx=4)
        ttk.Button(cat_frame, text="قالب نمونه CSV", command=self.show_csv_help).pack(side=tk.RIGHT, padx=4)
        ttk.Button(cat_frame, text="محاسبه و انتخاب مدل", command=self.calculate_and_select).pack(side=tk.RIGHT, padx=4)
        ttk.Button(cat_frame, text="خروجی Excel", command=self.export_excel).pack(side=tk.RIGHT, padx=4)
        ttk.Button(cat_frame, text="خروجی PDF", command=self.export_pdf).pack(side=tk.RIGHT, padx=4)

        # Output text
        out = ttk.LabelFrame(main, text="خروجی (نتایج)"); out.pack(fill=tk.BOTH, expand=True, pady=6)
        self.result_box = tk.Text(out, height=18, state="disabled", wrap="word"); self.result_box.pack(fill=tk.BOTH, expand=True)

        footer = ttk.Label(main, text="نسخه بتا v3 | خروجی Excel و PDF | برای انتخاب نهایی از دیتاشیت سازنده استفاده کنید.", foreground="#444")
        footer.pack(pady=6)

    def _add_row(self, parent, label, default=""):
        row = ttk.Frame(parent); row.pack(fill=tk.X, pady=3)
        entry = ttk.Entry(row, width=20, justify="center"); entry.pack(side=tk.RIGHT)
        entry.insert(0, default)
        ttk.Label(row, text=label).pack(side=tk.RIGHT, padx=8)
        return entry

    def show_csv_help(self):
        message = ("قالب CSV:\n"
                   "type,model,nom_kw,min_flow,max_flow,fan_kw,footprint,height_m,notes\n"
                   "type = open یا closed\n"
                   "nom_kw = ظرفیت نامی (kW) در شرایط مرجع\n"
                   "min_flow/max_flow = بازه مجاز دبی آب (m³/h)\n")
        messagebox.showinfo("قالب CSV", message)

    def load_catalog(self):
        path = filedialog.askopenfilename(title='انتخاب فایل CSV کاتالوگ', filetypes=[('CSV files','*.csv')])
        if not path: return
        try:
            self.catalog = load_catalog_from_csv(path)
            messagebox.showinfo("کاتالوگ", f"کاتالوگ با {len(self.catalog)} ردیف لود شد.")
        except Exception as e:
            messagebox.showerror("خطا در لود کاتالوگ", str(e))

    def calculate_and_select(self):
        try:
            flow_m3h = float(self.flow_entry.get())
            tin = float(self.tin_entry.get())
            tout = float(self.tout_entry.get())
            wbt = float(self.wbt_entry.get())
            coc = float(self.coc_entry.get())
            if tout >= tin:
                messagebox.showerror("خطا", "دمای خروجی باید کمتر از دمای ورودی باشد.")
                return
            rng = tin - tout
            # mass flow kg/s
            m_dot = (flow_m3h * 1000.0) / 3600.0
            # Q in kW
            q_kw = (m_dot * CP_WATER * rng)  # since CP in kJ/kg-K and m_dot kg/s, result kW
            # evaporation (approximation): Evap (m3/h) ≈ 0.001 * circulating_flow (m3/h) * Range(°C)
            evap_m3h = 0.001 * flow_m3h * rng
            # drift: default modern low-drift 0.002% (0.00002) of circulating flow
            drift_fraction = 0.00002
            drift_m3h = drift_fraction * flow_m3h
            # blowdown via COC: Blowdown = Evap / (COC - 1)  (if COC>1)
            blowdown_m3h = evap_m3h / (coc - 1.0) if coc > 1.0 else 0.0
            makeup_m3h = evap_m3h + drift_m3h + blowdown_m3h

            # model selection: convert field required to catalog nominal via env correction
            approach = tout - wbt
            f_env = estimate_env_correction(approach, wbt, "open")  # mode neutral here; user may supply type later
            # we assume open by default; allow selection later if needed
            q_required_field = q_kw  # for open
            q_nom_needed = q_required_field / max(0.01, f_env)

            chosen = select_model(self.catalog, "open", q_nom_needed, flow_m3h)
            # Prepare textual report
            lines = []
            lines.append(f"Project: {self.project_title.get()}")
            lines.append(f"Buyer: {self.buyer_name.get()} | Sales pos: {self.sales_pos.get()}")
            lines.append(f"Address: {self.install_addr.get()}")
            lines.append("-"*60)
            lines.append(f"Flow (circulating): {flow_m3h:,.3f} m³/h | Tin: {tin:.2f} °C | Tout: {tout:.2f} °C | WBT: {wbt:.2f} °C")
            lines.append(f"Range = {rng:.2f} °C | Approach = {approach:.2f} °C")
            lines.append(f"Calculated thermal duty (Q): {q_kw:,.2f} kW")
            lines.append("-"*40)
            lines.append("Water balance (approximate):")
            lines.append(f"Evaporation ≈ {evap_m3h:,.4f} m³/h")
            lines.append(f"Drift (assumed {drift_fraction*100:.4f}% of flow) ≈ {drift_m3h:,.4f} m³/h")
            lines.append(f"Blowdown (COC={coc}) ≈ {blowdown_m3h:,.4f} m³/h")
            lines.append(f"Make-up ≈ {makeup_m3h:,.4f} m³/h")
            lines.append(f"Environmental correction factor (f_env) ≈ {f_env:.3f}")
            lines.append(f"Equivalent nominal capacity required (catalog ref) ≈ {q_nom_needed:,.1f} kW")
            if chosen:
                lines.append("-"*40)
                lines.append("Selected model (based on current catalog & criteria):")
                lines.append(f"Model: {chosen.get('model')} | Type: {chosen.get('type')} | Nominal cap: {chosen.get('nom_kw')} kW")
                lines.append(f"Flow range: {chosen.get('min_flow')} - {chosen.get('max_flow')} m³/h")
                lines.append(f"Fan power: {chosen.get('fan_kw')} kW | Footprint: {chosen.get('footprint')} | Height: {chosen.get('height_m')} m")
                lines.append(f"Notes: {chosen.get('notes')}")
            else:
                lines.append("❗ بر اساس کاتالوگ فعلی، مدلی یافت نشد که پاسخگو باشد.")
            report_text = "\\n".join(lines)
            self.result_box.configure(state="normal")
            self.result_box.delete("1.0", tk.END)
            self.result_box.insert(tk.END, report_text)
            self.result_box.configure(state="disabled")

            # store last results
            self.last_results = {
                "project_title": self.project_title.get(),
                "buyer_name": self.buyer_name.get(),
                "sales_pos": self.sales_pos.get(),
                "install_addr": self.install_addr.get(),
                "flow_m3h": flow_m3h,
                "tin": tin,
                "tout": tout,
                "wbt": wbt,
                "coc": coc,
                "range": rng,
                "approach": approach,
                "q_kw": q_kw,
                "evap_m3h": evap_m3h,
                "drift_m3h": drift_m3h,
                "blowdown_m3h": blowdown_m3h,
                "makeup_m3h": makeup_m3h,
                "f_env": f_env,
                "q_nom_needed": q_nom_needed,
                "selected": chosen
            }

        except Exception as e:
            messagebox.showerror("خطا", str(e))

    def export_excel(self):
        if not self.last_results:
            messagebox.showwarning("هشدار", "ابتدا محاسبه را اجرا کنید.")
            return
        df_in = pd.DataFrame({
            "پارامتر": ["Project","Buyer","Sales pos","Address","Flow (m3/h)","Tin (°C)","Tout (°C)","WBT (°C)","Range (°C)","Approach (°C)","Q (kW)","Evap (m3/h)","Drift (m3/h)","Blowdown (m3/h)","Make-up (m3/h)","f_env","q_nom_needed (kW)"],
            "مقدار": [self.last_results["project_title"], self.last_results["buyer_name"], self.last_results["sales_pos"], self.last_results["install_addr"], self.last_results["flow_m3h"], self.last_results["tin"], self.last_results["tout"], self.last_results["wbt"], self.last_results["range"], self.last_results["approach"], self.last_results["q_kw"], self.last_results["evap_m3h"], self.last_results["drift_m3h"], self.last_results["blowdown_m3h"], self.last_results["makeup_m3h"], self.last_results["f_env"], self.last_results["q_nom_needed"]]
        })
        if self.last_results["selected"]:
            s = self.last_results["selected"]
            df_sel = pd.DataFrame({"Field":["Model","Type","Nominal (kW)","Flow range (m3/h)","Fan kW","Footprint","Height m","Notes"],
                                   "Value":[s.get("model"), s.get("type"), s.get("nom_kw"), f\"{s.get('min_flow')} - {s.get('max_flow')}\", s.get("fan_kw"), s.get("footprint"), s.get("height_m"), s.get("notes")]})
        else:
            df_sel = pd.DataFrame({"Field":["Selected"], "Value":["No suitable model found in catalog"]})

        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")], initialfile="cooling_tower_report.xlsx")
        if not path: return
        with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
            df_in.to_excel(writer, sheet_name="Inputs_Results", index=False)
            df_sel.to_excel(writer, sheet_name="Selected_Model", index=False)
        messagebox.showinfo("ذخیره شد", f"فایل اکسل ذخیره شد:\\n{path}")

    def export_pdf(self):
        if not self.last_results:
            messagebox.showwarning("هشدار", "ابتدا محاسبه را اجرا کنید.")
            return
        # Create a simple PDF using matplotlib text (works without reportlab)
        txt_lines = []
        txt_lines.append("Cooling Tower Selection Report")
        txt_lines.append(f"Project: {self.last_results['project_title']}")
        txt_lines.append(f"Buyer: {self.last_results['buyer_name']} | Sales pos: {self.last_results['sales_pos']}")
        txt_lines.append(f"Address: {self.last_results['install_addr']}")
        txt_lines.append("")
        txt_lines.append("Design conditions:")
        txt_lines.append(f"Flow (m3/h): {self.last_results['flow_m3h']} | Tin: {self.last_results['tin']} °C | Tout: {self.last_results['tout']} °C | WBT: {self.last_results['wbt']} °C")
        txt_lines.append(f"Range: {self.last_results['range']} °C | Approach: {self.last_results['approach']} °C")
        txt_lines.append(f"Calculated Q: {self.last_results['q_kw']:.2f} kW")
        txt_lines.append("")
        txt_lines.append("Water balance (approx):")
        txt_lines.append(f"Evaporation: {self.last_results['evap_m3h']:.4f} m3/h")
        txt_lines.append(f"Drift: {self.last_results['drift_m3h']:.4f} m3/h")
        txt_lines.append(f"Blowdown: {self.last_results['blowdown_m3h']:.4f} m3/h")
        txt_lines.append(f"Make-up: {self.last_results['makeup_m3h']:.4f} m3/h")
        txt_lines.append("")
        if self.last_results['selected']:
            s = self.last_results['selected']
            txt_lines.append("Selected model:")
            txt_lines.append(f"Model: {s.get('model')} | Type: {s.get('type')} | Nominal: {s.get('nom_kw')} kW")
            txt_lines.append(f"Flow range: {s.get('min_flow')} - {s.get('max_flow')} m3/h")
            txt_lines.append(f"Fan kW: {s.get('fan_kw')} | Footprint: {s.get('footprint')} | Height: {s.get('height_m')} m")
        else:
            txt_lines.append("No suitable model found in catalog.")

        # draw onto figure
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 in inches
        fig.text(0.01, 0.99, "\\n".join(txt_lines), va='top', fontsize=10, family='sans-serif')
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")], initialfile="cooling_tower_report.pdf")
        if not path:
            plt.close(fig); return
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        messagebox.showinfo("ذخیره شد", f"فایل PDF ذخیره شد:\\n{path}")

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
