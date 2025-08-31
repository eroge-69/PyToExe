import requests
import os
import re
import json
import csv
import math
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

from docx import Document
from docx.table import Table
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx2pdf import convert
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Tentar importar colorama para cores (opcional)
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

RESULTADO_DIR = "resultado_notas"
HISTORICO_CSV_PATH = "historico.csv"
ULTIMO_NUMERO_PATH = "ultimo_numero.txt"
MODELO_PATH = "nota_fatura_modelo.docx"

PADROES = {
    "pagamento": "(BB S/A): AG:  1504-0 | C/C:  22186-4",
    "favorecido": "TRINO LOCACOES E TERRAPLENAGEM",
    "naturaop": "Locação de Bens Moveis",
}

# Cores para a interface (se colorama não estiver disponível, usar códigos vazios)
if HAS_COLORAMA:
    C_TITLE = Fore.CYAN + Style.BRIGHT
    C_HEADER = Fore.YELLOW + Style.BRIGHT
    C_PROMPT = Fore.GREEN + Style.BRIGHT
    C_INPUT = Fore.WHITE + Style.BRIGHT
    C_INFO = Fore.BLUE
    C_WARN = Fore.RED + Style.BRIGHT
    C_SUCCESS = Fore.GREEN + Style.BRIGHT
    C_RESET = Style.RESET_ALL
else:
    C_TITLE = C_HEADER = C_PROMPT = C_INPUT = C_INFO = C_WARN = C_SUCCESS = C_RESET = ""


def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Imprime um cabeçalho formatado"""
    width = 60
    print(f"\n{C_TITLE}{'=' * width}")
    print(f"{title.center(width)}")
    print(f"{'=' * width}{C_RESET}\n")

def print_menu_item(key, description):
    """Imprime um item de menu formatado"""
    print(f"  {C_HEADER}[{key}]{C_RESET} {description}")

def print_success(message):
    """Imprime uma mensagem de sucesso"""
    print(f"{C_SUCCESS}✓ {message}{C_RESET}")

def print_warning(message):
    """Imprime uma mensagem de aviso"""
    print(f"{C_WARN}⚠ {message}{C_RESET}")

def print_error(message):
    """Imprime uma mensagem de erro"""
    print(f"{C_WARN}✗ {message}{C_RESET}")

def print_info(message):
    """Imprime uma mensagem informativa"""
    print(f"{C_INFO}ℹ {message}{C_RESET}")

def mostrar_loading(ativo, mensagem="Buscando informações do CNPJ"):
    """Exibe uma animação de loading enquanto busca informações"""
    chars = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    i = 0
    while ativo[0]:
        print(f"\r{C_INFO}{mensagem} {chars[i % len(chars)]}{C_RESET}", end="")
        i += 1
        time.sleep(0.1)
    print("\r" + " " * (len(mensagem) + 2) + "\r", end="")

def formatar_moeda(valor: float) -> str:
    """Formata valores monetários no padrão brasileiro"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_cno(cno: str) -> str:
    """Formata o CNO no padrão correto"""
    # Remove caracteres não numéricos
    cno_limpo = re.sub(r"\D", "", cno)
    
    # Aplica a formatação do CNO (exemplo: 123.456.789/0001-00)
    if len(cno_limpo) == 14:
        return f"{cno_limpo[:3]}.{cno_limpo[3:6]}.{cno_limpo[6:9]}/{cno_limpo[9:13]}-{cno_limpo[13:]}"
    elif len(cno_limpo) == 11:
        return f"{cno_limpo[:3]}.{cno_limpo[3:6]}.{cno_limpo[6:9]}-{cno_limpo[9:]}"
    else:
        return cno

def criar_modelo_basico():
    """Cria um modelo básico de nota fiscal se não existir"""
    doc = Document()
    
    # Configuração da página
    section = doc.sections[0]
    section.page_height = Inches(11.69)
    section.page_width = Inches(8.27)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    
    # Cabeçalho
    title = doc.add_heading('NOTA FISCAL', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Informações básicas
    doc.add_paragraph('Número: [nota_numero]')
    doc.add_paragraph('Data de Emissão: [emissao]')
    doc.add_paragraph('Data de Vencimento: [vencimento]')
    doc.add_paragraph('Favorecido: [favorecido]')
    doc.add_paragraph('Natureza da Operação: [naturaop]')
    doc.add_paragraph('Dados de Pagamento: [pagamento]')
    doc.add_paragraph('CNO da Obra: [cno_obra]')
    
    # Tabela de produtos
    table = doc.add_table(rows=1, cols=6)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Código'
    hdr_cells[1].text = 'Quantidade'
    hdr_cells[2].text = 'Descrição'
    hdr_cells[3].text = 'Aliq (%)'
    hdr_cells[4].text = 'Preço Unitário'
    hdr_cells[5].text = 'Preço Total'
    
    # Informações do tomador
    doc.add_paragraph('Tomador: [tomador]')
    doc.add_paragraph('CNPJ/CPF: [cnpj/cpf_tomador]')
    doc.add_paragraph('Endereço: [endereço_tomador]')
    doc.add_paragraph('Telefone: [telefone_tomador]')
    doc.add_paragraph('Inscrição Municipal/Estadual: [inscricao_estadual_tomador]')
    
    # Totais
    doc.add_paragraph('Deduções: [deducoes]')
    doc.add_paragraph('Total: [total_absoluto]')
    
    # Observações
    doc.add_paragraph('OBSERVAÇÕES: [observacao]')
    
    # Salvar o documento
    doc.save(MODELO_PATH)
    print_success(f"Modelo básico criado em: {MODELO_PATH}")

def ensure_dirs():
    if not os.path.exists(RESULTADO_DIR):
        os.makedirs(RESULTADO_DIR, exist_ok=True)
    
    if not os.path.exists(MODELO_PATH):
        criar_modelo_basico()

def ajustar_fonte_texto_longo(doc, max_caracteres=50, tamanho_minimo=6):
    """Ajusta o tamanho da fonte para textos muito longos em parágrafos"""
    for paragraph in doc.paragraphs:
        if len(paragraph.text) > max_caracteres:
            for run in paragraph.runs:
                if run.font.size and run.font.size.pt > Pt(tamanho_minimo):
                    run.font.size = Pt(max(Pt(tamanho_minimo).pt, run.font.size.pt - 2))

def ajustar_tamanho_pagina(doc):
    """Ajusta o tamanho da página baseado no conteúdo para manter uma única página"""
    # Calcular altura aproximada do conteúdo
    altura_total = 0
    for paragraph in doc.paragraphs:
        altura_total += len(paragraph.text) / 100
    
    for table in doc.tables:
        for row in table.rows:
            altura_total += 0.2
    
    # Ajustar altura da página se necessário
    section = doc.sections[0]
    altura_pagina = max(Inches(11.69), min(Inches(33.11), Inches(11.69 + (altura_total / 2))))
    section.page_height = altura_pagina
    
    return altura_pagina

def ajustar_tamanho_fonte(doc, tamanho=9):
    """Ajusta o tamanho da fonte em todo o documento para caber em uma página"""
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(tamanho)
    
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(tamanho)

def reduzir_espacamento(doc):
    """Reduz o espaçamento entre parágrafos para economizar espaço"""
    for paragraph in doc.paragraphs:
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.line_spacing = 1.0

def ler_ultimo_numero() -> str:
    ano_atual = datetime.now().year
    if not os.path.exists(ULTIMO_NUMERO_PATH):
        with open(ULTIMO_NUMERO_PATH, "w", encoding="utf-8") as f:
            f.write(f"{ano_atual}/0000")
    with open(ULTIMO_NUMERO_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()

def sugerir_proximo(ultimo: str) -> str:
    ano_atual = datetime.now().year
    try:
        ano, seq = ultimo.split("/")
        seq_num = int(seq)
    except Exception:
        ano, seq_num = str(ano_atual), 0
    if ano != str(ano_atual):
        seq_num = 0
    seq_num += 1
    return f"{ano_atual}/{seq_num:04d}"

def gravar_ultimo_numero(nota: str) -> None:
    with open(ULTIMO_NUMERO_PATH, "w", encoding="utf-8") as f:
        f.write(nota)

def mascarar_cnpj(cnpj: str) -> str:
    d = re.sub(r"\D", "", cnpj)
    if len(d) == 14:
        return f"{d[0:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:14]}"
    return cnpj

def mascarar_cpf(cpf: str) -> str:
    d = re.sub(r"\D", "", cpf)
    if len(d) == 11:
        return f"{d[0:3]}.{d[3:6]}.{d[6:9]}-{d[9:11]}"
    return cpf

def mascarar_cnpj_cpf(valor: str) -> Tuple[str, str]:
    d = re.sub(r"\D", "", valor)
    if len(d) == 14:
        return mascarar_cnpj(d), "CNPJ"
    elif len(d) == 11:
        return mascarar_cpf(d), "CPF"
    else:
        return valor, "DESCONHECIDO"

def mascarar_cep(cep: str) -> str:
    d = re.sub(r"\D", "", cep)
    if len(d) == 8:
        return f"{d[:5]}-{d[5:]}"
    return cep

def mascarar_telefone(tel: str) -> Tuple[str, str]:
    d = re.sub(r"\D", "", tel)
    if len(d) == 11:
        return f"({d[0:2]}) {d[2]}{d[3:7]}-{d[7:]}", "CELULAR"
    elif len(d) == 10:
        return f"({d[0:2]}) {d[2:6]}-{d[6:]}", "FIXO"
    elif len(d) == 9:
        return f"{d[0]}{d[1:5]}-{d[5:]}", "CELULAR"
    elif len(d) == 8:
        return f"{d[0:4]}-{d[4:]}", "FIXO"
    return tel, "DESCONHECIDO"

def mascarar_ie_im(valor: str) -> str:
    d = re.sub(r"\D", "", valor)
    if not d:
        return valor
    if len(d) <= 9:
        parts = []
        while d:
            parts.append(d[:3])
            d = d[3:]
        if len(parts) > 1:
            last = parts[-1]
            if len(last) >= 2:
                parts[-1] = f"{last[:-1]}-{last[-1:]}"
        return ".".join(parts)
    else:
        chunks = [d[i:i+3] for i in range(0, len(d)-2, 3)]
        tail = d[len(d)-2:]
        return ".".join(chunks) + "-" + tail

def mascarar_data(data_str: str) -> str:
    data_str = data_str.strip()
    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y"]:
        try:
            dt = datetime.strptime(data_str, fmt)
            return dt.strftime("%d/%m/%Y")
        except Exception:
            continue
    d = re.sub(r"\D", "", data_str)
    if len(d) == 8:
        try:
            dt = datetime.strptime(d, "%d%m%Y")
            return dt.strftime("%d/%m/%Y")
        except Exception:
            pass
    return data_str

def fetch_cnpj_sugestoes(cnpj: str) -> Dict[str, str]:
    d = re.sub(r"\D", "", cnpj)
    if len(d) != 14:
        return {}
    
    # Primeiro tentamos a API da ReceitaWS
    sugest = fetch_receitaws(d)
    
    # Buscar IE no CNPJ.biz
    ie = fetch_ie_from_cnpj_biz(d)
    if ie:
        sugest["ie"] = ie
    
    return sugest

def fetch_receitaws(cnpj: str) -> Dict[str, str]:
    """Busca informações na API da ReceitaWS"""
    url = f"https://receitaws.com.br/v1/cnpj/{cnpj}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'ERROR':
                print_warning("CNPJ não encontrado na base da ReceitaWS")
                return {}
            
            sugest = {}
            
            # Extrair dados da API
            if data.get('email'):
                sugest["email"] = data['email']
            
            if data.get('telefone'):
                sugest["telefone"] = data['telefone']
            
            # Construir endereço
            endereco_parts = []
            if data.get('logradouro'):
                endereco_parts.append(data['logradouro'])
            if data.get('numero'):
                endereco_parts.append(data['numero'])
            if data.get('complemento'):
                endereco_parts.append(data['complemento'])
            if data.get('bairro'):
                endereco_parts.append(data['bairro'])
            
            if endereco_parts:
                sugest["endereco"] = ", ".join(endereco_parts)
            
            if data.get('municipio'):
                sugest["cidade"] = data['municipio']
            
            if data.get('uf'):
                sugest["estado"] = data['uf']
            
            if data.get('cep'):
                sugest["cep"] = data['cep']
            
            return sugest
        else:
            print_warning(f"Erro na API ReceitaWS: {response.status_code}")
            return {}
    except Exception as e:
        print_warning(f"Falha na API ReceitaWS: {str(e)}")
        return {}

def fetch_cnpj_biz(cnpj: str) -> Dict[str, str]:
    """Fallback para buscar informações no site CNPJ.biz"""
    url = f"https://cnpj.biz/{cnpj}"
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=120000)
                
                # Aguardar elementos carregarem
                page.wait_for_selector("text=Logradouro", timeout=30000)
                
                html = page.content()
                browser.close()
                
            soup = BeautifulSoup(html, "lxml")
            sugest = {}

            # Buscar IE/IM
            ie_elements = soup.find_all('p')
            for p in ie_elements:
                if 'Inscrição Estadual' in p.text:
                    ie_b = p.find('b', class_='copy')
                    if ie_b:
                        sugest["ie"] = ie_b.get_text(strip=True)
                        break

            # Buscar telefone
            telefone_elements = soup.find_all('p')
            for p in telefone_elements:
                if 'Telefone' in p.text:
                    telefone_b = p.find('b', class_='copy')
                    if telefone_b:
                        sugest["telefone"] = telefone_b.get_text(strip=True)
                        break

            # Buscar CEP
            cep_elements = soup.find_all('p')
            for p in cep_elements:
                if 'CEP' in p.text:
                    cep_b = p.find('b', class_='copy')
                    if cep_b:
                        sugest["cep"] = cep_b.get_text(strip=True)
                        break

            # Buscar email
            email_elements = soup.find_all('p')
            for p in email_elements:
                if 'E-mail' in p.text:
                    email_b = p.find('b', class_='copy')
                    if email_b:
                        sugest["email"] = email_b.get_text(strip=True)
                        break

            # Buscar endereço completo
            endereco_parts = []
            
            # Logradouro
            for p in soup.find_all('p'):
                if 'Logradouro' in p.text:
                    logradouro_b = p.find('b', class_='copy')
                    if logradouro_b:
                        endereco_parts.append(logradouro_b.get_text(strip=True))
                        break
            
            # Complemento
            for p in soup.find_all('p'):
                if 'Complemento' in p.text:
                    complemento_b = p.find('b', class_='copy')
                    if complemento_b:
                        endereco_parts.append(complemento_b.get_text(strip=True))
                        break
            
            # Bairro
            for p in soup.find_all('p'):
                if 'Bairro' in p.text:
                    bairro_b = p.find('b', class_='copy')
                    if bairro_b:
                        endereco_parts.append(bairro_b.get_text(strip=True))
                        break
            
            if endereco_parts:
                sugest["endereco"] = ", ".join(endereco_parts)

            return sugest
            
        except Exception as e:
            print_warning(f"Tentativa {attempt + 1} no CNPJ.biz falhou: {str(e)}")
            if attempt < max_retries - 1:
                print_info("Tentando novamente em 5 segundos...")
                time.sleep(5)
            else:
                print_error("Todas as tentativas no CNPJ.biz falharam.")
                return {}
    
    return {}

def fetch_ie_from_cnpj_biz(cnpj: str) -> str:
    """Busca a Inscrição Estadual no site CNPJ.biz"""
    d = re.sub(r"\D", "", cnpj)
    if len(d) != 14:
        return ""
    
    url = f"https://cnpj.biz/{d}"
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=120000)
                
                # Aguardar elementos carregarem
                page.wait_for_selector("text=Informações de Registro", timeout=30000)
                
                html = page.content()
                browser.close()
                
            soup = BeautifulSoup(html, "lxml")
            
            # Buscar IE/IM - método específico para CNPJ.biz
            ie_elements = soup.find_all('p')
            for p in ie_elements:
                if 'Inscrição Estadual' in p.text:
                    ie_b = p.find('b', class_='copy')
                    if ie_b:
                        return ie_b.get_text(strip=True)
            
            return ""
            
        except Exception as e:
            print_warning(f"Tentativa {attempt + 1} para buscar IE falhou: {str(e)}")
            if attempt < max_retries - 1:
                print_info("Tentando novamente em 5 segundos...")
                time.sleep(5)
            else:
                print_error("Todas as tentativas para buscar IE falharam.")
                return ""
    
    return ""

def substituir_placeholders(doc: Document, variaveis: Dict[str, Any]) -> None:
    # Mapeamento de campos para compatibilidade com o modelo
    mapeamento_campos = {
        "inscricao_estadual_tomador": "inscricao_estadual_tomador",
        "observacao": "observacao"
    }
    
    for p in doc.paragraphs:
        for k, v in variaveis.items():
            if v is None: v = ""
            if isinstance(v, (int, float)):
                v = f"{v}"
            
            # Usar o nome do campo original se não houver mapeamento
            campo = mapeamento_campos.get(k, k)
            
            if f"[{campo}]" in p.text:
                inline = p.runs
                full_text = "".join(run.text for run in inline)
                full_text = full_text.replace(f"[{campo}]", str(v))
                if inline:
                    inline[0].text = full_text
                    for i in range(1, len(inline)):
                        inline[i].text = ""

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for k, v in variaveis.items():
                    if v is None: v = ""
                    if isinstance(v, (int, float)):
                        v = f"{v}"
                    
                    # Usar o nome do campo original se não houver mapeamento
                    campo = mapeamento_campos.get(k, k)
                    
                    if f"[{campo}]" in cell.text:
                        cell.text = cell.text.replace(f"[{campo}]", str(v))

def localizar_tabela_produtos(doc: Document) -> Optional[Table]:
    for table in doc.tables:
        headers = " ".join([c.text.strip().upper() for c in table.rows[0].cells])
        if ("CÓDIGO" in headers or "CÓDIGO" in headers.upper()) and "PREÇO TOTAL" in headers.upper():
            return table
    return None

def garantir_linhas_produtos(table: Table, total_linhas: int) -> None:
    atual = len(table.rows) - 1
    if total_linhas <= atual:
        return
    for _ in range(total_linhas - atual):
        table.add_row()

def coletar_itens() -> List[Dict[str, Any]]:
    while True:
        try:
            print(f"\n{C_PROMPT}Quantos produtos/itens deseja lançar?{C_RESET}")
            n = int(input(f"{C_INPUT}>> {C_RESET}"))
            if n <= 0:
                print_warning("Informe um número positivo.")
                continue
            break
        except ValueError:
            print_error("Digite um número válido.")
    
    itens = []
    ultimo = None
    
    for i in range(1, n + 1):
        print_header(f"Item {i} de {n}")
        
        if ultimo:
            print(f"{C_PROMPT}Duplicar do item anterior?{C_RESET} [{C_INFO}S{C_RESET}/{C_WARN}n{C_RESET}]")
            dup = input(f"{C_INPUT}>> {C_RESET}").strip().lower() or "s"
        else:
            dup = "n"
            
        if dup == "s":
            base = ultimo.copy()
            print(f"{C_PROMPT}Código{C_RESET} [{C_INFO}{base['codigo']}{C_RESET}]")
            codigo = input(f"{C_INPUT}>> {C_RESET}") or base['codigo']
            print(f"{C_PROMPT}Descrição{C_RESET} [{C_INFO}{base['descricao']}{C_RESET}]")
            desc = input(f"{C_INPUT}>> {C_RESET}") or base['descricao']
            print(f"{C_PROMPT}Quantidade{C_RESET} [{C_INFO}{base['quantidade']}{C_RESET}]")
            quant = input(f"{C_INPUT}>> {C_RESET}") or str(base['quantidade'])
            print(f"{C_PROMPT}Aliq (%){C_RESET} [{C_INFO}{base['aliq']}{C_RESET}]")
            aliq = input(f"{C_INPUT}>> {C_RESET}") or str(base['aliq'])
            print(f"{C_PROMPT}Preço unitário{C_RESET} [{C_INFO}{base['unitario']}{C_RESET}]")
            unita = input(f"{C_INPUT}>> {C_RESET}") or str(base['unitario'])
        else:
            print(f"{C_PROMPT}Código:{C_RESET}")
            codigo = input(f"{C_INPUT}>> {C_RESET}").strip()
            print(f"{C_PROMPT}Descrição:{C_RESET}")
            desc = input(f"{C_INPUT}>> {C_RESET}").strip()
            print(f"{C_PROMPT}Quantidade:{C_RESET}")
            quant = input(f"{C_INPUT}>> {C_RESET}").strip()
            print(f"{C_PROMPT}Aliq (%):{C_RESET}")
            aliq = input(f"{C_INPUT}>> {C_RESET}").strip()
            print(f"{C_PROMPT}Preço unitário:{C_RESET}")
            unita = input(f"{C_INPUT}>> {C_RESET}").strip()

        try:
            quantidade = float(str(quant).replace(",", "."))
        except:
            quantidade = 1.0
        try:
            aliqf = float(str(aliq).replace(",", "."))
        except:
            aliqf = 0.0
        try:
            unitario = float(str(unita).replace(",", "."))
        except:
            unitario = 0.0

        subtotal = quantidade * unitario
        total = subtotal * (1 + (aliqf/100.0))
        item = {
            "codigo": codigo,
            "descricao": desc,
            "quantidade": quantidade,
            "aliq": aliqf,
            "unitario": unitario,
            "total": total
        }
        itens.append(item)
        ultimo = item
        
        print_success(f"Item {i} adicionado: {desc} - {formatar_moeda(total)}")
    
    return itens

def preencher_tabela_produtos(table: Table, itens: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_linhas = max(len(itens), 7)
    garantir_linhas_produtos(table, total_linhas)
    variaveis = {}
    for idx, item in enumerate(itens, start=1):
        row = table.rows[idx]
        row.cells[0].text = item['codigo']
        row.cells[1].text = f"{item['quantidade']:.2f}".replace(".", ",")
        row.cells[2].text = item['descricao']
        row.cells[3].text = f"{item['aliq']:.2f}%".replace(".", ",")
        row.cells[4].text = formatar_moeda(item['unitario'])
        row.cells[5].text = formatar_moeda(item['total'])
        variaveis[f"código_{idx}"] = item['codigo']
        variaveis[f"quant_{idx}"] = f"{item['quantidade']:.2f}".replace(".", ",")
        variaveis[f"desc_{idx}"] = item['descricao']
        variaveis[f"alig_{idx}"] = f"{item['aliq']:.2f}%".replace(".", ",")
        variaveis[f"unita_{idx}"] = formatar_moeda(item['unitario'])
        variaveis[f"total_{idx}"] = formatar_moeda(item['total'])
    for idx in range(len(itens)+1, len(table.rows)):
        row = table.rows[idx]
        for c in row.cells:
            c.text = ""
    return variaveis

def somar_itens(itens: List[Dict[str, Any]]) -> float:
    return sum(x.get("total", 0.0) for x in itens)

def salvar_historico_csv(registro: Dict[str, Any]) -> None:
    file_exists = os.path.isfile(HISTORICO_CSV_PATH)
    with open(HISTORICO_CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        campos = ['nome_arquivo', 'tomador', 'nome_obra', 'valor']
        writer = csv.DictWriter(f, fieldnames=campos)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'nome_arquivo': registro.get('arquivo_pdf', ''),
            'tomador': registro.get('tomador', ''),
            'nome_obra': registro.get('nome_obra', ''),
            'valor': registro.get('total', '')
        })

def abrir_historico() -> None:
    if not os.path.exists(HISTORICO_CSV_PATH):
        print_warning("Nenhum histórico disponível.")
        return
    
    with open(HISTORICO_CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        historico = list(reader)
    
    if not historico:
        print_warning("Nenhum histórico disponível.")
        return
        
    print_header("HISTÓRICO DE NOTAS")
    for i, h in enumerate(historico, start=1):
        print(f"{C_HEADER}[{i}]{C_RESET} {h.get('nome_arquivo')} - {h.get('tomador')} - {h.get('nome_obra')} - {h.get('valor')}")
    
    try:
        print(f"\n{C_PROMPT}Escolha um para abrir (0 para sair):{C_RESET}")
        op = int(input(f"{C_INPUT}>> {C_RESET}"))
    except:
        return
        
    if op <= 0 or op > len(historico):
        return
        
    escolha = historico[op-1]
    caminho_pdf = escolha.get("nome_arquivo")
    
    if caminho_pdf and os.path.exists(caminho_pdf):
        try:
            os.startfile(caminho_pdf)
        except AttributeError:
            import subprocess, sys
            if sys.platform == "darwin":
                subprocess.call(["open", caminho_pdf])
            else:
                subprocess.call(["xdg-open", caminho_pdf])

def revisar_editar(variaveis: Dict[str, Any]) -> Dict[str, Any]:
    while True:
        print_header("REVISÃO DOS DADOS")
        for k, v in variaveis.items():
            if isinstance(v, float):
                print(f"{C_INFO}{k}: {formatar_moeda(v)}{C_RESET}")
            else:
                print(f"{C_INFO}{k}: {v}{C_RESET}")
                
        print(f"\n{C_PROMPT}Deseja alterar algum campo? (digite o nome da chave, ou ENTER para continuar):{C_RESET}")
        resp = input(f"{C_INPUT}>> {C_RESET}").strip()
        if not resp:
            return variaveis
        if resp in variaveis:
            print(f"{C_PROMPT}Novo valor para '{resp}':{C_RESET}")
            novo = input(f"{C_INPUT}>> {C_RESET}")
            variaveis[resp] = novo
        else:
            print_error("Chave não encontrada.")

def coletar_dados_principais() -> Dict[str, Any]:
    variaveis = {}
    
    print_header("DADOS PRINCIPAIS DA NOTA")
    
    ultimo = ler_ultimo_numero()
    sugest = sugerir_proximo(ultimo)
    print(f"{C_PROMPT}Sugestão de número da nota: {C_INFO}{sugest}{C_RESET}")
    print(f"{C_PROMPT}Digite o número da nota (ENTER para aceitar):{C_RESET}")
    nota = input(f"{C_INPUT}>> {C_RESET}").strip() or sugest
    if not re.match(r"^\d{4}/\d{4}$", nota):
        print_warning("Formato inválido. Usando sugestão.")
        nota = sugest
    gravar_ultimo_numero(nota)
    variaveis["nota_numero"] = nota

    def input_padrao(chave, rotulo):
        padrao = PADROES[chave]
        print(f"{C_PROMPT}{rotulo}{C_RESET} [{C_INFO}{padrao}{C_RESET}]")
        valor = input(f"{C_INPUT}>> {C_RESET}").strip() or padrao
        return valor

    variaveis["pagamento"] = input_padrao("pagamento", "DADOS DE PAGAMENTO")
    variaveis["favorecido"] = input_padrao("favorecido", "FAVORECIDO")
    variaveis["naturaop"] = input_padrao("naturaop", "NATUREZA DA OP.")
    
    print(f"{C_PROMPT}EMISSÃO (ex 21/08/2025):{C_RESET}")
    variaveis["emissao"] = mascarar_data(input(f"{C_INPUT}>> {C_RESET}"))
    
    print(f"{C_PROMPT}VENCIMENTO (ex 28/08/2025):{C_RESET}")
    variaveis["vencimento"] = mascarar_data(input(f"{C_INPUT}>> {C_RESET}"))

    print(f"{C_PROMPT}Tomador de Serviço ou Destinatário:{C_RESET}")
    variaveis["tomador"] = input(f"{C_INPUT}>> {C_RESET}").strip()
    
    print(f"{C_PROMPT}CNPJ/CPF do Tomador (somente números):{C_RESET}")
    doc_tom = input(f"{C_INPUT}>> {C_RESET}").strip()
    doc_mask, tipo_doc = mascarar_cnpj_cpf(doc_tom)
    variaveis["cnpj/cpf_tomador"] = doc_mask

    print_info("Buscando informações do CNPJ...")
    
    # Iniciar a barra de loading em uma thread separada
    loading_ativo = [True]
    loading_thread = threading.Thread(target=mostrar_loading, args=(loading_ativo,))
    loading_thread.start()
    
    try:
        sugestoes = fetch_cnpj_sugestoes(doc_tom)
    finally:
        # Parar a barra de loading
        loading_ativo[0] = False
        loading_thread.join()
    
    def sug(key, prompt, default=""):
        s = sugestoes.get(key, default)
        print(f"{C_PROMPT}{prompt}{C_RESET} [{C_INFO}{s}{C_RESET}]")
        val = input(f"{C_INPUT}>> {C_RESET}").strip() or s
        return val

    variaveis["cobranca"] = sug("endereco", "Endereço de cobrança")
    variaveis["endereço_tomador"] = sug("endereco", "Endereço")
    variaveis["email_tomador"] = sug("email", "E-mail")
    variaveis["cidade_tomador"] = sug("cidade", "Cidade")
    variaveis["estado/uf_tomador"] = sug("estado", "Estado/UF")
    
    # Usar a função sug para CEP também
    cep_input = sug("cep", "CEP")
    variaveis["cep_tomador"] = mascarar_cep(cep_input)
    
    # Para IE, usar a função sug com valor padrão vazio
    im_ie = sug("ie", "IM/IE", "")
    variaveis["inscricao_estadual_tomador"] = mascarar_ie_im(im_ie)
    
    # Usar a função sug para telefone também
    tel_input = sug("telefone", "Telefone")
    tel_mask, tel_tipo = mascarar_telefone(tel_input)
    variaveis["telefone_tomador"] = tel_mask

    print_header("DADOS DA OBRA")
    
    print(f"{C_PROMPT}Nome (obra):{C_RESET}")
    variaveis["nome_obra"] = input(f"{C_INPUT}>> {C_RESET}").strip()
    
    print(f"{C_PROMPT}Cidade (obra):{C_RESET}")
    variaveis["cidade_obra"] = input(f"{C_INPUT}>> {C_RESET}").strip()
    
    print(f"{C_PROMPT}Estado/UF (obra):{C_RESET}")
    variaveis["estado/uf_obra"] = input(f"{C_INPUT}>> {C_RESET}").strip()
    
    print(f"{C_PROMPT}CEP (obra):{C_RESET}")
    cep_obra = input(f"{C_INPUT}>> {C_RESET}").strip()
    variaveis["cep_obra"] = mascarar_cep(cep_obra)
    
    print(f"{C_PROMPT}CNO da Obra:{C_RESET}")
    cno_input = input(f"{C_INPUT}>> {C_RESET}").strip()
    variaveis["cno_obra"] = formatar_cno(cno_input)

    return variaveis

def preencher_modelo(variaveis: Dict[str, Any], itens: List[Dict[str, Any]]) -> Tuple[str, str]:
    ensure_dirs()
    
    doc = Document(MODELO_PATH)
    tabela = localizar_tabela_produtos(doc)
    produtos_vars = {}
    if tabela:
        produtos_vars = preencher_tabela_produtos(tabela, itens)
    
    total_soma = somar_itens(itens)
    
    # Formatar deduções
    print(f"{C_PROMPT}Deduções Legais (R$):{C_RESET} [{C_INFO}0{C_RESET}]")
    deducoes_input = input(f"{C_INPUT}>> {C_RESET}").strip() or "0"
    try:
        deducoes_valor = float(deducoes_input.replace("R$", "").replace(".", "").replace(",", "."))
        variaveis["deducoes"] = formatar_moeda(deducoes_valor)
    except:
        deducoes_valor = 0.0
        variaveis["deducoes"] = "R$ 0,00"
    
    # Calcular o total considerando as deduções
    total_com_deducoes = total_soma - deducoes_valor
    
    print(f"{C_INFO}Soma dos itens: {formatar_moeda(total_soma)}{C_RESET}")
    print(f"{C_INFO}Deduções: {formatar_moeda(deducoes_valor)}{C_RESET}")
    print(f"{C_INFO}Total com deduções: {formatar_moeda(total_com_deducoes)}{C_RESET}")
    
    print(f"{C_PROMPT}TOTAL (ENTER para aceitar o valor com deduções, ou digite um valor):{C_RESET}")
    escolha_total = input(f"{C_INPUT}>> {C_RESET}").strip()
    
    def parse_monetario(s: str) -> Optional[float]:
        if not s:
            return None
        s = s.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
        try:
            return float(s)
        except:
            return None
            
    total_user = parse_monetario(escolha_total)
    if total_user is None:
        total_final = total_com_deducoes
    else:
        # Se o usuário digitou um valor, recalcular as deduções para manter a consistência
        nova_deducao = total_soma - total_user
        if nova_deducao < 0:
            print_warning("O valor informado é maior que a soma dos itens. Deduções não podem ser negativas.")
            nova_deducao = 0
            total_final = total_soma
        else:
            total_final = total_user
            deducoes_valor = nova_deducao
            variaveis["deducoes"] = formatar_moeda(deducoes_valor)
        
        print_info(f"Deduções ajustadas para: {formatar_moeda(deducoes_valor)}")
    
    # Garantir que o valor final não seja negativo
    total_final = max(0.0, total_final)
    
    variaveis["total_absoluto"] = formatar_moeda(total_final)

    # Coletar observações
    print(f"\n{C_PROMPT}OBSERVAÇÕES (digite as observações para a nota fiscal):{C_RESET}")
    print(f"{C_INFO}Pressione ENTER duas vezes para finalizar{C_RESET}")
    observacoes = []
    print(f"{C_INPUT}>> {C_RESET}", end="")
    
    while True:
        linha = input().strip()
        if not linha:
            if not observacoes:  # Se é a primeira linha vazia
                continue
            else:  # Segunda linha vazia finaliza
                break
        observacoes.append(linha)
    
    variaveis["observacao"] = "\n".join(observacoes) if observacoes else "Nenhuma observação."

    all_vars = {**variaveis, **produtos_vars}
    substituir_placeholders(doc, all_vars)

    # Ajustes de formatação
    ajustar_tamanho_fonte(doc, 9)
    reduzir_espacamento(doc)
    ajustar_fonte_texto_longo(doc)
    ajustar_tamanho_pagina(doc)

    ensure_dirs()
    nome_base = variaveis["nota_numero"].replace("/", "_")
    docx_path = os.path.join(RESULTADO_DIR, f"{nome_base}.docx")
    doc.save(docx_path)

    print_success(f"Pré-visualização salva: {docx_path}")
    print(f"{C_PROMPT}Deseja alterar algum campo antes de gerar o PDF?{C_RESET} [{C_INFO}s{C_RESET}/{C_WARN}N{C_RESET}]")
    resp = input(f"{C_INPUT}>> {C_RESET}").strip().lower() or "n"
    if resp == "s":
        all_vars = revisar_editar(all_vars)
        doc2 = Document(MODELO_PATH)
        if tabela:
            tabela2 = localizar_tabela_produtos(doc2)
            if tabela2:
                preencher_tabela_produtos(tabela2, itens)
        substituir_placeholders(doc2, all_vars)
        ajustar_tamanho_fonte(doc2, 9)
        reduzir_espacamento(doc2)
        ajustar_fonte_texto_longo(doc2)
        ajustar_tamanho_pagina(doc2)
        doc2.save(docx_path)

    try:
        convert(docx_path)
        print_success("PDF gerado com sucesso!")
    except Exception as e:
        print_error("Falha ao converter para PDF via docx2pdf. Verifique se o Microsoft Word está instalado.")
    pdf_path = docx_path.replace(".docx", ".pdf")
    return docx_path, pdf_path

def criar_nota():
    clear_screen()
    print_header("CRIAR NOVA NOTA FISCAL")
    
    variaveis = coletar_dados_principais()
    itens = coletar_itens()
    docx_path, pdf_path = preencher_modelo(variaveis, itens)
    
    registro = {
        "nota_numero": variaveis["nota_numero"],
        "arquivo_docx": docx_path,
        "arquivo_pdf": pdf_path,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tomador": variaveis.get("tomador", ""),
        "nome_obra": variaveis.get("nome_obra", ""),
        "total": variaveis.get("total_absoluto", ""),
    }
    salvar_historico_csv(registro)
    
    print_success("Nota gerada com sucesso!")
    print_info(f"DOCX: {docx_path}")
    if os.path.exists(pdf_path):
        print_info(f"PDF: {pdf_path}")
    
    input(f"\n{C_PROMPT}Pressione ENTER para continuar...{C_RESET}")

def menu_principal():
    ensure_dirs()
    
    while True:
        clear_screen()

        intro = r"""
                                     /$$$$$$$$        /$$                                                                   
                                    |__  $$__/       |__/                                                                   
                                       | $$  /$$$$$$  /$$ /$$$$$$$   /$$$$$$                                                
                                       | $$ /$$__  $$| $$| $$__  $$ /$$__  $$                                               
                                       | $$| $$  \__/| $$| $$  \ $$| $$  \ $$                                               
                                       | $$| $$      | $$| $$  | $$| $$  | $$                                               
                                       | $$| $$      | $$| $$  | $$|  $$$$$$/                                               
                                       |__/|__/      |__/|__/  |__/ \______/                                                
                                                                                                                            
                                                                                                                            
                                                                                                                            
 /$$$$$$$$                                               /$$                                                                
|__  $$__/                                              | $$                                                                
   | $$  /$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$   /$$$$$$ | $$  /$$$$$$  /$$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$/$$$$ 
   | $$ /$$__  $$ /$$__  $$ /$$__  $$|____  $$ /$$__  $$| $$ /$$__  $$| $$__  $$ |____  $$ /$$__  $$ /$$__  $$| $$_  $$_  $$
   | $$| $$$$$$$$| $$  \__/| $$  \__/ /$$$$$$$| $$  \ $$| $$| $$$$$$$$| $$  \ $$  /$$$$$$$| $$  \ $$| $$$$$$$$| $$ \ $$ \ $$
   | $$| $$_____/| $$      | $$      /$$__  $$| $$  | $$| $$| $$_____/| $$  | $$ /$$__  $$| $$  | $$| $$_____/| $$ | $$ | $$
   | $$|  $$$$$$$| $$      | $$     |  $$$$$$$| $$$$$$$/| $$|  $$$$$$$| $$  | $$|  $$$$$$$|  $$$$$$$|  $$$$$$$| $$ | $$ | $$
   |__/ \_______/|__/      |__/      \_______/| $$____/ |__/ \_______/|__/  |__/ \_______/ \____  $$ \_______/|__/ |__/ |__/
                                              | $$                                         /$$  \ $$                        
                                              | $$                                        |  $$$$$$/                        
                                              |__/                                         \______/                                                                                                                                                                                          `--`-'                           
     """
    
        print(f"{intro}")
        print(f"TRINO TERRAPLENAGEM - SISTEMA DE GERAÇÃO DE NOTAS FATURAS")
        print(f"Desenvolvido por: João Vitor A. Macedo")


        print_header("SISTEMA DE NOTAS FATURA")
        
        print_menu_item("1", "Criar nova nota")
        print_menu_item("2", "Ver histórico")
        print_menu_item("0", "Sair")
        
        print(f"\n{C_PROMPT}Escolha uma opção:{C_RESET}")
        op = input(f"{C_INPUT}>> {C_RESET}").strip()
        
        if op == "1":
            criar_nota()
        elif op == "2":
            clear_screen()
            abrir_historico()
            input(f"\n{C_PROMPT}Pressione ENTER para continuar...{C_RESET}")
        elif op == "0":
            print_success("Saindo do sistema. Até logo!")
            break
        else:
            print_error("Opção inválida. Tente novamente.")
            input(f"\n{C_PROMPT}Pressione ENTER para continuar...{C_RESET}")

if __name__ == "__main__":
    menu_principal()