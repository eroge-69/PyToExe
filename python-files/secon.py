import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import bcrypt
import pandas as pd
from unidecode import unidecode
import os
from datetime import datetime
import shutil

usuario_global = ""

def normalizar(texto):
    return unidecode(str(texto)).strip().lower() if texto else ''

def registrar_log(usuario, acao):
    conn = sqlite3.connect('secon.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (usuario, acao, data_hora) VALUES (?, ?, datetime('now', 'localtime'))", (usuario, acao))
    conn.commit()
    conn.close()

def validar_dados(nome, serie, turma, ano):
    if not nome or any(char.isdigit() for char in nome):
        return False
    if not serie.isdigit():
        return False
    if not turma.isalpha() or len(turma) != 1:
        return False
    if not ano.isdigit():
        return False
    return True
def inicializar_db():
    conn = sqlite3.connect('secon.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha BLOB NOT NULL,
            nivel TEXT DEFAULT 'padrao'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            serie TEXT,
            letra_turma TEXT,
            ano TEXT,
            resultado TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            acao TEXT,
            data_hora TEXT
        )
    ''')
    admin_hash = bcrypt.hashpw("onze".encode(), bcrypt.gensalt())
    secretaria_hash = bcrypt.hashpw("secretaria".encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO usuarios (usuario, senha, nivel) VALUES ('admin', ?, 'admin') ON CONFLICT(usuario) DO UPDATE SET senha=excluded.senha, nivel='admin'", (admin_hash,))
    cursor.execute("INSERT INTO usuarios (usuario, senha, nivel) VALUES ('secretaria', ?, 'secreto') ON CONFLICT(usuario) DO UPDATE SET senha=excluded.senha", (secretaria_hash,))
    conn.commit()
    conn.close()

def autenticar(usuario, senha):
    conn = sqlite3.connect('secon.db')
    cursor = conn.cursor()
    cursor.execute("SELECT senha, nivel FROM usuarios WHERE usuario = ?", (usuario,))
    result = cursor.fetchone()
    conn.close()
    if result and bcrypt.checkpw(senha.encode(), result[0]):
        return result[1]
    return None

def verificar_senha_secretaria(senha_digitada):
    conn = sqlite3.connect('secon.db')
    cursor = conn.cursor()
    cursor.execute("SELECT senha FROM usuarios WHERE usuario = 'secretaria'")
    result = cursor.fetchone()
    conn.close()
    return bcrypt.checkpw(senha_digitada.encode(), result[0]) if result else False

def verificar_integridade():
    try:
        conn = sqlite3.connect('secon.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in cursor.fetchall()]
        obrigatorias = {"usuarios", "alunos", "logs"}
        if not obrigatorias.issubset(set(tabelas)):
            raise Exception("Tabelas obrigatórias não encontradas no banco.")
        conn.close()
    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Falha na integridade do banco:\n{e}")
        exit()

def criar_backup():
    if not os.path.exists("backup"):
        os.makedirs("backup")
    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destino = os.path.join("backup", f"secon_backup_{agora}.db")
    try:
        shutil.copyfile("secon.db", destino)
    except Exception as e:
        print(f"Erro ao criar backup: {e}")
def alterar_senha_secretaria(janela):
    def confirmar():
        atual = entry_atual.get()
        nova = entry_nova.get()
        repetir = entry_repetir.get()
        if nova != repetir:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return
        if not verificar_senha_secretaria(atual):
            messagebox.showerror("Erro", "Senha atual incorreta.")
            return
        nova_hash = bcrypt.hashpw(nova.encode(), bcrypt.gensalt())
        conn = sqlite3.connect('secon.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET senha = ? WHERE usuario = 'secretaria'", (nova_hash,))
        conn.commit()
        conn.close()
        registrar_log(usuario_global, "Alterou senha da secretária")
        messagebox.showinfo("Sucesso", "Senha alterada com sucesso.")
        win.destroy()

    win = tk.Toplevel(janela)
    win.title("Alterar senha da secretária")
    win.geometry("300x200")
    win.resizable(False, False)

    tk.Label(win, text="Senha atual:").pack(pady=5)
    entry_atual = tk.Entry(win, show="*")
    entry_atual.pack()

    tk.Label(win, text="Nova senha:").pack(pady=5)
    entry_nova = tk.Entry(win, show="*")
    entry_nova.pack()

    tk.Label(win, text="Repetir nova senha:").pack(pady=5)
    entry_repetir = tk.Entry(win, show="*")
    entry_repetir.pack()

    tk.Button(win, text="Confirmar", command=confirmar, bg="#4CAF50", fg="white").pack(pady=10)

def buscar_alunos(nome=None, serie=None, turma=None, ano=None):
    resultados = []
    conn = sqlite3.connect('secon.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alunos")
    for aluno in cursor.fetchall():
        nome_ok = normalizar(nome) in normalizar(aluno[1]) if nome else True
        serie_ok = normalizar(serie) == normalizar(aluno[2]) if serie else True
        turma_ok = normalizar(turma) == normalizar(aluno[3]) if turma else True
        ano_ok = normalizar(ano) == normalizar(aluno[4]) if ano else True
        if nome_ok and serie_ok and turma_ok and ano_ok:
            resultados.append(aluno)
    conn.close()
    return resultados
def importar_excel():
    def confirmar_importacao():
        senha = senha_entry.get()
        if not verificar_senha_secretaria(senha):
            messagebox.showerror("Erro", "Senha da secretária incorreta.")
            win.destroy()
            return

        caminho = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if caminho:
            try:
                df = pd.read_excel(caminho)
                registros_validos = 0
                conn = sqlite3.connect('secon.db')
                cursor = conn.cursor()
                for _, linha in df.iterrows():
                    nome = str(linha.get("nome", "")).strip()
                    serie = str(linha.get("serie", "")).strip()
                    turma = str(linha.get("letra_turma", "")).strip()
                    ano = str(linha.get("ano", "")).strip()
                    resultado = str(linha.get("resultado", "")).strip()
                    if validar_dados(nome, serie, turma, ano):
                        cursor.execute("INSERT INTO alunos (nome, serie, letra_turma, ano, resultado) VALUES (?, ?, ?, ?, ?)",
                                       (nome, serie, turma, ano, resultado))
                        registros_validos += 1
                conn.commit()
                conn.close()
                registrar_log(usuario_global, f"Importou {registros_validos} alunos")
                messagebox.showinfo("Importado", f"{registros_validos} alunos válidos importados com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar: {e}")
        win.destroy()

    win = tk.Toplevel()
    win.title("Autorização para Importar")
    win.geometry("300x120")
    win.resizable(False, False)
    tk.Label(win, text="Senha da secretária:").pack(pady=10)
    senha_entry = tk.Entry(win, show="*", width=25)
    senha_entry.pack()
    senha_entry.focus()
    tk.Button(win, text="Confirmar", command=confirmar_importacao, bg="#4CAF50", fg="white").pack(pady=10)

def exportar_excel():
    caminho = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if caminho:
        try:
            conn = sqlite3.connect('secon.db')
            df = pd.read_sql_query("SELECT * FROM alunos", conn)
            df.to_excel(caminho, index=False)
            registrar_log(usuario_global, "Exportou alunos")
            messagebox.showinfo("Exportado", "Exportação concluída com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")
        finally:
            conn.close()

def cadastrar_aluno():
    def solicitar_senha():
        def verificar():
            senha = senha_entry.get()
            if verificar_senha_secretaria(senha):
                win_senha.destroy()
                abrir_formulario()
            else:
                messagebox.showerror("Erro", "Senha da secretária incorreta.")
                win_senha.destroy()

        win_senha = tk.Toplevel(janela)
        win_senha.title("Autorização necessária")
        win_senha.geometry("300x120")
        win_senha.resizable(False, False)

        tk.Label(win_senha, text="Digite a senha da secretária:").pack(pady=10)
        senha_entry = tk.Entry(win_senha, show="*", width=25)
        senha_entry.pack(pady=5)
        senha_entry.focus()
        tk.Button(win_senha, text="Confirmar", command=verificar, bg="#F44336", fg="white").pack(pady=10)

    def abrir_formulario():
        def salvar():
            nome = entry_nome.get().strip()
            serie = entry_serie.get().strip()
            turma = entry_turma.get().strip()
            ano = entry_ano.get().strip()
            resultado = entry_resultado.get().strip()

            if not validar_dados(nome, serie, turma, ano):
                messagebox.showerror("Erro", "Dados inválidos.\nVerifique:\n- Nome sem números\n- Série e Ano com números\n- Turma com uma letra")
                return

            conn = sqlite3.connect('secon.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO alunos (nome, serie, letra_turma, ano, resultado) VALUES (?, ?, ?, ?, ?)",
                           (nome, serie, turma, ano, resultado))
            conn.commit()
            conn.close()
            registrar_log(usuario_global, f"Aluno cadastrado: {nome}")
            messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
            janela_cad.destroy()
            if 'buscar' in globals():
                buscar()

        janela_cad = tk.Toplevel(janela)
        janela_cad.title("Cadastrar Aluno")
        janela_cad.geometry("300x300")
        janela_cad.resizable(False, False)

        labels = ["Nome", "Série", "Turma", "Ano", "Resultado"]
        entries = []

        for label in labels:
            tk.Label(janela_cad, text=label + ":").pack(anchor="w", padx=10, pady=2)
            entry = tk.Entry(janela_cad, width=30)
            entry.pack(padx=10)
            entries.append(entry)

        entry_nome, entry_serie, entry_turma, entry_ano, entry_resultado = entries
        tk.Button(janela_cad, text="Salvar", command=salvar, bg="#4CAF50", fg="white").pack(pady=15)

    solicitar_senha()

def excluir_aluno():
    item = tree.selection()
    if not item:
        messagebox.showwarning("Aviso", "Selecione um aluno para excluir.")
        return
    aluno = tree.item(item)["values"]
    if not messagebox.askyesno("Confirmar", f"Deseja excluir o aluno: {aluno[1]}?"):
        return

    def confirmar():
        senha = senha_entry.get()
        if verificar_senha_secretaria(senha):
            conn = sqlite3.connect('secon.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alunos WHERE id = ?", (aluno[0],))
            conn.commit()
            conn.close()
            registrar_log(usuario_global, f"Aluno excluído: {aluno[1]}")
            tree.delete(item)
            messagebox.showinfo("Sucesso", "Aluno removido com sucesso.")
            win.destroy()
        else:
            messagebox.showerror("Erro", "Senha da secretária incorreta.")

    win = tk.Toplevel(janela)
    win.title("Autorização necessária")
    win.geometry("300x120")
    win.resizable(False, False)

    tk.Label(win, text="Digite a senha da secretária:").pack(pady=10)
    senha_entry = tk.Entry(win, show="*", width=25)
    senha_entry.pack(pady=5)
    senha_entry.focus()
    tk.Button(win, text="Confirmar", command=confirmar, bg="#F44336", fg="white").pack(pady=10)

def editar_aluno():
    item = tree.selection()
    if not item:
        messagebox.showwarning("Aviso", "Selecione um aluno para editar.")
        return
    aluno = tree.item(item)["values"]

    def confirmar_senha():
        senha = senha_entry.get()
        if verificar_senha_secretaria(senha):
            janela_senha.destroy()
            abrir_editor(aluno)
        else:
            messagebox.showerror("Erro", "Senha da secretária incorreta.")

    janela_senha = tk.Toplevel(janela)
    janela_senha.title("Autorização necessária")
    janela_senha.geometry("300x120")
    tk.Label(janela_senha, text="Digite a senha da secretária:").pack(pady=10)
    senha_entry = tk.Entry(janela_senha, show="*", width=25)
    senha_entry.pack()
    senha_entry.focus()
    tk.Button(janela_senha, text="Confirmar", command=confirmar_senha, bg="#F44336", fg="white").pack(pady=10)

def abrir_editor(aluno):
    janela_edit = tk.Toplevel(janela)
    janela_edit.title("Editar Aluno")
    janela_edit.geometry("300x300")
    janela_edit.resizable(False, False)

    campos = ["Nome", "Série", "Turma", "Ano", "Resultado"]
    valores = list(aluno[1:])
    entradas = []

    for idx, campo in enumerate(campos):
        tk.Label(janela_edit, text=campo + ":").pack(anchor="w", padx=10, pady=2)
        entry = tk.Entry(janela_edit, width=30)
        entry.insert(0, valores[idx])
        entry.pack(padx=10)
        entradas.append(entry)

    def salvar_edicao():
        nome, serie, turma, ano, resultado = [e.get().strip() for e in entradas]
        if not validar_dados(nome, serie, turma, ano):
            messagebox.showerror("Erro", "Dados inválidos.\nVerifique nome, série, turma e ano.")
            return
        conn = sqlite3.connect('secon.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alunos SET nome=?, serie=?, letra_turma=?, ano=?, resultado=?
            WHERE id=?
        """, (nome, serie, turma, ano, resultado, aluno[0]))
        conn.commit()
        conn.close()
        registrar_log(usuario_global, f"Aluno editado: {nome}")
        messagebox.showinfo("Sucesso", "Aluno atualizado com sucesso.")
        janela_edit.destroy()
        buscar()
        
    tk.Button(janela_edit, text="Salvar", command=salvar_edicao, bg="#2196F3", fg="white").pack(pady=15)

def abrir_principal(nivel):
    global janela
    global tree
    global buscar  # ✅ deve vir antes da definição da função buscar()

    janela = tk.Tk()
    janela.title(f"Secon - Usuário: {usuario_global}")
    janela.geometry("900x550")

    menu = tk.Menu(janela)

    menu_arquivo = tk.Menu(menu, tearoff=0)
    menu_arquivo.add_command(label="Importar Excel", command=importar_excel)
    menu_arquivo.add_command(label="Exportar Excel", command=exportar_excel)
    menu_arquivo.add_separator()
    menu_arquivo.add_command(label="Sair", command=janela.quit)
    menu.add_cascade(label="Arquivo", menu=menu_arquivo)

    menu_alunos = tk.Menu(menu, tearoff=0)
    menu_alunos.add_command(label="Cadastrar Aluno", command=cadastrar_aluno)
    menu_alunos.add_command(label="Editar Aluno Selecionado", command=editar_aluno)
    menu_alunos.add_command(label="Excluir Aluno Selecionado", command=excluir_aluno)
    menu.add_cascade(label="Alunos", menu=menu_alunos)

    if nivel == "admin":
        menu_config = tk.Menu(menu, tearoff=0)
        menu_config.add_command(label="Alterar senha da secretária", command=lambda: alterar_senha_secretaria(janela))
        menu.add_cascade(label="Configurações", menu=menu_config)

    janela.config(menu=menu)

    frame = tk.LabelFrame(janela, text="Buscar Alunos", padx=10, pady=10)
    frame.pack(pady=10)

    tk.Label(frame, text="Nome:").grid(row=0, column=0, sticky="e")
    nome_entry = tk.Entry(frame, width=30)
    nome_entry.grid(row=0, column=1)

    tk.Label(frame, text="Série:").grid(row=1, column=0, sticky="e")
    serie_entry = tk.Entry(frame)
    serie_entry.grid(row=1, column=1)

    tk.Label(frame, text="Turma:").grid(row=2, column=0, sticky="e")
    turma_entry = tk.Entry(frame)
    turma_entry.grid(row=2, column=1)

    tk.Label(frame, text="Ano:").grid(row=3, column=0, sticky="e")
    ano_entry = tk.Entry(frame)
    ano_entry.grid(row=3, column=1)

    def buscar():
        tree.delete(*tree.get_children())
        alunos = buscar_alunos(
            nome=nome_entry.get(),
            serie=serie_entry.get(),
            turma=turma_entry.get(),
            ano=ano_entry.get()
        )
        for aluno in alunos:
            tree.insert("", "end", values=aluno)

    tk.Button(frame, text="Buscar", command=buscar, bg="#4CAF50", fg="white").grid(
        row=4, column=0, columnspan=2, pady=10
    )

    tree = ttk.Treeview(janela, columns=("ID", "Nome", "Série", "Turma", "Ano", "Resultado"), show="headings", height=15)
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=130, anchor="center")
    tree.pack(padx=10, pady=10, fill="both", expand=True)

    janela.mainloop()

def login():
    def entrar(event=None):
        global usuario_global
        usuario = user_entry.get()
        senha = pass_entry.get()
        nivel = autenticar(usuario, senha)
        if nivel:
            usuario_global = usuario
            registrar_log(usuario, "Login")
            janela.destroy()
            abrir_principal(nivel)
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    janela = tk.Tk()
    janela.title("Login - Secon")
    janela.geometry("330x180")
    janela.resizable(False, False)

    container = tk.Frame(janela)
    container.pack(pady=30)

    tk.Label(container, text="Usuário:").grid(row=0, column=0, sticky="e", padx=5)
    user_entry = tk.Entry(container, width=25)
    user_entry.grid(row=0, column=1)

    tk.Label(container, text="Senha:").grid(row=1, column=0, sticky="e", padx=5)
    pass_entry = tk.Entry(container, show="*", width=25)
    pass_entry.grid(row=1, column=1, pady=10)

    tk.Button(container, text="Entrar", command=entrar, width=20, bg="#2196F3", fg="white").grid(
        row=2, column=0, columnspan=2, pady=10
    )

    janela.bind('<Return>', entrar)
    user_entry.focus()
    janela.mainloop()

if __name__ == "__main__":
    inicializar_db()
    verificar_integridade()
    try:
        login()
    finally:
        criar_backup()
