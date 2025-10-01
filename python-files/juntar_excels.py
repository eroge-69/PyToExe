import pandas as pd
import os

# Pasta onde estão os ficheiros
pasta = r"C:\Users\SeuNome\Documents\Excels"  

# Nome do ficheiro final
ficheiro_saida = r"C:\Users\SeuNome\Documents\Compilado.xlsx"

# Lista todos os ficheiros Excel na pasta
ficheiros = [f for f in os.listdir(pasta) if f.endswith('.xlsx')]

# Lista para armazenar os dataframes
dfs = []

for f in ficheiros:
    caminho = os.path.join(pasta, f)
    df = pd.read_excel(caminho)
    df['Origem'] = f  # opcional: marca de que ficheiro veio
    dfs.append(df)

# Junta tudo
resultado = pd.concat(dfs, ignore_index=True)

# Salva no Excel final
resultado.to_excel(ficheiro_saida, index=False)

print(f"Ficheiros compilados em: {ficheiro_saida}")