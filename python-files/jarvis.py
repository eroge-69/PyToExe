import speech_recognition as sr
import pyttsx3
import pyautogui
import os
import webbrowser
import tkinter as tk
import threading

# Inicializar voz
voz = pyttsx3.init()
voz.setProperty('rate', 160)  # velocidad de habla
voz.setProperty('volume', 1)  # volumen máximo

# Función para hablar
def hablar(texto):
    print(f"JARVIS: {texto}")
    voz.say(texto)
    voz.runAndWait()

# Función para escuchar voz y convertir a texto
def escuchar_comando():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        comando = r.recognize_google(audio, language="es-ES")
        print(f"Has dicho: {comando}")
        return comando.lower()
    except sr.UnknownValueError:
        hablar("No entendí lo que dijiste.")
        return ""
    except sr.RequestError:
        hablar("No se pudo conectar al servicio de reconocimiento de voz.")
        return ""

# Función para ejecutar comandos básicos
def ejecutar_comando(comando):
    if "abre bloc de notas" in comando:
        os.system("notepad")
        hablar("Abriendo el bloc de notas")
    elif "abre google" in comando:
        webbrowser.open("https://www.google.com")
        hablar("Abriendo Google")
    elif "abre youtube" in comando:
        webbrowser.open("https://www.youtube.com")
        hablar("Abriendo YouTube")
    elif "escribe" in comando:
        texto = comando.replace("escribe", "").strip()
        pyautogui.write(texto, interval=0.1)
        hablar("Escribiendo")
    elif "sube volumen" in comando:
        pyautogui.press("volumeup")
        hablar("Subiendo volumen")
    elif "baja volumen" in comando:
        pyautogui.press("volumedown")
        hablar("Bajando volumen")
    elif "silencio" in comando:
        pyautogui.press("volumemute")
        hablar("Silenciando")
    elif "cerrar ventana" in comando:
        pyautogui.hotkey('alt', 'f4')
        hablar("Cerrando la ventana activa")
    elif "apaga el computador" in comando:
        hablar("¿Estás seguro que quieres apagar el computador? Di sí para confirmar.")
        confirmacion = escuchar_comando()
        if "sí" in confirmacion:
            hablar("Apagando el sistema")
            os.system("shutdown /s /t 1")
        else:
            hablar("Cancelado")
    else:
        hablar("Comando no reconocido")

# Función principal en hilo
def iniciar_jarvis():
    hablar("Hola, soy JARVIS. ¿Qué necesitas?")
    while True:
        comando = escuchar_comando()
        if comando:
            ejecutar_comando(comando)

# Interfaz visual estilo JARVIS
ventana = tk.Tk()
ventana.title("J.A.R.V.I.S")
ventana.geometry("400x200")
ventana.config(bg="black")

etiqueta = tk.Label(ventana, text="JARVIS está escuchando...", fg="cyan", bg="black", font=("Consolas", 14))
etiqueta.pack(pady=20)

boton_iniciar = tk.Button(ventana, text="Activar JARVIS", command=lambda: threading.Thread(target=iniciar_jarvis).start(), font=("Consolas", 12), bg="gray20", fg="white")
boton_iniciar.pack(pady=10)

ventana.mainloop()
