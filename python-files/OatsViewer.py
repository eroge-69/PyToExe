import os
import tempfile
import tkinter as tk
from tkinter import filedialog
import webbrowser
import msvcrt  # Windows only
import time
import shutil

def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select a .oats file",
        filetypes=[("OATS files", "*.oats"), ("All files", "*.*")]
    )

    if not file_path:
        print("No file selected. Exiting.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    temp_dir = tempfile.gettempdir()
    temp_html_path = os.path.join(temp_dir, "temp_oats_view.html")

    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Opening temp HTML file: {temp_html_path}")

    webbrowser.open(f"file:///{temp_html_path.replace(os.sep, '/')}")

    print("Press '8' to save the HTML file permanently.")
    print("Press '9' to delete the temp file and exit.")

    saved_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SavedHTML")
    if not os.path.exists(saved_folder):
        os.makedirs(saved_folder)

    saved = False

    try:
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'8':
                    # Save the HTML permanently
                    if saved:
                        print("Already saved.")
                        continue
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    saved_path = os.path.join(saved_folder, base_name + ".html")

                    # If file exists, add a number suffix
                    count = 1
                    while os.path.exists(saved_path):
                        saved_path = os.path.join(saved_folder, f"{base_name}_{count}.html")
                        count += 1

                    shutil.move(temp_html_path, saved_path)
                    print(f"Saved HTML file to: {saved_path}")
                    saved = True
                elif key == b'9':
                    print("\n'9' pressed. Cleaning up and exiting...")
                    if os.path.exists(temp_html_path):
                        os.remove(temp_html_path)
                        print(f"Deleted temporary file: {temp_html_path}")
                    break
            time.sleep(0.1)
    except KeyboardInterrupt:
        # Cleanup on Ctrl+C
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
            print(f"\nDeleted temporary file: {temp_html_path}")

    print("Goodbye!")

if __name__ == "__main__":
    main()
