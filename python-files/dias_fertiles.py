# ... existing code ...
# Importaciones necesarias
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from fpdf import FPDF
import os

# Cargar fuentes personalizadas si están disponibles
def cargar_fuentes():
    try:
        import tkinter.font as tkFont
        tkFont.Font(family="League Spartan")
        tkFont.Font(family="Montserrat")
    except:
        pass  # Si no están, usar fuentes por defecto

# Colores
ROSA = "#FF69B4"
BLANCO = "#FFFFFF"
NEGRO = "#000000"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora de Días Fértiles")
        self.configure(bg=BLANCO)
        self.geometry("420x600")
        self.resizable(False, False)
        cargar_fuentes()
        self.crear_widgets()

    def crear_widgets(self):
        # Título
        self.titulo = tk.Label(self, text="Calculadora de Días Fértiles", bg=BLANCO, fg=ROSA, font=("League Spartan", 20, "bold"))
        self.titulo.pack(pady=(20, 10))

        # Formulario
        self.form_frame = tk.Frame(self, bg=BLANCO)
        self.form_frame.pack(pady=10)

        # Nombre
        self.nombre_label = tk.Label(self.form_frame, text="Nombre del paciente:", bg=BLANCO, fg=NEGRO, font=("Montserrat", 11))
        self.nombre_label.grid(row=0, column=0, sticky="w", pady=5)
        self.nombre_entry = tk.Entry(self.form_frame, font=("Montserrat", 11), width=25)
        self.nombre_entry.grid(row=0, column=1, pady=5)

        # Fecha de llenado
        self.fecha_label = tk.Label(self.form_frame, text="Fecha de llenado:", bg=BLANCO, fg=NEGRO, font=("Montserrat", 11))
        self.fecha_label.grid(row=1, column=0, sticky="w", pady=5)
        self.fecha_entry = DateEntry(self.form_frame, date_pattern='dd/mm/yyyy', font=("Montserrat", 11))
        self.fecha_entry.grid(row=1, column=1, pady=5)

        # Fecha de inicio del último periodo
        self.periodo_label = tk.Label(self.form_frame, text="Inicio del último periodo:", bg=BLANCO, fg=NEGRO, font=("Montserrat", 11))
        self.periodo_label.grid(row=2, column=0, sticky="w", pady=5)
        self.periodo_entry = DateEntry(self.form_frame, date_pattern='dd/mm/yyyy', font=("Montserrat", 11))
        self.periodo_entry.grid(row=2, column=1, pady=5)

        # Duración del ciclo
        self.ciclo_label = tk.Label(self.form_frame, text="Duración del ciclo (días):", bg=BLANCO, fg=NEGRO, font=("Montserrat", 11))
        self.ciclo_label.grid(row=3, column=0, sticky="w", pady=5)
        self.ciclo_spin = tk.Spinbox(self.form_frame, from_=21, to=35, font=("Montserrat", 11), width=5)
        self.ciclo_spin.grid(row=3, column=1, pady=5, sticky="w")

        # Duración del sangrado
        self.sangrado_label = tk.Label(self.form_frame, text="Duración del sangrado (días):", bg=BLANCO, fg=NEGRO, font=("Montserrat", 11))
        self.sangrado_label.grid(row=4, column=0, sticky="w", pady=5)
        self.sangrado_spin = tk.Spinbox(self.form_frame, from_=2, to=10, font=("Montserrat", 11), width=5)
        self.sangrado_spin.grid(row=4, column=1, pady=5, sticky="w")

        # Ciclos regulares
        self.regular_label = tk.Label(self.form_frame, text="¿Ciclos regulares?", bg=BLANCO, fg=NEGRO, font=("Montserrat", 11))
        self.regular_label.grid(row=5, column=0, sticky="w", pady=5)
        self.regular_var = tk.StringVar(value="Sí")
        self.regular_si = tk.Radiobutton(self.form_frame, text="Sí", variable=self.regular_var, value="Sí", bg=BLANCO, font=("Montserrat", 11))
        self.regular_no = tk.Radiobutton(self.form_frame, text="No", variable=self.regular_var, value="No", bg=BLANCO, font=("Montserrat", 11))
        self.regular_si.grid(row=5, column=1, sticky="w")
        self.regular_no.grid(row=5, column=1, sticky="e")

        # Botón calcular
        self.calcular_btn = tk.Button(self, text="Calcular días fértiles", bg=ROSA, fg=BLANCO, font=("Montserrat", 12, "bold"), command=self.calcular)
        self.calcular_btn.pack(pady=20)

        # Resultados
        self.resultado_label = tk.Label(self, text="", bg=BLANCO, fg=NEGRO, font=("Montserrat", 12))
        self.resultado_label.pack(pady=10)

        # Botón exportar PDF
        self.pdf_btn = tk.Button(self, text="Exportar a PDF", bg=NEGRO, fg=BLANCO, font=("Montserrat", 11), command=self.exportar_pdf, state="disabled")
        self.pdf_btn.pack(pady=5)

    def calcular(self):
        try:
            nombre = self.nombre_entry.get()
            fecha_cuestionario = self.fecha_entry.get_date()
            fecha_periodo = self.periodo_entry.get_date()
            duracion_ciclo = int(self.ciclo_spin.get())
            duracion_sangrado = int(self.sangrado_spin.get())
            regular = self.regular_var.get()
            if not nombre:
                messagebox.showerror("Error", "Por favor, ingresa el nombre del paciente.")
                return
            # Cálculo de días fértiles
            ovulacion = fecha_periodo + timedelta(days=duracion_ciclo-14)
            inicio_fertil = ovulacion - timedelta(days=4)
            fin_fertil = ovulacion + timedelta(days=1)
            self.resultado = {
                "nombre": nombre,
                "fecha_cuestionario": fecha_cuestionario.strftime('%d/%m/%Y'),
                "fecha_periodo": fecha_periodo.strftime('%d/%m/%Y'),
                "duracion_ciclo": duracion_ciclo,
                "duracion_sangrado": duracion_sangrado,
                "regular": regular,
                "inicio_fertil": inicio_fertil.strftime('%d/%m/%Y'),
                "fin_fertil": fin_fertil.strftime('%d/%m/%Y'),
                "ovulacion": ovulacion.strftime('%d/%m/%Y')
            }
            texto = f"Días fértiles más fuertes: {inicio_fertil.strftime('%d/%m/%Y')} a {fin_fertil.strftime('%d/%m/%Y')}\nDía probable de ovulación: {ovulacion.strftime('%d/%m/%Y')}"
            self.resultado_label.config(text=texto)
            self.pdf_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")

    def exportar_pdf(self):
        if not hasattr(self, 'resultado'):
            return
        archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="Guardar PDF")
        if not archivo:
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(255, 105, 180)  # Rosa
        pdf.cell(0, 15, "Calculadora de Días Fértiles", ln=1, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Nombre del paciente: {self.resultado['nombre']}", ln=1)
        pdf.cell(0, 10, f"Fecha de llenado: {self.resultado['fecha_cuestionario']}", ln=1)
        pdf.cell(0, 10, f"Inicio del último periodo: {self.resultado['fecha_periodo']}", ln=1)
        pdf.cell(0, 10, f"Duración del ciclo: {self.resultado['duracion_ciclo']} días", ln=1)
        pdf.cell(0, 10, f"Duración del sangrado: {self.resultado['duracion_sangrado']} días", ln=1)
        pdf.cell(0, 10, f"¿Ciclos regulares?: {self.resultado['regular']}", ln=1)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 13)
        pdf.set_text_color(255, 105, 180)
        pdf.cell(0, 10, f"Días fértiles más fuertes: {self.resultado['inicio_fertil']} a {self.resultado['fin_fertil']}", ln=1)
        pdf.cell(0, 10, f"Día probable de ovulación: {self.resultado['ovulacion']}", ln=1)
        pdf.output(archivo)
        messagebox.showinfo("PDF guardado", "El archivo PDF se ha guardado correctamente.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
# ... existing code ... 