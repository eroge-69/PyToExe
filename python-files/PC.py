import serial
import serial.tools.list_ports
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

def seleccionar_puerto():
    puertos = list(serial.tools.list_ports.comports())
    if not puertos:
        messagebox.showerror("Error", "No se detectaron dispositivos Bluetooth.")
        return None

    ventana = tk.Tk()
    ventana.title("Seleccionar dispositivo Bluetooth")
    ventana.geometry("400x150")

    puerto_var = tk.StringVar(value=puertos[0].device)

    tk.Label(ventana, text="Seleccione el puerto:", font=("Arial", 12)).pack(pady=10)
    ttk.Combobox(ventana, textvariable=puerto_var, values=[p.device for p in puertos], width=30).pack()

    def conectar():
        ventana.destroy()

    tk.Button(ventana, text="Conectar", command=conectar, bg="lightblue").pack(pady=10)
    ventana.mainloop()
    return puerto_var.get()

class TermoformadoraApp:
    def __init__(self, master, puerto_serial):
        self.master = master
        self.master.title("Sistema de Calentamiento Bilateral")
        self.master.attributes('-fullscreen', True)
        self.master.configure(bg="#f0f0f0")

        try:
            self.serial_con = serial.Serial(puerto_serial, 115200, timeout=1)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar al puerto: {e}")
            master.destroy()
            return

        self.temp_sup = tk.DoubleVar()
        self.temp_inf = tk.DoubleVar()
        self.tiempo_restante = tk.IntVar()
        self.tiempo_entrada = tk.IntVar(value=10)
        self.contador_activo = False

        self.xdata = list(range(20))
        self.ydata_sup = [0]*20
        self.ydata_inf = [0]*20

        self.dibujar_interfaz()

        self.master.bind("<Escape>", lambda e: master.destroy())
        self.actualizar_datos()

    def dibujar_interfaz(self):
        main_frame = tk.Frame(self.master, bg="#f0f0f0")
        main_frame.pack(expand=True)

        tk.Label(main_frame, text="Panel de Control - Termoformado", font=("Arial", 24, "bold"), bg="#f0f0f0").pack(pady=20)

        temp_frame = tk.Frame(main_frame, bg="#f0f0f0")
        temp_frame.pack()
        tk.Label(temp_frame, text="Temp. Superior:", font=("Arial", 14), bg="#f0f0f0").grid(row=0, column=0)
        tk.Label(temp_frame, textvariable=self.temp_sup, font=("Arial", 14), bg="#f0f0f0").grid(row=0, column=1, padx=10)
        tk.Label(temp_frame, text="Temp. Inferior:", font=("Arial", 14), bg="#f0f0f0").grid(row=1, column=0)
        tk.Label(temp_frame, textvariable=self.temp_inf, font=("Arial", 14), bg="#f0f0f0").grid(row=1, column=1, padx=10)

        timer_frame = tk.Frame(main_frame, bg="#f0f0f0")
        timer_frame.pack(pady=10)
        tk.Label(timer_frame, text="Tiempo calentamiento (s):", font=("Arial", 14), bg="#f0f0f0").grid(row=0, column=0)
        tk.Entry(timer_frame, textvariable=self.tiempo_entrada, font=("Arial", 14), width=5).grid(row=0, column=1)
        self.label_tiempo = tk.Label(timer_frame, text="00:00", font=("Arial", 24), fg="blue", bg="#f0f0f0")
        self.label_tiempo.grid(row=1, column=0, columnspan=2, pady=10)
        tk.Button(timer_frame, text="Iniciar", command=self.iniciar_temporizador, font=("Arial", 14), bg="lightgreen").grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(main_frame, text="Activar Vacío", font=("Arial", 14), bg="lightblue", width=20).pack(pady=10)

        tk.Button(main_frame, text="● PARO DE EMERGENCIA ●", font=("Arial", 14, "bold"), bg="red", fg="white", command=self.parada_emergencia).pack(pady=10)
        tk.Button(main_frame, text="Cerrar", font=("Arial", 14), command=self.master.destroy, bg="gray", fg="white").pack(pady=10)

        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.line1, = self.ax.plot([], [], label='Temp. Sup.')
        self.line2, = self.ax.plot([], [], label='Temp. Inf.')
        self.ax.set_ylim(0, 250)
        self.ax.grid(True)
        self.ax.legend()
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().pack(pady=10)

    def iniciar_temporizador(self):
        if not self.contador_activo:
            self.contador_activo = True
            self.tiempo_restante.set(self.tiempo_entrada.get())
            self.actualizar_temporizador()

    def actualizar_temporizador(self):
        t = self.tiempo_restante.get()
        if t > 0:
            self.tiempo_restante.set(t - 1)
            mins, secs = divmod(t, 60)
            self.label_tiempo.config(text=f"{mins:02d}:{secs:02d}")
            self.master.after(1000, self.actualizar_temporizador)
        else:
            self.label_tiempo.config(text="00:00")
            self.contador_activo = False
            messagebox.showinfo("Temporizador", "¡Tiempo de calentamiento finalizado!")

    def actualizar_datos(self):
        try:
            if self.serial_con.in_waiting:
                linea = self.serial_con.readline().decode().strip()
                if "T1=" in linea:
                    self.temp_sup.set(float(linea.split("=")[1]))
                elif "T2=" in linea:
                    self.temp_inf.set(float(linea.split("=")[1]))
        except Exception as e:
            print("Error:", e)

        self.ydata_sup = self.ydata_sup[1:] + [self.temp_sup.get()]
        self.ydata_inf = self.ydata_inf[1:] + [self.temp_inf.get()]
        self.line1.set_data(self.xdata, self.ydata_sup)
        self.line2.set_data(self.xdata, self.ydata_inf)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

        self.master.after(1000, self.actualizar_datos)

    def parada_emergencia(self):
        self.contador_activo = False
        self.tiempo_restante.set(0)
        self.label_tiempo.config(text="00:00")
        messagebox.showwarning("Emergencia", "¡Parada de emergencia activada!")

if __name__ == "__main__":
    puerto = seleccionar_puerto()
    if puerto:
        root = tk.Tk()
        app = TermoformadoraApp(root, puerto)
        root.mainloop()
