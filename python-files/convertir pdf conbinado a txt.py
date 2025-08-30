# %%
import requests
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
import pandas as pd
from datetime import datetime, timedelta
import os
import re
import threading
from urllib.parse import urljoin
import pdfplumber
from io import BytesIO
import warnings
from bs4 import BeautifulSoup
from PyPDF2 import PdfMerger

warnings.filterwarnings("ignore")

class LabPDFDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = ""
        self.downloaded_data = []
        self.patients_list = []
        self.pdf_files = []  # Lista de PDFs descargados
        self.setup_gui()
    
    # ------------------- Configuración GUI -------------------
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Descargador de PDFs de Laboratorio")
        self.root.geometry("900x650")
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuración conexión
        conn_frame = ttk.LabelFrame(main_frame, text="Configuración de Conexión", padding="5")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(conn_frame, text="URL Base:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(conn_frame, width=50)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.url_entry.insert(0, "http://52.168.89.164:8081")
        
        ttk.Label(conn_frame, text="Usuario:").grid(row=1, column=0, sticky=tk.W)
        self.user_entry = ttk.Entry(conn_frame, width=30)
        self.user_entry.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.user_entry.insert(0, "HVCMLAB")
        
        ttk.Label(conn_frame, text="Contraseña:").grid(row=2, column=0, sticky=tk.W)
        self.pass_entry = ttk.Entry(conn_frame, show="*", width=30)
        self.pass_entry.grid(row=2, column=1, sticky=tk.W, padx=5)
        self.pass_entry.insert(0, "Hvcm2024+")
        
        self.connect_btn = ttk.Button(conn_frame, text="Conectar", command=self.connect)
        self.connect_btn.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.auto_connect_btn = ttk.Button(conn_frame, text="Auto-Conectar", command=self.auto_connect)
        self.auto_connect_btn.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Filtros de búsqueda
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros de Búsqueda", padding="5")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(filter_frame, text="Fecha Inicio:").grid(row=0, column=0, sticky=tk.W)
        self.fecha_inicio = DateEntry(filter_frame, width=12, background='darkblue', foreground='white',
                                     borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_inicio.grid(row=0, column=1, padx=5)
        self.fecha_inicio.set_date(datetime.now() - timedelta(days=30))
        
        ttk.Label(filter_frame, text="Fecha Fin:").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.fecha_fin = DateEntry(filter_frame, width=12, background='darkblue', foreground='white',
                                   borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_fin.grid(row=0, column=3, padx=5)
        self.fecha_fin.set_date(datetime.now())
        
        ttk.Label(filter_frame, text="Apellidos:").grid(row=1, column=0, sticky=tk.W)
        self.apellidos_entry = ttk.Entry(filter_frame, width=20)
        self.apellidos_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Nombres:").grid(row=1, column=2, sticky=tk.W, padx=(20,0))
        self.nombres_entry = ttk.Entry(filter_frame, width=20)
        self.nombres_entry.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="H. Clínica:").grid(row=2, column=0, sticky=tk.W)
        self.hclinica_entry = ttk.Entry(filter_frame, width=15)
        self.hclinica_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Nro. Orden:").grid(row=2, column=2, sticky=tk.W, padx=(20,0))
        self.nro_orden_entry = ttk.Entry(filter_frame, width=15)
        self.nro_orden_entry.grid(row=2, column=3, padx=5, pady=5)
        
        # Botones principales
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.search_btn = ttk.Button(btn_frame, text="Buscar Pacientes", command=self.search_patients, state="disabled")
        self.search_btn.pack(side=tk.LEFT, padx=5)
        self.download_btn = ttk.Button(btn_frame, text="Descargar PDFs", command=self.download_pdfs, state="disabled")
        self.download_btn.pack(side=tk.LEFT, padx=5)
        self.combine_btn = ttk.Button(btn_frame, text="Combinar PDFs", command=self.combine_pdfs, state="disabled")
        self.combine_btn.pack(side=tk.LEFT, padx=5)
        self.pdf2txt_btn = ttk.Button(btn_frame, text="PDF → TXT", command=self.pdf_to_txt)
        self.pdf2txt_btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="5")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.tree = ttk.Treeview(results_frame, columns=('apellidos', 'nombres', 'fecha_nac', 'hclinica'), show='headings')
        self.tree.heading('apellidos', text='Apellidos')
        self.tree.heading('nombres', text='Nombres')
        self.tree.heading('fecha_nac', text='Fecha Nacimiento')
        self.tree.heading('hclinica', text='H. Clínica')
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="Log de Actividades", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.log_text = tk.Text(log_frame, height=8, state='disabled')
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    # ------------------- Funciones de Log y CSRF -------------------
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        self.root.update()
    
    def get_csrf_token(self, html_text):
        match = re.search(r'name="__RequestVerificationToken".*?value="(.+?)"', html_text, re.DOTALL)
        return match.group(1) if match else None
    
    # ------------------- Conexión -------------------
    def connect(self):
        def task():
            try:
                self.connect_btn.config(state="disabled")
                self.base_url = self.url_entry.get().rstrip('/')
                login_url = f"{self.base_url}/Account/Login"
                resp = self.session.get(login_url)
                if resp.status_code != 200:
                    raise Exception(f"No se pudo conectar al servidor, status: {resp.status_code}")
                
                csrf_token = self.get_csrf_token(resp.text)
                login_data = {'UserName': self.user_entry.get(), 'Password': self.pass_entry.get()}
                if csrf_token:
                    login_data['__RequestVerificationToken'] = csrf_token
                
                post_resp = self.session.post(login_url, data=login_data, headers={'Referer': login_url})
                if post_resp.status_code == 200 and any(x in post_resp.text for x in ["Logout", "Cerrar Sesión", "Bienvenido"]):
                    self.log("Login exitoso ✅")
                    self.root.after(0, lambda: self.search_btn.config(state="normal"))
                    self.root.after(0, lambda: self.connect_btn.config(text="Conectado", state="disabled"))
                else:
                    raise Exception("Login fallido")
            except Exception as e:
                self.log(f"Error de conexión: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error de conexión: {str(e)}"))
                self.root.after(0, lambda: self.connect_btn.config(state="normal"))
        threading.Thread(target=task, daemon=True).start()
    
    def auto_connect(self):
        self.log("Auto-conectando con configuración por defecto...")
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, "http://52.168.89.164:8081")
        self.user_entry.delete(0, tk.END)
        self.user_entry.insert(0, "HVCMLAB")
        self.pass_entry.delete(0, tk.END)
        self.pass_entry.insert(0, "Hvcm2024+")
        self.connect()
    
    # ------------------- Búsqueda de Pacientes -------------------
    def search_patients(self):
        def task():
            try:
                self.search_btn.config(state="disabled")
                self.log("Buscando pacientes...")
                params = {
                    'nombres': self.nombres_entry.get(),
                    'apellidos': self.apellidos_entry.get(),
                    'finicio': self.fecha_inicio.get(),
                    'ffin': self.fecha_fin.get(),
                    'hcl': self.hclinica_entry.get(),
                    'nord': self.nro_orden_entry.get(),
                    'page': 1,
                    'pageSize': 50
                }
                self.patients_list.clear()
                while True:
                    resp = self.session.get(f"{self.base_url}/Priv/Pacientes", params=params)
                    if resp.status_code != 200:
                        self.log(f"Error en página {params['page']}: {resp.status_code}")
                        break
                    data_json = resp.json()
                    html = data_json.get("Html", "")
                    has_items = data_json.get("HasItems", False)
                    if not has_items:
                        self.log(f"No hay más pacientes en página {params['page']}")
                        break
                    soup = BeautifulSoup(html, "html.parser")
                    rows = soup.find_all("tr", class_="grid-row")
                    for tr in rows:
                        tds = tr.find_all("td")
                        if len(tds) >= 4:
                            patient = {
                                "PA_ID": tds[0].get_text(strip=True),
                                "LastName": tds[1].get_text(strip=True),
                                "FirstName": tds[2].get_text(strip=True),
                                "BirthDate": tds[3].get_text(strip=True)
                            }
                            self.patients_list.append(patient)
                    self.log(f"Página {params['page']} procesada, pacientes encontrados: {len(rows)}")
                    params['page'] += 1
                self.populate_patients(self.patients_list)
                self.root.after(0, lambda: self.download_btn.config(state="normal"))
                self.log(f"Total pacientes encontrados: {len(self.patients_list)}")
            except Exception as e:
                self.log(f"Error en búsqueda: {str(e)}")
            finally:
                self.root.after(0, lambda: self.search_btn.config(state="normal"))
        threading.Thread(target=task, daemon=True).start()
    
    def populate_patients(self, patients):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for patient in patients:
            self.tree.insert('', 'end', values=(
                patient.get('LastName',''),
                patient.get('FirstName',''),
                patient.get('BirthDate',''),
                patient.get('PA_ID','')
            ))
    
    # ------------------- Descarga de PDFs -------------------
    def download_pdfs(self):
        def task():
            try:
                self.download_btn.config(state="disabled")
                folder = filedialog.askdirectory(title="Seleccionar carpeta para guardar PDFs")
                if not folder:
                    self.log("Descarga cancelada por usuario")
                    self.root.after(0, lambda: self.download_btn.config(state="normal"))
                    return
                self.log("Iniciando descarga de PDFs...")
                
                total_downloaded = 0
                self.downloaded_data.clear()
                self.pdf_files.clear()
                for patient in self.patients_list:
                    self.log(f"Procesando paciente: {patient['PA_ID']} - {patient['LastName']} {patient['FirstName']}")
                    patient_folder = os.path.join(folder, f"{patient['PA_ID']}_{patient['LastName']}")
                    os.makedirs(patient_folder, exist_ok=True)
                    
                    page = 1
                    while True:
                        resp = self.session.get(f"{self.base_url}/Priv/Ordenes", params={'patiendid': patient['PA_ID'], 'page': page, 'pageSize': 50})
                        if resp.status_code != 200:
                            break
                        data_json = resp.json()
                        html = data_json.get("Html", "")
                        soup = BeautifulSoup(html, "html.parser")
                        rows = soup.find_all("tr", class_="grid-row")
                        if not rows:
                            if page == 1:
                                self.log(f"Órdenes encontradas en página {page}: 0")
                            break
                        self.log(f"Órdenes encontradas en página {page}: {len(rows)}")
                        for tr in rows:
                            tds = tr.find_all("td")
                            if len(tds) >= 3:
                                sample_id = tds[0].get_text(strip=True)
                                register_date = tds[1].get_text(strip=True)
                                service = tds[2].get_text(strip=True)
                                pdf_url = f"{self.base_url}/Priv/Report?SID={sample_id}&RDT={register_date}"
                                r = self.session.get(pdf_url)
                                if r.status_code == 200:
                                    filename = f"{sample_id}.pdf"
                                    filepath = os.path.join(patient_folder, filename)
                                    with open(filepath, 'wb') as f:
                                        f.write(r.content)
                                    total_downloaded += 1
                                    self.pdf_files.append(filepath)  # Guardamos el PDF descargado
                        page += 1
                self.log(f"Descarga finalizada. Total PDFs: {total_downloaded}")
                if self.pdf_files:
                    self.root.after(0, lambda: self.combine_btn.config(state="normal"))
            except Exception as e:
                self.log(f"Error en descarga: {str(e)}")
            finally:
                self.root.after(0, lambda: self.download_btn.config(state="normal"))
        threading.Thread(target=task, daemon=True).start()
    
    # ------------------- Combinar PDFs -------------------
    def combine_pdfs(self):
        if not self.pdf_files:
            messagebox.showwarning("Advertencia", "No hay PDFs descargados para combinar")
            return
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar PDF combinado"
        )
        if not save_path:
            return
        try:
            merger = PdfMerger()
            for pdf_file in self.pdf_files:
                merger.append(pdf_file)
            merger.write(save_path)
            merger.close()
            self.log(f"PDF combinado guardado en: {save_path}")
            messagebox.showinfo("Éxito", f"PDF combinado guardado en:\n{save_path}")
        except Exception as e:
            self.log(f"Error al combinar PDFs: {str(e)}")
            messagebox.showerror("Error", f"No se pudo combinar PDFs: {str(e)}")
    
    # ------------------- Convertir PDF a TXT -------------------
    def pdf_to_txt(self):
        pdf_path = filedialog.askopenfilename(
            title="Seleccionar PDF a convertir",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not pdf_path:
            return
        txt_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Guardar archivo TXT"
        )
        if not txt_path:
            return
        try:
            self.log(f"Extrayendo texto de {os.path.basename(pdf_path)}...")
            full_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            self.log(f"Archivo TXT guardado en: {txt_path}")
            messagebox.showinfo("Éxito", f"Archivo TXT guardado en:\n{txt_path}")
        except Exception as e:
            self.log(f"Error al convertir PDF a TXT: {str(e)}")
            messagebox.showerror("Error", f"No se pudo convertir PDF a TXT: {str(e)}")
    
    # ------------------- Ejecutar GUI -------------------
    def run(self):
        self.root.mainloop()

# Ejecutar la aplicación
if __name__ == "__main__":
    app = LabPDFDownloader()
    app.run()
