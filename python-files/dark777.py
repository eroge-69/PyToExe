import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

def mostrar_banner():
    banner = """
    ██████╗  █████╗ ██████╗ ██╗  ██╗
    ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝
    ██║  ██║███████║██████╔╝█████╔╝ 
    ██║  ██║██╔══██║██╔══██╗██╔═██╗ 
    ██████╔╝██║  ██║██║  ██║██║  ██╗
    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
    """
    print(banner)

def criar_estrutura_pastas(base_dir):
    pastas = ["css", "js", "imagens", "fontes", "outros"]
    os.makedirs(base_dir, exist_ok=True)
    for pasta in pastas:
        os.makedirs(os.path.join(base_dir, pasta), exist_ok=True)

def baixar_arquivo(url, pasta_destino, session):
    try:
        resposta = session.get(url, stream=True, timeout=10)
        resposta.raise_for_status()
        
        nome_arquivo = os.path.basename(urlparse(url).path) or "index.html"
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        
        with open(caminho_completo, 'wb') as arquivo:
            for chunk in resposta.iter_content(chunk_size=8192):
                if chunk:
                    arquivo.write(chunk)
        print(f"[✓] Arquivo salvo: {caminho_completo}")
        return True
    except Exception as e:
        print(f"[✗] Erro ao baixar {url}: {e}")
        return False

def determinar_pasta_por_tipo(url):
    extensao = os.path.splitext(urlparse(url).path)[1].lower()
    if extensao in ('.css', '.scss', '.less'):
        return "css"
    elif extensao in ('.js', '.mjs'):
        return "js"
    elif extensao in ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'):
        return "imagens"
    elif extensao in ('.woff', '.woff2', '.ttf', '.otf', '.eot'):
        return "fontes"
    else:
        return "outros"

def copiar_site_completo(url, pasta_base="site_copiado"):
    try:
        mostrar_banner()
        print(f"\n[🔍] Iniciando cópia do site: {url}\n")
        
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        
        dominio = urlparse(url).netloc.replace("www.", "")
        pasta_base = os.path.join(pasta_base, dominio)
        criar_estrutura_pastas(pasta_base)
        
        resposta = session.get(url)
        resposta.raise_for_status()
        html = resposta.text
        
        caminho_html = os.path.join(pasta_base, "index.html")
        with open(caminho_html, 'w', encoding='utf-8') as arquivo:
            arquivo.write(html)
        
        soup = BeautifulSoup(html, 'html.parser')
        recursos = set()
        
        tags = soup.find_all(['link', 'script', 'img', 'source', 'video', 'audio'])
        print(f"[📥] Encontrados {len(tags)} recursos para baixar...")
        
        for tag in tags:
            if tag.name == 'link' and tag.get('href'):
                url_recurso = urljoin(url, tag.get('href'))
                recursos.add(url_recurso)
            elif tag.name in ('script', 'img', 'source', 'video', 'audio') and tag.get('src'):
                url_recurso = urljoin(url, tag.get('src'))
                recursos.add(url_recurso)
        
        for i, recurso in enumerate(recursos, 1):
            pasta_destino = os.path.join(pasta_base, determinar_pasta_por_tipo(recurso))
            print(f"[{i}/{len(recursos)}] Baixando: {recurso}")
            baixar_arquivo(recurso, pasta_destino, session)
            time.sleep(0.5)
        
        print(f"\n[✅] Site copiado com sucesso em: {os.path.abspath(pasta_base)}")
    except Exception as e:
        print(f"\n[❌] Erro fatal: {e}")

if __name__ == "__main__":
    url_site = input("Digite a URL do site para copiar: ").strip()
    if not url_site.startswith(('http://', 'https://')):
        url_site = 'https://' + url_site
    copiar_site_completo(url_site)