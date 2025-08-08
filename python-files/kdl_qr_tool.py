import tkinter as tk
from tkinter import ttk, messagebox
import json
import qrcode
from PIL import Image, ImageTk, ImageWin
import os
import sys
import win32print
import win32ui
import win32con

FALLBACK_KDL_DATA = [
    {"code": "A01", "display": "Cholera durch Vibrio cholerae 01, Biovar cholerae"},
    {"code": "A02", "display": "Salmonellenenteritis"},
    {"code": "B20", "display": "HIV-Krankheit, durch HIV-1-Virus"},
    {"code": "C34", "display": "Bösartige Neubildung: Bronchien und Lunge"},
    {"code": "E11", "display": "Nicht insulinabhängiger Diabetes mellitus"},
    {"code": "I10", "display": "Essentielle (primäre) Hypertonie"},
    {"code": "J45", "display": "Asthma bronchiale"},
    {"code": "K35", "display": "Akute Appendizitis"},
    {"code": "M54", "display": "Rückenschmerzen"},
    {"code": "N39", "display": "Sonstige Krankheiten der Harnorgane"}
]

def load_kdl_data():
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(here, "kdl_embedded.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and all("code" in x and "display" in x for x in data):
                    return data
    except Exception:
        pass
    return FALLBACK_KDL_DATA

KDL_DATA = load_kdl_data()

APP_DIR = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), "KDL_QR_Tool")
USAGE_FILE = os.path.join(APP_DIR, "kdl_usage.json")
os.makedirs(APP_DIR, exist_ok=True)

def load_usage():
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_usage(data):
    try:
        with open(USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

usage_data = load_usage()

class KDLQRApp:
    def __init__(self, root: tk.Tk, fallnummer_param=None):
        self.root = root
        self.root.title("KDL QR Tool")

        tk.Label(root, text="Fallnummer:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.fallnummer_entry = tk.Entry(root)
        self.fallnummer_entry.grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        if fallnummer_param:
            self.fallnummer_entry.insert(0, fallnummer_param)

        tk.Label(root, text="KDL:").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.kdl_var = tk.StringVar()
        self.kdl_dropdown = ttk.Combobox(root, textvariable=self.kdl_var, state="readonly", width=60)
        self.update_dropdown()
        self.kdl_dropdown.grid(row=1, column=1, padx=6, pady=6, sticky="ew")

        self.qr_label = tk.Label(root)
        self.qr_label.grid(row=2, column=0, padx=6, pady=6, sticky="nw")

        btn_frame = tk.Frame(root)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="QR-Code erstellen", command=self.generate_qr).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Drucken", command=self.print_qr).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Favoriten zurücksetzen", command=self.reset_favorites).pack(side="left", padx=6)

        root.grid_columnconfigure(1, weight=1)

        self.qr_pil = None
        self.qr_img = None

    def update_dropdown(self):
        count_by_code = {k: v for k, v in usage_data.items() if any(e["code"] == k for e in KDL_DATA)}
        favorites_sorted = sorted(count_by_code.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        favorite_codes = [code for code, _ in favorites_sorted]

        favorite_displays = [e["display"] for e in KDL_DATA if e["code"] in favorite_codes]
        remaining_displays = [e["display"] for e in sorted(KDL_DATA, key=lambda x: x["display"]) if e["display"] not in favorite_displays]

        values = []
        if favorite_displays:
            values.extend(favorite_displays)
            values.append("---")
        values.extend(remaining_displays)
        self.kdl_dropdown["values"] = values

    def get_kdl_code(self, display: str):
        for entry in KDL_DATA:
            if entry["display"] == display:
                return entry["code"]
        return None

    def generate_qr(self):
        fallnummer = self.fallnummer_entry.get().strip()
        display = self.kdl_var.get().strip()
        if not display or display == "---":
            messagebox.showerror("Fehler", "Bitte einen KDL-Eintrag wählen.")
            return

        code = self.get_kdl_code(display)
        if not fallnummer or not code:
            messagebox.showerror("Fehler", "Bitte Fallnummer und KDL auswählen.")
            return

        qr_data = f"{{sys:GUN_CID,cid:{fallnummer},formid:{code}}}"
        self.qr_pil = qrcode.make(qr_data)

        preview = self.qr_pil.resize((200, 200), Image.NEAREST)
        self.qr_img = ImageTk.PhotoImage(preview)
        self.qr_label.configure(image=self.qr_img)

        usage_data[code] = usage_data.get(code, 0) + 1
        save_usage(usage_data)
        self.update_dropdown()

    def print_qr(self):
        if self.qr_pil is None:
            messagebox.showerror("Fehler", "Bitte zuerst einen QR-Code generieren.")
            return

        try:
            printer = win32print.GetDefaultPrinter()
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(printer)
            hdc.StartDoc("KDL QR Label")
            hdc.StartPage()

            dpi_x = hdc.GetDeviceCaps(win32con.LOGPIXELSX)
            dpi_y = hdc.GetDeviceCaps(win32con.LOGPIXELSY)
            CM_TO_IN = 0.3937007874

            # QR-Code-Größe hier anpassen (cm in Pixel)
            qr_side_px = int(2.5 * CM_TO_IN * min(dpi_x, dpi_y))
            qr_print = self.qr_pil.resize((qr_side_px, qr_side_px), Image.NEAREST)

            final_img = Image.new("RGB", (qr_side_px, qr_side_px), "white")
            final_img.paste(qr_print, (0, 0))

            dib = ImageWin.Dib(final_img)
            dib.draw(hdc.GetHandleOutput(), (0, 0, qr_side_px, qr_side_px))

            hdc.EndPage()
            hdc.EndDoc()
            hdc.DeleteDC()
        except Exception as e:
            messagebox.showerror("Druckfehler", str(e))

    def reset_favorites(self):
        global usage_data
        usage_data = {}
        save_usage(usage_data)
        self.update_dropdown()
        messagebox.showinfo("Info", "Favoriten wurden zurückgesetzt.")

if __name__ == "__main__":
    fall_arg = None
    args = sys.argv[1:]
    for i, a in enumerate(args):
        s = a.strip()
        low = s.lower()
        if low.startswith("fall="):
            fall_arg = s.split("=", 1)[1]
            break
        if low in ("--fall", "/fall", "-fall"):
            if i + 1 < len(args):
                fall_arg = args[i + 1]
            break

    root = tk.Tk()
    app = KDLQRApp(root, fallnummer_param=fall_arg)
    root.mainloop()
