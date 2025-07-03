import os
import zipfile
import shutil
import time
import subprocess
import psutil
import requests
import tempfile

os.system("title XMS - .gg/xms")


WHITE = "\033[97m"
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

GITHUB_API_URL = "https://api.github.com/repos/steamgamee/list/contents"
RAW_BASE_URL = "https://raw.githubusercontent.com/steamgamee/list/main/"
DISCORD_LINK = ".gg/MAtcRxD6sR"

def pixel_text():
    print(f"""{CYAN}
██╗  ██╗███╗   ███╗ ██████╗ 
╚██╗██╔╝████╗ ████║██╔════╝ 
 ╚███╔╝ ██╔████╔██║╚█████╗  
 ██╔██╗ ██║╚██╔╝██║ ╚═══██╗ 
██╔╝ ██╗██║ ╚═╝ ██║██████╔╝ 
╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝  
{RESET}""")


def get_zip_filename_by_appid(appid):
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        for file in response.json():
            if file["name"].endswith(".zip") and appid in file["name"]:
                return file["name"]
        return None
    except Exception as e:
        print(f"{RED}Erreur d'accès à GitHub : {e}{RESET}")
        return None

def download_and_install_game(zip_filename):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_url = RAW_BASE_URL + zip_filename
            zip_path = os.path.join(temp_dir, zip_filename)

            print(f"{WHITE}[|] Téléchargement de : {zip_filename}{RESET}")
            r = requests.get(zip_url)
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                f.write(r.content)

            extract_path = os.path.join(temp_dir, "extracted")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            lua_dest = r"C:\Program Files (x86)\Steam\config\stplug-in"
            manifest_dest = r"C:\Program Files (x86)\Steam\config\depotcache"

            os.makedirs(lua_dest, exist_ok=True)
            os.makedirs(manifest_dest, exist_ok=True)

            files = os.listdir(extract_path)
            lua_file = next((f for f in files if f.endswith(".lua")), None)
            manifest_file = next((f for f in files if f.endswith(".manifest")), None)

            if lua_file and manifest_file:
                shutil.move(os.path.join(extract_path, lua_file), os.path.join(lua_dest, lua_file))
                shutil.move(os.path.join(extract_path, manifest_file), os.path.join(manifest_dest, manifest_file))
                print(f"{GREEN}[+] Jeu installé avec succès !{RESET}")
            else:
                print(f"{RED}[-] Fichiers requis manquants dans l'archive.{RESET}")
    except Exception as e:
        print(f"{RED}Erreur pendant l'installation : {e}{RESET}")

def is_steam_running():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and "steam" in proc.info['name'].lower():
                return True
        except:
            pass
    return False

def launch_steam():
    steam_path = r"C:\Program Files (x86)\Steam\Steam.exe"
    if os.path.exists(steam_path):
        try:
            subprocess.Popen(steam_path)
            return True
        except Exception as e:
            print(f"{RED}[+] Erreur lancement Steam : {e}{RESET}")
            return False
    else:
        print(f"{RED}[+] Steam non trouvé à : {steam_path}{RESET}")
        return False

def remove_all_games():
    lua_dest = r"C:\Program Files (x86)\Steam\config\stplug-in"
    manifest_dest = r"C:\Program Files (x86)\Steam\config\depotcache"

    for folder in [lua_dest, manifest_dest]:
        if os.path.isdir(folder):
            for f in os.listdir(folder):
                try:
                    os.remove(os.path.join(folder, f))
                except:
                    pass
    print(f"{GREEN}Tous les jeux ont été supprimés.{RESET}")

def paginated_game_list():
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()
        zip_files = [f["name"] for f in files if f["name"].endswith(".zip")]
        if not zip_files:
            print(f"{YELLOW} [=] Aucun jeu trouvé pour le moment.{RESET}")
            input(f"\n{CYAN}Appuyez sur Entrée pour continuer...{RESET}")
            return

        page_size = 15
        total_games = len(zip_files)
        total_pages = (total_games + page_size - 1) // page_size
        current_page = 1

        while True:
            os.system("cls" if os.name == "nt" else "clear")
            pixel_text()
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, total_games)
            current_games = zip_files[start_idx:end_idx]

            print(f"{CYAN}Jeux disponibles (page {current_page} / {total_pages}) :{RESET}\n")
            for name in current_games:
                if " - " in name:
                    game_name, appid_zip = name.rsplit(" - ", 1)
                    appid = appid_zip.replace(".zip", "")
                    print(f"{GREEN}[+] {game_name} (AppID : {appid}){RESET}")
                else:
                    print(f"{YELLOW}[???] Fichier inconnu : {name}{RESET}")

            print(f"""
{CYAN}Options :{RESET}
[1] Installer tous les jeux disponibles sur cette page
[2] Installer un jeu sur cette page
[3] Changer de page >> [page actuelle : {current_page}] < {total_pages}
[4] Retourner au menu principal
""")

            choice = input(f"{YELLOW}Votre choix : {RESET}").strip()

            if choice == "1":
                for name in current_games:
                    if " - " in name:
                        _, appid_zip = name.rsplit(" - ", 1)
                        appid = appid_zip.replace(".zip", "")
                        zip_file = get_zip_filename_by_appid(appid)
                        if zip_file:
                            download_and_install_game(zip_file)
                        else:
                            print(f"{RED}[→] Jeu {appid} introuvable, demande sur Discord : {DISCORD_LINK}{RESET}")
                input(f"\n{CYAN}Installation terminée. Appuyez sur Entrée...{RESET}")

            elif choice == "2":
                appid = input(f"{CYAN}Entrez l'AppID du jeu à installer (page actuelle) : {RESET}").strip()
                valid_appids = []
                for name in current_games:
                    if " - " in name:
                        _, appid_zip = name.rsplit(" - ", 1)
                        valid_appids.append(appid_zip.replace(".zip", ""))
                if appid in valid_appids:
                    zip_file = get_zip_filename_by_appid(appid)
                    if zip_file:
                        download_and_install_game(zip_file)
                    else:
                        print(f"{RED}[→] Jeu {appid} introuvable, demande sur Discord : {DISCORD_LINK}{RESET}")
                else:
                    print(f"{RED}[!] L'AppID {appid} n'est pas dans la page actuelle.{RESET}")
                input(f"\n{CYAN}Appuyez sur Entrée pour continuer...{RESET}")

            elif choice == "3":
                try:
                    page = int(input(f"{CYAN}Entrez la page à afficher (1 - {total_pages}) : {RESET}").strip())
                    if 1 <= page <= total_pages:
                        current_page = page
                    else:
                        print(f"{RED}Numéro de page invalide.{RESET}")
                        time.sleep(1.5)
                except ValueError:
                    print(f"{RED}Entrée invalide.{RESET}")
                    time.sleep(1.5)

            elif choice == "4":
                break

            else:
                print(f"{RED}Choix invalide.{RESET}")
                time.sleep(1.5)

    except Exception as e:
        print(f"{RED}Erreur lors de la récupération des jeux : {e}{RESET}")
        input(f"\n{CYAN}Appuyez sur Entrée pour continuer...{RESET}")

def main_menu():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        pixel_text()

        steam_running = is_steam_running()

        print(f"{CYAN}Menu principal :{RESET}")
        print("[1] Installer un jeu Steam depuis la base de données")
        if steam_running:
            print("[2] Relancer Steam")
        else:
            print("[2] Lancer Steam")
        print("[3] Supprimer tous les jeux installés")
        print("[4] Voir la liste des jeux disponibles")
        # bypass supprimé
        print("[0] Quitter")

        choice = input(f"\n{YELLOW}Choix : {RESET}")

        if choice == "1":
            appid = input(f"{CYAN}Entrez l'AppID du jeu : {RESET}").strip()
            zip_file = get_zip_filename_by_appid(appid)
            if zip_file:
                download_and_install_game(zip_file)
            else:
                print(f"{RED}[→] Le jeu n'est pas disponible, fais une demande sur le Discord : {DISCORD_LINK}{RESET}")
            input(f"\n{CYAN}Appuyez sur Entrée pour continuer...{RESET}")

        elif choice == "2":
            if steam_running:
                subprocess.run("taskkill /IM steam.exe /F", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(2)
                if launch_steam():
                    print(f"{GREEN}[+] Steam relancé avec succès.{RESET}")
                else:
                    print(f"{RED}[-] Impossible de relancer Steam.{RESET}")
            else:
                if launch_steam():
                    print(f"{GREEN}[+] Steam lancé avec succès.{RESET}")
                else:
                    print(f"{RED}[-] Impossible de lancer Steam.{RESET}")
            input(f"\n{CYAN}Appuyez sur Entrée pour continuer...{RESET}")

        elif choice == "3":
            remove_all_games()
            input(f"\n{CYAN}Appuyez sur Entrée pour continuer...{RESET}")

        elif choice == "4":
            paginated_game_list()

        elif choice == "0":
            print(f"{GREEN}Au revoir !{RESET}")
            break

        else:
            print(f"{RED}Choix invalide.{RESET}")
            time.sleep(1.5)

if __name__ == "__main__":
    main_menu()
