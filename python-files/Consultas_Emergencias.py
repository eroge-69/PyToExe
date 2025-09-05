import pyodbc
import sys
import os
from datetime import datetime
import textwrap

def get_connection():
    """Retorna uma conexão com o banco de dados"""
    server = 'FAC-DB53.facta.com.br'
    username = 'robopython'
    password = 'q#tre8lq6G@X$teTr*4o'
    database = 'Facta_01_BaseDados'
    
    conn_str = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        'ApplicationIntent=ReadOnly'
    )
    
    try:
        return pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        print(f"\nERRO: Não foi possível conectar ao banco de dados.")
        return None

def print_table(headers, rows, max_col_width=50):
    # Determinar a largura máxima de cada coluna
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(str(header))
        for row in rows:
            if i < len(row):
                # Para campos longos, considerar apenas a primeira linha
                cell_content = str(row[i])
                if len(cell_content) > max_col_width:
                    first_line = textwrap.wrap(cell_content, max_col_width)[0]
                    max_width = max(max_width, len(first_line))
                else:
                    max_width = max(max_width, len(cell_content))
        col_widths.append(min(max_width, max_col_width))
    
    # Ajustar a largura do cabeçalho se necessário
    for i, header in enumerate(headers):
        col_widths[i] = max(col_widths[i], len(str(header)))
    
    # Criar a linha separadora
    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    
    # Imprimir cabeçalho
    print(sep)
    print("| " + " | ".join(f"{str(header):<{col_widths[i]}}" for i, header in enumerate(headers)) + " |")
    print(sep)
    
    # Imprimir linhas de dados
    for row in rows:
        # Quebrar células longas em múltiplas linhas
        cell_lines = []
        max_lines = 1
        
        for i, cell in enumerate(row):
            cell_text = str(cell) if cell is not None else ""
            if len(cell_text) > col_widths[i]:
                wrapped_lines = textwrap.wrap(cell_text, col_widths[i])
                cell_lines.append(wrapped_lines)
                max_lines = max(max_lines, len(wrapped_lines))
            else:
                cell_lines.append([cell_text])
        
        # Imprimir todas as linhas necessárias para esta linha da tabela
        for line_idx in range(max_lines):
            line_cells = []
            for i in range(len(headers)):
                if line_idx < len(cell_lines[i]):
                    line_cells.append(f"{cell_lines[i][line_idx]:<{col_widths[i]}}")
                else:
                    line_cells.append(" " * col_widths[i])
            
            print("| " + " | ".join(line_cells) + " |")
    
    print(sep)

def consulta_aprovador_antigo(codigo):
    """Executa a consulta SQL para aprovador mais antigo"""
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return
            
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT TOP 3 codigo, login, nome, cpf, data_cadastro 
        FROM Corretor_Usuarios 
        WHERE Status = 'A' AND ID_PERFIL = 1 AND codigo = ? 
        ORDER BY Data_Cadastro ASC
        ''', codigo)
        
        resultados = cursor.fetchall()
        
        if not resultados:
            print(f"\nCorretor sem Perfil Aprovador definido: {codigo}")
        else:
            print("\n" + "=" * 80)
            print("RESULTADOS DA CONSULTA: APROVADOR MAIS ANTIGO".center(80))
            print("=" * 80)
            headers = ['Código', 'Login', 'Nome', 'CPF', 'Data Cadastro']
            rows = [
                (
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4].strftime('%d/%m/%Y %H:%M') if row[4] else 'N/A'
                )
                for row in resultados
            ]
            print_table(headers, rows)
        
    except pyodbc.Error as e:
        error_msg = f"\nERRO NA CONSULTA: {e}"
        print(error_msg)
    finally:
        if conn:
            conn.close()

def consulta_token_sms(login):
    """Executa a consulta SQL para token SMS"""
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return
            
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT Login, 
            CASE
                WHEN token_sms IS NULL THEN 'APP ATIVO'
                ELSE CAST(token_sms AS VARCHAR(50))
            END AS Token_SMS,
            data_criacao 
        FROM Token_app_usuarios 
        WHERE login = ?
        ''', login)
        
        resultados = cursor.fetchall()
        
        if not resultados:
            print(f"\nNenhum token encontrado para o login: {login}")
        else:
            print("\n" + "=" * 80)
            print("RESULTADOS DA CONSULTA: TOKEN SMS".center(80))
            print("=" * 80)
            headers = ['Login', 'Token SMS', 'Data Criação']
            rows = [
                (
                    row[0],
                    row[1],
                    row[2].strftime('%d/%m/%Y %H:%M') if row[2] else 'N/A'
                )
                for row in resultados
            ]
            print_table(headers, rows)
        
    except pyodbc.Error as e:
        error_msg = f"\nERRO NA CONSULTA: {e}"
        print(error_msg)
    finally:
        if conn:
            conn.close()

def consulta_por_telefone(telefone):
    """Executa a consulta SQL para buscar por telefone"""
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return
            
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT login, telefone, data_criacao
        FROM token_app_usuarios
        WHERE REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(telefone)), '(', ''), ')', ''), '-', ''), '.', ''), ' ', '') = 
              REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(?)), '(', ''), ')', ''), '-', ''), '.', ''), ' ', '')
        ''', telefone)
        
        resultados = cursor.fetchall()
        
        if not resultados:
            print(f"\nNenhum registro encontrado para o telefone: {telefone}")
        else:
            print("\n" + "=" * 80)
            print("RESULTADOS DA CONSULTA: BUSCA POR TELEFONE".center(80))
            print("=" * 80)
            headers = ['Login', 'Telefone', 'Data Criação']
            rows = [
                (
                    row[0],
                    row[1],
                    row[2].strftime('%d/%m/%Y %H:%M') if row[2] else 'N/A'
                )
                for row in resultados
            ]
            print_table(headers, rows)
        
    except pyodbc.Error as e:
        error_msg = f"\nERRO NA CONSULTA: {e}"
        print(error_msg)
    finally:
        if conn:
            conn.close()

def consulta_perfil_usuario(login):
    """Executa a consulta SQL para buscar perfil do usuário"""
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return
            
        cursor = conn.cursor()
        
        cursor.execute('''
        select cu.login,cu.ID_PERFIL as 'Código Perfil', ap.NOME as 'Nome Perfil', ap.LEGENDA_PERFIL as Descrição
        from Corretor_Usuarios Cu
        left join ANDAMENTO_PERFIS ap on ap.ID = Cu.ID_PERFIL
        where cu.Login = ?
        union all
        select f.login, f.id_perfil as 'Código Perfil', ap.NOME as 'Nome Perfil', ap.LEGENDA_PERFIL as Descrição
        from fl_funcionario f
        left join ANDAMENTO_PERFIS ap on ap.ID = f.ID_PERFIL
        where f.Login = ?
        ''', login, login)
        
        resultados = cursor.fetchall()
        
        if not resultados:
            print(f"\nNenhum perfil encontrado para o login: {login}")
        else:
            print("\n" + "=" * 80)
            print("RESULTADOS DA CONSULTA: PERFIL DO USUÁRIO".center(80))
            print("=" * 80)
            headers = ['Login', 'Código Perfil', 'Nome Perfil', 'Descrição']
            rows = [
                (
                    row[0],
                    row[1],
                    row[2],
                    row[3]
                )
                for row in resultados
            ]
            print_table(headers, rows, max_col_width=40)  # Largura menor para a descrição
        
    except pyodbc.Error as e:
        error_msg = f"\nERRO NA CONSULTA: {e}"
        print(error_msg)
    finally:
        if conn:
            conn.close()

def exibir_menu():
    """Exibe o menu de opções"""
    print("\n" + "=" * 60)
    print("MENU PRINCIPAL".center(60))
    print("=" * 60)
    print("1 - Consulta Aprovador Mais Antigo")
    print("2 - Consulta Token SMS")
    print("3 - Consulta de Token por nº de Telefone")
    print("4 - Consulta Perfil do Usuário")
    print("5 - Sair")
    print("=" * 60)

def safe_input(prompt):
    """Função segura para entrada de dados"""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada cancelada pelo usuário")
        return None
    except Exception as e:
        return None

def main():
    try:
        while True:
            exibir_menu()
            opcao = safe_input("\nDigite a opção desejada: ")
            if opcao is None:
                continue
            opcao = opcao.strip()
            
            if opcao == '1':
                print("\n" + "=" * 60)
                print("CONSULTA DE APROVADOR MAIS ANTIGO (PERFIL 1)".center(60))
                print("=" * 60)
                try:
                    codigo = safe_input("\nDigite o código do corretor: ")
                    if codigo is None:
                        continue
                    codigo = int(codigo.strip())
                    consulta_aprovador_antigo(codigo)
                except ValueError:
                    print("ERRO: Por favor, digite um número inteiro válido.")
            
            elif opcao == '2':
                print("\n" + "=" * 60)
                print("CONSULTA DE TOKEN SMS".center(60))
                print("=" * 60)
                login = safe_input("\nDigite o login para consulta: ")
                if login is not None:
                    consulta_token_sms(login.strip())
            
            elif opcao == '3':
                print("\n" + "=" * 60)
                print("CONSULTA DE TOKEN POR Nº DE TELEFONE".center(60))
                print("=" * 60)
                telefone = safe_input("\nDigite o telefone com DDD para consulta: ")
                if telefone is not None:
                    consulta_por_telefone(telefone.strip())
            
            elif opcao == '4':
                print("\n" + "=" * 60)
                print("CONSULTA PERFIL DO USUÁRIO".center(60))
                print("=" * 60)
                login = safe_input("\nDigite o login para consulta: ")
                if login is not None:
                    consulta_perfil_usuario(login.strip())
            
            elif opcao == '5':
                print("\nEncerrando o programa...")
                sys.exit(0)
            
            else:
                print("\nOpção inválida. Por favor, escolha 1, 2, 3, 4 ou 5.")
                
    except Exception as e:
        print(f"\nERRO CRÍTICO: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    # Verifica dependências
    try:
        import pyodbc
    except ImportError as e:
        print(f"ERRO: {e}. Instale as dependências com: pip install pyodbc")
        sys.exit(1)
    
    main()