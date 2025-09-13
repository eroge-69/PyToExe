import re
import fitz  # PyMuPDF
import os
import sys
from tkinter import Tk, filedialog, messagebox

def processar_pdf(input_pdf):
    try:
        # 📂 Pasta de saída (mesma do arquivo original)
        output_dir = os.path.dirname(input_pdf)

        # Texto que indica o fim de cada memorial
        assinatura_fim = "LUANA NUNES DE OLIVEIRA       KELITON PEREIRA CANABRAVA VELOSO"

        # Abrir PDF original
        doc = fitz.open(input_pdf)

        memoriais = []
        bloco_paginas = []
        texto_acumulado = ""

        # 🔎 Percorrer páginas do PDF
        for i, page in enumerate(doc, 1):
            texto = page.get_text("text")
            texto_acumulado += texto
            bloco_paginas.append(page.number)

            # Quando encontrar o fim do memorial
            if assinatura_fim in texto:
                memoriais.append((bloco_paginas.copy(), texto_acumulado))
                bloco_paginas = []
                texto_acumulado = ""

        if not memoriais:
            messagebox.showerror("Erro", "Nenhum memorial encontrado no PDF selecionado.")
            return

        # 📑 Criar PDFs individuais
        for idx, (paginas, texto) in enumerate(memoriais, 1):
            # Procurar Quadra e Lote
            quadra = re.search(r"Quadra:\s*(\d+)", texto)
            lote = re.search(r"Lote:\s*([A-Za-z0-9]+)", texto)

            quadra_num = quadra.group(1) if quadra else "XX"

            if lote:
                lote_num = lote.group(1)
            else:
                # Procurar padrões alternativos
                ar = re.search(r"ÁREA REMANESCENTE\s*-\s*(\d+)", texto, re.IGNORECASE)
                ap1 = re.search(r"ÁREA PÚBLICA\s*-\s*(\d+)", texto, re.IGNORECASE)
                ap2 = re.search(r"A\.P\s*-\s*(\d+)", texto, re.IGNORECASE)

                if ar:
                    lote_num = f"ar{ar.group(1)}"
                elif ap1:
                    lote_num = f"ap{ap1.group(1)}"
                elif ap2:
                    lote_num = f"ap{ap2.group(1)}"
                else:
                    lote_num = f"{idx:02d}"  # fallback sequencial

            # Nome do PDF final
            nome_pdf = f"nvl_min_mem_{quadra_num}_{lote_num}_r01.pdf"
            caminho_saida = os.path.join(output_dir, nome_pdf)

            # Criar novo PDF apenas com essas páginas
            novo = fitz.open()
            for p in paginas:
                novo.insert_pdf(doc, from_page=p, to_page=p)
            novo.save(caminho_saida)
            novo.close()

            print(f"✅ Criado: {caminho_saida}")

        doc.close()
        messagebox.showinfo("Concluído", "Todos os memoriais foram processados com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro inesperado", str(e))


if __name__ == "__main__":
    # 🖱️ Janela para selecionar o PDF
    Tk().withdraw()
    arquivo_pdf = filedialog.askopenfilename(
        title="Selecione o PDF de memoriais",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )

    if arquivo_pdf:
        processar_pdf(arquivo_pdf)
    else:
        messagebox.showwarning("Aviso", "Nenhum arquivo foi selecionado.")
