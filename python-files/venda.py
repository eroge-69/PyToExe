import tkinter as tk
from tkinter import simpledialog, messagebox
import mysql.connector
from datetime import datetime

# --- Configurações do Banco de Dados ---
# ATENÇÃO: Preencha com os dados da sua hospedagem
DB_HOST = "193.203.175.173"
DB_USER = "u356969723_dash"
DB_PASSWORD = "5691162002Lo@"
DB_NAME = "u356969723_dash"

# --- Módulo para Conexão e Inserção de Dados ---
def inserir_venda(id_funcionario, valor_venda, produto_vendido):
    """Insere uma nova venda no banco de dados MySQL, incluindo o produto."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        sql = "INSERT INTO vendas (id_funcionario, valor_venda, produto_vendido, data_venda) VALUES (%s, %s, %s, %s)"
        data = (id_funcionario, valor_venda, produto_vendido, datetime.now())
        
        cursor.execute(sql, data)
        conn.commit()
        
        messagebox.showinfo("Sucesso", "Venda de R$ {:.2f} registrada! Produto: {}".format(valor_venda, produto_vendido))

    except mysql.connector.Error as err:
        messagebox.showerror("Erro no Banco de Dados", f"Algo deu errado: {err}")
    
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# --- Módulo da Interface Gráfica (Tkinter) ---
class BotaoFlutuante(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.overrideredirect(True)
        self.wm_attributes("-topmost", 1)
        self.attributes("-alpha", 0.8)
        
        # Frame para organizar os botões
        self.frame = tk.Frame(self)
        self.frame.pack(padx=10, pady=10)
        
        # Botão "Vendeu!"
        self.button_vendeu = tk.Button(
            self.frame,
            text="Vendeu!",
            font=("Arial", 12, "bold"),
            bg="#2ecc71",
            fg="white",
            relief="raised",
            cursor="hand2",
            command=self.abrir_janela_venda
        )
        self.button_vendeu.pack(side=tk.LEFT, padx=5)
        
        # Botão "Fechar"
        self.button_fechar = tk.Button(
            self.frame,
            text="Fechar",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            relief="raised",
            cursor="hand2",
            command=self.destroy
        )
        self.button_fechar.pack(side=tk.LEFT, padx=5)
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f'+{screen_width-200}+{screen_height-100}')

    def abrir_janela_venda(self):
        """Abre uma nova janela de diálogo para registrar a venda."""
        try:
            id_funcionario = simpledialog.askinteger("Registro de Venda", "ID do funcionário:")
            if id_funcionario is None: return

            valor_venda = simpledialog.askfloat("Registro de Venda", "Valor da venda:")
            if valor_venda is None: return
            
            produto_vendido = simpledialog.askstring("Registro de Venda", "Produto vendido:")
            if produto_vendido is None: return

            inserir_venda(id_funcionario, valor_venda, produto_vendido)

        except Exception as e:
            messagebox.showerror("Erro de Entrada", "Algum dos valores inseridos não é válido. Tente novamente.")
            
if __name__ == "__main__":
    app = BotaoFlutuante()
    app.mainloop()