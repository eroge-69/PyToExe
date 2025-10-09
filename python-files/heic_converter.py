#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Converted from Jupyter Notebook: notebook.ipynb
Conversion Date: 2025-10-09T02:11:35.843Z
"""

import os
import glob
from PIL import Image
import pillow_heif

# Register the HEIF opener to allow Pillow to read HEIC files
# This is crucial for the conversion process.
try:
    # Ensure this is called only once
    pillow_heif.register_heif_opener()
except ValueError:
    # This happens if it's already registered, which is fine.
    pass 

def convert_heic_to_jpeg():
    """
    Prompts the user for a folder path, finds all HEIC files within it,
    converts them to JPEG, and saves the results in a new subfolder.
    """
    
    # --- 1. Get and Validate User Input ---
    
    print("-" * 50)
    print("HEIC to JPEG Batch Converter")
    print("-" * 50)
    
    # Use a loop to keep prompting until a valid path is given
    source_dir = ""
    while not os.path.isdir(source_dir):
        source_dir = input("Please enter the FULL path to the folder containing your HEIC files: ").strip()
        source_dir = os.path.normpath(source_dir)
        if not os.path.isdir(source_dir):
            print(f"Error: Folder not found at '{source_dir}'. Please try again.")

    # --- 2. Define and Create Output Folder ---
    
    output_folder_name = "converted_jpegs"
    # The output folder is created in the same location as the source folder
    output_dir = os.path.join(source_dir, output_folder_name)
    
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"\nCreated output folder: '{output_dir}'")
        else:
            print(f"\nUsing existing output folder: '{output_dir}'")
    except Exception as e:
        print(f"\nError: Could not create output folder. Reason: {e}")
        return

    # --- 3. Find HEIC Files ---
    
    # Look for both lowercase and uppercase HEIC extensions
    heic_files = glob.glob(os.path.join(source_dir, '*.heic'))
    heic_files.extend(glob.glob(os.path.join(source_dir, '*.HEIC')))
    
    if not heic_files:
        print("\nNo HEIC files (*.heic or *.HEIC) found in the specified folder.")
        return

    print(f"\nFound {len(heic_files)} HEIC file(s). Starting conversion...")

    # --- 4. Conversion Loop ---
    
    converted_count = 0
    
    for heic_path in heic_files:
        try:
            # Get the base filename (without path and extension)
            base_filename = os.path.splitext(os.path.basename(heic_path))[0]
            
            # Define the output JPEG path
            jpeg_path = os.path.join(output_dir, f"{base_filename}.jpeg")
            
            # 1. Open the HEIC file using pillow_heif
            heif_image = pillow_heif.open_heif(heic_path)
            
            # 2. Decode the HEIF image data into a Pillow Image object
            image = Image.frombytes(
                heif_image.mode, 
                heif_image.size, 
                heif_image.data,
                "raw",
                heif_image.mode,
                heif_image.stride,
            )
            
            # 3. Save the image as JPEG
            # Use quality=95 for high-quality output
            image.save(jpeg_path, "jpeg", quality=95)
            
            print(f"  [SUCCESS] Converted: {os.path.basename(heic_path)} -> {os.path.basename(jpeg_path)}")
            converted_count += 1
            
        except Exception as e:
            # Catch and report any errors during file processing
            print(f"  [FAILED] Could not process {os.path.basename(heic_path)}. Error: {e}")

    # --- 5. Final Summary ---
    
    print("\n" + "=" * 50)
    print(f"Conversion Complete!")
    print(f"Total files found: {len(heic_files)}")
    print(f"Total files converted: {converted_count}")
    print(f"Output files saved to: {output_dir}")
    print("=" * 50)


if __name__ == "__main__":
    convert_heic_to_jpeg()