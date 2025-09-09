import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin
from customtkinter import (
    CTk, CTkEntry, CTkLabel, CTkButton, CTkRadioButton, CTkOptionMenu,
    StringVar, set_appearance_mode, set_default_color_theme
)
from tkinter import filedialog
import yt_dlp
import concurrent.futures

set_appearance_mode("dark")  # ou "light"
set_default_color_theme("blue")  # pode ser "green", "dark-blue"...

class App(CTk):
    def __init__(self):
        super().__init__()
        self.title("Downloader de URL")
        self.geometry("600x600")
        self.resizable(False, False)

        # VARIÁVEIS
        self.download_type = StringVar(value="imagem")
        self.video_quality = StringVar(value="Alta")

        # COMPONENTES
        CTkLabel(self, text="Insira a(s) URL(s)", font=("Arial", 16)).pack(pady=(15, 5))
        self.inputURL = CTkEntry(self, width=450, height=35, placeholder_text="Cole uma ou várias URLs (1 por linha)")
        self.inputURL.pack(pady=5)

        CTkLabel(self, text="Nome da pasta (para imagens):", font=("Arial", 14)).pack(pady=(15, 5))
        self.inputFolder = CTkEntry(self, width=450, height=35, placeholder_text="Digite o nome da pasta")
        self.inputFolder.pack(pady=5)

        CTkLabel(self, text="Tipo de download:", font=("Arial", 14)).pack(pady=(15, 0))
        CTkRadioButton(self, text="Imagem", variable=self.download_type, value="imagem").pack(pady=2)
        CTkRadioButton(self, text="Vídeo", variable=self.download_type, value="video").pack(pady=2)
        CTkRadioButton(self, text="Áudio", variable=self.download_type, value="audio").pack(pady=2)

        CTkLabel(self, text="Qualidade do vídeo:", font=("Arial", 14)).pack(pady=(15, 5))
        self.qualidade_menu = CTkOptionMenu(self, values=["Alta", "Média", "Baixa"], variable=self.video_quality)
        self.qualidade_menu.pack(pady=2)

        CTkButton(self, text="Iniciar Download", command=self.baixar, height=40, width=200).pack(pady=(25, 15))
        self.status_label = CTkLabel(self, text="", wraplength=500)
        self.status_label.pack(pady=5)

    def baixar(self):
        urls_text = self.inputURL.get().strip()
        tipo = self.download_type.get().lower()

        if not urls_text:
            self.status_label.configure(text="⚠️ Insira pelo menos uma URL válida.")
            return

        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]

        if tipo == "imagem":
            pasta_nome = self.inputFolder.get().strip()
            if not pasta_nome:
                self.status_label.configure(text="⚠️ Insira o nome da pasta para salvar as imagens.")
                return
            self.processarURLs(urls, pasta_nome)
        elif tipo == "video":
            if len(urls) > 1:
                self.status_label.configure(text="⚠️ Para vídeos, insira apenas uma URL de cada vez.")
                return
            self.download_video(urls[0])
        elif tipo == "audio":
            if len(urls) > 1:
                self.status_label.configure(text="⚠️ Para áudios, insira apenas uma URL de cada vez.")
                return
            self.download_audio(urls[0])

    def download_video(self, url):
        pasta = filedialog.askdirectory(title="Escolha a pasta para salvar o vídeo")
        if not pasta:
            self.status_label.configure(text="⚠️ Nenhuma pasta selecionada.")
            return

        qualidade = self.video_quality.get().lower()
        if qualidade == "alta":
            format_video = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
        elif qualidade == "média":
            format_video = "best[height<=720]"
        elif qualidade == "baixa":
            format_video = "best[height<=480]"
        else:
            format_video = "best"

        try:
            ydl_opts = {
                'outtmpl': f'{pasta}/%(title)s.%(ext)s',
                'format': format_video,
                'merge_output_format': 'mp4',
                'noplaylist': True,
                'quiet': False,
                'no_warnings': True,
                'retries': 3,
                'concurrent_fragment_downloads': 8,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.status_label.configure(text="✅ Vídeo baixado com sucesso!")

        except Exception as e:
            self.status_label.configure(text=f"❌ Erro ao baixar vídeo: {e}")

    def download_audio(self, url):
        pasta = filedialog.askdirectory(title="Escolha a pasta para salvar o áudio")
        if not pasta:
            self.status_label.configure(text="⚠️ Nenhuma pasta selecionada.")
            return

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{pasta}/%(title)s.%(ext)s',
                'noplaylist': True,
                'quiet': False,
                'no_warnings': True,
                'retries': 3,
                'concurrent_fragment_downloads': 8,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.status_label.configure(text="✅ Áudio baixado com sucesso!")

        except Exception as e:
            self.status_label.configure(text=f"❌ Erro ao baixar áudio: {e}")

    def baixar_imagem(self, full_img_url, pasta_destino):
        try:
            img_data = requests.get(full_img_url, timeout=10).content
            img = Image.open(BytesIO(img_data))
            img_name = os.path.basename(full_img_url.split('?')[0])
            if not img_name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp")):
                img_name += ".jpg"
            img_path = os.path.join(pasta_destino, img_name)
            img.convert("RGB").save(img_path, "JPEG")
            return True
        except Exception as e:
            print(f"Erro ao baixar imagem: {e}")
            return False

    def processarURLs(self, urls, pasta_nome):
        self.status_label.configure(text="📥 Baixando imagens...")
        try:
            pasta_destino = os.path.join("imagens", pasta_nome)
            os.makedirs(pasta_destino, exist_ok=True)

            total_baixadas = 0
            for url in urls:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')

                img_tags = soup.find_all('img')
                full_img_urls = [
                    urljoin(url, img.get('src')) for img in img_tags if img.get('src')
                ]

                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                    resultados = list(executor.map(lambda img: self.baixar_imagem(img, pasta_destino), full_img_urls))
                    total_baixadas += sum(resultados)

            if total_baixadas > 0:
                self.status_label.configure(text=f"✅ {total_baixadas} imagem(ns) salvas em {pasta_destino}")
            else:
                self.status_label.configure(text="⚠️ Nenhuma imagem encontrada.")

        except Exception as e:
            self.status_label.configure(text=f"❌ Erro: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
