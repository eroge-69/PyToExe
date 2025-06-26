import shutil
import os
import sys
from pathlib import Path

def copiar_diretorio(origem: str, destino: str) -> None:
    """
    Copia recursivamente todo o conteúdo de `origem` para `destino`.

    Parâmetros
    ----------
    origem : str
        Caminho da pasta que será copiada.
    destino : str
        Caminho da pasta que receberá a cópia.
    """
    origem_path = Path(origem).expanduser().resolve()
    destino_path = Path(destino).expanduser().resolve()

    if not origem_path.is_dir():
        raise NotADirectoryError(f'O caminho de origem não existe ou não é uma pasta: {origem_path}')

    # Cria a pasta-destino, se necessário
    destino_path.mkdir(parents=True, exist_ok=True)

    for item in origem_path.rglob("*"):
        # Determina o caminho relativo ao diretório de origem
        rel_path = item.relative_to(origem_path)
        destino_item = destino_path / rel_path

        if item.is_dir():
            destino_item.mkdir(parents=True, exist_ok=True)
        else:
            # Garante que a pasta de destino exista
            destino_item.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, destino_item)  # copy2 mantém metadados (data/hora)

    print(f"Cópia concluída: '{origem_path}'  →  '{destino_path}'")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python copiar.py <diretorio_origem> <diretorio_destino>")
        sys.exit(1)

    origem_dir = 'Z:\\20. BANCO DO BRASIL\\2025\\CAMPANHAS\\02. CCBB EDITAL\\PLANO DE MÍDIA'
    destino_dir = "C:\\Users\\rafael.melo\\Desktop\\PM's\\EDITAL_BB"

    try:
        copiar_diretorio(origem_dir, destino_dir)
    except Exception as e:
        print(f"Erro ao copiar: {e}")
        sys.exit(1)