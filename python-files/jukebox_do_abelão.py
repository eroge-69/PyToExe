
import tkinter as tk
from tkinter import filedialog
import pygame
import os

class Jukebox:
    def __init__(self, root):
        self.root = root
        self.root.title("Jukebox do Abelão")
        self.root.geometry("400x400")
        self.root.config(bg="#111")

        pygame.mixer.init()

        self.musicas = []
        self.index_atual = 0

        self.label = tk.Label(root, text="🎵 Jukebox do Abelão", bg="#111", fg="white", font=("Arial", 18))
        self.label.pack(pady=10)

        self.lista = tk.Listbox(root, bg="#333", fg="white", selectbackground="#555", font=("Arial", 12))
        self.lista.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.lista.bind("<<ListboxSelect>>", self.selecionar_musica)

        self.botoes_frame = tk.Frame(root, bg="#111")
        self.botoes_frame.pack(pady=10)

        tk.Button(self.botoes_frame, text="▶️ Play", command=self.tocar).grid(row=0, column=0, padx=5)
        tk.Button(self.botoes_frame, text="⏸️ Pause", command=self.pausar).grid(row=0, column=1, padx=5)
        tk.Button(self.botoes_frame, text="⏭️ Próxima", command=self.proxima).grid(row=0, column=2, padx=5)
        tk.Button(self.botoes_frame, text="➕ Adicionar", command=self.adicionar_musicas).grid(row=0, column=3, padx=5)

    def adicionar_musicas(self):
        arquivos = filedialog.askopenfilenames(filetypes=[("Arquivos MP3", "*.mp3")])
        for arquivo in arquivos:
            self.musicas.append(arquivo)
            self.lista.insert(tk.END, os.path.basename(arquivo))

    def selecionar_musica(self, event):
        try:
            self.index_atual = self.lista.curselection()[0]
            self.tocar()
        except IndexError:
            pass

    def tocar(self):
        if self.musicas:
            pygame.mixer.music.load(self.musicas[self.index_atual])
            pygame.mixer.music.play()

    def pausar(self):
        pygame.mixer.music.pause()

    def proxima(self):
        if self.musicas:
            self.index_atual = (self.index_atual + 1) % len(self.musicas)
            self.tocar()
            self.lista.select_clear(0, tk.END)
            self.lista.select_set(self.index_atual)

if __name__ == "__main__":
    root = tk.Tk()
    app = Jukebox(root)
    root.mainloop()
