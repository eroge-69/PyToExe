from PyPDF2 import PdfReader, PdfWriter
from tqdm import tqdm

# Carrega os PDFs
pdf_fixo = PdfReader("Livro Acareg 15pag.pdf")
pdf_variavel = PdfReader("bingo 1200 QRcode.pdf")

# Loop por cada página do PDF variável
for i in tqdm(range(len(pdf_variavel.pages)), total=len(pdf_variavel.pages)):
    writer = PdfWriter()
    
    # Adicionar páginas fixas
    for j in range(len(pdf_fixo.pages)):
        writer.add_page(pdf_fixo.pages[j])
    
    # Adiciona uma página do PDF variável
    writer.add_page(pdf_variavel.pages[i])
    
    # Guarda num novo ficheiro
    with open(f"output_{i+1}.pdf", "wb") as f_out:
        writer.write(f_out)

print("✅ PDFs criados com sucesso!")