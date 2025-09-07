#!/usr/bin/env python3
import subprocess
import os
import sys

def main():
    # Caminho da raiz do jogo (onde está o TheBazaar.exe original)
    user = os.getlogin()
    root_game_path = fr"C:\Users\{user}\AppData\Roaming\Tempo Launcher - Beta\game\buildx64\TheBazaar.exe"

    if not os.path.exists(root_game_path):
        print(f"Erro: não encontrei o TheBazaar.exe em {root_game_path}")
        sys.exit(1)

    # Pega todos os argumentos passados para o wrapper
    args = sys.argv[1:]

    # Executa o EXE original passando os argumentos
    try:
        subprocess.run([root_game_path, *args], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o jogo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
