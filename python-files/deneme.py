import os
import platform
import subprocess
import getpass
import ctypes

def check_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_network_info():
    print("\n=== NETWORK CONFIGURATION ===\n")

    print(">> IP Configuration:")
    subprocess.call("ipconfig /all", shell=True)

    print("\n>> Active Connections:")
    subprocess.call("netstat -ano", shell=True)

    print("\n>> Routing Table:")
    subprocess.call("route print", shell=True)

def get_installed_software():
    print("\n=== INSTALLED SOFTWARE (via WMIC) ===\n")
    try:
        output = subprocess.check_output(
            'wmic product get name,version', 
            shell=True, 
            text=True,
            stderr=subprocess.DEVNULL
        )
        print(output)
    except subprocess.CalledProcessError:
        print("Could not retrieve installed software list.")
    except Exception as e:
        print(f"Error: {e}")

def get_user_info():
    print("=== SYSTEM INFORMATION ===\n")
    print(f">> Current User   : {getpass.getuser()}")
    print(f">> Hostname       : {platform.node()}")
    print(f">> OS             : {platform.system()} {platform.release()}")
    print(f">> Architecture   : {platform.machine()}")
    print(f">> Admin Rights   : {'Yes' if check_admin() else 'No'}")

def main():
    get_user_info()
    get_network_info()
    get_installed_software()

if __name__ == "__main__":
    main()
