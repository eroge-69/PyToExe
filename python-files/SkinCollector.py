import psutil, re, requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sys

    #cores
reset = '\033[00m'
black = '\033[30m'
red = '\033[31m'
green = '\033[32m'
orange = '\033[33m'
blue = '\033[34m'
purple = '\033[35m'
cyan = '\033[36m'
lightgrey = '\033[37m'
darkgrey = '\033[90m'
lightred = '\033[91m'
lightgreen = '\033[92m'
yellow = '\033[93m'
lightblue = '\033[94m'
pink = '\033[95m'
lightcyan = '\033[96m'

print(f'''{green}
  ___________   .__       _________        .__  .__                 __                
 /   _____/  | _|__| ____ \_   ___ \  ____ |  | |  |   ____   _____/  |_  ___________ 
 \_____  \|  |/ /  |/    \/    \  \/ /  _ \|  | |  | _/ __ \_/ ___\   __\/  _ \_  __  /
 /        \    <|  |   |  \     \___(  <_> )  |_|  |_\  ___/\  \___|  | (  <_> )  | \/
/_______  /__|_ \__|___|  /\______  /\____/|____/____/\___  >\___  >__|  \____/|__|   
        \/     \/       \/        \/                      \/     \/                   
{reset}{pink}                                                                       slayer ❤️  henri{reset}
''')

def get_client_info():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == "LeagueClientUx.exe":
            cmdline = " ".join(proc.info['cmdline'])
            port = re.search(r"--app-port=(\d+)", cmdline)
            token = re.search(r"--remoting-auth-token=([\w-]+)", cmdline)
            if port and token:
                return port.group(1), token.group(1)
    return None, None

def get_latest_version():
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    versions = requests.get(url).json()
    return versions[0]

def load_skin_map(version, locale="pt_BR"):
    base = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/{locale}"
    champs = requests.get(f"{base}/champion.json").json()["data"]
    skin_map = {}
    for key in champs.keys():
        champ = requests.get(f"{base}/champion/{key}.json").json()["data"][key]
        for skin in champ["skins"]:
            sid = str(skin["id"])
            # Se for skin default, podemos ignorar ou deixar vazio
            if skin["name"].lower() == "default":
                continue
            skin_map[sid] = skin["name"]
    return skin_map

def save_account_skins(port, token, skin_map):
    url = f"https://127.0.0.1:{port}/lol-inventory/v2/inventory/CHAMPION_SKIN"
    r = requests.get(url, verify=False, auth=("riot", token))
    if r.status_code != 200:
        print(f"❌ Erro {r.status_code}: {r.text}")
        return
    
    skins = r.json()
    names = []
    for skin in skins:
        sid = str(skin.get("itemId"))
        name = skin_map.get(sid)
        if name:
            names.append(name)

    with open("skins.txt", "w", encoding="utf-8") as f:
        f.write(" | ".join(names))

    print("✅ Skins salvas no arquivo skins.txt!")

if __name__ == "__main__":
    port, token = get_client_info()
    if not port or not token:
        print("LeagueClientUx.exe não detectado. O cliente está aberto?")
        sys.exit(1)
    print(f"🔑 Porta detectada: {port} | Token OK")
    print("⏱ Obtendo versão mais recente do Data Dragon...")
    version = get_latest_version()
    print(f"▶ Usando versão {version} com tradução pt-BR")
    skin_map = load_skin_map(version, locale="pt_BR")
    print(f"🗺 {len(skin_map)} skins reconhecidas em PT-BR")
    print("📥 Buscando skins da conta via API local...")
    save_account_skins(port, token, skin_map)
