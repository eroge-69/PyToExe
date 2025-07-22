import pandas as pd
import glob
import os

def main():
    pasta = os.getcwd()  # Usa a pasta atual onde está o .exe
    ficheiros = glob.glob(os.path.join(pasta, "*.csv"))

    if not ficheiros:
        print("Nenhum ficheiro CSV encontrado na pasta.")
        return

    dfs = []
    for i, f in enumerate(ficheiros):
        if i == 0:
            dfs.append(pd.read_csv(f))
        else:
            dfs.append(pd.read_csv(f, skiprows=1))  # Ignora cabeçalho

    df_final = pd.concat(dfs, ignore_index=True)
    df_final.to_csv(os.path.join(pasta, "ficheiro_unido.csv"), index=False)

    print("Ficheiro 'ficheiro_unido.csv' criado com sucesso!")

if __name__ == "__main__":
    main()
