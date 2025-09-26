import os
import argparse

def set_outlines(folder_path, thickness):
    texcoord_file = None
    ini_file = None

    # Find Texcoord.buf and Char.ini files in the current folder
    for file in os.listdir(folder_path):
        if "Texcoord.buf" in file:
            texcoord_file = file
        if ".ini" in file:
            ini_file = file

    if texcoord_file is None or ini_file is None:
        print(f"ERROR: Unable to find Texcoord.buf or Char.ini file in folder: {folder_path}")
        return

    with open(os.path.join(folder_path, ini_file), "r") as f:
        stride = int(f.read().split(texcoord_file)[0].split("\n")[-2].split("=")[1].strip())

    print(f"Folder: {folder_path}, Texcoord: {texcoord_file}, Ini: {ini_file}, Stride: {stride}")

    # Modify Texcoord.buf file to set the outline thickness
    with open(os.path.join(folder_path, texcoord_file), "rb+") as f:
        print("Removing outlines")
        data = bytearray(f.read())
        i = 0
        while i < len(data):
            data[i+3] = thickness
            i += stride

        print("Writing results to the file")
        f.seek(0)
        f.write(data)
        f.truncate()

    print("All operations complete in folder:", folder_path)

def main():
    parser = argparse.ArgumentParser(description="Set outline thickness for all Texcoord.buf files in the folder and subfolders")
    parser.add_argument("--thickness", type=int, default=80, help="Thickness of outline (0 - no outline, 255 - maximum outline)")
    args = parser.parse_args()

    current_folder = os.getcwd()
    print("Current folder:", current_folder)

    # Recursively traverse all subfolders and set outlines in Texcoord.buf files
    for folder_path, _, _ in os.walk(current_folder):
        set_outlines(folder_path, args.thickness)

if __name__ == "__main__":
    main()
