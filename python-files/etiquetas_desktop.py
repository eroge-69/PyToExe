#!/usr/bin/env python3
"""
Aplicativo Desktop (tkinter) para dividir etiquetas em PDF.
- 2 etiquetas por página (corte VERTICAL: esquerda/direita)
  - Opcional: descartar 1/3 inferior de cada etiqueta (mantém 2/3 superiores)
- 4 etiquetas por página (grade 2x2)

Saída: novo PDF com 1 etiqueta por página, nome: <arquivo>_1porpagina.pdf

Requisitos:
  pip install PyMuPDF==1.26.4

Para gerar .exe (no Windows):
  pip install pyinstaller
  pyinstaller --onefile --windowed etiquetas_desktop.py

Autor: você ;)
"""

import os
import sys
import traceback
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_TITULO = "Dividir Etiquetas PDF (Desktop)"


def recortes_4_por_pagina(rect: fitz.Rect) -> list:
    w, h = rect.width, rect.height
    return [
        fitz.Rect(0, 0, w/2, h/2),            # superior esquerdo
        fitz.Rect(w/2, 0, w, h/2),            # superior direito
        fitz.Rect(0, h/2, w/2, h),            # inferior esquerdo
        fitz.Rect(w/2, h/2, w, h),            # inferior direito
    ]


def recortes_2_por_pagina_vertical(rect: fitz.Rect) -> list:
    w, h = rect.width, rect.height
    # Metades lado a lado (esquerda / direita)
    return [
        fitz.Rect(0, 0, w/2, h),              # esquerda
        fitz.Rect(w/2, 0, w, h),              # direita
    ]


def processar_pdf(entrada: str, etiquetas_por_pagina: int, descartar_um_terco_inferior: bool) -> str:
    """
    Processa o PDF de entrada e retorna o caminho do arquivo de saída gerado.
    - etiquetas_por_pagina: 2 (vertical) ou 4 (grade)
    - descartar_um_terco_inferior: se True e etiquetas_por_pagina==2, mantém só 2/3 superiores
    """
    if not entrada.lower().endswith('.pdf'):
        raise ValueError("Selecione um arquivo PDF válido.")
    if etiquetas_por_pagina not in (2, 4):
        raise ValueError("'etiquetas_por_pagina' deve ser 2 ou 4.")

    try:
        origem = fitz.open(entrada)
    except Exception as e:
        raise RuntimeError(f"Erro ao abrir PDF: {e}")

    destino = fitz.open()

    for pagina in origem:
        if etiquetas_por_pagina == 4:
            recortes = recortes_4_por_pagina(pagina.rect)
        else:  # 2
            recortes = recortes_2_por_pagina_vertical(pagina.rect)

        for recorte in recortes:
            rec = recorte
            if etiquetas_por_pagina == 2 and descartar_um_terco_inferior:
                # Mantém 2/3 superiores
                altura_util = recorte.height * (2/3)
                rec = fitz.Rect(recorte.x0, recorte.y0, recorte.x1, recorte.y0 + altura_util)

            nova = destino.new_page(width=rec.width, height=rec.height)
            nova.show_pdf_page(nova.rect, origem, pagina.number, clip=rec)

    saida = os.path.splitext(entrada)[0] + "_1porpagina.pdf"
    destino.save(saida)
    destino.close()
    origem.close()
    return saida


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITULO)
        self.geometry("640x360")
        self.minsize(560, 320)

        # Estado
        self.arquivo_pdf = tk.StringVar()
        self.etiquetas_por_pagina = tk.StringVar(value="2")
        self.descartar_um_terco = tk.BooleanVar(value=True)
        self.status_text = tk.StringVar(value="Selecione o PDF e a quantidade de etiquetas por página.")

        self._build_ui()

    def _build_ui(self):
        pad = 12
        container = ttk.Frame(self, padding=pad)
        container.pack(fill=tk.BOTH, expand=True)

        # Seleção de arquivo
        frm_arq = ttk.LabelFrame(container, text="Arquivo PDF")
        frm_arq.pack(fill=tk.X, expand=False, pady=(0, pad))

        row1 = ttk.Frame(frm_arq)
        row1.pack(fill=tk.X, padx=pad, pady=pad)

        ent = ttk.Entry(row1, textvariable=self.arquivo_pdf)
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
        btn_sel = ttk.Button(row1, text="Selecionar...", command=self._escolher_pdf)
        btn_sel.pack(side=tk.LEFT, padx=(pad, 0))

        # Opções
        frm_opt = ttk.LabelFrame(container, text="Opções")
        frm_opt.pack(fill=tk.X, expand=False, pady=(0, pad))

        row2 = ttk.Frame(frm_opt)
        row2.pack(fill=tk.X, padx=pad, pady=(pad, 6))
        ttk.Label(row2, text="Etiquetas por página:").pack(side=tk.LEFT)
        combo = ttk.Combobox(row2, textvariable=self.etiquetas_por_pagina, values=["2", "4"], width=5, state="readonly")
        combo.pack(side=tk.LEFT, padx=(8, 0))

        row3 = ttk.Frame(frm_opt)
        row3.pack(fill=tk.X, padx=pad, pady=(0, pad))
        ttk.Checkbutton(row3, text="Descartar 1/3 inferior (manter 2/3 superiores) - somente p/ 2 por página",
                        variable=self.descartar_um_terco).pack(side=tk.LEFT)

        # Ações
        frm_actions = ttk.Frame(container)
        frm_actions.pack(fill=tk.X)

        btn_proc = ttk.Button(frm_actions, text="Processar", command=self._processar)
        btn_proc.pack(side=tk.LEFT)

        btn_sair = ttk.Button(frm_actions, text="Sair", command=self.destroy)
        btn_sair.pack(side=tk.LEFT, padx=(pad, 0))

        # Status
        frm_status = ttk.Frame(container)
        frm_status.pack(fill=tk.BOTH, expand=True, pady=(pad, 0))
        ttk.Label(frm_status, textvariable=self.status_text, foreground="#374151", wraplength=600, justify=tk.LEFT).pack(anchor="w")

        rodape = ttk.Label(container, text="SEM GALANTIA, COMPLO PORQUE QUIS!", foreground="#6b7280")
        rodape.pack(side=tk.BOTTOM, anchor="center", pady=(pad, 0))

    def _escolher_pdf(self):
        ini_dir = os.path.expanduser("~")
        filetypes = [("Arquivos PDF", "*.pdf"), ("Todos", "*.*")]
        fpath = filedialog.askopenfilename(title="Selecione o PDF", initialdir=ini_dir, filetypes=filetypes)
        if fpath:
            self.arquivo_pdf.set(fpath)

    def _processar(self):
        path = self.arquivo_pdf.get().strip()
        if not path:
            messagebox.showwarning("Atenção", "Selecione um arquivo PDF.")
            return
        try:
            etqs = int(self.etiquetas_por_pagina.get())
        except Exception:
            messagebox.showerror("Erro", "Quantidade de etiquetas inválida. Use 2 ou 4.")
            return

        self.status_text.set("Processando... Aguarde.")
        self.update_idletasks()

        try:
            saida = processar_pdf(
                entrada=path,
                etiquetas_por_pagina=etqs,
                descartar_um_terco_inferior=bool(self.descartar_um_terco.get())
            )
            self.status_text.set(f"Concluído! Arquivo gerado: {saida}")
            if messagebox.askyesno("Sucesso", f"PDF gerado com sucesso!\n\nAbrir pasta do arquivo?\n\n{saida}"):
                self._abrir_pasta(saida)
        except Exception as e:
            tb = traceback.format_exc()
            self.status_text.set(f"Falha ao processar. Detalhes no diálogo.")
            messagebox.showerror("Erro", f"Falha ao processar o PDF:\n{e}\n\nDetalhes:\n{tb}")

    def _abrir_pasta(self, arquivo: str):
        pasta = os.path.dirname(os.path.abspath(arquivo))
        try:
            if sys.platform.startswith('win'):
                os.startfile(pasta)  # type: ignore
            elif sys.platform == 'darwin':
                os.system(f"open '{pasta}'")
            else:
                os.system(f"xdg-open '{pasta}'")
        except Exception:
            pass


if __name__ == '__main__':
    app = App()
    app.mainloop()