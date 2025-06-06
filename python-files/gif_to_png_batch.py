
import os
from PIL import Image
import sys

def converter_gifs_na_pasta(pasta):
    arquivos = os.listdir(pasta)
    gifs = [f for f in arquivos if f.lower().endswith(".gif")]

    if not gifs:
        print("Nenhum arquivo GIF encontrado na pasta.")
        return

    for gif in gifs:
        caminho_completo = os.path.join(pasta, gif)
        nome_base = os.path.splitext(gif)[0]
        caminho_saida = os.path.join(pasta, nome_base + ".png")

        try:
            img = Image.open(caminho_completo)
            img.convert("RGBA").save(caminho_saida, "PNG")
            print(f"Convertido: {gif} → {nome_base}.png")
        except Exception as e:
            print(f"Erro ao converter {gif}: {e}")

    print("\nConversão concluída.")

if __name__ == "__main__":
    pasta_atual = os.path.dirname(sys.executable)
    converter_gifs_na_pasta(pasta_atual)
    input("\nPressione Enter para sair...")
