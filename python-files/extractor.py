import os
import sys
import hashlib
import getpass
import re


from colorama import Fore, Style, init
init(autoreset=True)

banner = """
█████╗ ███╗ ██╗ █████╗ ██╗ ██╗ ██╗███████╗████████╗██╗ ██████╗
██╔══██╗████╗ ██║██╔══██╗██║ ╚██╗ ██╔╝██╔════╝╚══██╔══╝██║██╔════╝
███████║██╔██╗ ██║███████║██║ ╚████╔╝ ███████╗ ██║ ██║██║
██╔══██║██║╚██╗██║██╔══██║██║ ╚██╔╝ ╚════██║ ██║ ██║██║
██║ ██║██║ ╚████║██║ ██║███████╗██║ ███████║ ██║ ██║╚██████╗
╚═╝ ╚═╝╚═╝ ╚═══╝╚═╝ ╚═╝╚══════╝╚═╝ ╚══════╝ ╚═╝ ╚═╝ ╚═════╝
"""


def print_gradient_banner():
lines = banner.splitlines()
for i, line in enumerate(lines):

color = Fore.WHITE if i < len(lines)//2 else Fore.CYAN
print(color + line)
print(Fore.LIGHTBLACK_EX + "Made by kyro1k for Analystic Network\n")

credentials = {
"Admin": "KyroAdmin22",
"Analystic": "3340"
}


def login():
print("Login")
username = input("Name: ")
password = getpass.getpass("Password: ")
if username in credentials and credentials[username] == password:
print(Fore.GREEN + "[+] Login erfolgreich!\n")
return True
else:
print(Fore.RED + "[-] Login fehlgeschlagen!")
return False


def get_hashes(filepath):
sha1 = hashlib.sha1()
sha256 = hashlib.sha256()
with open(filepath, 'rb') as f:
while chunk := f.read(8192):
sha1.update(chunk)
sha256.update(chunk)
return sha1.hexdigest(), sha256.hexdigest()


def extract_strings(filepath, min_length=4):
with open(filepath, 'rb') as f:
data = f.read()
# ASCII Strings
ascii_strings = re.findall(rb"[ -~]{%d,}" % min_length, data)
return [s.decode(errors="ignore") for s in ascii_strings]


def main():
print_gradient_banner()


if not login():
sys.exit(0)


print("Zieh deine Datei hier rein und drücke Enter:")
filepath = input().strip().strip('"')
if not os.path.isfile(filepath):
print(Fore.RED + "[-] Datei nicht gefunden!")
sys.exit(1)


sha1, sha256 = get_hashes(filepath)
strings = extract_strings(filepath)


print("\n=== Analyse Ergebnisse ===")
print("Dateiname: ", os.path.basename(filepath))
print("SHA-1 :", sha1)
print("SHA-256 :", sha256)


dps = [s for s in strings if "DPS" in s]
pcasvc = [s for s in strings if "PcaSvc" in s]

