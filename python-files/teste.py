import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from pdf2image import convert_from_path

pasta_destino = ""
arquivos_selecionados = []

def ao_alterar_checkbox():
    global pasta_destino
    if destino_var.get():
        pasta = filedialog.askdirectory(title="Selecione a pasta de destino")
        if pasta:
            pasta_destino = pasta
            caminho_label.config(text=f"Pasta de destino: {pasta_destino}")
        else:
            destino_var.set(False)
            pasta_destino = ""
            caminho_label.config(text="")
    else:
        pasta_destino = ""
        caminho_label.config(text="")

def selecionar_arquivos():
    global arquivos_selecionados
    arquivos = filedialog.askopenfilenames(
        title="Selecione imagens JPEG ou arquivos PDF",
        filetypes=[("Arquivos JPEG ou PDF", "*.jpeg *.pdf")]
    )
    if arquivos:
        arquivos_selecionados = arquivos
        log_text.insert(tk.END, f"🗂 {len(arquivos)} arquivo(s) selecionado(s).\n")

def salvar_em_pasta_escolhida(nome_arquivo):
    return os.path.join(pasta_destino, nome_arquivo)

def confirmar_conversao():
    if not arquivos_selecionados:
        messagebox.showwarning("Nenhum arquivo", "Selecione pelo menos um arquivo antes de converter.")
        return
    converter_arquivos(arquivos_selecionados)

def converter_arquivos(lista_arquivos):
    convertidos = 0
    erros = 0
    log_text.insert(tk.END, "\n▶ Iniciando conversão...\n")

    for caminho in lista_arquivos:
        try:
            nome_arquivo = os.path.basename(caminho)
            extensao = os.path.splitext(caminho)[1].lower()

            if extensao == ".jpeg":
                imagem = Image.open(caminho).convert("RGB")
                novo_nome = os.path.splitext(nome_arquivo)[0] + ".jpg"
                destino = salvar_em_pasta_escolhida(novo_nome) if destino_var.get() else os.path.splitext(caminho)[0] + ".jpg"
                imagem.save(destino, "JPEG")
                log_text.insert(tk.END, f"✔ JPEG convertido: {novo_nome}\n")
                convertidos += 1

            elif extensao == ".pdf":
                paginas = convert_from_path(caminho)
                for i, pagina in enumerate(paginas):
                    novo_nome = f"{os.path.splitext(nome_arquivo)[0]}_pagina{i+1}.jpg"
                    destino = salvar_em_pasta_escolhida(novo_nome) if destino_var.get() else os.path.join(os.path.dirname(caminho), novo_nome)
                    pagina.save(destino, "JPEG")
                    log_text.insert(tk.END, f"✔ Página PDF convertida: {novo_nome}\n")
                    convertidos += 1

        except Exception as e:
            erros += 1
            log_text.insert(tk.END, f"❌ Erro em {nome_arquivo}: {str(e)}\n")

    messagebox.showinfo("Conversão Finalizada", f"Arquivos convertidos: {convertidos}\nErros: {erros}")

# Interface
janela = tk.Tk()
janela.title("Conversor JPEG/PDF → JPG")
janela.geometry("570x480")
janela.resizable(False, False)

style = ttk.Style(janela)
style.theme_use('vista' if 'vista' in style.theme_names() else 'clam')

tk.Label(janela, text="Conversor de Imagens .jpeg e .pdf para .jpg", font=("Segoe UI", 12, "bold")).pack(pady=10)

# Botão de selecionar arquivos
btn_arquivos = ttk.Button(janela, text="Selecionar Arquivos", command=selecionar_arquivos)
btn_arquivos.pack(pady=5)

# Checkbox entre os botões
destino_var = tk.BooleanVar()
check_destino = tk.Checkbutton(janela, text="Salvar em pasta personalizada", variable=destino_var, command=ao_alterar_checkbox, font=("Segoe UI", 10))
check_destino.pack()
caminho_label = tk.Label(janela, text="", fg="blue", wraplength=540, justify="left", font=("Segoe UI", 9))
caminho_label.pack(pady=2)

# Botão de converter
btn_converter = ttk.Button(janela, text="Converter", command=confirmar_conversao)
btn_converter.pack(pady=10)

# Log
frame_log = ttk.Frame(janela)
frame_log.pack(padx=10, pady=10, fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame_log)
scrollbar.pack(side="right", fill="y")

log_text = tk.Text(frame_log, height=12, yscrollcommand=scrollbar.set, wrap="word", font=("Segoe UI", 9))
log_text.pack(fill="both", expand=True)
scrollbar.config(command=log_text.yview)

janela.mainloop()
