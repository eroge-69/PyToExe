import tkinter as tk
from tkinter import filedialog, messagebox

def carregar_arquivo():
    caminho = filedialog.askopenfilename(
        title="Selecione o arquivo de comparação",
        filetypes=[("Arquivos de texto", "*.txt")]
    )
    if caminho:
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                global dados_arquivo
                # Normaliza para minúsculas e remove espaços extras
                dados_arquivo = {linha.strip().lower() for linha in f if linha.strip()}
            messagebox.showinfo("Arquivo carregado", f"{len(dados_arquivo)} itens carregados.")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler o arquivo:\n{e}")

def comparar_texto():
    if not dados_arquivo:
        messagebox.showwarning("Aviso", "Carregue primeiro o arquivo de comparação.")
        return
    
    texto_usuario = entrada.get("1.0", tk.END).strip()
    itens_usuario = {linha.strip().lower() for linha in texto_usuario.split("\n") if linha.strip()}
    
    repetidos = sorted(itens_usuario & dados_arquivo)  # Interseção dos conjuntos
    
    saida.delete("1.0", tk.END)
    if repetidos:
        saida.insert(tk.END, "\n".join(repetidos))
    else:
        saida.insert(tk.END, "Nenhum item repetido encontrado.")

# Janela principal
root = tk.Tk()
root.title("Comparador de Texto")
root.geometry("700x400")

dados_arquivo = set()

# Botões
frame_botoes = tk.Frame(root)
frame_botoes.pack(fill=tk.X, pady=5)

btn_arquivo = tk.Button(frame_botoes, text="Carregar Arquivo", command=carregar_arquivo)
btn_arquivo.pack(side=tk.LEFT, padx=5)

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