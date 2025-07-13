import os
import re
import shutil
import fitz  # PyMuPDF
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta


# === Configuration === #
SCRIPT_DIR = Path(__file__).resolve().parent
PDF_FOLDER = SCRIPT_DIR / "PDF_Process"
OUTPUT_FOLDER = PDF_FOLDER / "Excel_Outputs"
BACKUP_FOLDER = SCRIPT_DIR / "BackUp"
RETENTION_DAYS = 15


# === Setup Directories === #
def setup_directories():
    PDF_FOLDER.mkdir(parents=True, exist_ok=True)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)


# === Cleanup Old Files === #
def delete_old_files(folder: Path, retention_days: int):
    cutoff_time = datetime.now() - timedelta(days=retention_days)
    for file in folder.glob("*"):
        if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_time:
            file.unlink()
            print(f"🗑️ Deleted old file: {file.name}")


# === Extract SKU Info from Lines === #
def extract_sku_rows(lines, page_num):
    products = []
    for line in lines:
        line = line.strip()
        match = re.match(r"^(\d+)\s+(\d+)\s+QTY\s*-\s*(.*?)\s*\|\s*(.+)", line, re.IGNORECASE)
        if match:
            products.append({
                "Page": page_num + 1,
                "ID": match.group(1),
                "SKU ID": match.group(3).strip(),
                "Description": match.group(4).strip(),
                "Qty": match.group(2)
            })
            print(f"✔️ Page {page_num + 1}: ID={match.group(1)}, SKU={match.group(3)}, Qty={match.group(2)}")
        else:
            fallback = re.match(r"^(\d+)\s+(.*?)\s*\|\s*(.+)", line)
            if fallback:
                products.append({
                    "Page": page_num + 1,
                    "ID": fallback.group(1),
                    "SKU ID": fallback.group(2).strip(),
                    "Description": fallback.group(3).strip(),
                    "Qty": "1"
                })
                print(f"➕ Fallback match Page {page_num + 1}: ID={fallback.group(1)}, SKU={fallback.group(2)}")
    return products


# === Process a Single PDF === #
def process_single_pdf(pdf_path: Path) -> Path | None:
    print(f"\n📖 Reading '{pdf_path.name}'")
    doc = fitz.open(pdf_path)
    all_products = []

    for page_num, page in enumerate(doc):
        lines = page.get_text().splitlines()
        all_products.extend(extract_sku_rows(lines, page_num))

    if all_products:
        df = pd.DataFrame(all_products)
        output_path = OUTPUT_FOLDER / f"{pdf_path.stem}_extracted.csv"
        df.to_csv(output_path, index=False)
        print(f"✅ Extracted to: {output_path}")
        return output_path
    else:
        print(f"⚠️ No valid SKU rows found in {pdf_path.name}")
        return None


# === Group and Export Summary === #
def group_by_sku(csv_paths: list[Path]):
    if not csv_paths:
        print("⚠️ No CSVs to group.")
        return

    all_dfs = []
    for csv_file in csv_paths:
        df = pd.read_csv(csv_file)
        df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce").fillna(0).astype(int)
        all_dfs.append(df)

    combined_df = pd.concat(all_dfs, ignore_index=True)
    grouped_df = (
        combined_df.groupby("SKU ID", as_index=False)["Qty"]
        .sum()
        .rename(columns={"Qty": "Total Qty"})
        .sort_values(by="Total Qty", ascending=False)
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = OUTPUT_FOLDER / f"grouped_sku_summary_{timestamp}.xlsx"
    grouped_df.to_excel(summary_path, index=False)
    print(f"\n📊 Grouped summary saved to: {summary_path}")


# === Backup and Retention Management === #
def backup_csv_files():
    for csv_file in OUTPUT_FOLDER.glob("*.csv"):
        destination = BACKUP_FOLDER / csv_file.name
        shutil.move(str(csv_file), str(destination))
        print(f"📁 Backed up: {csv_file.name} ➝ {destination}")


# === Main Routine === #
def main():
    setup_directories()
    delete_old_files(OUTPUT_FOLDER, RETENTION_DAYS)









    