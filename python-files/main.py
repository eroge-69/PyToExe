from banco import banco

def main():
    print("Bem-vindo ao Afonso's Bank!")
    banco.iniciar()

if __name__ == "__main__":
    main()
# main.py
from banco import banco

if __name__ == "__main__":
    banco.iniciar()
# main.py
from banco import banco

if __name__ == "__main__":
    banco.iniciar()
# main.py
from banco import banco

if __name__ == "__main__":
    banco.iniciar()
import tkinter as tk
from tkinter import messagebox, simpledialog
from banco import clientes, contas, transacoes, relatorios
from datetime import datetime

LUNA = "Ł"  # Símbolo da moeda Luna

# ---------- Janela principal ----------
root = tk.Tk()
root.title("Afonso's Bank")
root.geometry("800x600")
root.configure(bg="#1e1e2f")

# ---------- Funções de interface ----------
cliente_logado = None

def login():
    global cliente_logado
    nome = simpledialog.askstring("Login", "Nome do cliente:")
    senha = simpledialog.askstring("Login", "Senha:", show='*')
    dados = clientes.carregar_dados()
    cliente = next((c for c in dados["clientes"] if c["nome"] == nome and c["senha"] == senha), None)
    if cliente:
        cliente_logado = cliente
        messagebox.showinfo("Login", f"✅ Bem-vindo, {nome}!")
        mostrar_menu()
    else:
        messagebox.showerror("Login", "❌ Nome ou senha incorretos!")

def mostrar_menu():
    menu_frame = tk.Frame(root, bg="#1e1e2f")
    menu_frame.pack(fill="both", expand=True)

    tk.Label(menu_frame, text="Afonso's Bank", font=("Helvetica", 24), fg="#ffcc00", bg="#1e1e2f").pack(pady=20)

    # Botões principais
    botoes = [
        ("💰 Depositar", depositar),
        ("🏦 Levantar", levantar),
        ("🔁 Transferir", transferir_gui),
        ("💹 Aplicar Juros", aplicar_juros_gui),
        ("📄 Relatório de Conta", relatorio_gui),
        ("📊 Ranking de Clientes", ranking_gui),
        ("💸 Pedir dinheiro ao banco", pedir_dinheiro_gui),
        ("🚪 Sair", root.quit)
    ]

    for (txt, cmd) in botoes:
        tk.Button(menu_frame, text=txt, font=("Helvetica", 16), width=30, command=cmd, bg="#28293d", fg="#ffffff").pack(pady=5)

# ---------- Funções bancárias com GUI ----------
def depositar():
    if not cliente_logado:
        messagebox.showerror("Erro", "❌ Faça login primeiro!")
        return
    valor = simpledialog.askfloat("Depósito", "Valor a depositar:")
    conta = contas.buscar_conta_por_cliente(cliente_logado["id"])
    if conta and valor > 0:
        transacoes.depositar(conta["id"], valor)
        messagebox.showinfo("Depósito", f"💰 Depositado {valor:.2f} {LUNA} com sucesso!")

def levantar():
    if not cliente_logado:
        messagebox.showerror("Erro", "❌ Faça login primeiro!")
        return
    valor = simpledialog.askfloat("Levantamento", "Valor a levantar:")
    conta = contas.buscar_conta_por_cliente(cliente_logado["id"])
    if conta:
        res = transacoes.levantar(conta["id"], valor)
        if isinstance(res, dict):
            messagebox.showinfo("Levantamento", f"🏦 Levantado {valor:.2f} {LUNA} com sucesso!")
        else:
            messagebox.showerror("Erro", "❌ Saldo insuficiente!")

def transferir_gui():
    if not cliente_logado:
        messagebox.showerror("Erro", "❌ Faça login primeiro!")
        return
    conta_origem = contas.buscar_conta_por_cliente(cliente_logado["id"])
    destino_id = simpledialog.askinteger("Transferência", "ID da conta destino:")
    valor = simpledialog.askfloat("Transferência", "Valor a transferir:")
    if conta_origem:
        transacoes.transferir(conta_origem["id"], destino_id, valor)

def aplicar_juros_gui():
    taxa = simpledialog.askfloat("Juros", "Taxa de juros (%) a aplicar:")
    contas.aplicar_juros_automaticos(taxa)
    messagebox.showinfo("Juros", f"💹 Juros de {taxa}% aplicados a todas as contas!")

def relatorio_gui():
    conta = contas.buscar_conta_por_cliente(cliente_logado["id"])
    relatorios.gerar_relatorio_conta(conta["id"])

def ranking_gui():
    relatorios.ranking_clientes_trofeus()

def pedir_dinheiro_gui():
    conta = contas.buscar_conta_por_cliente(cliente_logado["id"])
    valor = simpledialog.askfloat("Empréstimo", "Valor a pedir ao banco:")
    transacoes.pedir_dinheiro(conta["id"], valor)

# ---------- Iniciar aplicação ----------
login()
root.mainloop()
