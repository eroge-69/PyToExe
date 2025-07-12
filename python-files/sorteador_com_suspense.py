
import csv
import random
import time
import tkinter as tk
from tkinter import filedialog, messagebox

def carregar_csv():
    caminho_arquivo = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not caminho_arquivo:
        return None

    participantes = []
    with open(caminho_arquivo, newline='', encoding='utf-8') as csvfile:
        leitor = csv.reader(csvfile)
        cabecalho = next(leitor)

        for linha in leitor:
            if len(linha) >= 3:
                nome = linha[0].strip()
                telefone = linha[1].strip()
                cidade = linha[2].strip()
                participantes.append((nome, telefone, cidade))
    return participantes

def sortear():
    participantes = carregar_csv()
    if not participantes:
        messagebox.showerror("Erro", "Nenhum participante carregado.")
        return

    janela = tk.Toplevel()
    janela.title("Sorteando...")
    janela.geometry("400x150")
    label = tk.Label(janela, text="Iniciando sorteio...", font=("Arial", 16))
    label.pack(expand=True)

    janela.update()

    for _ in range(20):
        sorteio_temp = random.choice(participantes)
        label.config(text=f"Sorteando: {sorteio_temp[0]}")
        janela.update()
        time.sleep(0.1 + random.random() * 0.1)

    sorteado = random.choice(participantes)
    label.config(text=f"🎉 Sorteado:\n{sorted(sorteado)[0]}\n📱 {sorteado[1]}\n🏙️ {sorteado[2]}")
    janela.update()

root = tk.Tk()
root.title("Sorteador de Participantes")
root.geometry("400x200")

titulo = tk.Label(root, text="Sorteio com Suspense", font=("Arial", 18))
titulo.pack(pady=10)

btn_sortear = tk.Button(root, text="Carregar CSV e Sortear", font=("Arial", 14), command=sortear)
btn_sortear.pack(pady=20)

root.mainloop()
