import serial
import threading
import tkinter as tk
from tkinter import messagebox

class SerialReaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Interfaz de Reconocimiento de Medicamentos")

        # Encabezado
        self.header = tk.Label(master, text="Configuración del Puerto Serial",
                               font=("Arial", 14, "bold"), fg="blue")
        self.header.pack(pady=(10, 0))

        # Campo para puerto COM
        self.com_label = tk.Label(master, text="Puerto COM:")
        self.com_label.pack()
        self.com_entry = tk.Entry(master)
        self.com_entry.insert(0, "COM3")
        self.com_entry.pack()

        # Campo para Baud Rate
        self.baud_label = tk.Label(master, text="Baud Rate:")
        self.baud_label.pack()
        self.baud_entry = tk.Entry(master)
        self.baud_entry.insert(0, "9600")
        self.baud_entry.pack()

        # Botones de control
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=5)

        self.start_button = tk.Button(self.button_frame, text="Iniciar", command=self.start_serial)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(self.button_frame, text="Detener", command=self.stop_serial, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Área de texto
        self.text_display = tk.Text(master, height=3, width=60, bg='black', fg='lime')
        self.text_display.pack(padx=10, pady=10)

        master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.serial_conn = None
        self.running = False
        self.read_thread = None

    def start_serial(self):
        port = self.com_entry.get().strip()
        baud = self.baud_entry.get().strip()

        try:
            self.serial_conn = serial.Serial(port, int(baud), timeout=1)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el puerto serial: {e}")
            return

        # Desactiva campos y botones relevantes
        self.com_entry.config(state=tk.DISABLED)
        self.baud_entry.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.running = True
        self.read_thread = threading.Thread(target=self.read_serial)
        self.read_thread.daemon = True
        self.read_thread.start()

    def stop_serial(self):
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()

        # Habilita campos y botones
        self.com_entry.config(state=tk.NORMAL)
        self.baud_entry.config(state=tk.NORMAL)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def read_serial(self):
        while self.running:
            try:
                if self.serial_conn.in_waiting:
                    data = self.serial_conn.readline().decode().strip()
                    self.text_display.delete(1.0, tk.END)
                    self.text_display.insert(tk.END, data)
            except Exception as e:
                self.text_display.delete(1.0, tk.END)
                self.text_display.insert(tk.END, f"Error de lectura serial: {e}")

    def on_close(self):
        self.stop_serial()
        self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = SerialReaderApp(root)
    root.mainloop()
