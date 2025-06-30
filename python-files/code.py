import customtkinter as ctk
import tkinter.filedialog as fd
from tkinter import messagebox
from PIL import Image
import fitz
import pandas as pd
import os
import re
from datetime import datetime

# === Configuration ===
CFAN_RED = "#D71920"
CFAN_GRAY = "#666666"
BACKGROUND = "#f4f4f4"

serial_pattern = r"\b\d{8}-\d{3}-\d{4}\b"
date_pattern = r"\b0?\d{1,2}/0?\d{1,2}/\d{4}\b"
rot_pattern = r"\b\d{1,4}(?:\.\d{1,2})?\b"
header_keywords = {"PART", "REV", "QTY", "PO", "DESCRIPTION", "DOM", "EXPIRATION"}

def normalize_serial(serial):
    parts = re.findall(r"\d+", str(serial))
    return "".join(parts).lstrip("0") if len(parts) == 3 else ""

def normalize_erp_lot(lot):
    try:
        val = float(lot)
        int_part = int(val)
        decimal_part = int(round((val - int_part) * 1000))
        if decimal_part == 0:
            return None
        return f"{int_part:08d}{decimal_part:04d}"
    except:
        return None

def extract_structured_data(pdf_path):
    doc = fitz.open(pdf_path)
    results = []
    current_group = []

    for page_num in range(1, len(doc)):
        lines = doc[page_num].get_text("text").splitlines()
        for line in lines:
            line = line.strip()
            if not line or any(h in line.upper() for h in header_keywords):
                continue
            if re.search(serial_pattern, line):
                if current_group:
                    result = process_group(current_group)
                    if result:
                        results.append(result)
                current_group = [line]
            else:
                current_group.append(line)
    if current_group:
        result = process_group(current_group)
        if result:
            results.append(result)
    return results

def process_group(group):
    group_text = " ".join(group)
    serial_match = re.search(serial_pattern, group_text)
    date_matches = re.findall(date_pattern, group_text)
    rot_match = re.findall(rot_pattern, group_text)

    rot_valid = None
    for r in rot_match:
        try:
            val = float(r)
            if 50 < val < 720:
                rot_valid = r
                break
        except:
            continue

    valid_dates = []
    for d in date_matches:
        try:
            dt = datetime.strptime(d, "%m/%d/%Y")
            if dt > datetime.today():
                valid_dates.append(dt)
        except:
            continue

    if serial_match and valid_dates and rot_valid:
        closest_exp = min(valid_dates)
        return {
            "Serial No.": serial_match.group(),
            "Expiration Date": closest_exp.strftime("%m/%d/%Y"),
            "Remaining Out Time": rot_valid
        }
    return None

# Interface helpers
def browse_pdf():
    path = fd.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if path:
        pdf_path_var.set(path)

def browse_folder():
    path = fd.askdirectory()
    if path:
        output_path_var.set(path)

def browse_excel():
    path = fd.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if path:
        erp_path_var.set(path)

def update_clock():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clock_label.configure(text=now)
    app.after(1000, update_clock)

# Main logic
def convert_to_excel():
    pdf_path = pdf_path_var.get()
    output_folder = output_path_var.get()
    receiving_start = receiving_var.get().strip()
    erp_path = erp_path_var.get()

    if not pdf_path or not output_folder or not receiving_start:
        messagebox.showwarning("Missing Input", "Please fill in the required fields.")
        return

    try:
        receiving_start = int(receiving_start)
    except ValueError:
        messagebox.showerror("Invalid Input", "Receiving number must be an integer.")
        return

    try:
        data = extract_structured_data(pdf_path)
        if not data:
            messagebox.showinfo("No Data", "No structured data found in the PDF.")
            return

        df = pd.DataFrame(data)
        df["Remaining Out Time"] = df["Remaining Out Time"].astype(float)
        df["Actual Out Time"] = df["Remaining Out Time"].apply(lambda x: round(720 - x, 2))
        df["Initial Out Time"] = df["Actual Out Time"]

        receiving_numbers = list(range(receiving_start, receiving_start + len(df)))
        df.insert(0, "Receiving Number", receiving_numbers)

        df = df[[
            "Receiving Number",
            "Serial No.",
            "Expiration Date",
            "Actual Out Time",
            "Initial Out Time",
            "Remaining Out Time"
        ]]

        receiving_end = receiving_numbers[-1]
        base_filename = f"{receiving_start}-{receiving_end}"
        raw_filename = os.path.join(output_folder, f"{base_filename}-rawextracted.xlsx")
        df.to_excel(raw_filename, index=False)

        final_filename = None
        if erp_path:
            try:
                erp_df = pd.read_excel(erp_path)

                df["__match_key__"] = df["Serial No."].apply(normalize_serial)
                erp_df["__match_key__"] = erp_df["Mfg.  Lot"].apply(normalize_erp_lot)

                merged = pd.merge(
                    erp_df,
                    df[["__match_key__", "Expiration Date", "Remaining Out Time", "Actual Out Time", "Initial Out Time"]],
                    how="left",
                    on="__match_key__"
                ).drop(columns=["__match_key__"])

                final_filename = os.path.join(output_folder, f"{base_filename}.xlsx")
                merged.to_excel(final_filename, index=False)

                os.startfile(final_filename)  # ✅ Ouverture automatique du fichier fusionné

            except Exception as e:
                messagebox.showerror("ERP Merge Error", f"Could not merge with Cloudsuite file:\n{str(e)}")

        message = f"Raw extraction file saved:\n{raw_filename}"
        if final_filename:
            message += f"\nMerged Cloudsuite file opened:\n{final_filename}"

        messagebox.showinfo("Success", message)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# === GUI Setup ===
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("CFAN PDF to Excel Extractor + Smart Cloudsuite Merge")
app.geometry("720x620")
app.resizable(False, False)
app.configure(fg_color=BACKGROUND)

pdf_path_var = ctk.StringVar()
output_path_var = ctk.StringVar()
receiving_var = ctk.StringVar()
erp_path_var = ctk.StringVar()

top_frame = ctk.CTkFrame(app, fg_color=BACKGROUND)
top_frame.pack(fill="x", padx=20, pady=(10, 5))

try:
    logo = ctk.CTkImage(Image.open("Asset-1@2x.png"), size=(100, 50))
    ctk.CTkLabel(top_frame, image=logo, text="").pack(side="left", padx=10)
except:
    ctk.CTkLabel(top_frame, text="[CFAN Logo]", font=("Segoe UI", 12, "bold"), text_color=CFAN_GRAY).pack(side="left", padx=10)

clock_label = ctk.CTkLabel(top_frame, text="", font=("Segoe UI", 11), text_color=CFAN_GRAY)
clock_label.pack(side="right", padx=10)
update_clock()

main_frame = ctk.CTkFrame(app, fg_color=BACKGROUND)
main_frame.pack(fill="both", expand=True, padx=30, pady=10)

ctk.CTkLabel(main_frame, text="PDF Certificate of Compliance:", anchor="w", font=("Segoe UI", 11)).pack(fill="x")
ctk.CTkEntry(main_frame, textvariable=pdf_path_var, placeholder_text="Select a PDF file").pack(fill="x", pady=5)
ctk.CTkButton(main_frame, text="Browse PDF", command=browse_pdf, fg_color=CFAN_RED).pack(pady=5)

ctk.CTkLabel(main_frame, text="Output Folder:", anchor="w", font=("Segoe UI", 11)).pack(fill="x", pady=(10, 0))
ctk.CTkEntry(main_frame, textvariable=output_path_var, placeholder_text="Choose output folder").pack(fill="x", pady=5)
ctk.CTkButton(main_frame, text="Select Folder", command=browse_folder, fg_color=CFAN_RED).pack(pady=5)

ctk.CTkLabel(main_frame, text="Cloudsuite Excel File (optional):", anchor="w", font=("Segoe UI", 11)).pack(fill="x", pady=(10, 0))
ctk.CTkEntry(main_frame, textvariable=erp_path_var, placeholder_text="Select Cloudsuite .xlsx file").pack(fill="x", pady=5)
ctk.CTkButton(main_frame, text="Browse Cloudsuite Excel", command=browse_excel, fg_color=CFAN_RED).pack(pady=5)

ctk.CTkLabel(main_frame, text="Starting Receiving Number (e.g. 47001):", anchor="w", font=("Segoe UI", 11)).pack(fill="x", pady=(10, 0))
ctk.CTkEntry(main_frame, textvariable=receiving_var, placeholder_text="47001").pack(fill="x", pady=5)

ctk.CTkButton(main_frame, text="🚀 Extract + (Optional) Merge",
              command=convert_to_excel,
              fg_color=CFAN_RED, hover_color="#b8141a",
              font=("Segoe UI", 13, "bold"), height=40).pack(pady=25)

ctk.CTkLabel(app, text="For assistance, contact: ugo.wassermann@c-fan.com",
             font=("Segoe UI", 10, "italic"), text_color=CFAN_GRAY).pack(pady=10)

app.mainloop()