import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime
import dados
# IMPORTANDO S FUNÇÕES DA VIEW
from view import *

hoje = datetime.today().strftime('%d/%m/%Y')

# JANELA PRINCIPAL
janela = tk.Tk()
janela.title("Biblioteca Comunitária")
janela.geometry("770x400")
janela.configure(background="#3C045A")
janela.resizable(False, False)

style = ttk.Style(janela)
style.theme_use("clam")

frameCima = tk.Frame(janela, width=770, height=50, background="#52057C", relief="flat")
frameCima.grid(row=0, column=0, columnspan=2, sticky="nsew")
frameEsquerda = tk.Frame(janela, width=150, height=265, background="#69069E", relief="solid")

frameEsquerda.grid(row=1, column=0, sticky="nsew")
frameEsquerda.grid_columnconfigure(0, weight=1)
frameEsquerda.grid_propagate(False)

frameDireita = tk.Frame(janela, width=600, height=265, background="#9C09EB", relief="raised")
frameDireita.grid(row=1, column=1, sticky="nsew")
frameDireita.grid_columnconfigure(1, weight=1)
frameDireita.grid_propagate(False)

janela.grid_rowconfigure(1, weight=1)
janela.grid_columnconfigure(0, weight=0)
janela.grid_columnconfigure(1, weight=1)

# LOGO
app_img = Image.open("imagens/estante-de-livros.png")
app_img = app_img.resize((40, 40))
app_img = ImageTk.PhotoImage(app_img)

app_logo = tk.Label(frameCima, image=app_img, compound="left",
                    padx=5, anchor="nw", background="#52057C")
app_logo.place(x=0, y=0)

app_ = tk.Label(frameCima, text="Biblioteca Comunitária - Sistema Gerenciador de Livros",
                compound="left", padx=5, anchor="nw",
                font=('Verdana', 15, 'bold'), background="#52057C")
app_.place(x=50, y=7)

# LISTRA ROXO ESCURO NO FINAL DA JANELA
app_linha = tk.Label(janela, background="#3C045A")
app_linha.place(x=0, y=383, width=770, height=35)  # ALTURA 5 PIXELS, POSIÇÃO Y NO FINAL


# NOVO USUÁRIO
def novo_usuario():
    #EVITE QUE AS JANELAS ANTIGAS APAREÇAM NA NOVA JANELA
    for widget in frameDireita.winfo_children():
        widget.destroy()

    global img_salvar

    def add():
        first_name = entrada_nome.get().strip()
        last_name = entrada_sobrenome.get().strip()
        adress = entrada_endereco.get().strip()
        email = entrada_email.get().strip().lower()
        phone = entrada_numero.get().strip()

        #VALIDAÇÃO ANTES DE QUALQUER COISA
        if not all([first_name, last_name, adress, email, phone]):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        #CHECA E-MAIL DUPLICADO
        try:
            conn = sqlite3.connect('biblioteca.db')
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM usuarios WHERE LOWER(email) = ?", (email,))
            if cursor.fetchone():
                conn.close()
                messagebox.showerror("Erro", "Este e-mail já está cadastrado!")
                return
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Falha ao verificar e-mail: {e}")
            return

        #INSERE APENAS UMA VEZ
        try:
            insert_user(first_name, last_name, adress, email, phone)
            messagebox.showinfo('Sucesso', 'Usuário cadastrado com sucesso!')
            # limpa campos uma única vez
            entrada_nome.delete(0, 'end')
            entrada_sobrenome.delete(0, 'end')
            entrada_endereco.delete(0, 'end')
            entrada_email.delete(0, 'end')
            entrada_numero.delete(0, 'end')
        except sqlite3.Error as e:
            messagebox.showerror("Erro", "Falha ao cadastrar usuário: {e}")

    #TÍTULO
    titulo = tk.Label(frameDireita, text="Cadastrar Novo Usuário",
                      font=('Verdana', 12, 'bold'),
                      bg="#9C09EB")
    titulo.grid(row=0, column=0, columnspan=2, pady=10)

    frameDireita.grid_columnconfigure(0, weight=1)
    frameDireita.grid_columnconfigure(1, weight=1)

    #FORMULÁRIO
    tk.Label(frameDireita, text="Nome*", bg="#9C09EB", font=('Verdana', 10)).grid(row=2, column=0, padx=5, pady=10, sticky="e")
    entrada_nome = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_nome.grid(row=2, column=1, padx=5, pady=10, sticky="w")

    tk.Label(frameDireita, text="Sobrenome*", bg="#9C09EB", font=('Verdana', 10)).grid(row=3, column=0, padx=5, pady=10, sticky="e")
    entrada_sobrenome = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_sobrenome.grid(row=3, column=1, padx=5, pady=10, sticky="w")

    tk.Label(frameDireita, text="Endereço*", bg="#9C09EB", font=('Verdana', 10)).grid(row=4, column=0, padx=5, pady=10, sticky="e")
    entrada_endereco = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_endereco.grid(row=4, column=1, padx=5, pady=10, sticky="w")

    tk.Label(frameDireita, text="Email*", bg="#9C09EB", font=('Verdana', 10)).grid(row=5, column=0, padx=5, pady=10, sticky="e")
    entrada_email = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_email.grid(row=5, column=1, padx=5, pady=10, sticky="w")

    tk.Label(frameDireita, text="Telefone*", bg="#9C09EB", font=('Verdana', 10)).grid(row=6, column=0, padx=5, pady=10, sticky="e")
    entrada_numero = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_numero.grid(row=6, column=1, padx=5, pady=10, sticky="w")

    #BOTÃO SALVAR
    img_salvar = Image.open("imagens/diskette.png").resize((20, 20))
    img_salvar = ImageTk.PhotoImage(img_salvar)

    salvar_btn = tk.Button(frameDireita, image=img_salvar, text="Salvar",
                           command=add, compound="left",
                           bg="#69069E", fg="white",
                           width=80, height=35, font=('Verdana', 10, 'bold'))
    salvar_btn.image = img_salvar
    salvar_btn.grid(row=7, column=0, columnspan=2, pady=20)



#VER USUÁRIO
def ver_usuario():
    titulo = tk.Label(frameDireita, text="Usuários Cadastrados",
                      font=('Verdana', 12, 'bold'),
                      bg="#9C09EB")
    titulo.grid(row=0, column=0, columnspan=2, pady=10)

    dados = get_users()
    list_header = ['ID', 'Nome', 'Sobrenome', 'Endereço', 'Email', 'Telefone']

    global tree

    # STYLE DA TREEVIEW
    style = ttk.Style()
    style.theme_use("clam")  #USAR 'CLAM' PERMITE MAIS PERSONALIZAÇÃO
    style.configure("Treeview",
                    background="#EDE7F6",  #COR DE FUNDO DAS LINHAS
                    foreground="black",  #COR DO TEXTO
                    rowheight=25,
                    fieldbackground="#EDE7F6")  #FUNCO DAS CÉLULAS
    style.map('Treeview', background=[('selected', '#7B1FA2')], foreground=[('selected', 'white')])  #SELECIONADO

    # TREEVIEW
    tree = ttk.Treeview(frameDireita, columns=list_header, show="headings")
    vsb = ttk.Scrollbar(frameDireita, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    tree.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
    vsb.grid(row=2, column=1, sticky='ns')

    #COFIGURANDO COLUNAS
    frameDireita.update_idletasks()
    frame_width = frameDireita.winfo_width() - 20
    col_widths = [50, 100, 100, 150, 150, 80]
    total_width = sum(col_widths)
    scale = frame_width / total_width

    for i, col in enumerate(list_header):
        tree.heading(col, text=col, anchor='center')
        tree.column(col, width=int(col_widths[i] * scale), anchor='center', stretch=True)

    #INSERINDO DADOS COM CORES ALTERNADAS
    for index, item in enumerate(dados):
        if index % 2 == 0:
            tree.insert('', 'end', values=item, tags=('evenrow',))
        else:
            tree.insert('', 'end', values=item, tags=('oddrow',))

    tree.tag_configure('evenrow', background="#EDE7F6")
    tree.tag_configure('oddrow', background="#D1C4E9")

    frameDireita.grid_rowconfigure(2, weight=1)
    frameDireita.grid_columnconfigure(0, weight=1)


frameDireita.grid_columnconfigure(1, weight=1)



#NOVO LIVRO
def novo_livro():
    for widget in frameDireita.winfo_children():
        widget.destroy()

    def add():
        try:
            #OBTER VALORES DOS CAMPOS
            title = entrada_titulo.get().strip()
            author = entrada_autor.get().strip()
            publisher = entrada_editora.get().strip()
            year = entrada_ano.get().strip()
            isbn = entrada_isbn.get().strip()

            #VERIFICAR OS CAMPOS VAZIOS
            if not all([title, author, publisher, year, isbn]):
                messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
                return

            #VERIFICAR SE O LIVRO JÁ EXISTE CONSULTANDO DIRETO NO BANCO DE DADOS
            conn = sqlite3.connect('biblioteca.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM livros WHERE LOWER(titulo) = LOWER(?)", (title,))
            if cursor.fetchone():
                messagebox.showerror("Erro", "Livro já cadastrado!")
                conn.close()
                return
            conn.close()

            #INSERIR NOVO LIVRO
            insert_book(title, author, publisher, year, isbn)
            messagebox.showinfo("Sucesso", "Livro cadastrado com sucesso!")

            #LIMPAR CAMPOS
            entrada_titulo.delete(0, 'end')
            entrada_autor.delete(0, 'end')
            entrada_editora.delete(0, 'end')
            entrada_ano.delete(0, 'end')
            entrada_isbn.delete(0, 'end')

        except sqlite3.Error as e:
            messagebox.showerror("Erro no Banco de Dados", "Erro: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", "Ocorreu um erro: {str(e)}")

    titulo = tk.Label(frameDireita, text="Inserir um Novo Livro",
                     font=('Verdana', 12, 'bold'), bg="#9C09EB")
    titulo.grid(row=0, column=0, columnspan=2, pady=10)

    # CAMPOS DO FORMULÁRIO
    tk.Label(frameDireita, text="Título*", bg="#9C09EB", font=('Verdana', 10)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    entrada_titulo = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_titulo.grid(row=1, column=1, padx=5, pady=10, sticky="w")

    tk.Label(frameDireita, text="Autor*", bg="#9C09EB", font=('Verdana', 10)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    entrada_autor = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_autor.grid(row=2, column=1, padx=5, pady=10, sticky="w")

    tk.Label(frameDireita, text="Editora*", bg="#9C09EB", font=('Verdana', 10)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
    entrada_editora = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_editora.grid(row=3, column=1, padx=5, pady=10, sticky="w")

    tk.Label(frameDireita, text="Publicação*", bg="#9C09EB", font=('Verdana', 10)).grid(row=4, column=0, sticky="e", padx=5, pady=5)
    entrada_ano = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_ano.grid(row=4, column=1, padx=5, pady=10, sticky="w")

    tk.Label(frameDireita, text="ISBN*", bg="#9C09EB", font=('Verdana', 10)).grid(row=5, column=0, sticky="e", padx=5, pady=5)
    entrada_isbn = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_isbn.grid(row=5, column=1, padx=5, pady=10, sticky="w")

    #BOTÃO SALVAR
    img_salvar = Image.open("imagens/diskette.png").resize((20, 20))
    img_salvar = ImageTk.PhotoImage(img_salvar)

    salvar_btn = tk.Button(frameDireita, image=img_salvar, text="Salvar", command=add,
                         compound="left", bg="#69069E", fg="white",
                         width=80, height=35, font=('Verdana', 10, 'bold'))
    salvar_btn.image = img_salvar
    salvar_btn.grid(row=7, column=0, columnspan=2, pady=20)

#FUNÇÃO VER LIVROS
def ver_livros():
    #LIPA O FRAME DIREITO
    for widget in frameDireita.winfo_children():
        widget.destroy()

    titulo = tk.Label(frameDireita, text="Livros Cadastrados",
                     font=('Verdana', 12, 'bold'),
                     bg="#9C09EB")
    titulo.grid(row=0, column=0, columnspan=2, pady=10)

    # Obtém os dados (com tratamento igual ao ver_usuario)
    dados = exibir_livros()
    if dados is None:
        dados = []

    list_header = ['ID', 'Titulo', 'Autor', 'Editora', 'Ano', 'ISBN']
    global tree

    # STYLE DA TREEVIEW (IDÊNTICO AO DE USUÁRIOS)
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                   background="#EDE7F6",
                   foreground="black",
                   rowheight=25,
                   fieldbackground="#EDE7F6")
    style.map('Treeview',
              background=[('selected', '#7B1FA2')],
              foreground=[('selected', 'white')])

    # TREEVIEW (MESMA CONFIGURAÇÃO)
    tree = ttk.Treeview(frameDireita, columns=list_header, show="headings")
    vsb = ttk.Scrollbar(frameDireita, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    tree.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
    vsb.grid(row=2, column=1, sticky='ns')

    #MESMO MÉTODO DE REDIMENSIONAMENTO DAS COLUNAS
    frameDireita.update_idletasks()
    frame_width = frameDireita.winfo_width() - 20
    col_widths = [50, 100, 100, 150, 150, 80]  # MESMAS LARGURAS
    total_width = sum(col_widths)
    scale = frame_width / total_width

    for i, col in enumerate(list_header):
        tree.heading(col, text=col, anchor='center')
        tree.column(col, width=int(col_widths[i] * scale), anchor='center', stretch=True)

    # MESMO ESQUEMA DE CORES ALTERNADAS
    for index, item in enumerate(dados):
        if index % 2 == 0:
            tree.insert('', 'end', values=item, tags=('evenrow',))
        else:
            tree.insert('', 'end', values=item, tags=('oddrow',))

    tree.tag_configure('evenrow', background="#EDE7F6")
    tree.tag_configure('oddrow', background="#D1C4E9")

    # MESMA CONFIGURAÇÃO DE REDIMENSIONAMENTO
    frameDireita.grid_rowconfigure(2, weight=1)
    frameDireita.grid_columnconfigure(0, weight=1)

#NOVO EMPRÉSTIMO
def realizar_emprestimo():
    for widget in frameDireita.winfo_children():
        widget.destroy()

    def add():
        try:
            #OBTER VALORES DOS CAMPOS
            user = entrada_id_usuario.get().strip()
            book = entrada_id_livro.get().strip()

            #VERIFICAR OS CAMPOS VAZIOS
            if not all([user, book]):
                messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
                return

            #INSERIR NOVO EMPRÉSTIMO
            insert_loan(user, book, hoje, None)
            messagebox.showinfo("Sucesso", "Empréstimo realizado com sucesso!")

            #LIMPAR CAMPOS
            entrada_id_usuario.delete(0, 'end')
            entrada_id_livro.delete(0, 'end')

        except sqlite3.Error as e:
            messagebox.showerror("Erro no Banco de Dados", "Erro: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", "Ocorreu um erro: {str(e)}")

    titulo = tk.Label(frameDireita, text="Realizar Empréstimo de um Novo Livro",
                     font=('Verdana', 12, 'bold'), bg="#9C09EB")
    titulo.grid(row=0, column=0, columnspan=2, pady=10)

    # CAMPOS DO FORMULÁRIO
    tk.Label(frameDireita, text="Digite o ID do usuário*", bg="#9C09EB", font=('Verdana', 10)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    entrada_id_usuario = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_id_usuario.grid(row=1, column=1, padx=5, pady=10, sticky="w")

    tk.Label(frameDireita, text="Digite o ID do Livro*", bg="#9C09EB", font=('Verdana', 10)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    entrada_id_livro = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_id_livro.grid(row=2, column=1, padx=5, pady=10, sticky="w")

    #BOTÃO SALVAR
    img_salvar = Image.open("imagens/diskette.png").resize((20, 20))
    img_salvar = ImageTk.PhotoImage(img_salvar)

    salvar_btn = tk.Button(frameDireita, image=img_salvar, text="Salvar", command=add,
                         compound="left", bg="#69069E", fg="white",
                         width=80, height=35, font=('Verdana', 10, 'bold'))
    salvar_btn.image = img_salvar
    salvar_btn.grid(row=7, column=0, columnspan=2, pady=20)

#VER LIVROS EMPRESTADOS
def ver_livros_emprestados():
    #LIMPA O FRAME DIREITO
    for widget in frameDireita.winfo_children():
        widget.destroy()

    titulo = tk.Label(frameDireita, text="Livros Emprestados",
                      font=('Verdana', 12, 'bold'),
                      bg="#9C09EB")
    titulo.grid(row=0, column=0, columnspan=2, pady=10)

    #OBTÉM DADOS
    books_on_loan = get_books_on_loan() or []  # garante lista, mesmo que venha None
    dados = []

    for book in books_on_loan:
        #BOOK = (ID, TÍTULO, USUÁRIO, DATA_EMPRÉSTIMO, DEVOLUÇÃO)
        dado = [book[0], book[1], book[2], book[3], book[4]]
        dados.append(dado)

    list_header = ['ID', 'Titulo', 'Usuário', 'Data Empréstimo', 'Data Devolução']
    global tree

    #STYLE DA TREEVIEW (IDÊNTICO AO DE USUÁRIOS)
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    background="#EDE7F6",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#EDE7F6")
    style.map('Treeview',
              background=[('selected', '#7B1FA2')],
              foreground=[('selected', 'white')])

    #TREEVIEW (MESMA CONFIGURAÇÃO)
    tree = ttk.Treeview(frameDireita, columns=list_header, show="headings")
    vsb = ttk.Scrollbar(frameDireita, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    tree.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
    vsb.grid(row=2, column=1, sticky='ns')

    #MESMO MÉTODO DE REDIMENSIONAMENTO DAS COLUNAS
    frameDireita.update_idletasks()
    frame_width = frameDireita.winfo_width() - 20
    col_widths = [20, 200, 100, 120, 120]  # MESMAS LARGURAS
    total_width = sum(col_widths)
    scale = frame_width / total_width

    for i, col in enumerate(list_header):
        tree.heading(col, text=col, anchor='center')
        tree.column(col, width=int(col_widths[i] * scale), anchor='center', stretch=True)

    # MESMO ESQUEMA DE CORES ALTERNADAS
    for index, item in enumerate(dados):
        if index % 2 == 0:
            tree.insert('', 'end', values=item, tags=('evenrow',))
        else:
            tree.insert('', 'end', values=item, tags=('oddrow',))

    tree.tag_configure('evenrow', background="#EDE7F6")
    tree.tag_configure('oddrow', background="#D1C4E9")

    # MESMA CONFIGURAÇÃO DE REDIMENSIONAMENTO
    frameDireita.grid_rowconfigure(2, weight=1)

#DEVOLUÇÃO DE UM EMPRÉSTIMO
def devolucao_emprestimo():
    for widget in frameDireita.winfo_children():
        widget.destroy()

    def add():
        try:
            #OBTER VALORES DOS CAMPOS
            loan_id = int(entrada_id_emprestimo.get().strip())
            return_date = entrada_data_retorno.get().strip()
            lista = [loan_id, return_date]

            #VERIFICAR OS CAMPOS VAZIOS
            if not all([loan_id, return_date]):
                messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
                return

            #INSERIR NOVO EMPRÉSTIMO
            update_loan_return_date(loan_id, return_date)
            messagebox.showinfo("Sucesso", "Devolução Realizada com Sucesso!")

            #LIMPAR CAMPOS
            entrada_id_emprestimo.delete(0, 'end')
            entrada_data_retorno.delete(0, 'end')

        except sqlite3.Error as e:
            messagebox.showerror("Erro no Banco de Dados", "Erro: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", "Ocorreu um erro: {str(e)}")

    titulo = tk.Label(frameDireita, text="Atualizar Devolução de um Empréstimo",
                     font=('Verdana', 12, 'bold'), bg="#9C09EB")
    titulo.grid(row=0, column=0, columnspan=2, pady=10)

    # CAMPOS DO FORMULÁRIO
    tk.Label(frameDireita, text="ID do Empréstimo*", bg="#9C09EB", font=('Verdana', 10)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    entrada_id_emprestimo = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_id_emprestimo.grid(row=1, column=1, padx=5, pady=10, sticky="w")

    tk.Label(frameDireita, text="Nova data de devolução*", bg="#9C09EB", font=('Verdana', 10)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    entrada_data_retorno = tk.Entry(frameDireita, width=65, justify="left", relief="solid")
    entrada_data_retorno.grid(row=2, column=1, padx=5, pady=10, sticky="w")

    #BOTÃO SALVAR
    img_salvar = Image.open("imagens/diskette.png").resize((20, 20))
    img_salvar = ImageTk.PhotoImage(img_salvar)

    salvar_btn = tk.Button(frameDireita, image=img_salvar, text="Salvar", command=add,
                         compound="left", bg="#69069E", fg="white",
                         width=80, height=35, font=('Verdana', 10, 'bold'))
    salvar_btn.image = img_salvar
    salvar_btn.grid(row=7, column=0, columnspan=2, pady=20)


#CONTROLADOR DO MENU
def controle(i):
    # USUÁRIO
    if i == 'novo_usuario':
        for widget in frameDireita.winfo_children():
            widget.destroy()
        novo_usuario()

    #VER OS USUÁRIOS
    if i == 'ver_usuario':
        for widget in frameDireita.winfo_children():
            widget.destroy()
        ver_usuario()

    #ADICIONAR LIVRO
    if i == 'novo_livro':
        for widget in frameDireita.winfo_children():
            widget.destroy()
        novo_livro()

    #EXIBIR LIVROS
    if i == 'ver_livro':
        for widget in frameDireita.winfo_children():
            widget.destroy()
        ver_livros()

    #NOVO EMPRÉSTIMO
    if i == 'emprestimo':
        for widget in frameDireita.winfo_children():
            widget.destroy()
        realizar_emprestimo()

    #NOVO EMPRÉSTIMO
    if i == 'ver_emprestimo':
        for widget in frameDireita.winfo_children():
            widget.destroy()
        ver_livros_emprestados()

    if i == 'devolver_emprestimo':
        for widget in frameDireita.winfo_children():
            widget.destroy()
        devolucao_emprestimo()

#-------------------- MENU --------------------

#NOVO USUÁRIO
img_user = Image.open("imagens/adicionar-usuario.png").resize((20, 20))
img_user = ImageTk.PhotoImage(img_user)

btn_novo_usuario = tk.Button(frameEsquerda, command=lambda: controle('novo_usuario'),
                             image=img_user, compound='left', text="Novo Usuário",
                             bg="#69069E", overrelief='ridge', relief='groove', padx=10)
btn_novo_usuario.grid(row=0, column=0, sticky="nsew", padx=5, pady=10)

#NOVO LIVRO
img_add_book = Image.open("imagens/mais.png").resize((20, 20))
img_add_book = ImageTk.PhotoImage(img_add_book)

btn_novo_livro = tk.Button(frameEsquerda, image=img_add_book, compound='left', command=lambda: controle('novo_livro'),
                           text="Novo Livro", bg="#69069E",
                           overrelief='ridge', relief='groove', padx=10)
btn_novo_livro.grid(row=1, column=0, sticky="nsew", padx=5, pady=10)

#EXIBIR LIVROS
img_book = Image.open("imagens/abra-o-livro.png").resize((20, 20))
img_book = ImageTk.PhotoImage(img_book)

btn_exibir_livros = tk.Button(frameEsquerda, image=img_book, compound='left', command=lambda: controle('ver_livro'),
                              text="Exibir Livros", bg="#69069E",
                              overrelief='ridge', relief='groove', padx=10)
btn_exibir_livros.grid(row=2, column=0, sticky="nsew", padx=5, pady=10)

#EXIBIR USUÁRIOS
img_view_user = Image.open("imagens/user.png").resize((20, 20))
img_view_user = ImageTk.PhotoImage(img_view_user)

btn_exibir_usuarios = tk.Button(frameEsquerda, image=img_view_user, command=lambda: controle('ver_usuario'),
                                compound='left',
                                text="Exibir Usuários", bg="#69069E",
                                overrelief='ridge', relief='groove', padx=10)
btn_exibir_usuarios.grid(row=3, column=0, sticky="nsew", padx=5, pady=10)

#NOVO EMPRÉSTIMO
img_new_emprestimo = Image.open("imagens/mais.png").resize((20, 20))
img_new_emprestimo = ImageTk.PhotoImage(img_new_emprestimo)

btn_emprestimo = tk.Button(frameEsquerda, image=img_new_emprestimo, compound='left', command=lambda: controle('emprestimo'),
                           text="Novo Empréstimo", bg="#69069E",
                           overrelief='ridge', relief='groove', padx=10)
btn_emprestimo.grid(row=4, column=0, sticky="nsew", padx=5, pady=10)

#LIVROS EMPRESTADOS
img_book_emprestado = Image.open("imagens/livro.png").resize((20, 20))
img_book_emprestado = ImageTk.PhotoImage(img_book_emprestado)

btn_book_emprestado = tk.Button(frameEsquerda, image=img_book_emprestado, compound='left', command=lambda:controle('ver_emprestimo'),
                                text="Livros Emprestados", bg="#69069E",
                                overrelief='ridge', relief='groove', padx=10)
btn_book_emprestado.grid(row=5, column=0, sticky="nsew", padx=5, pady=10)

#DEVOLVER LIVRO
img_devolver = Image.open("imagens/updating.png").resize((18, 18))
img_devolver = ImageTk.PhotoImage(img_devolver)

btn_devolver = tk.Button(frameEsquerda, image=img_devolver, compound='left', command=lambda: controle('devolver_emprestimo'),
                         text="Devolver Livro", bg="#69069E",
                         overrelief='ridge', relief='groove', padx=10)
btn_devolver.grid(row=6, column=0, sticky="nsew", padx=5, pady=10)



novo_usuario()
janela.mainloop()
