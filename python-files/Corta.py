# Certifique-se de ter instalado: pip install moviepy opencv-python

import cv2
import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip 

def cortar_video(video_path, duracoes):
    """
    Corta um vídeo em segmentos de durações especificadas usando MoviePy.
    O MoviePy é usado para garantir a remoção robusta de metadados.
    """
    nome_arquivo = os.path.splitext(os.path.basename(video_path))[0]
    saida_dir = os.path.join("saidas", nome_arquivo)
    os.makedirs(saida_dir, exist_ok=True)

    log = []
    
    try:
        # Carrega o clipe de vídeo com MoviePy para facilitar o corte e metadados
        clip = VideoFileClip(video_path)
    except Exception as e:
        messagebox.showerror("Erro de Carregamento", f"Não foi possível carregar o vídeo com MoviePy. Verifique a instalação do FFmpeg. Erro: {e}")
        return

    duracao_segundos = clip.duration
    log.append(f"Arquivo: {nome_arquivo}")
    log.append(f"Duração total: {duracao_segundos:.2f} segundos")

    for duracao in duracoes:
        log.append(f"\n>> Cortando em segmentos de {duracao} segundos...")
        
        partes = math.ceil(duracao_segundos / duracao)
        log.append(f"Isso gera {partes} partes de aproximadamente {duracao}s:")

        for i in range(partes):
            inicio = i * duracao
            # Garante que o fim não ultrapasse a duração total do vídeo
            fim = min((i + 1) * duracao, duracao_segundos)
            
            # Subclip: O método de corte nativo do MoviePy
            subclip = clip.subclip(inicio, fim)
            
            output_path = os.path.join(saida_dir, f"{nome_arquivo}_{duracao}s_p{i+1}.mp4")
            
            log.append(f"[SALVANDO] Parte {i+1}: {inicio:.2f}s → {fim:.2f}s em {output_path}")

            # --- PARTE DE LIMPEZA DE METADADOS ---
            try:
                subclip.write_videofile(
                    output_path, 
                    codec="libx264", 
                    audio_codec="aac",
                    temp_audiofile='temp-audio.m4a', 
                    remove_temp=True,
                    ffmpeg_params=['-map_metadata', '-1', '-movflags', 'faststart'], 
                    logger=None 
                )
            except Exception as e:
                log.append(f"ERRO ao escrever a parte {i+1}: {e}")
                continue


    clip.close() 
    log.append("\n✅ Finalizado! Os arquivos estão limpos de metadados e salvos na pasta 'saidas'.")
    messagebox.showinfo("Concluído", "\n".join(log))

def selecionar_video():
    video_path = filedialog.askopenfilename(
        filetypes=[("Arquivos de Vídeo", "*.mp4;*.avi;*.mov;*.mkv")]
    )
    if video_path:
        entrada_video.set(video_path)

def executar():
    video_path = entrada_video.get()
    if not video_path:
        messagebox.showerror("Erro", "Selecione um vídeo primeiro.")
        return

    duracoes = []
    if var15.get(): duracoes.append(15)
    if var30.get(): duracoes.append(30)
    if var60.get(): duracoes.append(60)

    custom = entrada_custom.get().strip()
    if custom:
        try:
            custom_duracoes = [int(x.strip()) for x in custom.split(",") if x.strip().isdigit() and int(x.strip()) > 0]
            duracoes.extend(custom_duracoes)
        except:
            messagebox.showerror("Erro", "Duração personalizada inválida. Use apenas números inteiros separados por vírgula.")
            return

    duracoes = sorted(list(set(duracoes)))

    if not duracoes:
        messagebox.showerror("Erro", "Selecione pelo menos uma duração válida.")
        return

    cortar_video(video_path, duracoes)

# --- GUI (Interface Gráfica) ---
root = tk.Tk()
root.title("Cortador e Limpador de Metadados (v3.0)")

entrada_video = tk.StringVar()
entrada_custom = tk.StringVar()
var15 = tk.BooleanVar()
var30 = tk.BooleanVar()
var60 = tk.BooleanVar()

tk.Label(root, text="Selecione o vídeo:").pack(pady=5)
tk.Entry(root, textvariable=entrada_video, width=50).pack(pady=5, padx=10)
tk.Button(root, text="Escolher...", command=selecionar_video).pack(pady=5)

tk.Label(root, text="Escolha as durações (segundos):").pack(pady=5)
tk.Checkbutton(root, text="15s", variable=var15).pack(anchor="w", padx=10)
tk.Checkbutton(root, text="30s", variable=var30).pack(anchor="w", padx=10)
tk.Checkbutton(root, text="60s", variable=var60).pack(anchor="w", padx=10)

tk.Label(root, text="Personalizado (ex: 10,45,120):").pack(pady=5)
tk.Entry(root, textvariable=entrada_custom, width=30).pack(pady=5)

tk.Button(root, text="Cortar e Limpar Metadados", command=executar, bg="#4CAF50", fg="white", font=('Arial', 10, 'bold')).pack(pady=15)

root.mainloop()