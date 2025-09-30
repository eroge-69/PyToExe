# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin

# --- CONFIGURACIÓN ---
# TODO: Paso 1: Reemplaza esta URL con la URL a la que el formulario de búsqueda envía los datos.
URL_BUSQUEDA = "https://www.contraloria.cl/web/cgr/dictamenes" # ¡Esta es una suposición! Debes verificarla.

# TODO: Paso 2: Reemplaza 'nombre_del_campo_de_texto' por el atributo "name" del campo de búsqueda en el HTML.
NOMBRE_CAMPO_BUSQUEDA = "texto" # ¡Esto es una suposición! Probablemente sea 'texto', 'query', o similar.

# Palabras clave que quieres buscar
KEYWORDS = ["feriado", "permiso", "vacacion", "vacaciones"]

# Carpeta donde se guardarán los archivos descargados
DOWNLOAD_FOLDER = "dictamenes_descargados"

# --- FIN DE LA CONFIGURACIÓN ---

def configurar_sesion():
    """Crea y configura una sesión de requests con un User-Agent."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })
    return session

def buscar_y_extraer_links(session, keyword):
    """Realiza la búsqueda y extrae los enlaces de los resultados."""
    print(f"\nBuscando dictámenes para la palabra clave: '{keyword}'...")
    links = []
    
    try:
        # Preparamos los datos que se enviarán en la petición.
        # Esto simula llenar el formulario de búsqueda.
        payload = {
            NOMBRE_CAMPO_BUSQUEDA: keyword
        }

        # Realizamos la petición. Usamos POST, que es común para formularios.
        # Si el sitio usa GET, esta línea debería cambiarse a:
        # response = session.get(URL_BUSQUEDA, params=payload)
        response = session.post(URL_BUSQUEDA, data=payload)
        response.raise_for_status() # Lanza un error si la petición falla (ej. 404, 500)

        soup = BeautifulSoup(response.text, 'html.parser')

        # --- TAREA MÁS IMPORTANTE ---
        # TODO: Paso 3: Debes encontrar el selector CSS correcto para los enlaces de descarga.
        # Inspecciona la página de resultados para ver qué etiqueta y clase tienen los links.
        # Ejemplo: soup.select('div.resultado-item > a.pdf-link')
        resultados = soup.select('a[href*=".pdf"]') # ¡Esto es una suposición! Busca enlaces que contengan ".pdf".

        if not resultados:
            print("No se encontraron enlaces con el selector actual. Debes ajustarlo.")
            return []

        for link_tag in resultados:
            # Obtenemos el enlace del atributo 'href'
            href = link_tag.get('href')
            if href:
                # Convertimos la URL relativa (ej. /docs/file.pdf) en absoluta
                full_url = urljoin(response.url, href)
                links.append(full_url)
        
        print(f"Se encontraron {len(links)} enlaces.")
        return links

    except requests.exceptions.RequestException as e:
        print(f"Error durante la búsqueda de '{keyword}': {e}")
        return []

def descargar_archivo(session, url, carpeta):
    """Descarga un único archivo desde una URL."""
    try:
        response = session.get(url, stream=True)
        response.raise_for_status()

        # Extraer el nombre del archivo de la URL
        nombre_archivo = url.split('/')[-1]
        if not nombre_archivo.endswith('.pdf'):
            nombre_archivo += '.pdf' # Asegurarse de que tenga extensión
            
        ruta_completa = os.path.join(carpeta, nombre_archivo)

        with open(ruta_completa, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"  -> Archivo guardado: {ruta_completa}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"  -> Error al descargar {url}: {e}")
        return False

def main():
    """Función principal que orquesta todo el proceso."""
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    session = configurar_sesion()

    for keyword in KEYWORDS:
        links_dictamenes = buscar_y_extraer_links(session, keyword)
        
        if links_dictamenes:
            print(f"Iniciando descargas para '{keyword}'...")
            for link in links_dictamenes:
                descargar_archivo(session, link, DOWNLOAD_FOLDER)
                time.sleep(1) # Pausa de 1 segundo para no sobrecargar el servidor

    print("\nProceso de descarga finalizado.")

# --- Punto de entrada del script ---
if __name__ == "__main__":
    main()