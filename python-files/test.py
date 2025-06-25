import os
import time
import fitz  # PyMuPDF
import pandas as pd
import win32print
import win32api
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flask import Flask, send_file
from threading import Thread

print('success')
# CONFIGURATION
WATCH_FOLDER = r"C:\PDFWatch"                     # Folder to monitor
EXCEL_PATH = os.path.join(WATCH_FOLDER, "output.xlsx")  # Excel output
PRINTER_NAME = "Your Printer Name Here"           # Set your actual printer name
EXPOSE_IP = '0.0.0.0'
PORT = 5000


# --------- PDF Handling ---------
def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()

def append_text_to_excel(text, source_file):
    new_row = {"Source": source_file, "Content": text}
    if os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.DataFrame([new_row])
    df.to_excel(EXCEL_PATH, index=False)


# --------- Printing ---------
def print_pdf(pdf_path):
    try:
        print(f"Printing PDF: {pdf_path}")
        # Set default printer temporarily
        original_printer = win32print.GetDefaultPrinter()
        win32print.SetDefaultPrinter(PRINTER_NAME)

        # Use ShellExecute to print
        win32api.ShellExecute(
            0,
            "print",
            pdf_path,
            None,
            ".",
            0
        )

        # Restore original printer
        win32print.SetDefaultPrinter(original_printer)
        print(f"Sent to printer: {PRINTER_NAME}")
    except Exception as e:
        print(f"[ERROR] Printing failed: {e}")


# --------- Folder Monitor ---------
class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.lower().endswith(".pdf"):
            print(f"New PDF detected: {event.src_path}")
            time.sleep(2)  # Wait for file to be fully saved
            print_pdf(event.src_path)
            time.sleep(2)  # Give the printer time before reading
            text = extract_text_from_pdf(event.src_path)
            print(text)
            append_text_to_excel(text, os.path.basename(event.src_path))
            print(f"Appended to Excel: {EXCEL_PATH}")


def start_monitor():
    if not os.path.exists(WATCH_FOLDER):
        os.makedirs(WATCH_FOLDER)
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()
    print(f"Watching folder: {WATCH_FOLDER}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# --------- Flask Server ---------
app = Flask(__name__)

@app.route('/')
def serve_excel():
    return send_file(EXCEL_PATH, as_attachment=True)

def run_flask():
    app.run(host=EXPOSE_IP, port=PORT)


# --------- Main ---------
if __name__ == "__main__":
    # Start web server
    Thread(target=run_flask, daemon=True).start()
    print(f"Excel accessible at: http://{EXPOSE_IP}:{PORT}/")

    # Start folder watcher
    start_monitor()
