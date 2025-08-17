import tkinter as tk
from tkinter import filedialog
from docx import Document
import random
import asyncio
import edge_tts
import os
import tempfile
import pygame

class RepasoInglesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Repaso de Inglés")
        self.root.geometry("700x400")

        # Inicializar pygame mixer
        pygame.mixer.init()

        # Variables
        self.frases = []         
        self.index = -1          
        self.historial = []      
        self.modo = None         

        # Label principal (texto grande)
        self.label = tk.Label(root, text="Carga un archivo Word para comenzar",
                              wraplength=650, font=("Arial", 22), justify="center")
        self.label.pack(expand=True)

        # Captura de teclas
        self.root.bind("<Key>", self.teclas)

        # Carpeta temporal y cache de audios
        self.tempdir = tempfile.gettempdir()
        self.voz = "en-US-AriaNeural"
        self.audio_cache = {}  # Diccionario {frase: archivo_mp3}

        # Cargar archivo automáticamente al inicio
        self.root.after(500, self.cargar_archivo)

    def cargar_archivo(self):
        archivo = filedialog.askopenfilename(filetypes=[("Word files", "*.docx")])
        if not archivo:
            self.label.config(text="❌ No se cargó ningún archivo.")
            return

        doc = Document(archivo)
        texto = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        # Crear pares (ingles, español)
        self.frases = [(texto[i], texto[i+1]) for i in range(0, len(texto), 2)]
        random.shuffle(self.frases)

        # Preguntar modo
        self.label.config(
            text="Selecciona modo de repaso:\n\n"
                 "[1] Inglés → Español\n"
                 "[2] Español → Inglés\n\n"
                 "(Pulsa 1 o 2 en el teclado numérico)"
        )

    def teclas(self, event):
        if not self.frases:
            return

        tecla = event.keysym

        # Selección de modo
        if self.modo is None:
            if tecla == "1":
                self.modo = 1
                self.label.config(text="Modo Inglés → Español.\nPulsa '1' para empezar.")
            elif tecla == "2":
                self.modo = 2
                self.label.config(text="Modo Español → Inglés.\nPulsa '4' para empezar.")
            return

        # --- MODO 1: Inglés primero ---
        if self.modo == 1:
            if tecla == "1":  # siguiente en inglés
                self.siguiente_frase()
                self.mostrar_frase(ingles=True, pronunciar=True)
            elif tecla == "2":  # repetir inglés
                if self.index >= 0:
                    self.mostrar_frase(ingles=True, pronunciar=True, repetir=True)
            elif tecla == "3":  # mostrar español
                if self.index >= 0:
                    self.mostrar_frase(ingles=False, pronunciar=False)
            elif tecla == "0":  # retroceder
                self.retroceder()

        # --- MODO 2: Español primero ---
        elif self.modo == 2:
            if tecla == "4":  # siguiente en español
                self.siguiente_frase()
                self.mostrar_frase(ingles=False, pronunciar=False)
            elif tecla == "5":  # mostrar inglés + pronunciar
                if self.index >= 0:
                    self.mostrar_frase(ingles=True, pronunciar=True)
            elif tecla == "0":  # retroceder
                self.retroceder()

    def siguiente_frase(self):
        self.index += 1
        if self.index >= len(self.frases):
            self.index = 0  
        self.historial.append(self.index)

    def retroceder(self):
        if len(self.historial) > 1:
            self.historial.pop()      
            self.index = self.historial[-1]  
            frase = self.frases[self.index]
            self.label.config(text=f"(Retroceso)\n\n{frase[0]}\n\n{frase[1]}")

    def mostrar_frase(self, ingles=True, pronunciar=False, repetir=False):
        frase = self.frases[self.index]
        if ingles:
            self.label.config(text=f"INGLÉS:\n\n{frase[0]}")
            if pronunciar:
                asyncio.run(self.pronunciar(frase[0]))
        else:
            self.label.config(text=f"ESPAÑOL:\n\n{frase[1]}")

    async def pronunciar(self, texto):
        # Revisar si el audio ya existe
        if texto in self.audio_cache:
            archivo = self.audio_cache[texto]
        else:
            archivo = os.path.join(self.tempdir, f"frase_{len(self.audio_cache)}.mp3")
            communicate = edge_tts.Communicate(texto, self.voz)
            await communicate.save(archivo)
            self.audio_cache[texto] = archivo
        
        # Reproducir audio con pygame
        pygame.mixer.music.load(archivo)
        pygame.mixer.music.play()

if __name__ == "__main__":
    root = tk.Tk()
    app = RepasoInglesApp(root)
    root.mainloop()
