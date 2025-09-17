import shutil
import tkinter as tk
from tkinter import filedialog
import os

def copiar_arquivos():
    # Pasta de origem predefinida
    pasta_origem = r'D:\steamAPI dlls'

    # Nomes dos arquivos a copiar
    arquivos = ['steam_api.dll', 'steam_api64.dll']

    # Inicializa o tkinter e oculta a janela principal
    root = tk.Tk()
    root.withdraw()

    # Abre a caixa de seleção de pasta
    pasta_destino = filedialog.askdirectory(title='Selecione a pasta de destino')

    if not pasta_destino:
        print('Nenhuma pasta selecionada. Operação cancelada.')
        return

    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)

        if os.path.exists(caminho_origem):
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f'Arquivo {arquivo} copiado com sucesso para {pasta_destino}')
            except Exception as e:
                print(f'Erro ao copiar {arquivo}: {e}')
        else:
            print(f'Arquivo {arquivo} não encontrado na pasta de origem.')

if __name__ == '__main__':
    copiar_arquivos()
