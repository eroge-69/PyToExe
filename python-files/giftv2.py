import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyodbc
import threading
from datetime import datetime
import json
import os

class CombatArmsGMTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Combat Arms GM Tool v1.0")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Database connection variables
        self.connection = None
        self.is_connected = False
        
        # Default connection settings
        self.config = {
            'server': '192.168.1.128\\BR', #NameofPC or IP + SQL Instance Name
            'username': 'sa', 
            'password': 'sqlpasswordhere',
            'database': 'COMBATARMS'
        }
        
        # Items cache
        self.all_items = []
        self.filtered_items = []
        
        self.setup_styles()
        self.create_interface()
        self.load_config()
        
    def setup_styles(self):
        """Configurar estilos da interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='white')
        style.configure('TButton', background='#4a5568', foreground='white')
        style.configure('TEntry', fieldbackground='#4a5568', foreground='white')
        style.configure('Treeview', background='#4a5568', foreground='white')
        style.configure('Treeview.Heading', background='#2d3748', foreground='white')
        
    def create_interface(self):
        """Criar a interface principal"""
        # Notebook para abas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba 1: Conexão
        self.create_connection_tab(notebook)
        
        # Aba 2: Buscar Itens
        self.create_search_tab(notebook)
        
        # Aba 3: Enviar Itens
        self.create_send_tab(notebook)
        
        # Aba 4: Logs
        self.create_logs_tab(notebook)
        
        # Status bar
        self.create_status_bar()
        
    def create_connection_tab(self, notebook):
        """Criar aba de conexão"""
        conn_frame = ttk.Frame(notebook)
        notebook.add(conn_frame, text='🔌 Conexão')
        
        # Title
        title = tk.Label(conn_frame, text="Configuração da Conexão", 
                        font=('Arial', 16, 'bold'), bg='#2b2b2b', fg='white')
        title.pack(pady=10)
        
        # Connection form
        form_frame = ttk.Frame(conn_frame)
        form_frame.pack(pady=20)
        
        # Server
        ttk.Label(form_frame, text="Servidor:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.server_entry = ttk.Entry(form_frame, width=30)
        self.server_entry.grid(row=0, column=1, padx=5, pady=5)
        self.server_entry.insert(0, self.config['server'])
        
        # Username
        ttk.Label(form_frame, text="Usuário:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)
        self.username_entry.insert(0, self.config['username'])
        
        # Password
        ttk.Label(form_frame, text="Senha:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.password_entry = ttk.Entry(form_frame, width=30, show='*')
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)
        self.password_entry.insert(0, self.config['password'])
        
        # Database
        ttk.Label(form_frame, text="Banco:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.database_entry = ttk.Entry(form_frame, width=30)
        self.database_entry.grid(row=3, column=1, padx=5, pady=5)
        self.database_entry.insert(0, self.config['database'])
        
        # Buttons
        btn_frame = ttk.Frame(conn_frame)
        btn_frame.pack(pady=20)
        
        self.test_btn = ttk.Button(btn_frame, text="🔍 Testar Conexão", command=self.test_connection)
        self.test_btn.pack(side='left', padx=5)
        
        self.connect_btn = ttk.Button(btn_frame, text="🔗 Conectar", command=self.connect_database)
        self.connect_btn.pack(side='left', padx=5)
        
        self.disconnect_btn = ttk.Button(btn_frame, text="❌ Desconectar", 
                                       command=self.disconnect_database, state='disabled')
        self.disconnect_btn.pack(side='left', padx=5)
        
        # Status
        self.conn_status = tk.Label(conn_frame, text="Status: Desconectado", 
                                   bg='#2b2b2b', fg='red', font=('Arial', 12, 'bold'))
        self.conn_status.pack(pady=10)
        
    def create_search_tab(self, notebook):
        """Criar aba de busca de itens com TODOS os campos - CORRIGIDA"""
        search_frame = ttk.Frame(notebook)
        notebook.add(search_frame, text='🔍 Buscar Itens')
        
        # Title
        title = tk.Label(search_frame, text="Buscar Itens - TODOS OS CAMPOS CBT_ProductInfo", 
                        font=('Arial', 16, 'bold'), bg='#2b2b2b', fg='white')
        title.pack(pady=10)
        
        # Search section
        search_section = ttk.Frame(search_frame)
        search_section.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(search_section, text="Pesquisar:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_section, width=30)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        self.search_btn = ttk.Button(search_section, text="🔍 Buscar", command=self.search_items)
        self.search_btn.pack(side='left', padx=5)
        
        self.load_all_btn = ttk.Button(search_section, text="📋 Carregar Todos", command=self.load_all_items)
        self.load_all_btn.pack(side='left', padx=5)
        
        # Results info
        self.results_label = tk.Label(search_frame, text="0 itens encontrados", 
                                     bg='#2b2b2b', fg='white')
        self.results_label.pack(anchor='w', padx=20, pady=5)
        
        # Container para a tabela com scrollbars - USANDO APENAS PACK
        table_container = ttk.Frame(search_frame)
        table_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview com TODAS as colunas da CBT_ProductInfo
        columns = (
            'ProductID', 'ProductName', 'SaleType', 'Price', 'SalePrice', 'BonusGP', 'ItemNum',
            'ItemNo00', 'ConsumeType00', 'Period00', 'ItemNo01', 'ConsumeType01', 'Period01',
            'ItemNo02', 'ConsumeType02', 'Period02', 'ItemNo03', 'ConsumeType03', 'Period03',
            'ItemNo04', 'ConsumeType04', 'Period04', 'ActivationUnlock', 'InboxGift'
        )
        
        self.items_tree = ttk.Treeview(table_container, columns=columns, show='headings', height=12)
        
        # Configurar TODAS as colunas
        column_configs = {
            'ProductID': {'text': 'ProductID', 'width': 80},
            'ProductName': {'text': 'Nome do Produto', 'width': 200},
            'SaleType': {'text': 'Tipo Venda', 'width': 70},
            'Price': {'text': 'Preço', 'width': 70},
            'SalePrice': {'text': 'Preço Venda', 'width': 80},
            'BonusGP': {'text': 'Bonus GP', 'width': 70},
            'ItemNum': {'text': 'Qtd Itens', 'width': 60},
            'ItemNo00': {'text': 'Item 00', 'width': 60},
            'ConsumeType00': {'text': 'Tipo 00', 'width': 60},
            'Period00': {'text': 'Período 00', 'width': 70},
            'ItemNo01': {'text': 'Item 01', 'width': 60},
            'ConsumeType01': {'text': 'Tipo 01', 'width': 60},
            'Period01': {'text': 'Período 01', 'width': 70},
            'ItemNo02': {'text': 'Item 02', 'width': 60},
            'ConsumeType02': {'text': 'Tipo 02', 'width': 60},
            'Period02': {'text': 'Período 02', 'width': 70},
            'ItemNo03': {'text': 'Item 03', 'width': 60},
            'ConsumeType03': {'text': 'Tipo 03', 'width': 60},
            'Period03': {'text': 'Período 03', 'width': 70},
            'ItemNo04': {'text': 'Item 04', 'width': 60},
            'ConsumeType04': {'text': 'Tipo 04', 'width': 60},
            'Period04': {'text': 'Período 04', 'width': 70},
            'ActivationUnlock': {'text': 'Activation', 'width': 80},
            'InboxGift': {'text': 'Inbox Gift', 'width': 70}
        }
        
        for col in columns:
            config = column_configs[col]
            self.items_tree.heading(col, text=config['text'])
            self.items_tree.column(col, width=config['width'])
        
        # Scrollbars - USANDO APENAS PACK
        h_scrollbar = ttk.Scrollbar(table_container, orient='horizontal', command=self.items_tree.xview)
        v_scrollbar = ttk.Scrollbar(table_container, orient='vertical', command=self.items_tree.yview)
        self.items_tree.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Posicionamento com pack
        self.items_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Double click to select item
        self.items_tree.bind('<Double-1>', self.on_item_double_click)
        
        # Quick send section
        quick_send_frame = ttk.Frame(search_frame)
        quick_send_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(quick_send_frame, text="Envio Rápido:").pack(side='left', padx=5)
        self.quick_player_entry = ttk.Entry(quick_send_frame, width=20)
        self.quick_player_entry.pack(side='left', padx=5)
        
        # Placeholder manual
        self.quick_player_entry.insert(0, "Nome do jogador")
        self.quick_player_entry.bind('<FocusIn>', self.clear_placeholder)
        self.quick_player_entry.bind('<FocusOut>', self.add_placeholder)
        self.quick_player_entry.config(foreground='gray')
        
        self.quick_send_btn = ttk.Button(quick_send_frame, text="📤 Enviar Selecionado", 
                                        command=self.quick_send_item)
        self.quick_send_btn.pack(side='left', padx=5)
        
    def clear_placeholder(self, event):
        """Limpar placeholder ao focar"""
        if self.quick_player_entry.get() == "Nome do jogador":
            self.quick_player_entry.delete(0, tk.END)
            self.quick_player_entry.config(foreground='white')
            
    def add_placeholder(self, event):
        """Adicionar placeholder ao desfocar"""
        if not self.quick_player_entry.get():
            self.quick_player_entry.insert(0, "Nome do jogador")
            self.quick_player_entry.config(foreground='gray')
        
    def create_send_tab(self, notebook):
        """Criar aba de envio de itens"""
        send_frame = ttk.Frame(notebook)
        notebook.add(send_frame, text='🎁 Enviar Itens')
        
        # Title
        title = tk.Label(send_frame, text="Enviar Item para Jogador", 
                        font=('Arial', 16, 'bold'), bg='#2b2b2b', fg='white')
        title.pack(pady=10)
        
        # Send form
        form_frame = ttk.Frame(send_frame)
        form_frame.pack(pady=20)
        
        # Player name
        ttk.Label(form_frame, text="Nome do Jogador:").grid(row=0, column=0, sticky='w', padx=5, pady=10)
        self.player_name_entry = ttk.Entry(form_frame, width=30)
        self.player_name_entry.grid(row=0, column=1, padx=5, pady=10)
        
        # Product ID
        ttk.Label(form_frame, text="Product ID:").grid(row=1, column=0, sticky='w', padx=5, pady=10)
        self.product_id_entry = ttk.Entry(form_frame, width=30)
        self.product_id_entry.grid(row=1, column=1, padx=5, pady=10)
        self.product_id_entry.bind('<KeyRelease>', self.preview_item)
        
        # Message
        ttk.Label(form_frame, text="Mensagem:").grid(row=2, column=0, sticky='nw', padx=5, pady=10)
        self.message_text = tk.Text(form_frame, width=30, height=3, bg='#4a5568', fg='white')
        self.message_text.grid(row=2, column=1, padx=5, pady=10)
        self.message_text.insert('1.0', 'Item enviado pela administração')
        
        # Send button
        send_btn = ttk.Button(form_frame, text="📤 Enviar Gift", command=self.send_item)
        send_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Quick actions - baseados nos ProductIDs reais
        quick_frame = ttk.LabelFrame(send_frame, text="Itens Populares")
        quick_frame.pack(pady=20, padx=20, fill='x')
        
        quick_buttons_frame = ttk.Frame(quick_frame)
        quick_buttons_frame.pack(pady=10)
        
        # Botões baseados nos dados reais da sua tabela
        ttk.Button(quick_buttons_frame, text="🔫 AK-47 (103)", 
                  command=lambda: self.set_quick_item(103)).pack(side='left', padx=5)
        ttk.Button(quick_buttons_frame, text="🔫 M4A1 (70)", 
                  command=lambda: self.set_quick_item(70)).pack(side='left', padx=5)
        ttk.Button(quick_buttons_frame, text="🔫 MP5A4 (65)", 
                  command=lambda: self.set_quick_item(65)).pack(side='left', padx=5)
        ttk.Button(quick_buttons_frame, text="📦 Supply Case (0)", 
                  command=lambda: self.set_quick_item(0)).pack(side='left', padx=5)
        
        # Item preview
        self.preview_frame = ttk.LabelFrame(send_frame, text="Preview do Item Completo")
        self.preview_frame.pack(pady=10, padx=20, fill='x')
        
        self.preview_text = scrolledtext.ScrolledText(self.preview_frame, height=8, 
                                                     bg='#4a5568', fg='white', state='disabled')
        self.preview_text.pack(pady=10, padx=10, fill='x')
        
    def set_quick_item(self, product_id):
        """Definir item rápido"""
        self.product_id_entry.delete(0, tk.END)
        self.product_id_entry.insert(0, str(product_id))
        self.preview_item(None)
        self.log_message(f"Item selecionado: ProductID {product_id}")
        
    def create_logs_tab(self, notebook):
        """Criar aba de logs"""
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text='📋 Logs')
        
        # Title
        title = tk.Label(logs_frame, text="Log de Ações", 
                        font=('Arial', 16, 'bold'), bg='#2b2b2b', fg='white')
        title.pack(pady=10)
        
        # Logs text area
        self.logs_text = scrolledtext.ScrolledText(logs_frame, bg='#1a1a1a', fg='lightgreen', 
                                                  font=('Consolas', 10))
        self.logs_text.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Clear logs button
        clear_btn = ttk.Button(logs_frame, text="🗑️ Limpar Logs", command=self.clear_logs)
        clear_btn.pack(pady=10)
        
        self.log_message("Combat Arms GM Tool iniciado")
        self.log_message("Versão: 1.0 - Mostrando TODOS os campos da CBT_ProductInfo")
        
    def create_status_bar(self):
        """Criar barra de status"""
        self.status_bar = tk.Label(self.root, text="Pronto - Conecte-se ao banco para começar", 
                                  bd=1, relief='sunken', anchor='w', bg='#2b2b2b', fg='white')
        self.status_bar.pack(side='bottom', fill='x')
        
    def load_config(self):
        """Carregar configuração salva"""
        try:
            if os.path.exists('gm_tool_config.json'):
                with open('gm_tool_config.json', 'r') as f:
                    self.config.update(json.load(f))
                    
                # Update form fields
                self.server_entry.delete(0, tk.END)
                self.server_entry.insert(0, self.config['server'])
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, self.config['username'])
                self.password_entry.delete(0, tk.END)
                self.password_entry.insert(0, self.config['password'])
                self.database_entry.delete(0, tk.END)
                self.database_entry.insert(0, self.config['database'])
                
                self.log_message("Configuração carregada do arquivo")
        except Exception as e:
            self.log_message(f"Erro ao carregar configuração: {e}")
            
    def save_config(self):
        """Salvar configuração atual"""
        try:
            self.config = {
                'server': self.server_entry.get(),
                'username': self.username_entry.get(),
                'password': self.password_entry.get(),
                'database': self.database_entry.get()
            }
            
            with open('gm_tool_config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
                
            self.log_message("Configuração salva")
        except Exception as e:
            self.log_message(f"Erro ao salvar configuração: {e}")
            
    def test_connection(self):
        """Testar conexão com o banco"""
        def test():
            try:
                self.update_status("Testando conexão com o banco...")
                conn_string = self.build_connection_string()
                
                test_conn = pyodbc.connect(conn_string, timeout=10)
                cursor = test_conn.cursor()
                
                # Testar tabelas específicas do Combat Arms
                cursor.execute("SELECT COUNT(*) FROM CBT_User")
                user_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM CBT_ProductInfo")
                product_count = cursor.fetchone()[0]
                
                test_conn.close()
                
                messagebox.showinfo("Sucesso", 
                                  f"Conexão testada com sucesso!"
                                  f"👥 Usuários: {user_count:,}"
                                  f"📦 Produtos: {product_count:,}")
                
                self.log_message(f"Teste bem-sucedido - {user_count} usuários, {product_count} produtos")
                self.update_status("Teste de conexão bem-sucedido")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Falha na conexão:{str(e)}")
                self.log_message(f"Erro no teste: {e}")
                self.update_status("Falha no teste de conexão")
                
        thread = threading.Thread(target=test)
        thread.daemon = True
        thread.start()
        
    def connect_database(self):
        """Conectar ao banco de dados"""
        def connect():
            try:
                self.update_status("Conectando ao banco...")
                conn_string = self.build_connection_string()
                
                self.connection = pyodbc.connect(conn_string)
                self.is_connected = True
                
                self.conn_status.config(text="Status: ✅ Conectado", fg='green')
                self.connect_btn.config(state='disabled')
                self.disconnect_btn.config(state='normal')
                
                messagebox.showinfo("Sucesso", "Conectado ao Combat Arms Database!")
                self.log_message("Conectado ao banco COMBATARMS")
                self.update_status("Conectado - Pronto para enviar itens")
                self.save_config()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Falha na conexão:{str(e)}")
                self.log_message(f"Erro na conexão: {e}")
                self.update_status("Erro na conexão")
                
        thread = threading.Thread(target=connect)
        thread.daemon = True
        thread.start()
        
    def disconnect_database(self):
        """Desconectar do banco"""
        if self.connection:
            self.connection.close()
            self.connection = None
            
        self.is_connected = False
        self.conn_status.config(text="Status: ❌ Desconectado", fg='red')
        self.connect_btn.config(state='normal')
        self.disconnect_btn.config(state='disabled')
        
        self.log_message("Desconectado do banco")
        self.update_status("Desconectado")
        
    def build_connection_string(self):
        """Construir string de conexão com fallback para drivers disponíveis"""
        server = self.server_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        database = self.database_entry.get()
        
        # Tentar diferentes drivers ODBC em ordem de preferência
        drivers = [
            "ODBC Driver 17 for SQL Server",
            "ODBC Driver 13 for SQL Server", 
            "ODBC Driver 11 for SQL Server",
            "SQL Server Native Client 11.0",
            "SQL Server Native Client 10.0",
            "SQL Server"
        ]
        
        # Testar qual driver está disponível
        available_driver = None
        for driver in drivers:
            try:
                test_conn_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE=master;UID={username};PWD={password};Timeout=5;"
                test_conn = pyodbc.connect(test_conn_string, timeout=2)
                test_conn.close()
                available_driver = driver
                break
            except:
                continue
        
        if not available_driver:
            # Fallback para string sem driver específico
            return f"SERVER={server};DATABASE={database};UID={username};PWD={password};Trusted_Connection=no;"
        
        # Retornar string com driver funcionando
        return f"DRIVER={{{available_driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=no;TrustServerCertificate=yes;"
        
    def load_all_items(self):
        """Carregar TODOS os produtos com TODOS os campos da CBT_ProductInfo"""
        if not self.is_connected:
            messagebox.showwarning("Aviso", "Conecte-se ao banco primeiro!")
            return
            
        def load():
            try:
                self.update_status("Carregando TODOS os produtos com TODOS os campos...")
                cursor = self.connection.cursor()
                
                # Query com TODOS os campos da CBT_ProductInfo
                query = """
                    SELECT 
                        ProductID, ProductName, SaleType, Price, SalePrice, BonusGP, ItemNum,
                        ItemNo00, ConsumeType00, Period00, ItemNo01, ConsumeType01, Period01,
                        ItemNo02, ConsumeType02, Period02, ItemNo03, ConsumeType03, Period03,
                        ItemNo04, ConsumeType04, Period04, ActivationUnlock, InboxGift
                    FROM CBT_ProductInfo
                    ORDER BY ProductID
                """
                
                cursor.execute(query)
                products = cursor.fetchall()
                
                self.all_items = []
                for product in products:
                    # Armazenar TODOS os campos
                    item_data = {
                        'ProductID': product[0],
                        'ProductName': product[1] if product[1] else f"Product {product[0]}",
                        'SaleType': product[2] if product[2] is not None else 0,
                        'Price': product[3] if product[3] is not None else 0,
                        'SalePrice': product[4] if product[4] is not None else 0,
                        'BonusGP': product[5] if product[5] is not None else 0,
                        'ItemNum': product[6] if product[6] is not None else 0,
                        'ItemNo00': product[7] if product[7] is not None else 0,
                        'ConsumeType00': product[8] if product[8] is not None else 0,
                        'Period00': product[9] if product[9] is not None else 0,
                        'ItemNo01': product[10] if product[10] is not None else 0,
                        'ConsumeType01': product[11] if product[11] is not None else 0,
                        'Period01': product[12] if product[12] is not None else 0,
                        'ItemNo02': product[13] if product[13] is not None else 0,
                        'ConsumeType02': product[14] if product[14] is not None else 0,
                        'Period02': product[15] if product[15] is not None else 0,
                        'ItemNo03': product[16] if product[16] is not None else 0,
                        'ConsumeType03': product[17] if product[17] is not None else 0,
                        'Period03': product[18] if product[18] is not None else 0,
                        'ItemNo04': product[19] if product[19] is not None else 0,
                        'ConsumeType04': product[20] if product[20] is not None else 0,
                        'Period04': product[21] if product[21] is not None else 0,
                        'ActivationUnlock': product[22] if product[22] is not None else 0,
                        'InboxGift': product[23] if product[23] is not None else 0
                    }
                    self.all_items.append(item_data)
                
                self.filtered_items = self.all_items.copy()
                self.update_items_display()
                
                self.log_message(f"{len(self.all_items)} produtos carregados com TODOS os campos")
                self.update_status(f"{len(self.all_items)} produtos carregados")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar produtos:{str(e)}")
                self.log_message(f"Erro ao carregar produtos: {e}")
                self.update_status("Erro ao carregar produtos")
                
        thread = threading.Thread(target=load)
        thread.daemon = True
        thread.start()
        
    def search_items(self):
        """Buscar produtos por nome ou ID"""
        if not self.is_connected:
            messagebox.showwarning("Aviso", "Conecte-se ao banco primeiro!")
            return
            
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self.filtered_items = self.all_items.copy()
            self.update_items_display()
            return
            
        def search():
            try:
                self.update_status("Buscando produtos...")
                cursor = self.connection.cursor()
                
                # Query com TODOS os campos
                query = """
                    SELECT 
                        ProductID, ProductName, SaleType, Price, SalePrice, BonusGP, ItemNum,
                        ItemNo00, ConsumeType00, Period00, ItemNo01, ConsumeType01, Period01,
                        ItemNo02, ConsumeType02, Period02, ItemNo03, ConsumeType03, Period03,
                        ItemNo04, ConsumeType04, Period04, ActivationUnlock, InboxGift
                    FROM CBT_ProductInfo
                    WHERE ProductName LIKE ? OR CAST(ProductID as VARCHAR) LIKE ?
                    ORDER BY ProductID
                """
                
                search_pattern = f"%{search_term}%"
                cursor.execute(query, (search_pattern, search_pattern))
                products = cursor.fetchall()
                
                self.filtered_items = []
                for product in products:
                    item_data = {
                        'ProductID': product[0],
                        'ProductName': product[1] if product[1] else f"Product {product[0]}",
                        'SaleType': product[2] if product[2] is not None else 0,
                        'Price': product[3] if product[3] is not None else 0,
                        'SalePrice': product[4] if product[4] is not None else 0,
                        'BonusGP': product[5] if product[5] is not None else 0,
                        'ItemNum': product[6] if product[6] is not None else 0,
                        'ItemNo00': product[7] if product[7] is not None else 0,
                        'ConsumeType00': product[8] if product[8] is not None else 0,
                        'Period00': product[9] if product[9] is not None else 0,
                        'ItemNo01': product[10] if product[10] is not None else 0,
                        'ConsumeType01': product[11] if product[11] is not None else 0,
                        'Period01': product[12] if product[12] is not None else 0,
                        'ItemNo02': product[13] if product[13] is not None else 0,
                        'ConsumeType02': product[14] if product[14] is not None else 0,
                        'Period02': product[15] if product[15] is not None else 0,
                        'ItemNo03': product[16] if product[16] is not None else 0,
                        'ConsumeType03': product[17] if product[17] is not None else 0,
                        'Period03': product[18] if product[18] is not None else 0,
                        'ItemNo04': product[19] if product[19] is not None else 0,
                        'ConsumeType04': product[20] if product[20] is not None else 0,
                        'Period04': product[21] if product[21] is not None else 0,
                        'ActivationUnlock': product[22] if product[22] is not None else 0,
                        'InboxGift': product[23] if product[23] is not None else 0
                    }
                    self.filtered_items.append(item_data)
                
                self.update_items_display()
                self.log_message(f"Busca '{search_term}': {len(self.filtered_items)} produtos encontrados")
                self.update_status(f"Busca concluída: {len(self.filtered_items)} produtos")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro na busca:{str(e)}")
                self.log_message(f"Erro na busca: {e}")
                self.update_status("Erro na busca")
                
        thread = threading.Thread(target=search)
        thread.daemon = True
        thread.start()
        
    def on_search_change(self, event):
        """Busca automática ao digitar"""
        search_term = self.search_entry.get().strip().lower()
        
        if not search_term:
            self.filtered_items = self.all_items.copy()
        else:
            self.filtered_items = [
                item for item in self.all_items
                if search_term in item['ProductName'].lower() or search_term in str(item['ProductID'])
            ]
        
        self.update_items_display()
        
    def update_items_display(self):
        """Atualizar exibição da lista com TODOS os campos"""
        # Limpar árvore
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        # Adicionar produtos com TODOS os valores
        for item in self.filtered_items:
            values = (
                item['ProductID'],
                item['ProductName'],
                item['SaleType'],
                f"${item['Price']:,}",
                f"${item['SalePrice']:,}",
                f"{item['BonusGP']:,}",
                item['ItemNum'],
                item['ItemNo00'],
                item['ConsumeType00'],
                item['Period00'],
                item['ItemNo01'],
                item['ConsumeType01'],
                item['Period01'],
                item['ItemNo02'],
                item['ConsumeType02'],
                item['Period02'],
                item['ItemNo03'],
                item['ConsumeType03'],
                item['Period03'],
                item['ItemNo04'],
                item['ConsumeType04'],
                item['Period04'],
                item['ActivationUnlock'],
                item['InboxGift']
            )
            self.items_tree.insert('', 'end', values=values)
            
        # Atualizar contador
        self.results_label.config(text=f"{len(self.filtered_items)} produtos encontrados")
        
    def on_item_double_click(self, event):
        """Ação ao clicar duplo em um produto"""
        selection = self.items_tree.selection()
        if selection:
            item_values = self.items_tree.item(selection[0], 'values')
            product_id = item_values[0]
            product_name = item_values[1]
            
            # Preencher no formulário de envio
            self.product_id_entry.delete(0, tk.END)
            self.product_id_entry.insert(0, product_id)
            
            # Mostrar preview
            self.preview_item(None)
            
            self.log_message(f"Produto selecionado: {product_name} (ID: {product_id})")
            
    def preview_item(self, event):
        """Mostrar preview COMPLETO do produto"""
        product_id = self.product_id_entry.get().strip()
        
        if not product_id:
            self.update_preview("")
            return
            
        # Buscar produto na lista carregada
        product_data = None
        for item in self.all_items:
            if str(item['ProductID']) == product_id:
                product_data = item
                break
                
        if product_data:
            preview_text = f"""
                🎁 PREVIEW COMPLETO DO PRODUTO:
                ═══════════════════════════════════════════════════════════════
                🆔 Product ID: {product_data['ProductID']}
                📝 Nome: {product_data['ProductName']}
                🏷️ Tipo de Venda: {product_data['SaleType']}
                💰 Preço: ${product_data['Price']:,}
                💸 Preço de Venda: ${product_data['SalePrice']:,}
                🎁 Bonus GP: {product_data['BonusGP']:,}
                📦 Quantidade de Itens: {product_data['ItemNum']}

                📋 ITENS INCLUSOS:
                ┌─────────────────────────────────────────────────────────────┐
                │ ITEM 00: {product_data['ItemNo00']} | Tipo: {product_data['ConsumeType00']} | Período: {product_data['Period00']}
                │ ITEM 01: {product_data['ItemNo01']} | Tipo: {product_data['ConsumeType01']} | Período: {product_data['Period01']}
                │ ITEM 02: {product_data['ItemNo02']} | Tipo: {product_data['ConsumeType02']} | Período: {product_data['Period02']}
                │ ITEM 03: {product_data['ItemNo03']} | Tipo: {product_data['ConsumeType03']} | Período: {product_data['Period03']}
                │ ITEM 04: {product_data['ItemNo04']} | Tipo: {product_data['ConsumeType04']} | Período: {product_data['Period04']}
                └─────────────────────────────────────────────────────────────┘

                ⚙️ CONFIGURAÇÕES:
                🔓 Activation Unlock: {product_data['ActivationUnlock']}
                📨 Inbox Gift: {product_data['InboxGift']}

                ✅ Este produto será enviado via stored procedure cbp_user_send_gift
                ═══════════════════════════════════════════════════════════════
            """.strip()
        else:
            preview_text = f"""
                ❓ Product ID: {product_id}
                ═══════════════════════════════════════════════════════════════
                ⚠️ Produto não encontrado na base carregada.
                💡 O produto ainda pode existir no banco.
                🔄 Tente carregar todos os produtos primeiro.
                ═══════════════════════════════════════════════════════════════
            """.strip()
            
        self.update_preview(preview_text)
        
    def update_preview(self, text):
        """Atualizar texto do preview"""
        self.preview_text.config(state='normal')
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert('1.0', text)
        self.preview_text.config(state='disabled')
        
    def send_item(self):
        """Enviar gift usando stored procedure do Combat Arms"""
        player_name = self.player_name_entry.get().strip()
        product_id = self.product_id_entry.get().strip()
        message = self.message_text.get('1.0', tk.END).strip()
        
        if not player_name:
            messagebox.showwarning("Aviso", "Digite o nome do jogador!")
            return
            
        if not product_id:
            messagebox.showwarning("Aviso", "Digite o Product ID!")
            return
            
        if not self.is_connected:
            messagebox.showwarning("Aviso", "Conecte-se ao banco primeiro!")
            return
            
        def send():
            try:
                self.update_status(f"Enviando gift para {player_name}...")
                cursor = self.connection.cursor()
                
                # 1. Buscar oidUser do jogador
                cursor.execute("SELECT oidUser FROM CBT_User WHERE NickName = ?", (player_name,))
                user_result = cursor.fetchone()
                
                if not user_result:
                    messagebox.showerror("Erro", f"Jogador '{player_name}' não encontrado!")
                    self.log_message(f"❌ Jogador não encontrado: {player_name}")
                    self.update_status("Jogador não encontrado")
                    return
                    
                user_oid = user_result[0]
                self.log_message(f"✅ Jogador encontrado: {player_name} (oidUser: {user_oid})")
                
                # 2. Verificar se produto existe
                cursor.execute("SELECT COUNT(1) FROM CBT_ProductInfo WHERE ProductID = ?", (product_id,))
                product_exists = cursor.fetchone()[0] > 0
                
                if not product_exists:
                    messagebox.showerror("Erro", f"Product ID {product_id} não encontrado na CBT_ProductInfo!")
                    self.log_message(f"❌ Product ID não encontrado: {product_id}")
                    self.update_status("Produto não encontrado")
                    return
                
                self.log_message(f"✅ Produto validado: {product_id}")
                
                # 3. Executar stored procedure cbp_user_send_gift
                self.update_status("Executando stored procedure...")
                
                # Preparar chamada da stored procedure
                sql_call = """
                    DECLARE @return_value int, @error int;
                    EXEC @return_value = [dbo].[cbp_user_send_gift]
                        @oiduser = ?,
                        @sendoiduser = NULL,
                        @sendnickname = NULL,
                        @productid = ?,
                        @productno = ?,
                        @orderno = ?,
                        @gifttype = 1,
                        @message = ?,
                        @expire = 1,
                        @error = @error OUTPUT;
                    SELECT @return_value as return_value, @error as error_code;
                """
                
                cursor.execute(sql_call, (user_oid, product_id, product_id, product_id, message))
                result = cursor.fetchone()
                
                return_value = result[0] if result else -1
                error_code = result[1] if result else -1
                
                self.connection.commit()
                
                if return_value == 0 and error_code == 0:
                    messagebox.showinfo("Sucesso", 
                                      f"🎁 Gift enviado com sucesso!"
                                      f"👤 Jogador: {player_name}"
                                      f"🎁 Product ID: {product_id}"
                                      f"💬 Mensagem: {message}")
                    
                    log_msg = f"🎁 GIFT ENVIADO: Product {product_id} → {player_name}"
                    self.log_message(log_msg)
                    self.update_status("Gift enviado com sucesso!")
                    
                    # Limpar formulário
                    self.clear_send_form()
                else:
                    messagebox.showerror("Erro", 
                                       f"Falha ao enviar gift!"
                                       f"Return Value: {return_value}"
                                       f"Error Code: {error_code}")
                    
                    self.log_message(f"❌ Erro no envio: return={return_value}, error={error_code}")
                    self.update_status("Erro ao enviar gift")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao enviar gift:{str(e)}")
                self.log_message(f"❌ Exceção no envio: {e}")
                self.update_status("Erro no envio")
                
        thread = threading.Thread(target=send)
        thread.daemon = True
        thread.start()
        
    def quick_send_item(self):
        """Envio rápido do produto selecionado"""
        player_name = self.quick_player_entry.get().strip()
        
        if player_name == "Nome do jogador" or not player_name:
            messagebox.showwarning("Aviso", "Digite o nome do jogador!")
            return
            
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um produto na lista!")
            return
            
        item_values = self.items_tree.item(selection[0], 'values')
        product_id = item_values[0]
        
        # Preencher formulário e enviar
        self.player_name_entry.delete(0, tk.END)
        self.player_name_entry.insert(0, player_name)
        self.product_id_entry.delete(0, tk.END)
        self.product_id_entry.insert(0, product_id)
        
        self.send_item()
        
    def clear_send_form(self):
        """Limpar formulário de envio"""
        self.player_name_entry.delete(0, tk.END)
        self.product_id_entry.delete(0, tk.END)
        self.message_text.delete('1.0', tk.END)
        self.message_text.insert('1.0', 'Item enviado pela administração')
        self.update_preview("")
        
    def log_message(self, message):
        """Adicionar mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.logs_text.insert(tk.END, log_entry)
        self.logs_text.see(tk.END)
        
    def clear_logs(self):
        """Limpar logs"""
        self.logs_text.delete('1.0', tk.END)
        self.log_message("Logs limpos")
        
    def update_status(self, message):
        """Atualizar barra de status"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = CombatArmsGMTool(root)
    root.mainloop()