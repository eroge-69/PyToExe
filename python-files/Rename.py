import os

# Pega a pasta atual
pasta_atual = os.getcwd()

# Lista todos os arquivos .mp3 na pasta atual
arquivos_mp3 = [f for f in os.listdir(pasta_atual) if f.lower().endswith('.mp3')]

# Ordena os arquivos (opcional, mas bom pra manter a ordem alfabética)
arquivos_mp3.sort()

# Renomeia os arquivos para "Faixa 001.mp3", "Faixa 002.mp3", etc.
for i, nome_antigo in enumerate(arquivos_mp3, start=1):
    novo_nome = f"Faixa {i:03}.mp3"
    os.rename(nome_antigo, novo_nome)
    print(f'Renomeado: "{nome_antigo}" -> "{novo_nome}"')

print("Renomeação concluída!")
