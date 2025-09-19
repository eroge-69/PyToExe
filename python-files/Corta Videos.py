import cv2
import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox

def cortar_video(video_path, duracoes):
    nome_arquivo = os.path.splitext(os.path.basename(video_path))[0]
    saida_dir = os.path.join("saidas", nome_arquivo)
    os.makedirs(saida_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        messagebox.showerror("Erro", "Não foi possível abrir o vídeo.")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duracao_segundos = total_frames / fps
    largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    altura = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    log = []
    log.append(f"Arquivo: {nome_arquivo}")
    log.append(f"Duração total: {duracao_segundos:.2f} segundos ({total_frames} frames, {fps} FPS)")

    for duracao in duracoes:
        log.append(f"\n>> Cortando em segmentos de {duracao} segundos...")
        partes = math.ceil(duracao_segundos / duracao)
        log.append(f"Isso gera {partes} partes:")

        for i in range(partes):
            inicio = i * duracao
            fim = min((i + 1) * duracao, duracao_segundos)
            log.append(f"Parte {i+1}: {inicio:.2f}s → {fim:.2f}s")

        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        parte = 1
        frame_count = 0
        out = None
        frames_por_segmento = duracao * fps

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frames_por_segmento == 0:
                if out:
                    out.release()
                output_path = os.path.join(saida_dir, f"{nome_arquivo}{parte}.mp4")
                out = cv2.VideoWriter(
                    output_path,
                    cv2.VideoWriter_fourcc(*'mp4v'),
                    fps,
                    (largura, altura)
                )
                log.append(f"[SALVANDO] {output_path}")
                parte += 1

            out.write(frame)
            frame_count += 1

        if out:
            out.release()
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    cap.release()
    log.append("\n✅ Finalizado!")
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
            custom_duracoes = [int(x.strip()) for x in custom.split(",") if x.strip().isdigit()]
            duracoes.extend(custom_duracoes)
        except:
            messagebox.showerror("Erro", "Duração personalizada inválida.")
            return

    if not duracoes:
        messagebox.showerror("Erro", "Selecione pelo menos uma duração.")
        return

    cortar_video(video_path, duracoes)

# GUI
root = tk.Tk()
root.title("Cortar Vídeo")

entrada_video = tk.StringVar()
entrada_custom = tk.StringVar()
var15 = tk.BooleanVar()
var30 = tk.BooleanVar()
var60 = tk.BooleanVar()

tk.Label(root, text="Selecione o vídeo:").pack(pady=5)
tk.Entry(root, textvariable=entrada_video, width=50).pack(pady=5)
tk.Button(root, text="Escolher...", command=selecionar_video).pack(pady=5)

tk.Label(root, text="Escolha as durações (segundos):").pack(pady=5)
tk.Checkbutton(root, text="15s", variable=var15).pack(anchor="w")
tk.Checkbutton(root, text="30s", variable=var30).pack(anchor="w")
tk.Checkbutton(root, text="60s", variable=var60).pack(anchor="w")

tk.Label(root, text="Personalizado (ex: 10,45,120):").pack(pady=5)
tk.Entry(root, textvariable=entrada_custom, width=30).pack(pady=5)

tk.Button(root, text="Cortar Vídeo", command=executar, bg="green", fg="white").pack(pady=10)

root.mainloop()
