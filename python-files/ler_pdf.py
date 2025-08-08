import os
import time
import math
import re
import unicodedata
from datetime import timedelta
import pdfplumber
import pandas as pd
from tkinter import (
    Tk, Toplevel, filedialog, Label, Entry, Button, StringVar, ttk, messagebox, Frame, Scrollbar, VERTICAL, HORIZONTAL, RIGHT, LEFT, Y, X, BOTH, BOTTOM
)

# -------------------------
# Utilitários
# -------------------------
def normalize_text(s: str) -> str:
    """Minusculas, remover acentos e colapsar espaços."""
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = " ".join(s.split())
    return s.strip().lower()

def parse_pages_input(pages_str: str, page_count: int):
    """Converte string tipo '1,3,5' ou '2-6' em lista [1,3,5] (1-indexed)."""
    pages_str = pages_str.strip()
    if pages_str == "":
        return list(range(1, page_count + 1))
    paginas = set()
    for parte in pages_str.split(","):
        parte = parte.strip()
        if not parte:
            continue
        if "-" in parte:
            try:
                inicio, fim = map(int, parte.split("-"))
                if inicio <= fim:
                    for p in range(inicio, fim + 1):
                        if 1 <= p <= page_count:
                            paginas.add(p)
            except Exception:
                continue
        else:
            if parte.isdigit():
                p = int(parte)
                if 1 <= p <= page_count:
                    paginas.add(p)
    return sorted(paginas)

def cluster_rows_by_y(words, y_tol=6):
    """Agrupa palavras (cada word tem 'top' e 'x0') em linhas por proximidade vertical."""
    if not words:
        return []
    # words já esperadas ordenadas por top
    rows = []
    current = [words[0]]
    for w in words[1:]:
        if abs(w.get("top", 0) - current[-1].get("top", 0)) <= y_tol:
            current.append(w)
        else:
            # finalizar grupo atual
            rows.append(sorted(current, key=lambda x: x.get("x0", 0)))
            current = [w]
    rows.append(sorted(current, key=lambda x: x.get("x0", 0)))
    return rows

# -------------------------
# Função para detectar e remover linhas finais que devem be ignoradas
# -------------------------
def is_ignore_line(text):
    text_norm = normalize_text(text)
    # frases ou padrões a ignorar (podem ser expandidos)
    patterns = [
        r"cif-aft emitente",
        r"impresso na versao nº",
        r"folha nº \d+\/\d+",
        r"debito mensal do fgts por empregado",
        r"ndfc \d+\.\d+\.\d+",
    ]
    for p in patterns:
        if re.search(p, text_norm):
            return True
    return False

# -------------------------
# Extrair data MM/AAAA próxima ao cabeçalho
# -------------------------
def extract_date_near_header(page, header_top=None, x0=None, x1=None):
    """Extrai data no formato MM/AAAA próxima ao cabeçalho, alinhada com a primeira coluna."""
    words = page.extract_words()
    date_pattern = r"\b(0?[1-9]|1[0-2])\/\d{4}\b"
    date_str = ""
    
    if header_top is not None and x0 is not None and x1 is not None:
        # Procurar data acima do cabeçalho, alinhada com a primeira coluna (até 150 unidades acima)
        candidates = []
        for w in words:
            text = w.get("text", "")
            top = w.get("top", 0)
            x_center = (w.get("x0", 0) + w.get("x1", 0)) / 2
            match = re.search(date_pattern, text)
            if match and top < header_top and top >= header_top - 150 and x0 <= x_center <= x1:
                candidates.append((top, match.group(0)))
        # Escolher a data mais próxima do cabeçalho (maior top)
        if candidates:
            date_str = max(candidates, key=lambda x: x[0])[1]
    else:
        # Fallback: procurar a primeira data na página
        for w in words:
            text = w.get("text", "")
            match = re.search(date_pattern, text)
            if match:
                date_str = match.group(0)
                break
    return date_str

# -------------------------
# Extrair dados de tabelas detectadas
# -------------------------
def extract_from_table(table, titles_norm, titles_original, header_indices=None, page=None):
    """
    Extrai dados de uma tabela, identificando o cabeçalho com base nos títulos normalizados
    ou usando índices de colunas fornecidos para páginas sem cabeçalho.
    Retorna (resultados, header_indices, date_str).
    """
    results = []
    new_header_indices = header_indices if header_indices is not None else {}
    date_str = ""
    
    if not table:
        return results, new_header_indices, date_str

    # Procurar a linha do cabeçalho, se não fornecida
    header_row_idx = None
    for row_idx, row in enumerate(table):
        if not row:
            continue
        # Normalizar cada célula da linha
        row_norm = [normalize_text(cell) if cell else "" for cell in row]
        # Verificar se todos os títulos esperados estão na linha
        found_titles = {t: None for t in titles_norm}
        for col_idx, cell_norm in enumerate(row_norm):
            for t in titles_norm:
                if t and (t == cell_norm or t in cell_norm):
                    found_titles[t] = col_idx
        if all(found_titles[t] is not None for t in titles_norm):
            new_header_indices = {t: found_titles[t] for t in titles_norm}
            header_row_idx = row_idx
            # Extrair data acima da primeira coluna, se página fornecida
            if page is not None:
                header_top = None
                header_x0 = None
                header_x1 = None
                first_col_idx = new_header_indices.get(titles_norm[0])
                if first_col_idx is not None and first_col_idx < len(row):
                    cell = row[first_col_idx]
                    if cell:
                        words = page.extract_words()
                        for w in words:
                            if normalize_text(w.get("text", "")) == normalize_text(cell):
                                header_top = w.get("top", 0)
                                header_x0 = w.get("x0", 0)
                                header_x1 = w.get("x1", 0)
                                break
                if header_top and header_x0 and header_x1:
                    date_str = extract_date_near_header(page, header_top, header_x0, header_x1)
            break
    else:
        # Se não encontrou cabeçalho e não tem header_indices, retorna vazio
        if not new_header_indices:
            return results, new_header_indices, date_str

    # Determinar a linha inicial (após cabeçalho ou início da tabela)
    start_row = 0
    if header_indices is None:
        start_row = header_row_idx + 1

    # Coletar linhas da tabela
    for row in table[start_row:]:
        if not row:
            continue
        # Ignorar linhas com menos células que o esperado
        if len(row) < max(new_header_indices.values(), default=0) + 1:
            continue
        # Montar dicionário para a linha
        row_vals = {}
        any_cell = False
        for orig, tnorm in zip(titles_original, titles_norm):
            col_idx = new_header_indices.get(tnorm)
            if col_idx is not None and col_idx < len(row):
                cell_value = row[col_idx] if row[col_idx] is not None else ""
                row_vals[orig] = cell_value.strip()
                if cell_value.strip():
                    any_cell = True
            else:
                row_vals[orig] = ""
        # Ignorar linhas vazias ou com padrões de exclusão
        full_line_text = " ".join(row_vals.get(col, "") for col in titles_original)
        if not any_cell or is_ignore_line(full_line_text):
            continue
        results.append(row_vals)

    return results, new_header_indices, date_str

# -------------------------
# Estratégia fallback usando palavras (extract_words) adaptada para pegar nomes completos na 1ª coluna
# -------------------------
def extract_from_words(page, titles_norm, titles_original, header_centers=None):
    """
    Detecta cabeçalhos por palavras (mesma linha vertical) ou usa centros fornecidos,
    depois coleta linhas abaixo por proximidade vertical e coloca palavras nas colunas
    com base na proximidade horizontal ao centro do cabeçalho.
    Junta palavras próximas na 1ª coluna para formar nomes completos.
    Retorna uma lista de (resultados, header_centers, date_str) para cada cabeçalho encontrado.
    """
    all_results = []
    
    words = page.extract_words()  # cada item tem text, x0, x1, top, bottom
    if not words:
        return [( [], [], "" )]

    # normalizar e calcular centros
    valid_words = []
    for w in words:
        w["text_norm"] = normalize_text(w.get("text", ""))
        try:
            w["x0"] = float(w.get("x0", 0))
            w["x1"] = float(w.get("x1", 0))
            w["top"] = float(w.get("top", 0))
            w["bottom"] = float(w.get("bottom", 0))
        except Exception:
            continue
        w["x_center"] = (w["x0"] + w["x1"]) / 2
        w["y_center"] = (w["top"] + w["bottom"]) / 2
        valid_words.append(w)

    words = valid_words

    # Procurar cabeçalho, se não fornecido
    if header_centers is None:
        # construir lista de ocorrências por título
        occs = {t: [] for t in titles_norm}
        for w in words:
            for t in titles_norm:
                if t and (w["text_norm"] == t or t in w["text_norm"]):
                    occs[t].append(w)

        # procurar combinações onde todas as titles aparecem na mesma linha (top parecido)
        header_candidates = []
        if any(occs.values()):
            base_title = titles_norm[0]
            base_list = occs.get(base_title, [])
            header_y_tol = 7  # tolerância vertical para definir "mesma linha"
            for base in base_list:
                base_top = base["top"]
                candidate = {base_title: base}
                ok = True
                for t in titles_norm[1:]:
                    choices = occs.get(t, [])
                    if not choices:
                        ok = False
                        break
                    best = min(choices, key=lambda x: abs(x["top"] - base_top))
                    if abs(best["top"] - base_top) <= header_y_tol:
                        candidate[t] = best
                    else:
                        ok = False
                        break
                if ok:
                    header_candidates.append(candidate)

        # deduplicar header candidates por top médio
        unique_headers = []
        seen_tops = []
        for c in header_candidates:
            mean_top = sum(v["top"] for v in c.values()) / len(c)
            if not any(abs(mean_top - s) < 5 for s in seen_tops):
                unique_headers.append((mean_top, c))
                seen_tops.append(mean_top)
    else:
        # Usar header_centers fornecido
        unique_headers = [(0, None)]  # Dummy header para processar dados

    # Processar cada cabeçalho encontrado na página
    for mean_top, header in unique_headers if header_centers is None else [(0, None)]:
        results = []
        centers = header_centers if header_centers is not None else []
        date_str = ""
        if header is not None:
            centers = []
            for orig, tnorm in zip(titles_original, titles_norm):
                w = header.get(tnorm)
                centers.append(w["x_center"] if w else None)
            header_top = mean_top
            # Extrair data acima da primeira coluna (base_title)
            base_title = titles_norm[0]
            base_word = header.get(base_title)
            if base_word:
                base_x0 = base_word["x0"]
                base_x1 = base_word["x1"]
                base_top = base_word["top"]
                date_str = extract_date_near_header(page, base_top, base_x0, base_x1)
        new_header_centers = centers

        # palavras abaixo do header (ou todas se não houver header)
        data_words = [w for w in words if header_centers is not None or w["y_center"] > mean_top + 1]
        if not data_words:
            all_results.append((results, new_header_centers, date_str))
            continue
        data_words = sorted(data_words, key=lambda x: (x["y_center"], x["x_center"]))

        # agrupar por linha (y)
        rows = cluster_rows_by_y(data_words, y_tol=6)

        # Calcular largura de coluna: metade da menor distância entre centros
        valid_centers = [c for c in centers if c is not None]
        col_width = 50
        if len(valid_centers) >= 2:
            dists = [abs(b - a) for a, b in zip(valid_centers, valid_centers[1:])]
            if dists:
                col_width = max(20, min(dists) / 2)

        consecutive_empty = 0
        for row_words in rows:
            row_vals = {}
            any_cell = False

            # 1ª coluna: juntar palavras próximas horizontalmente
            first_col_center = centers[0] if centers else None
            if first_col_center is not None:
                row_words_sorted = sorted(row_words, key=lambda w: w["x0"])
                nome_palavras = []
                last_x1 = None
                for w in row_words_sorted:
                    if (last_x1 is None and abs(w["x_center"] - first_col_center) <= col_width * 2) or \
                       (last_x1 is not None and w["x0"] - last_x1 <= col_width):
                        nome_palavras.append(w["text"])
                        last_x1 = w["x1"]
                nome_completo = " ".join(nome_palavras).strip()
                row_vals[titles_original[0]] = nome_completo
                if nome_completo:
                    any_cell = True
            else:
                row_vals[titles_original[0]] = ""

            # para as outras colunas, pegar palavra mais próxima do centro da coluna
            for orig, center in zip(titles_original[1:], centers[1:]):
                if center is None:
                    row_vals[orig] = ""
                    continue
                sel = [w for w in row_words if abs(w["x_center"] - center) <= col_width]
                if not sel:
                    if row_words:
                        nearest = min(row_words, key=lambda x: abs(x["x_center"] - center))
                        if abs(nearest["x_center"] - center) <= col_width * 2:
                            sel = [nearest]
                if sel:
                    text = " ".join(w["text"] for w in sorted(sel, key=lambda x: x["x_center"]))
                    row_vals[orig] = text.strip()
                    if text.strip():
                        any_cell = True
                else:
                    row_vals[orig] = ""

            # Ignorar linhas vazias
            if not any_cell:
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    break
                continue
            consecutive_empty = 0

            # Adicionar a coluna 'Data' com a data extraída
            row_vals["Data"] = date_str if date_str else ""

            # Ignorar linhas com textos específicos
            full_line_text = " ".join(row_vals.get(col, "") for col in titles_original)
            if is_ignore_line(full_line_text):
                continue

            results.append(row_vals)
            if len(results) > 5000:
                break

        all_results.append((results, new_header_centers, date_str))

    return all_results

# -------------------------
# Processamento principal
# -------------------------
def processar_pdf():
    arquivo = caminho_pdf.get()
    if not arquivo or not os.path.isfile(arquivo):
        messagebox.showerror("Erro", "Selecione um arquivo PDF válido.")
        return

    paginas_input = entrada_paginas.get().strip()
    titulos_input = entrada_titulos.get().strip()
    if not titulos_input:
        messagebox.showerror("Erro", "Informe os títulos para busca (separados por vírgula).")
        return

    titles_original = [t.strip() for t in titulos_input.split(",") if t.strip()]
    if not titles_original:
        messagebox.showerror("Erro", "Nenhum título válido informado.")
        return

    titles_norm = [normalize_text(t) for t in titles_original]

    try:
        inicio_proc = time.perf_counter()
        encontrados = []
        header_centers = None  # Para extract_from_words
        header_indices = None  # Para extract_from_table
        with pdfplumber.open(arquivo) as pdf:
            page_count = len(pdf.pages)
            paginas = parse_pages_input(paginas_input, page_count)
            if not paginas:
                messagebox.showerror("Erro", "Nenhuma página válida informada.")
                return

            total = len(paginas)
            progresso["maximum"] = total
            found_header_anywhere = False

            for i, num in enumerate(paginas, start=1):
                pg_idx = num - 1
                progresso["value"] = i
                root.update_idletasks()

                if pg_idx < 0 or pg_idx >= page_count:
                    continue
                page = pdf.pages[pg_idx]

                # Extrair tabelas detectadas (se houver)
                page_tables = []
                try:
                    page_tables = page.extract_tables() or []
                except Exception:
                    page_tables = []

                # Extrair dados de cada tabela na página
                for tbl in page_tables:
                    part, new_header_indices, date_str = extract_from_table(tbl, titles_norm, titles_original, header_indices, page)
                    if part:
                        for linha in part:
                            linha["Data"] = date_str if date_str else ""
                        encontrados.extend(part)
                        found_header_anywhere = True
                        if new_header_indices:
                            header_indices = new_header_indices

                # Extrair via fallback palavras
                words_results = extract_from_words(page, titles_norm, titles_original, header_centers)
                for part2, new_header_centers, date_str in words_results:
                    if part2:
                        for linha in part2:
                            linha["Data"] = date_str if date_str else ""
                        encontrados.extend(part2)
                        found_header_anywhere = True
                        if new_header_centers:
                            header_centers = new_header_centers

                elapsed = time.perf_counter() - inicio_proc
                remain = (elapsed / i) * (total - i) if i else 0
                percent = (i / total) * 100
                tempo_str.set(f"{percent:.1f}%  |  ETA: {str(timedelta(seconds=int(remain)))}  |  Elapsed: {str(timedelta(seconds=int(elapsed)))}")

        if not found_header_anywhere or not encontrados:
            messagebox.showinfo("Resultado", "Nenhum cabeçalho/dado correspondente encontrado nas páginas informadas.")
            tempo_str.set("")
            progresso["value"] = 0
            return

        # Organizar colunas, adicionando a nova coluna "Data" ao final se não existir
        cols = titles_original.copy()
        if "Data" not in cols:
            cols.append("Data")

        df = pd.DataFrame(encontrados)
        # Garantir todas as colunas estão presentes na ordem correta (preenchendo vazios)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        df = df[cols]
        df.fillna("", inplace=True)

        global tabela_final
        tabela_final = df

        messagebox.showinfo("Sucesso", f"{len(df)} registros encontrados. Mostrando pré-visualização.")
        show_preview(df)

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

# -------------------------
# Exportar CSV
# -------------------------
def exportar_csv():
    if 'tabela_final' not in globals() or tabela_final.empty:
        messagebox.showerror("Erro", "Nenhum dado para exportar.")
        return
    caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
    if caminho:
        tabela_final.to_csv(caminho, index=False, encoding="utf-8-sig")
        messagebox.showinfo("Exportado", f"Arquivo exportado: {caminho}")

# -------------------------
# Mostrar preview simples
# -------------------------
def show_preview(df: pd.DataFrame, max_rows=500):
    top = Toplevel(root)
    top.title("Pré-visualização - primeiras linhas")
    top.geometry("900x400")

    frame = Frame(top)
    frame.pack(fill=BOTH, expand=True)

    cols = list(df.columns)
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=120, anchor="w")

    vs = Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    hs = Scrollbar(frame, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
    vs.pack(side=RIGHT, fill=Y)
    hs.pack(side=BOTTOM, fill=X)
    tree.pack(side=LEFT, fill=BOTH, expand=True)

    for i, (_, row) in enumerate(df.iterrows()):
        if i >= max_rows:
            break
        vals = [row[c] for c in cols]
        tree.insert("", "end", values=vals)

    btn_frame = Frame(top)
    btn_frame.pack(fill=X, padx=6, pady=6)
    Button(btn_frame, text="Exportar CSV", command=exportar_csv).pack(side=LEFT, padx=6)

# -------------------------
# UI Principal
# -------------------------
root = Tk()
root.title("Leitor e Extrator de PDF - Melhorado")
root.geometry("640x360")
root.resizable(True, True)

caminho_pdf = StringVar()
tempo_str = StringVar()

Label(root, text="Arquivo PDF:").pack(anchor="w", padx=10, pady=(10, 2))
Entry(root, textvariable=caminho_pdf, width=90).pack(anchor="w", padx=10)
Button(root, text="Selecionar PDF", command=lambda: caminho_pdf.set(filedialog.askopenfilename(filetypes=[('PDF', '*.pdf')]))).pack(anchor="w", padx=10, pady=(4, 8))

Label(root, text="Páginas (ex: 1,3,5 ou 2-6) — vazio = todas:").pack(anchor="w", padx=10, pady=(6, 2))
entrada_paginas = Entry(root, width=40)
entrada_paginas.pack(anchor="w", padx=10)

Label(root, text="Títulos (separados por vírgula) — ex: Empregado, PIS, Admissão:").pack(anchor="w", padx=10, pady=(6, 2))
entrada_titulos = Entry(root, width=90)
entrada_titulos.pack(anchor="w", padx=10)

progresso = ttk.Progressbar(root, length=560)
progresso.pack(padx=10, pady=12)

Label(root, textvariable=tempo_str).pack(anchor="w", padx=10)

btn_frame = Frame(root)
btn_frame.pack(pady=6)
Button(btn_frame, text="Processar PDF", command=processar_pdf).pack(side=LEFT, padx=8)
Button(btn_frame, text="Exportar CSV (último resultado)", command=exportar_csv).pack(side=LEFT, padx=8)
Button(btn_frame, text="Sair", command=root.quit).pack(side=LEFT, padx=8)

root.mainloop()