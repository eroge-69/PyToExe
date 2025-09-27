import os
import argparse
import struct

def process_directory(directory, thickness):
    texcoord_file = [x for x in os.listdir(directory) if "Texcoord.buf" in x]
    if len(texcoord_file) == 0:
        print(f"ERROR: unable to find texcoord file in {directory}. Skipping this directory.")
        return

    texcoord_file = os.path.join(directory, texcoord_file[0])

    ini_file = [x for x in os.listdir(directory) if ".ini" in x]
    if len(ini_file) == 0:
        print(f"ERROR: unable to find .ini file in {directory}. Skipping this directory.")
        return

    ini_file = os.path.join(directory, ini_file[0])

    with open(ini_file, "r") as f:
        stride = int(f.read().split(os.path.basename(texcoord_file))[0].split("\n")[-2].split("=")[1].strip())

    print(f"Processing directory: {directory}, Texcoord: {texcoord_file}, Ini: {ini_file}, Stride: {stride}")

    with open(texcoord_file, "rb+") as f:
        print("Removing outlines")
        data = bytearray(f.read())
        i = 0
        while i < len(data):
            data[i + 3] = thickness
            i += stride

        print("Writing results to new file")
        f.seek(0)
        f.write(data)
        f.truncate()

    print(f"Operations complete for directory: {directory}\n")

def main():
    parser = argparse.ArgumentParser(description="Set outline thickness")
    parser.add_argument("--thickness", type=int, default=0, help="Thickness of outline (0 - no outline, 255 - maximum outline)")
    args = parser.parse_args()

    for root, dirs, files in os.walk("."):
        process_directory(root, args.thickness)

    print("All operations complete, exiting")

if __name__ == "__main__":
    main()
