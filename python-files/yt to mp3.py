import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import tkinter as tk
from tkinter import messagebox

# Inicializa el motor de voz
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # velocidad de habla

def hablar(texto):
    print("Asistente:", texto)
    engine.say(texto)
    engine.runAndWait()

def escuchar():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        hablar("Escuchando...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        comando = r.recognize_google(audio, language='es-ES')
        print("Tú dijiste:", comando)
        return comando.lower()
    except sr.UnknownValueError:
        hablar("No entendí eso.")
        return ""
    except sr.RequestError:
        hablar("Error al conectar con el servicio de voz.")
        return ""

def ejecutar_comando(comando):
    if 'hora' in comando:
        hora = datetime.datetime.now().strftime('%H:%M')
        hablar(f"Son las {hora}")

    elif 'abrir youtube' in comando:
        webbrowser.open("https://www.youtube.com")
        hablar("Abriendo YouTube")

    elif 'abrir google' in comando:
        webbrowser.open("https://www.google.com")
        hablar("Abriendo Google")

    elif 'abrir chat' in comando:
        webbrowser.open("https://www.chatgpt.com")
        hablar("Abriendo chat GPT")

    elif 'abrir música' in comando:
        music_path = "C:\\Users\\jaime\\Music"
        try:
            os.startfile(music_path)
            hablar("Abriendo tu música")
        except FileNotFoundError:
            hablar("No encontré la carpeta de música.")

    elif 'entorno de trabajo' in comando:
        ruta_entorno = r"C:\Users\jaime\AppData\Local\Programs\Microsoft VS Code\Code.exe"
        webbrowser.open("http://trainingdojo.xyz/")
        webbrowser.open("chat.openai.com")
        webbrowser.open("https://music.youtube.com/")
        try:
            os.startfile(ruta_entorno)
            hablar("Abriendo tu entorno de trabajo")
        except FileNotFoundError:
            hablar("No encontré tu entorno de trabajo.")

    elif 'abrir minecraft' in comando or 'jugar minecraft' in comando:
        ruta_minecraft = r"C:\Program Files\Modrinth App\Modrinth App.exe"
        try:
            os.startfile(ruta_minecraft)
            hablar("Abriendo Minecraft")
        except FileNotFoundError:
            hablar("No encontré Minecraft en tu PC.")

    elif 'abrir dc' in comando or 'abrir discord' in comando:
        ruta_discord = r"C:\Users\jaime\AppData\Local\Discord\app-1.0.9200\discord.exe"
        try:
            os.startfile(ruta_discord)
            hablar("Abriendo Discord")
        except FileNotFoundError:
            hablar("No encontré Discord en tu PC.")

    elif 'salir' in comando or 'detente' in comando:
        hablar("Adiós!")
        ventana.quit()

    else:
        hablar("No tengo ese comando aún.")

# 🎨 Interfaz gráfica
def iniciar_escucha():
    comando = escuchar()
    if comando:
        ejecutar_comando(comando)

ventana = tk.Tk()
ventana.title("Asistente de Voz")
ventana.geometry("300x200")
ventana.configure(bg="#f0f0f0")

etiqueta = tk.Label(ventana, text="Asistente de Voz", font=("Arial", 16), bg="#f0f0f0")
etiqueta.pack(pady=20)

boton_escuchar = tk.Button(ventana, text="🎤 Escuchar", font=("Arial", 14), command=iniciar_escucha, bg="#4CAF50", fg="white", padx=20, pady=10)
boton_escuchar.pack()

hablar("Hola, soy tu asistente de voz. Pulsa el botón para hablar.")
ventana.mainloop()
