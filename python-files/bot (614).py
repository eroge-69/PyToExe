import socket
import time
import random
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

# Configuración
SERVER = "irc.irc-hispano.org"
PORT = 6667
CHANNEL = "#Sevilla"
CANAL_IGNORADO = ["#gay_sevilla", "#gaycadiz", "#cadiz", "#chueca", "#mazmorra"]  # Canales ignorados
TIEMPO_CONEXION = 10 * 60  # Tiempo máximo de conexión (en segundos)
TIEMPO_DESCANSO = 15  # Tiempo de espera entre reconexiones (en segundos)

respondidos = set()
usuarios_ignorados = set()
contador_respuestas = 0
nick_queue = []
whois_pendiente = None

NICKS_POSSIBLES = [
    "_Clara27", "_Nuria22", "_Irene30", "_Lidia19", "_Alba24",
    "_Eva28", "_Patricia23", "_Beatriz31", "_Teresa20", "_Alicia26",
    "_Raquel21", "_Noelia29", "_Veronica18", "_Cristina25", "_Angela30",
    "_Lorena24", "_Miriam31", "_Silvia20", "_Natalia28", "_Esther22",
    "_Judith23", "_Ines19", "_Tamara27", "_Celia21", "_Belén30",
    "_Carla26", "_Rebeca18", "_Monica29", "_Vanesa25", "_Gemma20",
]

FRASES_MENSAJE = [
    "Hola, chica scort sevillana de 31 edad soy curvy",
    "Hablame al WhatsApp -->> 614 49 54 97 <<--, gracias ",
]

FRAGMENTOS_EXTRA = [
    "discrecion total.", "trato agradable.", "servicio serio.",
    "escribeme sin compromiso.", "", "", ""
]

FRAGS_PROHIBIDOS = [
    "pol", "mil", "dom", "pas", "gym", "het", "guar", "bi", "act", "gay",
    "alt", "39", "foto", "pro", "bur", "auten", "sum", "nac",
    "WPWebchat_63753sevillano", "MaduritoJoven47", "Dom-Perignon",
    "fiest", "dos", "maest", "foto", "azul", "gita", "lospa",
]

def barajar_nicks():
    nicks = NICKS_POSSIBLES[:]
    random.shuffle(nicks)
    return nicks

def mensaje_personalizado():
    frases = random.sample(FRASES_MENSAJE, len(FRASES_MENSAJE))
    extra = random.choice(FRAGMENTOS_EXTRA)
    return " ".join(frases) + (" " + extra if extra else "")

def hora_actual():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def enviar(sock, texto):
    sock.sendall((texto + "\r\n").encode("latin-1"))

def manejar_linea(sock, linea, nick_actual):
    global contador_respuestas, whois_pendiente

    if linea.startswith("PING"):
        enviar(sock, f"PONG {linea.split()[1]}")
        print(f"[{hora_actual()}] {Fore.YELLOW}[PING→PONG]{Style.RESET_ALL}")
        return

    parts = linea.split()

    if len(parts) >= 2:
        if parts[1] == "001":
            print(f"[{hora_actual()}] {Fore.GREEN}[+] Conectado. Uniéndose a {CHANNEL}...{Style.RESET_ALL}")
            enviar(sock, f"JOIN {CHANNEL}")
            return

        elif parts[1] == "433":
            nuevo_nick = random.choice([n for n in NICKS_POSSIBLES if n != nick_actual])
            enviar(sock, f"NICK {nuevo_nick}")
            enviar(sock, f"USER {nuevo_nick} 0 * :{nuevo_nick}")
            return

        elif parts[1] == "319" and whois_pendiente:
            try:
                canales = " ".join(parts[3:]).lower()  # Los canales en los que está el usuario
                # Filtrar los canales ignorados
                canales_ignorados = [canal for canal in CANAL_IGNORADO if canal.lower() in canales]
                
                if canales_ignorados:
                    # Si el usuario está en algún canal ignorado
                    if whois_pendiente not in usuarios_ignorados:
                        usuarios_ignorados.add(whois_pendiente)
                        canales_ignorados_str = ", ".join(canales_ignorados)
                        print(f"[{hora_actual()}] {Fore.RED}[!] Usuario '{whois_pendiente}' ignorado (está en: {canales_ignorados_str}){Style.RESET_ALL}")
                else:
                    # Responder si no está en canal ignorado
                    mensaje = mensaje_personalizado()
                    enviar(sock, f"PRIVMSG {whois_pendiente} :{mensaje}")
                    respondidos.add(whois_pendiente)
                    contador_respuestas += 1
                    print(f"{Fore.GREEN}[+] Enviado a {whois_pendiente}. Total: {contador_respuestas}{Style.RESET_ALL}")
            except Exception as e:
                print(f"[{hora_actual()}] {Fore.RED}[!] Error al procesar WHOIS: {e}{Style.RESET_ALL}")
            finally:
                whois_pendiente = None
            return

    if len(parts) >= 3 and parts[1] == "PRIVMSG" and parts[2].lower() == nick_actual.lower():
        origen = parts[0][1:].split("!")[0].lower()

        if any(frag in origen for frag in FRAGS_PROHIBIDOS):
            print(f"{Fore.RED}[-] {origen} contiene fragmentos prohibidos. Ignorado.{Style.RESET_ALL}")
            return

        if origen in respondidos:
            print(f"{Fore.RED}[-] {origen} ya fue respondido.{Style.RESET_ALL}")
            return

        if origen in usuarios_ignorados:
            print(f"{Fore.RED}[-] {origen} ignorado (está en uno de los canales ignorados).{Style.RESET_ALL}")
            return

        whois_pendiente = origen
        enviar(sock, f"WHOIS {origen}")
        return

def cuenta_regresiva(segundos):
    for i in range(segundos, 0, -1):
        print(f"\r[+] Reconectando en {i} segundos... ", end="", flush=True)
        time.sleep(1)
    print()

def ciclo_conexion():
    global respondidos, usuarios_ignorados, nick_queue, whois_pendiente
    respondidos = set()
    usuarios_ignorados = set()
    whois_pendiente = None

    if not nick_queue:
        nick_queue = barajar_nicks()

    nick_actual = nick_queue.pop(0)
    sock = socket.socket()
    sock.settimeout(60)
    sock.connect((SERVER, PORT))
    print(f"[{hora_actual()}] {Fore.GREEN}[+] Conectado a {SERVER}:{PORT} como {nick_actual}{Style.RESET_ALL}")

    enviar(sock, f"NICK {nick_actual}")
    enviar(sock, f"USER {nick_actual} 0 * :{nick_actual}")

    buffer = ""
    inicio = time.time()

    while True:
        ahora = time.time()
        if ahora - inicio >= TIEMPO_CONEXION:
            print(f"\n[{hora_actual()}] {Fore.RED}[-] Tiempo máximo alcanzado. Cerrando conexión.{Style.RESET_ALL}")
            enviar(sock, "QUIT :Reinicio.")
            sock.close()
            break

        try:
            datos = sock.recv(4096)
            if not datos:
                print(f"[{hora_actual()}] {Fore.RED}[-] Conexión cerrada.{Style.RESET_ALL}")
                break
            buffer += datos.decode("latin-1", errors="replace")
            while "\r\n" in buffer:
                linea, buffer = buffer.split("\r\n", 1)
                manejar_linea(sock, linea, nick_actual)
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[{hora_actual()}] {Fore.RED}[-] Error: {e}{Style.RESET_ALL}")
            break

def main():
    print(f"{Fore.CYAN}[*] Iniciando cliente IRC con reconexión cada 10 minutos...{Style.RESET_ALL}")
    while True:
        ciclo_conexion()
        print(f"[{hora_actual()}] {Fore.CYAN}[*] Esperando {TIEMPO_DESCANSO} segundos antes de reconectar...{Style.RESET_ALL}")
        cuenta_regresiva(TIEMPO_DESCANSO)

if __name__ == "__main__":
    main()
