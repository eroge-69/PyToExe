import tkinter as tk
from tkinter import messagebox, scrolledtext
import socket
import threading
import json
import hashlib
import time
import datetime  # Pour un formatage d'horodatage plus lisible


# --- Logique de base de la Blockchain (Simplifiée pour les Événements) ---
class Block:
    def __init__(self, index, timestamp, events, previous_hash):
        self.index = index
        self.timestamp = timestamp  # Stocke comme float (time.time())
        self.events = events
        self.previous_hash = previous_hash
        self.nonce = 0  # Nombre utilisé pour le Proof of Work
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Assurez-vous que l'horodatage est une chaîne pour un hachage cohérent
        block_string = json.dumps({
            "index": self.index,
            "timestamp": str(self.timestamp),
            "events": self.events,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode('utf-8')  # Encode explicitement en UTF-8
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty):
        target_prefix = '0' * difficulty
        while not self.hash.startswith(target_prefix):
            self.nonce += 1
            self.hash = self.calculate_hash()
        # print(f"Bloc miné : {self.hash} avec nonce {self.nonce}") # Le log passe par l'interface GUI maintenant


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_events = []  # Événements en attente d'être inclus dans un bloc
        self.difficulty = 2  # Difficulté simplifiée pour un minage rapide (nombre de zéros au début du hash)

    def create_genesis_block(self):
        # Le premier bloc de la chaîne
        return Block(0, time.time(), [{"message": "Bloc de Genèse créé"}], "0")

    @property
    def last_block(self):
        # Retourne le dernier bloc de la chaîne
        return self.chain[-1]

    def add_event(self, event_data):
        # Ajoute un nouvel événement à la liste des événements en attente
        self.pending_events.append(event_data)
        return len(self.chain)

    def mine_pending_events(self):
        # Mine un nouveau bloc contenant tous les événements en attente
        if not self.pending_events:
            return None  # Rien à miner

        # Crée une copie des événements en attente à inclure dans le bloc
        # et vide la liste originale des événements en attente immédiatement après
        events_to_mine = list(self.pending_events)
        self.pending_events = []  # Vide les événements en attente une fois qu'ils sont minés

        new_block = Block(
            len(self.chain),  # Index du nouveau bloc
            time.time(),  # Horodatage actuel
            events_to_mine,  # Les événements à inclure
            self.last_block.hash  # Hash du bloc précédent
        )
        new_block.mine_block(self.difficulty)  # Exécute le Proof of Work
        self.chain.append(new_block)  # Ajoute le nouveau bloc à la chaîne
        return new_block

    def get_chain_data(self):
        # Prépare les données de la chaîne pour la sérialisation JSON (pour l'envoi réseau)
        chain_data = []
        for block in self.chain:
            chain_data.append({
                "index": block.index,
                "timestamp": datetime.datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                "events": block.events,
                "previous_hash": block.previous_hash,
                "hash": block.hash,
                "nonce": block.nonce
            })
        return chain_data

    def get_pending_events_data(self):
        # Retourne les événements en attente
        return self.pending_events

    def replace_chain(self, new_chain_data):
        # Logique de remplacement de chaîne simplifiée pour la démo :
        # Vérifie juste si la chaîne reçue est plus longue que la nôtre.
        # Dans une vraie blockchain, vous valideriez chaque hash de bloc, son Proof of Work, etc.
        if len(new_chain_data) > len(self.chain):
            # Convertit les données de bloc reçues (dictionnaires) en objets Block
            temp_chain = []
            for block_data in new_chain_data:
                # Convertit la chaîne d'horodatage en float pour l'objet Block
                timestamp_float = datetime.datetime.strptime(block_data['timestamp'], '%Y-%m-%d %H:%M:%S').timestamp()
                block = Block(
                    block_data['index'],
                    timestamp_float,  # Utilise le float ici
                    block_data['events'],
                    block_data['previous_hash']
                )
                block.nonce = block_data.get('nonce', 0)  # Assure que le nonce est défini
                block.hash = block.calculate_hash()  # Recalcule le hash pour vérifier l'intégrité
                temp_chain.append(block)

            # Une vérification de validité très simplifiée pour la démo :
            # Vérifie seulement si les hashs correspondent après la conversion.
            # Une vraie validation de chaîne serait beaucoup plus rigoureuse.
            is_valid_simple = True
            for i in range(1, len(temp_chain)):
                if temp_chain[i].previous_hash != temp_chain[i - 1].hash:
                    is_valid_simple = False
                    break
                if temp_chain[i].hash != temp_chain[i].calculate_hash():
                    is_valid_simple = False
                    break

            if is_valid_simple:
                self.chain = temp_chain
                self.pending_events = []  # Vide les événements en attente car ils sont probablement dans la nouvelle chaîne
                return True
        return False


# --- État Global du Nœud ---
my_blockchain = Blockchain()  # Instance de la blockchain pour ce nœud
server_socket = None  # Le socket serveur pour écouter les connexions entrantes
listening_thread = None  # Le thread qui gère l'écoute
is_listening = False  # Drapeau pour contrôler le thread d'écoute

MY_HOST = '127.0.0.1'  # Adresse de bouclage pour les tests locaux. Utilisez votre IP réelle pour des machines différentes.
MY_PORT = 0  # Sera défini par l'interface graphique ou automatiquement

PEER_HOST = ''  # Hôte du pair distant
PEER_PORT = 0  # Port du pair distant


# --- Fonctions de Communication Socket ---
def send_message(host, port, message_type, payload):
    # Construit le message à envoyer
    message = {
        'type': message_type,
        'payload': payload
    }
    try:
        # Crée un socket TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # Définit un délai d'attente de 5 secondes pour la connexion et l'envoi
            s.connect((host, port))  # Se connecte au pair distant
            s.sendall(json.dumps(message).encode('utf-8'))  # Envoie le message JSON encodé
            log_message(f"Envoyé à {host}:{port} - Type: {message_type}")
            # Optionnellement, attendre une réponse, mais pour la simplicité, on suppose un envoi "fire-and-forget" pour la diffusion
    except ConnectionRefusedError:
        log_message(f"Erreur: Connexion refusée par {host}:{port}. Le pair est-il en ligne ?")
        messagebox.showerror("Erreur de Connexion",
                             f"Impossible de se connecter au pair à {host}:{port}. Vérifiez l'adresse et le port.")
    except socket.timeout:
        log_message(f"Erreur: Délai d'attente dépassé lors de la connexion à {host}:{port}.")
        messagebox.showerror("Erreur de Connexion", f"Délai d'attente dépassé pour {host}:{port}.")
    except Exception as e:
        log_message(f"Erreur lors de l'envoi du message à {host}:{port}: {e}")
        messagebox.showerror("Erreur d'Envoi", f"Erreur lors de l'envoi du message: {e}")


def handle_client_connection(conn, addr):
    # Gère une connexion cliente entrante dans un thread séparé
    global my_blockchain
    try:
        data = conn.recv(4096)  # Lit jusqu'à 4KB de données
        if data:
            message = json.loads(data.decode('utf-8'))  # Décode le message JSON
            message_type = message.get('type')
            payload = message.get('payload')
            log_message(f"Reçu de {addr[0]}:{addr[1]} - Type: {message_type}")

            if message_type == "NEW_EVENT":
                my_blockchain.add_event(payload)
                log_message(f"Événement ajouté aux événements en attente: {payload.get('name')}")
                update_gui_displays()  # Met à jour l'interface graphique
            elif message_type == "NEW_BLOCK":
                block_data = payload.get('block')
                # Dans un scénario réel, valider ce bloc correctement (Proof of Work, intégrité de la chaîne).
                # Pour cette démo, nous supposons qu'il est valide s'il provient d'un pair
                # et l'ajoutons s'il étend notre chaîne ou la remplace.
                if my_blockchain.replace_chain([block_data]):  # Simplifié : ne remplace que si plus long
                    log_message(f"Nouveau bloc reçu et chaîne mise à jour: Index {block_data.get('index')}")
                    update_gui_displays()
                else:
                    log_message(
                        f"Bloc reçu mais pas ajouté (chaîne locale plus longue ou non valide): Index {block_data.get('index')}")
                    # Si la chaîne locale n'est pas remplacée, on pourrait demander la chaîne complète du pair pour résoudre le conflit
            elif message_type == "REQUEST_CHAIN":
                chain_data = my_blockchain.get_chain_data()  # Récupère les données de la chaîne locale
                response_message = {
                    'type': "RESPOND_CHAIN",
                    'payload': {'chain': chain_data}
                }
                conn.sendall(json.dumps(response_message).encode('utf-8'))  # Envoie la chaîne en réponse
                log_message(f"Chaîne envoyée en réponse à {addr[0]}:{addr[1]}")
            elif message_type == "RESPOND_CHAIN":
                peer_chain_data = payload.get('chain')
                if my_blockchain.replace_chain(peer_chain_data):
                    log_message(f"Chaîne du pair reçue et notre chaîne mise à jour (longueur: {len(peer_chain_data)})")
                    update_gui_displays()
                else:
                    log_message(f"Chaîne du pair reçue mais notre chaîne est restée inchangée.")
            else:
                log_message(f"Type de message inconnu: {message_type}")

    except json.JSONDecodeError:
        log_message(f"Erreur JSON invalide de {addr[0]}:{addr[1]}")
    except Exception as e:
        log_message(f"Erreur lors de la gestion de la connexion de {addr[0]}:{addr[1]}: {e}")
    finally:
        conn.close()  # Ferme la connexion client


def listen_for_peers():
    # Fonction qui écoute les connexions entrantes, exécutée dans un thread séparé
    global server_socket, is_listening
    log_message(f"Le nœud {MY_HOST}:{MY_PORT} écoute les connexions...")
    try:
        while is_listening:
            conn, addr = server_socket.accept()  # Accepte une nouvelle connexion
            # Gère chaque connexion dans un nouveau thread pour éviter de bloquer l'écouteur
            client_handler = threading.Thread(target=handle_client_connection, args=(conn, addr))
            client_handler.daemon = True  # Permet au programme principal de quitter même si ce thread tourne
            client_handler.start()
    except socket.timeout:
        pass  # Attendu lors de l'arrêt du socket serveur
    except OSError as e:
        if is_listening:  # N'affiche l'erreur que si nous sommes censés écouter
            log_message(f"Erreur d'écoute du serveur: {e}")
            messagebox.showerror("Erreur Serveur", f"Erreur lors de l'écoute des connexions: {e}")
    except Exception as e:
        log_message(f"Erreur inattendue dans le thread d'écoute: {e}")
    finally:
        if server_socket:
            server_socket.close()  # S'assure que le socket est fermé
        log_message("Serveur d'écoute arrêté.")


# --- Fonctions GUI (Tkinter) ---
def log_message(msg):
    # Ajoute un message au journal dans l'interface graphique
    log_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")
    log_text.see(tk.END)  # Fait défiler automatiquement vers la fin


def start_node_gui():
    # Démarre le nœud : initialise le socket serveur et lance le thread d'écoute
    global server_socket, listening_thread, is_listening, MY_PORT, PEER_HOST, PEER_PORT

    try:
        # Récupère le port d'écoute depuis l'entrée GUI
        my_port_input = int(my_port_entry.get())
        if not (1024 <= my_port_input <= 65535):
            messagebox.showerror("Erreur de Port", "Le port doit être entre 1024 et 65535.")
            return
        MY_PORT = my_port_input

        # Récupère les détails du pair
        peer_address_input = peer_address_entry.get().split(':')
        if len(peer_address_input) == 2:
            PEER_HOST = peer_address_input[0]
            PEER_PORT = int(peer_address_input[1])
        else:
            PEER_HOST = ''  # Réinitialise si invalide
            PEER_PORT = 0
            messagebox.showwarning("Info Pair", "Format d'adresse du pair invalide. Ex: '127.0.0.1:8001'.")

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permet la réutilisation de l'adresse
        server_socket.settimeout(1.0)  # Délai d'attente pour accept(), permet de vérifier le drapeau is_listening
        server_socket.bind((MY_HOST, MY_PORT))  # Lie le socket à l'adresse et au port
        server_socket.listen(5)  # Max 5 connexions en attente
        is_listening = True

        listening_thread = threading.Thread(target=listen_for_peers)
        listening_thread.daemon = True  # Rend le thread démon pour qu'il se termine avec le programme principal
        listening_thread.start()

        log_message(f"Nœud démarré. Écoute sur {MY_HOST}:{MY_PORT}")
        # Mettre à jour l'état des boutons et champs de saisie
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        mine_button.config(state=tk.NORMAL)
        send_event_button.config(state=tk.NORMAL)
        request_chain_button.config(state=tk.NORMAL)
        my_port_entry.config(state=tk.DISABLED)
        peer_address_entry.config(state=tk.DISABLED)


    except ValueError:
        messagebox.showerror("Erreur de Saisie", "Le port doit être un nombre valide.")
    except socket.error as e:
        log_message(f"Erreur de démarrage du nœud : {e}")
        messagebox.showerror("Erreur de Démarrage",
                             f"Impossible de démarrer le nœud : {e}\nLe port est-il déjà utilisé ?")
        stop_node_gui()  # S'assure d'un arrêt propre si le bind échoue


def stop_node_gui():
    # Arrête le nœud : ferme le socket serveur et le thread d'écoute
    global is_listening, server_socket
    is_listening = False  # Indique au thread d'écoute de s'arrêter
    if server_socket:
        server_socket.close()  # Ferme le socket
        server_socket = None
    if listening_thread and listening_thread.is_alive():
        listening_thread.join(timeout=2)  # Donne 2 secondes au thread pour se terminer
    log_message("Nœud arrêté.")
    # Mettre à jour l'état des boutons et champs de saisie
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    mine_button.config(state=tk.DISABLED)
    send_event_button.config(state=tk.DISABLED)
    request_chain_button.config(state=tk.DISABLED)
    my_port_entry.config(state=tk.NORMAL)
    peer_address_entry.config(state=tk.NORMAL)


def add_and_send_face_event_gui():
    # Ajoute un événement simulé (détection de personne) et l'envoie au pair
    person_name = event_name_entry.get()
    if not person_name:
        messagebox.showerror("Erreur de Saisie", "Veuillez entrer un nom pour l'événement.")
        return

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    event_data = {'name': person_name, 'timestamp': timestamp, 'source_node': MY_PORT}

    # 1. Ajouter l'événement à la liste des événements en attente de ce nœud
    my_blockchain.add_event(event_data)
    log_message(f"Événement '{person_name}' ajouté à nos événements en attente.")
    update_gui_displays()  # Met à jour l'affichage local

    # 2. Diffuser l'événement au pair configuré
    if PEER_HOST and PEER_PORT:
        # L'envoi est fait dans un thread pour ne pas bloquer l'interface
        threading.Thread(target=send_message, args=(PEER_HOST, PEER_PORT, "NEW_EVENT", event_data)).start()
    else:
        log_message("Aucun pair configuré pour envoyer l'événement.")

    event_name_entry.delete(0, tk.END)  # Vide le champ de saisie


def mine_block_gui():
    # Mine un nouveau bloc à partir des événements en attente
    mined_block = my_blockchain.mine_pending_events()
    if mined_block:
        log_message(f"Bloc miné localement (Index: {mined_block.index}, Hash: {mined_block.hash[:10]}...)")
        update_gui_displays()  # Met à jour l'affichage de la blockchain locale
        # Diffuser le nouveau bloc au pair
        if PEER_HOST and PEER_PORT:
            # Envoie les données du bloc simplifiées pour qu'elles puissent être reconstituées
            block_payload = {
                "index": mined_block.index,
                "timestamp": datetime.datetime.fromtimestamp(mined_block.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                "events": mined_block.events,
                "previous_hash": mined_block.previous_hash,
                "hash": mined_block.hash,
                "nonce": mined_block.nonce
            }
            threading.Thread(target=send_message,
                             args=(PEER_HOST, PEER_PORT, "NEW_BLOCK", {'block': block_payload})).start()
    else:
        messagebox.showinfo("Minage", "Aucun événement en attente à miner.")


def request_chain_from_peer_gui():
    # Demande la chaîne de blocs au pair distant
    if PEER_HOST and PEER_PORT:
        threading.Thread(target=send_message, args=(PEER_HOST, PEER_PORT, "REQUEST_CHAIN", {})).start()
        log_message(f"Demande de chaîne envoyée au pair {PEER_HOST}:{PEER_PORT}.")
    else:
        messagebox.showwarning("Erreur", "Aucun pair configuré pour demander la chaîne.")


def update_gui_displays():
    # Met à jour les zones de texte de l'interface graphique

    # Mise à jour de l'affichage des événements en attente
    pending_events_text.delete('1.0', tk.END)
    pending = my_blockchain.get_pending_events_data()
    if pending:
        pending_events_text.insert(tk.END, "Événements en attente :\n")
        for event in pending:
            pending_events_text.insert(tk.END,
                                       f"  - Personne: {event.get('name', 'N/A')}, Heure: {event.get('timestamp', 'N/A')}, Source: {event.get('source_node', 'Local')}\n")
    else:
        pending_events_text.insert(tk.END, "Aucun événement en attente.\n")

    # Mise à jour de l'affichage de la Blockchain
    blockchain_text.delete('1.0', tk.END)
    chain = my_blockchain.get_chain_data()
    if chain:
        blockchain_text.insert(tk.END, f"Chaîne de Blocs (Longueur: {len(chain)}) :\n")
        for block in chain:
            blockchain_text.insert(tk.END, "--------------------------------------------------\n")
            blockchain_text.insert(tk.END, f"Bloc Index: {block['index']}\n")
            blockchain_text.insert(tk.END, f"Horodatage: {block['timestamp']}\n")
            blockchain_text.insert(tk.END, f"Événements: {block['events']}\n")
            blockchain_text.insert(tk.END, f"Hash Précédent: {block['previous_hash'][:15]}...\n")
            blockchain_text.insert(tk.END, f"Hash du Bloc: {block['hash'][:15]}...\n")
            blockchain_text.insert(tk.END, f"Nonce: {block['nonce']}\n")
        blockchain_text.insert(tk.END, "--------------------------------------------------\n")
    else:
        blockchain_text.insert(tk.END, "Chaîne de blocs vide.\n")


# --- Configuration de l'Interface Tkinter ---
app = tk.Tk()
app.title("Simulateur de Nœud Blockchain (Socket P2P)")
app.geometry("1000x800")  # Taille de la fenêtre
# Gère l'événement de fermeture de la fenêtre
app.protocol("WM_DELETE_WINDOW", lambda: on_closing())


def on_closing():
    # Demande confirmation avant de quitter et s'assure que les sockets sont fermés
    if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter ?"):
        stop_node_gui()  # S'assure que les sockets sont fermés proprement
        app.destroy()  # Ferme l'application Tkinter


# --- Cadre de Configuration du Nœud ---
node_config_frame = tk.LabelFrame(app, text="Configuration du Nœud", padx=10, pady=10)
node_config_frame.pack(pady=5, padx=10, fill="x")

tk.Label(node_config_frame, text="Mon Port d'écoute :").grid(row=0, column=0, sticky="w", pady=2)
my_port_entry = tk.Entry(node_config_frame, width=10)
my_port_entry.grid(row=0, column=1, pady=2, sticky="ew")
my_port_entry.insert(0, "8000")  # Port par défaut pour le Nœud 1

tk.Label(node_config_frame, text="Adresse Pair (IP:Port) :").grid(row=1, column=0, sticky="w", pady=2)
peer_address_entry = tk.Entry(node_config_frame, width=20)
peer_address_entry.grid(row=1, column=1, pady=2, sticky="ew")
peer_address_entry.insert(0, "127.0.0.1:8001")  # Pair par défaut pour le Nœud 1 (qui sera le Nœud 2)

start_button = tk.Button(node_config_frame, text="Démarrer Nœud", command=start_node_gui)
start_button.grid(row=0, column=2, padx=10, sticky="e")
stop_button = tk.Button(node_config_frame, text="Arrêter Nœud", command=stop_node_gui, state=tk.DISABLED)
stop_button.grid(row=1, column=2, padx=10, sticky="e")

# --- Cadre pour l'ajout d'événements (simulant une détection faciale) ---
event_frame = tk.LabelFrame(app, text="Générer Événement (Détection Faciale)", padx=10, pady=10)
event_frame.pack(pady=5, padx=10, fill="x")

tk.Label(event_frame, text="Nom Personne Détectée :").grid(row=0, column=0, sticky="w", pady=2)
event_name_entry = tk.Entry(event_frame, width=30)
event_name_entry.grid(row=0, column=1, pady=2, sticky="ew")

send_event_button = tk.Button(event_frame, text="Ajouter & Envoyer Événement", command=add_and_send_face_event_gui,
                              state=tk.DISABLED)
send_event_button.grid(row=1, column=0, columnspan=2, pady=5)

# --- Cadre pour les actions Blockchain ---
blockchain_actions_frame = tk.LabelFrame(app, text="Actions Blockchain", padx=10, pady=10)
blockchain_actions_frame.pack(pady=5, padx=10, fill="x")

mine_button = tk.Button(blockchain_actions_frame, text="Miner les Événements en Attente", command=mine_block_gui,
                        state=tk.DISABLED)
mine_button.pack(side=tk.LEFT, padx=5, pady=5, expand=True)

request_chain_button = tk.Button(blockchain_actions_frame, text="Demander Chaîne au Pair",
                                 command=request_chain_from_peer_gui, state=tk.DISABLED)
request_chain_button.pack(side=tk.LEFT, padx=5, pady=5, expand=True)

# --- Cadre principal pour les affichages des données ---
display_frame = tk.Frame(app, padx=10, pady=10)
display_frame.pack(pady=5, padx=10, fill="both", expand=True)

# --- Journal des Événements Réseau ---
log_frame = tk.LabelFrame(display_frame, text="Journal des Communications", padx=5, pady=5)
log_frame.pack(side=tk.TOP, fill="both", expand=True, pady=5)
log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=60, height=8, font=("Courier New", 9))
log_text.pack(fill="both", expand=True)

# --- Cadre pour les événements en attente ---
pending_events_frame = tk.LabelFrame(display_frame, text="Événements en Attente Locaux", padx=5, pady=5)
pending_events_frame.pack(side=tk.TOP, fill="both", expand=True, pady=5)
pending_events_text = scrolledtext.ScrolledText(pending_events_frame, wrap=tk.WORD, width=60, height=8,
                                                font=("Courier New", 9))
pending_events_text.pack(fill="both", expand=True)

# --- Cadre pour l'affichage de la Blockchain ---
blockchain_display_frame = tk.LabelFrame(display_frame, text="État de la Blockchain Locale", padx=5, pady=5)
blockchain_display_frame.pack(side=tk.TOP, fill="both", expand=True, pady=5)
blockchain_text = scrolledtext.ScrolledText(blockchain_display_frame, wrap=tk.WORD, width=60, height=15,
                                            font=("Courier New", 9))
blockchain_text.pack(fill="both", expand=True)

# Initialiser l'affichage au démarrage de l'application
update_gui_displays()

# Lancer la boucle principale de l'interface graphique
app.mainloop()

# Nettoyage à la sortie de l'application (en cas de fermeture anormale)
if server_socket:
    server_socket.close()