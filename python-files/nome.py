import os

def formatar_nome_arquivo(nome_original):
    """
    Formata o nome do arquivo com base em regras de comprimento.
    """
    # Remove a extensão para a verificação
    nome_sem_extensao = os.path.splitext(nome_original)[0]
    
    # Verifica se o nome é composto apenas por dígitos
    if not nome_sem_extensao.isdigit():
        return nome_sem_extensao # Não mexe em arquivos que não são só números
    
    # Regra 1: Para nomes de 16 dígitos (ex: '0022323577600002')
    if len(nome_sem_extensao) == 16:
        sem_inicio = nome_sem_extensao[2:]
        nome_formatado = sem_inicio[:-4]
        return nome_formatado
    
    # Regra 2: Para nomes de 10 dígitos (ex: '2232357760')
    elif len(nome_sem_extensao) == 10:
        nome_formatado = nome_sem_extensao[:-1]
        return nome_formatado
        
    # Se o nome não se encaixar em nenhuma das regras, retorna o original
    return nome_sem_extensao

def renomear_arquivos_na_pasta(caminho_da_pasta):
    """
    Percorre a pasta e renomeia os arquivos que se adequam aos padrões.
    """
    try:
        arquivos = os.listdir(caminho_da_pasta)
        
        for arquivo in arquivos:
            # Exclui o próprio script do processo de renomeação
            if arquivo == "renomear_arquivos.py":
                print(f"Ignorando o script de renomeação: {arquivo}")
                continue
                
            nome_original, extensao = os.path.splitext(arquivo)
            
            novo_nome = formatar_nome_arquivo(nome_original)
            
            # Se o novo nome for diferente do original, a formatação foi aplicada
            if novo_nome != nome_original:
                caminho_original = os.path.join(caminho_da_pasta, arquivo)
                novo_caminho = os.path.join(caminho_da_pasta, novo_nome + extensao)
                
                print(f"Renomeando: {arquivo} -> {novo_nome}{extensao}")
                os.rename(caminho_original, novo_caminho)
            else:
                print(f"Ignorando arquivo: {arquivo} (não corresponde aos padrões)")
            
        print("\nProcesso de renomeação concluído.")
        
    except FileNotFoundError:
        print(f"Erro: A pasta '{caminho_da_pasta}' não foi encontrada.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# O caminho da sua pasta de teste
caminho_da_pasta_alvo = r"C:\Users\igor.siqueira\Desktop\Teste"

renomear_arquivos_na_pasta(caminho_da_pasta_alvo)