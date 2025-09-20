import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import datetime
import webbrowser
from urllib.parse import quote

class PharmaQualifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PharmaQualify - Qualification Document Generator")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f8f9fa')
        
        # Colors
        self.pharma_blue = '#0066cc'
        self.pharma_light_blue = '#e6f0ff'
        self.pharma_dark_blue = '#004080'
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg='#f8f9fa')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_font = ('Segoe UI', 16, 'bold')
        title_label = tk.Label(self.main_frame, text="PharmaQualify - Qualification Document Generator", 
                              font=title_font, foreground=self.pharma_dark_blue, bg='#f8f9fa')
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create frames for each tab
        self.upload_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.dq_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.iq_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.oq_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.export_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        
        self.notebook.add(self.upload_frame, text='Upload PDI Report')
        self.notebook.add(self.dq_frame, text='Design Qualification')
        self.notebook.add(self.iq_frame, text='Installation Qualification')
        self.notebook.add(self.oq_frame, text='Operational Qualification')
        self.notebook.add(self.export_frame, text='Export Documents')
        
        # Setup each tab
        self.setup_upload_tab()
        self.setup_dq_tab()
        self.setup_iq_tab()
        self.setup_oq_tab()
        self.setup_export_tab()
        
        # Initialize data storage
        self.pdi_data = {
            'file_name': '',
            'equipment_id': '',
            'equipment_type': '',
            'manufacturer': '',
            'model_number': '',
            'upload_date': ''
        }
        
    def setup_upload_tab(self):
        # Upload section
        upload_lf = tk.LabelFrame(self.upload_frame, text="Upload Pre-Dispatch Inspection Report", 
                                 bg='#f8f9fa', fg='#004080', font=('Segoe UI', 10, 'bold'))
        upload_lf.pack(fill=tk.X, padx=10, pady=10)
        
        upload_btn = tk.Button(upload_lf, text="Select PDF File", command=self.upload_pdf, 
                              bg=self.pharma_blue, fg='white', relief=tk.FLAT, padx=20, pady=10,
                              font=('Segoe UI', 10))
        upload_btn.pack(pady=20)
        
        # File info section
        info_lf = tk.LabelFrame(self.upload_frame, text="File Information", 
                               bg='#f8f9fa', fg='#004080', font=('Segoe UI', 10, 'bold'))
        info_lf.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = scrolledtext.ScrolledText(info_lf, height=10, width=80, font=('Consolas', 10))
        info_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        info_text.config(state=tk.DISABLED)
        self.info_text = info_text
        
    def setup_dq_tab(self):
        # Design Qualification content
        dq_lf = tk.LabelFrame(self.dq_frame, text="Design Qualification Document", 
                             bg='#f8f9fa', fg='#004080', font=('Segoe UI', 10, 'bold'))
        dq_lf.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        dq_text = scrolledtext.ScrolledText(dq_lf, height=20, width=80, font=('Consolas', 10))
        dq_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        dq_text.insert(tk.END, "Design Qualification content will be generated here...")
        self.dq_text = dq_text
        
    def setup_iq_tab(self):
        # Installation Qualification content
        iq_lf = tk.LabelFrame(self.iq_frame, text="Installation Qualification Document", 
                             bg='#f8f9fa', fg='#004080', font=('Segoe UI', 10, 'bold'))
        iq_lf.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        iq_text = scrolledtext.ScrolledText(iq_lf, height=20, width=80, font=('Consolas', 10))
        iq_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        iq_text.insert(tk.END, "Installation Qualification content will be generated here...")
        self.iq_text = iq_text
        
    def setup_oq_tab(self):
        # Operational Qualification content
        oq_lf = tk.LabelFrame(self.oq_frame, text="Operational Qualification Document", 
                             bg='#f8f9fa', fg='#004080', font=('Segoe UI', 10, 'bold'))
        oq_lf.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        oq_text = scrolledtext.ScrolledText(oq_lf, height=20, width=80, font=('Consolas', 10))
        oq_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        oq_text.insert(tk.END, "Operational Qualification content will be generated here...")
        self.oq_text = oq_text
        
    def setup_export_tab(self):
        # Export options
        export_lf = tk.LabelFrame(self.export_frame, text="Export Options", 
                                 bg='#f8f9fa', fg='#004080', font=('Segoe UI', 10, 'bold'))
        export_lf.pack(fill=tk.X, padx=10, pady=10)
        
        format_frame = tk.Frame(export_lf, bg='#f8f9fa')
        format_frame.pack(pady=10)
        
        tk.Label(format_frame, text="Export Format:", bg='#f8f9fa', 
                font=('Segoe UI', 10)).grid(row=0, column=0, padx=5, pady=5)
        
        self.export_format = tk.StringVar(value="HTML")
        formats = ["HTML", "Text"]
        format_combo = ttk.Combobox(format_frame, textvariable=self.export_format, 
                                   values=formats, state="readonly", width=15)
        format_combo.grid(row=0, column=1, padx=5, pady=5)
        
        export_btn = tk.Button(export_lf, text="Export Documents", command=self.export_documents, 
                              bg=self.pharma_blue, fg='white', relief=tk.FLAT, padx=20, pady=10,
                              font=('Segoe UI', 10))
        export_btn.pack(pady=20)
        
    def upload_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDI Report PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.pdi_data['file_name'] = os.path.basename(file_path)
            self.pdi_data['upload_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Simulate extracting data from PDF (in a real app, you'd use a PDF library)
            self.pdi_data['equipment_id'] = "EQ-12345"
            self.pdi_data['equipment_type'] = "Tablet Press Machine"
            self.pdi_data['manufacturer'] = "PharmaTech Industries"
            self.pdi_data['model_number'] = "TP-2023X"
            
            # Update info text
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            info_str = f"File Name: {self.pdi_data['file_name']}\n"
            info_str += f"Upload Date: {self.pdi_data['upload_date']}\n"
            info_str += f"Equipment ID: {self.pdi_data['equipment_id']}\n"
            info_str += f"Equipment Type: {self.pdi_data['equipment_type']}\n"
            info_str += f"Manufacturer: {self.pdi_data['manufacturer']}\n"
            info_str += f"Model Number: {self.pdi_data['model_number']}\n"
            self.info_text.insert(tk.END, info_str)
            self.info_text.config(state=tk.DISABLED)
            
            # Generate document content
            self.generate_dq_content()
            self.generate_iq_content()
            self.generate_oq_content()
            
            messagebox.showinfo("Success", "PDI Report uploaded successfully! Data extracted.")
            
    def generate_dq_content(self):
        self.dq_text.config(state=tk.NORMAL)
        self.dq_text.delete(1.0, tk.END)
        
        dq_content = f"DESIGN QUALIFICATION PROTOCOL\n\n"
        dq_content += f"Equipment: {self.pdi_data['equipment_type']}\n"
        dq_content += f"Equipment ID: {self.pdi_data['equipment_id']}\n"
        dq_content += f"Manufacturer: {self.pdi_data['manufacturer']}\n"
        dq_content += f"Model: {self.pdi_data['model_number']}\n\n"
        dq_content += "This Design Qualification (DQ) protocol provides documentary evidence that the design of the equipment meets all predetermined user and regulatory requirements.\n\n"
        dq_content += "1.0 APPROVAL\n"
        dq_content += "Prepared By: ________________________\n"
        dq_content += "Reviewed By: ________________________\n"
        dq_content += "Approved By: ________________________\n\n"
        dq_content += "2.0 INTRODUCTION\n"
        dq_content += "This document outlines the design specifications and requirements for the equipment.\n\n"
        dq_content += "3.0 EQUIPMENT DESCRIPTION\n"
        dq_content += "Detailed description of the equipment and its intended use.\n\n"
        dq_content += "4.0 DESIGN SPECIFICATIONS\n"
        dq_content += "All design specifications are met as per the manufacturer's documentation."
        
        self.dq_text.insert(tk.END, dq_content)
        self.dq_text.config(state=tk.DISABLED)
        
    def generate_iq_content(self):
        self.iq_text.config(state=tk.NORMAL)
        self.iq_text.delete(1.0, tk.END)
        
        iq_content = f"INSTALLATION QUALIFICATION PROTOCOL\n\n"
        iq_content += f"Equipment: {self.pdi_data['equipment_type']}\n"
        iq_content += f"Equipment ID: {self.pdi_data['equipment_id']}\n"
        iq_content += f"Manufacturer: {self.pdi_data['manufacturer']}\n"
        iq_content += f"Model: {self.pdi_data['model_number']}\n\n"
        iq_content += "This Installation Qualification (IQ) protocol provides documentary evidence that the equipment is installed correctly and according to specifications.\n\n"
        iq_content += "1.0 APPROVAL\n"
        iq_content += "Prepared By: ________________________\n"
        iq_content += "Reviewed By: ________________________\n"
        iq_content += "Approved By: ________________________\n\n"
        iq_content += "2.0 INTRODUCTION\n"
        iq_content += "This document verifies that the equipment has been installed correctly.\n\n"
        iq_content += "3.0 INSTALLATION VERIFICATION\n"
        iq_content += "All installation requirements have been verified against the manufacturer's specifications.\n\n"
        iq_content += "4.0 DOCUMENTATION\n"
        iq_content += "All required documentation has been received and reviewed."
        
        self.iq_text.insert(tk.END, iq_content)
        self.iq_text.config(state=tk.DISABLED)
        
    def generate_oq_content(self):
        self.oq_text.config(state=tk.NORMAL)
        self.oq_text.delete(1.0, tk.END)
        
        oq_content = f"OPERATIONAL QUALIFICATION PROTOCOL\n\n"
        oq_content += f"Equipment: {self.pdi_data['equipment_type']}\n"
        oq_content += f"Equipment ID: {self.pdi_data['equipment_id']}\n"
        oq_content += f"Manufacturer: {self.pdi_data['manufacturer']}\n"
        oq_content += f"Model: {self.pdi_data['model_number']}\n\n"
        oq_content += "This Operational Qualification (OQ) protocol provides documentary evidence that the equipment operates as intended in all expected operating ranges.\n\n"
        oq_content += "1.0 APPROVAL\n"
        oq_content += "Prepared By: ________________________\n"
        oq_content += "Reviewed By: ________________________\n"
        oq_content += "Approved By: ________________________\n\n"
        oq_content += "2.0 INTRODUCTION\n"
        oq_content += "This document verifies that the equipment operates according to specifications.\n\n"
        oq_content += "3.0 OPERATIONAL TESTS\n"
        oq_content += "All operational tests have been performed and documented.\n\n"
        oq_content += "4.0 PERFORMANCE VERIFICATION\n"
        oq_content += "The equipment performs within all specified operating parameters."
        
        self.oq_text.insert(tk.END, oq_content)
        self.oq_text.config(state=tk.DISABLED)
        
    def export_documents(self):
        export_format = self.export_format.get()
        folder_path = filedialog.askdirectory(title="Select Export Folder")
        
        if folder_path:
            try:
                if export_format == "HTML":
                    self.export_html(folder_path)
                else:
                    self.export_text(folder_path)
                
                messagebox.showinfo("Success", f"Documents exported successfully to {folder_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export documents: {str(e)}")
                
    def export_html(self, folder_path):
        # Export DQ as HTML
        dq_filename = os.path.join(folder_path, "Design_Qualification.html")
        with open(dq_filename, 'w', encoding='utf-8') as f:
            f.write('<!DOCTYPE html>\n<html>\n<head>\n<title>Design Qualification</title>\n')
            f.write('<style>body { font-family: Arial, sans-serif; margin: 40px; }</style>\n')
            f.write('</head>\n<body>\n')
            f.write('<h1>DESIGN QUALIFICATION PROTOCOL</h1>\n')
            f.write(f'<p><strong>Equipment:</strong> {self.pdi_data["equipment_type"]}</p>\n')
            f.write(f'<p><strong>Equipment ID:</strong> {self.pdi_data["equipment_id"]}</p>\n')
            f.write(f'<p><strong>Manufacturer:</strong> {self.pdi_data["manufacturer"]}</p>\n')
            f.write(f'<p><strong>Model:</strong> {self.pdi_data["model_number"]}</p>\n')
            f.write('<p>This Design Qualification (DQ) protocol provides documentary evidence that the design of the equipment meets all predetermined user and regulatory requirements.</p>\n')
            f.write('<h2>1.0 APPROVAL</h2>\n')
            f.write('<p>Prepared By: ________________________</p>\n')
            f.write('<p>Reviewed By: ________________________</p>\n')
            f.write('<p>Approved By: ________________________</p>\n')
            f.write('<h2>2.0 INTRODUCTION</h2>\n')
            f.write('<p>This document outlines the design specifications and requirements for the equipment.</p>\n')
            f.write('<h2>3.0 EQUIPMENT DESCRIPTION</h2>\n')
            f.write('<p>Detailed description of the equipment and its intended use.</p>\n')
            f.write('<h2>4.0 DESIGN SPECIFICATIONS</h2>\n')
            f.write('<p>All design specifications are met as per the manufacturer\'s documentation.</p>\n')
            f.write('</body>\n</html>')
        
        # Similarly export IQ and OQ
        iq_filename = os.path.join(folder_path, "Installation_Qualification.html")
        with open(iq_filename, 'w', encoding='utf-8') as f:
            f.write('<!DOCTYPE html>\n<html>\n<head>\n<title>Installation Qualification</title>\n')
            f.write('<style>body { font-family: Arial, sans-serif; margin: 40px; }</style>\n')
            f.write('</head>\n<body>\n')
            f.write('<h1>INSTALLATION QUALIFICATION PROTOCOL</h1>\n')
            f.write(f'<p><strong>Equipment:</strong> {self.pdi_data["equipment_type"]}</p>\n')
            f.write(f'<p><strong>Equipment ID:</strong> {self.pdi_data["equipment_id"]}</p>\n')
            f.write(f'<p><strong>Manufacturer:</strong> {self.pdi_data["manufacturer"]}</p>\n')
            f.write(f'<p><strong>Model:</strong> {self.pdi_data["model_number"]}</p>\n')
            f.write('<p>This Installation Qualification (IQ) protocol provides documentary evidence that the equipment is installed correctly and according to specifications.</p>\n')
            f.write('<h2>1.0 APPROVAL</h2>\n')
            f.write('<p>Prepared By: ________________________</p>\n')
            f.write('<p>Reviewed By: ________________________</p>\n')
            f.write('<p>Approved By: ________________________</p>\n')
            f.write('<h2>2.0 INTRODUCTION</h2>\n')
            f.write('<p>This document verifies that the equipment has been installed correctly.</p>\n')
            f.write('<h2>3.0 INSTALLATION VERIFICATION</h2>\n')
            f.write('<p>All installation requirements have been verified against the manufacturer\'s specifications.</p>\n')
            f.write('<h2>4.0 DOCUMENTATION</h2>\n')
            f.write('<p>All required documentation has been received and reviewed.</p>\n')
            f.write('</body>\n</html>')
            
        oq_filename = os.path.join(folder_path, "Operational_Qualification.html")
        with open(oq_filename, 'w', encoding='utf-8') as f:
            f.write('<!DOCTYPE html>\n<html>\n<head>\n<title>Operational Qualification</title>\n')
            f.write('<style>body { font-family: Arial, sans-serif; margin: 40px; }</style>\n')
            f.write('</head>\n<body>\n')
            f.write('<h1>OPERATIONAL QUALIFICATION PROTOCOL</h1>\n')
            f.write(f'<p><strong>Equipment:</strong> {self.pdi_data["equipment_type"]}</p>\n')
            f.write(f'<p><strong>Equipment ID:</strong> {self.pdi_data["equipment_id"]}</p>\n')
            f.write(f'<p><strong>Manufacturer:</strong> {self.pdi_data["manufacturer"]}</p>\n')
            f.write(f'<p><strong>Model:</strong> {self.pdi_data["model_number"]}</p>\n')
            f.write('<p>This Operational Qualification (OQ) protocol provides documentary evidence that the equipment operates as intended in all expected operating ranges.</p>\n')
            f.write('<h2>1.0 APPROVAL</h2>\n')
            f.write('<p>Prepared By: ________________________</p>\n')
            f.write('<p>Reviewed By: ________________________</p>\n')
            f.write('<p>Approved By: ________________________</p>\n')
            f.write('<h2>2.0 INTRODUCTION</h2>\n')
            f.write('<p>This document verifies that the equipment operates according to specifications.</p>\n')
            f.write('<h2>3.0 OPERATIONAL TESTS</h2>\n')
            f.write('<p>All operational tests have been performed and documented.</p>\n')
            f.write('<h2>4.0 PERFORMANCE VERIFICATION</h2>\n')
            f.write('<p>The equipment performs within all specified operating parameters.</p>\n')
            f.write('</body>\n</html>')
    
    def export_text(self, folder_path):
        # Export DQ as text
        dq_filename = os.path.join(folder_path, "Design_Qualification.txt")
        with open(dq_filename, 'w', encoding='utf-8') as f:
            f.write("DESIGN QUALIFICATION PROTOCOL\n\n")
            f.write(f"Equipment: {self.pdi_data['equipment_type']}\n")
            f.write(f"Equipment ID: {self.pdi_data['equipment_id']}\n")
            f.write(f"Manufacturer: {self.pdi_data['manufacturer']}\n")
            f.write(f"Model: {self.pdi_data['model_number']}\n\n")
            f.write("This Design Qualification (DQ) protocol provides documentary evidence that the design of the equipment meets all predetermined user and regulatory requirements.\n\n")
            f.write("1.0 APPROVAL\n")
            f.write("Prepared By: ________________________\n")
            f.write("Reviewed By: ________________________\n")
            f.write("Approved By: ________________________\n\n")
            f.write("2.0 INTRODUCTION\n")
            f.write("This document outlines the design specifications and requirements for the equipment.\n\n")
            f.write("3.0 EQUIPMENT DESCRIPTION\n")
            f.write("Detailed description of the equipment and its intended use.\n\n")
            f.write("4.0 DESIGN SPECIFICATIONS\n")
            f.write("All design specifications are met as per the manufacturer's documentation.\n")
        
        # Similarly export IQ and OQ
        iq_filename = os.path.join(folder_path, "Installation_Qualification.txt")
        with open(iq_filename, 'w', encoding='utf-8') as f:
            f.write("INSTALLATION QUALIFICATION PROTOCOL\n\n")
            f.write(f"Equipment: {self.pdi_data['equipment_type']}\n")
            f.write(f"Equipment ID: {self.pdi_data['equipment_id']}\n")
            f.write(f"Manufacturer: {self.pdi_data['manufacturer']}\n")
            f.write(f"Model: {self.pdi_data['model_number']}\n\n")
            f.write("This Installation Qualification (IQ) protocol provides documentary evidence that the equipment is installed correctly and according to specifications.\n\n")
            f.write("1.0 APPROVAL\n")
            f.write("Prepared By: ________________________\n")
            f.write("Reviewed By: ________________________\n")
            f.write("Approved By: ________________________\n\n")
            f.write("2.0 INTRODUCTION\n")
            f.write("This document verifies that the equipment has been installed correctly.\n\n")
            f.write("3.0 INSTALLATION VERIFICATION\n")
            f.write("All installation requirements have been verified against the manufacturer's specifications.\n\n")
            f.write("4.0 DOCUMENTATION\n")
            f.write("All required documentation has been received and reviewed.\n")
            
        oq_filename = os.path.join(folder_path, "Operational_Qualification.txt")
        with open(oq_filename, 'w', encoding='utf-8') as f:
            f.write("OPERATIONAL QUALIFICATION PROTOCOL\n\n")
            f.write(f"Equipment: {self.pdi_data['equipment_type']}\n")
            f.write(f"Equipment ID: {self.pdi_data['equipment_id']}\n")
            f.write(f"Manufacturer: {self.pdi_data['manufacturer']}\n")
            f.write(f"Model: {self.pdi_data['model_number']}\n\n")
            f.write("This Operational Qualification (OQ) protocol provides documentary evidence that the equipment operates as intended in all expected operating ranges.\n\n")
            f.write("1.0 APPROVAL\n")
            f.write("Prepared By: ________________________\n")
            f.write("Reviewed By: ________________________\n")
            f.write("Approved By: ________________________\n\n")
            f.write("2.0 INTRODUCTION\n")
            f.write("This document verifies that the equipment operates according to specifications.\n\n")
            f.write("3.0 OPERATIONAL TESTS\n")
            f.write("All operational tests have been performed and documented.\n\n")
            f.write("4.0 PERFORMANCE VERIFICATION\n")
            f.write("The equipment performs within all specified operating parameters.\n")

def main():
    root = tk.Tk()
    app = PharmaQualifyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()