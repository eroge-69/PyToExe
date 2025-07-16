import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.config import change_settings

# Configura o caminho do ImageMagick
os.environ['IMAGEMAGICK_BINARY'] = r'C:\Program Files\ImageMagick-7.1.2-Q16\magick.exe'
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16\magick.exe"})

def buscar_legenda_auto(video_path):
    nome_base = os.path.splitext(os.path.basename(video_path))[0].lower() + ".txt"
    for root, dirs, files in os.walk("C:\\"):
        for file in files:
            if file.lower() == nome_base:
                return os.path.join(root, file)
    return None

def split_text_in_chunks(text, max_words_per_chunk=10):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words_per_chunk):
        chunk = ' '.join(words[i:i+max_words_per_chunk])
        chunks.append(chunk)
    return chunks

def criar_video_com_legenda(video_path, legenda_path, save_path):
    video = VideoFileClip(video_path)

    with open(legenda_path, 'r', encoding='utf-8') as f:
        full_text = f.read().strip()

    blocos = split_text_in_chunks(full_text, max_words_per_chunk=10)
    duracao_por_bloco = max(video.duration / len(blocos), 2)

    textos = []
    for i, bloco in enumerate(blocos):
        txt_clip = TextClip(bloco,
                            fontsize=40,
                            font='Arial-Bold',
                            color='white',
                            method='caption',
                            size=(video.w * 0.8, None),
                            align='center')

        bg_clip = ColorClip(size=txt_clip.size, color=(0, 0, 0)).set_opacity(0.6)

        pos = ('center', 'center')
        start = i * duracao_por_bloco

        txt_clip = txt_clip.set_position(pos).set_start(start).set_duration(duracao_por_bloco)
        bg_clip = bg_clip.set_position(pos).set_start(start).set_duration(duracao_por_bloco)

        textos.append(bg_clip)
        textos.append(txt_clip)

    video_final = CompositeVideoClip([video, *textos])

    video_final.write_videofile(save_path, codec='libx264', audio_codec='aac')


def processar_lote(videos_folder, output_folder, auto_legenda=True, legenda_manual=None):
    for file in os.listdir(videos_folder):
        if file.lower().endswith(('.mp4', '.avi', '.mov')):
            video_path = os.path.join(videos_folder, file)
            legenda_path = legenda_manual
            if auto_legenda:
                found = buscar_legenda_auto(video_path)
                if found:
                    legenda_path = found
                    print(f"Legenda encontrada para {file}: {legenda_path}")
                else:
                    print(f"Nenhuma legenda automática encontrada para {file}.")
            if not legenda_path or not os.path.isfile(legenda_path):
                print(f"Legenda ausente para {file}, pulando.")
                continue

            output_path = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_com_legenda.mp4")
            print(f"Processando: {file}")
            criar_video_com_legenda(video_path, legenda_path, output_path)
            print(f"Salvo em: {output_path}")
    print("✅ Processamento em lote concluído!")


# 🎨 Interface com tkinter
def selecionar_pastas():
    root = tk.Tk()
    root.withdraw()

    videos_folder = filedialog.askdirectory(title="Selecione a pasta com os vídeos")
    if not videos_folder:
        messagebox.showerror("Erro", "Nenhuma pasta de vídeos selecionada.")
        return

    output_folder = filedialog.askdirectory(title="Selecione a pasta para salvar os vídeos finais")
    if not output_folder:
        messagebox.showerror("Erro", "Nenhuma pasta de saída selecionada.")
        return

    if messagebox.askyesno("Legenda automática?", "Deseja que o programa procure a legenda automaticamente para cada vídeo?"):
        auto_legenda = True
        legenda_manual = None
    else:
        auto_legenda = False
        legenda_manual = filedialog.askopenfilename(title="Selecione a legenda para todos os vídeos",
                                                     filetypes=[("Arquivos de texto", "*.txt")])
        if not legenda_manual:
            messagebox.showerror("Erro", "Nenhuma legenda selecionada.")
            return

    processar_lote(videos_folder, output_folder, auto_legenda, legenda_manual)


if __name__ == '__main__':
    selecionar_pastas()
