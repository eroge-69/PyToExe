# ip_service_safe.py
import os
import time
import subprocess
import psutil
import re
import sys
import asyncio
import inspect

# ----------------- Imports -----------------
try:
    from colorama import init, Fore, Style
except ImportError:
    print("Die Bibliothek 'colorama' ist nicht installiert. Installiere sie mit:")
    print("pip install colorama")
    input("Drücke Enter zum Beenden...")
    sys.exit(1)

try:
    from TikTokApi import TikTokApi
except Exception:
    TikTokApi = None

try:
    import instaloader
except ImportError:
    instaloader = None

init(autoreset=True)

# ----------------- Hilfsfunktionen -----------------
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def wait(seconds):
    time.sleep(seconds)

def is_process_running(name):
    try:
        for proc in psutil.process_iter(['name']):
            pname = proc.info.get('name')
            if pname and name.lower() in pname.lower():
                return True
    except Exception:
        return False
    return False

def cyber_animation(name, blink=False):
    frames = [
        f"[{name}] Initialisierung...",
        f"[{name}] Scanne Prozesse...",
        f"[{name}] Injection läuft...",
        f"[{name}] Anti-Cheat wird gebypasst...",
        f"[{name}] Fertig!"
    ]
    colors = [Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.GREEN]
    for i, frame in enumerate(frames):
        clear()
        color = colors[i % len(colors)]
        if blink and i % 2 == 0:
            color = Fore.RED
        print(f"{color}{Style.BRIGHT}{frame}")
        wait(0.5)
    print(Fore.GREEN + f"{name} External ist nun aktiv!")
    wait(1)

def print_logo():
    clear()
    logo = f"""
{Fore.CYAN}{Style.BRIGHT}
██╗██████╗
██║██╔══██╗
██║██████╔╝
██║██╔═══╝ 
██║██║     
╚═╝╚═╝     
{Fore.YELLOW}     IP SERVICE
"""
    print(logo)
    wait(1)

# ----------------- Fortnite & R6 -----------------
fortnite_locations = [
    "Sweaty Sands", "Sludgy Swamp", "Dirty Docks", "Steamy Stacks",
    "Salty Springs", "Lazy Lake", "Holly Hedges", "Retail Row",
    "Misty Meadows", "Pleasant Park", "Weeping Woods", "Craggy Cliffs",
    "The Daily Bugle"
]

def fortnite_menu():
    process_name = "FortniteClient-Win64-Shipping.exe"
    while True:
        clear()
        print(Fore.CYAN + "===== Fortnite External =====\n")
        game_running = is_process_running(process_name)
        options = ["Aimbot", "ESP", "Silent Aim", "Godmode", "Teleport", "Zurück"]
        for idx, opt in enumerate(options, 1):
            if not game_running and idx <= 4:
                print(Fore.RED + f"{idx}. {opt} (Spiel läuft nicht!)")
            else:
                print(Fore.YELLOW + f"{idx}. {opt}")

        choice = input(Fore.WHITE + "Wähle Option 1-6: ").strip()
        if choice in ["1","2","3","4"]:
            if not game_running:
                print(Fore.RED + "Spiel läuft nicht! Cheats können nicht verwendet werden.")
                wait(1.5)
                continue
            cyber_animation("Fortnite", blink=True)
        elif choice == "5":
            print(Fore.CYAN + "\nWähle einen Ort zum Teleportieren:")
            for idx, loc in enumerate(fortnite_locations, start=1):
                print(Fore.YELLOW + f"{idx}. {loc}")
            sel = input(Fore.WHITE + "Nummer wählen: ").strip()
            try:
                sel = int(sel)
                if 1 <= sel <= len(fortnite_locations):
                    cyber_animation("Teleport", blink=True)
                else:
                    print(Fore.RED + "Ungültige Auswahl!")
                    wait(1)
            except:
                print(Fore.RED + "Ungültige Eingabe!")
                wait(1)
        elif choice == "6":
            break
        else:
            print(Fore.RED + "Ungültige Eingabe!")
            wait(1)

def r6_menu():
    process_name = "RainbowSix.exe"
    rooms = ["Lobby", "Garage", "Armory", "Control Room"]
    while True:
        clear()
        print(Fore.CYAN + "===== Rainbow Six Siege External =====\n")
        game_running = is_process_running(process_name)
        options = ["Aimbot", "ESP", "Silent Aim", "Godmode", "Teleport", "Zurück"]
        for idx, opt in enumerate(options, 1):
            if not game_running and idx <=4:
                print(Fore.RED + f"{idx}. {opt} (Spiel läuft nicht!)")
            else:
                print(Fore.YELLOW + f"{idx}. {opt}")

        choice = input(Fore.WHITE + "Wähle Option 1-6: ").strip()
        if choice in ["1","2","3","4"]:
            if not game_running:
                print(Fore.RED + "Spiel läuft nicht! Cheats können nicht verwendet werden.")
                wait(1.5)
                continue
            cyber_animation("R6", blink=True)
        elif choice == "5":
            print(Fore.CYAN + "\nWähle einen Raum zum Teleportieren:")
            for idx, room in enumerate(rooms, start=1):
                print(Fore.YELLOW + f"{idx}. {room}")
            sel = input(Fore.WHITE + "Nummer wählen: ").strip()
            try:
                sel = int(sel)
                if 1 <= sel <= len(rooms):
                    cyber_animation("Teleport", blink=True)
                else:
                    print(Fore.RED + "Ungültige Auswahl!")
                    wait(1)
            except:
                print(Fore.RED + "Ungültige Eingabe!")
                wait(1)
        elif choice == "6":
            break
        else:
            print(Fore.RED + "Ungültige Eingabe!")
            wait(1)

# ----------------- DDOS Tool -----------------
def validate_ip(ip):
    ipv4 = re.compile(r'^((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$')
    hostname = re.compile(r'^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')
    return bool(ipv4.match(ip)) or bool(hostname.match(ip))

def ddos_tool():
    try:
        clear()
        print(Fore.MAGENTA + "===== DDOS TOOL =====\n")
        ip = input(Fore.WHITE + "IP oder Host: ").strip()
        if not validate_ip(ip):
            print(Fore.RED + "Ungültige IP oder Hostname!")
            wait(1.5)
            return
        count = input("Anzahl Pakete (leer=10): ").strip()
        try:
            count = int(count)
        except:
            count = 10
        for i in range(1, count+1):
            print(Fore.RED + f"[PACKET {i}] Gesendet an {ip}")
            wait(0.1)
        input(Fore.GREEN + "\nFertig! [Enter]")
    except Exception as e:
        print(Fore.RED + f"FEHLER im DDOS-Tool: {e}")
        input("Drücke Enter zum Zurückkehren...")

# ----------------- Instagram Tracker -----------------
def instagram_tracker():
    if instaloader is None:
        print(Fore.RED + "Instaloader nicht installiert! 'pip install instaloader'")
        wait(1.5)
        return
    try:
        clear()
        print(Fore.BLUE + "===== Instagram Tracker =====\n")
        username = input(Fore.WHITE + "Benutzername: ").strip()
        if not username:
            print(Fore.RED + "Kein Benutzername eingegeben!")
            wait(1)
            return
        recent = input("Letzte N Posts (leer=12): ").strip()
        all_likes = input("Alle Likes summieren? (j/n): ").lower().strip()
        recent = int(recent) if recent.isdigit() else 12

        L = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(L.context, username)
        print(Fore.GREEN + f"Follower: {profile.followers} | Following: {profile.followees}\n")
        count = 0
        likes_total = 0
        for post in profile.get_posts():
            count += 1
            likes = getattr(post, "likes", 0)
            likes_total += likes
            print(Fore.YELLOW + f"Post {count}: {likes} Likes")
            if count >= recent:
                break
        if all_likes == "j":
            print(Fore.CYAN + f"\nSumme Likes: {likes_total}")
        input(Fore.GREEN + "\n[Enter] zum Zurückkehren...")
    except Exception as e:
        print(Fore.RED + f"FEHLER im Instagram Tracker: {e}")
        input("Drücke Enter zum Zurückkehren...")

# ----------------- TikTok Tracker (debugger integriert) -----------------
def tiktok_tracker():
    if TikTokApi is None:
        print(Fore.RED + "TikTokApi nicht installiert! 'pip install TikTokApi'")
        wait(1.5)
        return

    username = input(Fore.WHITE + "Benutzername: ").strip()
    if not username:
        print(Fore.RED + "Kein Benutzername eingegeben!")
        wait(1)
        return

    async def get_stats(username):
        try:
            async with TikTokApi() as api:
                user = await api.user(username=username)
                # Rohdaten anzeigen
                data = None
                if hasattr(user, "as_dict"):
                    data = user.as_dict() if callable(user.as_dict) else user.as_dict
                elif hasattr(user, "user_info"):
                    info = user.user_info
                    data = await info() if inspect.isawaitable(info) else info

                print(Fore.CYAN + "\n--- Rohdaten ---")
                print(data)

                stats = data.get("stats") if isinstance(data, dict) else {}
                follower = stats.get("followerCount") or stats.get("follower_count") or "N/A"
                following = stats.get("followingCount") or stats.get("following_count") or "N/A"
                likes = stats.get("heartCount") or stats.get("heart_count") or "N/A"
                print(Fore.GREEN + f"\nFollower: {follower} | Following: {following} | Likes: {likes}")

        except Exception as e:
            print(Fore.RED + f"Benutzer nicht gefunden oder API-Fehler: {e}")

    asyncio.run(get_stats(username))
    input(Fore.GREEN + "\n[Enter] zum Zurückkehren...")

# ----------------- Spotify Premium -----------------
def find_batch_file(filename):
    if os.name=="nt":
        drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
    else:
        drives = ["/"]
    for drive in drives:
        for root, dirs, files in os.walk(drive):
            if filename in files:
                return os.path.join(root, filename)
    return None

def spotify_menu():
    while True:
        clear()
        print(Fore.MAGENTA + "===== Spotify Premium =====\n")
        options = ["Injecten for Premium", "Zurück"]
        for idx,opt in enumerate(options,1):
            print(Fore.YELLOW + f"{idx}. {opt}")
        choice = input(Fore.WHITE + "Wähle Option 1-2: ").strip()
        if choice=="1":
            batch_file = find_batch_file("Install_New_theme.bat")
            if batch_file:
                print(Fore.GREEN + f"Starte Batch-Datei: {batch_file}")
                try:
                    subprocess.Popen(batch_file, shell=True)
                except Exception as e:
                    print(Fore.RED + f"Fehler beim Starten der Batch-Datei: {e}")
            else:
                print(Fore.RED + "Install_New_theme.bat nicht gefunden!")
            wait(2)
        elif choice=="2":
            break
        else:
            print(Fore.RED + "Ungültige Eingabe!")
            wait(1)

# ----------------- Hauptmenü -----------------
def main_menu():
    while True:
        print_logo()
        print(Fore.CYAN + "╔" + "═"*40 + "╗")
        print(Fore.CYAN + "║" + Fore.YELLOW + Style.BRIGHT + "            IP SERVICE MENU            " + Fore.CYAN + "║")
        print(Fore.CYAN + "╚" + "═"*40 + "╝\n")
        print(Fore.MAGENTA + "1. Fortnite External".ljust(30) + Fore.WHITE + "- Cheats & Teleport")
        print(Fore.MAGENTA + "2. Rainbow Six Siege External".ljust(30) + Fore.WHITE + "- Cheats & Teleport")
        print(Fore.MAGENTA + "3. DDOS Tool".ljust(30) + Fore.WHITE + "- Paket-Simulation")
        print(Fore.MAGENTA + "4. Instagram Tracker".ljust(30) + Fore.WHITE + "- Follower & Likes")
        print(Fore.MAGENTA + "5. TikTok Tracker".ljust(30) + Fore.WHITE + "- Follower")
        print(Fore.MAGENTA + "6. Spotify Premium".ljust(30) + Fore.WHITE + "- Injecten for Premium")
        print(Fore.MAGENTA + "7. Beenden".ljust(30) + Fore.WHITE + "- Programm schließen\n")

        choice = input(Fore.CYAN + "Wähle 1-7: " + Fore.WHITE).strip()
        if choice=="1":
            fortnite_menu()
        elif choice=="2":
            r6_menu()
        elif choice=="3":
            ddos_tool()
        elif choice=="4":
            instagram_tracker()
        elif choice=="5":
            tiktok_tracker()
        elif choice=="6":
            spotify_menu()
        elif choice=="7":
            print(Fore.GREEN + "Programm wird beendet...")
            break
        else:
            print(Fore.RED + "Ungültige Eingabe!")
            wait(1)

if __name__=="__main__":
    main_menu()
