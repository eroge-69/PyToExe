import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ExifTags
import exifread
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import json
import os
from hachoir.core import config
config.quiet = True  # suppress Hachoir warnings

# --- Function to extract metadata ---
def extract_metadata(file_path):
    metadata = {}
    android_info = {}
    camera_info = {}
    additional_info = {}

    # --- Pillow EXIF ---
    try:
        image = Image.open(file_path)
        exifdata = image._getexif() or {}
        for tag_id, value in exifdata.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            metadata[f"PIL_{tag}"] = str(value)

            # Android info
            if tag in ["Make", "Model", "Software"]:
                android_info[tag] = str(value)

            # Camera info
            if tag in ["Model", "Make", "LensModel", "FocalLength",
                       "FNumber", "ExposureTime", "ISOSpeedRatings"]:
                camera_info[tag] = str(value)
    except Exception:
        pass

    # --- exifread ---
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            for tag in tags.keys():
                metadata[f"ExifRead_{tag}"] = str(tags[tag])

                if "Software" in tag or "Model" in tag or "Make" in tag:
                    android_info[tag] = str(tags[tag])

                if any(word in tag for word in ["Focal", "Lens", "Aperture", "Exposure", "ISO"]):
                    camera_info[tag] = str(tags[tag])
    except Exception:
        pass

    # --- Hachoir deep metadata ---
    try:
        parser = createParser(file_path)
        if parser:
            with parser:
                meta = extractMetadata(parser)
                if meta:
                    for item in meta.exportPlaintext():
                        key, _, value = item.partition(":")
                        key = key.strip()
                        value = value.strip()
                        metadata[f"Hachoir_{key}"] = value

                        # Classify info
                        if any(word in key.lower() for word in ["software", "model", "make"]):
                            android_info[key] = value
                        elif any(word in key.lower() for word in ["lens", "focal", "aperture", "exposure", "iso", "shutter", "camera"]):
                            camera_info[key] = value
                        else:
                            additional_info[key] = value
    except Exception:
        pass

    # --- Attempt to recover stripped/erased metadata ---
    try:
        if os.path.getsize(file_path) > 0:
            parser = createParser(file_path)
            if parser:
                with parser:
                    meta = extractMetadata(parser)
                    if meta:
                        for item in meta.exportPlaintext():
                            key, _, value = item.partition(":")
                            key = key.strip()
                            value = value.strip()
                            additional_info[f"Recovered_{key}"] = value
    except Exception:
        pass

    return metadata, android_info, camera_info, additional_info

# --- Open image file ---
def open_file():
    global metadata, android_info, camera_info, additional_info
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.tiff *.bmp *.gif *.webp *.heic *.heif"),
                   ("All Files", "*.*")]
    )
    if not file_path:
        return

    metadata, android_info, camera_info, additional_info = extract_metadata(file_path)

    # Clear all text boxes
    for text_widget in [all_text, android_text, camera_text, additional_text]:
        text_widget.delete("1.0", "end")

    # Fill All Metadata
    if metadata:
        for key, value in metadata.items():
            all_text.insert("end", f"{key}: {value}\n")
    else:
        all_text.insert("end", "No metadata found.")

    # Fill Android Info
    if android_info:
        for key, value in android_info.items():
            android_text.insert("end", f"{key}: {value}\n")
    else:
        android_text.insert("end", "No Android-specific metadata found.")

    # Fill Camera Info
    if camera_info:
        for key, value in camera_info.items():
            camera_text.insert("end", f"{key}: {value}\n")
    else:
        camera_text.insert("end", "No Camera-specific metadata found.")

    # Fill Additional/Recovered Metadata
    if additional_info:
        for key, value in additional_info.items():
            additional_text.insert("end", f"{key}: {value}\n")
    else:
        additional_text.insert("end", "No additional/recovered metadata found.")

# --- Save metadata ---
def save_metadata_txt():
    content = all_text.get("1.0", "end").strip()
    if not content:
        messagebox.showwarning("Warning", "No metadata to save!")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Success", "Metadata saved successfully!")

def save_metadata_json():
    combined_data = {
        "All_Metadata": metadata,
        "Android_Info": android_info,
        "Camera_Info": camera_info,
        "Additional_Info": additional_info
    }
    file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                             filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, indent=4)
        messagebox.showinfo("Success", "Metadata saved as JSON successfully!")

# --- Modern GUI ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("📸 MetaDigger Pro - Smooth & Accurate")
root.geometry("1000x750")

# Header
header = ctk.CTkLabel(root, text="📸 MetaDigger Pro",
                      font=("Arial Rounded MT Bold", 32), text_color="cyan")
header.pack(pady=15)

subtitle = ctk.CTkLabel(root, text="Extract Complete Metadata, Android, Camera, and Attempt Recovered Data",
                        font=("Arial", 14))
subtitle.pack(pady=5)

# Buttons Frame
btn_frame = ctk.CTkFrame(root)
btn_frame.pack(pady=10)

open_btn = ctk.CTkButton(btn_frame, text="🖼 Open Image", command=open_file,
                         width=220, height=45, corner_radius=15, fg_color="dodgerblue")
open_btn.grid(row=0, column=0, padx=15, pady=10)

save_txt_btn = ctk.CTkButton(btn_frame, text="💾 Save as TXT", command=save_metadata_txt,
                             width=180, height=45, corner_radius=15, fg_color="seagreen")
save_txt_btn.grid(row=0, column=1, padx=15, pady=10)

save_json_btn = ctk.CTkButton(btn_frame, text="💾 Save as JSON", command=save_metadata_json,
                              width=180, height=45, corner_radius=15, fg_color="orange")
save_json_btn.grid(row=0, column=2, padx=15, pady=10)

# Tabs for Metadata Views
tabview = ctk.CTkTabview(root, width=950, height=550)
tabview.pack(pady=15)

tabview.add("🗂 All Metadata")
tabview.add("📱 Android Info")
tabview.add("📸 Camera Info")
tabview.add("🛠 Additional / Recovered Info")

all_text = ctk.CTkTextbox(tabview.tab("🗂 All Metadata"), width=920, height=500,
                          font=("Consolas", 12), wrap="word")
all_text.pack(padx=10, pady=10)

android_text = ctk.CTkTextbox(tabview.tab("📱 Android Info"), width=920, height=500,
                              font=("Consolas", 12), wrap="word")
android_text.pack(padx=10, pady=10)

camera_text = ctk.CTkTextbox(tabview.tab("📸 Camera Info"), width=920, height=500,
                             font=("Consolas", 12), wrap="word")
camera_text.pack(padx=10, pady=10)

additional_text = ctk.CTkTextbox(tabview.tab("🛠 Additional / Recovered Info"), width=920, height=500,
                                 font=("Consolas", 12), wrap="word")
additional_text.pack(padx=10, pady=10)

root.mainloop()
