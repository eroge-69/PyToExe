import sys
import re
from collections import defaultdict

def extraer_llamadas_por_usuario(log_path):
    llamadas_por_usuario = defaultdict(list)

    # Expresiones regulares para extraer información
    patron_request_response = re.compile(r'\b(REQUEST|RESPONSE)\b.*?\[(.*?)\].*?:\s*(POST|GET|PUT|DELETE)\s*:\s*(https?://[^\s]+)?', re.IGNORECASE)

    try:
        with open(log_path, 'r', encoding='latin-1') as file:
            for linea in file:
                match = patron_request_response.search(linea)
                if match:
                    tipo, datos_usuario, metodo, url = match.groups()
                    partes = datos_usuario.split('|')
                    if len(partes) >= 2:
                        usuario_id = partes[1]
                        if tipo == "RESPONSE" and not url:
                            continue  # Excluir RESPONSE sin URL
                        llamadas_por_usuario[usuario_id].append(f"{tipo} {metodo} {url if url else '[sin URL]'}")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return

    # Generar archivo de resumen
    try:
        with open("resumen_llamadas_por_usuario.txt", "w", encoding="latin-1") as resumen:
            for usuario, llamadas in llamadas_por_usuario.items():
                resumen.write(f"Usuario: {usuario}\n")
                resumen.write("Llamadas:\n")
                for i, llamada in enumerate(llamadas, 1):
                    resumen.write(f"  {i}. {llamada}\n")
                resumen.write("\n")
        print("Resumen generado exitosamente en 'resumen_llamadas_por_usuario.txt'")
    except Exception as e:
        print(f"Error al escribir el archivo de resumen: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python procesar_log.py <ruta_al_fichero_log>")
    else:
        log_path = sys.argv[1]
        extraer_llamadas_por_usuario(log_path)
