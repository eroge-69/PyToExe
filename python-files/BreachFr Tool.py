import requests
import json
import os
from colorama import init, Fore


init(autoreset=True)

BASE_URL = "https://oathnet.org/api/service/"
API_KEY = "86e85299fdedfbad63d4493fffb0bfcbcd2ed0a7bb18131caeb9c016384bff6f"

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def print_json(data):
    print(json.dumps(data, indent=4))

def init_search_session(query):
    url = BASE_URL + "search/init/"
    data = {"query": query}
    response = requests.post(url, headers=HEADERS, json=data)
    return response.json()

def search_breach(query):
    url = BASE_URL + "search-breach/"
    params = {"q": query}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def search_stealer(query):
    url = BASE_URL + "search-stealer/"
    params = {"q": query}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def holehe(email):
    url = BASE_URL + "holehe/"
    params = {"email": email}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def ghunt(email, search_id=None):
    url = BASE_URL + "ghunt/"
    params = {"email": email}
    if search_id:
        params["search_id"] = search_id
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def ip_lookup(ip):
    url = BASE_URL + "ip-info/"
    params = {"ip": ip}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def extract_subdomains(domain):
    url = BASE_URL + "extract-subdomain/"
    params = {"domain": domain}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def discord_to_roblox(discord_id):
    url = BASE_URL + "discord-to-roblox/"
    params = {"discord_id": discord_id}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def roblox_userinfo(username=None, user_id=None):
    url = BASE_URL + "roblox-userinfo/"
    params = {}
    if username:
        params["username"] = username
    if user_id:
        params["user_id"] = user_id
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def steam_userinfo(steam_id):
    url = BASE_URL + "steam/"
    params = {"steam_id": steam_id}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def xbox_userinfo(xbl_id):
    url = BASE_URL + "xbox/"
    params = {"xbl_id": xbl_id}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def discord_userinfo(discord_id):
    url = BASE_URL + "discord-userinfo/"
    params = {"discord_id": discord_id}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def discord_username_history(discord_id):
    url = BASE_URL + "discord-username-history/"
    params = {"discord_id": discord_id}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def minecraft_history(username):
    url = BASE_URL + "mc-history/"
    params = {"username": username}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def menu():
    while True:
        clear_terminal()

        print(f"{Fore.MAGENTA}BreachFr Tool - Sélectionne une option :")
        options = [
            ("1", f"{Fore.CYAN} Initier une recherche (session)"),
            ("2", f"{Fore.CYAN} Recherche Breach"),
            ("3", f"{Fore.CYAN} Recherche Stealer Logs"),
            ("4", f"{Fore.CYAN} Vérifier Holehe"),
            ("5", f"{Fore.CYAN} GHunt Google Lookup"),
            ("6", f"{Fore.CYAN} Lookup IP"),
            ("7", f"{Fore.CYAN} Extraire Subdomains"),
            ("8", f"{Fore.CYAN} Discord  Roblox"),
            ("9", f"{Fore.CYAN} Roblox User Info"),
            ("10", f"{Fore.CYAN} Steam Info"),
            ("11", f"{Fore.CYAN} Xbox Info"),
            ("12", f"{Fore.CYAN} Discord Info"),
            ("13", f"{Fore.CYAN} Historique Usernames Discord"),
            ("14", f"{Fore.CYAN} Minecraft Username History"),
            ("0", f"{Fore.RED} Quitter")
        ]
        
        for number, description in options:
            print(f"{number}. {description}")

        choice = input(f"{Fore.YELLOW}Ton choix : ")

        try:
            if choice == "1":
                query = input(f"{Fore.MAGENTA}Email ou identifiant à rechercher : ")
                print_json(init_search_session(query))
            elif choice == "2":
                query = input(f"{Fore.MAGENTA}Email (email) / Username (username) / Téléphone (+33 7 68 49 75 51) : ")
                print_json(search_breach(query))
            elif choice == "3":
                query = input(f"{Fore.MAGENTA}Email (email) / Username (username) / Domaine (url): ")
                print_json(search_stealer(query))
            elif choice == "4":
                email = input(f"{Fore.MAGENTA}Email : ")
                print_json(holehe(email))
            elif choice == "5":
                email = input(f"{Fore.MAGENTA}Email : ")
                sid = input(f"{Fore.MAGENTA}Search ID (laisser vide si aucun) : ")
                print_json(ghunt(email, sid if sid else None))
            elif choice == "6":
                ip = input(f"{Fore.MAGENTA}Adresse IP : ")
                print_json(ip_lookup(ip))
            elif choice == "7":
                domain = input(f"{Fore.MAGENTA}Nom de domaine : ")
                print_json(extract_subdomains(domain))
            elif choice == "8":
                discord_id = input(f"{Fore.MAGENTA}Discord ID : ")
                print_json(discord_to_roblox(discord_id))
            elif choice == "9":
                username = input(f"{Fore.MAGENTA}Roblox Username (laisser vide si ID) : ")
                user_id = input(f"{Fore.MAGENTA}Roblox User ID (laisser vide si Username) : ")
                print_json(roblox_userinfo(username or None, int(user_id) if user_id else None))
            elif choice == "10":
                steam_id = input(f"{Fore.MAGENTA}SteamID64 : ")
                print_json(steam_userinfo(steam_id))
            elif choice == "11":
                xbl_id = input(f"{Fore.MAGENTA}Gamertag ou XUID : ")
                print_json(xbox_userinfo(xbl_id))
            elif choice == "12":
                discord_id = input(f"{Fore.MAGENTA}Discord ID : ")
                print_json(discord_userinfo(discord_id))
            elif choice == "13":
                discord_id = input(f"{Fore.MAGENTA}Discord ID : ")
                print_json(discord_username_history(discord_id))
            elif choice == "14":
                username = input(f"{Fore.MAGENTA}Nom Minecraft : ")
                print_json(minecraft_history(username))
            elif choice == "0":
                print(f"{Fore.YELLOW} À bientôt !")
                break
            else:
                print(f"{Fore.RED} Choix invalide.")
        except Exception as e:
            print(f"{Fore.RED} Erreur : {e}")
        
        input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    menu()
