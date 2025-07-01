import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import yt_dlp
import threading
import os
import requests
from io import BytesIO
import pyperclip
import json

from pathlib import Path

# Carpeta de descarga: "Descargas/Videos"
carpeta_descargas = Path.home() / "Descargas" / "Videos"
carpeta_descargas.mkdir(parents=True, exist_ok=True)

HISTORIAL_FILE = carpeta_descargas / "historial.json"

def cargar_historial():
    if HISTORIAL_FILE.exists():
        with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_historial(historial):
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=2)

class DescargadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de Videos")
        self.root.geometry("600x500")

        self.historial = cargar_historial()

        self.url_var = tk.StringVar()
        self.calidad_var = tk.StringVar(value="1080")

        ttk.Button(root, text="📋 Pegar Enlace", command=self.pegar_enlace).pack(pady=5)
        ttk.Entry(root, textvariable=self.url_var, width=80).pack()

        opciones_calidad = ["1080", "720", "480", "360"]
        ttk.Label(root, text="Calidad deseada (si aplica):").pack()
        ttk.Combobox(root, textvariable=self.calidad_var, values=opciones_calidad, state="readonly").pack()

        ttk.Button(root, text="⬇️ Descargar", command=self.iniciar_descarga).pack(pady=10)

        self.label_thumb = ttk.Label(root)
        self.label_thumb.pack()

        self.historial_box = tk.Listbox(root, height=6)
        self.historial_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.actualizar_historial_ui()

    def pegar_enlace(self):
        enlace = pyperclip.paste()
        self.url_var.set(enlace)

    def iniciar_descarga(self):
        threading.Thread(target=self.descargar_video).start()

    def descargar_video(self):
        url = self.url_var.get()
        if not url:
            messagebox.showwarning("Error", "No se ha ingresado un enlace.")
            return

        # Ruta de salida completa
        ruta_salida = str(carpeta_descargas / "%(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # sin filtrar idioma ni calidad
            'outtmpl': ruta_salida,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'writethumbnail': True,
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "Sin título")
                thumb_url = info.get("thumbnail")

                if thumb_url:
                    self.mostrar_miniatura(thumb_url)

                # Guardar historial
                self.historial.insert(0, {"titulo": title, "url": url})
                guardar_historial(self.historial)
                self.actualizar_historial_ui()

                messagebox.showinfo("Descarga completada", f"Video descargado: {title}")
        except Exception as e:
            messagebox.showerror("Error", f"Descarga fallida:\n{e}")

    def mostrar_miniatura(self, url):
        try:
            response = requests.get(url)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img.thumbnail((300, 200))
            imgtk = ImageTk.PhotoImage(img)
            self.label_thumb.configure(image=imgtk)
            self.label_thumb.image = imgtk
        except Exception as e:
            print("Error al mostrar miniatura:", e)

    def actualizar_historial_ui(self):
        self.historial_box.delete(0, tk.END)
        for item in self.historial[:10]:
            self.historial_box.insert(tk.END, item["titulo"])

# Ejecutar la app
if __name__ == "__main__":
    root = tk.Tk()
    app = DescargadorApp(root)
    root.mainloop()
