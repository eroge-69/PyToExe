import requests
import concurrent.futures
from threading import Lock
import hashlib
import subprocess
import os, platform
from colorama import Fore, Style, init

unique_domains = set()
# Lock to ensure thread-safe access to the set and file
lock = Lock()

def get_cpu_id():
    try:
        # Menggunakan subprocess untuk menjalankan perintah yang mengambil CPU ID
        cpu_id = subprocess.check_output("wmic cpu get ProcessorId", shell=True).decode().split("\n")[1].strip()
        return cpu_id
    except Exception as e:
        print(f"Erreur lors de l'obtention de l'ID du processeur : {e}")
        return None

def generate_hwid(cpu_id):
    # Menggunakan hashlib untuk membuat hash dari CPU ID
    if cpu_id:
        hwid = hashlib.sha256(cpu_id.encode()).hexdigest()
        return hwid
    return None

cpu_id = get_cpu_id()
hwid = generate_hwid(cpu_id)


banner = f"""
            ⠀⠀⠀ ,_   _,,   , _,,_   _,  _,,  , ,_  ,   
        |_) /_,\  / /_,|_) (_, /_,|  | |_) |{Fore.GREEN}
        '| \'\_  \/`'\_'| \  _)'\_'\__|'| \'|__ 
        '  `  ` '     `'  `'     `   ` '  `  ' {Style.RESET_ALL}
              {Fore.RED}ValzyMT - Reverse URL 1.0{Style.RESET_ALL}
              Développeur : {Fore.RED}@ValzyMT{Style.RESET_ALL}                          
 
    Votre HWID: {hwid}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
	"""
os.system('cls' if os.name == 'nt' else 'clear')

print(banner)

hwid_urls = open("files/hwid.txt", "r").read()
checks = requests.get(hwid_urls).text
if hwid not in checks:
    print(" [ValzYReverse] Hwid non enregistré, contactez-nous sur le télégramme @Valzymtl.\n")
    exit()
    
banner2 = f"""
    1. Reverse URL [{Fore.RED}Private Server{Style.RESET_ALL}]
    2. Duplicate Remover [{Fore.GREEN}Delete Duplicate URL{Style.RESET_ALL}]
    3. URL vers IPs  (MAINTENANCE)

"""
print(banner2)

choices = int(input("ValzYReverse@users~: "))
if choices == 1:
    os.system('cmd /k python "files\ipreverse.py"')
elif choices == 2:
    os.system('cmd /k python "files\duplicateremover.py"')
elif choices == 3:
    os.system('cmd /k python "files\domaintoip.py"')
else:
    print("ValzY@Reverse>> [Introuvable]")
    