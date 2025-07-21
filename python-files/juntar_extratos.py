
import os
import fitz  # PyMuPDF

# Função para identificar pares de arquivos (Protheus e banco)
def identificar_pares(arquivos):
    pares = []
    protheus_files = [f for f in arquivos if 'PROTHEUS' in f.upper()]
    outros_files = [f for f in arquivos if 'PROTHEUS' not in f.upper()]

    for protheus in protheus_files:
        nome_base = protheus.upper().replace('PROTHEUS', '').strip()
        for outro in outros_files:
            if all(palavra in outro.upper() for palavra in nome_base.split()):
                pares.append((protheus, outro))
                break
    return pares

# Função para juntar dois PDFs em um único arquivo
def juntar_pdfs(arquivo1, arquivo2, nome_saida):
    pdf_arquivo = fitz.open()
    for arquivo in [arquivo1, arquivo2]:
        with fitz.open(arquivo) as pdf:
            for pagina in pdf:
                pdf_arquivo.insert_pdf(pdf, from_page=pagina.number, to_page=pagina.number)
    pdf_arquivo.save(nome_saida)
    pdf_arquivo.close()

# Função principal
def processar_pasta():
    arquivos_pdf = [f for f in os.listdir() if f.lower().endswith('.pdf')]
    pares = identificar_pares(arquivos_pdf)

    for protheus, banco in pares:
        partes_nome = banco.replace('.pdf', '').split()
        banco_nome = partes_nome[0].upper()
        sociedade = next((s for s in ['SP', 'RJ', 'DF', 'PI'] if s in partes_nome), 'OUTRO')
        nome_saida = f"{banco_nome}_{sociedade}.pdf"
        juntar_pdfs(protheus, banco, nome_saida)
        print(f"✅ Arquivo gerado: {nome_saida}")

# Executar o script
if __name__ == "__main__":
    processar_pasta()
