import os
import re

# Pega a pasta onde o script está
pasta = os.path.dirname(os.path.abspath(__file__))

# Expressão para capturar as linhas "Style:"
padrao = re.compile(r'^(Style:[^,]*,[^,]*,)(\d+)(,.*?,)(\d+)(,)', re.MULTILINE)

for nome_arquivo in os.listdir(pasta):
    if nome_arquivo.lower().endswith(".ass"):
        caminho = os.path.join(pasta, nome_arquivo)
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()

        # Função para substituir os valores certos
        def substituir(match):
            prefixo = match.group(1)
            fontsize = match.group(2)
            meio = match.group(3)
            outline = match.group(4)
            sufixo = match.group(5)

            # Converte os valores
            novo_fontsize = "80" if fontsize == "60" else fontsize
            novo_outline = "20" if outline == "50" else outline

            return f"{prefixo}{novo_fontsize}{meio}{novo_outline}{sufixo}"

        novo_conteudo = re.sub(padrao, substituir, conteudo)

        # Só salva se houve mudança
        if novo_conteudo != conteudo:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(novo_conteudo)
            print(f"✔ Alterado: {nome_arquivo}")
        else:
            print(f"– Nenhuma mudança: {nome_arquivo}")

print("✅ Concluído! Todos os arquivos .ass da pasta foram verificados.")
