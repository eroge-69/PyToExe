import tkinter as tk
from tkinter import messagebox
import threading
import cv2
from pyzbar import pyzbar
import mysql.connector
import numpy as np
from datetime import datetime, time

class QRReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Asistencia con QR")
        self.root.geometry("500x450")
        
        self.active = False
        self.camera = None
        self.ultimos_qr = set()
        self.conn = None
        self.cursor = None

        # -------------------------------
        # Configuración de conexión
        # -------------------------------
        tk.Label(root, text="Host:").pack()
        self.entry_host = tk.Entry(root)
        self.entry_host.insert(0, "localhost")
        self.entry_host.pack()

        tk.Label(root, text="Usuario:").pack()
        self.entry_user = tk.Entry(root)
        self.entry_user.insert(0, "root")
        self.entry_user.pack()

        tk.Label(root, text="Contraseña:").pack()
        self.entry_password = tk.Entry(root, show="*")
        self.entry_password.insert(0, "1234")  # puedes dejarlo vacío
        self.entry_password.pack()

        tk.Label(root, text="Base de Datos:").pack()
        self.entry_db = tk.Entry(root)
        self.entry_db.insert(0, "ingresoescolar")
        self.entry_db.pack()

        self.connect_button = tk.Button(root, text="Conectar", command=self.connect_db)
        self.connect_button.pack(pady=10)

        # Botones de control
        self.start_button = tk.Button(root, text="Iniciar Lector", command=self.start_reader, state="disabled")
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Detener Lector", command=self.stop_reader, state="disabled")
        self.stop_button.pack(pady=10)

        # Etiqueta de estado
        self.status_label = tk.Label(root, text="Estado: Sin conexión a BD", fg="red")
        self.status_label.pack(pady=20)

    def connect_db(self):
        """Conectar a MySQL con los datos ingresados"""
        host = self.entry_host.get()
        user = self.entry_user.get()
        password = self.entry_password.get()
        database = self.entry_db.get()

        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.conn.cursor()
            self.status_label.config(text="Conexión exitosa a la BD", fg="green")
            self.start_button.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error BD", f"No se pudo conectar:\n{e}")
            self.status_label.config(text="Estado: Error de conexión", fg="red")

    def start_reader(self):
        """Inicia la cámara y lectura QR en un hilo separado"""
        if not self.conn or not self.cursor:
            messagebox.showwarning("Sin conexión", "Primero debes conectar a la base de datos.")
            return

        self.active = True
        self.status_label.config(text="Estado: Lector iniciado", fg="green")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        thread = threading.Thread(target=self._run_reader)
        thread.start()

    def _run_reader(self):
        """Proceso de lectura QR"""
        self.camera = cv2.VideoCapture(0)

        while self.active:
            ret, frame = self.camera.read()
            if not ret:
                break

            qr_codes = pyzbar.decode(frame)
            for qr in qr_codes:
                matricula = qr.data.decode("utf-8")

                if matricula not in self.ultimos_qr:
                    self.ultimos_qr.add(matricula)
                    hora_actual = datetime.now()
                    hora_str = hora_actual.strftime("%H:%M:%S")

                    # Definir horarios
                    hora_entrada = time(8, 0)
                    hora_tolerancia = time(8, 15)
                    hora_salida = time(14, 0)

                    # Buscar en BD
                    self.cursor.execute("SELECT nombre, grado, grupo FROM estudiantes WHERE matricula=%s", (matricula,))
                    estudiante = self.cursor.fetchone()

                    if estudiante:
                        nombre_estudiante = estudiante[0]

                        # Determinar estado según hora
                        if hora_actual.time() >= hora_salida:
                            estado = "salida"
                            mensaje = f"{nombre_estudiante} marcó salida a las {hora_str}"
                        elif hora_entrada <= hora_actual.time() <= hora_tolerancia:
                            estado = "a_tiempo"
                            mensaje = f"{nombre_estudiante} llegó a tiempo a las {hora_str}"
                        elif hora_actual.time() > hora_tolerancia and hora_actual.time() < hora_salida:
                            estado = "tarde"
                            mensaje = f"{nombre_estudiante} llegó tarde a las {hora_str}"
                        else:
                            estado = "fuera_horario"
                            mensaje = f"{nombre_estudiante} escaneado fuera de horario"

                        # Mostrar en interfaz
                        self.status_label.config(
                            text=mensaje,
                            fg="green" if estado in ["a_tiempo","salida"] else "red"
                        )
                        print(mensaje)

                        # Registrar en BD
                        if estado != "fuera_horario":
                            self.cursor.execute(
                                "INSERT INTO registros_asistencia (matricula, nombre_estudiante, estado) VALUES (%s, %s)",
                                (matricula, nombre_estudiante, estado)
                            )
                            self.conn.commit()
                    else:
                        self.status_label.config(text=f"Matrícula {matricula} no encontrada", fg="red")

            cv2.imshow("Lector QR", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()

    def stop_reader(self):
        """Detener lector"""
        self.active = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Estado: Lector detenido", fg="blue")

        try:
            if self.cursor: self.cursor.close()
            if self.conn: self.conn.close()
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = QRReaderApp(root)
    root.mainloop()