import os
import time
import platform
import getpass
import random
import string

ARQUIVO_MACRO = "Fast Preguiça V4 Completo final2 (backup).mrf"
ARQUIVO_CHAVES = "chaves.txt"
ARQUIVO_LICENCA = "licenca.txt"

def gerar_chave():
    partes = []
    for _ in range(4):
        parte = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        partes.append(parte)
    return '-'.join(partes)

def gerar_varias_chaves(n=10):
    chaves = set()
    while len(chaves) < n:
        chaves.add(gerar_chave())
    return list(chaves)

def criar_arquivo_chaves():
    if not os.path.exists(ARQUIVO_CHAVES):
        chaves = gerar_varias_chaves(10)
        with open(ARQUIVO_CHAVES, "w") as f:
            for chave in chaves:
                f.write(chave + "\n")
        print(f"Arquivo '{ARQUIVO_CHAVES}' criado com 10 chaves.")

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_alerta():
    print("\033[91m")
    print("=" * 60)
    print("   ⚠️  ATENÇÃO! ⚠️")
    print("=" * 60)
    print(" SE VOCÊ COMPARTILHAR SUA CHAVE COM OUTRA PESSOA,")
    print(" O SISTEMA DETECTARÁ E A CHAVE SERÁ CANCELADA.")
    print(" VOCÊ E A OUTRA PESSOA PERDERÃO O ACESSO!")
    print("=" * 60)
    print("\033[0m")

def get_id_maquina():
    return platform.node() + "_" + getpass.getuser()

def esconder_macro():
    os.system(f'attrib +h "{ARQUIVO_MACRO}"')

def revelar_macro():
    os.system(f'attrib -h "{ARQUIVO_MACRO}"')

def ativar():
    limpar_tela()
    mostrar_alerta()
    print("===== SISTEMA DE ATIVAÇÃO =====")
    chave = input("Digite sua chave de ativação: ").strip().upper()

    if not os.path.exists(ARQUIVO_CHAVES):
        print("Arquivo de chaves não encontrado.")
        return

    with open(ARQUIVO_CHAVES, "r") as f:
        chaves = [linha.strip().upper() for linha in f if linha.strip()]

    if chave in chaves:
        id_maquina = get_id_maquina()
        with open(ARQUIVO_LICENCA, "w") as f:
            f.write(f"ATIVADO\nCHAVE: {chave}\nID: {id_maquina}")
        chaves.remove(chave)
        with open(ARQUIVO_CHAVES, "w") as f:
            f.write("\n".join(chaves))
        revelar_macro()
        print("\n\033[92mProduto ativado com sucesso nesta máquina!\033[0m")
        time.sleep(1)
        executar_macro()
    else:
        print("\n\033[91mChave inválida ou já utilizada.\033[0m")

def verificar_ativacao():
    if not os.path.exists(ARQUIVO_LICENCA):
        return False
    with open(ARQUIVO_LICENCA, "r") as f:
        dados = f.read()
    id_salvo = [linha for linha in dados.splitlines() if linha.startswith("ID:")]
    if id_salvo and get_id_maquina() in id_salvo[0]:
        return True
    return False

def executar_macro():
    if os.path.exists(ARQUIVO_MACRO):
        try:
            os.startfile(ARQUIVO_MACRO)
            print("\033[92mArquivo executado com sucesso!\033[0m")
        except Exception as e:
            print(f"\033[91mErro ao executar o arquivo: {e}\033[0m")
    else:
        print(f"\nArquivo '{ARQUIVO_MACRO}' não encontrado.")

def main():
    criar_arquivo_chaves()
    if verificar_ativacao():
        print("Produto já está ativado neste computador.")
        revelar_macro()
        executar_macro()
    else:
        esconder_macro()
        ativar()

if __name__ == "__main__":
    main()
