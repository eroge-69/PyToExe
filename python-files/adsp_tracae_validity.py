import os
import shutil
import xml.etree.ElementTree as ET

def get_trace_validity(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        for elem in root.iter():
            if elem.tag.lower() == 'trace_validity':
                return elem.text.strip().lower() if elem.text else ''
        return ''
    except Exception as e:
        print(f"Error parsing XML '{xml_path}': {e}")
        return None

def process_all_xml_files_in_subfolders(parent_folder, exclude_files):
    annotatable_folder = os.path.join(parent_folder, 'Annotatable')
    na_folder = os.path.join(parent_folder, 'NA')
    os.makedirs(annotatable_folder, exist_ok=True)
    os.makedirs(na_folder, exist_ok=True)

    for item in os.listdir(parent_folder):
        if item in ['Annotatable', 'NA']:
            continue

        subfolder_path = os.path.join(parent_folder, item)
        if os.path.isdir(subfolder_path):
            print(f"\nProcessing folder: {subfolder_path}")

            for filename in os.listdir(subfolder_path):
                # Exclude files ending with '_Scan.scan.xml'
                if filename.endswith('_Scan.scan.xml'):
                    print(f"Skipping file due to suffix exclusion: {filename}")
                    continue
                
                if filename.lower().endswith('.xml'):
                    if filename in exclude_files:
                        print(f"Skipping excluded file '{filename}'.")
                        continue

                    file_path = os.path.join(subfolder_path, filename)

                    validity = get_trace_validity(file_path)
                    if validity is None:
                        dest = os.path.join(na_folder, filename)
                        shutil.move(file_path, dest)
                        print(f"Invalid XML: '{filename}' moved to NA folder.")
                        continue

                    if validity == "valid":
                        dest = os.path.join(annotatable_folder, filename)
                        shutil.move(file_path, dest)
                        print(f"'trace_validity' is VALID: '{filename}' moved to Annotatable.")
                    else:
                        dest = os.path.join(na_folder, filename)
                        shutil.move(file_path, dest)
                        print(f"'trace_validity' is NOT valid (value: '{validity}'): '{filename}' moved to NA.")

try:
    parent_folder = input("Enter the parent folder path (e.g., 'adsp'): ")
    exclude_files = ['DREAM_label_project_structure.xml', 'GtexCameraCalibration.xml', 'project.xml']
    process_all_xml_files_in_subfolders(parent_folder, exclude_files)
except Exception as e:
    print(f"An error occurred: {e}")

input("\nPress Enter to exit...")
