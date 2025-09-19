
import os
import datetime
import pytesseract
from pdf2image import convert_from_path
import tkinter as tk
from tkinter import messagebox, scrolledtext

class TripFileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trip File Renamer")
        self.root.geometry("600x400")

        self.log = scrolledtext.ScrolledText(root, width=70, height=20)
        self.log.pack(pady=10)

        self.scan_button = tk.Button(root, text="Scan and Rename Files", command=self.scan_and_rename)
        self.scan_button.pack(pady=10)

    def extract_info(self, pdf_path):
        try:
            images = convert_from_path(pdf_path)
            for image in images:
                text = pytesseract.image_to_string(image)
                if "TRIP FILE COVER" in text.upper():
                    lines = text.splitlines()
                    flight = "UNKNOWN"
                    handler = "UNKNOWN"
                    for line in lines:
                        if "FLT NO" in line.upper():
                            flight_parts = line.split()
                            for part in flight_parts:
                                if any(char.isdigit() for char in part):
                                    flight = part.replace('.', '').upper()
                                    break
                        if "HANDLED BY" in line.upper() or "NAME / STAFF NO" in line.upper():
                            for word in line.split():
                                if word.isalpha() and word.upper() not in ["HANDLED", "BY", "NAME", "STAFF", "NO"]:
                                    handler = word.upper()
                                    break
                    return flight, handler
            return "UNKNOWN", "UNKNOWN"
        except Exception as e:
            return "UNKNOWN", "UNKNOWN"

    def scan_and_rename(self):
        folder = r"S:\LoadControlScanner"
        date_str = datetime.datetime.now().strftime("%d%b%y").upper()

        if not os.path.exists(folder):
            messagebox.showerror("Error", f"Folder '{folder}' does not exist.")
            return

        for filename in os.listdir(folder):
            if filename.lower().endswith(".pdf"):
                file_path = os.path.join(folder, filename)
                flight, handler = self.extract_info(file_path)
                if flight != "UNKNOWN" and handler != "UNKNOWN":
                    new_filename = f"{flight} {date_str} {handler}.pdf"
                    new_path = os.path.join(folder, new_filename)
                    os.rename(file_path, new_path)
                    self.log.insert(tk.END, f"Renamed: {filename} -> {new_filename}
")
                else:
                    self.log.insert(tk.END, f"Skipped: {filename} (not a trip file)
")

        messagebox.showinfo("Done", "File renaming completed.")

root = tk.Tk()
app = TripFileRenamerApp(root)
root.mainloop()
