import os
import subprocess
import sys

def list_python_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.endswith(".py") and os.path.isfile(os.path.join(folder_path, f))]

def convert_single_py_to_exe(folder_path):
    if not os.path.isdir(folder_path):
        print("Error: Invalid folder path.")
        return

    py_files = list_python_files(folder_path)

    if not py_files:
        print("No Python files found in the folder.")
        return

    print("\nPython files found:")
    for idx, file in enumerate(py_files):
        print(f"{idx + 1}: {file}")

    try:
        choice = int(input("\nEnter the number of the file you want to convert: "))
        if not (1 <= choice <= len(py_files)):
            print("Invalid selection.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    selected_file = py_files[choice - 1]
    full_path = os.path.join(folder_path, selected_file)

    print(f"\nConverting {selected_file} to .exe...\n")
    subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--onefile", "--noconfirm",
        full_path
    ])
    print("\nDone. Check the 'dist' folder for the .exe file.")

if __name__ == "__main__":
    folder = input("Enter the path to the folder containing Python files: ").strip()
    convert_single_py_to_exe(folder)
