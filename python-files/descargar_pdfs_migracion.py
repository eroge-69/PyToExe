
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

url_base = "https://www.inclusion.gob.es/web/migraciones/listado-completo"
carpeta_destino = "pdfs_migraciones"
os.makedirs(carpeta_destino, exist_ok=True)

def obtener_sopa(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"Error al acceder a {url}: {e}")
        return None

sopa_principal = obtener_sopa(url_base)
enlaces_subpaginas = []

for a in sopa_principal.find_all("a", href=True):
    href = a["href"]
    if "/web/migraciones/informacion-" in href:
        url_completa = urljoin(url_base, href)
        enlaces_subpaginas.append(url_completa)

enlaces_subpaginas = list(set(enlaces_subpaginas))
print(f"Encontradas {len(enlaces_subpaginas)} subpáginas para revisar...")

for subpagina in enlaces_subpaginas:
    print(f"\nRevisando: {subpagina}")
    sopa = obtener_sopa(subpagina)
    if not sopa:
        continue
    for a in sopa.find_all("a", href=True):
        href = a["href"]
        if ".pdf" in href.lower():
            pdf_url = urljoin(subpagina, href)
            nombre_archivo = os.path.join(carpeta_destino, os.path.basename(pdf_url))
            if not os.path.exists(nombre_archivo):
                try:
                    print(f"Descargando: {pdf_url}")
                    r = requests.get(pdf_url)
                    with open(nombre_archivo, "wb") as f:
                        f.write(r.content)
                except Exception as e:
                    print(f"Error al descargar {pdf_url}: {e}")
            else:
                print(f"Ya existe: {nombre_archivo}")
