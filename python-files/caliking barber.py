import tkinter as tk
from tkinter import messagebox, ttk
import csv
from datetime import datetime, timedelta
import os
#from PIL import Image, ImageTk, ImageOps

ARCHIVO_RESERVAS = "reservas.csv"
ARCHIVO_CLIENTES = "clientes_frecuentes.csv"


def inicializar_archivos():
    for archivo, campos in [
        (ARCHIVO_RESERVAS, ["Nombre", "Telefono", "Fecha", "Hora", "Barbero", "Servicio", "Costo"]),
        (ARCHIVO_CLIENTES, ["Nombre", "Telefono"])
    ]:
        if not os.path.exists(archivo):
            with open(archivo, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(campos)


def eliminar_reservas_pasadas():
    reservas_activas = []
    ahora = datetime.now()

    with open(ARCHIVO_RESERVAS, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            fecha_hora = datetime.strptime(f"{row['Fecha']} {row['Hora']}", "%Y-%m-%d %H:%M")
            if fecha_hora >= ahora:
                reservas_activas.append(row)

    with open(ARCHIVO_RESERVAS, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(reservas_activas)


def guardar_cliente_frecuente(nombre, telefono):
    existentes = []
    with open(ARCHIVO_CLIENTES, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            existentes.append((row['Nombre'], row['Telefono']))

    if (nombre, telefono) not in existentes:
        with open(ARCHIVO_CLIENTES, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([nombre, telefono])


def verificar_disponibilidad(fecha, hora, barbero):
    with open(ARCHIVO_RESERVAS, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Fecha"] == fecha and row["Hora"] == hora and row["Barbero"] == barbero:
                return False
    return True


def guardar_reserva(nombre, telefono, fecha, hora, barbero, servicio, costo):
    with open(ARCHIVO_RESERVAS, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([nombre, telefono, fecha, hora, barbero, servicio, costo])


def limpiar_campos():
    entry_nombre.delete(0, tk.END)
    entry_telefono.delete(0, tk.END)
    combo_hora.set("")
    entry_barbero.delete(0, tk.END)
    combo_servicio.set("")


def generar_horas_disponibles():
    horas_ocupadas = set()
    with open(ARCHIVO_RESERVAS, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            horas_ocupadas.add((row['Fecha'], row['Hora'], row['Barbero']))

    horas = []
    inicio = datetime.strptime("10:00", "%H:%M")
    fin = datetime.strptime("20:00", "%H:%M")
    hoy = datetime.now().strftime("%Y-%m-%d")

    while inicio < fin:
        hora_str = inicio.strftime("%H:%M")
        disponible = True
        for barbero in set([row["Barbero"] for row in csv.DictReader(open(ARCHIVO_RESERVAS))]):
            if (hoy, hora_str, barbero) in horas_ocupadas:
                disponible = False
        if disponible:
            horas.append(hora_str)
        inicio += timedelta(minutes=40)
    return horas


def realizar_reserva():
    nombre = entry_nombre.get().strip().title()
    telefono = entry_telefono.get().strip()
    barbero = entry_barbero.get().strip().title()
    hora = combo_hora.get()
    servicio = combo_servicio.get()
    fecha = datetime.now().strftime("%Y-%m-%d")
    dia_semana = datetime.now().weekday()

    if dia_semana >= 6:
        messagebox.showwarning("Cerrado", "La barbería no abre los domingos.")
        return

    if not (nombre and hora and servicio):
        messagebox.showwarning("Campos incompletos", "Completa todos los campos obligatorios.")
        return

    if barbero and not verificar_disponibilidad(fecha, hora, barbero):
        messagebox.showerror("No disponible", f"{barbero} ya tiene una reserva a esa hora.")
        return

    costos = {"Corte de cabello": 30000, "Corte y barba": 40000, "Solo barba": 20000}
    costo = costos.get(servicio, 0)

    guardar_reserva(nombre, telefono, fecha, hora, barbero, servicio, costo)
    guardar_cliente_frecuente(nombre, telefono)
    messagebox.showinfo("Reserva exitosa", f"Tu cita ha sido agendada. Total: ${costo:,.0f}")
    limpiar_campos()


inicializar_archivos()
eliminar_reservas_pasadas()

root = tk.Tk()
root.title("Caliking Barbershop - Reservas")
root.iconbitmap("caliking.ico")

# Fondo con imagen invertida
#original = Image.open("caliking.ico").convert("RGB")
#invertida = ImageOps.invert(original)
#fondo = ImageTk.PhotoImage(invertida)

canvas = tk.Canvas(root, width=900, height=650)
canvas.pack(fill="both", expand=True)
#canvas.create_image(0, 0, image=fondo, anchor="nw")

frame = tk.Frame(canvas, bg="#000000")
canvas.create_window((20, 20), window=frame, anchor="nw")

style = ttk.Style()
style.configure("TCombobox", fieldbackground="#333", background="#222", foreground="white")

labels = ["Nombre y Apellido:", "Telefono (opcional):", "Hora:", "Barbero (opcional):", "Servicio:"]
for i, text in enumerate(labels):
    tk.Label(frame, text=text, fg="white", bg="#000000").grid(row=i, column=0, sticky="e")

entry_nombre = tk.Entry(frame)
entry_telefono = tk.Entry(frame)
combo_hora = ttk.Combobox(frame, values=generar_horas_disponibles(), state="readonly")
entry_barbero = tk.Entry(frame)
combo_servicio = ttk.Combobox(frame, values=["Corte de cabello", "Corte y barba", "Solo barba"], state="readonly")

entries = [entry_nombre, entry_telefono, combo_hora, entry_barbero, combo_servicio]
for i, entry in enumerate(entries):
    entry.grid(row=i, column=1)

# Autocompletado de nombre con Enter
clientes_frecuentes = []
with open(ARCHIVO_CLIENTES, mode='r') as file:
    reader = csv.DictReader(file)
    clientes_frecuentes = [row['Nombre'] for row in reader]

def autocompletar_nombre(event):
    entrada = entry_nombre.get().strip().title()
    for nombre in clientes_frecuentes:
        if nombre.startswith(entrada):
            entry_nombre.delete(0, tk.END)
            entry_nombre.insert(0, nombre)
            return

entry_nombre.bind("<Return>", autocompletar_nombre)

btn_reservar = tk.Button(frame, text="Reservar", command=realizar_reserva, bg="#222", fg="white")
btn_reservar.grid(row=5, column=0, columnspan=2, pady=10)

# Mostrar reservas activas
lista_reservas = tk.Listbox(canvas, bg="#000000", fg="white", width=120, height=10)
canvas.create_window((20, 300), window=lista_reservas, anchor="nw")

if os.path.exists(ARCHIVO_RESERVAS):
    with open(ARCHIVO_RESERVAS, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            texto = f"{row['Fecha']} {row['Hora']} - {row['Nombre']} ({row['Servicio']}) - ${int(row['Costo']):,}"
            lista_reservas.insert(tk.END, texto)

# Centrar ventana
def centrar_ventana(ventana):
    ventana.update_idletasks()
    w = ventana.winfo_width()
    h = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (w // 2)
    y = (ventana.winfo_screenheight() // 2) - (h // 2)
    ventana.geometry(f"+{x}+{y}")

centrar_ventana(root)
root.mainloop()
