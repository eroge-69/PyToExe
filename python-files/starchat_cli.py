import threading
import miniupnpc
import socket
from rich import print
from rich.console import Console
import hashlib 
import random
import json
import ipaddress
import requests
from rich.progress import Progress
from datetime import datetime
import logging

logging.basicConfig(filename="starchat-debug.log", level=logging.DEBUG)

DEBUG_MODE = False

def debug(msg):
    if DEBUG_MODE:
        from datetime import datetime
        print(f"[cyan][DEBUG {datetime.now().strftime('%H:%M:%S')}][/cyan] {msg}")

port = 7001
screenName = None
auth = None
console = Console()
version = "1.0.0-Launchpad"

def ask_debug_mode():
    global DEBUG_MODE
    choice = input("# Debug [Enable Debug Mode? Y/N]: ").strip().lower()
    if choice == 'y':
        DEBUG_MODE = True
        debug("Debug mode enabled.")

def msgHandler(timeout, msg, host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(msg.encode())

            s.settimeout(timeout)
            response = s.recv(1024).decode()
            return response
    except Exception:
        console.print_exception(show_locals=True)
        return None

def encryptMsg(screenName, msg):
    hasher = hashlib.sha3_512()
    hasher.update(f"[{screenName}]: - {msg}".encode('utf-8'))
    return hasher.hexdigest()


def introScreen(version, screenName, auth):
    print("""
.▄▄ · ▄▄▄▄▄ ▄▄▄· ▄▄▄   ▄▄·  ▄ .▄ ▄▄▄· ▄▄▄▄▄
▐█ ▀. •██  ▐█ ▀█ ▀▄ █·▐█ ▌▪██▪▐█▐█ ▀█ •██  
▄▀▀▀█▄ ▐█.▪▄█▀▀█ ▐▀▀▄ ██ ▄▄██▀▐█▄█▀▀█  ▐█.▪
▐█▄▪▐█ ▐█▌·▐█ ▪▐▌▐█•█▌▐███▌██▌▐▀▐█ ▪▐▌ ▐█▌·
 ▀▀▀▀  ▀▀▀  ▀  ▀ .▀  ▀·▀▀▀ ▀▀▀ · ▀  ▀  ▀▀▀ 
""")
    print(f"""
============---------
Version[{version}] - Screen Name [""", screenName, f"""] - Auth Code [{auth}]
============---------
""")
    
def prepInit(auth, screenName, version):
    if auth is None:
        auth = random.randint(1000, 9999)
        debug(f"Generated random auth code: {auth}")

    if screenName is None or screenName.strip() == "":
        screenName = input("# Setup [ScreenName]: ").strip()
        debug(f"User input screenName: {screenName}")

    introScreen(version, screenName, auth)
    return auth, screenName


def netHandshake(screenName, auth, version):
    print(f"""
//////////////////////
NetHandler P2P Edition -=- {version}

===== Hosting =====
1. Host - Server for Connection from client
2. Client - Connecting to Host from client
 
""")
    
    try:
        choice = int(input("# Net [Hosting]: "))
    except ValueError:
        console.print("[X] Input must be a number")
        return
    
    if choice == 1:
        try:
            mode = input("# Net [Mode] - Choose Mode [1] LAN or [2] Public: ").strip()

            if mode == "1":
                host_ip = get_local_ip()
                print(f"# Net [LAN Mode] | Your Local IP: {host_ip} (share with LAN clients)")
            elif mode == "2":
                try:
                    response = requests.get("https://api.ipify.org")
                    host_ip = response.text
                    print(f"# Net [Public Mode] | Your Public IP: {host_ip} ⚠️ Port forwarding required!")
                except requests.exceptions.RequestException:
                    console.print_exception(show_locals=True)
                    return
            else:
                console.print("[X] Invalid mode selection.")
                return
              
        except requests.exceptions.RequestException as e:
            
            console.print_exception(show_locals=True)
        
        pickedPort = input("# Net [Host Port] - Pick a Public Port to Open |Default=7001|: ")
        if pickedPort.strip() == "":
            port = 7001
        else:
            port = int(pickedPort)


        start_server("0.0.0.0", int(port))

    elif choice == 2:
        host = input("# Net [Host IP] - Insert Host IP: ").strip()
        debug(f"Client selected host IP: {host}")

        try:
            port = int(input("# Net [Host Port]: ").strip())
            hostauth = int(input("# Net [Host Auth]: ").strip())
            debug(f"Client provided port: {port}, auth: {hostauth}")
        except ValueError:
            console.print("[X] Port and Auth must be numbers.")
            return

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                debug(f"Trying to connect to {(host, port)}...")
                s.connect((host, port))
                debug("Connection succeeded.")

                greeting = s.recv(1024).decode()
                debug(f"Received from server: {greeting}")

                if greeting == "Mayday":
                    infoPack = json.dumps([hostauth, screenName])
                    debug(f"Sending handshake info: {infoPack}")
                    s.sendall(infoPack.encode())

                    response = s.recv(1024).decode()
                    debug(f"Received handshake response: {response}")

                if response:
                    try:
                        welcome_data = json.loads(response)
                        print(f"[✓] Connected: {welcome_data['message']}")
                        hostScreenName = welcome_data.get("hostScreenName", "Server")
                        clientScreenName = screenName  # client's own screenName
                        
                        threading.Thread(target=client_receive_messages, args=(s,), daemon=True).start()

                        while True:
                            msg = input(f"[{screenName}]: ").strip()
                            if msg.lower() in ("exit", "quit"):
                                s.sendall(b"[DISCONNECT]")
                                print("[🔌] Disconnected.")
                                break
                            s.sendall(msg.encode())

                    except json.JSONDecodeError:
                        console.print("[X] Failed to parse welcome message.")

                else:
                    console.print("[X] Unexpected server greeting.")
            except Exception:
                console.print_exception(show_locals=True)

clients = []  # list of tuples (conn, screenName)
clients_lock = threading.Lock()

def broadcast(message, sender_conn):
    with clients_lock:
        for conn, _ in clients:
            if conn != sender_conn:
                try:
                    conn.sendall(message.encode())
                except Exception:
                    clients.remove((conn, _))

def handle_client(conn, addr):
    try:
        conn.sendall(b"Mayday")
        data = conn.recv(1024).decode()
        infoPack = json.loads(data)
        tempauth = int(infoPack[0])
        clientScreenName = infoPack[1]
        debug(f"Auth from client: {tempauth}, ScreenName: {clientScreenName}")

        if tempauth == auth:
            with clients_lock:
                clients.append((conn, clientScreenName))
            welcome_info = json.dumps({
                "message": f"Welcome to {screenName}'s Server, {clientScreenName}",
                "hostScreenName": screenName,
                "clientScreenName": clientScreenName
            })
            conn.sendall(welcome_info.encode())
            debug("Handshake successful, welcome sent.")

            # Now chat loop for this client:
            while True:
                msg = conn.recv(1024).decode()
                if not msg or msg == "[DISCONNECT]":
                    break
                full_msg = f"[{clientScreenName}]: {msg}"
                print(full_msg)  # log server side
                broadcast(full_msg, conn)

        else:
            conn.sendall(b"[X] Auth Failed.")
            debug("Handshake failed: invalid auth.")

    except Exception:
        console.print_exception(show_locals=True)
    finally:
        debug(f"Client {addr} disconnected")
        with clients_lock:
            clients[:] = [(c, n) for c, n in clients if c != conn]
        conn.close()

def start_server(host, port):
    if setup_upnp(port):
       print("[*] UPnP port forwarding succeeded.")
    else:
       print("[*] UPnP port forwarding failed or not supported.")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        debug(f"Server listening on {host}:{port}")

        print("# Net [Server] Server Started Successfully!")

        threading.Thread(target=server_send_loop, daemon=True).start()

        while True:
            conn, addr = s.accept()
            debug(f"Accepted connection from {addr}")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


def verify_connection(conn, addr):
    debug(f"Starting handshake with {addr}")
    try:
        conn.sendall(b"Mayday")
        
        # Receive client's info
        data = conn.recv(1024).decode()
        debug(f"Received handshake data: {data}")

        infoPack = json.loads(data)
        tempauth = int(infoPack[0])
        clientScreenName = infoPack[1]
        debug(f"Auth from client: {tempauth}, ScreenName: {clientScreenName}")

        if tempauth == auth:
            # Send welcome message including both screen names as JSON
            welcome_info = json.dumps({
                "message": f"Welcome to {screenName}'s Server, {clientScreenName}",
                "hostScreenName": screenName,
                "clientScreenName": clientScreenName
            })
            conn.sendall(welcome_info.encode())
            debug("Handshake successful, welcome sent.")

            chat_loop(conn, sender_name=screenName, receiver_name=clientScreenName)
        else:
            conn.sendall(b"[X] Auth Failed.")
            debug("Handshake failed: invalid auth.")
    except Exception:
        console.print_exception(show_locals=True)

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to a public DNS IP just to get our own IP
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_lan_ip(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return False

def chat_loop(conn, sender_name, receiver_name):
    recv_thread = threading.Thread(target=receive_messages, args=(conn, receiver_name, sender_name), daemon=True)
    send_thread = threading.Thread(target=send_messages, args=(conn, sender_name), daemon=True)

    recv_thread.start()
    send_thread.start()

    send_thread.join()

def send_messages(conn, sender_name):
    try:
        while True:
            msg = input(f"[{sender_name}]: ").strip()
            if msg.lower() in ["exit", "quit"]:
                conn.sendall(b"[DISCONNECT]")
                print("[🔌] Disconnected.")
                remove_upnp(port)
                break
            conn.sendall(msg.encode())
    except Exception:
        console.print_exception(show_locals=True)

def receive_messages(s):
    while True:
        try:
            msg = s.recv(1024).decode()
            if not msg:
                print("[*] Disconnected from server.")
                break
            print(f"\n[{screenName}]: {msg}", end="", flush=True)
        except Exception:
            print("[!] Connection lost.")
            break

def setup_upnp(port):
    upnp = miniupnpc.UPnP()
    upnp.discoverdelay = 200  # ms
    ndevices = upnp.discover()
    print(f"[UPnP] Found {ndevices} devices")

    upnp.selectigd()  # select the internet gateway device

    external_ip = upnp.externalipaddress()
    print(f"[UPnP] External IP: {external_ip}")

    # Try to add port mapping
    try:
        upnp.addportmapping(port, 'TCP', upnp.lanaddr, port, 'StarChat Upnp', '')
        print(f"[UPnP] Port {port} forwarded to local {upnp.lanaddr}:{port}")
        return True
    except Exception as e:
        print(f"[UPnP] Failed to add port mapping: {e}")
        return False

def remove_upnp(port):
    upnp = miniupnpc.UPnP()
    upnp.discoverdelay = 200
    upnp.discover()
    upnp.selectigd()
    try:
        upnp.deleteportmapping(port, 'TCP')
        print(f"[UPnP] Port {port} mapping removed")
    except Exception as e:
        print(f"[UPnP] Failed to remove port mapping: {e}")

def client_receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                print("[*] Disconnected from server.")
                break
            print(f"\n[{screenName}]: {msg}", end="", flush=True)
        except Exception:
            print("[!] Connection lost.")
            break

def server_send_loop():
    try:
        while True:
            msg = input(f"[{screenName}]: ").strip()
            if msg.lower() in ("exit", "quit"):
                print("[🔌] Server exiting.")
                break
            broadcast(f"[{screenName}]: {msg}", sender_conn=None)
    except Exception:
        console.print_exception(show_locals=True)

def main():
    # put your startup code here; example:
    global auth, screenName, version
    ask_debug_mode()
    auth, screenName = prepInit(auth, screenName, version)
    debug(f"Initialized with screenName={screenName}, auth={auth}")
    netHandshake(screenName, auth, version)

if __name__ == "__main__":
    main()