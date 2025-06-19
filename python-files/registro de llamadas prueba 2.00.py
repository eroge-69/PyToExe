import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import locale
from pathlib import Path

class RegistroLlamadas:
    def __init__(self):
        self.configurar_locale()
        self.credenciales = self.cargar_credenciales()
        self.mostrar_login()

    def configurar_locale(self):
        try:
            locale.setlocale(locale.LC_TIME, "es_ES.utf8")
        except:
            try:
                locale.setlocale(locale.LC_TIME, "Spanish_Spain.1252")
            except:
                pass

    def cargar_credenciales(self):
        return {"usuario": "samuel", "contraseña": "27dpr0400z"}

    def mostrar_login(self):
        self.login = tk.Tk()
        self.login.title("Iniciar Sesión")
        self.login.geometry("300x180")
        self.login.resizable(False, False)

        frame = ttk.Frame(self.login, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Usuario:").pack(anchor="w", pady=(0, 2))
        self.usuario_entry = ttk.Entry(frame)
        self.usuario_entry.pack(fill="x", pady=(0, 8))

        ttk.Label(frame, text="Contraseña:").pack(anchor="w", pady=(0, 2))
        self.contraseña_entry = ttk.Entry(frame, show="*")
        self.contraseña_entry.pack(fill="x", pady=(0, 12))

        ttk.Button(frame, text="Acceder", command=self.verificar_credenciales).pack(pady=4)

        self.login.mainloop()

    def verificar_credenciales(self):
        usuario = self.usuario_entry.get().strip()
        contraseña = self.contraseña_entry.get().strip()
        if usuario == self.credenciales["usuario"] and contraseña == self.credenciales["contraseña"]:
            self.login.destroy()
            self.iniciar_interfaz()
        else:
            messagebox.showerror("Acceso Denegado", "Usuario o contraseña incorrectos.")

    def iniciar_interfaz(self):
        self.ventana = tk.Tk()
        self.ventana.title("Registro de Llamadas")
        self.ventana.geometry("340x340")
        self.ventana.resizable(False, False)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TLabel", font=("Arial", 9))
        style.configure("TEntry", font=("Arial", 9))
        style.configure("TButton", font=("Arial", 9, "bold"), background="#2e8b57", foreground="white")

        self.crear_interfaz()
        self.ventana.mainloop()

    def crear_interfaz(self):
        frame = ttk.Frame(self.ventana, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Número:").pack(anchor="w")
        self.numero_entry = ttk.Entry(frame)
        self.numero_entry.pack(fill="x", pady=2)

        ttk.Label(frame, text="Cliente:").pack(anchor="w")
        self.cliente_entry = ttk.Entry(frame)
        self.cliente_entry.pack(fill="x", pady=2)

        ttk.Label(frame, text="Hotel:").pack(anchor="w")
        self.hotel_entry = ttk.Entry(frame)
        self.hotel_entry.pack(fill="x", pady=2)

        ttk.Label(frame, text="Concepto:").pack(anchor="w")
        self.concepto_text = tk.Text(frame, height=2, font=("Arial", 9), wrap="word", relief="solid", bd=1)
        self.concepto_text.pack(fill="x", pady=3)

        ttk.Button(frame, text="Guardar", command=self.guardar_registro).pack(pady=6)

        ttk.Label(frame, text="Último registro:").pack(anchor="w", pady=(8, 0))
        self.texto_visualizacion = tk.Text(frame, height=6, font=("Arial", 8), state=tk.DISABLED, wrap="word", relief="solid", bd=1)
        self.texto_visualizacion.pack(fill="x")

    def guardar_registro(self):
        fecha_actual = datetime.datetime.now()
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        hora = fecha_actual.strftime("%H:%M:%S")

        carpeta_actual = Path(__file__).parent.resolve()
        archivo = carpeta_actual / f"llamadas_{fecha_str}.txt"

        datos = {
            "Fecha": fecha_actual.strftime("%d/%m/%Y"),
            "Hora": hora,
            "Número": self.numero_entry.get().strip(),
            "Cliente": self.cliente_entry.get().strip().title(),
            "Hotel": self.hotel_entry.get().strip().title(),
            "Asesor": "Angel",  # Fijo
            "Concepto": self.concepto_text.get("1.0", tk.END).strip()
        }

        if not all([datos["Número"], datos["Cliente"], datos["Hotel"], datos["Concepto"]]):
            messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.")
            return

        try:
            archivo.touch(exist_ok=True)
            with open(archivo, "a", encoding="utf-8") as f:
                f.write(
                    f"Fecha    : {datos['Fecha']}\n"
                    f"Hora     : {datos['Hora']}\n"
                    f"Número   : {datos['Número']}\n"
                    f"Cliente  : {datos['Cliente']}\n"
                    f"Hotel    : {datos['Hotel']}\n"
                    f"Asesor   : {datos['Asesor']}\n"
                    f"Concepto : {datos['Concepto']}\n"
                    f"{'-'*40}\n"
                )
            messagebox.showinfo("Éxito", f"Guardado en:\n{archivo.resolve()}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
            return

        self.mostrar_ultimo(datos)
        self.limpiar()

    def mostrar_ultimo(self, datos):
        resumen = (
            f"Fecha    : {datos['Fecha']}\n"
            f"Hora     : {datos['Hora']}\n"
            f"Número   : {datos['Número']}\n"
            f"Cliente  : {datos['Cliente']}\n"
            f"Hotel    : {datos['Hotel']}\n"
            f"Asesor   : {datos['Asesor']}\n"
            f"Concepto : {datos['Concepto']}"
        )
        self.texto_visualizacion.config(state=tk.NORMAL)
        self.texto_visualizacion.delete("1.0", tk.END)
        self.texto_visualizacion.insert(tk.END, resumen)
        self.texto_visualizacion.config(state=tk.DISABLED)

    def limpiar(self):
        self.numero_entry.delete(0, tk.END)
        self.cliente_entry.delete(0, tk.END)
        self.hotel_entry.delete(0, tk.END)
        self.concepto_text.delete("1.0", tk.END)

if __name__ == "__main__":
    RegistroLlamadas()
