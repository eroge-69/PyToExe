import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import csv

def carregar_csv():
    caminho = filedialog.askopenfilename(
        title="Selecione o arquivo CSV",
        filetypes=[("Arquivos CSV", "*.csv")]
    )
    if caminho:
        try:
            coluna = simpledialog.askinteger(
                "Coluna",
                "Digite o número da coluna (1 para a primeira):",
                minvalue=1
            )
            if coluna is None:
                return  # Usuário cancelou
            
            with open(caminho, "r", encoding="utf-8") as f:
                leitor = csv.reader(f)
                global dados_csv
                dados_csv = {linha[coluna-1].strip().lower()
                             for linha in leitor if len(linha) >= coluna and linha[coluna-1].strip()}
            messagebox.showinfo("Arquivo carregado", f"{len(dados_csv)} itens carregados da coluna {coluna}.")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler o arquivo CSV:\n{e}")

def comparar_texto():
    if not dados_csv:
        messagebox.showwarning("Aviso", "Carregue primeiro o arquivo CSV.")
        return
    
    texto_usuario = entrada.get("1.0", tk.END).strip()
    itens_usuario = {linha.strip().lower() for linha in texto_usuario.split("\n") if linha.strip()}
    
    repetidos = sorted(itens_usuario & dados_csv)  # interseção
    
    saida.delete("1.0", tk.END)
    if repetidos:
        saida.insert(tk.END, "\n".join(repetidos))
    else:
        saida.insert(tk.END, "Nenhum item repetido encontrado.")

# Janela principal
root = tk.Tk()
root.title("Comparador de Texto com CSV")
root.geometry("750x400")

dados_csv = set()

# Botões
frame_botoes = tk.Frame(root)
frame_botoes.pack(fill=tk.X, pady=5)

btn_csv = tk.Button(frame_botoes, text="Carregar CSV", command=carregar_csv)
btn_csv.pack(side=tk.LEFT, padx=5)

btn_comparar = tk.Button(frame_botoes, text="Comparar", command=comparar_texto)
btn_comparar.pack(side=tk.LEFT, padx=5)

# Área de texto - duas colunas
frame_textos = tk.Frame(root)
frame_textos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

entrada = tk.Text(frame_textos, width=40)
entrada.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

saida = tk.Text(frame_textos, width=40, bg="#f0f0f0")
saida.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root.mainloop()