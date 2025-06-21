
# Online Python - IDE, Editor, Compiler, Interpreter

def sum(a, b):
    return (a + b)

a = int(input('Enter 1st number: '))
b = int(input('Enter 2nd number: '))

print(f'Sum of {a} and {b} is {sum(a, b)}')
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser

class BlocoDeNotas:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Bloco de Notas Colorido")
        self.texto = tk.Text(self.raiz, undo=True)
        self.texto.pack(expand=1, fill="both")

        self.criar_menu()

    def criar_menu(self):
        barra_menu = tk.Menu(self.raiz)
        self.raiz.config(menu=barra_menu)

        # Menu Arquivo
        menu_arquivo = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Novo", command=self.novo_arquivo)
        menu_arquivo.add_command(label="Abrir", command=self.abrir_arquivo)
        menu_arquivo.add_command(label="Salvar", command=self.salvar_arquivo)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self.raiz.quit)

        # Menu Editar
        menu_editar = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Editar", menu=menu_editar)
        menu_editar.add_command(label="Cortar", command=lambda: self.texto.event_generate("<<Cut>>"))
        menu_editar.add_command(label="Copiar", command=lambda: self.texto.event_generate("<<Copy>>"))
        menu_editar.add_command(label="Colar", command=lambda: self.texto.event_generate("<<Paste>>"))
        menu_editar.add_command(label="Selecionar Tudo", command=lambda: self.texto.event_generate("<<SelectAll>>"))

        # Menu Cores
        menu_cores = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Cores", menu=menu_cores)
        menu_cores.add_command(label="Cor de Fundo", command=self.mudar_cor_fundo)
        menu_cores.add_command(label="Cor do Texto", command=self.mudar_cor_texto)

    def novo_arquivo(self):
        self.texto.delete(1.0, tk.END)

    def abrir_arquivo(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt")])
        if caminho:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                conteudo = arquivo.read()
            self.texto.delete(1.0, tk.END)
            self.texto.insert(tk.END, conteudo)

    def salvar_arquivo(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Arquivos de Texto", "*.txt")])
        if caminho:
            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write(self.texto.get(1.0, tk.END))
            messagebox.showinfo("Salvo", "Arquivo salvo com sucesso!")

    def mudar_cor_fundo(self):
        cor = colorchooser.askcolor(title="Escolha a Cor de Fundo")[1]
        if cor:
            self.texto.config(bg=cor)

    def mudar_cor_texto(self):
        cor = colorchooser.askcolor(title="Escolha a Cor do Texto")[1]
        if cor:
            self.texto.config(fg=cor)

if __name__ == "__main__":
    raiz = tk.Tk()
    app = BlocoDeNotas(raiz)
    raiz.mainloop()
