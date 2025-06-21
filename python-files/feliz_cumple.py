import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import webbrowser

# Colores y fuentes
fondo_color = "#D0F0FF"
texto_color = "#003344"
boton_color = "#A6E3E9"
fuente = ("Segoe UI", 12)
pregunta_fuente = ("Segoe UI", 14, "bold")

# Preguntas
preguntas = [
    {"tipo": "normal", "pregunta": "¿Estás lista?", "opciones": ["Si", "No", "¿bromeas? lista es mi segundo nombre", "Lo tengo que pensar"], "correcta": "¿bromeas? lista es mi segundo nombre"},
    {"tipo": "normal", "pregunta": "Cuando fuimos a la cafetería en bariloche...¿Qué estuvo más horrible?", "opciones": ["Verte a la cara", "El brownie", "El batido", "Todas son correctas"], "correcta": "Todas son correctas"},
    {"tipo": "normal", "pregunta": "¿Cuál fue el momento en el que decidiste ser mi amiga?", "opciones": ["En el que te di pena", "Cuando mi mamá te pagó", "Cuando no te quedó otra", "Fue un accidente"], "correcta": "Fue un accidente"},
    {"tipo": "normal", "pregunta": "¿Hoy qué se festeja?", "opciones": ["La independencia", "El día de la bandera", "nada importante", "año nuevo judío"], "correcta": "nada importante"},
    {"tipo": "normal", "pregunta": "Por último ¿qué edad tenés?", "opciones": ["98", "No sé", "19", "20!!!?"], "correcta": "20!!!?"},
    {"tipo": "si_o_no", "pregunta": "¿Vamos a ser mjj, bff, mejus, mejoras, besties para toda la vida?"},
    {"tipo": "si_o_no", "pregunta": "¿Puedo ser tu sexy chambelán?"},
    {"tipo": "si_o_no", "pregunta": "¿me cedés tus derechos sobre tu persona para venderte por internet?"},
]

# Ventana
root = tk.Tk()
root.title("🎂 Feliz Cumple")
root.geometry("700x600")
root.configure(bg=fondo_color)

# Fondo decorativo
canvas = tk.Canvas(root, bg=fondo_color, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Cargar imágenes
try:
    torta_img = Image.open("torta.png").resize((80, 80))
    burbuja_img = Image.open("burbuja.png").resize((40, 40))
    torta = ImageTk.PhotoImage(torta_img)
    burbuja = ImageTk.PhotoImage(burbuja_img)
    canvas.create_image(60, 60, image=burbuja)
    canvas.create_image(640, 100, image=burbuja)
    canvas.create_image(350, 50, image=torta)
except:
    pass

# Etiqueta de pregunta
pregunta_label = tk.Label(canvas, text="", wraplength=600, bg=fondo_color, fg=texto_color, font=pregunta_fuente, justify="center")
pregunta_label.place(relx=0.5, rely=0.2, anchor="center")

# Botones
botones = []
for i in range(4):
    b = tk.Button(canvas, text="", width=40, bg=boton_color, fg=texto_color, font=fuente, relief="groove")
    b.place(relx=0.5, rely=0.35 + i*0.1, anchor="center")
    botones.append(b)

indice = 0
respuestas = []

def guardar_respuesta(pregunta, respuesta):
    respuestas.append(f"{pregunta}\n→ {respuesta}\n")

def verificar_respuesta(opcion):
    global indice
    p = preguntas[indice]
    if p["tipo"] == "si_o_no" and opcion == "No":
        messagebox.showerror("Esa respuesta es incorrecta. Te dejo intentar de nuevo. Ojito")
        return
    guardar_respuesta(p["pregunta"], opcion)
    indice += 1
    mostrar_pregunta()

def mostrar_pregunta():
    global indice
    if indice >= len(preguntas):
        mostrar_mensaje_final()
        return

    p = preguntas[indice]
    pregunta_label.config(text=p["pregunta"])

    for b in botones:
        b.place_forget()

    if p["tipo"] == "normal":
        for i, opcion in enumerate(p["opciones"]):
            botones[i].config(text=opcion, command=lambda o=opcion: verificar_respuesta(o))
            botones[i].place(relx=0.5, rely=0.35 + i*0.1, anchor="center")
    elif p["tipo"] == "si_o_no":
        botones[0].config(text="Sí", command=lambda: verificar_respuesta("Sí"))
        botones[1].config(text="No", command=lambda: verificar_respuesta("No"))
        botones[0].place(relx=0.5, rely=0.45, anchor="center")
        botones[1].place(relx=0.5, rely=0.55, anchor="center")

def mostrar_mensaje_final():
    for b in botones:
        b.place_forget()
    pregunta_label.config(
        text="🎉 ¡Feliz cumpleaños!\n\nTe amo mucho, cuchurrumin.\n\n💌 Tenés un regalo final abajo."
    )

    btn_drive = tk.Button(canvas, text="📁 Abrir archivo sorpresa (Drive)", bg="#89CFF0", fg="black", font=fuente, command=abrir_drive)
    btn_drive.place(relx=0.5, rely=0.7, anchor="center")

def abrir_drive():
    webbrowser.open("https://drive.google.com/file/d/19EmOGPZyc34N9c0ePBh7uexB-Lx8dRz1/view?usp=sharing")

# Iniciar juego
mostrar_pregunta()
root.mainloop()
