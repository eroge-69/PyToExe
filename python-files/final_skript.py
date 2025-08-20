import pandas as pd
import glob
import os
import zipfile

def is_valid_parquet(filepath):
    """Zkontroluje magic bytes PAR1 na začátku a na konci."""
    with open(filepath, "rb") as f:
        start = f.read(4)
        f.seek(-4, os.SEEK_END)
        end = f.read(4)
    return start == b"PAR1" and end == b"PAR1"

def is_zip_file(filepath):
    """Zkontroluje, zda soubor začíná PK.. (ZIP)."""
    with open(filepath, "rb") as f:
        start = f.read(4)
    return start.startswith(b"PK")

def convert_parquet_to_csv(parquet_path):
    """Načte Parquet a uloží jako CSV."""
    try:
        df = pd.read_parquet(parquet_path)
        csv_file = os.path.splitext(parquet_path)[0] + ".csv"
        df.to_csv(csv_file, index=False)
        print(f"✅ Převedeno: {os.path.basename(parquet_path)} -> {os.path.basename(csv_file)}")
    except Exception as e:
        print(f"❌ Chyba při čtení {parquet_path}: {e}")

def process_zip(zip_path):
    """Rozbalí ZIP a zpracuje všechny Parquet soubory uvnitř."""
    extract_dir = os.path.splitext(zip_path)[0]
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"📦 Rozbaleno: {os.path.basename(zip_path)} -> {extract_dir}")

    # projdi všechny soubory uvnitř rozbaleného archivu
    for root, _, files in os.walk(extract_dir):
        for f in files:
            if f.lower().endswith(".parquet"):
                full_path = os.path.join(root, f)
                if is_valid_parquet(full_path):
                    convert_parquet_to_csv(full_path)
                else:
                    print(f"⚠️ {f} uvnitř ZIPu není validní Parquet")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    for file in glob.glob(os.path.join(script_dir, "*")):
        if os.path.isdir(file):
            continue

        if file.lower().endswith(".parquet"):
            if is_valid_parquet(file):
                convert_parquet_to_csv(file)
            elif is_zip_file(file):
                process_zip(file)
            else:
                print(f"❌ {os.path.basename(file)} není validní Parquet ani ZIP")
        elif file.lower().endswith(".zip"):
            process_zip(file)
        else:
            # ignoruj jiné soubory
            pass

if __name__ == "__main__":
    main()
