import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Importações para geração de PDF (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas # Para customizar o rodapé da página

class LoginApp:
    def __init__(self, master):
        self.master = master
        master.title("Login - Departamento de Transportes SATE Vicência")
        master.geometry("400x250")
        master.resizable(False, False)

        # Cores (azul e verde mais escuros)
        primary_blue = "#0A3D62" # Azul principal mais escuro
        accent_green = "#1B5E20" # Verde para detalhes mais escuro
        text_white = "#FFFFFF"   # Branco para texto
        dark_text = "#333333"    # Texto escuro para contraste

        master.configure(bg=primary_blue)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=primary_blue)
        style.configure("TLabel", font=("Arial", 10), background=primary_blue, foreground=text_white)
        style.configure("TEntry", font=("Arial", 10), fieldbackground=text_white, foreground=dark_text)
        style.configure("TButton",
                        font=("Arial", 10, "bold"),
                        background=accent_green,
                        foreground=text_white,
                        padding=6,
                        relief="flat",
                        focusthickness=3,
                        focuscolor=text_white)
        style.map("TButton",
                  background=[("active", "#2E7D32")],
                  foreground=[("active", text_white)])

        login_frame = ttk.Frame(master, padding="20 20 20 20")
        login_frame.pack(expand=True)

        ttk.Label(login_frame, text="Nome de Usuário:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.username_entry = ttk.Entry(login_frame, width=30)
        self.username_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        self.username_entry.focus_set()

        ttk.Label(login_frame, text="Senha:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.password_entry = ttk.Entry(login_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Button(login_frame, text="Login", command=self.perform_login).grid(row=2, column=0, columnspan=2, pady=15)

        self.users_df = self.carregar_dados_usuarios() # Carrega usuários para autenticação

    def carregar_dados_usuarios(self):
        """Carrega os dados dos usuários de um arquivo CSV. Cria um admin padrão se o arquivo não existir."""
        try:
            df = pd.read_csv("users.csv")
            expected_cols = ["username", "password", "role"]
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None
            return df
        except FileNotFoundError:
            # Cria um usuário administrador padrão se o arquivo não existir
            default_user = pd.DataFrame([{"username": "admin", "password": "admin123", "role": "Administrador"}])
            default_user.to_csv("users.csv", index=False)
            return default_user
        except Exception as e:
            messagebox.showerror("Erro de Carregamento", f"Erro ao carregar dados de usuários: {e}. Criando um novo arquivo com usuário padrão.")
            default_user = pd.DataFrame([{"username": "admin", "password": "admin123", "role": "Administrador"}])
            default_user.to_csv("users.csv", index=False)
            return default_user

    def perform_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        user_found = self.users_df[(self.users_df['username'] == username) & (self.users_df['password'] == password)]

        if not user_found.empty:
            logged_in_user = user_found.iloc[0]
            messagebox.showinfo("Login Bem-Sucedido", f"Bem-vindo, {logged_in_user['username']}!")
            self.master.destroy() # Fecha a janela de login
            root = tk.Tk()
            AppAbastecimento(root, logged_in_user['username'], logged_in_user['role'])
            root.mainloop()
        else:
            messagebox.showerror("Erro de Login", "Nome de usuário ou senha inválidos.")


class AppAbastecimento:
    def __init__(self, master, logged_in_username, logged_in_role):
        self.master = master
        master.title("Departamento de Transportes SATE Vicência") # Título atualizado
        master.geometry("1100x750")

        self.logged_in_username = logged_in_username
        self.current_user_role = logged_in_role

        # Carrega os dados dos abastecimentos, dos veículos e dos usuários na inicialização
        self.abastecimentos = self.carregar_dados_abastecimentos()
        self.veiculos = self.carregar_dados_veiculos()
        self.users = self.carregar_dados_usuarios() # Carrega dados dos usuários

        # Configurações de estilo para uma aparência mais moderna (ttk)
        style = ttk.Style()
        style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

        # Cores (azul e verde mais escuros)
        primary_blue = "#0A3D62" # Azul principal mais escuro
        accent_green = "#1B5E20" # Verde para detalhes mais escuro
        text_white = "#FFFFFF"   # Branco para texto
        dark_text = "#333333"    # Texto escuro para contraste

        # Configurações gerais de fundo e texto
        master.configure(bg=primary_blue) # Fundo da janela principal

        style.configure("TNotebook", background=primary_blue, borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", primary_blue), ("!selected", primary_blue)],
                  foreground=[("selected", text_white), ("!selected", text_white)])
        style.configure("TNotebook.Tab", padding=[15, 5], font=("Arial", 10, "bold"))

        style.configure("TFrame", background=primary_blue)
        style.configure("TButton",
                        font=("Arial", 10, "bold"),
                        background=accent_green,
                        foreground=text_white,
                        padding=6,
                        relief="flat",
                        focusthickness=3,
                        focuscolor=text_white)
        style.map("TButton",
                  background=[("active", "#2E7D32")], # Um verde um pouco mais claro ao passar o mouse
                  foreground=[("active", text_white)])

        style.configure("TLabel", font=("Arial", 10), background=primary_blue, foreground=text_white)
        style.configure("TEntry", font=("Arial", 10), fieldbackground=text_white, foreground=dark_text)
        style.configure("TCombobox", font=("Arial", 10), fieldbackground=text_white, foreground=dark_text)

        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background=primary_blue, foreground=text_white)
        style.configure("Treeview", font=("Arial", 9), background=text_white, foreground=dark_text, fieldbackground=text_white)
        style.map("Treeview", background=[("selected", accent_green)], foreground=[("selected", text_white)])
        
        # Estilo para Radiobuttons
        style.configure("TRadiobutton", background=primary_blue, foreground=text_white, font=("Arial", 10))
        style.map("TRadiobutton", background=[("active", primary_blue)]) # Mantém o fundo azul ao ativar

        # Estilo para Text widget (na aba de gastos)
        style.configure("TText", background=text_white, foreground=dark_text, font=("Courier New", 10))


        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Criação das abas
        self.criar_aba_lancamentos()
        self.criar_aba_lista_completa()
        self.criar_aba_gastos()
        self.criar_aba_graficos()
        self.criar_aba_cadastro_veiculos() # Nova aba de cadastro de veículos
        self.criar_aba_acesso_usuarios() # Nova aba de acesso a usuários

        # Esconde a aba "Acesso a Usuários" se o usuário não for administrador
        if self.current_user_role != "Administrador":
            # Encontra o índice da aba "Acesso a Usuários"
            tab_names = [self.notebook.tab(tab, "text") for tab in self.notebook.tabs()]
            if "Acesso a Usuários" in tab_names:
                tab_index = tab_names.index("Acesso a Usuários")
                self.notebook.hide(tab_index)


        # Adiciona um evento para atualizar as abas ao mudar
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Rodapé (mais visível)
        self.footer_label = ttk.Label(master, text="CF Tecnologias", font=("Arial", 12, "bold"), background=primary_blue, foreground=text_white)
        self.footer_label.pack(side="bottom", pady=5)

    def carregar_dados_abastecimentos(self):
        """Carrega os dados dos abastecimentos de um arquivo CSV."""
        try:
            df = pd.read_csv("abastecimentos.csv")
            # Tenta ler no formato dd/mm/aaaa, se falhar, tenta o formato AAAA-MM-DD
            try:
                df['data'] = pd.to_datetime(df['data'], format="%d/%m/%Y").dt.date
            except ValueError:
                df['data'] = pd.to_datetime(df['data'], format="%Y-%m-%d").dt.date # Fallback para o formato original
            # Garante que todas as colunas existem, adicionando-as se ausentes
            expected_cols = ["data", "secretaria", "veiculo", "placa", "modelo", "observacao", "litros", "valor", "user", "combustivel"] # Adicionado 'user' e 'combustivel'
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None # Ou um valor padrão apropriado
            return df
        except FileNotFoundError:
            return pd.DataFrame(columns=["data", "secretaria", "veiculo", "placa", "modelo", "observacao", "litros", "valor", "user", "combustivel"])
        except Exception as e:
            messagebox.showerror("Erro de Carregamento", f"Erro ao carregar dados de abastecimentos: {e}. Criando um novo arquivo.")
            return pd.DataFrame(columns=["data", "secretaria", "veiculo", "placa", "modelo", "observacao", "litros", "valor", "user", "combustivel"])

    def salvar_dados_abastecimentos(self):
        """Salva os dados dos abastecimentos em um arquivo CSV."""
        try:
            # Cria uma cópia para não modificar o DataFrame original durante o salvamento
            df_to_save = self.abastecimentos.copy()
            # Converte a coluna 'data' para string no formato DD/MM/AAAA para salvar
            df_to_save['data'] = df_to_save['data'].apply(lambda x: x.strftime("%d/%m/%Y"))
            df_to_save.to_csv("abastecimentos.csv", index=False)
        except Exception as e:
            messagebox.showerror("Erro de Salvamento", f"Erro ao salvar dados de abastecimentos: {e}")

    def carregar_dados_veiculos(self):
        """Carrega os dados dos veículos de um arquivo CSV."""
        try:
            df = pd.read_csv("veiculos.csv")
            expected_cols = ["placa", "modelo", "secretaria", "observacao", "veiculo"] # Adicionado 'veiculo' para consistência
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None
            return df
        except FileNotFoundError:
            return pd.DataFrame(columns=["placa", "modelo", "secretaria", "observacao", "veiculo"])
        except Exception as e:
            messagebox.showerror("Erro de Carregamento", f"Erro ao carregar dados de veículos: {e}. Criando um novo arquivo.")
            return pd.DataFrame(columns=["placa", "modelo", "secretaria", "observacao", "veiculo"])

    def salvar_dados_veiculos(self):
        """Salva os dados dos veículos em um arquivo CSV."""
        try:
            self.veiculos.to_csv("veiculos.csv", index=False)
        except Exception as e:
            messagebox.showerror("Erro de Salvamento", f"Erro ao salvar dados de veículos: {e}")

    def carregar_dados_usuarios(self):
        """Carrega os dados dos usuários de um arquivo CSV. Cria um admin padrão se o arquivo não existir."""
        try:
            df = pd.read_csv("users.csv")
            expected_cols = ["username", "password", "role"]
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None
            return df
        except FileNotFoundError:
            # Cria um usuário administrador padrão se o arquivo não existir
            default_user = pd.DataFrame([{"username": "admin", "password": "admin123", "role": "Administrador"}])
            default_user.to_csv("users.csv", index=False)
            return default_user
        except Exception as e:
            messagebox.showerror("Erro de Carregamento", f"Erro ao carregar dados de usuários: {e}. Criando um novo arquivo com usuário padrão.")
            default_user = pd.DataFrame([{"username": "admin", "password": "admin123", "role": "Administrador"}])
            default_user.to_csv("users.csv", index=False)
            return default_user

    def salvar_dados_usuarios(self):
        """Salva os dados dos usuários em um arquivo CSV."""
        try:
            self.users.to_csv("users.csv", index=False)
        except Exception as e:
            messagebox.showerror("Erro de Salvamento", f"Erro ao salvar dados de usuários: {e}")

    def on_tab_change(self, event):
        """Atualiza o conteúdo das abas quando a aba é alterada."""
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Lançamentos":
            # A data não é mais preenchida automaticamente ao mudar de aba
            self.atualizar_combobox_placas()
        elif selected_tab == "Lista Completa":
            self.popular_lista_completa()
        elif selected_tab == "Gastos":
            self.atualizar_gastos()
        elif selected_tab == "Gráficos":
            self.atualizar_grafico()
        elif selected_tab == "Cadastro de Veículos":
            self.popular_lista_veiculos()
        elif selected_tab == "Acesso a Usuários":
            self.popular_lista_usuarios() # Atualiza a lista de usuários ao entrar na aba

    def criar_aba_lancamentos(self):
        """Cria a interface para a aba de Lançamentos."""
        frame = ttk.Frame(self.notebook, padding="15 15 15 15")
        self.notebook.add(frame, text="Lançamentos")

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)

        row_idx = 0
        ttk.Label(frame, text="Data (DD/MM/AAAA):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_data = ttk.Entry(frame, width=30)
        self.entry_data.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.entry_data.insert(0, datetime.date.today().strftime("%d/%m/%Y")) # Data atual no formato DD/MM/AAAA

        row_idx += 1
        ttk.Label(frame, text="Placa do Veículo:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.combobox_placa = ttk.Combobox(frame, width=28, state="readonly")
        self.combobox_placa.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.combobox_placa.bind("<<ComboboxSelected>>", self.preencher_dados_veiculo)
        
        # Campos que serão preenchidos automaticamente (read-only)
        row_idx += 1
        ttk.Label(frame, text="Secretaria:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_secretaria = ttk.Entry(frame, width=30, state="readonly")
        self.entry_secretaria.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        row_idx += 1
        ttk.Label(frame, text="Veículo (Nome):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_veiculo = ttk.Entry(frame, width=30, state="readonly")
        self.entry_veiculo.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        row_idx += 1
        ttk.Label(frame, text="Modelo:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_modelo = ttk.Entry(frame, width=30, state="readonly")
        self.entry_modelo.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        row_idx += 1
        ttk.Label(frame, text="Observação (Veículo):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_observacao = ttk.Entry(frame, width=30, state="readonly")
        self.entry_observacao.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        # Novo campo: Tipo de Combustível
        row_idx += 1
        ttk.Label(frame, text="Tipo de Combustível:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.combobox_combustivel = ttk.Combobox(frame, width=28, state="readonly", values=["Gasolina", "Etanol", "Diesel", "GNV", "Outro"])
        self.combobox_combustivel.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.combobox_combustivel.set("Gasolina") # Valor padrão

        # Campos de abastecimento
        row_idx += 1
        ttk.Label(frame, text="Litros (opcional):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_litros = ttk.Entry(frame, width=30)
        self.entry_litros.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        row_idx += 1
        ttk.Label(frame, text="Valor (R$):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_valor = ttk.Entry(frame, width=30)
        self.entry_valor.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        row_idx += 1
        ttk.Button(frame, text="Salvar Abastecimento", command=self.salvar_abastecimento).grid(row=row_idx, column=0, columnspan=2, pady=20)

        # Chamada inicial para popular o combobox e preencher os campos APÓS todos os widgets serem criados
        self.atualizar_combobox_placas()


    def atualizar_combobox_placas(self):
        """Atualiza a lista de placas no combobox da aba de Lançamentos."""
        if not self.veiculos.empty:
            placas = self.veiculos['placa'].tolist()
            self.combobox_placa['values'] = placas
            if placas:
                # Tenta manter a seleção atual se ainda for válida
                current_selection = self.combobox_placa.get()
                if current_selection in placas:
                    self.combobox_placa.set(current_selection)
                else:
                    self.combobox_placa.set(placas[0]) # Seleciona a primeira placa por padrão
                self.preencher_dados_veiculo() # Preenche os dados do veículo selecionado
            else:
                self.combobox_placa.set("") # Limpa se não houver placas
                self.limpar_campos_veiculo_lancamento()
        else:
            self.combobox_placa['values'] = []
            self.combobox_placa.set("")
            self.limpar_campos_veiculo_lancamento()

    def preencher_dados_veiculo(self, event=None):
        """Preenche os campos de veículo na aba de Lançamentos com base na placa selecionada."""
        selected_placa = self.combobox_placa.get()
        self.limpar_campos_veiculo_lancamento() # Limpa antes de preencher

        if selected_placa and not self.veiculos.empty:
            veiculo_data = self.veiculos[self.veiculos['placa'] == selected_placa].iloc[0]

            self.entry_secretaria.config(state="normal")
            self.entry_secretaria.insert(0, veiculo_data.get("secretaria", ""))
            self.entry_secretaria.config(state="readonly")

            self.entry_veiculo.config(state="normal")
            self.entry_veiculo.insert(0, veiculo_data.get("veiculo", ""))
            self.entry_veiculo.config(state="readonly")

            self.entry_modelo.config(state="normal")
            self.entry_modelo.insert(0, veiculo_data.get("modelo", ""))
            self.entry_modelo.config(state="readonly")

            self.entry_observacao.config(state="normal")
            self.entry_observacao.insert(0, veiculo_data.get("observacao", ""))
            self.entry_observacao.config(state="readonly")

    def limpar_campos_veiculo_lancamento(self):
        """Limpa os campos de dados do veículo na aba de Lançamentos."""
        self.entry_secretaria.config(state="normal")
        self.entry_secretaria.delete(0, tk.END)
        self.entry_secretaria.config(state="readonly")

        self.entry_veiculo.config(state="normal")
        self.entry_veiculo.delete(0, tk.END)
        self.entry_veiculo.config(state="readonly")

        self.entry_modelo.config(state="normal")
        self.entry_modelo.delete(0, tk.END)
        self.entry_modelo.config(state="readonly")

        self.entry_observacao.config(state="normal")
        self.entry_observacao.delete(0, tk.END)
        self.entry_observacao.config(state="readonly")

    def salvar_abastecimento(self, index_para_edicao=None):
        """
        Processa e salva um novo abastecimento ou edita um existente.
        Se index_para_edicao for fornecido, edita o registro nesse índice.
        """
        try:
            data_str = self.entry_data.get()
            placa = self.combobox_placa.get().strip() # Pega a placa do combobox
            combustivel = self.combobox_combustivel.get().strip() # Pega o tipo de combustível
            litros_str = self.entry_litros.get().strip().replace(',', '.')
            valor_str = self.entry_valor.get().strip().replace(',', '.')

            # Validação dos campos obrigatórios
            if not all([data_str, placa, valor_str, combustivel]): # Combustível agora é obrigatório
                messagebox.showwarning("Campos Vazios", "Por favor, preencha os campos obrigatórios (Data, Placa, Tipo de Combustível, Valor).")
                return

            # Valida se a placa existe nos veículos cadastrados
            if self.veiculos.empty or placa not in self.veiculos['placa'].values:
                messagebox.showerror("Placa Não Cadastrada", "A placa informada não está cadastrada. Por favor, cadastre o veículo primeiro.")
                return

            try:
                # Parse a data no formato DD/MM/AAAA
                data = datetime.datetime.strptime(data_str, "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Formato de Data Inválido", "A data deve estar no formato DD/MM/AAAA.")
                return

            # Litros pode ser vazio, converte para 0.0 se vazio
            litros = float(litros_str) if litros_str else 0.0
            if litros < 0: # Não permite litros negativos
                messagebox.showerror("Valor Inválido", "Litros não pode ser um número negativo.")
                return

            try:
                valor = float(valor_str)
                if valor <= 0:
                    raise ValueError("Valor deve ser um número positivo.")
            except ValueError:
                messagebox.showerror("Valor Inválido", "Valor deve ser um número válido e positivo.")
                return

            # Pega os dados completos do veículo pela placa
            veiculo_data = self.veiculos[self.veiculos['placa'] == placa].iloc[0]

            novo_registro = {
                "data": data,
                "secretaria": veiculo_data.get("secretaria", ""),
                "veiculo": veiculo_data.get("veiculo", ""), # Nome do veículo
                "placa": placa,
                "modelo": veiculo_data.get("modelo", ""),
                "observacao": veiculo_data.get("observacao", ""),
                "litros": litros,
                "valor": valor,
                "user": self.logged_in_username, # Adiciona o usuário logado
                "combustivel": combustivel # Adiciona o tipo de combustível
            }

            if index_para_edicao is not None:
                # Edita o registro existente
                for key, value in novo_registro.items():
                    self.abastecimentos.loc[index_para_edicao, key] = value
                messagebox.showinfo("Sucesso", "Abastecimento editado com sucesso!")
            else:
                # Adiciona um novo registro
                novo_df = pd.DataFrame([novo_registro])
                self.abastecimentos = pd.concat([self.abastecimentos, novo_df], ignore_index=True)
                messagebox.showinfo("Sucesso", "Abastecimento salvo com sucesso!")
                self.limpar_campos_lancamento() # Limpa apenas se for um novo lançamento

            self.salvar_dados_abastecimentos()
            self.atualizar_abas() # Força a atualização das outras abas

            # Fecha a janela de edição se ela estiver aberta
            if hasattr(self, 'edit_window') and self.edit_window.winfo_exists():
                self.edit_window.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

    def limpar_campos_lancamento(self):
        """Limpa os campos de entrada da aba de Lançamentos."""
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, datetime.date.today().strftime("%d/%m/%Y")) # Reinicia com a data atual no formato DD/MM/AAAA
        self.combobox_placa.set("") # Limpa a seleção da placa
        self.limpar_campos_veiculo_lancamento() # Limpa os campos de veículo
        self.combobox_combustivel.set("Gasolina") # Reseta o tipo de combustível
        self.entry_litros.delete(0, tk.END)
        self.entry_valor.delete(0, tk.END)

    def criar_aba_lista_completa(self):
        """Cria a interface para a aba de Lista Completa."""
        self.frame_lista = ttk.Frame(self.notebook, padding="15 15 15 15")
        self.notebook.add(self.frame_lista, text="Lista Completa")

        # Configura o Treeview (Tabela)
        columns = ("Data", "Secretaria", "Veículo", "Placa", "Modelo", "Observação", "Tipo Combustível", "Litros", "Valor", "Usuário Responsável") # Adicionado "Usuário Responsável" e "Tipo Combustível"
        self.tree = ttk.Treeview(self.frame_lista, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.ordenar_tabela(c))
            self.tree.column(col, width=100, anchor="center") # Largura padrão

        # Definir larguras específicas para melhor visualização
        self.tree.column("Data", width=80)
        self.tree.column("Secretaria", width=100)
        self.tree.column("Veículo", width=100)
        self.tree.column("Placa", width=70)
        self.tree.column("Modelo", width=90)
        self.tree.column("Observação", width=120)
        self.tree.column("Tipo Combustível", width=100) # Largura para o novo campo
        self.tree.column("Litros", width=60)
        self.tree.column("Valor", width=70)
        self.tree.column("Usuário Responsável", width=100) # Largura para o novo campo

        # Barra de rolagem
        vsb = ttk.Scrollbar(self.frame_lista, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.frame_lista, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.frame_lista.grid_rowconfigure(0, weight=1)
        self.frame_lista.grid_columnconfigure(0, weight=1)

        # Botões de edição e exclusão
        button_frame = ttk.Frame(self.frame_lista)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Editar Lançamento", command=self.editar_lancamento).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Excluir Lançamento(s)", command=self.excluir_lancamento).pack(side="left", padx=5)

        self.popular_lista_completa()

    def ordenar_tabela(self, col):
        """Ordena a tabela da lista completa."""
        # Mapeamento de nomes de coluna da exibição para nomes do DataFrame
        col_map = {
            "Data": "data",
            "Secretaria": "secretaria",
            "Veículo": "veiculo",
            "Placa": "placa",
            "Modelo": "modelo",
            "Observação": "observacao",
            "Tipo Combustível": "combustivel", # Mapeamento para a nova coluna
            "Litros": "litros",
            "Valor": "valor",
            "Usuário Responsável": "user" # Mapeamento para a nova coluna
        }
        df_col = col_map.get(col, col.lower()) # Pega o nome da coluna no DataFrame

        if self.abastecimentos.empty or df_col not in self.abastecimentos.columns:
            return

        # Obtém a ordem atual (True para crescente, False para decrescente)
        current_order = self.tree.heading(col, "reverse")
        new_order = not current_order

        # Ordena o DataFrame
        if df_col in ['litros', 'valor']:
            self.abastecimentos = self.abastecimentos.sort_values(by=df_col, ascending=new_order)
        elif df_col == 'data':
            # Ensure 'data' column is datetime objects for proper sorting
            self.abastecimentos['data'] = pd.to_datetime(self.abastecimentos['data'])
            self.abastecimentos = self.abastecimentos.sort_values(by=df_col, ascending=new_order)
            self.abastecimentos['data'] = self.abastecimentos['data'].dt.date # Convert back to date object for storage
        else: # For strings
            self.abastecimentos = self.abastecimentos.sort_values(by=df_col, ascending=new_order)

        self.salvar_dados_abastecimentos() # Salva a ordem atual
        self.popular_lista_completa() # Repopula a tabela com a nova ordem

        # Atualiza a direção da seta de ordenação no cabeçalho
        self.tree.heading(col, reverse=new_order)


    def popular_lista_completa(self):
        """Preenche a tabela da lista completa com os dados."""
        # Limpa todos os itens existentes
        for i in self.tree.get_children():
            self.tree.delete(i)

        if not self.abastecimentos.empty:
            # Garante que a data está no formato correto para exibição
            for index, row in self.abastecimentos.iterrows():
                data_formatada = row["data"].strftime("%d/%m/%Y") # Formato DD/MM/AAAA
                self.tree.insert("", "end", iid=index, values=( # Usa o índice do DataFrame como iid
                    data_formatada,
                    row["secretaria"],
                    row["veiculo"],
                    row["placa"],
                    row["modelo"],
                    row["observacao"],
                    row["combustivel"] if pd.notna(row['combustivel']) else "", # Tipo de Combustível
                    f"{row['litros']:.2f}" if pd.notna(row['litros']) else "", # Litros pode ser vazio
                    f"R$ {row['valor']:.2f}",
                    row["user"] if pd.notna(row['user']) else "" # Usuário responsável
                ))

    def editar_lancamento(self):
        """Abre uma nova janela para editar o lançamento selecionado."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Nenhum Lançamento Selecionado", "Por favor, selecione um lançamento na lista para editar.")
            return

        df_index = int(selected_item[0])
        lancamento_data = self.abastecimentos.loc[df_index].to_dict()

        self.edit_window = tk.Toplevel(self.master)
        self.edit_window.title("Editar Lançamento")
        self.edit_window.transient(self.master) # Faz a janela de edição ficar acima da principal
        self.edit_window.grab_set() # Bloqueia interação com a janela principal

        frame = ttk.Frame(self.edit_window, padding="15 15 15 15")
        frame.pack(expand=True, fill="both")

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)

        row_idx = 0
        ttk.Label(frame, text="Data (DD/MM/AAAA):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_entry_data = ttk.Entry(frame, width=30)
        self.edit_entry_data.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_entry_data.insert(0, lancamento_data["data"].strftime("%d/%m/%Y")) # Formato DD/MM/AAAA para edição

        row_idx += 1
        ttk.Label(frame, text="Placa do Veículo:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_combobox_placa = ttk.Combobox(frame, width=28, state="readonly")
        self.edit_combobox_placa.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_combobox_placa['values'] = self.veiculos['placa'].tolist() if not self.veiculos.empty else []
        self.edit_combobox_placa.set(lancamento_data["placa"])
        self.edit_combobox_placa.bind("<<ComboboxSelected>>", lambda e: self._preencher_dados_veiculo_edicao(self.edit_combobox_placa.get()))


        row_idx += 1
        ttk.Label(frame, text="Secretaria:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_entry_secretaria = ttk.Entry(frame, width=30, state="readonly")
        self.edit_entry_secretaria.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_entry_secretaria.config(state="normal")
        self.edit_entry_secretaria.insert(0, lancamento_data.get("secretaria", ""))
        self.edit_entry_secretaria.config(state="readonly")

        row_idx += 1
        ttk.Label(frame, text="Veículo (Nome):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_entry_veiculo = ttk.Entry(frame, width=30, state="readonly")
        self.edit_entry_veiculo.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_entry_veiculo.config(state="normal")
        self.edit_entry_veiculo.insert(0, lancamento_data.get("veiculo", ""))
        self.edit_entry_veiculo.config(state="readonly")

        row_idx += 1
        ttk.Label(frame, text="Modelo:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_entry_modelo = ttk.Entry(frame, width=30, state="readonly")
        self.edit_entry_modelo.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_entry_modelo.config(state="normal")
        self.edit_entry_modelo.insert(0, lancamento_data.get("modelo", ""))
        self.edit_entry_modelo.config(state="readonly")

        row_idx += 1
        ttk.Label(frame, text="Observação (Veículo):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_entry_observacao = ttk.Entry(frame, width=30, state="readonly")
        self.edit_entry_observacao.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_entry_observacao.config(state="normal")
        self.edit_entry_observacao.insert(0, lancamento_data.get("observacao", ""))
        self.edit_entry_observacao.config(state="readonly")

        # Campo de edição para Tipo de Combustível
        row_idx += 1
        ttk.Label(frame, text="Tipo de Combustível:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_combobox_combustivel = ttk.Combobox(frame, width=28, state="readonly", values=["Gasolina", "Etanol", "Diesel", "GNV", "Outro"])
        self.edit_combobox_combustivel.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_combobox_combustivel.set(lancamento_data.get("combustivel", "Gasolina")) # Pega o valor existente ou define um padrão

        row_idx += 1
        ttk.Label(frame, text="Litros (opcional):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_entry_litros = ttk.Entry(frame, width=30)
        self.edit_entry_litros.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_entry_litros.insert(0, str(lancamento_data["litros"]) if pd.notna(lancamento_data["litros"]) else "")

        row_idx += 1
        ttk.Label(frame, text="Valor (R$):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_entry_valor = ttk.Entry(frame, width=30)
        self.edit_entry_valor.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_entry_valor.insert(0, str(lancamento_data["valor"]))

        row_idx += 1
        ttk.Label(frame, text="Usuário Responsável:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_entry_user = ttk.Entry(frame, width=30, state="readonly") # Campo de usuário somente leitura
        self.edit_entry_user.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_entry_user.config(state="normal")
        self.edit_entry_user.insert(0, lancamento_data.get("user", ""))
        self.edit_entry_user.config(state="readonly")

        row_idx += 1
        ttk.Button(frame, text="Salvar Edição", command=lambda: self._salvar_edicao(df_index)).grid(row=row_idx, column=0, columnspan=2, pady=20)

    def _preencher_dados_veiculo_edicao(self, selected_placa):
        """Preenche os campos de veículo na janela de edição com base na placa selecionada."""
        self.edit_entry_secretaria.config(state="normal")
        self.edit_entry_secretaria.delete(0, tk.END)
        self.edit_entry_secretaria.config(state="readonly")

        self.edit_entry_veiculo.config(state="normal")
        self.edit_entry_veiculo.delete(0, tk.END)
        self.edit_entry_veiculo.config(state="readonly")

        self.edit_entry_modelo.config(state="normal")
        self.edit_entry_modelo.delete(0, tk.END)
        self.edit_entry_modelo.config(state="readonly")

        self.edit_entry_observacao.config(state="normal")
        self.edit_entry_observacao.delete(0, tk.END)
        self.edit_entry_observacao.config(state="readonly")

        if selected_placa and not self.veiculos.empty:
            veiculo_data = self.veiculos[self.veiculos['placa'] == selected_placa].iloc[0]

            self.edit_entry_secretaria.config(state="normal")
            self.edit_entry_secretaria.insert(0, veiculo_data.get("secretaria", ""))
            self.edit_entry_secretaria.config(state="readonly")

            self.edit_entry_veiculo.config(state="normal")
            self.edit_entry_veiculo.insert(0, veiculo_data.get("veiculo", ""))
            self.edit_entry_veiculo.config(state="readonly")

            self.edit_entry_modelo.config(state="normal")
            self.edit_entry_modelo.insert(0, veiculo_data.get("modelo", ""))
            self.edit_entry_modelo.config(state="readonly")

            self.edit_entry_observacao.config(state="normal")
            self.edit_entry_observacao.insert(0, veiculo_data.get("observacao", ""))
            self.edit_entry_observacao.config(state="readonly")

    def _salvar_edicao(self, df_index):
        """Salva as alterações de um lançamento editado."""
        try:
            data_str = self.edit_entry_data.get()
            placa = self.edit_combobox_placa.get().strip()
            combustivel = self.edit_combobox_combustivel.get().strip() # Pega o tipo de combustível editado
            litros_str = self.edit_entry_litros.get().strip().replace(',', '.')
            valor_str = self.edit_entry_valor.get().strip().replace(',', '.')
            user_responsavel = self.edit_entry_user.get().strip() # Pega o valor do campo de usuário

            if not all([data_str, placa, valor_str, combustivel]):
                messagebox.showwarning("Campos Vazios", "Por favor, preencha os campos obrigatórios (Data, Placa, Tipo de Combustível, Valor).")
                return

            if self.veiculos.empty or placa not in self.veiculos['placa'].values:
                messagebox.showerror("Placa Não Cadastrada", "A placa informada não está cadastrada. Por favor, cadastre o veículo primeiro.")
                return

            try:
                data = datetime.datetime.strptime(data_str, "%d/%m/%Y").date() # Parse a data no formato DD/MM/AAAA
            except ValueError:
                messagebox.showerror("Formato de Data Inválido", "A data deve estar no formato DD/MM/AAAA.")
                return

            litros = float(litros_str) if litros_str else 0.0
            if litros < 0:
                messagebox.showerror("Valor Inválido", "Litros não pode ser um número negativo.")
                return

            try:
                valor = float(valor_str)
                if valor <= 0:
                    raise ValueError("Valor deve ser um número positivo.")
            except ValueError:
                messagebox.showerror("Valor Inválido", "Valor deve ser um número válido e positivo.")
                return

            veiculo_data = self.veiculos[self.veiculos['placa'] == placa].iloc[0]

            self.abastecimentos.loc[df_index, "data"] = data
            self.abastecimentos.loc[df_index, "secretaria"] = veiculo_data.get("secretaria", "")
            self.abastecimentos.loc[df_index, "veiculo"] = veiculo_data.get("veiculo", "")
            self.abastecimentos.loc[df_index, "placa"] = placa
            self.abastecimentos.loc[df_index, "modelo"] = veiculo_data.get("modelo", "")
            self.abastecimentos.loc[df_index, "observacao"] = veiculo_data.get("observacao", "")
            self.abastecimentos.loc[df_index, "litros"] = litros
            self.abastecimentos.loc[df_index, "valor"] = valor
            self.abastecimentos.loc[df_index, "user"] = user_responsavel # Salva o usuário responsável
            self.abastecimentos.loc[df_index, "combustivel"] = combustivel # Salva o tipo de combustível

            self.salvar_dados_abastecimentos()
            messagebox.showinfo("Sucesso", "Lançamento atualizado com sucesso!")
            self.edit_window.destroy()
            self.atualizar_abas()

        except Exception as e:
            messagebox.showerror("Erro na Edição", f"Ocorreu um erro ao salvar a edição: {e}")

    def excluir_lancamento(self):
        """Exclui os lançamentos selecionados na lista."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Nenhum Lançamento Selecionado", "Por favor, selecione um ou mais lançamentos para excluir.")
            return

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir {len(selected_items)} lançamento(s) selecionado(s)?"):
            indices_para_excluir = [int(self.tree.item(item)['iid']) for item in selected_items]
            
            self.abastecimentos = self.abastecimentos.drop(indices_para_excluir).reset_index(drop=True)
            self.salvar_dados_abastecimentos()
            messagebox.showinfo("Sucesso", f"{len(selected_items)} lançamento(s) excluído(s) com sucesso!")
            self.atualizar_abas()

    def criar_aba_gastos(self):
        """Cria a interface para a aba de Gastos."""
        self.frame_gastos = ttk.Frame(self.notebook, padding="15 15 15 15")
        self.notebook.add(self.frame_gastos, text="Gastos")

        # Label para o total anual
        self.total_anual_gastos_label = tk.Label(self.frame_gastos, text="", font=("Arial", 14, "bold"),
                                                background="#0A3D62", foreground="#FFFFFF") # Cor do fundo do label
        self.total_anual_gastos_label.pack(pady=10)

        # Controles de filtro
        filter_frame_gastos = ttk.Frame(self.frame_gastos)
        filter_frame_gastos.pack(pady=10, fill="x")

        ttk.Label(filter_frame_gastos, text="Secretaria:").pack(side="left", padx=5)
        self.secretaria_gastos_var = tk.StringVar()
        self.secretaria_gastos_combobox = ttk.Combobox(filter_frame_gastos, textvariable=self.secretaria_gastos_var, state="readonly")
        self.secretaria_gastos_combobox.pack(side="left", padx=5)
        self.secretaria_gastos_combobox.bind("<<ComboboxSelected>>", lambda e: self.atualizar_gastos())

        ttk.Label(filter_frame_gastos, text="Ano:").pack(side="left", padx=5)
        self.entry_gastos_ano = ttk.Entry(filter_frame_gastos, width=8)
        self.entry_gastos_ano.pack(side="left", padx=5)
        self.entry_gastos_ano.insert(0, str(datetime.date.today().year))

        ttk.Label(filter_frame_gastos, text="Mês/Semana (MM ou WW):").pack(side="left", padx=5)
        self.entry_gastos_mes_semana = ttk.Entry(filter_frame_gastos, width=8)
        self.entry_gastos_mes_semana.pack(side="left", padx=5)

        ttk.Button(filter_frame_gastos, text="Aplicar Filtros", command=self.atualizar_gastos).pack(side="left", padx=10)
        ttk.Button(filter_frame_gastos, text="Imprimir", command=self.imprimir_gastos).pack(side="left", padx=10) # Botão Imprimir

        self.criterio_gastos = tk.StringVar()
        self.criterio_gastos.set("Mes") # Default selection

        radio_frame_gastos_group = ttk.Frame(self.frame_gastos)
        radio_frame_gastos_group.pack(pady=5, fill="x")
        ttk.Label(radio_frame_gastos_group, text="Agrupar por:").pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame_gastos_group, text="Mês", variable=self.criterio_gastos, value="Mes", command=self.atualizar_gastos).pack(side="left", padx=10)
        ttk.Radiobutton(radio_frame_gastos_group, text="Semana", variable=self.criterio_gastos, value="Semana", command=self.atualizar_gastos).pack(side="left", padx=10)
        ttk.Radiobutton(radio_frame_gastos_group, text="Secretaria", variable=self.criterio_gastos, value="Secretaria", command=self.atualizar_gastos).pack(side="left", padx=10)


        self.text_gastos = tk.Text(self.frame_gastos, height=20, width=80, wrap="word", font=("Courier New", 10))
        self.text_gastos.pack(pady=10, expand=True, fill="both")

        self.popular_secretarias_combobox()
        self.atualizar_gastos()

    def popular_secretarias_combobox(self):
        secretarias = sorted(self.veiculos['secretaria'].dropna().unique().tolist())
        self.secretaria_gastos_combobox['values'] = ["Todas as Secretarias"] + secretarias
        self.secretaria_gastos_combobox.set("Todas as Secretarias")

        if hasattr(self, 'secretaria_graficos_combobox'): # For the graphics tab
            self.secretaria_graficos_combobox['values'] = ["Todas as Secretarias"] + secretarias
            self.secretaria_graficos_combobox.set("Todas as Secretarias")


    def atualizar_gastos(self):
        """Calcula e exibe os gastos de acordo com o critério selecionado e filtros."""
        self.text_gastos.delete(1.0, tk.END)

        df_filtered = self.abastecimentos.copy()

        # Apply filters
        selected_secretaria = self.secretaria_gastos_var.get()
        if selected_secretaria != "Todas as Secretarias":
            df_filtered = df_filtered[df_filtered['secretaria'] == selected_secretaria]

        ano_str = self.entry_gastos_ano.get().strip()
        mes_semana_str = self.entry_gastos_mes_semana.get().strip()

        if ano_str:
            try:
                ano = int(ano_str)
                df_filtered = df_filtered[df_filtered['data'].apply(lambda x: x.year) == ano]
            except ValueError:
                messagebox.showwarning("Filtro Inválido", "Ano deve ser um número válido.")
                return

        if mes_semana_str:
            try:
                val = int(mes_semana_str)
                if self.criterio_gastos.get() == "Mes":
                    df_filtered = df_filtered[df_filtered['data'].apply(lambda x: x.month) == val]
                elif self.criterio_gastos.get() == "Semana":
                    # Week number is 1-52, so need to calculate it from date
                    df_filtered = df_filtered[df_filtered['data'].apply(lambda x: x.isocalendar()[1]) == val]
            except ValueError:
                messagebox.showwarning("Filtro Inválido", "Mês/Semana deve ser um número válido.")
                return

        if df_filtered.empty:
            self.text_gastos.insert(tk.END, "Nenhum dado de abastecimento para analisar com os filtros selecionados.")
            self.total_anual_gastos_label.config(text="Gasto Total do Ano: R$ 0,00")
            return

        # Calculate total annual expenditure for the filtered data
        current_year = datetime.datetime.now().year
        gastos_ano_atual = df_filtered[df_filtered['data'].apply(lambda x: x.year) == current_year]['valor'].sum()
        self.total_anual_gastos_label.config(text=f"Gasto Total do Ano ({current_year}): R$ {gastos_ano_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))


        try:
            df_filtered["data"] = pd.to_datetime(df_filtered["data"]) # Ensure 'data' is datetime for period operations
            
            criterio = self.criterio_gastos.get()

            gastos_agrupados = pd.Series(dtype=float) # Initialize as Series of float

            if criterio == "Mes":
                df_filtered["chave_agrupamento"] = df_filtered["data"].dt.to_period("M").astype(str)
                gastos_agrupados = df_filtered.groupby("chave_agrupamento")["valor"].sum().sort_index()
                self.text_gastos.insert(tk.END, "--- GASTOS POR MÊS ---\n\n")
            elif criterio == "Semana":
                df_filtered["chave_agrupamento"] = df_filtered["data"].dt.strftime("%Y-W%W") # Formato AAAA-WW
                gastos_agrupados = df_filtered.groupby("chave_agrupamento")["valor"].sum().sort_index()
                self.text_gastos.insert(tk.END, "--- GASTOS POR SEMANA ---\n\n")
            elif criterio == "Secretaria":
                gastos_agrupados = df_filtered.groupby("secretaria")["valor"].sum().sort_values(ascending=False)
                self.text_gastos.insert(tk.END, "--- GASTOS POR SECRETARIA ---\n\n")

            if not gastos_agrupados.empty:
                for index, valor in gastos_agrupados.items():
                    self.text_gastos.insert(tk.END, f"{index}: R$ {valor:,.2f}\n".replace(",", "X").replace(".", ",").replace("X", "."))
            else:
                self.text_gastos.insert(tk.END, "Nenhum dado encontrado para o critério selecionado.")

        except Exception as e:
            self.text_gastos.insert(tk.END, f"Erro ao calcular gastos: {e}")

    def imprimir_gastos(self):
        """Gera um PDF dos gastos exibidos na aba 'Gastos' com rodapé."""
        if self.text_gastos.get(1.0, tk.END).strip() == "Nenhum dado de abastecimento para analisar com os filtros selecionados." or self.abastecimentos.empty:
            messagebox.showwarning("Nenhum Dado", "Não há dados para imprimir.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF files", "*.pdf")],
                                                 title="Salvar Gastos Como PDF")
        if not file_path:
            return

        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Título
        story.append(Paragraph("Relatório de Gastos de Abastecimento", styles['h1']))
        story.append(Spacer(1, 0.5*cm))

        # Total Anual
        total_anual_text = self.total_anual_gastos_label.cget("text")
        story.append(Paragraph(total_anual_text, styles['h2']))
        story.append(Spacer(1, 0.5*cm))

        # Filtros aplicados
        secretaria = self.secretaria_gastos_var.get()
        ano = self.entry_gastos_ano.get().strip()
        mes_semana = self.entry_gastos_mes_semana.get().strip()
        agrupamento = self.criterio_gastos.get()

        filter_info = f"Filtros: Secretaria: {secretaria}, Ano: {ano if ano else 'Todos'}, Mês/Semana: {mes_semana if mes_semana else 'Todos'}"
        story.append(Paragraph(filter_info, styles['Normal']))
        story.append(Paragraph(f"Agrupado por: {agrupamento}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # Conteúdo do widget de texto
        gastos_content = self.text_gastos.get(1.0, tk.END).strip()
        for line in gastos_content.split('\n'):
            story.append(Paragraph(line, styles['Normal'])) # Usando 'Normal' para texto geral
        story.append(Spacer(1, 1*cm))

        # Rodapé personalizado
        def footer(canvas_obj, doc_obj):
            canvas_obj.saveState()
            canvas_obj.setFont('Helvetica', 9)
            canvas_obj.drawString(cm, 1.5 * cm, "Departamento de Transporte SATE Vicência")
            canvas_obj.drawString(cm, 1.0 * cm, "CF Tecnologias")
            canvas_obj.restoreState()

        try:
            doc.build(story, onFirstPage=footer, onLaterPages=footer)
            messagebox.showinfo("Sucesso", f"Relatório de gastos salvo como PDF em: {file_path}")
        except Exception as e:
            messagebox.showerror("Erro de Impressão", f"Ocorreu um erro ao gerar o PDF: {e}")


    def criar_aba_graficos(self):
        """Cria a interface para a aba de Gráficos."""
        self.frame_graficos = ttk.Frame(self.notebook, padding="15 15 15 15")
        self.notebook.add(self.frame_graficos, text="Gráficos")

        # Label para o total anual
        self.total_anual_graficos_label = tk.Label(self.frame_graficos, text="", font=("Arial", 14, "bold"),
                                                  background="#0A3D62", foreground="#FFFFFF") # Cor do fundo do label
        self.total_anual_graficos_label.pack(pady=10)

        # Controles de filtro
        filter_frame_graficos = ttk.Frame(self.frame_graficos)
        filter_frame_graficos.pack(pady=10, fill="x")

        ttk.Label(filter_frame_graficos, text="Secretaria:").pack(side="left", padx=5)
        self.secretaria_graficos_var = tk.StringVar()
        self.secretaria_graficos_combobox = ttk.Combobox(filter_frame_graficos, textvariable=self.secretaria_graficos_var, state="readonly")
        self.secretaria_graficos_combobox.pack(side="left", padx=5)
        self.secretaria_graficos_combobox.bind("<<ComboboxSelected>>", lambda e: self.atualizar_grafico())

        ttk.Label(filter_frame_graficos, text="Ano:").pack(side="left", padx=5)
        self.entry_graficos_ano = ttk.Entry(filter_frame_graficos, width=8)
        self.entry_graficos_ano.pack(side="left", padx=5)
        self.entry_graficos_ano.insert(0, str(datetime.date.today().year))

        ttk.Label(filter_frame_graficos, text="Mês/Semana (MM ou WW):").pack(side="left", padx=5)
        self.entry_graficos_mes_semana = ttk.Entry(filter_frame_graficos, width=8)
        self.entry_graficos_mes_semana.pack(side="left", padx=5)

        ttk.Button(filter_frame_graficos, text="Aplicar Filtros", command=self.atualizar_grafico).pack(side="left", padx=10)
        ttk.Button(filter_frame_graficos, text="Salvar Gráfico", command=self.salvar_grafico).pack(side="left", padx=10)


        self.tipo_grafico = tk.StringVar()
        self.tipo_grafico.set("Gastos por Mes")

        radio_frame_graficos_group = ttk.Frame(self.frame_graficos)
        radio_frame_graficos_group.pack(pady=5, fill="x")
        ttk.Label(radio_frame_graficos_group, text="Tipo de Gráfico:").pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame_graficos_group, text="Gastos por Mês", variable=self.tipo_grafico, value="Gastos por Mes", command=self.atualizar_grafico).pack(side="left", padx=10)
        ttk.Radiobutton(radio_frame_graficos_group, text="Gastos por Semana", variable=self.tipo_grafico, value="Gastos por Semana", command=self.atualizar_grafico).pack(side="left", padx=10)
        ttk.Radiobutton(radio_frame_graficos_group, text="Gastos por Secretaria", variable=self.tipo_grafico, value="Gastos por Secretaria", command=self.atualizar_grafico).pack(side="left", padx=10)
        ttk.Radiobutton(radio_frame_graficos_group, text="Ranking Consumo por Veículo/Secretaria", variable=self.tipo_grafico, value="Ranking Consumo", command=self.atualizar_grafico).pack(side="left", padx=10)


        self.canvas_frame = ttk.Frame(self.frame_graficos)
        self.canvas_frame.pack(expand=True, fill="both")

        self.popular_secretarias_combobox() # Ensure this is called to populate comboboxes
        self.atualizar_grafico()
        self.current_fig = None # To store the current matplotlib figure for saving

    def atualizar_grafico(self):
        """Gera e exibe o gráfico de acordo com o tipo selecionado e filtros."""
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        df_filtered = self.abastecimentos.copy()

        # Apply filters
        selected_secretaria = self.secretaria_graficos_var.get()
        if selected_secretaria != "Todas as Secretarias":
            df_filtered = df_filtered[df_filtered['secretaria'] == selected_secretaria]

        ano_str = self.entry_graficos_ano.get().strip()
        mes_semana_str = self.entry_graficos_mes_semana.get().strip()

        if ano_str:
            try:
                ano = int(ano_str)
                df_filtered = df_filtered[df_filtered['data'].apply(lambda x: x.year) == ano]
            except ValueError:
                messagebox.showwarning("Filtro Inválido", "Ano deve ser um número válido.")
                self.total_anual_graficos_label.config(text="Gasto Total do Ano: R$ 0,00")
                return

        if mes_semana_str:
            try:
                val = int(mes_semana_str)
                if self.tipo_grafico.get() in ["Gastos por Mes", "SecretariaMes"]:
                    df_filtered = df_filtered[df_filtered['data'].apply(lambda x: x.month) == val]
                elif self.tipo_grafico.get() in ["Gastos por Semana", "SecretariaSemana"]:
                    df_filtered = df_filtered[df_filtered['data'].apply(lambda x: x.isocalendar()[1]) == val]
            except ValueError:
                messagebox.showwarning("Filtro Inválido", "Mês/Semana deve ser um número válido.")
                self.total_anual_graficos_label.config(text="Gasto Total do Ano: R$ 0,00")
                return

        if df_filtered.empty:
            ttk.Label(self.canvas_frame, text="Nenhum dado para gerar gráficos com os filtros selecionados.", font=("Arial", 12)).pack(pady=20)
            self.total_anual_graficos_label.config(text="Gasto Total do Ano: R$ 0,00")
            self.current_fig = None
            return

        # Calculate total annual expenditure for the filtered data
        current_year = datetime.datetime.now().year
        gastos_ano_atual = df_filtered[df_filtered['data'].apply(lambda x: x.year) == current_year]['valor'].sum()
        self.total_anual_graficos_label.config(text=f"Gasto Total do Ano ({current_year}): R$ {gastos_ano_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))


        df_filtered["data"] = pd.to_datetime(df_filtered["data"]) # Ensure 'data' is datetime for period operations

        fig, ax = plt.subplots(figsize=(8, 6))
        plt.style.use('ggplot')

        tipo = self.tipo_grafico.get()

        try:
            if tipo == "Gastos por Mes":
                df_filtered["mes_ano"] = df_filtered["data"].dt.to_period("M").astype(str)
                gastos = df_filtered.groupby("mes_ano")["valor"].sum().sort_index()
                gastos.plot(kind="bar", ax=ax, title="Gastos por Mês", color='skyblue')
                ax.set_ylabel("Valor (R$)")
                ax.set_xlabel("Mês/Ano")
                ax.tick_params(axis='x', rotation=45)
            elif tipo == "Gastos por Semana":
                df_filtered["semana_ano"] = df_filtered["data"].dt.strftime("%Y-W%W")
                gastos = df_filtered.groupby("semana_ano")["valor"].sum().sort_index()
                gastos.plot(kind="bar", ax=ax, title="Gastos por Semana", color='lightcoral')
                ax.set_ylabel("Valor (R$)")
                ax.set_xlabel("Semana do Ano")
                ax.tick_params(axis='x', rotation=45)
            elif tipo == "Gastos por Secretaria":
                gastos = df_filtered.groupby("secretaria")["valor"].sum().sort_values(ascending=False)
                gastos.plot(kind="bar", ax=ax, title="Gastos por Secretaria", color='lightgreen')
                ax.set_ylabel("Valor (R$)")
                ax.set_xlabel("Secretaria")
                ax.tick_params(axis='x', rotation=45)
            elif tipo == "Ranking Consumo":
                # Ranking por valor (R$)
                consumo_ranking = df_filtered.groupby(["secretaria", "veiculo", "placa"])["valor"].sum().reset_index()
                consumo_ranking = consumo_ranking.sort_values(by=["secretaria", "valor"], ascending=[True, False])

                if consumo_ranking.empty:
                    ax.text(0.5, 0.5, "Nenhum dado para ranking de consumo.", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=12)
                    ax.axis('off')
                else:
                    ax.axis('off')
                    y_offset = 0.95
                    ax.text(0.02, y_offset, "Ranking de Consumo por Valor (Top 10 Geral):", transform=ax.transAxes, fontsize=12, weight='bold')
                    y_offset -= 0.05

                    for idx, row in consumo_ranking.head(10).iterrows():
                        ax.text(0.05, y_offset, f"{row['secretaria']} - {row['veiculo']} ({row['placa']}): R$ {row['valor']:.2f}", transform=ax.transAxes, fontsize=10)
                        y_offset -= 0.04
                    if len(consumo_ranking) > 10:
                        ax.text(0.05, y_offset, "...", transform=ax.transAxes, fontsize=10)

            plt.tight_layout() # Adjust layout for other plots

            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            toolbar = NavigationToolbar2Tk(canvas, self.canvas_frame)
            toolbar.update()
            canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.current_fig = fig # Store the figure for saving

        except Exception as e:
            messagebox.showerror("Erro de Gráfico", f"Ocorreu um erro ao gerar o gráfico: {e}")
            plt.close(fig)
            self.current_fig = None

    def salvar_grafico(self):
        """Salva o gráfico atual como um arquivo PDF ou PNG com rodapé."""
        if not self.current_fig:
            messagebox.showwarning("Nenhum Gráfico", "Não há gráfico para salvar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF files", "*.pdf"), ("PNG files", "*.png")],
                                                 title="Salvar Gráfico Como")
        if not file_path:
            return

        try:
            # Add footer before saving
            fig = self.current_fig
            
            # Adjust bottom margin to make space for the footer
            # fig.subplots_adjust(bottom=0.15) # This might interfere with existing tight_layout

            # Add footer text directly to the figure
            # Coordinates are relative to the figure (0 to 1)
            fig.text(0.02, 0.08, "Departamento de Transporte SATE Vicência", ha='left', va='center', fontsize=8, color='gray', transform=fig.transFigure)
            fig.text(0.02, 0.05, "CF Tecnologias", ha='left', va='center', fontsize=8, color='gray', transform=fig.transFigure)
            
            self.current_fig.savefig(file_path)
            messagebox.showinfo("Sucesso", f"Gráfico salvo em: {file_path}")

            # Close the figure after saving to free memory
            plt.close(fig)
            self.current_fig = None # Clear reference after saving

            # Re-render the graph if the tab is still active, to remove the footer from live view
            self.atualizar_grafico()

        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o gráfico: {e}")

    def criar_aba_cadastro_veiculos(self):
        """Cria a interface para a nova aba de Cadastro de Veículos."""
        self.frame_cadastro_veiculos = ttk.Frame(self.notebook, padding="15 15 15 15")
        self.notebook.add(self.frame_cadastro_veiculos, text="Cadastro de Veículos")

        self.frame_cadastro_veiculos.columnconfigure(0, weight=1)
        self.frame_cadastro_veiculos.columnconfigure(1, weight=3)

        # Campos de entrada para cadastro de veículos
        row_idx = 0
        ttk.Label(self.frame_cadastro_veiculos, text="Placa:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_cadastro_placa = ttk.Entry(self.frame_cadastro_veiculos, width=30)
        self.entry_cadastro_placa.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        row_idx += 1
        ttk.Label(self.frame_cadastro_veiculos, text="Veículo (Nome):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_cadastro_veiculo_nome = ttk.Entry(self.frame_cadastro_veiculos, width=30)
        self.entry_cadastro_veiculo_nome.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        row_idx += 1
        ttk.Label(self.frame_cadastro_veiculos, text="Modelo:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_cadastro_modelo = ttk.Entry(self.frame_cadastro_veiculos, width=30)
        self.entry_cadastro_modelo.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        row_idx += 1
        ttk.Label(self.frame_cadastro_veiculos, text="Secretaria:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_cadastro_secretaria = ttk.Entry(self.frame_cadastro_veiculos, width=30)
        self.entry_cadastro_secretaria.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        row_idx += 1
        ttk.Label(self.frame_cadastro_veiculos, text="Observação:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_cadastro_observacao = ttk.Entry(self.frame_cadastro_veiculos, width=30)
        self.entry_cadastro_observacao.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        # Botões de ação para veículos
        button_frame_veiculos = ttk.Frame(self.frame_cadastro_veiculos)
        button_frame_veiculos.grid(row=row_idx + 1, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame_veiculos, text="Salvar Veículo", command=self.salvar_veiculo).pack(side="left", padx=5)
        ttk.Button(button_frame_veiculos, text="Editar Veículo", command=self.editar_veiculo).pack(side="left", padx=5)
        ttk.Button(button_frame_veiculos, text="Excluir Veículo(s)", command=self.excluir_veiculo).pack(side="left", padx=5)

        # Campo de pesquisa
        row_idx += 2
        ttk.Label(self.frame_cadastro_veiculos, text="Pesquisar por Placa:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_pesquisa_placa = ttk.Entry(self.frame_cadastro_veiculos, width=30)
        self.entry_pesquisa_placa.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.entry_pesquisa_placa.bind("<KeyRelease>", self.pesquisar_veiculos) # Pesquisa ao digitar

        # Treeview para listar veículos
        row_idx += 1
        columns_veiculos = ("Placa", "Veículo", "Modelo", "Secretaria", "Observação")
        self.tree_veiculos = ttk.Treeview(self.frame_cadastro_veiculos, columns=columns_veiculos, show="headings")
        for col in columns_veiculos:
            self.tree_veiculos.heading(col, text=col)
            self.tree_veiculos.column(col, width=100, anchor="center")

        self.tree_veiculos.column("Placa", width=80)
        self.tree_veiculos.column("Veículo", width=120)
        self.tree_veiculos.column("Modelo", width=100)
        self.tree_veiculos.column("Secretaria", width=120)
        self.tree_veiculos.column("Observação", width=150)

        vsb_veiculos = ttk.Scrollbar(self.frame_cadastro_veiculos, orient="vertical", command=self.tree_veiculos.yview)
        hsb_veiculos = ttk.Scrollbar(self.frame_cadastro_veiculos, orient="horizontal", command=self.tree_veiculos.xview)
        self.tree_veiculos.configure(yscrollcommand=vsb_veiculos.set, xscrollcommand=hsb_veiculos.set)

        self.tree_veiculos.grid(row=row_idx, column=0, columnspan=2, sticky="nsew", pady=10)
        vsb_veiculos.grid(row=row_idx, column=2, sticky="ns")
        hsb_veiculos.grid(row=row_idx + 1, column=0, columnspan=2, sticky="ew")

        self.frame_cadastro_veiculos.grid_rowconfigure(row_idx, weight=1)
        self.frame_cadastro_veiculos.grid_columnconfigure(0, weight=1)
        self.frame_cadastro_veiculos.grid_columnconfigure(1, weight=1)

        self.popular_lista_veiculos() # Carrega a lista de veículos ao abrir a aba

    def salvar_veiculo(self):
        """Salva um novo veículo ou atualiza um existente."""
        placa = self.entry_cadastro_placa.get().strip().upper() # Placa em maiúsculas
        veiculo_nome = self.entry_cadastro_veiculo_nome.get().strip()
        modelo = self.entry_cadastro_modelo.get().strip()
        secretaria = self.entry_cadastro_secretaria.get().strip()
        observacao = self.entry_cadastro_observacao.get().strip()

        if not all([placa, veiculo_nome, modelo, secretaria]):
            messagebox.showwarning("Campos Obrigatórios", "Placa, Veículo, Modelo e Secretaria são obrigatórios.")
            return

        # Verifica se a placa já existe
        if placa in self.veiculos['placa'].values:
            messagebox.showwarning("Placa Existente", f"A placa '{placa}' já está cadastrada. Use 'Editar Veículo' para modificá-lo.")
            return

        novo_veiculo = pd.DataFrame([{
            "placa": placa,
            "veiculo": veiculo_nome,
            "modelo": modelo,
            "secretaria": secretaria,
            "observacao": observacao
        }])
        self.veiculos = pd.concat([self.veiculos, novo_veiculo], ignore_index=True)
        self.salvar_dados_veiculos()
        messagebox.showinfo("Sucesso", "Veículo cadastrado com sucesso!")
        self.limpar_campos_cadastro_veiculos()
        self.popular_lista_veiculos()
        self.atualizar_combobox_placas() # Atualiza o combobox de lançamentos

    def editar_veiculo(self):
        """Abre uma nova janela para editar o veículo selecionado."""
        selected_item = self.tree_veiculos.selection()
        if not selected_item:
            messagebox.showwarning("Nenhum Veículo Selecionado", "Por favor, selecione um veículo na lista para editar.")
            return

        # Pega a placa do item selecionado
        placa_para_editar = self.tree_veiculos.item(selected_item[0])['values'][0]
        veiculo_data = self.veiculos[self.veiculos['placa'] == placa_para_editar].iloc[0].to_dict()

        self.edit_veiculo_window = tk.Toplevel(self.master)
        self.edit_veiculo_window.title(f"Editar Veículo: {placa_para_editar}")
        self.edit_veiculo_window.transient(self.master)
        self.edit_veiculo_window.grab_set()

        frame = ttk.Frame(self.edit_veiculo_window, padding="15 15 15 15")
        frame.pack(expand=True, fill="both")

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)

        row_idx = 0
        ttk.Label(frame, text="Placa:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_veiculo_placa = ttk.Entry(frame, width=30, state="readonly") # Placa não editável
        self.edit_veiculo_placa.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_veiculo_placa.insert(0, veiculo_data["placa"])

        row_idx += 1
        ttk.Label(frame, text="Veículo (Nome):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_veiculo_nome = ttk.Entry(frame, width=30)
        self.edit_veiculo_nome.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_veiculo_nome.insert(0, veiculo_data["veiculo"])

        row_idx += 1
        ttk.Label(frame, text="Modelo:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_veiculo_modelo = ttk.Entry(frame, width=30)
        self.edit_veiculo_modelo.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_veiculo_modelo.insert(0, veiculo_data["modelo"])

        row_idx += 1
        ttk.Label(frame, text="Secretaria:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_veiculo_secretaria = ttk.Entry(frame, width=30)
        self.edit_veiculo_secretaria.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_veiculo_secretaria.insert(0, veiculo_data["secretaria"])

        row_idx += 1
        ttk.Label(frame, text="Observação:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_veiculo_observacao = ttk.Entry(frame, width=30)
        self.edit_veiculo_observacao.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_veiculo_observacao.insert(0, veiculo_data["observacao"])

        row_idx += 1
        ttk.Button(frame, text="Salvar Edição", command=lambda: self._salvar_edicao_veiculo(placa_para_editar)).grid(row=row_idx, column=0, columnspan=2, pady=20)

    def _salvar_edicao_veiculo(self, placa_original):
        """Salva as alterações de um veículo editado."""
        try:
            veiculo_nome = self.edit_veiculo_nome.get().strip()
            modelo = self.edit_veiculo_modelo.get().strip()
            secretaria = self.edit_veiculo_secretaria.get().strip()
            observacao = self.edit_veiculo_observacao.get().strip()

            if not all([veiculo_nome, modelo, secretaria]):
                messagebox.showwarning("Campos Obrigatórios", "Veículo, Modelo e Secretaria são obrigatórios.")
                return

            # Encontra o índice do veículo no DataFrame
            idx = self.veiculos[self.veiculos['placa'] == placa_original].index[0]

            self.veiculos.loc[idx, "veiculo"] = veiculo_nome
            self.veiculos.loc[idx, "modelo"] = modelo
            self.veiculos.loc[idx, "secretaria"] = secretaria
            self.veiculos.loc[idx, "observacao"] = observacao

            self.salvar_dados_veiculos()
            messagebox.showinfo("Sucesso", "Veículo atualizado com sucesso!")
            self.edit_veiculo_window.destroy()
            self.popular_lista_veiculos()
            self.atualizar_combobox_placas() # Atualiza combobox de lançamentos
            self.atualizar_abas() # Atualiza todas as abas que dependem dos dados do veículo

        except Exception as e:
            messagebox.showerror("Erro na Edição", f"Ocorreu um erro ao salvar a edição do veículo: {e}")

    def excluir_veiculo(self):
        """Exclui os veículos selecionados na lista."""
        selected_items = self.tree_veiculos.selection()
        if not selected_items:
            messagebox.showwarning("Nenhum Veículo Selecionado", "Por favor, selecione um ou mais veículos para excluir.")
            return

        placas_para_excluir = [self.tree_veiculos.item(item)['values'][0] for item in selected_items]

        # Verifica se algum veículo a ser excluído tem lançamentos associados
        abastecimentos_com_veiculo = self.abastecimentos[self.abastecimentos['placa'].isin(placas_para_excluir)]
        if not abastecimentos_com_veiculo.empty:
            messagebox.showwarning("Veículo com Lançamentos", "Não é possível excluir veículos que possuem lançamentos de abastecimento registrados. Exclua os lançamentos primeiro.")
            return

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir {len(selected_items)} veículo(s) selecionado(s)?"):
            self.veiculos = self.veiculos[~self.veiculos['placa'].isin(placas_para_excluir)].reset_index(drop=True)
            self.salvar_dados_veiculos()
            messagebox.showinfo("Sucesso", f"{len(selected_items)} veículo(s) excluído(s) com sucesso!")
            self.popular_lista_veiculos()
            self.atualizar_combobox_placas() # Atualiza o combobox de lançamentos

    def limpar_campos_cadastro_veiculos(self):
        """Limpa os campos de entrada da aba de Cadastro de Veículos."""
        self.entry_cadastro_placa.delete(0, tk.END)
        self.entry_cadastro_veiculo_nome.delete(0, tk.END)
        self.entry_cadastro_modelo.delete(0, tk.END)
        self.entry_cadastro_secretaria.delete(0, tk.END)
        self.entry_cadastro_observacao.delete(0, tk.END)

    def popular_lista_veiculos(self, df_filtrado=None):
        """Preenche a tabela de veículos com os dados, opcionalmente filtrados."""
        for i in self.tree_veiculos.get_children():
            self.tree_veiculos.delete(i)

        df_to_display = df_filtrado if df_filtrado is not None else self.veiculos

        if not df_to_display.empty:
            for index, row in df_to_display.iterrows():
                self.tree_veiculos.insert("", "end", values=(
                    row["placa"],
                    row["veiculo"],
                    row["modelo"],
                    row["secretaria"],
                    row["observacao"]
                ))

    def pesquisar_veiculos(self, event=None):
        """Filtra a lista de veículos com base na placa digitada."""
        termo_pesquisa = self.entry_pesquisa_placa.get().strip().upper()
        if termo_pesquisa:
            df_filtrado = self.veiculos[self.veiculos['placa'].str.contains(termo_pesquisa, na=False, case=False)]
            self.popular_lista_veiculos(df_filtrado)
        else:
            self.popular_lista_veiculos() # Mostra todos se a pesquisa estiver vazia

    def atualizar_abas(self):
        """Força a atualização de todas as abas que precisam ser recarregadas."""
        self.popular_lista_completa()
        self.atualizar_gastos()
        self.atualizar_grafico()
        self.popular_lista_veiculos()
        self.popular_lista_usuarios() # Atualiza a lista de usuários
        self.atualizar_combobox_placas()


    def criar_aba_acesso_usuarios(self):
        """Cria a interface para a nova aba de Acesso a Usuários."""
        self.frame_acesso_usuarios = ttk.Frame(self.notebook, padding="15 15 15 15")
        self.notebook.add(self.frame_acesso_usuarios, text="Acesso a Usuários")

        # Título extra grande
        ttk.Label(self.frame_acesso_usuarios, text="Departamento de Transporte SATE Vicência",
                  font=("Arial", 24, "bold"), background="#0A3D62", foreground="#FFFFFF").pack(pady=20)

        # Frame para os controles de usuário
        user_controls_frame = ttk.Frame(self.frame_acesso_usuarios)
        user_controls_frame.pack(pady=10, fill="x")
        user_controls_frame.columnconfigure(0, weight=1)
        user_controls_frame.columnconfigure(1, weight=3)

        row_idx = 0
        ttk.Label(user_controls_frame, text="Nome de Usuário:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_user_username = ttk.Entry(user_controls_frame, width=30)
        self.entry_user_username.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        row_idx += 1
        ttk.Label(user_controls_frame, text="Senha:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_user_password = ttk.Entry(user_controls_frame, width=30, show="*") # Senha oculta
        self.entry_user_password.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)

        row_idx += 1
        ttk.Label(user_controls_frame, text="Nível de Acesso:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.combobox_user_role = ttk.Combobox(user_controls_frame, width=28, state="readonly", values=["Administrador", "Usuário"])
        self.combobox_user_role.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.combobox_user_role.set("Usuário") # Padrão

        # Botões de ação para usuários
        button_frame_users = ttk.Frame(self.frame_acesso_usuarios)
        button_frame_users.pack(pady=10, fill="x")
        
        self.btn_add_user = ttk.Button(button_frame_users, text="Adicionar Usuário", command=self.salvar_usuario)
        self.btn_add_user.pack(side="left", padx=5)
        self.btn_edit_user = ttk.Button(button_frame_users, text="Editar Usuário", command=self.editar_usuario_dialog)
        self.btn_edit_user.pack(side="left", padx=5)
        self.btn_delete_user = ttk.Button(button_frame_users, text="Excluir Usuário(s)", command=self.excluir_usuario)
        self.btn_delete_user.pack(side="left", padx=5)

        # Treeview para listar usuários
        columns_users = ("Nome de Usuário", "Nível de Acesso")
        self.tree_users = ttk.Treeview(self.frame_acesso_usuarios, columns=columns_users, show="headings")
        for col in columns_users:
            self.tree_users.heading(col, text=col)
            self.tree_users.column(col, width=150, anchor="center")

        self.tree_users.column("Nome de Usuário", width=200)
        self.tree_users.column("Nível de Acesso", width=150)

        vsb_users = ttk.Scrollbar(self.frame_acesso_usuarios, orient="vertical", command=self.tree_users.yview)
        hsb_users = ttk.Scrollbar(self.frame_acesso_usuarios, orient="horizontal", command=self.tree_users.xview)
        self.tree_users.configure(yscrollcommand=vsb_users.set, xscrollcommand=hsb_users.set)

        self.tree_users.pack(expand=True, fill="both", pady=10)
        vsb_users.pack(side="right", fill="y")
        hsb_users.pack(side="bottom", fill="x")

        # Rodapé da aba (específico para esta aba)
        ttk.Label(self.frame_acesso_usuarios, text="CF Tecnologias", font=("Arial", 10, "bold"),
                  background="#0A3D62", foreground="#FFFFFF").pack(side="bottom", pady=5)

        self.popular_lista_usuarios()
        self.atualizar_permissoes_acesso_usuarios() # Define o estado dos botões com base no papel

    def atualizar_permissoes_acesso_usuarios(self):
        """Atualiza o estado dos botões na aba de acesso a usuários com base no papel do usuário."""
        if self.current_user_role == "Administrador":
            self.btn_add_user.config(state="normal")
            self.btn_edit_user.config(state="normal")
            self.btn_delete_user.config(state="normal")
        else:
            self.btn_add_user.config(state="disabled")
            self.btn_edit_user.config(state="disabled")
            self.btn_delete_user.config(state="disabled")
            # messagebox.showinfo("Acesso Restrito", "Você não tem permissão para gerenciar usuários.") # Removido para evitar pop-up constante


    def salvar_usuario(self, index_para_edicao=None):
        """Salva um novo usuário ou atualiza um existente."""
        if self.current_user_role != "Administrador":
            messagebox.showwarning("Permissão Negada", "Você não tem permissão para adicionar/editar usuários.")
            return

        username = self.entry_user_username.get().strip()
        password = self.entry_user_password.get().strip()
        role = self.combobox_user_role.get().strip()

        if not all([username, password, role]):
            messagebox.showwarning("Campos Obrigatórios", "Nome de Usuário, Senha e Nível de Acesso são obrigatórios.")
            return

        if index_para_edicao is None: # Adicionar novo usuário
            if username in self.users['username'].values:
                messagebox.showwarning("Usuário Existente", f"O nome de usuário '{username}' já existe.")
                return
            
            novo_usuario = pd.DataFrame([{"username": username, "password": password, "role": role}])
            self.users = pd.concat([self.users, novo_usuario], ignore_index=True)
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            self.limpar_campos_usuario()
        else: # Editar usuário existente
            # Verifica se o novo username já existe e não é o próprio usuário que está sendo editado
            if username in self.users['username'].values and self.users.loc[index_para_edicao, 'username'] != username:
                messagebox.showwarning("Usuário Existente", f"O nome de usuário '{username}' já existe.")
                return

            self.users.loc[index_para_edicao, "username"] = username
            self.users.loc[index_para_edicao, "password"] = password
            self.users.loc[index_para_edicao, "role"] = role
            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            # Fecha a janela de edição se ela estiver aberta
            if hasattr(self, 'edit_user_window') and self.edit_user_window.winfo_exists():
                self.edit_user_window.destroy()

        self.salvar_dados_usuarios()
        self.popular_lista_usuarios()

    def editar_usuario_dialog(self):
        """Abre uma nova janela para editar o usuário selecionado."""
        if self.current_user_role != "Administrador":
            messagebox.showwarning("Permissão Negada", "Você não tem permissão para editar usuários.")
            return

        selected_item = self.tree_users.selection()
        if not selected_item:
            messagebox.showwarning("Nenhum Usuário Selecionado", "Por favor, selecione um usuário na lista para editar.")
            return

        df_index = int(selected_item[0]) # O iid é o índice do DataFrame
        user_data = self.users.loc[df_index].to_dict()

        self.edit_user_window = tk.Toplevel(self.master)
        self.edit_user_window.title(f"Editar Usuário: {user_data['username']}")
        self.edit_user_window.transient(self.master)
        self.edit_user_window.grab_set()

        frame = ttk.Frame(self.edit_user_window, padding="15 15 15 15")
        frame.pack(expand=True, fill="both")

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)

        row_idx = 0
        ttk.Label(frame, text="Nome de Usuário:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_user_username_entry = ttk.Entry(frame, width=30)
        self.edit_user_username_entry.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_user_username_entry.insert(0, user_data["username"])

        row_idx += 1
        ttk.Label(frame, text="Senha:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_user_password_entry = ttk.Entry(frame, width=30, show="*")
        self.edit_user_password_entry.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_user_password_entry.insert(0, user_data["password"]) # Preenche a senha existente

        row_idx += 1
        ttk.Label(frame, text="Nível de Acesso:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.edit_user_role_combobox = ttk.Combobox(frame, width=28, state="readonly", values=["Administrador", "Usuário"])
        self.edit_user_role_combobox.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        self.edit_user_role_combobox.set(user_data["role"])

        row_idx += 1
        ttk.Button(frame, text="Salvar Edição", command=lambda: self._salvar_edicao_usuario(df_index)).grid(row=row_idx, column=0, columnspan=2, pady=20)

    def _salvar_edicao_usuario(self, df_index):
        """Salva as alterações de um usuário editado."""
        username = self.edit_user_username_entry.get().strip()
        password = self.edit_user_password_entry.get().strip()
        role = self.edit_user_role_combobox.get().strip()

        if not all([username, password, role]):
            messagebox.showwarning("Campos Obrigatórios", "Nome de Usuário, Senha e Nível de Acesso são obrigatórios.")
            return
        
        # Verifica se o novo username já existe e não é o próprio usuário que está sendo editado
        if username in self.users['username'].values and self.users.loc[df_index, 'username'] != username:
            messagebox.showwarning("Usuário Existente", f"O nome de usuário '{username}' já existe.")
            return

        self.users.loc[df_index, "username"] = username
        self.users.loc[df_index, "password"] = password
        self.users.loc[df_index, "role"] = role

        self.salvar_dados_usuarios()
        messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
        self.edit_user_window.destroy()
        self.popular_lista_usuarios()

    def excluir_usuario(self):
        """Exclui os usuários selecionados na lista."""
        if self.current_user_role != "Administrador":
            messagebox.showwarning("Permissão Negada", "Você não tem permissão para excluir usuários.")
            return

        selected_items = self.tree_users.selection()
        if not selected_items:
            messagebox.showwarning("Nenhum Usuário Selecionado", "Por favor, selecione um ou mais usuários para excluir.")
            return

        # Não permite excluir o último administrador
        admin_users = self.users[self.users['role'] == 'Administrador']
        if len(admin_users) == len(selected_items) and all(self.users.loc[int(self.tree_users.item(item)['iid']), 'role'] == 'Administrador' for item in selected_items):
            messagebox.showwarning("Erro de Exclusão", "Não é possível excluir todos os usuários administradores. Deve haver pelo menos um administrador no sistema.")
            return

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir {len(selected_items)} usuário(s) selecionado(s)?"):
            indices_para_excluir = [int(self.tree_users.item(item)['iid']) for item in selected_items]
            
            self.users = self.users.drop(indices_para_excluir).reset_index(drop=True)
            self.salvar_dados_usuarios()
            messagebox.showinfo("Sucesso", f"{len(selected_items)} usuário(s) excluído(s) com sucesso!")
            self.popular_lista_usuarios()

    def limpar_campos_usuario(self):
        """Limpa os campos de entrada da aba de Acesso a Usuários."""
        self.entry_user_username.delete(0, tk.END)
        self.entry_user_password.delete(0, tk.END)
        self.combobox_user_role.set("Usuário") # Reinicia para o padrão

    def popular_lista_usuarios(self):
        """Preenche a tabela de usuários com os dados."""
        for i in self.tree_users.get_children():
            self.tree_users.delete(i)

        if not self.users.empty:
            for index, row in self.users.iterrows():
                self.tree_users.insert("", "end", iid=index, values=(
                    row["username"],
                    row["role"]
                ))


if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginApp(root)
    root.mainloop()
