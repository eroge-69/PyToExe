
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Fecha actual
fecha_hoy = datetime.today().strftime('%Y-%m-%d')

# URL de búsqueda (simulada, ya que el sitio requiere interacción JS)
search_url = f"https://www.boletinoficial.gob.ar/search?fechaDesde={fecha_hoy}&fechaHasta={fecha_hoy}&organismo=ANMAT"

# Encabezados para simular navegador
headers = {
    'User-Agent': 'Mozilla/5.0'
}

# Realizar la solicitud HTTP
response = requests.get(search_url, headers=headers)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    disposiciones = []

    # Simulación de estructura HTML (ajustar según estructura real)
    for item in soup.find_all('div', class_='resultado-busqueda'):
        numero = item.find('h2').get_text(strip=True)
        titulo = item.find('p').get_text(strip=True)
        enlace = item.find('a')['href']
        disposiciones.append({
            "numero": numero,
            "titulo": titulo,
            "link": f"https://www.boletinoficial.gob.ar{enlace}"
        })

    # Mostrar resultados
    for dispo in disposiciones:
        print(f"Disposición Nº {dispo['numero']} - {dispo['titulo']}")
        print(f"Link: {dispo['link']}
")
else:
    print(f"Error al acceder al Boletín Oficial: {response.status_code}")
