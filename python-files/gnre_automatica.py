import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime, timedelta
import calendar


def proximo_dia_util(data):
    while data.weekday() >= 5:  # 5 = sábado, 6 = domingo
        data += timedelta(days=1)
    return data


def extrair_dados_cte(xml_path):
    ns = {'ns': 'http://www.portalfiscal.inf.br/cte'}
    tree = ET.parse(xml_path)
    root = tree.getroot()

    ide = root.find('.//ns:ide', ns)
    emit = root.find('.//ns:emit', ns)
    vPrest = root.find('.//ns:vPrest', ns)
    imp = root.find('.//ns:ICMSOutraUF', ns)

    nCT = ide.find('ns:nCT', ns).text
    data_emissao = ide.find('ns:dhEmi', ns).text
    data_emissao = datetime.strptime(data_emissao[:10], "%Y-%m-%d")

    vencimento = proximo_dia_util(datetime.now())
    if vencimento.date() == data_emissao.date():
        vencimento = data_emissao

    dados = {
        'cnpj_emitente': emit.find('ns:CNPJ', ns).text,
        'ie_emitente': emit.find('ns:IE', ns).text,
        'nome_emitente': emit.find('ns:xNome', ns).text,
        'uf_emitente': ide.find('ns:UFEnv', ns).text,
        'uf_destino': ide.find('ns:UFFim', ns).text,
        'data_emissao': data_emissao.strftime('%d/%m/%Y'),
        'valor_total': vPrest.find('ns:vTPrest', ns).text,
        'valor_icms': imp.find('ns:vICMSOutraUF', ns).text if imp is not None else "0.00",
        'nCT': nCT,
        'periodo_ref': f"{data_emissao.month:02d}/{data_emissao.year}",
        'data_vencimento': vencimento.strftime('%d/%m/%Y'),
        'n_controle': f'0000000{nCT.zfill(9)}',  # Exemplo de controle
    }

    return dados


def gerar_pdf_gnre(dados, pasta_destino):
    pdf_nome = f"GNRE_{dados['nCT']}.pdf"
    pdf_path = os.path.join(pasta_destino, pdf_nome)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, "GUIA NACIONAL DE RECOLHIMENTO DE TRIBUTOS ESTADUAIS (GNRE)")

    y -= 30
    c.setFont("Helvetica", 11)
    campos = [
        f"Razão Social: {dados['nome_emitente']}",
        f"CNPJ: {dados['cnpj_emitente']}  IE: {dados['ie_emitente']}  UF: {dados['uf_emitente']}",
        f"Nº Documento de Origem (CT-e): {dados['nCT']}",
        f"Período de Referência: {dados['periodo_ref']}",
        f"Nº de Controle: {dados['n_controle']}",
        f"Código da Receita: 100030  UF Favorecida: {dados['uf_destino']}",
        f"Valor Principal: R$ {dados['valor_icms']}",
        f"Multa: R$ 0,00",
        f"Juros: R$ 0,00",
        f"Atualização Monetária: R$ 0,00",
        f"Total a Recolher: R$ {dados['valor_icms']}",
        f"Data de Vencimento: {dados['data_vencimento']}",
        f"Informações Complementares: CT-e {dados['nCT']}",
    ]

    for campo in campos:
        c.drawString(30, y, campo)
        y -= 20

    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, 40, "Documento gerado automaticamente - Este PDF simula uma GNRE")

    c.save()


def selecionar_xml():
    arquivo = filedialog.askopenfilename(title="Selecione o XML do CT-e",
                                          filetypes=[("Arquivo XML", "*.xml")])
    if arquivo:
        try:
            dados = extrair_dados_cte(arquivo)
            pasta_destino = os.path.dirname(arquivo)
            gerar_pdf_gnre(dados, pasta_destino)
            messagebox.showinfo("Sucesso", f"GNRE gerada com sucesso na pasta:\n{pasta_destino}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar o XML:\n{str(e)}")


# Interface gráfica
janela = tk.Tk()
janela.title("Gerador de GNRE Automática")

janela.geometry("500x200")
janela.resizable(False, False)

lbl = tk.Label(janela, text="Selecione o XML do CT-e para gerar a GNRE", font=("Arial", 12))
lbl.pack(pady=20)

btn = tk.Button(janela, text="Selecionar XML e Gerar GNRE", font=("Arial", 12), command=selecionar_xml)
btn.pack(pady=10)

janela.mainloop()
