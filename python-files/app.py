import webview
import pandas as pd
import os
import json
import csv
from datetime import datetime
import re
from io import StringIO

# --- Configurações Iniciais ---
# Arquivos de configuração e lista de relatórios
CONFIG_FILE = 'config.json'
REPORTS_LIST_FILE = 'relatorios_lista.csv'

# Define o diretório padrão como a pasta 'Documentos'
DOCUMENTS_PATH = os.path.join(os.path.expanduser('~'), 'Documents') 

DEFAULT_CONFIG = {
    'base_dir': DOCUMENTS_PATH,
    'reports_folder_name': 'OrganizadorDeRelatorios'
}

# BASE_DIR agora é usado apenas para a lógica de desenvolvimento e localização simples
# Para um arquivo único, __file__ aponta para ele mesmo.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Funções de Utilitário ---

def load_config():
    """Carrega ou cria o arquivo de configuração."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Garante que 'base_dir' existe e é válido, caso contrário, usa o padrão.
                if 'base_dir' not in config or not os.path.exists(config['base_dir']):
                     config['base_dir'] = DOCUMENTS_PATH
                return config
        except json.JSONDecodeError:
            print(f"Erro ao ler {CONFIG_FILE}. Usando configurações padrão.")
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config_data):
    """Salva a configuração no arquivo JSON."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

def get_report_dir(config):
    """Retorna o caminho completo da pasta de relatórios."""
    return os.path.join(config['base_dir'], config['reports_folder_name'])

# Inicializa/Carrega as configurações
CONFIG = load_config()
REPORT_DIR = get_report_dir(CONFIG) 
# Cria a pasta de relatórios se não existir
os.makedirs(REPORT_DIR, exist_ok=True) 

# Inicializa o CSV de relatórios se não existir
if not os.path.exists(REPORTS_LIST_FILE):
    with open(REPORTS_LIST_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['nome_arquivo', 'nome_exibicao', 'data_criacao'])

# --- API do pywebview ---

class Api:
    def __init__(self):
        self.config = CONFIG

    def formatar_cpf(self, cpf):
        """Formata uma string de CPF (apenas dígitos) para o padrão 000.000.000-00."""
        # Garante 11 dígitos, preenchendo com zeros à esquerda
        cpf_limpo = re.sub(r'\D', '', str(cpf).zfill(11))
        if len(cpf_limpo) == 11:
            return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return cpf_limpo 
    
    def formatar_nb(self, nb):
        """Formata uma string de NB (apenas dígitos)."""
        nb_limpo = re.sub(r'\D', '', str(nb))
        return nb_limpo

    # --- Dashboard View ---

    def get_dados_dashboard(self):
        """Retorna a lista de relatórios e configurações atuais, ordenados por nome."""
        try:
            df = pd.read_csv(REPORTS_LIST_FILE, encoding='utf-8')
            # Garante que a lista de relatórios está ordenada no dashboard
            df = df.sort_values(by='nome_exibicao', ascending=True) 
            relatorios = df.to_dict('records')
        except pd.errors.EmptyDataError:
            relatorios = []
        except Exception as e:
            print(f"Erro ao ler relatorios_lista.csv: {e}")
            relatorios = []

        current_report_dir = get_report_dir(self.config) 

        return {
            'relatorios': relatorios,
            'config': {
                'base_dir': self.config['base_dir'],
                'reports_folder_name': self.config['reports_folder_name'],
                'full_path': current_report_dir
            }
        }

    def criar_novo_relatorio(self, dados):
        """Cria um novo arquivo Excel com nome IGUAL ao nome de exibição."""
        # Nota: REPORT_DIR é uma variável global
        global REPORT_DIR 
        
        nome_exibicao = dados.get('nome').strip()
        now = datetime.now()
        data_str_display = now.strftime('%d/%m/%Y %H:%M')

        if not nome_exibicao:
            return {'success': False, 'message': 'Nome do Relatório é obrigatório.'}

        # Nome do arquivo é o nome de exibição (limpo de caracteres não permitidos em FS)
        nome_arquivo_base = re.sub(r'[\\/:*?"<>|]', '', nome_exibicao).strip() 
        if not nome_arquivo_base:
             return {'success': False, 'message': 'Nome do relatório inválido após limpeza.'}
       
        # Garante a extensão
        nome_arquivo = f"{nome_arquivo_base}.xlsx"
        caminho_arquivo = os.path.join(REPORT_DIR, nome_arquivo)
        
        # Se o arquivo já existe, impede a criação
        if os.path.exists(caminho_arquivo):
             return {'success': False, 'message': f'Um relatório com o nome "{nome_exibicao}" já existe. Por favor, escolha outro nome ou exclua o existente.'}


        try:
            # 1. Cria o arquivo Excel (apenas com cabeçalhos)
            df_novo = pd.DataFrame(columns=['Nome', 'CPF', 'NB'])
            df_novo.to_excel(caminho_arquivo, index=False)

            # 2. Registra no CSV de metadados
            try:
                # Tenta ler o CSV, se existir e não estiver vazio
                df_meta = pd.read_csv(REPORTS_LIST_FILE, encoding='utf-8')
                
                novo_registro = {
                    'nome_arquivo': nome_arquivo,
                    'nome_exibicao': nome_exibicao,
                    'data_criacao': data_str_display
                }
                # Adiciona o novo registro
                df_meta = pd.concat([df_meta, pd.DataFrame([novo_registro])], ignore_index=True)
                
                df_meta.to_csv(REPORTS_LIST_FILE, index=False, encoding='utf-8')

            except pd.errors.EmptyDataError:
                # Se o CSV estiver vazio, cria o DataFrame com o novo registro e salva
                novo_registro = {
                    'nome_arquivo': nome_arquivo,
                    'nome_exibicao': nome_exibicao,
                    'data_criacao': data_str_display
                }
                df_meta = pd.DataFrame([novo_registro], columns=['nome_arquivo', 'nome_exibicao', 'data_criacao'])
                df_meta.to_csv(REPORTS_LIST_FILE, index=False, encoding='utf-8')


            return {'success': True, 'message': f'Relatório "{nome_exibicao}" criado com sucesso ({data_str_display}).', 'data': {'nome_arquivo': nome_arquivo, 'nome_exibicao': nome_exibicao}}

        except Exception as e:
            print(f"Erro ao criar relatório: {e}")
            return {'success': False, 'message': f'Erro interno ao criar/salvar o arquivo: {e}'}

    # --- Report Manager View ---

    def salvar_cliente(self, dados):
        """Sempre adiciona uma nova linha, ordena por nome e salva com CPF formatado no Excel."""
        # Nota: REPORT_DIR é uma variável global
        global REPORT_DIR 
        
        nome_arquivo = dados.get('nome_arquivo')
        nome = dados.get('nome')
        cpf = dados.get('cpf')
        nb = dados.get('nb')

        if not nome_arquivo or not nome or not cpf:
            return {'success': False, 'message': 'Nome do Arquivo, Nome e CPF são obrigatórios.'}

        caminho_arquivo = os.path.join(REPORT_DIR, nome_arquivo)

        # Padroniza e limpa o CPF/NB
        cpf_limpo = str(cpf).strip().zfill(11) 
        nb_str = self.formatar_nb(nb)
        
        # Formata o CPF para ser exibido no Excel
        cpf_formatado_excel = self.formatar_cpf(cpf_limpo)
       
        nova_linha_dados = pd.DataFrame([{'Nome': nome, 'CPF': cpf_formatado_excel, 'NB': nb_str}])

        try:
            # 1. Carrega o relatório (ou cria se não existir)
            if os.path.exists(caminho_arquivo):
                df_relatorio = pd.read_excel(caminho_arquivo)
                
                # Garante que as colunas existem
                if not all(col in df_relatorio.columns for col in ['Nome', 'CPF', 'NB']):
                    df_relatorio = pd.DataFrame(columns=['Nome', 'CPF', 'NB'])
            else:
                 df_relatorio = pd.DataFrame(columns=['Nome', 'CPF', 'NB'])
            
            # 2. ANEXA A NOVA LINHA
            df_relatorio = pd.concat([df_relatorio, nova_linha_dados], ignore_index=True)
            
            # CRÍTICO: 3. GARANTE A ORDENAÇÃO ALFABÉTICA antes de salvar no Excel
            if 'Nome' in df_relatorio.columns:
                # Converte para string e ignora o caso (key=...)
                df_relatorio = df_relatorio.sort_values(by='Nome', key=lambda x: x.astype(str).str.lower(), ascending=True, ignore_index=True)
          
            # 4. Salva de volta no Excel
            df_relatorio.to_excel(caminho_arquivo, index=False)

            dados_cliente = {
                'nome': nome,
                'cpf': cpf_limpo, 
                'cpf_formatado': cpf_formatado_excel, 
                'nb': nb_str
            }

            return {'success': True, 'message': f'Cliente "{nome}" adicionado com sucesso e lista reordenada.', 'data': dados_cliente}

        except Exception as e:
            print(f"Erro ao salvar cliente: {e}")
            return {'success': False, 'message': f'Erro interno ao salvar cliente: {e}'}

    def carregar_clientes(self, nome_arquivo):
        """Carrega e retorna a lista de clientes de um arquivo Excel (ordenada e formatada para preview e busca)."""
        # Nota: REPORT_DIR é uma variável global
        global REPORT_DIR 
        
        if not nome_arquivo:
            return {'success': False, 'message': 'Nome do arquivo não fornecido.'}

        caminho_arquivo = os.path.join(REPORT_DIR, nome_arquivo)

        try:
            if os.path.exists(caminho_arquivo):
                df_relatorio = pd.read_excel(caminho_arquivo)
                
                if df_relatorio.empty:
                    return {'success': True, 'data': [], 'message': 'O relatório está vazio.'}

                # CRÍTICO: Garante ordenação alfabética (embora já deva estar no arquivo)
                if 'Nome' in df_relatorio.columns:
                    # Converte para string e ignora o caso (key=...)
                    df_relatorio = df_relatorio.sort_values(by='Nome', key=lambda x: x.astype(str).str.lower(), ascending=True, ignore_index=True)
                
                # Tratamento e formatação de colunas para o Preview
                df_relatorio['Nome'] = df_relatorio['Nome'].fillna('')
                
                # O CPF é carregado formatado (ex: 123.456.789-01) ou como número
                # Para o preview, queremos a versão formatada
                df_relatorio['CPF_Formatado'] = df_relatorio['CPF'].astype(str).str.strip().fillna('')
                
                # E o CPF limpo para a busca JS
                df_relatorio['CPF_Limpo'] = df_relatorio['CPF_Formatado'].str.replace(r'[^\d]', '', regex=True)
                
                # Limpa o 'nan' do NB
                df_relatorio['NB_Formatado'] = df_relatorio['NB'].astype(str).str.strip().fillna('').replace('nan', '')

                # Renomeia o 'CPF_Limpo' para 'CPF' para uso no JS
                clientes = df_relatorio[['Nome', 'CPF_Limpo', 'CPF_Formatado', 'NB_Formatado']].rename(columns={'CPF_Limpo': 'CPF'}).to_dict('records')
                
                return {'success': True, 'data': clientes}
            else:
                return {'success': False, 'message': 'Arquivo de relatório não encontrado.'}

        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
            return {'success': False, 'message': f'Erro interno ao carregar clientes (Verifique se o arquivo Excel está corrompido ou aberto): {e}'}

    # --- Configurações View ---
    
    def selecionar_pasta_api(self):
        """Abre o diálogo nativo para seleção de pasta."""
        try:
            # Obtém a janela principal (a primeira)
            result = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
            if result and len(result) > 0:
                return {'success': True, 'path': result[0]}
            return {'success': False, 'message': 'Nenhuma pasta selecionada.'}
        except Exception as e:
            print(f"Erro ao abrir diálogo de pasta: {e}")
            return {'success': False, 'message': f'Erro ao abrir diálogo: {e}'}


    def salvar_configuracoes_api(self, dados):
        """Salva o Diretório Base e o Nome da Pasta de Relatórios, renomeando-a se necessário."""
        global REPORT_DIR # Permite alterar a variável global
        
        old_config = load_config() 
       
        new_base_dir = dados.get('base_dir')
        new_folder_name = dados.get('reports_folder_name')

        if not new_base_dir or not new_folder_name:
            return {'success': False, 'message': 'Diretório Base e Nome da Pasta são obrigatórios.'}
            
        old_full_path = os.path.join(old_config['base_dir'], old_config['reports_folder_name'])
        new_full_path = os.path.join(new_base_dir, new_folder_name)
    
        # Se os caminhos forem diferentes E a pasta antiga existir, tenta renomear
        if new_full_path != old_full_path and os.path.exists(old_full_path):
            try:
                os.rename(old_full_path, new_full_path)
                REPORT_DIR = new_full_path 
            except FileNotFoundError:
                # Se a pasta antiga não existir, apenas garante que a nova exista
                os.makedirs(new_full_path, exist_ok=True)
            except PermissionError:
                return {'success': False, 'message': 'Erro de Permissão: Não foi possível renomear a pasta. Tente fechar o Explorador de Arquivos.'}
            except Exception as e:
                return {'success': False, 'message': f'Erro ao renomear a pasta: {e}'}
        
        # Se a pasta nova não existir (e não houve renomeação), cria
        elif not os.path.exists(new_full_path):
            os.makedirs(new_full_path, exist_ok=True)
            
        # Atualiza a configuração in-memory
        self.config['base_dir'] = new_base_dir
        self.config['reports_folder_name'] = new_folder_name

        try:
            # Salva no arquivo JSON
            save_config(self.config)
            # Atualiza o caminho global para o caso de ter mudado
            REPORT_DIR = get_report_dir(self.config)

            return {'success': True, 'message': 'Configurações salvas e pasta atualizada com sucesso.', 'config': self.config}
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return {'success': False, 'message': f'Erro ao salvar configurações: {e}'}

# --- HTML/CSS/JS (Conteúdo da Interface) ---

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Organizador de Relatórios</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
    
    <style>
        /* Reset e Base */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'SF Pro Text', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }

        :root {
            --color-primary: #007aff; 
            --color-secondary: #1d1d1f;
            --color-bg-light: #f5f5f7;
            --color-bg-sidebar: #ffffff; 
            --color-border: #e8e8e8;
            --color-shadow-light: rgba(0, 0, 0, 0.05);
            --color-success: #34c759;
            --color-error: #ff3b30;
            --color-text-subtle: #8e8e93;
        }

        body {
            background-color: var(--color-bg-light);
            color: var(--color-secondary);
            overflow: hidden;
            font-size: 15px;
        }

        /* Layout Principal */
        .container {
            display: flex;
            height: 100vh;
        }

        /* Loading Screen */
        .loading-screen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background-color: var(--color-bg-light);
            color: var(--color-secondary);
            font-size: 1.1em;
            font-weight: 500;
            z-index: 100;
        }
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-top: 4px solid var(--color-primary);
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin-bottom: 15px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }


        /* Sidebar */
        .sidebar {
            width: 250px;
            background-color: var(--color-bg-sidebar);
            color: var(--color-secondary);
            padding: 20px;
            box-shadow: 1px 0 0 var(--color-border);
            flex-shrink: 0;
        }

        .logo {
            font-size: 1.2em;
            font-weight: 700;
            color: var(--color-secondary);
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--color-border);
            letter-spacing: 0.5px;
            text-align: center;
        }

        .sidebar nav button {
            display: flex;
            align-items: center;
            width: 100%;
            padding: 10px 15px;
            margin-bottom: 5px;
            background: none;
            border: none;
            color: var(--color-secondary);
            text-align: left;
            font-size: 0.95em;
            cursor: pointer;
            border-radius: 8px;
            transition: background-color 0.15s, color 0.15s;
            font-weight: 500;
        }

        .sidebar nav button i.fas {
            font-size: 1.1em;
            margin-right: 12px;
        }

        .sidebar nav button:hover:not(.active) {
            background-color: #f0f0f5;
        }

        .sidebar nav button.active {
            background-color: var(--color-primary);
            color: white;
            font-weight: 600;
        }

        /* Conteúdo Principal */
        .content {
            flex-grow: 1;
            padding: 30px;
            overflow-y: auto;
            display: none;
        }

        .section-title {
            color: var(--color-secondary);
            margin-bottom: 30px;
            font-size: 2em;
            font-weight: 700;
        }

        .subsection-title {
            color: var(--color-secondary);
            margin-top: 20px;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        /* Cartões */
        .card {
            background-color: var(--color-bg-sidebar);
            padding: 25px;
            border-radius: 12px;
            border: 1px solid var(--color-border);
            box-shadow: 0 4px 10px var(--color-shadow-light);
        }

        /* Botões */
        button {
            padding: 10px 18px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 600;
            margin-top: 15px;
            transition: background-color 0.2s, opacity 0.2s;
        }

        .btn-primary {
            background-color: var(--color-primary);
            color: white;
        }

        .btn-primary:hover {
            background-color: #0071e3;
        }

        .btn-secondary {
            background-color: #f0f0f5;
            color: var(--color-secondary);
            border: 1px solid #ddd;
        }
        .btn-secondary:hover {
            background-color: #e0e0e0;
        }

        .btn-success {
            background-color: var(--color-success);
            color: white;
        }
        .btn-success:hover {
            background-color: #24a144;
        }

        .btn-sm {
            padding: 6px 12px;
            font-size: 0.85em;
            margin-top: 0;
            font-weight: 500;
        }

        button i.fas {
            margin-right: 8px;
        }

        /* Formulários e Inputs */
        label {
            display: block;
            margin-top: 18px;
            margin-bottom: 5px;
            font-weight: 600;
            color: var(--color-secondary);
            font-size: 0.9em;
        }

        input[type="text"],
        input[type="date"],
        select {
            width: 100%;
            padding: 12px;
            margin-bottom: 10px;
            border: 1px solid var(--color-border);
            border-radius: 8px;
            font-size: 1em;
            background-color: #ffffff;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        input:focus, select:focus {
            border-color: var(--color-primary);
            box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15);
            outline: none;
        }

        .form-help {
            font-size: 0.85em;
            color: var(--color-text-subtle);
            margin-bottom: 10px;
        }

        /* Dashboard Layout */
        .dashboard-layout {
            display: flex;
            gap: 25px;
        }

        .relatorios-existentes {
            flex: 3;
            padding: 0;
        }

        .criar-rapido-form {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .relatorios-existentes h3, .criar-rapido-form h3 {
            padding: 25px;
            font-size: 1.1em;
            font-weight: 600;
            color: var(--color-secondary);
            border-bottom: 1px solid var(--color-border);
            margin-top: 0;
        }

        /* Tabelas */
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: var(--color-bg-sidebar);
        }

        th, td {
            padding: 15px 25px;
            text-align: left;
            border-bottom: 1px solid #f0f0f0;
        }

        th {
            background-color: #fafafa;
            color: var(--color-text-subtle);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
        }

        tr:hover:not(:first-child) {
            background-color: #fcfcfc;
        }

        .table-name { font-weight: 600; }
        .table-file { font-size: 0.9em; color: var(--color-text-subtle); }

        /* Feedback e Info Path */
        .feedback {
            margin-top: 15px;
            padding: 10px 15px;
            border-radius: 8px;
            font-weight: 500;
            font-size: 0.9em;
        }

        .feedback.success {
            background-color: #e6ffed;
            color: var(--color-success);
            border: 1px solid #b7e4c7;
        }

        .feedback.error {
            background-color: #fff0f0;
            color: var(--color-error);
            border: 1px solid #ffb3b3;
        }

        .info-path {
            margin: 25px 0 0 0; 
            padding-top: 15px;
            border-top: 1px solid var(--color-border);
            font-size: 0.85em;
            color: var(--color-text-subtle);
            word-break: break-all;
        }

        .info-path span {
            font-weight: 500;
            color: var(--color-secondary);
        }

        .info-path i.fas {
            margin-right: 8px;
        }

        /* Report Manager Tabs */
        .tabs-container {
            margin-top: 25px;
        }

        .tabs {
            display: flex;
            border-bottom: 1px solid var(--color-border);
        }

        .tab-button {
            background: #f0f0f5;
            color: var(--color-secondary);
            padding: 10px 20px;
            border: 1px solid var(--color-border);
            border-bottom: none;
            cursor: pointer;
            margin-right: 5px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-top: 0;
        }

        .tab-button.active {
            background-color: var(--color-bg-sidebar);
            border-color: var(--color-border);
            border-bottom: 1px solid var(--color-bg-sidebar);
            font-weight: 600;
            z-index: 10;
        }

        .tab-content {
            padding: 25px;
            border: 1px solid var(--color-border);
            border-radius: 0 12px 12px 12px;
            background-color: var(--color-bg-sidebar);
            min-height: 250px;
            box-shadow: 0 4px 8px var(--color-shadow-light);
            display: none;
        }
        .tab-content.active {
            display: block;
        }

        /* Campo de Busca Rápida */
        .report-selector-container {
            margin-bottom: 25px;
        }
        .report-selector-container label {
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 1em;
            font-weight: 700;
        }
        .report-selector-container label i.fas {
            margin-right: 10px;
        }


        .search-container {
            position: relative;
            margin-bottom: 20px;
        }

        .search-container input {
            padding-left: 40px; 
        }

        .search-container .fas.fa-search {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--color-text-subtle);
            font-size: 0.9em;
        }


        /* Configurações */
        .input-with-button {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .input-with-button input {
            flex-grow: 1;
        }

        .input-with-button button {
            flex-shrink: 0;
            width: auto;
            margin-top: 0;
        }
        
        .tab-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    </style>
</head>
<body>

    <div class="container">
        <aside class="sidebar">
            <h1 class="logo">Organizador de Relatórios</h1>
            <nav>
                <button onclick="navigateTo('dashboard-view')" id="nav-dashboard" class="active"><i class="fas fa-chart-line"></i> Dashboard</button>
                <button onclick="navigateTo('report-manager-view')" id="nav-reports"><i class="fas fa-clipboard-list"></i> Gerenciar</button>
                <button onclick="navigateTo('settings-view')" id="nav-settings"><i class="fas fa-cogs"></i> Configurações</button>
            </nav>
        </aside>

        <main class="content">
            <div id="loading-screen" class="loading-screen">
                <div class="spinner"></div>
                Carregando a aplicação...
            </div>

            <section id="dashboard-view" class="view" style="display: none;">
                <h2 class="section-title">Dashboard</h2>
                <div class="dashboard-layout">
                    <div class="card relatorios-existentes">
                        <h3>Relatórios Criados</h3>
                        <table id="relatorios-table">
                            <thead>
                                <tr>
                                    <th>Nome</th>
                                    <th>Arquivo</th>
                                    <th>Criado em</th>
                                    <th>Ação</th>
                                </tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>

                    <div class="card criar-rapido-form">
                        <h3>Criar Novo Relatório</h3>
                        <form id="form-criar-relatorio">
                            <p class="form-help">O nome do arquivo Excel será **EXATAMENTE** o nome que você digitar aqui.</p>
                            <label for="relatorio-nome">Nome do Relatório:</label>
                            <input type="text" id="relatorio-nome" required placeholder="Ex: Aposentadorias Setembro">
                            
                            <button type="submit" class="btn-primary"><i class="fas fa-file-excel"></i> Criar Relatório</button>
                        </form>
                        <p id="dashboard-feedback" class="feedback"></p>
                    </div>
                </div>
            </section>

            <section id="report-manager-view" class="view" style="display: none;">
                <h2 class="section-title">Gerenciador de Clientes</h2>
                <div class="report-selector-container card">
                    <label for="report-select"><i class="fas fa-folder-open"></i> Selecione o Relatório para Gerenciar:</label>
                    <select id="report-select" onchange="loadReportData(this.value)">
                        <option value="">-- Selecione um Relatório --</option>
                    </select>
                </div>

                <div class="tabs-container">
                    <div class="tabs">
                        <button class="tab-button active" onclick="showTab('add-client-tab', this)"><i class="fas fa-user-plus"></i> Adicionar Cliente</button>
                        <button class="tab-button" onclick="showTab('preview-tab', this)" disabled><i class="fas fa-eye"></i> Preview</button>
                    </div>

                    <div id="add-client-tab" class="tab-content active">
                        <form id="form-salvar-cliente">
                            <p class="form-help">Cada submissão adiciona uma **nova linha**. Os clientes serão ordenados automaticamente no Excel.</p>
                            <label for="cliente-nome">Nome do Cliente:</label>
                            <input type="text" id="cliente-nome" required placeholder="Nome Completo">

                            <label for="cliente-cpf">CPF (somente 11 números):</label>
                            <input type="text" id="cliente-cpf" pattern="[0-9]{11}" maxlength="11" required placeholder="Ex: 12345678901">

                            <label for="cliente-nb">NB (Número de Benefício):</label>
                            <input type="text" id="cliente-nb" placeholder="Opcional. Ex: 1234567890">

                            <button type="submit" class="btn-success"><i class="fas fa-save"></i> Adicionar Cliente</button>
                        </form>
                        <p id="manager-feedback" class="feedback"></p>
                    </div>

                    <div id="preview-tab" class="tab-content">
                        <h3 class="subsection-title">Clientes em <span id="preview-report-name">--</span></h3>
                        
                        <div class="search-container">
                            <i class="fas fa-search"></i>
                            <input type="text" id="client-search" placeholder="Buscar por Nome ou CPF..." onkeyup="filterClients()">
                        </div>
                        
                        <table id="clientes-preview-table">
                            <thead>
                                <tr>
                                    <th>Nome</th>
                                    <th>CPF</th>
                                    <th>NB</th>
                                </tr>
                            </thead>
                            <tbody id="clientes-tbody">
                                <tr><td colspan="3">Selecione um relatório.</td></tr>
                            </tbody>
                        </table>
                        <p id="preview-feedback" class="feedback"></p>
                    </div>
                </div>
            </section>

            <section id="settings-view" class="view" style="display: none;">
                <h2 class="section-title">Configurações</h2>
                <div class="card">
                    <form id="form-configuracoes">
                        <p class="form-help">O diretório base é onde a pasta "OrganizadorDeRelatorios" será criada. Padrão: Pasta Documentos.</p>
                        <label for="base-dir">Diretório Base:</label>
                        <div class="input-with-button">
                            <input type="text" id="base-dir" readonly required>
                            <button type="button" class="btn-secondary" onclick="selectFolder()"><i class="fas fa-folder"></i> Mudar Pasta</button>
                        </div>

                        <label for="reports-folder-name">Nome da Subpasta de Relatórios:</label>
                        <input type="text" id="reports-folder-name" required>

                        <button type="submit" class="btn-primary"><i class="fas fa-save"></i> Salvar Configurações</button>
                    </form>
                    <p id="settings-feedback" class="feedback"></p>
                    <p id="current-full-path" class="info-path"><i class="fas fa-info-circle"></i> Caminho Completo Atual: <span></span></p>
                </div>
            </section>
        </main>
    </div>

    <script>
        let reportsList = [];
        let currentReportFileName = '';
        let currentClientsData = []; 

        function navigateTo(viewId) {
            document.querySelectorAll('.view').forEach(view => view.style.display = 'none');
            document.getElementById(viewId).style.display = 'block';

            document.querySelectorAll('.sidebar button').forEach(button => button.classList.remove('active'));
            document.getElementById(`nav-${viewId.replace('-view', '')}`).classList.add('active');

            if (viewId === 'dashboard-view') {
                loadDashboardData();
            } else if (viewId === 'settings-view') {
                loadSettingsData();
            } else if (viewId === 'report-manager-view') {
                loadReportSelect();
                document.getElementById('report-select').value = "";
                currentReportFileName = '';
                currentClientsData = []; 
                showTab('add-client-tab', document.querySelectorAll('.tab-button')[0]);
                document.querySelectorAll('.tab-button')[1].disabled = true;
                document.querySelector('#clientes-tbody').innerHTML = '<tr><td colspan="3">Selecione um relatório.</td></tr>';
                document.getElementById('preview-report-name').textContent = '--';
                document.getElementById('client-search').value = ''; 
            }
        }

        function showTab(tabId, button) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');

            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            if (tabId === 'preview-tab' && currentReportFileName) {
                loadReportPreview(currentReportFileName);
            }
        }

        function setFeedback(elementId, message, isSuccess = true) {
            const el = document.getElementById(elementId);
            el.textContent = message;
            el.className = `feedback ${isSuccess ? 'success' : 'error'}`;
            setTimeout(() => el.textContent = '', 5000);
        }

        // --- Lógica do Filtro Rápido (CORRIGIDA) ---

        function filterClients() {
            const searchTerm = document.getElementById('client-search').value.toLowerCase().trim();
            const tbody = document.getElementById('clientes-tbody');
            // Ignora linhas de "Nenhum cliente cadastrado"
            const rows = tbody.querySelectorAll('tr:not(.no-data-row)'); 
            let found = false;
            
            // Remove a linha de "Nenhum resultado" temporariamente
            let noResultRow = tbody.querySelector('.no-result-row');
            if (noResultRow) {
                noResultRow.remove();
                noResultRow = null; 
            }
            
            // 1. Prepara os termos de busca
            // cleanedSearchTerm será "" se for apenas texto (ex: "ju"), ou o número (ex: "123")
            const cleanedSearchTerm = searchTerm.replace(/\D/g, ''); 

            rows.forEach(row => {
                // As células são 0: Nome, 1: CPF, 2: NB
                const nameCell = row.cells[0]?.textContent.toLowerCase() || '';
                
                // 2. Verifica a correspondência por NOME
                const matchesName = nameCell.includes(searchTerm);

                // 3. Verifica a correspondência por CPF (CRÍTICO: SÓ checa se o termo de busca tiver dígitos)
                let matchesCpf = false;
                if (cleanedSearchTerm.length > 0) {
                    // Pega o CPF da célula e remove a formatação
                    const cpfCellClean = row.cells[1]?.textContent.replace(/\D/g, '') || ''; 
                    matchesCpf = cpfCellClean.includes(cleanedSearchTerm);
                }
                
                // 4. A linha corresponde se o nome OU o CPF corresponder
                const isMatch = matchesName || matchesCpf;
                
                // Oculta ou mostra a linha
                row.style.display = isMatch ? '' : 'none';
                
                if (isMatch) {
                    found = true;
                }
            });

            // Se a busca não for vazia e nenhum resultado foi encontrado, exibe a mensagem
            if (searchTerm !== '' && !found) {
                noResultRow = document.createElement('tr');
                noResultRow.classList.add('no-result-row');
                noResultRow.innerHTML = '<td colspan="3">Nenhum cliente encontrado.</td>';
                tbody.appendChild(noResultRow);
            }
        }


        // --- Funções de Carregamento de Dados ---

        async function loadDashboardData() {
            try {
                const result = await pywebview.api.get_dados_dashboard();
                reportsList = result.relatorios;

                const tbody = document.querySelector('#relatorios-table tbody');
                tbody.innerHTML = '';
                if (reportsList.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="4">Nenhum relatório encontrado.</td></tr>';
                } else {
                    reportsList.forEach(report => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td class="table-name">${report.nome_exibicao}</td>
                            <td class="table-file">${report.nome_arquivo}</td>
                            <td>${report.data_criacao}</td>
                            <td><button class="btn-sm btn-secondary" onclick="navigateToReportManager('${report.nome_arquivo}')"><i class="fas fa-edit"></i> Gerenciar</button></td>
                        `;
                        tbody.appendChild(tr);
                    });
                }
            } catch (error) {
                setFeedback('dashboard-feedback', 'Erro ao carregar dados do Dashboard.', false);
                console.error('Erro get_dados_dashboard:', error);
            }
        }

        function navigateToReportManager(fileName) {
            navigateTo('report-manager-view');
            // Pequeno atraso para garantir que o select já foi populado
            setTimeout(() => {
                const selectEl = document.getElementById('report-select');
                selectEl.value = fileName;
                loadReportData(fileName);
            }, 200);
        }

        async function loadReportSelect() {
             const result = await pywebview.api.get_dados_dashboard();
             reportsList = result.relatorios;

             const select = document.getElementById('report-select');
             select.innerHTML = '<option value="">-- Selecione um Relatório --</option>';
             reportsList.forEach(report => {
                 const option = document.createElement('option');
                 option.value = report.nome_arquivo;
                 option.textContent = report.nome_exibicao;
                 select.appendChild(option);
             });
        }

        function loadReportData(fileName) {
            currentReportFileName = fileName;
            const tabButtons = document.querySelectorAll('.tab-button');

            if (fileName) {
                // Habilita as tabs e carrega o nome do relatório
                tabButtons.forEach(btn => btn.disabled = false);
                const report = reportsList.find(r => r.nome_arquivo === fileName);
                document.getElementById('preview-report-name').textContent = report ? `: ${report.nome_exibicao}` : '';
                
                // Se o preview estiver ativo, carrega a lista de clientes
                if (document.getElementById('preview-tab').classList.contains('active')) {
                    loadReportPreview(fileName);
                }
            } else {
                // Desabilita as tabs
                tabButtons.forEach(btn => btn.disabled = true);
                document.querySelector('#clientes-tbody').innerHTML = '<tr><td colspan="3">Selecione um relatório.</td></tr>';
                document.getElementById('preview-report-name').textContent = '--';
                currentReportFileName = '';
                currentClientsData = [];
                document.getElementById('client-search').value = '';
            }
        }

        async function loadReportPreview(fileName) {
            document.getElementById('preview-feedback').textContent = 'Carregando clientes...';
            try {
                const result = await pywebview.api.carregar_clientes(fileName);
                const tbody = document.getElementById('clientes-tbody');
                tbody.innerHTML = '';
                document.getElementById('preview-feedback').textContent = '';
                
                if (result.success && result.data.length > 0) {
                    currentClientsData = result.data;
                    currentClientsData.forEach(cliente => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>${cliente.Nome}</td>
                            <td>${cliente.CPF_Formatado}</td>
                            <td>${cliente.NB_Formatado || '-'}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                    // Aplica o filtro existente (se o usuário já digitou algo)
                    filterClients();
                } else {
                    currentClientsData = [];
                    const message = result.message || 'Nenhum cliente cadastrado neste relatório.';
                    const tr = document.createElement('tr');
                    tr.classList.add('no-data-row'); 
                    tr.innerHTML = `<td colspan="3">${message}</td>`;
                    tbody.appendChild(tr);
                    if (!result.success) setFeedback('preview-feedback', result.message, false);
                }

            } catch (error) {
                setFeedback('preview-feedback', 'Erro ao carregar preview do relatório. Verifique o console.', false);
                console.error('Erro carregar_clientes:', error);
            }
        }

        async function loadSettingsData() {
            try {
                const result = await pywebview.api.get_dados_dashboard();
                const config = result.config;

                document.getElementById('base-dir').value = config.base_dir;
                document.getElementById('reports-folder-name').value = config.reports_folder_name;
                document.querySelector('#current-full-path span').textContent = config.full_path;
            } catch (error) {
                setFeedback('settings-feedback', 'Erro ao carregar configurações.', false);
                console.error('Erro ao carregar configurações:', error);
            }
        }

        // --- Funções de Submissão de Formulário ---

        // 1. Criação Rápida de Relatório
        document.getElementById('form-criar-relatorio').addEventListener('submit', async (e) => {
            e.preventDefault();
            const nome = document.getElementById('relatorio-nome').value.trim();
            
            const result = await pywebview.api.criar_novo_relatorio({ nome });

            if (result.success) {
                setFeedback('dashboard-feedback', result.message, true);
                document.getElementById('form-criar-relatorio').reset();
                loadDashboardData();
                loadReportSelect(); // Atualiza o select do Gerenciador
            } else {
                setFeedback('dashboard-feedback', result.message, false);
            }
        });
        
        // 2. Salvar Cliente 
        document.getElementById('form-salvar-cliente').addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!currentReportFileName) {
                setFeedback('manager-feedback', 'Selecione um relatório para adicionar um cliente.', false);
                return;
            }

            const nome = document.getElementById('cliente-nome').value.trim();
            const cpf = document.getElementById('cliente-cpf').value.trim();
            const nb = document.getElementById('cliente-nb').value.trim();

            if (cpf.length !== 11 || isNaN(cpf)) {
                setFeedback('manager-feedback', 'O CPF deve ter exatamente 11 dígitos numéricos.', false);
                return;
            }

            const dados = {
                nome_arquivo: currentReportFileName,
                nome,
                cpf,
                nb
            };

            const result = await pywebview.api.salvar_cliente(dados);
            if (result.success) {
                setFeedback('manager-feedback', result.message, true);
                document.getElementById('form-salvar-cliente').reset();
                // Atualiza o preview se a aba estiver ativa
                if (document.getElementById('preview-tab').classList.contains('active')) {
                    loadReportPreview(currentReportFileName);
                }
            } else {
                setFeedback('manager-feedback', result.message, false);
            }
        });

        // 3. Seleção de Pasta (Configurações)
        async function selectFolder() {
            const result = await pywebview.api.selecionar_pasta_api();
            if (result.success) {
                document.getElementById('base-dir').value = result.path;
            } else {
                setFeedback('settings-feedback', result.message, false);
            }
        }

        // 4. Salvar Configurações (com Renomeação de Pasta)
        document.getElementById('form-configuracoes').addEventListener('submit', async (e) => {
            e.preventDefault();
            const base_dir = document.getElementById('base-dir').value.trim();
            const reports_folder_name = document.getElementById('reports-folder-name').value.trim();

            const result = await pywebview.api.salvar_configuracoes_api({ base_dir, reports_folder_name });

            if (result.success) {
                setFeedback('settings-feedback', result.message, true);
                loadSettingsData();
                loadReportSelect(); // Atualiza a lista de relatórios no Gerenciador (caso a pasta tenha mudado)
            } else {
                setFeedback('settings-feedback', result.message, false);
            }
        });

        // --- Sincronização CRÍTICA pywebviewready ---

        function initApp() {
            document.getElementById('loading-screen').style.display = 'none';
            document.querySelector('.content').style.display = 'block';
            navigateTo('dashboard-view'); 
        }

        window.addEventListener('pywebviewready', initApp);
    </script>
</body>
</html>
"""

# --- Inicialização do pywebview (CRÍTICO) ---

def start_pywebview():
    """Função wrapper para iniciar o pywebview, expondo a API."""
    api = Api()
    
    # CRÍTICO: Passar o conteúdo HTML diretamente como string
    webview.create_window(
        'Organizador de Relatórios',
        html=HTML_CONTENT, 
        js_api=api,
        width=1100,
        height=750,
        resizable=True
    )
    # Define o modo de depuração para False para produção (pode ser True para testes)
    webview.start(debug=False)

if __name__ == '__main__':
    start_pywebview()