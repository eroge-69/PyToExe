import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Label
from PyPDF2 import PdfReader, PdfWriter
import os

def selecionar_arquivo():
    caminho = filedialog.askopenfilename(
        title="Selecione o arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    if caminho:
        entrada_arquivo.delete(0, tk.END)
        entrada_arquivo.insert(0, caminho)

def selecionar_pasta():
    caminho = filedialog.askdirectory(title="Selecione a pasta de destino")
    if caminho:
        entrada_pasta.delete(0, tk.END)
        entrada_pasta.insert(0, caminho)

def processar_pdf():
    arquivo_pdf = entrada_arquivo.get().strip()
    pasta_destino = entrada_pasta.get().strip()
    try:
        num_chars = int(entrada_criterio.get().strip())
    except ValueError:
        messagebox.showerror("Erro", "Número de caracteres inválido!")
        return

    if not arquivo_pdf:
        messagebox.showerror("Erro", "Selecione um arquivo PDF!")
        return

    if not pasta_destino:
        messagebox.showerror("Erro", "Selecione uma pasta de destino!")
        return

    # Create a processing window
    processing_window = Toplevel(root)
    processing_window.title("Processando")
    Label(processing_window, text="Processando PDF, por favor aguarde...").pack(padx=20, pady=20)
    processing_window.update()

    try:
        leitor = PdfReader(arquivo_pdf)
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir o PDF:\n{e}")
        processing_window.destroy()
        return

    paginas_por_codigo = {}

    # Para cada página, extrai o texto, pega a primeira linha e os primeiros 'num_chars' caracteres
    for pagina in leitor.pages:
        texto = pagina.extract_text()
        if not texto:
            continue
        linhas = texto.splitlines()
        if not linhas:
            continue
        codigo = linhas[0][:num_chars]
        if codigo not in paginas_por_codigo:
            paginas_por_codigo[codigo] = []
        paginas_por_codigo[codigo].append(pagina)

    # Cria um PDF para cada grupo de páginas
    for codigo, paginas in paginas_por_codigo.items():
        escritor = PdfWriter()
        for pagina in paginas:
            escritor.add_page(pagina)
        caminho_saida = os.path.join(pasta_destino, f"{codigo}.pdf")
        with open(caminho_saida, "wb") as saida:
            escritor.write(saida)

    processing_window.destroy()
    messagebox.showinfo("Concluído", "PDF processado com sucesso!")

# Initialize the main window
root = tk.Tk()
root.title("Divisor de PDF")

# Allow window to be resizable
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(3, weight=1)

# Define and initialize widgets
entrada_arquivo = tk.Entry(root, width=50)
entrada_arquivo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

btn_selecionar_arquivo = tk.Button(root, text="Selecionar Arquivo", command=selecionar_arquivo)
btn_selecionar_arquivo.grid(row=0, column=2, padx=10, pady=10)

entrada_pasta = tk.Entry(root, width=50)
entrada_pasta.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

btn_selecionar_pasta = tk.Button(root, text="Selecionar Pasta", command=selecionar_pasta)
btn_selecionar_pasta.grid(row=1, column=2, padx=10, pady=10)

# Add label for character count
label_criterio = tk.Label(root, text="Quantidade de caracteres:")
label_criterio.grid(row=2, column=0, padx=10, pady=10)

entrada_criterio = tk.Entry(root, width=10)
entrada_criterio.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

btn_processar = tk.Button(root, text="Processar PDF", command=processar_pdf)
btn_processar.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

# Start the main loop
root.mainloop()