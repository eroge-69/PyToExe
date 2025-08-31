import os
import json
import fitz  # PyMuPDF
from pathlib import Path
import re
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES, TkinterDnD
from datetime import datetime
import webbrowser

# Paths and patterns
BASE_DIR = Path(__file__).parent.resolve()
INPUT_DIR = BASE_DIR / "Input"
OUTPUT_DIR = BASE_DIR / "Output"
CONFIG_FILE = BASE_DIR / "coords.json"
LOG_FILE = BASE_DIR / "log.txt"
STAMP_PATTERN = re.compile(r"stamp_(\d+)\.(png|jpg|jpeg)$", re.IGNORECASE)

# Utilities
def detect_stamps():
    stamps = {}
    for file in BASE_DIR.iterdir():
        match = STAMP_PATTERN.match(file.name)
        if match:
            num = int(match.group(1))
            stamps[num] = file
    return dict(sorted(stamps.items()))

def load_coordinates():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_coordinates(coords):
    with open(CONFIG_FILE, "w") as f:
        json.dump(coords, f)

def log_action(message):
    with open(LOG_FILE, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {message}\n")

def preview_pdf(path):
    webbrowser.open_new(str(path))

def insert_stamps(pdf_path, output_path, stamps, coordinates):
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        for num, stamp_path in stamps.items():
            x, y = coordinates[str(num)]
            stamp_pix = fitz.Pixmap(str(stamp_path))
            page.insert_image(
                rect=(x, y, x + stamp_pix.width, y + stamp_pix.height),
                filename=str(stamp_path)
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(output_path)
        doc.close()
        log_action(f"Stamped: {pdf_path.name}")
        preview_pdf(output_path)
    except Exception as e:
        log_action(f"Error stamping {pdf_path.name}: {e}")
        ttk.Messagebox.show_error("Error", f"Failed to stamp {pdf_path.name}.\n{e}")

# GUI App
class PDFStamperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Auto Stamper for Inspection Reports")
        self.root.geometry("700x600")

        self.stamps = detect_stamps()
        if not self.stamps:
            ttk.Messagebox.show_error("Error", "No stamp images found (e.g., stamp_1.png, stamp_2.png).")
            root.destroy()
            return

        self.saved_coords = load_coordinates()
        self.coord_entries = {}
        self.status_var = ttk.StringVar(value="Ready")

        self.build_gui()

    def build_gui(self):
        ttk.Label(self.root, text="PDF Auto Stamper for Inspection Reports", font=("Helvetica", 18, "bold")).pack(pady=10)

        notebook = ttk.Notebook(self.root, bootstyle="primary")
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Tab 1: Coordinate Setup
        setup_tab = ttk.Frame(notebook)
        notebook.add(setup_tab, text="Coordinate Setup")

        ttk.Label(setup_tab, text="Enter coordinates (X, Y) for each stamp", font=("Helvetica", 12)).pack(pady=5)

        canvas = ttk.Canvas(setup_tab)
        scrollbar = ttk.Scrollbar(setup_tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, num in enumerate(self.stamps):
            frame = ttk.Frame(scroll_frame)
            frame.grid(row=i, column=0, pady=5, padx=10, sticky="w")

            ttk.Label(frame, text=f"Stamp {num}:", width=12).grid(row=0, column=0)

            x_entry = ttk.Entry(frame, width=10)
            y_entry = ttk.Entry(frame, width=10)

            if str(num) in self.saved_coords:
                x_entry.insert(0, self.saved_coords[str(num)][0])
                y_entry.insert(0, self.saved_coords[str(num)][1])
            else:
                x_entry.insert(0, "250")
                y_entry.insert(0, "250")

            x_entry.grid(row=0, column=1, padx=5)
            y_entry.grid(row=0, column=2, padx=5)

            self.coord_entries[num] = (x_entry, y_entry)

        ttk.Button(setup_tab, text="💾 Save Coordinates", command=self.save_coords, bootstyle="success").pack(pady=10)
        ttk.Button(setup_tab, text="📁 Process PDFs in Input Folder", command=self.process_input_folder, bootstyle="info").pack(pady=5)

        # Tab 2: Drag & Drop
        drag_tab = ttk.Frame(notebook)
        notebook.add(drag_tab, text="Drag & Drop")

        self.drop_label = ttk.Label(drag_tab, text="📥 Drag & drop PDF files here", relief="ridge", padding=30, bootstyle="light")
        self.drop_label.pack(pady=20, fill="x", padx=20)

        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)

        ttk.Label(drag_tab, textvariable=self.status_var, relief="sunken", anchor="w", bootstyle="secondary").pack(fill="x", side="bottom")

    def save_coords(self):
        try:
            coords = {str(num): (int(x.get()), int(y.get())) for num, (x, y) in self.coord_entries.items()}
            save_coordinates(coords)
            self.status_var.set("Coordinates saved.")
            log_action("Coordinates saved.")
        except ValueError:
            ttk.Messagebox.show_error("Invalid Input", "Please enter valid numeric coordinates.")

    def process_input_folder(self):
        coords = load_coordinates()
        stamps = detect_stamps()
        found = False

        for root, _, files in os.walk(INPUT_DIR):
            for file in files:
                if file.lower().endswith(".pdf"):
                    found = True
                    input_path = Path(root) / file
                    relative_path = input_path.relative_to(INPUT_DIR)
                    output_path = OUTPUT_DIR / relative_path
                    insert_stamps(input_path, output_path, stamps, coords)

        if not found:
            ttk.Messagebox.show_info("No PDFs", "No PDF files found in the Input folder.")
            log_action("No PDFs found in Input folder.")
        else:
            ttk.Messagebox.show_info("Success", "All PDFs have been stamped.")
            log_action("Processed all PDFs in Input folder.")
        self.status_var.set("Ready")

    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        pdfs = [Path(f) for f in files if f.lower().endswith(".pdf")]
        if not pdfs:
            ttk.Messagebox.show_warning("Invalid Files", "Please drop valid PDF files.")
            return

        coords = load_coordinates()
        stamps = detect_stamps()
        self.status_var.set("Processing dropped files...")

        for pdf in pdfs:
            output_path = OUTPUT_DIR / pdf.name
            insert_stamps(pdf, output_path, stamps, coords)

        ttk.Messagebox.show_info("Done", "Dropped PDFs have been stamped.")
        log_action(f"Stamped {len(pdfs)} dropped PDFs.")
        self.status_var.set("Ready")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    style = ttk.Style(theme="journal")  # Try "darkly", "journal", "cyborg" for other looks
    app = PDFStamperApp(root)
    root.mainloop()