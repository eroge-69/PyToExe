import os

# Pega o diretório onde o .exe está localizado
pasta_atual = os.path.dirname(os.path.abspath(__file__))

# Lista arquivos de imagem
arquivos = [f for f in os.listdir(pasta_atual) if f.lower().endswith((".png", ".jpg"))]

# Gera arquivo de saída
with open(os.path.join(pasta_atual, "lista_imagens.txt"), "w", encoding="utf-8") as f:
    for nome in arquivos:
        caminho = os.path.join(pasta_atual, nome)
        f.write(caminho + "\n")