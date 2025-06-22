import os
import re
import threading
from pathlib import Path
from datetime import datetime
from tkinter import Tk, Label, Button, filedialog, StringVar
from tkinter import ttk
from PyPDF2 import PdfReader
from openpyxl import Workbook


class PDFExtractorApp:
    def __init__(self, master):
        self.master = master
        master.title("PDF ამომღები")
        master.geometry("600x300")

        self.folder_path = None
        self.status_var = StringVar()
        self.result_var = StringVar()

        self.label = Label(master, text="აირჩიე მთავარი ფოლდერი, რომელიც შეიცავს ქვეფოლდერებს:")
        self.label.pack(pady=10)

        self.select_button = Button(master, text="აირჩიე ფოლდერი", command=self.select_folder)
        self.select_button.pack()

        self.start_button = Button(master, text="დაწყება", command=self.start_processing)
        self.start_button.pack(pady=10)

        self.progress = ttk.Progressbar(master, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=10)

        self.status_label = Label(master, textvariable=self.status_var)
        self.status_label.pack()

        self.result_label = Label(master, textvariable=self.result_var, wraplength=580, justify="left")
        self.result_label.pack(pady=10)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        self.status_var.set(f"მთავარი ფოლდერი: {self.folder_path}")

    def start_processing(self):
        if not self.folder_path:
            self.status_var.set("გთხოვთ, აირჩიეთ ფოლდერი.")
            return

        thread = threading.Thread(target=self.process_all_folders)
        thread.start()

    def extract_info_from_pdf(self, file_path):
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            return {"error": f"PDF წაკითხვის შეცდომა: {e}"}

        result = {"file": Path(file_path).name}

        match = re.search(
            r"მიწის ნაკვეთის (მართლზომიერი მფლობელი|თვითნებურად დამკავებელი პირი)\s*:\s*ფიზიკური პირი,\s+([\wა-ჰ]+)\s+([\wა-ჰ]+)\s+[\wა-ჰ]+\s*/(\d{11})/",
            text
        )
        if match:
            result["last_name"] = match.group(3)
            result["id_number"] = match.group(4)
        else:
            result["last_name"] = None
            result["id_number"] = None

        cad_match = re.search(r"საკადასტრო კოდი[:\s]*(\d{2,3}\.\d{2,3}\.\d{2,3}\.\d{3}\.\d{3})", text)
        if not cad_match:
            cad_match = re.search(r"საველე კოდი[:\s]*(\d{2,3}\.\d{2,3}\.\d{2,3}\.\d{3}\.\d{3})", text)

        result["cadastral_code"] = cad_match.group(1) if cad_match else None
        return result

    def process_all_folders(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"log_{timestamp}.txt"
        excel_file = f"results_{timestamp}.xlsx"

        wb = Workbook()
        ws = wb.active
        ws.append(["ფოლდერი", "პირადი ნომერი", "გვარი", "საკადასტრო კოდი"])

        all_folders = [f for f in Path(self.folder_path).iterdir() if f.is_dir()]
        total = len(all_folders)
        self.progress["maximum"] = total

        with open(log_file, "w", encoding="utf-8") as log:
            for i, folder in enumerate(sorted(all_folders, key=lambda x: x.name)):
                self.progress["value"] = i + 1
                self.status_var.set(f"დამუშავება: {folder.name}")

                found_file = None
                for file in folder.glob("*.pdf"):
                    if "dssi4sign" in file.name.lower():
                        found_file = file
                        break
                if not found_file:
                    for file in folder.glob("*.pdf"):
                        if "redi" in file.name.lower():
                            found_file = file
                            break

                if not found_file:
                    log.write(f"[{folder.name}] PDF ფაილი ვერ მოიძებნა\n")
                    ws.append([folder.name, "ვერ მოიძებნა", "ვერ მოიძებნა", "ვერ მოიძებნა"])
                    continue

                data = self.extract_info_from_pdf(found_file)
                if "error" in data:
                    log.write(f"[{folder.name}] შეცდომა: {data['error']}\n")
                    ws.append([folder.name, "შეცდომა", "შეცდომა", "შეცდომა"])
                    continue

                log.write(f"[{folder.name}] დამუშავდა ფაილი: {found_file.name}\n")
                ws.append([
                    folder.name,
                    data.get("id_number", "ვერ მოიძებნა"),
                    data.get("last_name", "ვერ მოიძებნა"),
                    data.get("cadastral_code", "ვერ მოიძებნა")
                ])

        wb.save(excel_file)
        self.status_var.set("დამუშავება დასრულდა!")
        self.result_var.set(f"Excel ფაილი: {os.path.abspath(excel_file)}\nLog ფაილი: {os.path.abspath(log_file)}")


if __name__ == "__main__":
    root = Tk()
    app = PDFExtractorApp(root)
    root.mainloop()
