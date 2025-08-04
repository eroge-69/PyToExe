
import os
import shutil
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

def organizar_fotos(pasta_origem, pasta_destino):
    pasta_origem = Path(pasta_origem)
    pasta_destino = Path(pasta_destino)

    if not pasta_origem.exists() or not pasta_destino.exists():
        messagebox.showerror("Erro", "Verifica se ambas as pastas existem.")
        return

    for ficheiro in pasta_origem.glob("*"):
        if ficheiro.is_file():
            try:
                timestamp = ficheiro.stat().st_mtime
                data = datetime.fromtimestamp(timestamp)
                ano = str(data.year)
                mes = f"{data.month:02d}"
                destino = pasta_destino / ano / mes
                destino.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ficheiro, destino / ficheiro.name)
            except Exception as e:
                print(f"Erro ao processar {ficheiro.name}: {e}")

    messagebox.showinfo("Concluído", "✅ As fotos foram organizadas com sucesso!")

def escolher_pasta_origem():
    pasta = filedialog.askdirectory(title="Selecionar pasta com fotos")
    if pasta:
        entrada_origem.delete(0, tk.END)
        entrada_origem.insert(0, pasta)

def escolher_pasta_destino():
    pasta = filedialog.askdirectory(title="Selecionar pasta de destino")
    if pasta:
        entrada_destino.delete(0, tk.END)
        entrada_destino.insert(0, pasta)

# Interface gráfica
janela = tk.Tk()
janela.title("Organizador de Fotos por Ano/Mês")
janela.geometry("500x200")

tk.Label(janela, text="Pasta com fotos:").pack(pady=5)
entrada_origem = tk.Entry(janela, width=60)
entrada_origem.pack()
tk.Button(janela, text="Selecionar pasta", command=escolher_pasta_origem).pack(pady=5)

tk.Label(janela, text="Pasta de destino:").pack(pady=5)
entrada_destino = tk.Entry(janela, width=60)
entrada_destino.pack()
tk.Button(janela, text="Selecionar pasta", command=escolher_pasta_destino).pack(pady=5)

tk.Button(janela, text="📂 Organizar Fotos", command=lambda: organizar_fotos(entrada_origem.get(), entrada_destino.get()), bg="lightblue").pack(pady=10)

janela.mainloop()
