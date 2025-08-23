"""
Nombre: WpKiller
Autor: Alejandro Herrero (aka. k4ixer)
Versión: v0.2 (Linux y Windows)
"""

# LIBS -> NORMAL
import os
import requests
import time
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


"""
IDEAS:

1) Hacer peticion al servidor de github para verificar la version del script con la version del servidor,
en caso de ser diferente anunciarselo al usuario para que actualize el programa
"""

version = 0.2

#FUNCIONES -> UTILIDAD
def cls():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def end():
    sys.exit()

def validate_url(target):
    try:
        r = requests.get(f"{target}", verify=False)
        if r.status_code == 404 or r.status_code == 401:
            banner()
            print("\033[91m   [+] ERROR: La URL no se encuentra disponible\033[0m")
            end()
    except requests.ConnectionError:
        banner()
        print("\033[91m   [+] ERROR: La URL no existe\033[0m")
        end()

def validate_wordpress(target):
    validate = requests.get(f"{target}/wp-includes/", verify=False)
    if validate.status_code == 404:
        banner()
        print("\033[91m   [+] ERROR: La URL no es un WordPress\033[0m")
        end()

#FUNCIONES -> PERSONALIZACIÓN
def banner():
    cls()
    print()
    print("\033[94m  ██╗    ██╗██████╗     ██╗  ██╗██╗██╗     ██╗     ███████╗██████╗\033[0m")
    print("\033[94m  ██║    ██║██╔══██╗    ██║ ██╔╝██║██║     ██║     ██╔════╝██╔══██╗\033[0m")
    print("\033[94m  ██║ █╗ ██║██████╔╝    █████╔╝ ██║██║     ██║     █████╗  ██████╔╝\033[0m")
    print("\033[94m  ██║███╗██║██╔═══╝     ██╔═██╗ ██║██║     ██║     ██╔══╝  ██╔══██╗\033[0m")
    print("\033[94m  ╚███╔███╔╝██║         ██║  ██╗██║███████╗███████╗███████╗██║  ██║\033[0m")
    print("\033[94m   ╚══╝╚══╝ ╚═╝         ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝╚═╝  ╚═╝\033[0m")
    print()

def menu():
    def volverMenu():
        volver = input("[>] Volver al menu (y/N): ").lower()
        if volver == "y":
            main()
        else:
            end()

    cls()
    banner()
    print("\033[93m   [1] Enumerar WordPress\033[0m")
    print("\033[93m   [2] Enumerar Plugins (NO DISPONIBLE)\033[0m")
    print("")

    op = int(input("   [>] Opción: "))

    while True:
        if op == 1:
            enumerar(target)
            enumerar_api(target)
            print("\033[92m   [✓] Análisis completo.\033[0m")
            volverMenu()
        elif op == 2:
            print("[+] ERROR: No disponible")
            time.sleep(1)
            #enumerar_plugins()
        else:
            print("[+] ERROR: Introduce una opción valida")
            time.sleep(1)

#FUNCIONES -> PROGRAMA
def enumerar(target):
    banner()
    #Versión de WordPress
    print("\033[93m   Enumerando versión de WordPress...\033[0m")
    r = requests.get(f"{target}", verify=False)
    start = r.text.find('<meta name="generator" content="WordPress')
    if start != -1:
        start_quote = r.text.find('"', start + 30) + 1
        end_quote = r.text.find('"', start_quote)
        version = r.text[start_quote:end_quote].replace('WordPress ', '')
        print()
        print(f"\033[96m   [+] Versión -> {version}\033[0m")
        print()
    else:
        print("\033[91m   [+] No se encontró versión de WordPress\033[0m")
        print()

    #Enumeración de usuarios mediante API REST
    print("\033[93m   Enumerando usuarios...\033[0m")
    found_username = 0
    api = requests.get(f"{target}/wp-json/wp/v2/users", verify=False)
    if api.status_code == 200:
        print()
        print(f"\033[96m   [+] JSON con usuarios -> {target}/wp-json/wp/v2/users\033[0m")
    else:
        found_username + 1
    
    #Enumeración de usuarios mediante author-sitemap.xml
    authorsitemap = requests.get(f"{target}/author-sitemap.xml", verify=False)
    if authorsitemap.status_code == 200:
        print()
        print(f"\033[96m   [+] XML con usuarios -> {target}/author-sitemap.xml\033[0m")
    else:
        found_username + 1

    if found_username == 2:
        print("\033[91m   [+] No se han encontrado usuarios\033[0m")
        print()

    #Comprobar si está activo xmlrpc.php
    xmlrpc = requests.get(f"{target}/xmlrpc.php", verify=False)
    if xmlrpc.status_code == 200:
        print(f"\033[96m   [+] xmlrpc.php -> {target}/xmlrpc.php\033[0m")
        print()

def enumerar_api(target):
    def enum_rest(target, ruta, nombre):
        r = requests.get(f"{target}/wp-json{ruta}", verify=False)
        if r.status_code == 200:
            print(f"\033[96m   [+] {nombre} -> {target}/wp-json{ruta}\033[0m")

    validate_api = requests.get(f"{target}/wp-json", verify=False)
    if validate_api.status_code != 200:
        print("\033[91m   [+] Sin acceso a la API REST\033[0m")
        print()
    else:
        print()
        print("\033[93m   Enumerando API REST...\033[0m")
        print()
        enum_rest(target, '/wp/v2/users', 'USUARIOS');
        enum_rest(target, '/wp/v2/posts', 'ENTRADAS');
        enum_rest(target, '/wp/v2/media', 'MEDIA');
        enum_rest(target, '/wp/v2/pages', 'PÁGINAS');
        enum_rest(target, '/wp/v2/settings', 'CONFIGURACIONES');
        enum_rest(target, '/wp/v2/comments', 'COMENTARIOS');
        enum_rest(target, '/wp/v2/categories', 'CATEGORÍAS');
        enum_rest(target, '/wp/v2/tags', 'ETIQUETAS');
        enum_rest(target, '/wp/v2/types', 'TIPOS DE CONTENIDO');
        enum_rest(target, '/wp/v2/statuses', 'ESTADOS');
        enum_rest(target, '/wp/v2/themes', 'TEMAS');
        enum_rest(target, '/wp/v2/search', 'BÚSQUEDA');
        enum_rest(target, '/wp/v2/block-types', 'TIPOS DE BLOQUES');
        enum_rest(target, '/wp/v2/blocks', 'BLOQUES');
        enum_rest(target, '/wp/v2/blocks/<id>/autosaves/', 'AUTOSAVES BLOQUES');
        enum_rest(target, '/wp/v2/block-renderer', 'RENDERIZADOR BLOQUES');
        enum_rest(target, '/wp/v2/block-directory/search', 'BÚSQUEDA DIRECTORIO BLOQUES');
        enum_rest(target, '/wp/v2/plugins', 'PLUGINS');
        print()

def enumerar_archivosSensibles():
    def enum_files(target, ruta, nombre):
        r = requests.get(f"{target}/wp-json{ruta}", verify=False)
        if r.status_code == 200:
            print(f"\033[96m   [+] {nombre} -> {target}/wp-json{ruta}\033[0m")

    validate_api = requests.get(f"{target}/wp-json", verify=False)
    if validate_api.status_code != 200:
        print("\033[91m   [+] Sin acceso a la API REST\033[0m")
        print()
    else:
        print()
        print("\033[93m   Enumerando API REST...\033[0m")
        print()
        enum_files(target, '/wp/v2/users', 'USUARIOS');
        print()

def enumerar_plugins():

    global lineaPos
    banner()
    print("\033[93m   [1] Diccionario -> plugins.txt (80000L)\033[0m")
    print("\033[93m   [2] Diccionario -> personalizado\033[0m")
    print("")

    op = int(input("   [>] Opción: "))

    if op == 1:
        path = "/usr/share/wordlists/plugins.txt" # Modificar por la ruta donde se encuentra el wordlist en producción
    elif op == 2:
        path = input("[+] Ruta del diccionario: ")

    with open(f"{path}", "r", encoding="utf-8") as wordlist:
        for linea in wordlist:
            linea = linea.strip()
            r = requests.get(f"{target}/wp-content/plugins/{linea}")
            lineaPos += 1
            banner()
            print(int("Linea: " + lineaPos))
            time.sleep(0.1)
            os.system("clear")

# FUNCIÓN -> MAIN
def main():
    global target
    lineaPos = 0
    banner()
    target = input("   [+] Introduce la URL del target (ej: http://example.com): ").strip()
    #validate_url(target)
    #validate_wordpress(target)
    menu()
    print("")

#EJECUCIÓN
if __name__ == "__main__":
    main()