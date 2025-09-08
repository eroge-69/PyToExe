import sys
import os
import time
import webbrowser
import getpass

def slowprint(s, delay=0.1):
    for c in s + '\n':
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)

# Pulizia dello schermo
os.system("clear")

# Stampa del banner
print('''\033[92m
=============================================================================

    ███╗   ███╗██████╗        ███████╗ ██████╗ ██████╗  ██████╗██╗ ██████╗ 
    ████╗ ████║██╔══██╗       ██╔════╝██╔═══██╗██╔══██╗██╔════╝██║██╔═══██╗
    ██╔████╔██║██████╔╝       ███████╗██║   ██║██████╔╝██║     ██║██║   ██║
    ██║╚██╔╝██║██╔══██╗       ╚════██║██║   ██║██╔══██╗██║     ██║██║   ██║
    ██║ ╚═╝ ██║██║  ██║██╗    ███████║╚██████╔╝██║  ██║╚██████╗██║╚██████╔╝
    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝    ╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝ ╚═════╝       
            
=============================================================================
''')

# Definisci la KEY corretta
CORRECT_KEY = "12345"

try:
    slowprint('\033[91m [] F**K THE WORLD & government: ', 0.1)
    slowprint('\033[80m [] This is not a game, use it wisely ', 0.1)
    print("---------------------------------------------------")

    # Input della KEY
    user_key = getpass.getpass("\n\033[97m [] Enter KEY: ")
    os.system("clear")

    # Verifica la KEY
    if user_key == CORRECT_KEY:
        # Booting Screen
        slowprint("[] Booting..... ", 0.01)
        slowprint("\033[91m[] Don't Misuse Your Power", 0.01)
        slowprint("\033[91m[] With Some Great Power Comes Great Responsibility", 0.01)
        slowprint("\033[97m[] Govt. Controls Our Media... Social Medias are fake", 0.01)
        time.sleep(1)
        slowprint("\033[97m[] Booting Completed :)", 0.01)
        time.sleep(1)
        os.system("clear")

        slowprint("\033[92m[*] Starting Tool....", 0.1)
        time.sleep(0.3)
        os.system("clear")

        print('''\033[95m 

··············································································
:   ▄████████    ▄████████  ▄██████▄     ▄████████  ▄████████  ▄█   ▄██████▄ :
:  ███    ███   ███    ███ ███    ███   ███    ███ ███    ███ ███  ███    ███:
:  ███    █▀    ███    █▀  ███    ███   ███    ███ ███    █▀  ███▌ ███    ███:
: ▄███▄▄▄       ███        ███    ███  ▄███▄▄▄▄██▀ ███        ███▌ ███    ███:
:▀▀███▀▀▀     ▀███████████ ███    ███ ▀▀███▀▀▀▀▀   ███        ███▌ ███    ███:
:  ███                 ███ ███    ███ ▀███████████ ███    █▄  ███  ███    ███:
:  ███           ▄█    ███ ███    ███   ███    ███ ███    ███ ███  ███    ███:
:  ███         ▄████████▀   ▀██████▀    ███    ███ ████████▀  █▀    ▀██████▀ :
:                                       ███    ███                           :
··············································································

''')
        print("\033[97m          ================================================ ")
        slowprint("\t\t\033[91mPrivacy is a myth, just like democracy ")
        slowprint("\t\t\tDate: " + time.strftime("%d/%m/%y"))
        print("\033[97m          ================================================ ")

        def main_menu():
            print('''\033[95m
[01]  | Dos attack                  [11] | Subdomain emulator
[02]  | Bruteforce                  [12] | Email generator
[03]  | Email bomber                [13] | Chat AI
[04]  | Discord Info account        [14] | Osint menu
[05]  | Discord nitro generator     [15] | About me
[06]  | webhook spammer             [00] | Exit
[07]  | IP generator                
[08]  | Website scanner             
[09]  | Password generator          
[10]  | SQL injection tester        
''')

            while True:
                choice = input("\033[97mEnter the number of the tool you want to use: ")
                
                if choice == '1':
                    slowprint("\033[92mStarting Dos attack tool...")
                    # Add your Dos attack code here
                    break
                elif choice == '2':
                    slowprint("\033[92mStarting Bruteforce tool...")
                    # Add your Bruteforce code here
                    break
                elif choice == '3':
                    slowprint("\033[92mStarting Email bomber tool...")
                    # Add your Email bomber code here
                    break
                elif choice == '4':
                    slowprint("\033[92mStarting Discord Info account tool...")
                    # Add your Discord Info account code here
                    break
                elif choice == '5':
                    slowprint("\033[92mStarting Discord nitro generator tool...")
                    # Add your Discord nitro generator code here
                    break
                elif choice == '6':
                    slowprint("\033[92mStarting webhook spammer tool...")
                    # Add your webhook spammer code here
                    break
                elif choice == '7':
                    slowprint("\033[92mStarting IP generator tool...")
                    # Add your IP generator code here
                    break
                elif choice == '8':
                    slowprint("\033[92mStarting Website scanner tool...")
                    # Add your Website scanner code here
                    break
                elif choice == '9':
                    slowprint("\033[92mStarting Password generator tool...")
                    # Add your Password generator code here
                    break
                elif choice == '10':
                    slowprint("\033[92mStarting SQL injection tester tool...")
                    # Add your SQL injection tester code here
                    break
                elif choice == '11':
                    slowprint("\033[92mStarting Subdomain emulator tool...")
                    # Add your Subdomain emulator code here
                    break
                elif choice == '12':
                    slowprint("\033[92mStarting Email generator tool...")
                    # Add your Email generator code here
                    break
                elif choice == '13':
                    slowprint("\033[92mStarting Chat AI tool...")
                    # Add your Chat AI code here
                    break
                elif choice == '14':
                    osint_menu()
                    break
                elif choice == '15':
                    slowprint("\033[92mAbout me: This is a security testing toolkit")
                    break
                elif choice == '00' or choice == '0':
                    slowprint("\033[92mExiting...")
                    sys.exit(0)
                else:
                    slowprint("\033[91mInvalid choice. Please try again.")

        def osint_menu():
            slowprint("\033[92mStarting Osint menu tool...")
            os.system("clear")
            print('''\033[95m

            

    ███████             ███              █████                                                     
  ███░░░░░███          ░░░              ░░███                                                      
 ███     ░░███  █████  ████  ████████   ███████      █████████████    ██████  ████████   █████ ████               
░███      ░███ ███░░  ░░███ ░░███░░███ ░░░███░      ░░███░░███░░███  ███░░███░░███░░███ ░░███ ░███ 
░███      ░███░░█████  ░███  ░███ ░███   ░███        ░███ ░███ ░███ ░███████  ░███ ░███  ░███ ░███ 
░░███     ███  ░░░░███ ░███  ░███ ░███   ░███ ███    ░███ ░███ ░███ ░███░░░   ░███ ░███  ░███ ░███ 
 ░░░███████░   ██████  █████ ████ █████  ░░█████     █████░███ █████░░██████  ████ █████ ░░████████
   ░░░░░░░    ░░░░░░  ░░░░░ ░░░░ ░░░░░    ░░░░░     ░░░░░ ░░░ ░░░░░  ░░░░░░  ░░░░ ░░░░░   ░░░░░░░░                                                                                
''')    
            print('''\033[95m
[01]  | Search number           [07] | Search by IP address
[02]  | Search by HLR           [08] | Search by username
[03]  | Search in databases     [09] | Discord search 
[04]  | GitHub pull request     [10] | Password encryption
[05]  | Instagram search        [11] | Google Dork
[06]  | Dns Scan                [12] | Email Lookup
[00]  | Back to main menu                
''')

            while True:
                choice = input("\033[97mEnter the number of the tool you want to use: ")
                if choice == '1':
                    slowprint("\033[92mStarting Search number tool...")
                    break
                elif choice == '2':
                    slowprint("\033[92mStarting Search by HLR tool...")
                    break
                elif choice == '3':
                    slowprint("\033[92mStarting Search in databases tool...")
                    break
                elif choice == '4':
                    slowprint("\033[92mStarting GitHub pull request tool...")
                    break
                elif choice == '5':
                    slowprint("\033[92mStarting Instagram search tool...")
                    break
                elif choice == '6':
                    slowprint("\033[92mStarting Dns Scan tool...")
                    break
                elif choice == '7':
                    slowprint("\033[92mStarting Search by IP address tool...")
                    break
                elif choice == '8':
                    slowprint("\033[92mStarting Search by username tool...")
                    break
                elif choice == '9':
                    slowprint("\033[92mStarting Discord search tool...")
                    break
                elif choice == '10':
                    slowprint("\033[92mStarting Password encryption tool...")
                    break
                elif choice == '11':
                    slowprint("\033[92mStarting Google Dork tool...")
                    break
                elif choice == '12':
                    slowprint("\033[92mStarting Email Lookup tool...")
                    break
                elif choice == '00' or choice == '0':
                    main_menu()
                    break
                else:
                    slowprint("\033[91mInvalid choice. Please try again.")

        # Start main menu
        main_menu()
    
    else:
        slowprint("\033[91mInvalid KEY! Access denied.")
        sys.exit(1)

except KeyboardInterrupt:
    slowprint("\n\033[91mProgram interrupted by user.")
    sys.exit(1)
except Exception as e:
    slowprint(f"\033[91mAn error occurred: {str(e)}")
    sys.exit(1)