import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ----- TABELA DE CONTRIBUIÇÃO DIÁRIA -----
TIPOS = {
    "Permanente": {
        "residência padrão alto":      (160, 1),
        "residência padrão médio":     (130, 1),
        "residência padrão baixo":     (100, 1),
        "hotel (exceto banheira, lavanderia e cozinha)": (100, 1),
        "hotel (com cozinha e lavanderia, exceto banheira)": (240, 1),
        "hotel (com cozinha, lavanderia e banheira)": (300, 1),
        "alojamento provisório": (80, 1),
        "orfanato - asilo": (120, 1),
        "escola (internato)": (150, 1),
        "presídio": (240, 1),
        "quartel": (120, 1),
        "área rural": (100, 1)
    },
    "Temporário": {
        "fábrica em geral": (70, 0.30),
        "escritório": (50, 0.20),
        "edifício público ou comercial": (50, 0.20),
        "escola de meio período": (50, 0.20),
        "escola de período integral": (100, 0.30),
        "creche": (50, 0.20),
        "bar": (6, 0.10),
        "restaurante e similares": (25, 0.10),
        "cinema, teatro, templo, igreja etc.": (2, 0.02),
        "ambulatório": (25, 0.20),
        "estação ferroviária/rodoviária/metrov.": (25, 0.20),
        "sanitário público": (480, 4)
    }
}

def get_profundidade_util(volume):
    if volume <= 6:
        return 1.20, 2.20
    elif volume <= 10:
        return 1.50, 2.50
    else:
        return 1.80, 2.80

def atualizar_opcoes_tipo(event):
    tipo = combo_tipo.get()
    combo_local['values'] = list(TIPOS[tipo].keys())
    combo_local.current(0)

volume_ts = None
volume_fa = None
area_sumidouro = None
dim_tanque = {}
dim_filtro = {}
dim_sumidouro = {}

def calcular_volumes():
    global volume_ts, volume_fa, area_sumidouro, ultimo_texto_resultado
    try:
        n_pessoas = int(entry_pessoas.get())
        tempo_limpeza = int(entry_tempo_limpeza.get())
        temp_media = float(entry_temp_media.get())
        k_percol = float(entry_percolacao.get())
        tipo = combo_tipo.get()
        local = combo_local.get()
        
        q, lf = TIPOS[tipo][local]
        Q = n_pessoas * q  # L/dia

        Td = 24  # Tempo de detenção hidráulica
        Vu_TS = Q * Td / 24 / 1000  # m³

        # Acúmulo de lodo simplificado para exemplo
        if temp_media < 10:
            K = 94 if tempo_limpeza == 1 else 174
        elif temp_media < 20:
            K = 65 if tempo_limpeza == 1 else 145
        else:
            K = 57 if tempo_limpeza == 1 else 137
        V_lodo = n_pessoas * lf * K / 1000  # m³

        V_total_TS = Vu_TS + V_lodo

        Vu_FA = Vu_TS  # ou use outra regra se desejar

        taxa_aplic_diaria = k_percol  # L/m2.dia
        Area_sumidouro = Q / taxa_aplic_diaria

        # Armazena para uso nos botões de dimensões
        volume_ts = V_total_TS
        volume_fa = Vu_FA
        area_sumidouro = Area_sumidouro

        resultado = f"""
--- CÁLCULO DE VOLUMES/ÁREA ---

TANQUE SÉPTICO:
- Volume útil: {Vu_TS:.2f} m³
- Volume de lodo: {V_lodo:.2f} m³
- Volume total: {V_total_TS:.2f} m³

FILTRO ANAERÓBIO:
- Volume útil recomendado: {Vu_FA:.2f} m³

SUMIDOURO:
- Área de infiltração requerida: {Area_sumidouro:.2f} m²

Agora clique nos botões abaixo para obter as dimensões otimizadas de cada dispositivo!
        """
        ultimo_texto_resultado = resultado
        text_result.config(state='normal')
        text_result.delete(1.0, tk.END)
        text_result.insert(tk.END, resultado)
        text_result.config(state='disabled')

    except Exception as e:
        messagebox.showerror("Erro", f"Verifique os dados inseridos.\n{e}")

def otimizar_tanque():
    global volume_ts, dim_tanque, ultimo_texto_resultado
    if not volume_ts:
        messagebox.showwarning("Atenção", "Calcule primeiro os volumes/área!")
        return
    geom = simpledialog.askstring("Geometria", "Qual geometria do tanque séptico?\nDigite 'retangular' ou 'cilíndrico'")
    if not geom: return
    Vu = volume_ts
    prof_min, prof_max = get_profundidade_util(Vu)
    profundidade = round((prof_min + prof_max) / 2, 2)

    if geom.lower() == "retangular":
        largura = 0.80
        comprimento = Vu / (largura * profundidade)
        if comprimento/largura < 2:
            largura = comprimento / 2
            comprimento = Vu / (largura * profundidade)
        elif comprimento/largura > 4:
            comprimento = largura * 4
            largura = Vu / (comprimento * profundidade)
        resultado = (
            f"[TANQUE SÉPTICO RETANGULAR — OTIMIZADO]\n"
            f"Volume total: {Vu:.2f} m³\n"
            f"Profundidade útil (sugerida): {profundidade:.2f} m (Faixa: {prof_min}-{prof_max} m)\n"
            f"Largura interna: {largura:.2f} m (mín. 0,80 m)\n"
            f"Comprimento: {comprimento:.2f} m\n"
            f"Razão comprimento/largura: {comprimento/largura:.2f} (Norma: 2:1 a 4:1)\n"
        )
        dim_tanque.clear()
        dim_tanque.update({
            'geometria': 'retangular',
            'comprimento': comprimento,
            'largura': largura,
            'profundidade': profundidade,
            'volume': Vu
        })
    elif geom.lower() == "cilíndrico":
        diametro = max(1.10, math.sqrt((4 * Vu) / (math.pi * profundidade)))
        resultado = (
            f"[TANQUE SÉPTICO CILÍNDRICO — OTIMIZADO]\n"
            f"Volume total: {Vu:.2f} m³\n"
            f"Profundidade útil (sugerida): {profundidade:.2f} m (Faixa: {prof_min}-{prof_max} m)\n"
            f"Diâmetro interno: {diametro:.2f} m (mín. 1,10 m)\n"
        )
        dim_tanque.clear()
        dim_tanque.update({
            'geometria': 'cilíndrico',
            'diametro': diametro,
            'profundidade': profundidade,
            'volume': Vu
        })
    else:
        messagebox.showerror("Erro", "Geometria inválida.")
        return
    ultimo_texto_resultado = resultado
    text_result.config(state='normal')
    text_result.delete(1.0, tk.END)
    text_result.insert(tk.END, resultado)
    text_result.config(state='disabled')

def otimizar_filtro():
    global volume_fa, dim_filtro, ultimo_texto_resultado
    if not volume_fa:
        messagebox.showwarning("Atenção", "Calcule primeiro os volumes/área!")
        return
    Vu = volume_fa
    h = max(1.20, round((1.20 + 1.60) / 2, 2))
    h1 = 0.15
    h2 = 0.10
    H = h + h1 + h2
    diametro = 1.20  # Valor genérico para visualização
    resultado = (
        f"[FILTRO ANAERÓBIO — OTIMIZADO]\n"
        f"Volume útil: {Vu:.2f} m³\n"
        f"Diâmetro sugerido (visualização): {diametro:.2f} m\n"
        f"Altura útil (h): {h:.2f} m (Norma: ≥1,20 m)\n"
        f"Altura da calha coletora (h1): {h1:.2f} m\n"
        f"Altura sobressalente (h2): {h2:.2f} m\n"
        f"Altura total (H): {H:.2f} m\n"
    )
    dim_filtro.clear()
    dim_filtro.update({
        'diametro': diametro,
        'volume': Vu,
        'h': h,
        'h1': h1,
        'h2': h2,
        'H': H
    })
    ultimo_texto_resultado = resultado
    text_result.config(state='normal')
    text_result.delete(1.0, tk.END)
    text_result.insert(tk.END, resultado)
    text_result.config(state='disabled')

def otimizar_sumidouro():
    global area_sumidouro, dim_sumidouro, ultimo_texto_resultado
    if not area_sumidouro:
        messagebox.showwarning("Atenção", "Calcule primeiro os volumes/área!")
        return
    area = area_sumidouro
    diametro = max(1.00, round(math.sqrt((4 * area) / math.pi), 2))
    H = 2.0  # profundidade genérica
    resultado = (
        f"[SUMIDOURO — OTIMIZADO]\n"
        f"Área de infiltração: {area:.2f} m²\n"
        f"Diâmetro interno sugerido: {diametro:.2f} m (Norma: ≥1,00 m)\n"
        f"Profundidade visualizada no corte: {H:.2f} m\n"
    )
    dim_sumidouro.clear()
    dim_sumidouro.update({
        'area': area,
        'diametro': diametro,
        'H': H
    })
    ultimo_texto_resultado = resultado
    text_result.config(state='normal')
    text_result.delete(1.0, tk.END)
    text_result.insert(tk.END, resultado)
    text_result.config(state='disabled')

# --- DESENHOS NOVO PADRÃO ---
def desenhar_tanque_retangular_corte(L, h, nome_img):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot([0, L, L, 0, 0], [0, 0, h, h, 0], 'k', lw=2)
    ax.hlines(h*0.8, 0.1*L, 0.9*L, color='b', linestyle='dashed', lw=1.5, label='N.A.')
    ax.plot([-0.12*L, 0], [h*0.8, h*0.8], 'r', lw=2)
    ax.plot([L, L+0.12*L], [h*0.8, h*0.8], 'r', lw=2)
    ax.annotate('', xy=(0, h+0.09*h), xytext=(L, h+0.09*h), arrowprops=dict(arrowstyle='<->'))
    ax.text(L/2, h+0.13*h, f"L = {L:.2f} m", ha='center', va='bottom', fontsize=10)
    ax.annotate('', xy=(L+0.14*L, 0), xytext=(L+0.14*L, h), arrowprops=dict(arrowstyle='<->'))
    ax.text(L+0.17*L, h/2, f"h = {h:.2f} m", ha='left', va='center', fontsize=10, rotation=90)
    ax.set_xlim(-0.3*L, L+0.3*L)
    ax.set_ylim(-0.2*h, h+0.4*h)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(nome_img, bbox_inches='tight')
    plt.close()

def desenhar_tanque_retangular_planta(L, W, nome_img):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot([0, L, L, 0, 0], [0, 0, W, W, 0], 'k', lw=2)
    ax.add_patch(plt.Circle((0.25*L, 0.7*W), 0.1*W, fill=False, color='k', lw=2))
    ax.add_patch(plt.Circle((0.75*L, 0.7*W), 0.1*W, fill=False, color='k', lw=2))
    ax.annotate('', xy=(0, W+0.11*W), xytext=(L, W+0.11*W), arrowprops=dict(arrowstyle='<->'))
    ax.text(L/2, W+0.17*W, f"L = {L:.2f} m", ha='center', va='bottom', fontsize=10)
    ax.annotate('', xy=(-0.14*L, 0), xytext=(-0.14*L, W), arrowprops=dict(arrowstyle='<->'))
    ax.text(-0.18*L, W/2, f"W = {W:.2f} m", ha='right', va='center', fontsize=10, rotation=90)
    ax.set_xlim(-0.4*L, L+0.3*L)
    ax.set_ylim(-0.3*W, W+0.4*W)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(nome_img, bbox_inches='tight')
    plt.close()

def desenhar_tanque_cilindrico_corte(D, h, nome_img):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot([0, D, D, 0, 0], [0, 0, h, h, 0], 'k', lw=2)
    ax.hlines(h*0.8, 0.12*D, 0.88*D, color='b', linestyle='dashed', lw=1.5)
    ax.plot([-0.14*D, 0], [h*0.8, h*0.8], 'r', lw=2)
    ax.plot([D, D+0.14*D], [h*0.8, h*0.8], 'r', lw=2)
    ax.annotate('', xy=(0, h+0.09*h), xytext=(D, h+0.09*h), arrowprops=dict(arrowstyle='<->'))
    ax.text(D/2, h+0.13*h, f"D = {D:.2f} m", ha='center', va='bottom', fontsize=10)
    ax.annotate('', xy=(D+0.13*D, 0), xytext=(D+0.13*D, h), arrowprops=dict(arrowstyle='<->'))
    ax.text(D+0.17*D, h/2, f"h = {h:.2f} m", ha='left', va='center', fontsize=10, rotation=90)
    ax.set_xlim(-0.3*D, D+0.3*D)
    ax.set_ylim(-0.2*h, h+0.4*h)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(nome_img, bbox_inches='tight')
    plt.close()

def desenhar_tanque_cilindrico_planta(D, nome_img):
    fig, ax = plt.subplots(figsize=(4, 4))
    circle = plt.Circle((0, 0), D/2, fill=False, color='k', lw=2)
    ax.add_patch(circle)
    ax.add_patch(plt.Circle((0.18*D, 0.18*D), 0.12*D, fill=False, color='k', lw=2))
    ax.annotate('', xy=(-D/2, -0.7*D/2), xytext=(D/2, -0.7*D/2), arrowprops=dict(arrowstyle='<->'))
    ax.text(0, -0.85*D/2, f"D = {D:.2f} m", ha='center', va='top', fontsize=10)
    ax.set_xlim(-0.8*D, 0.8*D)
    ax.set_ylim(-0.8*D, 0.8*D)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(nome_img, bbox_inches='tight')
    plt.close()

def desenhar_filtro_corte(D, h, h1, h2, nome_img):
    H = h + h1 + h2
    fig, ax = plt.subplots(figsize=(3, 4))
    ax.plot([0, D, D, 0, 0], [0, 0, H, H, 0], 'k', lw=2)
    ax.hlines(h, 0, D, color='gray', linestyle='--', lw=1)
    ax.hlines(h+h1, 0, D, color='gray', linestyle='--', lw=1)
    ax.annotate('', xy=(D+0.11*D, 0), xytext=(D+0.11*D, h), arrowprops=dict(arrowstyle='<->'))
    ax.text(D+0.14*D, h/2, f"h = {h:.2f} m", ha='left', va='center', fontsize=10, rotation=90)
    ax.annotate('', xy=(D+0.11*D, h), xytext=(D+0.11*D, h+h1), arrowprops=dict(arrowstyle='<->'))
    ax.text(D+0.14*D, h+0.5*h1, f"h1 = {h1:.2f} m", ha='left', va='center', fontsize=9, rotation=90)
    ax.annotate('', xy=(D+0.11*D, h+h1), xytext=(D+0.11*D, H), arrowprops=dict(arrowstyle='<->'))
    ax.text(D+0.14*D, h+h1+0.5*h2, f"h2 = {h2:.2f} m", ha='left', va='center', fontsize=9, rotation=90)
    ax.annotate('', xy=(0, H+0.08*H), xytext=(D, H+0.08*H), arrowprops=dict(arrowstyle='<->'))
    ax.text(D/2, H+0.14*H, f"D = {D:.2f} m", ha='center', va='bottom', fontsize=10)
    ax.set_xlim(-0.3*D, D+0.5*D)
    ax.set_ylim(-0.2*H, H+0.3*H)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(nome_img, bbox_inches='tight')
    plt.close()

def desenhar_filtro_planta(D, nome_img):
    fig, ax = plt.subplots(figsize=(4, 4))
    circle = plt.Circle((0, 0), D/2, fill=False, color='k', lw=2)
    ax.add_patch(circle)
    ax.annotate('', xy=(-D/2, -0.7*D/2), xytext=(D/2, -0.7*D/2), arrowprops=dict(arrowstyle='<->'))
    ax.text(0, -0.85*D/2, f"D = {D:.2f} m", ha='center', va='top', fontsize=10)
    ax.set_xlim(-0.8*D, 0.8*D)
    ax.set_ylim(-0.8*D, 0.8*D)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(nome_img, bbox_inches='tight')
    plt.close()

def desenhar_sumidouro_corte(D, H, nome_img):
    fig, ax = plt.subplots(figsize=(3, 4))
    ax.plot([0, D, D, 0, 0], [0, 0, H, H, 0], 'k', lw=2)
    ax.annotate('', xy=(0, H+0.09*H), xytext=(D, H+0.09*H), arrowprops=dict(arrowstyle='<->'))
    ax.text(D/2, H+0.13*H, f"D = {D:.2f} m", ha='center', va='bottom', fontsize=10)
    ax.annotate('', xy=(D+0.13*D, 0), xytext=(D+0.13*D, H), arrowprops=dict(arrowstyle='<->'))
    ax.text(D+0.17*D, H/2, f"H = {H:.2f} m", ha='left', va='center', fontsize=10, rotation=90)
    ax.set_xlim(-0.3*D, D+0.5*D)
    ax.set_ylim(-0.2*H, H+0.3*H)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(nome_img, bbox_inches='tight')
    plt.close()

def desenhar_sumidouro_planta(D, nome_img):
    fig, ax = plt.subplots(figsize=(4, 4))
    circle = plt.Circle((0, 0), D/2, fill=False, color='k', lw=2)
    ax.add_patch(circle)
    ax.annotate('', xy=(-D/2, -0.7*D/2), xytext=(D/2, -0.7*D/2), arrowprops=dict(arrowstyle='<->'))
    ax.text(0, -0.85*D/2, f"D = {D:.2f} m", ha='center', va='top', fontsize=10)
    ax.set_xlim(-0.8*D, 0.8*D)
    ax.set_ylim(-0.8*D, 0.8*D)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(nome_img, bbox_inches='tight')
    plt.close()

# --- PDF RELATÓRIO MULTIPÁGINAS ---
def gerar_pdf_relatorio():
    if not dim_tanque or not dim_filtro or not dim_sumidouro:
        messagebox.showwarning("Atenção", "Calcule e otimize as dimensões dos 3 dispositivos antes de gerar o relatório!")
        return

    file_pdf = "Relatorio_Dimensionamento_Sistema_Esgoto.pdf"
    c = canvas.Canvas(file_pdf, pagesize=A4)
    width, height = A4

    # -------------- PÁGINA TANQUE SÉPTICO --------------
    c.setFont("Helvetica-Bold", 15)
    c.drawString(2*cm, height-2*cm, "Relatório de Dimensionamento — Sistema de Tratamento de Esgoto")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height-3*cm, "Tanque Séptico")
    y = height-4*cm
    c.setFont("Helvetica", 10)
    # Texto das dimensões
    text_lines = [
        f"Geometria: {dim_tanque.get('geometria', 'retangular').capitalize()}",
        f"Volume total: {dim_tanque.get('volume', 0):.2f} m³",
        f"Profundidade útil: {dim_tanque.get('profundidade', 0):.2f} m",
        f"Largura interna: {dim_tanque.get('largura', 0):.2f} m" if dim_tanque.get('geometria', 'retangular') == 'retangular' else f"Diâmetro interno: {dim_tanque.get('diametro', 0):.2f} m",
        f"Comprimento: {dim_tanque.get('comprimento', 0):.2f} m" if dim_tanque.get('geometria', 'retangular') == 'retangular' else "",
    ]
    for line in text_lines:
        c.drawString(2*cm, y, line)
        y -= 0.5*cm

    # Desenhos
    if dim_tanque.get('geometria', 'retangular') == 'retangular':
        desenhar_tanque_retangular_corte(dim_tanque['comprimento'], dim_tanque['profundidade'], "tq_ret_corte.png")
        desenhar_tanque_retangular_planta(dim_tanque['comprimento'], dim_tanque['largura'], "tq_ret_planta.png")
        c.drawImage("tq_ret_corte.png", 1*cm, y-9*cm, width=11*cm, preserveAspectRatio=True, mask='auto')
        c.drawImage("tq_ret_planta.png", 12*cm, y-9*cm, width=8*cm, preserveAspectRatio=True, mask='auto')
    else:
        desenhar_tanque_cilindrico_corte(dim_tanque['diametro'], dim_tanque['profundidade'], "tq_cil_corte.png")
        desenhar_tanque_cilindrico_planta(dim_tanque['diametro'], "tq_cil_planta.png")
        c.drawImage("tq_cil_corte.png", 1*cm, y-9*cm, width=11*cm, preserveAspectRatio=True, mask='auto')
        c.drawImage("tq_cil_planta.png", 12*cm, y-9*cm, width=8*cm, preserveAspectRatio=True, mask='auto')
    c.showPage()

    # -------------- PÁGINA FILTRO ANAERÓBIO --------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height-3*cm, "Filtro Anaeróbio")
    y = height-4*cm
    c.setFont("Helvetica", 10)
    text_lines = [
        f"Volume útil: {dim_filtro.get('volume', 0):.2f} m³",
        f"Diâmetro para visualização: {dim_filtro.get('diametro', 0):.2f} m",
        f"Altura útil: {dim_filtro.get('h', 0):.2f} m",
        f"Altura da calha coletora: {dim_filtro.get('h1', 0):.2f} m",
        f"Altura sobressalente: {dim_filtro.get('h2', 0):.2f} m",
        f"Altura total: {dim_filtro.get('H', 0):.2f} m",
    ]
    for line in text_lines:
        c.drawString(2*cm, y, line)
        y -= 0.5*cm

    img_y = 15*cm

    desenhar_filtro_corte(dim_filtro['diametro'], dim_filtro['h'], dim_filtro['h1'], dim_filtro['h2'], "filtro_corte.png")
    desenhar_filtro_planta(dim_filtro['diametro'], "filtro_planta.png")
    c.drawImage("filtro_corte.png", 1*cm, y-15*cm, width=8*cm, preserveAspectRatio=True, mask='auto')
    c.drawImage("filtro_planta.png", 10*cm, y-15*cm, width=7*cm, preserveAspectRatio=True, mask='auto')
    c.showPage()

    # -------------- PÁGINA SUMIDOURO --------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height-3*cm, "Sumidouro")
    y = height-4*cm
    c.setFont("Helvetica", 10)
    text_lines = [
        f"Área de infiltração: {dim_sumidouro.get('area', 0):.2f} m²",
        f"Diâmetro interno sugerido: {dim_sumidouro.get('diametro', 0):.2f} m",
        f"Profundidade visualizada no corte: {dim_sumidouro.get('H', 0):.2f} m",
    ]
    for line in text_lines:
        c.drawString(2*cm, y, line)
        y -= 0.5*cm
    
    img_y = 15*cm

    desenhar_sumidouro_corte(dim_sumidouro['diametro'], dim_sumidouro['H'], "sumidouro_corte.png")
    desenhar_sumidouro_planta(dim_sumidouro['diametro'], "sumidouro_planta.png")
    c.drawImage("sumidouro_corte.png", 1*cm, y-15*cm, width=8*cm, preserveAspectRatio=True, mask='auto')
    c.drawImage("sumidouro_planta.png", 10*cm, y-15*cm, width=7*cm, preserveAspectRatio=True, mask='auto')
    c.showPage()

    c.save()
    messagebox.showinfo("PDF Gerado", f"O relatório foi salvo como {file_pdf}.")

# -- INTERFACE --
cm = 28.35
root = tk.Tk()
root.title("Dimensionamento Completo — NBR 17076:2024")
frm = ttk.Frame(root, padding=20)
frm.grid()

ttk.Label(frm, text="Tipo de ocupação:").grid(column=0, row=0, sticky='w')
combo_tipo = ttk.Combobox(frm, values=list(TIPOS.keys()), state="readonly")
combo_tipo.current(0)
combo_tipo.grid(column=1, row=0)
combo_tipo.bind("<<ComboboxSelected>>", atualizar_opcoes_tipo)

ttk.Label(frm, text="Local/Atividade:").grid(column=0, row=1, sticky='w')
combo_local = ttk.Combobox(frm, values=list(TIPOS["Permanente"].keys()), state="readonly")
combo_local.current(0)
combo_local.grid(column=1, row=1)

ttk.Label(frm, text="Nº de pessoas/unidades:").grid(column=0, row=2, sticky='w')
entry_pessoas = ttk.Entry(frm)
entry_pessoas.grid(column=1, row=2)

ttk.Label(frm, text="Tempo entre limpezas (anos):").grid(column=0, row=3, sticky='w')
entry_tempo_limpeza = ttk.Entry(frm)
entry_tempo_limpeza.grid(column=1, row=3)

ttk.Label(frm, text="Temperatura média (°C):").grid(column=0, row=4, sticky='w')
entry_temp_media = ttk.Entry(frm)
entry_temp_media.grid(column=1, row=4)

ttk.Label(frm, text="Taxa percolação solo (L/m².dia):").grid(column=0, row=5, sticky='w')
entry_percolacao = ttk.Entry(frm)
entry_percolacao.grid(column=1, row=5)

ttk.Button(frm, text="Calcular Volumes/Área", command=calcular_volumes).grid(column=0, row=6, columnspan=2, pady=10)
ttk.Button(frm, text="Tanque Séptico Otimizado", command=otimizar_tanque).grid(column=0, row=7, padx=5, pady=5)
ttk.Button(frm, text="Filtro Anaeróbio Otimizado", command=otimizar_filtro).grid(column=1, row=7, padx=5, pady=5)
ttk.Button(frm, text="Sumidouro Otimizado", command=otimizar_sumidouro).grid(column=2, row=7, padx=5, pady=5)
ttk.Button(frm, text="Gerar Relatório PDF", command=gerar_pdf_relatorio).grid(column=0, row=8, columnspan=3, pady=10)

ultimo_texto_resultado = ""
text_result = tk.Text(frm, width=80, height=22, state='disabled')
text_result.grid(column=0, row=9, columnspan=3, pady=10)

atualizar_opcoes_tipo(None)
root.mainloop()
