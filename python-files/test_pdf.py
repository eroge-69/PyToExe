
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
import random
import json
import os
from datetime import datetime

HISTORIAL_FILE = "historial.json"

def extraer_texto_pdf(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    return texto

def generar_preguntas(texto, num_preguntas=30):
    oraciones = [o.strip() for o in texto.split('.') if len(o.strip().split()) > 5]
    preguntas = []
    for _ in range(min(num_preguntas, len(oraciones))):
        oracion = random.choice(oraciones)
        palabras = oracion.split()
        if len(palabras) < 5:
            continue
        idx = random.randint(1, len(palabras) - 2)
        respuesta = palabras[idx]
        palabras[idx] = "_____"
        pregunta = " ".join(palabras)
        opciones = [respuesta] + random.sample([w for w in texto.split() if w != respuesta and len(w) > 3], 3)
        random.shuffle(opciones)
        preguntas.append({
            "pregunta": pregunta,
            "respuesta": respuesta,
            "opciones": opciones
        })
    return preguntas

class TestApp:
    def __init__(self, master):
        self.master = master
        master.title("Generador de Test PDF")
        master.geometry("600x400")

        self.boton_cargar = tk.Button(master, text="Cargar PDF", command=self.cargar_pdf)
        self.boton_cargar.pack(pady=10)

        self.texto_pregunta = tk.Label(master, wraplength=550, justify="left", text="")
        self.texto_pregunta.pack(pady=20)

        self.botones_opciones = []
        for _ in range(4):
            btn = tk.Button(master, text="", command=lambda b=_: self.comprobar_respuesta(b))
            btn.pack(pady=2)
            self.botones_opciones.append(btn)

        self.resultado = tk.Label(master, text="Aciertos: 0 | Fallos: 0")
        self.resultado.pack(pady=10)

        self.preguntas = []
        self.indice_pregunta = 0
        self.aciertos = 0
        self.fallos = 0

    def cargar_pdf(self):
        ruta = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not ruta:
            return
        texto = extraer_texto_pdf(ruta)
        self.preguntas = generar_preguntas(texto)
        self.indice_pregunta = 0
        self.aciertos = 0
        self.fallos = 0
        self.mostrar_pregunta()

    def mostrar_pregunta(self):
        if self.indice_pregunta >= len(self.preguntas):
            self.guardar_historial()
            messagebox.showinfo("Fin", f"Test finalizado.\nAciertos: {self.aciertos}\nFallos: {self.fallos}")
            return

        pregunta = self.preguntas[self.indice_pregunta]
        self.texto_pregunta.config(text=f"Pregunta {self.indice_pregunta + 1}: {pregunta['pregunta']}")
        for i, btn in enumerate(self.botones_opciones):
            btn.config(text=pregunta["opciones"][i], state="normal")

        self.resultado.config(text=f"Aciertos: {self.aciertos} | Fallos: {self.fallos}")

    def comprobar_respuesta(self, indice):
        seleccion = self.botones_opciones[indice].cget("text")
        correcta = self.preguntas[self.indice_pregunta]["respuesta"]
        if seleccion == correcta:
            self.aciertos += 1
        else:
            self.fallos += 1
        self.indice_pregunta += 1
        self.mostrar_pregunta()

    def guardar_historial(self):
        datos = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "aciertos": self.aciertos,
            "fallos": self.fallos
        }
        historial = []
        if os.path.exists(HISTORIAL_FILE):
            with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
                historial = json.load(f)
        historial.append(datos)
        with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
            json.dump(historial, f, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = TestApp(root)
    root.mainloop()
