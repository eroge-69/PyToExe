# -*- coding: utf-8 -*-
"""
Procesador de facturas Amex

Este código proporciona una sencilla interfaz gráfica para el script desarrollado como Amextron 
disponible en : 
https://drive.google.com/file/d/1vcxJZntbQDFeMNvzsRgWX8bchwKHQtSV/view?usp=drive_link

Se permite: 
1. Proporcionar un nombre y un mes. 
2. Seleccionar una carpeta comprimida en formato .zip que contiene las facturas en formato pdf y xml
3. Se procesan ambos formatos siguiendo las instrucciones del script Amextron: extrae datos de los archivos XML, renombra los pdf  según su UUID (en caso de 
encontrar una coincidencia con esa frase) y se genera un reporte en Excel. 
4. Guarda el archivo Excel generado, los archivos XML originales y los pdf renombrados. Ignora cualquier otro archivo contenido en la carpeta original comprimida
en formato .zip

Posee cualquier limitación derivada del script original Amextron. Las limitaciones de la interfaz no incluye algunos casos de uso extravagantes y el manejo
de excepciones y errores es nulo.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import pdfplumber
import shutil
import threading
from pathlib import Path

class App:
    """
    La aplicacion principal que maneja y administra la GUI
    """
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Procesador de facturas Amex")
        self.root.geometry("600x550")
        self.root.configure(bg="#f0f0f0")

        self.zip_path = None

        # --- Main Frame ---
        main_frame = tk.Frame(self.root, padx=15, pady=15, bg="#f0f0f0")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Input Fields ---
        fields_frame = tk.LabelFrame(main_frame, text="Datos de Entrada", padx=10, pady=10, bg="#f0f0f0", font=("Helvetica", 12))
        fields_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(fields_frame, text="Nombre:", bg="#f0f0f0", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.personaje_entry = tk.Entry(fields_frame, width=40, font=("Helvetica", 10))
        self.personaje_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        tk.Label(fields_frame, text="Mes:", bg="#f0f0f0", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.mes_entry = tk.Entry(fields_frame, width=40, font=("Helvetica", 10))
        self.mes_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        
        fields_frame.grid_columnconfigure(1, weight=1)

        # --- File Selection ---
        file_frame = tk.Frame(main_frame, bg="#f0f0f0")
        file_frame.pack(fill=tk.X, pady=10)

        self.select_button = tk.Button(file_frame, text="1. Seleccionar Archivo .ZIP", command=self.select_zip, font=("Helvetica", 10, "bold"), bg="#007bff", fg="white", relief=tk.FLAT, padx=10)
        self.select_button.pack(side=tk.LEFT)

        self.file_label = tk.Label(file_frame, text="Ningún archivo seleccionado", bg="#e9ecef", fg="#495057", padx=10, anchor="w")
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # --- Process Button ---
        self.process_button = tk.Button(main_frame, text="2. Iniciar Procesamiento", command=self.start_processing_thread, font=("Helvetica", 12, "bold"), bg="#28a745", fg="white", relief=tk.FLAT, state=tk.DISABLED, pady=5)
        self.process_button.pack(fill=tk.X, pady=10)

        # --- Status Log ---
        log_frame = tk.LabelFrame(main_frame, text="Registro de Actividad", padx=10, pady=10, bg="#f0f0f0", font=("Helvetica", 12))
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.status_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled', font=("Courier New", 9))
        self.status_log.pack(fill=tk.BOTH, expand=True)

    def update_status(self, message):
        """Appends a message to the status log on the GUI."""
        self.status_log.config(state='normal')
        self.status_log.insert(tk.END, message + "\n")
        self.status_log.config(state='disabled')
        self.status_log.see(tk.END)
        self.root.update_idletasks()

    def select_zip(self):
        """Opens a file dialog to select a zip file."""
        path = filedialog.askopenfilename(
            title="Seleccione el archivo ZIP con las facturas",
            filetypes=[("Zip files", "*.zip")]
        )
        if path:
            self.zip_path = path
            self.file_label.config(text=os.path.basename(path))
            self.update_status(f"Archivo seleccionado: {path}")
            self.process_button.config(state=tk.NORMAL) # Enable process button
        else:
            self.file_label.config(text="Ningún archivo seleccionado")
            self.process_button.config(state=tk.DISABLED)

    def start_processing_thread(self):
        """
        Validates inputs and starts the file processing in a separate thread
        to keep the GUI responsive.
        """
        personaje = self.personaje_entry.get().strip().upper()
        mes = self.mes_entry.get().strip().upper()

        if not personaje or not mes:
            messagebox.showerror("Error de Entrada", "Los campos '´Persona' y 'Mes' no pueden estar vacíos.")
            return
        
        if not self.zip_path:
            messagebox.showerror("Error de Entrada", "Por favor, seleccione un archivo ZIP para procesar.")
            return

        # Disable buttons to prevent multiple runs
        self.process_button.config(state=tk.DISABLED)
        self.select_button.config(state=tk.DISABLED)

        # Run the main logic in a new thread
        processing_thread = threading.Thread(
            target=self.process_files,
            args=(personaje, mes, self.zip_path)
        )
        processing_thread.start()

    def process_files(self, personaje, mes, zip_path):
        """
        The core logic for processing the files. This function is run in a
        separate thread.
        """
        temp_dir = None
        try:
            # Create a temporary directory for processing
            temp_dir = Path(f"./temp_{personaje}_{mes}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir) # Clean up old temp dir if it exists
            temp_dir.mkdir()
            self.update_status(f"Directorio temporal creado en: {temp_dir.resolve()}")

            # Extract the zip file
            extract_path = temp_dir / personaje
            self.update_status(f"Extrayendo '{Path(zip_path).name}' a {extract_path}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            self.update_status("✅ Extracción completada.")

            # Initialize DataFrame
            df = pd.DataFrame(columns=['UUID', "RFC del emisor", 'Subtotal', 'IVA', 'Total', "Tipo", "Nombre"])
            
            # Process XML files
            self.update_status("Procesando archivos XML...")
            nombrederaices = {
                'cfdi': 'http://www.sat.gob.mx/cfd/4',
                'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
            }
            
            all_files = list(os.walk(extract_path))
            for dirpath, _, filenames in all_files:
                for item in filenames:
                    if item.lower().endswith(".xml"):
                        xml_path = Path(dirpath) / item
                        try:
                            tree = ET.parse(xml_path)
                            root = tree.getroot()
                            
                            complemento = root.find('.//tfd:TimbreFiscalDigital', nombrederaices)
                            if complemento is None:
                                self.update_status(f"  - Advertencia: No se encontró TimbreFiscalDigital en {item}")
                                continue
                            
                            uuid = complemento.get("UUID")
                            emisor = root.find('cfdi:Emisor', nombrederaices)
                            
                            impuestos = root.find('cfdi:Impuestos', nombrederaices)
                            iva = "0"
                            if impuestos is not None and impuestos.get('TotalImpuestosTrasladados'):
                                iva = impuestos.get('TotalImpuestosTrasladados')
                            
                            new_row = pd.Series({
                                "UUID": uuid,
                                "Total": root.get("Total"),
                                "RFC del emisor": emisor.get("Nombre") if emisor is not None else "N/A",
                                'Subtotal': root.get('SubTotal'),
                                'IVA': iva,
                                "Tipo": root.get('TipoDeComprobante'),
                                "Nombre": item
                            })
                            df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
                            
                            # Rename XML file
                            os.rename(xml_path, xml_path.parent / f"{uuid}.xml")

                        except ET.ParseError:
                            self.update_status(f"  - Error: No se pudo parsear el XML {item}. Omitiendo.")
                        except Exception as e:
                            self.update_status(f"  - Error procesando {item}: {e}")

            self.update_status(f"✅ {len(df)} facturas XML procesadas.")

            # Convert columns to correct types
            for col in ['Subtotal', 'IVA', 'Total']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # Process and rename PDF files
            self.update_status("Renombrando archivos PDF según UUID...")
            for dirpath, _, filenames in all_files:
                for archivo in filenames:
                    if archivo.lower().endswith('.pdf'):
                        pdf_path = Path(dirpath) / archivo
                        renamed = False
                        try:
                            with pdfplumber.open(pdf_path) as pdf:
                                for uuid_to_find in df['UUID'].tolist():
                                    for page in pdf.pages:
                                        text = page.extract_text()
                                        if text and uuid_to_find in text:
                                            new_name = pdf_path.parent / f"{uuid_to_find}.pdf"
                                            os.rename(pdf_path, new_name)
                                            self.update_status(f"  - Renombrado: {archivo} -> {new_name.name}")
                                            renamed = True
                                            break
                                    if renamed:
                                        break
                        except Exception as e:
                            self.update_status(f"  - Error procesando PDF {archivo}: {e}")
            self.update_status("✅ Procesamiento de PDF completado.")

            # Create Excel file
            excel_name = f"{mes}_{personaje}.xlsx"
            excel_path = temp_dir / excel_name
            self.update_status(f"Creando archivo Excel: {excel_name}...")
            df.to_excel(excel_path, index=False)
            self.update_status("✅ Archivo Excel creado.")

            # Ask user where to save the final zip file
            output_zip_name = f"PROCESADO_{personaje}_{mes}.zip"
            save_path = filedialog.asksaveasfilename(
                defaultextension=".zip",
                initialfile=output_zip_name,
                filetypes=[("Zip files", "*.zip")],
                title="Guardar archivo Zip procesado"
            )

            if not save_path:
                self.update_status("Operación cancelada por el usuario.")
                return

            # Create final zip file
            self.update_status(f"Creando archivo ZIP final en: {save_path}")
            with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add processed files from the extraction folder
                for root_dir, _, files_in_dir in os.walk(extract_path):
                    for file in files_in_dir:
                        file_path = Path(root_dir) / file
                        arcname = file_path.relative_to(extract_path)
                        zipf.write(file_path, arcname=arcname)
                # Add the excel file to the root of the zip
                zipf.write(excel_path, arcname=excel_name)
            
            self.update_status("--------------------------------------------------")
            self.update_status(" PROCESO COMPLETADO CON ÉXITO ")
            self.update_status(f"Archivo final guardado en: {save_path}")
            messagebox.showinfo("Éxito", f"Proceso completado.\nEl archivo ha sido guardado en:\n{save_path}")

        except Exception as e:
            error_message = f"ERROR INESPERADO: {e}"
            self.update_status(error_message)
            messagebox.showerror("Error Crítico", f"Ocurrió un error durante el proceso:\n{e}")
        finally:
            # Clean up temporary directory
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir)
                self.update_status(f"Directorio temporal '{temp_dir.name}' eliminado.")
            # Re-enable buttons
            self.process_button.config(state=tk.NORMAL)
            self.select_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
