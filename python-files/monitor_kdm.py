import time
import os
import shutil
import zipfile

from pathlib import Path

origem = Path(r"C:\data\KDM COMPACTADOS")
destino_base = Path(r"C:\data\KDM")
log_path = Path(r"C:\scripts\log.txt")
log_path.parent.mkdir(parents=True, exist_ok=True)

def log(msg):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def process_zip(zip_path):
    nome = zip_path.stem
    destino = destino_base / nome
    try:
        destino.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destino)
        log(f"Descompactado com sucesso: {zip_path} -> {destino}")
    except Exception as e:
        log(f"Erro ao descompactar {zip_path}: {e}")

def monitorar_pasta():
    log("Monitoramento iniciado")
    processados = set()
    while True:
        for zip_file in origem.glob("*.zip"):
            if zip_file not in processados:
                time.sleep(2)  # Espera o arquivo terminar de copiar
                process_zip(zip_file)
                processados.add(zip_file)
        time.sleep(5)

if __name__ == "__main__":
    monitorar_pasta()