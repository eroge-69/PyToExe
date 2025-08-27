"""
Nombre: WpKiller
Autor: Alejandro Herrero (aka. k4ixer)
Versión: v0.2 (Linux y Windows)
"""

#LIBS
import os
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#VAR -> COLORES
NEGRO = '\033[30m'
ROJO = '\033[31m'
VERDE = '\033[32m'
AMARILLO = '\033[33m'
AZUL = '\033[34m'
MAGENTA = '\033[35m'
CIAN = '\033[36m'
BLANCO = '\033[37m'
GRIS = '\033[90m'
ROJO_BRILLANTE = '\033[91m'
VERDE_BRILLANTE = '\033[92m'
AMARILLO_BRILLANTE = '\033[93m'
AZUL_BRILLANTE = '\033[94m'
MAGENTA_BRILLANTE = '\033[95m'
CIAN_BRILLANTE = '\033[96m'
BLANCO_BRILLANTE = '\033[97m'
RESET = "\033[0m"

#VAR -> GLOBALES
version = 0.2
isTargetDefined = True

#FUNCIONES -> UTILIDAD
def cls():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def end():
    sys.exit()

#FUNCIONES -> PERSONALIZACIÓN
linea = f"{BLANCO}    -------------------------------------------------------------------"

def banner():
    cls()
    print(f"{ROJO_BRILLANTE}")
    print("     █     █░ ██▓███      ██ ▄█▀ ██▓ ██▓     ██▓    ▓█████  ██▀███  ")
    print("    ▓█░ █ ░█░▓██░  ██▒    ██▄█▒ ▓██▒▓██▒    ▓██▒    ▓█   ▀ ▓██ ▒ ██▒")
    print("    ▒█░ █ ░█ ▓██░ ██▓▒   ▓███▄░ ▒██▒▒██░    ▒██░    ▒███   ▓██ ░▄█ ▒")
    print("    ░█░ █ ░█ ▒██▄█▓▒ ▒   ▓██ █▄ ░██░▒██░    ▒██░    ▒▓█  ▄ ▒██▀▀█▄  ")
    print("    ░░██▒██▓ ▒██▒ ░  ░   ▒██▒ █▄░██░░██████▒░██████▒░▒████▒░██▓ ▒██▒")
    print("    ░ ▓░▒ ▒  ▒▓▒░ ░  ░   ▒ ▒▒ ▓▒░▓  ░ ▒░▓  ░░ ▒░▓  ░░░ ▒░ ░░ ▒▓ ░▒▓░")
    print("      ▒ ░ ░  ░▒ ░        ░ ░▒ ▒░ ▒ ░░ ░ ▒  ░░ ░ ▒  ░ ░ ░  ░  ░▒ ░ ▒░")
    print("      ░   ░  ░░          ░ ░░ ░  ▒ ░  ░ ░     ░ ░      ░     ░░   ░ ")
    print("        ░                ░  ░    ░      ░  ░    ░  ░   ░  ░   ░     ")
    print(f"                                                                 {RESET}")

#MAIN PROGRAM
def main():

    target = "null"

    #FUNCIONES -> PROGRAMA
    def wpversion():
        try:
            r = requests.get(f"{target}", verify=False, timeout=10)
            start = r.text.find('<meta name="generator" content="WordPress')
            if start != -1:
                start_quote = r.text.find('"', start + 30) + 1
                end_quote = r.text.find('"', start_quote)
                version = r.text[start_quote:end_quote].replace('WordPress ', '')
                print()
                print(f"{CIAN}    Versión -> {CIAN_BRILLANTE}{version}{RESET}")
            else:
                print(f"{ROJO_BRILLANTE}    No se encontró la versión de WordPress{RESET}")
        except requests.exceptions.RequestException as e:
            print(f"{ROJO_BRILLANTE}    ERROR: No se pudo conectar al target -> {e}{RESET}")

    def wpusers():
        enumerated = 0
        try:
            apiREST = requests.get(f"{target}/wp-json/wp/v2/users", verify=False, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"{ROJO_BRILLANTE}    ERROR: No se pudo acceder a la API REST -> {e}{RESET}")
            return
        
        try:
            xmlUsuarios = requests.get(f"{target}/author-sitemap.xml", verify=False, timeout=10)
        except requests.exceptions.RequestException:
            xmlUsuarios = None

        if apiREST.status_code == 200:
            try:
                users_data = apiREST.json()
                for user in users_data:
                    user_id = user.get("id")
                    user_name = user.get("name")
                    print()
                    print(f"{CIAN}    Usuarios encontrados mediante: {CIAN_BRILLANTE}API REST")
                    print()
                    print(f"{CIAN}    ID:{CIAN_BRILLANTE}{user_id} {CIAN} Usuario:{CIAN_BRILLANTE}{user_name}{RESET}")
                    enumerated += 1
            except ValueError:
                print(f"{ROJO_BRILLANTE}    ERROR: Respuesta de la API no es JSON válido{RESET}")

        if xmlUsuarios and xmlUsuarios.status_code == 200 and enumerated != 1:
            print()
            print(f"{CIAN}    Usuarios encontrados en: {CIAN_BRILLANTE}{target}/author-sitemap.xml")

    def wpPosts():
        try:
            post_data = apiREST.json()
            for post in post_data:
                post_id = post.get("id")
                post_title = post.get("title", {}).get("rendered")
                print()
                print(f"{CIAN}    ID: {CIAN_BRILLANTE} {post_id}")
                print(f"{CIAN}    Título: {CIAN_BRILLANTE} {post_title}{RESET}")
        except Exception as e:
            print(f"{ROJO_BRILLANTE}    ERROR al obtener los posts -> {e}{RESET}")

    def enumerar_api():
        print()
        def enum_rest(target, ruta, nombre):
            try:
                r = requests.get(f"{target}/wp-json{ruta}", verify=False, timeout=10)
                if r.status_code == 200:
                    print(f"{CIAN}    {nombre} ->{CIAN_BRILLANTE} /wp-json{ruta}{RESET}")
            except requests.exceptions.RequestException:
                pass

        try:
            validate_api = requests.get(f"{target}/wp-json", verify=False, timeout=10)
            if validate_api.status_code != 200:
                print(f"{ROJO_BRILLANTE}    Sin acceso a la API REST{RESET}")
            else:
                enum_rest(target, '/wp/v2/users', 'USUARIOS')
                enum_rest(target, '/wp/v2/posts', 'ENTRADAS')
                enum_rest(target, '/wp/v2/media', 'MEDIA')
                enum_rest(target, '/wp/v2/pages', 'PÁGINAS')
                enum_rest(target, '/wp/v2/settings', 'CONFIGURACIONES')
                enum_rest(target, '/wp/v2/comments', 'COMENTARIOS')
                enum_rest(target, '/wp/v2/categories', 'CATEGORÍAS')
                enum_rest(target, '/wp/v2/tags', 'ETIQUETAS')
                enum_rest(target, '/wp/v2/types', 'TIPOS DE CONTENIDO')
                enum_rest(target, '/wp/v2/statuses', 'ESTADOS')
                enum_rest(target, '/wp/v2/themes', 'TEMAS')
                enum_rest(target, '/wp/v2/search', 'BÚSQUEDA')
                enum_rest(target, '/wp/v2/block-types', 'TIPOS DE BLOQUES')
                enum_rest(target, '/wp/v2/blocks', 'BLOQUES')
                enum_rest(target, '/wp/v2/blocks/<id>/autosaves/', 'AUTOSAVES BLOQUES')
                enum_rest(target, '/wp/v2/block-renderer', 'RENDERIZADOR BLOQUES')
                enum_rest(target, '/wp/v2/block-directory/search', 'BÚSQUEDA DIRECTORIO BLOQUES')
                enum_rest(target, '/wp/v2/plugins', 'PLUGINS')
        except requests.exceptions.RequestException as e:
            print(f"{ROJO_BRILLANTE}    ERROR: No se pudo validar la API REST -> {e}{RESET}")

    def checkVersion():
        global version
        try:
            versionActual = str(requests.get("https://gist.githubusercontent.com/k4ixer/0da081b275aef06ca1dab04617bca840/raw/cf759c34d4bc7d28ff784c0edbf074a342451ef5/WPKVERSION.txt").text)
            if str(version) != versionActual:
                print()
                print(f"{AMARILLO_BRILLANTE}    Nueva actualización disponible -> {AMARILLO}{versionActual}{RESET}")
            else:
                print()
                print(f"{AMARILLO_BRILLANTE}    Ultima versioón instalada{RESET}")

        except requests.exceptions.RequestException:
            print(f"{ROJO_BRILLANTE}    ERROR: No se pudo verificar la versión{RESET}")

    def help():
        print()
        print(f"{AMARILLO_BRILLANTE}    Comandos: {RESET}")
        print(f"{CIAN_BRILLANTE}    help {CIAN}-> Muestra esta pantalla de ayuda{RESET}")
        print(f"{CIAN_BRILLANTE}    cls  {CIAN}-> Limpia la terminal{RESET}")
        print(f"{CIAN_BRILLANTE}    check version  {CIAN}-> Verifica si tienes la ultima versión del programa{RESET}")
        print(f"{CIAN_BRILLANTE}    set target  {CIAN}-> Actualiza el target del objetivo{RESET}")
        print(f"{CIAN_BRILLANTE}    wp version  {CIAN}-> Muestra la versión de WordPress del target{RESET}")
        print(f"{CIAN_BRILLANTE}    wp users  {CIAN}-> Enumera los usuarios del target{RESET}")
        print(f"{CIAN_BRILLANTE}    wp posts  {CIAN}-> Enumera todos los posts de la web{RESET}")
        print(f"{CIAN_BRILLANTE}    wp rest  {CIAN}-> Enumera los endpoints de la API REST{RESET}")
    
    print(linea)
    print(f"{ROJO_BRILLANTE}    Target: {ROJO}{target}{RESET}")
    
    while True:
        print(linea)
        try:
            text = input(f"{GRIS}    =>{BLANCO} ").strip()
            if text == "help":
                help()
            elif text == "cls":
                cls()
                banner()
                print(linea)
                print(f"{ROJO_BRILLANTE}    Target: {ROJO}{target}{RESET}")
            elif text == "set target":
                print()
                target = input(f"{AMARILLO_BRILLANTE}    Target: {BLANCO}")
                isTargetDefined = True
                cls()
                banner()
                print(linea)
                print(f"{ROJO_BRILLANTE}    Target: {ROJO}{target}{RESET}")
            elif text == "wp version":
                if target == "null":
                    print()
                    print(f"{AMARILLO_BRILLANTE}    ERROR: El target está vacío, utiliza 'set target' para establecerlo{RESET}")
                else:
                    wpversion()
            elif text == "wp users":
                if target == "null":
                    print()
                    print(f"{AMARILLO_BRILLANTE}    ERROR: El target está vacío, utiliza 'set target' para establecerlo{RESET}")
                else:
                    wpusers()
            elif text == "wp posts":
                if target == "null":
                    print()
                    print(f"{AMARILLO_BRILLANTE}    ERROR: El target está vacío, utiliza 'set target' para establecerlo{RESET}")
                else:
                    try:
                        apiREST = requests.get(f"{target}/wp-json/wp/v2/posts", verify=False, timeout=10)
                        if apiREST.status_code == 200:
                            wpPosts()
                        else:
                            print(f"{AMARILLO_BRILLANTE}    ERROR: La API REST está deshabilitada{RESET}")
                    except requests.exceptions.RequestException as e:
                        print(f"{ROJO_BRILLANTE}    ERROR: No se pudo acceder a la API REST -> {e}{RESET}")
            elif text == "wp rest":
                if target == "null":
                    print()
                    print(f"{AMARILLO_BRILLANTE}    ERROR: El target está vacío, utiliza 'set target' para establecerlo{RESET}")
                else:
                    try:
                        apiREST = requests.get(f"{target}/wp-json/wp/v2/posts", verify=False, timeout=10)
                        if apiREST.status_code == 200:
                            enumerar_api()
                        else:
                            print(f"{AMARILLO_BRILLANTE}    ERROR: La API REST está deshabilitada{RESET}")
                    except requests.exceptions.RequestException as e:
                        print(f"{ROJO_BRILLANTE}    ERROR: No se pudo acceder a la API REST -> {e}{RESET}")
            elif text == "check version":
                checkVersion()
            else:
                print(f"{AMARILLO_BRILLANTE}    Introduce un comando válido!{RESET}")
        except KeyboardInterrupt:
            print(f"\n{AMARILLO_BRILLANTE}    Saliendo...{RESET}")
            break
        except Exception as e:
            print(f"{ROJO_BRILLANTE}    ERROR inesperado -> {e}{RESET}")
                
banner()
main()
