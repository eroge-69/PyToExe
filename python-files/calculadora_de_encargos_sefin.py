import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from datetime import datetime, date
import requests
import numpy as np
from pathlib import Path
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class SelicCorrector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculadora de Encargos - Taxa Selic Acumulada com Multa")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Dados da Selic
        self.selic_data = None
        self.input_file = None
        self.output_data = None
        
        # Variável para controlar o cálculo de multa
        self.incluir_multa = tk.BooleanVar(value=False)
        
        self.setup_ui()
        self.load_selic_data()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Calculadora de Encargos - Juros Taxa Selic Acumulada com Multa", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status da Selic
        self.status_label = ttk.Label(main_frame, text="Carregando dados da Selic...", 
                                     foreground='orange')
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Frame para seleção de arquivo
        file_frame = ttk.LabelFrame(main_frame, text="1. Selecionar Arquivo", padding="10")
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="Escolher Arquivo Excel/CSV", 
                  command=self.select_file).grid(row=0, column=0, padx=(0, 10))
        
        self.file_label = ttk.Label(file_frame, text="Nenhum arquivo selecionado", 
                                   foreground='gray')
        self.file_label.grid(row=0, column=1, sticky=tk.W)
        
        # Frame para opções de cálculo
        options_frame = ttk.LabelFrame(main_frame, text="2. Opções de Cálculo", padding="10")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Checkbox para incluir multa
        multa_checkbox = ttk.Checkbutton(
            options_frame, 
            text="Incluir multa diária de 0,33% (limitada a 10%)", 
            variable=self.incluir_multa,
            command=self.on_multa_changed
        )
        multa_checkbox.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Label explicativa sobre a multa
        self.multa_info = ttk.Label(
            options_frame, 
            text="• A multa será calculada como 0,33% ao dia entre as datas inicial e final\n• O valor da multa será limitado ao máximo de 10% do valor inicial\n• O resultado final incluirá juros + multa",
            foreground='gray',
            justify=tk.LEFT
        )
        self.multa_info.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Frame para instruções
        info_frame = ttk.LabelFrame(main_frame, text="3. Instruções", padding="10")
        info_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        instructions = """O arquivo deve conter três colunas:
• Data Inicial (aceita: formato de data do Excel, DD/MM/AAAA, MM/AAAA, AAAA-MM)
• Data Final (aceita: formato de data do Excel, DD/MM/AAAA, MM/AAAA, AAAA-MM)
• Valor Inicial (valores numéricos, aceita vírgulas como separador decimal)

O programa irá:
• Corrigir CADA VALOR pela Selic entre as datas inicial e final específicas
• Usar fórmula: (Fator Data Inicial - Fator Mês Anterior à Data Final) + 1
• MANTER TODOS OS REGISTROS SEPARADOS (uma linha para cada período)
• Opcionalmente incluir multa de 0,33% ao dia (limitada a 10%)
• Gerar arquivo Excel com: datas, valor inicial, valor corrigido, juros, multa e valor total final"""
        
        ttk.Label(info_frame, text=instructions, justify=tk.LEFT, 
                 wraplength=700).grid(row=0, column=0, sticky=tk.W)
        
        # Frame para preview dos dados de entrada
        preview_frame = ttk.LabelFrame(main_frame, text="4. Preview dos Dados de Entrada", padding="10")
        preview_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Treeview para preview de entrada
        columns = ('Data Inicial', 'Data Final', 'Valor Inicial')
        self.tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=5)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # Scrollbar para o treeview de entrada
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Frame para preview dos resultados
        results_frame = ttk.LabelFrame(main_frame, text="5. Preview dos Resultados", padding="10")
        results_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Treeview para preview dos resultados - colunas básicas
        self.base_result_columns = ('Data Inicial', 'Data Final', 'Valor Inicial', 'Valor Corrigido', 'Juros', 'Fator Correção')
        self.multa_result_columns = ('Data Inicial', 'Data Final', 'Valor Inicial', 'Valor Corrigido', 'Juros', 'Alíquota Multa', 'Valor Multa', 'Valor Total Final', 'Fator Correção')
        
        self.results_tree = ttk.Treeview(results_frame, columns=self.base_result_columns, show='headings', height=5)
        
        self.configure_results_tree()
        
        # Scrollbar para o treeview de resultados
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Frame para botões de ação
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        self.process_button = ttk.Button(button_frame, text="Processar e Corrigir", 
                                        command=self.process_data, state='disabled',
                                        style='Accent.TButton')
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_button = ttk.Button(button_frame, text="Exportar Resultado", 
                                       command=self.export_data, state='disabled')
        self.export_button.pack(side=tk.LEFT)
        
        # Barra de progresso
        self.progress_var = tk.StringVar()
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=8, column=0, columnspan=2, pady=(10, 0))
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        main_frame.rowconfigure(6, weight=1)
    
    def configure_results_tree(self):
        """Configura as colunas do TreeView de resultados baseado na opção de multa"""
        # Limpar TreeView
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if self.incluir_multa.get():
            columns = self.multa_result_columns
        else:
            columns = self.base_result_columns
        
        # Reconfigurar colunas
        self.results_tree.configure(columns=columns)
        
        # Configurar headers e larguras
        for col in columns:
            self.results_tree.heading(col, text=col)
            if col in ['Valor Inicial', 'Valor Corrigido', 'Juros', 'Valor Multa', 'Valor Total Final']:
                self.results_tree.column(col, width=120)
            elif col in ['Fator Correção', 'Alíquota Multa']:
                self.results_tree.column(col, width=100)
            else:
                self.results_tree.column(col, width=100)
    
    def on_multa_changed(self):
        """Callback quando a opção de multa é alterada"""
        self.configure_results_tree()
        
        # Atualizar preview se já há dados processados
        if hasattr(self, 'output_data') and self.output_data is not None:
            self.update_results_preview(self.output_data)
    
    def load_selic_data(self):
        """Carrega os dados da Selic usando a API do IPEA"""
        try:
            import ipeadatapy as ip
            
            self.status_label.config(text="Carregando dados da Selic via API do IPEA...", foreground='orange')
            self.root.update()

            def importar_series_temporais(codigos_series, ano_inicial):
                """Importa séries temporais do ipeadata"""
                series_importadas = {}
                
                for nome_serie, codigo_serie in codigos_series.items():
                    try:
                        # Importar a série
                        serie = ip.timeseries(codigo_serie, yearGreaterThan=ano_inicial)
                        
                        if 'VALUE ((% a.m.))' in serie.columns:
                            coluna_valores = 'VALUE ((% a.m.))'
                        elif 'VALUE (-)' in serie.columns:
                            coluna_valores = 'VALUE (-)'
                        else:
                            raise ValueError(f"A série '{codigo_serie}' não possui as colunas esperadas.")
                        
                        serie = serie[coluna_valores].rename(nome_serie).to_frame().reset_index()
                        series_importadas[nome_serie] = serie
                    
                    except Exception as e:
                        raise Exception(f"Erro ao importar a série '{nome_serie}' ({codigo_serie}): {e}")
                
                return series_importadas

            def calcular_variacoes(series):
                """Calcula a variação percentual mensal e o fator para a SELIC"""
                series_variadas = {}

                for nome_serie, df in series.items():
                    try:
                        if df.shape[0] < 2:
                            raise ValueError(f"A série '{nome_serie}' não possui dados suficientes.")

                        valores = df[nome_serie]

                        if nome_serie == 'SELIC':
                            # Cálculo do fator mensal
                            fator = (1 + valores / 100).rename('Fator')
                            # Cálculo do fator acumulado
                            fator_acumulado = fator.cumprod().rename('Fator Acumulado')

                            # Criar vetor de correção legal
                            fator_correcao_legal = [0] * len(valores)

                            # Último mês (mês atual) recebe 0
                            fator_correcao_legal[-1] = 0
                            # Penúltimo mês recebe 1
                            if len(valores) > 1:
                                fator_correcao_legal[-2] = 1

                            # Acumular da terceira última linha até a primeira
                            soma = 1
                            for i in range(len(valores) - 3, -1, -1):
                                soma += valores[i + 1]
                                fator_correcao_legal[i] = round(float(soma), 10)

                            df_resultado = df.copy()
                            df_resultado[f'{nome_serie} Fator'] = fator
                            df_resultado[f'{nome_serie} Fator Acumulado'] = fator_acumulado
                            df_resultado[f'{nome_serie} Fator Correção Legal'] = fator_correcao_legal
                            df_resultado[f'{nome_serie} Fator Correção Legal GRPFOR'] = fator_correcao_legal #[int(x * 100) / 100.0 for x in fator_correcao_legal]
                        
                        series_variadas[nome_serie] = df_resultado

                    except Exception as e:
                        raise Exception(f"Erro ao processar a série '{nome_serie}': {e}")
                
                return series_variadas

            # Definindo ano inicial
            ano_inicial = 1993

            # Séries de interesse
            codigos_series = {
                'SELIC': 'BM12_TJOVER12'
            }

            # Consultando séries
            series = importar_series_temporais(codigos_series, ano_inicial)

            # Calculando as taxas de variação e fatores mensais
            series = calcular_variacoes(series)

            # Montando base final
            merged_df = list(series.values())[0]

            # Formatando o dataframe final
            merged_df['DATE'] = merged_df['DATE'].dt.strftime('%m-%Y')
            merged_df = merged_df[['DATE', 'SELIC Fator Correção Legal GRPFOR']]
            merged_df = merged_df.rename(columns={'DATE':'Data', 'SELIC Fator Correção Legal GRPFOR':'Taxa de Juros'})
            merged_df['Taxa de Juros'] = merged_df['Taxa de Juros'] / 100
            
            self.selic_data = merged_df
            
            self.status_label.config(text=f"✓ Dados da Selic carregados ({len(self.selic_data)} registros)", 
                                   foreground='green')
            
        except ImportError:
            error_msg = "Biblioteca 'ipeadatapy' não encontrada. Execute: pip install ipeadatapy"
            self.status_label.config(text=f"✗ {error_msg}", foreground='red')
            messagebox.showerror("Erro", error_msg)
            
        except Exception as e:
            self.status_label.config(text=f"✗ Erro ao carregar dados da Selic: {str(e)}", 
                                   foreground='red')
            messagebox.showerror("Erro", f"Erro ao carregar dados da Selic:\n{str(e)}")
    
    def select_file(self):
        """Seleciona o arquivo de entrada"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls"), 
                      ("Arquivos CSV", "*.csv"),
                      ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.input_file = file_path
            self.file_label.config(text=Path(file_path).name, foreground='black')
            self.load_input_data()
    
    def load_input_data(self):
        """Carrega e valida os dados do arquivo de entrada"""
        try:
            # Determinar o tipo de arquivo e carregar
            if self.input_file.endswith('.csv'):
                data = pd.read_csv(self.input_file)
            else:
                data = pd.read_excel(self.input_file)
            
            # Verificar se tem pelo menos 3 colunas
            if len(data.columns) < 3:
                raise ValueError("O arquivo deve ter pelo menos 3 colunas: Data Inicial, Data Final e Valor")
            
            # Assumir que as três primeiras colunas são Data Inicial, Data Final e Valor
            data = data.iloc[:, :3]
            data.columns = ['Data Inicial', 'Data Final', 'Valor Inicial']
            
            # Limpar dados nulos
            data = data.dropna()
            
            # Converter valores para numérico (tratando vírgulas como separador decimal)
            data['Valor Inicial'] = data['Valor Inicial'].astype(str).str.replace(',', '.', regex=False)
            data['Valor Inicial'] = pd.to_numeric(data['Valor Inicial'], errors='coerce')
            data = data.dropna()
            
            if len(data) == 0:
                raise ValueError("Nenhum dado válido encontrado no arquivo")
            
            # Armazenar dados originais
            self.input_data = data
            
            # Atualizar preview
            self.update_preview(data)
            
            # Habilitar botão de processar
            if self.selic_data is not None:
                self.process_button.config(state='normal')
            
            self.progress_var.set(f"✓ {len(data)} registros carregados do arquivo")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo:\n{str(e)}")
            self.progress_var.set("✗ Erro ao carregar arquivo")
    
    def update_preview(self, data):
        """Atualiza o preview dos dados de entrada"""
        # Limpar preview anterior
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar novos dados (máximo 50 linhas no preview)
        for idx, row in data.head(50).iterrows():
            self.tree.insert('', 'end', values=(row['Data Inicial'], row['Data Final'], f"R$ {row['Valor Inicial']:,.2f}"))
        
        if len(data) > 50:
            self.tree.insert('', 'end', values=("...", "...", f"... e mais {len(data)-50} registros"))
    
    def update_results_preview(self, results_data):
        """Atualiza o preview dos resultados processados"""
        # Limpar preview anterior
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if results_data is None or len(results_data) == 0:
            return
        
        # Adicionar resultados (máximo 50 linhas no preview)
        valid_results = results_data[results_data['Erro'] == ''].head(50)
        
        for idx, row in valid_results.iterrows():
            if self.incluir_multa.get():
                values = (
                    str(row['Data Inicial']),
                    str(row['Data Final']),
                    f"R$ {row['Valor Inicial']:,.2f}",
                    f"R$ {row['Valor Corrigido']:,.2f}",
                    f"R$ {row['Juros do Período']:,.2f}",
                    f"{row['Alíquota Multa']:.2f}%",
                    f"R$ {row['Valor Multa']:,.2f}",
                    f"R$ {row['Valor Total Final']:,.2f}",
                    f"{row['Fator de Correção']:.6f}"
                )
            else:
                values = (
                    str(row['Data Inicial']),
                    str(row['Data Final']),
                    f"R$ {row['Valor Inicial']:,.2f}",
                    f"R$ {row['Valor Corrigido']:,.2f}",
                    f"R$ {row['Juros do Período']:,.2f}",
                    f"{row['Fator de Correção']:.6f}"
                )
            self.results_tree.insert('', 'end', values=values)
        
        # Mostrar registros com erro separadamente
        error_results = results_data[results_data['Erro'] != '']
        if len(error_results) > 0:
            if self.incluir_multa.get():
                self.results_tree.insert('', 'end', values=("--- REGISTROS COM ERRO ---", "", "", "", "", "", "", "", ""))
            else:
                self.results_tree.insert('', 'end', values=("--- REGISTROS COM ERRO ---", "", "", "", "", ""))
            
            for idx, row in error_results.head(10).iterrows():
                if self.incluir_multa.get():
                    values = (
                        str(row['Data Inicial']),
                        str(row['Data Final']),
                        f"R$ {row['Valor Inicial']:,.2f}",
                        "ERRO",
                        row['Erro'],
                        "", "", "", ""
                    )
                else:
                    values = (
                        str(row['Data Inicial']),
                        str(row['Data Final']),
                        f"R$ {row['Valor Inicial']:,.2f}",
                        "ERRO",
                        row['Erro'],
                        ""
                    )
                self.results_tree.insert('', 'end', values=values)
        
        if len(results_data) > 50:
            if self.incluir_multa.get():
                self.results_tree.insert('', 'end', values=("...", "...", f"... e mais {len(results_data)-50} registros", "", "", "", "", "", ""))
            else:
                self.results_tree.insert('', 'end', values=("...", "...", f"... e mais {len(results_data)-50} registros", "", "", ""))
    
    def normalize_date(self, date_input):
        """Normaliza diferentes formatos de data para MM-YYYY"""
        try:
            # Se já é um objeto datetime/Timestamp (formato nativo do Excel)
            if pd.isna(date_input):
                return None
                
            if isinstance(date_input, (pd.Timestamp, datetime)):
                return date_input.strftime("%m-%Y")
            
            # Converter para string se não for
            date_str = str(date_input).strip()
            
            # Remover informações de tempo se existirem (ex: "2020-01-15 00:00:00")
            if ' ' in date_str:
                date_str = date_str.split(' ')[0]
            
            # Tentar vários formatos de string
            formats = [
                "%d/%m/%Y",  # DD/MM/YYYY
                "%m/%Y",     # MM/YYYY
                "%Y-%m",     # YYYY-MM
                "%Y-%m-%d",  # YYYY-MM-DD
                "%d-%m-%Y",  # DD-MM-YYYY
                "%m-%Y",     # MM-YYYY
                "%Y/%m/%d",  # YYYY/MM/DD
                "%d.%m.%Y",  # DD.MM.YYYY
                "%Y.%m.%d"   # YYYY.MM.DD
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%m-%Y")
                except:
                    continue
            
            # Tentar converter string que pode ser timestamp do Excel
            try:
                # Se for um número (timestamp do Excel)
                if date_str.replace('.', '').isdigit():
                    # Converter timestamp do Excel para datetime
                    excel_date = float(date_str)
                    # Excel conta dias desde 1900-01-01 (com correção de bug)
                    dt = datetime(1900, 1, 1) + pd.Timedelta(days=excel_date-2)
                    return dt.strftime("%m-%Y")
            except:
                pass
            
            # Se nenhum formato funcionou, tentar extrair mês e ano manualmente
            # Remover caracteres não numéricos e separar
            clean_str = date_str.replace('/', '-').replace('.', '-').replace(' ', '-')
            parts = [p for p in clean_str.split('-') if p.isdigit()]
            
            if len(parts) >= 2:
                # Identificar ano (número de 4 dígitos ou > 31)
                year_candidates = [int(p) for p in parts if len(p) == 4 or int(p) > 31]
                month_candidates = [int(p) for p in parts if int(p) <= 12 and int(p) >= 1]
                
                if year_candidates and month_candidates:
                    year = year_candidates[0]
                    month = month_candidates[0]
                    return f"{month:02d}-{year}"
                
                # Fallback: assumir que os dois últimos números são mês e ano
                try:
                    if len(parts) >= 3:  # DD/MM/YYYY
                        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                        if year < 100:  # Converter ano de 2 dígitos
                            year += 2000 if year < 50 else 1900
                    elif len(parts) == 2:  # MM/YYYY ou YYYY/MM
                        p1, p2 = int(parts[0]), int(parts[1])
                        if p1 > 12:  # Primeiro é ano
                            year, month = p1, p2
                        else:  # Primeiro é mês
                            month, year = p1, p2
                    
                    if 1 <= month <= 12 and year > 1900:
                        return f"{month:02d}-{year}"
                except:
                    pass
            
            return None
            
        except Exception as e:
            print(f"Erro ao fazer parse da data '{date_input}': {e}")
            return None
    
    def parse_full_date(self, date_input):
            """Converte a data de entrada para um objeto datetime completo"""
            try:
                # Se já é um objeto datetime/Timestamp
                if isinstance(date_input, (pd.Timestamp, datetime)):
                    return date_input.replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Converter para string se não for
                date_str = str(date_input).strip()
                
                # Remover informações de tempo se existirem
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                
                # Tentar vários formatos de string
                formats = [
                    "%d/%m/%Y",  # DD/MM/YYYY
                    "%Y-%m-%d",  # YYYY-MM-DD
                    "%d-%m-%Y",  # DD-MM-YYYY
                    "%Y/%m/%d",  # YYYY/MM/DD
                    "%d.%m.%Y",  # DD.MM.YYYY
                    "%Y.%m.%d"   # YYYY.MM.DD
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except:
                        continue
                
                # Se é só mês/ano, assumir o primeiro dia do mês
                month_year_formats = [
                    "%m/%Y",     # MM/YYYY
                    "%Y-%m",     # YYYY-MM
                    "%m-%Y",     # MM-YYYY
                ]
                
                for fmt in month_year_formats:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.replace(day=1)  # Primeiro dia do mês
                    except:
                        continue
                
                # Tentar timestamp do Excel
                try:
                    if date_str.replace('.', '').isdigit():
                        excel_date = float(date_str)
                        return datetime(1900, 1, 1) + pd.Timedelta(days=excel_date-2)
                except:
                    pass
                
                return None
                
            except Exception as e:
                print(f"Erro ao normalizar data '{date_input}': {e}")
                return None

    def calculate_daily_fine(self, start_date, end_date, initial_value):
        """Calcula a multa diária de 0,33% limitada a 10%"""
        try:
            # Converter datas para objetos datetime
            start_dt = self.parse_full_date(start_date)
            end_dt = self.parse_full_date(end_date)
            
            if start_dt is None or end_dt is None:
                return 0.0, 0.0  # alíquota, valor
            
            # Se a data final for só mês/ano, assumir o último dia do mês
            if len(str(end_date).replace(' ', '').split('/')) == 2 or len(str(end_date).replace(' ', '').split('-')) == 2:
                # Ir para o próximo mês e subtrair um dia para pegar o último dia do mês
                if end_dt.month == 12:
                    next_month = end_dt.replace(year=end_dt.year + 1, month=1)
                else:
                    next_month = end_dt.replace(month=end_dt.month + 1)
                end_dt = next_month - pd.Timedelta(days=1)
            
            # Calcular diferença em dias
            days_diff = (end_dt - start_dt).days
            
            if days_diff <= 0:
                return 0.0, 0.0
            
            # Calcular multa: 0,33% ao dia
            daily_rate = 0.0033  # 0,33%
            total_fine_rate = days_diff * daily_rate
            
            # Limitar a 10%
            if total_fine_rate > 0.10:
                total_fine_rate = 0.10
            
            # Calcular valor da multa
            fine_value = initial_value * total_fine_rate
            
            return total_fine_rate * 100, fine_value  # retorna em percentual e valor
            
        except Exception as e:
            print(f"Erro ao calcular multa entre {start_date} e {end_date}: {e}")
            return 0.0, 0.0
    
    def get_previous_month(self, date_str):
        """Retorna o mês anterior à data fornecida no formato MM-YYYY"""
        try:
            date_obj = datetime.strptime(date_str, "%m-%Y")
            # Subtrair um mês
            if date_obj.month == 1:
                prev_date = date_obj.replace(year=date_obj.year - 1, month=12)
            else:
                prev_date = date_obj.replace(month=date_obj.month - 1)
            
            return prev_date.strftime("%m-%Y")
        except:
            return None
    
    def calculate_correction_between_dates(self, start_date_str, end_date_str):
        """
        Calcula a correção Selic entre duas datas específicas usando:
        Fator = (Fator da Data Inicial - Fator do Mês Anterior à Data Final)
        """
        try:
            # Obter o mês anterior à data final
            prev_end_month = self.get_previous_month(end_date_str)
            if not prev_end_month:
                return 0.0
            
            # Encontrar os fatores nas datas
            start_factor = None
            prev_end_factor = None
            
            for idx, row in self.selic_data.iterrows():
                if row['Data'] == start_date_str:
                    start_factor = row['Taxa de Juros']
                if row['Data'] == prev_end_month:
                    prev_end_factor = row['Taxa de Juros']
            
            # Se não encontrou as datas exatas, buscar as mais próximas
            if start_factor is None or prev_end_factor is None:
                selic_dates = pd.to_datetime(self.selic_data['Data'], format='%m-%Y')
                start_dt = datetime.strptime(start_date_str, "%m-%Y")
                prev_end_dt = datetime.strptime(prev_end_month, "%m-%Y")
                
                # Buscar data de início mais próxima (anterior ou igual)
                if start_factor is None:
                    valid_starts = selic_dates <= start_dt
                    if valid_starts.any():
                        start_idx = valid_starts[::-1].idxmax()  # Último True (mais recente <= start_dt)
                        start_factor = self.selic_data.iloc[start_idx]['Taxa de Juros']
                    else:
                        start_factor = 0.0
                
                # Buscar data final mais próxima (anterior ou igual)
                if prev_end_factor is None:
                    valid_ends = selic_dates <= prev_end_dt
                    if valid_ends.any():
                        end_idx = valid_ends[::-1].idxmax()  # Último True (mais recente <= prev_end_dt)
                        prev_end_factor = self.selic_data.iloc[end_idx]['Taxa de Juros']
                    else:
                        prev_end_factor = 0.0
            
            # Aplicar a fórmula correta: (Fator Data Inicial - Fator Mês Anterior à Data Final)
            # Os fatores já estão como fatores de correção, então usamos diretamente
            correction_factor = start_factor - prev_end_factor + 0.01
            
            # Retornar o fator de correção (já representa o ganho percentual)
            return correction_factor
            
        except Exception as e:
            print(f"Erro no cálculo da correção entre {start_date_str} e {end_date_str}: {e}")
            print(f"Start factor: {start_factor if 'start_factor' in locals() else 'N/A'}")
            print(f"Prev end factor: {prev_end_factor if 'prev_end_factor' in locals() else 'N/A'}")
            return 0.0
    
    def process_data(self):
        """Processa os dados e calcula as correções"""
        try:
            self.progress_var.set("Processando dados...")
            self.root.update()
            
            results = []
            incluir_multa = self.incluir_multa.get()
            
            for idx, row in self.input_data.iterrows():
                # Normalizar datas inicial e final para cálculo de juros
                normalized_start = self.normalize_date(row['Data Inicial'])
                normalized_end = self.normalize_date(row['Data Final'])
                
                if normalized_start is None or normalized_end is None:
                    result = {
                        'Data Inicial': row['Data Inicial'],
                        'Data Final': row['Data Final'],
                        'Valor Inicial': row['Valor Inicial'],
                        'Valor Corrigido': row['Valor Inicial'],
                        'Juros do Período': 0.0,
                        'Fator de Correção': 0.0,
                        'Erro': 'Data inválida'
                    }
                    
                    if incluir_multa:
                        result.update({
                            'Alíquota Multa': 0.0,
                            'Valor Multa': 0.0,
                            'Valor Total Final': row['Valor Inicial']
                        })
                    
                    results.append(result)
                    continue
                
                # Verificar se a data inicial é anterior à data final
                start_dt = datetime.strptime(normalized_start, "%m-%Y")
                end_dt = datetime.strptime(normalized_end, "%m-%Y")
                
                if start_dt > end_dt:
                    result = {
                        'Data Inicial': row['Data Inicial'],
                        'Data Final': row['Data Final'],
                        'Valor Inicial': row['Valor Inicial'],
                        'Valor Corrigido': row['Valor Inicial'],
                        'Juros do Período': 0.0,
                        'Fator de Correção': 0.0,
                        'Erro': 'Data inicial posterior à data final'
                    }
                    
                    if incluir_multa:
                        result.update({
                            'Alíquota Multa': 0.0,
                            'Valor Multa': 0.0,
                            'Valor Total Final': row['Valor Inicial']
                        })
                    
                    results.append(result)
                    continue
                
                # Calcular correção usando o método Selic
                correction_factor = self.calculate_correction_between_dates(normalized_start, normalized_end)
                
                # Calcular valores dos juros
                initial_value = row['Valor Inicial']
                corrected_value = initial_value * (1 + correction_factor)
                interest_value = corrected_value - initial_value
                
                # Calcular multa se solicitado
                fine_rate = 0.0
                fine_value = 0.0
                
                if incluir_multa:
                    fine_rate, fine_value = self.calculate_daily_fine(
                        row['Data Inicial'], 
                        row['Data Final'], 
                        initial_value
                    )
                
                # Calcular valor total final
                total_final_value = corrected_value + fine_value
                
                result = {
                    'Data Inicial': row['Data Inicial'],
                    'Data Final': row['Data Final'],
                    'Valor Inicial': initial_value,
                    'Valor Corrigido': corrected_value,
                    'Juros do Período': interest_value,
                    'Fator de Correção': correction_factor,
                    'Erro': ''
                }
                
                if incluir_multa:
                    result.update({
                        'Alíquota Multa': fine_rate,
                        'Valor Multa': fine_value,
                        'Valor Total Final': total_final_value
                    })
                
                results.append(result)
            
            self.output_data = pd.DataFrame(results)
            
            # Atualizar interface
            self.progress_var.set(f"✓ Processamento concluído! {len(results)} registros processados")
            self.export_button.config(state='normal')
            
            # Atualizar preview dos resultados
            self.update_results_preview(self.output_data)
            
            # Contar registros processados
            registros_validos = len([r for r in results if not r['Erro']])
            registros_erro = len([r for r in results if r['Erro']])
            
            multa_text = ""
            if incluir_multa:
                multa_text = "\n• Multa diária de 0,33% (limitada a 10%) aplicada"
            
            summary = f"""Processamento Concluído:
            
• {registros_validos} registros processados com sucesso
• {registros_erro} registros com erro
• Total: {len(results)} registros{multa_text}

Cada valor foi corrigido pela Selic entre suas datas inicial e final específicas
usando a fórmula: (Fator Data Inicial - Fator Mês Anterior à Data Final) + 1."""
            
            messagebox.showinfo("Processamento Concluído", summary)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar dados:\n{str(e)}")
            self.progress_var.set("✗ Erro no processamento")
    
    def export_data(self):
        """Exporta os resultados para um arquivo Excel"""
        try:
            if self.output_data is None:
                messagebox.showwarning("Aviso", "Nenhum dado processado para exportar")
                return
            
            file_path = filedialog.asksaveasfilename(
                title="Salvar resultado",
                defaultextension=".xlsx",
                filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos os arquivos", "*.*")]
            )
            
            if file_path:
                # Preparar dados para exportação (mantendo todos os registros individuais)
                export_data = self.output_data.copy()
                
                # Filtrar apenas registros válidos (sem erro) para formatação
                registros_validos = export_data[export_data['Erro'] == ''].copy()
                registros_erro = export_data[export_data['Erro'] != ''].copy()

                # --- NOVO: Dividir a Alíquota Multa por 100 para o formato de porcentagem do Excel ---
                if 'Alíquota Multa' in registros_validos.columns:
                    registros_validos['Alíquota Multa'] = registros_validos['Alíquota Multa'] / 100
                
                # Reunir todos os registros novamente
                if len(registros_erro) > 0:
                    export_data = pd.concat([registros_validos, registros_erro], ignore_index=True)
                else:
                    export_data = registros_validos
                
                # Exportar para Excel com cada registro individual
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    sheet_name = 'Correção com Multa' if self.incluir_multa.get() else 'Correção por Período'
                    
                    # Exporta o DataFrame com os dados numéricos brutos
                    export_data.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Acessa a planilha para aplicar a formatação de célula
                    workbook = writer.book
                    sheet = writer.sheets[sheet_name]
                    
                    # Dicionário de colunas e seus formatos
                    format_mapping = {
                        'Valor Inicial': '#.##0,00',
                        'Valor Corrigido': '#.##0,00',
                        'Juros do Período': '#.##0,00',
                        'Valor Multa': '#.##0,00',
                        'Valor Total Final': '#.##0,00',
                        'Fator de Correção': '0.000000',
                        'Alíquota Multa': '0.00%'
                    }
                    
                    # Itera sobre as colunas para aplicar a formatação
                    for col_name, fmt in format_mapping.items():
                        if col_name in export_data.columns:
                            # Encontra a letra da coluna no Excel
                            col_idx = export_data.columns.get_loc(col_name) + 1
                            col_letter = get_column_letter(col_idx)
                            
                            # Aplica a formatação a todas as células da coluna
                            for cell in sheet[col_letter]:
                                cell.number_format = fmt
                    
                    # Se houver registros com erro, criar uma aba separada
                    if len(registros_erro) > 0:
                        registros_erro.to_excel(writer, sheet_name='Registros com Erro', index=False)
                
                registros_processados = len(export_data)
                self.progress_var.set(f"✓ Arquivo exportado: {Path(file_path).name} ({registros_processados} registros)")
                
                multa_info = " (com multa)" if self.incluir_multa.get() else ""
                messagebox.showinfo("Sucesso", f"Arquivo exportado com sucesso!\n\n{file_path}\n\n{registros_processados} registros individuais processados{multa_info}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar arquivo:\n{str(e)}")
    
    def run(self):
        """Executa a aplicação"""
        self.root.mainloop()

if __name__ == "__main__":
    # Verificar dependências
    try:
        import pandas as pd
        import numpy as np
        import ipeadatapy as ip
    except ImportError as e:
        print(f"Erro: Biblioteca necessária não encontrada - {e}")
        print("Execute: pip install pandas numpy ipeadatapy openpyxl")
        exit(1)
    
    app = SelicCorrector()
    app.run()