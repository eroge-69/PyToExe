import customtkinter as ctk
from tkinter import filedialog, messagebox
import fitz
import os
import threading
from datetime import datetime
import mysql.connector
import tempfile
import atexit
import win32print
import win32ui
import win32con
from PIL import Image, ImageWin

# ---------- Setup Appearance ----------
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AdvancedKanbanSlicerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Advanced PDF Kanban Slicer")
        self.geometry("800x500")
        self.resizable(False, False)

        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.custom_sections = []
        self.cm_to_pt = 28.3465  # cm to point
        self.temp_files = []

        self.create_widgets()
        self.load_designs()
        self.load_printers()

        # Clean up temporary files on exit
        atexit.register(self.cleanup_temp_files)

    # ------------------ WIDGETS ------------------
    def create_widgets(self):
        self.title_label = ctk.CTkLabel(
            self.frame,
            text="Advanced PDF Kanban Slicer",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.pack(pady=(0, 20))

        # Design dropdown
        self.design_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.design_frame.pack(fill="x", pady=5)
        self.design_label = ctk.CTkLabel(
            self.design_frame, text="Select Layout Design:", width=150, anchor="w"
        )
        self.design_label.pack(side="left", padx=(0,10))
        self.design_var = ctk.StringVar()
        self.design_dropdown = ctk.CTkOptionMenu(
            self.design_frame, variable=self.design_var, values=[], command=self.on_design_change
        )
        self.design_dropdown.pack(side="left", fill="x", expand=True)

        # Input PDF file
        self.input_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.input_frame.pack(fill="x", pady=5)
        self.input_label = ctk.CTkLabel(
            self.input_frame, text="Select PDF File:", width=120, anchor="w"
        )
        self.input_label.pack(side="left", padx=(0,10))
        self.input_path = ctk.CTkEntry(self.input_frame, placeholder_text="Path to PDF...", width=350)
        self.input_path.pack(side="left", expand=True, fill="x")
        self.browse_input_button = ctk.CTkButton(
            self.input_frame, text="Browse", width=80, command=self.browse_input
        )
        self.browse_input_button.pack(side="right")

        # Skip empty pages checkbox
        self.skip_empty_pages_var = ctk.BooleanVar(value=True)
        self.skip_empty_pages_checkbox = ctk.CTkCheckBox(
            self.frame, text="Skip empty pages", variable=self.skip_empty_pages_var
        )
        self.skip_empty_pages_checkbox.pack(anchor="w", pady=(10,5), padx=5)

        # Sections label
        self.sections_display_label = ctk.CTkLabel(
            self.frame,
            text="Current Sections: None",
            font=ctk.CTkFont(size=12, slant="italic")
        )
        self.sections_display_label.pack(pady=(5,10))

        # Printer dropdown
        self.printer_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.printer_frame.pack(fill="x", pady=5)
        self.printer_label = ctk.CTkLabel(
            self.printer_frame, text="Select Printer:", width=120, anchor="w"
        )
        self.printer_label.pack(side="left", padx=(0,10))
        self.printer_var = ctk.StringVar()
        self.printer_dropdown = ctk.CTkOptionMenu(
            self.printer_frame, variable=self.printer_var, values=[], command=lambda x: None
        )
        self.printer_dropdown.pack(side="left", fill="x", expand=True)

        # Print button
        self.print_button = ctk.CTkButton(
            self.frame, text="Print Directly",
            command=self.start_print_thread,
            fg_color="#0d6efd", hover_color="#084298"
        )
        self.print_button.pack(fill="x", pady=5)

        # Log textbox
        self.log_textbox = ctk.CTkTextbox(
            self.frame, width=500, height=120, font=("Consolas",9), state="disabled"
        )
        self.log_textbox.pack(pady=5, padx=5, fill="x")

    # ------------------ DATABASE ------------------
    def load_designs(self):
        try:
            conn = mysql.connector.connect(
                host="192.168.0.145",
                user="bilgy",
                password="123",
                database="nic"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT design_name FROM design_kanban")
            designs = [row[0] for row in cursor.fetchall()]
            self.design_dropdown.configure(values=designs)
            if designs:
                self.design_var.set(designs[0])
                self.on_design_change(designs[0])
            cursor.close()
            conn.close()
        except Exception as e:
            self.log(f"Failed to load designs: {e}", "ERROR")

    def on_design_change(self, design_name):
        try:
            conn = mysql.connector.connect(
                host="192.168.0.145",
                user="bilgy",
                password="123",
                database="nic"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM design_kanban WHERE design_name=%s", (design_name,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                self.custom_sections = []
                for i in range(1, 7):
                    y_from = row.get(f'y_from_{i}')
                    y_to = row.get(f'y_to_{i}')
                    if y_from is not None and y_to is not None:
                        self.custom_sections.append({'yFrom': float(y_from), 'yTo': float(y_to)})
                self.update_sections_display()
                self.log(f"Layout '{design_name}' loaded from database", "SUCCESS")
            else:
                self.log(f"Layout '{design_name}' not found", "WARNING")
        except Exception as e:
            self.log(f"Failed to load layout '{design_name}': {e}", "ERROR")

    # ------------------ PRINTER ------------------
    def load_printers(self):
        printers = [p[2] for p in win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        )]
        self.printer_dropdown.configure(values=printers)
        if printers:
            self.printer_var.set(printers[0])

    # ------------------ FILE BROWSING ------------------
    def browse_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files","*.pdf")])
        if file_path:
            self.input_path.delete(0,"end")
            self.input_path.insert(0,file_path)

    # ------------------ SECTIONS ------------------
    def update_sections_display(self):
        if not self.custom_sections:
            self.sections_display_label.configure(text="Current Sections: None")
        else:
            display_text = "Current Sections:\n"
            for i, section in enumerate(self.custom_sections):
                display_text += f"{i+1}. {section['yFrom']:.1f}cm - {section['yTo']:.1f}cm\n"
            self.sections_display_label.configure(text=display_text.strip())

    # ------------------ LOG ------------------
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert(ctk.END, f"{formatted_message}\n", level)
        lines = self.log_textbox.get("1.0", ctk.END).splitlines()
        if len(lines) > 50:
            self.log_textbox.delete("1.0", f"{len(lines)-50}.0")
        self.log_textbox.see(ctk.END)
        self.log_textbox.configure(state="disabled")
        self.update_idletasks()

    # ------------------ PRINT USING WIN32PRINT ------------------
    def start_print_thread(self):
        input_file = self.input_path.get()
        printer_name = self.printer_var.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showwarning("Warning","Please select a valid PDF file first.")
            return
        if not printer_name:
            messagebox.showwarning("Warning","Please select a printer first.")
            return
        threading.Thread(
            target=self.print_pdf_win32,
            args=(input_file, printer_name),
            daemon=True
        ).start()

    def print_pdf_win32(self, pdf_file, printer_name):
        try:
            doc = fitz.open(pdf_file)
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_name)
            hDC.StartDoc(pdf_file)

            for page_num, page in enumerate(doc):
                for section in self.custom_sections:
                    y_from_pt = section['yFrom'] * self.cm_to_pt
                    y_to_pt = section['yTo'] * self.cm_to_pt
                    rect = fitz.Rect(0, y_from_pt, page.rect.width, y_to_pt)
                    pix = page.get_pixmap(clip=rect, dpi=300)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                    # PIL → DIB → printer
                    dib = ImageWin.Dib(img)
                    hDC.StartPage()
                    dib.draw(hDC.GetHandleOutput(), (0,0,img.width,img.height))
                    hDC.EndPage()

                self.log(f"Page {page_num+1}/{len(doc)} printed.", "INFO")

            hDC.EndDoc()
            hDC.DeleteDC()
            doc.close()
            self.log("Printing finished successfully.", "SUCCESS")

        except Exception as e:
            self.log(f"Failed to print PDF: {e}", "ERROR")

    # ------------------ CLEANUP TEMP FILES ------------------
    def cleanup_temp_files(self):
        for f in self.temp_files:
            try:
                os.unlink(f)
            except:
                pass
        self.temp_files.clear()

# ------------------ RUN APP ------------------
if __name__ == "__main__":
    app = AdvancedKanbanSlicerApp()
    app.mainloop()
