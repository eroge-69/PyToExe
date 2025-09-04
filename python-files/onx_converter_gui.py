import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import re, requests
from io import BytesIO
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage

# --- Arabic to Latin translit map ---
AR2LATIN = {
    "ا":"a","أ":"a","إ":"i","آ":"a","ى":"a","ئ":"e","ؤ":"o","ء":"",
    "ب":"b","ت":"t","ث":"th","ج":"j","ح":"h","خ":"kh",
    "د":"d","ذ":"dh","ر":"r","ز":"z","س":"s","ش":"sh",
    "ص":"s","ض":"d","ط":"t","ظ":"z","ع":"a","غ":"gh",
    "ف":"f","ق":"q","ك":"k","گ":"g","چ":"ch","ل":"l","م":"m","ن":"n",
    "ه":"h","ة":"a","و":"w","ي":"y","ﻻ":"la","لا":"la","ٱ":"a",
    "َ":"","ً":"","ُ":"","ٌ":"","ِ":"","ٍ":"","ْ":"","ّ":""
}

def transliterate_mixed(s: str) -> str:
    if not isinstance(s,str) or not s.strip():
        return ""
    out = []
    for ch in s:
        if ch in AR2LATIN:
            out.append(AR2LATIN[ch])
        else:
            out.append(ch)
    return "".join(out).upper()

def fix_image_path(p: str) -> str:
    if not isinstance(p,str) or not p.strip():
        return ""
    p = p.replace("/home/u239199524/domains/","")
    p = p.replace("public_html/","")
    if not p.startswith("http"):
        p = "https://" + p
    return p

def process_csv(input_path, output_path):
    df = pd.read_csv(input_path, dtype=str)

    # Fix product image
    if "Embedded Product Image" in df.columns:
        df["PRODUCT IMAGE"] = df["Embedded Product Image"].apply(fix_image_path)
        df.drop(columns=["Embedded Product Image"], inplace=True)

    # Rename
    rename_map = {}
    for c in df.columns:
        if c == "مقاس العبايه":
            rename_map[c] = "SIZE"
        elif c in ["أزرار العبايه (طقطق)", "الأزرار", "أزرار"]:
            rename_map[c] = "TAKTAK"
        elif c == "ملاحظات أو مقاسات أخرى":
            rename_map[c] = "NOTES"
        elif c in ["Full Name (Billing)", "الاسم (الفاتورة)", "اسم (الفاتورة)"]:
            rename_map[c] = "Full Name (Billing)"
        elif c in ["تاريخ الطلب", "Order date", "Order Date"]:
            rename_map[c] = "Order Date"
    df = df.rename(columns=rename_map)

    # TAKTAK
    if "TAKTAK" in df.columns:
        df["TAKTAK"] = df["TAKTAK"].fillna("").astype(str).str.strip().replace({
            "مع أزرار":"TAKTAK","بدون أزرار":"NO"
        })

    # ALAGI
    addon_cols = [c for c in df.columns if str(c).startswith("اضافة فستان")]
    df["ALAGI"] = df.apply(lambda r: "ALAGI" if any(isinstance(r.get(c),str) and "مع فستان" in r.get(c,"") for c in addon_cols) else "", axis=1)
    df = df[[c for c in df.columns if not str(c).startswith("اضافة فستان")]]

    # NOTES
    notes_col = "NOTES" if "NOTES" in df.columns else None
    cust_col = "Customer Note" if "Customer Note" in df.columns else None
    merged=[]
    for i in range(len(df)):
        note_val = str(df.at[i,notes_col]) if notes_col and pd.notna(df.at[i,notes_col]) else ""
        cust_val = str(df.at[i,cust_col]) if cust_col and pd.notna(df.at[i,cust_col]) else ""
        merged.append("CALL MAMA" if note_val.strip() or cust_val.strip() else "")
    df["NOTES"]=merged
    if cust_col and cust_col in df.columns: df.drop(columns=[cust_col], inplace=True)

    # Names
    if "Full Name (Billing)" in df.columns:
        df["Full Name (Billing)"] = df["Full Name (Billing)"].apply(transliterate_mixed)

    # Column order
    ordered = ["PRODUCT IMAGE","Product Name","SIZE","TAKTAK","NOTES","ALAGI","Order Date","Order Number","Full Name (Billing)"]
    ordered = [c for c in ordered if c in df.columns]
    df_out = df[ordered].copy()

    # Create Excel
    wb = Workbook()
    ws = wb.active
    ws.append(df_out.columns.tolist())

    for i,row in df_out.iterrows():
        ws.append(row.tolist())
        img_url = row.get("PRODUCT IMAGE","")
        if img_url:
            try:
                r = requests.get(img_url, timeout=10)
                if r.status_code == 200:
                    img_bytes = BytesIO(r.content)
                    img = XLImage(img_bytes)
                    img.width, img.height = 80,80
                    ws.add_image(img, f"A{i+2}")
            except:
                pass

    wb.save(output_path)

# --- Tkinter GUI ---
def run_gui():
    root = tk.Tk()
    root.title("ONX CSV → XLSX Converter")

    def select_file():
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
        if file_path:
            save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files","*.xlsx")])
            if save_path:
                try:
                    process_csv(file_path, save_path)
                    messagebox.showinfo("Success", f"File converted and saved:\n{save_path}")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    btn = tk.Button(root, text="Select CSV to Convert", command=select_file, font=("Arial",14))
    btn.pack(padx=20, pady=40)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
