import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from datetime import datetime
import re

class DataFrameViewer:
    def __init__(self, df):
        self.df = df
        self.current_index = 0
        self.max_index = len(df) - 1
        
        # Campos que queremos exibir (adicionando o novo campo Telefone Sem 9)
        self.fields = [
            'CPF', 'Nome', 'Nome Abreviado', 'RG', 'Orgão Expeditor', 'Dat. Expedição',
            'Cep', 'E-Mail', 'Tip. Logradouro', 'Logradouro', 
            'Num. Endereço', 'Bairro', 'Telefone', 'Telefone Sem 9'
        ]
        
        # Campos que contêm datas (para formatação)
        self.date_fields = ['Dat. Expedição']
        
        self.setup_ui()
        self.update_display()
    
    def format_date(self, date_value):
        """Formatar data para dd/mm/aaaa"""
        if pd.isna(date_value) or date_value == '' or str(date_value).lower() == 'nan':
            return ''
        
        try:
            # Se já é uma string, tentar converter
            if isinstance(date_value, str):
                # Tentar diferentes formatos de data
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']:
                    try:
                        date_obj = datetime.strptime(date_value.split()[0], fmt)  # Remove hora se existir
                        return date_obj.strftime('%d/%m/%Y')
                    except:
                        continue
                # Se não conseguiu converter, retorna como string
                return str(date_value)
            
            # Se é um objeto datetime do pandas
            elif hasattr(date_value, 'strftime'):
                return date_value.strftime('%d/%m/%Y')
            
            # Para outros tipos, converter para string
            else:
                return str(date_value)
                
        except Exception as e:
            print(f"Erro ao formatar data '{date_value}': {e}")
            return str(date_value)
    
    def format_cpf(self, cpf_value):
        """Formatar CPF garantindo 11 dígitos com zeros à esquerda"""
        if pd.isna(cpf_value) or cpf_value == '' or str(cpf_value).lower() == 'nan':
            return ''
        
        # Converter para string e remover caracteres não numéricos
        cpf_str = str(cpf_value).strip()
        cpf_digits = ''.join(filter(str.isdigit, cpf_str))
        
        # Se não tem dígitos, retorna vazio
        if not cpf_digits:
            return ''
        
        # Completar com zeros à esquerda até ter 11 dígitos
        cpf_formatted = cpf_digits.zfill(11)
        
        # Se tem mais de 11 dígitos, manter como está (pode ser um erro de dados)
        if len(cpf_digits) > 11:
            cpf_formatted = cpf_digits
        
        return cpf_formatted
    
    def format_telefone(self, telefone_value, remover_9=False):
        """Formatar telefone removendo DDD (31) e opcionalmente o primeiro 9"""
        if pd.isna(telefone_value) or telefone_value == '' or str(telefone_value).lower() == 'nan':
            return ''
        
        # Converter para string e remover caracteres não numéricos
        telefone_str = str(telefone_value).strip()
        telefone_digits = ''.join(filter(str.isdigit, telefone_str))
        
        print(f"Processando telefone: '{telefone_value}' -> dígitos: '{telefone_digits}'")
        
        # Se não tem dígitos, retorna vazio
        if not telefone_digits:
            return ''
        
        # Remover DDD 31 se presente
        # Verifica se começa com 31 e tem pelo menos 10 dígitos (31 + 8 ou 9 dígitos do número)
        if telefone_digits.startswith('31') and len(telefone_digits) >= 10:
            telefone_sem_ddd = telefone_digits[2:]  # Remove os primeiros 2 dígitos (31)
            print(f"Removendo DDD 31: '{telefone_digits}' -> '{telefone_sem_ddd}'")
        else:
            telefone_sem_ddd = telefone_digits
            print(f"Não removeu DDD (não começa com 31 ou muito curto): '{telefone_digits}'")
        
        # Se solicitado, remover o primeiro 9 (para celulares)
        if remover_9:
            # Verifica se começa com 9 e tem 9 dígitos (formato celular 9XXXX-XXXX)
            if telefone_sem_ddd.startswith('9') and len(telefone_sem_ddd) == 9:
                telefone_sem_9 = telefone_sem_ddd[1:]  # Remove o primeiro dígito (9)
                print(f"Removendo 9 inicial: '{telefone_sem_ddd}' -> '{telefone_sem_9}'")
                return telefone_sem_9
            else:
                print(f"Não remove 9 (não começa com 9 ou tamanho incorreto): '{telefone_sem_ddd}'")
                return telefone_sem_ddd
        
        return telefone_sem_ddd
    
    def format_cep(self, cep_value):
        """Formatar CEP removendo todos os caracteres não numéricos"""
        if pd.isna(cep_value) or cep_value == '' or str(cep_value).lower() == 'nan':
            return ''
        
        # Converter para string e remover caracteres não numéricos
        cep_str = str(cep_value).strip()
        cep_digits = ''.join(filter(str.isdigit, cep_str))
        
        print(f"Processando CEP: '{cep_value}' -> dígitos: '{cep_digits}'")
        
        # Se não tem dígitos, retorna vazio
        if not cep_digits:
            return ''
        
        # Completar com zeros à esquerda se tiver menos de 8 dígitos
        if len(cep_digits) < 8:
            cep_formatted = cep_digits.zfill(8)
            print(f"CEP completado com zeros: '{cep_digits}' -> '{cep_formatted}'")
        else:
            cep_formatted = cep_digits
        
        return cep_formatted
    
    def abreviar_nome(self, nome_completo):
        """Abreviar nome mantendo primeiro e último nome completos"""
        # Debug: imprimir o que está sendo processado
        print(f"Processando nome: '{nome_completo}' (tipo: {type(nome_completo)})")
        
        # Verificações mais robustas
        if nome_completo is None:
            print("Nome é None")
            return ''
            
        if pd.isna(nome_completo):
            print("Nome é NaN (pandas)")
            return ''
            
        # Converter para string e limpar
        nome_str = str(nome_completo).strip()
        
        # Verificações adicionais
        if not nome_str or nome_str.lower() in ['nan', 'none', '']:
            print(f"Nome inválido após conversão: '{nome_str}'")
            return ''
        
        print(f"Nome processado: '{nome_str}'")
        
        # Dividir o nome em palavras
        palavras = nome_str.split()
        print(f"Palavras encontradas: {palavras}")
        
        # Se tem apenas uma palavra, retorna como está
        if len(palavras) <= 1:
            print("Nome tem apenas 1 palavra, retornando completo")
            return nome_str
        
        # Se tem apenas duas palavras, retorna como está
        if len(palavras) == 2:
            print("Nome tem 2 palavras, retornando completo")
            return nome_str
        
        # Se tem 3 ou mais palavras, abreviar
        print("Iniciando abreviação...")
        nome_abreviado = []
        
        # Primeiro nome completo
        nome_abreviado.append(palavras[0])
        print(f"Primeiro nome: {palavras[0]}")
        
        # Nomes do meio abreviados
        preposicoes = ['de', 'da', 'do', 'das', 'dos', 'e', 'du', 'le', 'la', 'del', 'della']
        
        for i in range(1, len(palavras) - 1):
            palavra = palavras[i]
            print(f"Processando palavra do meio: '{palavra}'")
            
            # Pular preposições e conectivos comuns
            if palavra.lower() in preposicoes:
                nome_abreviado.append(palavra)
                print(f"Preposição mantida: {palavra}")
            else:
                # Abreviar pegando apenas a primeira letra
                if len(palavra) > 0:
                    abrev = palavra[0].upper()
                    nome_abreviado.append(abrev)
                    print(f"Palavra abreviada: {palavra} -> {abrev}")
        
        # Último nome completo
        nome_abreviado.append(palavras[-1])
        print(f"Último nome: {palavras[-1]}")
        
        resultado = ' '.join(nome_abreviado)
        print(f"Nome abreviado final: '{resultado}'")
        
        return resultado
    
    def simplificar_orgao_expeditor(self, orgao):
        """Simplificar órgão expeditor (ex: SSPMG -> SSP)"""
        if pd.isna(orgao) or orgao == '' or str(orgao).lower() == 'nan':
            return ''
        
        orgao_str = str(orgao).strip().upper()
        
        # Regras de simplificação
        if orgao_str == 'SSPMG':
            return 'SSP'
        elif orgao_str.startswith('SSP'):
            return 'SSP'
        elif orgao_str == 'PCMG':
            return 'PC'
        elif orgao_str.startswith('PC'):
            return 'PC'
        else:
            # Para outros casos, retornar como está
            return orgao_str
    
    def setup_ui(self):
        # Criar janela principal
        self.root = tk.Tk()
        self.root.title(f"Visualizador de Dados - Total: {len(self.df)} registros")
        self.root.geometry("800x650")  # Aumentei um pouco a altura para acomodar o novo campo
        self.root.resizable(True, True)
        
        # Manter janela sempre no topo
        self.root.attributes('-topmost', True)
        
        # Frame principal com scroll
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame para navegação
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill='x', pady=(0, 10))
        
        # Botões de navegação
        self.btn_anterior = ttk.Button(nav_frame, text="← Anterior", command=self.anterior)
        self.btn_anterior.pack(side='left', padx=(0, 5))
        
        self.btn_proximo = ttk.Button(nav_frame, text="Próximo →", command=self.proximo)
        self.btn_proximo.pack(side='left', padx=(0, 10))
        
        # Campo para ir diretamente a uma linha
        ttk.Label(nav_frame, text="Ir para linha:").pack(side='left', padx=(10, 5))
        
        self.entry_linha = ttk.Entry(nav_frame, width=8)
        self.entry_linha.pack(side='left', padx=(0, 5))
        self.entry_linha.bind('<Return>', self.ir_para_linha)
        
        self.btn_ir = ttk.Button(nav_frame, text="Ir", command=self.ir_para_linha)
        self.btn_ir.pack(side='left', padx=(0, 10))
        
        # Label com posição atual
        self.lbl_posicao = ttk.Label(nav_frame, text="", font=('Arial', 10, 'bold'))
        self.lbl_posicao.pack(side='left', padx=(10, 0))
        
        # Checkbox para manter sempre no topo
        self.always_on_top = tk.BooleanVar(value=True)
        chk_top = ttk.Checkbutton(nav_frame, text="Sempre no topo", 
                                 variable=self.always_on_top,
                                 command=self.toggle_always_on_top)
        chk_top.pack(side='right')
        
        # Frame com scroll para os dados
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame para os campos de dados
        self.data_frame = scrollable_frame
        self.field_vars = {}
        self.field_labels = {}
        
        # Criar campos para cada informação
        for i, field in enumerate(self.fields):
            # Frame para cada campo
            field_frame = ttk.Frame(self.data_frame)
            field_frame.pack(fill='x', pady=2)
            field_frame.grid_columnconfigure(1, weight=1)
            
            # Label do campo
            label = ttk.Label(field_frame, text=f"{field}:", width=18, anchor='w')  # Aumentei a largura para acomodar "Telefone Sem 9"
            label.grid(row=0, column=0, sticky='w', padx=(0, 10))
            
            # Entry para mostrar o valor
            var = tk.StringVar()
            entry = ttk.Entry(field_frame, textvariable=var, state='readonly', width=50)
            entry.grid(row=0, column=1, sticky='ew', padx=(0, 5))
            
            # Botão para copiar
            btn_copy = ttk.Button(field_frame, text="Copiar", width=8,
                                command=lambda f=field: self.copiar_campo(f))
            btn_copy.grid(row=0, column=2, padx=(5, 0))
            
            self.field_vars[field] = var
        
        # Empacotar canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind para navegação com teclado
        self.root.bind('<Left>', lambda e: self.anterior())
        self.root.bind('<Right>', lambda e: self.proximo())
        self.root.bind('<Prior>', lambda e: self.anterior())  # Page Up
        self.root.bind('<Next>', lambda e: self.proximo())    # Page Down
        
        # Focar na janela para receber eventos de teclado
        self.root.focus_set()
    
    def update_display(self):
        """Atualiza a exibição com os dados da linha atual"""
        if self.current_index < 0 or self.current_index > self.max_index:
            return
        
        current_row = self.df.iloc[self.current_index]
        print(f"\n=== Atualizando display para índice {self.current_index} ===")
        
        # Atualizar cada campo
        for field in self.fields:
            print(f"Processando campo: {field}")
            
            # Verificar se é um campo especial que precisa ser gerado
            if field == 'Nome Abreviado':
                # Gerar nome abreviado a partir do campo Nome
                if 'Nome' in current_row:
                    nome_completo = current_row['Nome']
                    print(f"Gerando nome abreviado para: {nome_completo}")
                    formatted_value = self.abreviar_nome(nome_completo)
                    print(f"Resultado da abreviação: {formatted_value}")
                else:
                    formatted_value = "Campo Nome não encontrado"
                    print("Campo Nome não encontrado no DataFrame")
                
                # Importante: definir o valor na interface
                print(f"Definindo valor na interface para Nome Abreviado: '{formatted_value}'")
                self.field_vars[field].set(formatted_value)
            
            elif field == 'Telefone Sem 9':
                # Gerar telefone sem 9 a partir do campo Telefone
                if 'Telefone' in current_row:
                    telefone_original = current_row['Telefone']
                    print(f"Gerando telefone sem 9 para: {telefone_original}")
                    formatted_value = self.format_telefone(telefone_original, remover_9=True)
                    print(f"Resultado do telefone sem 9: {formatted_value}")
                else:
                    formatted_value = "Campo Telefone não encontrado"
                    print("Campo Telefone não encontrado no DataFrame")
                
                # Definir o valor na interface
                print(f"Definindo valor na interface para Telefone Sem 9: '{formatted_value}'")
                self.field_vars[field].set(formatted_value)
            
            elif field in current_row:
                value = current_row[field]
                
                # Verificar se é CPF
                if field == 'CPF':
                    formatted_value = self.format_cpf(value)
                # Verificar se é CEP
                elif field == 'Cep':
                    formatted_value = self.format_cep(value)
                # Verificar se é Telefone (campo original, remover apenas DDD)
                elif field == 'Telefone':
                    formatted_value = self.format_telefone(value, remover_9=False)
                # Verificar se é Órgão Expeditor
                elif field == 'Orgão Expeditor':
                    formatted_value = self.simplificar_orgao_expeditor(value)
                # Verificar se é um campo de data
                elif field in self.date_fields:
                    formatted_value = self.format_date(value)
                else:
                    # Para outros campos, converter para string preservando zeros à esquerda
                    if pd.isna(value):
                        formatted_value = ""
                    else:
                        formatted_value = str(value)
                
                print(f"Valor formatado para {field}: {formatted_value}")
                self.field_vars[field].set(formatted_value)
            else:
                formatted_value = "Campo não encontrado"
                print(f"Campo {field} não encontrado no DataFrame")
                self.field_vars[field].set(formatted_value)
        
        # Atualizar posição
        self.lbl_posicao.config(text=f"Registro {self.current_index + 1} de {len(self.df)}")
        
        # Atualizar estado dos botões
        self.btn_anterior.config(state='normal' if self.current_index > 0 else 'disabled')
        self.btn_proximo.config(state='normal' if self.current_index < self.max_index else 'disabled')
    
    def anterior(self):
        """Navegar para o registro anterior"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
    
    def proximo(self):
        """Navegar para o próximo registro"""
        if self.current_index < self.max_index:
            self.current_index += 1
            self.update_display()
    
    def ir_para_linha(self, event=None):
        """Navegar diretamente para uma linha específica"""
        try:
            linha_str = self.entry_linha.get().strip()
            if not linha_str:
                return
            
            linha = int(linha_str)
            
            # Converter para índice (linha - 1, pois mostramos linha 1 como primeiro registro)
            novo_index = linha - 1
            
            if 0 <= novo_index <= self.max_index:
                self.current_index = novo_index
                self.update_display()
                self.entry_linha.delete(0, tk.END)  # Limpar campo após navegar
                self.mostrar_feedback(f"Navegou para linha {linha}")
            else:
                self.mostrar_feedback(f"Linha {linha} não existe! Use entre 1 e {len(self.df)}")
                
        except ValueError:
            self.mostrar_feedback("Digite um número válido!")
        except Exception as e:
            self.mostrar_feedback(f"Erro: {str(e)}")
    
    def copiar_campo(self, field):
        """Copiar o valor de um campo específico para a área de transferência"""
        try:
            value = self.field_vars[field].get()
            if value and value != "Campo não encontrado":
                pyperclip.copy(value)
                # Feedback visual temporário
                self.mostrar_feedback(f"'{field}' copiado!")
            else:
                self.mostrar_feedback("Campo vazio ou não encontrado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao copiar: {str(e)}")
    
    def mostrar_feedback(self, mensagem):
        """Mostra uma mensagem de feedback temporária"""
        # Criar janela de feedback
        feedback = tk.Toplevel(self.root)
        feedback.title("")
        feedback.geometry("200x50")
        feedback.attributes('-topmost', True)
        feedback.overrideredirect(True)  # Remove decorações da janela
        
        # Centralizar na tela
        feedback.geometry(f"+{self.root.winfo_x() + 50}+{self.root.winfo_y() + 50}")
        
        # Label com a mensagem
        lbl = ttk.Label(feedback, text=mensagem, font=('Arial', 9))
        lbl.pack(expand=True)
        
        # Destruir após 1.5 segundos
        feedback.after(1500, feedback.destroy)
    
    def toggle_always_on_top(self):
        """Alternar se a janela fica sempre no topo"""
        self.root.attributes('-topmost', self.always_on_top.get())
    
    def run(self):
        """Executar a interface"""
        self.root.mainloop()

def main():
    try:
        # Ler o Excel com todos os campos como texto para preservar zeros à esquerda
        print("Carregando arquivo Excel...")
        df = pd.read_excel('minha_tabela(Dados).xlsx', dtype=str)
        
        if df.empty:
            messagebox.showerror("Erro", "O arquivo Excel está vazio!")
            return
        
        print(f"DataFrame carregado com {len(df)} registros")
        print(f"Colunas disponíveis: {list(df.columns)}")
        
        # Verificar se as colunas esperadas existem
        expected_fields = [
            'CPF', 'Nome', 'RG', 'Orgão Expeditor', 'Dat. Expedição',
            'Cep', 'E-Mail', 'Tip. Logradouro', 'Logradouro', 
            'Num. Endereço', 'Bairro', 'Telefone'
        ]
        
        missing_fields = [field for field in expected_fields if field not in df.columns]
        if missing_fields:
            print(f"Atenção: Campos não encontrados no arquivo: {missing_fields}")
            print("O visualizador ainda funcionará, mas esses campos aparecerão como 'Campo não encontrado'")
        
        # Verificar alguns nomes para debug
        if 'Nome' in df.columns:
            print("\n=== Teste de alguns nomes ===")
            for i in range(min(3, len(df))):
                nome = df.iloc[i]['Nome']
                print(f"Registro {i}: {nome} (tipo: {type(nome)})")
        
        # Verificar alguns telefones para debug
        if 'Telefone' in df.columns:
            print("\n=== Teste de alguns telefones ===")
            for i in range(min(3, len(df))):
                telefone = df.iloc[i]['Telefone']
                print(f"Registro {i}: {telefone} (tipo: {type(telefone)})")
        
        # Verificar alguns CEPs para debug
        if 'Cep' in df.columns:
            print("\n=== Teste de alguns CEPs ===")
            for i in range(min(3, len(df))):
                cep = df.iloc[i]['Cep']
                print(f"Registro {i}: {cep} (tipo: {type(cep)})")
        
        # Criar e executar o visualizador
        viewer = DataFrameViewer(df)
        viewer.run()
        
    except FileNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'minha_tabela(Dados).xlsx' não encontrado!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
        print(f"Erro detalhado: {e}")

if __name__ == '__main__':
    main()