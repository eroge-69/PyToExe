import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

# ================= CONFIGURAÇÕES =================
VALOR_SEMESTRAL = 150.0  # valor fixo, pode editar aqui
VALOR_ANUAL = 250.0      # valor fixo, pode editar aqui

# ================= BANCO DE DADOS =================

def init_db():
    conn = sqlite3.connect("assinaturas.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bairros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assinantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            endereco TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assinaturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assinante_id INTEGER,
            bairro_id INTEGER,
            data_inicio TEXT,
            duracao TEXT CHECK(duracao IN ('6 meses','12 meses')) NOT NULL,
            data_vencimento TEXT,
            valor REAL,
            status TEXT CHECK(status IN ('Ativa','Cancelada')) NOT NULL DEFAULT 'Ativa',
            FOREIGN KEY(assinante_id) REFERENCES assinantes(id),
            FOREIGN KEY(bairro_id) REFERENCES bairros(id)
        )
    """)

    conn.commit()
    conn.close()

# ================= FUNÇÕES =================

def atualizar_treeview(tree, tabela):
    for item in tree.get_children():
        tree.delete(item)

    conn = sqlite3.connect("assinaturas.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {tabela}")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)
    conn.close()

# ================= INTERFACE =================

def main():
    init_db()

    root = tk.Tk()
    root.title("Controle de Assinaturas")
    root.geometry("900x650")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # -------- ABA BAIRROS --------
    frame_bairros = ttk.Frame(notebook)
    notebook.add(frame_bairros, text="Bairros")

    tk.Label(frame_bairros, text="Nome do Bairro:").pack(pady=5)
    entry_bairro = tk.Entry(frame_bairros)
    entry_bairro.pack(pady=5)

    def adicionar_bairro():
        nome = entry_bairro.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Digite o nome do bairro!")
            return
        try:
            conn = sqlite3.connect("assinaturas.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO bairros (nome) VALUES (?)", (nome,))
            conn.commit()
            conn.close()
            atualizar_treeview(tree_bairros, "bairros")
            entry_bairro.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Este bairro já existe!")

    tk.Button(frame_bairros, text="Adicionar", command=adicionar_bairro).pack(pady=5)

    tree_bairros = ttk.Treeview(frame_bairros, columns=("ID", "Nome"), show="headings")
    tree_bairros.heading("ID", text="ID")
    tree_bairros.heading("Nome", text="Nome")
    tree_bairros.pack(expand=True, fill="both")
    atualizar_treeview(tree_bairros, "bairros")

    # -------- ABA ASSINANTES --------
    frame_assinantes = ttk.Frame(notebook)
    notebook.add(frame_assinantes, text="Assinantes")

    tk.Label(frame_assinantes, text="Nome:").pack()
    entry_nome = tk.Entry(frame_assinantes)
    entry_nome.pack()

    tk.Label(frame_assinantes, text="Telefone:").pack()
    entry_telefone = tk.Entry(frame_assinantes)
    entry_telefone.pack()

    tk.Label(frame_assinantes, text="Endereço:").pack()
    entry_endereco = tk.Entry(frame_assinantes)
    entry_endereco.pack()

    def adicionar_assinante():
        nome = entry_nome.get().strip()
        telefone = entry_telefone.get().strip()
        endereco = entry_endereco.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "O nome é obrigatório!")
            return
        conn = sqlite3.connect("assinaturas.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO assinantes (nome, telefone, endereco) VALUES (?,?,?)", (nome, telefone, endereco))
        conn.commit()
        conn.close()
        atualizar_treeview(tree_assinantes, "assinantes")
        entry_nome.delete(0, tk.END)
        entry_telefone.delete(0, tk.END)
        entry_endereco.delete(0, tk.END)

    tk.Button(frame_assinantes, text="Adicionar", command=adicionar_assinante).pack(pady=5)

    tree_assinantes = ttk.Treeview(frame_assinantes, columns=("ID", "Nome", "Telefone", "Endereço"), show="headings")
    for col in ("ID", "Nome", "Telefone", "Endereço"):
        tree_assinantes.heading(col, text=col)
    tree_assinantes.pack(expand=True, fill="both")
    atualizar_treeview(tree_assinantes, "assinantes")

    # -------- ABA ASSINATURAS --------
    frame_assinaturas = ttk.Frame(notebook)
    notebook.add(frame_assinaturas, text="Assinaturas")

    tk.Label(frame_assinaturas, text="ID Assinante:").pack()
    entry_assinante_id = tk.Entry(frame_assinaturas)
    entry_assinante_id.pack()

    tk.Label(frame_assinaturas, text="ID Bairro:").pack()
    entry_bairro_id = tk.Entry(frame_assinaturas)
    entry_bairro_id.pack()

    tk.Label(frame_assinaturas, text="Data de início (dd/mm/aaaa):").pack()
    entry_data_inicio = tk.Entry(frame_assinaturas)
    entry_data_inicio.pack()

    tk.Label(frame_assinaturas, text="Plano:").pack()
    plano_var = tk.StringVar(value="6 meses")
    combo_plano = ttk.Combobox(frame_assinaturas, textvariable=plano_var, values=("6 meses", "12 meses"))
    combo_plano.pack()

    def adicionar_assinatura():
        assinante_id = entry_assinante_id.get().strip()
        bairro_id = entry_bairro_id.get().strip()
        data_inicio = entry_data_inicio.get().strip()
        duracao = plano_var.get()

        if not assinante_id or not bairro_id or not data_inicio:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return

        try:
            dt_inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Erro", "Data inválida! Use o formato dd/mm/aaaa.")
            return

        meses = 6 if duracao == "6 meses" else 12
        dt_vencimento = dt_inicio + timedelta(days=30*meses)

        valor = VALOR_SEMESTRAL if duracao == "6 meses" else VALOR_ANUAL

        conn = sqlite3.connect("assinaturas.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO assinaturas (assinante_id, bairro_id, data_inicio, duracao, data_vencimento, valor, status)
            VALUES (?,?,?,?,?,?,?)
        """, (assinante_id, bairro_id, data_inicio, duracao, dt_vencimento.strftime("%d/%m/%Y"), valor, "Ativa"))
        conn.commit()
        conn.close()

        atualizar_treeview(tree_assinaturas, "assinaturas")
        entry_assinante_id.delete(0, tk.END)
        entry_bairro_id.delete(0, tk.END)
        entry_data_inicio.delete(0, tk.END)

    tk.Button(frame_assinaturas, text="Adicionar", command=adicionar_assinatura).pack(pady=5)

    tree_assinaturas = ttk.Treeview(frame_assinaturas, columns=("ID", "Assinante", "Bairro", "Data Início", "Plano", "Vencimento", "Valor", "Status"), show="headings")
    for col in ("ID", "Assinante", "Bairro", "Data Início", "Plano", "Vencimento", "Valor", "Status"):
        tree_assinaturas.heading(col, text=col)
    tree_assinaturas.pack(expand=True, fill="both")
    atualizar_treeview(tree_assinaturas, "assinaturas")

    # -------- ABA RELATÓRIOS --------
    frame_relatorios = ttk.Frame(notebook)
    notebook.add(frame_relatorios, text="Relatórios")

    text_relatorio = tk.Text(frame_relatorios)
    text_relatorio.pack(expand=True, fill="both")

    def gerar_relatorio():
        text_relatorio.delete("1.0", tk.END)
        conn = sqlite3.connect("assinaturas.db")
        cursor = conn.cursor()

        cursor.execute("SELECT data_inicio, valor FROM assinaturas WHERE status='Ativa'")
        assinaturas = cursor.fetchall()

        relatorio = {}
        for data_inicio, valor in assinaturas:
            mes = data_inicio[3:10]  # pega mm/aaaa
            relatorio[mes] = relatorio.get(mes, 0) + valor

        for mes, total in relatorio.items():
            text_relatorio.insert(tk.END, f"Mês {mes}: R$ {total:.2f}\n")

        conn.close()

    tk.Button(frame_relatorios, text="Gerar Relatório", command=gerar_relatorio).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
