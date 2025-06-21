import os
import platform
import time
from colorama import Fore, Style, init

os.system("title NoxxPinger")


init(autoreset=True)

ascii_art = f"""{Fore.WHITE}
        {Fore.RED}                   
            _______      
       //\\/  ,,,  \//\\
       |/\| ,;;;;;, |/\|
      //\\\;------;///\\ 
      //  \/   .   \/  \\
     (| ,-_| \ | / |_-, |)
       //`__\.-.-./__`\\
      // /.-(() ())-.\ \\
     (\ |)   '---'   (| /)
      ` (|           |) `
        \)          (/       
 
   
         {Fore.WHITE}Noxx - Ping Tool
{Fore.RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━
{Fore.RED}Discord  : {Fore.RED}official.noxx
Server   : {Fore.RED}https://discord.gg/VwwHVev5Kf
Owner  : {Fore.RED}official.noxx
━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}
"""

def continuous_ping(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    print(f"\n{Fore.CYAN}Start continuous pinging {ip}. Press Ctrl+C for at stoppe.\n")
    try:
        while True:
            command = f"ping {param} 1 {ip}"
            os.system(command)
            time.sleep(1) 
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Ping stoppet af brugeren.{Style.RESET_ALL}")

def menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(ascii_art)
    while True:
        ip = input(f"{Fore.RED}[~] {Fore.WHITE}Enter IP to ping: ")
        if ip.lower() == "exit":
            print(f"{Fore.RED}Bye!")
            break
        continuous_ping(ip)

if __name__ == "__main__":
    menu()