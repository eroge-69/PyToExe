import sys

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from tkinter.font import Font
except ModuleNotFoundError:
    print("\n[ERROR] tkinter module not found. Please ensure it is installed and available in your Python environment.")
    print("Tip: Use a full desktop Python environment with GUI support.")
else:
    import csv
    import sqlite3
    import qrcode
    import datetime
    import os
    import platform
    import subprocess
    from PyPDF2 import PdfMerger

    try:
        from fpdf import FPDF
    except ModuleNotFoundError:
        print("\n[ERROR] fpdf module not found. PDF generation will be disabled.")
        FPDF = None

    class MASDevlopApp(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("MAS Devlop Software")
            self.geometry("1200x800")
            self.configure(bg="#f2f2f2")

            self.conn = sqlite3.connect("mas_bills.db")
            self.cursor = self.conn.cursor()
            self.create_table()
            self.create_widgets()

        def create_table(self):
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    address TEXT,
                    ptn_no TEXT,
                    usage TEXT,
                    builtup REAL,
                    alv REAL,
                    rv REAL,
                    total_tax REAL,
                    bill_no TEXT,
                    date TEXT,
                    modification_type TEXT,
                    modification_note TEXT,
                    old_name TEXT,
                    new_name TEXT
                )
            """)
            self.conn.commit()

        def show_module(self, title):
            win = tk.Toplevel(self)
            win.title(title)
            win.geometry("600x600")

            form_frame = ttk.Frame(win)
            form_frame.pack(pady=20)

            field_config = {
                "New Registration": [
                    ("नाव", "name"),
                    ("पत्ता", "address"),
                    ("PTN क्रमांक", "ptn"),
                    ("वापराचा प्रकार", "usage"),
                    ("बांधकाम क्षेत्र (चौ. फूट)", "builtup"),
                    ("ALV", "alv"),
                    ("RV", "rv")
                ],
                "Edit Property": [
                    ("सध्याचे नाव", "old_name"),
                    ("नवीन नाव", "new_name"),
                    ("नवीन पत्ता", "address"),
                    ("नवीन वापर प्रकार", "usage")
                ],
                "Create Supp Bill": [
                    ("PTN क्रमांक", "ptn"),
                    ("पूरक कारण", "modification_note"),
                    ("RV", "rv")
                ],
                "Heir Transfer": [
                    ("मूळ मालकाचे नाव", "old_name"),
                    ("वारसाचे नाव", "new_name"),
                    ("PTN क्रमांक", "ptn")
                ]
            }

            fields = field_config.get(title, [("PTN क्रमांक", "ptn")])
            module_entries = {}
            for i, (label_text, key) in enumerate(fields):
                ttk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky="e", padx=5, pady=5)
                entry = ttk.Entry(form_frame, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5)
                module_entries[key] = entry

            def save_module_data():
                data = {k: v.get() for k, v in module_entries.items()}
                date = datetime.datetime.today().strftime("%Y-%m-%d")
                bill_no = f"MAS-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                rv = float(data.get("rv", 0)) if "rv" in data else 0
                total_tax = round(rv * 0.2, 2)

                self.cursor.execute("""
                    INSERT INTO bills (name, address, ptn_no, usage, builtup, alv, rv, total_tax, bill_no, date, modification_type, modification_note, old_name, new_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data.get('name'), data.get('address'), data.get('ptn'), data.get('usage'),
                    float(data.get('builtup', 0)) if 'builtup' in data else None,
                    float(data.get('alv', 0)) if 'alv' in data else None,
                    rv, total_tax, bill_no, date, title, data.get('modification_note'),
                    data.get('old_name'), data.get('new_name')
                ))
                self.conn.commit()

                qr_data = f"""Pay ₹{total_tax} for PTN {data.get('ptn')} to Solapur MahanagarPalika\nAccount No: 123456789012\nIFSC: SBIN0000001"""
                qr_img = qrcode.make(qr_data)
                qr_path = os.path.join(os.getcwd(), f"{bill_no}_qr.png")
                qr_img.save(qr_path)

                if FPDF:
                    pdf = FPDF()
                    pdf.add_page()
                    if os.path.exists("solapur_logo.png"):
                        pdf.image("solapur_logo.png", x=10, y=8, w=25)
                    pdf.set_font("Arial", size=14)
                    pdf.cell(200, 10, txt="सोलापूर महानगरपालिका, सोलापूर", ln=True, align='C')
                    pdf.set_font("Arial", size=12)
                    pdf.ln(5)
                    for key, value in data.items():
                        if value:
                            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
                    pdf.cell(200, 10, txt=f"कर (RV × 20%): ₹{total_tax}", ln=True)
                    pdf.image(qr_path, x=160, y=pdf.get_y()+10, w=30)
                    if os.path.exists("signature.png"):
                        pdf.image("signature.png", x=20, y=pdf.get_y()+20, w=40)
                    if os.path.exists("seal.png"):
                        pdf.image("seal.png", x=160, y=pdf.get_y()+20, w=30)
                    output_path = os.path.join(os.getcwd(), f"{bill_no}.pdf")
                    pdf.output(output_path)

                messagebox.showinfo("यश", f"{title} नोंदणी यशस्वी!\nबिल क्रमांक: {bill_no}\nPDF तयार: {bill_no}.pdf")
                win.destroy()

            ttk.Button(win, text="साठवा", command=save_module_data).pack(pady=10)
            ttk.Button(win, text="Close", command=win.destroy).pack(pady=5)

        def create_widgets(self):
            header_font = Font(family="Arial", size=16, weight="bold")
            self.header = tk.Label(self, text="सोलापूर महानगरपालिका, सोलापूर\nMAS Devlop - मालमत्ता मूल्यांकन व कर बिल", font=header_font, bg="#f2f2f2")
            self.header.pack(pady=10)

            nav_frame = ttk.LabelFrame(self, text="मेनू पर्याय")
            nav_frame.pack(padx=10, pady=10, fill="x")

            menu_buttons = [
                ("New Registration", lambda: self.show_module("New Registration")),
                ("Edit Property", lambda: self.show_module("Edit Property")),
                ("Create Supp Bill", lambda: self.show_module("Create Supp Bill")),
                ("Add Measurement", lambda: self.show_module("Add Measurement")),
                ("Heir Transfer", lambda: self.show_module("Heir Transfer")),
                ("General Rebate", lambda: self.show_module("General Rebate")),
                ("Other Supp Bill", lambda: self.show_module("Other Supp Bill")),
                ("Edit Supp Bill", lambda: self.show_module("Edit Supp Bill"))
            ]

            for idx, (text, cmd) in enumerate(menu_buttons):
                ttk.Button(nav_frame, text=text, command=cmd).grid(row=0, column=idx, padx=5, pady=5)

    if __name__ == "__main__":
        try:
            app = MASDevlopApp()
            app.mainloop()
        except NameError:
            print("MASDevlopApp class is not defined. Please ensure the class is implemented correctly.")
