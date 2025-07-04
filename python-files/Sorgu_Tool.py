import os
import time
import textwrap

def BagimlilikKur(packet_name):
    print("-- GEREKLİ KURULUMLAR YAPILIYOR --")
    time.sleep(1)
    os.system(f"pip install {packet_name}")

try:
    import json
except ImportError:
    BagimlilikKur("json")
    import json

try:
    import requests
except ImportError:
    BagimlilikKur("requests")
    import requests

try:
    from colorama import *
except ImportError:
    BagimlilikKur("colorama")
    from colorama import *

init(autoreset=True)

# Renkler (parlak)
red = Style.BRIGHT + Fore.RED
blue = Style.BRIGHT + Fore.BLUE
reset = Style.RESET_ALL
green = Style.BRIGHT + Fore.GREEN
cyan = Style.BRIGHT + Fore.CYAN
magenta = Style.BRIGHT + Fore.MAGENTA
yellow = Style.BRIGHT + Fore.YELLOW
white = Style.BRIGHT + Fore.WHITE

def ClearScreen():
    os.system("cls" if os.name == "nt" else "clear")

def WaitUserKeys():
    input(f"\n{yellow}>> Devam etmek için ENTER'a bas...{reset}")

def PrintBannerAnimated():
    import time
    ClearScreen()
    ascii_lines = [
        "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
        "░░░░░████░░░░░░░░░░░░░░░████░░░░░",
        "░░░░███░░░░░░░░░░░░░░░░░░░███░░░░",
        "░░░███░░░░░░░░░░░░░░░░░░░░░███░░░",
        "░░███░░░░░░░░░░░░░░░░░░░░░░░███░░",
        "░███░░░░░░░░░░░░░░░░░░░░░░░░░███░",
        "████░░░░░░░░░░░░░░░░░░░░░░░░░████",
        "████░░░░░░░░░░░░░░░░░░░░░░░░░████",
        "██████░░░░░░░███████░░░░░░░██████",
        "█████████████████████████████████",
        "█████████████████████████████████",
        "░███████████████████████████████░",
        "░░████░███████████████████░████░░",
        "░░░░░░░███▀███████████▀███░░░░░░░",
        "░░░░░░████──▀███████▀──████░░░░░░",
        "░░░░░░█████───█████───█████░░░░░░",
        "░░░░░░███████▄█████▄███████░░░░░░",
        "░░░░░░░███████████████████░░░░░░░",
        "░░░░░░░░█████████████████░░░░░░░░",
        "░░░░░░░░░███████████████░░░░░░░░░",
        "░░░░░░░░░░█████████████░░░░░░░░░░",
        "░░░░░░░░░░░███████████░░░░░░░░░░░",
        "░░░░░░░░░░███──▀▀▀──███░░░░░░░░░░",
        "░░░░░░░░░░███─█████─███░░░░░░░░░░",
        "░░░░░░░░░░░███─███─███░░░░░░░░░░░",
        "░░░░░░░░░░░░█████████░░░░░░░░░░░░",
    ]
    for line in ascii_lines:
        print(line)
        time.sleep(0.03)

    print()
    for i in range(12):
        print(f"TOOL BY : SAHMARAN | API BY : RAMO {'🐍' * (i % 4)}", end='\r')
        time.sleep(0.3)
    print("\n")



def ApiGet(endpoint: str, param_key: str, param_val: str):
    try:
        url = f"http://ramowlf.xyz/ramowlf/{endpoint}.php?{param_key}={param_val}"
        response = requests.get(url)
        if response.status_code == 200:
            print(f"\n{green}>>> SONUÇ:{reset}\n{cyan}{response.text}{reset}")
        else:
            print(f"{red}[HATA] HTTP {response.status_code}{reset}")
    except Exception as e:
        print(f"{red}[HATA] {str(e)}{reset}")

def Menu():
    print(f"""
{blue}┌───────────────────── {white}MENÜ{blue} ─────────────────────┐                                    
│ {green}1{reset}) Ad Soyad İl Sorgu                          
│ {green}2{reset}) Aile Sorgu (TC)                                 
│ {green}3{reset}) Adres Sorgu (TC)                                
│ {green}4{reset}) GSM'den TC Sorgu                                
│ {green}5{reset}) TC'den GSM Sorgu                                
│ {green}6{reset}) SGK Bilgisi                                    
│ {green}7{reset}) Sülale Sorgu                                   
│ {green}8{reset}) Tapu Bilgisi                                   
│ {green}9{reset}) TC Bilgisi                                     
│{green}10{reset}) Okul No Sorgu                                  
│{green}11{reset}) Vergi Bilgisi                                  
│{green}x{reset}) Çıkış                                          
└────────────────────────────────────────────────┘
""")

def AdSoyadSorgu():
    ad = input("Ad > ")
    soyad = input("Soyad > ")
    il = input("İl > ")
    ApiGet("adsoyad", "ad", ad + f"&soyad={soyad}&il={il}")

def AnaDongu():
    while True:
        PrintBannerAnimated()
        Menu()
        secim = input(f"{yellow}[SEÇİM]: {reset}")

        if secim == "1":
            ClearScreen()
            AdSoyadSorgu()
            WaitUserKeys()
        elif secim == "2":
            ClearScreen()
            ApiGet("aile", "tc", input("TC > "))
            WaitUserKeys()
        elif secim == "3":
            ClearScreen()
            ApiGet("adres", "tc", input("TC > "))
            WaitUserKeys()
        elif secim == "4":
            ClearScreen()
            ApiGet("gsmtc", "gsm", input("GSM > "))
            WaitUserKeys()
        elif secim == "5":
            ClearScreen()
            ApiGet("tcgsm", "tc", input("TC > "))
            WaitUserKeys()
        elif secim == "6":
            ClearScreen()
            ApiGet("sgk", "tc", input("TC > "))
            WaitUserKeys()
        elif secim == "7":
            ClearScreen()
            ApiGet("sulale", "tc", input("TC > "))
            WaitUserKeys()
        elif secim == "8":
            ClearScreen()
            ApiGet("tapu", "tc", input("TC > "))
            WaitUserKeys()
        elif secim == "9":
            ClearScreen()
            ApiGet("tc", "tc", input("TC > "))
            WaitUserKeys()
        elif secim == "10":
            ClearScreen()
            ApiGet("okulno", "tc", input("TC > "))
            WaitUserKeys()
        elif secim == "11":
            ClearScreen()
            ApiGet("v", "tc", input("TC > "))
            WaitUserKeys()
        elif secim == "x":
            print(f"{green}Görüşmek üzere!{reset}")
            break
        else:
            print(f"{red}Geçersiz seçim!{reset}")
            WaitUserKeys()

# Başlat
if __name__ == "__main__":
    AnaDongu()
