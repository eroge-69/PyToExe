import os
import shutil
import tempfile

def ocisti_folder(putanja):
    if os.path.exists(putanja):
        for root, dirs, files in os.walk(putanja):
            for fajl in files:
                try:
                    os.remove(os.path.join(root, fajl))
                except:
                    pass
            for dir in dirs:
                try:
                    shutil.rmtree(os.path.join(root, dir))
                except:
                    pass

# 1. %temp%
ocisti_folder(tempfile.gettempdir())

# 2. C:\Windows\Temp
ocisti_folder(r"C:\Windows\Temp")

# 3. C:\Windows\Prefetch
ocisti_folder(r"C:\Windows\Prefetch")

print("Čišćenje završeno!")
input("Pritisni Enter za izlaz...")
