def windows_diagnose():
    while True:
        print("\033[33m--- Windows Diagnose (Manual) ---\033[0m")
        print("1. Hard Drive | Memory (RAM) Health")
        print("2. Windows Command Line Tools")
        print("3. Go Back")

        choice = input("Enter Choice 1|2|3:")

        if choice == '1':
           print("\033[33m--- Diagnose PC or Laptop Memory (RAM): ---\033[0m")
           print("> Windows + R (Keyboard)")
           print("> Type \033[92mmdsched.exe\033[0m - Restart PC or Laptop - Done!")
           print("#####################")
           
           print("\033[33m--- Disk Cleanup: ---\033[0m")
           print("> Windows + R (Keyboard)")
           print("> Type \033[92mcleanmgr /cDrive\033[0m")
           print("#####################")
           
           print("\033[33m--- Check Hard Drive Status (SSD or HDD): ---\033[0m")
           print("> CMD - Run as administrator")
           print("> Type \033[92mwmic diskdrive get status\033[0m")
           print("#####################") 
           
           print("\033[33m--- View Windows Original Product Key: ---\033[0m")
           print("> CMD - Run as administrator")
           print("> Type \033[92mwmic path softwarelicensingservice get OA3xOriginalProductKey\033[0m")
           print("or")
           print("TQV42-ND6XW-PXYPG-H6Q2C-4RG4D (Optional)")
           print("#####################")
           
           print("\033[33m--- View PC or Laptop Specification: ---\033[0m")
           print("> CMD - Run as administrator")
           print("> Type \033[92msysteminfo\033[0m")
           print("#####################")
        elif  choice == '2':
           print("\033[33m--- 3 Critical Windows command-line tools: ---\033[0m")
           print("> CMD - Run as administrator")
           print("> Type - \033[92msfc /scannow\033[0m")
           print("#####################")
           
           print("> CMD - Run as administrator")
           print("> Type - \033[92mdism /english /online /cleanup-image /restorehealth\033[0m")
           print("#####################")
           
           print("> CMD - Run as administrator")
           print("> Type - \033[92mchkdsk c: /f /r\033[0m")
           print("#####################")

        elif choice == '3':
            break
        else:
            print("\033[91mInvalid input, please try again!\033[0m")
        

def windows_activation():
    while True:
        print("\033[33m--- Windows Activation (Online)---\033[0m")
        print("1. MAS")
        print("2. Back to Main Menu")

        choice = input("Enter Choice 1|2:")

        if choice == '1':
           code() 
        elif  choice == '2':
            break
        else:
            print("\033[91mInvalid input, please try again!\033[0m")

def code():
    while True:
        print("\033[33m--- Microsoft Activation Script (MAS) ---\033[0m")
        print("> Open PowerShell")
        print("> To do that, press the Windows key + X, then select PowerShell or Terminal.")
        print("> Copy and paste the code below, then press enter.")
        print("> \033[92mirm https://get.activated.win | iex \033[0m")
        print("or")
        print("> \033[92mirm https://massgrave.dev/get | iex \033[0m")
        print("2. Go Back")
        print("#####################")

        choice = input("Enter 2 to Go Back:")
        
        if  choice == '2':
            break
        else:
            print("\033[91mInvalid input, please try again!\033[0m")
                
                            
def main_menu():
    while True:
        print("\033[33m--- MAIN MENU ---\033[0m")
        print("-- Basic Windows Tools --")
        print("1. Windows Activation (Online)")
        print("2. Windows Diagnose (Manual)")
        print("3. Exit")

        choice = input("Enter Choice 1|2|3:")

        if choice == '1':
            windows_activation()
        elif choice == '2':
            windows_diagnose()
        elif choice == '3':
            print("Exiting the program, Goodbye!")
            break
        else:
            print("\033[91mInvalid input, please try again!\033[0m")
            
        
if __name__ =="__main__":
    main_menu()
