import tkinter as tk
from tkinter import filedialog
import os
import time
import subprocess
import json


def get_exif_metadata(filename: str) -> dict:
    """Extract all EXIF metadata (including MakerNotes) using ExifTool."""
    result = subprocess.run(
        ["exiftool", "-json", filename], capture_output=True, text=True
    )

    # ExifTool returns a JSON array
    data = json.loads(result.stdout)[0]
    return data


def make_directories(selected_directory):
    unedited = os.path.join(selected_directory, "unedited")
    raws = os.path.join(selected_directory, "raws")
    exports = os.path.join(selected_directory, "exports")
    jpg = os.path.join(selected_directory, "jpg")
    mov = os.path.join(selected_directory, "mov")

    os.makedirs(unedited, exist_ok=True)
    os.makedirs(raws, exist_ok=True)
    os.makedirs(exports, exist_ok=True)
    os.makedirs(jpg, exist_ok=True)
    os.makedirs(mov, exist_ok=True)


def directory_date(files, selected_directory):
    for file_path in files:
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        ext_no_dot = ext.lstrip(".")
        meta = get_exif_metadata(file_path)
        make = meta.get("Make")
        model = meta.get("Model")

        created = os.path.getmtime(file_path)
        created = time.localtime(created)
        created = time.strftime("%d_%m_%Y", created)
        created_dir_name = os.path.join(selected_directory, created)
        os.makedirs(created_dir_name, exist_ok=True)
        make_directories(created_dir_name)

        if ext == ".jpg":
            target_subdir = "jpg"
            if model is None:
                destination = os.path.join(created_dir_name, target_subdir, filename)
            else:
                make_model_path = os.path.join(
                    created_dir_name, target_subdir, f"{make} {model}"
                )

                os.makedirs(make_model_path, exist_ok=True)
                destination = os.path.join(
                    created_dir_name, target_subdir, f"{make} {model}", filename
                )
        elif ext == ".nef":
            target_subdir = "raws"
            nef = os.path.join(created_dir_name, target_subdir, ext_no_dot)
            os.makedirs(nef, exist_ok=True)
            make_model_path = os.path.join(nef, f"{make} {model}")
            os.makedirs(make_model_path, exist_ok=True)
            destination = os.path.join(
                created_dir_name, target_subdir, ext_no_dot, f"{make} {model}", filename
            )

        elif ext == ".arw":
            target_subdir = "raws"
            arw = os.path.join(created_dir_name, target_subdir, ext_no_dot)
            os.makedirs(arw, exist_ok=True)
            make_model_path = os.path.join(arw, f"{make} {model}")
            os.makedirs(make_model_path, exist_ok=True)
            destination = os.path.join(
                created_dir_name, target_subdir, ext_no_dot, f"{make} {model}", filename
            )

        elif ext == ".raf":
            target_subdir = "raws"
            raf = os.path.join(created_dir_name, target_subdir, ext_no_dot)
            os.makedirs(raf, exist_ok=True)
            make_model_path = os.path.join(raf, f"{make} {model}")
            os.makedirs(make_model_path, exist_ok=True)
            destination = os.path.join(
                created_dir_name, target_subdir, ext_no_dot, f"{make} {model}", filename
            )

        elif ext == ".cr2":
            target_subdir = "raws"
            cr2 = os.path.join(created_dir_name, target_subdir, ext_no_dot)
            os.makedirs(cr2, exist_ok=True)
            make_model_path = os.path.join(cr2, f"{make} {model}")
            os.makedirs(make_model_path, exist_ok=True)
            destination = os.path.join(
                created_dir_name, target_subdir, ext_no_dot, f"{make} {model}", filename
            )

        elif ext == ".mov":
            target_subdir = "mov"
            destination = os.path.join(created_dir_name, target_subdir, filename)
        else:
            continue

        os.rename(file_path, destination)


def select_directory():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    selected_directory = filedialog.askdirectory(title="Select a Directory")

    if selected_directory:
        all_files = []
        for dirpath, _, filenames in os.walk(selected_directory):
            for file in filenames:
                if file.lower().endswith(
                    (".jpg", ".nef", ".mov", ".arw", ".raf", ".cr2")
                ):
                    all_files.append(os.path.join(dirpath, file))

        directory_date(all_files, selected_directory)


if __name__ == "__main__":
    select_directory()
