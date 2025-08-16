import os
import zipfile
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import pandas as pd
import re
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image as PILImage

def extrair_zip(zip_path, destino):
    if os.path.exists(destino):
        shutil.rmtree(destino)
    os.makedirs(destino, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destino)

def extrair_mensagens_imagens(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        texto = f.read()
    padrao = re.compile(
        r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2}) - (.*?): \u200e?(IMG-[\d\-WA]+\.jpg|STK-[\d\-WA]+\.webp) \(arquivo anexado\)\n(.*?)(?=\n\d{2}/\d{2}/\d{4} \d{2}:\d{2} -|$)",
        re.DOTALL
    )
    resultados = []
    for match in padrao.finditer(texto):
        data, autor, imagem, comentario = match.groups()
        resultados.append({
            "Data": data,
            "Autor": autor.strip(),
            "Imagem": imagem.strip(),
            "Comentário": comentario.strip()
        })
    return resultados

def gerar_excel(mensagens, destino):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    folder_path = r"C:\Users\IgorPimentaGavaJoão\Downloads\08.08.2025"
    df = pd.DataFrame(mensagens)
    df["Extension"] = ".jpg"
    df["Date accessed"] = now
    df["Date modified"] = now
    df["Folder Path"] = folder_path
    df["Data de envio"] = df["Data"]
    df["Name"] = df["Imagem"]
    df["Date created"] = df["Data"]
    df.rename(columns={"Comentário": "Comentário", "Autor": "Autor da legenda"}, inplace=True)
    colunas = ["Name", "Extension", "Date accessed", "Date modified",
               "Comentário", "Autor da legenda", "Date created", "Folder Path", "Data de envio"]
    df = df[colunas]
    df.to_excel(destino, index=False)

def gerar_pdf(mensagens, pasta_imgs, destino_pdf):
    from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Paragraph, PageBreak, Table, TableStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas as pdf_canvas
    from PIL import Image as PILImage

    class FooterCanvas(pdf_canvas.Canvas):
        def __init__(self, *args, **kwargs):
            pdf_canvas.Canvas.__init__(self, *args, **kwargs)
        def showPage(self):
            self.__footer()
            pdf_canvas.Canvas.showPage(self)
        def save(self):
            self.__footer()
            pdf_canvas.Canvas.save(self)
        def __footer(self):
            page_num = self.getPageNumber()
            self.setFont("Helvetica", 9)
            self.drawRightString(A4[0] - 20, 15, f"Página {page_num}")

    doc = SimpleDocTemplate(destino_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle(
        name="Normal",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        spaceAfter=2
    )
    style_header = ParagraphStyle(
        name="Header",
        fontName="Helvetica-Bold",
        fontSize=16,
        alignment=1,
        spaceAfter=12
    )
    elements = []
    elements.append(Paragraph("Relatório Fotográfico WhatsApp", style_header))

    fotos_por_linha = 3
    linhas_por_pagina = 4
    fotos_por_pagina = fotos_por_linha * linhas_por_pagina
    largura_img = 80
    altura_img = 80
    grid = []
    linha = []
    count = 0
    for idx, msg in enumerate(mensagens):
        img_path = None
        for root, _, files in os.walk(pasta_imgs):
            for f in files:
                if f == msg["Imagem"]:
                    img_path = os.path.join(root, f)
                    break
        if not img_path:
            continue
        img = Image(img_path, width=largura_img, height=altura_img)
        legenda = Paragraph(f"<b>{msg['Autor']}</b><br/>{msg['Data']}<br/>{msg['Comentário']}", style_normal)
        cell = [img, legenda]
        linha.append(cell)
        count += 1
        if len(linha) == fotos_por_linha:
            grid.append(linha)
            linha = []
        if count % fotos_por_pagina == 0 and grid:
            t = Table(grid, colWidths=[A4[0]/fotos_por_linha-20]*fotos_por_linha)
            t.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
            ]))
            elements.append(t)
            elements.append(PageBreak())
            grid = []
    if linha:
        grid.append(linha)
    if grid:
        t = Table(grid, colWidths=[A4[0]/fotos_por_linha-20]*fotos_por_linha)
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t)
    doc.build(elements, canvasmaker=FooterCanvas)

def exportar_zip(arquivos, zip_destino):
    with zipfile.ZipFile(zip_destino, "w") as z:
        for path in arquivos:
            z.write(path, arcname=os.path.basename(path))

def processar(zip_path, opcao):
    pasta_temp = "temp_conversa"
    extrair_zip(zip_path, pasta_temp)

    txt_file = next((os.path.join(root, f)
                     for root, _, files in os.walk(pasta_temp)
                     for f in files if f.endswith(".txt")), None)
    if not txt_file:
        return None, "Arquivo de conversa .txt não encontrado."

    mensagens = extrair_mensagens_imagens(txt_file)
    if not mensagens:
        return None, "Nenhuma imagem com comentário encontrada."

    os.makedirs("saida", exist_ok=True)

    if opcao == "excel":
        caminho_excel = "saida/relatorio_formatado.xlsx"
        gerar_excel(mensagens, caminho_excel)
        zip_final = "saida/relatorio_excel.zip"
        exportar_zip([caminho_excel], zip_final)
        return zip_final, None
    else:
        caminho_pdf = "saida/relatorio_fotografico.pdf"
        gerar_pdf(mensagens, pasta_temp, caminho_pdf)
        zip_final = "saida/relatorio_pdf.zip"
        exportar_zip([caminho_pdf], zip_final)
        return zip_final, None

# --- INTERFACE TKINTER ---
def abrir_arquivo():
    file_path = filedialog.askopenfilename(filetypes=[("ZIP Files", "*.zip")])
    if file_path:
        entrada_path.set(file_path)
        status.set("Arquivo carregado. Pronto para gerar relatório.")

def executar():
    status.set("Processando...")
    root.update_idletasks()
    zip_path = entrada_path.get()
    tipo = var_tipo.get()
    pasta_temp = "temp_conversa"
    extrair_zip(zip_path, pasta_temp)
    txt_file = next((os.path.join(root, f)
                     for root, _, files in os.walk(pasta_temp)
                     for f in files if f.endswith(".txt")), None)
    if not txt_file:
        messagebox.showerror("Erro", "Arquivo de conversa .txt não encontrado.")
        status.set("")
        return
    mensagens = extrair_mensagens_imagens(txt_file)
    if not mensagens:
        messagebox.showerror("Erro", "Nenhuma imagem com comentário encontrada.")
        status.set("")
        return
    if tipo == "excel":
        destino = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if destino:
            gerar_excel(mensagens, destino)
            messagebox.showinfo("Sucesso", f"Relatório gerado: {destino}")
            os.startfile(os.path.abspath(destino))
    else:
        destino = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if destino:
            gerar_pdf(mensagens, pasta_temp, destino)
            messagebox.showinfo("Sucesso", f"Relatório gerado: {destino}")
            os.startfile(os.path.abspath(destino))
    status.set("Concluído.")

root = tk.Tk()
root.title("Gerador de Relatório WhatsApp")
root.geometry("480x320")

entrada_path = tk.StringVar()
status = tk.StringVar()
var_tipo = tk.StringVar(value="excel")

tk.Label(root, text="Arquivo ZIP da conversa:").pack(pady=5)
tk.Entry(root, textvariable=entrada_path, width=60).pack()
tk.Button(root, text="Selecionar Arquivo", command=abrir_arquivo).pack(pady=5)

tk.Label(root, text="Formato do relatório:").pack()
tk.Radiobutton(root, text="Excel", variable=var_tipo, value="excel").pack()
tk.Radiobutton(root, text="PDF Fotográfico", variable=var_tipo, value="pdf").pack()

tk.Button(root, text="Gerar Relatório", command=executar, bg="green", fg="white").pack(pady=10)

tk.Label(root, textvariable=status, fg="blue").pack(pady=10)

root.mainloop()
