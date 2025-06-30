import os
import shutil
import tempfile
import zipfile
import rarfile
import tkinter as tk
from tkinter import filedialog, messagebox

def is_stream_file(filename):
    return filename.endswith((".yft", ".ytd"))

def is_meta_file(filename):
    return filename.endswith(".meta")

def generate_fxmanifest(car_name, output_path):
    manifest = f"""fx_version 'cerulean'
game 'gta5'

files {{
    'data/**/*.meta'
}}

data_file 'VEHICLE_METADATA_FILE' 'data/vehicles.meta'
data_file 'VEHICLE_VARIATION_FILE' 'data/carvariations.meta'
data_file 'HANDLING_FILE' 'data/handling.meta'
data_file 'CARCOLS_FILE' 'data/carcols.meta'
data_file 'VEHICLE_LAYOUTS_FILE' 'data/vehiclelayouts.meta'
"""
    with open(os.path.join(output_path, 'fxmanifest.lua'), 'w') as f:
        f.write(manifest)

def process_car_folder(car_folder, output_base, car_name_override=None):
    car_name = car_name_override or os.path.basename(car_folder)
    output_path = os.path.join(output_base, car_name)
    stream_path = os.path.join(output_path, 'stream')
    data_path = os.path.join(output_path, 'data')

    os.makedirs(stream_path, exist_ok=True)
    os.makedirs(data_path, exist_ok=True)

    for root, dirs, files in os.walk(car_folder):
        for file in files:
            src_file = os.path.join(root, file)
            if is_stream_file(file):
                shutil.copy2(src_file, stream_path)
            elif is_meta_file(file):
                shutil.copy2(src_file, data_path)

    generate_fxmanifest(car_name, output_path)

def extract_archive(archive_path, temp_dir):
    extracted_path = os.path.join(temp_dir, os.path.splitext(os.path.basename(archive_path))[0])
    os.makedirs(extracted_path, exist_ok=True)
    try:
        if archive_path.lower().endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(extracted_path)
        elif archive_path.lower().endswith('.rar'):
            with rarfile.RarFile(archive_path) as rf:
                rf.extractall(extracted_path)
        else:
            return None
        return extracted_path
    except Exception as e:
        messagebox.showerror("Extraction Error", f"Failed to extract {archive_path}: {e}")
        return None

def start_conversion(input_dir, output_dir):
    if not input_dir or not output_dir:
        messagebox.showerror("Error", "Please select both input and output directories.")
        return

    temp_dir = tempfile.mkdtemp()
    processed_count = 0

    for item in os.listdir(input_dir):
        item_path = os.path.join(input_dir, item)
        if os.path.isdir(item_path):
            process_car_folder(item_path, output_dir)
            processed_count += 1
        elif item.lower().endswith(('.zip', '.rar')):
            extracted = extract_archive(item_path, temp_dir)
            if extracted:
                process_car_folder(extracted, output_dir, car_name_override=os.path.splitext(item)[0])
                processed_count += 1

    shutil.rmtree(temp_dir)
    messagebox.showinfo("Done", f"Processed {processed_count} car(s) successfully!")

def browse_input(entry_input):
    path = filedialog.askdirectory(title="Select folder containing car folders or archives")
    if path:
        entry_input.delete(0, tk.END)
        entry_input.insert(0, path)

def browse_output(entry_output):
    path = filedialog.askdirectory(title="Select output folder for FiveM cars")
    if path:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, path)

def main():
    root = tk.Tk()
    root.title("GTA V Addon Car -> FiveM Converter")
    root.geometry("500x220")

    tk.Label(root, text="Cars directory (folders or archives):").pack(pady=5)
    frame_input = tk.Frame(root)
    entry_input = tk.Entry(frame_input, width=50)
    entry_input.pack(side=tk.LEFT, padx=5)
    btn_input = tk.Button(frame_input, text="Browse", command=lambda: browse_input(entry_input))
    btn_input.pack(side=tk.LEFT)
    frame_input.pack()

    tk.Label(root, text="Output directory:").pack(pady=5)
    frame_output = tk.Frame(root)
    entry_output = tk.Entry(frame_output, width=50)
    entry_output.pack(side=tk.LEFT, padx=5)
    btn_output = tk.Button(frame_output, text="Browse", command=lambda: browse_output(entry_output))
    btn_output.pack(side=tk.LEFT)
    frame_output.pack()

    btn_start = tk.Button(root, text="Start Conversion", command=lambda: start_conversion(entry_input.get(), entry_output.get()))
    btn_start.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
