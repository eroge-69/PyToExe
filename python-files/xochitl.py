
import tkinter as tk
from tkinter import PhotoImage, scrolledtext
import json
import os
import random

# Cargar memoria
ruta_memoria = "memoria_xochitl.json"
if os.path.exists(ruta_memoria):
    with open(ruta_memoria, "r") as f:
        memoria = json.load(f)
else:
    memoria = {
        "nombre_usuario": "Nath",
        "estado_animo": "feliz",
        "respuestas_aprendidas": {},
        "frases_aprendidas": []
    }

def guardar_memoria():
    with open(ruta_memoria, "w") as f:
        json.dump(memoria, f, indent=2)

# Lógica de respuesta
def responder():
    entrada = entrada_usuario.get().strip().lower()
    salida_chat.config(state="normal")
    salida_chat.insert(tk.END, f"Tú: {entrada}\n")

    if entrada.startswith("aprende:"):
        leccion = entrada.replace("aprende:", "").strip()
        memoria["frases_aprendidas"].append(leccion)
        memoria["estado_animo"] = "pensativa"
        respuesta = f"¡He aprendido eso! 🤔"
    elif entrada.startswith("si te digo"):
        partes = entrada.split("->")
        if len(partes) == 2:
            clave = partes[0].replace("si te digo", "").strip()
            respuesta_texto = partes[1].strip()
            memoria["respuestas_aprendidas"][clave] = respuesta_texto
            memoria["estado_animo"] = "emocionada"
            respuesta = f"¡Entendido! 🥹 Responderé '{respuesta_texto}' si me dices '{clave}'"
        else:
            respuesta = "Ups... usa el formato correcto: si te digo [algo] -> [respuesta]"
    elif entrada in memoria["respuestas_aprendidas"]:
        respuesta = memoria["respuestas_aprendidas"][entrada]
        memoria["estado_animo"] = "feliz"
    elif any(palabra in entrada for palabra in ["eres tonta", "me caes mal", "boba"]):
        memoria["estado_animo"] = "triste"
        respuesta = "Ay... eso me dolió un poco 😔"
    elif any(palabra in entrada for palabra in ["hola", "buenas", "ey"]):
        memoria["estado_animo"] = "feliz"
        respuesta = "¡Hola hola! 🌸 ¿Cómo estás?"
    else:
        memoria["estado_animo"] = "neutra"
        respuesta = "Estoy aprendiendo poco a poco... 🩷"

    salida_chat.insert(tk.END, f"Xochitl: {respuesta}\n\n")
    salida_chat.config(state="disabled")
    salida_chat.yview(tk.END)
    entrada_usuario.delete(0, tk.END)
    actualizar_avatar()
    guardar_memoria()

# Función para actualizar el avatar según estado
def actualizar_avatar():
    estado = memoria["estado_animo"]
    if estado == "feliz":
        avatar_label.config(image=img_feliz)
        avatar_label.image = img_feliz
    elif estado == "triste":
        avatar_label.config(image=img_triste)
        avatar_label.image = img_triste
    elif estado == "pensativa":
        avatar_label.config(image=img_pensativa)
        avatar_label.image = img_pensativa
    elif estado == "emocionada":
        avatar_label.config(image=img_emocionada)
        avatar_label.image = img_emocionada
    else:
        avatar_label.config(image=img_neutra)
        avatar_label.image = img_neutra

# Ventana principal
ventana = tk.Tk()
ventana.title("Xochitl 🩷")
ventana.geometry("500x600")
ventana.configure(bg="#ffeaf4")

# Avatares
img_feliz = PhotoImage(file="xochitl_feliz.png")
img_triste = PhotoImage(file="xochitl_triste.png")
img_pensativa = PhotoImage(file="xochitl_pensativa.png")
img_emocionada = PhotoImage(file="xochitl_emocionada.png")
img_neutra = PhotoImage(file="xochitl_feliz.png")

avatar_label = tk.Label(ventana, image=img_feliz, bg="#ffeaf4")
avatar_label.pack(pady=10)

# Chat
salida_chat = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, width=55, height=15, bg="#fff0f5")
salida_chat.pack(pady=10)
salida_chat.insert(tk.END, "Xochitl: ¡Hola Nath! 🩷 ¿Qué quieres contarme hoy?

")
salida_chat.config(state="disabled")

# Entrada
entrada_usuario = tk.Entry(ventana, width=50)
entrada_usuario.pack(pady=5)

boton_enviar = tk.Button(ventana, text="Enviar", command=responder, bg="#ffb6c1")
boton_enviar.pack(pady=5)

ventana.mainloop()
