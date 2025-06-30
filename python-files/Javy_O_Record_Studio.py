import os
import whisper
import uuid
import datetime
import sqlite3
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from fpdf import FPDF
import qrcode
import pygame

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

DB_NAME = "canciones.db"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Javy O Record Studio")
        self.geometry("1260x700")
        try:
            self.iconbitmap("logo.ico.ico")
        except:
            pass

        self.model = whisper.load_model("base")
        self.audio_path = ""
        self.transcribed_text = ""
        self.identificador_actual = ""
        self.qr_path_actual = ""

        pygame.mixer.init()
        self.create_db()
        self.create_widgets()

    def create_db(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS canciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identificador TEXT,
            titulo TEXT,
            genero TEXT,
            ruta_audio TEXT,
            fecha TEXT
        )
        """)
        conn.commit()
        conn.close()

    def create_widgets(self):
        title_label = ctk.CTkLabel(self, text="Javy O Record Studio", font=("Arial", 24, "bold"))
        title_label.pack(pady=5)

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = ctk.CTkFrame(main_frame, width=300)
        left_frame.pack(side="left", fill="y", padx=5)

        btn_width = 140
        btn_height = 50

        self.titulo_entry = ctk.CTkEntry(left_frame, placeholder_text="Título de la Canción", state="readonly", width=btn_width*1.5)
        self.titulo_entry.pack(pady=5)

        self.genero_entry = ctk.CTkEntry(left_frame, placeholder_text="Género", width=btn_width*1.5)
        self.genero_entry.pack(pady=5)

        self.upload_button = ctk.CTkButton(left_frame, text="Subir Audio", command=self.upload_audio, width=btn_width, height=btn_height)
        self.upload_button.pack(pady=2)

        self.save_btn = ctk.CTkButton(left_frame, text="Guardar", command=self.guardar_registro, width=btn_width, height=btn_height)
        self.save_btn.pack(pady=2)

        self.export_lyrics_btn = ctk.CTkButton(left_frame, text="Letra PDF", command=self.export_lyrics_pdf, width=btn_width, height=btn_height)
        self.export_lyrics_btn.pack(pady=2)

        self.export_cert_btn = ctk.CTkButton(left_frame, text="Certificado PDF", command=self.export_certificate_pdf, width=btn_width, height=btn_height)
        self.export_cert_btn.pack(pady=2)

        self.clean_btn = ctk.CTkButton(left_frame, text="Limpiar", command=self.limpiar_campos, width=btn_width, height=btn_height)
        self.clean_btn.pack(pady=2)

        self.exit_btn = ctk.CTkButton(left_frame, text="Cerrar", command=self.destroy, width=btn_width, height=btn_height)
        self.exit_btn.pack(pady=2)

        center_frame = ctk.CTkFrame(main_frame)
        center_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.textbox = ctk.CTkTextbox(center_frame, font=("Segoe UI", 14))
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)

        controls_frame = ctk.CTkFrame(center_frame)
        controls_frame.pack(pady=5)

        self.play_btn = ctk.CTkButton(controls_frame, text="Play", command=self.play_audio, state="disabled", width=100)
        self.play_btn.pack(side="left", padx=5)

        self.pause_btn = ctk.CTkButton(controls_frame, text="Pause", command=self.pause_audio, state="disabled", width=100)
        self.pause_btn.pack(side="left", padx=5)

        self.stop_btn = ctk.CTkButton(controls_frame, text="Stop", command=self.stop_audio, state="disabled", width=100)
        self.stop_btn.pack(side="left", padx=5)

        right_frame = ctk.CTkFrame(main_frame, width=200)
        right_frame.pack(side="right", fill="y", padx=5)

        generos = [
            "Rancheras", "Baladas", "Cumbias", "Salsa", "Rock and Roll",
            "Orquestales", "Boleros", "Cristianas", "Pop", "Modernas"
        ]

        for genero in generos:
            btn = ctk.CTkButton(right_frame, text=genero, width=btn_width, height=btn_height,
                                command=lambda g=genero: self.mostrar_genero(g))
            btn.pack(pady=2)

    def upload_audio(self):
        path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if path:
            self.audio_path = path
            base_title = os.path.splitext(os.path.basename(self.audio_path))[0].title()
            self.titulo_entry.configure(state="normal")
            self.titulo_entry.delete(0, tk.END)
            self.titulo_entry.insert(0, base_title)
            self.titulo_entry.configure(state="readonly")

            pygame.mixer.music.load(self.audio_path)
            self.play_btn.configure(state="normal")
            self.pause_btn.configure(state="normal")
            self.stop_btn.configure(state="normal")

            self.transcribe_audio()

    def play_audio(self):
        pygame.mixer.music.play()

    def pause_audio(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    def stop_audio(self):
        pygame.mixer.music.stop()

    def transcribe_audio(self):
        self.textbox.delete("1.0", tk.END)
        self.textbox.insert(tk.END, "Transcribiendo... por favor espera...")
        self.update()
        result = self.model.transcribe(self.audio_path)
        self.transcribed_text = result["text"].strip()
        self.textbox.delete("1.0", tk.END)
        self.textbox.insert(tk.END, self.transcribed_text)

    def generar_identificador(self):
        return f"JORS-{str(uuid.uuid4())[:5].upper()}"

    def generar_qr(self, titulo, today):
        qr_data = f"ID: {self.identificador_actual}\nTítulo: {titulo}\nAutor: Ricardo Javier Ortega Aguilar\nFecha: {today}"
        qr = qrcode.make(qr_data)
        qr_path = f"qr_{self.identificador_actual}.png"
        qr.save(qr_path)
        self.qr_path_actual = qr_path

    def guardar_registro(self):
        titulo = self.titulo_entry.get().strip()
        genero = self.genero_entry.get().strip()
        today = datetime.date.today().strftime("%d/%m/%Y")

        if not titulo or not genero:
            messagebox.showwarning("Faltan Datos", "Debes tener título y género para guardar.")
            return

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id FROM canciones WHERE titulo = ?", (titulo,))
        if c.fetchone():
            respuesta = messagebox.askyesno("Título Registrado", f"El título '{titulo}' ya está registrado.\n¿Desea guardar este título nuevamente?")
            if not respuesta:
                conn.close()
                self.limpiar_campos()
                return

        self.identificador_actual = self.generar_identificador()
        self.generar_qr(titulo, today)

        c.execute("INSERT INTO canciones (identificador, titulo, genero, ruta_audio, fecha) VALUES (?, ?, ?, ?, ?)",
                  (self.identificador_actual, titulo, genero, self.audio_path, today))
        conn.commit()
        conn.close()
        messagebox.showinfo("Guardado", f"Registro de {titulo} guardado correctamente con ID {self.identificador_actual}.")

    def mostrar_genero(self, genero):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT titulo, identificador FROM canciones WHERE genero LIKE ?", (f"%{genero}%",))
        resultados = c.fetchall()
        conn.close()

        if resultados:
            info = "\n\n".join([f"Título: {t}\nIdentificador: {i}" for t, i in resultados])
            messagebox.showinfo(f"Canciones de {genero}", info)
        else:
            messagebox.showinfo("Sin resultados", f"No hay canciones registradas en {genero}.")

    def export_lyrics_pdf(self):
        titulo = self.titulo_entry.get().strip()
        genero = self.genero_entry.get().strip()
        text = self.textbox.get("1.0", tk.END).strip()
        today = datetime.date.today().strftime("%d/%m/%Y")

        if not titulo or not genero or not self.identificador_actual:
            messagebox.showwarning("Faltan Datos", "Debes tener título, género y guardar el registro antes de exportar.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not filepath:
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"{titulo}", ln=True, align="C")
        pdf.set_font("Arial", '', 12)
        pdf.ln(10)

        for line in text.split(". "):
            pdf.multi_cell(0, 10, line.strip() + ".")
            pdf.ln(2)

        pdf.ln(10)
        pdf.cell(0, 10, f"Género: {genero}", ln=True)
        pdf.cell(0, 10, f"Identificador: {self.identificador_actual}", ln=True)
        pdf.cell(0, 10, f"Fecha: {today}", ln=True)
        pdf.cell(0, 10, "Autor: Ricardo Javier Ortega Aguilar", ln=True)

        if self.qr_path_actual and os.path.exists(self.qr_path_actual):
            pdf.image(self.qr_path_actual, x=80, w=50)

        try:
            pdf.output(filepath)
            messagebox.showinfo("PDF", "Letra exportada correctamente.")
        except PermissionError:
            messagebox.showerror("Error", "No se pudo guardar el archivo. Verifica que no esté abierto o elige otra ubicación.")

    def export_certificate_pdf(self):
        titulo = self.titulo_entry.get().strip()
        today = datetime.date.today().strftime("%d/%m/%Y")

        if not titulo or not self.identificador_actual:
            messagebox.showwarning("Faltan Datos", "Debes tener título y guardar el registro antes de exportar el certificado.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not filepath:
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Javy O Record Studio", ln=True, align="C")
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, "Andador 68-410 México D.F.", ln=True, align="C")
        pdf.cell(0, 10, "(52)-98-44-79-7431", ln=True, align="C")
        pdf.cell(0, 10, "rickoortega@gmail.com", ln=True, align="C")
        pdf.ln(10)

        pdf.cell(0, 10, "CERTIFICADO DIGITAL DE AUTORÍA", ln=True, align="C")
        pdf.ln(10)

        pdf.cell(0, 10, f"Nombre de la Obra: {titulo}", ln=True)
        pdf.cell(0, 10, "Autor/Compositor: Ricardo Javier Ortega Aguilar", ln=True)
        pdf.cell(0, 10, "Productor: Javy O Record Studio", ln=True)
        pdf.cell(0, 10, f"Identificador único: {self.identificador_actual}", ln=True)
        pdf.cell(0, 10, f"Fecha de Creación: {today}", ln=True)
        pdf.cell(0, 10, f"Fecha de Fijación en Medio Tangible: {today}", ln=True)
        pdf.ln(5)

        pdf.multi_cell(0, 10,
            "Declaración de Derechos de Autor\n"
            "De acuerdo con el Convenio de Berna para la Protección de las Obras Literarias y Artísticas, "
            "la obra mencionada anteriormente está protegida por derechos de autor desde el momento de su "
            "creación y fijación en un medio tangible. Esta protección es automática y no requiere registro "
            "formal en los países miembros del Convenio.\n\n"
            "El titular de los derechos de autor es el autor o compositor de la obra, y Javy O Record Studio "
            "actúa como productor y colaborador en la fijación y distribución de la misma.\n\n"
            "Derechos Reservados\n"
            "Todos los derechos de autor están reservados. Queda prohibida la reproducción, distribución, "
            "comunicación pública o transformación de esta obra sin la autorización expresa del titular de los derechos.\n\n"
            "Referencia al Convenio de Berna\n"
            "Este certificado se emite en cumplimiento con los principios establecidos en el Convenio de Berna, "
            "adoptado el 9 de septiembre de 1886 y revisado en varias ocasiones, que garantiza la protección "
            "de los derechos de autor en los más de 180 países miembros.\n\n"
            "Sello Discográfico: Javy O Record Studio\n"
            f"Fecha: {today}\n\n"
            "Esta prueba digital de autoría es válida de manera ilimitada hasta 70 años después de la muerte "
            "del compositor o de los compositores.\n\n"
            "TODOS LOS DERECHOS RESERVADOS"
        )

        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Información de la Publicación", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Título de la Obra: {titulo}", ln=True)
        pdf.cell(0, 10, "Registro de: 1 Canción", ln=True)
        pdf.cell(0, 10, f"Identificador único: {self.identificador_actual}", ln=True)
        pdf.cell(0, 10, f"Fecha de publicación: {today}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, "Nombre del registrante: Ricardo Javier Ortega Aguilar", ln=True)
        pdf.cell(0, 10, "E-mail del registrante: rickoortega@gmail.com", ln=True)
        pdf.cell(0, 10, "_" * 60, ln=True)
        pdf.cell(0, 10, "Tipo de registro: Letra y Música", ln=True)
        pdf.cell(0, 10, "Autor/es de la letra: Ricardo Javier Ortega Aguilar", ln=True)
        pdf.cell(0, 10, "Autor/es de la música: Ricardo Javier Ortega Aguilar", ln=True)

        if self.qr_path_actual and os.path.exists(self.qr_path_actual):
            pdf.image(self.qr_path_actual, x=80, w=50)

        try:
            pdf.output(filepath)
            messagebox.showinfo("PDF", "Certificado exportado correctamente.")
        except PermissionError:
            messagebox.showerror("Error", "No se pudo guardar el archivo. Verifica que no esté abierto o elige otra ubicación.")

    def limpiar_campos(self):
        self.titulo_entry.configure(state="normal")
        self.titulo_entry.delete(0, tk.END)
        self.titulo_entry.configure(state="readonly")
        self.genero_entry.delete(0, tk.END)
        self.textbox.delete("1.0", tk.END)
        self.audio_path = ""
        self.transcribed_text = ""
        self.identificador_actual = ""
        self.qr_path_actual = ""
        self.play_btn.configure(state="disabled")
        self.pause_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        messagebox.showinfo("Limpiar", "Campos limpiados, puedes empezar de nuevo.")

if __name__ == '__main__':
    app = App()
    app.mainloop()
