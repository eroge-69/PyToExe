import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import ctypes

# Força o Windows a usar o ícone na taskbar
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"youtube.downloader")

# Configurações do CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")  # Tema com aparência escura e próxima de roxo escuro

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("600x320")
        self.resizable(False, False)

        # Ícone personalizado
        self.iconbitmap("favicon.ico")

        # --- Widgets ---

        self.label_link = ctk.CTkLabel(self, text="Link do YouTube:", anchor="w")
        self.label_link.pack(padx=20, pady=(20, 5), fill='x')

        self.link_entry = ctk.CTkEntry(self, width=560)
        self.link_entry.pack(padx=20, fill='x')

        self.label_path = ctk.CTkLabel(self, text="Pasta para salvar:", anchor="w")
        self.label_path.pack(padx=20, pady=(15, 5), fill='x')

        frame_path = ctk.CTkFrame(self)
        frame_path.pack(padx=20, fill='x')

        self.path_var = ctk.StringVar(value=os.getcwd())
        self.path_entry = ctk.CTkEntry(frame_path, textvariable=self.path_var)
        self.path_entry.pack(side="left", fill='x', expand=True, pady=5)

        self.browse_button = ctk.CTkButton(frame_path, text="Selecionar", width=80, command=self.selecionar_pasta)
        self.browse_button.pack(side="left", padx=10, pady=5)

        self.label_tipo = ctk.CTkLabel(self, text="Tipo de download:", anchor="w")
        self.label_tipo.pack(padx=20, pady=(15, 5), fill='x')

        self.tipo_download = ctk.StringVar(value="video")
        frame_tipo = ctk.CTkFrame(self)
        frame_tipo.pack(padx=20, fill='x')

        self.radio_video = ctk.CTkRadioButton(frame_tipo, text="Vídeo", variable=self.tipo_download, value="video")
        self.radio_video.pack(side="left", padx=10, pady=5)

        self.radio_audio = ctk.CTkRadioButton(frame_tipo, text="Áudio (MP3)", variable=self.tipo_download, value="audio")
        self.radio_audio.pack(side="left", padx=10, pady=5)

        self.download_button = ctk.CTkButton(self, text="Baixar", width=120, height=40, command=self.iniciar_download)
        self.download_button.pack(pady=20)

        self.progress = ctk.CTkProgressBar(self, width=560)
        self.progress.set(0)
        self.progress.pack(padx=20, pady=(5, 10), fill='x')

        self.status_label = ctk.CTkLabel(self, text="", anchor="center")
        self.status_label.pack(padx=20)

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory(initialdir=self.path_var.get())
        if pasta:
            self.path_var.set(pasta)

    def iniciar_download(self):
        link = self.link_entry.get().strip()
        pasta = self.path_var.get().strip()
        tipo = self.tipo_download.get()

        if not link:
            messagebox.showerror("Erro", "Por favor, insira o link do vídeo.")
            return
        if not pasta or not os.path.isdir(pasta):
            messagebox.showerror("Erro", "Por favor, selecione uma pasta válida.")
            return

        self.download_button.configure(state="disabled")
        self.progress.set(0)
        self.status_label.configure(text="Iniciando download...")

        threading.Thread(target=self.baixar_video, args=(link, pasta, tipo), daemon=True).start()

    def baixar_video(self, link, pasta, tipo):
        ydl_opts = {
            'outtmpl': os.path.join(pasta, '%(title)s.%(ext)s'),
            'quiet': True,
            'progress_hooks': [self.progress_hook],
        }

        if tipo == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                # Adicione o caminho do seu ffmpeg se necessário
            })
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                'merge_output_format': 'mp4',
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            self.status_label.configure(text=f"✅ Download concluído!\nArquivo salvo em:\n{os.path.abspath(pasta)}")
            self.progress.set(1)
            messagebox.showinfo("Download concluído", "O download foi concluído com sucesso!")
        except Exception as e:
            self.status_label.configure(text=f"❌ Erro: {e}")
            self.progress.set(0)
        finally:
            self.download_button.configure(state="normal")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                percent = float(d.get('_percent_str', '0%').strip().replace('%','')) / 100
            except:
                percent = 0
            eta = d.get('_eta_str', '').strip()
            self.progress.set(percent)
            self.status_label.configure(text=f"Baixando... {int(percent*100)}% - ETA: {eta}")
        elif d['status'] == 'finished':
            self.status_label.configure(text="Download finalizado, processando arquivo...")

if __name__ == "__main__":
    app = App()
    app.mainloop()
