
import tkinter as tk
from tkinter import messagebox

# Pontuações iniciais
grupo_a = 0
grupo_b = 0

# Metas
meta_a = 28
meta_b = 128

# Função para adicionar ponto
def adicionar_ponto(grupo):
    global grupo_a, grupo_b
    if grupo == "A":
        grupo_a += 1
        label_a.config(text=f"Grupo A (Expedição): {grupo_a} pontos")
        if grupo_a == meta_a:
            messagebox.showinfo("Meta A atingida", f"Você atingiu {meta_a} pontos no Grupo A!")
    elif grupo == "B":
        grupo_b += 1
        label_b.config(text=f"Grupo B (Movimentação): {grupo_b} pontos")
        if grupo_b == meta_b:
            messagebox.showinfo("Meta B atingida", f"Você atingiu {meta_b} pontos no Grupo B!")

# Interface
janela = tk.Tk()
janela.title("Contador de Pontos")
janela.geometry("400x400")
janela.resizable(False, False)

tk.Label(janela, text="Contador de Pontos", font=("Arial", 16, "bold")).pack(pady=10)

label_a = tk.Label(janela, text="Grupo A (Expedição): 0 pontos", font=("Arial", 12))
label_a.pack(pady=5)

label_b = tk.Label(janela, text="Grupo B (Movimentação): 0 pontos", font=("Arial", 12))
label_b.pack(pady=5)

frame_a = tk.LabelFrame(janela, text="Grupo A - Expedição", padx=10, pady=10)
frame_a.pack(pady=10)

botoes_a = ["Certidão", "Documento", "Histórico de Parte", "Termo"]
for nome in botoes_a:
    tk.Button(frame_a, text=nome, width=25, command=lambda n=nome: adicionar_ponto("A")).pack(pady=2)

frame_b = tk.LabelFrame(janela, text="Grupo B - Movimentação", padx=10, pady=10)
frame_b.pack(pady=10)

tk.Button(frame_b, text="Movimento", width=25, command=lambda: adicionar_ponto("B")).pack(pady=2)

janela.mainloop()
