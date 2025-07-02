import tkinter as tk
from tkinter import filedialog, messagebox
from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile
import datetime

def gerar_video(texto, output_path):
    try:
        # Criar áudio com gTTS
        tts = gTTS(texto, lang='pt')
        temp_audio = os.path.join(tempfile.gettempdir(), "temp_audio.mp3")
        tts.save(temp_audio)

        # Duração do áudio
        audio = AudioFileClip(temp_audio)
        duracao_audio = audio.duration

        # Criar imagem com o texto centralizado
        largura, altura = 1280, 720
        img = Image.new('RGB', (largura, altura), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        font_path = "arial.ttf"  # Substitua se quiser uma fonte personalizada
        try:
            fonte = ImageFont.truetype(font_path, 48)
        except:
            fonte = ImageFont.load_default()

        linhas = []
        largura_max = largura - 100
        palavras = texto.split()
        linha_atual = ""
        for palavra in palavras:
            if draw.textlength(linha_atual + " " + palavra, font=fonte) < largura_max:
                linha_atual += " " + palavra
            else:
                linhas.append(linha_atual.strip())
                linha_atual = palavra
        linhas.append(linha_atual.strip())

        y_texto = altura // 2 - len(linhas) * 30
        for linha in linhas:
            largura_linha = draw.textlength(linha, font=fonte)
            draw.text(((largura - largura_linha) / 2, y_texto), linha, font=fonte, fill="white")
            y_texto += 60

        imagem_path = os.path.join(tempfile.gettempdir(), "temp_imagem.png")
        img.save(imagem_path)

        # Criar vídeo com imagem e áudio
        clip_imagem = ImageClip(imagem_path).set_duration(duracao_audio)
        clip_imagem = clip_imagem.set_audio(audio)
        clip_imagem = clip_imagem.set_fps(24)

        clip_imagem.write_videofile(output_path, codec="libx264", audio_codec="aac")

        os.remove(temp_audio)
        os.remove(imagem_path)

    except Exception as e:
        messagebox.showerror("Erro ao gerar vídeo", str(e))

def salvar_video():
    texto = texto_input.get("1.0", tk.END).strip()
    if not texto:
        messagebox.showwarning("Aviso", "Digite algum texto para gerar o vídeo.")
        return

    caminho_saida = filedialog.asksaveasfilename(defaultextension=".mp4",
                                                 filetypes=[("Vídeo MP4", "*.mp4")],
                                                 title="Salvar vídeo como")
    if not caminho_saida:
        return

    btn_gerar.config(state="disabled")
    lbl_status.config(text="⏳ Gerando vídeo...")
    root.update()

    gerar_video(texto, caminho_saida)

    lbl_status.config(text="✅ Vídeo salvo com sucesso!")
    btn_gerar.config(state="normal")

# Interface gráfica
root = tk.Tk()
root.title("Gerador de Vídeo com Narração")
root.geometry("600x400")
root.resizable(False, False)

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(fill="both", expand=True)

lbl_titulo = tk.Label(frame, text="Digite o texto a ser narrado:", font=("Arial", 14))
lbl_titulo.pack()

texto_input = tk.Text(frame, height=10, font=("Arial", 12), wrap=tk.WORD)
texto_input.pack(fill="both", expand=True, pady=10)

btn_gerar = tk.Button(frame, text="🎬 Gerar Vídeo", font=("Arial", 12), bg="#4CAF50", fg="white", command=salvar_video)
btn_gerar.pack(pady=10)

lbl_status = tk.Label(frame, text="", font=("Arial", 11), fg="gray")
lbl_status.pack()

root.mainloop()
