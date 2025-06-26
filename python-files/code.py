import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog

def verificar_e_instalar_pyinstaller():
    """Verifica se o PyInstaller está instalado e, se não, o instala via pip."""
    print("Verificando se o PyInstaller está instalado...")
    try:
        import PyInstaller
        print("PyInstaller já está instalado.")
        return True
    except ImportError:
        print("PyInstaller não encontrado. Tentando instalar via pip...")
        try:
            # Usamos sys.executable para garantir que estamos usando o pip do ambiente python correto
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller instalado com sucesso!")
            return True
        except subprocess.CalledProcessError:
            print("\nERRO: Falha ao instalar o PyInstaller.")
            print("Por favor, instale manualmente executando: pip install pyinstaller")
            return False

def selecionar_arquivo():
    """Abre uma janela para o usuário selecionar o arquivo .py a ser convertido."""
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal do tkinter
    
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione o arquivo Python (.py) para converter",
        filetypes=[("Arquivos Python", "*.py"), ("Todos os arquivos", "*.*")]
    )
    return caminho_arquivo

def criar_executavel(script_path, opcoes):
    """Executa o comando PyInstaller para criar o executável."""
    if not os.path.exists(script_path):
        print(f"ERRO: O arquivo '{script_path}' não foi encontrado.")
        return

    print("\nIniciando o processo de conversão. Isso pode levar alguns minutos...")
    
    # Monta o comando
    comando = ['pyinstaller'] + opcoes + [script_path]
    
    print(f"Executando comando: {' '.join(comando)}")

    try:
        # Executa o comando e captura a saída em tempo real
        processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
        
        while True:
            output = processo.stdout.readline()
            if output == '' and processo.poll() is not None:
                break
            if output:
                print(output.strip())

        # Verifica se o processo terminou com erro
        if processo.poll() != 0:
             raise subprocess.CalledProcessError(processo.poll(), comando)

        # O nome do executável será o mesmo do script, sem a extensão .py
        nome_base = os.path.splitext(os.path.basename(script_path))[0]
        caminho_exe = os.path.join("dist", f"{nome_base}.exe")

        print("\n--------------------------------------------------")
        print("✨ Conversão concluída com sucesso! ✨")
        print(f"O executável foi criado em: {os.path.abspath(caminho_exe)}")
        print("--------------------------------------------------")

    except subprocess.CalledProcessError as e:
        print("\n--------------------------------------------------")
        print(f"❌ ERRO durante a conversão: O PyInstaller retornou o código de erro {e.returncode}.")
        print("Verifique as mensagens de erro acima para mais detalhes.")
        print("--------------------------------------------------")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")

def main():
    """Função principal que orquestra o processo."""
    print("=============================================")
    print("    Conversor Automático de .py para .exe    ")
    print("=============================================\n")

    if not verificar_e_instalar_pyinstaller():
        input("Pressione Enter para sair.")
        return

    caminho_do_script = selecionar_arquivo()

    if not caminho_do_script:
        print("Nenhum arquivo selecionado. Operação cancelada.")
        return

    print(f"Arquivo selecionado: {caminho_do_script}\n")

    # Coletando opções do usuário
    opcoes_pyinstaller = []

    onefile = input("Deseja criar um único arquivo executável (s/n)? (s) ").lower().strip()
    if onefile != 'n':
        opcoes_pyinstaller.append('--onefile')

    no_console = input("Seu programa é uma aplicação de janela (sem console)? (s/n)? (n) ").lower().strip()
    if no_console == 's':
        opcoes_pyinstaller.append('--windowed') # ou --noconsole

    caminho_icone = input("Deseja adicionar um ícone (.ico)? (deixe em branco para não usar) ").strip()
    if caminho_icone and os.path.exists(caminho_icone):
        opcoes_pyinstaller.append(f'--icon={caminho_icone}')
    elif caminho_icone:
        print("Aviso: Caminho do ícone não encontrado. O ícone não será adicionado.")

    criar_executavel(caminho_do_script, opcoes_pyinstaller)
    
    input("\nPressione Enter para fechar o programa.")


if __name__ == "__main__":
    main()