import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# -----------------------
# Helper: bersihkan angka jadi float
# -----------------------
def clean_currency(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float, np.integer, np.floating)):
        return float(x)
    s = str(x).strip()
    s = s.replace('Rp', '').replace('IDR', '').replace(' ', '')
    s_clean = s.replace('.', '').replace(',', '')
    try:
        return float(s_clean)
    except:
        try:
            return float(s)
        except:
            return np.nan

# -----------------------
# Mapping produk <-> premi
# -----------------------
product_map = {4500: "Ekonomi", 7500: "Bisnis", 12500: "Eksekutif"}
order_map = {"Ekonomi": 1, "Bisnis": 2, "Eksekutif": 3}

def map_product_by_value(v):
    if pd.isna(v):
        return None
    try:
        key = int(round(float(v)))
    except:
        return None
    return product_map.get(key)

# -----------------------
# Proses utama
# -----------------------
def process_files(kai_file, ppm_file, status_label):
    try:
        status_label.config(text="⏳ Sedang memproses...", fg="blue")
        status_label.update_idletasks()

        kai = pd.read_excel(kai_file, sheet_name="Sheet1")
        ppm = pd.read_excel(ppm_file, sheet_name="Sheet1")

        # Preprocessing
        kai_clean = kai.drop_duplicates(subset=["polis_number"])
        ppm_clean = ppm.drop_duplicates(subset=["insurance_polis"])

        if "source_file" in kai_clean.columns:
            kai_clean["source_file"] = kai_clean["source_file"].astype(str).str.replace(".xlsx", "", regex=False).str.strip()
        if "source_file" in ppm_clean.columns:
            ppm_clean["source_file"] = (
                ppm_clean["source_file"].astype(str)
                .str.replace("2025.xlsx", "", regex=False)
                .str.replace(".xlsx", "", regex=False)
                .str.strip()
            )

        merged = kai_clean.merge(
            ppm_clean,
            left_on="polis_number",
            right_on="insurance_polis",
            how="inner",
            suffixes=("_kai", "_ppm")
        )

        if "source_file_kai" in merged.columns and "source_file_ppm" in merged.columns:
            merged = merged[merged["source_file_kai"] == merged["source_file_ppm"]]

        # Ambil kolom yang dibutuhkan
        cols_needed = [
            "polis_number",
            "city_origin",
            "city_destination",
            "product",
            "premi",
            "policy_status",
            "fee/mdr_rate",
            "amount",
            "fee/mdr_pg",
            "premi_asuransi",
            "komisi_asuransi",
            "komisi_kai",
            "source_file_kai"
        ]
        cols_present = [c for c in cols_needed if c in merged.columns]
        match = merged[cols_present].copy().rename(columns={"source_file_kai": "source_file"})

        # Normalisasi angka
        match["policy_status_norm"] = match["policy_status"].astype(str).str.lower().str.strip()
        match["premi_num"] = match["premi"].apply(clean_currency)
        match["amount_num"] = match["amount"].apply(clean_currency)

        # Mapping product lama
        match["product_old"] = match["premi_num"].apply(map_product_by_value)

        # Logika reschedule
        def calc_premi_plus(row):
            if row["policy_status_norm"] == "reschedule":
                if row["premi_num"] == row["amount_num"]:
                    return row["amount_num"]
                else:
                    return row["premi_num"] + row["amount_num"]
            else:
                return row["amount_num"]

        match["premi_plus_amount"] = match.apply(calc_premi_plus, axis=1)

        def calc_product_new(row):
            if row["policy_status_norm"] == "reschedule":
                if row["premi_num"] == row["amount_num"]:
                    return row["product_old"]
                else:
                    return map_product_by_value(row["premi_plus_amount"])
            return row["product_old"]

        match["product_new"] = match.apply(calc_product_new, axis=1)

        def transition(old, new):
            if old == new:
                return old
            return f"{old} → {new}"

        match["product_transition"] = match.apply(lambda r: transition(r["product_old"], r["product_new"]), axis=1)

        def is_upgrade(old, new):
            if pd.isna(old) or pd.isna(new):
                return False
            return order_map.get(new, 0) > order_map.get(old, 0)

        match["is_upgrade"] = match.apply(lambda r: is_upgrade(r["product_old"], r["product_new"]), axis=1)

        # Data unmatch
        unmatch_ppm = ppm_clean[~ppm_clean["insurance_polis"].isin(kai_clean["polis_number"])]
        unmatch_kai = kai_clean[~kai_clean["polis_number"].isin(ppm_clean["insurance_polis"])]

        # Duplicates check
        dup_kai = kai[kai.duplicated(subset=["polis_number", "source_file"], keep=False)].copy()
        dup_kai["source"] = "KAI"
        dup_kai["duplicate_count"] = dup_kai.groupby(["polis_number", "source_file"])["polis_number"].transform("count")

        dup_ppm = ppm[ppm.duplicated(subset=["insurance_polis", "source_file"], keep=False)].copy()
        dup_ppm["source"] = "PPM"
        dup_ppm["duplicate_count"] = dup_ppm.groupby(["insurance_polis", "source_file"])["insurance_polis"].transform("count")

        duplicates_check = pd.concat([dup_kai, dup_ppm], ignore_index=True)

        # Save output
        output_file = "Output_Merged.xlsx"
        with pd.ExcelWriter(output_file) as writer:
            match.to_excel(writer, sheet_name="Match", index=False)
            unmatch_ppm.to_excel(writer, sheet_name="Unmatch_PPM", index=False)
            unmatch_kai.to_excel(writer, sheet_name="Unmatch_KAI", index=False)
            duplicates_check.to_excel(writer, sheet_name="Duplicates_Check", index=False)

        status_label.config(text=f"✅ Selesai! Hasil: {os.path.abspath(output_file)}", fg="green")

    except Exception as e:
        status_label.config(text=f"❌ Error: {str(e)}", fg="red")

# -----------------------
# GUI
# -----------------------
def run_gui():
    root = tk.Tk()
    root.title("KAI - PPM Matcher")

    # Path variables
    kai_path = tk.StringVar()
    ppm_path = tk.StringVar()

    # Browse buttons
    def browse_kai():
        file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file:
            kai_path.set(file)

    def browse_ppm():
        file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file:
            ppm_path.set(file)

    # Labels & buttons
    tk.Label(root, text="File KAI:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    tk.Entry(root, textvariable=kai_path, width=50).grid(row=0, column=1, padx=5)
    tk.Button(root, text="Browse", command=browse_kai).grid(row=0, column=2, padx=5)

    tk.Label(root, text="File PPM:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    tk.Entry(root, textvariable=ppm_path, width=50).grid(row=1, column=1, padx=5)
    tk.Button(root, text="Browse", command=browse_ppm).grid(row=1, column=2, padx=5)

    status_label = tk.Label(root, text="⚡ Ready", fg="black")
    status_label.grid(row=3, column=0, columnspan=3, pady=10)

    def run_process():
        if not kai_path.get() or not ppm_path.get():
            messagebox.showerror("Error", "Pilih file KAI dan PPM terlebih dahulu")
            return
        process_files(kai_path.get(), ppm_path.get(), status_label)

    tk.Button(root, text="Process", command=run_process, bg="green", fg="white").grid(row=2, column=1, pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
