import zipfile
import os
import csv
from concurrent.futures import ThreadPoolExecutor

def contar_linhas_zip(caminho_zip, extensoes=(".txt", ".log", ".json")):
    total_zip = 0
    try:
        with zipfile.ZipFile(caminho_zip, 'r') as zip:
            for nome_interno in zip.namelist():
                if nome_interno.endswith(extensoes):
                    try:
                        with zip.open(nome_interno) as arquivo:
                            for _ in arquivo:
                                total_zip += 1
                    except Exception as e:
                        print(f"Erro ao ler {nome_interno} em {caminho_zip}: {e}")
    except Exception as e:
        print(f"Erro ao processar {caminho_zip}: {e}")
    return caminho_zip, total_zip

def contar_linhas_em_diretorio(diretorio, extensoes=(".txt", ".log", ".json"), max_threads=8, exportar_csv=False):
    arquivos_zip = []
    for root, _, files in os.walk(diretorio):
        for f in files:
            if f.endswith(".zip"):
                arquivos_zip.append(os.path.join(root, f))

    total_geral = 0
    resultados_csv = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        resultados = executor.map(lambda f: contar_linhas_zip(f, extensoes), arquivos_zip)

    for caminho, total in resultados:
        nome_arquivo = os.path.basename(caminho)
        print(f"{nome_arquivo}: {total} linhas")
        resultados_csv.append((nome_arquivo, total))
        total_geral += total

    print(f"\nTotal geral de linhas: {total_geral}")

    if exportar_csv:
        caminho_csv = os.path.join(diretorio, "resultado_linhas.csv")
        try:
            with open(caminho_csv, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Arquivo ZIP", "Total de Linhas"])
                writer.writerows(resultados_csv)
            print(f"\nResultados exportados para: {caminho_csv}")
        except Exception as e:
            print(f"Erro ao exportar CSV: {e}")

# Exemplo de uso
if __name__ == "__main__":
    contar_linhas_em_diretorio(".", extensoes=(".txt", ".log", ".json"), exportar_csv=True)
