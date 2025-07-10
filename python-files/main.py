'''
KeyAuth.cc Python Example

Go to https://keyauth.cc/app/ and click the Python tab. Copy that code and replace the existing keyauthapp instance in this file.

If you get an error saying it can't find module KeyAuth, try following this https://github.com/KeyAuth/KeyAuth-Python-Example#how-to-compile

If that doesn't work for you, you can paste the contents of KeyAuth.py ABOVE this comment and then remove the "from keyauth import api" and that should work too.

READ HERE TO LEARN ABOUT KEYAUTH FUNCTIONS https://github.com/KeyAuth/KeyAuth-Python-Example#keyauthapp-instance-definition
'''
from keyauth import api

import sys
import time
import platform
import os
import colorama
from colorama import Fore
import hashlib
from time import sleep
from datetime import datetime, UTC

# import json as jsond
# ^^ only for auto login/json writing/reading

# watch setup video if you need help https://www.youtube.com/watch?v=L2eAQOmuUiA

def clear():
    if platform.system() == 'Windows':
        os.system('cls & title Python Example')  # clear console, change title
    elif platform.system() == 'Linux':
        os.system('clear')  # Clear the terminal
        sys.stdout.write("\033]0;Python Example\007")  # Set terminal title
        sys.stdout.flush() 
    elif platform.system() == 'Darwin':
        os.system("clear && printf '\033[3J'")  # Clear terminal and scrollback
        os.system('echo -n -e "\033]0;Python Example\007"')  # Set terminal title

print("Initializing")


def getchecksum():
    md5_hash = hashlib.md5()
    file = open(''.join(sys.argv), "rb")
    md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest


keyauthapp = api(
    name = "Bjornkiri66's Application", # App name 
    ownerid = "dZzsdrXBEE", # Account ID
    version = "1.0", # Application version. Used for automatic downloads see video here https://www.youtube.com/watch?v=kW195PLCBKs
    hash_to_check = getchecksum()
)

def answer():
    try:
        print("""1.Key
2.register user + Pass + Key
        """)
        ans = input("Select Option: ")
        if ans == "4":
            user = input('Provide username: ')
            password = input('Provide password: ')
            code = input('Enter 2fa code: (not using 2fa? Just press enter)')
            keyauthapp.login(user, password, code)
        elif ans == "2":
            user = input('Provide username: ')
            password = input('Provide password: ')
            license = input('Provide License: ')
            keyauthapp.register(user, password, license)
        elif ans == "3":
            user = input('Provide username: ')
            license = input('Provide License: ')
            keyauthapp.upgrade(user, license)
        elif ans == "1":
            key = input('Enter your license: ')
            code = input('Enter 2fa code: (not using 2fa? Just press enter)')
            keyauthapp.license(key, code)
        else:
            print("\nInvalid option")
            sleep(1)
            clear()
            answer()
    except KeyboardInterrupt:
        os._exit(1)


answer()

'''try:
    if os.path.isfile('auth.json'): #Checking if the auth file exist
        if jsond.load(open("auth.json"))["authusername"] == "": #Checks if the authusername is empty or not
            print("""
1. Login
2. Register
            """)
            ans=input("Select Option: ")  #Skipping auto-login bc auth file is empty
            if ans=="1": 
                user = input('Provide username: ')
                password = input('Provide password: ')
                keyauthapp.login(user,password)
                authfile = jsond.load(open("auth.json"))
                authfile["authusername"] = user
                authfile["authpassword"] = password
                jsond.dump(authfile, open('auth.json', 'w'), sort_keys=False, indent=4)
            elif ans=="2":
                user = input('Provide username: ')
                password = input('Provide password: ')
                license = input('Provide License: ')
                keyauthapp.register(user,password,license) 
                authfile = jsond.load(open("auth.json"))
                authfile["authusername"] = user
                authfile["authpassword"] = password
                jsond.dump(authfile, open('auth.json', 'w'), sort_keys=False, indent=4)
            else:
                print("\nNot Valid Option") 
                os._exit(1) 
        else:
            try: #2. Auto login
                with open('auth.json', 'r') as f:
                    authfile = jsond.load(f)
                    authuser = authfile.get('authusername')
                    authpass = authfile.get('authpassword')
                    keyauthapp.login(authuser,authpass)
            except Exception as e: #Error stuff
                print(e)
    else: #Creating auth file bc its missing
        try:
            f = open("auth.json", "a") #Writing content
            f.write("""{
    "authusername": "",
    "authpassword": ""
}""")
            f.close()
            print ("""
1. Login
2. Register
            """)#Again skipping auto-login bc the file is empty/missing
            ans=input("Select Option: ") 
            if ans=="1": 
                user = input('Provide username: ')
                password = input('Provide password: ')
                keyauthapp.login(user,password)
                authfile = jsond.load(open("auth.json"))
                authfile["authusername"] = user
                authfile["authpassword"] = password
                jsond.dump(authfile, open('auth.json', 'w'), sort_keys=False, indent=4)
            elif ans=="2":
                user = input('Provide username: ')
                password = input('Provide password: ')
                license = input('Provide License: ')
                keyauthapp.register(user,password,license)
                authfile = jsond.load(open("auth.json"))
                authfile["authusername"] = user
                authfile["authpassword"] = password
                jsond.dump(authfile, open('auth.json', 'w'), sort_keys=False, indent=4)
            else:
                print("\nNot Valid Option") 
                os._exit(1) 
        except Exception as e: #Error stuff
            print(e)
            os._exit(1) 
except Exception as e: #Error stuff
    print(e)
    os._exit(1)'''

keyauthapp.fetchStats()
logo = f"""
{Fore.RED}                                 [7;31m ╔═╗╦╔╗╔╔═╗╔═╗╦═╗ [0m
{Fore.RED}                                 [7;31m ╠═╝║║║║║ ╦║╣ ╠╦╝ [0m
{Fore.RED}                                 [7;31m ╩  ╩╝╚╝╚═╝╚═╝╩╚═ [0m
{Fore.RED}                     [40;31m╔═════════════[ [40;37m969 PINGER [0m[40;31m]════════════╗
{Fore.RED}                     [40;31m║                                       [40;31m║
{Fore.RED}                     [40;31m║         [0m[[31mDeveloper[0m]   [104m @969 [0m[40;37m          [40;31m║
{Fore.RED}                     [40;31m║        [40;37m [[31mDiscord[0m]  [7;31m .gg/xyzmodz [0m[40;37m      [40;31m║
{Fore.RED}                     [40;31m║                                       [40;31m║
{Fore.RED}                     [40;31m║[40;37m         Please [7;31mPROVIDE[0m The IP         [40;31m║ 
{Fore.RED}                     [40;31m╚═══════════════════════════════════════╝ 
"""
def clear_screen():
    # Clear the console screen
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def set_console_title(title: str):
    # Set console window title (Windows only)
    if platform.system() == "Windows":
        os.system(f"title {title}")

def ping(ip: str, count: int) -> bool:
    """
    Ping the given IP address 'count' times.
    Returns True if any ping response contains TTL, False otherwise.
    """
    # Construct ping command based on OS
    system = platform.system()
    if system == "Windows":
        # -n count pings, timeout 1000ms per ping default
        cmd = ["ping", "-n", str(count), ip]
    else:
        # Unix-like: -c count pings
        cmd = ["ping", "-c", str(count), ip]

    try:
        # Run ping and capture output
        completed = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = completed.stdout + completed.stderr
        # Check if "TTL=" or "ttl=" is in output indicating a reply
        if "TTL=" in output.upper():
            return True
        else:
            return False
    except Exception:
        return False

def main():
    # Set console code page to UTF-8 and mode (Windows only)
    if platform.system() == "Windows":
        os.system("chcp 65001 > nul")
        os.system("mode 117,29 > nul")

    while True:
        clear_screen()
        set_console_title(".                                               + 969 + IP PINGER")
        print(logo)
        print()

        # Input speed with validation
        while True:
            speed = input("\033[37m[root@\033[31m969\033[37m] Requests speed : (1 = Fast / 2 = Default / 3 = Low): ").strip()
            if speed in ("1", "2", "3"):
                break
            else:
                print()
                print("\033[37m[root@\033[31mINFO\033[37m] ERROR ! Choose a number between (1, 2, 3)")
                time.sleep(2)

        print()
        ip = input("\033[37m[root@\033[31m969\033[37m] Please specify an IP : ").strip()
        print()

        # Convert speed to int for ping count
        count = int(speed)

        # Ping loop
        while True:
            is_connected = ping(ip, count)
            if is_connected:
                print(f"\033[37m[root@\033[31m969\033[37m] : \033[102m CONNECTED \033[0m to [\033[92m {ip} \033[0m] [\033[92m+\033[0m] Status : \033[102m ONLINE \033[0m BY 969")
                print()
            else:
                print(f"\033[37m[root@\033[31m969\033[37m] : \033[41m DOWNED \033[0m to [\033[31m {ip} \033[0m] [\033[31m-\033[0m] Status : \033[41m OFFLINE \033[0m BY 969")
                print()
            # No delay specified in original batch, so continue immediately

if __name__ == "__main__":
    main()

