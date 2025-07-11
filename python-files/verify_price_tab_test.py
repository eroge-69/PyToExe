import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import re

def validar_arquivo():
    arquivo = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if not arquivo:
        return

    resultado_texto.delete(1.0, tk.END)
    linha_arq = 0
    erro = 0

    try:
        with open(arquivo, "r", encoding="utf-8") as arq:
            for linha in arq:
                linha_arq += 1
                partes = linha.strip().split("|")

                if len(partes) < 4:
                    if partes[0] == "":
                        pass
                    else:
                        resultado_texto.insert(tk.END, f"linha {linha_arq} em formato incorreto --> {linha}")
                        erro += 1
                else:
                    if partes[0] == "":
                        resultado_texto.insert(tk.END, f"linha {linha_arq} está sem o código de barras --> {linha}")
                        erro += 1
                    if partes[1] == "":
                        resultado_texto.insert(tk.END, f"linha {linha_arq} está sem descrição --> {linha}")
                        erro += 1
                    if partes[2] == "":
                        resultado_texto.insert(tk.END, f"linha {linha_arq} está sem preço 1 --> {linha}")
                        erro += 1

        if erro == 0:
            resultado_texto.insert(tk.END, "Arquivo está em conformidade!\n")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao ler o arquivo: {e}")

def copiar_texto():
    texto = resultado_texto.get(1.0, tk.END)
    root.clipboard_clear()
    root.clipboard_append(texto)
    messagebox.showinfo("Copiado", "Texto copiado para a área de transferência!")

# Interface
root = tk.Tk()
root.title("Validador de Arquivo de Preços")

btn_abrir = tk.Button(root, text="Selecionar Arquivo", command=validar_arquivo)
btn_abrir.pack(pady=5)

resultado_texto = scrolledtext.ScrolledText(root, width=100, height=25, state='normal')
resultado_texto.pack(padx=10, pady=5)

btn_copiar = tk.Button(root, text="Copiar Resultado", command=copiar_texto)
btn_copiar.pack(pady=5)

root.mainloop()