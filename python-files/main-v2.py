import os
import requests
import json
import subprocess

# config
JSON_URL = "https://raw.githubusercontent.com/TS-DEV-JAVA/Poke-dl-api/refs/heads/main/Api-db.json"  
FFMPEG_EXE = "ffmpeg.exe"
OUTPUT_DIR = "downloaded"

# color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# the cool ahh banner
banner_lines = [
    f"{RED}    ____        __                  ____",
    f"{GREEN}   / __ \\____  / /_____        ____/ / /",
    f"{YELLOW}  / /_/ / __ \\/ //_/ _ \\______/ __  / / ",
    f"{BLUE} / ____/ /_/ / ,< /  __/_____/ /_/ / /  ",
    f"{RED}/_/    \\____/_/|_|\\___/      \\__,_/_/   {RESET}"
]

def print_banner():
    os.system("cls" if os.name == "nt" else "clear")
    for line in banner_lines:
        print(line)
    print()

def get_json():
    try:
        response = requests.get(JSON_URL)
        return response.json()
    except:
        print(RED + "[!] Failed to fetch JSON from URL." + RESET)
        exit()

def select_from_list(options, label_color=GREEN):
    for i, option in enumerate(options, 1):
        print(f"{label_color}{i}. {option}{RESET}")
    while True:
        try:
            choice = int(input(YELLOW + "[?] Choose number: " + RESET))
            if 1 <= choice <= len(options):
                return options[choice - 1]
        except:
            pass
        print(RED + "[!] Invalid choice." + RESET)

def main():
    print_banner()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    data = get_json()
    shows = list(data.keys())

    print(BLUE + "[+] Available Series:" + RESET)
    show_name = select_from_list(shows)

    print(GREEN + f"\n[+] Episodes in {show_name}:" + RESET)
    episodes = data[show_name]
    ep_titles = [f"{ep['title']}\n   {BLUE}{ep['url']}{RESET}" for ep in episodes]
    selected_index = ep_titles.index(select_from_list(ep_titles, GREEN))

    selected_ep = episodes[selected_index]
    file_name = f"{selected_ep['title'].replace(' ', '_').replace(':', '-')}.mp4"
    out_path = os.path.join(OUTPUT_DIR, file_name)

    print(YELLOW + f"\n[~] Downloading: {selected_ep['title']}" + RESET)
    print(BLUE + f"[~] URL: {selected_ep['url']}" + RESET)

    command = [
        FFMPEG_EXE,
        "-i", selected_ep["url"],
        "-c", "copy",
        "-bsf:a", "aac_adtstoasc",
        out_path
    ]

    subprocess.run(command)
    print(GREEN + f"[✓] Saved to: {out_path}" + RESET)

if __name__ == "__main__":
    main()
