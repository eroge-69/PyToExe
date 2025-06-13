import os
import shutil
import xml.etree.ElementTree as ET
from tkinter import filedialog, Tk
from pathlib import Path

def select_file(title, filetypes):
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    return file_path

def select_folder(title):
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title=title)
    return folder_path

def extract_file_paths_from_xml(xml_path):
    media_files = set()
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for elem in root.iter():
            if elem.text and (".mp4" in elem.text.lower() or ".mov" in elem.text.lower() or ".avi" in elem.text.lower() or
                              ".mp3" in elem.text.lower() or ".wav" in elem.text.lower() or
                              ".jpg" in elem.text.lower() or ".png" in elem.text.lower()):
                media_files.add(elem.text.strip())
    except ET.ParseError:
        print("Error parsing the XML file. Please select a valid EDIUS-exported XML file.")
    return media_files

def copy_files_to_folder(file_paths, destination_folder):
    for file_path in file_paths:
        if os.path.isfile(file_path):
            try:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(destination_folder, filename)

                # Handle duplicate file names
                count = 1
                while os.path.exists(dest_path):
                    filename_base, ext = os.path.splitext(filename)
                    dest_path = os.path.join(destination_folder, f"{filename_base}_{count}{ext}")
                    count += 1

                shutil.copy2(file_path, dest_path)
                print(f"Copied: {file_path} → {dest_path}")
            except Exception as e:
                print(f"Error copying file: {file_path} - {e}")
        else:
            print(f"File not found: {file_path}")

def main():
    print("🔍 Please select the EDIUS-exported XML project file...")
    xml_file = select_file("Select EDIUS XML File", [("XML Files", "*.xml")])
    if not xml_file:
        print("No file selected.")
        return

    print("📁 Please select a destination folder...")
    destination = select_folder("Select Destination Folder for Consolidated Files")
    if not destination:
        print("No folder selected.")
        return

    print("📂 Extracting media file paths from XML...")
    media_paths = extract_file_paths_from_xml(xml_file)
    if not media_paths:
        print("No media files found in the XML.")
        return

    print(f"🗂️ Found {len(media_paths)} media files. Starting copy...")
    copy_files_to_folder(media_paths, destination)

    print("\n✅ All media files have been copied successfully.")

if __name__ == "__main__":
    main()
