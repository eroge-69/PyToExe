import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import bcrypt
import fitz
import re
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageTk
import pytesseract
import os
import shutil
import multiprocessing
from tqdm import tqdm
from datetime import datetime
from io import BytesIO

# --- Configuração do Tesseract (AJUSTE O CAMINHO AQUI!) ---
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- Funções do Banco de Dados ---
def criar_banco():
    print("Criando banco de dados...")
    conn = sqlite3.connect('codigos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    ''')
    try:
        hashed_admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('INSERT INTO usuarios (username, password, tipo) VALUES (?, ?, ?)',
                       ('admin', hashed_admin_password, 'admin'))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    try:
        hashed_user_password = bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('INSERT INTO usuarios (username, password, tipo) VALUES (?, ?, ?)',
                       ('usuario', hashed_user_password, 'usuario'))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pares_codigos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_dom TEXT UNIQUE NOT NULL,
            codigo_direta TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Banco de dados criado com sucesso.")

def verificar_login(username, password):
    print(f"Verificando login para usuário: {username}")
    conn = sqlite3.connect('codigos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password, tipo FROM usuarios WHERE username = ?', (username,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        stored_hashed_password = resultado[0].encode('utf-8')
        user_type = resultado[1]
        try:
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                print(f"Login bem-sucedido para {username} como {user_type}")
                return user_type
        except ValueError as e:
            print(f"Erro ao verificar senha (salt inválido): {e}")
            return None
    print("Usuário ou senha inválidos.")
    return None

def adicionar_usuario_db(username, password, tipo):
    conn = sqlite3.connect('codigos.db')
    cursor = conn.cursor()
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('INSERT INTO usuarios (username, password, tipo) VALUES (?, ?, ?)',
                       (username, hashed_password, tipo))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Usuário '{username}' adicionado como '{tipo}' com sucesso!")
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", f"Usuário '{username}' já existe. Escolha outro nome.")
        return False
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao adicionar usuário: {e}")
        return False
    finally:
        conn.close()

def get_todos_usuarios():
    conn = sqlite3.connect('codigos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, tipo FROM usuarios')
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

def excluir_usuario_db(user_id):
    conn = sqlite3.connect('codigos.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT username, tipo FROM usuarios WHERE id = ?', (user_id,))
        resultado_user_a_excluir = cursor.fetchone()
        if not resultado_user_a_excluir:
            messagebox.showerror("Erro", "Usuário não encontrado.")
            return False
        username_to_delete = resultado_user_a_excluir[0]
        tipo_to_delete = resultado_user_a_excluir[1]
        if tipo_to_delete == 'admin':
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo = 'admin'")
            num_admins = cursor.fetchone()[0]
            if num_admins == 1:
                messagebox.showerror("Erro", "Não é possível excluir o único usuário administrador.")
                return False
        cursor.execute('DELETE FROM usuarios WHERE id = ?', (user_id,))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Usuário '{username_to_delete}' excluído com sucesso!")
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao excluir usuário: {e}")
        return False
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao excluir usuário: {e}")
        return False
    finally:
        conn.close()

def alterar_senha_db(user_id, nova_senha):
    conn = sqlite3.connect('codigos.db')
    cursor = conn.cursor()
    try:
        hashed_new_password = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('UPDATE usuarios SET password = ? WHERE id = ?', (hashed_new_password, user_id))
        conn.commit()
        messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao alterar senha: {e}")
        return False
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao alterar senha: {e}")
        return False
    finally:
        conn.close()

def adicionar_par_db(codigo_dom, codigo_direta):
    conn = sqlite3.connect('codigos.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO pares_codigos (codigo_dom, codigo_direta) VALUES (?, ?)',
                       (codigo_dom, codigo_direta))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Par '{codigo_dom} ↔ {codigo_direta}' adicionado com sucesso!")
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", f"Um dos códigos ('{codigo_dom}' ou '{codigo_direta}') já existe em um par.")
        return False
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao adicionar par: {e}")
        return False
    finally:
        conn.close()

def get_todos_pares():
    conn = sqlite3.connect('codigos.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, codigo_dom, codigo_direta FROM pares_codigos')
    except sqlite3.OperationalError:
        cursor.execute('SELECT id, codigo_dom, codigo_direto FROM pares_codigos')
    pares = cursor.fetchall()
    conn.close()
    return pares

def excluir_par_db(par_id):
    conn = sqlite3.connect('codigos.db')
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM pares_codigos WHERE id = ?', (par_id,))
        conn.commit()
        messagebox.showinfo("Sucesso", "Par de códigos excluído com sucesso!")
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao excluir par: {e}")
        return False
    finally:
        conn.close()

def buscar_pares_db(termo_busca):
    conn = sqlite3.connect('codigos.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT id, codigo_dom, codigo_direta FROM pares_codigos
            WHERE codigo_dom = ? OR codigo_direta = ?
        ''', (termo_busca, termo_busca))
    except sqlite3.OperationalError:
        cursor.execute('''
            SELECT id, codigo_dom, codigo_direto FROM pares_codigos
            WHERE codigo_dom = ? OR codigo_direto = ?
        ''', (termo_busca, termo_busca))
    pares = cursor.fetchall()
    conn.close()
    return pares

def get_todos_pares_dict_dom_direta():
    conn = sqlite3.connect('codigos.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT codigo_dom, codigo_direta FROM pares_codigos')
    except sqlite3.OperationalError:
        cursor.execute('SELECT codigo_dom, codigo_direto FROM pares_codigos')
    pares = cursor.fetchall()
    conn.close()
    pares_dict = {dom: direta for dom, direta in pares}
    return pares_dict

def get_todos_pares_dict_direta_dom():
    conn = sqlite3.connect('codigos.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT codigo_dom, codigo_direta FROM pares_codigos')
    except sqlite3.OperationalError:
        cursor.execute('SELECT codigo_dom, codigo_direto FROM pares_codigos')
    pares = cursor.fetchall()
    conn.close()
    pares_dict = {direta: dom for dom, direta in pares}
    return pares_dict

# --- Funções das Telas da Aplicação ---
def abrir_tela_gerenciar_usuarios():
    janela_gerenciar_usuarios = tk.Toplevel(janela_principal)
    janela_gerenciar_usuarios.title("Gerenciar Usuários")
    janela_gerenciar_usuarios.geometry("600x600")
    janela_gerenciar_usuarios.transient(janela_principal)
    janela_gerenciar_usuarios.grab_set()

    def atualizar_lista_usuarios():
        for i in tree_usuarios.get_children():
            tree_usuarios.delete(i)
        usuarios = get_todos_usuarios()
        for user in usuarios:
            tree_usuarios.insert("", "end", iid=user[0], values=(user[1], user[2]))

    def salvar_novo_usuario():
        username = entry_novo_usuario.get().strip()
        password = entry_nova_senha.get().strip()
        tipo = combo_tipo_usuario.get().strip()
        if not username or not password or not tipo:
            messagebox.showwarning("Aviso", "Todos os campos de Usuário/Senha/Tipo devem ser preenchidos para adicionar!")
            return
        if adicionar_usuario_db(username, password, tipo):
            entry_novo_usuario.delete(0, tk.END)
            entry_nova_senha.delete(0, tk.END)
            combo_tipo_usuario.set("usuario")
            atualizar_lista_usuarios()

    def realizar_alterar_senha():
        item_selecionado = tree_usuarios.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário na lista para alterar a senha!")
            return
        nova_senha = entry_nova_senha.get().strip()
        if not nova_senha:
            messagebox.showwarning("Aviso", "O campo 'Senha' deve ser preenchido para alterar a senha!")
            return
        user_id = item_selecionado[0]
        username_selecionado = tree_usuarios.item(item_selecionado, "values")[0]
        confirmar = messagebox.askyesno("Confirmar Alteração",
                                       f"Tem certeza que deseja alterar a senha do usuário '{username_selecionado}'?")
        if confirmar:
            if alterar_senha_db(user_id, nova_senha):
                entry_nova_senha.delete(0, tk.END)

    def deletar_usuario_selecionado():
        item_selecionado = tree_usuarios.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário para excluir!")
            return
        user_id = item_selecionado[0]
        username_selecionado = tree_usuarios.item(item_selecionado, "values")[0]
        confirmar = messagebox.askyesno("Confirmar Exclusão",
                                       f"Tem certeza que deseja excluir o usuário '{username_selecionado}'?")
        if confirmar:
            if excluir_usuario_db(user_id):
                atualizar_lista_usuarios()

    def on_user_select(event):
        item_selecionado = tree_usuarios.selection()
        if item_selecionado:
            valores = tree_usuarios.item(item_selecionado, "values")
            entry_novo_usuario.delete(0, tk.END)
            entry_novo_usuario.insert(0, valores[0])
            combo_tipo_usuario.set(valores[1])
            entry_nova_senha.delete(0, tk.END)

    tk.Label(janela_gerenciar_usuarios, text="Gerenciamento de Usuários",
             font=("Helvetica", 16, "bold")).pack(pady=10)
    frame_add_alterar = tk.LabelFrame(janela_gerenciar_usuarios, text="Adicionar ou Alterar Usuário", padx=10, pady=10)
    frame_add_alterar.pack(pady=10, padx=20, fill="x")
    tk.Label(frame_add_alterar, text="Usuário:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_novo_usuario = tk.Entry(frame_add_alterar, width=30)
    entry_novo_usuario.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(frame_add_alterar, text="Senha:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_nova_senha = tk.Entry(frame_add_alterar, width=30, show="*")
    entry_nova_senha.grid(row=1, column=1, padx=5, pady=5)
    tk.Label(frame_add_alterar, text="Tipo:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    combo_tipo_usuario = ttk.Combobox(frame_add_alterar, values=["usuario", "admin"], width=27, state="readonly")
    combo_tipo_usuario.set("usuario")
    combo_tipo_usuario.grid(row=2, column=1, padx=5, pady=5)
    frame_botoes_acao = tk.Frame(frame_add_alterar)
    frame_botoes_acao.grid(row=3, column=0, columnspan=2, pady=10)
    tk.Button(frame_botoes_acao, text="Adicionar Usuário", command=salvar_novo_usuario,
              bg="#28A745", fg="white", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes_acao, text="Alterar Senha", command=realizar_alterar_senha,
              bg="#FFC107", fg="black", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes_acao, text="Excluir Usuário", command=deletar_usuario_selecionado,
              bg="#DC3545", fg="white", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Label(janela_gerenciar_usuarios, text="Usuários Existentes",
             font=("Helvetica", 14, "bold")).pack(pady=10)
    tree_usuarios = ttk.Treeview(janela_gerenciar_usuarios, columns=("Usuário", "Tipo"), show="headings")
    tree_usuarios.heading("Usuário", text="Usuário")
    tree_usuarios.heading("Tipo", text="Tipo")
    tree_usuarios.column("Usuário", width=200, anchor="center")
    tree_usuarios.column("Tipo", width=150, anchor="center")
    tree_usuarios.pack(pady=10, fill="both", expand=True, padx=20)
    tree_usuarios.bind("<<TreeviewSelect>>", on_user_select)
    atualizar_lista_usuarios()

def abrir_tela_gerenciar_pares():
    janela_gerenciar_pares = tk.Toplevel(janela_principal)
    janela_gerenciar_pares.title("Gerenciar Pares de Códigos")
    janela_gerenciar_pares.geometry("750x700")
    janela_gerenciar_pares.transient(janela_principal)
    janela_gerenciar_pares.grab_set()

    def _sort_treeview_column(tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(key=lambda t: t[0].lower() if isinstance(t[0], str) else t[0], reverse=reverse)
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
        tv.heading(col, command=lambda: _sort_treeview_column(tv, col, not reverse))

    def atualizar_lista_pares():
        for i in tree_pares.get_children():
            tree_pares.delete(i)
        pares = get_todos_pares()
        for par in pares:
            tree_pares.insert("", "end", iid=par[0], values=(par[1], par[2]))
        _sort_treeview_column(tree_pares, "Cód. DOM", False)

    def atualizar_treeview_busca_pares(pares_encontrados):
        for i in tree_resultados_busca_pares.get_children():
            tree_resultados_busca_pares.delete(i)
        if not pares_encontrados:
            tree_resultados_busca_pares.insert("", "end", values=("Nenhum resultado encontrado.", ""))
            return
        for par in pares_encontrados:
            tree_resultados_busca_pares.insert("", "end", iid=par[0], values=(par[1], par[2]))

    def salvar_novo_par():
        codigo_dom = entry_codigo_dom.get().strip()
        codigo_direta = entry_codigo_direta.get().strip()
        if not codigo_dom or not codigo_direta:
            messagebox.showwarning("Aviso", "Ambos os códigos devem ser preenchidos!")
            return
        if adicionar_par_db(codigo_dom, codigo_direta):
            entry_codigo_dom.delete(0, tk.END)
            entry_codigo_direta.delete(0, tk.END)
            atualizar_lista_pares()
            realizar_busca_pares()

    def realizar_alterar_par():
        item_selecionado = tree_pares.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um par na lista para alterar!")
            return
        codigo_dom_novo = entry_codigo_dom.get().strip()
        codigo_direta_novo = entry_codigo_direta.get().strip()
        if not codigo_dom_novo or not codigo_direta_novo:
            messagebox.showwarning("Aviso", "Ambos os campos de código devem ser preenchidos para alterar!")
            return
        par_id = item_selecionado[0]
        original_values = tree_pares.item(item_selecionado, "values")
        codigo_dom_original_tree = original_values[0]
        codigo_direta_original_tree = original_values[1]
        confirmar = messagebox.askyesno("Confirmar Alteração",
                                       f"Tem certeza que deseja alterar o par '{codigo_dom_original_tree} ↔ {codigo_direta_original_tree}' para '{codigo_dom_novo} ↔ {codigo_direta_novo}'?")
        if confirmar:
            conn = sqlite3.connect('codigos.db')
            cursor = conn.cursor()
            try:
                cursor.execute('UPDATE pares_codigos SET codigo_dom = ?, codigo_direta = ? WHERE id = ?',
                               (codigo_dom_novo, codigo_direta_novo, par_id))
                conn.commit()
                messagebox.showinfo("Sucesso", "Par alterado com sucesso!")
                entry_codigo_dom.delete(0, tk.END)
                entry_codigo_direta.delete(0, tk.END)
                atualizar_lista_pares()
                realizar_busca_pares()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Um dos códigos já existe em outro par. Códigos devem ser únicos.")
            except sqlite3.Error as e:
                messagebox.showerror("Erro de Banco de Dados", f"Erro ao alterar par: {e}")
            finally:
                conn.close()

    def deletar_par_selecionado():
        item_selecionado = tree_pares.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um par para excluir!")
            return
        par_id = item_selecionado[0]
        original_values = tree_pares.item(item_selecionado, "values")
        codigo_dom = original_values[0]
        codigo_direta = original_values[1]
        confirmar = messagebox.askyesno("Confirmar Exclusão",
                                       f"Tem certeza que deseja excluir o par '{codigo_dom} ↔ {codigo_direta}'?")
        if confirmar:
            if excluir_par_db(par_id):
                atualizar_lista_pares()
                realizar_busca_pares()

    def realizar_busca_pares():
        termo = entry_termo_busca_pares.get().strip()
        if termo:
            pares_encontrados = buscar_pares_db(termo)
            atualizar_treeview_busca_pares(pares_encontrados)
        else:
            atualizar_treeview_busca_pares([])
            tree_resultados_busca_pares.insert("", "end", values=("Digite um termo para buscar.", ""))

    def on_search_result_select(event):
        item_selecionado = tree_resultados_busca_pares.selection()
        if item_selecionado:
            valores = tree_resultados_busca_pares.item(item_selecionado, "values")
            if valores[0] != "Nenhum resultado encontrado." and valores[0] != "Digite um termo para buscar.":
                entry_codigo_dom.delete(0, tk.END)
                entry_codigo_dom.insert(0, valores[0])
                entry_codigo_direta.delete(0, tk.END)
                entry_codigo_direta.insert(0, valores[1])
            tree_resultados_busca_pares.selection_remove(item_selecionado)

    def on_par_select(event):
        item_selecionado = tree_pares.selection()
        if item_selecionado:
            valores = tree_pares.item(item_selecionado, "values")
            entry_codigo_dom.delete(0, tk.END)
            entry_codigo_dom.insert(0, valores[0])
            entry_codigo_direta.delete(0, tk.END)
            entry_codigo_direta.insert(0, valores[1])

    tk.Label(janela_gerenciar_pares, text="Gerenciamento de Pares de Códigos",
             font=("Helvetica", 16, "bold")).pack(pady=10)
    frame_add_alterar_par = tk.LabelFrame(janela_gerenciar_pares, text="Adicionar ou Alterar Par", padx=10, pady=10)
    frame_add_alterar_par.pack(pady=10, padx=20, fill="x")
    tk.Label(frame_add_alterar_par, text="Código DOM:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_codigo_dom = tk.Entry(frame_add_alterar_par, width=30)
    entry_codigo_dom.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(frame_add_alterar_par, text="Código Direta:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_codigo_direta = tk.Entry(frame_add_alterar_par, width=30)
    entry_codigo_direta.grid(row=1, column=1, padx=5, pady=5)
    frame_botoes_pares = tk.Frame(frame_add_alterar_par)
    frame_botoes_pares.grid(row=2, column=0, columnspan=2, pady=10)
    tk.Button(frame_botoes_pares, text="Adicionar Par", command=salvar_novo_par,
              bg="#28A745", fg="white", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes_pares, text="Alterar Par", command=realizar_alterar_par,
              bg="#FFC107", fg="black", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes_pares, text="Excluir Par", command=deletar_par_selecionado,
              bg="#DC3545", fg="white", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Label(janela_gerenciar_pares, text="Buscar Pares Cadastrados",
             font=("Helvetica", 14, "bold")).pack(pady=(20,10))
    frame_busca_gerenciar_pares = tk.Frame(janela_gerenciar_pares)
    frame_busca_gerenciar_pares.pack(pady=5, padx=20, fill="x")
    entry_termo_busca_pares = tk.Entry(frame_busca_gerenciar_pares, width=40, font=("Helvetica", 10), relief="solid", bd=1)
    entry_termo_busca_pares.pack(side=tk.LEFT, padx=5, ipady=3, expand=True, fill="x")
    tk.Button(frame_busca_gerenciar_pares, text="Buscar", command=realizar_busca_pares,
              font=("Helvetica", 10, "bold"), bg="#5cb85c", fg="white", relief="raised", padx=10, pady=3).pack(side=tk.LEFT, padx=5)
    tk.Label(janela_gerenciar_pares, text="Resultados da Busca (Pares)",
             font=("Helvetica", 12, "bold")).pack(pady=(10,5))
    tree_resultados_busca_pares = ttk.Treeview(janela_gerenciar_pares, columns=("Cód. DOM", "Cód. Direta"), show="headings", height=1)
    tree_resultados_busca_pares.heading("Cód. DOM", text="Código DOM")
    tree_resultados_busca_pares.heading("Cód. Direta", text="Código Direta")
    tree_resultados_busca_pares.column("Cód. DOM", width=250, anchor="center")
    tree_resultados_busca_pares.column("Cód. Direta", width=250, anchor="center")
    tree_resultados_busca_pares.pack(pady=5, fill="x", padx=20)
    tree_resultados_busca_pares.bind("<Double-1>", on_search_result_select)
    tk.Label(janela_gerenciar_pares, text="Pares de Códigos Cadastrados",
             font=("Helvetica", 14, "bold")).pack(pady=(20,10))
    tree_pares = ttk.Treeview(janela_gerenciar_pares, columns=("Cód. DOM", "Cód. Direta"), show="headings", height=5)
    tree_pares.heading("Cód. DOM", text="Código DOM")
    tree_pares.heading("Cód. Direta", text="Código Direta")
    tree_pares.column("Cód. DOM", width=250, anchor="center")
    tree_pares.column("Cód. Direta", width=250, anchor="center")
    tree_pares.pack(pady=10, fill="both", expand=True, padx=20)
    tree_pares.bind("<<TreeviewSelect>>", on_par_select)
    tree_pares.heading("Cód. DOM", text="Código DOM", command=lambda: _sort_treeview_column(tree_pares, "Cód. DOM", False))
    tree_pares.heading("Cód. Direta", text="Código Direta", command=lambda: _sort_treeview_column(tree_pares, "Cód. Direta", False))
    atualizar_lista_pares()

# --- Funções para Processamento de PDF ---
def preprocess_image(img):
    """Pré-processa a imagem para melhorar a qualidade do OCR."""
    img = img.convert("L")  # Converter para escala de cinza
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)  # Aumentar contraste
    return img

def _worker_process_page(args):
    """
    Função wrapper que o pool de processos irá chamar.
    Recebe os argumentos desempacotados e os passa para apply_tesseract_to_image.
    """
    page_index, image_bytes, dpi, replacements, tesseract_path = args
    changes = apply_tesseract_to_image(image_bytes, dpi, replacements, tesseract_path)
    return page_index, changes

def apply_tesseract_to_image(image_bytes, dpi, replacements, tesseract_path):
    """
    Função para aplicar o Tesseract, a ser executada em um processo filho.
    Recebe bytes da imagem e retorna as mudanças encontradas.
    """
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    img = Image.open(BytesIO(image_bytes))
    img = preprocess_image(img)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, lang='por')
    changes_on_page = []
    for i in range(len(data['text'])):
        text_found = data['text'][i].strip()
        if not text_found:
            continue
        for old_code, new_code in replacements.items():
            if old_code == text_found:
                changes_on_page.append({
                    "left": data['left'][i],
                    "top": data['top'][i],
                    "width": data['width'][i],
                    "height": data['height'][i],
                    "text_found_ocr": text_found,
                    "old_code_matched": old_code,
                    "new_code_replacement": new_code
                })
                break
    return changes_on_page

def processar_e_substituir_pdf():
    pdf_path = entry_pdf_path.get().strip()
    if not pdf_path:
        messagebox.showwarning("Aviso", "Por favor, selecione um arquivo PDF primeiro.")
        return
    direcao_substituicao = var_direcao_substituicao.get()
    if direcao_substituicao == "DOM -> DIRETA":
        pares_para_substituir = get_todos_pares_dict_dom_direta()
    elif direcao_substituicao == "DIRETA -> DOM":
        pares_para_substituir = get_todos_pares_dict_direta_dom()
    else:
        messagebox.showerror("Erro", "Direção de substituição inválida.")
        return
    if not pares_para_substituir:
        messagebox.showwarning("Aviso", "Nenhum par de códigos cadastrado para realizar substituições.")
        return
    output_folder = filedialog.askdirectory(title="Selecione a pasta de saída")
    if not output_folder:
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"processed_{timestamp}_{os.path.basename(pdf_path)}"
    output_filepath = os.path.join(output_folder, output_filename)
    backup_path = os.path.join(output_folder, f"backup_{timestamp}_{os.path.basename(pdf_path)}")
    try:
        shutil.copy(pdf_path, backup_path)
    except Exception as e:
        messagebox.showerror("Erro de Backup", f"Não foi possível criar o backup do PDF original: {e}")
        return
    try:
        # Criar widgets de progresso dentro do frame_pdf_selection
        progress_label = tk.Label(frame_pdf_selection, text="Iniciando processamento...", font=("Helvetica", 10))
        progress_label.grid(row=3, column=0, columnspan=3, pady=5)
        percent_label = tk.Label(frame_pdf_selection, text="0%", font=("Helvetica", 10))
        percent_label.grid(row=4, column=0, columnspan=3, pady=5)
        progress_bar = ttk.Progressbar(frame_pdf_selection, orient="horizontal", length=300, mode="determinate")
        progress_bar.grid(row=5, column=0, columnspan=3, pady=5)
        janela_principal.update_idletasks()

        original_doc = fitz.open(pdf_path)
        total_pages = original_doc.page_count
        output_doc = fitz.open()
        progress_bar["maximum"] = total_pages * 2  # Análise + Aplicação

        # Preparar tarefas para o pool
        tasks_for_pool = []
        for page_num in range(total_pages):
            page = original_doc[page_num]
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            tasks_for_pool.append((page_num, img_bytes, 300, pares_para_substituir, TESSERACT_PATH))

        # Processar páginas com multiprocessing
        results_from_pool = [None] * total_pages
        processed_pages = 0
        with multiprocessing.Pool(processes=os.cpu_count()) as pool:
            for page_index, changes_on_page_data in tqdm(pool.imap_unordered(_worker_process_page, tasks_for_pool), total=total_pages, desc="Analisando páginas"):
                results_from_pool[page_index] = changes_on_page_data
                processed_pages += 1
                progress_bar["value"] = processed_pages
                percent = (processed_pages / (total_pages * 2)) * 100
                progress_label.config(text=f"Analisando página {page_index+1} de {total_pages}")
                percent_label.config(text=f"{int(percent)}%")
                janela_principal.update_idletasks()

        # Aplicar alterações ao PDF
        progress_label.config(text="Aplicando alterações ao PDF...")
        for page_num in range(total_pages):
            page_original = original_doc[page_num]
            new_page = output_doc.new_page(width=page_original.rect.width, height=page_original.rect.height)
            new_page.show_pdf_page(new_page.rect, original_doc, page_num)
            changes_data = results_from_pool[page_num]
            pix_for_drawing = page_original.get_pixmap(dpi=300)
            scale_factor_x = page_original.rect.width / pix_for_drawing.width
            scale_factor_y = page_original.rect.height / pix_for_drawing.height
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except IOError:
                font = ImageFont.load_default()
            for change in changes_data:
                x0_img = change['left']
                y0_img = change['top']
                w_img = change['width']
                h_img = change['height']
                text_found_ocr = change['text_found_ocr']
                old_code_matched = change['old_code_matched']
                new_code_replacement = change['new_code_replacement']
                x0_pdf = x0_img * scale_factor_x
                y0_pdf = y0_img * scale_factor_y
                x1_pdf = (x0_img + w_img) * scale_factor_x
                y1_pdf = (y0_img + h_img) * scale_factor_y
                rect_to_erase = fitz.Rect(x0_pdf, y0_pdf, x1_pdf, y1_pdf)
                new_page.draw_rect(rect_to_erase, color=(1, 1, 1), fill=True)
                final_text_to_insert = text_found_ocr.replace(old_code_matched, new_code_replacement)
                fontsize_estimated = rect_to_erase.height * 0.8
                if fontsize_estimated < 5:
                    fontsize_estimated = 5
                new_page.insert_text(
                    (x0_pdf, y0_pdf),
                    final_text_to_insert,
                    fontsize=fontsize_estimated,
                    fontname="helv",
                    color=(0, 0, 0),
                    set_simple=True
                )
            processed_pages += 1
            progress_bar["value"] = processed_pages
            percent = (processed_pages / (total_pages * 2)) * 100
            progress_label.config(text=f"Aplicando alterações na página {page_num+1} de {total_pages}")
            percent_label.config(text=f"{int(percent)}%")
            janela_principal.update_idletasks()

        output_doc.save(output_filepath)
        output_doc.close()
        original_doc.close()
        # Remover widgets de progresso
        progress_label.destroy()
        percent_label.destroy()
        progress_bar.destroy()
        messagebox.showinfo("Sucesso", f"Processamento concluído! Arquivo salvo em:\n{output_filepath}")
        os.startfile(output_filepath)
    except Exception as e:
        # Remover widgets de progresso em caso de erro
        if 'progress_label' in locals():
            progress_label.destroy()
        if 'percent_label' in locals():
            percent_label.destroy()
        if 'progress_bar' in locals():
            progress_bar.destroy()
        messagebox.showerror("Erro de Processamento", f"Ocorreu um erro durante o processamento do PDF: {e}")
        raise

def selecionar_pdf():
    filepath = filedialog.askopenfilename(filetypes=[("Arquivos PDF", "*.pdf")])
    if filepath:
        entry_pdf_path.delete(0, tk.END)
        entry_pdf_path.insert(0, filepath)

# --- Funções de Login e Interface Gráfica ---
def fazer_login():
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    user_type = verificar_login(username, password)
    if user_type:
        tela_login.destroy()
        abrir_janela_principal(user_type)
    else:
        messagebox.showerror("Login", "Usuário ou senha inválidos.")

def abrir_janela_principal(user_type):
    global janela_principal, entry_pdf_path, var_direcao_substituicao, entry_busca_principal, tree_resultados_principal, logo_img_tk, frame_pdf_selection

    janela_principal = tk.Tk()
    janela_principal.title("Sistema de Gerenciamento de Códigos")
    janela_principal.geometry("800x700")

    # --- Adicionar Imagem como Fundo ---
    try:
        image_path = r"C:\Users\Allan\Desktop\projetoDireta\1234.jpg"
        logo_img = Image.open(image_path)
        window_width = 800
        window_height = 700
        logo_img = logo_img.resize((window_width, window_height), Image.LANCZOS)
        logo_img_tk = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(janela_principal, image=logo_img_tk)
        logo_label.image = logo_img_tk
        logo_label.place(x=0, y=0, relwidth=1, relheight=1)
        logo_label.lower()
    except FileNotFoundError:
        print(f"Erro: Arquivo de imagem '{image_path}' não encontrado. Verifique o caminho.")
        messagebox.showerror("Erro de Imagem", f"Não foi possível carregar a imagem: {image_path}. Arquivo não encontrado.")
        tk.Label(janela_principal, text="[Imagem não encontrada]").pack(pady=10)
    except Exception as e:
        print(f"Erro ao carregar imagem: {e}")
        messagebox.showerror("Erro de Imagem", f"Ocorreu um erro ao carregar a imagem: {e}")
        tk.Label(janela_principal, text="[Erro ao carregar imagem]").pack(pady=10)

    # Menu Bar
    menubar = tk.Menu(janela_principal)
    janela_principal.config(menu=menubar)
    admin_menu = tk.Menu(menubar, tearoff=0)
    if user_type == "admin":
        admin_menu.add_command(label="Gerenciar Usuários", command=abrir_tela_gerenciar_usuarios)
        admin_menu.add_command(label="Gerenciar Pares de Códigos", command=abrir_tela_gerenciar_pares)
        menubar.add_cascade(label="Administração", menu=admin_menu)

    # Título Principal
    tk.Label(janela_principal, text="Bem vindo", font=("Helvetica", 18, "bold")).pack(pady=20)

    # --- Seção de Seleção de PDF ---
    frame_pdf_selection = tk.LabelFrame(janela_principal, text="Processar PDF", padx=10, pady=10)
    frame_pdf_selection.pack(pady=5, padx=20, fill="x")

    tk.Label(frame_pdf_selection, text="Caminho do PDF:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_pdf_path = tk.Entry(frame_pdf_selection, width=50)
    entry_pdf_path.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(frame_pdf_selection, text="Selecionar PDF", command=selecionar_pdf).grid(row=0, column=2, padx=5, pady=5)

    tk.Label(frame_pdf_selection, text="Direção de Substituição:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    var_direcao_substituicao = tk.StringVar(value="DOM -> DIRETA")
    ttk.Radiobutton(frame_pdf_selection, text="DOM -> DIRETA", variable=var_direcao_substituicao, value="DOM -> DIRETA").grid(row=1, column=1, padx=5, pady=5, sticky="w")
    ttk.Radiobutton(frame_pdf_selection, text="DIRETA -> DOM", variable=var_direcao_substituicao, value="DIRETA -> DOM").grid(row=1, column=1, padx=5, pady=5, sticky="e")

    tk.Button(frame_pdf_selection, text="Processar PDF", command=processar_e_substituir_pdf,
              bg="#007BFF", fg="white", font=("Helvetica", 10, "bold")).grid(row=2, column=0, columnspan=3, pady=10)

    frame_pdf_selection.grid_columnconfigure(1, weight=1)

    # --- Seção de Busca Direta de Códigos ---
    frame_busca_e_resultados = tk.Frame(janela_principal)
    frame_busca_e_resultados.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)

    tk.Label(frame_busca_e_resultados, text="Buscar Pares de Códigos",
             font=("Helvetica", 14, "bold")).pack(pady=(10, 5))

    frame_busca_input = tk.Frame(frame_busca_e_resultados)
    frame_busca_input.pack(pady=5, fill="x")

    entry_busca_principal = tk.Entry(frame_busca_input, width=40, font=("Helvetica", 10), relief="solid", bd=1)
    entry_busca_principal.pack(side=tk.LEFT, padx=5, ipady=3, expand=True, fill="x")

    tk.Button(frame_busca_input, text="Buscar", command=realizar_busca_principal,
              font=("Helvetica", 10, "bold"), bg="#5cb85c", fg="white", relief="raised", padx=10, pady=3).pack(side=tk.LEFT, padx=5)

    tk.Label(frame_busca_e_resultados, text="Resultados da Busca",
             font=("Helvetica", 12, "bold")).pack(pady=(10, 5))

    tree_resultados_principal = ttk.Treeview(frame_busca_e_resultados, columns=("Cód. DOM", "Cód. Direta"), show="headings", height=1)
    tree_resultados_principal.heading("Cód. DOM", text="Código DOM")
    tree_resultados_principal.heading("Cód. Direta", text="Código Direta")
    tree_resultados_principal.column("Cód. DOM", width=250, anchor="center")
    tree_resultados_principal.column("Cód. Direta", width=250, anchor="center")
    tree_resultados_principal.pack(pady=5, fill="x")

    tree_resultados_principal.insert("", "end", values=("Digite um termo para buscar.", ""))

    janela_principal.mainloop()

# --- Função de Busca para a Tela Principal ---
def realizar_busca_principal():
    termo = entry_busca_principal.get().strip()
    for i in tree_resultados_principal.get_children():
        tree_resultados_principal.delete(i)
    if termo:
        pares_encontrados = buscar_pares_db(termo)
        if pares_encontrados:
            for par in pares_encontrados:
                tree_resultados_principal.insert("", "end", values=(par[1], par[2]))
        else:
            tree_resultados_principal.insert("", "end", values=("Nenhum resultado encontrado para o termo exato.", ""))
    else:
        tree_resultados_principal.insert("", "end", values=("Digite um termo para buscar.", ""))

# --- Tela de Login ---
if __name__ == '__main__':
    criar_banco()
    tela_login = tk.Tk()
    tela_login.title("Login")
    tela_login.geometry("300x200")
    tela_login.resizable(False, False)
    frame_login = tk.Frame(tela_login, padx=20, pady=20)
    frame_login.pack(expand=True)
    tk.Label(frame_login, text="Usuário:", font=("Helvetica", 10)).pack(pady=5)
    entry_username = tk.Entry(frame_login, width=25)
    entry_username.pack(pady=5)
    tk.Label(frame_login, text="Senha:", font=("Helvetica", 10)).pack(pady=5)
    entry_password = tk.Entry(frame_login, width=25, show="*")
    entry_password.pack(pady=5)
    tk.Button(frame_login, text="Entrar", command=fazer_login, bg="#007BFF", fg="white", font=("Helvetica", 10, "bold")).pack(pady=10)
    tela_login.mainloop()