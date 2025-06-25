import win32netcon
import win32net
import os
import glob
import shutil
import pyodbc as db

# Dados de acesso e caminho da pasta de rede de origem
rede_path_origem = "//cr7260nt036/GEPSO03/RELATORIOS/CNPJ_EXTRACAO_MENSAL";
# Caminho da pasta de destino
rede_path_destino = "//DF7436SR489/PUB";
dominio =''
dsname = 'ISO_RJ_BQA1_EXT_SOCIO_PJ_M*'

sql_server = "DF7436SR489"
sql_database = "DB5063_MP"
connection_string = f"DRIVER={{SQL Server}};SERVER={sql_server};DATABASE={sql_database};Trusted_Connection=yes;"


# Função para recuperar senha do banco de dados
def recupera_senha(tipo, connection_string):
    with db.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute(f"EXEC [DB5063_MP].[ADM].[spRecuperaSenhaWebScraping] ?", (tipo,))
        row = cursor.fetchone()
        if row:
            usuario = row[0]
            senha = row[1]
            return usuario, senha
        else:
            raise ValueError("Não foi possível recuperar as credenciais.")
        

# Função para mapear a pasta de rede
def conectar_pasta_rede(path, usuario, senha, dominio=''):
    info = {
        'remote': path,
        'password': senha,
        'username': usuario,
        'domainname': dominio,
        'flags': win32netcon.CONNECT_INTERACTIVE
    }
    try:
        win32net.NetUseAdd(None, 2, info)
        print(f'Conectado com sucesso em {path}!')
    except Exception as e:
        print(f'Erro ao conectar em {path}: {e}')

# Buscar arquivos com "TESTE_LOG" no nome
def buscar_arquivo(path, termo):
    padrao = os.path.join(path, f'*{termo}*')
    arquivos = glob.glob(padrao)
    return arquivos

# Copiar arquivos para a pasta de destino
def copiar_arquivos(arquivos, destino):
    for arquivo in arquivos:
        try:
            shutil.copy2(arquivo, destino)
            print(f'Arquivo {os.path.basename(arquivo)} copiado para {destino}')
        except Exception as e:
            print(f'Erro ao copiar {arquivo}: {e}')

if __name__ == '__main__':
    # Conectar nas pastas de origem e destino
    
    usuario, senha = recupera_senha("RF",connection_string)
    
    conectar_pasta_rede(rede_path_origem, usuario, senha, dominio)
    conectar_pasta_rede(rede_path_destino, usuario, senha, dominio)

    # Buscar arquivos
    arquivos_encontrados = buscar_arquivo(rede_path_origem, dsname)
    if arquivos_encontrados:
        print('Arquivos encontrados:')
        for arquivo in arquivos_encontrados:
            print(arquivo)
        # Copiar arquivos encontrados
        copiar_arquivos(arquivos_encontrados, rede_path_destino)
    else:
        print('Nenhum arquivo encontrado.')