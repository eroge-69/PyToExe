import os
import shutil
import subprocess
import sys
import zipfile
import re

# Verifica se PyPDF2 está instalado e instala se necessário
try:
    from PyPDF2 import PdfMerger
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    from PyPDF2 import PdfMerger

# Verifica se rarfile está instalado e instala se necessário
try:
    import rarfile
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rarfile"])
    import rarfile

# Verifica se Pillow está instalado e instala se necessário
try:
    from PIL import Image
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

def descompactar_arquivos(caminho_principal):
    for item in os.listdir(caminho_principal):
        caminho_item = os.path.join(caminho_principal, item)
        nome_base, extensao = os.path.splitext(item)

        if extensao.lower() == ".zip":
            try:
                with zipfile.ZipFile(caminho_item, 'r') as zip_ref:
                    pasta_destino = os.path.join(caminho_principal, nome_base)
                    os.makedirs(pasta_destino, exist_ok=True)
                    zip_ref.extractall(pasta_destino)
            except Exception as e:
                print(f"Erro ao extrair {item}: {e}")
            try:
                os.remove(caminho_item)
            except PermissionError:
                print(f"Arquivo em uso, não foi possível remover: {caminho_item}")

        elif extensao.lower() == ".rar":
            try:
                with rarfile.RarFile(caminho_item) as rar_ref:
                    pasta_destino = os.path.join(caminho_principal, nome_base)
                    os.makedirs(pasta_destino, exist_ok=True)
                    rar_ref.extractall(pasta_destino)
                try:
                    os.remove(caminho_item)
                except PermissionError:
                    print(f"Arquivo em uso, não foi possível remover: {caminho_item}")
            except rarfile.RarCannotExec:
                print(f"Erro ao extrair {item}: UnRAR não encontrado. Instale o UnRAR no sistema.")

def limpar_nome(nome):
    nome = re.sub(r'[^a-zA-Z0-9_\-]', '_', nome)
    return nome[:100]

def renomear_subpastas_para_numeros(caminho_principal):
    subpastas = [p for p in os.listdir(caminho_principal) if os.path.isdir(os.path.join(caminho_principal, p))]
    subpastas.sort()
    for i, nome_antigo in enumerate(subpastas, start=1):
        caminho_antigo = os.path.join(caminho_principal, nome_antigo)
        caminho_novo = os.path.join(caminho_principal, str(i))
        if caminho_antigo != caminho_novo:
            os.rename(caminho_antigo, caminho_novo)

def converter_imagens_para_pdfs(caminho_subpasta):
    imagens = [f for f in os.listdir(caminho_subpasta) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    pdfs_gerados = []
    for img_nome in imagens:
        caminho_img = os.path.join(caminho_subpasta, img_nome)
        try:
            imagem = Image.open(caminho_img).convert("RGB")
            nome_base = limpar_nome(os.path.splitext(img_nome)[0])
            nome_pdf = nome_base + ".pdf"
            caminho_pdf = os.path.join(caminho_subpasta, nome_pdf)
            imagem.save(caminho_pdf)
            pdfs_gerados.append(caminho_pdf)
        except Exception as e:
            print(f"Erro ao converter imagem {img_nome}: {e}")
    return pdfs_gerados

def compilar_pdfs_em_subpastas(caminho_principal):
    arquivos_compilados = []
    subpastas = sorted([p for p in os.listdir(caminho_principal) if os.path.isdir(os.path.join(caminho_principal, p))], key=lambda x: int(x) if x.isdigit() else x)

    for nome_subpasta in subpastas:
        caminho_subpasta = os.path.join(caminho_principal, nome_subpasta)
        converter_imagens_para_pdfs(caminho_subpasta)
        pdfs = [f for f in os.listdir(caminho_subpasta) if f.lower().endswith(".pdf")]
        pdfs.sort()
        if pdfs:
            merger = PdfMerger()
            for pdf in pdfs:
                caminho_pdf = os.path.join(caminho_subpasta, pdf)
                merger.append(caminho_pdf)
            nome_compilado = f"{nome_subpasta}.pdf"
            caminho_compilado = os.path.join(caminho_principal, nome_compilado)
            merger.write(caminho_compilado)
            merger.close()
            arquivos_compilados.append(nome_compilado)

    # Após compilar, apagar todas as subpastas
    for nome_subpasta in subpastas:
        caminho_subpasta = os.path.join(caminho_principal, nome_subpasta)
        try:
            shutil.rmtree(caminho_subpasta)
        except Exception as e:
            print(f"Erro ao excluir subpasta {nome_subpasta}: {e}")

    return sorted(arquivos_compilados)

def main():
    caminho_principal = r"C:\\Users\\hans.santos\\Documents\\analise documental"
    print(f"Descompactando arquivos em: {caminho_principal}")
    descompactar_arquivos(caminho_principal)

    print("Renomeando subpastas para números sequenciais...")
    renomear_subpastas_para_numeros(caminho_principal)

    print(f"Compilando PDFs das subpastas de: {caminho_principal}")
    arquivos = compilar_pdfs_em_subpastas(caminho_principal)

    print("\nArquivos compilados e salvos na pasta principal em ordem alfabética:")
    for arq in arquivos:
        print(f" - {arq}")

if __name__ == "__main__":
    main()
