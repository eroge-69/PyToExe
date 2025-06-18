import subprocess
import os

# Run Burp.bat in a hidden window
subprocess.run([r"C:\Burp\Burp.bat"], shell=True, creationflags=subprocess.CREATE_NO_WINDOW) 