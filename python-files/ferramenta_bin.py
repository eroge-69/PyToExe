# Nome do arquivo: ferramenta_bin.py

import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import threading

# --- Funções de Lógica (copiadas do nosso script do Colab) ---

def extrair_blocos_completos(caminho_arquivo_entrada, status_callback):
    """Lê o arquivo original e salva cada bloco de 2352 bytes intacto em uma lista."""
    try:
        status_callback("Lendo e processando o arquivo...")
        
        lista_de_blocos = []
        tamanho_bloco_inteiro = 0x930  # 2352 bytes

        with open(caminho_arquivo_entrada, 'rb') as f:
            while True:
                bloco_inteiro = f.read(tamanho_bloco_inteiro)
                if not bloco_inteiro:
                    break
                lista_de_blocos.append(bloco_inteiro.hex())

        base, ext = os.path.splitext(caminho_arquivo_entrada)
        caminho_blocos_json = f"{base}_blocos_completos.json"

        with open(caminho_blocos_json, 'w') as f:
            json.dump(lista_de_blocos, f)
        
        status_callback(f"Extração concluída!\nArquivo de blocos salvo em:\n{caminho_blocos_json}")
        messagebox.showinfo("Sucesso", f"Extração concluída!\nArquivo de blocos salvo em:\n{caminho_blocos_json}")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro durante a extração:\n{e}")
        status_callback("Pronto.")

def remontar_a_partir_dos_blocos(caminho_base, status_callback):
    """Lê o JSON com a lista de blocos e os junta para recriar o arquivo original."""
    try:
        base, ext = os.path.splitext(caminho_base)
        caminho_blocos_json = f"{base}_blocos_completos.json"

        if not os.path.exists(caminho_blocos_json):
            messagebox.showerror("Erro", f"Arquivo de restauração não encontrado:\n{caminho_blocos_json}\n\nExecute a extração primeiro.")
            status_callback("Pronto.")
            return

        status_callback(f"Lendo o arquivo de restauração...")
        with open(caminho_blocos_json, 'r') as f:
            lista_de_blocos_hex = json.load(f)

        status_callback("Juntando todos os blocos...")
        dados_reconstruidos = b"".join([bytes.fromhex(bloco) for bloco in lista_de_blocos_hex])

        caminho_arquivo_reconstruido = f"{base}_restaurado.bin"
        with open(caminho_arquivo_reconstruido, 'wb') as f:
            f.write(dados_reconstruidos)

        status_callback(f"Remontagem concluída!\nArquivo restaurado salvo em:\n{caminho_arquivo_reconstruido}")
        messagebox.showinfo("Sucesso", f"Remontagem concluída!\nArquivo restaurado salvo em:\n{caminho_arquivo_reconstruido}")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro durante a remontagem:\n{e}")
        status_callback("Pronto.")

# --- Classe da Interface Gráfica ---

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Ferramenta de Arquivos BIN")
        self.root.geometry("450x200")

        self.label = tk.Label(root, text="Selecione uma ação", font=("Helvetica", 12))
        self.label.pack(pady=10)

        self.btn_extrair = tk.Button(root, text="1. Extrair Blocos Completos", command=self.run_extrair, width=30, height=2)
        self.btn_extrair.pack(pady=5)

        self.btn_remontar = tk.Button(root, text="2. Remontar a Partir dos Blocos", command=self.run_remontar, width=30, height=2)
        self.btn_remontar.pack(pady=5)
        
        self.status_label = tk.Label(root, text="Pronto.", fg="grey")
        self.status_label.pack(side="bottom", fill="x")

    def run_in_thread(self, target_func, *args):
        # Roda a função pesada em uma thread separada para não travar a interface
        thread = threading.Thread(target=target_func, args=args)
        thread.start()

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def run_extrair(self):
        filepath = filedialog.askopenfilename(title="Selecione o arquivo .bin original")
        if not filepath:
            return
        self.update_status("Iniciando extração...")
        self.run_in_thread(extrair_blocos_completos, filepath, self.update_status)

    def run_remontar(self):
        filepath = filedialog.askopenfilename(title="Selecione o arquivo .bin original (para referência)")
        if not filepath:
            return
        self.update_status("Iniciando remontagem...")
        self.run_in_thread(remontar_a_partir_dos_blocos, filepath, self.update_status)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()